"""Eligible flat-account entry opportunities and explicitly fixed-horizon labels."""

from collections import Counter
from datetime import datetime
from decimal import Context, Decimal, localcontext
from typing import Any

from quantpilot.backtest.config import SimulationParameters
from quantpilot.backtest.execution import SimulatedExecutionProvider
from quantpilot.backtest.history import HistoricalClock, HistoricalMarketDataProvider
from quantpilot.backtest.ledger import PortfolioLedger
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.config import stable_id
from quantpilot.models import (
    Candle,
    LiquiditySnapshot,
    MarketConstraints,
    OrderIntent,
    OrderState,
    QuoteConversion,
    RiskDecision,
    Signal,
)
from quantpilot.trading.config import ResearchParameters, RiskParameters
from quantpilot.trading.risk import DeterministicRiskEngine
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout

from .domain import LearningConfig, Sample
from .features import extract_features

D = Decimal


def market_input(
    raw: dict[str, Any],
) -> tuple[
    HistoricalMarketDataProvider, RiskParameters, tuple[str, ...], tuple[QuoteConversion, ...]
]:
    data = HistoricalMarketDataProvider(
        {p: tuple(Candle.model_validate(c) for c in rows) for p, rows in raw["candles"].items()},
        {p: MarketConstraints.model_validate(m) for p, m in raw["markets"].items()},
        ResearchParameters.model_validate(raw.get("research", {})),
        SimulationParameters.model_validate(raw.get("simulation", {})),
        {
            p: tuple(LiquiditySnapshot.model_validate(q) for q in rows)
            for p, rows in raw.get("quotes", {}).items()
        },
    )
    return (
        data,
        RiskParameters.model_validate(raw.get("risk", {})),
        tuple(raw["approved"]),
        tuple(QuoteConversion.model_validate(x) for x in raw.get("fx", [])),
    )


def funded_ledger(replay: HistoricalReplay, now: datetime) -> PortfolioLedger:
    ledger = PortfolioLedger(replay.data.simulation.initial_capital_tmn, replay.data.research)
    if replay.conversions(now):
        p = replay.data.simulation
        if p.quote_funding_fraction:
            budget = p.initial_capital_tmn * p.quote_funding_fraction
            quantity = (budget / (replay.rate(now) * (1 + p.fx_fee))).next_minus()
            if quantity > 0:
                ledger.convert("USDT", quantity, replay.rate(now), p.fx_fee, now)
    return ledger


async def label_entry(
    replay: HistoricalReplay, signal: Signal, risk: RiskDecision, config: LearningConfig
) -> tuple[tuple[datetime, Decimal, Decimal] | None, str]:
    with localcontext(Context(prec=34)):
        return await _label_entry(replay, signal, risk, config)


async def _label_entry(
    replay: HistoricalReplay, signal: Signal, risk: RiskDecision, config: LearningConfig
) -> tuple[tuple[datetime, Decimal, Decimal] | None, str]:
    data, pair = replay.data, signal.symbol
    rows = data.candles[pair]
    indices = [i for i, c in enumerate(rows) if c.open_time == signal.as_of]
    if not indices or indices[0] + config.label_bars >= len(rows):
        return None, "RIGHT_CENSORED"
    index = indices[0]
    end = index + config.label_bars
    if (
        rows[index].close_time - rows[index].open_time
    ).total_seconds() != data.research.entry_seconds:
        raise ValueError(
            "AI labels require entry-timeframe source candles; resample explicitly first"
        )
    assert signal.atr is not None and risk.reference_price is not None
    ledger = funded_ledger(replay, signal.as_of)
    clock = HistoricalClock(signal.as_of)
    execution = SimulatedExecutionProvider(clock, data, ledger)
    quote = pair.split("/")[1]
    entry_fx = D(1) if quote == "TMN" else replay.rate(signal.as_of)
    execution.plan("label-entry", signal.atr, risk.reference_price, entry_fx)
    await execution.submit(
        OrderIntent(
            client_id="label-entry",
            decision_id="label",
            account_id="backtest",
            symbol=pair,
            side="BUY",
            order_type="MARKET",
            base_quantity=risk.quantity,
        )
    )
    await execution.process(rows[index], True, entry_fx, rows[index - 1].volume if index else D(0))
    if await execution.lookup("label-entry") != OrderState.FILLED:
        return None, "ENTRY_NOT_FULLY_EXECUTABLE"
    clock.advance(rows[end].open_time)
    exit_fx = D(1) if quote == "TMN" else replay.rate(clock.now())
    execution.plan("label-exit", signal.atr, rows[end].open, exit_fx)
    await execution.submit(
        OrderIntent(
            client_id="label-exit",
            decision_id="label",
            account_id="backtest",
            symbol=pair,
            side="SELL",
            order_type="MARKET",
            base_quantity=risk.quantity,
        )
    )
    await execution.process(rows[end], True, exit_fx, rows[end - 1].volume)
    if await execution.lookup("label-exit") != OrderState.FILLED:
        return None, "EXIT_NOT_FULLY_EXECUTABLE"
    buys, sells = await execution.fills("label-entry"), await execution.fills("label-exit")
    entry = sum((f.base_quantity * f.price.amount + f.fee.amount for f in buys), D(0)) * entry_fx
    exit_value = (
        sum((f.base_quantity * f.price.amount - f.fee.amount for f in sells), D(0)) * exit_fx
    )
    # Per-trade round-trip conversion friction, not gains on idle USDT balances.
    fx_fee = data.simulation.fx_fee if quote == "USDT" else D(0)
    entry *= 1 + fx_fee
    exit_value *= 1 - fx_fee
    pnl = exit_value - entry
    return (clock.now(), pnl, pnl / entry), "LABELED"


