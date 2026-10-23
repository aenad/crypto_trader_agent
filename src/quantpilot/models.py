"""Immutable domain contracts. TMN is Toman; IRR is a distinct currency."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Annotated, Literal, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, field_validator, model_validator


def exact_decimal(value: object) -> object:
    if isinstance(value, (float, bool)):
        raise ValueError("Use Decimal, integer or decimal string; never float")
    return value


Amount = Annotated[Decimal, BeforeValidator(exact_decimal), Field(ge=0, allow_inf_nan=False)]
PositiveAmount = Annotated[
    Decimal, BeforeValidator(exact_decimal), Field(gt=0, allow_inf_nan=False)
]


class DomainModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    @field_validator("*", mode="after")
    @classmethod
    def aware_time(cls, value: object) -> object:
        if isinstance(value, datetime) and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Timezone-aware timestamps required")
        return value


class Money(DomainModel):
    amount: Amount
    currency: str = Field(pattern=r"^[A-Z0-9]+$")


class MarketEvent(DomainModel):
    event_id: str
    symbol: str = Field(pattern=r"^[A-Z0-9]+/(TMN|IRR|USDT)$")
    event_time: datetime
    received_at: datetime
    source: str


class Candle(MarketEvent):
    open_time: datetime
    close_time: datetime
    open: PositiveAmount
    high: PositiveAmount
    low: PositiveAmount
    close: PositiveAmount
    volume: Amount
    closed: bool

    @model_validator(mode="after")
    def valid_ohlc(self) -> Self:
        if not self.open_time < self.close_time <= self.event_time:
            raise ValueError("Invalid candle time range")
        if not self.low <= min(self.open, self.close) <= max(self.open, self.close) <= self.high:
            raise ValueError("Invalid OHLC bounds")
        return self


class MarketConstraints(DomainModel):
    symbol: str
    quote: Literal["TMN", "USDT"]
    spot_enabled: bool
    account_enabled: bool
    quantity_step: PositiveAmount
    price_tick: PositiveAmount
    minimum_quantity: PositiveAmount
    minimum_notional: PositiveAmount
    taker_fee_rate: Amount = Field(le=1)


class DepthLevel(DomainModel):
    price: PositiveAmount
    quantity: PositiveAmount


class LiquiditySnapshot(DomainModel):
    as_of: datetime
    bids: tuple[DepthLevel, ...]
    asks: tuple[DepthLevel, ...]

    @model_validator(mode="after")
    def valid_book(self) -> Self:
        if not self.bids or not self.asks:
            raise ValueError("Both book sides required")
        if max(x.price for x in self.bids) >= min(x.price for x in self.asks):
            raise ValueError("Crossed or locked book")
        if any(
            len({level.price for level in side}) != len(side) for side in (self.bids, self.asks)
        ):
            raise ValueError("Duplicate depth prices")
        return self


class MarketSnapshot(DomainModel):
    symbol: str
    as_of: datetime
    candles: tuple[Candle, ...]
    source: str
    trend_candles: tuple[Candle, ...] = ()
    market: MarketConstraints | None = None
    liquidity: LiquiditySnapshot | None = None

    @model_validator(mode="after")
    def point_in_time(self) -> Self:
        for series in (self.candles, self.trend_candles):
            previous: datetime | None = None
            for candle in series:
                if candle.symbol != self.symbol or not candle.closed:
                    raise ValueError("Only closed candles of the requested symbol are allowed")
                if candle.event_time > self.as_of or candle.received_at > self.as_of:
                    raise ValueError("Future candle unavailable at snapshot time")
                if previous is not None and candle.open_time < previous:
                    raise ValueError("Candles overlap, repeat or are unordered")
                previous = candle.close_time
        if self.market and self.market.symbol != self.symbol:
            raise ValueError("Market constraint symbol mismatch")
        if self.liquidity and self.liquidity.as_of > self.as_of:
            raise ValueError("Future liquidity snapshot")
        return self


class Signal(DomainModel):
    symbol: str
    action: Literal["BUY", "SELL", "HOLD"]
    strategy_version: str
    as_of: datetime
    reasons: tuple[str, ...]
    snapshot_id: str | None = None
    parameters_id: str | None = None
    parameters_json: str | None = None
    entry_price: PositiveAmount | None = None
    exit_price: PositiveAmount | None = None
    stop_loss: PositiveAmount | None = None
    take_profit: PositiveAmount | None = None
    atr: PositiveAmount | None = None
    evidence: tuple[tuple[str, str], ...] = ()


class AIAnalysis(DomainModel):
    model_version: str
    input_id: str
    verdict: Literal["ACCEPT", "REJECT", "ABSTAIN"]
    reasons: tuple[str, ...]


class RiskDecision(DomainModel):
    allowed: bool
    reasons: tuple[str, ...]
    parameters_id: str | None = None
    parameters_json: str | None = None
    quantity: Amount = Decimal("0")
    reference_price: PositiveAmount | None = None
    stop_loss: PositiveAmount | None = None
    take_profit: PositiveAmount | None = None
    risk_tmn: Amount = Decimal("0")
    notional_tmn: Amount = Decimal("0")
    halt_new_entries: bool = False


class OrderState(str, Enum):
    CREATED = "CREATED"
    SUBMITTED = "SUBMITTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


class OrderIntent(DomainModel):
    """Spot-only; unsupported margin/leverage fields are forbidden extra inputs."""

    client_id: str
    decision_id: str
    account_id: str
    symbol: str = Field(pattern=r"^[A-Z0-9]+/(TMN|USDT)$")
    side: Literal["BUY", "SELL"]
    order_type: Literal["MARKET", "LIMIT"]
    base_quantity: PositiveAmount
    limit_price: PositiveAmount | None = None

    @model_validator(mode="after")
    def price_required(self) -> Self:
        if (self.order_type == "LIMIT") != (self.limit_price is not None):
            raise ValueError("Limit price required only for LIMIT")
        return self


class Fill(DomainModel):
    fill_id: str
    client_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    base_quantity: PositiveAmount
    price: Money
    fee: Money
    executed_at: datetime


class AssetBalance(DomainModel):
    currency: str
    free: Amount
    reserved: Amount


class Position(DomainModel):
    position_id: str
    symbol: str = Field(pattern=r"^[A-Z0-9]+/(TMN|USDT)$")
    quantity: Amount
    entry_price: PositiveAmount
    stop_loss: PositiveAmount
    take_profit: PositiveAmount
    opened_at: datetime
    updated_at: datetime
    state: Literal["OPEN", "CLOSED"] = "OPEN"
    applied_fills: tuple[tuple[str, str], ...] = ()

    @model_validator(mode="after")
    def valid_position(self) -> Self:
        if self.stop_loss >= self.take_profit or self.updated_at < self.opened_at:
            raise ValueError("Invalid position levels or timestamps")
        if (self.state == "CLOSED") != (self.quantity == 0):
            raise ValueError("Position state/quantity mismatch")
        if len({key for key, _ in self.applied_fills}) != len(self.applied_fills):
            raise ValueError("Duplicate applied fill identity")
        return self


class QuoteConversion(DomainModel):
    quote: Literal["TMN", "USDT"]
    tmn_per_unit: PositiveAmount
    as_of: datetime


class PortfolioState(DomainModel):
    account_id: str
    as_of: datetime
    balances: tuple[AssetBalance, ...]
    reporting_currency: Literal["TMN"] = "TMN"
    positions: tuple[Position, ...] = ()
    equity_tmn: Amount | None = None
    daily_open_equity_tmn: PositiveAmount | None = None
    peak_equity_tmn: PositiveAmount | None = None
    trading_day: date | None = None
    gross_exposure_tmn: Amount = Decimal("0")
    reserved_exposure_tmn: Amount = Decimal("0")
    reserved_risk_tmn: Amount = Decimal("0")
    pending_symbols: tuple[str, ...] = ()
    conversions: tuple[QuoteConversion, ...] = ()
    risk_halted: bool = False

    @model_validator(mode="after")
    def unique_account_rows(self) -> Self:
        if len({b.currency for b in self.balances}) != len(self.balances):
            raise ValueError("Duplicate asset balances")
        opened = [p.symbol for p in self.positions if p.state == "OPEN"]
        if len(set(opened)) != len(opened):
            raise ValueError("Duplicate open market positions")
        if len({r.quote for r in self.conversions}) != len(self.conversions):
            raise ValueError("Duplicate quote conversions")
        if any(p.updated_at > self.as_of for p in self.positions):
            raise ValueError("Future position state")
        if any(r.as_of > self.as_of for r in self.conversions):
            raise ValueError("Future currency conversion")
        if len(set(self.pending_symbols)) != len(self.pending_symbols):
            raise ValueError("Duplicate pending markets")
        return self


class DecisionRecord(DomainModel):
    decision_id: str
    config_id: str
    snapshot_id: str
    account_id: str
    as_of: datetime
    signal: Signal
    analysis: AIAnalysis
    risk: RiskDecision
    execution_state: Literal["NOT_SUBMITTED"] = "NOT_SUBMITTED"
