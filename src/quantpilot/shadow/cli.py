"""Persistent public-data-only SHADOW runner. All balances/orders are virtual."""

import argparse
import asyncio
import json
import uuid
from pathlib import Path
from typing import Any

from quantpilot.llm_settings import configure_shadow, load_llm_settings
from quantpilot.marketdata.transport import MCPConnection, RestPublic

from .ai import ShadowAI
from .engine import ShadowEngine
from .feed import WallClock, WallexLiveFeed
from .guard import PublicGetTransport
from .health import HealthServer
from .service import ShadowSession, export_activity, health, replay_decisions, run_shadow
from .storage import ShadowStore


async def start(args: Any) -> None:
    import httpx

    try:
        settings = load_llm_settings(
            None if getattr(args, "no_env_file", False) else getattr(args, "env_file", Path(".env"))
        )
        cfg = configure_shadow(
            json.loads(args.config.read_text(encoding="utf-8"), parse_float=str),
            settings,
            allow_network=args.allow_llm_network,
        )
    except (ValueError, OSError):
        raise ValueError(
            "Invalid shadow configuration; credentials must not be stored in config"
        ) from None
    if args.max_cycles is not None and args.max_cycles < 1:
        raise ValueError("Positive max-cycles required")
    clock = WallClock()
    ai = ShadowAI(
        cfg,
        args.responses,
        clock,
        replay=not args.allow_llm_network,
        token=settings.token.get_secret_value() if args.allow_llm_network else None,
    )
    engine = ShadowEngine(cfg, ai)
    store = ShadowStore(args.db)
    store.claim(str(uuid.uuid4()), clock.now())
    try:
        session = ShadowSession(store, engine)
        with HealthServer(store, cfg.health_port) as server:
            print(
                json.dumps(
                    {
                        "mode": "SHADOW",
                        "account": "VIRTUAL_ONLY",
                        "exchange_mutations": "BLOCKED",
                        "health": f"http://127.0.0.1:{server.server.server_port}/health",
                        "ai": ai.identity(),
                    }
                ),
                flush=True,
            )
            async with httpx.AsyncClient(
                base_url="https://api.wallex.ir",
                transport=PublicGetTransport(),
                trust_env=False,
                follow_redirects=False,
                timeout=20,
            ) as client:
                source = (
                    RestPublic(client)
                    if cfg.public_transport == "REST"
                    else MCPConnection(args.db.parent / "public-tools.json")
                )
                await run_shadow(
                    session, WallexLiveFeed(source, cfg, clock), clock, args.max_cycles
                )
    finally:
        if store.owner is not None:
            store.release()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    starting = commands.add_parser("start")
    starting.add_argument("--config", type=Path, required=True)
    starting.add_argument("--db", type=Path, default=Path("data/shadow/session.sqlite"))
    starting.add_argument("--responses", type=Path, default=Path("data/shadow/responses"))
    starting.add_argument("--allow-llm-network", action="store_true")
    dotenv = starting.add_mutually_exclusive_group()
    dotenv.add_argument("--env-file", type=Path, default=Path(".env"))
    dotenv.add_argument("--no-env-file", action="store_true")
    starting.add_argument("--max-cycles", type=int)
    for command in ("stop", "portfolio", "health", "export", "replay"):
        sub = commands.add_parser(command)
        sub.add_argument("--db", type=Path, default=Path("data/shadow/session.sqlite"))
        if command == "export":
            sub.add_argument("--output", type=Path, required=True)
        if command == "replay":
            sub.add_argument("--responses", type=Path, default=Path("data/shadow/responses"))
            sub.add_argument("--model", type=Path)
            sub.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "start":
        try:
            asyncio.run(start(args))
        except KeyboardInterrupt:
            pass
        return
    store = ShadowStore(args.db, create=False)
    if args.command == "stop":
        store.request_stop()
        print(json.dumps({"stop_requested": True, "mode": "SHADOW"}))
        return
    if args.command == "portfolio":
        _, state = store.checkpoint()
        print(
            json.dumps(
                {
                    "mode": "SHADOW",
                    "virtual_only": True,
                    "portfolio": state["portfolio"],
                    "ledger": state["ledger"],
                    "orders": state["execution"],
                },
                sort_keys=True,
                indent=2,
            )
        )
        return
    if args.command == "health":
        print(json.dumps(health(store, WallClock().now()), sort_keys=True))
        return
    with store.frozen() as frozen:
        if args.command == "export":
            export_activity(frozen, args.output)
            print(json.dumps({"exported": str(args.output)}))
        else:
            result = asyncio.run(replay_decisions(frozen, args.responses, WallClock(), args.model))
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(
                    json.dumps(result, sort_keys=True, indent=2), encoding="utf-8"
                )
            print(json.dumps(result, sort_keys=True))
            if result["status"] != "MATCH":
                raise SystemExit(1)


if __name__ == "__main__":
    main()
