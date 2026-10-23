"""Durable coordinator, graceful controls and replay of original evidence."""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from quantpilot.config import stable_id
from quantpilot.interfaces import Clock

from .ai import ShadowAI, core_version
from .domain import ShadowConfig, ShadowFrame
from .engine import ShadowEngine
from .feed import FrameSource
from .storage import ShadowStore


class ShadowSession:
    def __init__(self, store: ShadowStore, engine: ShadowEngine):
        self.store, self.engine = store, engine
        manifest = {
            "schema": "shadow-v1",
            "config": engine.config.model_dump(mode="json"),
            "config_id": engine.config.config_id,
            "core_version": core_version(),
            "ai": engine.ai.identity(),
            "exchange_mutations": "BLOCKED",
            "account": "VIRTUAL_ONLY",
        }
        store.initialize(manifest, engine.dump())
        store.verify()
        self.seq, state = store.checkpoint()
        engine.restore(state)

    async def process(self, frame: ShadowFrame) -> dict[str, Any] | None:
        seq = self.store.enqueue(frame)
        if seq <= self.seq:
            return None
        start = time.perf_counter()
        self.engine.ai.last_latency = {}
        try:
            result = await self.engine.apply(frame)
            self.store.commit(seq, result, self.engine.dump(), self.seq)
            self.seq = seq
        except BaseException:
            # Resolve a local commit's ambiguous return before continuing. A
            # checkpoint is authoritative if the transaction already committed.
            persisted_seq, persisted = self.store.checkpoint()
            self.engine.restore(persisted)
            self.seq = persisted_seq
            raise
        self.store.operational(
            {
                "kind": "FRAME_COMMITTED",
                "as_of": frame.as_of.isoformat(),
                "processing_seconds": time.perf_counter() - start,
                "latency": self.engine.ai.last_latency,
                "ai_status": "UNAVAILABLE"
                if any(
                    d["ai"] is not None
                    and (
                        d["ai"]["candidate"]["prediction"] is None
                        or (
                            self.engine.config.ai_mode == "QUANT_ML_LLM"
                            and d["ai"]["candidate"]["analyst"] is None
                        )
                    )
                    for d in result["decisions"]
                )
                else "EVALUATED"
                if any(d["ai"] is not None for d in result["decisions"])
                else "NOT_EVALUATED",
                "stale_symbols": result["stale_symbols"],
                "frame_id": frame.frame_id,
            }
        )
        return result

    async def recover(self) -> None:
        harness = self.engine.ai.harness
        previous = harness.replay_only if harness else True
        if harness:
            harness.replay_only = True
        try:
            for _, frame in self.store.pending():
                await self.process(frame)
        finally:
            if harness:
                harness.replay_only = previous


async def run_shadow(
    session: ShadowSession, source: FrameSource, clock: Clock, maximum_cycles: int | None = None
) -> None:
    store, cfg = session.store, session.engine.config
    done = asyncio.Event()

    async def heartbeat() -> None:
        while not done.is_set():
            store.heartbeat(clock.now())
            try:
                await asyncio.wait_for(done.wait(), timeout=5)
            except asyncio.TimeoutError:
                pass

    task = asyncio.create_task(heartbeat())
    try:
        await session.recover()
        cycles = 0
        while not store.control()["stop"] and (maximum_cycles is None or cycles < maximum_cycles):
            start = time.perf_counter()
            try:
                frame = await asyncio.wait_for(source.poll(), timeout=120)
            except (Exception, asyncio.TimeoutError):
                # No fabricated market frame or fills during an interruption.
                store.operational({"kind": "FEED_UNAVAILABLE", "at": clock.now().isoformat()})
                cycles += 1
                await asyncio.sleep(min(cfg.poll_seconds * 2, 30))
                continue
            if store.control()["stop"]:
                break
            store.operational(
                {
                    "kind": "FEED_RECEIVED",
                    "at": clock.now().isoformat(),
                    "acquisition_seconds": time.perf_counter() - start,
                }
            )
            await session.process(frame)
            cycles += 1
            # Small waits make CLI stop responsive without hard process killing.
            end = time.monotonic() + cfg.poll_seconds
            while time.monotonic() < end and not store.control()["stop"]:
                await asyncio.sleep(min(0.25, max(0, end - time.monotonic())))
    finally:
        done.set()
        await task
        store.operational({"kind": "RUNNER_STOPPED", "at": clock.now().isoformat()})
        store.release()