async def build_dataset(raw: dict[str, Any], config: LearningConfig) -> dict[str, Any]:
    with localcontext(Context(prec=34)):
        return await _build_dataset(raw, config)


async def _build_dataset(raw: dict[str, Any], config: LearningConfig) -> dict[str, Any]:
    data, risk, approved, fx = market_input(raw)
    replay = HistoricalReplay(data, risk, approved, fx)
    eligibility = MarketEligibilityFilter(approved)
    strategy = MomentumBreakout(data.research, eligibility)
    times = sorted({c.close_time for rows in data.candles.values() for c in rows})
    samples = []
    counts: Counter[str] = Counter()
    for now in times:
        if int(now.timestamp()) % data.research.entry_seconds:
            continue
        snapshots = {p: await data.snapshot(p, now) for p in sorted(data.candles)}
        ledger = funded_ledger(replay, now)
        marks = {"USDT": replay.rate(now)} if replay.conversions(now) else {}
        portfolio = ledger.snapshot(now, marks, replay.conversions(now))
        manager = DeterministicRiskEngine(
            risk, data.research, eligibility, snapshots, ("backtest",)
        )
        for pair, snapshot in snapshots.items():
            signal = strategy.evaluate(snapshot, portfolio)
            if signal.action != "BUY":
                counts["STRATEGY_NOT_BUY"] += 1
                continue
            decision = manager.check(signal, portfolio)
            if not decision.allowed:
                counts["RISK_REJECTED"] += 1
                for reason in decision.reasons:
                    counts[f"RISK_{reason}"] += 1
                continue
            counts["ELIGIBLE_SIGNALS"] += 1
            label, status = await label_entry(replay, signal, decision, config)
            counts[status] += 1
            if label is None:
                continue
            ended, pnl, net = label
            features = extract_features(snapshot, signal, data.research)
            assert signal.snapshot_id is not None
            samples.append(
                Sample(
                    sample_id=stable_id(
                        {
                            "snapshot": signal.snapshot_id,
                            "label_config": config.config_id,
                            "risk": risk.parameters_id,
                            "execution": data.simulation.config_id,
                        }
                    ),
                    symbol=pair,
                    as_of=now,
                    label_end=ended,
                    snapshot_id=signal.snapshot_id,
                    features=features,
                    positive=int(pnl > 0),
                    net_pnl_tmn=pnl,
                    net_return=net,
                ).model_dump(mode="json")
            )
    manifest = {
        "schema": "eligible-fixed-horizon-v1",
        "source_id": stable_id(raw),
        "learning_config": config.model_dump(mode="json"),
        "counts": dict(counts),
        "research": data.research.model_dump(mode="json"),
        "risk": risk.model_dump(mode="json"),
        "simulation": data.simulation.model_dump(mode="json"),
        "label_policy": (
            "Flat-account eligible BUY; executable fixed-horizon next-open roundtrip "
            "after all costs; partial/unfillable/right-censored excluded, not labeled losses"
        ),
        "limitations": [
            "Labels predict profit CONDITIONAL on complete execution",
            "Fixed-horizon target differs from production strategy lifecycle",
            "Overlapping opportunities are not an investable standalone portfolio",
            "Static supplied universe may contain survivorship bias",
        ],
    }
    return {
        "dataset_id": stable_id({"manifest": manifest, "samples": samples}),
        "manifest": manifest,
        "samples": samples,
    }
