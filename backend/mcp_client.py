"""Small async MCP client supporting Streamable HTTP and stdio transports."""
import json
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from .config import Settings


class MCPUnavailable(RuntimeError):
    pass


class WallexMCP:
    def __init__(self, settings: Settings, *, sub_account_context: bool = False):
        self.settings = settings
        self.sub_account_context = sub_account_context

    def http_headers(self) -> dict[str, str]:
        headers = {}
        if self.settings.mcp_bearer_token:
            headers["Authorization"] = f"Bearer {self.settings.mcp_bearer_token}"
        api_key = self.settings.wallex_api_key.get_secret_value()
        if api_key:
            headers["X-API-Key"] = api_key
        if self.sub_account_context:
            identity = self.settings.wallex_sub_account_client_id.get_secret_value()
            if not api_key or not identity:
                raise MCPUnavailable("Key and sub-account ID required for explicit read context")
            headers["sub-account-client-id"] = identity
        return headers

    @asynccontextmanager
    async def session(self) -> AsyncIterator[Any]:
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
            from mcp.client.streamable_http import streamablehttp_client
        except ImportError as exc:
            raise MCPUnavailable("پکیج MCP نصب نیست؛ ابتدا pip install -r requirements.txt را اجرا کنید.") from exc
        if self.settings.mcp_transport == "stdio":
            if not self.settings.mcp_command:
                raise MCPUnavailable("MCP_COMMAND is not configured")
            try:
                args = json.loads(self.settings.mcp_args)
                env = json.loads(self.settings.mcp_env_json)
            except json.JSONDecodeError as exc:
                raise MCPUnavailable(f"Invalid MCP_ARGS or MCP_ENV_JSON: {exc}") from exc
            params = StdioServerParameters(command=self.settings.mcp_command, args=args, env=env or None)
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    yield session
            return

        if self.settings.mcp_transport != "streamable_http":
            raise MCPUnavailable("MCP_TRANSPORT must be streamable_http or stdio")
        headers = self.http_headers() or None
        async with streamablehttp_client(self.settings.mcp_url, headers=headers) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                yield session

    async def list_tools(self) -> list[dict[str, Any]]:
        async with self.session() as session:
            result = await session.list_tools()
            return [{"name": tool.name, "description": tool.description, "input_schema": tool.inputSchema} for tool in result.tools]

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        # Legacy API is read-only. Private order execution exists solely in
        # quantpilot.live behind independently configured authorization.
        allowed = {
            "wallex_spot_get_markets", "wallex_basic_get_markets",
            "wallex_basic_candle_history", "wallex_basic_get_latest_trades",
            "wallex_basic_get_market_depth", "wallex_spot_get_depth",
            "wallex_basic_get_account_balances", "wallex_basic_get_account_fees",
            "wallex_spot_get_orders", "wallex_spot_get_open_order",
            "wallex_spot_get_orders_client",
        }
        if name not in allowed:
            raise MCPUnavailable("Tool is outside the approved read-only spot allowlist")
        async with self.session() as session:
            result = await session.call_tool(name, arguments or {})
            if result.isError:
                raise MCPUnavailable(f"MCP tool {name!r} returned an error")
            structured = getattr(result, "structuredContent", None)
            if structured is not None:
                return structured
            values = []
            for item in result.content:
                if getattr(item, "type", None) == "text":
                    try:
                        values.append(json.loads(item.text))
                    except json.JSONDecodeError:
                        values.append(item.text)
            return values[0] if len(values) == 1 else values
