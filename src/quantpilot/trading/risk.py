"""Deterministic sizing on explicit snapshots. Never submits or reserves orders."""

from collections.abc import Collection, Mapping
from decimal import ROUND_DOWN, ROUND_UP, Context, Decimal, localcontext
from zoneinfo import ZoneInfo

from quantpilot.config import stable_id
from quantpilot.models import MarketSnapshot, PortfolioState, QuoteConversion, RiskDecision, Signal
from quantpilot.spot import validate_spot_order

from .config import ResearchParameters, RiskParameters
from .features import FeatureEngine, liquidity_features
from .strategy import MarketEligibilityFilter, MomentumBreakout, validate_series

D = Decimal


def rounded(value: Decimal, step: Decimal, up: bool = False) -> Decimal:
    return (value / step).to_integral_value(rounding=ROUND_UP if up else ROUND_DOWN) * step


class DeterministicRiskEngine:
    """RiskManager port; bind the same immutable snapshots used by Strategy."""

    def __init__(
        self,
        parameters: RiskParameters,
        research: ResearchParameters,
        eligibility: MarketEligibilityFilter,
        snapshots: Mapping[str, MarketSnapshot],
        approved_accounts: Collection[str],
    ):
        self.parameters, self.research = parameters, research
        self.eligibility, self.snapshots = eligibility, dict(snapshots)
        self.approved_accounts = frozenset(approved_accounts)

    def check(self, signal: Signal, portfolio: PortfolioState) -> RiskDecision:
        with localcontext(Context(prec=34)) as ctx:
            ctx.prec = 34
            return self._check(signal, portfolio)

    def _check(self, signal: Signal, portfolio: PortfolioState) -> RiskDecision:
        p = self.parameters
        halt = False

        def reject(*reasons: str) -> RiskDecision:
            return RiskDecision(
                allowed=False,
                reasons=tuple(reasons),
                parameters_id=p.parameters_id,
                parameters_json=p.model_dump_json(),
                halt_new_entries=halt,
            )

        now = signal.as_of
        if portfolio.account_id not in self.approved_accounts:
            return reject("ACCOUNT_NOT_APPROVED")
        if not 0 <= (now - portfolio.as_of).total_seconds() <= p.max_snapshot_age_seconds:
            return reject("STALE_ACCOUNT")
        snapshot = self.snapshots.get(signal.symbol)
        if snapshot is None or snapshot.as_of != now:
            return reject("MISSING_OR_STALE_MARKET_CONTEXT")
        if signal.snapshot_id != stable_id(snapshot.model_dump(mode="json")):
            return reject("SIGNAL_SNAPSHOT_MISMATCH")
        if (
            signal.parameters_id != self.research.parameters_id
            or signal.strategy_version != self.research.version
        ):
            return reject("STRATEGY_PARAMETER_MISMATCH")
        expected = MomentumBreakout(self.research, self.eligibility).evaluate(snapshot, portfolio)
        if signal != expected:
            return reject("STRATEGY_SIGNAL_MISMATCH")
        eligibility = self.eligibility.reasons(snapshot)
        if eligibility:
            return reject(*eligibility)
        market = snapshot.market
        book = snapshot.liquidity
        assert market is not None
        if (
            book is None
            or not 0 <= (now - book.as_of).total_seconds() <= p.max_snapshot_age_seconds
        ):
            return reject("MISSING_OR_STALE_LIQUIDITY")
        liquid = liquidity_features(book, p.slippage_fraction)
        if liquid.spread > p.max_spread:
            return reject("EXCESSIVE_SPREAD")
        free = {balance.currency: balance.free for balance in portfolio.balances}
        position = next(
            (
                pos
                for pos in portfolio.positions
                if pos.symbol == signal.symbol and pos.state == "OPEN"
            ),
            None,
        )
        # Exits reduce exposure and must not be blocked by entry-loss circuit breakers.
        if signal.action == "SELL":
            if position is None:
                return reject("NO_POSITION_TO_SELL")
            price = rounded(liquid.bid * (1 - p.slippage_fraction), market.price_tick)
            qty = rounded(
                min(position.quantity, free.get(signal.symbol.split("/")[0], D(0))),
                market.quantity_step,
            )
            if qty < market.minimum_quantity or qty * price < market.minimum_notional:
                return reject("EXIT_BELOW_MINIMUM_OR_RESERVED")
            depth = liquid.bid_depth_quote * p.max_depth_participation
            qty = min(qty, rounded(depth / price, market.quantity_step))
            if qty < market.minimum_quantity or qty * price < market.minimum_notional:
                return reject("INSUFFICIENT_EXIT_LIQUIDITY")
            try:
                validate_spot_order(
                    signal.symbol,
                    signal.action,
                    qty,
                    price,
                    market,
                    (signal.symbol,),
                    free,
                    market.taker_fee_rate,
                )
            except ValueError as exc:
                return reject(str(exc))
            return RiskDecision(
                allowed=True,
                reasons=("REDUCE_ONLY_EXIT",),
                parameters_id=p.parameters_id,
                parameters_json=p.model_dump_json(),
                quantity=qty,
                reference_price=price,
            )
        equity = portfolio.equity_tmn
        daily = portfolio.daily_open_equity_tmn
        peak = portfolio.peak_equity_tmn
        if equity is None or daily is None or peak is None:
            return reject("MISSING_EQUITY_BASELINES")
        if portfolio.trading_day != now.astimezone(ZoneInfo("Asia/Tehran")).date():
            return reject("DAILY_BASELINE_DATE_MISMATCH")
        breakers = []
        if portfolio.risk_halted:
            breakers.append("RISK_HALT_LATCHED")
        if (daily - equity) / daily >= p.daily_loss_fraction:
            breakers.append("DAILY_LOSS_LIMIT")
        if (peak - equity) / peak >= p.max_drawdown_fraction:
            breakers.append("MAX_DRAWDOWN")
        if breakers:
            halt = True
            return reject(*breakers)
        if signal.action != "BUY":
            return reject("NO_ENTRY_SIGNAL")
        opened = [pos for pos in portfolio.positions if pos.state == "OPEN"]
        asset = signal.symbol.split("/")[0]
        if (
            position
            or any(pos.symbol.split("/")[0] == asset for pos in opened)
            or any(symbol.split("/")[0] == asset for symbol in portfolio.pending_symbols)
        ):
            return reject("POSITION_OR_ORDER_ALREADY_EXISTS")
        if len(opened) + len(portfolio.pending_symbols) >= p.max_positions:
            return reject("MAX_CONCURRENT_POSITIONS")
        try:
            validate_series(
                snapshot.candles,
                self.research.entry_seconds,
                snapshot,
                self.research.max_candle_lag_seconds,
            )
            validate_series(
                snapshot.trend_candles,
                self.research.trend_seconds,
                snapshot,
                self.research.max_candle_lag_seconds,
            )
            features = FeatureEngine(self.research).compute(snapshot.candles)
        except ValueError:
            return reject("INVALID_ENTRY_HISTORY")
        if signal.atr != features.atr or signal.entry_price != features.close:
            return reject("ENTRY_FEATURE_MISMATCH")
        if features.atr <= 0:
            return reject("INVALID_ATR")
        fx: dict[str, QuoteConversion] = {rate.quote: rate for rate in portfolio.conversions}

        def conversion(quote: str) -> Decimal:
            if quote == "TMN":
                return D(1)
            rate = fx.get(quote)
            if rate is None or not 0 <= (now - rate.as_of).total_seconds() <= p.max_fx_age_seconds:
                raise ValueError("Missing or stale conversion")
            return rate.tmn_per_unit

        try:
            rate = conversion(market.quote)
            open_risk = portfolio.reserved_risk_tmn
            marked_exposure = D(0)
            for pos in opened:
                context = self.snapshots.get(pos.symbol)
                if (
                    context is None
                    or context.as_of != now
                    or context.market is None
                    or context.liquidity is None
                    or (now - context.liquidity.as_of).total_seconds() > p.max_snapshot_age_seconds
                ):
                    return reject("MISSING_POSITION_RISK_CONTEXT")
                position_rate = conversion(context.market.quote)
                cost_buffer = context.market.taker_fee_rate + p.slippage_fraction
                open_risk += (
                    pos.quantity
                    * (
                        max(D(0), pos.entry_price - pos.stop_loss)
                        + pos.entry_price * cost_buffer
                        + pos.stop_loss * cost_buffer
                    )
                    * position_rate
                )
                mark = liquidity_features(context.liquidity, p.slippage_fraction).ask
                marked_exposure += pos.quantity * mark * position_rate
        except ValueError:
            return reject("MISSING_OR_STALE_FX")
        price = rounded(liquid.ask * (1 + p.slippage_fraction), market.price_tick, up=True)
        if abs(price - features.close) / features.close > p.max_entry_drift:
            return reject("ENTRY_PRICE_DRIFT")
        stop = rounded(price - self.research.stop_atr * features.atr, market.price_tick)
        target = rounded(price + self.research.target_atr * features.atr, market.price_tick)
        if not 0 < stop < price < target:
            return reject("INVALID_ROUNDED_ATR_LEVELS")
        cost = market.taker_fee_rate + p.slippage_fraction
        loss_per_unit = price - stop + price * cost + stop * cost
        net_reward = target - price - price * cost - target * cost
        if net_reward <= 0 or net_reward / loss_per_unit < p.min_net_reward_risk:
            return reject("FEES_ERASE_REWARD")
        remaining = (
            equity * p.max_exposure_fraction
            - max(portfolio.gross_exposure_tmn, marked_exposure)
            - portfolio.reserved_exposure_tmn
        )
        risk_budget = min(equity * p.risk_per_trade, equity * p.max_open_risk_fraction - open_risk)
        if remaining <= 0 or risk_budget <= 0:
            return reject("EXPOSURE_OR_RISK_BUDGET_EXHAUSTED")
        cash = free.get(market.quote, D(0)) / (1 + market.taker_fee_rate)
        notional_cap = min(
            remaining / rate,
            equity * p.max_asset_fraction / rate,
            cash,
            liquid.ask_depth_quote * p.max_depth_participation,
        )
        quantity = rounded(
            min(notional_cap / price, risk_budget / (rate * loss_per_unit)), market.quantity_step
        )
        if quantity < market.minimum_quantity or quantity * price < market.minimum_notional:
            return reject("BELOW_MINIMUM_SIZE_OR_LIQUIDITY")
        try:
            validate_spot_order(
                signal.symbol,
                signal.action,
                quantity,
                price,
                market,
                (signal.symbol,),
                free,
                market.taker_fee_rate,
            )
        except ValueError as exc:
            return reject(str(exc))
        return RiskDecision(
            allowed=True,
            reasons=("ENTRY_WITHIN_RISK_LIMITS",),
            parameters_id=p.parameters_id,
            parameters_json=p.model_dump_json(),
            quantity=quantity,
            reference_price=price,
            stop_loss=stop,
            take_profit=target,
            risk_tmn=quantity * loss_per_unit * rate,
            notional_tmn=quantity * price * rate,
        )
