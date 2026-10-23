"""Deterministic CPU LightGBM research training and checksum-verified text artifacts."""

import hashlib
import json
import math
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from importlib.metadata import version
from pathlib import Path
from typing import Any

from quantpilot.config import stable_id

from .domain import FeatureVector, LearningConfig, Prediction, Sample
from .splits import Split


def implementation_id() -> str:
    root = Path(__file__).resolve().parent.parent
    files = [root / "models.py", root / "config.py", root / "spot.py"]
    for package in ("ai", "trading", "backtest"):
        files.extend(sorted((root / package).glob("*.py")))
    return stable_id(
        {path.relative_to(root).as_posix(): path.read_text(encoding="utf-8") for path in files}
    )


def calibrated(probability: float, temperature: float) -> float:
    p = min(1 - 1e-12, max(1e-12, probability))
    return 1 / (1 + math.exp(-math.log(p / (1 - p)) / temperature))


def predictive_metrics(labels: Sequence[int], predictions: Sequence[float]) -> dict[str, Any]:
    if not labels or len(labels) != len(predictions):
        raise ValueError("Nonempty paired predictions required")
    if any(y not in (0, 1) for y in labels) or any(
        not math.isfinite(p) or not 0 <= p <= 1 for p in predictions
    ):
        raise ValueError("Invalid prediction/target")
    n = len(labels)
    brier = sum((p - y) ** 2 for y, p in zip(labels, predictions, strict=True)) / n
    logloss = (
        -sum(
            y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12))
            for y, p in zip(labels, predictions, strict=True)
        )
        / n
    )
    positive = [p for y, p in zip(labels, predictions, strict=True) if y]
    negative = [p for y, p in zip(labels, predictions, strict=True) if not y]
    auc = (
        sum((a > b) + 0.5 * (a == b) for a in positive for b in negative)
        / (len(positive) * len(negative))
        if positive and negative
        else None
    )
    bins = []
    for index in range(10):
        group = [
            (y, p) for y, p in zip(labels, predictions, strict=True) if min(int(p * 10), 9) == index
        ]
        if group:
            bins.append(
                {
                    "bin": index,
                    "count": len(group),
                    "mean_probability": sum(p for _, p in group) / len(group),
                    "positive_rate": sum(y for y, _ in group) / len(group),
                }
            )
    tp = sum(y == 1 and p >= 0.5 for y, p in zip(labels, predictions, strict=True))
    fp = sum(y == 0 and p >= 0.5 for y, p in zip(labels, predictions, strict=True))
    return {
        "count": n,
        "positive_rate": sum(labels) / n,
        "brier": brier,
        "log_loss": logloss,
        "roc_auc": auc,
        "accuracy": sum((p >= 0.5) == bool(y) for y, p in zip(labels, predictions, strict=True))
        / n,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / len(positive) if positive else None,
        "expected_calibration_error": sum(
            b["count"] * abs(b["positive_rate"] - b["mean_probability"]) for b in bins
        )
        / n,
        "reliability_bins": bins,
    }


def overlap_weights(rows: tuple[Sample, ...]) -> list[float]:
    # Penalize concurrent label intervals across ALL markets. This complements
    # boundary purging; it does not make overlapping observations independent.
    return [
        1 / sum(other.as_of <= row.label_end and other.label_end >= row.as_of for other in rows)
        for row in rows
    ]


