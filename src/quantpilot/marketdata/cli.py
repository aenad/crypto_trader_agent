"""Public-only data CLI. Does not load .env or use account credentials."""

import argparse
import asyncio
import json
import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from pathlib import Path

import httpx

from quantpilot.models import DomainModel

from .collect import Collectors, MarketScanner, PublicSource
from .domain import CollectionPolicy, utc_time
from .mock import MockPublic
from .normalize import RESOLUTIONS
from .storage import LocalCatalog, ParquetStore, PostgresCatalog
from .stream import PublicStream
from .transport import MCPConnection, RestPublic


def policy_from_file(path: Path | None) -> CollectionPolicy:
    if path is None:
        raise ValueError("An explicit --whitelist JSON file is required")
    approved = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(approved, list) or not all(isinstance(pair, str) for pair in approved):
        raise ValueError("Whitelist must be a JSON array of canonical market symbols")
    excluded = json.loads(files("quantpilot.marketdata").joinpath("excluded.json").read_text())
    return CollectionPolicy(approved=frozenset(approved), excluded=frozenset(excluded))


def store_from_args(args: argparse.Namespace) -> ParquetStore:
    if args.local_metadata:
        return ParquetStore(args.output, LocalCatalog(args.output / "metadata-offline"))
    dsn = os.environ.get("QUANTPILOT_POSTGRES_DSN")
    if not dsn:
        raise ValueError(
            "Set QUANTPILOT_POSTGRES_DSN or explicitly use --local-metadata for offline demo"
        )
    return ParquetStore(args.output, PostgresCatalog(dsn))


async def execute(
    args: argparse.Namespace, source: PublicSource, policy: CollectionPolicy, now: datetime
) -> None:
    scanner = MarketScanner(source, policy)
    markets = await scanner.scan()
    if args.command == "scan":
        print(json.dumps([m.model_dump(mode="json") for m in markets]))
        return
    if args.symbol not in {market.symbol for market in markets}:
        raise ValueError("Market not returned as spot and competition-approved")
    collectors = Collectors(source, policy)
    store = store_from_args(args)
    seconds = RESOLUTIONS[args.resolution]
    end = (
        utc_time(args.end)
        if args.end
        else datetime.fromtimestamp(int(now.timestamp()) // seconds * seconds, timezone.utc)
    )
    start = utc_time(args.start) if args.start else end - timedelta(seconds=seconds * args.bars)
    provenance = {
        "source": source.source,
        "resolution": args.resolution,
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
    if args.command == "stream":

        async def recover() -> None:
            current = datetime.now(timezone.utc)
            stop = datetime.fromtimestamp(
                int(current.timestamp()) // seconds * seconds, timezone.utc
            )
            backfill = await collectors.candles(args.symbol, args.resolution, start, stop, current)
            if backfill:
                store.save("candles", args.symbol, list(backfill), {**provenance, "recovery": True})

        if args.channel in ("1m", "1h", "1d"):
            expected = {"1m": "1", "1h": "60", "1d": "1D"}[args.channel]
            if args.resolution != expected:
                raise ValueError("Stream candle channel and resolution must match")
            await recover()
        count = 0
        stream = PublicStream(policy).events(args.symbol, args.channel, recover)
        try:
            async with asyncio.timeout(args.duration):
                async for event in stream:
                    store.save(
                        "stream",
                        args.symbol,
                        [event],
                        {
                            "channel": event.channel,
                            "epoch": event.epoch,
                            "source": "wallex-ws",
                            "gaps_possible": True,
                        },
                    )
                    count += 1
                    if count >= args.events:
                        break
        except TimeoutError:
            pass
        finally:
            await stream.aclose()
        print(json.dumps({"stored_stream_events": count}))
        return
    events: list[DomainModel]
    if args.kind == "candles":
        events = list(await collectors.candles(args.symbol, args.resolution, start, end, now))
    elif args.kind == "book":
        events = [await collectors.order_book(args.symbol, now)]
    else:
        events = list(await collectors.recent_trades(args.symbol, now))
    manifest = store.save(args.kind, args.symbol, list(events), provenance)
    print(
        json.dumps(
            {
                "dataset_id": manifest["dataset_id"],
                "rows": manifest["rows"],
                "kind": args.kind,
                "source": source.source,
            }
        )
    )


async def run(args: argparse.Namespace) -> None:
    if args.command == "discover":
        print(json.dumps(await MCPConnection(args.metadata).request("discover", {})))
        return
    policy = policy_from_file(args.whitelist)
    if args.source == "mock":
        now = datetime(2026, 10, 22, 10, tzinfo=timezone.utc)
        await execute(args, MockPublic(now), policy, now)
    elif args.source == "mcp":
        await execute(args, MCPConnection(args.metadata), policy, datetime.now(timezone.utc))
    else:
        async with httpx.AsyncClient(base_url="https://api.wallex.ir", timeout=20) as client:
            await execute(args, RestPublic(client), policy, datetime.now(timezone.utc))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Collect verified public Wallex market data only")
    result.add_argument("command", choices=["discover", "scan", "collect", "stream"])
    result.add_argument("--source", choices=["mcp", "rest", "mock"], default="mcp")
    result.add_argument("--whitelist", type=Path)
    result.add_argument("--symbol", default="BTC/USDT")
    result.add_argument("--kind", choices=["candles", "book", "trades"], default="candles")
    result.add_argument("--resolution", choices=list(RESOLUTIONS), default="1")
    result.add_argument("--start")
    result.add_argument("--end")
    result.add_argument("--bars", type=int, default=30)
    result.add_argument("--output", type=Path, default=Path("data/marketdata"))
    result.add_argument("--metadata", type=Path, default=Path("data/marketdata/tools.json"))
    result.add_argument("--local-metadata", action="store_true")
    result.add_argument(
        "--channel", choices=["trade", "buyDepth", "sellDepth", "1m", "1h", "1d"], default="trade"
    )
    result.add_argument("--events", type=int, default=10)
    result.add_argument("--duration", type=int, default=60)
    return result


def main() -> None:
    args = parser().parse_args()
    if args.bars < 1 or args.events < 1 or args.duration < 1:
        raise SystemExit("Positive bars/events/duration required")
    try:
        asyncio.run(run(args))
    except Exception as exc:
        # Never stringify database/transport exceptions: DSNs may contain secrets.
        raise SystemExit(
            f"Collection failed ({type(exc).__name__}); no successful dataset claimed"
        ) from None


if __name__ == "__main__":
    main()
