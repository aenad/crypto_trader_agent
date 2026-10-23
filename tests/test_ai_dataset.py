import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from quantpilot.ai.cli import synthetic_input
from quantpilot.ai.dataset import build_dataset, label_entry, market_input
from quantpilot.ai.domain import FeatureVector, LearningConfig
from quantpilot.ai.evaluation import samples_from
from quantpilot.backtest.config import SimulationParameters
from quantpilot.backtest.history import HistoricalMarketDataProvider
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.models import Candle, MarketConstraints, RiskDecision, Signal
from quantpilot.trading.config import ResearchParameters, RiskParameters

D = Decimal
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def label_fixture(participation=".1"):
    rows = []
    for index, price in enumerate((100, 100, 100, 110, 110)):
        end = NOW + timedelta(minutes=5 * (index + 1))
        rows.append(
            Candle(
                event_id=str(index),
                symbol="BTC/TMN",
                event_time=end,
                received_at=end,
                source="synthetic",
                open_time=end - timedelta(minutes=5),
                close_time=end,
                open=D(price),
                close=D(price),
                high=D(price + 1),
                low=D(price - 1),
                volume=D(100),
                closed=True,
            )
        )
    market = MarketConstraints(
        symbol="BTC/TMN",
        quote="TMN",
        spot_enabled=True,
        account_enabled=True,
        quantity_step=D(".001"),
        price_tick=D(".01"),
        minimum_quantity=D(".001"),
        minimum_notional=D(1),
        taker_fee_rate=D(".001"),
    )
    data = HistoricalMarketDataProvider(
        {"BTC/TMN": tuple(rows)},
        {"BTC/TMN": market},
        ResearchParameters(),
        SimulationParameters(volume_participation=D(participation), exit_fee=D(".002")),
    )
    replay = HistoricalReplay(data, RiskParameters(), ("BTC/TMN",))
    signal = Signal(
        symbol="BTC/TMN",
        as_of=rows[0].close_time,
        action="BUY",
        strategy_version="fixture",
        reasons=("FIXTURE",),
        atr=D(5),
    )
    risk = RiskDecision(allowed=True, reasons=("FIXTURE",), reference_price=D(101), quantity=D(1))
    return replay, signal, risk


def test_labels_use_next_open_execution_and_all_costs_hand_calculated():
    replay, signal, risk = label_fixture()
    result, status = asyncio.run(label_entry(replay, signal, risk, LearningConfig(label_bars=2)))
    assert status == "LABELED"
    end, pnl, net = result
    # Buy 100.16 + 0.10016; sell 109.83 - 0.21966.
    assert pnl == D("9.35018")
    assert end == NOW + timedelta(minutes=15)
    assert abs(net - pnl / D("100.26016")) < D("1e-26")


def test_incomplete_execution_and_unavailable_future_are_censored():
    replay, signal, risk = label_fixture(".001")
    assert (
        asyncio.run(label_entry(replay, signal, risk, LearningConfig(label_bars=2)))[1]
        == "ENTRY_NOT_FULLY_EXECUTABLE"
    )
    assert (
        asyncio.run(label_entry(replay, signal, risk, LearningConfig(label_bars=20)))[1]
        == "RIGHT_CENSORED"
    )


def test_dataset_contains_only_eligible_signals_and_no_targets_in_features():
    raw = synthetic_input(96)
    config = LearningConfig(label_bars=2, embargo_seconds=0)
    bundle = asyncio.run(build_dataset(raw, config))
    rows = samples_from(bundle)
    assert rows
    assert bundle["manifest"]["counts"]["ELIGIBLE_SIGNALS"] >= len(rows)
    assert all(tuple(r.features.model_dump()) == FeatureVector.names() for r in rows)
    assert all(r.label_end > r.as_of for r in rows)
    assert not any("label" in k or "pnl" in k or "profit" in k for k in FeatureVector.names())
    restricted = synthetic_input(96)
    restricted["approved"] = []
    empty = asyncio.run(build_dataset(restricted, config))
    assert not empty["samples"]


def test_future_perturbation_does_not_change_earlier_features_or_matured_labels():
    raw = synthetic_input(96)
    config = LearningConfig(label_bars=2, embargo_seconds=0)
    first = asyncio.run(build_dataset(raw, config))
    changed = synthetic_input(96)
    cutoff = changed["candles"]["BTC/TMN"][72]["open_time"]
    for row in changed["candles"]["BTC/TMN"][72:]:
        for key in ("open", "close", "high", "low"):
            row[key] = str(D(row[key]) * 2)
        row["volume"] = "1000"
    second = asyncio.run(build_dataset(changed, config))
    before = [r for r in first["samples"] if r["label_end"] < cutoff]
    after = [r for r in second["samples"] if r["label_end"] < cutoff]
    assert before and before == after


def test_dataset_checksum_and_market_history_validation():
    raw = synthetic_input(96)
    bundle = asyncio.run(build_dataset(raw, LearningConfig(label_bars=2)))
    bundle["samples"][0]["features"]["rsi"] = "99"
    with pytest.raises(ValueError, match="checksum"):
        samples_from(bundle)
    raw["candles"]["BTC/TMN"][1]["symbol"] = "ETH/TMN"
    with pytest.raises(ValueError):
        market_input(raw)
