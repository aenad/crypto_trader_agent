"""Bounded, allowlisted artifact projections; never open .env or exchange credentials."""

import json
from datetime import datetime, timezone
from decimal import Context, Decimal, localcontext
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from quantpilot.config import stable_id

from .demo import demo
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
    RunEntry,
    Source,
)
from .shadow_reader import read_shadow

D = Decimal
LIMIT = 64 * 1024 * 1024


class InvalidReport(ValueError):
    pass


class UnknownRun(LookupError):
    pass


def at(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InvalidReport("TIMESTAMP_TIMEZONE_REQUIRED")
    return parsed


def num(value: Any) -> Decimal | None:
    if value is None:
        return None
    if isinstance(value, (float, bool)):
        raise InvalidReport("EXACT_DECIMAL_REQUIRED")
    parsed = D(value)
    if not parsed.is_finite():
        raise InvalidReport("NONFINITE_METRIC")
    return parsed


def fill_row(row: dict[str, Any]) -> FillRow:
    return FillRow(
        id=row["fill_id"],
        order_id=row["client_id"],
        symbol=row["symbol"],
        side=row["side"],
        quantity=row["base_quantity"],
        price=row["price"]["amount"],
        fee=row["fee"]["amount"],
        fee_currency=row["fee"]["currency"],
        at=at(row["executed_at"]),
    )


def order_row(row: dict[str, Any]) -> OrderRow:
    intent = row["intent"]
    quantity = D(intent["base_quantity"])
    filled = (
        num(row.get("executed_quantity"))
        if "executed_quantity" in row
        else quantity - D(row["remaining"])
        if "remaining" in row
        else None
    )
    return OrderRow(
        id=intent["client_id"],
        symbol=intent["symbol"],
        side=intent["side"],
        state=row["state"],
        quantity=quantity,
        filled_quantity=filled,
        at=at(row.get("submitted_at", row.get("submitted", row.get("updated_at")))),
    )


def project_decisions(
    decisions: list[dict[str, Any]], approved: list[str], traces: list[dict[str, Any]] | None = None
) -> tuple[tuple[MarketRow, ...], tuple[AIRow, ...], tuple[Rejection, ...]]:
    latest: dict[str, MarketRow] = {}
    ai: list[AIRow] = []
    rejected = []
    linked = {t["trace_id"]: t for t in traces or []}
    if len(linked) != len(traces or []):
        raise InvalidReport("DUPLICATE_ANALYST_TRACES")
    for row in decisions:
        signal, risk = row["signal"], row["risk"]
        symbol, when = signal["symbol"], at(signal["as_of"])
        latest[symbol] = MarketRow(
            symbol=symbol,
            status="RECORDED",
            action=signal["action"],
            as_of=when,
            reasons=tuple(signal.get("reasons", ())),
        )
        if signal["action"] != "HOLD" and (not risk["allowed"] or row.get("outcome") == "REJECTED"):
            rejected.append(Rejection(symbol=symbol, at=when, reasons=tuple(risk["reasons"])))
        candidate = (row.get("ai") or {}).get("candidate")
        analysis = row.get("analysis") or (row.get("ai") or {}).get("analysis")
        if candidate:
            prediction, analyst = candidate.get("prediction"), candidate.get("analyst")
            trace = linked.get(candidate.get("analyst_trace_id"), {})
            ai.append(
                AIRow(
                    symbol=symbol,
                    as_of=when,
                    score=num(prediction["probability"]) if prediction else None,
                    assessment=analyst["assessment"] if analyst else "NOT_RECORDED",
                    fusion=candidate["verdict"],
                    model_version=prediction["model_version"] if prediction else None,
                    # Prompt version is not present in Phase 6 decision exports.
                    prompt_version=trace.get("prompt_version"),
                    analyst_model_version=trace.get("model_id"),
                )
            )
        elif analysis:
            ai.append(
                AIRow(
                    symbol=symbol,
                    as_of=when,
                    fusion=analysis["verdict"],
                    model_version=analysis.get("model_version"),
                )
            )
    for symbol in approved:
        latest.setdefault(symbol, MarketRow(symbol=symbol, status="NOT_OBSERVED", action="UNKNOWN"))
    return tuple(latest[k] for k in sorted(latest)), tuple(ai[-250:]), tuple(rejected[-500:])


def curve_points(rows: list[dict[str, Any]], initial: Decimal | None) -> tuple[EquityPoint, ...]:
    peak = initial
    points: list[EquityPoint] = []
    for row in rows:
        when, value = at(row["at"]), D(row["equity_tmn"])
        if not value.is_finite() or value < 0 or (points and when < points[-1].at):
            raise InvalidReport("INVALID_OR_UNORDERED_EQUITY")
        peak = max(peak or value, value)
        point = EquityPoint(
            at=when, equity_tmn=value, drawdown_pct=(1 - value / peak) * 100 if peak else D(0)
        )
        if points and when == points[-1].at:
            points[-1] = point
        else:
            points.append(point)
    return tuple(points)


def daily_points(
    curve: tuple[EquityPoint, ...],
    decisions: list[dict[str, Any]],
    fills: tuple[FillRow, ...],
    initial: Decimal | None,
) -> tuple[DayRow, ...]:
    if not curve or initial is None:
        return ()
    zone = ZoneInfo("Asia/Tehran")
    closes = {p.at.astimezone(zone).date().isoformat(): p.equity_tmn for p in curve}
    counts: dict[str, int] = {}
    for decision in decisions:
        day = at(decision["signal"]["as_of"]).astimezone(zone).date().isoformat()
        counts[day] = counts.get(day, 0) + 1
    executed: dict[str, int] = {}
    for fill in fills:
        day = fill.at.astimezone(zone).date().isoformat()
        executed[day] = executed.get(day, 0) + 1
    rows = []
    previous = initial
    for day, equity in sorted(closes.items()):
        rows.append(
            DayRow(
                day=day,
                pnl_tmn=equity - previous,
                decisions=counts.get(day, 0),
                fills=executed.get(day, 0),
            )
        )
        previous = equity
    return tuple(rows)


class ReportRepository:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def path(self, relative: str) -> Path:
        result = (self.root / relative).resolve()
        if not result.is_relative_to(self.root) or any(
            p.startswith(".") for p in Path(relative).parts
        ):
            raise InvalidReport("ARTIFACT_PATH_OUTSIDE_CATALOG")
        return result

    def read(self, path: Path) -> Any:
        if not path.resolve().is_relative_to(self.root):
            raise InvalidReport("ARTIFACT_PATH_OUTSIDE_CATALOG")
        if path.suffix not in {".json", ".jsonl"} or path.stat().st_size > LIMIT:
            raise InvalidReport("UNSUPPORTED_OR_OVERSIZED_ARTIFACT")
        raw = path.read_text(encoding="utf-8")
        if path.suffix == ".jsonl":
            return [json.loads(line, parse_float=str) for line in raw.splitlines() if line.strip()]
        return json.loads(raw, parse_float=str)

    def entries(self) -> tuple[RunEntry, ...]:
        path = self.root / "catalog.json"
        if not path.exists():
            return ()
        raw = self.read(path)
        entries = tuple(RunEntry.model_validate(item) for item in raw["runs"])
        if (
            len(entries) > 100
            or len({e.id for e in entries}) != len(entries)
            or any(e.id == "demo" for e in entries)
        ):
            raise InvalidReport("INVALID_CATALOG")
        return entries

    def get(self, identity: str, now: datetime | None = None) -> DashboardView:
        now = now or datetime.now(timezone.utc)
        if identity == "demo":
            return demo(now)
        entry = next((e for e in self.entries() if e.id == identity), None)
        if entry is None:
            raise UnknownRun(identity)
        with localcontext(Context(prec=34)):
            return self._project(entry, now)

    def _project(self, entry: RunEntry, now: datetime) -> DashboardView:
        base = self.path(entry.path)
        limitations = [
            "Read-only recorded artifact; the dashboard does not contact an exchange.",
            "Unknown telemetry and missing metrics are not replaced with zero.",
            "Reported replay results are displayed, not rerun or independently verified here.",
            "Order API latency is unavailable unless explicitly measured by the producer.",
        ]
        orders: tuple[OrderRow, ...] = ()
        fills: tuple[FillRow, ...] = ()
        decisions: list[dict[str, Any]] = []
        approved: list[str] = []
        evidence = []
        health = [
            EvidenceRow(name=n, status="NOT_OBSERVED", detail="No current connection probe")
            for n in ("MCP", "WebSocket", "API errors", "Circuit breakers")
        ]
        metrics_raw: dict[str, Any] = {}
        trades: list[dict[str, Any]] = []
        rows: list[dict[str, Any]] = []
        parameters: dict[str, Any] = {}
        freshness = 60
        reported_stale = False
        fixture_market = False
        if entry.kind == "BACKTEST":
            raw = self.read(base)
            metrics_raw = raw["metrics"]
            rows, decisions, trades = raw["equity_curve"], raw["decisions"], raw["trades"]
            orders = tuple(order_row(o) for o in raw["orders"])
            fills = tuple(fill_row(f) for f in raw["ledger"] if f.get("kind") == "FILL")
            approved = raw["manifest"]["configuration"]["approved"]
            parameters = raw["manifest"]["configuration"]
            evidence.append(
                EvidenceRow(
                    name="Backtest", status="RECORDED", detail=str(raw["manifest"]["run_id"])
                )
            )
            limitations.extend(str(s) for s in raw["manifest"].get("assumptions", ()))
        elif entry.kind == "SHADOW":
            if base.suffix == ".sqlite":
                manifest, state, frames, operations, statuses = read_shadow(base, now)
                health.extend(EvidenceRow.model_validate(s) for s in statuses)
            else:
                manifest = self.read(self.path(entry.path + "/manifest.json"))
                state = self.read(self.path(entry.path + "/portfolio.json"))
                frames = self.read(self.path(entry.path + "/frames.jsonl"))
                op_path = self.path(entry.path + "/operations.jsonl")
                operations = self.read(op_path) if op_path.exists() else []
            events = [o for o in operations if o["kind"] in {"FEED_UNAVAILABLE", "FRAME_COMMITTED"}]
            if events:
                failed = events[-1]["kind"] == "FEED_UNAVAILABLE"
                health.append(
                    EvidenceRow(
                        name="Latest feed operation",
                        status="ERROR" if failed else "RECORDED",
                        detail="FEED_UNAVAILABLE" if failed else "FRAME_COMMITTED",
                    )
                )
            commits = [o for o in operations if o["kind"] == "FRAME_COMMITTED"]
            if commits:
                commit = commits[-1]
                for label, seconds in [
                    ("Frame processing", commit.get("processing_seconds")),
                    ("LLM processing", commit.get("latency", {}).get("llm_seconds")),
                ]:
                    if seconds is not None:
                        health.append(
                            EvidenceRow(
                                name=label,
                                status="RECORDED",
                                detail=f"{D(str(seconds)) * 1000:.2f} ms at last commit",
                            )
                        )
            approved = manifest["config"]["approved"]
            fixture_market = any(
                f.get("simulated_market_data")
                or f.get("frame", {}).get("depth_timestamps") == "FIXTURE"
                for f in frames
            )
            parameters = manifest["config"]
            freshness = int(parameters["freshness_seconds"])
            reported_stale = bool(frames and frames[-1]["result"].get("valuation_stale", False))
            transport = parameters["public_transport"]
            health = [h for h in health if h.name not in {"MCP", "WebSocket"}]
            health.extend(
                [
                    EvidenceRow(
                        name="MCP",
                        status="LAST_READ_OK"
                        if transport == "MCP" and events and events[-1]["kind"] == "FRAME_COMMITTED"
                        else "NOT_USED"
                        if transport != "MCP"
                        else "NOT_OBSERVED",
                        detail="Configured feed: " + transport + "; not a persistent probe",
                    ),
                    EvidenceRow(
                        name="WebSocket", status="NOT_USED", detail="Runner uses REST/MCP polling"
                    ),
                ]
            )
            ledger = state["ledger"]
            health.append(
                EvidenceRow(
                    name="Risk circuit",
                    status="LATCHED" if ledger["halted"] else "RECORDED_CLEAR",
                    detail="Persisted virtual risk state",
                )
            )
            trades = ledger["trades"]
            metrics_raw = {
                "initial_capital_tmn": manifest["config"]["simulation"]["initial_capital_tmn"],
                "realized_pnl_tmn": ledger["realized"],
                "total_fees_tmn": ledger["fees"],
            }
            for frame in frames:
                result = frame["result"]
                rows.append({"at": result["as_of"], "equity_tmn": result["equity_tmn"]})
                decisions.extend(result["decisions"])
            orders = tuple(order_row(o) for o in state["execution"]["orders"].values())
            fills = tuple(fill_row(f) for f in ledger["events"] if f.get("kind") == "FILL")
            evidence.append(
                EvidenceRow(
                    name="Shadow", status="VIRTUAL_ONLY", detail="Exported virtual accounting"
                )
            )
            limitations.append(
                "Public live market data does not make SHADOW portfolio results real trading."
            )
            if fixture_market:
                limitations.append(
                    "SIMULATED MARKET DATA: fixture frames, not live Wallex observations."
                )
        else:
            # Deliberately read an explicit export, not an active execution database or credentials.
            events = self.read(base)
            latest_orders: dict[str, dict[str, Any]] = {}
            for event in events:
                kind, body = event["event"], event["evidence"]
                if kind == "RECONCILED":
                    rows.append({"at": body["as_of"], "equity_tmn": body["equity_tmn"]})
                elif kind == "RISK_DECISION":
                    decisions.append(body)
                elif kind == "ORDER_TRANSITION":
                    latest_orders[body["intent"]["client_id"]] = body
            orders = tuple(order_row(o) for o in latest_orders.values())
            fills = tuple(
                sorted(
                    (fill_row(f) for o in latest_orders.values() for f in o["fills"]),
                    key=lambda f: (f.at, f.id),
                )
            )
            approved = sorted({r["signal"]["symbol"] for r in decisions})
            # Initial capital is absent from Phase 7 exported bootstrap evidence. Do not infer it.
            metrics_raw = {
                "initial_capital_tmn": None,
                "realized_pnl_tmn": None,
                "total_fees_tmn": None,
            }
            evidence.append(
                EvidenceRow(
                    name="Live export",
                    status="OPERATOR_RECORDED",
                    detail="Not exchange-authenticated by the dashboard",
                )
            )
            limitations.extend(
                [
                    "LIVE initial capital, realized PnL and fees lack a complete ledger export.",
                    "LIVE net return is unavailable; never inferred from the first equity sample.",
                ]
            )
        initial = num(metrics_raw.get("initial_capital_tmn"))
        if initial is not None and initial <= 0:
            raise InvalidReport("POSITIVE_INITIAL_CAPITAL_REQUIRED")
        curve = curve_points(rows, initial)
        if curve and curve[-1].at > now:
            raise InvalidReport("FUTURE_RECORDED_EQUITY")
        last = curve[-1].equity_tmn if curve else None
        pnl = [D(t["pnl_tmn"]) for t in trades]
        metrics = Metrics(
            initial_capital_tmn=initial,
            equity_tmn=last,
            realized_pnl_tmn=num(metrics_raw.get("realized_pnl_tmn")),
            net_return_pct=(last / initial - 1) * 100 if last is not None and initial else None,
            max_drawdown_pct=max((p.drawdown_pct for p in curve), default=None),
            win_rate_pct=D(sum(p > 0 for p in pnl)) / len(pnl) * 100 if pnl else None,
            fees_tmn=num(metrics_raw.get("total_fees_tmn")),
            trade_count=len(trades) if entry.kind != "LIVE" else None,
        )
        traces = self.read(self.path(entry.analyst_traces)) if entry.analyst_traces else None
        markets, ai, rejected = project_decisions(decisions, approved, traces)
        comparison = []
        if entry.replay:
            result = self.read(self.path(entry.replay))
            status = result["status"]
            if status not in {"MATCH", "DIVERGED"}:
                raise InvalidReport("UNKNOWN_REPLAY_STATUS")
            evidence.append(
                EvidenceRow(
                    name="Replay",
                    status="REPORTED_" + status,
                    detail=f"{result['frames']} frames; not rerun by dashboard",
                )
            )
        if entry.comparison:
            result = self.read(self.path(entry.comparison))
            if result["schema"] != "hybrid-ablation-v1" or not result["shared_inputs"]:
                raise InvalidReport("INVALID_COMPARISON")
            for name, variant in result["variants"].items():
                m = variant["metrics"]
                comparison.append(
                    ComparisonRow(
                        variant=name,
                        net_return_pct=num(m["net_return_pct"]),
                        max_drawdown_pct=num(m["max_drawdown_pct"]),
                        trades=int(m["trade_count"]),
                        fees_tmn=num(m["total_fees_tmn"]),
                    )
                )
            evidence.append(
                EvidenceRow(
                    name="AI comparison",
                    status="RESEARCH_ONLY",
                    detail="Separate same-input evaluation: " + result["dataset_id"],
                )
            )
            limitations.extend(str(s) for s in result.get("limitations", ()))
            limitations.extend(str(s) for s in result.get("promotion", {}).get("reasons", ()))
        if entry.health:
            telemetry = self.read(self.path(entry.health))
            if telemetry["mode"] != entry.kind:
                raise InvalidReport("TELEMETRY_MODE_MISMATCH")
            health.append(
                EvidenceRow(
                    name="Recorded runner",
                    status=str(telemetry.get("status", "UNKNOWN")),
                    detail="Exported observation, not a current liveness probe",
                )
            )
            if "stale_market_data" in telemetry:
                health.append(
                    EvidenceRow(
                        name="Market freshness",
                        status="STALE" if telemetry["stale_market_data"] else "RECORDED_FRESH",
                        detail="At health export time only",
                    )
                )
        as_of = curve[-1].at if curve else None
        simulated = entry.kind != "LIVE"
        source = Source(
            id=entry.id,
            title=entry.title,
            kind=entry.kind,
            simulated=simulated,
            label={
                "BACKTEST": "SIMULATED · Historical backtest",
                "SHADOW": "VIRTUAL · Simulated-market SHADOW"
                if fixture_market
                else "VIRTUAL · Recorded-market SHADOW",
                "LIVE": "RECORDED LIVE EXPORT · Not independently exchange-verified",
            }[entry.kind],
            as_of=as_of,
            content_id=stable_id(
                {
                    "entry": entry.model_dump(mode="json"),
                    "metrics": metrics.model_dump(mode="json"),
                    "curve": [p.model_dump(mode="json") for p in curve],
                }
            ),
            stale=bool(
                entry.kind != "BACKTEST"
                and (as_of is None or (now - as_of).total_seconds() > freshness or reported_stale)
            ),
        )
        if source.stale:
            markets = tuple(m.model_copy(update={"status": "STALE_RECORDED"}) for m in markets)
        step = max(1, (len(curve) + 1998) // 1999)
        displayed = curve[::step]
        if curve and displayed[-1] != curve[-1]:
            displayed += (curve[-1],)
        detail: dict[str, str] = {}
        if "research" in parameters and "risk" in parameters:
            research, risk = parameters["research"], parameters["risk"]
            detail["strategy"] = (
                f"Momentum Breakout: completed {research['entry_seconds']}s entry / "
                f"{research['trend_seconds']}s trend candles. Prior breakout window "
                "excludes current candle; no leverage or shorting."
            )
            detail["risk_policy"] = (
                f"Risk per trade {D(risk['risk_per_trade']) * 100}%; "
                f"maximum {risk['max_positions']} positions; daily loss "
                f"{D(risk['daily_loss_fraction']) * 100}%; drawdown "
                f"{D(risk['max_drawdown_fraction']) * 100}%. Fees and liquidity checked."
            )
        projected = DashboardView(
            source=source,
            generated_at=now,
            metrics=metrics,
            equity=displayed,
            markets=markets,
            ai=ai,
            orders=orders[-500:],
            fills=fills[-500:],
            rejections=rejected,
            daily=daily_points(curve, decisions, fills, initial),
            comparison=tuple(comparison),
            evidence=tuple(evidence),
            health=tuple(health),
            limitations=tuple(limitations),
            **detail,
        )
        content = projected.model_dump(mode="json", exclude={"generated_at"})
        content["source"].pop("content_id")
        return projected.model_copy(
            update={"source": source.model_copy(update={"content_id": stable_id(content)})}
        )
