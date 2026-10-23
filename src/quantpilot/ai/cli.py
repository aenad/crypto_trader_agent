"""Offline hybrid-AI research CLI. No exchange orders or live enablement."""

import argparse
import asyncio
import json
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from quantpilot.models import Candle, MarketConstraints

from .analyst import ResponseStore
from .dataset import build_dataset
from .domain import LearningConfig
from .evaluation import evaluate, seed_demo_responses, training_report
from .learning import FrozenModel


def synthetic_input(count: int = 480) -> dict[str, Any]:
    """Seeded synthetic market, unoptimized short windows for plumbing only."""
    rng = random.Random(173)
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    rows: list[dict[str, Any]] = []
    previous = Decimal(100000)
    for i in range(count):
        opening = previous
        close = opening + Decimal(rng.choice((-900, -450, 200, 600, 1200)))
        if i % 6 == 0:
            prior = max((Decimal(c["high"]) for c in rows[-5:]), default=opening)
            close = max(close, prior + Decimal(400))
        close = max(Decimal(50000), close)
        end = start + timedelta(minutes=5 * (i + 1))
        row = Candle(
            event_id=f"phase5-synthetic:{i}",
            symbol="BTC/TMN",
            event_time=end,
            received_at=end,
            source="SYNTHETIC_PHASE5_NOT_WALLEX",
            open_time=end - timedelta(minutes=5),
            close_time=end,
            open=opening,
            close=close,
            high=max(opening, close) + 100,
            low=min(opening, close) - 100,
            volume=Decimal(800 if i % 6 == 0 else 200),
            closed=True,
        )
        rows.append(row.model_dump(mode="json"))
        previous = close
    market = MarketConstraints(
        symbol="BTC/TMN",
        quote="TMN",
        spot_enabled=True,
        account_enabled=True,
        quantity_step=Decimal("0.001"),
        price_tick=Decimal(1),
        minimum_quantity=Decimal("0.001"),
        minimum_notional=Decimal(100),
        taker_fee_rate=Decimal("0.001"),
    )
    return {
        "candles": {"BTC/TMN": rows},
        "markets": {"BTC/TMN": market.model_dump(mode="json")},
        "approved": ["BTC/TMN"],
        "research": {
            "ema_fast": 3,
            "ema_slow": 8,
            "breakout_window": 5,
            "volume_window": 5,
            "atr_period": 3,
            "rsi_period": 5,
            "adx_period": 3,
            "rsi_min": "1",
            "rsi_max": "99",
            "min_adx": "0",
        },
        "simulation": {"volume_participation": "0.10"},
        "risk": {"min_net_reward_risk": "0.5"},
    }


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"), parse_float=str)
    if not isinstance(value, dict):
        raise ValueError("JSON object required")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    dataset = commands.add_parser("dataset")
    dataset.add_argument("--input", type=Path, required=True)
    dataset.add_argument("--output", type=Path, required=True)
    dataset.add_argument("--config", type=Path)
    training = commands.add_parser("train")
    training.add_argument("--dataset", type=Path, required=True)
    training.add_argument("--output", type=Path, required=True)
    evaluation = commands.add_parser("evaluate")
    evaluation.add_argument("--input", type=Path, required=True)
    evaluation.add_argument("--dataset", type=Path, required=True)
    evaluation.add_argument("--model", type=Path, required=True)
    evaluation.add_argument("--responses", type=Path, required=True)
    evaluation.add_argument("--analyst-model-id", required=True)
    evaluation.add_argument("--output", type=Path, required=True)
    demo = commands.add_parser("demo")
    demo.add_argument("--output", type=Path, default=Path("artifacts/ai-demo"))
    args = parser.parse_args()
    if args.command == "dataset":
        config = LearningConfig.model_validate(read_json(args.config) if args.config else {})
        bundle = asyncio.run(build_dataset(read_json(args.input), config))
        write_json(args.output, bundle)
        print(
            json.dumps({"dataset_id": bundle["dataset_id"], "counts": bundle["manifest"]["counts"]})
        )
    elif args.command == "train":
        bundle = read_json(args.dataset)
        config = LearningConfig.model_validate(bundle["manifest"]["learning_config"])
        model, report = training_report(bundle, config)
        directory = model.save(args.output / "models")
        write_json(args.output / "training-report.json", report)
        print(
            json.dumps(
                {
                    "model_path": str(directory),
                    "model_version": model.model_version,
                    "deployment_enabled": False,
                }
            )
        )
    elif args.command == "evaluate":
        bundle = read_json(args.dataset)
        config = LearningConfig.model_validate(bundle["manifest"]["learning_config"])
        result = asyncio.run(
            evaluate(
                read_json(args.input),
                bundle,
                FrozenModel.load(args.model),
                config,
                args.output,
                ResponseStore(args.responses),
                args.analyst_model_id,
            )
        )
        print(json.dumps(result["promotion"]))
    else:
        raw = synthetic_input()
        config = LearningConfig(
            label_bars=2,
            embargo_seconds=0,
            minimum_train=10,
            minimum_validation=5,
            minimum_test=5,
            min_data_in_leaf=3,
            rounds=20,
        )
        bundle = asyncio.run(build_dataset(raw, config))
        write_json(args.output / "synthetic-input.json", raw)
        write_json(args.output / "dataset.json", bundle)
        model, report = training_report(bundle, config)
        model.save(args.output / "models")
        write_json(args.output / "training-report.json", report)
        responses = ResponseStore(args.output / "responses")
        model_id = "SYNTHETIC_ANALYST_FIXTURE_V1"
        asyncio.run(seed_demo_responses(raw, bundle, responses, model_id))
        result = asyncio.run(
            evaluate(raw, bundle, model, config, args.output, responses, model_id, synthetic=True)
        )
        print(
            json.dumps(
                {
                    "dataset_samples": len(bundle["samples"]),
                    "model_version": model.model_version,
                    "variants": {
                        name: value["metrics"] for name, value in result["variants"].items()
                    },
                    "promotion": result["promotion"],
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
