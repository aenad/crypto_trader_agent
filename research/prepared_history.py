"""Research-only past-visible aggregation cache; no strategy/risk overrides."""

from bisect import bisect_right

from quantpilot.backtest.history import HistoricalMarketDataProvider
from quantpilot.models import MarketConstraints, MarketSnapshot
from quantpilot.trading.timeframes import resample


class PreparedHistory(HistoricalMarketDataProvider):
    def __init__(self, original):
        super().__init__(
            original.candles,
            original.markets,
            original.research,
            original.simulation,
            original.quotes,
            original.fx_market,
        )
        self.prepared = {}
        self.prepared_times = {}
        for pair, source in self.published.items():
            for interval in {self.research.entry_seconds, self.research.trend_seconds}:
                rows = resample(source, interval, source[-1].close_time)
                self.prepared[pair, interval] = rows
                self.prepared_times[pair, interval] = [c.close_time for c in rows]

    async def snapshot(self, symbol, as_of):
        # Future aggregations exist in memory but cannot enter any snapshot.
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
        if liquidity is None and visible:
            liquidity = self.proxy(visible[-1].close, visible[-1].volume, as_of)

        def prefix(interval):
            key = symbol, interval
            return self.prepared[key][: bisect_right(self.prepared_times[key], as_of)]

        return MarketSnapshot(
            symbol=symbol,
            as_of=as_of,
            source=source,
            market=market,
            liquidity=liquidity,
            candles=prefix(self.research.entry_seconds),
            trend_candles=prefix(self.research.trend_seconds),
        )
