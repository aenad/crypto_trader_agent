import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal, localcontext

import pytest

from quantpilot.backtest.cli import demo_input, execute
from quantpilot.backtest.config import SimulationParameters
from quantpilot.backtest.execution import SimulatedExecutionProvider
from quantpilot.backtest.history import HistoricalClock, HistoricalMarketDataProvider
from quantpilot.backtest.ledger import PortfolioLedger
from quantpilot.backtest.replay import HistoricalReplay
from quantpilot.backtest.reports import build_report, export_report
from quantpilot.models import (
    Candle,
    DepthLevel,
    Fill,
    LiquiditySnapshot,
    MarketConstraints,
    Money,
    OrderIntent,
    OrderState,
    QuoteConversion,
)
from quantpilot.trading.config import ResearchParameters, RiskParameters

D = Decimal
NOW = datetime(2026, 10, 20, tzinfo=timezone.utc)


def fill(identifier, side, quantity, price, fee="0", pair="BTC/TMN", seconds=0):
    quote = pair.split("/")[1]
    return Fill(
        fill_id=identifier,
        client_id=identifier,
        symbol=pair,
        side=side,
        base_quantity=D(quantity),
        price=Money(amount=D(price), currency=quote),
        fee=Money(amount=D(fee), currency=quote),
        executed_at=NOW + timedelta(seconds=seconds),
    )


def candle(index=0, low="90", high="110", volume="100", opening="100"):
    end = NOW + timedelta(minutes=5 * (index + 1))
    return Candle(
        event_id=str(index),
        symbol="BTC/TMN",
        event_time=end,
        received_at=end,
        source="test",
        open_time=end - timedelta(minutes=5),
        close_time=end,
        open=D(opening),
        close=D(100),
        high=D(high),
        low=D(low),
        volume=D(volume),
        closed=True,
    )


def provider(rows=None, quotes=None, **parameters):
    market = MarketConstraints(
        symbol="BTC/TMN",
        quote="TMN",
        spot_enabled=True,
        account_enabled=True,
        quantity_step=D("0.01"),
        price_tick=D("0.01"),
        minimum_quantity=D("0.01"),
        minimum_notional=D(1),
        taker_fee_rate=D("0.001"),
    )
    return HistoricalMarketDataProvider(
        {"BTC/TMN": rows or (candle(), candle(1))},
        {"BTC/TMN": market},
        ResearchParameters(),
        SimulationParameters(**parameters),
        quotes,
    )


def test_hand_calculated_round_trip():
    ledger = PortfolioLedger(D(1000), ResearchParameters())
    ledger.apply_fill(fill("buy", "BUY", "2", "100", "2"), D(1), D(5))
    assert ledger.free("TMN") == D(798)
    assert ledger.valuation({"BTC": D(110)}) == (D(1018), D(18), D(220))
    ledger.apply_fill(fill("sell", "SELL", "2", "120", "2.4", seconds=60), D(1), D(5))
    assert ledger.realized == D("35.6")
    assert ledger.fees == D("4.4")
    assert ledger.free("TMN") == D("1035.6")
    assert ledger.trades[0]["pnl_tmn"] == "35.6"
    assert ledger.trades[0]["holding_seconds"] == "60.0"


def test_average_cost_partial_fills_and_replay():
    ledger = PortfolioLedger(D(1000), ResearchParameters())
    first = fill("one", "BUY", "1", "100", "1")
    ledger.apply_fill(first, D(1), D(5))
    ledger.apply_fill(first, D(1), D(5))
    ledger.apply_fill(fill("two", "BUY", "1", "120", "1.2", seconds=1), D(1), D(5))
    ledger.apply_fill(fill("three", "SELL", "1", "130", "1.3", seconds=2), D(1), D(5))
    assert ledger.holding("BTC").basis_tmn == D("111.1")
    assert ledger.realized == D("17.6")
    assert not ledger.trades
    ledger.apply_fill(fill("four", "SELL", "1", "90", "0.9", seconds=3), D(1), D(5))
    assert ledger.realized == D("-4.4")
    assert ledger.free("TMN") == D("995.6")
    assert len(ledger.trades) == 1
    with pytest.raises(ValueError, match="Conflicting"):
        ledger.apply_fill(first.model_copy(update={"base_quantity": D(2)}), D(1), D(5))


