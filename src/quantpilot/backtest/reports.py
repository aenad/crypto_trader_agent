import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

from quantpilot.config import stable_id

if TYPE_CHECKING:
    from .replay import HistoricalReplay

D = Decimal


def build_report(run: "HistoricalReplay") -> dict[str, Any]:
    trades, curve = run.ledger.trades, run.equity
    pnls = [D(t["pnl_tmn"]) for t in trades]
    wins, losses = sum((x for x in pnls if x > 0), D(0)), -sum((x for x in pnls if x < 0), D(0))
    duration = D(
        str(
            (
                datetime.fromisoformat(curve[-1]["at"]) - datetime.fromisoformat(curve[0]["at"])
            ).total_seconds()
        )
    )
    exposure_time = D(0)
    for previous, current in zip(curve, curve[1:]):
        seconds = D(
            str(
                (
                    datetime.fromisoformat(current["at"]) - datetime.fromisoformat(previous["at"])
                ).total_seconds()
            )
        )
        equity = D(previous["equity_tmn"])
        exposure_time += seconds * (D(previous["exposure_tmn"]) / equity if equity else D(0))
    configuration = {
        "simulation": run.data.simulation.model_dump(mode="json"),
        "research": run.data.research.model_dump(mode="json"),
        "risk": run.risk_parameters.model_dump(mode="json"),
        "approved": run.approved,
    }
    if run.decision_start is not None:
        configuration["decision_start"] = run.decision_start.isoformat()
    if run.evaluation_id is not None:
        configuration["entry_evaluator_id"] = run.evaluation_id
    inputs = {
        "candles": {
            p: [c.model_dump(mode="json") for c in rows]
            for p, rows in sorted(run.data.candles.items())
        },
        "markets": {p: m.model_dump(mode="json") for p, m in sorted(run.data.markets.items())},
        "quotes": {
            p: [b.model_dump(mode="json") for b in rows]
            for p, rows in sorted(run.data.quotes.items())
        },
        "fx": [x.model_dump(mode="json") for x in run.fx],
        "fx_market": run.data.fx_market.model_dump(mode="json") if run.data.fx_market else None,
    }
    manifest = {
        "config_id": stable_id(configuration),
        "input_id": stable_id(inputs),
        "configuration": configuration,
        "engine_version": "spot-backtest-v2",
        "assumptions": [
            "Completed candles published at event_time; download receipt ignored",
            "OHLC proxy spread/depth is a scenario assumption, not reconstructed order book",
            "Market orders: next bar open with adverse spread/slippage; prior-volume cap",
            "Limits: strict penetration, no price improvement; close-time volume cap",
            "Protective exits evaluated by unchanged Phase 3 close-bar policy, executed next open",
            "Terminal auction: final close discounted by spread/slippage/haircut; volume cap",
            "Spot inventory average-cost basis; quote FX gains separately realized in TMN",
            "Initial USDT funding is an explicit rate/fee research assumption",
            "Terminal USDT sale requires explicit enabled FX route and fresh recorded bids",
            "New entries stop before the configured terminal liquidation window",
            "Static market permissions/fees/constraints over input interval; no queue model",
        ],
    }
    manifest["run_id"] = stable_id(
        {
            "config": manifest["config_id"],
            "input": manifest["input_id"],
            "engine": manifest["engine_version"],
        }
    )
    return {
        "manifest": manifest,
        "metrics": {
            "initial_capital_tmn": str(run.ledger.initial),
            "final_toman_balance_tmn": str(run.ledger.holding("TMN").quantity),
            "fully_settled_tmn": all(
                asset == "TMN" or h.quantity == 0 for asset, h in run.ledger.holdings.items()
            ),
            "final_equity_tmn": curve[-1]["equity_tmn"],
            "net_return_pct": str((D(curve[-1]["equity_tmn"]) / run.ledger.initial - 1) * 100),
            "realized_pnl_tmn": str(run.ledger.realized),
            "unrealized_pnl_tmn": curve[-1]["unrealized_tmn"],
            "max_drawdown_pct": str(max(D(x["drawdown"]) for x in curve) * 100),
            "win_rate": str(D(sum(x > 0 for x in pnls)) / len(pnls)) if pnls else None,
            "profit_factor": str(wins / losses) if losses else None,
            "profit_factor_status": "DEFINED" if losses else "NO_REALIZED_LOSSES",
            "trade_count": len(trades),
            "fill_count": len(run.ledger.seen),
            "average_holding_seconds": str(
                sum((D(t["holding_seconds"]) for t in trades), D(0)) / len(trades)
            )
            if trades
            else None,
            "total_fees_tmn": str(run.ledger.fees),
            "time_weighted_exposure": str(exposure_time / duration) if duration else "0",
            "max_exposure_fraction": str(
                max(
                    (
                        D(row["exposure_tmn"]) / D(row["equity_tmn"])
                        if D(row["equity_tmn"])
                        else D(0)
                    )
                    for row in curve
                )
            ),
        },
        "residual_positions": run.residuals,
        "remaining_holdings": {
            asset: str(h.quantity) for asset, h in sorted(run.ledger.holdings.items())
            if asset != "TMN" and h.quantity > 0
        },
        "equity_curve": curve,
        "trades": trades,
        "ledger": run.ledger.events,
        "decisions": run.decisions,
        "orders": [
            {
                "intent": o.intent.model_dump(mode="json"),
                "state": o.state.value,
                "submitted_at": o.submitted.isoformat(),
                "remaining": str(o.remaining),
            }
            for o in run.execution.orders.values()
        ],
    }


def export_report(report: dict[str, Any], directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "report.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    for name in ("equity_curve", "trades", "ledger", "decisions", "orders"):
        rows = report[name]
        keys = sorted({key for row in rows for key in row}) or ["empty"]
        with (directory / f"{name}.csv").open("w", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=keys)
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        key: json.dumps(value, sort_keys=True)
                        if isinstance(value, (dict, list))
                        else value
                        for key, value in row.items()
                    }
                )
    with (directory / "metrics.csv").open("w", newline="", encoding="utf-8") as output:
        metric_writer = csv.writer(output)
        metric_writer.writerow(["metric", "value"])
        metric_writer.writerows(report["metrics"].items())
