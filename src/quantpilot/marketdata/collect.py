"""Collection services independent of transport and persistence."""

from datetime import datetime, timedelta
from typing import Any, Protocol

from quantpilot.models import Candle, MarketSnapshot

from . import normalize
from .domain import Book, CollectionPolicy, Market, Trade, canonical_pair


class PublicSource(Protocol):
    source: str

    async def request(self, kind: str, args: dict[str, Any]) -> Any: ...


class MarketScanner:
    def __init__(self, source: PublicSource, policy: CollectionPolicy):
        self.source, self.policy = source, policy

    async def scan(self) -> list[Market]:
        return [
            m
            for m in normalize.markets(await self.source.request("markets", {}))
            if m.spot and m.symbol in self.policy.approved and m.symbol not in self.policy.excluded
        ]


class Collectors:
    def __init__(self, source: PublicSource, policy: CollectionPolicy):
        self.source, self.policy = source, policy

    def permit(self, pair: str) -> str:
        canonical_pair(pair)
        if pair not in self.policy.approved or pair in self.policy.excluded:
            raise ValueError("Market not competition-whitelisted")
        return pair.replace("/", "")

    async def candles(
        self, pair: str, resolution: str, start: datetime, end: datetime, now: datetime
    ) -> list[Candle]:
        wire = self.permit(pair)
        if any(t.tzinfo is None for t in (start, end, now)):
            raise ValueError("Timezone-aware range required")
        seconds = normalize.RESOLUTIONS[resolution]
        if start >= end or end > now:
            raise ValueError("Invalid range or incomplete end candle")
        if int(start.timestamp()) % seconds or int(end.timestamp()) % seconds:
            raise ValueError("Range must align to candle boundaries")
        rows = []
        cursor = start
        while cursor < end:
            stop = min(end, cursor + timedelta(seconds=seconds * self.policy.chunk_bars))
            payload = await self.source.request(
                "candles",
                {
                    "symbol": wire,
                    "resolution": resolution,
                    "from": int(cursor.timestamp()),
                    "to": int(stop.timestamp()) - 1,
                },
            )
            batch = normalize.candles(payload, pair, resolution, now, cursor, stop)
            normalize.validate_coverage(batch, cursor, stop, seconds)
            rows.extend(batch)
            cursor = stop
        return rows

    async def recent_trades(self, pair: str, now: datetime) -> list[Trade]:
        rows = normalize.recent_trades(
            await self.source.request("trades", {"symbol": self.permit(pair)}), pair, now
        )
        if not rows or (now - rows[-1].event_time).total_seconds() > self.policy.freshness_seconds:
            raise ValueError("Latest trade is stale or missing")
        return rows

    async def order_book(self, pair: str, now: datetime) -> Book:
        return normalize.book(
            await self.source.request("book", {"symbol": self.permit(pair)}), pair, now
        )


class HistoricalDataLoader:
    def __init__(self, collectors: Collectors):
        self.collectors = collectors

    async def load(
        self, pair: str, resolution: str, start: datetime, end: datetime, now: datetime
    ) -> list[Candle]:
        return await self.collectors.candles(pair, resolution, start, end, now)


class CandleCollector:
    """Implements the Phase 1 MarketDataProvider with closed candles."""

    def __init__(self, collectors: Collectors, resolution: str = "1", bars: int = 60):
        self.collectors, self.resolution, self.bars = collectors, resolution, bars

    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        seconds = normalize.RESOLUTIONS[self.resolution]
        end = datetime.fromtimestamp(int(as_of.timestamp()) // seconds * seconds, as_of.tzinfo)
        start = end - timedelta(seconds=seconds * self.bars)
        rows = await self.collectors.candles(symbol, self.resolution, start, end, as_of)
        return MarketSnapshot(
            symbol=symbol, as_of=as_of, candles=tuple(rows), source=self.collectors.source.source
        )


class OrderBookCollector:
    def __init__(self, collectors: Collectors):
        self.collectors = collectors

    async def collect(self, pair: str, now: datetime) -> Book:
        return await self.collectors.order_book(pair, now)


class RecentTradesCollector:
    def __init__(self, collectors: Collectors):
        self.collectors = collectors

    async def collect(self, pair: str, now: datetime) -> list[Trade]:
        return await self.collectors.recent_trades(pair, now)
