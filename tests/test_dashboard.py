import asyncio
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from test_shadow import setup_context

from quantpilot.dashboard.api import create_app
from quantpilot.dashboard.repository import ReportRepository
from quantpilot.shadow.ai import ShadowAI
from quantpilot.shadow.engine import ShadowEngine
from quantpilot.shadow.feed import WallClock
from quantpilot.shadow.service import ShadowSession, export_activity
from quantpilot.shadow.storage import ShadowStore
from quantpilot.trading.config import ResearchParameters, RiskParameters

D = Decimal
NOW = datetime(2026, 10, 23, tzinfo=timezone.utc)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def backtest(root):
    report = {
        "metrics": {
            "initial_capital_tmn": "10000",
            "final_equity_tmn": "1",
            "net_return_pct": "999",
            "realized_pnl_tmn": "800",
            "total_fees_tmn": "20",
        },
        "manifest": {
            "run_id": "fixture-run",
            "assumptions": ["Conservative synthetic fills"],
            "configuration": {
                "approved": ["BTC/TMN", "ETH/TMN"],
                "research": ResearchParameters().model_dump(mode="json"),
                "risk": RiskParameters().model_dump(mode="json"),
            },
        },
        "equity_curve": [
            {"at": f"2026-10-{20 + i}T10:00:00Z", "equity_tmn": str(v)}
            for i, v in enumerate([10000, 12000, 9000])
        ]
        + [{"at": "2026-10-22T14:00:00Z", "equity_tmn": "11000"}],
        "decisions": [
            {
                "signal": {
                    "symbol": "BTC/TMN",
                    "as_of": "2026-10-20T10:00:00Z",
                    "action": "BUY",
                    "reasons": ["BREAKOUT"],
                },
                "risk": {"allowed": False, "reasons": ["LIQUIDITY_LIMIT"]},
            }
        ],
        "orders": [],
        "ledger": [],
        "trades": [{"pnl_tmn": "1000"}, {"pnl_tmn": "-200"}],
        "api_key": "FAKE-SECRET-NEVER-PROJECT",
        "raw_llm_response": "PRIVATE-NARRATIVE",
    }
    write(root / "run/report.json", report)
    write(
        root / "catalog.json",
        {
            "runs": [
                {
                    "id": "baseline",
                    "title": "Recorded baseline",
                    "kind": "BACKTEST",
                    "path": "run/report.json",
                }
            ]
        },
    )
    return report


