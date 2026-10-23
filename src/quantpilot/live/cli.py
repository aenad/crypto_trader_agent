"""Local execution journal inspection and kill latch only. No activation command."""

import argparse
import json
from pathlib import Path

from .domain import LiveConfig
from .storage import LiveStore


def main() -> None:
    parser = argparse.ArgumentParser(description="Local LIVE journal tools; never calls Wallex")
    parser.add_argument("action", choices=("status", "kill", "export"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = LiveConfig.model_validate_json(args.config.read_text(encoding="utf-8"))
    if not args.db.is_file():
        parser.error("An existing dedicated LIVE database is required")
    if args.action == "export" and args.output is None:
        parser.error("--output is required for export")
    if args.action == "kill":
        # Independent of the writer lease: an operator can stop an active execution process.
        args.db.with_suffix(args.db.suffix + ".kill").touch(exist_ok=True)
        print(json.dumps({"kill": True, "config_id": config.config_id}))
        return
    store = LiveStore(args.db, config.config_id)
    try:
        if args.action == "export":
            # Account-sensitive export; the operator controls its destination.
            with args.output.open("x", encoding="utf-8") as output:
                for row in store.db.execute("SELECT body FROM live_audit ORDER BY seq"):
                    output.write(row[0] + "\n")
        print(
            json.dumps(
                {
                    "mode": "LIVE",
                    "config_id": config.config_id,
                    "kill": store.get("kill") is not None,
                    "suspension": store.get("suspended"),
                    "orders": [
                        {"client_id": r.intent.client_id, "state": r.state.value, "phase": r.phase}
                        for r in store.orders()
                    ],
                },
                sort_keys=True,
            )
        )
    finally:
        store.close()


if __name__ == "__main__":
    main()
