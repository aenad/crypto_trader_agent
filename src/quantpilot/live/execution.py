"""Private execution adapter; no strategy/LLM gets its underlying transport."""

import asyncio
import hashlib
import os
from collections.abc import Mapping
from datetime import datetime
from decimal import Context, Decimal, localcontext
from pathlib import Path
from typing import Protocol
from zoneinfo import ZoneInfo

from pydantic import SecretStr

from quantpilot.ai.fusion import HybridEvaluator
from quantpilot.config import stable_id
from quantpilot.interfaces import Clock
from quantpilot.lifecycle import LifecycleManager
from quantpilot.models import (
    AssetBalance,
    Fill,
    MarketSnapshot,
    OrderIntent,
    OrderState,
    PortfolioState,
    Signal,
)
from quantpilot.spot import validate_spot_order
from quantpilot.trading.lifecycle import apply_simulated_fill
from quantpilot.trading.risk import DeterministicRiskEngine, rounded
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

from .domain import (
    TERMINAL,
    AccountAuthorization,
    Blocked,
    ExchangeOrder,
    LiveConfig,
    OrderRecord,
    credential_fingerprint,
)
from .storage import LiveStore
from .transport import ID, WallexSpotREST, decimal

D = Decimal


class SpotExchange(Protocol):
    async def verify_account_context(self, selector: str) -> None: ...
    async def close(self) -> None: ...
    async def submit(self, intent: OrderIntent) -> ExchangeOrder: ...
    async def lookup(self, intent: OrderIntent) -> ExchangeOrder: ...
    async def cancel(self, intent: OrderIntent) -> None: ...
    async def balances(self, semantics: str) -> tuple[AssetBalance, ...]: ...
    async def open_ids(self) -> frozenset[str]: ...
    async def markets(self) -> dict[str, object]: ...
    async def fees(self) -> dict[str, object]: ...


def require_activation(
    config: LiveConfig,
    grant: AccountAuthorization,
    now: datetime,
    environ: Mapping[str, str],
) -> SecretStr:
    """Exactly one dedicated env credential; separate authorization file binds its fingerprint."""
    if not config.enabled or environ.get("QUANTPILOT_LIVE_AUTHORIZATION") != config.config_id:
        raise Blocked("LIVE_DISABLED")
    if grant.config_id != config.config_id or grant.account_id != config.account_id:
        raise Blocked("AUTHORIZATION_SCOPE_MISMATCH")
    if (
        grant.account_type != config.account_type
        or grant.sub_account_client_id != config.sub_account_client_id
    ):
        raise Blocked("AUTHORIZATION_ACCOUNT_CONTEXT_MISMATCH")
    if config.account_type == "CREDIT_SPOT" and grant.balance_value_semantics != "FREE":
        raise Blocked("CREDIT_AVAILABLE_BALANCE_SEMANTICS_REQUIRED")
    if not grant.valid_from <= now < grant.expires_at or (
        config.deadline is not None and grant.expires_at < config.deadline
    ):
        raise Blocked("AUTHORIZATION_EXPIRED_OR_TOO_SHORT")
    if not (grant.spot_read and grant.spot_trade and grant.withdrawal_disabled):
        raise Blocked("ACCOUNT_PERMISSIONS_NOT_APPROVED")
    key = SecretStr(environ.get("QUANTPILOT_WALLEX_LIVE_API_KEY", ""))
    if not key.get_secret_value() or credential_fingerprint(key) != grant.credential_sha256:
        raise Blocked("CREDENTIAL_SCOPE_MISMATCH")
    return key


def activated_adapter(
    config: LiveConfig,
    grant: AccountAuthorization,
    store: LiveStore,
    clock: Clock,
    environ: Mapping[str, str] | None = None,
) -> "ProtectedExecution":
    env = os.environ if environ is None else environ
    key = require_activation(config, grant, clock.now(), env)

    def authorize_wire_mutation(method: str, identity: str) -> None:
        require_activation(config, grant, clock.now(), env)
        record = store.order(identity)
        required_phase = "SUBMITTING" if method == "POST" else "CANCELING"
        if record is None or record.phase != required_phase:
            raise Blocked("DURABLE_MUTATION_AUTHORIZATION_REQUIRED")
        if method == "POST":
            if store.get("kill") is not None or store.kill_path.exists():
                raise Blocked("KILL_SWITCH_ACTIVE")
            if store.get("suspended") is not None and record.intent.side == "BUY":
                raise Blocked("TRADING_SUSPENDED")
            if config.expired(clock.now()):
                raise Blocked("CHALLENGE_DEADLINE_PASSED")

    if config.sub_account_client_id is not None:
        exchange = WallexSpotREST(
            key,
            authorize_mutation=authorize_wire_mutation,
            sub_account_client_id=SecretStr(config.sub_account_client_id),
        )
    else:
        exchange = WallexSpotREST(key, authorize_mutation=authorize_wire_mutation)
    return ProtectedExecution(config, grant, store, clock, exchange, env)


