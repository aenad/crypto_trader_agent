"""Atomic Parquet batches plus PostgreSQL metadata; no database secrets in output."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Protocol

from quantpilot.config import stable_id
from quantpilot.models import DomainModel


class Catalog(Protocol):
    def register(self, manifest: dict[str, Any]) -> None: ...


class PostgresCatalog:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def register(self, manifest: dict[str, Any]) -> None:
        import psycopg
        from psycopg.types.json import Jsonb

        with psycopg.connect(self.dsn, connect_timeout=10) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS quantpilot_datasets (
                dataset_id TEXT PRIMARY KEY, kind TEXT NOT NULL, symbol TEXT NOT NULL,
                manifest JSONB NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now())""")
            db.execute(
                """INSERT INTO quantpilot_datasets(dataset_id,kind,symbol,manifest)
                VALUES (%s,%s,%s,%s) ON CONFLICT(dataset_id) DO NOTHING""",
                (manifest["dataset_id"], manifest["kind"], manifest["symbol"], Jsonb(manifest)),
            )


class LocalCatalog:
    """Offline test/demo substitute, not the production metadata database."""

    def __init__(self, root: Path):
        self.root = root

    def register(self, manifest: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        path = self.root / (manifest["dataset_id"] + ".json")
        atomic_bytes(path, json.dumps(manifest, sort_keys=True).encode())


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        name = tmp.name
        tmp.write(content)
        tmp.flush()
        os.fsync(tmp.fileno())
    try:
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class ParquetStore:
    def __init__(self, root: Path, catalog: Catalog):
        self.root, self.catalog = root, catalog

    def save(
        self, kind: str, symbol: str, events: list[DomainModel], provenance: dict[str, Any]
    ) -> dict[str, Any]:
        import pyarrow as pa
        import pyarrow.parquet as pq

        if kind not in ("candles", "book", "trades", "stream") or not events:
            raise ValueError("Nonempty validated event batch required")
        unique: dict[str, str] = {}
        for event in events:
            row = event.model_dump(mode="json")
            if row["symbol"] != symbol:
                raise ValueError("Mixed batch symbols")
            event_id = row["event_id"]
            encoded = json.dumps(row, sort_keys=True, separators=(",", ":"))
            if event_id in unique and unique[event_id] != encoded:
                raise ValueError("Conflicting duplicate event")
            unique[event_id] = encoded
        rows = [
            {"event_id": key, "symbol": symbol, "payload_json": unique[key]}
            for key in sorted(unique)
        ]
        dataset_id = stable_id({"kind": kind, "rows": rows, "provenance": provenance})
        path = self.root / kind / symbol.replace("/", "_") / (dataset_id + ".parquet")
        if not path.exists():
            sink = pa.BufferOutputStream()
            pq.write_table(pa.Table.from_pylist(rows), sink, compression="zstd")
            atomic_bytes(path, sink.getvalue().to_pybytes())
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest = {
            "dataset_id": dataset_id,
            "kind": kind,
            "symbol": symbol,
            "path": str(path.resolve()),
            "rows": len(rows),
            "sha256": digest,
            "schema_version": 1,
            "provenance": provenance,
        }
        self.catalog.register(manifest)
        return manifest
