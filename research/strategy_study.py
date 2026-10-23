"""Bounded, source-pinned offline study using the existing trading engines.

Run from repository root: python -m research.strategy_study --help.
Public candle cache is input, never an order book. No execution credentials are
loaded except by the explicitly read-only metadata subcommand.
"""

import argparse
import asyncio
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Context, Decimal, localcontext
from pathlib import Path

from quantpilot.ai.dataset import market_input
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.backtest.reports import export_report
from quantpilot.config import stable_id
from quantpilot.models import Candle
from quantpilot.shadow.ai import core_version
from quantpilot.trading.config import ResearchParameters, RiskParameters
from quantpilot.trading.features import FeatureEngine, liquidity_features
from quantpilot.trading.risk import rounded
from quantpilot.trading.timeframes import resample
from research.prepared_history import PreparedHistory

D = Decimal
PLAN = Path("research/strategy-study-v1/plan.json")
ROOT = Path("data/strategy-research-v1-prepared")


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=str)


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        f.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dt(value):
    value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Aware UTC timestamps required")
    return value.astimezone(timezone.utc)


def load_minutes(folder, start, end):
    """Validate arrays, reject conflicting duplicates, split gaps, never fill them."""
    seen, hashes = {}, {}
    duplicates = 0
    for path in sorted(Path(folder).glob("*.json")):
        raw = read(path)
        hashes[str(path)] = digest(path)
        if raw.get("s") != "ok":
            raise ValueError("Unsuccessful historical source")
        if len({len(raw[k]) for k in ("t", "o", "h", "l", "c", "v")}) != 1:
            raise ValueError("Mismatched OHLCV arrays")
        for i, t in enumerate(raw["t"]):
            at = datetime.fromtimestamp(t, timezone.utc)
            if at < start or at + timedelta(seconds=60) > end:
                continue
            if t % 60:
                raise ValueError("Unaligned source timestamp")
            values = tuple(D(str(raw[k][i])) for k in ("o", "h", "l", "c", "v"))
            if t in seen:
                if seen[t] != values:
                    raise ValueError("Conflicting duplicate timestamp")
                duplicates += 1
            seen[t] = values
    segments = []
    previous = None
    for t, values in sorted(seen.items()):
        if previous is None or t != previous + 60:
            segments.append([])
        at = datetime.fromtimestamp(t, timezone.utc)
        closed = at + timedelta(seconds=60)
        # Receipt time is unknown in this old cache; publication at close is an
        # explicit replay assumption, not a claim about historical network latency.
        segments[-1].append(
            Candle(
                event_id=stable_id(["wallex-udf-1m", t, [str(x) for x in values]]),
                symbol="BTC/TMN",
                event_time=closed,
                received_at=closed,
                source="wallex-udf-cached-public-observation",
                open_time=at,
                close_time=closed,
                open=values[0],
                high=values[1],
                low=values[2],
                close=values[3],
                volume=values[4],
                closed=True,
            )
        )
        previous = t
    return segments, hashes, duplicates


def aggregate(segment, seconds=300):
    if not segment:
        return ()
    # Trim partial boundary buckets only; internal gaps were split upstream.
    start = int(segment[0].open_time.timestamp())
    start = (start + seconds - 1) // seconds * seconds
    stop = int(segment[-1].close_time.timestamp()) // seconds * seconds
    rows = tuple(
        c
        for c in segment
        if int(c.open_time.timestamp()) >= start and int(c.close_time.timestamp()) <= stop
    )
    return resample(rows, seconds, rows[-1].close_time) if rows else ()


async def metadata():
    """Only GET fees/markets; persist an allowlisted numeric projection."""
    from quantpilot.live.settings import load_wallex_settings
    from quantpilot.live.transport import WallexSpotREST

    connection = load_wallex_settings()
    client = WallexSpotREST(
        connection.api_key, sub_account_client_id=connection.sub_account_client_id
    )
    result = {
        "at": datetime.now(timezone.utc).isoformat(),
        "symbol": "BTC/TMN",
        "exchange_mutations": 0,
        "live_enabled": False,
        "scope": "configured credential and explicit sub-account read selector",
    }
    try:
        fees, markets = await client.fees(), await client.markets()
        f, m = fees["BTCTMN"], markets["BTCTMN"]
        if m["baseAsset"] != "BTC" or m["quoteAsset"] != "TMN":
            raise ValueError("MARKET_IDENTITY_MISMATCH")
        result.update(
            status="READ_VERIFIED",
            maker_fee=str(D(f["makerFeeRate"])),
            taker_fee=str(D(f["takerFeeRate"])),
            minimum_quantity=str(D(m["minQty"])),
            minimum_notional=str(D(m["minNotional"])),
            quantity_step=str(D(10) ** -int(m["stepSize"])),
            price_tick=str(D(10) ** -int(m["tickSize"])),
            endpoints=["GET /v1/account/fee", "GET /v1/markets"],
        )
    except Exception as exc:
        result.update(status="READ_FAILED", exception_type=type(exc).__name__)
        response = getattr(exc, "response", None)
        if response is not None:
            result["http_status"] = response.status_code
    finally:
        await client.close()
    write(ROOT / "current-cost-metadata.json", result)
    print(json.dumps(result))


