import asyncio
from types import SimpleNamespace

import pytest
from test_live import fixture
from test_live_service import Source, ready

from quantpilot.ai.runtime import HybridRuntimeConfig, build_evaluator
from quantpilot.config import stable_id
from quantpilot.live.service import ExecutionService
from quantpilot.models import AIAnalysis
from quantpilot.trading.config import ResearchParameters


def test_runtime_no_implicit_ai_or_missing_model():
    assert HybridRuntimeConfig().mode == "QUANT_ONLY"
    with pytest.raises(ValueError):
        HybridRuntimeConfig(mode="QUANT_ML_LLM")
    with pytest.raises(ValueError):
        HybridRuntimeConfig(timeout_seconds=0)


def test_runtime_builds_replay_harness_without_credentials(monkeypatch, tmp_path):
    research = ResearchParameters()
    model = SimpleNamespace(metadata={"research_id": stable_id(research.model_dump(mode="json"))})
    monkeypatch.setattr("quantpilot.ai.runtime.FrozenModel.load", lambda path: model)
    config = HybridRuntimeConfig(mode="QUANT_ML_LLM", model_path="FAKE", analyst_model_id="FAKE")
    evaluator = build_evaluator(config, research, tmp_path, SimpleNamespace())
    assert evaluator is not None and evaluator.analyst.replay_only
    with pytest.raises(ValueError, match="Dedicated LLM"):
        build_evaluator(config, research, tmp_path, SimpleNamespace(), replay_only=False)


class Evaluator:
    mode = "QUANT_ML_LLM"

    def __init__(self, verdict, approved=True):
        self.model = SimpleNamespace(metadata={"live_enabled": approved})
        self.verdict = verdict
        self.recommendations = []

    async def evaluate(self, signal, snapshot):
        assert signal.action == "BUY" and signal.symbol == snapshot.symbol
        analysis = AIAnalysis(
            model_version="TEST-ONLY",
            input_id="test",
            verdict=self.verdict,
            reasons=("FAKE-EVIDENCE",),
        )
        self.recommendations.append(analysis)
        return analysis


@pytest.mark.parametrize("verdict,expected", [("ACCEPT", 1), ("REJECT", 0), ("ABSTAIN", 0)])
def test_hybrid_service_veto_and_risk_ordering(tmp_path, verdict, expected):
    async def scenario():
        a, exchange, store, snapshot, _, _ = fixture(
            tmp_path, ai={"mode": "QUANT_ML_LLM", "model_path": "FAKE", "analyst_model_id": "FAKE"}
        )
        try:
            await ready(a, snapshot)
            evaluator = Evaluator(verdict)
            service = ExecutionService(a, Source(snapshot), evaluator=evaluator)
            assert await service.tick() == expected
            assert exchange.submissions == expected
            assert len(evaluator.recommendations) == 1
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


def test_live_forbids_research_model_or_missing_evaluator(tmp_path):
    a, _, store, snapshot, _, _ = fixture(
        tmp_path, ai={"mode": "QUANT_ML_LLM", "model_path": "FAKE", "analyst_model_id": "FAKE"}
    )
    try:
        with pytest.raises(ValueError, match="required"):
            ExecutionService(a, Source(snapshot))
        with pytest.raises(ValueError, match="research-only"):
            ExecutionService(a, Source(snapshot), evaluator=Evaluator("ACCEPT", False))
    finally:
        store.close()
