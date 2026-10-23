"""Credential-isolated hybrid evaluator construction, shared by execution services."""

from pathlib import Path
from typing import Literal, Self

from pydantic import SecretStr, model_validator

from quantpilot.interfaces import Clock
from quantpilot.models import DomainModel
from quantpilot.trading.config import ResearchParameters

from .analyst import AnalystHarness, JsonGatewayProvider, ReplayOnlyProvider, ResponseStore
from .fusion import HybridEvaluator
from .learning import FrozenModel


class HybridRuntimeConfig(DomainModel):
    mode: Literal["QUANT_ONLY", "QUANT_ML", "QUANT_ML_LLM"] = "QUANT_ONLY"
    model_path: str | None = None
    analyst_model_id: str = "unconfigured"
    gateway: str | None = None
    timeout_seconds: int = 10
    call_budget: int = 100

    @model_validator(mode="after")
    def valid(self) -> Self:
        if not 1 <= self.timeout_seconds <= 60 or not 1 <= self.call_budget <= 10000:
            raise ValueError("Invalid analyst budgets")
        if self.mode != "QUANT_ONLY" and not self.model_path:
            raise ValueError("Frozen model artifact required for hybrid mode")
        if self.mode == "QUANT_ML_LLM" and self.analyst_model_id == "unconfigured":
            raise ValueError("Explicit analyst model required")
        return self


def build_evaluator(
    config: HybridRuntimeConfig,
    research: ResearchParameters,
    responses: Path,
    clock: Clock,
    *,
    replay_only: bool = True,
    token: SecretStr | None = None,
) -> HybridEvaluator | None:
    if config.mode == "QUANT_ONLY":
        return None
    model = FrozenModel.load(Path(str(config.model_path)))
    harness = None
    if config.mode == "QUANT_ML_LLM":
        if replay_only:
            provider = ReplayOnlyProvider(config.analyst_model_id)
            harness = AnalystHarness(
                provider,
                ResponseStore(responses),
                clock,
                replay_only=True,
                timeout_seconds=config.timeout_seconds,
                max_provider_calls=config.call_budget,
            )
        else:
            if not config.gateway or token is None or not token.get_secret_value():
                raise ValueError("Dedicated LLM gateway and token required")
            harness = AnalystHarness(
                JsonGatewayProvider(
                    config.gateway,
                    config.analyst_model_id,
                    token.get_secret_value(),
                    config.timeout_seconds,
                ),
                ResponseStore(responses),
                clock,
                replay_only=False,
                timeout_seconds=config.timeout_seconds,
                max_provider_calls=config.call_budget,
            )
    return HybridEvaluator(model, research, config.mode, harness)