def prepare():
    plan = read(PLAN)
    if (ROOT / "manifest.json").exists():
        raise ValueError("Study already prepared; do not overwrite")
    segments, hashes, duplicates = load_minutes(
        plan["source_chunks"], dt(plan["requested_start"]), dt(plan["requested_end"])
    )
    baseline = read(plan["baseline_input"])
    metadata_file = ROOT / "current-cost-metadata.json"
    current = read(metadata_file) if metadata_file.exists() else {}
    prior = read(plan["prior_metadata"])
    if current.get("status") != "READ_VERIFIED":
        current = {
            "status": "PRIOR_OBSERVATION_SCENARIO_ONLY",
            "at": None,
            "maker_fee": prior["btctmn_fees"]["makerFeeRate"],
            "taker_fee": prior["btctmn_fees"]["takerFeeRate"],
            "quantity_step": str(D(10) ** -int(prior["market_limits"]["stepSize"])),
            "price_tick": str(D(10) ** -int(prior["market_limits"]["tickSize"])),
            "minimum_quantity": prior["market_limits"]["minQty"],
            "minimum_notional": prior["market_limits"]["minNotional"],
        }
    coverage = []
    dataset_ids = {}
    for index, minutes in enumerate(segments):
        # Every variant uses 15-minute trend confirmation. Align the leading
        # bucket too, otherwise partial trend bars would invalidate all snapshots.
        aligned = [
            c
            for c in minutes
            if int(c.open_time.timestamp())
            >= (int(minutes[0].open_time.timestamp()) + 899) // 900 * 900
        ]
        candles = aggregate(aligned)
        if not candles:
            continue
        name = f"segment-{index}"
        encoded = [c.model_dump(mode="json") for c in candles]
        write(ROOT / "datasets" / f"{name}.json", encoded)
        dataset_ids[name] = stable_id(encoded)
        coverage.append(
            {
                "segment": name,
                "start": candles[0].open_time.isoformat(),
                "end": candles[-1].close_time.isoformat(),
                "minutes": len(minutes),
                "five_minute_candles": len(candles),
                "data_id": dataset_ids[name],
            }
        )
    protected = [Path(plan["baseline_input"]), Path(plan["baseline_report"])]
    protected += list(Path("data/backtest-long/baseline").glob("*"))
    manifest = {
        "plan": plan,
        "plan_id": stable_id(plan),
        "core_version": core_version(),
        "runner_sha256": digest(__file__),
        "prepared_provider_sha256": digest("research/prepared_history.py"),
        "source_sha256": hashes,
        "baseline_sha256": {str(p): digest(p) for p in protected},
        "research": ResearchParameters.model_validate(baseline.get("research", {})).model_dump(
            mode="json"
        ),
        "risk": RiskParameters.model_validate(baseline.get("risk", {})).model_dump(mode="json"),
        "market": current,
        "coverage": coverage,
        "dataset_ids": dataset_ids,
        "duplicate_minutes_identical": duplicates,
        "received_minutes": sum(len(x) for x in segments),
        "expected_minutes": int(
            (dt(plan["requested_end"]) - dt(plan["requested_start"])).total_seconds() // 60
        ),
        "publication_assumption": "at candle close; old cache receipt times unavailable",
        "historical_books": False,
        "live_enabled": False,
        "exchange_mutations": 0,
    }
    write(ROOT / "manifest.json", manifest)
    print(json.dumps({"prepared": str(ROOT), "coverage": coverage, "metadata": current["status"]}))


