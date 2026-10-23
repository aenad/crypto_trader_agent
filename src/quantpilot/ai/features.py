from decimal import Context, Decimal, localcontext

from quantpilot.config import stable_id
from quantpilot.models import MarketSnapshot, Signal
from quantpilot.trading.config import ResearchParameters
from quantpilot.trading.features import FeatureEngine, liquidity_features

from .domain import AnalystContext, ContextBar, FeatureVector


def extract_features(
    snapshot: MarketSnapshot, signal: Signal, parameters: ResearchParameters
) -> FeatureVector:
    if signal.as_of != snapshot.as_of or signal.snapshot_id != stable_id(
        snapshot.model_dump(mode="json")
    ):
        raise ValueError("AI signal/snapshot mismatch")
    if snapshot.liquidity is None:
        raise ValueError("Missing AI liquidity context")
    with localcontext(Context(prec=34)):
        engine = FeatureEngine(parameters)
        entry, trend = engine.compute(snapshot.candles), engine.compute(snapshot.trend_candles)
        depth = liquidity_features(snapshot.liquidity, parameters.depth_band)
        total = depth.ask_depth_quote + depth.bid_depth_quote
        return FeatureVector(
            entry_ema_gap=(entry.ema_fast - entry.ema_slow) / entry.close,
            trend_ema_gap=(trend.ema_fast - trend.ema_slow) / trend.close,
            rsi=entry.rsi,
            atr_fraction=entry.atr / entry.close,
            adx=entry.adx,
            relative_volume=entry.relative_volume,
            breakout_fraction=entry.close / entry.prior_high - 1,
            trend_adx=trend.adx,
            trend_atr_fraction=trend.atr / trend.close,
            spread=depth.spread,
            depth_imbalance=(depth.bid_depth_quote - depth.ask_depth_quote) / total
            if total
            else Decimal(0),
            hour_utc=Decimal(str(snapshot.as_of.timestamp() % 86400)) / Decimal(3600),
        )


def assemble_context(
    snapshot: MarketSnapshot, signal: Signal, parameters: ResearchParameters
) -> AnalystContext:
    # Explicit numeric allowlist: no source strings, account balances, notes,
    # arbitrary event IDs, news, environment or credentials enter this boundary.
    return AnalystContext(
        symbol=snapshot.symbol,
        as_of=snapshot.as_of,
        snapshot_id=stable_id(snapshot.model_dump(mode="json")),
        features=extract_features(snapshot, signal, parameters),
        bars=tuple(
            ContextBar(
                close_time=c.close_time, close=c.close, high=c.high, low=c.low, volume=c.volume
            )
            for c in snapshot.candles[-8:]
        ),
    )
