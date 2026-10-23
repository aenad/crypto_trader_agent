"""Centrifugo JSON protocol, public channels only. Every reconnect is a data gap."""

import asyncio
import json
from collections.abc import AsyncGenerator, Awaitable, Callable
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from quantpilot.config import stable_id
from quantpilot.models import MarketEvent

from .domain import CollectionPolicy, Level
from .normalize import candles, recent_trades
from .transport import RateLimited


class StreamObservation(MarketEvent):
    channel: str
    payload_json: str
    epoch: int
    timestamp_kind: str
    candle_complete: bool | None = None


def channel_name(pair: str, kind: str) -> str:
    wire = pair.replace("/", "")
    if kind == "trade":
        return f"public:{wire}@trade"
    if kind in ("buyDepth", "sellDepth"):
        return f"orderbook:{wire}@{kind}"
    if kind in ("1m", "1h", "1d"):
        return f"candle:{wire}@{kind}"
    raise ValueError("Unsupported documented stream channel")


def publication(frame: dict[str, Any], channel: str) -> Any:
    if frame.get("error"):
        if frame["error"].get("code") == 106:
            raise RateLimited(2)
        raise ValueError("WebSocket command rejected")
    if "push" not in frame:
        return None
    push = frame["push"]
    if "disconnect" in push:
        raise OSError("Server disconnected public stream")
    if push.get("channel") != channel:
        raise ValueError("Unexpected WebSocket channel")
    return push.get("pub", {}).get("data")


def normalize_stream(
    data: Any, pair: str, kind: str, now: datetime, epoch: int, freshness: int
) -> StreamObservation | None:
    channel = channel_name(pair, kind)
    complete = None
    if isinstance(data, dict) and "message" in data:
        data = data["message"]
    if kind == "trade":
        if data.get("symbol", pair.replace("/", "")) != pair.replace("/", ""):
            raise ValueError("Stream trade symbol mismatch")
        rows = recent_trades(
            {"latestTrades": [{**data, "symbol": pair.replace("/", "")}]}, pair, now
        )
        if not rows or (now - rows[-1].event_time).total_seconds() > freshness:
            raise ValueError("Stale stream trade")
        event_time, timestamp_kind = rows[-1].event_time, "exchange"
    elif kind in ("buyDepth", "sellDepth"):
        # Sides are independent observations; never combine across epochs or
        # pretend this is an exchange-sequenced historical full book.
        if not isinstance(data, list) or not data:
            raise ValueError("Empty stream book side")
        levels = [
            Level(price=Decimal(str(row["price"])), quantity=Decimal(str(row["quantity"])))
            for row in data
        ]
        if len({level.price for level in levels}) != len(levels):
            raise ValueError("Duplicate stream book price")
        event_time, timestamp_kind = now, "observation"
    else:
        resolution = {"1m": "1", "1h": "60", "1d": "1D"}[kind]
        seconds = {"1m": 60, "1h": 3600, "1d": 86400}[kind]
        stamps = data.get("t", [])
        if not stamps:
            raise ValueError("Empty stream candle")
        start = datetime.fromtimestamp(min(stamps), timezone.utc)
        last_open = datetime.fromtimestamp(max(stamps), timezone.utc)
        if last_open > now:
            raise ValueError("Future stream candle")
        validation_end = max(now, last_open + timedelta(seconds=seconds))
        # Validate OHLC of open updates without inserting them into the closed
        # historical candle dataset. Completeness stays explicit on the event.
        candle_rows = candles(data, pair, resolution, validation_end, start, validation_end)
        if not candle_rows:
            return None
        complete = candle_rows[-1].close_time <= now
        event_time = candle_rows[-1].close_time if complete else last_open
        timestamp_kind = "exchange" if complete else "exchange_open_candle"
        if now - event_time > timedelta(seconds=max(seconds * 2, freshness)):
            raise ValueError("Stale stream candle")
    encoded = json.dumps(data, sort_keys=True, default=str)
    return StreamObservation(
        event_id=stable_id({"channel": channel, "data": encoded}),
        symbol=pair,
        event_time=event_time,
        received_at=now,
        source="wallex-ws",
        channel=channel,
        payload_json=encoded,
        epoch=epoch,
        timestamp_kind=timestamp_kind,
        candle_complete=complete,
    )


class PublicStream:
    def __init__(self, policy: CollectionPolicy, max_reconnects: int = 4):
        self.policy, self.max_reconnects = policy, max_reconnects

    async def events(
        self, pair: str, kind: str, recover: Callable[[], Awaitable[None]] | None = None
    ) -> AsyncGenerator[StreamObservation, None]:
        if pair not in self.policy.approved or pair in self.policy.excluded:
            raise ValueError("Stream market is not whitelisted")
        channel = channel_name(pair, kind)
        seen: set[str] = set()
        previous: datetime | None = None
        for epoch in range(self.max_reconnects + 1):
            try:
                async with connect(
                    "wss://api.wallex.ir/connection/websocket",
                    open_timeout=15,
                    ping_interval=None,
                    max_queue=32,
                ) as ws:
                    await ws.send(json.dumps({"id": 1, "connect": {}}))
                    connected = subscribed = False
                    if epoch and recover:
                        await recover()
                    while True:
                        raw = await asyncio.wait_for(ws.recv(), timeout=45)
                        for line in raw.splitlines():
                            frame = json.loads(line, parse_float=Decimal)
                            if frame == {}:
                                await ws.send("{}")
                                continue
                            if frame.get("error"):
                                if frame["error"].get("code") == 106:
                                    raise RateLimited(2)
                                raise ValueError("Public WebSocket subscription rejected")
                            if frame.get("id") == 1 and "connect" in frame:
                                connected = True
                                await ws.send(
                                    json.dumps({"id": 2, "subscribe": {"channel": channel}})
                                )
                                continue
                            if frame.get("id") == 2 and "subscribe" in frame:
                                subscribed = True
                                continue
                            data = publication(frame, channel)
                            if data is None:
                                continue
                            if not connected or not subscribed:
                                raise ValueError("Publication before subscription acknowledgement")
                            event = normalize_stream(
                                data,
                                pair,
                                kind,
                                datetime.now(timezone.utc),
                                epoch,
                                self.policy.freshness_seconds,
                            )
                            if event is None or event.event_id in seen:
                                continue
                            if previous is not None and event.event_time < previous:
                                raise ValueError("Out-of-order stream event")
                            previous = event.event_time
                            if len(seen) >= 10000:
                                raise ValueError(
                                    "Stream dedup budget reached; restart with checkpoint"
                                )
                            seen.add(event.event_id)
                            yield event
            except (OSError, TimeoutError, ConnectionClosed, RateLimited) as exc:
                if epoch == self.max_reconnects:
                    raise RuntimeError("Stream reconnect budget exhausted") from None
                await asyncio.sleep(
                    exc.delay if isinstance(exc, RateLimited) else min(2**epoch, 30)
                )