def manifest():
    value = read(ROOT / "manifest.json")
    if (
        value["core_version"] != core_version()
        or value["runner_sha256"] != digest(__file__)
        or value["prepared_provider_sha256"] != digest("research/prepared_history.py")
    ):
        raise ValueError("Research source changed; preserve pinned study")
    if value["plan_id"] != stable_id(read(PLAN)):
        raise ValueError("Research plan changed")
    for p, sha in value["baseline_sha256"].items():
        if digest(p) != sha:
            raise ValueError("Protected baseline changed")
    return value


def make_input(m, rows, variant, scenario):
    settings = m["plan"]["scenarios"][scenario]
    fees = m["market"]
    rate = (
        settings.get("fee")
        or fees["maker_fee" if settings["fee_source"] == "observed_maker" else "taker_fee"]
    )
    market = {
        "symbol": "BTC/TMN",
        "quote": "TMN",
        "spot_enabled": True,
        "account_enabled": True,
        "taker_fee_rate": rate,
        **{
            k: fees[k]
            for k in ("quantity_step", "price_tick", "minimum_quantity", "minimum_notional")
        },
    }
    research = {**m["research"], **variant}
    # Risk constraints are immutable; only cost estimate tracks the cost scenario.
    risk = {**m["risk"], "slippage_fraction": settings["slippage"]}
    return {
        "candles": {"BTC/TMN": rows},
        "markets": {"BTC/TMN": market},
        "approved": ["BTC/TMN"],
        "research": research,
        "risk": risk,
        "simulation": {
            "initial_capital_tmn": "5000000",
            "entry_fee": rate,
            "exit_fee": rate,
            "half_spread": settings["half_spread"],
            "slippage": settings["slippage"],
            "volume_participation": settings["volume_participation"],
            "operating_profile": "CONTINUOUS",
        },
    }


def summarize(report):
    reasons, actions, allowed = Counter(), Counter(), Counter()
    for decision in report["decisions"]:
        action = decision["signal"]["action"]
        actions[action] += 1
        if decision["risk"]["allowed"]:
            allowed[action] += 1
        else:
            reasons.update(decision["risk"]["reasons"])
    pnls = sorted(D(t["pnl_tmn"]) for t in report["trades"])
    distribution = {
        "n": len(pnls),
        "minimum": str(min(pnls)) if pnls else None,
        "maximum": str(max(pnls)) if pnls else None,
        "mean": str(sum(pnls) / len(pnls)) if pnls else None,
        "values_tmn": [str(x) for x in pnls],
    }
    return {
        "metrics": report["metrics"],
        "actions": dict(actions),
        "risk_approvals": dict(allowed),
        "risk_reasons": dict(reasons),
        "pnl_distribution": distribution,
        "residual_positions": report["residual_positions"],
        "remaining_holdings": report["remaining_holdings"],
        "config_id": report["manifest"]["config_id"],
        "input_id": report["manifest"]["input_id"],
    }


async def run_window(m, variant_name, variant, period, scenario):
    destination = ROOT / "runs" / variant_name / scenario / period
    summary_path = destination / "summary.json"
    if summary_path.exists():
        return read(summary_path)
    start, end = map(dt, m["plan"]["periods"][period])
    results = []
    for info in m["coverage"]:
        if dt(info["end"]) <= start or dt(info["start"]) >= end:
            continue
        path = ROOT / "datasets" / f"{info['segment']}.json"
        stored = read(path)
        if stable_id(stored) != info["data_id"]:
            raise ValueError("Dataset identity mismatch")
        # All earlier contiguous rows are warmup only, never inherited cash/PnL.
        rows = [c for c in stored if dt(c["close_time"]) < end]
        actual_start = max(start, dt(info["start"]))
        if not rows or dt(rows[-1]["close_time"]) <= actual_start:
            continue
        raw = make_input(m, rows, variant, scenario)
        data, risk, approved, fx = market_input(raw)
        data = PreparedHistory(data)
        report = await HistoricalReplay(data, risk, approved, fx, decision_start=actual_start).run()
        target = destination / info["segment"]
        if target.exists():
            raise ValueError("Incomplete prior run; preserve it and use reviewed new study")
        export_report(report, target)
        write(target / "input.json", raw)
        results.append(
            {
                "segment": info["segment"],
                "decision_start": actual_start.isoformat(),
                "decision_end": rows[-1]["close_time"],
                **summarize(report),
            }
        )
    # Disconnected windows have independent 5m accounts. Do not claim compounding.
    metrics = {
        "net_return_pct": str(sum(D(r["metrics"]["net_return_pct"]) for r in results)),
        "max_drawdown_pct": str(
            max((D(r["metrics"]["max_drawdown_pct"]) for r in results), default=D(0))
        ),
        "trade_count": sum(r["metrics"]["trade_count"] for r in results),
        "realized_pnl_tmn": str(sum(D(r["metrics"]["realized_pnl_tmn"]) for r in results)),
        "total_fees_tmn": str(sum(D(r["metrics"]["total_fees_tmn"]) for r in results)),
    }
    result = {
        "variant": variant_name,
        "period": period,
        "scenario": scenario,
        "aggregation": "sum of per-segment returns, not a compounded account",
        "segments": results,
        "metrics": metrics,
        "plan_id": m["plan_id"],
        "core_version": m["core_version"],
    }
    write(summary_path, result)
    print(json.dumps({k: v for k, v in result.items() if k != "segments"}), flush=True)
    return result


