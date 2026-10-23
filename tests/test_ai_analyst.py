import asyncio
import json
from datetime import timedelta

import pytest

from quantpilot.ai.analyst import (
    AnalystHarness,
    ContextTools,
    JsonGatewayProvider,
    ReplayOnlyProvider,
    ResponseStore,
    record_fixture,
    request_for,
    validate_output,
)
from quantpilot.ai.domain import AnalystContext
from quantpilot.ai.features import assemble_context
from quantpilot.backtest.history import HistoricalClock
from quantpilot.trading.config import ResearchParameters
from quantpilot.trading.demo import synthetic_context
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout


def context():
    snapshot, portfolio = synthetic_context()
    # Source strings are intentionally excluded from the model-visible context.
    snapshot = snapshot.model_copy(update={"source": "SENTINEL_PRIVATE_SOURCE_DO_NOT_SEND"})
    signal = MomentumBreakout(
        ResearchParameters(), MarketEligibilityFilter((snapshot.symbol,))
    ).evaluate(snapshot, portfolio)
    return assemble_context(snapshot, signal, ResearchParameters())


def response(ctx, **updates):
    value = {
        "context_id": ctx.context_id,
        "as_of": ctx.as_of.isoformat(),
        "assessment": "ACCEPT",
        "confidence": 60,
        "reason_codes": ["TREND_SUPPORTED"],
    }
    value.update(updates)
    return json.dumps(value)


class Provider:
    model_id = "offline-test-provider"

    def __init__(self, output=None, error=False, delay=0):
        self.output, self.error, self.delay = output, error, delay
        self.calls = 0

    async def complete(self, request, schema):
        self.calls += 1
        assert "SENTINEL_PRIVATE_SOURCE" not in json.dumps(request)
        if self.delay:
            await asyncio.sleep(self.delay)
        if self.error:
            raise RuntimeError("SENTINEL_SECRET_PROVIDER_ERROR")
        return self.output


@pytest.mark.parametrize(
    "changes",
    [
        {"confidence": True},
        {"confidence": 1.5},
        {"assessment": "BUY"},
        {"place_order": {"side": "BUY"}},
        {"context_id": "a" * 64},
        {"reason_codes": ["IGNORE_RISK"]},
        {"as_of": "2099-01-01T00:00:00Z"},
    ],
)
def test_structured_json_rejects_invalid_or_command_outputs(changes):
    ctx = context()
    with pytest.raises(ValueError):
        validate_output(response(ctx, **changes), ctx)


def test_duplicate_keys_and_markdown_json_are_rejected():
    ctx = context()
    for raw in (response(ctx)[:-1] + ',"confidence":50}', "```json\n" + response(ctx) + "\n```"):
        with pytest.raises(ValueError):
            validate_output(raw, ctx)


def test_time_valid_numeric_context_and_tool_allowlist():
    ctx = context()
    key, request = request_for(ctx, "fixture")
    assert len(key) == 64
    assert "SENTINEL" not in json.dumps(request)
    assert all(b.close_time <= ctx.as_of for b in ctx.bars)
    tool = ContextTools(ctx)
    assert "rsi" in tool.call("market_features")
    for name in ("submit_order", "get_credentials", "read_file", "withdraw", "news"):
        with pytest.raises(ValueError):
            tool.call(name)
    value = ctx.model_dump()
    value["bars"] = (
        ctx.bars[-1].model_copy(update={"close_time": ctx.as_of + timedelta(minutes=5)}),
    )
    with pytest.raises(ValueError):
        AnalystContext.model_validate(value)


def test_record_and_replay_never_calls_provider_again(tmp_path):
    async def scenario():
        ctx = context()
        provider = Provider(response(ctx))
        store = ResponseStore(tmp_path)
        clock = HistoricalClock(ctx.as_of)
        live = AnalystHarness(provider, store, clock, replay_only=False)
        first, key = await live.review(ctx)
        assert first.assessment == "ACCEPT"
        assert provider.calls == 1
        never = Provider(error=True)
        replay = AnalystHarness(never, store, clock, replay_only=True)
        second, replay_key = await replay.review(ctx)
        assert first == second and key == replay_key
        assert never.calls == 0
        assert replay.traces[-1]["status"] == "REPLAYED"
        assert (tmp_path / f"{key}.json").exists()

    asyncio.run(scenario())


