from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator
from typing_extensions import Self

from quantpilot.models import DomainModel, MarketEvent, PositiveAmount


class Market(DomainModel):
    symbol: str
    base: str
    quote: Literal["TMN", "USDT"]
    spot: bool


class Trade(MarketEvent):
    price: PositiveAmount
    quantity: PositiveAmount
    buyer_initiated: bool
    identity_kind: Literal["exchange_id", "content_hash"] = "content_hash"


class Level(DomainModel):
    price: PositiveAmount
    quantity: PositiveAmount


class Book(MarketEvent):
    bids: tuple[Level, ...]
    asks: tuple[Level, ...]
    timestamp_kind: Literal["exchange", "observation"] = "observation"

    @model_validator(mode="after")
    def non_crossed(self) -> Self:
        if not self.bids or not self.asks:
            raise ValueError("Empty book side")
        if max(x.price for x in self.bids) >= min(x.price for x in self.asks):
            raise ValueError("Crossed book")
        return self


class CollectionPolicy(DomainModel):
    approved: frozenset[str] = Field(min_length=1)
    excluded: frozenset[str] = frozenset()
    freshness_seconds: int = Field(default=180, ge=1)
    chunk_bars: int = Field(default=300, ge=1, le=1000)

    @model_validator(mode="after")
    def canonical_symbols(self) -> Self:
        for pair in self.approved | self.excluded:
            canonical_pair(pair)
        if self.approved & self.excluded:
            raise ValueError("Whitelist intersects excluded markets")
        return self


def canonical_pair(pair: str) -> str:
    import re

    if not re.fullmatch(r"[A-Z0-9]+/(TMN|USDT)", pair):
        raise ValueError("Expected canonical BASE/TMN or BASE/USDT symbol")
    base, quote = pair.split("/")
    if base == quote:
        raise ValueError("Identical base and quote")
    return pair


def utc_time(value: str | int | float) -> datetime:
    from datetime import timezone

    if isinstance(value, str):
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if result.tzinfo is None:
            raise ValueError("Timestamp has no timezone")
        return result.astimezone(timezone.utc)
    return datetime.fromtimestamp(value, timezone.utc)
