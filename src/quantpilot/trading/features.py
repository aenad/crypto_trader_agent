"""Decimal indicators: SMA-seeded EMA and Wilder RSI/ATR/ADX, past-only."""

from dataclasses import dataclass
from decimal import Context, Decimal, localcontext

from quantpilot.models import Candle, LiquiditySnapshot

from .config import ResearchParameters

D = Decimal


def ema(values: tuple[Decimal, ...], period: int) -> Decimal:
    if period < 1 or len(values) < period:
        raise ValueError("INSUFFICIENT_EMA_HISTORY")
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        result = sum(values[:period], D(0)) / D(period)
        alpha = D(2) / D(period + 1)
        for value in values[period:]:
            result += alpha * (value - result)
        return +result


def wilder(values: tuple[Decimal, ...], period: int) -> list[Decimal]:
    if period < 1 or len(values) < period:
        raise ValueError("INSUFFICIENT_WILDER_HISTORY")
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        result = [sum(values[:period], D(0)) / D(period)]
        for value in values[period:]:
            result.append((result[-1] * D(period - 1) + value) / D(period))
        return result


def rsi(values: tuple[Decimal, ...], period: int) -> Decimal:
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        changes = tuple(b - a for a, b in zip(values, values[1:]))
        gain = wilder(tuple(max(x, D(0)) for x in changes), period)[-1]
        loss = wilder(tuple(max(-x, D(0)) for x in changes), period)[-1]
        if loss == 0:
            return D(100) if gain else D(50)
        return D(100) - D(100) / (1 + gain / loss)


def true_ranges(rows: tuple[Candle, ...]) -> tuple[Decimal, ...]:
    return tuple(
        max(row.high - row.low, abs(row.high - rows[i - 1].close), abs(row.low - rows[i - 1].close))
        if i
        else row.high - row.low
        for i, row in enumerate(rows)
    )


def atr(rows: tuple[Candle, ...], period: int) -> Decimal:
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        return wilder(true_ranges(rows), period)[-1]


def adx(rows: tuple[Candle, ...], period: int) -> Decimal:
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        positive, negative = [], []
        for previous, current in zip(rows, rows[1:]):
            up, down = current.high - previous.high, previous.low - current.low
            positive.append(up if up > down and up > 0 else D(0))
            negative.append(down if down > up and down > 0 else D(0))
        trs = wilder(true_ranges(rows)[1:], period)
        plus = wilder(tuple(positive), period)
        minus = wilder(tuple(negative), period)
        dx = []
        for tr, p, m in zip(trs, plus, minus, strict=True):
            pdi = D(100) * p / tr if tr else D(0)
            mdi = D(100) * m / tr if tr else D(0)
            dx.append(D(100) * abs(pdi - mdi) / (pdi + mdi) if pdi + mdi else D(0))
        return wilder(tuple(dx), period)[-1]


@dataclass(frozen=True)
class Features:
    close: Decimal
    ema_fast: Decimal
    ema_slow: Decimal
    rsi: Decimal
    atr: Decimal
    adx: Decimal
    relative_volume: Decimal
    prior_high: Decimal
    prior_low: Decimal

    def evidence(self, prefix: str) -> tuple[tuple[str, str], ...]:
        from dataclasses import fields

        return tuple(
            (f"{prefix}.{field.name}", str(getattr(self, field.name))) for field in fields(self)
        )


class FeatureEngine:
    def __init__(self, parameters: ResearchParameters):
        self.parameters = parameters

    def compute(self, rows: tuple[Candle, ...]) -> Features:
        p = self.parameters
        if any(not row.closed for row in rows):
            raise ValueError("INCOMPLETE_CANDLES")
        required = max(
            p.ema_slow,
            p.rsi_period + 1,
            p.atr_period,
            2 * p.adx_period,
            p.breakout_window + 1,
            p.volume_window + 1,
        )
        if len(rows) < required:
            raise ValueError("INSUFFICIENT_HISTORY")
        with localcontext(Context(prec=34)) as ctx:
            ctx.prec = 34
            closes = tuple(row.close for row in rows)
            prior = rows[-p.breakout_window - 1 : -1]
            previous_volume = sum(
                (row.volume for row in rows[-p.volume_window - 1 : -1]), D(0)
            ) / D(p.volume_window)
            return Features(
                close=closes[-1],
                ema_fast=ema(closes, p.ema_fast),
                ema_slow=ema(closes, p.ema_slow),
                rsi=rsi(closes, p.rsi_period),
                atr=atr(rows, p.atr_period),
                adx=adx(rows, p.adx_period),
                relative_volume=rows[-1].volume / previous_volume if previous_volume > 0 else D(0),
                prior_high=max(row.high for row in prior),
                prior_low=min(row.low for row in prior),
            )


@dataclass(frozen=True)
class LiquidityFeatures:
    bid: Decimal
    ask: Decimal
    spread: Decimal
    ask_depth_quote: Decimal
    bid_depth_quote: Decimal


def liquidity_features(book: LiquiditySnapshot, band: Decimal) -> LiquidityFeatures:
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        bid = max(level.price for level in book.bids)
        ask = min(level.price for level in book.asks)
        return LiquidityFeatures(
            bid,
            ask,
            (ask - bid) / ((ask + bid) / D(2)),
            sum(
                (
                    level.price * level.quantity
                    for level in book.asks
                    if level.price <= ask * (1 + band)
                ),
                D(0),
            ),
            sum(
                (
                    level.price * level.quantity
                    for level in book.bids
                    if level.price >= bid * (1 - band)
                ),
                D(0),
            ),
        )
