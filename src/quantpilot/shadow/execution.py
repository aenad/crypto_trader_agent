"""Virtual orders only. No exchange adapter, HTTP method or MCP session exists here."""

from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal, localcontext

from quantpilot.backtest.execution import Pending
from quantpilot.backtest.ledger import PortfolioLedger
from quantpilot.config import stable_id
from quantpilot.interfaces import Clock
from quantpilot.models import Fill, MarketSnapshot, Money, OrderIntent, OrderState
from quantpilot.spot import validate_spot_order

from .domain import ShadowConfig

D = Decimal


class ShadowExecutionProvider:
    def __init__(self, config: ShadowConfig, ledger: PortfolioLedger, clock: Clock):
        self.config, self.ledger, self.clock = config, ledger, clock
        self.orders: dict[str, Pending] = {}
        self.plans: dict[str, tuple[Decimal, Decimal, Decimal]] = {}
        self.used_books: dict[str, str] = {}

    def plan(self, client_id: str, atr: Decimal, price: Decimal, fx: Decimal) -> None:
        if min(atr, price, fx) <= 0:
            raise ValueError("Invalid virtual execution plan")
        self.plans[client_id] = (atr, price, fx)

    def active(self, pair: str | None = None) -> list[Pending]:
        return [
            o
            for o in self.orders.values()
            if o.state in (OrderState.SUBMITTED, OrderState.PARTIALLY_FILLED)
            and (pair is None or o.intent.symbol == pair)
        ]

    async def submit(self, intent: OrderIntent) -> OrderState:
        with localcontext(Context(prec=34)):
            if intent.client_id in self.orders:
                if self.orders[intent.client_id].intent != intent:
                    raise ValueError("Conflicting virtual order")
                return self.orders[intent.client_id].state
            if (
                intent.account_id != "shadow"
                or intent.symbol not in self.config.approved
                or intent.order_type != "MARKET"
            ):
                raise PermissionError("ONLY_APPROVED_VIRTUAL_MARKET_ORDERS_ALLOWED")
            if self.config.expired(self.clock.now()) or (
                intent.side == "BUY" and not self.config.entries_allowed(self.clock.now())
            ):
                raise ValueError("COMPETITION_ENTRY_OR_ORDER_DEADLINE")
            atr, price, fx = self.plans.pop(intent.client_id)
            market = next(m for m in self.config.markets if m.symbol == intent.symbol)
            if (
                intent.base_quantity % market.quantity_step
                or intent.base_quantity < market.minimum_quantity
            ):
                raise ValueError("Invalid virtual order precision")
            base, quote = intent.symbol.split("/")
            fee = max(self.config.simulation.entry_fee, market.taker_fee_rate)
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
                self.config.approved,
                {asset: self.ledger.free(asset)},
                fee,
            )
            self.ledger.reserve(asset, reserved)
            self.orders[intent.client_id] = Pending(
                intent, self.clock.now(), atr, intent.base_quantity, reserved, asset, price, fx
            )
            return OrderState.SUBMITTED

    async def settle(self, snapshot: MarketSnapshot) -> str:
        """Queue a reduce-only virtual sale; only a LATER book can fill it."""
        pair = snapshot.symbol
        if self.active(pair):
            return "PENDING:" + pair
        position = self.ledger.positions.get(pair)
        if position is None or position.quantity == 0:
            return "NO_HOLDING:" + pair
        market, book = snapshot.market, snapshot.liquidity
        if market is None or book is None:
            return "UNAVAILABLE:" + pair
        best = max(book.bids, key=lambda level: level.price)
        price = (
            best.price * (1 - self.config.simulation.slippage) / market.price_tick
        ).to_integral_value(rounding=ROUND_FLOOR) * market.price_tick
        quantity = min(
            position.quantity,
            self.ledger.free(pair.split("/")[0]),
            best.quantity * self.config.simulation.book_participation,
        )
        quantity = (quantity / market.quantity_step).to_integral_value(
            rounding=ROUND_FLOOR
        ) * market.quantity_step
        if quantity < market.minimum_quantity or quantity * price < market.minimum_notional:
            return "DUST_OR_NO_LIQUIDITY:" + pair
        identity = "settle:" + stable_id([pair, snapshot.as_of.isoformat()])
        atr = (position.take_profit - position.stop_loss) / (
            self.config.research.stop_atr + self.config.research.target_atr
        )
        self.plan(identity, atr, price, D(1))
        try:
            await self.submit(
                OrderIntent(
                    client_id=identity,
                    decision_id=identity,
                    account_id="shadow",
                    symbol=pair,
                    side="SELL",
                    order_type="MARKET",
                    base_quantity=quantity,
                )
            )
        except ValueError:
            return "REJECTED:" + pair
        return "QUEUED:" + pair

    async def lookup(self, client_id: str) -> OrderState:
        return self.orders[client_id].state

    async def fills(self, client_id: str) -> tuple[Fill, ...]:
        return tuple(self.orders[client_id].executions)

    async def cancel(self, client_id: str) -> OrderState:
        order = self.orders[client_id]
        if order in self.active():
            self.ledger.release(order.asset, order.reserved)
            order.reserved = D(0)
            order.state = OrderState.CANCELED
        return order.state

    async def expire(self) -> None:
        for order in self.active():
            if (
                self.clock.now() - order.submitted
            ).total_seconds() >= self.config.simulation.order_ttl_seconds:
                await self.cancel(order.intent.client_id)

    async def on_book(self, snapshot: MarketSnapshot, fx: Decimal) -> None:
        with localcontext(Context(prec=34)):
            await self._on_book(snapshot, fx)

    async def _on_book(self, snapshot: MarketSnapshot, fx: Decimal) -> None:
        book, market = snapshot.liquidity, snapshot.market
        configured = next((m for m in self.config.markets if m.symbol == snapshot.symbol), None)
        if configured is not None:
            configured = configured.model_copy(
                update={
                    "taker_fee_rate": max(
                        configured.taker_fee_rate,
                        self.config.simulation.entry_fee,
                        self.config.simulation.exit_fee,
                    )
                }
            )
        if (
            book is None
            or market is None
            or configured is None
            or snapshot.symbol not in self.config.approved
            or not market.spot_enabled
            or not market.account_enabled
            or market != configured
        ):
            return
        now = self.clock.now()
        if not 0 <= (now - book.as_of).total_seconds() <= self.config.freshness_seconds:
            return
        digest = stable_id(book.model_dump(mode="json"))
        if self.used_books.get(snapshot.symbol) == digest:
            return
        self.used_books[snapshot.symbol] = digest
        p = self.config.simulation
        pools = {
            side: [
                [level.price, level.quantity * p.book_participation]
                for level in sorted(
                    book.asks if side == "BUY" else book.bids,
                    key=lambda level: level.price,
                    reverse=side == "SELL",
                )
            ]
            for side in ("BUY", "SELL")
        }
        for order in self.active(snapshot.symbol):
            intent = order.intent
            if book.as_of <= order.submitted or now <= order.submitted:
                continue
            if intent.side == "BUY" and (fx > order.maximum_fx or self.ledger.halted):
                await self.cancel(intent.client_id)
                continue
            for level in pools[intent.side]:
                if order.remaining == 0:
                    break
                direction = D(1) if intent.side == "BUY" else D(-1)
                price = level[0] * (1 + direction * p.slippage)
                price = (price / market.price_tick).to_integral_value(
                    rounding=ROUND_CEILING if intent.side == "BUY" else ROUND_FLOOR
                ) * market.price_tick
                if price <= 0 or (
                    intent.side == "BUY"
                    and (
                        price > order.budget_price
                        or price - self.config.research.stop_atr * order.atr <= 0
                    )
                ):
                    await self.cancel(intent.client_id)
                    break
                quantity = min(order.remaining, level[1])
                quantity = (quantity / market.quantity_step).to_integral_value(
                    rounding=ROUND_FLOOR
                ) * market.quantity_step
                if quantity < market.minimum_quantity or quantity * price < market.minimum_notional:
                    continue
                fee = max(
                    p.entry_fee if intent.side == "BUY" else p.exit_fee, market.taker_fee_rate
                )
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
                    fee=Money(amount=quantity * price * fee, currency=market.quote),
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
                order.executions.append(fill)
                order.state = (
                    OrderState.FILLED if order.remaining == 0 else OrderState.PARTIALLY_FILLED
                )
                if order.remaining == 0:
                    self.ledger.release(order.asset, order.reserved)
                    order.reserved = D(0)
