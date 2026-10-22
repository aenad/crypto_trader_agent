from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .market_data import MarketDataService
from .market_rules import check_market, parse_pair
from .mcp_client import MCPUnavailable, WallexMCP
from .schemas import HealthResponse, Market, OrderIntent, OrderResult, Signal
from .agent import TradingAgent
from .memory import AgentMemory


settings = get_settings()
mcp = WallexMCP(settings)
market_data = MarketDataService(settings, mcp)
memory = AgentMemory(settings.memory_db_path)
agent = TradingAgent(settings, market_data, memory)


@asynccontextmanager
async def lifespan(_: FastAPI):
    memory.append("startup", {
        "mode": settings.trading_mode,
        "strategy_version": "ema12_26_rsi_volume_v1",
        "risk_per_trade": settings.risk_per_trade,
        "max_order_quote": settings.max_order_quote,
        "max_daily_loss": settings.max_daily_loss,
    })
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health():
    try:
        await mcp.list_tools()
        connected, message = True, "MCP متصل است؛ اجرای سفارش واقعی همچنان با تنظیمات ایمن کنترل می‌شود."
    except Exception as exc:
        connected, message = False, f"MCP در دسترس نیست: {exc}"
    return HealthResponse(
        status="ok" if connected else "degraded", mcp_connected=connected,
        trading_mode=settings.trading_mode, live_trading_enabled=settings.live_trading_enabled,
        message=message,
    )


@app.get("/api/mcp/tools")
async def list_mcp_tools():
    try:
        return {"roles": await market_data.discover(), "all": await market_data.tools()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/markets", response_model=list[Market])
async def markets():
    try:
        payload = await market_data.get_markets()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    rows = payload if isinstance(payload, list) else payload.get("markets", payload.get("data", [])) if isinstance(payload, dict) else []
    result = []
    for row in rows:
        if isinstance(row, str):
            symbol, raw = row, {"symbol": row}
        elif isinstance(row, dict):
            symbol = str(row.get("symbol") or row.get("pair") or row.get("market") or row.get("name") or "")
            raw = row
        else:
            continue
        if not symbol:
            continue
        allowed, reason = check_market(symbol)
        base, quote = parse_pair(symbol)
        result.append(Market(symbol=symbol, base=base, quote=quote, eligible=allowed, reason=reason, raw=raw))
    return result


@app.get("/api/signals", response_model=list[Signal])
async def signals(limit: int = 30):
    try:
        payload = await market_data.get_markets()
        rows = payload if isinstance(payload, list) else payload.get("markets", payload.get("data", [])) if isinstance(payload, dict) else []
        symbols = []
        for row in rows:
            symbol = row if isinstance(row, str) else (row.get("symbol") or row.get("pair") or row.get("market") or "") if isinstance(row, dict) else ""
            allowed, _ = check_market(str(symbol)) if symbol else (False, "")
            if allowed:
                symbols.append(str(symbol))
        results = []
        for symbol in symbols[: max(1, min(limit, settings.signal_limit))]:
            try:
                results.append(await agent.run(symbol))
            except Exception as exc:
                results.append(Signal(symbol=symbol, action="hold", confidence=0, reasons=[f"دادهٔ کندل دریافت نشد: {exc}"], timestamp="", mode=settings.trading_mode))
        return results
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/signals/{symbol:path}", response_model=Signal)
async def signal_for_market(symbol: str):
    allowed, reason = check_market(symbol)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)
    try:
        return await agent.run(symbol)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/balance")
async def balance():
    try:
        return await market_data.get_balance()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/api/ticker/{symbol:path}")
async def ticker(symbol: str):
    allowed, reason = check_market(symbol)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)
    try:
        return await market_data.get_ticker(symbol)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/orders", response_model=OrderResult)
async def create_order(intent: OrderIntent):
    allowed, reason = check_market(intent.symbol)
    if not allowed:
        raise HTTPException(status_code=400, detail=reason)
    if intent.market_type != "spot" or intent.leverage != 1:
        raise HTTPException(status_code=400, detail="فقط سفارش اسپات و بدون لوریج پذیرفته می‌شود.")
    if settings.trading_mode != "live" or not settings.live_trading_enabled:
        result = OrderResult(
            accepted=False, mode=settings.trading_mode, symbol=intent.symbol, side=intent.side,
            amount=intent.amount, reason="حالت امن فعال است؛ سفارش فقط به‌صورت shadow ثبت می‌شود و ابزار MCP سفارش پیکربندی/فعال نشده است.",
        )
        memory.append("order_rejected", {"intent": intent.model_dump(), "result": result.model_dump()}, intent.symbol)
        return result
    # Intentionally fail closed until an exact order tool and its argument schema are configured.
    raise HTTPException(status_code=501, detail="اتصال سفارش زنده فعال نشده است؛ نام ابزار و schema ابزار سفارش MCP باید صریحاً پیکربندی و بازبینی شود.")


class MemoryNote(BaseModel):
    key: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    value: str = Field(min_length=1, max_length=4000)


@app.get("/api/memory/events")
async def memory_events(kind: str | None = None, symbol: str | None = None,
                        limit: int = Query(default=50, ge=1, le=200)):
    return memory.history(kind, symbol, limit)


@app.get("/api/memory/context")
async def memory_context():
    return memory.context()


@app.post("/api/memory/notes")
async def save_memory_note(note: MemoryNote):
    memory.set_note(note.key, note.value)
    return {"saved": True, "key": note.key}


@app.get("/api/account/summary")
async def account_summary():
    try:
        return await market_data.get_balance()
    except MCPUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
