"""Bounded, read-only REST diagnosis with explicit credit account discovery."""

import asyncio
import json
import re
from collections.abc import Awaitable, Callable
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from .settings import WallexConnectionSettings

PATHS = frozenset(
    {
        "/sub-accounts",
        "/v1/account/balances",
        "/v1/account/balances-detail",
        "/v1/prop/user/packages/active",
        "/v1/prop/user/packages/overview",
        "/v1/account/fee",
        "/v1/account/openOrders",
    }
)


def safe_error_details(response: httpx.Response) -> dict[str, object]:
    """Expose fixed generic messages/categories, never arbitrary upstream text."""
    details: dict[str, object] = {}
    if len(response.content) > 32768:
        return {"server_error_body": "OMITTED_TOO_LARGE"}
    try:
        body = response.json()
    except ValueError:
        return {"server_error_body": "NON_JSON_OMITTED"}
    if not isinstance(body, dict):
        return {"server_error_body": "UNSUPPORTED_SHAPE_OMITTED"}
    error = object_map(body.get("error"))
    message = next(
        (
            v
            for v in (
                body.get("message"),
                body.get("detail"),
                error.get("message"),
                body.get("error"),
            )
            if isinstance(v, str)
        ),
        "",
    )
    normalized = " ".join(message.lower().strip().rstrip(".").split())
    generic = {
        "unauthorized": "Unauthorized",
        "unauthenticated": "Unauthenticated",
        "access denied": "Access denied",
        "permission denied": "Permission denied",
        "forbidden": "Forbidden",
        "invalid api key": "Invalid API key",
        "api key expired": "API key expired",
        "token expired": "Token expired",
    }
    auth_words = set(
        (
            "please login first you must be logged in log sign to continue unauthorized "
            "unauthenticated access denied forbidden permission required authentication "
            "authorization invalid key api is not expired token session before route "
            "ابتدا لطفا لطفاً وارد حساب کاربری خود شوید سایت برای این عملیات انجام نیاز به "
            "ورود است احراز هویت نامعتبر کلید منقضی شده دسترسی غیرمجاز مجاز نیست لاگین کنید "
            "توکن باید می"
        ).split()
    )
    words = re.findall(r"[^\W\d_]+", normalized)
    safe_phrase = (
        bool(words)
        and len(words) <= 25
        and len(message) <= 160
        and all(word in auth_words for word in words)
        and re.fullmatch(r"[\w\s.,!؟،؛\u200c-]+", normalized) is not None
        and not any(char.isdigit() for char in normalized)
    )
    details["server_message"] = generic.get(
        normalized, message.strip() if safe_phrase else "UNRECOGNIZED_MESSAGE_OMITTED"
    )
    details["server_message_present"] = bool(message)
    categories = {
        "authentication": (
            "unauthenticated",
            "unauthorized",
            "authentication",
            "login",
            "log in",
            "sign in",
            "احراز هویت",
            "ورود",
            "وارد",
            "لاگین",
        ),
        "api_key": ("api key", "api-key", "apikey", "کلید"),
        "access_permission": ("permission", "access", "forbidden", "دسترسی", "مجوز"),
        "sub_account": ("sub-account", "subaccount", "حساب اعتباری", "زیرحساب"),
        "main_account": ("main account", "حساب اصلی"),
        "expiry": ("expired", "expiration", "منقضی"),
        "ip_restriction": ("ip address", "ip restriction", "آی پی"),
    }
    details["server_message_categories"] = [
        name for name, words in categories.items() if any(word in normalized for word in words)
    ]
    code = next(
        (
            v
            for v in (
                body.get("code"),
                body.get("error_code"),
                body.get("errorCode"),
                error.get("code"),
            )
            if type(v) is int and 0 <= v <= 1000000000
        ),
        None,
    )
    if code is not None:
        details["server_error_code"] = code
    challenge = response.headers.get("WWW-Authenticate", "").split(" ", 1)[0].lower()
    if challenge in ("basic", "bearer"):
        details["auth_challenge_scheme"] = challenge
    return details


