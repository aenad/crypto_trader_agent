"""Offline spot-only boundary and settlement regressions; no private network calls."""

import asyncio
from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError
from test_backtest import NOW, fill, provider
from test_shadow import later, session, setup_context

from quantpilot.backtest.execution import SimulatedExecutionProvider
from quantpilot.backtest.history import HistoricalClock
from quantpilot.backtest.ledger import PortfolioLedger
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.live.domain import AccountAuthorization
from quantpilot.live.settlement import settlement_report
from quantpilot.models import AssetBalance, OrderIntent, PortfolioState
from quantpilot.shadow.ai import ShadowAI
from quantpilot.shadow.engine import ShadowEngine
from quantpilot.shadow.feed import WallClock
from quantpilot.spot import SpotPolicy, validate_spot_order
from quantpilot.trading.config import ResearchParameters, RiskParameters
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

D = Decimal


def guard(side="BUY", quantity="1", price="100", funds=None, **changes):
    market = provider().markets["BTC/TMN"]
    validate_spot_order(
        "BTC/TMN",
        side,
        D(quantity),
        D(price),
        market.model_copy(update=changes),
        ("BTC/TMN",),
        {k: D(v) for k, v in (funds or {"TMN": "1000"}).items()},
        D(".001"),
    )


@pytest.mark.parametrize("side,funds", [("BUY", {"TMN": "100.1"}), ("SELL", {"BTC": "1"})])
def test_spot_accepts_owned_and_funded_orders(side, funds):
    guard(side=side, funds=funds)


@pytest.mark.parametrize(
    "side,funds",
    [
        ("BUY", {"TMN": "99"}),
        ("BUY", {"TMN": "100"}),  # Including fee shortage.
        ("SELL", {"TMN": "10000"}),
        ("SELL", {"BTC": ".99"}),
        ("BUY", {"TMN": "-1"}),
    ],
)
def test_spot_rejects_unfunded_or_unowned_orders(side, funds):
    with pytest.raises(ValueError):
        guard(side=side, funds=funds)


@pytest.mark.parametrize(
    "field",
    [
        "margin_enabled",
        "leverage_enabled",
        "short_selling_enabled",
        "borrowing_enabled",
        "derivatives_enabled",
    ],
)
def test_permanent_policy_cannot_enable_non_spot(field):
    with pytest.raises(ValidationError):
        SpotPolicy.model_validate({field: True})


@pytest.mark.parametrize(
    "extra",
    [{"market_type": "MARGIN"}, {"leverage": "2"}, {"side": "SHORT"}, {"symbol": "BTC-PERP"}],
)
def test_order_contract_rejects_margin_leverage_short_and_derivatives(extra):
    payload = dict(
        client_id="x",
        decision_id="x",
        account_id="backtest",
        symbol="BTC/TMN",
        side="BUY",
        order_type="MARKET",
        base_quantity="1",
    )
    with pytest.raises(ValidationError):
        OrderIntent.model_validate({**payload, **extra})


@pytest.mark.parametrize(
    "changes", [{"spot_enabled": False}, {"account_enabled": False}, {"quote": "USDT"}]
)
def test_unverified_market_fails_closed(changes):
    with pytest.raises(ValueError):
        guard(**changes)
    with pytest.raises(ValidationError):
        provider().markets["BTC/TMN"].model_validate(
            {
                **provider().markets["BTC/TMN"].model_dump(),
                "account_enabled": None,
            }
        )


def test_backtest_boundary_rejects_disabled_and_unapproved_market():
    async def scenario():
        for disabled, approved in ((True, ("BTC/TMN",)), (False, ())):
            data = provider()
            data.markets["BTC/TMN"] = data.markets["BTC/TMN"].model_copy(
                update={"spot_enabled": not disabled}
            )
            ledger = PortfolioLedger(D(1000), ResearchParameters())
            execution = SimulatedExecutionProvider(HistoricalClock(NOW), data, ledger, approved)
            execution.plan("x", D(5), D(100))
            with pytest.raises(ValueError):
                await execution.submit(
                    OrderIntent(
                        client_id="x",
                        decision_id="x",
                        account_id="backtest",
                        symbol="BTC/TMN",
                        side="BUY",
                        order_type="MARKET",
                        base_quantity=D(1),
                    )
                )
            assert ledger.free("TMN") == 1000 and not execution.orders

    asyncio.run(scenario())


