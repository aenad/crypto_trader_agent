"""Strict normalization: never silently repair gaps or infer historical books."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from quantpilot.config import stable_id
from quantpilot.models import Candle

from .domain import Book, Level, Market, Trade, canonical_pair, utc_time

RESOLUTIONS = {
    "1": 60,
    "15": 900,
    "60": 3600,
    "240": 14400,
    "480": 28800,
    "720": 43200,
    "1D": 86400,
    "2D": 172800,
    "3D": 259200,
}


def unwrap(payload: Any) -> Any:
    if isinstance(payload, dict) and payload.get("success") is False:
        raise ValueError("Wallex reports unsuccessful response")
    return payload.get("result", payload) if isinstance(payload, dict) else payload


def decimal_value(value: Any) -> Decimal:
    # MCP structuredContent may already contain JSON floats. Decimal(str(...))
    # preserves only exposed decimal digits; never claim original JSON precision.
    return Decimal(str(value))


def markets(payload: Any) -> list[Market]:
    rows = unwrap(payload)["markets"]
    result = []
    for row in rows:
        quote = row["quote_asset"]
        if quote not in ("TMN", "USDT"):
            continue
        pair = canonical_pair(f"{row['base_asset']}/{quote}")
        if row["symbol"] != pair.replace("/", ""):
            raise ValueError("Market wire/base/quote mismatch")
        result.append(
            Market(
                symbol=pair, base=row["base_asset"], quote=quote, spot=row.get("is_spot") is True
            )
        )
    return result


def candles(
    payload: Any, pair: str, resolution: str, received: datetime, start: datetime, end: datetime
) -> list[Candle]:
    canonical_pair(pair)
    seconds = RESOLUTIONS[resolution]
    data = unwrap(payload)
    if data.get("s") == "no_data":
        return []
    if data.get("s") != "ok":
        raise ValueError("Unsuccessful candle status")
    keys = ("t", "o", "h", "l", "c", "v")
    if any(not isinstance(data.get(k), list) for k in keys):
        raise ValueError("Missing candle columns")
    if len({len(data[k]) for k in keys}) != 1:
        raise ValueError("Candle column lengths differ")
    result = []
    previous = None
    for ts, op, hi, lo, cl, vol in zip(*(data[k] for k in keys), strict=True):
        opened = utc_time(ts)
        if previous is not None and opened <= previous:
            raise ValueError("Duplicate or unordered candle timestamps")
        if int(opened.timestamp()) % seconds:
            raise ValueError("Candle resolution/alignment mismatch")
        previous = opened
        closed = opened + timedelta(seconds=seconds)
        if opened < start or opened >= end:
            continue
        if closed > received or closed > end:
            continue  # Current candle is explicitly excluded, never persisted as closed.
        result.append(
            Candle(
                event_id=stable_id(
                    {"pair": pair, "resolution": resolution, "open": opened.isoformat()}
                ),
                symbol=pair,
                event_time=closed,
                received_at=received,
                source="wallex",
                open_time=opened,
                close_time=closed,
                closed=True,
                open=decimal_value(op),
                high=decimal_value(hi),
                low=decimal_value(lo),
                close=decimal_value(cl),
                volume=decimal_value(vol),
            )
        )
    return result


def validate_coverage(rows: list[Candle], start: datetime, end: datetime, seconds: int) -> None:
    if start >= end or int((end - start).total_seconds()) % seconds:
        raise ValueError("Invalid historical range")
    expected = int((end - start).total_seconds()) // seconds
    if (
        len(rows) != expected
        or not rows
        or rows[0].open_time != start
        or rows[-1].close_time != end
    ):
        raise ValueError("Candle gap or incomplete historical coverage")
    for left, right in zip(rows, rows[1:]):
        if left.close_time != right.open_time:
            raise ValueError("Candle gap, duplicate or ordering error")


def recent_trades(payload: Any, pair: str, received: datetime) -> list[Trade]:
    canonical_pair(pair)
    result: dict[str, Trade] = {}
    for row in unwrap(payload)["latestTrades"]:
        if row["symbol"] != pair.replace("/", ""):
            raise ValueError("Trade symbol mismatch")
        when = utc_time(row["timestamp"])
        if when > received:
            raise ValueError("Future trade")
        identity = stable_id(
            {k: row[k] for k in ("symbol", "timestamp", "price", "quantity", "isBuyOrder")}
        )
        result[identity] = Trade(
            event_id=identity,
            symbol=pair,
            event_time=when,
            received_at=received,
            source="wallex",
            price=decimal_value(row["price"]),
            quantity=decimal_value(row["quantity"]),
            buyer_initiated=row["isBuyOrder"],
        )
    return sorted(result.values(), key=lambda event: event.event_time)


def book(payload: Any, pair: str, received: datetime) -> Book:
    canonical_pair(pair)
    data = unwrap(payload)

    def levels(key: str, reverse: bool) -> tuple[Level, ...]:
        result = tuple(
            Level(price=decimal_value(row["price"]), quantity=decimal_value(row["quantity"]))
            for row in data[key]
        )
        if len({level.price for level in result}) != len(result):
            raise ValueError("Duplicate book price")
        return tuple(sorted(result, key=lambda level: level.price, reverse=reverse))

    # This response has no exchange timestamp. Observation time must stay explicit.
    return Book(
        event_id=stable_id(
            {
                "pair": pair,
                "observed": received.isoformat(),
                "data": {
                    k: [{"price": str(r["price"]), "quantity": str(r["quantity"])} for r in data[k]]
                    for k in ("bid", "ask")
                },
            }
        ),
        symbol=pair,
        event_time=received,
        received_at=received,
        source="wallex",
        bids=levels("bid", True),
        asks=levels("ask", False),
    )
