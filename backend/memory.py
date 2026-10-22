"""Persistent audit history and explicit agent notes; never store credentials here."""
import json
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AgentMemory:
    def __init__(self, path: str):
        self.path = Path(path)

    @contextmanager
    def connection(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=10)) as db, db:
            db.row_factory = sqlite3.Row
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL, kind TEXT NOT NULL,
                symbol TEXT, payload TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS notes (
                key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS recorded_runs (
                run_id TEXT PRIMARY KEY, event_id INTEGER NOT NULL)""")
            yield db

    def append_once(self, run_id: str, kind: str, payload: dict[str, Any], symbol: str | None = None):
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute("SELECT event_id FROM recorded_runs WHERE run_id=?", (run_id,)).fetchone()
            if existing:
                return existing["event_id"]
            cursor = db.execute("INSERT INTO events(created_at,kind,symbol,payload) VALUES(?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), kind, symbol, encoded))
            db.execute("INSERT INTO recorded_runs(run_id,event_id) VALUES(?,?)", (run_id, cursor.lastrowid))
            return cursor.lastrowid

    def append(self, kind: str, payload: dict[str, Any], symbol: str | None = None) -> int:
        encoded = json.dumps(payload, ensure_ascii=False, allow_nan=False)
        with self.connection() as db:
            cursor = db.execute(
                "INSERT INTO events(created_at,kind,symbol,payload) VALUES(?,?,?,?)",
                (datetime.now(timezone.utc).isoformat(), kind, symbol, encoded),
            )
            return cursor.lastrowid

    def history(self, kind: str | None = None, symbol: str | None = None, limit: int = 50):
        conditions, params = [], []
        for name, value in (("kind", kind), ("symbol", symbol)):
            if value is not None:
                conditions.append(f"{name} = ?")
                params.append(value)
        where = " WHERE " + " AND ".join(conditions) if conditions else ""
        with self.connection() as db:
            rows = db.execute(
                f"SELECT * FROM events{where} ORDER BY id DESC LIMIT ?",
                [*params, max(1, min(limit, 200))],
            ).fetchall()
        return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]

    def set_note(self, key: str, value: str):
        with self.connection() as db:
            db.execute(
                "INSERT INTO notes(key,value,updated_at) VALUES(?,?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, value, datetime.now(timezone.utc).isoformat()),
            )

    def notes(self):
        with self.connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM notes ORDER BY key")]

    def context(self):
        return {"notes": self.notes(), "recent_decisions": self.history("decision", limit=10)}
