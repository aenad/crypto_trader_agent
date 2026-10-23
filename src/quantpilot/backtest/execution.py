"""Conservative, offline exchange simulator; no network or exchange tools."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal, localcontext

from quantpilot.models import Candle, Fill, Money, OrderIntent, OrderState
from quantpilot.spot import validate_spot_order

from .history import HistoricalClock, HistoricalMarketDataProvider
from .ledger import PortfolioLedger

D = Decimal


@dataclass
class Pending:
    intent: OrderIntent
    submitted: datetime
    atr: Decimal
    remaining: Decimal
    reserved: Decimal
    asset: str
    budget_price: Decimal
    maximum_fx: Decimal
    state: OrderState = OrderState.SUBMITTED
    executions: list[Fill] = field(default_factory=list)


class SimulatedExecutionProvider:
    def __init__(
        self,
        clock: HistoricalClock,
        data: HistoricalMarketDataProvider,
        ledger: PortfolioLedger,
        approved: tuple[str, ...] | None = None,
    ):
        self.clock, self.data, self.ledger = clock, data, ledger
        self.approved = tuple(data.candles) if approved is None else approved
        self.orders: dict[str, Pending] = {}
        self.plans: dict[str, tuple[Decimal, Decimal, Decimal]] = {}

    def plan(
        self, client_id: str, atr: Decimal, maximum_buy_price: Decimal, maximum_fx: Decimal = D(1)
    ) -> None:
        if atr <= 0 or maximum_buy_price <= 0 or maximum_fx <= 0:
            raise ValueError("Positive execution plan required")
        self.plans[client_id] = atr, maximum_buy_price, maximum_fx

    async def submit(self, intent: OrderIntent) -> OrderState:
        with localcontext(Context(prec=34)):
            return await self._submit(intent)

    async def _submit(self, intent: OrderIntent) -> OrderState:
        if intent.client_id in self.orders:
            if self.orders[intent.client_id].intent != intent:
                raise ValueError("Conflicting client ID")
            return self.orders[intent.client_id].state
        atr, price, maximum_fx = self.plans.pop(intent.client_id)
        market = self.data.markets[intent.symbol]
        if (
            intent.account_id != "backtest"
            or intent.base_quantity % market.quantity_step
            or intent.base_quantity < market.minimum_quantity
            or (intent.limit_price is not None and intent.limit_price % market.price_tick)
        ):
            raise ValueError("Invalid simulated account/order precision or minimum quantity")
        if intent.side == "BUY" and intent.limit_price is not None:
            price = max(price, intent.limit_price)
        base, quote = intent.symbol.split("/")
        fee = max(self.data.simulation.entry_fee, self.data.markets[intent.symbol].taker_fee_rate)
        asset = quote if intent.side == "BUY" else base
        reserved = (
            intent.base_quantity * price * (1 + fee)
            if intent.side == "BUY"
            else intent.base_quantity
        )
        validate_spot_order(
            intent.symbol,
            intent.side,
            intent.base_quantity,
            intent.limit_price or price,
            market,
            self.approved,
            {asset: self.ledger.free(asset)},
            fee,
        )
        self.ledger.reserve(asset, reserved)
        self.orders[intent.client_id] = Pending(
            intent, self.clock.now(), atr, intent.base_quantity, reserved, asset, price, maximum_fx
        )
        return OrderState.SUBMITTED

    async def lookup(self, client_id: str) -> OrderState:
        return self.orders[client_id].state

    async def fills(self, client_id: str) -> tuple[Fill, ...]:
        return tuple(self.orders[client_id].executions)

    async def cancel(self, client_id: str) -> OrderState:
        order = self.orders[client_id]
        if order.state in (OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED):
            self.ledger.release(order.asset, order.reserved)
            order.reserved = D(0)
            order.state = OrderState.CANCELED
        return order.state

    def active(self, pair: str | None = None) -> list[Pending]:
        return [
            o
            for o in self.orders.values()
            if o.state in (OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED)
            and (pair is None or o.intent.symbol == pair)
        ]

    async def process(
        self, candle: Candle, opening: bool, fx: Decimal, previous_volume: Decimal = D(0)
    ) -> None:
        with localcontext(Context(prec=34)):
            await self._process(candle, opening, fx, previous_volume)

    async def _process(
        self, candle: Candle, opening: bool, fx: Decimal, previous_volume: Decimal
    ) -> None:
        now, p = self.clock.now(), self.data.simulation
        if now != (candle.open_time if opening else candle.close_time):
            raise ValueError("Execution event does not match historical clock")
        market = self.data.markets[candle.symbol]
        if (
            candle.symbol not in self.approved
            or not market.spot_enabled
            or not market.account_enabled
        ):
            for order in self.active(candle.symbol):
                await self.cancel(order.intent.client_id)
            return
        book = self.data.recorded_quote(candle.symbol, now) if opening else None
        # One shared capacity pool per side/event. OHLC capacity at open uses
        # only the PREVIOUS completed candle, never the future candle volume.
        pools = {
            side: [
                [level.price, level.quantity * p.book_participation]
                for level in sorted(
                    book.asks if side == "BUY" else book.bids,
                    key=lambda x: x.price,
                    reverse=side == "SELL",
                )
            ]
            if book
            else [[candle.open, previous_volume * p.volume_participation]]
            for side in ("BUY", "SELL")
        }
        limit_capacity = candle.volume * p.volume_participation
        for order in self.active(candle.symbol):
            if (now - order.submitted).total_seconds() >= p.order_ttl_seconds:
                await self.cancel(order.intent.client_id)
                continue
            intent = order.intent
            if intent.side == "BUY" and fx > order.maximum_fx:
                await self.cancel(intent.client_id)
                continue
            # A close-derived decision may execute at the following bar open,
            # including a shared timestamp, but never in the bar that generated it.
            if order.submitted > candle.open_time:
                continue
            if intent.order_type == "MARKET":
                if not opening:
                    continue
                levels = pools[intent.side]
            else:
                if opening:
                    continue
                assert intent.limit_price is not None
                penetration = market.price_tick * p.limit_penetration_ticks
                touched = (
                    candle.low <= intent.limit_price - penetration
                    if intent.side == "BUY"
                    else candle.high >= intent.limit_price + penetration
                )
                if not touched:
                    continue
                levels = [[intent.limit_price, limit_capacity]]
            for level in levels:
                if order.remaining <= 0:
                    break
                price = level[0]
                if intent.order_type == "MARKET":
                    direction = D(1) if intent.side == "BUY" else D(-1)
                    price *= 1 + direction * p.slippage
                    if not book:
                        price *= 1 + direction * p.half_spread
                rounding = ROUND_CEILING if intent.side == "BUY" else ROUND_FLOOR
                price = (price / market.price_tick).to_integral_value(
                    rounding=rounding
                ) * market.price_tick
                if price <= 0:
                    await self.cancel(intent.client_id)
                    break
                if intent.side == "BUY" and price - self.data.research.stop_atr * order.atr <= 0:
                    await self.cancel(intent.client_id)
                    break
                if intent.side == "BUY" and price > order.budget_price:
                    await self.cancel(intent.client_id)
                    break
                quantity = min(order.remaining, level[1])
                quantity = (quantity / market.quantity_step).to_integral_value(
                    rounding=ROUND_FLOOR
                ) * market.quantity_step
                if quantity < market.minimum_quantity or quantity * price < market.minimum_notional:
                    continue
                fee_rate = max(
                    p.entry_fee if intent.side == "BUY" else p.exit_fee, market.taker_fee_rate
                )
                fee = quantity * price * fee_rate
                release = (
                    quantity * order.budget_price * (1 + max(p.entry_fee, market.taker_fee_rate))
                    if intent.side == "BUY"
                    else quantity
                )
                fill = Fill(
                    fill_id=f"{intent.client_id}:{len(order.executions)}",
                    client_id=intent.client_id,
                    symbol=intent.symbol,
                    side=intent.side,
                    base_quantity=quantity,
                    price=Money(amount=price, currency=market.quote),
                    fee=Money(amount=fee, currency=market.quote),
                    executed_at=now,
                )
                self.ledger.release(order.asset, release)
                try:
                    self.ledger.apply_fill(fill, fx, order.atr)
                except Exception:
                    self.ledger.reserve(order.asset, release)
                    raise
                order.reserved -= release
                order.remaining -= quantity
                level[1] -= quantity
                if intent.order_type == "LIMIT":
                    limit_capacity -= quantity
                order.executions.append(fill)
                order.state = (
                    OrderState.FILLED if order.remaining == 0 else OrderState.PARTIALLY_FILLED
                )
                if order.remaining == 0:
                    self.ledger.release(order.asset, order.reserved)
                    order.reserved = D(0)
