"""Hybrid deployment diagnostics. This command cannot activate or submit orders."""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from quantpilot.ai.evaluation import samples_from
from quantpilot.ai.learning import FrozenModel
from quantpilot.ai.preflight import check as check_llm
from quantpilot.config import stable_id
from quantpilot.live.domain import LiveConfig
from quantpilot.shadow.domain import ShadowConfig


async def inspect(
    config_path: Path, env_file: Path, dataset: Path | None, call_llm: bool
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "live_activated": False,
        "exchange_mutations": 0,
        "ready_for_hybrid_shadow": False,
        "ready_for_live": False,
        "blockers": [],
        "model_status": "NOT_CHECKED",
        "training_status": "NOT_CHECKED",
    }
    blockers: list[str] = report["blockers"]
    cfg: ShadowConfig | LiveConfig
    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        if raw.get("mode") == "SHADOW":
            cfg = ShadowConfig.model_validate(raw)
            ai_mode, model_path = cfg.ai_mode, cfg.model_path
        else:
            live = LiveConfig.model_validate(raw)
            cfg = live
            ai_mode, model_path = live.ai.mode, live.ai.model_path
        report.update(
            config_id=cfg.config_id, operating_profile=cfg.operating_profile.value, ai_mode=ai_mode
        )
    except (ValueError, OSError, TypeError, AttributeError):
        blockers.append("CONFIGURATION_INVALID")
        return report
    if ai_mode != "QUANT_ML_LLM":
        blockers.append("HYBRID_MODE_REQUIRED")
    if not model_path:
        blockers.append("MODEL_PATH_REQUIRED")
    else:
        try:
            model = FrozenModel.load(Path(model_path))
            matches = model.metadata.get("research_id") == stable_id(
                cfg.research.model_dump(mode="json")
            )
            report.update(
                model_status="COMPATIBLE",
                model_version=model.model_version,
                model_matches_strategy=matches,
                model_live_approved=model.metadata.get("live_enabled") is True,
            )
            if not matches:
                blockers.append("MODEL_STRATEGY_MISMATCH")
        except Exception as exc:
            report.update(
                model_status="UNAVAILABLE_OR_INCOMPATIBLE", model_error_type=type(exc).__name__
            )
            blockers.append("MODEL_UNAVAILABLE_OR_INCOMPATIBLE")
    try:
        llm = await check_llm(env_file, None, call_llm)
        report["llm"] = llm
        if not all(
            llm.get(k)
            for k in ("gateway_configured", "analyst_model_configured", "llm_token_configured")
        ):
            blockers.append("LLM_CONFIGURATION_INCOMPLETE")
        if llm["llm_status"] != "SCHEMA_VERIFIED":
            blockers.append("LLM_CONNECTION_UNVERIFIED")
    except (ValueError, OSError):
        blockers.append("LLM_CONFIGURATION_INVALID")
    report["ready_for_hybrid_shadow"] = not blockers
    if dataset is not None:
        try:
            bundle = json.loads(dataset.read_text(encoding="utf-8"))
            rows = samples_from(bundle)
            report.update(
                training_samples=len(rows),
                training_status="SAMPLES_AVAILABLE_NOT_VALIDATED"
                if rows
                else "NO_ELIGIBLE_SAMPLES",
            )
        except (ValueError, OSError, KeyError, TypeError):
            report["training_status"] = "DATASET_INVALID"
    report["live_blockers"] = [
        "ACCOUNT_EXECUTION_REVIEW_REQUIRED",
        "SEPARATE_LIVE_AUTHORIZATION_REQUIRED",
    ]
    if any(not market.account_enabled for market in cfg.markets):
        report["live_blockers"].append("ACCOUNT_MARKET_PERMISSION_UNVERIFIED")
    if report.get("model_live_approved") is not True:
        report["live_blockers"].append("VALIDATED_BASELINE_MODEL_REQUIRED")
    if report["training_status"] in ("NO_ELIGIBLE_SAMPLES", "DATASET_INVALID"):
        report["live_blockers"].append("ELIGIBLE_TRAINING_DATA_REQUIRED")
    # This diagnostic never treats local declarations as exchange introspection.
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--env-file", type=Path, default=Path(".env"))
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--call-llm", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(inspect(args.config, args.env_file, args.dataset, args.call_llm))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    if not result["ready_for_hybrid_shadow"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
