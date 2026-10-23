from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BeforeValidator, Field

from quantpilot.models import DomainModel, exact_decimal

Number = Annotated[Decimal, BeforeValidator(exact_decimal), Field(allow_inf_nan=False)]
Kind = Literal["DEMO", "BACKTEST", "SHADOW", "LIVE"]


class RunEntry(DomainModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")
    title: str = Field(min_length=1, max_length=100)
    kind: Literal["BACKTEST", "SHADOW", "LIVE"]
    path: str
    replay: str | None = None
    comparison: str | None = None
    health: str | None = None
    analyst_traces: str | None = None


class Source(DomainModel):
    id: str
    title: str
    kind: Kind
    simulated: bool
    label: str
    as_of: datetime | None = None
    content_id: str
    stale: bool = False


class Metrics(DomainModel):
    initial_capital_tmn: Number | None = None
    equity_tmn: Number | None = None
    realized_pnl_tmn: Number | None = None
    net_return_pct: Number | None = None
    max_drawdown_pct: Number | None = None
    win_rate_pct: Number | None = None
    fees_tmn: Number | None = None
    trade_count: int | None = None


class EquityPoint(DomainModel):
    at: datetime
    equity_tmn: Number
    drawdown_pct: Number


class MarketRow(DomainModel):
    symbol: str
    status: str
    action: str
    as_of: datetime | None = None
    reasons: tuple[str, ...] = ()


class AIRow(DomainModel):
    symbol: str
    as_of: datetime | None = None
    score: Annotated[Number, Field(ge=0, le=1)] | None = None
    assessment: str = "NOT_RECORDED"
    fusion: str = "NOT_RECORDED"
    model_version: str | None = None
    prompt_version: str | None = None
    analyst_model_version: str | None = None


class OrderRow(DomainModel):
    id: str
    symbol: str
    side: str
    state: str
    quantity: Number
    filled_quantity: Number | None = None
    at: datetime | None = None
    latency_ms: Number | None = None


class FillRow(DomainModel):
    id: str
    order_id: str
    symbol: str
    side: str
    quantity: Number
    price: Number
    fee: Number
    fee_currency: str
    at: datetime


class Rejection(DomainModel):
    symbol: str
    at: datetime | None = None
    reasons: tuple[str, ...]


class DayRow(DomainModel):
    day: str
    pnl_tmn: Number
    decisions: int
    fills: int


class ComparisonRow(DomainModel):
    variant: str
    net_return_pct: Number | None = None
    max_drawdown_pct: Number | None = None
    trades: int = 0
    fees_tmn: Number | None = None


class EvidenceRow(DomainModel):
    name: str
    status: str
    detail: str


class DashboardView(DomainModel):
    schema_version: Literal["dashboard-v1"] = "dashboard-v1"
    source: Source
    generated_at: datetime
    metrics: Metrics
    equity: tuple[EquityPoint, ...] = ()
    markets: tuple[MarketRow, ...] = ()
    ai: tuple[AIRow, ...] = ()
    orders: tuple[OrderRow, ...] = ()
    fills: tuple[FillRow, ...] = ()
    rejections: tuple[Rejection, ...] = ()
    daily: tuple[DayRow, ...] = ()
    comparison: tuple[ComparisonRow, ...] = ()
    evidence: tuple[EvidenceRow, ...] = ()
    health: tuple[EvidenceRow, ...] = ()
    limitations: tuple[str, ...] = ()
    strategy: str = (
        "Baseline design: completed-candle Momentum Breakout; inspect recorded run parameters."
    )
    risk_policy: str = (
        "Deterministic sizing, exposure, loss and drawdown gates; inspect run settings."
    )
    ai_contribution: str = (
        "Unmeasured: recorded predictions alone do not establish incremental benefit."
    )
