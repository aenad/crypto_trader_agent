"""Out-of-time predictive evaluation and A/B/C portfolio ablation on one window."""

import csv
import json
import random
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from quantpilot.backtest.history import HistoricalClock
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.backtest.reports import export_report
from quantpilot.config import stable_id
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

from .analyst import AnalystHarness, ReplayOnlyProvider, ResponseStore, record_fixture
from .dataset import funded_ledger, market_input
from .domain import LearningConfig, Sample
from .features import assemble_context
from .fusion import HybridEvaluator
from .learning import FrozenModel, predictive_metrics, train
from .splits import chronological_split, walk_forward


def samples_from(bundle: dict[str, Any]) -> tuple[Sample, ...]:
    expected = stable_id({"manifest": bundle["manifest"], "samples": bundle["samples"]})
    if expected != bundle["dataset_id"]:
        raise ValueError("Dataset checksum mismatch")
    return tuple(Sample.model_validate(r) for r in bundle["samples"])


def score(model: FrozenModel, rows: tuple[Sample, ...]) -> dict[str, Any]:
    if not rows:
        return {"status": "NO_SAMPLES"}
    raw, predictions = model.probabilities([r.features for r in rows])
    labels = [r.positive for r in rows]
    baseline = [float(model.metadata["training_positive_rate"])] * len(labels)
    return {
        "calibrated": predictive_metrics(labels, predictions),
        "uncalibrated": predictive_metrics(labels, raw),
        "training_prior_baseline": predictive_metrics(labels, baseline),
    }


def training_report(
    bundle: dict[str, Any], config: LearningConfig
) -> tuple[FrozenModel, dict[str, Any]]:
    rows = samples_from(bundle)
    split = chronological_split(rows, config.embargo_seconds)
    if len(split.test) < config.minimum_test:
        raise ValueError("Insufficient untouched test samples")
    research_id = stable_id(bundle["manifest"]["research"])
    model = train(split, config, bundle["dataset_id"], research_id)
    folds = []
    for index, fold in enumerate(walk_forward(rows, split.test_start, config.embargo_seconds)):
        try:
            fitted = train(fold, config, bundle["dataset_id"], research_id)
            if len(fold.test) < config.minimum_test:
                raise ValueError("Insufficient forward fold samples")
            folds.append(
                {
                    "fold": index,
                    "status": "EVALUATED",
                    "train_count": len(fold.train),
                    "validation_count": len(fold.validation),
                    "test_count": len(fold.test),
                    "purged": fold.purged,
                    "model_version": fitted.model_version,
                    "test_start": fold.test_start.isoformat(),
                    "metrics": score(fitted, fold.test),
                }
            )
        except ValueError as error:
            folds.append({"fold": index, "status": "INSUFFICIENT_DATA", "reason": str(error)})
    report = {
        "model_version": model.model_version,
        "dataset_id": bundle["dataset_id"],
        "train_count": len(split.train),
        "validation_count": len(split.validation),
        "test_count": len(split.test),
        "purged": split.purged,
        "validation_start": split.validation_start.isoformat(),
        "test_start": split.test_start.isoformat(),
        "fitted_validation_diagnostics": score(model, split.validation),
        "walk_forward": folds,
        "test_labels_used_for_training_or_calibration": False,
        "threshold_source": "Predeclared LearningConfig; not optimized on final holdout",
        "deployment_enabled": False,
    }
    return model, report


def daily_returns(report: dict[str, Any], start: datetime) -> dict[str, float]:
    initial = float(report["metrics"]["initial_capital_tmn"])
    days: dict[str, float] = {}
    for row in report["equity_curve"]:
        timestamp = datetime.fromisoformat(row["at"])
        if timestamp >= start:
            days[timestamp.date().isoformat()] = float(row["equity_tmn"])
    result = {}
    previous = initial
    for day, value in sorted(days.items()):
        result[day] = (value - previous) / initial
        previous = value
    return result


def paired_uncertainty(
    baseline: dict[str, Any], variant: dict[str, Any], start: datetime, seed: int = 173
) -> dict[str, Any]:
    a, b = daily_returns(baseline, start), daily_returns(variant, start)
    days = sorted(set(a) & set(b))
    if len(days) < 5:
        return {
            "status": "INCONCLUSIVE_TOO_FEW_DAY_BLOCKS",
            "day_blocks": len(days),
            "return_difference_95pct_interval": None,
        }
    # Paired UTC day-block bootstrap; uncertainty estimate, not independent-trade CI.
    differences = [b[day] - a[day] for day in days]
    rng = random.Random(seed)
    values = sorted(sum(rng.choice(differences) for _ in days) * 100 for _ in range(1000))
    return {
        "status": "EXPLORATORY_PAIRED_DAY_BOOTSTRAP",
        "day_blocks": len(days),
        "seed": seed,
        "replicates": 1000,
        "return_difference_95pct_interval": [values[24], values[974]],
        "limitations": "Serial dependence and universe/sample selection uncertainty may remain",
    }