def candidates(payload: Any) -> list[str]:
    """Require the verified array and explicit eligibility flags; do not guess IDs."""
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("ACCOUNT_LIST_NOT_SUCCESSFUL")
    rows = payload.get("result")
    if not isinstance(rows, list):
        raise ValueError("UNSUPPORTED_ACCOUNT_LIST_SHAPE")
    total = (payload.get("result_info") or {}).get("total_count")
    if total is not None and (type(total) is not int or total != len(rows)):
        raise ValueError("INCOMPLETE_ACCOUNT_LIST")
    ids = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("UNSUPPORTED_ACCOUNT_ROW")
        if (
            row.get("isActive") is True
            and row.get("isSuspend") is False
            and row.get("type") == "prop"
        ):
            identity = row.get("clientId")
            if not isinstance(identity, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", identity):
                raise ValueError("INVALID_DISCOVERED_ID")
            ids.append(identity)
    if len(set(ids)) != len(ids):
        raise ValueError("DUPLICATE_DISCOVERED_ID")
    return ids


def number(value: object) -> Decimal | None:
    if not isinstance(value, (str, int, Decimal)) or isinstance(value, bool):
        return None
    try:
        result = Decimal(value)
    except (InvalidOperation, ValueError):
        return None
    return result if result.is_finite() and result >= 0 else None


def object_map(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


async def diagnose(
    connection: WallexConnectionSettings,
    *,
    transport: httpx.AsyncBaseTransport | None = None,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> dict[str, object]:
    """Fixed allowlisted GETs; retry transient statuses once, never 401/403.

    IDs and payloads stay in memory. Findings contain statuses/booleans only.
    This cannot authorize, activate or submit a trade.
    """
    observations: list[dict[str, object]] = []
    report: dict[str, object] = {
        "transport": "REST",
        "checks": observations,
        "account_discovery": "UNVERIFIED",
        "sub_account_id_matches_discovery": False,
        "account_identity_verified": False,
        "api_key_matches_sub_account": "UNVERIFIED",
        "trading_permissions_verified": False,
        "credit_order_routing_verified": False,
        "live_enabled": False,
        "exchange_mutation_calls": 0,
    }
    async with httpx.AsyncClient(
        transport=transport,
        timeout=15,
        trust_env=False,
        follow_redirects=False,
    ) as client:

        async def read(path: str, headers: dict[str, str], label: str) -> Any:
            if path not in PATHS:
                raise ValueError("READ_ENDPOINT_BLOCKED")
            row: dict[str, object] = {"check": label, "method": "GET", "path": path}
            observations.append(row)
            for attempt in range(2):
                row["attempts"] = attempt + 1
                try:
                    response = await client.get(connection.api_base + path, headers=headers)
                    row["http_status"] = response.status_code
                    if response.status_code in (429, 502, 503, 504) and attempt == 0:
                        delay = response.headers.get("Retry-After", "")
                        # Respect server delays; do not retry early when outside our bounded run.
                        if delay and (not delay.isdigit() or int(delay) > 3):
                            row["status"] = "DEFERRED_RETRY_AFTER"
                            return None
                        await sleep(float(delay) if delay else 1.0)
                        continue
                    if response.status_code != 200:
                        row["status"] = "HTTP_FAILURE"
                        row.update(safe_error_details(response))
                        return None
                    if len(response.content) > 2 * 1024 * 1024:
                        row["status"] = "RESPONSE_TOO_LARGE"
                        return None
                    body = json.loads(response.text, parse_float=Decimal)
                    if not isinstance(body, dict) or body.get("success") is not True:
                        row["status"] = "UNVERIFIED_RESPONSE"
                        return None
                    row["status"] = "REPORTED_SUCCESS"
                    return body
                except (httpx.HTTPError, ValueError, TypeError):
                    row["status"] = "READ_FAILED"
                    return None
            return None

        key_headers = connection.private_headers()
        listing = await read("/sub-accounts", key_headers, "account_list")
        try:
            ids = candidates(listing)
        except (ValueError, AttributeError, TypeError) as exc:
            # Fixed parser reason codes only, never remote text or raw exceptions.
            report["account_discovery"] = "SCHEMA_OR_ACCESS_UNVERIFIED"
            report["selection_error"] = str(exc) if isinstance(exc, ValueError) else "INVALID_LIST"
            report["status"] = "ACCOUNT_SELECTION_BLOCKED"
            return report
        report["active_prop_accounts"] = len(ids)
        configured = connection.sub_account_client_id.get_secret_value()
        if configured:
            if configured not in ids:
                report["status"] = "CONFIGURED_ACCOUNT_NOT_IN_ACTIVE_LIST"
                return report
            identity = configured
        elif len(ids) == 1:
            identity = ids[0]
        else:
            report["status"] = "AMBIGUOUS_OR_MISSING_ACTIVE_ACCOUNT"
            return report
        report["account_discovery"] = (
            "MATCHED_CONFIGURED_ID" if configured else "UNIQUE_ACTIVE_PROP"
        )
        report["sub_account_id_matches_discovery"] = bool(configured)
        # Context is derived only from the verified API list, never a guessed header value.
        headers = {**key_headers, "sub-account-client-id": identity}
        wallet = await read("/v1/account/balances-detail", headers, "credit_wallet")
        package = await read("/v1/prop/user/packages/active", headers, "credit_package")
        package_source = "ACTIVE_ENDPOINT" if package is not None else "UNAVAILABLE"
        if package is None:
            overview = await read(
                "/v1/prop/user/packages/overview", key_headers, "package_overview_fallback"
            )
            entries = object_map(object_map(overview).get("result")).get("userPackages")
            if isinstance(entries, list):
                matches = [
                    entry
                    for entry in entries
                    if isinstance(entry, dict)
                    and object_map(entry.get("userPackageDetail")).get("subAccountClientId")
                    == identity
                ]
                if len(matches) == 1:
                    package = matches[0]
                    package_source = "OVERVIEW_MATCHED_SELECTED_ID"
        own = await read("/v1/account/balances", key_headers, "key_wallet_no_selector")
        await read("/v1/account/fee", headers, "account_fees")
        await read("/v1/account/openOrders", headers, "open_orders")
        report["credit_wallet_readable"] = wallet is not None
        report["credit_package_readable"] = package is not None
        report["credit_package_source"] = package_source
        report["status"] = "CREDIT_READS_READY" if wallet and package else "PARTIAL_READ_ACCESS"
        if wallet is not None:
            credit = object_map(object_map(wallet.get("result")).get("TMN"))
            available, frozen, total = (
                number(credit.get(k)) for k in ("available", "freeze", "total")
            )
            report["credit_tmn_schema_valid"] = (
                available is not None
                and frozen is not None
                and total is not None
                and available + frozen == total
            )
            if available is not None:
                report["credit_free_tmn_covers_order_cap"] = available >= Decimal("500000")
            # Useful anomaly indicator only, never account identity proof.
            if own is not None:
                row = object_map(
                    object_map(object_map(own.get("result")).get("balances")).get("TMN")
                )
                value, locked = number(row.get("value")), number(row.get("locked"))
                if value is not None and locked == 0 and frozen == 0 and total is not None:
                    report["wallet_value_comparison"] = "EQUAL" if value == total else "DIFFERENT"
                    report["wallet_comparison_proves_key_ownership"] = False
        if wallet is not None and report.get("credit_tmn_schema_valid") is not True:
            report["status"] = "SCHEMA_REVIEW_REQUIRED"
        elif any(row.get("status") != "REPORTED_SUCCESS" for row in observations):
            report["status"] = (
                "CREDIT_READS_READY_WITH_WARNINGS"
                if wallet is not None and package is not None
                else "PARTIAL_READ_ACCESS"
            )
    return report