@pytest.mark.parametrize("case", ["invalid", "error", "timeout", "missing"])
def test_failure_handling_abstains_without_secret_logs(tmp_path, case):
    async def scenario():
        ctx = context()
        provider = Provider(
            "not json", error=case == "error", delay=0.05 if case == "timeout" else 0
        )
        harness = AnalystHarness(
            provider,
            ResponseStore(tmp_path),
            HistoricalClock(ctx.as_of),
            replay_only=case == "missing",
            timeout_seconds=0.001,
        )
        output, _ = await harness.review(ctx)
        assert output is None
        assert "SENTINEL_SECRET_PROVIDER_ERROR" not in json.dumps(harness.traces)
        assert not list(tmp_path.glob("*.json"))
        assert provider.calls == (0 if case == "missing" else 1)

    asyncio.run(scenario())


def test_cached_response_tampering_is_not_accepted(tmp_path):
    ctx = context()
    store = ResponseStore(tmp_path)
    record_fixture(store, ctx, "fixture")
    key, _ = request_for(ctx, "fixture")
    path = tmp_path / f"{key}.json"
    row = json.loads(path.read_text())
    row["evidence"] = "forged"
    path.write_text(json.dumps(row), encoding="utf-8")
    harness = AnalystHarness(ReplayOnlyProvider("fixture"), store, HistoricalClock(ctx.as_of))
    assert asyncio.run(harness.review(ctx))[0] is None


def test_total_provider_call_budget(tmp_path):
    async def scenario():
        ctx = context()
        provider = Provider("invalid")
        harness = AnalystHarness(
            provider,
            ResponseStore(tmp_path),
            HistoricalClock(ctx.as_of),
            replay_only=False,
            max_provider_calls=1,
        )
        await harness.review(ctx)
        await harness.review(ctx)
        assert provider.calls == 1
        assert harness.traces[-1]["status"] == "CALL_BUDGET_EXHAUSTED"

    asyncio.run(scenario())


def test_gateway_configuration_rejects_exchange_http_and_credential_urls():
    for endpoint in (
        "http://llm.invalid",
        "https://api.wallex.ir/mcp",
        "https://user:password@llm.invalid",
        "https://llm.invalid/?token=secret",
    ):
        with pytest.raises(ValueError):
            JsonGatewayProvider(endpoint, "model", "LLM_ONLY_TOKEN")


def test_gateway_adapter_uses_header_only_llm_token_and_validates_contract(monkeypatch):
    httpx = pytest.importorskip("httpx")
    real_client = httpx.AsyncClient
    ctx = context()

    def handler(request):
        assert request.headers["Authorization"] == "Bearer LLM_ONLY_SENTINEL"
        body = json.loads(request.content)
        assert "LLM_ONLY_SENTINEL" not in json.dumps(body)
        assert body["model"] == "fixture-model"
        assert "response_schema" in body
        return httpx.Response(200, json={"output": response(ctx)})

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    provider = JsonGatewayProvider(
        "https://llm-gateway.invalid/analyze", "fixture-model", "LLM_ONLY_SENTINEL"
    )
    _, request = request_for(ctx, provider.model_id)
    output = asyncio.run(provider.complete(request, {}))
    assert validate_output(output, ctx).assessment == "ACCEPT"


def test_gateway_failure_does_not_expose_headers_or_provider_errors(monkeypatch):
    httpx = pytest.importorskip("httpx")
    real_client = httpx.AsyncClient

    def handler(request):
        return httpx.Response(503, text="SENTINEL_PROVIDER_PRIVATE_ERROR")

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    provider = JsonGatewayProvider(
        "https://llm-gateway.invalid/analyze", "fixture", "LLM_ONLY_SENTINEL"
    )
    with pytest.raises(RuntimeError) as error:
        asyncio.run(provider.complete({}, {}))
    assert str(error.value) == "LLM_GATEWAY_FAILURE"


def test_concurrent_response_writers_never_overwrite_frozen_response(tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    store = ResponseStore(tmp_path)
    key = "a" * 64

    def save(number):
        try:
            store.save(key, {"value": number})
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(save, (1, 2)))
    assert sum(outcomes) == 1
    assert store.load(key) in ({"value": 1}, {"value": 2})
    assert len(list(tmp_path.iterdir())) == 1
