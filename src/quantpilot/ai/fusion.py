"""Veto-only research recommendations. The original signal still goes to risk."""

from typing import Literal

from quantpilot.config import stable_id
from quantpilot.models import AIAnalysis, MarketSnapshot, Signal
from quantpilot.trading.config import ResearchParameters

from .analyst import AnalystHarness
from .domain import CandidateRecommendation
from .features import assemble_context, extract_features
from .learning import FrozenModel


class HybridEvaluator:
    def __init__(
        self,
        model: FrozenModel,
        research: ResearchParameters,
        mode: Literal["QUANT_ML", "QUANT_ML_LLM"],
        analyst: AnalystHarness | None = None,
    ):
        if mode == "QUANT_ML_LLM" and analyst is None:
            raise ValueError("LLM harness required")
        if model.metadata.get("research_id") != stable_id(research.model_dump(mode="json")):
            raise ValueError("Model/strategy feature parameters mismatch")
        self.model, self.research, self.mode, self.analyst = model, research, mode, analyst
        self.recommendations: list[CandidateRecommendation] = []

    async def recommend(self, signal: Signal, snapshot: MarketSnapshot) -> CandidateRecommendation:
        base = {
            "signal_id": stable_id(signal.model_dump(mode="json")),
            "symbol": signal.symbol,
            "as_of": signal.as_of,
        }
        if signal.action != "BUY":
            return CandidateRecommendation(
                **base,
                action=signal.action,
                verdict="ACCEPT",
                reasons=("DETERMINISTIC_EXIT_OR_HOLD_UNCHANGED",),
            )
        try:
            prediction = self.model.predict(
                extract_features(snapshot, signal, self.research), signal.as_of
            )
        except Exception:
            return CandidateRecommendation(
                **base, action="HOLD", verdict="ABSTAIN", reasons=("ML_UNAVAILABLE_OR_INVALID",)
            )
        output, trace_id = None, None
        if self.mode == "QUANT_ML_LLM":
            assert self.analyst is not None
            output, trace_id = await self.analyst.review(
                assemble_context(snapshot, signal, self.research)
            )
        if prediction.quality != "HIGH":
            return CandidateRecommendation(
                **base,
                action="HOLD",
                verdict="REJECT",
                reasons=("ML_BELOW_FROZEN_THRESHOLD",),
                prediction=prediction,
                analyst=output,
                analyst_trace_id=trace_id,
            )
        if self.mode == "QUANT_ML":
            return CandidateRecommendation(
                **base,
                action="BUY",
                verdict="ACCEPT",
                reasons=("ML_THRESHOLD_PASSED_RESEARCH_ONLY",),
                prediction=prediction,
            )
        if output is None or output.assessment == "ABSTAIN":
            return CandidateRecommendation(
                **base,
                action="HOLD",
                verdict="ABSTAIN",
                reasons=("LLM_MISSING_INVALID_OR_ABSTAINED",),
                prediction=prediction,
                analyst=output,
                analyst_trace_id=trace_id,
            )
        accepted = output.assessment == "ACCEPT"
        return CandidateRecommendation(
            **base,
            action="BUY" if accepted else "HOLD",
            verdict="ACCEPT" if accepted else "REJECT",
            reasons=("LLM_ACCEPT" if accepted else "LLM_VETO",),
            prediction=prediction,
            analyst=output,
            analyst_trace_id=trace_id,
        )

    async def evaluate(self, signal: Signal, snapshot: MarketSnapshot) -> AIAnalysis:
        candidate = await self.recommend(signal, snapshot)
        self.recommendations.append(candidate)
        return AIAnalysis(
            model_version=f"{self.mode}:{self.model.model_version}:veto-only-v1",
            input_id=stable_id(candidate.model_dump(mode="json")),
            verdict=candidate.verdict,
            reasons=candidate.reasons,
        )
