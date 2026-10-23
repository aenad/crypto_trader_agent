"""Summarize completed, pinned research without opening any new experiment."""

import csv
import json
from decimal import Context, Decimal, localcontext

from research.strategy_study import ROOT, digest, manifest, read, write

D = Decimal


def common_row(summary):
    segments = summary["segments"]
    values = [D(pnl) for s in segments for pnl in s["pnl_distribution"]["values_tmn"]]
    positive = sum((p for p in values if p > 0), D(0))
    negative = -sum((p for p in values if p < 0), D(0))
    n = len(values)
    risk = {}
    for s in segments:
        for k, v in s["risk_reasons"].items():
            risk[k] = risk.get(k, 0) + v
    return {
        "mode": "BACKTEST",
        "variant": summary["variant"],
        "scenario": summary["scenario"],
        "period": summary["period"],
        "independent_accounts": len(segments),
        "net_return_pct_sum_not_compounded": summary["metrics"]["net_return_pct"],
        "equal_capital_account_mean_return_pct": str(
            D(summary["metrics"]["net_return_pct"]) / len(segments)
        )
        if segments
        else None,
        "max_segment_drawdown_pct": summary["metrics"]["max_drawdown_pct"],
        "trade_count": n,
        "realized_pnl_tmn_sum": summary["metrics"]["realized_pnl_tmn"],
        "unrealized_pnl_tmn_sum": str(sum(D(s["metrics"]["unrealized_pnl_tmn"]) for s in segments)),
        "fees_tmn_sum": summary["metrics"]["total_fees_tmn"],
        "win_rate": str(D(sum(v > 0 for v in values)) / n) if n else None,
        "profit_factor": str(positive / negative) if negative else None,
        "profit_factor_status": "DEFINED"
        if negative
        else "NO_REALIZED_LOSSES"
        if n
        else "NO_TRADES",
        "average_net_pnl_tmn": str(sum(values) / n) if n else None,
        "average_holding_seconds": str(
            sum(
                D(s["metrics"]["average_holding_seconds"] or "0") * s["metrics"]["trade_count"]
                for s in segments
            )
            / n
        )
        if n
        else None,
        "max_exposure_fraction": str(
            max((D(s["metrics"]["max_exposure_fraction"]) for s in segments), default=D(0))
        ),
        "segment_time_weighted_exposures": [
            s["metrics"]["time_weighted_exposure"] for s in segments
        ],
        "buy_candidates": sum(s["actions"].get("BUY", 0) for s in segments),
        "risk_approved_buy": sum(s["risk_approvals"].get("BUY", 0) for s in segments),
        "risk_reasons": risk,
        "pnl_distribution_tmn": [str(v) for v in sorted(values)],
        "open_holdings": [s["remaining_holdings"] for s in segments],
        "uncertainty": (
            "No significance/robustness claim; inspect trade count and short independent windows"
        ),
    }


def main():
    m = manifest()
    final = read(ROOT / "final.json")
    read(ROOT / "sensitivity.json")  # Require completion, not merely partial outputs.
    rows = [common_row(read(p)) for p in sorted((ROOT / "runs").rglob("summary.json"))]
    old = "data/strategy-research-v1/runs/A_baseline/taker/train/segment-0/report.json"
    new = ROOT / "runs/A_baseline/taker/train/segment-0/report.json"
    equivalence = read(old) == read(new)
    if not equivalence:
        raise ValueError("Prepared provider differs from original historical replay")
    write(
        ROOT / "comparison.json",
        {
            "mode": "BACKTEST",
            "performance_kind": "SIMULATED_ON_OBSERVED_OHLCV",
            "plan_id": m["plan_id"],
            "selection": final["selection"],
            "rows": rows,
            "historical_original_vs_prepared_full_report": "MATCH",
            "summary_source_sha256": digest(__file__),
            "baseline_artifacts_unchanged": True,
            "live_enabled": False,
            "exchange_mutations": 0,
            "maker_scenario": "Conditional fee bound, not simulated maker queue/fill probability",
        },
    )
    with (ROOT / "comparison.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(
            {k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()}
            for row in rows
        )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "selection": final["selection"],
                "historical_cache_equivalence": "MATCH",
            }
        )
    )


if __name__ == "__main__":
    with localcontext(Context(prec=34)):
        main()