class FrozenModel:
    def __init__(self, text: str, metadata: dict[str, Any]):
        import lightgbm as lgb

        self.metadata = metadata
        if metadata["lightgbm_version"] != version("lightgbm"):
            raise ValueError("LightGBM version mismatch; reproduce the artifact environment")
        if metadata["numpy_version"] != version("numpy"):
            raise ValueError("NumPy version mismatch")
        if metadata.get("implementation_id") != implementation_id():
            raise ValueError("Artifact implementation mismatch; use the frozen source revision")
        if metadata["features"] != list(FeatureVector.names()):
            raise ValueError("Feature schema mismatch")
        self._booster = lgb.Booster(model_str=text)
        if self._booster.feature_name() != list(FeatureVector.names()):
            raise ValueError("Model feature mismatch")
        self.text = text

    @property
    def model_version(self) -> str:
        return stable_id(
            {
                "metadata": self.metadata,
                "model_sha256": hashlib.sha256(self.text.encode()).hexdigest(),
            }
        )

    def probabilities(self, features: list[FeatureVector]) -> tuple[list[float], list[float]]:
        import numpy as np

        raw = [
            float(p)
            for p in self._booster.predict(
                np.asarray([f.numbers() for f in features]), num_threads=1
            )
        ]
        return raw, [calibrated(p, float(self.metadata["temperature"])) for p in raw]

    def predict(self, features: FeatureVector, as_of: datetime) -> Prediction:
        if as_of <= datetime.fromisoformat(self.metadata["trained_through"]):
            raise ValueError(
                "Inference precedes availability of frozen training/calibration labels"
            )
        raw, probabilities = self.probabilities([features])
        p = probabilities[0]
        return Prediction(
            model_version=self.model_version,
            as_of=as_of,
            features=features,
            raw_probability=Decimal(str(raw[0])),
            probability=Decimal(str(p)),
            quality="HIGH"
            if p >= float(self.metadata["config"]["probability_threshold"])
            else "LOW",
        )

    def save(self, root: Path) -> Path:
        directory = root / self.model_version
        directory.mkdir(parents=True, exist_ok=True)
        artifact = {
            "model_version": self.model_version,
            "metadata": self.metadata,
            "model_sha256": hashlib.sha256(self.text.encode()).hexdigest(),
        }
        encoded = json.dumps(artifact, sort_keys=True, indent=2) + "\n"
        for name, content in (("model.txt", self.text), ("artifact.json", encoded)):
            path = directory / name
            if path.exists():
                if path.read_text(encoding="utf-8") != content:
                    raise ValueError("Frozen artifact conflict")
            else:
                with path.open("x", encoding="utf-8", newline="\n") as output:
                    output.write(content)
        return directory

    @classmethod
    def load(cls, directory: Path) -> "FrozenModel":
        artifact = json.loads((directory / "artifact.json").read_text(encoding="utf-8"))
        text = (directory / "model.txt").read_text(encoding="utf-8")
        if hashlib.sha256(text.encode()).hexdigest() != artifact["model_sha256"]:
            raise ValueError("Model checksum mismatch")
        model = cls(text, artifact["metadata"])
        if model.model_version != artifact["model_version"]:
            raise ValueError("Artifact manifest mismatch")
        return model


def train(
    split: Split, config: LearningConfig, dataset_id: str, research_id: str | None = None
) -> FrozenModel:
    import lightgbm as lgb
    import numpy as np

    if len(split.train) < config.minimum_train or len(split.validation) < config.minimum_validation:
        raise ValueError("Insufficient purged training/calibration samples")
    if {r.positive for r in split.train} != {0, 1} or {r.positive for r in split.validation} != {
        0,
        1,
    }:
        raise ValueError("Both classes required in training and calibration")
    if max(r.label_end for r in split.train) >= split.validation_start:
        raise ValueError("Training label crosses calibration boundary")
    if max(r.label_end for r in split.validation) >= split.test_start:
        raise ValueError("Calibration label crosses evaluation boundary")
    matrix = np.asarray([r.features.numbers() for r in split.train], dtype=np.float64)
    data = lgb.Dataset(
        matrix,
        label=[r.positive for r in split.train],
        weight=overlap_weights(split.train),
        feature_name=list(FeatureVector.names()),
    )
    parameters = {
        "objective": "binary",
        "metric": "binary_logloss",
        "verbosity": -1,
        "num_threads": 1,
        "deterministic": True,
        "force_col_wise": True,
        "seed": config.seed,
        "data_random_seed": config.seed,
        "feature_fraction_seed": config.seed,
        "bagging_seed": config.seed,
        "num_leaves": config.num_leaves,
        "min_data_in_leaf": config.min_data_in_leaf,
        "learning_rate": 0.05,
        "max_bin": 63,
    }
    booster = lgb.train(parameters, data, num_boost_round=config.rounds)
    raw = [
        float(p)
        for p in booster.predict(
            np.asarray([r.features.numbers() for r in split.validation]), num_threads=1
        )
    ]
    targets = [r.positive for r in split.validation]
    temperature = min(
        (0.5, 0.75, 1.0, 1.5, 2.0, 3.0),
        key=lambda t: predictive_metrics(targets, [calibrated(p, t) for p in raw])["log_loss"],
    )
    metadata = {
        "schema": "lightgbm-quality-v1",
        "features": list(FeatureVector.names()),
        "feature_schema": "phase5-features-v1",
        "config": config.model_dump(mode="json"),
        "lightgbm_version": version("lightgbm"),
        "numpy_version": version("numpy"),
        "implementation_id": implementation_id(),
        "dataset_id": dataset_id,
        "research_id": research_id,
        "training_ids": [r.sample_id for r in split.train],
        "calibration_ids": [r.sample_id for r in split.validation],
        "temperature": temperature,
        "trained_through": max(r.label_end for r in split.train + split.validation).isoformat(),
        "status": "RESEARCH_FROZEN",
        "live_enabled": False,
        "parameters": parameters,
        "training_positive_rate": sum(target.positive for target in split.train) / len(split.train),
        "calibration_method": "Validation temperature grid; fitted validation diagnostics",
    }
    return FrozenModel(booster.model_to_string(), metadata)
