"""Allowlisted Wallex connection settings; never an execution authorization."""

import os
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Final, Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

API_BASE: Final = "https://api.wallex.ir"
WS_URL: Final = "wss://api.wallex.ir/connection/websocket"
MCP_URL: Final = "https://api.wallex.ir/mcp"
FIELDS = {
    "WALLEX_API_BASE": "api_base",
    "WALLEX_WS_URL": "ws_url",
    "WALLEX_MCP_URL": "mcp_url",
    "WALLEX_API_KEY": "api_key",
    "WALLEX_SUB_ACCOUNT_CLIENT_ID": "sub_account_client_id",
}


class WallexConnectionSettings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    api_base: Literal["https://api.wallex.ir"] = API_BASE
    ws_url: Literal["wss://api.wallex.ir/connection/websocket"] = WS_URL
    mcp_url: Literal["https://api.wallex.ir/mcp"] = MCP_URL
    api_key: SecretStr = Field(default=SecretStr(""), exclude=True, repr=False)
    sub_account_client_id: SecretStr = Field(default=SecretStr(""), exclude=True, repr=False)

    @field_validator("api_key", "sub_account_client_id")
    @classmethod
    def safe_header(cls, value: SecretStr) -> SecretStr:
        if any(ord(c) <= 32 or ord(c) == 127 for c in value.get_secret_value()):
            raise ValueError("INVALID_PRIVATE_HEADER")
        return value

    @field_validator("sub_account_client_id")
    @classmethod
    def valid_id(cls, value: SecretStr) -> SecretStr:
        raw = value.get_secret_value()
        if raw and not re.fullmatch(r"[A-Za-z0-9_-]{1,200}", raw):
            raise ValueError("INVALID_SUB_ACCOUNT_ID")
        return value

    def private_headers(self, *, sub_account_context: bool = False) -> dict[str, str]:
        """Explicit read context only; neither header proves order-account ownership."""
        key = self.api_key.get_secret_value()
        if not key:
            raise ValueError("WALLEX_API_KEY_REQUIRED")
        headers = {"X-API-Key": key}
        if sub_account_context:
            identity = self.sub_account_client_id.get_secret_value()
            if not identity:
                raise ValueError("SUB_ACCOUNT_CLIENT_ID_REQUIRED")
            headers["sub-account-client-id"] = identity
        return headers


def load_wallex_settings(
    env_file: Path | None = Path(".env"),
    environ: Mapping[str, str] | None = None,
) -> WallexConnectionSettings:
    """Process canonical > process legacy MCP_URL > file canonical > file alias.

    Reads only the five Wallex keys and MCP_URL compatibility alias. Does not
    export variables, interpolate values or load LLM/activation credentials.
    """
    try:
        values: dict[str, str] = {}
        allowed = set(FIELDS) | {"MCP_URL"}
        if env_file is not None and env_file.is_file():
            if env_file.stat().st_size > 1024 * 1024:
                raise ValueError("ENV_FILE_TOO_LARGE")
            for line in env_file.read_text(encoding="utf-8-sig").splitlines():
                match = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$", line)
                if not match or match[1] not in allowed:
                    continue
                if match[1] in values:
                    raise ValueError("DUPLICATE_WALLEX_SETTING")
                raw = match[2].strip()
                if raw.startswith(("'", '"')):
                    end = raw.rfind(raw[0])
                    tail = raw[end + 1 :].strip()
                    if end == 0 or (tail and not tail.startswith("#")):
                        raise ValueError("INVALID_ENV_LITERAL")
                    raw = raw[1:end]
                else:
                    raw = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
                values[match[1]] = raw
        process = os.environ if environ is None else environ
        mcp = process.get(
            "WALLEX_MCP_URL",
            process.get("MCP_URL", values.get("WALLEX_MCP_URL", values.get("MCP_URL", MCP_URL))),
        )
        values.update({key: process[key] for key in FIELDS if key in process})
        payload = {field: values[key] for key, field in FIELDS.items() if key in values}
        payload["mcp_url"] = mcp
        return WallexConnectionSettings.model_validate(payload)
    except (ValueError, OSError, TypeError):
        # Do not expose Pydantic input values, source lines, URLs or credentials.
        raise ValueError(
            "Invalid Wallex settings; check the documented connection fields"
        ) from None
