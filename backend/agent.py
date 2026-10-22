"""Checkpointed analysis workflow. Live execution is outside this graph."""
from pathlib import Path
from typing import Any, TypedDict
from uuid import uuid4

from .market_rules import check_market, normalize_pair
from .schemas import Signal
from .strategy import analyze_candles


class AgentState(TypedDict, total=False):
    symbol: str
    context: dict[str, Any]
    candles: Any
    signal: dict[str, Any]
    strategy_version: str
    execution: str


class TradingAgent:
    def __init__(self, settings, market_data, memory):
        self.settings = settings
        self.market_data = market_data
        self.memory = memory

    def build(self, checkpointer):
        from langgraph.graph import StateGraph, START, END
        from langchain_core.tools import tool

        @tool
        async def get_candles(symbol: str) -> Any:
            """Read candle data for one eligible spot pair through the configured MCP."""
            allowed, reason = check_market(symbol)
            if not allowed:
                raise ValueError(reason)
            return await self.market_data.get_candles(symbol)

        @tool
        def read_memory() -> dict:
            """Read persistent notes and recent decisions as analysis context."""
            return self.memory.context()

        @tool
        def analyze_market(symbol: str, candles: Any) -> dict:
            """Calculate the versioned EMA/RSI/volume baseline from candle data."""
            return analyze_candles(symbol, candles, self.settings).model_dump()

        async def load_context(state):
            return {"context": await read_memory.ainvoke({}),
                    "strategy_version": "ema12_26_rsi_volume_v1"}

        async def fetch_data(state):
            return {"candles": await get_candles.ainvoke({"symbol": state["symbol"]})}

        async def analyze(state):
            return {"signal": await analyze_market.ainvoke({"symbol": state["symbol"], "candles": state["candles"]})}

        def execution_gate(state):
            # No holdings schema or execution adapter exists yet. Never turn
            # analysis results or remembered decisions into order authorization.
            return {"execution": "analysis_only"}

        def record(state, config):
            self.memory.append_once(config["configurable"]["thread_id"], "decision", {
                "thread_id": config["configurable"]["thread_id"],
                "strategy_version": state["strategy_version"],
                "interval": self.settings.candle_interval,
                "signal": state["signal"], "execution": state["execution"],
            }, state["symbol"])
            return {}

        builder = StateGraph(AgentState)
        for name, node in (("load_memory", load_context), ("fetch_candles", fetch_data),
                           ("analyze_strategy", analyze), ("execution_gate", execution_gate),
                           ("record_decision", record)):
            builder.add_node(name, node)
        sequence = [START, "load_memory", "fetch_candles", "analyze_strategy", "execution_gate", "record_decision", END]
        for left, right in zip(sequence, sequence[1:]):
            builder.add_edge(left, right)
        return builder.compile(checkpointer=checkpointer)

    async def run(self, symbol: str) -> Signal:
        try:
            from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        except ImportError as exc:
            raise RuntimeError("Install requirements.txt to enable the LangGraph agent") from exc
        normalized = normalize_pair(symbol)
        allowed, reason = check_market(normalized)
        if not allowed:
            raise ValueError(reason)
        Path(self.settings.graph_db_path).parent.mkdir(parents=True, exist_ok=True)
        # Each market observation gets its own thread. Fresh runs never reuse
        # stale candle data from a previous analysis.
        thread_id = str(uuid4())
        async with AsyncSqliteSaver.from_conn_string(self.settings.graph_db_path) as saver:
            graph = self.build(saver)
            result = await graph.ainvoke({"symbol": normalized},
                {"configurable": {"thread_id": thread_id}})
        return Signal.model_validate(result["signal"])
