"""Offline only. All credentials are fake and every exchange is injected or MockTransport."""

import asyncio
import json
from datetime import timedelta
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr, ValidationError
from test_shadow import setup_context

from quantpilot.config import stable_id
from quantpilot.live.domain import (
    AccountAuthorization,
    Blocked,
    LiveConfig,
    credential_fingerprint,
)
from quantpilot.live.execution import ProtectedExecution, require_activation
from quantpilot.live.storage import LiveStore
from quantpilot.live.transport import WallexSpotREST, parse_order
from quantpilot.models import AssetBalance, MarketSnapshot, OrderIntent, OrderState
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

D = Decimal


class Clock:
    def __init__(self, at):
        self.at = at

    def now(self):
        return self.at


def raw_order(intent, parts=(), status="NEW", fee_asset="TMN", fee_rate=D(".001")):
    rows = []
    for q, at in parts:
        cost = q * intent.limit_price
        fee = cost * fee_rate if fee_asset == "TMN" else q * fee_rate
        rows.append(
            {
                "quantity": str(q),
                "price": str(intent.limit_price),
                "sum": str(cost),
                "fee": str(fee),
                "feeAsset": fee_asset,
                "isBuyer": intent.side == "BUY",
                "symbol": intent.symbol.replace("/", ""),
                "timestamp": at.isoformat(),
            }
        )
    return {
        "clientOrderId": intent.client_id,
        "symbol": intent.symbol.replace("/", ""),
        "side": intent.side,
        "type": intent.order_type,
        "origQty": str(intent.base_quantity),
        "executedQty": str(sum((q for q, _ in parts), D(0))),
        "executedSum": str(sum((q * intent.limit_price for q, _ in parts), D(0))),
        "status": status,
        "active": status == "NEW",
        "fills": rows,
    }


class Exchange:
    def __init__(self, cfg, clock):
        self.cfg, self.clock = cfg, clock
        self.raw, self.intents = {}, {}
        self.amounts = {"TMN": cfg.capital_tmn, "BTC": D(0)}
        self.applied = set()
        self.submissions = self.cancellations = self.reads = 0
        self.submit_failure = self.cancel_failure = self.lookup_failure = False
        self.read_failures = 0
        self.fill_on_submit = False
        self.fill_on_cancel = False
        self.foreign_order = False
        self.changed_precision = False

    async def close(self):
        pass

    async def submit(self, intent):
        self.submissions += 1
        self.intents[intent.client_id] = intent
        self.raw[intent.client_id] = raw_order(intent)
        if self.fill_on_submit:
            self.fill(intent, intent.base_quantity, "FILLED")
        if self.submit_failure:
            raise TimeoutError("fake transport may have accepted order")
        return parse_order(self.raw[intent.client_id], intent)

    def fill(self, intent, quantity, status="NEW", fee_asset="TMN"):
        self.raw[intent.client_id] = raw_order(
            intent,
            ((quantity, self.clock.now()),),
            status,
            fee_asset,
        )
        self._apply(intent)

    def _apply(self, intent):
        observed = parse_order(self.raw[intent.client_id], intent)
        for fill in observed.fills:
            if fill.fill_id in self.applied:
                continue
            sign = 1 if fill.side == "BUY" else -1
            self.amounts["BTC"] += sign * fill.base_quantity
            self.amounts["TMN"] -= sign * fill.base_quantity * fill.price.amount
            self.amounts[fill.fee.currency] -= fill.fee.amount
            self.applied.add(fill.fill_id)

    async def lookup(self, intent):
        self.reads += 1
        if self.lookup_failure:
            raise TimeoutError("fake unavailable")
        return parse_order(self.raw[intent.client_id], intent)

    async def cancel(self, intent):
        self.cancellations += 1
        if self.fill_on_cancel:
            self.fill(intent, intent.base_quantity, "FILLED")
        else:
            self.raw[intent.client_id].update(status="CANCELED", active=False)
        if self.cancel_failure:
            raise TimeoutError("fake cancel response lost")

    async def balances(self, semantics):
        if self.read_failures:
            self.read_failures -= 1
            raise ConnectionError("offline temporary")
        reserved = {k: D(0) for k in self.amounts}
        for identity, raw in self.raw.items():
            intent = self.intents[identity]
            if raw["active"]:
                left = intent.base_quantity - D(raw["executedQty"])
                asset = "TMN" if intent.side == "BUY" else "BTC"
                reserved[asset] += left * (intent.limit_price if intent.side == "BUY" else 1)
        return tuple(
            AssetBalance(currency=k, free=v - reserved[k], reserved=reserved[k])
            for k, v in self.amounts.items()
        )

    async def open_ids(self):
        return frozenset(
            [key for key, raw in self.raw.items() if raw["active"]]
            + (["foreign"] if self.foreign_order else [])
        )

    async def markets(self):
        market = self.cfg.markets[0]
        return {
            "BTCTMN": {
                "symbol": "BTCTMN",
                "baseAsset": "BTC",
                "quoteAsset": "TMN",
                "stepSize": 4 if self.changed_precision else 3,
                "tickSize": 2,
                "minQty": str(market.minimum_quantity),
                "minNotional": str(market.minimum_notional),
                "maxQty": "1000000",
            }
        }

    async def fees(self):
        return {"BTCTMN": {"takerFeeRate": ".001", "makerFeeRate": ".001"}}


