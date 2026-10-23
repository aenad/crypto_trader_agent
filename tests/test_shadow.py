import asyncio
import json
from datetime import timedelta
from decimal import Decimal

import pytest

from quantpilot.models import Candle, DepthLevel, LiquiditySnapshot, MarketSnapshot
from quantpilot.shadow.ai import ShadowAI
from quantpilot.shadow.domain import ShadowConfig, ShadowFrame
from quantpilot.shadow.engine import ShadowEngine
from quantpilot.shadow.feed import WallClock
from quantpilot.shadow.service import ShadowSession, export_activity, health, replay_decisions
from quantpilot.shadow.storage import ShadowStore, pack
from quantpilot.trading.demo import synthetic_context

D = Decimal


def setup_context(**simulation):
    original, _ = synthetic_context()
    payload = original.model_dump(mode="json")
    payload["symbol"] = "BTC/TMN"
    payload["market"].update(symbol="BTC/TMN", quote="TMN")
    for key in ("candles", "trend_candles"):
        for candle in payload[key]:
            candle["symbol"] = "BTC/TMN"
    snapshot = MarketSnapshot.model_validate(payload)
    cfg = ShadowConfig(
        approved=(snapshot.symbol,),
        markets=(snapshot.market,),
        ai_mode="QUANT_ONLY",
        simulation=simulation,
        health_port=0,
        poll_seconds=1,
    )
    return cfg, ShadowFrame(as_of=snapshot.as_of, snapshots=(snapshot,), depth_timestamps="FIXTURE")


def later(frame, seconds=15, new_book=True, drop=None):
    now = frame.as_of + timedelta(seconds=seconds)
    snap = frame.snapshots[0]
    book = snap.liquidity.model_copy(update={"as_of": now}) if new_book else snap.liquidity
    candles = snap.candles
    if drop is not None:
        price = snap.candles[-1].close - D(drop)
        candles = candles + (
            Candle(
                event_id=f"after:{now.isoformat()}",
                symbol=snap.symbol,
                event_time=now,
                received_at=now,
                source="fixture",
                open_time=candles[-1].close_time,
                close_time=now,
                open=price,
                close=price,
                high=price + D(".1"),
                low=price - D(".1"),
                volume=D(100),
                closed=True,
            ),
        )
        book = LiquiditySnapshot(
            as_of=now,
            bids=(DepthLevel(price=price - D(".01"), quantity=D(10000)),),
            asks=(DepthLevel(price=price + D(".01"), quantity=D(10000)),),
        )
    return ShadowFrame(
        as_of=now,
        snapshots=(snap.model_copy(update={"as_of": now, "liquidity": book, "candles": candles}),),
        depth_timestamps="FIXTURE",
    )


def session(tmp_path, cfg, filename="session.sqlite"):
    store = ShadowStore(tmp_path / filename)
    store.claim("test-owner", WallClock().now())
    engine = ShadowEngine(cfg, ShadowAI(cfg, tmp_path / "responses", WallClock()))
    return ShadowSession(store, engine)


def test_virtual_entry_next_observation_exit_and_exact_restart_replay(tmp_path):
    async def scenario():
        cfg, first = setup_context()
        live = session(tmp_path, cfg)
        result = await live.process(first)
        assert result["decisions"][0]["outcome"] == "ACCEPTED"
        assert not live.engine.ledger.seen  # Never fill the decision's own book.
        second = later(first)
        result = await live.process(second)
        assert live.engine.ledger.seen
        assert not result["decisions"]  # Closed candle processed once across quote polls.
        position = live.engine.ledger.positions["BTC/TMN"]
        assert position.quantity > 0
        state = live.engine.dump()
        live.store.release()
        restarted = session(tmp_path, cfg)
        assert restarted.engine.dump() == state
        third = later(first, 300, drop="20")
        result = await restarted.process(third)
        assert result["decisions"][0]["signal"]["action"] == "SELL"
        await restarted.process(later(third))
        assert restarted.engine.ledger.positions["BTC/TMN"].state == "CLOSED"
        assert restarted.engine.ledger.realized < 0
        assert restarted.engine.ledger.fees > 0
        restarted.store.verify()
        replay = await replay_decisions(restarted.store, tmp_path / "responses", WallClock())
        assert replay["status"] == "MATCH" and replay["frames"] == 4
        assert replay["decisions"] == 2
        assert replay["llm_network_calls"] == 0

    asyncio.run(scenario())


