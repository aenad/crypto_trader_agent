import json
from datetime import datetime
from decimal import Decimal
from importlib.resources import files
from typing import Literal, Self

from pydantic import Field, model_validator

from quantpilot.backtest.config import SimulationParameters
from quantpilot.config import stable_id
from quantpilot.models import DomainModel, LiquiditySnapshot, MarketConstraints, MarketSnapshot
from quantpilot.profiles import ProfileConfig
from quantpilot.spot import SpotPolicy
from quantpilot.trading.config import ResearchParameters, RiskParameters


class ShadowConfig(ProfileConfig):
    trading: SpotPolicy = SpotPolicy()
    mode: Literal["SHADOW"] = "SHADOW"
    approved: tuple[str, ...] = Field(min_length=1, max_length=10)
    markets: tuple[MarketConstraints, ...]
    fx_market: MarketConstraints | None = None
    research: ResearchParameters = ResearchParameters()
    risk: RiskParameters = RiskParameters()
    simulation: SimulationParameters = SimulationParameters()
    ai_mode: Literal["QUANT_ONLY", "QUANT_ML", "QUANT_ML_LLM"] = "QUANT_ML_LLM"
    model_path: str | None = None
    analyst_model_id: str = "unconfigured"
    llm_gateway: str | None = None
    llm_timeout_seconds: int = Field(default=10, ge=1, le=60)
    llm_call_budget: int = Field(default=100, ge=1, le=10000)
    public_transport: Literal["REST", "MCP"] = "REST"
    poll_seconds: int = Field(default=15, ge=1, le=300)
    freshness_seconds: int = Field(default=20, ge=1, le=60)
    health_port: int = Field(default=8766, ge=0, le=65535)

    @model_validator(mode="after")
    def consistent(self) -> Self:
        if self.force_final_liquidation and self.deadline is None:
            raise ValueError("Shadow competition liquidation requires an explicit deadline")
        if (
            self.simulation.deadline is not None
            or self.simulation.operating_profile != "CONTINUOUS"
        ):
            raise ValueError("Configure the operating schedule only on ShadowConfig")
        if (
            len(set(self.approved)) != len(self.approved)
            or {m.symbol for m in self.markets} != set(self.approved)
            or len(self.markets) != len(self.approved)
        ):
            raise ValueError("Unique explicit constraints required for every approved market")
        if len({s.split("/")[0] for s in self.approved}) != len(self.approved):
            raise ValueError("One route per base asset required")
        excluded = set(
            json.loads(files("quantpilot.marketdata").joinpath("excluded.json").read_text())
        )
        if set(self.approved) & excluded:
            raise ValueError("Market is in the competition exclusion list")
        if any(s.split("/")[0] in ("TMN", "USDT", "IRR") for s in self.approved):
            raise ValueError("Quote assets are funding instruments, not strategy routes")
        if self.ai_mode != "QUANT_ONLY" and not self.model_path:
            raise ValueError("A frozen LightGBM artifact is required; no implicit mock AI")
        if self.freshness_seconds > self.risk.max_snapshot_age_seconds:
            raise ValueError("Shadow freshness cannot exceed risk freshness")
        if any(p.endswith("/USDT") for p in self.approved) and (
            self.fx_market is None
            or self.fx_market.symbol != "USDT/TMN"
            or self.fx_market.quote != "TMN"
        ):
            raise ValueError("USDT virtual funding requires explicit USDT/TMN constraints")
        return self

    @property
    def config_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


class ShadowFrame(DomainModel):
    as_of: datetime
    snapshots: tuple[MarketSnapshot, ...] = Field(min_length=1)
    fx_book: LiquiditySnapshot | None = None
    depth_timestamps: Literal["OBSERVATION", "EXCHANGE", "FIXTURE"] = "OBSERVATION"

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if len({s.symbol for s in self.snapshots}) != len(self.snapshots):
            raise ValueError("Duplicate snapshot pair")
        if any(s.as_of != self.as_of for s in self.snapshots):
            raise ValueError("Frame timestamps must agree")
        if self.fx_book and self.fx_book.as_of > self.as_of:
            raise ValueError("Future FX book")
        return self

    @property
    def frame_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


def age_seconds(now: datetime, then: datetime) -> Decimal:
    return Decimal(str((now - then).total_seconds()))
