"""Deterministic, explainable spot signal baseline; it does not promise profit."""
from datetime import datetime, timezone
from typing import Any
import math

from .config import Settings
from .market_rules import check_market
from .schemas import Signal


def _unwrap_rows(payload: Any) -> list[Any]:
    if isinstance(payload, dict):
        if all(isinstance(payload.get(key), list) for key in ("t", "o", "h", "l", "c", "v")):
            if len({len(payload[key]) for key in ("t", "o", "h", "l", "c", "v")}) != 1:
                raise ValueError("Candle column lengths differ")
            return [list(row) for row in sorted(zip(*(payload[key] for key in ("t", "o", "h", "l", "c", "v"))), key=lambda row: row[0])]
        for key in ("candles", "data", "result", "items", "rows", "history"):
            if key in payload:
                return _unwrap_rows(payload[key])
        if all(key in payload for key in ("open", "high", "low", "close")):
            return [payload]
    if isinstance(payload, list):
        return payload
    return []


def _number(row: Any, *keys: str, index: int | None = None) -> float | None:
    value = None
    if isinstance(row, dict):
        for key in keys:
            if key in row:
                value = row[key]
                break
    elif isinstance(row, (list, tuple)) and index is not None and len(row) > index:
        value = row[index]
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (TypeError, ValueError):
        return None


def normalize_candles(payload: Any) -> list[dict[str, float]]:
    rows = _unwrap_rows(payload)
    candles = []
    for row in rows:
        close = _number(row, "close", "c", "price", index=4)
        high = _number(row, "high", "h", index=2)
        low = _number(row, "low", "l", index=3)
        open_ = _number(row, "open", "o", index=1)
        volume = _number(row, "volume", "v", "baseVolume", index=5) or 0.0
        if close and high and low and open_:
            candles.append({"open": open_, "high": high, "low": low, "close": close, "volume": volume})
    return candles


def _ema(values: list[float], span: int) -> float:
    alpha = 2 / (span + 1)
    result = values[0]
    for value in values[1:]:
        result = alpha * value + (1 - alpha) * result
    return result


def _rsi(values: list[float], period: int = 14) -> float:
    changes = [right - left for left, right in zip(values, values[1:])][-period:]
    gains = sum(max(change, 0) for change in changes) / period
    losses = sum(max(-change, 0) for change in changes) / period
    if losses == 0:
        return 100.0 if gains else 50.0
    return 100 - 100 / (1 + gains / losses)


def analyze_candles(symbol: str, payload: Any, settings: Settings, *, held_base: float = 0) -> Signal:
    allowed, market_reason = check_market(symbol)
    candles = normalize_candles(payload)
    now = datetime.now(timezone.utc).isoformat()
    if not allowed:
        return Signal(symbol=symbol, action="hold", confidence=1, reasons=[market_reason], timestamp=now, mode=settings.trading_mode)
    if len(candles) < 30:
        return Signal(symbol=symbol, action="hold", confidence=0, reasons=["برای تحلیل حداقل ۳۰ کندل معتبر لازم است."], timestamp=now, mode=settings.trading_mode)

    close = [item["close"] for item in candles]
    current = close[-1]
    ema_fast = _ema(close[-50:], 12)
    ema_slow = _ema(close[-50:], 26)
    rsi = _rsi(close)
    returns = [(right / left) - 1 for left, right in zip(close[-21:-1], close[-20:]) if left]
    volatility = (sum((x - sum(returns) / max(len(returns), 1)) ** 2 for x in returns) / max(len(returns), 1)) ** 0.5 if returns else 0
    recent_volume = sum(x["volume"] for x in candles[-5:]) / 5
    baseline_volume = sum(x["volume"] for x in candles[-25:-5]) / 20
    volume_ratio = recent_volume / baseline_volume if baseline_volume > 0 else 1

    bullish = ema_fast > ema_slow and 42 <= rsi <= 68 and volume_ratio >= 0.8
    bearish = ema_fast < ema_slow or rsi >= 75
    action = "buy" if bullish and held_base <= 0 else "sell" if (bearish and held_base > 0) else "hold"
    confidence = min(0.95, max(0.05, 0.45 + (0.18 if ema_fast > ema_slow else -0.12) + (0.12 if 45 <= rsi <= 65 else -0.08) + min(0.15, max(0, (volume_ratio - 1) * 0.1))))
    stop = current * (1 - max(0.015, 2 * volatility))
    target = current * (1 + max(0.025, 3 * volatility))
    risk_amount = settings.max_order_quote * settings.risk_per_trade
    risk_per_unit = max(current - stop, current * 0.001)
    quote_size = min(settings.max_order_quote, risk_amount / (risk_per_unit / current)) if action == "buy" else 0
    reasons = [
        f"EMA12 {'بالاتر از' if ema_fast > ema_slow else 'پایین‌تر از'} EMA26 است.",
        f"RSI14 برابر {rsi:.1f} و نسبت حجم اخیر به میانگین برابر {volume_ratio:.2f} است.",
        "سیگنال فقط برای اسپات و بدون لوریج ارزیابی می‌شود.",
        "این سیگنال احتمالاتی است و سود را تضمین نمی‌کند؛ پیش از اجرا ریسک، موجودی و وضعیت جفت‌ارز دوباره بررسی شود.",
    ]
    return Signal(
        symbol=symbol, action=action, confidence=round(confidence, 3),
        entry_price=current if action == "buy" else None,
        exit_price=current if action == "sell" else None,
        stop_loss=round(stop, 8), take_profit=round(target, 8),
        position_quote=round(quote_size, 2), reasons=reasons,
        indicators={"ema12": round(ema_fast, 8), "ema26": round(ema_slow, 8), "rsi14": round(rsi, 4), "volume_ratio": round(volume_ratio, 4), "volatility": round(volatility, 6)},
        timestamp=now, mode=settings.trading_mode,
    )