def test_fx_basis_is_not_double_counted():
    ledger = PortfolioLedger(D(10000), ResearchParameters())
    ledger.convert("USDT", D(10), D(100), D("0.01"), NOW)
    assert ledger.free("TMN") == D(8990)
    ledger.apply_fill(fill("b", "BUY", "1", "5", "0", pair="BTC/USDT"), D(110), D("0.1"))
    assert ledger.realized == D(45)  # 550 spent at current FX minus 505 original basis.
    ledger.apply_fill(
        fill("s", "SELL", "1", "6", "0", pair="BTC/USDT", seconds=1), D(120), D("0.1")
    )
    assert ledger.realized == D(215)  # Plus 720 - 550.
    ledger.convert("USDT", D(11), D(120), D(0), NOW + timedelta(seconds=2), True)
    assert ledger.realized == D(310)  # Remaining original USDT: 600 - 505.
    assert ledger.free("TMN") == D(10310)
    assert ledger.valuation({}) == (D(10310), D(0), D(0))


def test_rejected_accounting_is_atomic_and_reservations_prevent_overspend():
    ledger = PortfolioLedger(D(1000), ResearchParameters())
    ledger.reserve("TMN", D(950))
    with pytest.raises(ValueError):
        ledger.apply_fill(fill("b", "BUY", "1", "100"), D(1), D(5))
    assert ledger.free("TMN") == D(50)
    assert not ledger.positions
    ledger.release("TMN", D(950))
    ledger.apply_fill(fill("b", "BUY", "1", "100"), D(1), D(5))
    with pytest.raises(ValueError):
        ledger.apply_fill(fill("s", "SELL", "1", "100", "101", seconds=1), D(1), D(5))
    assert ledger.free("BTC") == D(1)
    assert ledger.free("TMN") == D(900)


def intent(identifier="order", kind="MARKET", quantity="1", price=None):
    return OrderIntent(
        client_id=identifier,
        decision_id=identifier,
        account_id="backtest",
        symbol="BTC/TMN",
        side="BUY",
        order_type=kind,
        base_quantity=D(quantity),
        limit_price=price,
    )


def test_market_next_open_partial_shared_capacity_and_cancel():
    async def scenario():
        data = provider(volume_participation=D("0.01"))
        clock = HistoricalClock(NOW + timedelta(minutes=5))
        ledger = PortfolioLedger(D(1000), data.research)
        execution = SimulatedExecutionProvider(clock, data, ledger)
        for identifier in ("a", "b"):
            execution.plan(identifier, D(5), D(110))
            await execution.submit(intent(identifier, quantity="2"))
        # Previous completed volume 100 -> shared capacity one BTC, not two per order.
        await execution.process(candle(1), True, D(1), D(100))
        assert await execution.lookup("a") == OrderState.PARTIALLY_FILLED
        assert not await execution.fills("b")
        result = (await execution.fills("a"))[0]
        assert result.executed_at == NOW + timedelta(minutes=5)
        assert result.price.amount == D("100.16")  # adverse spread/slip, round up.
        assert result.base_quantity == D(1)
        await execution.cancel("a")
        await execution.cancel("b")
        assert ledger.reserved["TMN"] == 0
        assert ledger.free("BTC") == 1

    asyncio.run(scenario())


def test_limit_requires_penetration_and_cannot_fill_signal_bar():
    async def scenario():
        data = provider(volume_participation=D("0.1"))
        clock = HistoricalClock(NOW + timedelta(minutes=5))
        ledger = PortfolioLedger(D(1000), data.research)
        execution = SimulatedExecutionProvider(clock, data, ledger)
        execution.plan("order", D(5), D(100))
        await execution.submit(intent(kind="LIMIT", price=D(95)))
        await execution.process(candle(0), False, D(1))
        assert not await execution.fills("order")
        clock.advance(NOW + timedelta(minutes=10))
        await execution.process(candle(1, low="95"), False, D(1))
        assert not await execution.fills("order")
        await execution.process(candle(1, low="94.99"), False, D(1))
        assert (await execution.fills("order"))[0].price.amount == D(95)

    asyncio.run(scenario())


