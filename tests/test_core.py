import asyncio
from datetime import timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from quantpilot.config import EngineConfig, ExecutionMode, stable_id
from quantpilot.demo import FixedClock, MockMarketData, make_demo
from quantpilot.models import Candle, MarketSnapshot, Money


def test_decimal_and_currency_contract():
    assert Money(amount="10.25", currency="TMN").amount == Decimal("10.25")
    assert Money(amount="10", currency="TMN") != Money(amount="10", currency="IRR")
    for value in (0.1, True, "NaN", "Infinity", "-1"):
        with pytest.raises(ValidationError):
            Money(amount=value, currency="TMN")


def test_canonical_config_and_mode_validation():
    assert stable_id({"a": 1, "b": 2}) == stable_id({"b": 2, "a": 1})
    assert EngineConfig().config_id == EngineConfig.from_env({}).config_id
    assert EngineConfig(mode=ExecutionMode.BACKTEST).config_id != EngineConfig().config_id
    with pytest.raises(ValidationError):
        EngineConfig(live_execution_enabled=True)
    with pytest.raises(ValueError):
        EngineConfig.from_env({"QUANTPILOT_MODE": "invalid"})


def test_candle_point_in_time_and_ordering():
    now = FixedClock().now()
    snapshot = asyncio.run(MockMarketData().snapshot("BTC/USDT", now))
    candle = snapshot.candles[0]
    for updates in ({"high": "1"}, {"event_time": now.replace(tzinfo=None)}, {"volume": -1}):
        with pytest.raises(ValidationError):
            Candle.model_validate({**candle.model_dump(), **updates})
    for candles in (
        (candle, candle),
        (Candle.model_validate({**candle.model_dump(), "closed": False}),),
    ):
        with pytest.raises(ValidationError):
            MarketSnapshot(symbol="BTC/USDT", as_of=now, candles=candles, source="test")
    with pytest.raises(ValidationError):
        MarketSnapshot(
            symbol="BTC/USDT", as_of=now - timedelta(seconds=1), candles=(candle,), source="test"
        )


@pytest.mark.parametrize("mode", [ExecutionMode.BACKTEST, ExecutionMode.SHADOW])
def test_shared_engine_deterministic_and_no_execution(mode):
    async def run():
        engine = make_demo(EngineConfig(mode=mode))
        first = await engine.observe("BTC/USDT", "offline-demo")
        second = await engine.observe("BTC/USDT", "offline-demo")
        assert first == second
        assert first.signal.action == "HOLD"
        assert not first.risk.allowed
        assert first.execution_state == "NOT_SUBMITTED"
        assert engine.execution is None

    asyncio.run(run())


def test_live_stops_before_data_access():
    class Tripwire:
        async def snapshot(self, *args):
            raise AssertionError("LIVE accessed data")

    engine = make_demo(EngineConfig(mode=ExecutionMode.LIVE))
    engine.data = Tripwire()
    with pytest.raises(RuntimeError, match="LIVE runs disabled"):
        asyncio.run(engine.observe("BTC/USDT", "offline-demo"))


def test_wrong_account_rejected():
    engine = make_demo()
    with pytest.raises(KeyError):
        asyncio.run(engine.observe("BTC/USDT", "another-account"))


def test_audit_failure_prevents_event_publication():
    class BrokenAudit:
        async def append(self, record):
            raise OSError("Synthetic storage failure")

    engine = make_demo()
    engine.decisions = BrokenAudit()
    with pytest.raises(OSError):
        asyncio.run(engine.observe("BTC/USDT", "offline-demo"))
    assert engine.bus.events == []


def test_structured_logging_omits_arbitrary_messages():
    import json
    import logging

    from quantpilot.logging import JsonFormatter

    event = logging.LogRecord("test", logging.INFO, "", 0, "untrusted-payload", (), None)
    encoded = JsonFormatter().format(event)
    assert "untrusted-payload" not in encoded
    assert json.loads(encoded)["level"] == "INFO"


def test_record_json_round_trip():
    from quantpilot.models import DecisionRecord

    result = asyncio.run(make_demo().observe("BTC/USDT", "offline-demo"))
    assert DecisionRecord.model_validate_json(result.model_dump_json()) == result
