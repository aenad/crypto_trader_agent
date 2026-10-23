"""Documented spot REST contracts; single attempts for all mutations."""

import asyncio
import json
import re
from collections.abc import Callable, Mapping
from datetime import datetime
from decimal import Context, Decimal, localcontext
from typing import Any

import httpx
from pydantic import SecretStr

from quantpilot.config import stable_id
from quantpilot.models import AssetBalance, Fill, Money, OrderIntent, OrderState

from .domain import Blocked, ExchangeOrder

D = Decimal
ID = re.compile(r"^[A-Za-z0-9_-]{1,100}$")


def decimal(value: object) -> Decimal:
    if not isinstance(value, (str, int, Decimal)) or isinstance(value, bool):
        raise Blocked("INVALID_NUMERIC_CONTRACT")
    result = D(value)
    if not result.is_finite() or result < 0:
        raise Blocked("INVALID_NUMERIC_CONTRACT")
    return result


def parse_order(raw: dict[str, Any], intent: OrderIntent) -> ExchangeOrder:
    with localcontext(Context(prec=34)):
        return _parse_order(raw, intent)


def _parse_order(raw: dict[str, Any], intent: OrderIntent) -> ExchangeOrder:
    """Cumulative fills use canonical multiset occurrence IDs: docs provide no trade ID."""
    if (
        any(
            raw.get(k) != v
            for k, v in {
                "clientOrderId": intent.client_id,
                "symbol": intent.symbol.replace("/", ""),
                "side": intent.side,
                "type": intent.order_type,
            }.items()
        )
        or decimal(raw["origQty"]) != intent.base_quantity
    ):
        raise Blocked("ORDER_IDENTITY_MISMATCH")
    qty, cost = decimal(raw["executedQty"]), decimal(raw["executedSum"])
    if qty > intent.base_quantity:
        raise Blocked("OVERFILL")
    status = raw["status"]
    if status not in {"NEW", "FILLED", "CANCELED"}:
        raise Blocked("UNKNOWN_EXCHANGE_STATUS")
    active = raw["active"]
    if not isinstance(active, bool) or active != (status == "NEW"):
        raise Blocked("INCONSISTENT_ORDER_STATUS")
    if (status == "FILLED") != (qty == intent.base_quantity):
        raise Blocked("INCONSISTENT_FILLED_QUANTITY")
    state = {
        "NEW": OrderState.SUBMITTED,
        "FILLED": OrderState.FILLED,
        "CANCELED": OrderState.CANCELED,
    }[status]
    if status == "NEW" and qty > 0:
        state = OrderState.PARTIALLY_FILLED
    rows = raw.get("fills", [])
    if not isinstance(rows, list):
        raise Blocked("INVALID_FILL_LIST")
    fills: list[Fill] = []
    occurrences: dict[str, int] = {}
    quote = intent.symbol.split("/")[1]
    for row in rows:
        if row["symbol"] != raw["symbol"] or row["isBuyer"] is not (intent.side == "BUY"):
            raise Blocked("FILL_IDENTITY_MISMATCH")
        q, price, fee = decimal(row["quantity"]), decimal(row["price"]), decimal(row["fee"])
        if q * price != decimal(row["sum"]):
            raise Blocked("FILL_COST_MISMATCH")
        if intent.limit_price is not None and (
            (intent.side == "BUY" and price > intent.limit_price)
            or (intent.side == "SELL" and price < intent.limit_price)
        ):
            raise Blocked("LIMIT_PRICE_VIOLATION")
        at = datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
        canonical = [
            str(q.normalize()),
            str(price.normalize()),
            str(fee.normalize()),
            row["feeAsset"],
            at.isoformat(),
        ]
        digest = stable_id(canonical)
        occurrence = occurrences.get(digest, 0)
        occurrences[digest] = occurrence + 1
        fills.append(
            Fill(
                fill_id=stable_id([intent.client_id, digest, occurrence]),
                client_id=intent.client_id,
                symbol=intent.symbol,
                side=intent.side,
                base_quantity=q,
                price=Money(amount=price, currency=quote),
                fee=Money(amount=fee, currency=row["feeAsset"]),
                executed_at=at,
            )
        )
    if (
        sum((f.base_quantity for f in fills), D(0)) != qty
        or sum((f.base_quantity * f.price.amount for f in fills), D(0)) != cost
    ):
        raise Blocked("INCOMPLETE_CUMULATIVE_FILLS")
    return ExchangeOrder(
        state=state,
        executed_quantity=qty,
        executed_sum=cost,
        fills=tuple(sorted(fills, key=lambda f: (f.executed_at, f.fill_id))),
    )


