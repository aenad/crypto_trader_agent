import asyncio
import json
import urllib.error
import urllib.request

import httpx
import pytest
from test_shadow import later, session, setup_context

from quantpilot.shadow.feed import ReadOnlyPublic, WallClock
from quantpilot.shadow.guard import PublicGetTransport
from quantpilot.shadow.health import HealthServer
from quantpilot.shadow.service import replay_decisions, run_shadow
from quantpilot.shadow.storage import ShadowStore


@pytest.mark.parametrize(
    "method,path,headers",
    [
        ("POST", "/v1/account/orders", {}),
        ("DELETE", "/v1/account/orders", {}),
        ("PUT", "/v1/depth", {}),
        ("PATCH", "/v1/depth", {}),
        ("GET", "/v1/account/balances", {}),
        ("GET", "/v1/depth", {"X-API-Key": "PRIVATE_SENTINEL"}),
        ("GET", "/v1/depth", {"Authorization": "Bearer PRIVATE_SENTINEL"}),
    ],
)
def test_exchange_mutations_private_reads_and_credentials_blocked_before_transport(
    method, path, headers
):
    calls = []

    async def scenario():
        def handler(request):
            calls.append(request)
            return httpx.Response(200, json={})

        async with httpx.AsyncClient(
            base_url="https://api.wallex.ir",
            transport=PublicGetTransport(httpx.MockTransport(handler)),
        ) as client:
            with pytest.raises(PermissionError):
                await client.request(method, path, headers=headers)

    asyncio.run(scenario())
    assert not calls


@pytest.mark.parametrize(
    "operation",
    [
        "orders",
        "place_order",
        "cancel_order",
        "withdraw",
        "wallex_spot_post_account_orders",
        "wallex_otc_place_easy_trade_order",
        "discover",
    ],
)
def test_mcp_capability_boundary_blocks_non_public_operations(operation):
    class Source:
        source = "test"

        async def request(self, *args):
            raise AssertionError("Transport must not be invoked")

    with pytest.raises(PermissionError):
        asyncio.run(ReadOnlyPublic(Source()).request(operation, {}))


def test_temporary_network_failure_recovers_without_creating_fake_events(tmp_path):
    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)

        class Source:
            count = 0

            async def poll(self):
                self.count += 1
                if self.count == 1:
                    raise OSError("SENTINEL_PRIVATE_NETWORK_ERROR")
                return frame if self.count == 2 else later(frame)

        await run_shadow(live, Source(), WallClock(), maximum_cycles=3)
        records = list(live.store.records())
        assert len(records) == 2
        assert len(live.engine.ledger.seen) == 1
        ops = live.store.operations()
        assert any(o["kind"] == "FEED_UNAVAILABLE" for o in ops)
        assert "SENTINEL_PRIVATE_NETWORK_ERROR" not in json.dumps(ops)
        assert live.store.control()["owner"] is None

    asyncio.run(scenario())


def test_stop_requested_during_poll_prevents_new_frame_and_orders(tmp_path):
    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)

        class Source:
            async def poll(self):
                live.store.request_stop()
                return frame

        await run_shadow(live, Source(), WallClock(), maximum_cycles=1)
        assert not list(live.store.records())
        assert not live.engine.execution.orders

    asyncio.run(scenario())


def test_commit_succeeded_but_return_was_interrupted_recovers_authoritative_checkpoint(
    tmp_path, monkeypatch
):
    async def scenario():
        cfg, frame = setup_context()
        live = session(tmp_path, cfg)
        real = live.store.commit

        def interrupted(*args, **kwargs):
            real(*args, **kwargs)
            raise OSError("AFTER_COMMIT_FAILURE")

        monkeypatch.setattr(live.store, "commit", interrupted)
        with pytest.raises(OSError):
            await live.process(frame)
        assert live.seq == 1
        assert live.engine.dump() == live.store.checkpoint()[1]
        monkeypatch.setattr(live.store, "commit", real)
        assert await live.process(frame) is None
        await live.process(later(frame))
        assert len(live.engine.ledger.seen) == 1
        assert (await replay_decisions(live.store, tmp_path / "unused", WallClock()))[
            "status"
        ] == "MATCH"

    asyncio.run(scenario())


def test_unrelated_database_is_never_reused(tmp_path):
    import sqlite3

    path = tmp_path / "other.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE unrelated(value TEXT)")
    with pytest.raises(ValueError, match="dedicated"):
        ShadowStore(path)


def test_local_health_endpoint_is_read_only(tmp_path):
    cfg, frame = setup_context()
    live = session(tmp_path, cfg)
    asyncio.run(live.process(frame))
    live.store.heartbeat(WallClock().now())
    with HealthServer(live.store, 0) as server:
        url = f"http://127.0.0.1:{server.server.server_port}/health"
        # The fixture frame may be ahead of wall time; degraded is correct.
        try:
            response = urllib.request.urlopen(url, timeout=3)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body = json.loads(response.read())
        assert body["mode"] == "SHADOW" and body["exchange_mutations"] == "BLOCKED"
        assert "PRIVATE" not in json.dumps(body)
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(
                urllib.request.Request(url, data=b"{}", method="POST"), timeout=3
            )
        assert error.value.code == 405