def fixture(tmp_path, **config_changes):
    _, frame = setup_context()
    snapshot = frame.snapshots[0]
    config = LiveConfig(
        enabled=True,
        account_id="fake-dedicated-main-spot",
        approved=(snapshot.symbol,),
        markets=(snapshot.market,),
        max_order_tmn=D("500000"),
        deadline=frame.as_of + timedelta(days=3),
        **config_changes,
    )
    clock = Clock(frame.as_of)
    key = SecretStr("TEST-ONLY-NOT-A-REAL-KEY")
    grant = AccountAuthorization(
        config_id=config.config_id,
        account_id=config.account_id,
        account_type="MAIN_SPOT",
        credential_sha256=credential_fingerprint(key),
        evidence_reference="MOCK-OPERATOR-EVIDENCE",
        spot_read=True,
        spot_trade=True,
        withdrawal_disabled=True,
        balance_value_semantics="FREE",
        valid_from=clock.now() - timedelta(seconds=1),
        expires_at=config.deadline + timedelta(days=1),
    )
    env = {
        "QUANTPILOT_LIVE_AUTHORIZATION": config.config_id,
        "QUANTPILOT_WALLEX_LIVE_API_KEY": key.get_secret_value(),
    }
    store = LiveStore(tmp_path / "live.sqlite", config.config_id)
    exchange = Exchange(config, clock)
    adapter = ProtectedExecution(config, grant, store, clock, exchange, env)
    return adapter, exchange, store, snapshot, clock, env


async def prepare(adapter, snapshot):
    await adapter.bootstrap()
    await adapter.recover((snapshot,))
    adapter.resume_after_reconciliation()
    portfolio = adapter.store.portfolio()
    signal = MomentumBreakout(
        adapter.config.research,
        MarketEligibilityFilter(
            adapter.config.approved,
        ),
    ).evaluate(snapshot, portfolio)
    assert signal.action == "BUY"
    return adapter.authorize(signal, "qp-test-order")


def test_live_defaults_and_separate_activation(tmp_path):
    a, _, store, _, clock, env = fixture(tmp_path)
    try:
        disabled = a.config.model_copy(update={"enabled": False})
        with pytest.raises(Blocked, match="LIVE_DISABLED"):
            require_activation(disabled, a.grant, clock.now(), env)
        with pytest.raises(Blocked, match="LIVE_DISABLED"):
            require_activation(a.config, a.grant, clock.now(), {})
        for field in ("spot_read", "spot_trade", "withdrawal_disabled"):
            with pytest.raises(Blocked, match="PERMISSIONS"):
                require_activation(
                    a.config, a.grant.model_copy(update={field: False}), clock.now(), env
                )
        with pytest.raises(Blocked, match="CREDENTIAL_SCOPE"):
            require_activation(
                a.config,
                a.grant,
                clock.now(),
                {
                    **env,
                    "QUANTPILOT_WALLEX_LIVE_API_KEY": "DIFFERENT-FAKE-KEY",
                },
            )
        with pytest.raises(ValidationError):
            a.grant.model_validate({**a.grant.model_dump(), "account_type": "CREDIT"})
    finally:
        store.close()


