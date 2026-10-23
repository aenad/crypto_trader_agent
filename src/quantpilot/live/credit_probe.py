"""Read-only credit-account discovery. Never an execution or activation entry point."""

import argparse
import asyncio
import json
import logging
import os
import re
from collections.abc import Mapping
from datetime import timedelta
from pathlib import Path
from typing import Any

from pydantic import SecretStr

ENDPOINT = "https://api.wallex.ir/mcp"
ACCOUNT_LIST = "wallex_credit_active_sub_accounts_list"
WALLET = "wallex_credit_sub_account_balances_details"
PACKAGE = "wallex_credit_active_user_package_details"
READ_TOOLS = frozenset({ACCOUNT_LIST, WALLET, PACKAGE})


def load_key(path: Path, environ: Mapping[str, str] | None = None) -> SecretStr:
    """Read only the approved key; no interpolation, global dotenv or key logging."""
    env = os.environ if environ is None else environ
    value: str | None = env.get("WALLEX_API_KEY")
    if value is None:
        if not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise ValueError("LOCAL_KEY_FILE_MISSING_OR_TOO_LARGE")
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = re.match(r"^\s*(?:export\s+)?WALLEX_API_KEY\s*=\s*(.*)$", line)
            if not match:
                continue
            if value is not None:
                raise ValueError("DUPLICATE_WALLEX_KEY")
            raw = match[1].strip()
            if raw.startswith(("'", '"')):
                end = raw.rfind(raw[0])
                if end == 0 or (
                    raw[end + 1 :].strip() and not raw[end + 1 :].strip().startswith("#")
                ):
                    raise ValueError("INVALID_KEY_LITERAL")
                value = raw[1:end]
            else:
                value = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
    if not value or any(ord(c) <= 32 or ord(c) == 127 for c in value):
        raise ValueError("MISSING_OR_INVALID_WALLEX_KEY")
    return SecretStr(value)


async def read_accounts(session: Any, include_details: bool = False) -> dict[str, object]:
    """Discover the exact schema first. Do not select an account implicitly."""
    tools: dict[str, Any] = {}
    cursor = None
    cursors: set[str] = set()
    for _ in range(20):
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
        # Constant allowlist: no CLI, LLM or remote-text tool routing.
        tool = tools.get(name)
        if (
            name not in READ_TOOLS
            or tool is None
            or "STATE-CHANGING" in (tool.description or "").upper()
        ):
            raise ValueError("VERIFIED_READ_ONLY_ACCOUNT_TOOL_REQUIRED")
        validate({}, tool.inputSchema)
        result = await session.call_tool(name, {})
        if result.isError:
            raise ValueError("CREDIT_ACCOUNT_READ_FAILED")
        if result.structuredContent is not None:
            return result.structuredContent
        for item in result.content:
            if getattr(item, "type", None) == "text":
                try:
                    return json.loads(item.text)
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


async def probe(key: SecretStr, include_details: bool = False) -> dict[str, object]:
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

    async with streamablehttp_client(
        ENDPOINT,
        headers={"X-API-Key": key.get_secret_value()},
        timeout=timedelta(seconds=15),
        sse_read_timeout=timedelta(seconds=20),
        httpx_client_factory=http_client,
        terminate_on_close=False,
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await read_accounts(session, include_details)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument(
        "--include-details",
        action="store_true",
        help="Also read credit wallet/package; print status only, no account data",
    )
    args = parser.parse_args()
    # Prevent library diagnostics from emitting headers or raw account responses.
    logging.disable(logging.CRITICAL)
    try:
        key = load_key(args.env_file)
        result = asyncio.run(asyncio.wait_for(probe(key, args.include_details), timeout=45))
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
                }
            )
        )
        raise SystemExit(1) from None
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
