"""Observation-only orchestration shared across all configured modes."""

from .config import EngineConfig, ExecutionMode, stable_id
from .interfaces import (
    Clock,
    DecisionRepository,
    EventBus,
    ExecutionProvider,
    MarketDataProvider,
    PortfolioRepository,
    RiskManager,
    SignalEvaluator,
    Strategy,
)
from .models import DecisionRecord


class TradingEngine:
    def __init__(
        self,
        config: EngineConfig,
        clock: Clock,
        data: MarketDataProvider,
        portfolios: PortfolioRepository,
        strategy: Strategy,
        evaluator: SignalEvaluator,
        risk: RiskManager,
        decisions: DecisionRepository,
        bus: EventBus,
        execution: ExecutionProvider | None = None,
    ):
        self.config = config
        self.clock = clock
        self.data = data
        self.portfolios = portfolios
        self.strategy = strategy
        self.evaluator = evaluator
        self.risk = risk
        self.decisions = decisions
        self.bus = bus
        self.execution = execution  # Contract injection only; never submitted in Phase 1.

    async def observe(self, symbol: str, account_id: str) -> DecisionRecord:
        if self.config.mode == ExecutionMode.LIVE:
            raise RuntimeError("LIVE runs disabled in Phase 1")
        now = self.clock.now()
        snapshot = await self.data.snapshot(symbol, now)
        portfolio = await self.portfolios.load(account_id)
        if snapshot.symbol != symbol or snapshot.as_of != now:
            raise ValueError("Snapshot identity or as-of mismatch")
        if portfolio.account_id != account_id or portfolio.as_of > now:
            raise ValueError("Account identity or as-of mismatch")
        signal = self.strategy.evaluate(snapshot, portfolio)
        if signal.symbol != symbol or signal.as_of != now:
            raise ValueError("Signal identity or as-of mismatch")
        if signal.strategy_version != self.config.strategy_version:
            raise ValueError("Strategy version mismatch")
        analysis = await self.evaluator.evaluate(signal, snapshot)
        risk = self.risk.check(signal, portfolio)
        snapshot_id = stable_id(snapshot.model_dump(mode="json"))
        decision_id = stable_id(
            {
                "config": self.config.config_id,
                "snapshot": snapshot_id,
                "portfolio": portfolio.model_dump(mode="json"),
                "signal": signal.model_dump(mode="json"),
                "analysis": analysis.model_dump(mode="json"),
                "risk": risk.model_dump(mode="json"),
            }
        )
        record = DecisionRecord(
            decision_id=decision_id,
            config_id=self.config.config_id,
            snapshot_id=snapshot_id,
            account_id=account_id,
            as_of=now,
            signal=signal,
            analysis=analysis,
            risk=risk,
        )
        await self.decisions.append(record)
        if risk.halt_new_entries and not portfolio.risk_halted:
            # Persist the circuit breaker explicitly. No automatic daily/manual reset.
            await self.portfolios.save(portfolio.model_copy(update={"risk_halted": True}))
        await self.bus.publish(record)
        return record
