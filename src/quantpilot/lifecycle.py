"""Durable operator controls; stopping never generates orders or liquidation."""

from enum import Enum
from typing import Protocol


class LifecycleState(str, Enum):
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    DEGRADED = "DEGRADED"
    RISK_PAUSED = "RISK_PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"


class ControlStore(Protocol):
    def get(self, key: str) -> str | None: ...
    def set(self, key: str, value: str) -> None: ...


class LifecycleManager:
    """Caller commits transitions in its existing journal transaction."""

    def __init__(self, store: ControlStore):
        self.store = store
        # A restart always requires reconciliation and explicit authorization again.
        store.set("lifecycle", LifecycleState.STARTING.value)

    @property
    def state(self) -> LifecycleState:
        return LifecycleState(self.store.get("lifecycle") or "STOPPED")

    def resume(
        self, *, reconciled: bool, orders_known: bool, risk_ok: bool, authorized: bool
    ) -> None:
        if not all((reconciled, orders_known, risk_ok, authorized)):
            raise ValueError("STARTUP_CHECKS_REQUIRED")
        self.store.set("lifecycle", "RUNNING")
        self.store.set("entry_control", "ALLOW")

    def command(self, operation: str) -> None:
        states = {
            "STOP_NEW_ENTRIES": self.state.value,
            "PAUSE_TRADING": "RISK_PAUSED",
            "GRACEFUL_SHUTDOWN": "STOPPING",
        }
        if operation not in states:
            raise ValueError("Closing positions requires a separately risk-authorized order")
        self.store.set("entry_control", "BLOCK")
        self.store.set("lifecycle", states[operation])

    def permits(self, side: str) -> bool:
        return self.state in (LifecycleState.RUNNING, LifecycleState.DEGRADED) and (
            side == "SELL" or self.store.get("entry_control") == "ALLOW"
        )

    def stopped(self) -> None:
        self.store.set("lifecycle", "STOPPED")
