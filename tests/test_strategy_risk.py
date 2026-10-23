import asyncio
from datetime import timedelta
from decimal import Decimal, localcontext

import pytest
from pydantic import ValidationError

from quantpilot.config import EngineConfig
from quantpilot.demo import (
    AbstainingEvaluator,
    InMemoryEventBus,
    MemoryDecisionRepository,
    MemoryPortfolioRepository,
)
from quantpilot.engine import TradingEngine
from quantpilot.models import (
    AssetBalance,
    DepthLevel,
    OrderIntent,
    Position,
)
from quantpilot.trading.config import ResearchParameters, RiskParameters
from quantpilot.trading.demo import NOW, PAIR, SyntheticClock, SyntheticSource, synthetic_context
from quantpilot.trading.features import FeatureEngine, adx, atr, ema, rsi
from quantpilot.trading.lifecycle import apply_simulated_fill, exit_signal, simulated_fill
from quantpilot.trading.risk import DeterministicRiskEngine
from quantpilot.trading.strategy import (
    MarketEligibilityFilter,
    MomentumBreakout,
    Regime,
    RegimeDetector,
)

D = Decimal
P = ResearchParameters()
LIMITS = RiskParameters()
ELIGIBLE = MarketEligibilityFilter({PAIR})


def changed(model, **updates):
    return type(model).model_validate({**model.model_dump(), **updates})


def decision(snapshot=None, portfolio=None, limits=LIMITS, parameters=P):
    original, account = synthetic_context(parameters)
    snapshot = snapshot or original
    portfolio = portfolio or account
    signal = MomentumBreakout(parameters, ELIGIBLE).evaluate(snapshot, portfolio)
    risk = DeterministicRiskEngine(
        limits, parameters, ELIGIBLE, {PAIR: snapshot}, {account.account_id}
    )
    return signal, risk.check(signal, portfolio)


def position(symbol=PAIR, quantity=D("1"), stop=D(110), target=D(140)):
    return Position(
        position_id="p-" + symbol,
        symbol=symbol,
        quantity=quantity,
        entry_price=D(120),
        stop_loss=stop,
        take_profit=target,
        opened_at=NOW - timedelta(hours=2),
        updated_at=NOW - timedelta(hours=1),
    )


def test_indicator_known_values_and_wilder_initialization():
    assert ema(tuple(map(D, [1, 2, 3, 4])), 3) == D(3)
    assert rsi((D(5),) * 6, 3) == 50
    assert rsi(tuple(map(D, range(1, 9))), 3) == 100
    assert rsi(tuple(map(D, range(9, 1, -1))), 3) == 0
    snapshot, _ = synthetic_context()
    assert atr(snapshot.trend_candles, 14) == D("0.2")
    assert adx(snapshot.trend_candles, 14) == 100
    with pytest.raises(ValueError):
        ema((D(1),), 3)


def test_prior_breakout_window_and_relative_volume():
    snapshot, _ = synthetic_context()
    f = FeatureEngine(P).compute(snapshot.candles)
    previous = snapshot.candles[-P.breakout_window - 1 : -1]
    assert f.prior_high == max(c.high for c in previous)
    assert f.prior_low == min(c.low for c in previous)
    assert f.prior_high < snapshot.candles[-1].close
    assert f.relative_volume == 2


def test_buy_signal_and_fee_buffered_size():
    snapshot, account = synthetic_context()
    signal, risk = decision(snapshot, account)
    assert signal.action == "BUY" and risk.allowed
    assert signal.atr > 0 and risk.stop_loss < risk.reference_price < risk.take_profit
    assert risk.risk_tmn <= account.equity_tmn * LIMITS.risk_per_trade
    assert risk.notional_tmn <= account.equity_tmn * LIMITS.max_asset_fraction
    assert risk.quantity % snapshot.market.quantity_step == 0
    assert signal.parameters_id and risk.parameters_id
    assert signal.parameters_json and risk.parameters_json


def test_determinism_including_decimal_context():
    first = decision()
    with localcontext() as ctx:
        from decimal import ROUND_UP

        ctx.prec = 10
        ctx.rounding = ROUND_UP
        second = decision()
    assert first == second


