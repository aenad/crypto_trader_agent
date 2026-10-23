"""Offline JSON history replay and conservative sensitivity scenarios."""

import argparse
import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from quantpilot.models import Candle, LiquiditySnapshot, MarketConstraints, QuoteConversion
from quantpilot.trading.config import ResearchParameters, RiskParameters

from .config import SimulationParameters
from .history import HistoricalMarketDataProvider
from .replay import HistoricalReplay
from .reports import export_report

D = Decimal


def demo_input() -> dict[str, Any]:
    """Synthetic history; useful for mechanics, never profitability evidence."""
    start = datetime(2026, 10, 20, tzinfo=timezone.utc)
    rows = []
    for i in range(720):
        price = D(100000) + D(i) * 100 + (D(700) if i % 2 else D(-700))
        if i == 660:
            price += D(2000)
        close = start + timedelta(minutes=5 * (i + 1))
        rows.append(
            Candle(
                event_id=f"demo:{i}",
                symbol="BTC/TMN",
                event_time=close,
                received_at=close,
                source="synthetic",
                open_time=close - timedelta(minutes=5),
                close_time=close,
                open=price,
                high=price + 200,
                low=price - 200,
                close=price,
                volume=D(400) if i == 660 else D(200),
                closed=True,
            ).model_dump(mode="json")
        )
    market = MarketConstraints(
        symbol="BTC/TMN",
        quote="TMN",
        spot_enabled=True,
        account_enabled=True,
        quantity_step=D("0.001"),
        price_tick=D(1),
        minimum_quantity=D("0.001"),
        minimum_notional=D(100),
        taker_fee_rate=D("0.001"),
    )
    return {
        "candles": {"BTC/TMN": rows},
        "markets": {"BTC/TMN": market.model_dump(mode="json")},
        "approved": ["BTC/TMN"],
    }


async def execute(
    raw: dict[str, Any], simulation: SimulationParameters | None = None
) -> dict[str, Any]:
    research = ResearchParameters.model_validate(raw.get("research", {}))
    risk = RiskParameters.model_validate(raw.get("risk", {}))
    simulation = simulation or SimulationParameters.model_validate(raw.get("simulation", {}))
    data = HistoricalMarketDataProvider(
        {p: tuple(Candle.model_validate(c) for c in rows) for p, rows in raw["candles"].items()},
        {p: MarketConstraints.model_validate(m) for p, m in raw["markets"].items()},
        research,
        simulation,
        {
            p: tuple(LiquiditySnapshot.model_validate(b) for b in rows)
            for p, rows in raw.get("quotes", {}).items()
        },
        MarketConstraints.model_validate(raw["fx_market"]) if raw.get("fx_market") else None,
    )
    return await HistoricalReplay(
        data,
        risk,
        tuple(raw["approved"]),
        tuple(QuoteConversion.model_validate(x) for x in raw.get("fx", [])),
    ).run()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON with candles, markets, approved; optional fx/quotes/configs",
    )
    parser.add_argument("--output", type=Path, default=Path("artifacts/backtest"))
    parser.add_argument(
        "--parquet",
        type=Path,
        action="append",
        default=[],
        help="Phase 2 candle batch; repeat per file. Requires --input market/config metadata",
    )
    parser.add_argument(
        "--sensitivity",
        action="store_true",
        help="Also run doubled costs/spread and halved volume capacity",
    )
    args = parser.parse_args()
    raw = (
        json.loads(args.input.read_text(encoding="utf-8"), parse_float=str)
        if args.input
        else demo_input()
    )
    if args.parquet:
        if not args.input:
            parser.error("--parquet requires explicit --input market/config metadata")
        import pyarrow.parquet as pq

        grouped: dict[str, list[dict[str, Any]]] = {}
        for path in args.parquet:
            for encoded in (
                pq.read_table(path, columns=["payload_json"]).column("payload_json").to_pylist()
            ):
                value = json.loads(encoded, parse_float=str)
                event = Candle.model_validate(value)
                grouped.setdefault(event.symbol, []).append(event.model_dump(mode="json"))
        raw["candles"] = {
            pair: sorted(rows, key=lambda c: c["open_time"]) for pair, rows in grouped.items()
        }
    report = asyncio.run(execute(raw))
    export_report(report, args.output)
    if args.sensitivity:
        original = SimulationParameters.model_validate(raw.get("simulation", {}))
        scenarios = {
            "double_costs": original.model_copy(
                update={
                    "half_spread": original.half_spread * 2,
                    "slippage": original.slippage * 2,
                    "entry_fee": original.entry_fee * 2,
                    "exit_fee": original.exit_fee * 2,
                }
            ),
            "half_capacity": original.model_copy(
                update={
                    "volume_participation": original.volume_participation / 2,
                    "book_participation": original.book_participation / 2,
                }
            ),
        }
        for name, parameters in scenarios.items():
            validated = SimulationParameters.model_validate(parameters.model_dump())
            export_report(asyncio.run(execute(raw, validated)), args.output / name)
    print(json.dumps(report["metrics"], sort_keys=True))


if __name__ == "__main__":
    main()
