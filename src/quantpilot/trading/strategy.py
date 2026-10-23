from collections.abc import Collection
from decimal import Context, Decimal, localcontext
from enum import Enum
from typing import Any

from quantpilot.config import stable_id
from quantpilot.models import Candle, MarketSnapshot, PortfolioState, Signal

from .config import ResearchParameters
from .features import FeatureEngine, Features, liquidity_features


class Regime(str, Enum):
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    RANGE = "RANGE"
    VOLATILE = "VOLATILE"
    ILLIQUID = "ILLIQUID"


class RegimeDetector:
    def __init__(self, parameters: ResearchParameters):
        self.parameters = parameters

    def classify(self, trend: Features, spread: object) -> Regime:
        from decimal import Decimal

        with localcontext(Context(prec=34)) as ctx:
            ctx.prec = 34
            if not isinstance(spread, Decimal) or spread > self.parameters.max_spread:
                return Regime.ILLIQUID
            if trend.atr / trend.close > self.parameters.max_atr_fraction:
                return Regime.VOLATILE
            if trend.adx < self.parameters.min_adx:
                return Regime.RANGE
            if trend.ema_fast > trend.ema_slow:
                return Regime.UPTREND
            if trend.ema_fast < trend.ema_slow:
                return Regime.DOWNTREND
            return Regime.RANGE


class MarketEligibilityFilter:
    def __init__(self, approved: Collection[str], excluded: Collection[str] = ()):
        self.approved = frozenset(approved)
        self.excluded = frozenset(excluded)

    def reasons(self, snapshot: MarketSnapshot) -> tuple[str, ...]:
        market = snapshot.market
        reasons = []
        if snapshot.symbol not in self.approved or snapshot.symbol in self.excluded:
            reasons.append("MARKET_NOT_APPROVED")
        if market is None:
            reasons.append("MISSING_MARKET_CONSTRAINTS")
        elif (
            market.symbol != snapshot.symbol
            or not snapshot.symbol.endswith("/" + market.quote)
            or not market.spot_enabled
            or not market.account_enabled
        ):
            reasons.append("MARKET_OR_ACCOUNT_INELIGIBLE")
        return tuple(reasons)


def validate_series(
    rows: tuple[Candle, ...], seconds: int, snapshot: MarketSnapshot, lag: int
) -> None:
    if not rows:
        raise ValueError("MISSING_CANDLES")
    for row in rows:
        if (row.close_time - row.open_time).total_seconds() != seconds:
            raise ValueError("TIMEFRAME_MISMATCH")
        if int(row.open_time.timestamp()) % seconds:
            raise ValueError("CANDLE_ALIGNMENT")
    for left, right in zip(rows, rows[1:]):
        if left.close_time != right.open_time:
            raise ValueError("CANDLE_GAP")
    boundary = int(snapshot.as_of.timestamp()) // seconds * seconds
    if boundary - int(rows[-1].close_time.timestamp()) > lag:
        raise ValueError("STALE_CANDLES")


class MomentumBreakout:
    def __init__(self, parameters: ResearchParameters, eligibility: MarketEligibilityFilter):
        self.parameters, self.eligibility = parameters, eligibility

    def evaluate(self, snapshot: MarketSnapshot, portfolio: PortfolioState) -> Signal:
        with localcontext(Context(prec=34)) as ctx:
            ctx.prec = 34
            return self._evaluate(snapshot, portfolio)

    def _evaluate(self, snapshot: MarketSnapshot, portfolio: PortfolioState) -> Signal:
        p = self.parameters
        base: dict[str, Any] = dict(
            symbol=snapshot.symbol,
            strategy_version=p.version,
            as_of=snapshot.as_of,
            snapshot_id=stable_id(snapshot.model_dump(mode="json")),
            parameters_id=p.parameters_id,
            parameters_json=p.model_dump_json(),
        )
        eligibility_reasons = self.eligibility.reasons(snapshot)
        if eligibility_reasons:
            return Signal(**base, action="HOLD", reasons=eligibility_reasons)
        base_asset = snapshot.symbol.split("/")[0]
        owned = sum(
            (b.free + b.reserved for b in portfolio.balances if b.currency == base_asset),
            Decimal(0),
        )
        if owned == 0 and any(
            pos.symbol == snapshot.symbol and pos.state == "OPEN" for pos in portfolio.positions
        ):
            return Signal(**base, action="HOLD", reasons=("NO_OWNED_SPOT_ASSET",))
        try:
            validate_series(snapshot.candles, p.entry_seconds, snapshot, p.max_candle_lag_seconds)
            position = next(
                (
                    pos
                    for pos in portfolio.positions
                    if pos.symbol == snapshot.symbol and pos.state == "OPEN"
                ),
                None,
            )
            if position:
                from .lifecycle import exit_signal

                reason, price = exit_signal(position, snapshot.candles[-1], None, snapshot.as_of, p)
                if reason:
                    return Signal(**base, action="SELL", reasons=(reason,), exit_price=price)
            validate_series(
                snapshot.trend_candles, p.trend_seconds, snapshot, p.max_candle_lag_seconds
            )
            engine = FeatureEngine(p)
            entry = engine.compute(snapshot.candles)
            trend = engine.compute(snapshot.trend_candles)
        except ValueError as exc:
            return Signal(**base, action="HOLD", reasons=(str(exc),))
        evidence = entry.evidence("entry") + trend.evidence("trend")
        position = next(
            (
                pos
                for pos in portfolio.positions
                if pos.symbol == snapshot.symbol and pos.state == "OPEN"
            ),
            None,
        )
        if position:
            from .lifecycle import exit_signal

            reason, price = exit_signal(
                position, snapshot.candles[-1], entry.ema_fast, snapshot.as_of, p
            )
            return Signal(
                **base,
                action="SELL" if reason else "HOLD",
                reasons=(reason or "KEEP_POSITION",),
                exit_price=price,
                evidence=evidence,
            )
        if snapshot.liquidity is None:
            return Signal(**base, action="HOLD", reasons=("MISSING_LIQUIDITY",), evidence=evidence)
        liquid = liquidity_features(snapshot.liquidity, p.depth_band)
        regime = RegimeDetector(p).classify(trend, liquid.spread)
        evidence += (
            ("regime", regime.value),
            ("spread", str(liquid.spread)),
            ("ask_depth_quote", str(liquid.ask_depth_quote)),
            ("bid_depth_quote", str(liquid.bid_depth_quote)),
        )
        reasons = []
        if regime != Regime.UPTREND:
            reasons.append("REGIME_NOT_UPTREND")
        if entry.close <= entry.prior_high:
            reasons.append("NO_BREAKOUT")
        if not p.rsi_min <= entry.rsi <= p.rsi_max:
            reasons.append("RSI_OUTSIDE_ENTRY_RANGE")
        if entry.relative_volume < p.min_relative_volume:
            reasons.append("LOW_RELATIVE_VOLUME")
        if entry.atr <= 0 or entry.close - p.stop_atr * entry.atr <= 0:
            reasons.append("INVALID_ATR_STOP")
        if reasons:
            return Signal(**base, action="HOLD", reasons=tuple(reasons), evidence=evidence)
        return Signal(
            **base,
            action="BUY",
            reasons=("MOMENTUM_BREAKOUT_CONFIRMED",),
            entry_price=entry.close,
            atr=entry.atr,
            stop_loss=entry.close - p.stop_atr * entry.atr,
            take_profit=entry.close + p.target_atr * entry.atr,
            evidence=evidence,
        )