def test_reservations_prevent_double_spending_and_overselling():
    ledger = PortfolioLedger(D(1000), ResearchParameters())
    ledger.reserve("TMN", D(900))
    with pytest.raises(ValueError):
        ledger.reserve("TMN", D(101))
    with pytest.raises(ValueError):
        ledger.apply_fill(fill("buy", "BUY", "1", "100", "1"), D(1), D(5))
    ledger.release("TMN", D(900))
    ledger.apply_fill(fill("buy", "BUY", "2", "100", "1"), D(1), D(5))
    ledger.reserve("BTC", D("1.5"))
    with pytest.raises(ValueError):
        ledger.apply_fill(fill("oversell", "SELL", "1", "100"), D(1), D(5))
    assert ledger.free("BTC") == D(".5") and ledger.free("TMN") == D(799)


def test_strategy_holds_when_position_has_no_owned_asset():
    cfg, frame = setup_context()
    snap = frame.snapshots[0]
    ledger = PortfolioLedger(D(5000000), cfg.research)
    bought = fill("buy", "BUY", "1", "100", "1")
    ledger.apply_fill(bought, D(1), D(5))
    account = ledger.snapshot(snap.as_of, {"BTC": D(100)}, ())
    account = account.model_copy(
        update={"balances": (AssetBalance(currency="TMN", free=D(100), reserved=D(0)),)}
    )
    signal = MomentumBreakout(cfg.research, MarketEligibilityFilter(cfg.approved)).evaluate(
        snap, account
    )
    assert signal.action == "HOLD" and signal.reasons == ("NO_OWNED_SPOT_ASSET",)


def test_shadow_deadline_queues_then_confirms_sale_and_replays(tmp_path):
    async def scenario():
        cfg, first = setup_context()
        cfg = cfg.model_copy(
            update={"deadline": first.as_of + timedelta(seconds=40), "liquidation_seconds": 20}
        )
        live = session(tmp_path, cfg)
        await live.process(first)
        await live.process(later(first))
        assert live.engine.ledger.holding("BTC").quantity > 0
        window = later(first, 20)
        result = await live.process(window)
        assert result["settlement"]["phase"] == "LIQUIDATING"
        assert result["settlement"]["actions"] == ["QUEUED:BTC/TMN"]
        assert not result["settlement"]["fully_settled"]
        result = await live.process(later(window))
        assert result["settlement"]["fully_settled"]
        assert not result["settlement"]["remaining_holdings"]
        assert live.engine.ledger.realized != 0
        assert D(result["equity_tmn"]) == D(result["settlement"]["final_toman_balance_tmn"])
        from quantpilot.shadow.service import replay_decisions

        replay = await replay_decisions(live.store, tmp_path / "responses", WallClock())
        assert replay["status"] == "MATCH" and replay["llm_network_calls"] == 0
        live.store.release()

    asyncio.run(scenario())


def test_shadow_deadline_preserves_unfilled_crypto_and_cancels_orders(tmp_path):
    async def scenario():
        cfg, first = setup_context()
        cfg = cfg.model_copy(
            update={"deadline": first.as_of + timedelta(seconds=40), "liquidation_seconds": 20}
        )
        engine = ShadowEngine(cfg, ShadowAI(cfg, tmp_path / "responses", WallClock()))
        await engine.apply(first)
        await engine.apply(later(first))
        await engine.apply(later(first, 20))
        result = await engine.apply(later(first, 40))
        assert result["settlement"]["remaining_holdings"]["BTC"] != "0"
        assert not result["settlement"]["fully_settled"]
        assert not engine.execution.active()

    asyncio.run(scenario())


