"""Read-only credit-account discovery. Never an execution or activation entry point."""

import argparse
import asyncio
import json
import logging
from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from typing import Any

from pydantic import SecretStr

from .settings import WallexConnectionSettings, load_wallex_settings

ENDPOINT = "https://api.wallex.ir/mcp"
ACCOUNT_LIST = "wallex_credit_active_sub_accounts_list"
WALLET = "wallex_credit_sub_account_balances_details"
PACKAGE = "wallex_credit_active_user_package_details"
READ_TOOLS = frozenset({ACCOUNT_LIST, WALLET, PACKAGE})


def load_key(path: Path, environ: Mapping[str, str] | None = None) -> SecretStr:
    """Compatibility helper; read only allowlisted settings, never global dotenv."""
    key = load_wallex_settings(path, environ).api_key
    if not key.get_secret_value():
        raise ValueError("WALLEX_API_KEY_REQUIRED")
    return key


async def read_accounts(
    session: Any,
    include_details: bool = False,
    progress: dict[str, str] | None = None,
) -> dict[str, object]:
    """Discover the exact schema first. Do not select an account implicitly."""
    tools: dict[str, Any] = {}
    cursor = None
    cursors: set[str] = set()
    for _ in range(20):
        if progress is not None:
            progress["stage"] = "MCP_TOOLS_LIST"
        page = await session.list_tools(cursor=cursor)
        for tool in page.tools:
            if tool.name in tools:
                raise ValueError("DUPLICATE_TOOL_METADATA")
            tools[tool.name] = tool
        cursor = page.nextCursor
        if not cursor:
            break
        if cursor in cursors:
            raise ValueError("REPEATED_DISCOVERY_CURSOR")
        cursors.add(cursor)
    else:
        raise ValueError("DISCOVERY_PAGE_LIMIT")
    from jsonschema import validate

    async def read(name: str) -> Any:
        def finish(body: Any) -> Any:
            if progress is not None:
                progress["read:" + name] = (
                    "REPORTED_SUCCESS"
                    if isinstance(body, dict) and body.get("success") is True
                    else "UNVERIFIED_RESPONSE"
                )
            return body

        # Constant allowlist: no CLI, LLM or remote-text tool routing.
        tool = tools.get(name)
        if (
            name not in READ_TOOLS
            or tool is None
            or "STATE-CHANGING" in (tool.description or "").upper()
        ):
            raise ValueError("VERIFIED_READ_ONLY_ACCOUNT_TOOL_REQUIRED")
        validate({}, tool.inputSchema)
        if progress is not None:
            progress["stage"] = "MCP_CALL:" + name
        result = await session.call_tool(name, {})
        if result.isError:
            raise ValueError("CREDIT_ACCOUNT_READ_FAILED")
        if result.structuredContent is not None:
            return finish(result.structuredContent)
        for item in result.content:
            if getattr(item, "type", None) == "text":
                try:
                    return finish(json.loads(item.text))
                except (ValueError, TypeError):
                    continue
        raise ValueError("STRUCTURED_CREDIT_RESPONSE_REQUIRED")

    payload = await read(ACCOUNT_LIST)
    # Never print or persist an account dump or interpret an undocumented result
    # shape as authenticated account identity / trade permission.
    reported_success = isinstance(payload, dict) and payload.get("success") is True
    reported_failure = isinstance(payload, dict) and payload.get("success") is False
    # Count only an explicit array at a known envelope path; no inference from
    # arbitrary dictionary values and no disclosure of account IDs or balances.
    node: Any = payload
    account_count: int | None = None
    shape = "UNRECOGNIZED"
    for _ in range(4):
        if isinstance(node, list):
            shape, account_count = "ARRAY", len(node)
            break
        if not isinstance(node, dict):
            break
        shape = "OBJECT"
        if node.get("success") is False:
            reported_failure, reported_success = True, False
            break
        paths = [
            name
            for name in ("result", "data", "accounts", "subAccounts", "sub_accounts")
            if name in node
        ]
        if len(paths) != 1:
            break
        node = node[paths[0]]
    summary: dict[str, object] = {
        "mcp_connected": True,
        "verified_account_list_tool": ACCOUNT_LIST,
        "private_read_status": (
            "REPORTED_SUCCESS"
            if reported_success
            else "REPORTED_FAILURE"
            if reported_failure
            else "RESPONSE_REQUIRES_SCHEMA_REVIEW"
        ),
        "account_identity_verified": False,
        "credit_order_routing_verified": False,
        "trading_permissions_verified": False,
        "account_list_shape": shape,
        "returned_account_count": account_count,
        "live_enabled": False,
        "exchange_mutation_calls": 0,
    }
    if include_details:
        for name, label in ((WALLET, "credit_wallet"), (PACKAGE, "active_package")):
            try:
                detail = await read(name)
                summary[label + "_read_status"] = (
                    "REPORTED_SUCCESS"
                    if isinstance(detail, dict) and detail.get("success") is True
                    else "UNVERIFIED_RESPONSE"
                )
            except Exception:
                summary[label + "_read_status"] = "READ_FAILED"
        # No identity/permission/ownership flags are upgraded from success alone.
    return summary


