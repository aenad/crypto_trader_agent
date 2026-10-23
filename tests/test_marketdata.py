import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from quantpilot.marketdata.collect import CandleCollector, Collectors, MarketScanner
from quantpilot.marketdata.domain import CollectionPolicy
from quantpilot.marketdata.mock import MockPublic
from quantpilot.marketdata.normalize import candles, recent_trades, validate_coverage
from quantpilot.marketdata.storage import LocalCatalog, ParquetStore
from quantpilot.marketdata.stream import channel_name, normalize_stream, publication
from quantpilot.marketdata.transport import MCPPublic, RateLimited, RestPublic, retry

NOW = datetime(2026, 10, 22, 10, tzinfo=timezone.utc)
PAIR = "BTC/USDT"
POLICY = CollectionPolicy(approved=frozenset({PAIR}), chunk_bars=2)


def test_offline_scan_collect_storage_roundtrip(tmp_path):
    import pyarrow.parquet as pq

    async def run():
        source = MockPublic(NOW)
        assert (await MarketScanner(source, POLICY).scan())[0].symbol == PAIR
        collector = Collectors(source, POLICY)
        snapshot = await CandleCollector(collector, bars=5).snapshot(PAIR, NOW)
        assert len(snapshot.candles) == 5 and source.calls.count("candles") == 3
        book = await collector.order_book(PAIR, NOW)
        trades = await collector.recent_trades(PAIR, NOW)
        store = ParquetStore(tmp_path, LocalCatalog(tmp_path / "catalog"))
        for kind, rows in [
            ("candles", list(snapshot.candles)),
            ("book", [book]),
            ("trades", trades),
        ]:
            first = store.save(kind, PAIR, rows, {"source": "synthetic"})
            second = store.save(kind, PAIR, rows, {"source": "synthetic"})
            assert first == second
            table = pq.read_table(first["path"])
            assert table.num_rows == len(rows)
            encoded = json.loads(table.to_pylist()[0]["payload_json"])
            assert encoded["symbol"] == PAIR
            assert (tmp_path / "catalog" / (first["dataset_id"] + ".json")).exists()

    asyncio.run(run())


def candle_payload():
    return asyncio.run(
        MockPublic(NOW).request(
            "candles",
            {
                "symbol": "BTCUSDT",
                "resolution": "1",
                "from": int(NOW.timestamp()) - 180,
                "to": int(NOW.timestamp()) - 1,
            },
        )
    )


@pytest.mark.parametrize("change", ["duplicate", "reverse", "columns", "ohlc", "alignment"])
def test_invalid_candles_rejected(change):
    payload = candle_payload()
    if change == "duplicate":
        payload["t"][1] = payload["t"][0]
    if change == "reverse":
        payload["t"].reverse()
    if change == "columns":
        payload["v"].pop()
    if change == "ohlc":
        payload["h"][0] = "1"
    if change == "alignment":
        payload["t"][0] += 1
    with pytest.raises(ValueError):
        candles(payload, PAIR, "1", NOW, NOW - timedelta(minutes=3), NOW)


def test_gaps_missing_and_incomplete():
    payload = candle_payload()
    rows = candles(payload, PAIR, "1", NOW, NOW - timedelta(minutes=3), NOW)
    with pytest.raises(ValueError, match="gap"):
        validate_coverage(rows[:1] + rows[2:], NOW - timedelta(minutes=3), NOW, 60)
    open_payload = {
        **payload,
        "t": [int(NOW.timestamp()) - 120, int(NOW.timestamp()) - 60, int(NOW.timestamp())],
    }
    result = candles(
        open_payload, PAIR, "1", NOW, NOW - timedelta(minutes=2), NOW + timedelta(minutes=1)
    )
    assert len(result) == 2 and all(row.closed for row in result)


