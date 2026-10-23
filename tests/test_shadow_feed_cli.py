import asyncio
import json
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

import pytest
from test_shadow import session, setup_context

from quantpilot.backtest.history import HistoricalClock
from quantpilot.shadow.feed import WallexLiveFeed
from quantpilot.trading.config import ResearchParameters


class PublicFixture:
    source = "mock-public"

    def __init__(self, gap=False):
        self.calls = []
        self.gap = gap

    async def request(self, kind, args):
        self.calls.append((kind, args))
        if kind == "markets":
            return {
                "result": {
                    "markets": [
                        {
                            "symbol": "BTCTMN",
                            "base_asset": "BTC",
                            "quote_asset": "TMN",
                            "is_spot": True,
                        }
                    ]
                }
            }
        if kind == "book":
            return {
                "result": {
                    "bid": [{"price": "100", "quantity": "100000"}],
                    "ask": [{"price": "100.1", "quantity": "100000"}],
                }
            }
        if kind == "candles":
            times = list(range(args["from"], args["to"] + 1, 60))
            if self.gap:
                times = times[1:]
            return {
                "s": "ok",
                "t": times,
                "o": ["100"] * len(times),
                "h": ["101"] * len(times),
                "l": ["99"] * len(times),
                "c": ["100"] * len(times),
                "v": ["10"] * len(times),
            }
        raise AssertionError("Nonpublic operation")


def test_live_adapter_normalizes_completed_data_caches_history_and_backfills():
    async def scenario():
        cfg, frame = setup_context()
        cfg = cfg.model_copy(
            update={
                "research": ResearchParameters(
                    ema_fast=3,
                    ema_slow=8,
                    atr_period=3,
                    adx_period=3,
                    rsi_period=3,
                    volume_window=5,
                    breakout_window=5,
                )
            }
        )
        clock = HistoricalClock(frame.as_of)
        source = PublicFixture()
        feed = WallexLiveFeed(source, cfg, clock)
        first = await feed.poll()
        assert first.depth_timestamps == "OBSERVATION"
        snap = first.snapshots[0]
        assert len(snap.candles) >= 24 and len(snap.trend_candles) >= 8
        assert all(c.close_time <= first.as_of for c in snap.candles + snap.trend_candles)
        assert snap.liquidity.as_of == first.as_of
        initial = sum(kind == "candles" for kind, _ in source.calls)
        clock.advance(clock.now() + timedelta(seconds=15))
        await feed.poll()
        assert sum(kind == "candles" for kind, _ in source.calls) == initial
        clock.advance(clock.now() + timedelta(seconds=60))
        await feed.poll()
        assert sum(kind == "candles" for kind, _ in source.calls) == initial + 1
        assert all(
            args.get("resolution") == "1" for kind, args in source.calls if kind == "candles"
        )

    asyncio.run(scenario())


def test_gap_and_missing_markets_fail_instead_of_synthesizing_data():
    async def scenario():
        cfg, frame = setup_context()
        clock = HistoricalClock(frame.as_of)
        with pytest.raises(ValueError):
            await WallexLiveFeed(PublicFixture(gap=True), cfg, clock).poll()

        class Missing(PublicFixture):
            async def request(self, kind, args):
                return {"result": {"markets": []}}

        with pytest.raises(ValueError, match="UNAVAILABLE"):
            await WallexLiveFeed(Missing(), cfg, clock).poll()

    asyncio.run(scenario())


def test_control_export_and_replay_cli_commands(tmp_path):
    cfg, frame = setup_context()
    live = session(tmp_path, cfg)
    asyncio.run(live.process(frame))
    live.store.release()

    def command(name, *extra):
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "quantpilot.shadow.cli",
                name,
                "--db",
                str(live.store.path),
                *map(str, extra),
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr
        return json.loads(result.stdout)

    assert command("portfolio")["virtual_only"] is True
    assert command("health")["status"] == "STOPPED"
    assert (
        command("replay", "--responses", tmp_path / "empty", "--output", tmp_path / "replay.json")[
            "status"
        ]
        == "MATCH"
    )
    assert command("export", "--output", tmp_path / "export")["exported"]
    assert command("stop")["stop_requested"] is True
    assert (tmp_path / "replay.json").exists()
    assert (tmp_path / "export/frames.jsonl").exists()


def test_cli_configuration_errors_do_not_echo_secret_values(tmp_path):
    cfg, frame = setup_context()
    value = cfg.model_dump(mode="json")
    value["api_key"] = "DO_NOT_ECHO_SENTINEL"
    config = tmp_path / "bad.json"
    config.write_text(json.dumps(value), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantpilot.shadow.cli",
            "start",
            "--config",
            str(config),
            "--db",
            str(tmp_path / "unused.sqlite"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "DO_NOT_ECHO_SENTINEL" not in result.stderr + result.stdout
    assert not Path(tmp_path / "unused.sqlite").exists()
