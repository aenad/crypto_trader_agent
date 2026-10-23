"""SQLite inbox + atomic virtual checkpoint/decision commits; telemetry is separate."""

import json
import sqlite3
import tempfile
import zlib
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from types import TracebackType
from typing import Any, Literal

from quantpilot.config import stable_id

from .domain import ShadowFrame


class ClosingConnection(sqlite3.Connection):
    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        try:
            return super().__exit__(kind, error, traceback)
        finally:
            self.close()


def pack(value: dict[str, Any]) -> bytes:
    return zlib.compress(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def unpack(value: bytes) -> dict[str, Any]:
    result: dict[str, Any] = json.loads(zlib.decompress(value))
    return result


class ShadowStore:
    def __init__(self, path: Path, create: bool = True):
        self.path = path
        self.owner: str | None = None
        if not create:
            if not path.exists():
                raise FileNotFoundError("Shadow session does not exist")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            if any(not t.startswith("qp_shadow_") for t in tables):
                raise ValueError("Use a dedicated shadow database; unrelated tables found")
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
              CREATE TABLE IF NOT EXISTS qp_shadow_meta(id INTEGER PRIMARY KEY, data BLOB NOT NULL);
              CREATE TABLE IF NOT EXISTS qp_shadow_control(id INTEGER PRIMARY KEY, owner TEXT,
                heartbeat TEXT, lease_until TEXT, stop INTEGER NOT NULL DEFAULT 0);
              INSERT OR IGNORE INTO qp_shadow_control(id) VALUES(1);
              CREATE TABLE IF NOT EXISTS qp_shadow_frames(
                seq INTEGER PRIMARY KEY, frame_id TEXT UNIQUE,
                input BLOB NOT NULL, output BLOB, state BLOB, chain TEXT);
              CREATE TABLE IF NOT EXISTS qp_shadow_checkpoint(id INTEGER PRIMARY KEY, seq INTEGER,
                data BLOB NOT NULL, digest TEXT NOT NULL);
              CREATE TABLE IF NOT EXISTS qp_shadow_ops(seq INTEGER PRIMARY KEY, data TEXT NOT NULL);
            """)

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10, factory=ClosingConnection)

    def claim(self, owner: str, now: datetime) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT owner,lease_until FROM qp_shadow_control WHERE id=1"
            ).fetchone()
            if row[0] and row[1] and datetime.fromisoformat(row[1]) > now:
                raise RuntimeError("Shadow writer lease is already held")
            db.execute(
                "UPDATE qp_shadow_control SET owner=?,heartbeat=?,lease_until=?,stop=0 WHERE id=1",
                (owner, now.isoformat(), (now + timedelta(seconds=60)).isoformat()),
            )
        self.owner = owner

    def _owned(self, db: sqlite3.Connection) -> None:
        owner = db.execute("SELECT owner FROM qp_shadow_control WHERE id=1").fetchone()[0]
        if not self.owner or owner != self.owner:
            raise RuntimeError("Shadow writer lease lost")

    def heartbeat(self, now: datetime) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db)
            db.execute(
                "UPDATE qp_shadow_control SET heartbeat=?,lease_until=? WHERE id=1",
                (now.isoformat(), (now + timedelta(seconds=60)).isoformat()),
            )

    def release(self) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db)
            db.execute("UPDATE qp_shadow_control SET owner=NULL,lease_until=NULL WHERE id=1")
        self.owner = None

    def request_stop(self) -> None:
        with self.connect() as db:
            db.execute("UPDATE qp_shadow_control SET stop=1 WHERE id=1")

    def control(self) -> dict[str, Any]:
        with self.connect() as db:
            row = db.execute(
                "SELECT owner,heartbeat,lease_until,stop FROM qp_shadow_control WHERE id=1"
            ).fetchone()
        return dict(zip(("owner", "heartbeat", "lease_until", "stop"), row, strict=True))

    def initialize(self, manifest: dict[str, Any], initial: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db)
            row = db.execute("SELECT data FROM qp_shadow_meta WHERE id=1").fetchone()
            if row:
                if unpack(row[0])["manifest"] != manifest:
                    raise ValueError("Shadow configuration/version mismatch")
            else:
                db.execute(
                    "INSERT INTO qp_shadow_meta VALUES(1,?)",
                    (pack({"manifest": manifest, "initial": initial}),),
                )
                db.execute(
                    "INSERT INTO qp_shadow_checkpoint VALUES(1,0,?,?)",
                    (pack(initial), stable_id(initial)),
                )

    def metadata(self) -> dict[str, Any]:
        with self.connect() as db:
            row = db.execute("SELECT data FROM qp_shadow_meta WHERE id=1").fetchone()
        if not row:
            raise ValueError("Shadow session is not initialized")
        return unpack(row[0])

    def checkpoint(self) -> tuple[int, dict[str, Any]]:
        with self.connect() as db:
            row = db.execute(
                "SELECT seq,data,digest FROM qp_shadow_checkpoint WHERE id=1"
            ).fetchone()
        state = unpack(row[1])
        if stable_id(state) != row[2]:
            raise ValueError("Shadow checkpoint checksum mismatch")
        return int(row[0]), state

    def enqueue(self, frame: ShadowFrame) -> int:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db)
            existing = db.execute(
                "SELECT seq FROM qp_shadow_frames WHERE frame_id=?", (frame.frame_id,)
            ).fetchone()
            if existing:
                return int(existing[0])
            if db.execute("SELECT 1 FROM qp_shadow_frames WHERE output IS NULL").fetchone():
                raise RuntimeError("Recover pending frame before accepting another")
            cursor = db.execute(
                "INSERT INTO qp_shadow_frames(frame_id,input) VALUES(?,?)",
                (frame.frame_id, pack(frame.model_dump(mode="json"))),
            )
            assert cursor.lastrowid is not None
            return cursor.lastrowid

    def pending(self) -> list[tuple[int, ShadowFrame]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT seq,input FROM qp_shadow_frames WHERE output IS NULL ORDER BY seq"
            ).fetchall()
        return [(r[0], ShadowFrame.model_validate(unpack(r[1]))) for r in rows]

    def commit(
        self, seq: int, output: dict[str, Any], state: dict[str, Any], expected_seq: int
    ) -> None:
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._owned(db)
            current = db.execute("SELECT seq FROM qp_shadow_checkpoint WHERE id=1").fetchone()[0]
            if current != expected_seq or seq <= current:
                raise ValueError("Stale shadow commit")
            row = db.execute(
                "SELECT frame_id,output FROM qp_shadow_frames WHERE seq=?", (seq,)
            ).fetchone()
            if not row or row[1] is not None:
                raise ValueError("Frame already committed or missing")
            previous = db.execute(
                "SELECT chain FROM qp_shadow_frames "
                "WHERE output IS NOT NULL ORDER BY seq DESC LIMIT 1"
            ).fetchone()
            prior = previous[0] if previous else stable_id(self.metadata()["initial"])
            chain = stable_id(
                {
                    "previous": prior,
                    "frame": row[0],
                    "output": stable_id(output),
                    "state": stable_id(state),
                }
            )
            db.execute(
                "UPDATE qp_shadow_frames SET output=?,state=?,chain=? WHERE seq=?",
                (pack(output), pack(state), chain, seq),
            )
            db.execute(
                "UPDATE qp_shadow_checkpoint SET seq=?,data=?,digest=? WHERE id=1",
                (seq, pack(state), stable_id(state)),
            )

    def records(self) -> Iterator[tuple[int, dict[str, Any], dict[str, Any], dict[str, Any], str]]:
        db = self.connect()
        try:
            for r in db.execute(
                "SELECT seq,input,output,state,chain FROM qp_shadow_frames "
                "WHERE output IS NOT NULL ORDER BY seq"
            ):
                yield r[0], unpack(r[1]), unpack(r[2]), unpack(r[3]), r[4]
        finally:
            db.close()

    def verify(self) -> None:
        prior = stable_id(self.metadata()["initial"])
        last = 0
        state = self.metadata()["initial"]
        for seq, frame, output, post, chain in self.records():
            expected = stable_id(
                {
                    "previous": prior,
                    "frame": ShadowFrame.model_validate(frame).frame_id,
                    "output": stable_id(output),
                    "state": stable_id(post),
                }
            )
            if expected != chain:
                raise ValueError("Shadow journal hash-chain mismatch")
            prior = chain
            last = seq
            state = post
        checkpoint_seq, checkpoint = self.checkpoint()
        if checkpoint_seq != last or checkpoint != state:
            raise ValueError("Journal/checkpoint divergence")

    def operational(self, event: dict[str, Any]) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT INTO qp_shadow_ops(data) VALUES(?)", (json.dumps(event, sort_keys=True),)
            )

    def operations(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as db:
            rows = db.execute(
                "SELECT data FROM qp_shadow_ops ORDER BY seq DESC LIMIT ?", (limit,)
            ).fetchall()
        return [json.loads(r[0]) for r in reversed(rows)]

    def iter_operations(self) -> Iterator[dict[str, Any]]:
        db = self.connect()
        try:
            for row in db.execute("SELECT data FROM qp_shadow_ops ORDER BY seq"):
                yield json.loads(row[0])
        finally:
            db.close()

    @contextmanager
    def frozen(self) -> Iterator["ShadowStore"]:
        with tempfile.TemporaryDirectory(prefix="quantpilot-shadow-snapshot-") as directory:
            target = Path(directory) / "session.sqlite"
            source = self.connect()
            destination = sqlite3.connect(target)
            try:
                source.backup(destination)
            finally:
                source.close()
                destination.close()
            yield ShadowStore(target, create=False)
