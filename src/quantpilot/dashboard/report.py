"""Judge-facing exports preserve source labels, missing values and evidence boundaries."""

import csv
import html
import io

from .domain import DashboardView


def text(value: object) -> str:
    return html.escape(str(value)).replace("|", "\\|").replace("`", "'").replace("\n", " ")


def competition_markdown(view: DashboardView) -> str:
    m, source = view.metrics, view.source
    lines = [
        "# Wallex QuantPilot — Competition Evaluation",
        "",
        f"**{text(source.label)}**",
        "",
        f"Run: {text(source.title)} · Mode: {source.kind}",
        f"Data as of: {source.as_of.isoformat() if source.as_of else 'NOT RECORDED'}",
        f"Content ID: `{source.content_id}`",
        "",
        "Final status: **PROVISIONAL / NOT CERTIFIED**. "
        "No terminal liquidation certification is imported.",
        "",
        "## Account performance (TMN = Toman)",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for name in type(m).model_fields:
        value = getattr(m, name)
        lines.append(f"| {name} | {value if value is not None else 'NOT AVAILABLE'} |")
    lines.extend(
        [
            "",
            "## Activity by Tehran calendar day",
            "",
            "Coverage is observed activity, not proof of three complete trading days.",
            "",
            "| Day | Equity change TMN | Decisions | Fills |",
            "|---|---:|---:|---:|",
        ]
    )
    lines.extend(f"| {d.day} | {d.pnl_tmn} | {d.decisions} | {d.fills} |" for d in view.daily)
    lines.extend(
        [
            "",
            "## Execution reliability",
            "",
            f"Displayed orders: {len(view.orders)}; unknown outcomes: "
            f"{sum(o.state == 'UNKNOWN' for o in view.orders)}; "
            f"displayed rejections: {len(view.rejections)}.",
            "Counts may be display-capped; canceled/unknown orders "
            "are not claimed as successful trades.",
            "Order API latency is unavailable unless recorded. No inferred exchange uptime.",
            "",
            "## Strategy explanation",
            "",
            text(view.strategy),
            "",
            "## AI contribution",
            "",
            text(view.ai_contribution),
            "",
            "| Variant | Return % | Drawdown % | Trades | Fees TMN |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    lines.extend(
        f"| {text(c.variant)} | {c.net_return_pct} | {c.max_drawdown_pct} "
        f"| {c.trades} | {c.fees_tmn} |"
        for c in view.comparison
    )
    lines.extend(
        [
            "",
            "## Risk management",
            "",
            text(view.risk_policy),
            "",
            "## Reproducibility, backtesting and shadow results",
            "",
        ]
    )
    lines.extend(
        f"- {text(e.name)}: **{text(e.status)}** — {text(e.detail)}" for e in view.evidence
    )
    lines.extend(["", "## System health (observed evidence only)", ""])
    lines.extend(f"- {text(e.name)}: {text(e.status)} — {text(e.detail)}" for e in view.health)
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {text(limitation)}" for limitation in view.limitations)
    return "\n".join(lines) + "\n"


def metrics_csv(view: DashboardView) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["source_id", "mode", "simulated", "metric", "value"])
    for key in type(view.metrics).model_fields:
        value = getattr(view.metrics, key)
        writer.writerow(
            [
                view.source.id,
                view.source.kind,
                str(view.source.simulated),
                key,
                "NOT_AVAILABLE" if value is None else str(value),
            ]
        )
    return output.getvalue()