def test_terminal_fx_requires_approved_route_and_real_recorded_depth():
    async def scenario():
        data = provider()
        data.fx_market = data.markets["BTC/TMN"].model_copy(update={"symbol": "USDT/TMN"})
        from quantpilot.models import DepthLevel, LiquiditySnapshot

        now = data.candles["BTC/TMN"][-1].close_time
        book = LiquiditySnapshot(
            as_of=now,
            bids=(DepthLevel(price=D(100), quantity=D(100)),),
            asks=(DepthLevel(price=D(101), quantity=D(100)),),
        )
        data.quotes["USDT/TMN"] = (book,)
        data.quote_times["USDT/TMN"] = [now]
        replay = HistoricalReplay(data, RiskParameters(), ("BTC/TMN",))
        replay.ledger.convert("USDT", D(1), D(100), D(".001"), NOW)
        await replay.liquidate(now)
        assert replay.ledger.holding("USDT").quantity == 0
        assert replay.ledger.realized < 0 and not replay.residuals

    asyncio.run(scenario())


def test_live_settlement_reports_only_verified_cash_and_inventory():
    buysell = (
        fill("buy", "BUY", "2", "100", "2"),
        fill("sell", "SELL", "1", "120", "1.2", seconds=1),
    )
    account = PortfolioState(
        account_id="dedicated",
        as_of=NOW + timedelta(seconds=1),
        balances=(
            AssetBalance(currency="TMN", free=D("916.8"), reserved=D(0)),
            AssetBalance(currency="BTC", free=D(1), reserved=D(0)),
        ),
    )
    report = settlement_report(account, buysell, {"BTC": D(110)}, D(1000), 0)
    assert D(report["realized_pnl_tmn"]) == D("17.8")
    assert D(report["unrealized_pnl_tmn"]) == D(9)
    assert D(report["fees_tmn"]) == D("3.2")
    assert D(report["net_return_pct"]) == D("2.68")
    assert not report["fully_settled_tmn"]
    with pytest.raises(ValueError):
        settlement_report(account, (), {"BTC": D(110)}, D(1000), 0)


def test_unknown_live_account_type_is_rejected():
    with pytest.raises(ValidationError):
        AccountAuthorization.model_validate({"account_type": "UNKNOWN"})


@pytest.mark.parametrize(
    "tool",
    [
        "wallex_margin_open_position",
        "wallex_margin_close_position_id",
        "wallex_spot_post_account_orders",
        "wallex_spot_delete_account_orders",
        "wallex_credit_create_transfer_to_sub_account",
        "wallex_otc_place_easy_trade_order",
        "withdraw",
        "unrecognized_tool",
    ],
)
def test_legacy_mcp_blocks_unsafe_tools_before_connecting(monkeypatch, tool):
    from pathlib import Path
    from unittest.mock import Mock

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    from backend.mcp_client import MCPUnavailable, WallexMCP

    # Do not instantiate Settings: it would load the user's .env.
    client = WallexMCP(None)
    client.session = Mock(side_effect=AssertionError("Must not open a network session"))
    with pytest.raises(MCPUnavailable):
        asyncio.run(client.call_tool(tool, {}))
    client.session.assert_not_called()


def test_live_base_fee_settlement_accounting_and_pending_orders():
    from quantpilot.models import Money

    bought = fill("buy", "BUY", "2", "100").model_copy(
        update={"fee": Money(amount=D(".02"), currency="BTC")}
    )
    sold = fill("sell", "SELL", "1.9", "120", "1", seconds=1)
    account = PortfolioState(
        account_id="dedicated",
        as_of=NOW + timedelta(seconds=1),
        balances=(
            AssetBalance(currency="TMN", free=D(1027), reserved=D(0)),
            AssetBalance(currency="BTC", free=D(".08"), reserved=D(0)),
        ),
    )
    report = settlement_report(account, (bought, sold), {"BTC": D(120)}, D(1000), 1)
    assert D(report["final_equity_tmn"]) == D("1036.60")
    assert D(report["fees_tmn"]) == D(3)
    assert report["unresolved_orders"] == 1 and not report["fully_settled_tmn"]


def test_protected_live_settlement_projection_is_read_only(tmp_path):
    from test_live import fixture, prepare

    async def scenario():
        adapter, exchange, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await prepare(adapter, snapshot)  # Mock bootstrap and risk authorization only.
            report = adapter.settlement_report()
            assert D(report["final_toman_balance_tmn"]) == D(5000000)
            assert D(report["realized_pnl_tmn"]) == 0
            assert report["fully_settled_tmn"] and not report["competition_complete"]
            assert not exchange.intents  # No mock submission either.
        finally:
            store.close()

    asyncio.run(scenario())
