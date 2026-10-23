import asyncio
import json
from datetime import datetime, timedelta, timezone

import pytest

from quantpilot.ai.analyst import ResponseStore
from quantpilot.ai.cli import read_json, synthetic_input
from quantpilot.ai.dataset import build_dataset, market_input
from quantpilot.ai.domain import LearningConfig
from quantpilot.ai.evaluation import (
    evaluate,
    paired_uncertainty,
    seed_demo_responses,
    training_report,
)
from quantpilot.ai.learning import FrozenModel
from quantpilot.backtest.replay import HistoricalReplay


def test_real_training_artifact_and_recorded_llm_ablation_are_reproducible(tmp_path):
    pytest.importorskip("lightgbm")

    async def scenario():
        raw = synthetic_input(240)
        config = LearningConfig(
            label_bars=2,
            embargo_seconds=0,
            minimum_train=10,
            minimum_validation=5,
            minimum_test=5,
            min_data_in_leaf=3,
            rounds=10,
        )
        bundle = await build_dataset(raw, config)
        model, development = training_report(bundle, config)
        path = model.save(tmp_path / "models")
        model = FrozenModel.load(path)
        responses = ResponseStore(tmp_path / "responses")
        await seed_demo_responses(raw, bundle, responses, "SYNTHETIC_TEST_ONLY")
        first = await evaluate(
            raw, bundle, model, config, tmp_path / "first", responses, "SYNTHETIC_TEST_ONLY", True
        )
        second = await evaluate(
            raw, bundle, model, config, tmp_path / "second", responses, "SYNTHETIC_TEST_ONLY", True
        )
        assert first == second
        assert development["test_labels_used_for_training_or_calibration"] is False
        assert len(development["walk_forward"]) == 2
        assert first["promotion"]["status"] == "NOT_ENABLED"
        assert first["llm"]["historical_network_calls"] == 0
        assert first["llm"]["requested"] > 0
        assert first["llm"]["replayed_valid"] > 0
        ids = {v["run_id"] for v in first["variants"].values()}
        assert len(ids) == 3
        for variant in first["variants"]:
            assert (tmp_path / "first" / variant / "ledger.csv").is_file()
            report = json.loads((tmp_path / "first" / variant / "report.json").read_text())
            assert report["metrics"]["initial_capital_tmn"] == "5000000"
            assert all(row["at"] >= first["test_start"] for row in report["equity_curve"])
            assert report["manifest"]["configuration"]["decision_start"] == first["test_start"]
        assert (tmp_path / "first/ai-evaluation.md").exists()
        assert (tmp_path / "first/ai-evaluation.json").exists()
        assert (tmp_path / "first/holdout-predictions.csv").exists()
        traces = json.loads((tmp_path / "first/analyst-traces.json").read_text())
        assert all(t["status"] in ("REPLAYED", "CACHE_MISS") for t in traces)
        changed = synthetic_input(240)
        changed["risk"]["min_net_reward_risk"] = "0.6"
        with pytest.raises(ValueError, match="provenance"):
            await evaluate(
                changed,
                bundle,
                model,
                config,
                tmp_path / "invalid",
                responses,
                "SYNTHETIC_TEST_ONLY",
            )

    asyncio.run(scenario())


def test_uncertainty_uses_paired_day_blocks_and_marks_small_samples_inconclusive():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def report(extra, days):
        return {
            "metrics": {"initial_capital_tmn": "5000000"},
            "equity_curve": [
                {
                    "at": (start + timedelta(days=i)).isoformat(),
                    "equity_tmn": str(5000000 + extra * i),
                }
                for i in range(days)
            ],
        }

    small = paired_uncertainty(report(0, 3), report(100, 3), start)
    assert small["return_difference_95pct_interval"] is None
    first = paired_uncertainty(report(0, 8), report(100, 8), start)
    assert first == paired_uncertainty(report(0, 8), report(100, 8), start)
    assert first["return_difference_95pct_interval"][0] > 0


def test_json_cli_input_preserves_exact_decimal_tokens(tmp_path):
    path = tmp_path / "number.json"
    path.write_text('{"price": 0.12345678901234567890123456789}', encoding="utf-8")
    assert read_json(path)["price"] == "0.12345678901234567890123456789"


def test_holdout_capital_and_fx_accounting_exclude_training_period_gains():
    from decimal import Decimal

    raw = synthetic_input(3)
    candles = raw["candles"].pop("BTC/TMN")
    for candle in candles:
        candle["symbol"] = "BTC/USDT"
    raw["candles"]["BTC/USDT"] = candles
    market = raw["markets"].pop("BTC/TMN")
    market.update(symbol="BTC/USDT", quote="USDT")
    raw["markets"]["BTC/USDT"] = market
    raw["approved"] = ["BTC/USDT"]
    raw["fx"] = [
        {"quote": "USDT", "tmn_per_unit": "1000" if index == 0 else "2000", "as_of": timestamp}
        for index, timestamp in enumerate(
            [row["open_time"] for row in candles] + [candles[-1]["close_time"]]
        )
    ]
    data, risk, approved, fx = market_input(raw)
    start = data.candles["BTC/USDT"][1].open_time
    report = asyncio.run(HistoricalReplay(data, risk, approved, fx, decision_start=start).run())
    assert report["equity_curve"][0]["at"] == start.isoformat()
    assert report["equity_curve"][0]["equity_tmn"] == "5000000"
    metrics = report["metrics"]
    assert metrics["trade_count"] == 0
    assert abs(
        Decimal(metrics["final_equity_tmn"]) + Decimal(metrics["total_fees_tmn"]) - Decimal(5000000)
    ) < Decimal("1e-20")
