"""Global time boundaries across markets; purge the full forward label interval."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from .domain import Sample


@dataclass(frozen=True)
class Split:
    train: tuple[Sample, ...]
    validation: tuple[Sample, ...]
    test: tuple[Sample, ...]
    validation_start: datetime
    test_start: datetime
    purged: int


def validate_samples(rows: tuple[Sample, ...]) -> None:
    if not rows or tuple((r.as_of, r.symbol) for r in rows) != tuple(
        sorted((r.as_of, r.symbol) for r in rows)
    ):
        raise ValueError("Samples must be nonempty and chronological by time/symbol")
    if len({r.sample_id for r in rows}) != len(rows) or len(
        {(r.as_of, r.symbol) for r in rows}
    ) != len(rows):
        raise ValueError("Duplicate sample identities")


def at_boundaries(
    rows: tuple[Sample, ...],
    validation_start: datetime,
    test_start: datetime,
    end: datetime | None,
    embargo_seconds: int,
) -> Split:
    validate_samples(rows)
    if embargo_seconds < 0 or validation_start >= test_start:
        raise ValueError("Invalid chronological boundaries")
    gap = timedelta(seconds=embargo_seconds)
    train = tuple(
        r for r in rows if r.as_of < validation_start and r.label_end < validation_start - gap
    )
    validation = tuple(
        r
        for r in rows
        if validation_start <= r.as_of < test_start and r.label_end < test_start - gap
    )
    test = tuple(
        r for r in rows if r.as_of >= test_start and (end is None or r.label_end < end - gap)
    )
    considered = sum(end is None or r.as_of < end for r in rows)
    return Split(
        train,
        validation,
        test,
        validation_start,
        test_start,
        considered - len(train) - len(validation) - len(test),
    )


def chronological_split(rows: tuple[Sample, ...], embargo_seconds: int = 900) -> Split:
    validate_samples(rows)
    times = sorted({r.as_of for r in rows})
    if len(times) < 10:
        raise ValueError("Too few distinct signal times")
    return at_boundaries(
        rows, times[len(times) * 6 // 10], times[len(times) * 8 // 10], None, embargo_seconds
    )


def walk_forward(
    rows: tuple[Sample, ...], holdout_start: datetime, embargo_seconds: int = 900
) -> tuple[Split, ...]:
    development = tuple(
        r for r in rows if r.label_end < holdout_start - timedelta(seconds=embargo_seconds)
    )
    validate_samples(development)
    times = sorted({r.as_of for r in development})
    if len(times) < 20:
        raise ValueError("Insufficient development data for walk-forward")
    # Expanding training; each fold has separate calibration and forward test.
    # No final-holdout labels participate in development folds.
    result = []
    for percent in (40, 60):
        a, b, c = (len(times) * x // 100 for x in (percent, percent + 15, percent + 30))
        result.append(at_boundaries(development, times[a], times[b], times[c], embargo_seconds))
    return tuple(result)
