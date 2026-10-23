"""Synthetic public-frame SHADOW rehearsal using the unchanged shared core."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from quantpilot.models import MarketSnapshot
from quantpilot.shadow.ai import ShadowAI
from quantpilot.shadow.domain import ShadowConfig, ShadowFrame
from quantpilot.shadow.engine import ShadowEngine
from quantpilot.shadow.feed import WallClock
from quantpilot.shadow.service import ShadowSession
from quantpilot.shadow.storage import ShadowStore
from quantpilot.trading.demo import synthetic_context


async def create_session(path: Path) -> None:
    if path.exists():
        raise FileExistsError("Choose a new offline SHADOW database")
    original, _ = synthetic_context()
    now = datetime.now(timezone.utc)
    end = now.replace(minute=now.minute // 15 * 15, second=0, microsecond=0) - timedelta(minutes=15)
    shift = end - original.as_of
    raw: dict[str, Any] = original.model_dump(mode="json")
    raw["symbol"] = "BTC/TMN"
    raw["market"].update(symbol="BTC/TMN", quote="TMN")
    raw["as_of"] = end.isoformat()
    raw["liquidity"]["as_of"] = end.isoformat()
    for key in ("candles", "trend_candles"):
        for candle in raw[key]:
            candle["symbol"] = "BTC/TMN"
            for field in ("event_time", "received_at", "open_time", "close_time"):
                candle[field] = (datetime.fromisoformat(candle[field]) + shift).isoformat()
    snapshot = MarketSnapshot.model_validate(raw)
    assert snapshot.market is not None and snapshot.liquidity is not None
    config = ShadowConfig(
        approved=(snapshot.symbol,), markets=(snapshot.market,), ai_mode="QUANT_ONLY"
    )
    store = ShadowStore(path)
    store.claim("offline-ui-rehearsal", now)
    try:
        session = ShadowSession(
            store, ShadowEngine(config, ShadowAI(config, path.parent / "responses", WallClock()))
        )
        for seconds in (0, 15, 30):
            at = end + timedelta(seconds=seconds)
            fresh = snapshot.model_copy(
                update={
                    "as_of": at,
                    "liquidity": snapshot.liquidity.model_copy(update={"as_of": at}),
                }
            )
            await session.process(
                ShadowFrame(as_of=at, snapshots=(fresh,), depth_timestamps="FIXTURE")
            )
    finally:
        store.release()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/dashboard"))
    args = parser.parse_args()
    asyncio.run(create_session(args.root / "offline-shadow/session.sqlite"))
    catalog_path = args.root / "catalog.json"
    catalog = (
        json.loads(catalog_path.read_text(encoding="utf-8"))
        if catalog_path.exists()
        else {"runs": []}
    )
    if any(r["id"] == "offline-shadow" for r in catalog["runs"]):
        raise ValueError("Offline rehearsal already registered")
    catalog["runs"].append(
        {
            "id": "offline-shadow",
            "title": "Synthetic core rehearsal",
            "kind": "SHADOW",
            "path": "offline-shadow/session.sqlite",
        }
    )
    with catalog_path.open("w", encoding="utf-8") as output:
        json.dump(catalog, output, indent=2)
    print("SIMULATED market data; virtual SHADOW portfolio. No exchange or LLM calls.")


if __name__ == "__main__":
    main()
