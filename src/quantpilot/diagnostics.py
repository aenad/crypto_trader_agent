"""Read-only trading decision counters from existing reports and frozen journals."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from quantpilot.ai.dataset import market_input
from quantpilot.config import stable_id
from quantpilot.shadow.storage import ShadowStore

MODE_NAMES = {
    "QUANT_ONLY": "QUANT_ONLY",
    "QUANT_ML": "QUANT_WITH_ML",
    "QUANT_ML_LLM": "QUANT_WITH_ML_AND_LLM",
}
LOCATIONS = {
    "strategy": "src/quantpilot/trading/strategy.py:MomentumBreakout.evaluate",
    "features": "src/quantpilot/trading/features.py:FeatureEngine.compute",
    "regime": "src/quantpilot/trading/strategy.py:RegimeDetector.classify",
    "risk": "src/quantpilot/trading/risk.py:DeterministicRiskEngine._check",
    "spot_guard": "src/quantpilot/spot.py:validate_spot_order",
    "ai": "src/quantpilot/ai/fusion.py:HybridEvaluator.recommend",
    "shadow_dispatch": "src/quantpilot/shadow/engine.py:ShadowEngine._apply",
    "shadow_execution": "src/quantpilot/shadow/execution.py:ShadowExecutionProvider",
    "accounting": "src/quantpilot/backtest/ledger.py:PortfolioLedger.apply_fill",
}


def reason(value: object) -> str:
    text = str(value)
    return text if re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}", text) else "NON_CODE_REASON_OMITTED"


def summarize(decisions: list[dict[str, Any]], ai_mode: str) -> dict[str, Any]:
    counts = Counter(
        {
            k: 0
            for k in (
                "strategy_evaluations",
                "buy_candidates",
                "sell_candidates",
                "hold_decisions",
                "ai_approvals",
                "ai_rejections",
                "ai_abstentions",
                "ai_skipped",
                "risk_approvals",
                "risk_rejections",
                "candidate_risk_rejections",
            )
        }
    )
    reasons: dict[str, Counter[str]] = {
        k: Counter() for k in ("strategy", "risk", "ai", "dispatch")
    }
    traces: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions):
        signal, risk = decision["signal"], decision["risk"]
        action = signal["action"]
        counts["strategy_evaluations"] += 1
        counts[
            {"BUY": "buy_candidates", "SELL": "sell_candidates", "HOLD": "hold_decisions"}[action]
        ] += 1
        reasons["strategy"].update(reason(r) for r in signal.get("reasons", ()))
        risk_allowed = risk["allowed"] is True
        counts["risk_approvals" if risk_allowed else "risk_rejections"] += 1
        if not risk_allowed:
            reasons["risk"].update(reason(r) for r in risk.get("reasons", ()))
            if action != "HOLD":
                counts["candidate_risk_rejections"] += 1
        ai = decision.get("ai")
        analysis = ai.get("analysis") if isinstance(ai, dict) else decision.get("analysis")
        if analysis is None:
            counts["ai_skipped"] += 1
            ai_result = (
                "AI_DISABLED_QUANT_ONLY"
                if ai_mode == "QUANT_ONLY"
                else "AI_NOT_REQUIRED_FOR_EXIT_OR_HOLD"
                if action != "BUY"
                else "AI_RESULT_NOT_RECORDED"
            )
            reasons["ai"][ai_result] += 1
        else:
            verdict = analysis["verdict"]
            counts[
                {"ACCEPT": "ai_approvals", "REJECT": "ai_rejections", "ABSTAIN": "ai_abstentions"}[
                    verdict
                ]
            ] += 1
            ai_result = verdict
            if verdict != "ACCEPT":
                reasons["ai"].update(reason(r) for r in analysis.get("reasons", ()))
        outcome = decision.get("outcome")
        if outcome is not None and outcome != "ACCEPTED":
            reasons["dispatch"][reason(outcome)] += 1
        if action != "HOLD" or index == 0:
            if len(traces) < 20:
                traces.append(
                    {
                        "decision_ref": decision.get("decision_id", stable_id(decision)),
                        "as_of": signal["as_of"],
                        "symbol": signal["symbol"],
                        "action": action,
                        "snapshot_id": signal.get("snapshot_id"),
                        "strategy_reasons": [reason(r) for r in signal["reasons"]],
                        "ai_result": ai_result,
                        "risk_allowed": risk_allowed,
                        "risk_reasons": [reason(r) for r in risk.get("reasons", ())],
                        "risk_quantity": risk.get("quantity"),
                        "regime": dict(signal.get("evidence", ())).get("regime"),
                        "feature_input": {
                            k: v
                            for k, v in signal.get("evidence", ())
                            if k
                            in {
                                "entry.atr",
                                "entry.rsi",
                                "entry.relative_volume",
                                "entry.prior_high",
                            }
                        },
                        "position_sizing": (
                            "COMPLETED"
                            if risk_allowed
                            else "NOT_REACHED"
                            if set(risk.get("reasons", ()))
                            & {"FEES_ERASE_REWARD", "NO_ENTRY_SIGNAL"}
                            else "CALCULATED_BELOW_MINIMUM"
                            if "BELOW_MINIMUM_SIZE_OR_LIQUIDITY" in risk.get("reasons", ())
                            else "NOT_DETERMINABLE"
                        ),
                        "spot_guard": "PASSED" if risk_allowed else "NOT_PROVEN_REACHED",
                        "outcome": outcome,
                        "source_functions": LOCATIONS,
                    }
                )
    return {
        "counts": dict(counts),
        "reasons": {k: dict(v) for k, v in reasons.items()},
        "representative_decisions": traces,
    }


def attach_orders(
    report: dict[str, Any], orders: dict[str, Any], fills: list[dict[str, Any]]
) -> None:
    for trace in report["representative_decisions"]:
        order = orders.get(trace["decision_ref"])
        trace["execution"] = (
            {"status": "NOT_RECORDED"}
            if order is None
            else {
                "status": order["state"],
                "fill_count": sum(f["client_id"] == trace["decision_ref"] for f in fills),
            }
        )


def shadow_report(path: Path) -> dict[str, Any]:
    store = ShadowStore(path, create=False)
    with store.frozen() as snapshot:
        snapshot.verify()
        manifest = snapshot.metadata()["manifest"]
        mode = manifest["config"]["ai_mode"]
        records = list(snapshot.records())
        decisions = [d for _, _, out, _, _ in records for d in out["decisions"]]
        report = summarize(decisions, mode)
        _, state = snapshot.checkpoint()
        orders = state["execution"]["orders"]
        fills = {f["fill_id"] for o in orders.values() for f in o["executions"]}
        attach_orders(report, orders, [f for o in orders.values() for f in o["executions"]])
        pending = snapshot.pending()
        ops = list(snapshot.iter_operations())
        errors = [e for e in ops if e.get("kind") == "EXECUTION_ERROR"]
        report["counts"].update(
            market_events_received=sum(len(raw["snapshots"]) for _, raw, _, _, _ in records)
            + sum(len(f.snapshots) for _, f in pending),
            valid_market_events=sum(
                sum(s["symbol"] not in out["stale_symbols"] for s in raw["snapshots"])
                for _, raw, out, _, _ in records
            ),
            frames_committed=len(records),
            pending_frames=len(pending),
            orders_created=len(orders),
            orders_submitted_to_simulated_execution=sum(
                o["state"] not in ("CREATED", "REJECTED", "UNKNOWN") for o in orders.values()
            ),
            simulated_fills=len(fills),
            execution_errors_observed=len(errors),
            processing_errors_observed=sum(e.get("kind") == "FRAME_PROCESSING_FAILED" for e in ops),
            feed_interruptions_observed=sum(e.get("kind") == "FEED_UNAVAILABLE" for e in ops),
        )
        report["reasons"]["execution"] = dict(
            Counter(reason(e.get("reason_code", "SIMULATED_EXECUTION_FAILED")) for e in errors)
        )
        report.update(
            source="SHADOW",
            ai_mode=mode,
            ai_mode_label=MODE_NAMES[mode],
            journal_integrity="VERIFIED",
            config_id=manifest["config_id"],
            virtual_realized_pnl_tmn=state["ledger"]["realized"],
            accounting_fill_count=len(state["ledger"]["seen"]),
            source_version_matches_current=_shadow_source_matches(manifest),
            notes=[
                "Events are recorded market snapshots, not API requests or unique candles.",
                "Pending frames are received but not counted as validated.",
                "Error counts cover recorded telemetry; old unlogged failures are unknown.",
                "Reason categories overlap. Risk rejection counts include HOLD/NO_ENTRY_SIGNAL.",
            ],
        )
        return report


def _shadow_source_matches(manifest: dict[str, Any]) -> bool:
    from quantpilot.shadow.ai import core_version

    return bool(manifest["core_version"] == core_version())


def historical_report(path: Path, input_path: Path | None) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    configuration = raw["manifest"]["configuration"]
    ai_mode = "QUANT_ONLY" if "entry_evaluator_id" not in configuration else "RECORDED_EVALUATOR"
    result = summarize(raw["decisions"], ai_mode)
    orders = raw["orders"]
    fills = {r["fill_id"] for r in raw["ledger"] if r.get("kind") == "FILL"}
    attach_orders(
        result,
        {o["intent"]["decision_id"]: o for o in orders},
        [f for f in raw["ledger"] if f.get("kind") == "FILL"],
    )
    result["counts"].update(
        market_events_received=None,
        valid_market_events=None,
        orders_created=len(orders),
        orders_submitted_to_simulated_execution=sum(
            o["state"] not in ("CREATED", "REJECTED", "UNKNOWN") for o in orders
        ),
        simulated_fills=len(fills),
        execution_errors_observed=0,
    )
    result.update(
        source="BACKTEST",
        ai_mode=ai_mode,
        metrics=raw["metrics"],
        notes=[
            "Counts are recorded strategy decisions, not repeated internal recomputations.",
            "Completed replay has no uncaught execution error; order rejection is separate.",
            "OHLC proxy liquidity is an assumption, not a historical order book.",
        ],
    )
    if input_path is not None:
        source = json.loads(input_path.read_text(encoding="utf-8"), parse_float=str)
        data, _, _, fx = market_input(source)
        inputs = {
            "candles": {
                p: [c.model_dump(mode="json") for c in rows]
                for p, rows in sorted(data.candles.items())
            },
            "markets": {p: m.model_dump(mode="json") for p, m in sorted(data.markets.items())},
            "quotes": {
                p: [b.model_dump(mode="json") for b in rows]
                for p, rows in sorted(data.quotes.items())
            },
            "fx": [v.model_dump(mode="json") for v in fx],
            "fx_market": data.fx_market.model_dump(mode="json") if data.fx_market else None,
        }
        if stable_id(inputs) != raw["manifest"]["input_id"]:
            raise ValueError("Historical input/report identity mismatch")
        n = sum(len(rows) for rows in data.candles.values())
        result["counts"].update(market_events_received=n, valid_market_events=n)
        result["input_identity"] = "VERIFIED"
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shadow-db", type=Path)
    parser.add_argument("--backtest-report", type=Path)
    parser.add_argument("--historical-input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.shadow_db is None and args.backtest_report is None:
        parser.error("Provide --shadow-db and/or --backtest-report")
    result: dict[str, Any] = {"live_enabled": False, "exchange_mutations": 0, "sources": []}
    if args.shadow_db is not None:
        result["sources"].append(shadow_report(args.shadow_db))
    if args.backtest_report is not None:
        result["sources"].append(historical_report(args.backtest_report, args.historical_input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "exported": str(args.output),
                "sources": len(result["sources"]),
                "exchange_mutations": 0,
                "live_enabled": False,
            }
        )
    )


if __name__ == "__main__":
    main()
