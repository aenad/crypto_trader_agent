"""Offline safeguards for the bounded research runner, not strategy profitability."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from quantpilot.backtest.cli import demo_input
from quantpilot.trading.config import ResearchParameters, RiskParameters
from research.strategy_study import aggregate, load_minutes, make_input, select, summarize


def cache(path, timestamps, closes=None):
    prices = closes or [100] * len(timestamps)
    path.write_text(
        json.dumps(
            {
                "s": "ok",
                "t": timestamps,
                "o": prices,
                "h": prices,
                "l": prices,
                "c": prices,
                "v": [1] * len(prices),
            }
        )
    )


def test_research_splits_actual_gaps_and_deduplicates_without_inventing_candles(tmp_path):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t = int(start.timestamp())
    cache(tmp_path / "a.json", [t, t + 60, t + 180])
    cache(tmp_path / "b.json", [t + 60, t + 240])
    segments, hashes, duplicates = load_minutes(tmp_path, start, start + timedelta(minutes=5))
    assert [len(s) for s in segments] == [2, 2]
    assert duplicates == 1 and len(hashes) == 2
    assert not any(aggregate(s) for s in segments)
    cache(tmp_path / "c.json", [t + 60], [101])
    with pytest.raises(ValueError, match="Conflicting duplicate"):
        load_minutes(tmp_path, start, start + timedelta(minutes=5))


def test_research_rejects_malformed_arrays_and_excludes_incomplete_terminal_minute(tmp_path):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    t = int(start.timestamp())
    cache(tmp_path / "a.json", [t, t + 60])
    segments, _, _ = load_minutes(tmp_path, start, start + timedelta(seconds=90))
    assert sum(len(s) for s in segments) == 1
    raw = json.loads((tmp_path / "a.json").read_text())
    raw["v"] = []
    (tmp_path / "a.json").write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="Mismatched"):
        load_minutes(tmp_path, start, start + timedelta(minutes=5))


def test_research_scenarios_preserve_risk_and_spot_guards():
    m = {
        "plan": {
            "scenarios": {
                "taker": {
                    "fee_source": "observed_taker",
                    "slippage": "0.001",
                    "half_spread": "0.0005",
                    "volume_participation": "0.01",
                },
                "adverse": {
                    "fee_source": "stress",
                    "fee": "0.005",
                    "slippage": "0.002",
                    "half_spread": "0.001",
                    "volume_participation": "0.005",
                },
            }
        },
        "market": {
            "maker_fee": "0.0025",
            "taker_fee": "0.003",
            "quantity_step": "0.00000001",
            "price_tick": "1",
            "minimum_quantity": "0.00000001",
            "minimum_notional": "50000",
        },
        "research": ResearchParameters().model_dump(mode="json"),
        "risk": RiskParameters().model_dump(mode="json"),
    }
    for scenario in ("taker", "adverse"):
        raw = make_input(m, [], {"target_atr": "8"}, scenario)
        observed = RiskParameters.model_validate(raw["risk"])
        baseline = RiskParameters()
        for field in RiskParameters.model_fields:
            if field != "slippage_fraction":
                assert getattr(observed, field) == getattr(baseline, field)
        assert observed.slippage_fraction >= baseline.slippage_fraction
        assert raw["simulation"]["operating_profile"] == "CONTINUOUS"
        assert raw["research"]["stop_atr"] == "2"
        assert Decimal(raw["markets"]["BTC/TMN"]["minimum_notional"]) == 50000


def test_selection_never_accepts_final_results_and_does_not_force_winner():
    policy = {
        "minimum_train_trades": 20,
        "minimum_validation_trades": 10,
        "maximum_drawdown_pct": "5",
    }

    def outcome(trades, net):
        return {"metrics": {"trade_count": trades, "net_return_pct": net, "max_drawdown_pct": "1"}}

    pair = {"train": outcome(30, "1"), "validation": outcome(11, "-0.1")}
    result = select({"B_target8": pair}, policy)
    assert result["candidate_supported"] is False and result["selected"] == "A_baseline"
    pair["validation"] = outcome(11, "0.2")
    assert select({"B_target8": pair}, policy)["selected"] == "B_target8"
    pair["final"] = outcome(100, "999")
    with pytest.raises(ValueError, match="train/validation only"):
        select({"B_target8": pair}, policy)


def test_research_summary_uses_existing_engine_and_reports_no_trade_uncertainty():
    from quantpilot.backtest.cli import execute

    raw = demo_input()
    raw["candles"]["BTC/TMN"] = raw["candles"]["BTC/TMN"][:3]
    report = asyncio.run(execute(raw))
    result = summarize(report)
    assert result["actions"] == {"HOLD": 3}
    assert result["metrics"]["trade_count"] == 0
    assert result["pnl_distribution"]["mean"] is None
    assert result["pnl_distribution"]["values_tmn"] == []