def test_symbol_and_whitelist_before_call():
    with pytest.raises(ValueError):
        CollectionPolicy(approved=frozenset({"BTC/IRR"}))
    with pytest.raises(ValueError):
        CollectionPolicy(approved=frozenset({PAIR}), excluded=frozenset({PAIR}))
    source = MockPublic(NOW)
    with pytest.raises(ValueError):
        asyncio.run(Collectors(source, POLICY).order_book("ETH/USDT", NOW))
    assert source.calls == []


def test_stale_trades_duplicates_and_wrong_symbol():
    data = asyncio.run(MockPublic(NOW).request("trades", {"symbol": "BTCUSDT"}))
    data["result"]["latestTrades"] *= 2
    assert len(recent_trades(data, PAIR, NOW)) == 1
    with pytest.raises(ValueError):
        recent_trades(data, "ETH/USDT", NOW)
    with pytest.raises(ValueError, match="stale"):
        asyncio.run(
            Collectors(MockPublic(NOW), POLICY).recent_trades(PAIR, NOW + timedelta(hours=1))
        )


def test_rest_allowlist_and_retry_after():
    seen = []

    async def handle(request):
        seen.append(request)
        if len(seen) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"result": {"markets": []}})

    async def run():
        async with httpx.AsyncClient(
            base_url="https://api.wallex.ir", transport=httpx.MockTransport(handle)
        ) as client:
            adapter = RestPublic(client)
            assert await adapter.request("markets", {}) == {"result": {"markets": []}}
            with pytest.raises(ValueError):
                await adapter.request("submit_order", {})
        assert len(seen) == 2 and all(r.method == "GET" for r in seen)
        assert seen[0].url.path == "/hector/web/v1/markets"
        assert all("X-API-Key" not in r.headers for r in seen)

    asyncio.run(run())


def test_retry_budget():
    waits = []

    async def fail():
        raise RateLimited(3)

    async def sleep(delay):
        waits.append(delay)

    with pytest.raises(RuntimeError):
        asyncio.run(retry(fail, attempts=3, sleep=sleep))
    assert waits == [3, 3]


def test_mcp_discovery_schema_and_mutation_block(tmp_path):
    class Session:
        async def list_tools(self, cursor=None):
            return SimpleNamespace(
                nextCursor=None,
                tools=[
                    SimpleNamespace(
                        name="wallex_basic_get_latest_trades",
                        description="Public latest trades",
                        inputSchema={
                            "type": "object",
                            "properties": {"symbol": {"type": "string"}},
                            "required": ["symbol"],
                            "additionalProperties": False,
                        },
                    )
                ],
            )

        async def call_tool(self, name, args):
            assert name == "wallex_basic_get_latest_trades"
            return SimpleNamespace(
                isError=False,
                structuredContent=None,
                content=[SimpleNamespace(type="text", text='{"success":true}')],
            )

    async def run():
        adapter = MCPPublic(Session())
        await adapter.discover(tmp_path / "tools.json")
        assert json.loads((tmp_path / "tools.json").read_text())["tools"]
        assert await adapter.request("trades", {"symbol": "BTCUSDT"}) == {"success": True}
        with pytest.raises(ValueError):
            await adapter.request("order", {})
        from jsonschema import ValidationError

        with pytest.raises(ValidationError):
            await adapter.request("trades", {"symbol": 1})

    asyncio.run(run())


def test_websocket_protocol_and_validation():
    channel = channel_name(PAIR, "trade")
    assert channel == "public:BTCUSDT@trade"
    assert publication(
        {"push": {"channel": channel, "pub": {"data": {"price": "1"}}}}, channel
    ) == {"price": "1"}
    with pytest.raises(ValueError):
        publication({"error": {"code": 1}}, channel)
    with pytest.raises(ValueError):
        publication({"push": {"channel": "wrong"}}, channel)
    with pytest.raises(ValueError):
        channel_name(PAIR, "margin")
    event = normalize_stream(
        {"price": "100", "quantity": "1", "timestamp": NOW.isoformat(), "isBuyOrder": True},
        PAIR,
        "trade",
        NOW,
        0,
        180,
    )
    assert event and event.timestamp_kind == "exchange"