async def seed_demo_responses(
    raw: dict[str, Any], bundle: dict[str, Any], store: ResponseStore, model_id: str
) -> None:
    data, risk, approved, fx = market_input(raw)
    replay = HistoricalReplay(data, risk, approved, fx)
    strategy = MomentumBreakout(data.research, MarketEligibilityFilter(approved))
    for sample in samples_from(bundle):
        snapshot = await data.snapshot(sample.symbol, sample.as_of)
        ledger = funded_ledger(replay, sample.as_of)
        conversions = replay.conversions(sample.as_of)
        marks = {"USDT": replay.rate(sample.as_of)} if conversions else {}
        signal = strategy.evaluate(snapshot, ledger.snapshot(sample.as_of, marks, conversions))
        if signal.action != "BUY":
            raise ValueError("Dataset no longer matches strategy")
        context = assemble_context(snapshot, signal, data.research)
        record_fixture(
            store,
            context,
            model_id,
            "VETO" if context.features.atr_fraction > Decimal("0.018") else "ACCEPT",
        )


async def evaluate(
    raw: dict[str, Any],
    bundle: dict[str, Any],
    model: FrozenModel,
    config: LearningConfig,
    output: Path,
    responses: ResponseStore,
    analyst_model_id: str,
    synthetic: bool = False,
) -> dict[str, Any]:
    rows = samples_from(bundle)
    if (
        model.metadata["dataset_id"] != bundle["dataset_id"]
        or bundle["manifest"]["source_id"] != stable_id(raw)
        or model.metadata["config"] != config.model_dump(mode="json")
    ):
        raise ValueError("Evaluation provenance/configuration does not match frozen model")
    split = chronological_split(rows, config.embargo_seconds)
    if len(split.test) < config.minimum_test:
        raise ValueError("Insufficient test data")
    if max(r.label_end for r in split.train + split.validation) >= split.test_start:
        raise ValueError("Training/calibration labels overlap holdout")
    data, risk, approved, fx = market_input(raw)
    harness = AnalystHarness(
        ReplayOnlyProvider(analyst_model_id),
        responses,
        HistoricalClock(split.test_start),
        replay_only=True,
    )
    variants = {
        "A_QUANT": None,
        "B_QUANT_ML": HybridEvaluator(model, data.research, "QUANT_ML"),
        "C_QUANT_ML_LLM": HybridEvaluator(model, data.research, "QUANT_ML_LLM", harness),
    }
    cache_id = stable_id(
        {
            path.name: stable_id(json.loads(path.read_text(encoding="utf-8")))
            for path in sorted(responses.root.glob("*.json"))
        }
    )
    portfolios = {}
    for name, evaluator in variants.items():
        identity = (
            stable_id(
                {
                    "variant": name,
                    "model": model.model_version,
                    "policy": "veto-only-v1",
                    "analyst": analyst_model_id,
                    "responses": cache_id,
                }
            )
            if evaluator
            else None
        )
        replay = HistoricalReplay(
            data,
            risk,
            approved,
            fx,
            evaluator=evaluator,
            decision_start=split.test_start,
            evaluation_id=identity,
        )
        report = await replay.run()
        export_report(report, output / name)
        portfolios[name] = report
        if evaluator:
            (output / name / "recommendations.json").write_text(
                json.dumps(
                    [r.model_dump(mode="json") for r in evaluator.recommendations],
                    sort_keys=True,
                    indent=2,
                ),
                encoding="utf-8",
            )
    traces = harness.traces
    valid = sum(t["status"] == "REPLAYED" for t in traces)
    retrospective = sum(
        datetime.fromisoformat(t["recorded_at"])
        > datetime.fromisoformat(t["input_snapshot"]["as_of"])
        for t in traces
        if t.get("recorded_at")
    )
    uncertainty = {
        name: paired_uncertainty(portfolios["A_QUANT"], report, split.test_start, config.seed)
        for name, report in portfolios.items()
        if name != "A_QUANT"
    }
    reasons = ["Research-only evaluation; no deployment automatically enabled"]
    if synthetic or any(t.get("evidence") == "SYNTHETIC_FIXTURE" for t in traces):
        reasons.append("Synthetic data/responses cannot establish trading or LLM effectiveness")
    if not traces or valid != len(traces):
        reasons.append("LLM response coverage incomplete or absent")
    if retrospective:
        reasons.append(
            "Retrospective LLM responses: model future-knowledge contamination cannot be ruled out"
        )
    if int(portfolios["B_QUANT_ML"]["metrics"]["trade_count"]) == 0:
        reasons.append("No ML-selected closed trades; incremental LLM trading value unmeasured")
    if any(
        int(r["metrics"]["trade_count"]) < config.minimum_promotion_trades
        for r in portfolios.values()
    ):
        reasons.append("Insufficient holdout closed trades for promotion")
    if any(u["status"] == "INCONCLUSIVE_TOO_FEW_DAY_BLOCKS" for u in uncertainty.values()):
        reasons.append("Insufficient independent time blocks for reliable uncertainty estimates")
    result = {
        "schema": "hybrid-ablation-v1",
        "model_version": model.model_version,
        "dataset_id": bundle["dataset_id"],
        "test_start": split.test_start.isoformat(),
        "test_end": max(c[-1].close_time for c in data.candles.values()).isoformat(),
        "initial_capital_tmn": str(data.simulation.initial_capital_tmn),
        "shared_inputs": "Identical history/universe/window/capital/strategy/risk/costs/execution",
        "predictive_holdout": score(model, split.test),
        "uncertainty": uncertainty,
        "variants": {
            name: {"metrics": report["metrics"], "run_id": report["manifest"]["run_id"]}
            for name, report in portfolios.items()
        },
        "llm": {
            "model_id": analyst_model_id,
            "requested": len(traces),
            "replayed_valid": valid,
            "retrospective_responses": retrospective,
            "historical_network_calls": 0,
            "future_news_or_labels_in_context": False,
        },
        "promotion": {"status": "NOT_ENABLED", "reasons": reasons},
        "limitations": [
            "Cost-aware fixed-horizon label is a proxy for strategy lifecycle returns",
            "Conditional full-fill labels exclude censored opportunities; inspect dataset counts",
            "Same-clock next-open execution assumes zero compute latency",
            "Time-valid context cannot guarantee historically available pretrained knowledge",
            "No prospective shadow, real LLM efficacy or universe generalization established",
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    prediction_rows = []
    for sample in split.test:
        prediction = model.predict(sample.features, sample.as_of)
        prediction_rows.append(
            {
                "sample_id": sample.sample_id,
                "symbol": sample.symbol,
                "as_of": sample.as_of.isoformat(),
                "label_end": sample.label_end.isoformat(),
                "positive": sample.positive,
                "net_return": str(sample.net_return),
                "model_version": model.model_version,
                "raw_probability": str(prediction.raw_probability),
                "probability": str(prediction.probability),
                "quality": prediction.quality,
                **sample.features.model_dump(mode="json"),
            }
        )
    with (output / "holdout-predictions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(prediction_rows[0]))
        writer.writeheader()
        writer.writerows(prediction_rows)
    (output / "analyst-traces.json").write_text(
        json.dumps(traces, sort_keys=True, indent=2), encoding="utf-8"
    )
    (output / "ai-evaluation.json").write_text(
        json.dumps(result, sort_keys=True, indent=2), encoding="utf-8"
    )
    (output / "ai-evaluation.md").write_text(markdown_report(result), encoding="utf-8")
    return result


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Hybrid AI evaluation",
        "",
        "Status: **research only; AI deployment NOT enabled**.",
        "",
        f"Model: `{report['model_version']}`",
        f"Holdout starts: {report['test_start']}",
        "",
        "| Variant | Net return % | Max drawdown % | Closed trades | Fees TMN |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, variant in report["variants"].items():
        m = variant["metrics"]
        lines.append(
            f"| {name} | {m['net_return_pct']} | {m['max_drawdown_pct']} "
            f"| {m['trade_count']} | {m['total_fees_tmn']} |"
        )
    lines.extend(
        ["", "## Promotion and uncertainty", ""]
        + [f"- {r}" for r in report["promotion"]["reasons"]]
    )
    lines.extend(
        [
            "",
            "See ai-evaluation.json for metrics, calibration, uncertainty and provenance.",
            "",
        ]
    )
    return "\n".join(lines)
