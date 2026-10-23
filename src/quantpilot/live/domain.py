"""Explicit activation and execution evidence; no environment loading at import time."""

import hashlib
from datetime import datetime
from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator

from quantpilot.config import stable_id
from quantpilot.marketdata.domain import canonical_pair
from quantpilot.models import (
    Amount,
    DomainModel,
    Fill,
    MarketConstraints,
    OrderIntent,
    OrderState,
    PositiveAmount,
)
from quantpilot.spot import SpotPolicy
from quantpilot.trading.config import ResearchParameters, RiskParameters


class Blocked(RuntimeError):
    """A fixed safe reason code, never an exchange body or credential."""


class LiveConfig(DomainModel):
    trading: SpotPolicy = SpotPolicy()
    enabled: bool = False
    account_id: str = Field(min_length=1)
    approved: tuple[str, ...] = Field(min_length=1)
    markets: tuple[MarketConstraints, ...] = Field(min_length=1)
    capital_tmn: PositiveAmount = Decimal("5000000")
    max_order_tmn: PositiveAmount
    deadline: datetime
    liquidation_seconds: int = Field(default=300, ge=1)
    max_age_seconds: int = Field(default=10, ge=1, le=30)
    max_fee_rate: Amount = Field(default=Decimal("0.005"), lt=1)
    max_depth_fraction: PositiveAmount = Field(default=Decimal("0.05"), le=1)
    max_slippage: Amount = Field(default=Decimal("0.001"), le=Decimal("0.01"))
    research: ResearchParameters = ResearchParameters()
    risk: RiskParameters = RiskParameters()

    @model_validator(mode="after")
    def valid(self) -> Self:
        import json
        from importlib.resources import files

        excluded = set(
            json.loads(files("quantpilot.marketdata").joinpath("excluded.json").read_text())
        )
        for symbol in self.approved:
            canonical_pair(symbol)
        if len(set(self.approved)) != len(self.approved) or set(self.approved) & excluded:
            raise ValueError("Duplicate or excluded approved market")
        if {m.symbol for m in self.markets} != set(self.approved):
            raise ValueError("Explicit market constraints required for every approved market")
        if len(self.markets) != len(self.approved) or self.max_order_tmn > self.capital_tmn:
            raise ValueError("Invalid market list or budget")
        # Protected initial deployment uses direct Toman settlement only. Do not guess FX routing.
        if any(m.quote != "TMN" for m in self.markets):
            raise ValueError("Protected live settlement currently requires direct TMN markets")
        if any(not m.symbol.endswith("/TMN") for m in self.markets):
            raise ValueError("Market symbol and quote must agree")
        return self

    @property
    def config_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))


class AccountAuthorization(DomainModel):
    """Separate operator evidence, NOT an invented exchange introspection response."""

    config_id: str
    account_id: str
    account_type: Literal["MAIN_SPOT"]
    credential_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    evidence_reference: str = Field(min_length=1)
    spot_read: bool
    spot_trade: bool
    withdrawal_disabled: bool
    # Official docs do not unambiguously define whether value includes locked assets.
    balance_value_semantics: Literal["FREE", "TOTAL"]
    valid_from: datetime
    expires_at: datetime

    @model_validator(mode="after")
    def interval(self) -> Self:
        if self.expires_at <= self.valid_from:
            raise ValueError("Invalid authorization validity")
        return self


def credential_fingerprint(secret: SecretStr) -> str:
    return hashlib.sha256(secret.get_secret_value().encode()).hexdigest()


class ExchangeOrder(DomainModel):
    state: OrderState
    executed_quantity: Amount
    executed_sum: Amount
    fills: tuple[Fill, ...]


class OrderRecord(DomainModel):
    intent: OrderIntent
    state: OrderState = OrderState.CREATED
    phase: Literal["PREPARED", "SUBMITTING", "OBSERVED", "CANCELING", "UNCERTAIN"] = "PREPARED"
    atr: PositiveAmount
    updated_at: datetime
    executed_quantity: Amount = Decimal(0)
    executed_sum: Amount = Decimal(0)
    fills: tuple[Fill, ...] = ()
    purpose: Literal["STRATEGY", "FINAL_LIQUIDATION"] = "STRATEGY"


TERMINAL = frozenset({OrderState.FILLED, OrderState.CANCELED, OrderState.REJECTED})
