import asyncio
import json
from decimal import Decimal

import pytest

from quantpilot.ai.analyst import AnalystHarness, ReplayOnlyProvider, ResponseStore, record_fixture
from quantpilot.ai.cli import synthetic_input
from quantpilot.ai.dataset import market_input
from quantpilot.ai.domain import Prediction
from quantpilot.ai.features import assemble_context
from quantpilot.ai.fusion import HybridEvaluator
from quantpilot.backtest.history import HistoricalClock
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.config import stable_id
from quantpilot.models import AIAnalysis
from quantpilot.trading.config import ResearchParameters, RiskParameters
from quantpilot.trading.demo import synthetic_context
from quantpilot.trading.risk import DeterministicRiskEngine
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout


class QualityModel:
    model_version = "UNIT_TEST_MODEL_NOT_LIGHTGBM"

    def __init__(self, research, quality="HIGH", fail=False):
        self.metadata = {"research_id": stable_id(research.model_dump(mode="json"))}
        self.quality, self.fail, self.calls = quality, fail, 0

    def predict(self, features, as_of):
        self.calls += 1
        if self.fail:
            raise RuntimeError("MODEL_UNAVAILABLE")
        probability = Decimal(".9") if self.quality == "HIGH" else Decimal(".1")
        return Prediction(
            model_version=self.model_version,
            as_of=as_of,
            features=features,
            raw_probability=probability,
            probability=probability,
            quality=self.quality,
        )


def strategy_context():
    snapshot, portfolio = synthetic_context()
    parameters = ResearchParameters()
    eligibility = MarketEligibilityFilter((snapshot.symbol,))
    signal = MomentumBreakout(parameters, eligibility).evaluate(snapshot, portfolio)
    assert signal.action == "BUY"
    return snapshot, portfolio, signal, parameters, eligibility


@pytest.mark.parametrize(
    "assessment,expected",
    [("ACCEPT", "ACCEPT"), ("VETO", "REJECT"), ("ABSTAIN", "ABSTAIN"), (None, "ABSTAIN")],
)
def test_fusion_is_structured_veto_only_and_cache_failure_abstains(tmp_path, assessment, expected):
    snapshot, portfolio, signal, parameters, eligibility = strategy_context()
    store = ResponseStore(tmp_path)
    if assessment:
        record_fixture(store, assemble_context(snapshot, signal, parameters), "fixture", assessment)
    harness = AnalystHarness(ReplayOnlyProvider("fixture"), store, HistoricalClock(snapshot.as_of))
    evaluator = HybridEvaluator(QualityModel(parameters), parameters, "QUANT_ML_LLM", harness)
    original = signal.model_dump_json()
    candidate = asyncio.run(evaluator.recommend(signal, snapshot))
    assert candidate.verdict == expected
    assert candidate.authorized_to_trade is False
    assert signal.model_dump_json() == original
    # Even unanimous AI ACCEPT cannot bypass the canonical deterministic risk halt.
    manager = DeterministicRiskEngine(
        RiskParameters(),
        parameters,
        eligibility,
        {snapshot.symbol: snapshot},
        (portfolio.account_id,),
    )
    risk = manager.check(signal, portfolio.model_copy(update={"risk_halted": True}))
    assert risk.allowed is False
    assert "RISK_HALT_LATCHED" in risk.reasons


def test_low_ml_rejects_but_both_independent_components_are_logged(tmp_path):
    snapshot, _, signal, parameters, _ = strategy_context()
    store = ResponseStore(tmp_path)
    record_fixture(store, assemble_context(snapshot, signal, parameters), "fixture")
    harness = AnalystHarness(ReplayOnlyProvider("fixture"), store, HistoricalClock(snapshot.as_of))
    evaluator = HybridEvaluator(
        QualityModel(parameters, "LOW"), parameters, "QUANT_ML_LLM", harness
    )
    candidate = asyncio.run(evaluator.recommend(signal, snapshot))
    assert candidate.verdict == "REJECT"
    assert candidate.analyst.assessment == "ACCEPT"
    assert candidate.prediction.quality == "LOW"
    assert len(harness.traces) == 1


def test_ml_failures_abstain_and_ai_never_blocks_sell():
    snapshot, _, signal, parameters, _ = strategy_context()
    model = QualityModel(parameters, fail=True)
    evaluator = HybridEvaluator(model, parameters, "QUANT_ML")
    assert asyncio.run(evaluator.recommend(signal, snapshot)).verdict == "ABSTAIN"
    exit_signal = signal.model_copy(update={"action": "SELL"})
    candidate = asyncio.run(evaluator.recommend(exit_signal, snapshot))
    assert candidate.action == "SELL" and candidate.verdict == "ACCEPT"
    assert model.calls == 1


def test_feature_parameter_mismatch_is_rejected():
    _, _, _, parameters, _ = strategy_context()
    with pytest.raises(ValueError, match="parameters"):
        HybridEvaluator(
            QualityModel(parameters), parameters.model_copy(update={"ema_fast": 4}), "QUANT_ML"
        )


class AcceptAll:
    async def evaluate(self, signal, snapshot):
        return AIAnalysis(
            model_version="TEST_ACCEPT_ALL",
            input_id=signal.snapshot_id,
            verdict="ACCEPT",
            reasons=("TEST",),
        )


def test_ai_acceptance_preserves_core_accounting_and_changes_replay_identity():
    data, risk, approved, fx = market_input(synthetic_input(96))
    baseline = asyncio.run(HistoricalReplay(data, risk, approved, fx).run())
    filtered = asyncio.run(
        HistoricalReplay(
            data, risk, approved, fx, evaluator=AcceptAll(), evaluation_id="TEST_ACCEPT_ALL"
        ).run()
    )
    assert baseline["metrics"] == filtered["metrics"]
    assert baseline["manifest"]["run_id"] != filtered["manifest"]["run_id"]
    assert any(d.get("analysis", {}).get("verdict") == "ACCEPT" for d in filtered["decisions"])


def test_ai_accepted_candidates_still_rejected_by_risk():
    raw = synthetic_input(96)
    raw["risk"]["min_net_reward_risk"] = "10"
    data, risk, approved, fx = market_input(raw)
    evaluator = HybridEvaluator(QualityModel(data.research), data.research, "QUANT_ML")
    result = asyncio.run(
        HistoricalReplay(
            data,
            risk,
            approved,
            fx,
            evaluator=evaluator,
            evaluation_id="UNIT_TEST_REJECTED_BY_RISK",
        ).run()
    )
    accepted = [d for d in result["decisions"] if d.get("analysis", {}).get("verdict") == "ACCEPT"]
    assert accepted and all(not d["risk"]["allowed"] for d in accepted)
    assert result["metrics"]["fill_count"] == 0
    assert not any(
        "credential" in json.dumps(c.model_dump(mode="json")) for c in evaluator.recommendations
    )
