from decimal import Decimal

from pydantic import Field

from quantpilot.config import stable_id
from quantpilot.models import Amount, PositiveAmount
from quantpilot.profiles import ProfileConfig
from quantpilot.spot import SpotPolicy


class SimulationParameters(ProfileConfig):
    trading: SpotPolicy = SpotPolicy()
    initial_capital_tmn: PositiveAmount = Decimal("5000000")
    entry_fee: Amount = Field(default=Decimal("0.001"), le=Decimal("0.1"))
    exit_fee: Amount = Field(default=Decimal("0.001"), le=Decimal("0.1"))
    half_spread: PositiveAmount = Field(default=Decimal("0.0005"), lt=Decimal("0.1"))
    slippage: Amount = Field(default=Decimal("0.001"), le=Decimal("0.1"))
    volume_participation: PositiveAmount = Field(default=Decimal("0.01"), le=1)
    book_participation: PositiveAmount = Field(default=Decimal("0.10"), le=1)
    order_ttl_seconds: int = Field(default=900, ge=1)
    limit_penetration_ticks: int = Field(default=1, ge=1)
    terminal_haircut: Amount = Field(default=Decimal("0.002"), le=Decimal("0.1"))
    fx_fee: Amount = Field(default=Decimal("0.001"), le=Decimal("0.1"))
    quote_funding_fraction: Amount = Field(default=Decimal("0.25"), le=1)
    max_quote_age_seconds: int = Field(default=30, ge=0)
    max_fx_age_seconds: int = Field(default=60, ge=0)

    @property
    def config_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))