async def probe(
    key: SecretStr,
    include_details: bool = False,
    *,
    sub_account_client_id: SecretStr | None = None,
    progress: dict[str, str] | None = None,
) -> dict[str, object]:
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    def http_client(
        headers: dict[str, str] | None = None,
        timeout: httpx.Timeout | None = None,
        auth: httpx.Auth | None = None,
    ) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers=headers,
            timeout=timeout or httpx.Timeout(15),
            auth=auth,
            follow_redirects=False,
            trust_env=False,
        )

    headers = {"X-API-Key": key.get_secret_value()}
    if sub_account_client_id is not None:
        headers = WallexConnectionSettings(
            api_key=key, sub_account_client_id=sub_account_client_id
        ).private_headers(sub_account_context=True)
    if progress is not None:
        progress["stage"] = "MCP_CONNECT"
    async with streamablehttp_client(
        ENDPOINT,
        headers=headers,
        timeout=timedelta(seconds=15),
        sse_read_timeout=timedelta(seconds=20),
        httpx_client_factory=http_client,
        terminate_on_close=False,
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            if progress is not None:
                progress["stage"] = "MCP_INITIALIZE"
            await session.initialize()
            if progress is not None:
                progress["initialized"] = "true"
            return await read_accounts(session, include_details, progress)


async def rest_probe(
    connection: WallexConnectionSettings,
    *,
    sub_account_context: bool,
    progress: dict[str, str] | None = None,
) -> dict[str, object]:
    """One fixed official wallet GET. Never emits account data or follows redirects."""
    import httpx

    path = "/v1/account/balances-detail" if sub_account_context else "/v1/account/balances"
    headers = connection.private_headers(sub_account_context=sub_account_context)
    headers.update({"Accept": "application/json", "Content-Type": "application/json"})
    if progress is not None:
        progress["stage"] = "REST_WALLET_GET"
    async with httpx.AsyncClient(timeout=15, follow_redirects=False, trust_env=False) as client:
        response = await client.get(connection.api_base + path, headers=headers)
    success = False
    if response.status_code == 200:
        try:
            body = response.json()
            success = isinstance(body, dict) and body.get("success") is True
        except ValueError:
            pass
    return {
        "status": "READ_SUCCEEDED" if success else "READ_FAILED",
        "transport": "REST",
        "http_status_codes": [response.status_code],
        "request_path": path,
        "private_read_status": "REPORTED_SUCCESS" if success else "FAILED",
        "sub_account_header_sent": sub_account_context,
        "account_identity_verified": False,
        "trading_permissions_verified": False,
        "credit_order_routing_verified": False,
        "api_key_matches_sub_account": "UNVERIFIED",
        "live_enabled": False,
        "exchange_mutation_calls": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument(
        "--diagnose",
        action="store_true",
        help="Discover account ID and run a bounded read-only REST diagnostic matrix",
    )
    parser.add_argument(
        "--file-only",
        action="store_true",
        help="Use the selected env file without process environment overrides",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Save sanitized diagnostic output as JSON; contains no account dumps",
    )
    parser.add_argument(
        "--rest",
        action="store_true",
        help="Read the official wallet REST endpoint directly instead of MCP",
    )
    parser.add_argument(
        "--include-details",
        action="store_true",
        help="MCP only: also read credit wallet/package; print status only, no account data",
    )
    parser.add_argument(
        "--sub-account-context",
        action="store_true",
        help="Send sub-account read context; MCP forwarding remains unverified",
    )
    args = parser.parse_args()
    # Prevent library diagnostics from emitting headers or raw account responses.
    logging.disable(logging.CRITICAL)
    progress = {"stage": "LOAD_LOCAL_SETTINGS"}
    try:
        connection = load_wallex_settings(args.env_file, {} if args.file_only else None)
        connection.private_headers(sub_account_context=args.sub_account_context)
        if args.diagnose:
            from .credit_diagnostics import diagnose

            progress["stage"] = "REST_DIAGNOSTIC_MATRIX"
            operation = diagnose(connection)
        else:
            operation = (
                rest_probe(
                    connection,
                    sub_account_context=args.sub_account_context,
                    progress=progress,
                )
                if args.rest
                else probe(
                    connection.api_key,
                    args.include_details,
                    sub_account_client_id=connection.sub_account_client_id
                    if args.sub_account_context
                    else None,
                    progress=progress,
                )
            )
        result = asyncio.run(
            asyncio.wait_for(
                operation,
                timeout=120 if args.diagnose else 45,
            )
        )
        if not args.diagnose:
            result["sub_account_header_sent"] = args.sub_account_context
        if not args.rest and not args.diagnose:
            result["mcp_header_forwarding_verified"] = False
        result["api_key_matches_sub_account"] = "UNVERIFIED"
    except (Exception, BaseExceptionGroup) as exc:
        pending: list[BaseException] = [exc]
        failures: list[str] = []
        statuses: list[int] = []
        while pending:
            error = pending.pop()
            if isinstance(error, BaseExceptionGroup):
                pending.extend(error.exceptions)
            else:
                # Type names only; never an exception's message/body/headers.
                failures.append(type(error).__name__)
                code = getattr(getattr(error, "response", None), "status_code", None)
                if isinstance(code, int):
                    statuses.append(code)
        print(
            json.dumps(
                {
                    "status": "READ_FAILED",
                    "live_enabled": False,
                    "exchange_mutation_calls": 0,
                    "message": "Read failed; check key permissions and MCP connectivity.",
                    "failure_types": sorted(set(failures)),
                    "http_status_codes": sorted(set(statuses)),
                    "failed_stage": progress["stage"],
                    "mcp_connected": progress.get("initialized") == "true",
                    "completed_reads": {
                        key.removeprefix("read:"): value
                        for key, value in progress.items()
                        if key.startswith("read:")
                    },
                }
            )
        )
        raise SystemExit(1) from None
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, sort_keys=True, indent=2), encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result.get("status") == "READ_FAILED" or (
        args.diagnose
        and result.get("status") not in ("CREDIT_READS_READY", "CREDIT_READS_READY_WITH_WARNINGS")
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
