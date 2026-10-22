import time
from typing import Any
from .market_rules import normalize_pair, check_market
from .config import Settings
from .mcp_client import MCPUnavailable, WallexMCP


ROLE_TOOLS = {
    "markets": "wallex_spot_get_markets",
    "ticker": "wallex_basic_get_latest_trades",
    "candles": "wallex_basic_candle_history",
    "balance": "wallex_basic_get_account_balances",
    "orders": "wallex_spot_get_orders",
}


class MarketDataService:
    def __init__(self, settings: Settings, client: WallexMCP):
        self.settings = settings
        self.client = client
        self._tools: list[dict[str, Any]] = []

    async def tools(self, refresh: bool = False) -> list[dict[str, Any]]:
        if not self._tools or refresh:
            self._tools = await self.client.list_tools()
        return self._tools

    async def discover(self) -> dict[str, list[dict[str, Any]]]:
        tools = await self.tools()
        return {role: [tool for tool in tools if tool["name"] == name] for role, name in ROLE_TOOLS.items()}

    async def call_role(self, role: str, arguments: dict[str, Any] | None = None) -> Any:
        mapping = await self.discover()
        candidates = mapping.get(role, [])
        if not candidates:
            raise MCPUnavailable(f"No MCP tool discovered for role {role!r}; configure MCP_TOOLS_{role.upper()}.")
        if len(candidates) != 1:
            raise MCPUnavailable(
                f"Multiple MCP tools may provide {role!r}; configure the exact tool name in MCP_TOOLS_{role.upper()} "
                f"(discovered: {', '.join(item['name'] for item in candidates)})."
            )
        tool = candidates[0]
        args = arguments or {}
        schema = tool["input_schema"]
        if set(schema.get("required", [])) - args.keys():
            raise MCPUnavailable(f"Required arguments missing for {tool['name']}")
        if schema.get("additionalProperties") is False and args.keys() - schema.get("properties", {}).keys():
            raise MCPUnavailable(f"Unexpected arguments for {tool['name']}")
        return await self.client.call_tool(tool["name"], args)

    async def get_markets(self) -> Any:
        payload = await self.call_role("markets")
        while isinstance(payload, dict):
            nested = next((payload[key] for key in ("result", "symbols", "markets", "data") if key in payload), None)
            if nested is None:
                payload = [{**row, "symbol": row.get("symbol", key)} for key, row in payload.items() if isinstance(row, dict)]
                break
            payload = nested
        if not isinstance(payload, list):
            raise MCPUnavailable("Unexpected Wallex markets response")
        return [{**row, "symbol": normalize_pair(str(row.get("symbol", "")))}
                if isinstance(row, dict) else {"symbol": normalize_pair(row)}
                for row in payload if isinstance(row, (dict, str))]

    async def get_ticker(self, symbol: str) -> Any:
        return {"symbol": normalize_pair(symbol), "price_kind": "recent_trades",
                "received_at": int(time.time()),
                "data": await self.call_role("ticker", {"symbol": self.wire_symbol(symbol)})}

    @staticmethod
    def wire_symbol(symbol: str) -> str:
        normalized = normalize_pair(symbol)
        allowed, reason = check_market(normalized)
        if not allowed:
            raise ValueError(reason)
        return normalized.replace("/", "")

    async def get_candles(self, symbol: str, interval: str | None = None, limit: int | None = None) -> Any:
        intervals = {"1m": ("1", 60), "5m": ("5", 300), "15m": ("15", 900),
                     "30m": ("30", 1800), "1h": ("60", 3600), "4h": ("240", 14400), "1d": ("D", 86400)}
        chosen = interval or self.settings.candle_interval
        if chosen not in intervals:
            raise ValueError(f"Unsupported candle interval: {chosen}")
        resolution, seconds = intervals[chosen]
        end = int(time.time()) // seconds * seconds
        return await self.call_role("candles", {
            "symbol": self.wire_symbol(symbol), "resolution": resolution,
            "from": end - seconds * (limit or 200), "to": end - 1,
        })

    async def get_balance(self) -> Any:
        return await self.call_role("balance")
