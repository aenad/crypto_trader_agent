import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from quantpilot.config import stable_id
from quantpilot.readiness import inspect
from quantpilot.trading.config import ResearchParameters


def llm_result(**changes):
    return {
        "gateway_configured": True,
        "analyst_model_configured": True,
        "llm_token_configured": True,
        "llm_status": "SCHEMA_VERIFIED",
        **changes,
    }


def fake_checks(monkeypatch, *, research_matches=True, llm=None):
    research = ResearchParameters()
    model = SimpleNamespace(
        model_version="TEST-MODEL",
        metadata={
            "research_id": stable_id(research.model_dump(mode="json"))
            if research_matches
            else "WRONG",
            "live_enabled": False,
        },
    )
    monkeypatch.setattr("quantpilot.readiness.FrozenModel.load", lambda path: model)

    async def check(*args):
        return llm or llm_result()

    monkeypatch.setattr("quantpilot.readiness.check_llm", check)


def test_readiness_shadow_is_not_live_authorization(monkeypatch, tmp_path):
    fake_checks(monkeypatch)
    r = asyncio.run(
        inspect(Path("config/shadow-ai.deploy.json"), tmp_path / "unused.env", None, True)
    )
    assert r["ready_for_hybrid_shadow"] and not r["ready_for_live"]
    assert not r["live_activated"] and r["exchange_mutations"] == 0
    assert "VALIDATED_BASELINE_MODEL_REQUIRED" in r["live_blockers"]


def test_readiness_rejects_wrong_strategy_and_unverified_llm(monkeypatch, tmp_path):
    fake_checks(monkeypatch, research_matches=False, llm=llm_result(llm_status="NOT_CALLED"))
    r = asyncio.run(
        inspect(Path("config/shadow-ai.deploy.json"), tmp_path / "unused.env", None, False)
    )
    assert not r["ready_for_hybrid_shadow"]
    assert {"MODEL_STRATEGY_MISMATCH", "LLM_CONNECTION_UNVERIFIED"} <= set(r["blockers"])


def test_readiness_masks_invalid_config(tmp_path):
    p = tmp_path / "config.json"
    p.write_text('{"private":"DO_NOT_ECHO", "mode":"INVALID"}')
    r = asyncio.run(inspect(p, tmp_path / "unused.env", None, False))
    assert "DO_NOT_ECHO" not in json.dumps(r)
    assert r["blockers"] == ["CONFIGURATION_INVALID"]