def test_recorded_book_walk_partial_and_no_future_quote():
    async def scenario():
        at = NOW + timedelta(minutes=5)
        book = LiquiditySnapshot(
            as_of=at,
            bids=(DepthLevel(price=D(99), quantity=D(10)),),
            asks=(DepthLevel(price=D(101), quantity=D(2)), DepthLevel(price=D(102), quantity=D(2))),
        )
        data = provider(quotes={"BTC/TMN": (book,)}, book_participation=D("0.5"))
        assert data.recorded_quote("BTC/TMN", NOW) is None
        clock = HistoricalClock(at)
        ledger = PortfolioLedger(D(1000), data.research)
        execution = SimulatedExecutionProvider(clock, data, ledger)
        execution.plan("order", D(5), D(110))
        await execution.submit(intent(quantity="3"))
        await execution.process(candle(1), True, D(1), D(1000))
        fills = await execution.fills("order")
        assert [f.base_quantity for f in fills] == [D(1), D(1)]
        assert [f.price.amount for f in fills] == [D("101.11"), D("102.11")]
        assert await execution.lookup("order") == OrderState.PARTIALLY_FILLED

    asyncio.run(scenario())


def test_gap_above_risk_budget_cancels_instead_of_overspending():
    async def scenario():
        data = provider()
        clock = HistoricalClock(NOW + timedelta(minutes=5))
        ledger = PortfolioLedger(D(1000), data.research)
        execution = SimulatedExecutionProvider(clock, data, ledger)
        execution.plan("order", D(5), D(100))
        await execution.submit(intent())
        await execution.process(candle(1), True, D(1), D(100))
        assert await execution.lookup("order") == OrderState.CANCELED
        assert ledger.free("TMN") == 1000

    asyncio.run(scenario())


def test_clock_and_history_are_point_in_time():
    data = provider()
    clock = HistoricalClock(NOW)
    with pytest.raises(ValueError):
        clock.advance(NOW - timedelta(seconds=1))
    snap = asyncio.run(data.snapshot("BTC/TMN", NOW + timedelta(minutes=5)))
    assert len(snap.candles) == 1
    assert all(c.close_time <= snap.as_of for c in snap.candles + snap.trend_candles)
    with pytest.raises(ValueError, match="gaps"):
        provider(rows=(candle(), candle(2)))


def test_terminal_liquidation_respects_capacity_reports_residual():
    async def scenario():
        data = provider()
        replay = HistoricalReplay(data, RiskParameters(), ("BTC/TMN",))
        replay.ledger.apply_fill(fill("b", "BUY", "2", "100"), D(1), D(5))
        await replay.liquidate(NOW + timedelta(minutes=10))
        assert replay.ledger.positions["BTC/TMN"].quantity == D(1)
        assert replay.residuals[0]["quantity"] == "1.00"
        assert replay.ledger.events[-1]["price"]["amount"] == "99.65"

    asyncio.run(scenario())


def test_reproducible_replay_reports_and_future_append(tmp_path):
    raw = demo_input()
    raw["candles"]["BTC/TMN"] = raw["candles"]["BTC/TMN"][:12]
    first = asyncio.run(execute(raw))
    second = asyncio.run(execute(raw))
    assert first == second
    assert first["metrics"]["initial_capital_tmn"] == "5000000"
    assert first["metrics"]["net_return_pct"] == "0"
    assert first["metrics"]["trade_count"] == 0
    export_report(first, tmp_path)
    assert (tmp_path / "report.json").is_file()
    assert (tmp_path / "metrics.csv").is_file()
    longer = demo_input()
    longer["candles"]["BTC/TMN"] = longer["candles"]["BTC/TMN"][:15]
    extended = asyncio.run(execute(longer))
    assert extended["decisions"][:12] == first["decisions"]


def test_missing_fx_fails_closed():
    data = provider()
    replay = HistoricalReplay(data, RiskParameters(), ("BTC/TMN",))
    with pytest.raises(ValueError, match="FX"):
        replay.rate(NOW)
    replay.fx = (QuoteConversion(quote="USDT", tmn_per_unit=D(1000), as_of=NOW),)
    assert replay.rate(NOW) == 1000
    with pytest.raises(ValueError, match="stale"):
        replay.rate(NOW + timedelta(minutes=5))


def test_ledger_does_not_depend_on_callers_decimal_precision():
    outputs = []
    for precision in (8, 40):
        with localcontext() as context:
            context.prec = precision
            ledger = PortfolioLedger(D(1000), ResearchParameters())
            ledger.apply_fill(fill("b", "BUY", "2", "100", "2"), D(1), D(5))
            ledger.apply_fill(fill("s", "SELL", "2", "120", "2.4", seconds=1), D(1), D(5))
            outputs.append(ledger.realized)
    assert outputs == [D("35.6"), D("35.6")]


