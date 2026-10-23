"""Sanitized hybrid readiness checks; never submits exchange orders."""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from quantpilot.llm_settings import load_llm_settings

from .analyst import JsonGatewayProvider
from .learning import FrozenModel


async def check(env_file: Path, model: Path | None, call_llm: bool) -> dict[str, Any]:
    settings = load_llm_settings(env_file)
    values = settings.overrides
    report: dict[str, Any] = {
        "live_enabled": False,
        "exchange_mutations": 0,
        "gateway_configured": bool(values.get("llm_gateway")),
        "analyst_model_configured": bool(values.get("analyst_model_id")),
        "llm_token_configured": bool(settings.token.get_secret_value()),
        "llm_status": "NOT_CALLED",
        "model_status": "NOT_PROVIDED",
    }
    if model is not None:
        try:
            loaded = FrozenModel.load(model)
            report.update(
                model_status="COMPATIBLE_RESEARCH_ARTIFACT",
                model_version=loaded.model_version,
                model_live_enabled=False,
            )
        except Exception as exc:
            report.update(
                model_status="INCOMPATIBLE_OR_INVALID", model_error_type=type(exc).__name__
            )
    if call_llm:
        try:
            provider = JsonGatewayProvider(
                str(values.get("llm_gateway", "")),
                str(values.get("analyst_model_id", "")),
                settings.token.get_secret_value(),
                int(values.get("llm_timeout_seconds", 10)),
            )
            if not settings.token.get_secret_value():
                raise ValueError("Missing dedicated token")
            response = await provider.complete(
                {
                    "purpose": "CONNECTION_CHECK_ONLY_NOT_A_TRADING_RECOMMENDATION",
                    "instruction": "Return a JSON object with status equal to ok.",
                },
                {
                    "type": "object",
                    "properties": {"status": {"const": "ok"}},
                    "required": ["status"],
                    "additionalProperties": False,
                },
            )
            report["llm_status"] = (
                "SCHEMA_VERIFIED" if json.loads(response) == {"status": "ok"} else "INVALID_OUTPUT"
            )
        except Exception as exc:
            report.update(llm_status="FAILED", llm_error_type=type(exc).__name__)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--model", type=Path)
    parser.add_argument("--call-llm", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = asyncio.run(check(args.env_file, args.model, args.call_llm))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))
    if report["model_status"] == "INCOMPATIBLE_OR_INVALID" or (
        args.call_llm and report["llm_status"] != "SCHEMA_VERIFIED"
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
