import asyncio
import json

import httpx
import pytest

from quantpilot.ai.analyst import JsonGatewayProvider


@pytest.mark.parametrize("suffix", ["", "/chat/completions"])
def test_documented_boxapi_contract(monkeypatch, suffix):
    real_client = httpx.AsyncClient

    def handler(request):
        assert str(request.url) == "https://ai.boxapi.ir/ai/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer FAKE-LLM-TOKEN"
        body = json.loads(request.content)
        assert body["model"] == "TEST-MODEL"
        assert body["stream"] is False and "messages" in body
        assert "FAKE-LLM-TOKEN" not in json.dumps(body)
        assert "request" not in body
        return httpx.Response(
            200,
            json={
                "choices": [{"finish_reason": "stop", "message": {"content": '{"status":"ok"}'}}]
            },
        )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    provider = JsonGatewayProvider(
        "https://ai.boxapi.ir/ai/v1" + suffix, "TEST-MODEL", "FAKE-LLM-TOKEN"
    )
    assert json.loads(asyncio.run(provider.complete({"purpose": "TEST"}, {}))) == {"status": "ok"}


@pytest.mark.parametrize(
    "choice",
    [
        {"finish_reason": "length", "message": {"content": "{}"}},
        {"finish_reason": "stop", "message": {"content": None}},
        {"finish_reason": "stop", "message": {"content": "{}", "tool_calls": [{}]}},
    ],
)
def test_boxapi_rejects_truncation_tools_or_nontext(monkeypatch, choice):
    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: real_client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json={"choices": [choice]})
            ),
            **kwargs,
        ),
    )
    provider = JsonGatewayProvider("https://ai.boxapi.ir/ai/v1", "TEST-MODEL", "FAKE")
    with pytest.raises(RuntimeError, match="LLM_GATEWAY_FAILURE"):
        asyncio.run(provider.complete({}, {}))