def active_history():
    raw = demo_input()
    rows = raw["candles"]["BTC/TMN"][:90]
    raw["candles"]["BTC/TMN"] = rows
    raw["research"] = {
        "ema_fast": 3,
        "ema_slow": 8,
        "breakout_window": 5,
        "volume_window": 5,
        "atr_period": 3,
        "adx_period": 3,
        "rsi_period": 5,
        "min_adx": "0",
        "rsi_min": "1",
        "rsi_max": "99",
    }
    for key in ("open", "high", "low", "close"):
        rows[66][key] = str(int(rows[66][key]) + 2000)
    rows[66]["volume"] = "400"
    return raw


def test_exact_phase3_engines_complete_a_repeatable_trade_without_future_leakage():
    raw = active_history()
    result = asyncio.run(execute(raw))
    assert result == asyncio.run(execute(raw))
    assert result["metrics"]["fill_count"] >= 2
    assert result["metrics"]["trade_count"] == 1
    assert any(d["signal"]["action"] == "BUY" and d["risk"]["allowed"] for d in result["decisions"])
    assert D(result["metrics"]["final_equity_tmn"]) == (
        D(5000000) + D(result["metrics"]["realized_pnl_tmn"])
    )
    assert not result["residual_positions"]
    cutoff = active_history()
    cutoff["candles"]["BTC/TMN"] = cutoff["candles"]["BTC/TMN"][:70]
    earlier = asyncio.run(execute(cutoff))
    assert earlier["decisions"] == result["decisions"][:70]


def test_hand_calculated_metrics_drawdown_and_exposure():
    replay = HistoricalReplay(provider(), RiskParameters(), ("BTC/TMN",))
    replay.ledger = PortfolioLedger(D(1000), ResearchParameters())
    replay.sample(NOW)
    replay.ledger.apply_fill(fill("b", "BUY", "2", "100", "2"), D(1), D(5))
    replay.marks["BTC"] = D(90)
    replay.sample(NOW + timedelta(seconds=10))
    replay.ledger.apply_fill(fill("s", "SELL", "2", "120", "2.4", seconds=20), D(1), D(5))
    replay.sample(NOW + timedelta(seconds=20))
    metrics = build_report(replay)["metrics"]
    assert D(metrics["net_return_pct"]) == D("3.56")
    assert D(metrics["max_drawdown_pct"]) == D("2.2")
    assert D(metrics["realized_pnl_tmn"]) == D("35.6")
    assert D(metrics["win_rate"]) == 1
    assert metrics["profit_factor"] is None
    assert D(metrics["average_holding_seconds"]) == 20
    assert D(metrics["total_fees_tmn"]) == D("4.4")
    assert abs(D(metrics["time_weighted_exposure"]) - D(180) / D(978) / 2) < D("1e-26")


def test_sell_limit_partial_fill_and_entry_exit_fee_settings():
    async def scenario():
        data = provider(entry_fee=D("0.002"), exit_fee=D("0.003"))
        clock = HistoricalClock(NOW + timedelta(minutes=5))
        ledger = PortfolioLedger(D(1000), data.research)
        ledger.apply_fill(fill("initial", "BUY", "2", "100"), D(1), D(5))
        execution = SimulatedExecutionProvider(clock, data, ledger)
        execution.plan("exit", D(5), D(105))
        order = intent("exit", "LIMIT", "2", D(105)).model_copy(update={"side": "SELL"})
        await execution.submit(order)
        clock.advance(NOW + timedelta(minutes=10))
        await execution.process(candle(1, high="105.01"), False, D(1))
        result = (await execution.fills("exit"))[0]
        assert result.base_quantity == 1
        assert result.price.amount == 105
        assert result.fee.amount == D("0.315")
        assert ledger.realized == D("4.685")

    asyncio.run(scenario())


def test_expired_orders_release_reservations():
    async def scenario():
        data = provider(order_ttl_seconds=300)
        clock = HistoricalClock(NOW)
        ledger = PortfolioLedger(D(1000), data.research)
        execution = SimulatedExecutionProvider(clock, data, ledger)
        execution.plan("order", D(5), D(110))
        await execution.submit(intent())
        clock.advance(NOW + timedelta(minutes=5))
        await execution.process(candle(1), True, D(1), D(100))
        assert await execution.lookup("order") == OrderState.CANCELED
        assert ledger.free("TMN") == 1000

    asyncio.run(scenario())


