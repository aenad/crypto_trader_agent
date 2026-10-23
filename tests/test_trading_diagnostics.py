import asyncio
import json
from decimal import Decimal, localcontext

import pytest
from test_shadow import later, session, setup_context

from quantpilot.backtest.cli import demo_input, execute
from quantpilot.diagnostics import historical_report, shadow_report
from quantpilot.shadow.feed import WallClock
from quantpilot.shadow.service import replay_decisions


async def round_trip(path):
    cfg, first = setup_context()
    live = session(path, cfg)
    initial = live.engine.ledger.free("TMN")
    try:
        entry = await live.process(first)
        decision = entry["decisions"][0]
        assert decision["signal"]["action"] == "BUY" and decision["risk"]["allowed"]
        assert Decimal(decision["risk"]["quantity"]) > 0
        assert not live.engine.ledger.seen
        await live.process(later(first))
        assert live.engine.ledger.positions["BTC/TMN"].quantity > 0
        close_frame = later(first, 300, drop="20")
        close = await live.process(close_frame)
        assert close["decisions"][0]["signal"]["action"] == "SELL"
        assert close["decisions"][0]["risk"]["allowed"]
        await live.process(later(close_frame))
        ledger = live.engine.ledger
        assert ledger.positions["BTC/TMN"].state == "CLOSED"
        assert ledger.holding("BTC").quantity == 0 and not ledger.reserved.get("BTC", 0)
        fills = [f for f in ledger.events if f["kind"] == "FILL"]
        assert len(fills) == 2 and {f["side"] for f in fills} == {"BUY", "SELL"}
        with localcontext() as ctx:
            ctx.prec = 34
            expected = initial
            for f in fills:
                cash = Decimal(f["base_quantity"]) * Decimal(f["price"]["amount"])
                expected += cash if f["side"] == "SELL" else -cash
                expected -= Decimal(f["fee"]["amount"])
            assert ledger.free("TMN") == expected
            assert ledger.realized == expected - initial
        diagnostic = shadow_report(live.store.path)
        counts = diagnostic["counts"]
        assert counts["buy_candidates"] == counts["sell_candidates"] == 1
        assert (
            counts["risk_approvals"] == counts["orders_created"] == counts["simulated_fills"] == 2
        )
        assert counts["orders_submitted_to_simulated_execution"] == 2
        assert counts["execution_errors_observed"] == 0
        assert diagnostic["accounting_fill_count"] == 2
        replay = await replay_decisions(live.store, path / "responses", WallClock())
        assert replay["status"] == "MATCH"
        return {
            "source": "SYNTHETIC_OFFLINE_ONLY",
            "counts": counts,
            "initial_tmn": str(initial),
            "final_tmn": str(expected),
            "realized_pnl_tmn": str(ledger.realized),
            "fees_tmn": str(ledger.fees),
            "replay": replay["status"],
            "exchange_mutations": 0,
        }
    finally:
        live.store.release()


def test_existing_strategy_risk_buy_fill_sell_accounting_and_replay(tmp_path):
    result = asyncio.run(round_trip(tmp_path))
    assert result["replay"] == "MATCH"


def test_execution_failure_is_logged_without_sensitive_error_and_rolled_back(tmp_path, monkeypatch):
    async def scenario():
        cfg, first = setup_context()
        live = session(tmp_path, cfg)
        before = live.engine.dump()

        async def fail(intent):
            raise RuntimeError("PRIVATE_EXCEPTION_DO_NOT_EXPORT")

        monkeypatch.setattr(live.engine.execution, "submit", fail)
        try:
            with pytest.raises(RuntimeError):
                await live.process(first)
            assert live.engine.dump() == before
            report = shadow_report(live.store.path)
            assert report["counts"]["execution_errors_observed"] == 1
            assert report["counts"]["orders_created"] == 0
            assert report["counts"]["pending_frames"] == 1
            assert "PRIVATE_EXCEPTION" not in json.dumps(report)
            assert report["reasons"]["execution"] == {"SIMULATED_EXECUTION_FAILED": 1}
        finally:
            live.store.release()

    asyncio.run(scenario())


def test_historical_diagnostic_verifies_inputs_and_counts_recorded_decisions(tmp_path):
    raw = demo_input()
    raw["candles"]["BTC/TMN"] = raw["candles"]["BTC/TMN"][:3]
    result = asyncio.run(execute(raw))
    p = tmp_path / "report.json"
    p.write_text(json.dumps(result))
    inputs = tmp_path / "input.json"
    inputs.write_text(json.dumps(raw))
    r = historical_report(p, inputs)
    assert r["counts"]["market_events_received"] == r["counts"]["valid_market_events"] == 3
    assert r["counts"]["hold_decisions"] == 3 and r["counts"]["simulated_fills"] == 0
    assert r["counts"]["ai_skipped"] == 3
    raw["candles"]["BTC/TMN"][0]["volume"] = "999"
    inputs.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="identity mismatch"):
        historical_report(p, inputs)
