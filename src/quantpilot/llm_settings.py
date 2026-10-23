"""Allowlisted LLM settings; no global dotenv loading or exchange credentials."""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from quantpilot.shadow.domain import ShadowConfig

FIELDS = {
    "QUANTPILOT_LLM_GATEWAY": "llm_gateway",
    "QUANTPILOT_LLM_MODEL_ID": "analyst_model_id",
    "QUANTPILOT_LLM_TIMEOUT_SECONDS": "llm_timeout_seconds",
    "QUANTPILOT_LLM_CALL_BUDGET": "llm_call_budget",
}
TOKEN = "QUANTPILOT_LLM_TOKEN"
ALLOWED = frozenset((*FIELDS, TOKEN))


class LLMSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    token: SecretStr = Field(default=SecretStr(""), exclude=True, repr=False)
    overrides: dict[str, str | int] = Field(default_factory=dict, repr=False)


def _literal(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')):
        quote = value[0]
        end = value.rfind(quote)
        if end == 0 or (value[end + 1 :].strip() and not value[end + 1 :].strip().startswith("#")):
            raise ValueError("INVALID_LLM_ENV_LITERAL")
        return value[1:end]
    return re.split(r"\s+#", value, maxsplit=1)[0].strip()


def load_llm_settings(
    env_file: Path | None = Path(".env"),
    environ: Mapping[str, str] | None = None,
) -> LLMSettings:
    """Process env > dotenv > JSON. Empty non-secret values leave JSON unchanged.

    File values are literal (no shell execution, interpolation, or multiline strings).
    An explicitly empty process token overrides a file token and disables its use.
    """
    try:
        values: dict[str, str] = {}
        if env_file is not None and env_file.exists():
            if env_file.stat().st_size > 1024 * 1024:
                raise ValueError("ENV_FILE_TOO_LARGE")
            for line in env_file.read_text(encoding="utf-8-sig").splitlines():
                match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
                if match and match[1] in ALLOWED:
                    if match[1] in values:
                        raise ValueError("DUPLICATE_LLM_SETTING")
                    values[match[1]] = _literal(match[2])
        process = os.environ if environ is None else environ
        values.update({key: process[key] for key in ALLOWED if key in process})
        overrides: dict[str, str | int] = {}
        for key, field in FIELDS.items():
            value = values.get(key, "").strip()
            if not value:
                continue
            if any(ord(char) < 32 or ord(char) == 127 for char in value):
                raise ValueError("CONTROL_CHARACTER_IN_SETTING")
            overrides[field] = (
                int(value) if field in {"llm_timeout_seconds", "llm_call_budget"} else value
            )
        if "llm_gateway" in overrides:
            url = urlsplit(str(overrides["llm_gateway"]))
            host = (url.hostname or "").lower()
            port = url.port
            if (
                url.scheme != "https"
                or not host
                or url.username
                or url.password
                or url.query
                or url.fragment
                or host == "wallex.ir"
                or host.endswith(".wallex.ir")
                or any(char.isspace() for char in url.netloc)
                or (port is not None and not 1 <= port <= 65535)
            ):
                raise ValueError("APPROVED_HTTPS_GATEWAY_REQUIRED")
        token = values.get(TOKEN, "")
        if token and not token.strip():
            raise ValueError("INVALID_TOKEN")
        if any(ord(char) < 32 or ord(char) == 127 for char in token):
            raise ValueError("INVALID_TOKEN")
        return LLMSettings(token=SecretStr(token), overrides=overrides)
    except (ValueError, OSError, TypeError):
        # Never propagate raw file lines, invalid URLs, credential values or validation inputs.
        raise ValueError(
            "Invalid LLM environment configuration; check the documented LLM fields"
        ) from None


def configure_shadow(
    raw: dict[str, Any],
    settings: LLMSettings,
    *,
    allow_network: bool,
) -> ShadowConfig:
    try:
        config = ShadowConfig.model_validate({**raw, **settings.overrides})
        if allow_network and (
            config.ai_mode != "QUANT_ML_LLM"
            or not config.llm_gateway
            or not config.analyst_model_id.strip()
            or config.analyst_model_id == "unconfigured"
            or not settings.token.get_secret_value()
        ):
            raise ValueError("INCOMPLETE_NETWORK_CONFIGURATION")
        return config
    except (ValueError, TypeError):
        raise ValueError(
            "Invalid SHADOW/LLM settings; real calls require QUANT_ML_LLM, a frozen model, "
            "gateway, model ID and dedicated LLM token"
        ) from None
