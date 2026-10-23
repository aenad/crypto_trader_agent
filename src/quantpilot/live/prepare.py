"""Build a disabled credit Spot candidate from read-only exchange metadata."""

import argparse
import asyncio
import json
from decimal import Decimal
from pathlib import Path
from typing import Any

from quantpilot.llm_settings import LLMSettings, load_llm_settings
from quantpilot.models import MarketConstraints

from .domain import Blocked, LiveConfig
from .settings import WallexConnectionSettings, load_wallex_settings
from .transport import WallexSpotREST, decimal


def candidate(
    connection: WallexConnectionSettings,
    llm: LLMSettings,
    markets: dict[str, Any],
    fees: dict[str, Any],
    intent: dict[str, Any],
) -> LiveConfig:
    selector = connection.sub_account_client_id.get_secret_value()
    if not selector:
        raise Blocked("CREDIT_SELECTOR_REQUIRED")
    if intent.get("approved") != ["BTC/TMN"]:
        raise Blocked("REVIEWED_BTC_SCOPE_REQUIRED")
    row, fee = markets["BTCTMN"], fees["BTCTMN"]
    if (
        row.get("symbol") != "BTCTMN"
        or row.get("baseAsset") != "BTC"
        or row.get("quoteAsset") != "TMN"
    ):
        raise Blocked("MARKET_IDENTITY_MISMATCH")
    step, tick = row["stepSize"], row["tickSize"]
    if type(step) is not int or type(tick) is not int or not 0 <= step <= 18 or not 0 <= tick <= 18:
        raise Blocked("INVALID_PRECISION_METADATA")
    rate = max(decimal(fee["makerFeeRate"]), decimal(fee["takerFeeRate"]))
    if rate >= Decimal("0.1"):
        raise Blocked("UNREVIEWED_FEE_RATE")
    market = MarketConstraints(
        symbol="BTC/TMN",
        quote="TMN",
        spot_enabled=True,
        account_enabled=False,
        quantity_step=Decimal(10) ** -step,
        price_tick=Decimal(10) ** -tick,
        minimum_quantity=decimal(row["minQty"]),
        minimum_notional=decimal(row["minNotional"]),
        taker_fee_rate=rate,
    )
    # These are review candidates, not API permission introspection or activation.
    return LiveConfig(
        enabled=False,
        account_type="CREDIT_SPOT",
        account_id="credit-review-candidate",
        sub_account_client_id=selector,
        approved=("BTC/TMN",),
        markets=(market,),
        capital_tmn=intent["capital_tmn"],
        max_order_tmn=intent["max_order_tmn"],
        max_fee_rate=max(Decimal("0.005"), rate),
        deadline=intent.get("deadline"),
        liquidation_seconds=intent.get("liquidation_seconds", 300),
        ai={
            "mode": "QUANT_ML_LLM",
            "model_path": "artifacts/deployment-models/baseline",
            "analyst_model_id": llm.overrides.get("analyst_model_id", "unconfigured"),
            "gateway": llm.overrides.get("llm_gateway"),
            "timeout_seconds": llm.overrides.get("llm_timeout_seconds", 10),
            "call_budget": llm.overrides.get("llm_call_budget", 100),
        },
    )


async def prepare(env_file: Path, intent_file: Path, output: Path) -> dict[str, Any]:
    if not output.name.endswith(".local.json"):
        raise ValueError("Use a private .local.json destination")
    if output.exists():
        raise ValueError("Candidate destination already exists; preserve previous reviews")
    connection = load_wallex_settings(env_file)
    llm = load_llm_settings(env_file)
    intent = json.loads(intent_file.read_text(encoding="utf-8"), parse_float=str)
    client = WallexSpotREST(
        connection.api_key, sub_account_client_id=connection.sub_account_client_id
    )
    try:
        await client.verify_account_context(connection.sub_account_client_id.get_secret_value())
        config = candidate(connection, llm, await client.markets(), await client.fees(), intent)
    finally:
        await client.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))
    return {
        "status": "DISABLED_CANDIDATE_CREATED",
        "live_enabled": False,
        "exchange_mutations": 0,
        "config_id": config.config_id,
        "key_ownership_verified": False,
        "order_routing_verified": False,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env-file", type=Path, default=Path(".env"))
    p.add_argument("--intent", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    try:
        report = asyncio.run(prepare(args.env_file, args.intent, args.output))
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "PREPARATION_FAILED",
                    "error_type": type(exc).__name__,
                    "live_enabled": False,
                    "exchange_mutations": 0,
                }
            )
        )
        raise SystemExit(1) from None
    print(json.dumps(report))


if __name__ == "__main__":
    main()