def select(results, policy):
    """Only train/validation summaries are permitted; final cannot enter ranking."""
    accepted = []
    rejected = {}
    for name, pair in results.items():
        if set(pair) != {"train", "validation"}:
            raise ValueError("Selection accepts train/validation only")
        train, validation = pair["train"]["metrics"], pair["validation"]["metrics"]
        reasons = []
        if train["trade_count"] < policy["minimum_train_trades"]:
            reasons.append("INSUFFICIENT_TRAIN_TRADES")
        if validation["trade_count"] < policy["minimum_validation_trades"]:
            reasons.append("INSUFFICIENT_VALIDATION_TRADES")
        if D(train["net_return_pct"]) <= 0 or D(validation["net_return_pct"]) <= 0:
            reasons.append("NO_POSITIVE_TRAIN_AND_VALIDATION_RETURN")
        if max(D(train["max_drawdown_pct"]), D(validation["max_drawdown_pct"])) > D(
            policy["maximum_drawdown_pct"]
        ):
            reasons.append("EXCESSIVE_DRAWDOWN")
        if reasons:
            rejected[name] = reasons
        else:
            accepted.append(name)
    accepted.sort(
        key=lambda n: (
            -D(results[n]["validation"]["metrics"]["net_return_pct"]),
            -D(results[n]["train"]["metrics"]["net_return_pct"]),
            n,
        )
    )
    return {
        "selected": accepted[0] if accepted else "A_baseline",
        "candidate_supported": bool(accepted),
        "rejections": rejected,
        "basis": "taker train/validation only; no final outcome used",
    }


async def selection():
    m = manifest()
    results = {}
    for name, variant in m["plan"]["variants"].items():
        results[name] = {}
        for period in ("train", "validation"):
            results[name][period] = await run_window(m, name, variant, period, "taker")
    value = select(results, m["plan"]["selection"])
    value.update(
        plan_id=m["plan_id"],
        core_version=m["core_version"],
        frozen_at=datetime.now(timezone.utc).isoformat(),
        selection_inputs_id=stable_id(results),
    )
    write(ROOT / "selection.json", value)
    print(json.dumps(value))


async def sensitivity():
    m = manifest()
    results = []
    for name, variant in m["plan"]["variants"].items():
        for scenario in ("maker_fee_bound", "adverse"):
            results.append(await run_window(m, name, variant, "validation", scenario))
    for name, variant in m["plan"]["parameter_sensitivity"].items():
        results.append(await run_window(m, name, variant, "validation", "taker"))
    # Fixed-rule walk-forward windows are descriptive; no hyperparameter updates.
    for period in ("walk_1", "walk_2"):
        for name, variant in m["plan"]["variants"].items():
            results.append(await run_window(m, name, variant, period, "taker"))
    write(ROOT / "sensitivity.json", results)


async def final():
    m = manifest()
    chosen = read(ROOT / "selection.json")
    if chosen["plan_id"] != m["plan_id"] or chosen["core_version"] != m["core_version"]:
        raise ValueError("Selection identity mismatch")
    if (ROOT / "final-opened.json").exists():
        raise ValueError("Final holdout already opened; no repeated test selection")
    write(
        ROOT / "final-opened.json",
        {"selection_id": stable_id(chosen), "opened_at": datetime.now(timezone.utc).isoformat()},
    )
    names = sorted({"A_baseline", chosen["selected"]})
    results = []
    for name in names:
        results.append(await run_window(m, name, m["plan"]["variants"][name], "final", "taker"))
    write(
        ROOT / "final.json",
        {"selection": chosen, "results": results, "live_enabled": False, "exchange_mutations": 0},
    )