@pytest.mark.parametrize(
    "case,reason",
    [
        ("volume", "LOW_RELATIVE_VOLUME"),
        ("breakout", "NO_BREAKOUT"),
        ("trend", "REGIME_NOT_UPTREND"),
        ("gap", "CANDLE_GAP"),
        ("timeframe", "TIMEFRAME_MISMATCH"),
        ("short", "INSUFFICIENT_HISTORY"),
    ],
)
def test_hold_rules(case, reason):
    snapshot, account = synthetic_context()
    rows = list(snapshot.candles)
    if case == "volume":
        rows[-1] = changed(rows[-1], volume=D(1))
    if case == "breakout":
        rows[-1] = changed(rows[-1], open=D(120), close=D(120), high=D(121), low=D(119))
    if case == "trend":
        trend = tuple(
            changed(
                row,
                open=D(200) - D(i) / 10,
                close=D(200) - D(i) / 10,
                high=D("200.1") - D(i) / 10,
                low=D("199.9") - D(i) / 10,
            )
            for i, row in enumerate(snapshot.trend_candles)
        )
        snapshot = changed(snapshot, trend_candles=trend)
    if case == "gap":
        rows.pop(-3)
    if case == "timeframe":
        rows[-1] = changed(rows[-1], open_time=rows[-1].open_time + timedelta(seconds=1))
    if case == "short":
        rows = rows[-10:]
    snapshot = changed(snapshot, candles=tuple(rows))
    result = MomentumBreakout(P, ELIGIBLE).evaluate(snapshot, account)
    assert result.action == "HOLD" and reason in result.reasons


def test_no_future_or_incomplete_candles():
    snapshot, _ = synthetic_context()
    last = snapshot.candles[-1]
    with pytest.raises(ValidationError):
        changed(snapshot, as_of=NOW - timedelta(seconds=1))
    with pytest.raises(ValidationError):
        changed(snapshot, candles=snapshot.candles[:-1] + (changed(last, closed=False),))
    with pytest.raises(ValueError):
        FeatureEngine(P).compute(snapshot.candles[:-1] + (changed(last, closed=False),))


def test_regime_volatility_and_spread():
    from dataclasses import replace

    snapshot, _ = synthetic_context()
    trend = FeatureEngine(P).compute(snapshot.trend_candles)
    detector = RegimeDetector(P)
    assert detector.classify(trend, D("0.1")) == Regime.ILLIQUID
    assert detector.classify(replace(trend, atr=D(100)), D(0)) == Regime.VOLATILE
    assert detector.classify(replace(trend, adx=D(0)), D(0)) == Regime.RANGE


@pytest.mark.parametrize(
    "case,reason",
    [
        ("loss", "DAILY_LOSS_LIMIT"),
        ("drawdown", "MAX_DRAWDOWN"),
        ("halt", "RISK_HALT_LATCHED"),
        ("positions", "MAX_CONCURRENT_POSITIONS"),
        ("pending", "POSITION_OR_ORDER_ALREADY_EXISTS"),
        ("exposure", "EXPOSURE_OR_RISK_BUDGET_EXHAUSTED"),
        ("fx", "MISSING_OR_STALE_FX"),
        ("stale_account", "STALE_ACCOUNT"),
        ("day", "DAILY_BASELINE_DATE_MISMATCH"),
        ("cash", "BELOW_MINIMUM_SIZE_OR_LIQUIDITY"),
    ],
)
def test_account_risk_rejections(case, reason):
    snapshot, account = synthetic_context()
    if case == "loss":
        account = changed(account, equity_tmn=D(4800000))
    if case == "drawdown":
        account = changed(account, peak_equity_tmn=D(6000000))
    if case == "halt":
        account = changed(account, risk_halted=True)
    if case == "positions":
        account = changed(account, positions=(position("ETH/USDT"), position("SOL/USDT")))
    if case == "pending":
        account = changed(account, pending_symbols=(PAIR,))
    if case == "exposure":
        account = changed(account, reserved_exposure_tmn=D(1000000))
    if case == "fx":
        account = changed(account, conversions=())
    if case == "stale_account":
        old = NOW - timedelta(minutes=10)
        account = changed(
            account, as_of=old, conversions=(changed(account.conversions[0], as_of=old),)
        )
    if case == "day":
        account = changed(account, trading_day=account.trading_day - timedelta(days=1))
    if case == "cash":
        account = changed(
            account, balances=(AssetBalance(currency="USDT", free=D(0), reserved=D(100)),)
        )
    signal, risk = decision(snapshot, account)
    assert not risk.allowed and reason in risk.reasons
    if case in ("loss", "drawdown", "halt"):
        assert risk.halt_new_entries


@pytest.mark.parametrize(
    "case,reason",
    [
        ("liquidity", "BELOW_MINIMUM_SIZE_OR_LIQUIDITY"),
        ("minimum", "BELOW_MINIMUM_SIZE_OR_LIQUIDITY"),
        ("fees", "FEES_ERASE_REWARD"),
        ("stale_book", "MISSING_OR_STALE_LIQUIDITY"),
    ],
)
def test_market_risk_rejections(case, reason):
    snapshot, account = synthetic_context()
    if case == "minimum":
        snapshot = changed(snapshot, market=changed(snapshot.market, minimum_notional=D(100000)))
    if case == "fees":
        snapshot = changed(snapshot, market=changed(snapshot.market, taker_fee_rate=D("0.1")))
    if case == "stale_book":
        snapshot = changed(
            snapshot, liquidity=changed(snapshot.liquidity, as_of=NOW - timedelta(minutes=5))
        )
    if case == "liquidity":
        snapshot = changed(
            snapshot,
            liquidity=changed(
                snapshot.liquidity,
                asks=(DepthLevel(price=snapshot.candles[-1].close, quantity=D("0.00001")),),
            ),
        )
    _, risk = decision(snapshot, account)
    assert not risk.allowed and reason in risk.reasons