def test_demo_and_health_are_explicitly_offline(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        demo = client.get("/api/dashboard/runs/demo").json()
        assert demo["source"]["simulated"] is True and demo["source"]["kind"] == "DEMO"
        assert "SIMULATED" in demo["source"]["label"]
        assert demo["metrics"]["initial_capital_tmn"] == "5000000"
        assert all(e["status"] == "ILLUSTRATIVE" for e in demo["evidence"])
        health = client.get("/api/dashboard/health").json()
        assert health["exchange_connected"] is False and health["live_activation"] == "UNAVAILABLE"


def test_hand_calculated_metrics_not_untrusted_summary(tmp_path):
    backtest(tmp_path)
    view = ReportRepository(tmp_path).get("baseline", NOW)
    assert view.metrics.equity_tmn == D(11000)
    assert view.metrics.net_return_pct == D(10)
    assert view.metrics.max_drawdown_pct == D(25)
    assert view.metrics.win_rate_pct == D(50)
    assert [d.pnl_tmn for d in view.daily] == [D(0), D(2000), D(-1000)]
    assert sum(d.pnl_tmn for d in view.daily) == D(1000)
    assert view.markets[1].status == "NOT_OBSERVED"
    assert view.rejections[0].reasons == ("LIQUIDITY_LIMIT",)
    assert "300s" in view.strategy and "0.500%" in view.risk_policy


def test_exports_preserve_labels_decimals_and_strip_private_fields(tmp_path):
    backtest(tmp_path)
    with TestClient(create_app(tmp_path)) as client:
        for path in (
            "/api/dashboard/runs/baseline",
            "/api/dashboard/reports/baseline.json",
            "/api/dashboard/reports/baseline.md",
            "/api/dashboard/reports/baseline.csv",
        ):
            response = client.get(path)
            assert response.status_code == 200
            assert "FAKE-SECRET" not in response.text and "PRIVATE-NARRATIVE" not in response.text
            assert response.headers["cache-control"] == "no-store"
        report = client.get("/api/dashboard/reports/baseline.md").text
        assert "SIMULATED" in report and "NOT CERTIFIED" in report
        assert "Activity by Tehran calendar day" in report
        csv = client.get("/api/dashboard/reports/baseline.csv").text
        assert "BACKTEST,True,net_return_pct,10" in csv
        runs = client.get("/api/dashboard/runs").json()
        assert "path" not in runs[1]


@pytest.mark.parametrize(
    "fault", ["missing", "bad_json", "nan", "unordered", "future", "secret_path"]
)
def test_bad_artifact_fails_closed_without_demo_fallback(tmp_path, fault):
    raw = backtest(tmp_path)
    if fault == "missing":
        (tmp_path / "run/report.json").unlink()
    elif fault == "bad_json":
        (tmp_path / "run/report.json").write_text("broken")
    elif fault == "secret_path":
        write(
            tmp_path / "catalog.json",
            {
                "runs": [
                    {"id": "baseline", "title": "Wrong file", "kind": "BACKTEST", "path": "../.env"}
                ]
            },
        )
    else:
        if fault == "nan":
            raw["metrics"]["realized_pnl_tmn"] = "NaN"
        elif fault == "future":
            raw["equity_curve"][-1]["at"] = "2099-01-01T00:00:00Z"
        else:
            raw["equity_curve"].reverse()
        write(tmp_path / "run/report.json", raw)
    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/api/dashboard/runs/baseline")
        assert response.status_code == 409
        assert "ARTIFACT_UNAVAILABLE" in response.text
        assert "5000000" not in response.text


def test_no_mutation_or_live_activation_routes(tmp_path):
    with TestClient(create_app(tmp_path)) as client:
        for path in ("/api/dashboard/runs/demo", "/api/dashboard/health"):
            assert client.post(path, json={"action": "BUY"}).status_code == 405
        assert client.post("/api/orders", json={"amount": 100}).status_code == 404
        assert client.get("/api/dashboard/runs/unknown").status_code == 404
        assert client.get("/api/dashboard/reports/bad%0D%0Aname.json").status_code == 422


def test_shadow_export_and_active_database_project_same_virtual_results(tmp_path):
    async def setup():
        cfg, frame = setup_context()
        store = ShadowStore(tmp_path / "session.sqlite")
        store.claim("mock-runner", frame.as_of)
        session = ShadowSession(
            store, ShadowEngine(cfg, ShadowAI(cfg, tmp_path / "responses", WallClock()))
        )
        await session.process(frame)
        with store.frozen() as frozen:
            export_activity(frozen, tmp_path / "export")
        return frame, store

    frame, store = asyncio.run(setup())
    write(
        tmp_path / "catalog.json",
        {
            "runs": [
                {
                    "id": "stream",
                    "title": "Current virtual state",
                    "kind": "SHADOW",
                    "path": "session.sqlite",
                },
                {"id": "snapshot", "title": "Virtual export", "kind": "SHADOW", "path": "export"},
            ]
        },
    )
    repo = ReportRepository(tmp_path)
    before = (tmp_path / "session.sqlite").stat().st_mtime_ns
    live = repo.get("stream", frame.as_of)
    exported = repo.get("snapshot", frame.as_of)
    assert live.metrics == exported.metrics and live.orders == exported.orders
    assert live.source.simulated is True and live.source.stale is False
    assert any(h.name == "Shadow runner" and h.status == "RUNNING" for h in live.health)
    assert any(h.name == "Frame processing" for h in live.health)
    assert (tmp_path / "session.sqlite").stat().st_mtime_ns == before
    stale = repo.get("stream", frame.as_of + timedelta(minutes=5))
    assert stale.source.stale and all(m.status == "STALE_RECORDED" for m in stale.markets)
    store.release()


def test_live_export_never_infers_missing_financial_metrics(tmp_path):
    audit = {
        "event": "RECONCILED",
        "evidence": {"as_of": "2026-10-22T12:00:00Z", "equity_tmn": "5001000"},
    }
    (tmp_path / "execution.jsonl").write_text(json.dumps(audit) + "\n")
    write(
        tmp_path / "catalog.json",
        {
            "runs": [
                {
                    "id": "actual",
                    "title": "Operator export",
                    "kind": "LIVE",
                    "path": "execution.jsonl",
                }
            ]
        },
    )
    view = ReportRepository(tmp_path).get("actual", NOW)
    assert view.source.simulated is False
    assert "Not independently exchange-verified" in view.source.label
    assert view.metrics.initial_capital_tmn is None and view.metrics.net_return_pct is None
    assert view.metrics.realized_pnl_tmn is None and view.metrics.trade_count is None


def test_replay_and_ai_comparison_are_reported_evidence_not_live_promotion(tmp_path):
    backtest(tmp_path)
    catalog = json.loads((tmp_path / "catalog.json").read_text())
    catalog["runs"][0].update(replay="replay.json", comparison="comparison.json")
    write(tmp_path / "catalog.json", catalog)
    write(tmp_path / "replay.json", {"status": "MATCH", "frames": 3})
    write(
        tmp_path / "comparison.json",
        {
            "schema": "hybrid-ablation-v1",
            "shared_inputs": "same window",
            "dataset_id": "fixture",
            "variants": {
                "A_QUANT": {
                    "metrics": {
                        "net_return_pct": "1.2",
                        "max_drawdown_pct": ".4",
                        "trade_count": 2,
                        "total_fees_tmn": "20",
                    }
                }
            },
        },
    )
    view = ReportRepository(tmp_path).get("baseline", NOW)
    assert view.comparison[0].net_return_pct == D("1.2")
    assert any(e.status == "REPORTED_MATCH" for e in view.evidence)
    assert any(e.status == "RESEARCH_ONLY" for e in view.evidence)


def test_active_shadow_checkpoint_corruption_is_not_presented_as_valid(tmp_path):
    async def setup():
        cfg, frame = setup_context()
        store = ShadowStore(tmp_path / "session.sqlite")
        store.claim("mock", frame.as_of)
        ShadowSession(store, ShadowEngine(cfg, ShadowAI(cfg, tmp_path / "r", WallClock())))
        store.release()

    asyncio.run(setup())
    with sqlite3.connect(tmp_path / "session.sqlite") as db:
        db.execute("UPDATE qp_shadow_checkpoint SET digest='broken'")
    write(
        tmp_path / "catalog.json",
        {"runs": [{"id": "bad", "title": "Bad", "kind": "SHADOW", "path": "session.sqlite"}]},
    )
    with TestClient(create_app(tmp_path)) as client:
        assert client.get("/api/dashboard/runs/bad").status_code == 409


def test_model_and_prompt_versions_require_a_matching_recorded_trace(tmp_path):
    raw = backtest(tmp_path)
    raw["decisions"][0]["ai"] = {
        "candidate": {
            "prediction": {"probability": ".67", "model_version": "frozen-fixture"},
            "analyst": {"assessment": "VETO"},
            "verdict": "REJECT",
            "analyst_trace_id": "trace-1",
        }
    }
    write(tmp_path / "run/report.json", raw)
    catalog = json.loads((tmp_path / "catalog.json").read_text())
    catalog["runs"][0]["analyst_traces"] = "traces.json"
    write(tmp_path / "catalog.json", catalog)
    write(
        tmp_path / "traces.json",
        [
            {
                "trace_id": "trace-1",
                "prompt_version": "recorded-prompt-v1",
                "model_id": "recorded-analyst",
                "request": "PRIVATE-CONTEXT",
            }
        ],
    )
    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/api/dashboard/runs/baseline")
        row = response.json()["ai"][0]
        assert row["score"] == "0.67" and row["assessment"] == "VETO"
        assert row["prompt_version"] == "recorded-prompt-v1"
        assert row["analyst_model_version"] == "recorded-analyst"
        assert "PRIVATE-CONTEXT" not in response.text


def test_corrupt_sqlite_file_is_a_safe_unavailable_response(tmp_path):
    (tmp_path / "wrong.sqlite").write_bytes(b"not a database")
    write(
        tmp_path / "catalog.json",
        {
            "runs": [
                {"id": "bad", "title": "Bad database", "kind": "SHADOW", "path": "wrong.sqlite"}
            ]
        },
    )
    with TestClient(create_app(tmp_path)) as client:
        response = client.get("/api/dashboard/runs/bad")
        assert response.status_code == 409 and "database" not in response.text


def test_report_identifier_covers_decision_changes(tmp_path):
    raw = backtest(tmp_path)
    repo = ReportRepository(tmp_path)
    first = repo.get("baseline", NOW)
    raw["decisions"][0]["signal"]["reasons"] = ["DIFFERENT_EVIDENCE"]
    write(tmp_path / "run/report.json", raw)
    second = repo.get("baseline", NOW)
    assert first.metrics == second.metrics
    assert first.source.content_id != second.source.content_id


def test_offline_core_rehearsal_and_cli_report_are_simulated(tmp_path, monkeypatch, capsys):
    from quantpilot.dashboard.cli import main as generate
    from quantpilot.dashboard.offline import main as rehearse

    monkeypatch.setattr("sys.argv", ["offline", "--root", str(tmp_path)])
    rehearse()
    assert "SIMULATED" in capsys.readouterr().out
    view = ReportRepository(tmp_path).get("offline-shadow")
    assert view.source.simulated and "Simulated-market" in view.source.label
    monkeypatch.setattr(
        "sys.argv",
        [
            "report",
            "--root",
            str(tmp_path),
            "--run",
            "offline-shadow",
            "--output",
            str(tmp_path / "judges"),
        ],
    )
    generate()
    capsys.readouterr()
    result = json.loads((tmp_path / "judges/competition.json").read_text())
    assert result["source"]["simulated"] is True
    assert (tmp_path / "judges/competition.md").exists()
    assert (tmp_path / "judges/competition.csv").exists()
    with pytest.raises(FileExistsError):
        generate()