class ProtectedExecution:
    """ExecutionProvider implementation, gated by fresh same-core risk authorization.

    Initialization/recovery is read-only. Restart never auto-resumes trading. Unknown results
    keep their client IDs forever and are resolved by GET only, including after a 404.
    """

    def __init__(
        self,
        config: LiveConfig,
        grant: AccountAuthorization,
        store: LiveStore,
        clock: Clock,
        exchange: SpotExchange,
        environ: Mapping[str, str],
    ):
        self.config, self.grant, self.store = config, grant, store
        self.clock, self._exchange, self._env = clock, exchange, environ
        self._lock = asyncio.Lock()
        self._reconciled: datetime | None = None
        self._snapshots: dict[str, MarketSnapshot] = {}
        self._authorizations: dict[str, tuple[OrderIntent, Decimal, str]] = {}
        self._entry_signals: dict[str, Signal] = {}
        self._ai_approvals: dict[str, OrderIntent] = {}
        self._maximum_quantities: dict[str, Decimal | None] = {}
        require_activation(config, grant, clock.now(), environ)
        if store.get("config") != config.config_id:
            raise Blocked("STORE_SCOPE_MISMATCH")
        binding = stable_id(
            [
                grant.account_id,
                grant.account_type,
                grant.credential_sha256,
                grant.balance_value_semantics,
                grant.sub_account_client_id,
            ]
        )
        previous = store.get("account_binding")
        if previous is not None and previous != binding:
            raise Blocked("ACCOUNT_BINDING_CHANGED")
        root = Path(__file__).resolve().parents[1]
        implementation = stable_id(
            [
                (
                    str(path.relative_to(root)).replace("\\", "/"),
                    hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest(),
                )
                for path in sorted(root.rglob("*.py"))
            ]
        )
        old_implementation = store.get("implementation")
        if old_implementation is not None and old_implementation != implementation:
            raise Blocked("EXECUTION_IMPLEMENTATION_CHANGED")
        with store.db:
            self.lifecycle = LifecycleManager(store)
            store.set("account_binding", binding)
            store.set("implementation", implementation)
            store.audit(
                "ACTIVATION_SCOPE_CHECKED",
                {
                    "config_id": config.config_id,
                    "account_id": grant.account_id,
                    "account_type": grant.account_type,
                    "evidence_reference": grant.evidence_reference,
                    "valid_from": grant.valid_from.isoformat(),
                    "expires_at": grant.expires_at.isoformat(),
                    "as_of": clock.now().isoformat(),
                    "implementation_id": implementation,
                },
            )

    async def close(self) -> None:
        """Close transport resources; caller owns the execution journal lifetime."""
        with self.store.db:
            self.lifecycle.command("GRACEFUL_SHUTDOWN")
        await self._exchange.close()
        with self.store.db:
            self.lifecycle.stopped()

    def _clear_authorizations(self) -> None:
        self._authorizations.clear()
        self._entry_signals.clear()
        self._ai_approvals.clear()

    def revoke_authorization(self, client_id: str) -> None:
        self._authorizations.pop(client_id, None)
        self._entry_signals.pop(client_id, None)
        self._ai_approvals.pop(client_id, None)

    async def evaluate_entry(self, intent: OrderIntent, evaluator: HybridEvaluator) -> bool:
        """Bind hybrid acceptance to the exact risk-authorized intent and market cut."""
        signal = self._entry_signals.get(intent.client_id)
        grant = self._authorizations.get(intent.client_id)
        if (
            intent.side != "BUY"
            or signal is None
            or grant is None
            or grant[0] != intent
            or self.config.ai.mode == "QUANT_ONLY"
            or evaluator.mode != self.config.ai.mode
            or evaluator.model.metadata.get("live_enabled") is not True
        ):
            raise Blocked("HYBRID_ENTRY_CONTEXT_REQUIRED")
        self._validate_intent(intent, False)
        snapshot = self._market_context(intent.symbol)
        try:
            analysis = await evaluator.evaluate(signal, snapshot)
            if (
                self._authorizations.get(intent.client_id) != grant
                or self._entry_signals.get(intent.client_id) != signal
            ):
                raise Blocked("HYBRID_CONTEXT_CHANGED")
            self._validate_intent(intent, False)
            with self.store.db:
                self.store.audit(
                    "HYBRID_EVALUATION",
                    {
                        "client_id": intent.client_id,
                        "signal_id": stable_id(signal.model_dump(mode="json")),
                        "analysis": analysis.model_dump(mode="json"),
                        "candidate": evaluator.recommendations[-1].model_dump(mode="json"),
                    },
                )
            if analysis.verdict != "ACCEPT":
                self.revoke_authorization(intent.client_id)
                return False
            self._ai_approvals[intent.client_id] = intent
            return True
        except BaseException:
            self.revoke_authorization(intent.client_id)
            raise

    def control(self, operation: str) -> None:
        with self.store.db:
            self.lifecycle.command(operation)
            self._clear_authorizations()
            self.store.audit("LIFECYCLE_CONTROL", {"operation": operation})

    def _gate(self, *, allow_suspension: bool = False, cancel_only: bool = False) -> None:
        require_activation(self.config, self.grant, self.clock.now(), self._env)
        if (
            self.store.get("kill") is not None or self.store.kill_path.exists()
        ) and not cancel_only:
            raise Blocked("KILL_SWITCH_ACTIVE")
        if not allow_suspension and self.store.get("suspended") is not None:
            raise Blocked("TRADING_SUSPENDED")

    def kill(self) -> None:
        self._clear_authorizations()
        self.store.kill_path.touch(exist_ok=True)
        self.store.latch("OPERATOR_KILL", kill=True)

    def _fresh(self, at: datetime) -> None:
        if not 0 <= (self.clock.now() - at).total_seconds() <= self.config.max_age_seconds:
            raise Blocked("STALE_EXECUTION_CONTEXT")

    def _market_context(self, symbol: str) -> MarketSnapshot:
        if symbol not in self.config.approved or symbol not in self._snapshots:
            raise Blocked("MARKET_NOT_APPROVED_OR_MISSING")
        snapshot = self._snapshots[symbol]
        self._fresh(snapshot.as_of)
        if snapshot.liquidity is None or snapshot.market is None:
            raise Blocked("MISSING_EXECUTION_CONTEXT")
        self._fresh(snapshot.liquidity.as_of)
        if snapshot.market != next(m for m in self.config.markets if m.symbol == symbol):
            raise Blocked("MARKET_CONSTRAINTS_MISMATCH")
        return snapshot

    async def bootstrap(self) -> None:
        """Adopt only an empty dedicated main-spot account funded with the exact Toman budget."""
        async with self._lock:
            if self.config.sub_account_client_id is not None:
                await self._exchange.verify_account_context(self.config.sub_account_client_id)
            if self.store.portfolio() is not None:
                raise Blocked("ALREADY_INITIALIZED")
            balances = await self._exchange.balances(self.grant.balance_value_semantics)
            if (
                await self._exchange.open_ids()
                or any(
                    b.reserved
                    or b.free != (self.config.capital_tmn if b.currency == "TMN" else D(0))
                    for b in balances
                )
                or not any(b.currency == "TMN" for b in balances)
            ):
                raise Blocked("DEDICATED_CASH_ONLY_ACCOUNT_REQUIRED")
            portfolio = PortfolioState(
                account_id=self.config.account_id,
                as_of=self.clock.now(),
                balances=balances,
                equity_tmn=self.config.capital_tmn,
                peak_equity_tmn=self.config.capital_tmn,
                daily_open_equity_tmn=self.config.capital_tmn,
                trading_day=self.clock.now().astimezone(ZoneInfo("Asia/Tehran")).date(),
            )
            with self.store.db:
                self.store.set("portfolio", portfolio.model_dump_json())
                self.store.audit(
                    "BOOTSTRAP",
                    {"account": self.config.account_id, "as_of": self.clock.now().isoformat()},
                )

    def _apply(self, record: OrderRecord, observed: ExchangeOrder) -> PortfolioState:
        portfolio = self.store.portfolio()
        if portfolio is None:
            raise Blocked("ACCOUNT_NOT_INITIALIZED")
        previous = {f.fill_id: f for f in record.fills}
        current = {f.fill_id: f for f in observed.fills}
        if not previous.keys() <= current.keys() or any(
            current[k] != f for k, f in previous.items()
        ):
            raise Blocked("FILL_HISTORY_CHANGED")
        if observed.executed_quantity < record.executed_quantity:
            raise Blocked("EXECUTED_QUANTITY_REGRESSED")
        if record.state in TERMINAL and observed.state != record.state:
            raise Blocked("TERMINAL_STATE_REGRESSED")
        amounts = {b.currency: b.free + b.reserved for b in portfolio.balances}
        positions = {p.symbol: p for p in portfolio.positions if p.state == "OPEN"}
        for fill in observed.fills:
            if fill.fill_id in previous:
                continue
            if fill.executed_at > self.clock.now():
                raise Blocked("FUTURE_EXCHANGE_FILL")
            base, quote = fill.symbol.split("/")
            if fill.fee.currency not in (base, quote):
                raise Blocked("UNSUPPORTED_FEE_ASSET")
            fee_notional = fill.fee.amount * (fill.price.amount if fill.fee.currency == base else 1)
            fee_cap = min(
                self.config.max_fee_rate,
                next(m.taker_fee_rate for m in self.config.markets if m.symbol == fill.symbol),
            )
            if fee_notional > fill.base_quantity * fill.price.amount * fee_cap:
                raise Blocked("UNEXPECTED_FEE_RATE")
            sign = 1 if fill.side == "BUY" else -1
            amounts[base] = amounts.get(base, D(0)) + sign * fill.base_quantity
            amounts[quote] = (
                amounts.get(quote, D(0)) - sign * fill.base_quantity * fill.price.amount
            )
            amounts[fill.fee.currency] -= fill.fee.amount
            if any(value < 0 for value in amounts.values()):
                raise Blocked("NEGATIVE_RECONSTRUCTED_BALANCE")
            # This existing pure domain reducer handles real input fills too; no fill simulation.
            position = apply_simulated_fill(
                positions.get(fill.symbol), fill, record.atr, self.config.research
            )
            if position.state == "CLOSED":
                positions.pop(fill.symbol, None)
            else:
                positions[fill.symbol] = position
        return PortfolioState.model_validate(
            {
                **portfolio.model_dump(),
                "as_of": self.clock.now(),
                "positions": tuple(positions.values()),
                "balances": tuple(
                    AssetBalance(currency=k, free=v, reserved=D(0))
                    for k, v in sorted(amounts.items())
                ),
            }
        )

    def _observe(self, record: OrderRecord, observed: ExchangeOrder) -> OrderState:
        with localcontext(Context(prec=34)):
            portfolio = self._apply(record, observed)
        updated = OrderRecord.model_validate(
            {
                **record.model_dump(),
                **observed.model_dump(),
                "phase": "OBSERVED",
                "updated_at": self.clock.now(),
            }
        )
        self.store.save(updated, portfolio)  # Fill dedup, positions and order commit atomically.
        self._reconciled = None
        return updated.state

    def _unknown(self, record: OrderRecord) -> None:
        self._reconciled = None
        self._clear_authorizations()
        record = self.store.order(record.intent.client_id) or record
        self.store.save(
            record.model_copy(
                update={
                    "state": OrderState.UNKNOWN,
                    "phase": "UNCERTAIN",
                    "updated_at": self.clock.now(),
                }
            )
        )
        self.store.latch("UNRELIABLE_ORDER_STATE")

    async def _lookup(self, record: OrderRecord) -> OrderState:
        try:
            return self._observe(record, await self._exchange.lookup(record.intent))
        except Exception:
            self._unknown(record)
            raise Blocked("ORDER_RECONCILIATION_REQUIRED") from None

    async def lookup(self, client_id: str) -> OrderState:
        async with self._lock:
            record = self.store.order(client_id)
            if record is None:
                raise Blocked("UNKNOWN_LOCAL_ORDER")
            return await self._lookup(record)

    async def fills(self, client_id: str) -> tuple[Fill, ...]:
        record = self.store.order(client_id)
        if record is None:
            raise Blocked("UNKNOWN_LOCAL_ORDER")
        return record.fills  # Explicitly cached; lookup/recover obtains fresh exchange evidence.

    async def cancel(self, client_id: str) -> OrderState:
        async with self._lock:
            self._gate(allow_suspension=True, cancel_only=True)
            record = self.store.order(client_id)
            if record is None:
                raise Blocked("UNKNOWN_LOCAL_ORDER")
            # Never resend a cancel whose response is ambiguous. First resolve it with GET.
            if record.state == OrderState.UNKNOWN or record.phase in {"SUBMITTING", "CANCELING"}:
                return await self._lookup(record)
            if record.state in TERMINAL:
                return record.state
            record = record.model_copy(
                update={"phase": "CANCELING", "updated_at": self.clock.now()}
            )
            self.store.save(record)
            self._reconciled = None
            self._clear_authorizations()
            try:
                await self._exchange.cancel(record.intent)
                return await self._lookup(record)  # Cancellation can race with the final fill.
            except Exception:
                self._unknown(record)
                raise Blocked("CANCEL_RECONCILIATION_REQUIRED") from None

    async def recover(self, snapshots: tuple[MarketSnapshot, ...], attempts: int = 3) -> None:
        """Bounded read retries/backoff. Successful reconciliation does not clear a latched halt."""
        async with self._lock:
            self._clear_authorizations()
            self._reconciled = None
            self._snapshots = {s.symbol: s for s in snapshots}
            if len(self._snapshots) != len(snapshots) or not 1 <= attempts <= 5:
                raise Blocked("INVALID_RECOVERY_INPUT")
            for attempt in range(attempts):
                try:
                    await self._reconcile()
                    return
                except Exception:
                    self._reconciled = None
                    if attempt + 1 == attempts:
                        self.store.latch("RECONCILIATION_FAILED")
                        raise Blocked("RECONCILIATION_FAILED") from None
                    await asyncio.sleep(min(0.1 * 2**attempt, 1))

    async def _reconcile(self) -> None:
        if self.config.sub_account_client_id is not None:
            await self._exchange.verify_account_context(self.config.sub_account_client_id)
        for record in self.store.orders():
            if record.state not in TERMINAL or record.phase != "OBSERVED":
                await self._lookup(record)
        portfolio = self.store.portfolio()
        if portfolio is None:
            raise Blocked("ACCOUNT_NOT_INITIALIZED")
        markets, fees = await self._exchange.markets(), await self._exchange.fees()
        for market in self.config.markets:
            symbol = market.symbol.replace("/", "")
            row, fee = markets[symbol], fees[symbol]
            if not isinstance(row, dict) or not isinstance(fee, dict):
                raise Blocked("INVALID_MARKET_METADATA")
            if (
                row.get("symbol") != symbol
                or row.get("baseAsset") != market.symbol.split("/")[0]
                or row.get("quoteAsset") != "TMN"
            ):
                raise Blocked("MARKET_IDENTITY_CHANGED")
            if not market.spot_enabled or not market.account_enabled:
                raise Blocked("MARKET_PERMISSION_DENIED")
            step, tick = row["stepSize"], row["tickSize"]
            if (
                type(step) is not int
                or type(tick) is not int
                or not 0 <= step <= 18
                or not 0 <= tick <= 18
            ):
                raise Blocked("INVALID_PRECISION_METADATA")
            if (
                D(10) ** -step != market.quantity_step
                or D(10) ** -tick != market.price_tick
                or decimal(row["minQty"]) != market.minimum_quantity
                or decimal(row["minNotional"]) != market.minimum_notional
                or max(decimal(fee["takerFeeRate"]), decimal(fee["makerFeeRate"]))
                > market.taker_fee_rate
                or market.taker_fee_rate > self.config.max_fee_rate
            ):
                raise Blocked("MARKET_LIMITS_OR_FEES_CHANGED")
            # The verified endpoint may omit a venue maximum. Do not invent one;
            # risk, local fee-aware caps and executable depth remain mandatory.
            self._maximum_quantities[market.symbol] = (
                decimal(row["maxQty"]) if "maxQty" in row else None
            )
        active = {r.intent.client_id for r in self.store.orders() if r.state not in TERMINAL}
        if await self._exchange.open_ids() != active:
            raise Blocked("EXTERNAL_OR_MISSING_OPEN_ORDERS")
        actual = await self._exchange.balances(self.grant.balance_value_semantics)
        expected = {b.currency: b.free + b.reserved for b in portfolio.balances}
        observed = {b.currency: b.free + b.reserved for b in actual}
        if len(observed) != len(actual) or any(
            expected.get(k, D(0)) != observed.get(k, D(0))
            for k in expected.keys() | observed.keys()
        ):
            raise Blocked("EXCHANGE_BALANCE_MISMATCH")
        expected_locked: dict[str, Decimal] = {}
        for record in self.store.orders():
            if record.state in TERMINAL:
                continue
            intent = record.intent
            remaining = intent.base_quantity - record.executed_quantity
            asset = "TMN" if intent.side == "BUY" else intent.symbol.split("/")[0]
            assert intent.limit_price is not None
            amount = remaining * (intent.limit_price if intent.side == "BUY" else 1)
            expected_locked[asset] = expected_locked.get(asset, D(0)) + amount
        for balance in actual:
            minimum = expected_locked.get(balance.currency, D(0))
            if not minimum <= balance.reserved <= minimum * (1 + self.config.max_fee_rate):
                raise Blocked("UNEXPLAINED_LOCKED_BALANCE")
        for position in portfolio.positions:
            if position.quantity != observed.get(position.symbol.split("/")[0], D(0)):
                raise Blocked("POSITION_INVENTORY_MISMATCH")
        for symbol in self.config.approved:
            self._market_context(symbol)
        now = self.clock.now()
        # Align the decision cut with the newly observed account. Preserve book/candle times.
        self._snapshots = {
            symbol: snapshot.model_copy(update={"as_of": now})
            for symbol, snapshot in self._snapshots.items()
        }
        equity = observed.get("TMN", D(0))
        exposure = D(0)
        for position in portfolio.positions:
            book = self._market_context(position.symbol).liquidity
            assert book is not None
            value = position.quantity * max(level.price for level in book.bids)
            exposure += value
        equity += exposure
        peak = max(portfolio.peak_equity_tmn or self.config.capital_tmn, equity)
        day = now.astimezone(ZoneInfo("Asia/Tehran")).date()
        day_open = equity if day != portfolio.trading_day else portfolio.daily_open_equity_tmn
        assert day_open is not None
        halted = (
            1 - equity / peak >= self.config.risk.max_drawdown_fraction
            or 1 - equity / day_open >= self.config.risk.daily_loss_fraction
        )
        updated = PortfolioState.model_validate(
            {
                **portfolio.model_dump(),
                "as_of": now,
                "balances": actual,
                "equity_tmn": equity,
                "peak_equity_tmn": peak,
                "daily_open_equity_tmn": day_open,
                "trading_day": day,
                "gross_exposure_tmn": exposure,
                "pending_symbols": tuple(
                    sorted(
                        {r.intent.symbol for r in self.store.orders() if r.state not in TERMINAL}
                    )
                ),
                "risk_halted": halted or portfolio.risk_halted,
            }
        )
        with self.store.db:
            self.store.set("portfolio", updated.model_dump_json())
            self.store.audit(
                "RECONCILED",
                {
                    "as_of": now.isoformat(),
                    "equity_tmn": str(equity),
                    "active_order_ids": sorted(active),
                },
            )
        if halted:
            self.store.latch("DRAWDOWN_OR_DAILY_LOSS")
        self._reconciled = now

    def resume_after_reconciliation(self) -> None:
        """Explicit operator action. Never clear kill or drawdown latches through recovery."""
        self._gate(allow_suspension=True)
        if self._reconciled is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        self._fresh(self._reconciled)
        portfolio = self.store.portfolio()
        if portfolio is None or portfolio.risk_halted:
            raise Blocked("RISK_SUSPENSION_LATCHED")
        with self.store.db:
            self.lifecycle.resume(
                reconciled=True,
                orders_known=all(
                    r.state != OrderState.UNKNOWN and r.phase not in {"SUBMITTING", "CANCELING"}
                    for r in self.store.orders()
                ),
                risk_ok=True,
                authorized=True,
            )
            self.store.db.execute("DELETE FROM live_meta WHERE key='suspended'")
            self.store.audit("OPERATOR_RESUME", {"as_of": self.clock.now().isoformat()})

    def health(self) -> dict[str, object]:
        """Secret-free operational status; does not imply remote account identity verification."""
        fresh = (
            self._reconciled is not None
            and 0
            <= (self.clock.now() - self._reconciled).total_seconds()
            <= self.config.max_age_seconds
        )
        return {
            "mode": "LIVE",
            "operating_profile": self.config.operating_profile.value,
            "lifecycle": self.lifecycle.state.value,
            "config_id": self.config.config_id,
            "reconciled": fresh,
            "kill": self.store.get("kill") is not None or self.store.kill_path.exists(),
            "suspension": self.store.get("suspended"),
            "unknown_orders": sum(r.state == OrderState.UNKNOWN for r in self.store.orders()),
            "ready": fresh
            and self.lifecycle.permits("BUY")
            and not self.store.get("kill")
            and not self.store.kill_path.exists()
            and not self.store.get("suspended"),
        }

    def settlement_report(self) -> dict[str, object]:
        """No network calls; only reconciled balances and verified journal fills."""
        from .settlement import settlement_report

        if self._reconciled is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        self._fresh(self._reconciled)
        portfolio = self.store.portfolio()
        if portfolio is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        marks = {}
        for position in portfolio.positions:
            if position.state == "OPEN":
                snapshot = self._market_context(position.symbol)
                assert snapshot.liquidity is not None
                marks[position.symbol.split("/")[0]] = max(
                    level.price for level in snapshot.liquidity.bids
                )
        records = self.store.orders()
        try:
            report = settlement_report(
                portfolio,
                [fill for record in records for fill in record.fills],
                marks,
                self.config.capital_tmn,
                sum(r.state not in TERMINAL for r in records),
            )
            report["as_of"] = self._reconciled.isoformat()
            report["competition_complete"] = self.config.expired(self.clock.now()) and bool(
                report["fully_settled_tmn"]
            )
            return report
        except ValueError as exc:
            raise Blocked(str(exc)) from None

    def decision_context(self) -> tuple[tuple[MarketSnapshot, ...], PortfolioState]:
        """Aligned immutable account/market cut for canonical external strategy evaluation."""
        if self._reconciled is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        self._fresh(self._reconciled)
        portfolio = self.store.portfolio()
        if portfolio is None:
            raise Blocked("ACCOUNT_NOT_INITIALIZED")
        return tuple(self._snapshots.values()), portfolio

    def authorize(self, signal: Signal, client_id: str) -> OrderIntent:
        """Only same-core recomputed risk can authorize an entry; no AI/tool bypass."""
        self._gate(allow_suspension=signal.action == "SELL")
        if not self.lifecycle.permits(signal.action):
            raise Blocked("LIFECYCLE_NOT_RUNNING")
        if not ID.fullmatch(client_id):
            raise Blocked("INVALID_CLIENT_ID")
        if signal.action == "BUY" and not self.config.entries_allowed(self.clock.now()):
            raise Blocked("LIQUIDATION_WINDOW")
        portfolio = self.store.portfolio()
        if portfolio is None or self._reconciled is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        self._fresh(self._reconciled)
        self._fresh(signal.as_of)
        snapshot = self._market_context(signal.symbol)
        eligibility = MarketEligibilityFilter(self.config.approved)
        risk = DeterministicRiskEngine(
            self.config.risk,
            self.config.research,
            eligibility,
            self._snapshots,
            (self.config.account_id,),
        )
        decision = risk.check(signal, portfolio)
        with self.store.db:
            self.store.audit(
                "RISK_DECISION",
                {
                    "signal": signal.model_dump(mode="json"),
                    "risk": decision.model_dump(mode="json"),
                    "snapshot": snapshot.model_dump(mode="json"),
                    "portfolio": portfolio.model_dump(mode="json"),
                },
            )
        if not decision.allowed or signal.action not in {"BUY", "SELL"}:
            raise Blocked("DETERMINISTIC_RISK_REJECTED")
        assert snapshot.market is not None and snapshot.liquidity is not None
        # Keep the LIMIT no worse than the Risk Engine's adverse execution reference.
        price = (
            min(x.price for x in snapshot.liquidity.asks)
            if signal.action == "BUY"
            else max(x.price for x in snapshot.liquidity.bids)
        )
        price = rounded(price, snapshot.market.price_tick, up=signal.action == "BUY")
        quantity = decision.quantity
        if signal.action == "SELL":
            quantity = rounded(
                quantity / (1 + self.config.max_fee_rate), snapshot.market.quantity_step
            )
        if (
            quantity < snapshot.market.minimum_quantity
            or quantity * price < snapshot.market.minimum_notional
        ):
            raise Blocked("RISK_APPROVED_QUANTITY_BELOW_EXECUTION_MINIMUM")
        intent = OrderIntent(
            client_id=client_id,
            decision_id=stable_id(
                [signal.model_dump(mode="json"), decision.model_dump(mode="json")]
            ),
            account_id=self.config.account_id,
            symbol=signal.symbol,
            side=signal.action,
            order_type="LIMIT",
            base_quantity=quantity,
            limit_price=price,
        )
        self._authorizations[client_id] = (intent, signal.atr or D(1), "STRATEGY")
        self._ai_approvals.pop(client_id, None)
        if signal.action == "BUY":
            self._entry_signals[client_id] = signal
        return intent

    def _validate_intent(self, intent: OrderIntent, liquidation: bool) -> None:
        self._gate(allow_suspension=liquidation or intent.side == "SELL")
        if not liquidation and not self.lifecycle.permits(intent.side):
            raise Blocked("LIFECYCLE_NOT_RUNNING")
        if self._reconciled is None:
            raise Blocked("RECONCILIATION_REQUIRED")
        self._fresh(self._reconciled)
        if self.config.expired(self.clock.now()):
            raise Blocked("CHALLENGE_DEADLINE_PASSED")
        snapshot = self._market_context(intent.symbol)
        market, book = snapshot.market, snapshot.liquidity
        assert market is not None and book is not None
        if intent.account_id != self.config.account_id or intent.order_type != "LIMIT":
            raise Blocked("INVALID_ORDER_SCOPE")
        q, price = intent.base_quantity, intent.limit_price
        assert price is not None
        if (
            q % market.quantity_step
            or price % market.price_tick
            or q < market.minimum_quantity
            or q * price < market.minimum_notional
        ):
            raise Blocked("ORDER_SIZE_OR_PRECISION")
        maximum = self._maximum_quantities.get(intent.symbol, D(0))
        if maximum is not None and q > maximum:
            raise Blocked("MAXIMUM_ORDER_QUANTITY")
        if (
            intent.side == "BUY"
            and self.config.max_order_tmn is not None
            and q * price * (1 + self.config.max_fee_rate) > self.config.max_order_tmn
        ):
            raise Blocked("ORDER_BUDGET_EXCEEDED")
        base = intent.symbol.split("/")[0]
        portfolio = self.store.portfolio()
        assert portfolio is not None
        if any(r.state not in TERMINAL for r in self.store.orders()):
            raise Blocked("OUTSTANDING_ORDER_MUST_RESOLVE_FIRST")
        free = {b.currency: b.free for b in portfolio.balances}
        if intent.side == "BUY":
            if q * price * (1 + self.config.max_fee_rate) > free.get("TMN", D(0)):
                raise Blocked("INSUFFICIENT_FREE_BALANCE")
        elif q * (1 + self.config.max_fee_rate) > free.get(base, D(0)):
            # Reserve even a possible base-asset fee. Final liquidation reports residual dust.
            raise Blocked("INSUFFICIENT_BASE_WITH_FEE_BUFFER")
        try:
            validate_spot_order(
                intent.symbol,
                intent.side,
                q,
                price,
                market,
                self.config.approved,
                free,
                self.config.max_fee_rate,
                reserve_base_fee=True,
            )
        except ValueError as exc:
            raise Blocked(str(exc)) from None
        levels = book.asks if intent.side == "BUY" else book.bids
        best = (
            min(x.price for x in levels) if intent.side == "BUY" else max(x.price for x in levels)
        )
        if abs(price / best - 1) > self.config.max_slippage:
            raise Blocked("LIMIT_OUTSIDE_SLIPPAGE_BOUND")
        depth = sum(
            (
                x.quantity
                for x in levels
                if (x.price <= price if intent.side == "BUY" else x.price >= price)
            ),
            D(0),
        )
        if q > depth * self.config.max_depth_fraction:
            raise Blocked("INSUFFICIENT_EXECUTABLE_DEPTH")

    async def submit(self, intent: OrderIntent) -> OrderState:
        async with self._lock:
            existing = self.store.order(intent.client_id)
            if existing is not None:
                if existing.intent != intent:
                    raise Blocked("CLIENT_ID_REUSED_WITH_DIFFERENT_INTENT")
                # Even PREPARED is never resent automatically: operator creates a new reviewed ID.
                return existing.state
            grant = self._authorizations.pop(intent.client_id, None)
            self._entry_signals.pop(intent.client_id, None)
            ai_approval = self._ai_approvals.pop(intent.client_id, None)
            if grant is None or grant[0] != intent:
                raise Blocked("ORDER_NOT_AUTHORIZED")
            if (
                intent.side == "BUY"
                and self.config.ai.mode != "QUANT_ONLY"
                and ai_approval != intent
            ):
                raise Blocked("HYBRID_ACCEPTANCE_REQUIRED")
            liquidation = grant[2] == "FINAL_LIQUIDATION"
            self._validate_intent(intent, liquidation)
            record = OrderRecord(
                intent=intent, atr=grant[1], updated_at=self.clock.now(), purpose=grant[2]
            )
            self.store.save(record)
            record = record.model_copy(update={"phase": "SUBMITTING"})
            self.store.save(record)  # Durable uncertain-send boundary BEFORE any network await.
            self._reconciled = None
            self._clear_authorizations()
            try:
                return self._observe(record, await self._exchange.submit(intent))
            except asyncio.CancelledError:
                self._unknown(record)
                raise
            except Exception:
                self._unknown(record)
                raise Blocked("SUBMISSION_RESULT_AMBIGUOUS") from None

    async def strategy_cycle(
        self, snapshots: tuple[MarketSnapshot, ...]
    ) -> tuple[OrderIntent, ...]:
        """Read/reconcile and propose only. An execution service must explicitly submit intents."""
        await self.recover(snapshots)
        portfolio = self.store.portfolio()
        assert portfolio is not None
        strategy = MomentumBreakout(
            self.config.research, MarketEligibilityFilter(self.config.approved)
        )
        result = []
        for snapshot in self._snapshots.values():
            signal = strategy.evaluate(snapshot, portfolio)
            identity = (
                "qp-" + stable_id([self.config.config_id, signal.model_dump(mode="json")])[:48]
            )
            try:
                result.append(self.authorize(signal, identity))
            except Blocked as exc:
                with self.store.db:
                    self.store.audit(
                        "STRATEGY_SKIPPED", {"symbol": snapshot.symbol, "reason": str(exc)}
                    )
        return tuple(result)

    async def final_liquidation(self, snapshots: tuple[MarketSnapshot, ...]) -> tuple[str, ...]:
        """One bounded tick. Cancel -> reconcile -> reduce-only direct-TMN LIMIT orders.

        No forced fills, no deadline override, no kill bypass. Call on refreshed data until
        complete; remainder/dust is explicit. Unknown cancels stop the entire tick.
        """
        self._gate(allow_suspension=True)
        now = self.clock.now()
        if not self.config.settling(now):
            raise Blocked("NOT_IN_LIQUIDATION_WINDOW")
        if self.config.expired(now):
            raise Blocked("CHALLENGE_DEADLINE_PASSED")
        await self.recover(snapshots)
        for record in self.store.orders():
            if record.state not in TERMINAL:
                await self.cancel(record.intent.client_id)
                latest = self.store.order(record.intent.client_id)
                if latest is None or latest.state not in TERMINAL:
                    raise Blocked("LIQUIDATION_CANCEL_NOT_RESOLVED")
        await self.recover(snapshots)
        portfolio = self.store.portfolio()
        assert portfolio is not None
        results = []
        for position in portfolio.positions:
            # Reconcile before each order: prior partial/full fills can change available inventory.
            await self.recover(snapshots)
            current = self.store.portfolio()
            assert current is not None
            snapshot = self._market_context(position.symbol)
            market, book = snapshot.market, snapshot.liquidity
            assert market is not None and book is not None
            base = position.symbol.split("/")[0]
            free = next((b.free for b in current.balances if b.currency == base), D(0))
            bid = max(x.price for x in book.bids)
            quantity = rounded(
                min(
                    free / (1 + self.config.max_fee_rate),
                    sum((x.quantity for x in book.bids if x.price >= bid), D(0))
                    * self.config.max_depth_fraction,
                ),
                market.quantity_step,
            )
            if quantity < market.minimum_quantity or quantity * bid < market.minimum_notional:
                results.append("DUST_OR_NO_LIQUIDITY:" + position.symbol)
                continue
            price = rounded(bid, market.price_tick)
            identity = (
                "qp-final-"
                + stable_id(
                    [
                        self.config.config_id,
                        position.symbol,
                        [r.model_dump(mode="json") for r in self.store.orders()],
                    ]
                )[:40]
            )
            intent = OrderIntent(
                client_id=identity,
                decision_id="FINAL:" + self.config.config_id,
                account_id=self.config.account_id,
                symbol=position.symbol,
                side="SELL",
                order_type="LIMIT",
                base_quantity=quantity,
                limit_price=price,
            )
            self._authorizations[identity] = (intent, D(1), "FINAL_LIQUIDATION")
            state = await self.submit(intent)
            results.append(f"{identity}:{state.value}")
        with self.store.db:
            self.store.audit("LIQUIDATION_TICK", {"as_of": now.isoformat(), "results": results})
        return tuple(results)
