import time
from importlib.resources import files
from pathlib import Path
from typing import Any

from quantpilot.ai.analyst import (
    AnalystHarness,
    JsonGatewayProvider,
    ReplayOnlyProvider,
    ResponseStore,
    request_for,
    validate_output,
)
from quantpilot.ai.domain import AnalystContext, AnalystOutput
from quantpilot.ai.fusion import HybridEvaluator
from quantpilot.ai.learning import FrozenModel, implementation_id
from quantpilot.config import stable_id
from quantpilot.interfaces import Clock
from quantpilot.models import MarketSnapshot, Signal

from .domain import ShadowConfig


class MonitoredHarness(AnalystHarness):
    llm_seconds: float = 0
    evidence: dict[str, Any] | None = None

    async def review(self, context: AnalystContext) -> tuple[AnalystOutput | None, str]:
        if self.evidence is not None:
            key, _ = request_for(context, self.provider.model_id)
            if key not in self.evidence:
                raise ValueError("Missing recorded decision LLM outcome")
            output = self.evidence[key]
            return (
                validate_output(AnalystOutput.model_validate(output).model_dump_json(), context)
                if output is not None
                else None
            ), key
        start = time.perf_counter()
        try:
            return await super().review(context)
        finally:
            self.llm_seconds = time.perf_counter() - start


class ShadowAI:
    def __init__(
        self,
        config: ShadowConfig,
        responses: Path,
        clock: Clock,
        replay: bool = True,
        token: str | None = None,
        model_path: Path | None = None,
    ):
        self.config, self.harness, self.evaluator = config, None, None
        self.model_version: str | None = None
        if config.ai_mode != "QUANT_ONLY":
            model = FrozenModel.load(model_path or Path(str(config.model_path)))
            self.model_version = model.model_version
            provider: Any = ReplayOnlyProvider(config.analyst_model_id)
            if not replay:
                if not config.llm_gateway or not token:
                    raise ValueError("Dedicated LLM gateway/token required")
                provider = JsonGatewayProvider(
                    config.llm_gateway,
                    config.analyst_model_id,
                    token,
                    timeout=config.llm_timeout_seconds,
                )
            self.harness = MonitoredHarness(
                provider,
                ResponseStore(responses),
                clock,
                replay_only=replay,
                timeout_seconds=config.llm_timeout_seconds,
                max_provider_calls=config.llm_call_budget,
            )
            self.evaluator = HybridEvaluator(model, config.research, config.ai_mode, self.harness)
        self.last_latency: dict[str, float] = {}

    async def evaluate(self, signal: Signal, snapshot: MarketSnapshot) -> dict[str, Any] | None:
        if self.evaluator is None or signal.action != "BUY":
            return None
        start = time.perf_counter()
        assert self.harness is not None
        self.harness.llm_seconds = 0
        analysis = await self.evaluator.evaluate(signal, snapshot)
        self.last_latency = {
            "ai_seconds": time.perf_counter() - start,
            "llm_seconds": self.harness.llm_seconds,
        }
        return {
            "analysis": analysis.model_dump(mode="json"),
            "candidate": self.evaluator.recommendations[-1].model_dump(mode="json"),
        }

    def identity(self) -> dict[str, Any]:
        return {
            "mode": self.config.ai_mode,
            "model_version": self.model_version,
            "analyst_model": self.config.analyst_model_id,
            "policy": "veto-only-v1",
        }


def core_version() -> str:
    root = Path(__file__).parent
    return stable_id(
        {
            "phase5": implementation_id(),
            "exclusion_policy": files("quantpilot.marketdata")
            .joinpath("excluded.json")
            .read_text(),
            "shadow": {p.name: p.read_text(encoding="utf-8") for p in sorted(root.glob("*.py"))},
        }
    )
