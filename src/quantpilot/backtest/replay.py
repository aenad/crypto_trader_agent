"""Single-process historical event loop using the unmodified Phase 3 engines."""

from datetime import datetime, timedelta
from decimal import ROUND_FLOOR, Context, Decimal, localcontext
from typing import Any

from quantpilot.config import stable_id
from quantpilot.interfaces import SignalEvaluator
from quantpilot.models import Fill, Money, OrderIntent, QuoteConversion
from quantpilot.spot import validate_spot_order
from quantpilot.trading.config import RiskParameters
from quantpilot.trading.risk import DeterministicRiskEngine
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

from .execution import SimulatedExecutionProvider
from .history import HistoricalClock, HistoricalMarketDataProvider
from .ledger import PortfolioLedger

D = Decimal


class HistoricalReplay:
    def __init__(
        self,
        data: HistoricalMarketDataProvider,
        risk: RiskParameters,
        approved: tuple[str, ...],
        fx: tuple[QuoteConversion, ...] = (),
        evaluator: SignalEvaluator | None = None,
        decision_start: datetime | None = None,
        evaluation_id: str | None = None,
    ):
        self.data, self.risk_parameters, self.approved, self.fx = data, risk, approved, fx
        self.evaluator, self.decision_start = evaluator, decision_start
        if decision_start is not None and (
            decision_start.tzinfo is None
            or not min(rows[0].open_time for rows in data.candles.values())
            <= decision_start
            <= max(rows[-1].close_time for rows in data.candles.values())
        ):
            raise ValueError("Decision start must be an aware timestamp inside the history")
        if evaluator is not None and evaluation_id is None:
            raise ValueError("An AI evaluation identity is required for reproducible replay")
        self.evaluation_id = evaluation_id
        if any(x.quote != "USDT" for x in fx) or tuple(x.as_of for x in fx) != tuple(
            sorted({x.as_of for x in fx})
        ):
            raise ValueError("USDT FX history must be unique and chronological")
        self.clock = HistoricalClock(min(rows[0].open_time for rows in data.candles.values()))
        self.ledger = PortfolioLedger(data.simulation.initial_capital_tmn, data.research)
        self.execution = SimulatedExecutionProvider(self.clock, data, self.ledger, approved)
        self.decisions: list[dict[str, Any]] = []
        self.equity: list[dict[str, str]] = []
        self.residuals: list[dict[str, str]] = []
        self.marks: dict[str, Decimal] = {}

    def rate(self, now: datetime) -> Decimal:
        rows = [x for x in self.fx if x.as_of <= now]
        if (
            not rows
            or (now - rows[-1].as_of).total_seconds() > self.data.simulation.max_fx_age_seconds
        ):
            raise ValueError("Missing/stale explicit USDT/TMN FX history")
        return rows[-1].tmn_per_unit

    def conversions(self, now: datetime) -> tuple[QuoteConversion, ...]:
        if not any(pair.endswith("/USDT") for pair in self.data.candles):
            return ()
        rate = self.rate(now)
        self.marks["USDT"] = rate
        # Keep the original provenance timestamp, not a refreshed old quote.
        return (next(x for x in reversed(self.fx) if x.as_of <= now),)

    def mark(self, pair: str, price: Decimal, now: datetime) -> None:
        base, quote = pair.split("/")
        rate = D(1) if quote == "TMN" else self.rate(now)
        self.marks[base] = price * rate

    def sample(self, now: datetime) -> None:
        equity, unrealized, exposure = self.ledger.valuation(self.marks)
        self.ledger.peak = max(equity, self.ledger.peak)
        self.equity.append(
            {
                "at": now.isoformat(),
                "equity_tmn": str(equity),
                "realized_tmn": str(self.ledger.realized),
                "unrealized_tmn": str(unrealized),
                "exposure_tmn": str(exposure),
                "drawdown": str((self.ledger.peak - equity) / self.ledger.peak),
            }
        )

    async def run(self) -> dict[str, Any]:
        with localcontext(Context(prec=34)):
            return await self._run()

    async def _run(self) -> dict[str, Any]:
        if self.equity:
            raise ValueError("Replay instances are single-use")
        eligibility = MarketEligibilityFilter(self.approved)
        strategy = MomentumBreakout(self.data.research, eligibility)
        events: dict[datetime, dict[str, list[Any]]] = {}
        for pair, rows in sorted(self.data.candles.items()):
            for index, candle in enumerate(rows):
                events.setdefault(candle.open_time, {"open": [], "close": []})["open"].append(
                    (pair, index, candle)
                )
                events.setdefault(candle.close_time, {"open": [], "close": []})["close"].append(
                    (pair, index, candle)
                )
        if self.decision_start is not None:
            # Earlier rows are feature warmup ONLY. Start capital and accounting
            # at evaluation time, excluding training-period FX gains/losses.
            events = {time: event for time, event in events.items() if time >= self.decision_start}
        first = min(events)
        conversions = self.conversions(first)
        self.sample(first)
        if conversions and self.data.simulation.quote_funding_fraction:
            p = self.data.simulation
            budget = p.initial_capital_tmn * p.quote_funding_fraction
            self.ledger.convert(
                "USDT",
                budget / (self.rate(first) * (1 + p.fx_fee)),
                self.rate(first),
                p.fx_fee,
                first,
            )
        entry_cutoff = max(events) - timedelta(seconds=self.data.simulation.liquidation_seconds)
        for now, event in sorted(events.items()):
            self.clock.advance(now)
            conversions = self.conversions(now)
            if now >= entry_cutoff:
                for order in self.execution.active():
                    if order.intent.side == "BUY":
                        await self.execution.cancel(order.intent.client_id)
            for pair, _, candle in event["close"]:
                await self.execution.process(
                    candle, False, D(1) if pair.endswith("/TMN") else self.rate(now)
                )
                book = self.data.recorded_quote(pair, now)
                self.mark(
                    pair,
                    max(x.price for x in book.bids)
                    if book
                    else candle.close * (1 - self.data.simulation.half_spread),
                    now,
                )
            # Revalue base inventory when quote FX changes, even without a new base candle.
            for pair, rows in self.data.candles.items():
                visible = [c for c in rows if c.close_time <= now]
                if visible and pair.endswith("/USDT"):
                    book = self.data.recorded_quote(pair, now)
                    self.mark(
                        pair,
                        max(x.price for x in book.bids)
                        if book
                        else visible[-1].close * (1 - self.data.simulation.half_spread),
                        now,
                    )
            self.sample(now)
            snapshots = {
                pair: await self.data.snapshot(pair, now) for pair in sorted(self.data.candles)
            }
            for pair, _, _ in event["close"]:
                if self.decision_start is not None and now < self.decision_start:
                    continue
                if int(now.timestamp()) % self.data.research.entry_seconds:
                    continue
                active = self.execution.active()
                pending = tuple(sorted({o.intent.symbol for o in active}))
                reserved_exposure = sum(
                    (
                        o.reserved * (D(1) if o.intent.symbol.endswith("/TMN") else self.rate(now))
                        for o in active
                        if o.intent.side == "BUY"
                    ),
                    D(0),
                )
                # Conservative: reserve the full remaining notional as open risk.
                portfolio = self.ledger.snapshot(
                    now, self.marks, conversions, pending, reserved_exposure, reserved_exposure
                )
                signal = strategy.evaluate(snapshots[pair], portfolio)
                if signal.action == "SELL":
                    # Protective exit takes priority over an unfinished entry.
                    for order in self.execution.active(pair):
                        if order.intent.side == "BUY":
                            await self.execution.cancel(order.intent.client_id)
                    pending = tuple(sorted({o.intent.symbol for o in self.execution.active()}))
                    portfolio = self.ledger.snapshot(
                        now, self.marks, conversions, pending, reserved_exposure, reserved_exposure
                    )
                # AI is an optional BUY veto. It never mutates the canonical
                # signal or suppresses exits. Risk remains the final gate.
                analysis = None
                if signal.action == "BUY" and self.evaluator is not None:
                    analysis = await self.evaluator.evaluate(signal, snapshots[pair])
                manager = DeterministicRiskEngine(
                    self.risk_parameters, self.data.research, eligibility, snapshots, ("backtest",)
                )
                decision = manager.check(signal, portfolio)
                if signal.action == "BUY" and now >= entry_cutoff:
                    decision = decision.model_copy(
                        update={"allowed": False, "reasons": ("COMPETITION_ENTRY_CUTOFF",)}
                    )
                self.ledger.halted |= decision.halt_new_entries
                if self.ledger.halted:
                    for order in self.execution.active():
                        if order.intent.side == "BUY":
                            await self.execution.cancel(order.intent.client_id)
                record = {
                    "at": now.isoformat(),
                    "signal": signal.model_dump(mode="json"),
                    "risk": decision.model_dump(mode="json"),
                }
                if analysis is not None:
                    record["analysis"] = analysis.model_dump(mode="json")
                self.decisions.append(record)
                if (
                    not decision.allowed
                    or signal.action == "HOLD"
                    or pair in pending
                    or (analysis is not None and analysis.verdict != "ACCEPT")
                ):
                    continue
                identifier = stable_id(record)
                assert decision.reference_price is not None
                atr = signal.atr
                if atr is None:
                    position = self.ledger.positions.get(pair)
                    if position is None:
                        continue
                    atr = (position.take_profit - position.stop_loss) / (
                        self.data.research.stop_atr + self.data.research.target_atr
                    )
                self.execution.plan(
                    identifier,
                    atr,
                    decision.reference_price,
                    D(1) if pair.endswith("/TMN") else self.rate(now),
                )
                intent = OrderIntent(
                    client_id=identifier,
                    decision_id=identifier,
                    account_id="backtest",
                    symbol=pair,
                    side=signal.action,
                    order_type="MARKET",
                    base_quantity=decision.quantity,
                )
                await self.execution.submit(intent)
            for pair, index, candle in event["open"]:
                previous = self.data.candles[pair][index - 1].volume if index else D(0)
                await self.execution.process(
                    candle, True, D(1) if pair.endswith("/TMN") else self.rate(now), previous
                )
                book = self.data.recorded_quote(pair, now)
                self.mark(
                    pair,
                    max(x.price for x in book.bids)
                    if book
                    else candle.open * (1 - self.data.simulation.half_spread),
                    now,
                )
            self.sample(now)
        await self.liquidate(max(events))
        self.sample(max(events))
        from .reports import build_report

        return build_report(self)

    async def liquidate(self, now: datetime) -> None:
        for order in self.execution.active():
            await self.execution.cancel(order.intent.client_id)
        for pair, position in sorted(self.ledger.positions.items()):
            if position.state != "OPEN":
                continue
            market, p = self.data.markets[pair], self.data.simulation
            if pair not in self.approved or not market.spot_enabled or not market.account_enabled:
                self.residuals.append(
                    {
                        "symbol": pair,
                        "quantity": str(position.quantity),
                        "reason": "SPOT_MARKET_NOT_ELIGIBLE",
                    }
                )
                continue
            candle = self.data.candles[pair][-1]
            # Explicit terminal auction assumption, with no fictitious next bar.
            book = self.data.recorded_quote(pair, now)
            best_bid = max(book.bids, key=lambda level: level.price) if book else None
            reference = best_bid.price if best_bid else candle.close * (1 - p.half_spread)
            price = reference * (1 - p.slippage) * (1 - p.terminal_haircut)
            price = (price / market.price_tick).to_integral_value(
                rounding=ROUND_FLOOR
            ) * market.price_tick
            capacity = (
                best_bid.quantity * p.book_participation
                if best_bid
                else candle.volume * p.volume_participation
            )
            consumed = sum(
                (
                    f.base_quantity
                    for o in self.execution.orders.values()
                    for f in o.executions
                    if f.symbol == pair and f.executed_at == now
                ),
                D(0),
            )
            quantity = min(
                position.quantity,
                self.ledger.free(pair.split("/")[0]),
                max(D(0), capacity - consumed),
            )
            quantity = (quantity / market.quantity_step).to_integral_value(
                rounding=ROUND_FLOOR
            ) * market.quantity_step
            if quantity >= market.minimum_quantity and quantity * price >= market.minimum_notional:
                fill = Fill(
                    fill_id=f"terminal:{pair}",
                    client_id=f"terminal:{pair}",
                    symbol=pair,
                    side="SELL",
                    base_quantity=quantity,
                    price=Money(amount=price, currency=market.quote),
                    fee=Money(
                        amount=quantity * price * max(p.exit_fee, market.taker_fee_rate),
                        currency=market.quote,
                    ),
                    executed_at=now,
                )
                atr = (position.take_profit - position.stop_loss) / (
                    self.data.research.stop_atr + self.data.research.target_atr
                )
                self.ledger.apply_fill(fill, D(1) if market.quote == "TMN" else self.rate(now), atr)
            remaining = self.ledger.positions[pair].quantity
            if remaining:
                self.residuals.append(
                    {
                        "symbol": pair,
                        "quantity": str(remaining),
                        "reason": "TERMINAL_VOLUME_OR_MINIMUM_CONSTRAINT",
                    }
                )
        quantity = self.ledger.free("USDT")
        fx_market, book = self.data.fx_market, self.data.recorded_quote("USDT/TMN", now)
        if quantity and fx_market is not None and book is not None:
            best = max(book.bids, key=lambda level: level.price)
            price = (
                best.price
                * (1 - self.data.simulation.slippage)
                * (1 - self.data.simulation.terminal_haircut)
                / fx_market.price_tick
            ).to_integral_value(rounding=ROUND_FLOOR) * fx_market.price_tick
            size = min(quantity, best.quantity * self.data.simulation.book_participation)
            size = (size / fx_market.quantity_step).to_integral_value(
                rounding=ROUND_FLOOR
            ) * fx_market.quantity_step
            fee = max(self.data.simulation.fx_fee, fx_market.taker_fee_rate)
            try:
                validate_spot_order(
                    "USDT/TMN",
                    "SELL",
                    size,
                    price,
                    fx_market,
                    ("USDT/TMN",),
                    {"USDT": quantity},
                    fee,
                )
            except ValueError:
                pass  # Residual explicitly reported below; never fabricate an FX fill.
            else:
                self.ledger.convert("USDT", size, price, fee, now, True)
        quantity = self.ledger.free("USDT")
        if quantity:
            self.residuals.append(
                {
                    "symbol": "USDT/TMN",
                    "quantity": str(quantity),
                    "reason": "NO_VERIFIED_TERMINAL_FX_EXECUTION_ROUTE",
                }
            )
