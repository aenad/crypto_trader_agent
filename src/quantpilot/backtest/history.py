from bisect import bisect_right
from datetime import datetime
from decimal import Decimal

from quantpilot.models import (
    Candle,
    DepthLevel,
    LiquiditySnapshot,
    MarketConstraints,
    MarketSnapshot,
)
from quantpilot.trading.config import ResearchParameters
from quantpilot.trading.timeframes import resample

from .config import SimulationParameters


class HistoricalClock:
    def __init__(self, initial: datetime):
        if initial.tzinfo is None:
            raise ValueError("Aware clock required")
        self._now = initial

    def now(self) -> datetime:
        return self._now

    def advance(self, now: datetime) -> None:
        if now.tzinfo is None or now < self._now:
            raise ValueError("Historical clock cannot move backwards")
        self._now = now


class HistoricalMarketDataProvider:
    def __init__(
        self,
        candles: dict[str, tuple[Candle, ...]],
        markets: dict[str, MarketConstraints],
        research: ResearchParameters,
        simulation: SimulationParameters,
        quotes: dict[str, tuple[LiquiditySnapshot, ...]] | None = None,
        fx_market: MarketConstraints | None = None,
    ):
        self.candles, self.markets = candles, markets
        self.research, self.simulation = research, simulation
        self.quotes = quotes or {}
        self.fx_market = fx_market
        if fx_market is not None and (
            fx_market.symbol != "USDT/TMN" or fx_market.quote != "TMN"
        ):
            raise ValueError("Explicit spot USDT/TMN settlement route required")
        if not candles:
            raise ValueError("Nonempty historical universe required")
        # A base asset may have only one pricing/execution route in a run.
        # Cross-quote routing and basis allocation require a separate policy.
        if len({p.split("/")[0] for p in candles}) != len(candles):
            raise ValueError("Multiple quote routes for the same base are unsupported")
        if any(p.split("/")[0] in ("USDT", "TMN", "IRR") for p in candles):
            raise ValueError("Quote funding uses explicit FX history, not a strategy market")
        bounds = {(rows[0].open_time, rows[-1].close_time) for rows in candles.values() if rows}
        if len(bounds) != 1:
            raise ValueError("Historical markets must share replay start/end boundaries")
        self.quote_times = {pair: [q.as_of for q in rows] for pair, rows in self.quotes.items()}
        for pair, rows in candles.items():
            if pair not in markets or not rows or markets[pair].symbol != pair:
                raise ValueError("Every nonempty history needs explicit market constraints")
            if markets[pair].quote != pair.split("/")[-1]:
                raise ValueError("Historical market quote mismatch")
            previous = None
            for row in rows:
                if row.symbol != pair or not row.closed:
                    raise ValueError("Invalid historical candle identity/completeness")
                if row.event_time != row.close_time:
                    raise ValueError(
                        "Replay requires publication at candle close; latency unsupported"
                    )
                if previous is not None and row.open_time != previous:
                    raise ValueError("Historical gaps, overlap or duplicates")
                previous = row.close_time
        for times in self.quote_times.values():
            if times != sorted(set(times)):
                raise ValueError("Historical quotes must be unique and ordered")
        self.close_times = {pair: [c.close_time for c in rows] for pair, rows in candles.items()}
        self.published = {
            pair: tuple(c.model_copy(update={"received_at": c.event_time}) for c in rows)
            for pair, rows in candles.items()
        }

    def recorded_quote(self, pair: str, now: datetime) -> LiquiditySnapshot | None:
        index = bisect_right(self.quote_times.get(pair, []), now) - 1
        if index < 0:
            return None
        book = self.quotes[pair][index]
        if (now - book.as_of).total_seconds() > self.simulation.max_quote_age_seconds:
            return None
        return book

    def proxy(self, price: Decimal, volume: Decimal, now: datetime) -> LiquiditySnapshot:
        # Assumption-only liquidity input to the unchanged risk engine, never a
        # claimed historical order book. Execution uses a separate volume cap.
        return LiquiditySnapshot(
            as_of=now,
            bids=(
                DepthLevel(
                    price=price * (1 - self.simulation.half_spread),
                    quantity=max(volume, Decimal("0.00000001")),
                ),
            ),
            asks=(
                DepthLevel(
                    price=price * (1 + self.simulation.half_spread),
                    quantity=max(volume, Decimal("0.00000001")),
                ),
            ),
        )

    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        # Download receipt times are not historical publication times. The run
        # manifest explicitly assumes publication at event/close time.
        visible = self.published[symbol][: bisect_right(self.close_times[symbol], as_of)]
        market = self.markets[symbol]
        market = MarketConstraints(
            **{
                **market.model_dump(),
                "taker_fee_rate": max(
                    market.taker_fee_rate, self.simulation.entry_fee, self.simulation.exit_fee
                ),
            }
        )
        liquidity = self.recorded_quote(symbol, as_of)
        source = "historical-recorded-quote" if liquidity else "historical-ohlcv-proxy-assumption"
        if not liquidity and visible:
            liquidity = self.proxy(visible[-1].close, visible[-1].volume, as_of)
        return MarketSnapshot(
            symbol=symbol,
            as_of=as_of,
            source=source,
            candles=resample(visible, self.research.entry_seconds, as_of) if visible else (),
            trend_candles=resample(visible, self.research.trend_seconds, as_of) if visible else (),
            market=market,
            liquidity=liquidity,
        )
