"""Uses an isolated temporary PostgreSQL cluster if local binaries are installed."""

import asyncio
import os
import shutil
import socket
import subprocess
from pathlib import Path

import pytest
from test_marketdata import NOW, PAIR, POLICY

from quantpilot.marketdata.collect import CandleCollector, Collectors
from quantpilot.marketdata.mock import MockPublic
from quantpilot.marketdata.storage import ParquetStore, PostgresCatalog


def test_postgres_catalog_and_parquet(tmp_path):
    import psycopg
    import pyarrow.parquet as pq

    if os.environ.get("QUANTPILOT_RUN_POSTGRES_TEST") != "1":
        pytest.skip("Opt in with QUANTPILOT_RUN_POSTGRES_TEST=1 for isolated local server test")
    initdb = shutil.which("initdb")
    pg_ctl = shutil.which("pg_ctl")
    if not initdb or not pg_ctl:
        pytest.skip("Local PostgreSQL binaries unavailable; no existing server touched")
    cluster = tmp_path / "isolated-cluster"
    subprocess.run(
        [
            initdb,
            "-D",
            str(cluster),
            "-A",
            "trust",
            "-U",
            "quantpilot",
            "--no-locale",
            "--encoding=UTF8",
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    subprocess.run(
        [
            pg_ctl,
            "-D",
            str(cluster),
            "-l",
            str(tmp_path / "postgres.log"),
            "-o",
            f"-p {port} -h 127.0.0.1",
            "-w",
            "start",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=90,
    )
    try:
        dsn = f"host=127.0.0.1 port={port} user=quantpilot dbname=postgres"
        store = ParquetStore(tmp_path / "parquet", PostgresCatalog(dsn))
        snapshot = asyncio.run(
            CandleCollector(Collectors(MockPublic(NOW), POLICY), bars=3).snapshot(PAIR, NOW)
        )
        manifest = store.save("candles", PAIR, list(snapshot.candles), {"source": "test"})
        store.save("candles", PAIR, list(snapshot.candles), {"source": "test"})
        with psycopg.connect(dsn) as db:
            row = db.execute("SELECT manifest FROM quantpilot_datasets").fetchall()
            assert len(row) == 1 and row[0][0]["sha256"] == manifest["sha256"]
        assert pq.read_table(Path(manifest["path"])).num_rows == 3
    finally:
        subprocess.run(
            [pg_ctl, "-D", str(cluster), "-m", "fast", "-w", "stop"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=90,
        )