def test_submission_is_idempotent_and_risk_bound(tmp_path):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            with pytest.raises(Blocked, match="NOT_AUTHORIZED"):
                await a.submit(
                    intent.model_copy(update={"base_quantity": intent.base_quantity * 2})
                )
            intent = a.authorize(
                MomentumBreakout(
                    a.config.research,
                    MarketEligibilityFilter(
                        a.config.approved,
                    ),
                ).evaluate(snapshot, store.portfolio()),
                intent.client_id,
            )
            assert await a.submit(intent) == OrderState.SUBMITTED
            assert await a.submit(intent) == OrderState.SUBMITTED
            assert e.submissions == 1
            with pytest.raises(Blocked, match="REUSED"):
                await a.submit(intent.model_copy(update={"base_quantity": D(1)}))
            assert store.orders()[0].phase == "OBSERVED"
            store.verify()
        finally:
            store.close()

    asyncio.run(scenario())


def test_timeout_never_reposts_and_recovers_across_restart(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, env = fixture(tmp_path)
        intent = await prepare(a, snapshot)
        e.submit_failure = True
        with pytest.raises(Blocked, match="AMBIGUOUS"):
            await a.submit(intent)
        assert await a.submit(intent) == OrderState.UNKNOWN
        assert e.submissions == 1
        cfg, grant = a.config, a.grant
        store.close()
        store = LiveStore(tmp_path / "live.sqlite", cfg.config_id)
        a = ProtectedExecution(cfg, grant, store, clock, e, env)
        try:
            await a.recover((snapshot,))
            assert store.order(intent.client_id).state == OrderState.SUBMITTED
            assert e.submissions == 1
            assert store.get("suspended") is not None
            a.resume_after_reconciliation()
            assert store.get("suspended") is None
        finally:
            store.close()

    asyncio.run(scenario())


def test_partial_fill_cancel_and_exact_accounting(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            await a.submit(intent)
            quantity = intent.base_quantity / 2
            e.fill(intent, quantity)
            assert await a.lookup(intent.client_id) == OrderState.PARTIALLY_FILLED
            first = store.portfolio()
            assert first.positions[0].quantity == quantity
            cost = quantity * intent.limit_price
            cash = next(b.free for b in first.balances if b.currency == "TMN")
            assert cash == a.config.capital_tmn - cost * D("1.001")
            await a.lookup(intent.client_id)
            assert store.portfolio() == first
            assert await a.cancel(intent.client_id) == OrderState.CANCELED
            await a.recover((snapshot,))
            assert store.portfolio().positions[0].quantity == quantity
            assert e.cancellations == 1
            assert len(await a.fills(intent.client_id)) == 1
        finally:
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("failure", ["cancel_timeout", "cancel_fill_race", "lookup_timeout"])
def test_cancel_races_and_failures(tmp_path, failure):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            await a.submit(intent)
            if failure == "cancel_fill_race":
                e.fill_on_cancel = True
                assert await a.cancel(intent.client_id) == OrderState.FILLED
                assert store.portfolio().positions[0].quantity == intent.base_quantity
            else:
                e.cancel_failure = failure == "cancel_timeout"
                e.lookup_failure = failure == "lookup_timeout"
                with pytest.raises(Blocked):
                    await a.cancel(intent.client_id)
                assert store.order(intent.client_id).state == OrderState.UNKNOWN
                e.cancel_failure = e.lookup_failure = False
                # Resolution is GET only, not a repeat DELETE.
                assert await a.cancel(intent.client_id) == OrderState.CANCELED
                assert e.cancellations == 1
        finally:
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("fault", ["balances", "foreign_order", "precision", "stale", "network"])
def test_unreliable_context_suspends(tmp_path, fault):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            await a.bootstrap()
            if fault == "balances":
                e.amounts["TMN"] += 1
            elif fault == "foreign_order":
                e.foreign_order = True
            elif fault == "precision":
                e.changed_precision = True
            elif fault == "stale":
                clock.at += timedelta(seconds=31)
            else:
                e.read_failures = 100
            with pytest.raises(Blocked, match="RECONCILIATION_FAILED"):
                await a.recover((snapshot,), attempts=1)
            assert store.get("suspended")
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


def test_transient_read_reconnect_and_kill_persistence(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, env = fixture(tmp_path)
        await a.bootstrap()
        e.read_failures = 1
        await a.recover((snapshot,))
        a.kill()
        cfg, grant = a.config, a.grant
        store.close()
        store = LiveStore(tmp_path / "live.sqlite", cfg.config_id)
        a = ProtectedExecution(cfg, grant, store, clock, e, env)
        try:
            await a.recover((snapshot,))
            with pytest.raises(Blocked, match="KILL_SWITCH"):
                a.resume_after_reconciliation()
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


def test_drawdown_latch_is_not_auto_cleared(tmp_path):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await a.bootstrap()
            portfolio = store.portfolio().model_copy(update={"peak_equity_tmn": D("10000000")})
            with store.db:
                store.set("portfolio", portfolio.model_dump_json())
            await a.recover((snapshot,))
            assert store.portfolio().risk_halted
            with pytest.raises(Blocked, match="RISK_SUSPENSION"):
                a.resume_after_reconciliation()
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


def test_final_liquidation_reduces_only_and_reports_dust(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            e.fill_on_submit = True
            assert await a.submit(intent) == OrderState.FILLED
            with pytest.raises(Blocked, match="NOT_IN_LIQUIDATION"):
                await a.final_liquidation((snapshot,))
            clock.at = a.config.deadline - timedelta(seconds=200)
            data = snapshot.model_dump(mode="json")
            data["as_of"] = clock.at.isoformat()
            data["liquidity"]["as_of"] = clock.at.isoformat()
            fresh = MarketSnapshot.model_validate(data)
            result = await a.final_liquidation((fresh,))
            assert any("FILLED" in item for item in result)
            exits = [r for r in store.orders() if r.purpose == "FINAL_LIQUIDATION"]
            assert len(exits) == 1 and exits[0].intent.side == "SELL"
            assert exits[0].intent.base_quantity < intent.base_quantity
            # Subsequent ticks shrink the fee buffer residual; never claim guaranteed liquidation.
            for _ in range(4):
                result = await a.final_liquidation((fresh,))
                if any("DUST" in item for item in result):
                    break
            assert any("DUST" in item for item in result)
            count = e.submissions
            clock.at = a.config.deadline
            with pytest.raises(Blocked, match="DEADLINE_PASSED"):
                await a.final_liquidation((fresh,))
            assert e.submissions == count
        finally:
            store.close()

    asyncio.run(scenario())


def test_writer_lock_and_audit_tamper_detection(tmp_path):
    a, _, store, _, _, _ = fixture(tmp_path)
    try:
        with pytest.raises(Blocked, match="WRITER_ALREADY"):
            LiveStore(tmp_path / "live.sqlite", a.config.config_id)
        store.latch("TEST")
        with store.db:
            store.db.execute("UPDATE live_audit SET body='{}' WHERE seq=1")
        with pytest.raises(Blocked, match="AUDIT_CORRUPT"):
            store.verify()
    finally:
        store.close()


def test_fill_multiset_and_contract_rejections():
    from quantpilot.trading.demo import NOW

    intent = OrderIntent(
        client_id="test",
        decision_id="test",
        account_id="test",
        symbol="BTC/TMN",
        side="BUY",
        order_type="LIMIT",
        base_quantity=D(2),
        limit_price=D(100),
    )
    raw = raw_order(intent, ((D(1), NOW), (D(1), NOW)), "FILLED")
    parsed = parse_order(raw, intent)
    assert len({f.fill_id for f in parsed.fills}) == 2
    assert parse_order({**raw, "fills": list(reversed(raw["fills"]))}, intent) == parsed
    for broken in (
        {"fills": []},
        {"status": "WHATEVER"},
        {"symbol": "ETHUSDT"},
        {"executedQty": "3"},
        {"active": True},
    ):
        with pytest.raises(Blocked):
            parse_order({**raw, **broken}, intent)


def test_http_contract_auth_redaction_no_retry_and_no_unsafe_paths():
    async def scenario():
        seen = []
        secret = "OFFLINE-TEST-SECRET"

        def handler(request):
            seen.append(request)
            assert request.url.host == "api.wallex.ir"
            assert request.headers["x-api-key"] == secret
            if request.method == "POST":
                assert json.loads(request.content)["client_id"] == "test-client"
                raise httpx.ReadTimeout(secret, request=request)
            return httpx.Response(200, json={"success": True, "result": {}})

        client = WallexSpotREST(
            SecretStr(secret),
            transport=httpx.MockTransport(handler),
            authorize_mutation=lambda method, identity: None,
        )
        intent = OrderIntent(
            client_id="test-client",
            decision_id="d",
            account_id="a",
            symbol="BTC/TMN",
            side="BUY",
            order_type="LIMIT",
            base_quantity=D(1),
            limit_price=D(100),
        )
        try:
            with pytest.raises(Blocked) as error:
                await client.submit(intent)
            assert secret not in str(error.value)
            assert len(seen) == 1
            await client.cancel(intent)
            assert seen[-1].method == "DELETE"
            assert json.loads(seen[-1].content)["clientOrderId"] == intent.client_id
            assert "clientOrderId" not in seen[-1].url.params
            with pytest.raises(Blocked, match="ENDPOINT_BLOCKED"):
                await client._request("POST", "/v1/account/crypto-withdrawal")
            with pytest.raises(Blocked, match="INVALID_CLIENT_ID"):
                await client.lookup(intent.model_copy(update={"client_id": "../profile"}))
            assert len(seen) == 2
        finally:
            await client.close()

    asyncio.run(scenario())


def test_risk_rejects_fabricated_signal(tmp_path):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await prepare(a, snapshot)
            strategy = MomentumBreakout(
                a.config.research, MarketEligibilityFilter(a.config.approved)
            )
            signal = strategy.evaluate(snapshot, store.portfolio())
            with pytest.raises(Blocked, match="RISK_REJECTED"):
                a.authorize(signal.model_copy(update={"snapshot_id": stable_id("forged")}), "bad")
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


def test_stale_authorization_cannot_submit(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            clock.at += timedelta(seconds=11)
            with pytest.raises(Blocked, match="STALE"):
                await a.submit(intent)
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


def test_base_asset_fee_and_cumulative_identical_partial_fills(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            await a.submit(intent)
            half = intent.base_quantity / 2
            e.raw[intent.client_id] = raw_order(intent, ((half, clock.now()),), fee_asset="BTC")
            e._apply(intent)
            await a.lookup(intent.client_id)
            e.raw[intent.client_id] = raw_order(
                intent,
                ((half, clock.now()), (half, clock.now())),
                "FILLED",
                fee_asset="BTC",
            )
            e._apply(intent)
            await a.lookup(intent.client_id)
            await a.recover((snapshot,))
            assert len(await a.fills(intent.client_id)) == 2
            assert store.portfolio().positions[0].quantity == intent.base_quantity * D(".999")
            before = store.portfolio().positions
            await a.lookup(intent.client_id)
            assert store.portfolio().positions == before
        finally:
            store.close()

    asyncio.run(scenario())


def test_missing_fill_history_stops_instead_of_inventing_fills(tmp_path):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            await a.submit(intent)
            e.fill(intent, intent.base_quantity / 2)
            await a.lookup(intent.client_id)
            before = store.portfolio()
            e.raw[intent.client_id]["fills"] = []
            with pytest.raises(Blocked, match="RECONCILIATION_REQUIRED"):
                await a.lookup(intent.client_id)
            assert store.portfolio() == before
            assert store.get("suspended")
        finally:
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("fault", ["ambiguous_cancel", "kill", "stale"])
def test_final_liquidation_never_bypasses_operational_stops(tmp_path, fault):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            await a.submit(intent)
            clock.at = a.config.deadline - timedelta(seconds=100)
            fresh = snapshot.model_copy(
                update={
                    "as_of": clock.now(),
                    "liquidity": snapshot.liquidity.model_copy(update={"as_of": clock.now()}),
                }
            )
            if fault == "ambiguous_cancel":
                e.cancel_failure = True
            elif fault == "kill":
                a.kill()
            else:
                fresh = snapshot
            with pytest.raises(Blocked):
                await a.final_liquidation((fresh,))
            assert e.submissions == 1
        finally:
            store.close()

    asyncio.run(scenario())


def test_external_kill_file_works_while_writer_running(tmp_path, monkeypatch, capsys):
    from quantpilot.live.cli import main

    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            path = tmp_path / "config.json"
            path.write_text(a.config.model_dump_json(), encoding="utf-8")
            monkeypatch.setattr(
                "sys.argv",
                [
                    "quantpilot-live",
                    "kill",
                    "--config",
                    str(path),
                    "--db",
                    str(tmp_path / "live.sqlite"),
                ],
            )
            main()
            assert json.loads(capsys.readouterr().out)["kill"] is True
            with pytest.raises(Blocked, match="KILL_SWITCH"):
                await a.submit(intent)
            assert a.health()["kill"] is True
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("status", [404, 409, 429, 500, 302])
def test_http_failures_do_not_retry_mutation(status):
    async def scenario():
        count = 0

        def handler(request):
            nonlocal count
            count += 1
            return httpx.Response(
                status,
                headers={"Location": "https://untrusted.invalid"},
                json={"success": False, "message": "sensitive response"},
            )

        client = WallexSpotREST(
            SecretStr("FAKE"),
            transport=httpx.MockTransport(handler),
            authorize_mutation=lambda method, identity: None,
        )
        try:
            intent = OrderIntent(
                client_id="t",
                decision_id="d",
                account_id="a",
                symbol="BTC/TMN",
                side="BUY",
                order_type="LIMIT",
                base_quantity=D(1),
                limit_price=D(1),
            )
            with pytest.raises(Blocked) as exc:
                await client.submit(intent)
            assert "sensitive response" not in str(exc.value)
            assert count == 1
        finally:
            await client.close()

    asyncio.run(scenario())


def test_raw_transport_mutations_are_disabled_by_default():
    async def scenario():
        def handler(request):
            pytest.fail("A disabled raw transport must not reach the exchange")

        client = WallexSpotREST(SecretStr("FAKE"), transport=httpx.MockTransport(handler))
        try:
            intent = OrderIntent(
                client_id="t",
                decision_id="d",
                account_id="a",
                symbol="BTC/TMN",
                side="BUY",
                order_type="LIMIT",
                base_quantity=D(1),
                limit_price=D(1),
            )
            with pytest.raises(Blocked, match="MUTATIONS_DISABLED"):
                await client.submit(intent)
        finally:
            await client.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("semantics,expected_free", [("FREE", D(100)), ("TOTAL", D(90))])
def test_balance_normalization_requires_explicit_semantics(semantics, expected_free):
    async def scenario():
        def handler(request):
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "balances": {
                            "TMN": {"asset": "TMN", "value": "100", "locked": "10"},
                        }
                    },
                },
            )

        client = WallexSpotREST(SecretStr("FAKE"), transport=httpx.MockTransport(handler))
        try:
            balances = await client.balances(semantics)
            assert balances[0].free == expected_free and balances[0].reserved == D(10)
        finally:
            await client.close()

    asyncio.run(scenario())


def test_realistic_processing_delay_aligns_decision_cut_without_refreshing_book_time(tmp_path):
    async def scenario():
        a, e, store, snapshot, clock, _ = fixture(tmp_path)
        try:
            await a.bootstrap()
            await a.recover((snapshot,))
            a.resume_after_reconciliation()
            clock.at += timedelta(seconds=2)
            proposals = await a.strategy_cycle((snapshot,))
            assert len(proposals) == 1 and e.submissions == 0
            snapshots, portfolio = a.decision_context()
            assert snapshots[0].as_of == portfolio.as_of == clock.now()
            assert snapshots[0].liquidity.as_of == snapshot.liquidity.as_of
            await a.submit(proposals[0])
            assert e.submissions == 1
        finally:
            store.close()

    asyncio.run(scenario())


def test_unresolved_submission_stays_suspended_without_duplicate_post(tmp_path):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            e.submit_failure = e.lookup_failure = True
            with pytest.raises(Blocked):
                await a.submit(intent)
            with pytest.raises(Blocked):
                await a.recover((snapshot,), attempts=1)
            assert await a.submit(intent) == OrderState.UNKNOWN
            assert e.submissions == 1 and store.get("suspended")
        finally:
            store.close()

    asyncio.run(scenario())


def test_local_status_and_export_do_not_need_credentials(tmp_path, monkeypatch, capsys):
    from quantpilot.live.cli import main

    a, _, store, _, _, _ = fixture(tmp_path)
    config_path = tmp_path / "config.json"
    config_path.write_text(a.config.model_dump_json(), encoding="utf-8")
    store.close()
    base = [
        "quantpilot-live",
        "status",
        "--config",
        str(config_path),
        "--db",
        str(tmp_path / "live.sqlite"),
    ]
    monkeypatch.setattr("sys.argv", base)
    main()
    assert json.loads(capsys.readouterr().out)["orders"] == []
    output = tmp_path / "audit.jsonl"
    monkeypatch.setattr("sys.argv", [base[0], "export", *base[2:], "--output", str(output)])
    main()
    capsys.readouterr()
    assert "ACTIVATION_SCOPE_CHECKED" in output.read_text()
    assert "TEST-ONLY-NOT-A-REAL-KEY" not in output.read_text()
    with pytest.raises(FileExistsError):
        main()


def test_protected_factory_requires_a_durable_send_boundary(tmp_path, monkeypatch):
    from quantpilot.live.execution import activated_adapter

    a, e, store, _, clock, env = fixture(tmp_path)
    captured = {}

    def transport(key, *, authorize_mutation):
        captured["guard"] = authorize_mutation
        assert key.get_secret_value() == "TEST-ONLY-NOT-A-REAL-KEY"
        return e

    monkeypatch.setattr("quantpilot.live.execution.WallexSpotREST", transport)
    try:
        activated_adapter(a.config, a.grant, store, clock, env)
        with pytest.raises(Blocked, match="DURABLE_MUTATION"):
            captured["guard"]("POST", "unprepared")
        assert e.submissions == 0
    finally:
        store.close()


@pytest.mark.parametrize("change", ["budget", "maximum_quantity", "precision", "scope"])
def test_final_size_and_scope_checks_prevent_network_submission(tmp_path, change):
    async def scenario():
        a, e, store, snapshot, _, _ = fixture(tmp_path)
        try:
            intent = await prepare(a, snapshot)
            if change == "maximum_quantity":
                a._maximum_quantities[intent.symbol] = D("0.000001")
            elif change == "budget":
                # A tighter configured budget is a post-risk execution constraint.
                a.config = a.config.model_copy(update={"max_order_tmn": D(1)})
                # Config changes cannot retain the existing authorization scope.
            else:
                intent = intent.model_copy(
                    update=(
                        {"base_quantity": intent.base_quantity + D(".0001")}
                        if change == "precision"
                        else {"account_id": "different"}
                    )
                )
            with pytest.raises(Blocked):
                await a.submit(intent)
            assert e.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())
