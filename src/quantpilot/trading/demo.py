"""Offline Phase 3 research wiring with explicit synthetic account/market data."""

import argparse
import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from quantpilot.config import EngineConfig
from quantpilot.demo import (
    AbstainingEvaluator,
    InMemoryEventBus,
    MemoryDecisionRepository,
    MemoryPortfolioRepository,
)
from quantpilot.engine import TradingEngine
from quantpilot.models import (
    AssetBalance,
    Candle,
    DepthLevel,
    LiquiditySnapshot,
    MarketConstraints,
    MarketSnapshot,
    PortfolioState,
    QuoteConversion,
)

from .config import ResearchParameters, RiskParameters
from .risk import DeterministicRiskEngine
from .strategy import MarketEligibilityFilter, MomentumBreakout

D = Decimal
NOW = datetime(2026, 10, 23, 10, tzinfo=timezone.utc)
PAIR = "BTC/USDT"


def synthetic_context(
    parameters: ResearchParameters | None = None,
) -> tuple[MarketSnapshot, PortfolioState]:
    p = parameters or ResearchParameters()
    count = max(
        220,
        p.ema_slow + 20,
        2 * p.adx_period + 5,
        p.breakout_window + 5,
        p.volume_window + 5,
        p.rsi_period + 5,
        p.atr_period + 5,
    )

    def series(seconds: int, noisy: bool) -> tuple[Candle, ...]:
        rows = []
        for i in range(count):
            price = D(100) + D(i) / D(10)
            if noisy:
                price += D(1) if i % 2 == 0 else D(-1)
                if i == count - 1:
                    price = D(100) + D(count - 2) / D(10) + D("1.5")
            closed = NOW - timedelta(seconds=seconds * (count - i - 1))
            rows.append(
                Candle(
                    event_id=f"synthetic-{seconds}-{i}",
                    symbol=PAIR,
                    event_time=closed,
                    received_at=closed,
                    source="synthetic",
                    open_time=closed - timedelta(seconds=seconds),
                    close_time=closed,
                    open=price,
                    high=price + D("0.1"),
                    low=price - D("0.1"),
                    close=price,
                    volume=D(20) if i == count - 1 else D(10),
                    closed=True,
                )
            )
        return tuple(rows)

    entry = series(p.entry_seconds, True)
    price = entry[-1].close
    snapshot = MarketSnapshot(
        symbol=PAIR,
        as_of=NOW,
        candles=entry,
        trend_candles=series(p.trend_seconds, False),
        source="synthetic",
        market=MarketConstraints(
            symbol=PAIR,
            quote="USDT",
            spot_enabled=True,
            account_enabled=True,
            quantity_step=D("0.001"),
            price_tick=D("0.01"),
            minimum_quantity=D("0.001"),
            minimum_notional=D(5),
            taker_fee_rate=D("0.001"),
        ),
        liquidity=LiquiditySnapshot(
            as_of=NOW,
            bids=(DepthLevel(price=price - D("0.01"), quantity=D(10000)),),
            asks=(DepthLevel(price=price + D("0.01"), quantity=D(10000)),),
        ),
    )
    portfolio = PortfolioState(
        account_id="research-demo",
        as_of=NOW,
        balances=(
            AssetBalance(currency="USDT", free=D(10000), reserved=D(0)),
            AssetBalance(currency="BTC", free=D(0), reserved=D(0)),
        ),
        equity_tmn=D(5000000),
        daily_open_equity_tmn=D(5000000),
        peak_equity_tmn=D(5000000),
        trading_day=NOW.astimezone(ZoneInfo("Asia/Tehran")).date(),
        conversions=(QuoteConversion(quote="USDT", tmn_per_unit=D(1000), as_of=NOW),),
    )
    return snapshot, portfolio


class SyntheticSource:
    def __init__(self, context: MarketSnapshot):
        self.context = context

    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        return self.context


class SyntheticClock:
    def now(self) -> datetime:
        return NOW


async def research_demo(parameters: ResearchParameters, limits: RiskParameters) -> str:
    snapshot, portfolio = synthetic_context(parameters)
    eligibility = MarketEligibilityFilter({PAIR})
    engine = TradingEngine(
        EngineConfig(strategy_version=parameters.version),
        SyntheticClock(),
        SyntheticSource(snapshot),
        MemoryPortfolioRepository(portfolio),
        MomentumBreakout(parameters, eligibility),
        AbstainingEvaluator(),
        DeterministicRiskEngine(
            limits, parameters, eligibility, {PAIR: snapshot}, {portfolio.account_id}
        ),
        MemoryDecisionRepository(),
        InMemoryEventBus(),
    )
    result = await engine.observe(PAIR, portfolio.account_id)
    return result.model_dump_json(indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 3 synthetic strategy/risk research; no orders"
    )
    parser.add_argument("--parameters", type=Path)
    parser.add_argument("--risk", type=Path)
    args = parser.parse_args()
    parameters = (
        ResearchParameters.model_validate_json(args.parameters.read_text(encoding="utf-8"))
        if args.parameters
        else ResearchParameters()
    )
    limits = (
        RiskParameters.model_validate_json(args.risk.read_text(encoding="utf-8"))
        if args.risk
        else RiskParameters()
    )
    print(asyncio.run(research_demo(parameters, limits)))


if __name__ == "__main__":
    main()
