from functools import lru_cache
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    
    app_name: str = "Nova Trading Engine"
    mcp_transport: str = "streamable_http"
    mcp_url: str = "https://api.wallex.ir/mcp"
    mcp_command: str = ""
    mcp_args: str = "[]"
    mcp_env_json: str = "{}"
    mcp_bearer_token: str = ""
    wallex_api_key: SecretStr = SecretStr("")
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