def test_unapproved_market_and_account():
    snapshot, account = synthetic_context()
    signal = MomentumBreakout(P, MarketEligibilityFilter(())).evaluate(snapshot, account)
    assert signal.action == "HOLD" and "MARKET_NOT_APPROVED" in signal.reasons
    signal = MomentumBreakout(P, ELIGIBLE).evaluate(snapshot, account)
    risk = DeterministicRiskEngine(LIMITS, P, ELIGIBLE, {PAIR: snapshot}, ())
    assert "ACCOUNT_NOT_APPROVED" in risk.check(signal, account).reasons


def test_risk_rejects_forged_signal():
    snapshot, account = synthetic_context()
    signal = MomentumBreakout(P, ELIGIBLE).evaluate(snapshot, account)
    forged = changed(signal, atr=D(1))
    risk = DeterministicRiskEngine(LIMITS, P, ELIGIBLE, {PAIR: snapshot}, {account.account_id})
    assert "STRATEGY_SIGNAL_MISMATCH" in risk.check(forged, account).reasons


def test_stop_target_precedence_gap_and_time_exit():
    snapshot, _ = synthetic_context()
    pos = position(stop=D(120), target=D(125))
    bar = changed(snapshot.candles[-1], open=D(122), close=D(122), high=D(130), low=D(115))
    assert exit_signal(pos, bar, None, NOW, P) == ("ATR_STOP", D(120))
    assert exit_signal(pos, changed(bar, open=D(118)), None, NOW, P) == ("STOP_GAP", D(118))
    assert exit_signal(pos, changed(bar, low=D(121)), None, NOW, P)[0] == "TAKE_PROFIT"
    assert (
        exit_signal(
            pos, changed(bar, low=D(121), high=D(123)), None, NOW, changed(P, max_hold_seconds=1)
        )[0]
        == "MAX_HOLD_TIME"
    )


def test_sell_allowed_during_entry_halt_without_full_trend_history():
    snapshot, account = synthetic_context()
    account = changed(
        account,
        positions=(position(stop=D(124)),),
        risk_halted=True,
        balances=(AssetBalance(currency="BTC", free=D(1), reserved=D(0)),),
    )
    snapshot = changed(snapshot, trend_candles=())
    signal, risk = decision(snapshot, account)
    assert signal.action == "SELL" and risk.allowed and risk.quantity <= 1


def test_simulated_partial_fill_and_no_stop_widening():
    intent = OrderIntent(
        client_id="sim-1",
        decision_id="decision",
        account_id="mock",
        symbol=PAIR,
        side="BUY",
        order_type="MARKET",
        base_quantity=D(1),
    )
    first = simulated_fill(intent, D(120), NOW, D("0.001"))
    pos = apply_simulated_fill(None, first, D(2), P)
    assert pos.stop_loss == 116 and pos.take_profit == 126
    assert apply_simulated_fill(pos, first, D(2), P) == pos
    with pytest.raises(ValueError, match="Conflicting replay"):
        apply_simulated_fill(pos, changed(first, base_quantity=D(2)), D(2), P)
    partial = simulated_fill(changed(intent, client_id="sim-2"), D(119), NOW + timedelta(seconds=1))
    updated = apply_simulated_fill(pos, partial, D(3), P)
    assert updated.quantity == 2 and updated.stop_loss >= pos.stop_loss
    sell = changed(intent, client_id="sim-exit", side="SELL", base_quantity=D(2))
    closed = apply_simulated_fill(
        updated, simulated_fill(sell, D(121), NOW + timedelta(seconds=2)), D(2), P
    )
    assert closed.state == "CLOSED" and closed.quantity == 0
    with pytest.raises(ValueError):
        apply_simulated_fill(None, simulated_fill(sell, D(121), NOW), D(2), P)


