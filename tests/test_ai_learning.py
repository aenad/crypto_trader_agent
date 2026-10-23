from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from quantpilot.ai.domain import FeatureVector, LearningConfig, Sample
from quantpilot.ai.learning import (
    FrozenModel,
    calibrated,
    overlap_weights,
    predictive_metrics,
    train,
)
from quantpilot.ai.splits import chronological_split, walk_forward
from quantpilot.config import stable_id

D = Decimal
NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def feature(value=1):
    return FeatureVector(
        entry_ema_gap=D(value) / 100,
        trend_ema_gap=D(value) / 100,
        rsi=D(50 + value),
        atr_fraction=D(".01"),
        adx=D(25),
        relative_volume=D(2),
        breakout_fraction=D(".001"),
        trend_adx=D(30),
        trend_atr_fraction=D(".01"),
        spread=D(".001"),
        depth_imbalance=D(0),
        hour_utc=D(12),
    )


def samples(count=120, markets=("BTC/TMN",), horizon=2):
    return tuple(
        Sample(
            sample_id=f"sample-{i}-{pair}",
            symbol=pair,
            as_of=NOW + timedelta(minutes=5 * i),
            label_end=NOW + timedelta(minutes=5 * (i + horizon)),
            snapshot_id=stable_id({"time": i, "pair": pair}),
            features=feature(1 if i % 2 else -1),
            positive=i % 2,
            net_return=D(".01") if i % 2 else D("-.01"),
            net_pnl_tmn=D(100) if i % 2 else D(-100),
        )
        for i in range(count)
        for pair in markets
    )


def configuration():
    return LearningConfig(
        embargo_seconds=300,
        minimum_train=10,
        minimum_validation=5,
        minimum_test=5,
        rounds=15,
        min_data_in_leaf=3,
    )


def test_purge_and_embargo_apply_globally_across_markets():
    rows = samples(markets=("BTC/TMN", "ETH/TMN"), horizon=8)
    split = chronological_split(rows, 900)
    assert split.purged > 0
    assert max(r.label_end for r in split.train) < split.validation_start - timedelta(seconds=900)
    assert max(r.label_end for r in split.validation) < split.test_start - timedelta(seconds=900)
    for at in {r.as_of for r in rows}:
        memberships = [
            {r.symbol for r in group if r.as_of == at}
            for group in (split.train, split.validation, split.test)
        ]
        assert sum(bool(s) for s in memberships) <= 1


def test_walk_forward_never_reads_final_holdout_labels():
    rows = samples(180)
    final = chronological_split(rows, 300)
    folds = walk_forward(rows, final.test_start, 300)
    assert len(folds) == 2
    for fold in folds:
        assert max(r.label_end for r in fold.train) < fold.validation_start
        assert max(r.label_end for r in fold.validation) < fold.test_start
        assert max(r.label_end for r in fold.test) < final.test_start - timedelta(seconds=300)
        assert not {r.sample_id for r in fold.train + fold.validation + fold.test} & {
            r.sample_id for r in final.test
        }


def test_splits_reject_unordered_duplicates_and_short_data():
    rows = samples()
    with pytest.raises(ValueError):
        chronological_split(tuple(reversed(rows)))
    with pytest.raises(ValueError):
        chronological_split((rows[0], rows[0]) + rows[1:])
    with pytest.raises(ValueError):
        chronological_split(rows[:5])


def test_calibration_and_metrics_hand_calculation():
    result = predictive_metrics([0, 1], [0.5, 0.5])
    assert result["brier"] == 0.25
    assert result["roc_auc"] == 0.5
    assert result["expected_calibration_error"] == 0
    assert calibrated(0.5, 2) == 0.5
    assert abs(calibrated(0.8, 1) - 0.8) < 1e-12
    assert predictive_metrics([1, 1], [0.8, 0.9])["roc_auc"] is None
    with pytest.raises(ValueError):
        predictive_metrics([0], [float("nan")])


def test_overlap_weights_reduce_concurrent_influence():
    rows = samples(20, horizon=6)
    assert all(0 < w < 1 for w in overlap_weights(rows))


def test_real_lightgbm_freeze_reload_determinism_and_label_isolation(tmp_path):
    pytest.importorskip("lightgbm")
    split = chronological_split(samples(), 300)
    config = configuration()
    model = train(split, config, "fixture")
    repeated = train(split, config, "fixture")
    assert model.model_version == repeated.model_version
    assert model.text == repeated.text
    # Alter all final targets/features: training/calibration model must be identical.
    altered = tuple(
        r.model_copy(
            update={
                "features": feature(90),
                "positive": 1 - r.positive,
                "net_pnl_tmn": -r.net_pnl_tmn,
                "net_return": -r.net_return,
            }
        )
        for r in split.test
    )
    untouched = train(replace(split, test=altered), config, "fixture")
    assert model.text == untouched.text
    assert model.metadata["temperature"] == untouched.metadata["temperature"]
    directory = model.save(tmp_path)
    restored = FrozenModel.load(directory)
    row = split.test[0]
    assert model.predict(row.features, row.as_of) == restored.predict(row.features, row.as_of)
    assert restored.metadata["live_enabled"] is False
    with pytest.raises(ValueError, match="precedes"):
        model.predict(row.features, split.train[-1].as_of)
    path = directory / "model.txt"
    path.write_text(path.read_text() + "tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="checksum"):
        FrozenModel.load(directory)


def test_training_fails_for_single_class_and_inadequate_samples():
    pytest.importorskip("lightgbm")
    split = chronological_split(samples(), 300)
    with pytest.raises(ValueError, match="Insufficient"):
        train(split, LearningConfig(minimum_train=1000), "fixture")
    only_positive = tuple(
        r.model_copy(update={"positive": 1, "net_pnl_tmn": D(100), "net_return": D(".01")})
        for r in split.train
    )
    with pytest.raises(ValueError, match="Both classes"):
        train(replace(split, train=only_positive), configuration(), "fixture")
