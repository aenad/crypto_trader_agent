from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from quantpilot.live.settings import WallexConnectionSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", populate_by_name=True,
    )

    
    app_name: str = "Nova Trading Engine"
    mcp_transport: str = "streamable_http"
    mcp_url: Literal["https://api.wallex.ir/mcp"] = Field(
        default="https://api.wallex.ir/mcp",
        validation_alias=AliasChoices("WALLEX_MCP_URL", "MCP_URL"),
    )
    mcp_command: str = ""
    mcp_args: str = "[]"
    mcp_env_json: str = "{}"
    mcp_bearer_token: str = ""
    wallex_api_key: SecretStr = SecretStr("")
    wallex_api_base: Literal["https://api.wallex.ir"] = "https://api.wallex.ir"
    wallex_ws_url: Literal["wss://api.wallex.ir/connection/websocket"] = (
        "wss://api.wallex.ir/connection/websocket"
    )
    wallex_sub_account_client_id: SecretStr = Field(default=SecretStr(""), exclude=True, repr=False)
    mcp_tools_markets: str = ""
    mcp_tools_ticker: str = ""
    mcp_tools_candles: str = ""
    mcp_tools_balance: str = ""
    mcp_tools_orders: str = ""
    trading_mode: str = "shadow"
    live_trading_enabled: bool = False
    max_order_quote: float = 250_000
    max_daily_loss: float = 150_000
    risk_per_trade: float = 0.005
    signal_interval_seconds: int = 30
    signal_limit: int = 30
    candle_interval: str = "15m"
    memory_db_path: str = "data/agent_memory.sqlite3"
    graph_db_path: str = "data/agent_checkpoints.sqlite3"

    @field_validator("wallex_api_key", "wallex_sub_account_client_id")
    @classmethod
    def safe_private_header(cls, value: SecretStr) -> SecretStr:
        return WallexConnectionSettings.safe_header(value)

    @field_validator("wallex_sub_account_client_id")
    @classmethod
    def safe_sub_account(cls, value: SecretStr) -> SecretStr:
        return WallexConnectionSettings.valid_id(value)


@lru_cache
def get_settings() -> Settings:
    return Settings()
