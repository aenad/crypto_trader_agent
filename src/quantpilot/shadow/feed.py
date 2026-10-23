"""Polling verified public adapters; no authentication, mutation or synthetic depth."""

from datetime import datetime, timedelta, timezone
from typing import Any, Protocol

from quantpilot.interfaces import Clock
from quantpilot.marketdata import normalize
from quantpilot.marketdata.collect import PublicSource
from quantpilot.models import Candle, DepthLevel, LiquiditySnapshot, MarketSnapshot
from quantpilot.trading.timeframes import resample

from .domain import ShadowConfig, ShadowFrame


class FrameSource(Protocol):
    async def poll(self) -> ShadowFrame: ...


class WallClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)


class ReadOnlyPublic:
    """Capability wrapper in addition to transport GET/tool allowlists."""

    def __init__(self, source: PublicSource):
        self._source = source

    @property
    def source(self) -> str:
        return self._source.source

    async def request(self, kind: str, args: dict[str, Any]) -> Any:
        if kind not in ("markets", "candles", "book", "trades"):
            raise PermissionError("SHADOW_EXCHANGE_MUTATION_BLOCKED")
        return await self._source.request(kind, args)


class WallexLiveFeed:
    def __init__(self, source: PublicSource, config: ShadowConfig, clock: Clock):
        self.source, self.config, self.clock = ReadOnlyPublic(source), config, clock
        self.cache: dict[str, tuple[Candle, ...]] = {}
        self.last_scan: datetime | None = None

    async def book(self, pair: str) -> LiquiditySnapshot:
        started = self.clock.now()
        payload = await self.source.request("book", {"symbol": pair.replace("/", "")})
        now = self.clock.now()
        if (now - started).total_seconds() > self.config.freshness_seconds:
            raise ValueError("DEPTH_REQUEST_EXCEEDED_FRESHNESS_BUDGET")
        normalized = normalize.book(payload, pair, now)
        # The verified public depth endpoint lacks exchange timestamps. Keep
        # observation provenance explicit; never assert exchange freshness.
        return LiquiditySnapshot(
            as_of=normalized.event_time,
            bids=tuple(
                DepthLevel(price=level.price, quantity=level.quantity) for level in normalized.bids
            ),
            asks=tuple(
                DepthLevel(price=level.price, quantity=level.quantity) for level in normalized.asks
            ),
        )

    async def history(self, pair: str) -> tuple[Candle, ...]:
        p = self.config.research
        now = self.clock.now()
        end = datetime.fromtimestamp(int(now.timestamp()) // 60 * 60, timezone.utc)
        warmup = (
            max(
                p.ema_slow + 20,
                2 * p.adx_period + 20,
                p.volume_window + 20,
                p.breakout_window + 20,
                p.rsi_period + 20,
                p.atr_period + 20,
            )
            * p.trend_seconds
        )
        start = datetime.fromtimestamp(
            (int(end.timestamp()) - warmup) // p.trend_seconds * p.trend_seconds, timezone.utc
        )
        cached = self.cache.get(pair, ())
        cursor = cached[-1].close_time if cached else start
        if cursor < start:
            cursor = start
            cached = ()
        added = []
        while cursor < end:
            stop = min(end, cursor + timedelta(minutes=300))
            payload = await self.source.request(
                "candles",
                {
                    "symbol": pair.replace("/", ""),
                    "resolution": "1",
                    "from": int(cursor.timestamp()),
                    "to": int(stop.timestamp()) - 1,
                },
            )
            batch = normalize.candles(payload, pair, "1", self.clock.now(), cursor, stop)
            normalize.validate_coverage(batch, cursor, stop, 60)
            added.extend(batch)
            cursor = stop
        rows = tuple(c for c in cached + tuple(added) if c.open_time >= start)
        self.cache[pair] = rows
        return rows

    async def poll(self) -> ShadowFrame:
        now = self.clock.now()
        if self.last_scan is None or (now - self.last_scan).total_seconds() >= 60:
            available = {
                m.symbol
                for m in normalize.markets(await self.source.request("markets", {}))
                if m.spot
            }
            if not set(self.config.approved) <= available:
                raise ValueError("APPROVED_MARKET_UNAVAILABLE")
            self.last_scan = self.clock.now()
        histories = {pair: await self.history(pair) for pair in sorted(self.config.approved)}
        books = {pair: await self.book(pair) for pair in sorted(self.config.approved)}
        fx = (
            await self.book("USDT/TMN")
            if any(p.endswith("/USDT") for p in self.config.approved)
            else None
        )
        as_of = self.clock.now()
        markets = {m.symbol: m for m in self.config.markets}
        snapshots = []
        for pair, rows in histories.items():
            market = markets[pair].model_copy(
                update={
                    "taker_fee_rate": max(
                        markets[pair].taker_fee_rate,
                        self.config.simulation.entry_fee,
                        self.config.simulation.exit_fee,
                    )
                }
            )
            snapshots.append(
                MarketSnapshot(
                    symbol=pair,
                    as_of=as_of,
                    source=self.source.source,
                    candles=resample(rows, self.config.research.entry_seconds, as_of),
                    trend_candles=resample(rows, self.config.research.trend_seconds, as_of),
                    market=market,
                    liquidity=books[pair],
                )
            )
        return ShadowFrame(as_of=as_of, snapshots=tuple(snapshots), fx_book=fx)
