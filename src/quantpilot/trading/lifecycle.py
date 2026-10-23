"""Pure exit policies and simulated fill transitions; no exchange access."""

from datetime import datetime
from decimal import Context, Decimal, localcontext

from quantpilot.config import stable_id
from quantpilot.models import Candle, Fill, Money, OrderIntent, Position

from .config import ResearchParameters


def exit_signal(
    position: Position,
    candle: Candle,
    ema: Decimal | None,
    now: datetime,
    parameters: ResearchParameters,
) -> tuple[str | None, Decimal | None]:
    if position.state != "OPEN" or candle.close_time <= position.opened_at:
        return None, None
    # No intrabar inference if the position opened partway through this bar.
    if candle.open_time >= position.opened_at:
        if candle.open <= position.stop_loss:
            return "STOP_GAP", candle.open
        if candle.low <= position.stop_loss:
            return "ATR_STOP", position.stop_loss  # Conservative precedence if both levels touched.
        if candle.high >= position.take_profit:
            return "TAKE_PROFIT", max(candle.open, position.take_profit)
    if (now - position.opened_at).total_seconds() >= parameters.max_hold_seconds:
        return "MAX_HOLD_TIME", candle.close
    if ema is not None and candle.close < ema:
        return "TREND_EXIT", candle.close
    return None, None


def simulated_fill(
    intent: OrderIntent, price: Decimal, at: datetime, fee_rate: Decimal = Decimal("0")
) -> Fill:
    if not Decimal(0) <= fee_rate < 1:
        raise ValueError("Invalid simulated fee")
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        quote = intent.symbol.split("/")[1]
        if intent.order_type == "LIMIT":
            raise ValueError("Phase 3 mock helper accepts MARKET intents only")
        return Fill(
            fill_id=stable_id(
                {
                    "intent": intent.model_dump(mode="json"),
                    "at": at.isoformat(),
                    "price": str(price),
                    "fee_rate": str(fee_rate),
                }
            ),
            client_id=intent.client_id,
            symbol=intent.symbol,
            side=intent.side,
            base_quantity=intent.base_quantity,
            price=Money(amount=price, currency=quote),
            fee=Money(amount=price * intent.base_quantity * fee_rate, currency=quote),
            executed_at=at,
        )


def apply_simulated_fill(
    position: Position | None, fill: Fill, atr_at_entry: Decimal, parameters: ResearchParameters
) -> Position:
    """Update a simulated long position, deduplicating exact fill replays."""
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        base, quote = fill.symbol.split("/")
        if fill.price.currency != quote or fill.fee.currency not in (base, quote):
            raise ValueError("Unsupported fill currency")
        digest = stable_id(fill.model_dump(mode="json"))
        if position and fill.fill_id in dict(position.applied_fills):
            if dict(position.applied_fills)[fill.fill_id] != digest:
                raise ValueError("Conflicting replay of simulated fill")
            return position
        applied = (position.applied_fills if position else ()) + ((fill.fill_id, digest),)
        if position and (
            position.symbol != fill.symbol
            or position.state != "OPEN"
            or fill.executed_at < position.updated_at
        ):
            raise ValueError("Position identity/state/time mismatch")
        if fill.side == "SELL":
            if position is None:
                raise ValueError("No short selling")
            quantity = fill.base_quantity + (
                fill.fee.amount if fill.fee.currency == base else Decimal(0)
            )
            if quantity > position.quantity:
                raise ValueError("Oversell")
            return Position(
                **{
                    **position.model_dump(),
                    "quantity": position.quantity - quantity,
                    "updated_at": fill.executed_at,
                    "state": "CLOSED" if quantity == position.quantity else "OPEN",
                    "applied_fills": applied,
                }
            )
        if atr_at_entry <= 0:
            raise ValueError("Positive entry ATR required")
        net = fill.base_quantity - (fill.fee.amount if fill.fee.currency == base else Decimal(0))
        if net <= 0:
            raise ValueError("Fees consume entire fill")
        old = position.quantity if position else Decimal(0)
        price = (
            (position.entry_price * old if position else Decimal(0)) + fill.price.amount * net
        ) / (old + net)
        stop = fill.price.amount - parameters.stop_atr * atr_at_entry
        target = fill.price.amount + parameters.target_atr * atr_at_entry
        if position:
            stop = max(stop, position.stop_loss)  # A later partial fill never widens the stop.
            target = position.take_profit
        if stop <= 0 or stop >= target:
            raise ValueError("Invalid ATR protection levels")
        return Position(
            position_id=position.position_id if position else fill.client_id,
            symbol=fill.symbol,
            quantity=old + net,
            entry_price=price,
            stop_loss=stop,
            take_profit=target,
            opened_at=position.opened_at if position else fill.executed_at,
            updated_at=fill.executed_at,
            applied_fills=applied,
        )
