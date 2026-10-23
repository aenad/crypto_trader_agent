"""Deterministic frame reducer reusing strategy, risk, AI fusion and Decimal ledger."""

from collections.abc import Awaitable
from copy import deepcopy
from datetime import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Context, Decimal, localcontext
from typing import Any, TypeVar
from zoneinfo import ZoneInfo

from quantpilot.backtest.history import HistoricalClock
from quantpilot.backtest.ledger import PortfolioLedger
from quantpilot.config import stable_id
from quantpilot.models import OrderIntent, QuoteConversion
from quantpilot.trading.lifecycle import exit_signal
from quantpilot.trading.risk import DeterministicRiskEngine
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout, validate_series

from .ai import ShadowAI
from .domain import ShadowConfig, ShadowFrame
from .execution import ShadowExecutionProvider
from .state import dump_ledger, dump_orders, load_ledger, load_orders

D = Decimal
T = TypeVar("T")


class ShadowEngine:
    def __init__(self, config: ShadowConfig, ai: ShadowAI):
        self.config, self.ai = config, ai
        self.clock = HistoricalClock(datetime.fromisoformat("1970-01-01T00:00:00+00:00"))
        self.ledger = PortfolioLedger(config.simulation.initial_capital_tmn, config.research)
        self.execution = ShadowExecutionProvider(config, self.ledger, self.clock)
        self.last_decided: dict[str, str] = {}
        self.marks: dict[str, Decimal] = {}
        self.funded = False
        self.last_frame: str | None = None
        self.latest_portfolio: dict[str, Any] | None = None
        self.last_execution_error: dict[str, str] | None = None

    async def _execute(self, operation: str, call: Awaitable[T]) -> T:
        try:
            return await call
        except BaseException as exc:
            self.last_execution_error = {
                "operation": operation,
                "exception_type": type(exc).__name__,
            }
            raise

    def dump(self) -> dict[str, Any]:
        return {
            "ledger": dump_ledger(self.ledger),
            "execution": dump_orders(self.execution),
            "clock": self.clock.now().isoformat(),
            "last_decided": dict(self.last_decided),
            "marks": {k: str(v) for k, v in self.marks.items()},
            "funded": self.funded,
            "last_frame": self.last_frame,
            "portfolio": deepcopy(self.latest_portfolio),
        }

    def restore(self, state: dict[str, Any]) -> None:
        load_ledger(self.ledger, state["ledger"])
        load_orders(self.execution, state["execution"])
        self.clock = HistoricalClock(datetime.fromisoformat(state["clock"]))
        self.execution.clock = self.clock
        self.last_decided = dict(state["last_decided"])
        self.marks = {k: D(v) for k, v in state["marks"].items()}
        self.funded = state["funded"]
        self.last_frame = state["last_frame"]
        self.latest_portfolio = deepcopy(state["portfolio"])

    def fresh(self, frame: ShadowFrame) -> tuple[set[str], bool]:
        now, cfg = frame.as_of, self.config
        fx_needed = any(s.endswith("/USDT") for s in cfg.approved) or cfg.fx_market is not None
        fx_fresh = not fx_needed or (
            cfg.fx_market is not None
            and cfg.fx_market.spot_enabled
            and cfg.fx_market.account_enabled
            and frame.fx_book is not None
            and 0
            <= (now - frame.fx_book.as_of).total_seconds()
            <= min(cfg.freshness_seconds, cfg.risk.max_fx_age_seconds)
        )
        pairs = set()
        for s in frame.snapshots:
            try:
                validate_series(
                    s.candles, cfg.research.entry_seconds, s, cfg.research.max_candle_lag_seconds
                )
                if (
                    s.liquidity is not None
                    and s.market is not None
                    and s.market.spot_enabled
                    and s.market.account_enabled
                    and 0 <= (now - s.liquidity.as_of).total_seconds() <= cfg.freshness_seconds
                    and (s.symbol.endswith("/TMN") or fx_fresh)
                ):
                    pairs.add(s.symbol)
            except ValueError:
                pass
        return pairs, bool(fx_fresh)

    async def apply(self, frame: ShadowFrame) -> dict[str, Any]:
        self.last_execution_error = None
        before = self.dump()
        try:
            with localcontext(Context(prec=34)):
                return await self._apply(frame)
        except BaseException:
            self.restore(before)
            raise

    async def _apply(self, frame: ShadowFrame) -> dict[str, Any]:
        if frame.frame_id == self.last_frame:
            raise ValueError("Duplicate reducer frame")
        if frame.as_of <= self.clock.now():
            raise ValueError("Non-monotonic shadow frame")
        cfg, now = self.config, frame.as_of
        if {s.symbol for s in frame.snapshots} != set(cfg.approved):
            raise ValueError("Incomplete shadow universe")
        markets = {m.symbol: m for m in cfg.markets}
        for snapshot in frame.snapshots:
            expected = markets[snapshot.symbol]
            if snapshot.market is None:
                raise ValueError("Missing shadow market constraints")
            expected = expected.model_copy(
                update={
                    "taker_fee_rate": max(
                        expected.taker_fee_rate, cfg.simulation.entry_fee, cfg.simulation.exit_fee
                    )
                }
            )
            if snapshot.market != expected:
                raise ValueError("Unconfigured market constraints")
        self.clock.advance(now)
        fresh, fx_fresh = self.fresh(frame)
        rates: tuple[QuoteConversion, ...] = ()
        if frame.fx_book is not None:
            rate = max(level.price for level in frame.fx_book.bids)
            rates = (QuoteConversion(quote="USDT", tmn_per_unit=rate, as_of=frame.fx_book.as_of),)
            if fx_fresh:
                self.marks["USDT"] = rate
        settling = cfg.settling(now)
        expired = cfg.expired(now)
        if not self.funded and fx_fresh and not settling:
            if self.ledger.day is None:
                self.ledger.day = now.astimezone(ZoneInfo("Asia/Tehran")).date()
                self.ledger.daily_open = self.ledger.initial
            if rates and cfg.simulation.quote_funding_fraction:
                assert frame.fx_book is not None
                ask = min(level.price for level in frame.fx_book.asks)
                fx_market = cfg.fx_market
                assert fx_market is not None
                fee = max(cfg.simulation.fx_fee, fx_market.taker_fee_rate)
                ask = (
                    ask * (1 + cfg.simulation.slippage) / fx_market.price_tick
                ).to_integral_value(rounding=ROUND_CEILING) * fx_market.price_tick
                budget = cfg.simulation.initial_capital_tmn * cfg.simulation.quote_funding_fraction
                quantity = (budget / (ask * (1 + fee))).next_minus()
                capacity = (
                    min(frame.fx_book.asks, key=lambda level: level.price).quantity
                    * cfg.simulation.book_participation
                )
                quantity = (min(quantity, capacity) / fx_market.quantity_step).to_integral_value(
                    rounding=ROUND_FLOOR
                ) * fx_market.quantity_step
                if (
                    quantity < fx_market.minimum_quantity
                    or quantity * ask < fx_market.minimum_notional
                ):
                    quantity = D(0)
                if quantity > 0:
                    self.ledger.convert("USDT", quantity, ask, fee, now)
            self.funded = True
        snapshots = {s.symbol: s for s in frame.snapshots}
        for pair in sorted(fresh):
            book = snapshots[pair].liquidity
            assert book is not None
            rate = D(1) if pair.endswith("/TMN") else self.marks["USDT"]
            self.marks[pair.split("/")[0]] = max(level.price for level in book.bids) * rate
        await self.execution.expire()
        if len(fresh) != len(cfg.approved) or settling:
            for order in self.execution.active():
                if order.intent.side == "BUY" or expired:
                    await self._execute("cancel", self.execution.cancel(order.intent.client_id))
        # Marked loss stops must cancel previously approved entries BEFORE fills.
        portfolio = self.portfolio(frame, rates)
        equity, day, peak = (
            portfolio.equity_tmn,
            portfolio.daily_open_equity_tmn,
            portfolio.peak_equity_tmn,
        )
        assert equity is not None and day is not None and peak is not None
        if (day - equity) / day >= cfg.risk.daily_loss_fraction or (
            peak - equity
        ) / peak >= cfg.risk.max_drawdown_fraction:
            self.ledger.halted = True
        if self.ledger.halted:
            for order in self.execution.active():
                if order.intent.side == "BUY":
                    await self._execute("cancel", self.execution.cancel(order.intent.client_id))
        for order in self.execution.active():
            position = self.ledger.positions.get(order.intent.symbol)
            snapshot = snapshots[order.intent.symbol]
            if order.intent.side == "BUY" and position is not None and snapshot.candles:
                reason, _ = exit_signal(position, snapshot.candles[-1], None, now, cfg.research)
                if reason:
                    await self._execute("cancel", self.execution.cancel(order.intent.client_id))
        # All fills consume only later, genuinely observed public depth.
        for pair in sorted(fresh):
            await self._execute(
                "fill",
                self.execution.on_book(
                    snapshots[pair], D(1) if pair.endswith("/TMN") else self.marks["USDT"]
                ),
            )
        settlement = []
        if settling and not expired:
            for pair in sorted(fresh):
                settlement.append(
                    await self._execute("settle", self.execution.settle(snapshots[pair]))
                )
            if fx_fresh:
                self.settle_quote(frame)
        strategy = MomentumBreakout(cfg.research, MarketEligibilityFilter(cfg.approved))
        manager = DeterministicRiskEngine(
            cfg.risk, cfg.research, MarketEligibilityFilter(cfg.approved), snapshots, ("shadow",)
        )
        decisions = []
        for pair, snapshot in sorted(snapshots.items()):
            if settling:
                continue
            bar = snapshot.candles[-1].close_time.isoformat() if snapshot.candles else "missing"
            if self.last_decided.get(pair) == bar:
                continue
            portfolio = self.portfolio(frame, rates)
            signal = strategy.evaluate(snapshot, portfolio)
            if signal.action == "SELL":
                for order in self.execution.active(pair):
                    if order.intent.side == "BUY":
                        await self._execute("cancel", self.execution.cancel(order.intent.client_id))
                portfolio = self.portfolio(frame, rates)
            ai = await self.ai.evaluate(signal, snapshot) if pair in fresh else None
            risk = manager.check(signal, portfolio)
            self.ledger.halted |= risk.halt_new_entries
            pending = bool(self.execution.active(pair))
            ai_accept = (
                ai is None
                and cfg.ai_mode == "QUANT_ONLY"
                or ai is not None
                and ai["analysis"]["verdict"] == "ACCEPT"
            )
            if signal.action != "BUY":
                ai_accept = True
            outcome = (
                "PROFILE_ENTRY_BLOCKED"
                if signal.action == "BUY" and not cfg.entries_allowed(now)
                else "STALE"
                if pair not in fresh or (signal.action == "BUY" and len(fresh) != len(cfg.approved))
                else "HOLD"
                if signal.action == "HOLD"
                else "RISK_REJECTED"
                if not risk.allowed
                else "AI_REJECTED"
                if not ai_accept
                else "PENDING_ORDER"
                if pending
                else "ACCEPTED"
            )
            record = {
                "symbol": pair,
                "as_of": now.isoformat(),
                "signal": signal.model_dump(mode="json"),
                "risk": risk.model_dump(mode="json"),
                "ai": ai,
                "outcome": outcome,
                "portfolio_before": portfolio.model_dump(mode="json"),
            }
            decision_id = stable_id(record)
            if outcome == "ACCEPTED":
                assert risk.reference_price is not None
                atr = signal.atr
                if atr is None:
                    position = self.ledger.positions[pair]
                    atr = (position.take_profit - position.stop_loss) / (
                        cfg.research.stop_atr + cfg.research.target_atr
                    )
                self.execution.plan(
                    decision_id,
                    atr,
                    risk.reference_price,
                    D(1) if pair.endswith("/TMN") else self.marks["USDT"],
                )
                await self._execute(
                    "submit",
                    self.execution.submit(
                        OrderIntent(
                            client_id=decision_id,
                            decision_id=decision_id,
                            account_id="shadow",
                            symbol=pair,
                            side=signal.action,
                            order_type="MARKET",
                            base_quantity=risk.quantity,
                        )
                    ),
                )
            decisions.append({"decision_id": decision_id, **record})
            self.last_decided[pair] = bar
        if self.ledger.halted:
            for order in self.execution.active():
                if order.intent.side == "BUY":
                    await self._execute("cancel", self.execution.cancel(order.intent.client_id))
        portfolio = self.portfolio(frame, rates)
        self.latest_portfolio = portfolio.model_dump(mode="json")
        self.last_frame = frame.frame_id
        equity, unrealized, exposure = self.ledger.valuation(self.marks)
        return {
            "frame_id": frame.frame_id,
            "as_of": now.isoformat(),
            "decisions": decisions,
            "portfolio": self.latest_portfolio,
            "equity_tmn": str(equity),
            "realized_pnl_tmn": str(self.ledger.realized),
            "unrealized_pnl_tmn": str(unrealized),
            "fees_tmn": str(self.ledger.fees),
            "exposure_tmn": str(exposure),
            "stale_symbols": sorted(set(cfg.approved) - fresh),
            "valuation_stale": len(fresh) != len(cfg.approved),
            "orders": dump_orders(self.execution),
            "settlement": {
                "phase": "DEADLINE_PASSED" if expired else "LIQUIDATING" if settling else "TRADING",
                "actions": settlement,
                "final_toman_balance_tmn": str(self.ledger.holding("TMN").quantity),
                "net_return_pct": str((equity / self.ledger.initial - 1) * 100),
                "remaining_holdings": {
                    asset: str(h.quantity)
                    for asset, h in sorted(self.ledger.holdings.items())
                    if asset != "TMN" and h.quantity > 0
                },
                "fully_settled": not self.execution.active()
                and all(
                    asset == "TMN" or h.quantity == 0 for asset, h in self.ledger.holdings.items()
                ),
            },
        }

    def settle_quote(self, frame: ShadowFrame) -> None:
        """Virtual FX sale at observed executable bids; retain dust/unavailable liquidity."""
        market, book = self.config.fx_market, frame.fx_book
        if market is None or book is None or not market.spot_enabled or not market.account_enabled:
            return
        digest = stable_id(book.model_dump(mode="json"))
        if self.execution.used_books.get("USDT/TMN") == digest:
            return
        self.execution.used_books["USDT/TMN"] = digest
        best = max(book.bids, key=lambda level: level.price)
        price = (
            best.price * (1 - self.config.simulation.slippage) / market.price_tick
        ).to_integral_value(rounding=ROUND_FLOOR) * market.price_tick
        quantity = min(
            self.ledger.free("USDT"), best.quantity * self.config.simulation.book_participation
        )
        quantity = (quantity / market.quantity_step).to_integral_value(
            rounding=ROUND_FLOOR
        ) * market.quantity_step
        if quantity >= market.minimum_quantity and quantity * price >= market.minimum_notional:
            self.ledger.convert(
                "USDT",
                quantity,
                price,
                max(self.config.simulation.fx_fee, market.taker_fee_rate),
                frame.as_of,
                True,
            )

    def portfolio(self, frame: ShadowFrame, rates: tuple[QuoteConversion, ...]) -> Any:
        active = self.execution.active()
        exposure = sum(
            (
                o.reserved
                * (D(1) if o.intent.symbol.endswith("/TMN") else self.marks.get("USDT", D(0)))
                for o in active
                if o.intent.side == "BUY"
            ),
            D(0),
        )
        return self.ledger.snapshot(
            frame.as_of,
            self.marks,
            rates,
            tuple(sorted({o.intent.symbol for o in active})),
            exposure,
            exposure,
        ).model_copy(update={"account_id": "shadow"})