def test_engine_persists_breaker_and_never_submits():
    snapshot, account = synthetic_context()
    account = changed(account, equity_tmn=D(4800000))
    repo = MemoryPortfolioRepository(account)
    engine = TradingEngine(
        EngineConfig(strategy_version=P.version),
        SyntheticClock(),
        SyntheticSource(snapshot),
        repo,
        MomentumBreakout(P, ELIGIBLE),
        AbstainingEvaluator(),
        DeterministicRiskEngine(LIMITS, P, ELIGIBLE, {PAIR: snapshot}, {account.account_id}),
        MemoryDecisionRepository(),
        InMemoryEventBus(),
    )
    result = asyncio.run(engine.observe(PAIR, account.account_id))
    assert result.risk.halt_new_entries and repo.state.risk_halted
    assert result.execution_state == "NOT_SUBMITTED" and engine.execution is None


def test_sell_cannot_consume_reserved_inventory():
    snapshot, account = synthetic_context()
    account = changed(
        account,
        positions=(position(stop=D(124)),),
        balances=(AssetBalance(currency="BTC", free=D(0), reserved=D(1)),),
    )
    signal, risk = decision(snapshot, account)
    assert signal.action == "SELL" and not risk.allowed
    assert "EXIT_BELOW_MINIMUM_OR_RESERVED" in risk.reasons


def test_cross_quote_position_blocks_same_asset_entry():
    snapshot, account = synthetic_context()
    account = changed(account, positions=(position("BTC/TMN"),))
    _, risk = decision(snapshot, account)
    assert "POSITION_OR_ORDER_ALREADY_EXISTS" in risk.reasons


def test_minimum_size_is_rejected_not_rounded_up():
    snapshot, account = synthetic_context()
    snapshot = changed(snapshot, market=changed(snapshot.market, quantity_step=D(10)))
    _, risk = decision(snapshot, account)
    assert not risk.allowed and risk.quantity == 0


def test_rsi_filter_and_atr_stop_configuration():
    snapshot, account = synthetic_context()
    strict = changed(P, rsi_max=D(52))
    signal = MomentumBreakout(strict, ELIGIBLE).evaluate(snapshot, account)
    assert signal.action == "HOLD" and "RSI_OUTSIDE_ENTRY_RANGE" in signal.reasons
    assert strict.parameters_id != P.parameters_id
    with pytest.raises(ValidationError):
        RiskParameters(risk_per_trade=D("0.006"))


def test_entry_atr_levels_come_from_fill_not_signal_reference():
    intent = OrderIntent(
        client_id="sim",
        decision_id="d",
        account_id="offline",
        symbol=PAIR,
        side="BUY",
        order_type="MARKET",
        base_quantity=D(1),
    )
    fill = simulated_fill(intent, D(130), NOW)
    actual = apply_simulated_fill(None, fill, D(2), P)
    assert actual.stop_loss == 126 and actual.take_profit == 136


def test_new_position_does_not_use_pre_entry_bar_extremes():
    snapshot, _ = synthetic_context()
    bar = changed(snapshot.candles[-1], low=D(90), high=D(150))
    pos = changed(position(), opened_at=NOW - timedelta(minutes=1), updated_at=NOW)
    assert exit_signal(pos, bar, None, NOW, P) == (None, None)


def test_resample_5_and_15_minutes_from_completed_history():
    from quantpilot.marketdata.collect import CandleCollector, Collectors
    from quantpilot.marketdata.domain import CollectionPolicy
    from quantpilot.marketdata.mock import MockPublic
    from quantpilot.trading.timeframes import research_snapshot

    base = asyncio.run(
        CandleCollector(
            Collectors(MockPublic(NOW), CollectionPolicy(approved=frozenset({PAIR}))), bars=30
        ).snapshot(PAIR, NOW)
    )
    result = research_snapshot(base, P)
    assert len(result.candles) == 6 and len(result.trend_candles) == 2
    assert result.candles[0].volume == D("17.5")
    assert result.candles[0].open == 100 and result.candles[0].close == 101
    assert all(row.close_time <= NOW for row in result.trend_candles)


def test_resample_drops_open_target_without_future_data():
    from quantpilot.marketdata.collect import CandleCollector, Collectors
    from quantpilot.marketdata.domain import CollectionPolicy
    from quantpilot.marketdata.mock import MockPublic
    from quantpilot.trading.timeframes import resample

    base = asyncio.run(
        CandleCollector(
            Collectors(MockPublic(NOW), CollectionPolicy(approved=frozenset({PAIR}))), bars=30
        ).snapshot(PAIR, NOW)
    )
    cutoff = NOW - timedelta(minutes=2)
    available = tuple(row for row in base.candles if row.close_time <= cutoff)
    # Real historical collection received_at is later than event time. Set the
    # test's availability explicitly to each close, without using future records.
    available = tuple(changed(row, received_at=row.close_time) for row in available)
    result = resample(available, 300, cutoff)
    assert len(result) == 5 and result[-1].close_time == NOW - timedelta(minutes=5)
    with pytest.raises(ValueError):
        resample(available[:2] + available[3:], 300, cutoff)
