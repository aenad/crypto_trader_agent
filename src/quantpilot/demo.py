"""Network-free wiring demo; placeholders are not a strategy or simulator."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from .config import EngineConfig, stable_id
from .engine import TradingEngine
from .logging import JsonFormatter, log_decision
from .models import (
    AIAnalysis,
    AssetBalance,
    Candle,
    DecisionRecord,
    MarketEvent,
    MarketSnapshot,
    PortfolioState,
    RiskDecision,
    Signal,
)


class FixedClock:
    def now(self) -> datetime:
        return datetime(2026, 10, 22, 10, 0, tzinfo=timezone.utc)


class MockMarketData:
    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot:
        candle = Candle(
            event_id="demo-candle-1",
            symbol=symbol,
            event_time=as_of,
            received_at=as_of,
            source="synthetic",
            open_time=as_of - timedelta(minutes=15),
            close_time=as_of,
            open=Decimal("100"),
            high=Decimal("102"),
            low=Decimal("99"),
            close=Decimal("101"),
            volume=Decimal("2"),
            closed=True,
        )
        return MarketSnapshot(symbol=symbol, as_of=as_of, candles=(candle,), source="synthetic")


class MemoryPortfolioRepository:
    def __init__(self, state: PortfolioState):
        self.state = state

    async def load(self, account_id: str) -> PortfolioState:
        if self.state.account_id != account_id:
            raise KeyError(account_id)
        return self.state

    async def save(self, state: PortfolioState) -> None:
        self.state = state


class MemoryDecisionRepository:
    def __init__(self) -> None:
        self.records: dict[str, DecisionRecord] = {}

    async def append(self, record: DecisionRecord) -> None:
        existing = self.records.get(record.decision_id)
        if existing is not None and existing != record:
            raise ValueError("Conflicting decision identity")
        self.records[record.decision_id] = record


class InMemoryEventBus:
    """Single-process collection adapter; not a durable delivery guarantee."""

    def __init__(self) -> None:
        self.events: list[MarketEvent | DecisionRecord] = []

    async def publish(self, event: MarketEvent | DecisionRecord) -> None:
        self.events.append(event)


class PlaceholderStrategy:
    def evaluate(self, snapshot: MarketSnapshot, portfolio: PortfolioState) -> Signal:
        return Signal(
            symbol=snapshot.symbol,
            action="HOLD",
            strategy_version="phase1-placeholder",
            as_of=snapshot.as_of,
            reasons=("No strategy implemented in Phase 1",),
        )


class AbstainingEvaluator:
    async def evaluate(self, signal: Signal, snapshot: MarketSnapshot) -> AIAnalysis:
        return AIAnalysis(
            model_version="none",
            input_id=stable_id(snapshot.model_dump(mode="json")),
            verdict="ABSTAIN",
            reasons=("No AI implemented in Phase 1",),
        )


class DenyAllRisk:
    def check(self, signal: Signal, portfolio: PortfolioState) -> RiskDecision:
        return RiskDecision(allowed=False, reasons=("Execution disabled in Phase 1",))


def make_demo(config: EngineConfig | None = None) -> TradingEngine:
    clock = FixedClock()
    portfolio = PortfolioState(
        account_id="offline-demo",
        as_of=clock.now(),
        balances=(AssetBalance(currency="TMN", free=Decimal("5000000"), reserved=Decimal("0")),),
    )
    return TradingEngine(
        config or EngineConfig(),
        clock,
        MockMarketData(),
        MemoryPortfolioRepository(portfolio),
        PlaceholderStrategy(),
        AbstainingEvaluator(),
        DenyAllRisk(),
        MemoryDecisionRepository(),
        InMemoryEventBus(),
    )


async def run_demo() -> None:
    result = await make_demo(EngineConfig.from_env()).observe("BTC/USDT", "offline-demo")
    logger = logging.getLogger("quantpilot.demo")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    log_decision(logger, result)
    print(result.model_dump_json(indent=2))


def main() -> None:
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
