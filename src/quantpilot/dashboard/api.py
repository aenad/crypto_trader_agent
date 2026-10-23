"""Read-only FastAPI application; no legacy router, .env loader or exchange capability."""

import os
import sqlite3
import zlib
from pathlib import Path
from typing import Annotated, Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi import Path as ApiPath

from .domain import DashboardView
from .report import competition_markdown, metrics_csv
from .repository import ReportRepository, UnknownRun

RunID = Annotated[str, ApiPath(pattern=r"^[a-z0-9][a-z0-9-]{0,63}$")]


def create_app(root: Path | None = None) -> FastAPI:
    repo = ReportRepository(
        root or Path(os.environ.get("QUANTPILOT_DASHBOARD_ROOT", "data/dashboard"))
    )
    application = FastAPI(title="Wallex QuantPilot · read-only dashboard", version="phase8-v1")

    @application.middleware("http")
    async def safe_headers(request: Request, call_next: Any) -> Response:
        response: Response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    def load(identity: str) -> DashboardView:
        try:
            return repo.get(identity)
        except UnknownRun:
            raise HTTPException(404, "RUN_NOT_FOUND") from None
        except (
            ValueError,
            OSError,
            KeyError,
            TypeError,
            ArithmeticError,
            AttributeError,
            IndexError,
            sqlite3.Error,
            zlib.error,
        ):
            raise HTTPException(409, "ARTIFACT_UNAVAILABLE_OR_INVALID") from None

    @application.get("/api/dashboard/health")
    def health() -> dict[str, object]:
        return {
            "status": "OK",
            "service": "READ_ONLY_DASHBOARD",
            "exchange_connected": False,
            "exchange_mutations": "UNAVAILABLE",
            "live_activation": "UNAVAILABLE",
        }

    @application.get("/api/dashboard/runs")
    def runs() -> list[dict[str, str]]:
        try:
            return [{"id": "demo", "title": "Competition rehearsal", "kind": "DEMO"}] + [
                {"id": e.id, "title": e.title, "kind": e.kind} for e in repo.entries()
            ]
        except (ValueError, OSError, KeyError, TypeError):
            raise HTTPException(409, "CATALOG_UNAVAILABLE_OR_INVALID") from None

    @application.get("/api/dashboard/runs/{run_id}", response_model=DashboardView)
    def view(run_id: RunID) -> DashboardView:
        return load(run_id)

    @application.get("/api/dashboard/reports/{run_id}.json", response_model=DashboardView)
    def report_json(run_id: RunID, response: Response) -> DashboardView:
        response.headers["Content-Disposition"] = f'attachment; filename="{run_id}-report.json"'
        return load(run_id)

    @application.get("/api/dashboard/reports/{run_id}.md")
    def report_markdown(run_id: RunID) -> Response:
        return Response(
            competition_markdown(load(run_id)),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{run_id}-report.md"'},
        )

    @application.get("/api/dashboard/reports/{run_id}.csv")
    def report_csv(run_id: RunID) -> Response:
        return Response(
            metrics_csv(load(run_id)),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{run_id}-metrics.csv"'},
        )

    return application


app = create_app()
