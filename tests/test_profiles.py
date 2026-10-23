import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal as D

import pytest

from quantpilot.backtest.cli import demo_input, execute
from quantpilot.config import EngineConfig, ExecutionMode
from quantpilot.lifecycle import LifecycleManager, LifecycleState
from quantpilot.live.storage import LiveStore
from quantpilot.profiles import OperatingProfile, ProfileConfig
from quantpilot.trading.config import RiskParameters
from quantpilot.trading.sizing import AdaptivePositionSizer

NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


@pytest.mark.parametrize("mode", list(ExecutionMode))
@pytest.mark.parametrize("profile", list(OperatingProfile))
def test_independent_modes(mode, profile):
    cfg = EngineConfig(mode=mode, operating_profile=profile)
    assert cfg.mode == mode and cfg.operating_profile == profile
    assert not cfg.live_execution_enabled


def test_indefinite_and_legacy():
    cfg = ProfileConfig()
    for days in (0, 3, 365, 3650):
        now = NOW + timedelta(days=days)
        assert cfg.entries_allowed(now) and not cfg.settling(now, now)
        assert not cfg.expired(now)
    legacy = ProfileConfig(deadline=NOW)
    assert legacy.operating_profile == OperatingProfile.COMPETITION
    assert legacy.settling(NOW - timedelta(seconds=1))
    assert not legacy.entries_allowed(NOW)
    with pytest.raises(ValueError):
        ProfileConfig(operating_profile="CONTINUOUS", deadline=NOW)


def test_optional_competition_policies():
    cfg = ProfileConfig(
        operating_profile="COMPETITION",
        starts_at=NOW,
        deadline=NOW + timedelta(days=3),
        force_final_liquidation=False,
    )
    assert not cfg.entries_allowed(NOW - timedelta(seconds=1))
    assert not cfg.settling(cfg.deadline)
    assert not cfg.entries_allowed(cfg.deadline)


def test_dynamic_time_independent_sizer():
    def size(equity):
        return AdaptivePositionSizer.quantity(
            price=D(100),
            loss_per_unit=D(10),
            risk_budget=equity * D(".005"),
            quote_to_tmn=D(1),
            notional_cap=equity * D(".1"),
        )

    assert size(D(2000)) == 2 * size(D(1000))
    assert RiskParameters().absolute_order_hard_cap_tmn == D(500000)
    assert RiskParameters(absolute_order_hard_cap_tmn=None).absolute_order_hard_cap_tmn is None


def test_durable_restart_and_shutdown_do_not_sell(tmp_path):
    path = tmp_path / "lifecycle.sqlite"
    store = LiveStore(path, "test-only")
    with store.db:
        manager = LifecycleManager(store)
        assert not manager.permits("BUY")
        with pytest.raises(ValueError):
            manager.resume(reconciled=False, orders_known=True, risk_ok=True, authorized=True)
        manager.resume(reconciled=True, orders_known=True, risk_ok=True, authorized=True)
        manager.command("STOP_NEW_ENTRIES")
        assert not manager.permits("BUY") and manager.permits("SELL")
        manager.command("GRACEFUL_SHUTDOWN")
        assert not manager.permits("SELL")
        manager.stopped()
    assert store.orders() == ()
    store.close()
    store = LiveStore(path, "test-only")
    with store.db:
        manager = LifecycleManager(store)
        assert manager.state == LifecycleState.STARTING
        assert not manager.permits("BUY") and not manager.permits("SELL")
    assert store.orders() == ()
    store.close()


def test_replay_profiles_same_core(monkeypatch):
    from quantpilot.backtest.replay import HistoricalReplay

    calls = []
    original = HistoricalReplay.liquidate

    async def tracked(self, now):
        calls.append(now)
        await original(self, now)

    monkeypatch.setattr(HistoricalReplay, "liquidate", tracked)
    raw = demo_input()
    raw["candles"]["BTC/TMN"] = raw["candles"]["BTC/TMN"][:3]
    continuous = asyncio.run(execute(raw))
    assert not calls
    raw["simulation"] = {"operating_profile": "COMPETITION", "force_final_liquidation": True}
    competition = asyncio.run(execute(raw))
    assert (
        continuous["manifest"]["configuration"]["simulation"]["operating_profile"] == "CONTINUOUS"
    )
    assert (
        competition["manifest"]["configuration"]["simulation"]["operating_profile"] == "COMPETITION"
    )
    assert competition["metrics"]["fully_settled_tmn"]
    assert len(calls) == 1
