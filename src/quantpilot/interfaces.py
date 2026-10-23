"""Ports for a single core; implementations must live outside business logic."""

from datetime import datetime
from typing import Protocol

from .models import (
    AIAnalysis,
    DecisionRecord,
    Fill,
    MarketEvent,
    MarketSnapshot,
    OrderIntent,
    OrderState,
    PortfolioState,
    RiskDecision,
    Signal,
)


class Clock(Protocol):
    def now(self) -> datetime: ...


class MarketDataProvider(Protocol):
    async def snapshot(self, symbol: str, as_of: datetime) -> MarketSnapshot: ...


class ExecutionProvider(Protocol):
    async def submit(self, intent: OrderIntent) -> OrderState: ...
    async def lookup(self, client_id: str) -> OrderState: ...
    async def cancel(self, client_id: str) -> OrderState: ...
    async def fills(self, client_id: str) -> tuple[Fill, ...]: ...


class Strategy(Protocol):
    def evaluate(self, snapshot: MarketSnapshot, portfolio: PortfolioState) -> Signal: ...


class SignalEvaluator(Protocol):
    async def evaluate(self, signal: Signal, snapshot: MarketSnapshot) -> AIAnalysis: ...


class RiskManager(Protocol):
    def check(self, signal: Signal, portfolio: PortfolioState) -> RiskDecision: ...


class PortfolioRepository(Protocol):
    async def load(self, account_id: str) -> PortfolioState: ...
    async def save(self, state: PortfolioState) -> None: ...


class DecisionRepository(Protocol):
    async def append(self, record: DecisionRecord) -> None: ...


class EventBus(Protocol):
    async def publish(self, event: MarketEvent | DecisionRecord) -> None: ...
