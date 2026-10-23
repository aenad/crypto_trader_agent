"""Secret-free core settings and canonical identifiers."""

import hashlib
import json
import os
from enum import Enum
from typing import Mapping, Self

from pydantic import model_validator

from quantpilot.profiles import ProfileConfig
from quantpilot.spot import SpotPolicy


class ExecutionMode(str, Enum):
    BACKTEST = "BACKTEST"
    SHADOW = "SHADOW"
    LIVE = "LIVE"


def stable_id(value: object) -> str:
    canonical = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode()).hexdigest()


class EngineConfig(ProfileConfig):
    trading: SpotPolicy = SpotPolicy()
    mode: ExecutionMode = ExecutionMode.SHADOW
    strategy_version: str = "phase1-placeholder"
    schema_version: str = "1"
    live_execution_enabled: bool = False

    @model_validator(mode="after")
    def forbid_live_execution(self) -> Self:
        if self.live_execution_enabled:
            raise ValueError("Live execution cannot be enabled in Phase 1")
        return self

    @property
    def config_id(self) -> str:
        return stable_id(self.model_dump(mode="json"))

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> Self:
        env = os.environ if environ is None else environ
        raw = env.get("QUANTPILOT_LIVE_EXECUTION_ENABLED", "false").lower()
        if raw not in ("true", "false"):
            raise ValueError("QUANTPILOT_LIVE_EXECUTION_ENABLED must be true or false")
        return cls(
            operating_profile=env.get("QUANTPILOT_OPERATING_PROFILE", "CONTINUOUS").upper(),
            mode=ExecutionMode(env.get("QUANTPILOT_MODE", "SHADOW").upper()),
            live_execution_enabled=raw == "true",
        )
