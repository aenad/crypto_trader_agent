"""Offline service lifecycle tests; no real keys, transports or exchange requests."""

import asyncio

import pytest
from test_live import fixture

from quantpilot.lifecycle import LifecycleState
from quantpilot.live.domain import Blocked
from quantpilot.live.service import ExecutionService


class Source:
    def __init__(self, snapshot, fail=False):
        self.snapshot, self.fail = snapshot, fail

    async def snapshots(self):
        if self.fail:
            raise TimeoutError("FAKE_NETWORK_FAILURE")
        return (self.snapshot,)


async def ready(adapter, snapshot):
    await adapter.bootstrap()
    await adapter.recover((snapshot,))
    adapter.resume_after_reconciliation()


def test_service_requires_explicit_resume(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await a.bootstrap()
            await a.recover((snapshot,))
            with pytest.raises(Blocked, match="EXPLICIT_RESUME_REQUIRED"):
                await ExecutionService(a, Source(snapshot)).tick()
            assert exchange.submissions == 0
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


def test_service_reconciles_and_never_duplicates_order(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await ready(a, snapshot)
            service = ExecutionService(a, Source(snapshot))
            assert await service.tick() == 1
            assert await service.tick() == 0
            assert exchange.submissions == 1
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


def test_service_network_failure_pauses_without_orders(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await ready(a, snapshot)
            await ExecutionService(a, Source(snapshot, fail=True)).run(
                asyncio.Event(), maximum_cycles=1
            )
            assert exchange.submissions == 0
            assert store.get("suspended") is not None
            assert a.lifecycle.state == LifecycleState.STOPPED
        finally:
            store.close()

    asyncio.run(scenario())


def test_service_entry_veto_and_shutdown_without_sales(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(tmp_path)

        async def veto(intent):
            return False

        try:
            await ready(a, snapshot)
            await ExecutionService(a, Source(snapshot), entry_veto=veto).run(
                asyncio.Event(), maximum_cycles=1
            )
            assert exchange.submissions == 0
            assert store.orders() == ()
            assert a.lifecycle.state == LifecycleState.STOPPED
        finally:
            store.close()

    asyncio.run(scenario())


def test_service_preexisting_stop_never_submits(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(tmp_path)
        try:
            await ready(a, snapshot)
            stop = asyncio.Event()
            stop.set()
            await ExecutionService(a, Source(snapshot)).run(stop)
            assert exchange.submissions == 0
        finally:
            store.close()

    asyncio.run(scenario())
