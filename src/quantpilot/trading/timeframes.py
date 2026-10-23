"""Past-only aggregation from verified closed base candles; never requests APIs."""

from datetime import datetime, timedelta, timezone
from decimal import Context, Decimal, localcontext

from quantpilot.config import stable_id
from quantpilot.models import Candle, MarketSnapshot

from .config import ResearchParameters


def resample(rows: tuple[Candle, ...], seconds: int, as_of: datetime) -> tuple[Candle, ...]:
    if not rows or as_of.tzinfo is None or seconds <= 0:
        raise ValueError("Valid closed source history and as-of required")
    base = int((rows[0].close_time - rows[0].open_time).total_seconds())
    if base <= 0 or seconds % base:
        raise ValueError("Target must be a multiple of source interval")
    groups: dict[int, list[Candle]] = {}
    previous = None
    for row in rows:
        if not row.closed or row.event_time > as_of or row.received_at > as_of:
            raise ValueError("Unavailable/incomplete source candle")
        if row.symbol != rows[0].symbol or (row.close_time - row.open_time).total_seconds() != base:
            raise ValueError("Mixed source series")
        if previous is not None and row.open_time != previous:
            raise ValueError("Source gap/duplicate/order error")
        previous = row.close_time
        key = int(row.open_time.timestamp()) // seconds * seconds
        groups.setdefault(key, []).append(row)
    output = []
    with localcontext(Context(prec=34)) as ctx:
        ctx.prec = 34
        for bucket, bars in groups.items():
            start = datetime.fromtimestamp(bucket, timezone.utc)
            stop = start + timedelta(seconds=seconds)
            if stop > as_of:
                continue  # Completed source bars can still belong to an open target bar.
            if (
                len(bars) != seconds // base
                or bars[0].open_time != start
                or bars[-1].close_time != stop
            ):
                raise ValueError("Incomplete target candle")
            output.append(
                Candle(
                    event_id=stable_id({"target": seconds, "inputs": [b.event_id for b in bars]}),
                    symbol=bars[0].symbol,
                    event_time=max(b.event_time for b in bars),
                    received_at=max(b.received_at for b in bars),
                    source="resampled:" + bars[0].source,
                    open_time=start,
                    close_time=stop,
                    open=bars[0].open,
                    close=bars[-1].close,
                    high=max(b.high for b in bars),
                    low=min(b.low for b in bars),
                    volume=sum((b.volume for b in bars), Decimal(0)),
                    closed=True,
                )
            )
    return tuple(output)


def research_snapshot(base: MarketSnapshot, parameters: ResearchParameters) -> MarketSnapshot:
    return MarketSnapshot(
        symbol=base.symbol,
        as_of=base.as_of,
        source=base.source,
        candles=resample(base.candles, parameters.entry_seconds, base.as_of),
        trend_candles=resample(base.candles, parameters.trend_seconds, base.as_of),
        market=base.market,
        liquidity=base.liquidity,
    )
