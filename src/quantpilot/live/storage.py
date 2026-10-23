"""Single-writer execution journal. Commit-before-send prevents blind resubmission."""

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from quantpilot.config import stable_id
from quantpilot.models import PortfolioState

from .domain import Blocked, OrderRecord


class LiveStore:
    def __init__(self, path: Path, config_id: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.kill_path = path.with_suffix(path.suffix + ".kill")
        self._lease = path.with_suffix(path.suffix + ".lock").open("a+b")
        try:
            if os.name == "nt":
                import msvcrt

                self._lease.seek(0)
                if not self._lease.read(1):
                    self._lease.write(b"0")
                    self._lease.flush()
                self._lease.seek(0)
                msvcrt.locking(self._lease.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self._lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)  # type: ignore[attr-defined]
        except OSError:
            self._lease.close()
            raise Blocked("EXECUTION_WRITER_ALREADY_RUNNING") from None
        self.db = sqlite3.connect(path)
        tables = {
            r[0] for r in self.db.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        if any(not name.startswith("live_") for name in tables):
            self.close()
            raise Blocked("DEDICATED_EXECUTION_DATABASE_REQUIRED")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS live_orders(id TEXT PRIMARY KEY, body TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS live_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS live_audit(
                seq INTEGER PRIMARY KEY, previous TEXT NOT NULL, digest TEXT NOT NULL,
                body TEXT NOT NULL);
        """)
        existing = self.get("config")
        if existing is not None and existing != config_id:
            self.close()
            raise Blocked("EXECUTION_CONFIG_CHANGED")
        with self.db:
            self.set("config", config_id)
        try:
            self.verify()
        except Exception:
            self.close()
            raise

    def close(self) -> None:
        self.db.close()
        self._lease.close()  # OS releases the process lock on crash as well.

    def get(self, key: str) -> str | None:
        row = self.db.execute("SELECT value FROM live_meta WHERE key=?", (key,)).fetchone()
        return None if row is None else str(row[0])

    def set(self, key: str, value: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO live_meta VALUES(?,?)", (key, value))

    def orders(self) -> tuple[OrderRecord, ...]:
        return tuple(
            OrderRecord.model_validate_json(row[0])
            for row in self.db.execute("SELECT body FROM live_orders ORDER BY id")
        )

    def order(self, identity: str) -> OrderRecord | None:
        row = self.db.execute("SELECT body FROM live_orders WHERE id=?", (identity,)).fetchone()
        return None if row is None else OrderRecord.model_validate_json(row[0])

    def portfolio(self) -> PortfolioState | None:
        raw = self.get("portfolio")
        return None if raw is None else PortfolioState.model_validate_json(raw)

    def audit(self, event: str, evidence: dict[str, Any]) -> None:
        # Callers supply only structured local evidence, never HTTP responses/errors/headers.
        body = json.dumps({"event": event, "evidence": evidence}, sort_keys=True)
        previous = self.db.execute(
            "SELECT digest FROM live_audit ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        parent = "0" * 64 if previous is None else previous[0]
        digest = stable_id([parent, body])
        self.db.execute(
            "INSERT INTO live_audit(previous,digest,body) VALUES(?,?,?)", (parent, digest, body)
        )

    def verify(self) -> None:
        previous = "0" * 64
        for parent, digest, body in self.db.execute(
            "SELECT previous,digest,body FROM live_audit ORDER BY seq"
        ):
            if parent != previous or stable_id([parent, body]) != digest:
                raise Blocked("EXECUTION_AUDIT_CORRUPT")
            previous = digest

    def save(self, record: OrderRecord, portfolio: PortfolioState | None = None) -> None:
        with self.db:
            self.db.execute(
                "INSERT OR REPLACE INTO live_orders VALUES(?,?)",
                (record.intent.client_id, record.model_dump_json()),
            )
            if portfolio is not None:
                self.set("portfolio", portfolio.model_dump_json())
            self.audit("ORDER_TRANSITION", record.model_dump(mode="json"))

    def latch(self, reason: str, *, kill: bool = False) -> None:
        with self.db:
            self.set("kill" if kill else "suspended", reason)
            self.audit("KILL" if kill else "SUSPEND", {"reason": reason})