def test_partial_depth_is_shared_not_reused_and_survives_restart(tmp_path):
    async def scenario():
        cfg, first = setup_context(book_participation=D(".001"))
        live = session(tmp_path, cfg)
        await live.process(first)
        second = later(first)
        await live.process(second)
        quantity = live.engine.ledger.positions["BTC/TMN"].quantity
        assert quantity == D(10)
        assert live.engine.execution.active()
        await live.process(later(second, seconds=2, new_book=False))
        assert live.engine.ledger.positions["BTC/TMN"].quantity == quantity
        live.store.release()
        resumed = session(tmp_path, cfg)
        await resumed.process(later(second, seconds=15))
        assert resumed.engine.ledger.positions["BTC/TMN"].quantity == D(20)
        assert (await replay_decisions(resumed.store, tmp_path / "responses", WallClock()))[
            "status"
        ] == "MATCH"

    asyncio.run(scenario())


def test_stale_data_cancels_pending_buys_and_never_fills(tmp_path):
    async def scenario():
        cfg, first = setup_context()
        live = session(tmp_path, cfg)
        await live.process(first)
        stale = later(first, seconds=25, new_book=False)
        result = await live.process(stale)
        assert result["valuation_stale"] is True
        assert result["stale_symbols"] == ["BTC/TMN"]
        assert not live.engine.ledger.seen
        assert not live.engine.execution.active()
        assert live.engine.ledger.free("TMN") == 5000000

    asyncio.run(scenario())


def test_duplicate_input_and_failed_commit_are_idempotent(tmp_path, monkeypatch):
    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)
        initial = live.engine.dump()
        real = live.store.commit

        def failure(*args, **kwargs):
            raise OSError("INJECTED_DISK_FAILURE")

        monkeypatch.setattr(live.store, "commit", failure)
        with pytest.raises(OSError):
            await live.process(frame)
        assert live.engine.dump() == initial
        assert len(live.store.pending()) == 1
        assert not list(live.store.records())
        monkeypatch.setattr(live.store, "commit", real)
        await live.recover()
        committed = live.engine.dump()
        assert len(live.engine.execution.orders) == 1
        assert await live.process(frame) is None
        assert live.engine.dump() == committed
        assert len(list(live.store.records())) == 1

    asyncio.run(scenario())


def test_failed_fill_commit_rolls_back_every_mutable_ledger_field(tmp_path, monkeypatch):
    from quantpilot.config import stable_id

    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)
        await live.process(frame)
        before = live.engine.dump()
        before_id = stable_id(before)
        real = live.store.commit

        def failure(*args, **kwargs):
            raise OSError("FILL_COMMIT_FAILED")

        monkeypatch.setattr(live.store, "commit", failure)
        with pytest.raises(OSError):
            await live.process(later(frame))
        assert stable_id(before) == before_id  # Snapshot itself must not have mutated.
        assert stable_id(live.engine.dump()) == before_id
        assert not live.engine.ledger.events
        assert not live.engine.ledger.seen
        monkeypatch.setattr(live.store, "commit", real)
        await live.recover()
        assert len(live.engine.ledger.events) == 1
        assert len(live.engine.ledger.seen) == 1
        assert (await replay_decisions(live.store, tmp_path / "empty", WallClock()))[
            "status"
        ] == "MATCH"

    asyncio.run(scenario())


def test_crash_after_inbox_persistence_recovers_without_duplicate_orders(tmp_path):
    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)
        live.store.enqueue(frame)
        live.store.release()
        resumed = session(tmp_path, cfg)
        await resumed.recover()
        assert not resumed.store.pending()
        assert len(resumed.engine.execution.orders) == 1
        assert (await replay_decisions(resumed.store, tmp_path / "responses", WallClock()))[
            "status"
        ] == "MATCH"

    asyncio.run(scenario())


def test_writer_lease_config_and_journal_tamper_protection(tmp_path):
    cfg, frame = setup_context()
    live = session(tmp_path, cfg)
    other = ShadowStore(live.store.path)
    with pytest.raises(RuntimeError, match="lease"):
        other.claim("competitor", WallClock().now())
    asyncio.run(live.process(frame))
    with live.store.connect() as db:
        db.execute("UPDATE qp_shadow_frames SET output=? WHERE seq=1", (pack({"forged": True}),))
    with pytest.raises(ValueError, match="hash-chain"):
        live.store.verify()