def test_documented_evidence_schemas():
    path = Path(__file__).parents[1] / "docs/evidence/wallex-tools.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    names = {tool["name"] for tool in metadata["tools"]}
    from quantpilot.marketdata.transport import TOOLS

    assert set(TOOLS.values()) <= names


def test_websocket_reconnect_heartbeat_and_duplicates(monkeypatch):
    import quantpilot.marketdata.stream as module

    now = datetime.now(timezone.utc)
    channel = channel_name(PAIR, "trade")
    trade = {"price": "100", "quantity": "1", "timestamp": now.isoformat(), "isBuyOrder": True}

    def push(value):
        return json.dumps({"push": {"channel": channel, "pub": {"data": value}}})

    first = push(trade)
    second = push({**trade, "quantity": "2"})
    frames = [
        iter(['{"id":1,"connect":{}}', '{"id":2,"subscribe":{}}', "{}", first]),
        iter(['{"id":1,"connect":{}}', '{"id":2,"subscribe":{}}', first, second]),
    ]
    sent, recovered = [], []

    class Socket:
        async def __aenter__(self):
            self.frames = frames.pop(0)
            return self

        async def __aexit__(self, *args):
            pass

        async def send(self, value):
            sent.append(json.loads(value))

        async def recv(self):
            try:
                return next(self.frames)
            except StopIteration:
                raise OSError("Synthetic disconnect") from None

    async def sleep(delay):
        pass

    async def recover():
        recovered.append(True)

    monkeypatch.setattr(module, "connect", lambda *a, **k: Socket())
    monkeypatch.setattr(module.asyncio, "sleep", sleep)

    async def run():
        generator = module.PublicStream(POLICY).events(PAIR, "trade", recover)
        result = []
        try:
            async for event in generator:
                result.append(event)
                if len(result) == 2:
                    break
        finally:
            await generator.aclose()
        assert [e.epoch for e in result] == [0, 1]
        assert result[0].event_id != result[1].event_id

    asyncio.run(run())
    assert recovered == [True] and {} in sent


def test_live_public_fixtures_normalize_without_network():
    from quantpilot.marketdata.normalize import book, markets

    root = Path(__file__).parents[1] / "docs/evidence"
    assert any(
        m.symbol == PAIR
        for m in markets(json.loads((root / "markets-public.json").read_text(encoding="utf-8")))
    )
    from decimal import Decimal

    payload = json.loads(
        (root / "book-public.json").read_text(encoding="utf-8"), parse_float=Decimal
    )
    assert book(payload, PAIR, NOW).timestamp_kind == "observation"


def test_depth_message_envelope():
    result = normalize_stream(
        {"message": [{"price": "100", "quantity": "1"}]}, PAIR, "buyDepth", NOW, 0, 180
    )
    assert result and result.channel == "orderbook:BTCUSDT@buyDepth"


def test_open_candle_stream_is_never_marked_complete():
    ts = int(NOW.timestamp())
    data = {"s": "ok", "t": [ts], "o": ["100"], "h": ["101"], "l": ["99"], "c": ["100"], "v": ["1"]}
    event = normalize_stream(data, PAIR, "1m", NOW, 0, 180)
    assert event and event.candle_complete is False
    assert event.timestamp_kind == "exchange_open_candle"
    with pytest.raises(RateLimited):
        publication({"error": {"code": 106}}, channel_name(PAIR, "trade"))


def test_failed_catalog_does_not_claim_commit(tmp_path):
    class Broken:
        def register(self, manifest):
            raise OSError("Synthetic catalog outage")

    snapshot = asyncio.run(
        CandleCollector(Collectors(MockPublic(NOW), POLICY), bars=2).snapshot(PAIR, NOW)
    )
    with pytest.raises(OSError):
        ParquetStore(tmp_path, Broken()).save("candles", PAIR, list(snapshot.candles), {})