async def replay_decisions(
    store: ShadowStore, responses: Path, clock: Clock, model_path: Path | None = None
) -> dict[str, Any]:
    store.verify()
    metadata = store.metadata()
    manifest = metadata["manifest"]
    if manifest["core_version"] != core_version():
        raise ValueError("Replay source version mismatch")
    cfg = ShadowConfig.model_validate(manifest["config"])
    ai = ShadowAI(cfg, responses, clock, replay=True, model_path=model_path)
    if ai.identity() != manifest["ai"]:
        raise ValueError("Replay model or policy identity mismatch")
    engine = ShadowEngine(cfg, ai)
    engine.restore(metadata["initial"])
    comparisons = []
    decision_count = 0
    for seq, raw, expected, state, _ in store.records():
        if ai.harness is not None:
            evidence = {}
            for decision in expected["decisions"]:
                if decision["ai"] is not None:
                    candidate = decision["ai"]["candidate"]
                    if candidate["analyst_trace_id"] is not None:
                        evidence[candidate["analyst_trace_id"]] = candidate["analyst"]
            ai.harness.evidence = evidence
        actual = await engine.apply(ShadowFrame.model_validate(raw))
        decision_count += len(expected["decisions"])
        comparisons.append(
            {
                "seq": seq,
                "frame_id": expected["frame_id"],
                "decisions_match": stable_id(actual) == stable_id(expected),
                "state_matches": stable_id(engine.dump()) == stable_id(state),
            }
        )
    matched = all(r["decisions_match"] and r["state_matches"] for r in comparisons)
    return {
        "status": "MATCH" if matched else "DIVERGED",
        "frames": len(comparisons),
        "decisions": decision_count,
        "comparisons": comparisons,
        "pending_frames_not_replayed": len(store.pending()),
        "exchange_mutations": "BLOCKED",
        "llm_network_calls": 0,
    }


def health(store: ShadowStore, now: datetime) -> dict[str, Any]:
    control = store.control()
    _, state = store.checkpoint()
    operations = store.operations()
    commits = [e for e in operations if e["kind"] == "FRAME_COMMITTED"]
    last = commits[-1] if commits else None
    running = bool(
        control["owner"]
        and control["lease_until"]
        and datetime.fromisoformat(control["lease_until"]) > now
    )
    cfg = ShadowConfig.model_validate(store.metadata()["manifest"]["config"])
    age = (
        (now - datetime.fromisoformat(state["clock"])).total_seconds()
        if state["last_frame"]
        else None
    )
    recent = [e for e in operations if e["kind"] in ("FEED_UNAVAILABLE", "FRAME_COMMITTED")]
    feed_error = bool(recent and recent[-1]["kind"] == "FEED_UNAVAILABLE")
    ai_events = [e for e in commits if e.get("ai_status") not in (None, "NOT_EVALUATED")]
    ai_unavailable = bool(ai_events and ai_events[-1]["ai_status"] == "UNAVAILABLE")
    stale = (
        age is None
        or age < 0
        or age > cfg.freshness_seconds
        or bool(last and last["stale_symbols"])
    )
    status = (
        "STOPPED"
        if not running
        else "STOPPING"
        if control["stop"]
        else "DEGRADED"
        if stale or feed_error or ai_unavailable
        else "HEALTHY"
    )
    return {
        "status": status,
        "mode": "SHADOW",
        "virtual_only": True,
        "exchange_mutations": "BLOCKED",
        "running": running,
        "stop_requested": bool(control["stop"]),
        "last_frame_age_seconds": age,
        "stale_market_data": stale,
        "network_interruption": feed_error,
        "last_latency": last,
        "pending_recovery_frames": len(store.pending()),
        "ai_mode": cfg.ai_mode,
        "ai_status": ai_events[-1]["ai_status"] if ai_events else "NOT_YET_OBSERVED",
        "llm_configuration": "GATEWAY_CONFIGURED" if cfg.llm_gateway else "RECORDED_RESPONSES_ONLY",
        "portfolio_as_of": state["portfolio"]["as_of"] if state["portfolio"] else None,
    }


def export_activity(store: ShadowStore, destination: Path) -> None:
    store.verify()
    destination.mkdir(parents=True, exist_ok=True)
    for name, rows in (
        (
            "frames",
            ({"seq": r[0], "frame": r[1], "result": r[2], "chain": r[4]} for r in store.records()),
        ),
        ("operations", store.iter_operations()),
    ):
        with (destination / f"{name}.jsonl").open("w", encoding="utf-8") as output:
            for row in rows:
                output.write(json.dumps(row, sort_keys=True) + "\n")
    (destination / "manifest.json").write_text(
        json.dumps(store.metadata()["manifest"], sort_keys=True, indent=2), encoding="utf-8"
    )
    (destination / "portfolio.json").write_text(
        json.dumps(store.checkpoint()[1], sort_keys=True, indent=2), encoding="utf-8"
    )
