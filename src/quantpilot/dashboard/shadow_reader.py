"""Consistent read-only view of the existing SHADOW schema, without runner imports."""

import json
import re
import sqlite3
import zlib
from datetime import datetime
from pathlib import Path
from typing import Any

from quantpilot.config import stable_id

MAX = 64 * 1024 * 1024


def unpack(blob: bytes) -> dict[str, Any]:
    decoder = zlib.decompressobj()
    raw = decoder.decompress(blob, MAX + 1)
    if len(raw) > MAX or not decoder.eof:
        raise ValueError("OVERSIZED_OR_INVALID_SHADOW_RECORD")
    result: dict[str, Any] = json.loads(raw)
    return result


def read_shadow(
    path: Path, now: datetime
) -> tuple[
    dict[str, Any], dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, str]]
]:
    if path.stat().st_size > MAX * 8:
        raise ValueError("SHADOW_DATABASE_TOO_LARGE")
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2)
    try:
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        metadata = unpack(db.execute("SELECT data FROM qp_shadow_meta WHERE id=1").fetchone()[0])
        seq, blob, digest = db.execute(
            "SELECT seq,data,digest FROM qp_shadow_checkpoint WHERE id=1"
        ).fetchone()
        state = unpack(blob)
        if stable_id(state) != digest:
            raise ValueError("SHADOW_CHECKPOINT_DIGEST_MISMATCH")
        frames, used = [], 0
        for input_blob, packed in db.execute(
            "SELECT input,output FROM qp_shadow_frames "
            "WHERE output IS NOT NULL AND seq<=? ORDER BY seq",
            (seq,),
        ):
            result = unpack(packed)
            projected = {
                key: result[key] for key in ("as_of", "equity_tmn", "decisions", "valuation_stale")
            }
            used += len(json.dumps(projected))
            if used > MAX:
                raise ValueError("SHADOW_HISTORY_TOO_LARGE")
            # pack() uses sorted keys: the provenance marker precedes the large candle payload.
            # This is a display label only, not a substitute for full journal/replay verification.
            prefix = zlib.decompressobj().decompress(input_blob, 1024)
            frames.append(
                {
                    "result": projected,
                    "simulated_market_data": bool(
                        re.search(rb'"depth_timestamps":"FIXTURE"', prefix)
                    ),
                }
            )
        operations = [
            json.loads(r[0], parse_float=str)
            for r in db.execute("SELECT data FROM qp_shadow_ops ORDER BY seq DESC LIMIT 200")
        ][::-1]
        owner, lease, stop = db.execute(
            "SELECT owner,lease_until,stop FROM qp_shadow_control WHERE id=1"
        ).fetchone()
        running = bool(owner and lease and datetime.fromisoformat(lease) > now)
        health = [
            {
                "name": "Shadow runner",
                "status": "STOPPING" if stop and running else "RUNNING" if running else "STOPPED",
                "detail": "Current local writer lease",
            }
        ]
        return metadata["manifest"], state, frames, operations, health
    finally:
        db.close()
