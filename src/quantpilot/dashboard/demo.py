"""Deterministic illustrative data for UI development only; not a strategy backtest."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from quantpilot.config import stable_id

from .domain import (
    AIRow,
    ComparisonRow,
    DashboardView,
    DayRow,
    EquityPoint,
    EvidenceRow,
    FillRow,
    MarketRow,
    Metrics,
    OrderRow,
    Rejection,
    Source,
)

D = Decimal


def demo(now: datetime) -> DashboardView:
    start = datetime(2026, 10, 20, tzinfo=timezone.utc)
    values = [
        D(5000000),
        D(5020000),
        D(5060000),
        D(5030000),
        D(5090000),
        D(5120000),
        D(5080000),
        D(5130000),
        D(5170000),
        D(5150000),
        D(5190000),
        D(5215000),
    ]
    peak = values[0]
    curve = []
    for i, value in enumerate(values):
        peak = max(peak, value)
        curve.append(
            EquityPoint(
                at=start + timedelta(hours=i * 6),
                equity_tmn=value,
                drawdown_pct=(1 - value / peak) * 100,
            )
        )
    last = curve[-1].at
    return DashboardView(
        source=Source(
            id="demo",
            title="Competition rehearsal",
            kind="DEMO",
            simulated=True,
            label="SIMULATED · UI demonstration only",
            as_of=last,
            content_id=stable_id([str(v) for v in values]),
        ),
        generated_at=now,
        metrics=Metrics(
            initial_capital_tmn=D(5000000),
            equity_tmn=values[-1],
            realized_pnl_tmn=D(184000),
            net_return_pct=D("4.3"),
            max_drawdown_pct=max(p.drawdown_pct for p in curve),
            win_rate_pct=D("62.5"),
            fees_tmn=D(16000),
            trade_count=8,
        ),
        equity=tuple(curve),
        markets=tuple(
            MarketRow(
                symbol=s,
                status="SIMULATED",
                action=a,
                as_of=last,
                reasons=("Illustrative signal, not model inference",),
            )
            for s, a in [("BTC/TMN", "BUY"), ("ETH/TMN", "HOLD"), ("SOL/TMN", "SELL")]
        ),
        ai=(
            AIRow(
                symbol="BTC/TMN",
                as_of=last,
                score=D(".72"),
                assessment="ACCEPT",
                fusion="ACCEPT",
                model_version="demo-lightgbm-v1",
                prompt_version="demo-prompt-v1",
            ),
            AIRow(
                symbol="ETH/TMN",
                as_of=last,
                score=D(".43"),
                assessment="VETO",
                fusion="REJECT",
                model_version="demo-lightgbm-v1",
                prompt_version="demo-prompt-v1",
            ),
        ),
        orders=(
            OrderRow(
                id="demo-buy-01",
                symbol="BTC/TMN",
                side="BUY",
                state="FILLED",
                quantity=D(".0001"),
                filled_quantity=D(".0001"),
                at=last,
                latency_ms=D(148),
            ),
            OrderRow(
                id="demo-exit-02",
                symbol="SOL/TMN",
                side="SELL",
                state="PARTIALLY_FILLED",
                quantity=D(".8"),
                filled_quantity=D(".5"),
                at=last,
                latency_ms=D(206),
            ),
        ),
        fills=(
            FillRow(
                id="demo-fill-01",
                order_id="demo-buy-01",
                symbol="BTC/TMN",
                side="BUY",
                quantity=D(".0001"),
                price=D(8000000000),
                fee=D(800),
                fee_currency="TMN",
                at=last,
            ),
        ),
        rejections=(Rejection(symbol="ETH/TMN", at=last, reasons=("AI_VETO", "WEAK_MOMENTUM")),),
        daily=(
            DayRow(day="2026-10-20", pnl_tmn=D(30000), decisions=24, fills=3),
            DayRow(day="2026-10-21", pnl_tmn=D(100000), decisions=27, fills=4),
            DayRow(day="2026-10-22", pnl_tmn=D(85000), decisions=22, fills=2),
        ),
        comparison=tuple(
            ComparisonRow(
                variant=n, net_return_pct=D(r), max_drawdown_pct=D(d), trades=t, fees_tmn=D(f)
            )
            for n, r, d, t, f in [
                ("Quant only", "2.6", "1.8", 12, "24000"),
                ("Quant + LightGBM", "3.5", "1.2", 10, "19000"),
                ("Quant + LightGBM + LLM", "4.3", ".8", 8, "16000"),
            ]
        ),
        evidence=(
            EvidenceRow(
                name="Backtest",
                status="ILLUSTRATIVE",
                detail="No engine run behind this UI dataset",
            ),
            EvidenceRow(
                name="Replay", status="ILLUSTRATIVE", detail="Not a recorded replay result"
            ),
            EvidenceRow(
                name="AI comparison", status="ILLUSTRATIVE", detail="No measured model benefit"
            ),
        ),
        health=tuple(
            EvidenceRow(name=n, status=s, detail=d)
            for n, s, d in [
                ("Mode", "DEMO", "No exchange connection or trading"),
                ("MCP", "NOT_CONNECTED", "Offline UI dataset"),
                ("WebSocket", "NOT_CONNECTED", "Offline UI dataset"),
                ("API errors", "NOT_OBSERVED", "No live telemetry"),
                ("Circuit breakers", "SIMULATED", "Live execution remains disabled"),
            ]
        ),
        limitations=(
            "SIMULATED UI fixtures: all performance and AI values are illustrative.",
            "Not a backtest, SHADOW session or real trading result.",
            "Demo fills are illustrative examples, not a complete accounting ledger.",
        ),
        ai_contribution="Illustrative comparison only. No causal AI benefit is established.",
    )
