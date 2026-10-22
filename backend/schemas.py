from typing import Any, Literal
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    mcp_connected: bool
    trading_mode: str
    live_trading_enabled: bool
    message: str


class Market(BaseModel):
    symbol: str
    base: str | None = None
    quote: str | None = None
    eligible: bool = False
    reason: str = ""
    raw: dict[str, Any] = Field(default_factory=dict)


class Signal(BaseModel):
    symbol: str
    action: Literal["buy", "sell", "hold"]
    confidence: float
    entry_price: float | None = None
    exit_price: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None
    position_quote: float = 0
    reasons: list[str] = Field(default_factory=list)
    indicators: dict[str, float] = Field(default_factory=dict)
    timestamp: str
    mode: str = "shadow"


class OrderIntent(BaseModel):
    symbol: str
    side: Literal["buy", "sell"]
    amount: float = Field(gt=0)
    price: float | None = Field(default=None, gt=0)
    market_type: Literal["spot"] = "spot"
    leverage: int = Field(default=1, ge=1, le=1)


class OrderResult(BaseModel):
    accepted: bool
    mode: str
    symbol: str
    side: str
    amount: float
    reason: str
    order: dict[str, Any] | None = None