class WallexSpotREST:
    """No arbitrary URL, cookies, redirects, logging hooks, withdrawals or POST retry."""

    def __init__(
        self,
        key: SecretStr,
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        authorize_mutation: Callable[[str, str], None] | None = None,
        sub_account_client_id: SecretStr | None = None,
    ):
        from .settings import WallexConnectionSettings

        connection = WallexConnectionSettings(
            api_key=key, sub_account_client_id=sub_account_client_id or SecretStr("")
        )
        self._headers = connection.private_headers(
            sub_account_context=sub_account_client_id is not None
        )
        self._selector = sub_account_client_id
        self._key = key
        self._authorize_mutation = authorize_mutation
        self._client = httpx.AsyncClient(
            transport=transport,
            trust_env=False,
            follow_redirects=False,
            timeout=10,
        )
        self._lock = asyncio.Lock()

    async def close(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        payload: Mapping[str, str] | None = None,
        params: Mapping[str, str | int] | None = None,
    ) -> dict[str, Any]:
        allowed = (
            (method == "POST" and path == "/v1/account/orders")
            or (method == "DELETE" and path == "/v1/account/orders")
            or (
                method == "GET"
                and path
                in {
                    "/v1/account/balances",
                    "/v1/account/balances-detail",
                    "/sub-accounts",
                    "/v1/account/fee",
                    "/v1/account/openOrders",
                    "/v1/markets",
                }
            )
            or (
                method == "GET"
                and path.startswith("/v1/account/orders/")
                and ID.fullmatch(path.removeprefix("/v1/account/orders/"))
            )
        )
        if not allowed:
            raise Blocked("ENDPOINT_BLOCKED")
        # Serialize and throttle this credential's requests. Recovery performs bounded GET retries.
        async with self._lock:
            try:
                if method in {"POST", "DELETE"}:
                    if self._authorize_mutation is None:
                        raise Blocked("TRANSPORT_MUTATIONS_DISABLED")
                    identity = (
                        (payload or {}).get("client_id", "")
                        if method == "POST"
                        else str((payload or {}).get("clientOrderId", ""))
                    )
                    self._authorize_mutation(method, identity)
                self._client.cookies.clear()
                response = await self._client.request(
                    method,
                    "https://api.wallex.ir" + path,
                    json=payload,
                    params=params,
                    headers=self._headers,
                )
                if response.status_code == 429:
                    raise Blocked("RATE_LIMITED")
                if response.status_code not in (200, 201):
                    # Even 404 is not authoritative proof an ambiguous order never existed.
                    raise Blocked("EXCHANGE_REQUEST_UNRELIABLE")
                data = json.loads(response.content, parse_float=D)
                if not isinstance(data, dict) or data.get("success") is not True:
                    raise Blocked("EXCHANGE_REQUEST_UNRELIABLE")
                result = data["result"]
                if path == "/sub-accounts" and isinstance(result, list):
                    return {"accounts": result}
                if not isinstance(result, dict):
                    raise Blocked("INVALID_EXCHANGE_RESULT")
                return result
            except (httpx.HTTPError, ValueError, KeyError):
                raise Blocked("EXCHANGE_REQUEST_UNRELIABLE") from None
            finally:
                await asyncio.sleep(0.11)

    async def submit(self, intent: OrderIntent) -> ExchangeOrder:
        if not ID.fullmatch(intent.client_id) or intent.order_type != "LIMIT":
            raise Blocked("PROTECTED_LIMIT_ORDER_REQUIRED")
        raw = await self._request(
            "POST",
            "/v1/account/orders",
            payload={
                "client_id": intent.client_id,
                "symbol": intent.symbol.replace("/", ""),
                "type": "LIMIT",
                "side": intent.side,
                "quantity": str(intent.base_quantity),
                "price": str(intent.limit_price),
            },
        )
        return parse_order(raw, intent)

    async def verify_account_context(self, selector: str) -> None:
        if self._selector is None or self._selector.get_secret_value() != selector:
            raise Blocked("CREDIT_SELECTOR_MISMATCH")
        rows = (await self._request("GET", "/sub-accounts"))["accounts"]
        matches = [r for r in rows if r.get("clientId") == selector]
        if (
            len(matches) != 1
            or matches[0].get("isActive") is not True
            or matches[0].get("isSuspend") is not False
            or matches[0].get("type") != "prop"
        ):
            raise Blocked("CREDIT_ACCOUNT_NOT_ACTIVE_OR_UNVERIFIED")

    async def lookup(self, intent: OrderIntent) -> ExchangeOrder:
        if not ID.fullmatch(intent.client_id):
            raise Blocked("INVALID_CLIENT_ID")
        return parse_order(
            await self._request(
                "GET",
                "/v1/account/orders/" + intent.client_id,
            ),
            intent,
        )

    async def cancel(self, intent: OrderIntent) -> None:
        if not ID.fullmatch(intent.client_id):
            raise Blocked("INVALID_CLIENT_ID")
        await self._request(
            "DELETE",
            "/v1/account/orders",
            payload={
                "clientOrderId": intent.client_id,
            },
        )

    async def balances(self, semantics: str) -> tuple[AssetBalance, ...]:
        if self._selector is not None:
            if semantics != "FREE":
                raise Blocked("CREDIT_AVAILABLE_BALANCE_SEMANTICS_REQUIRED")
            raw = await self._request("GET", "/v1/account/balances-detail")
            balances = []
            for asset, row in raw.items():
                available, locked, total = (
                    decimal(row["available"]),
                    decimal(row["freeze"]),
                    decimal(row["total"]),
                )
                if available + locked != total:
                    raise Blocked("CREDIT_BALANCE_TOTAL_MISMATCH")
                balances.append(AssetBalance(currency=asset, free=available, reserved=locked))
            return tuple(balances)
        raw = (await self._request("GET", "/v1/account/balances"))["balances"]
        if semantics not in {"FREE", "TOTAL"}:
            raise Blocked("UNVERIFIED_BALANCE_SEMANTICS")
        result = []
        for asset, row in raw.items():
            value, locked = decimal(row["value"]), decimal(row["locked"])
            if row["asset"] != asset:
                raise Blocked("BALANCE_IDENTITY_MISMATCH")
            result.append(
                AssetBalance(
                    currency=asset,
                    reserved=locked,
                    free=value if semantics == "FREE" else value - locked,
                )
            )
        return tuple(result)

    async def open_ids(self) -> frozenset[str]:
        ids: set[str] = set()
        for page in range(1, 101):
            result = await self._request(
                "GET", "/v1/account/openOrders", params={"page": page, "per_page": 100}
            )
            # Strict documented older shape. New grouped shapes require verified normalization.
            rows = result.get("orders")
            if not isinstance(rows, list):
                raise Blocked("UNSUPPORTED_OPEN_ORDERS_SHAPE")
            for row in rows:
                identity = row["clientOrderId"]
                if identity in ids or row["active"] is not True:
                    raise Blocked("INCONSISTENT_OPEN_ORDERS")
                ids.add(identity)
            if len(rows) < 100:
                return frozenset(ids)
        raise Blocked("OPEN_ORDER_PAGINATION_LIMIT")

    async def markets(self) -> dict[str, Any]:
        return (await self._request("GET", "/v1/markets"))["symbols"]  # type: ignore[no-any-return]

    async def fees(self) -> dict[str, Any]:
        return await self._request("GET", "/v1/account/fee")
