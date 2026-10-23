from decimal import Decimal
from typing import Self

from pydantic import Field, model_validator

from quantpilot.config import stable_id
from quantpilot.models import Amount, DomainModel, PositiveAmount


class ResearchParameters(DomainModel):
    version: str = "momentum_breakout_v1"
    entry_seconds: int = Field(default=300, ge=60)
    trend_seconds: int = Field(default=900, ge=60)
    ema_fast: int = Field(default=50, ge=2)
    ema_slow: int = Field(default=200, ge=3)
    rsi_period: int = Field(default=14, ge=2)
    atr_period: int = Field(default=14, ge=2)
    adx_period: int = Field(default=14, ge=2)
    breakout_window: int = Field(default=20, ge=2)
    volume_window: int = Field(default=20, ge=2)
    rsi_min: Amount = Decimal("50")
    rsi_max: Amount = Decimal("70")
    min_relative_volume: PositiveAmount = Decimal("1.2")
    min_adx: Amount = Decimal("20")
    max_atr_fraction: PositiveAmount = Decimal("0.05")
    max_spread: PositiveAmount = Decimal("0.003")
    depth_band: PositiveAmount = Decimal("0.0025")
    stop_atr: PositiveAmount = Decimal("2")
    target_atr: PositiveAmount = Decimal("3")
    max_hold_seconds: int = Field(default=86400, ge=1)
    max_candle_lag_seconds: int = Field(default=60, ge=0)

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.ema_fast >= self.ema_slow or not 0 <= self.rsi_min < self.rsi_max <= 100:
            raise ValueError("Invalid EMA/RSI parameters")
        if self.trend_seconds < self.entry_seconds or self.trend_seconds % self.entry_seconds:
            raise ValueError("Trend interval must be an entry interval multiple")
        return self

    @property
    def parameters_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


class RiskParameters(DomainModel):
    max_order_equity_fraction: PositiveAmount = Field(default=Decimal("0.10"), le=1)
    absolute_order_hard_cap_tmn: PositiveAmount | None = Decimal("500000")
    version: str = "deterministic_risk_v1"
    risk_per_trade: PositiveAmount = Field(default=Decimal("0.005"), le=Decimal("0.005"))
    max_positions: int = Field(default=2, ge=1)
    max_asset_fraction: PositiveAmount = Field(default=Decimal("0.10"), le=1)
    max_exposure_fraction: PositiveAmount = Field(default=Decimal("0.20"), le=1)
    max_open_risk_fraction: PositiveAmount = Field(default=Decimal("0.01"), le=1)
    daily_loss_fraction: PositiveAmount = Field(default=Decimal("0.03"), le=1)
    max_drawdown_fraction: PositiveAmount = Field(default=Decimal("0.05"), le=1)
    max_spread: PositiveAmount = Field(default=Decimal("0.003"), le=1)
    slippage_fraction: Amount = Field(default=Decimal("0.001"), le=Decimal("0.10"))
    max_depth_participation: PositiveAmount = Field(default=Decimal("0.05"), le=1)
    min_net_reward_risk: PositiveAmount = Decimal("1")
    max_entry_drift: PositiveAmount = Decimal("0.005")
    max_snapshot_age_seconds: int = Field(default=30, ge=0)
    max_fx_age_seconds: int = Field(default=60, ge=0)

    @property
    def parameters_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))
