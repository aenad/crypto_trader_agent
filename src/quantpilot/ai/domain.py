from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, Field, model_validator

from quantpilot.config import stable_id
from quantpilot.models import Amount, DomainModel, exact_decimal

Number = Annotated[Decimal, BeforeValidator(exact_decimal), Field(allow_inf_nan=False)]


class FeatureVector(DomainModel):
    entry_ema_gap: Number
    trend_ema_gap: Number
    rsi: Number
    atr_fraction: Number
    adx: Number
    relative_volume: Number
    breakout_fraction: Number
    trend_adx: Number
    trend_atr_fraction: Number
    spread: Number
    depth_imbalance: Number
    hour_utc: Number

    @classmethod
    def names(cls) -> tuple[str, ...]:
        return tuple(cls.model_fields)

    def numbers(self) -> list[float]:
        # Floating point is confined to statistical ML, never portfolio accounting.
        return [float(getattr(self, name)) for name in self.names()]


class Sample(DomainModel):
    sample_id: str
    symbol: str
    as_of: datetime
    label_end: datetime
    snapshot_id: str
    features: FeatureVector
    positive: Literal[0, 1]
    net_return: Number
    net_pnl_tmn: Number

    @model_validator(mode="after")
    def valid_label(self) -> Self:
        if self.label_end <= self.as_of or self.positive != int(self.net_pnl_tmn > 0):
            raise ValueError("Invalid label interval or sign")
        return self


class LearningConfig(DomainModel):
    label_bars: int = Field(default=6, ge=1, le=288)
    embargo_seconds: int = Field(default=900, ge=0)
    rounds: int = Field(default=40, ge=1, le=1000)
    num_leaves: int = Field(default=7, ge=2, le=64)
    min_data_in_leaf: int = Field(default=10, ge=2)
    seed: int = 173
    minimum_train: int = Field(default=100, ge=10)
    minimum_validation: int = Field(default=30, ge=5)
    minimum_test: int = Field(default=30, ge=5)
    probability_threshold: Amount = Field(default=Decimal("0.55"), le=1)
    minimum_promotion_trades: int = Field(default=30, ge=10)

    @property
    def config_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


class Prediction(DomainModel):
    model_version: str
    feature_schema: Literal["phase5-features-v1"] = "phase5-features-v1"
    as_of: datetime
    features: FeatureVector
    raw_probability: Amount = Field(le=1)
    probability: Amount = Field(le=1)
    quality: Literal["LOW", "HIGH"]
    research_only: Literal[True] = True


class ContextBar(DomainModel):
    close_time: datetime
    close: Amount
    high: Amount
    low: Amount
    volume: Amount


class AnalystContext(DomainModel):
    version: Literal["analyst-context-v1"] = "analyst-context-v1"
    symbol: str = Field(pattern=r"^[A-Z0-9]+/(TMN|USDT)$")
    as_of: datetime
    snapshot_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    features: FeatureVector
    bars: tuple[ContextBar, ...] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def past_only(self) -> Self:
        times = tuple(b.close_time for b in self.bars)
        if times != tuple(sorted(set(times))) or times[-1] > self.as_of:
            raise ValueError("Future or unordered LLM context")
        return self

    @property
    def context_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


Reason = Literal[
    "TREND_SUPPORTED",
    "HIGH_VOLATILITY",
    "LOW_LIQUIDITY",
    "WEAK_MOMENTUM",
    "INSUFFICIENT_CONTEXT",
    "CONTEXT_CONSISTENT",
]


class AnalystOutput(DomainModel):
    context_id: str = Field(pattern=r"^[a-f0-9]{64}$")
    as_of: datetime
    assessment: Literal["ACCEPT", "VETO", "ABSTAIN"]
    confidence: int = Field(strict=True, ge=0, le=100)
    reason_codes: tuple[Reason, ...] = Field(min_length=1, max_length=6)


class CandidateRecommendation(DomainModel):
    policy_version: Literal["veto-only-v1"] = "veto-only-v1"
    signal_id: str
    symbol: str
    as_of: datetime
    action: Literal["BUY", "SELL", "HOLD"]
    verdict: Literal["ACCEPT", "REJECT", "ABSTAIN"]
    reasons: tuple[str, ...]
    prediction: Prediction | None = None
    analyst: AnalystOutput | None = None
    analyst_trace_id: str | None = None
    authorized_to_trade: Literal[False] = False