async def diagnose():
    m = manifest()
    raw = read(m["plan"]["baseline_input"])
    report = read(m["plan"]["baseline_report"])
    data, risk, _, _ = market_input(raw)
    research = data.research
    signals = []
    for row in report["decisions"]:
        signal = row["signal"]
        if signal["action"] != "BUY":
            continue
        now = dt(signal["as_of"])
        snap = await data.snapshot(signal["symbol"], now)
        features = FeatureEngine(research).compute(snap.candles)
        liquidity = liquidity_features(snap.liquidity, risk.slippage_fraction)
        market = snap.market
        price = rounded(liquidity.ask * (1 + risk.slippage_fraction), market.price_tick, up=True)
        stop = rounded(price - research.stop_atr * features.atr, market.price_tick)
        target = rounded(price + research.target_atr * features.atr, market.price_tick)
        cases = {}
        for name, fee in (
            ("original_research", market.taker_fee_rate),
            ("observed_taker", D(m["market"]["taker_fee"])),
            ("observed_maker_fee_bound", D(m["market"]["maker_fee"])),
        ):
            with localcontext(Context(prec=34)):
                slip = risk.slippage_fraction
                reward = target - price
                loss = price - stop
                entry_fee, target_fee, stop_fee = price * fee, target * fee, stop * fee
                entry_slip, target_slip, stop_slip = price * slip, target * slip, stop * slip
                net = reward - entry_fee - target_fee - entry_slip - target_slip
                planned = loss + entry_fee + stop_fee + entry_slip + stop_slip
                category = (
                    "A_NON_POSITIVE_NET_REWARD"
                    if net <= 0
                    else (
                        "B_POSITIVE_REWARD_INSUFFICIENT_RR"
                        if net / planned < risk.min_net_reward_risk
                        else "PASSES_COST_GEOMETRY"
                    )
                )
                cases[name] = {
                    "fee_per_side": str(fee),
                    "entry_fee": str(entry_fee),
                    "target_exit_fee": str(target_fee),
                    "stop_exit_fee": str(stop_fee),
                    "extra_entry_slippage_allowance": str(entry_slip),
                    "extra_target_exit_slippage_allowance": str(target_slip),
                    "extra_stop_exit_slippage_allowance": str(stop_slip),
                    "net_projected_reward": str(net),
                    "net_planned_risk": str(planned),
                    "net_reward_risk": str(net / planned),
                    "category": category,
                }
        signals.append(
            {
                "timestamp": signal["as_of"],
                "symbol": signal["symbol"],
                "unit": "TMN per one BTC; not an approved order quantity",
                "entry_reference_price": str(price),
                "atr": str(features.atr),
                "stop_price": str(stop),
                "target_price": str(target),
                "gross_reward": str(target - price),
                "gross_loss": str(price - stop),
                "stop_distance": str(price - stop),
                "atr_fraction": str(features.atr / price),
                "entry_half_spread": str(liquidity.ask - features.close),
                "full_spread_fraction": str(liquidity.spread),
                "entry_reference_slippage": str(price - liquidity.ask),
                "required_net_reward_risk": str(risk.min_net_reward_risk),
                "reasons": row["risk"]["reasons"],
                "cases": cases,
            }
        )
    if len(signals) != 8:
        raise ValueError("Baseline differs from expected eight BUY; investigate before research")
    result = {
        "signals": signals,
        "source_report_sha256": digest(m["plan"]["baseline_report"]),
        "classification": {
            name: dict(Counter(s["cases"][name]["category"] for s in signals))
            for name in signals[0]["cases"]
        },
        "note": "Reproduces risk cost allowance exactly, not guaranteed realized fees. "
        "Spread/entry slippage already affect reference; extra allowance is explicit.",
    }
    write(ROOT / "eight-buy-diagnosis.json", result)
    flat = [
        {**{k: v for k, v in s.items() if k != "cases"}, "case": name, **case}
        for s in signals
        for name, case in s["cases"].items()
    ]
    with (ROOT / "eight-buy-diagnosis.csv").open("x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]))
        writer.writeheader()
        writer.writerows(flat)
    print(json.dumps(result["classification"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command", choices=["metadata", "prepare", "diagnose", "select", "sensitivity", "final"]
    )
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    else:
        with localcontext(Context(prec=34)):
            asyncio.run(
                {
                    "metadata": metadata,
                    "diagnose": diagnose,
                    "select": selection,
                    "sensitivity": sensitivity,
                    "final": final,
                }[args.command]()
            )


if __name__ == "__main__":
    main()
