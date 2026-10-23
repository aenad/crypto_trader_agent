"""Public-only transport adapters; no credentials or mutation methods."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, TypeVar

import httpx
from jsonschema import validate

T = TypeVar("T")
TOOLS = {
    "markets": "wallex_spot_get_markets",
    "candles": "wallex_basic_candle_history",
    "book": "wallex_basic_get_market_depth",
    "trades": "wallex_basic_get_latest_trades",
}
PATHS = {
    "markets": "/hector/web/v1/markets",
    "candles": "/v1/udf/history",
    "book": "/v1/depth",
    "trades": "/v1/trades",
}


class RateLimited(Exception):
    def __init__(self, delay: float):
        self.delay = min(max(delay, 0), 120)


async def retry(
    operation: Callable[[], Awaitable[T]],
    attempts: int = 4,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    for attempt in range(attempts):
        try:
            return await operation()
        except (RateLimited, httpx.TransportError, httpx.HTTPStatusError, OSError) as exc:
            if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                raise
            if attempt == attempts - 1:
                raise RuntimeError("Public data retry budget exhausted") from None
            await sleep(exc.delay if isinstance(exc, RateLimited) else min(2**attempt, 30))
    raise RuntimeError("Invalid retry budget")


class RestPublic:
    source = "wallex-rest"

    def __init__(self, client: httpx.AsyncClient):
        self.client = client
        self.lock = asyncio.Lock()

    async def request(self, kind: str, args: dict[str, Any]) -> Any:
        if kind not in PATHS:
            raise ValueError("Unsupported read operation")

        async def read() -> Any:
            async with self.lock:
                await asyncio.sleep(0.25)
                response = await self.client.get(PATHS[kind], params=args)
            if response.status_code == 429:
                header = response.headers.get("Retry-After", "1")
                try:
                    delay = float(header)
                except ValueError:
                    from email.utils import parsedate_to_datetime

                    delay = (
                        parsedate_to_datetime(header) - datetime.now(timezone.utc)
                    ).total_seconds()
                raise RateLimited(delay)
            response.raise_for_status()
            return json.loads(response.text, parse_float=Decimal)

        return await retry(read)


class MCPPublic:
    source = "wallex-mcp"

    def __init__(self, session: Any):
        self.session = session
        self.metadata: dict[str, Any] = {}
        self.lock = asyncio.Lock()

    async def discover(self, destination: Path) -> None:
        tools: list[dict[str, Any]] = []
        cursor = None
        seen = set()
        while True:
            page = await self.session.list_tools(cursor=cursor)
            tools.extend(
                {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in page.tools
            )
            cursor = page.nextCursor
            if not cursor:
                break
            if cursor in seen:
                raise ValueError("MCP pagination cursor repeated")
            seen.add(cursor)
        self.metadata = {tool["name"]: tool for tool in tools}
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(
                {
                    "endpoint": "https://api.wallex.ir/mcp",
                    "verified_at": datetime.now(timezone.utc).isoformat(),
                    "tools": tools,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    async def request(self, kind: str, args: dict[str, Any]) -> Any:
        if kind not in TOOLS:
            raise ValueError("Unsupported public MCP operation")
        name = TOOLS[kind]
        metadata = self.metadata.get(name)
        if metadata is None or "STATE-CHANGING" in (metadata.get("description") or ""):
            raise ValueError("Public tool has not been verified in this session")
        validate(args, metadata["input_schema"])
        async with self.lock:
            await asyncio.sleep(0.25)
            result = await asyncio.wait_for(self.session.call_tool(name, args), timeout=30)
        if result.isError:
            raise ValueError("Public MCP tool reported an error")
        for item in result.content:
            if getattr(item, "type", None) == "text":
                try:
                    payload = json.loads(item.text, parse_float=Decimal)
                    if isinstance(payload, dict) and payload.get("success") is False:
                        raise ValueError("Public MCP response reports failure")
                    return payload
                except json.JSONDecodeError:
                    continue
        if result.structuredContent is not None:
            if result.structuredContent.get("success") is False:
                raise ValueError("Public MCP response reports failure")
            return result.structuredContent
        raise ValueError("MCP response has no structured data")


class MCPConnection:
    """Re-establish public sessions on transient failures; never load account keys."""

    source = "wallex-mcp"

    def __init__(self, metadata_path: Path):
        self.metadata_path = metadata_path

    async def request(self, kind: str, args: dict[str, Any]) -> Any:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamablehttp_client

        async def operation() -> Any:
            try:
                async with streamablehttp_client("https://api.wallex.ir/mcp") as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        adapter = MCPPublic(session)
                        await adapter.discover(self.metadata_path)
                        if kind == "discover":
                            return {"tools": len(adapter.metadata)}
                        return await adapter.request(kind, args)
            except BaseExceptionGroup as exc:
                pending: list[BaseException] = list(exc.exceptions)
                while pending:
                    item = pending.pop()
                    if isinstance(item, BaseExceptionGroup):
                        pending.extend(item.exceptions)
                    elif isinstance(item, httpx.HTTPStatusError):
                        if item.response.status_code == 429:
                            raise RateLimited(2) from None
                        raise item from None
                    elif isinstance(item, (httpx.TransportError, OSError)):
                        raise item from None
                raise RuntimeError("MCP public session failed") from None

        return await retry(operation)