def test_health_stop_export_and_consistent_snapshot(tmp_path):
    cfg, frame = setup_context()
    live = session(tmp_path, cfg)
    asyncio.run(live.process(frame))
    live.store.heartbeat(frame.as_of)
    status = health(live.store, frame.as_of)
    assert status["status"] == "HEALTHY"
    assert status["exchange_mutations"] == "BLOCKED"
    assert status["last_latency"]["processing_seconds"] >= 0
    assert health(live.store, frame.as_of + timedelta(seconds=40))["stale_market_data"] is True
    live.store.request_stop()
    assert live.store.control()["stop"] == 1
    with live.store.frozen() as frozen:
        export_activity(frozen, tmp_path / "export")
        assert len(list(frozen.records())) == 1
    assert (
        json.loads((tmp_path / "export/portfolio.json").read_text())["portfolio"]["account_id"]
        == "shadow"
    )
    assert (tmp_path / "export/frames.jsonl").exists()


def test_mode_precision_and_model_requirements_fail_closed():
    cfg, _ = setup_context()
    with pytest.raises(ValueError):
        ShadowConfig.model_validate({**cfg.model_dump(), "mode": "LIVE"})
    with pytest.raises(ValueError):
        ShadowConfig.model_validate({**cfg.model_dump(), "ai_mode": "QUANT_ML_LLM"})
    with pytest.raises(ValueError):
        ShadowConfig.model_validate({**cfg.model_dump(), "approved": ["BTC/IRR"]})


def test_risk_rejections_are_recorded_and_marked_loss_cancels_partial_entries(tmp_path):
    async def scenario():
        cfg, frame = setup_context()
        rejected = cfg.model_copy(
            update={"risk": cfg.risk.model_copy(update={"min_net_reward_risk": D(10)})}
        )
        live = session(tmp_path, rejected, "rejected.sqlite")
        result = await live.process(frame)
        assert result["decisions"][0]["outcome"] == "RISK_REJECTED"
        assert result["decisions"][0]["signal"]["action"] == "BUY"
        assert not live.engine.execution.orders
        cfg, frame = setup_context(book_participation=D(".001"))
        cfg = cfg.model_copy(
            update={"risk": cfg.risk.model_copy(update={"max_drawdown_fraction": D(".00000001")})}
        )
        limited = session(tmp_path, cfg, "limited.sqlite")
        await limited.process(frame)
        await limited.process(later(frame))
        quantity = limited.engine.ledger.positions["BTC/TMN"].quantity
        result = await limited.process(later(frame, seconds=30))
        assert result["portfolio"]["risk_halted"] is True
        assert limited.engine.ledger.positions["BTC/TMN"].quantity == quantity
        assert not limited.engine.execution.active()

    asyncio.run(scenario())


def test_usdt_funding_uses_observed_ask_capacity_and_toman_accounting(tmp_path):
    from quantpilot.models import MarketConstraints

    async def scenario():
        snapshot, _ = synthetic_context()
        fx_market = MarketConstraints(
            symbol="USDT/TMN",
            quote="TMN",
            spot_enabled=True,
            account_enabled=True,
            quantity_step=D(".001"),
            price_tick=D(1),
            minimum_quantity=D(".001"),
            minimum_notional=D(100),
            taker_fee_rate=D(".001"),
        )
        cfg = ShadowConfig(
            approved=(snapshot.symbol,),
            markets=(snapshot.market,),
            fx_market=fx_market,
            ai_mode="QUANT_ONLY",
            health_port=0,
        )
        fx = LiquiditySnapshot(
            as_of=snapshot.as_of,
            bids=(DepthLevel(price=D(1000), quantity=D(100)),),
            asks=(DepthLevel(price=D(1001), quantity=D(100)),),
        )
        frame = ShadowFrame(
            as_of=snapshot.as_of, snapshots=(snapshot,), fx_book=fx, depth_timestamps="FIXTURE"
        )
        live = session(tmp_path, cfg)
        first = await live.process(frame)
        # 10% of 100 USDT depth, ask+slippage rounded UP to 1003, plus 0.1% fee.
        assert live.engine.ledger.holding("USDT").quantity == 10
        assert D(first["equity_tmn"]) == D("4999959.97000")
        now = frame.as_of + timedelta(seconds=15)
        next_frame = ShadowFrame(
            as_of=now,
            snapshots=(
                snapshot.model_copy(
                    update={
                        "as_of": now,
                        "liquidity": snapshot.liquidity.model_copy(update={"as_of": now}),
                    }
                ),
            ),
            fx_book=fx.model_copy(update={"as_of": now}),
            depth_timestamps="FIXTURE",
        )
        result = await live.process(next_frame)
        assert live.engine.ledger.seen
        assert abs(
            D(result["equity_tmn"])
            - cfg.simulation.initial_capital_tmn
            - D(result["realized_pnl_tmn"])
            - D(result["unrealized_pnl_tmn"])
        ) < D("1e-20")
        assert (await replay_decisions(live.store, tmp_path / "empty", WallClock()))[
            "status"
        ] == "MATCH"

    asyncio.run(scenario())
