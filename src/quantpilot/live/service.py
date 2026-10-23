"""Bounded ticks and an interruptible continuous loop; no activation or credential loading."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Protocol

from quantpilot.ai.fusion import HybridEvaluator
from quantpilot.lifecycle import LifecycleState
from quantpilot.models import MarketSnapshot, OrderIntent

from .domain import Blocked
from .execution import ProtectedExecution


class SnapshotSource(Protocol):
    async def snapshots(self) -> tuple[MarketSnapshot, ...]: ...


class ExecutionService:
    """Requires an already explicitly resumed, separately activated adapter.

    Startup never bootstraps/adopts an account or clears suspension. Any cycle failure
    invalidates outstanding proposals and latches suspension; restart cannot resume.
    The optional evaluator can only veto entries, never manufacture an order.
    """

    def __init__(
        self,
        execution: ProtectedExecution,
        source: SnapshotSource,
        *,
        entry_veto: Callable[[OrderIntent], Awaitable[bool]] | None = None,
        evaluator: HybridEvaluator | None = None,
        poll_seconds: float = 15,
        timeout_seconds: float = 30,
    ):
        if poll_seconds <= 0 or timeout_seconds <= 0:
            raise ValueError("Positive service intervals required")
        self.execution, self.source = execution, source
        self.entry_veto = entry_veto
        self.evaluator = evaluator
        ai = execution.config.ai
        if ai.mode != "QUANT_ONLY" and (evaluator is None or evaluator.mode != ai.mode):
            raise ValueError("Configured hybrid evaluator is required; no quant-only fallback")
        if ai.mode == "QUANT_ONLY" and evaluator is not None:
            raise ValueError("Evaluator requires explicit hybrid configuration")
        if evaluator is not None and evaluator.model.metadata.get("live_enabled") is not True:
            raise ValueError("A research-only model cannot authorize protected LIVE evaluation")
        self.poll_seconds, self.timeout_seconds = poll_seconds, timeout_seconds

    async def tick(self) -> int:
        adapter = self.execution
        if adapter.lifecycle.state not in (LifecycleState.RUNNING, LifecycleState.DEGRADED):
            raise Blocked("EXPLICIT_RESUME_REQUIRED")
        snapshots = await asyncio.wait_for(self.source.snapshots(), self.timeout_seconds)
        if adapter.config.expired(adapter.clock.now()):
            adapter.control("STOP_NEW_ENTRIES")
            return 0
        if adapter.config.settling(adapter.clock.now()):
            return len(await adapter.final_liquidation(snapshots))
        intents = await adapter.strategy_cycle(snapshots)
        sent = 0
        for intent in intents:
            if intent.side == "BUY" and self.evaluator is not None:
                if not await asyncio.wait_for(
                    adapter.evaluate_entry(intent, self.evaluator), self.timeout_seconds
                ):
                    continue
            if intent.side == "BUY" and self.entry_veto is not None:
                accepted = await asyncio.wait_for(self.entry_veto(intent), self.timeout_seconds)
                if accepted is not True:
                    adapter.revoke_authorization(intent.client_id)
                    with adapter.store.db:
                        adapter.store.audit("SERVICE_ENTRY_VETO", {"client_id": intent.client_id})
                    continue
            await adapter.submit(intent)
            sent += 1
        return sent

    async def run(self, stop: asyncio.Event, *, maximum_cycles: int | None = None) -> None:
        if maximum_cycles is not None and maximum_cycles < 1:
            raise ValueError("Positive cycle count required")
        adapter = self.execution
        cycles = 0
        try:
            while not stop.is_set() and (maximum_cycles is None or cycles < maximum_cycles):
                try:
                    await self.tick()
                except Exception as exc:
                    # Do not log remote messages, credentials or raw exception text.
                    adapter.store.latch("SERVICE_CYCLE_FAILED")
                    adapter.control("PAUSE_TRADING")
                    with adapter.store.db:
                        adapter.store.audit("SERVICE_FAILED", {"error_type": type(exc).__name__})
                    break
                cycles += 1
                if maximum_cycles is not None and cycles >= maximum_cycles:
                    break
                try:
                    await asyncio.wait_for(stop.wait(), self.poll_seconds)
                except asyncio.TimeoutError:
                    pass
        finally:
            # Resource release never creates a closing order or cancels an unknown one.
            await adapter.close()