def test_cli_generates_json_csv_and_sensitivity_reports(tmp_path):
    import json
    import subprocess
    import sys

    raw = active_history()
    path = tmp_path / "input.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "quantpilot.backtest.cli",
            "--input",
            str(path),
            "--output",
            str(tmp_path / "report"),
            "--sensitivity",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    for name in ("", "double_costs", "half_capacity"):
        directory = tmp_path / "report" / name
        assert (directory / "report.json").is_file()
        assert (directory / "ledger.csv").is_file()
        assert (directory / "metrics.csv").is_file()
    baseline = json.loads((tmp_path / "report/report.json").read_text())
    expensive = json.loads((tmp_path / "report/double_costs/report.json").read_text())
    assert baseline["manifest"]["input_id"] == expensive["manifest"]["input_id"]
    assert baseline["manifest"]["config_id"] != expensive["manifest"]["config_id"]


def test_usdt_replay_retains_fx_when_no_terminal_spot_route():
    raw = demo_input()
    rows = raw["candles"].pop("BTC/TMN")[:2]
    for row in rows:
        row["symbol"] = "BTC/USDT"
    raw["candles"]["BTC/USDT"] = rows
    market = raw["markets"].pop("BTC/TMN")
    market.update(symbol="BTC/USDT", quote="USDT")
    raw["markets"]["BTC/USDT"] = market
    raw["approved"] = ["BTC/USDT"]
    raw["fx"] = [
        {"quote": "USDT", "tmn_per_unit": "1000", "as_of": timestamp}
        for timestamp in [rows[0]["open_time"]] + [r["close_time"] for r in rows]
    ]
    result = asyncio.run(execute(raw))
    metrics = result["metrics"]
    assert metrics["trade_count"] == 0
    assert len(result["ledger"]) == 1  # Explicit research funding assumption only.
    assert result["remaining_holdings"]["USDT"] != "0"
    assert not metrics["fully_settled_tmn"]
    assert result["residual_positions"] == []  # Continuous replay does not force settlement.
    # Funding fee is in the remaining quote's basis, not prematurely realized.
    assert D(metrics["realized_pnl_tmn"]) == 0
    assert abs(D(metrics["unrealized_pnl_tmn"]) + D(metrics["total_fees_tmn"])) < D("1e-20")
    assert abs(D(metrics["final_equity_tmn"]) - D(5000000) - D(metrics["unrealized_pnl_tmn"])) < D(
        "1e-20"
    )


def test_profit_factor_counts_closed_round_trips():
    replay = HistoricalReplay(provider(), RiskParameters(), ("BTC/TMN",))
    replay.ledger = PortfolioLedger(D(1000), ResearchParameters())
    replay.sample(NOW)
    for offset, price, fee in ((0, "110", "1.1"), (20, "90", "0.9")):
        replay.ledger.apply_fill(
            fill(f"b{offset}", "BUY", "1", "100", "1", seconds=offset), D(1), D(5)
        )
        replay.ledger.apply_fill(
            fill(f"s{offset}", "SELL", "1", price, fee, seconds=offset + 10), D(1), D(5)
        )
    replay.sample(NOW + timedelta(seconds=30))
    metrics = build_report(replay)["metrics"]
    assert metrics["trade_count"] == 2
    assert D(metrics["win_rate"]) == D("0.5")
    assert D(metrics["profit_factor"]) == D("7.9") / D("11.9")


def test_phase2_parquet_candles_can_feed_cli(tmp_path, monkeypatch, capsys):
    import json
    import sys

    from quantpilot.backtest.cli import main
    from quantpilot.marketdata.storage import LocalCatalog, ParquetStore

    pytest.importorskip("pyarrow")
    raw = demo_input()
    candles = [Candle.model_validate(row) for row in raw.pop("candles")["BTC/TMN"][:3]]
    store = ParquetStore(tmp_path / "data", LocalCatalog(tmp_path / "catalog"))
    manifest = store.save("candles", "BTC/TMN", candles, {"source": "offline-test"})
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps(raw), encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "quantpilot-backtest",
            "--input",
            str(metadata),
            "--parquet",
            manifest["path"],
            "--output",
            str(tmp_path / "report"),
        ],
    )
    main()
    assert (tmp_path / "report/report.json").exists()
    assert json.loads(capsys.readouterr().out)["trade_count"] == 0
