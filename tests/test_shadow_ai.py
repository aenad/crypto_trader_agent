import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from test_shadow import later, setup_context

from quantpilot.ai.analyst import record_fixture
from quantpilot.ai.domain import FeatureVector, LearningConfig, Sample
from quantpilot.ai.features import assemble_context
from quantpilot.ai.learning import train
from quantpilot.ai.splits import chronological_split
from quantpilot.backtest.history import HistoricalClock
from quantpilot.config import stable_id
from quantpilot.shadow.ai import ShadowAI
from quantpilot.shadow.domain import ShadowConfig
from quantpilot.shadow.engine import ShadowEngine
from quantpilot.shadow.service import ShadowSession, replay_decisions
from quantpilot.shadow.storage import ShadowStore
from quantpilot.trading.strategy import MarketEligibilityFilter, MomentumBreakout


@pytest.mark.parametrize("failure", [False, True])
def test_actual_lightgbm_harness_fusion_risk_and_recorded_failures_replay(tmp_path, failure):
    pytest.importorskip("lightgbm")

    async def scenario():
        cfg, frame = setup_context()
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        samples = []
        for i in range(120):
            values = {name: Decimal(".01") for name in FeatureVector.names()}
            values.update(
                entry_ema_gap=Decimal(".01") if i % 2 else Decimal("-.01"),
                trend_ema_gap=Decimal(".01") if i % 2 else Decimal("-.01"),
                rsi=Decimal(51 if i % 2 else 49),
            )
            samples.append(
                Sample(
                    sample_id=str(i),
                    symbol="BTC/TMN",
                    as_of=start + timedelta(minutes=5 * i),
                    label_end=start + timedelta(minutes=5 * (i + 1)),
                    snapshot_id=stable_id({"i": i}),
                    features=FeatureVector(**values),
                    positive=i % 2,
                    net_return=Decimal(1 if i % 2 else -1),
                    net_pnl_tmn=Decimal(1 if i % 2 else -1),
                )
            )
        learning = LearningConfig(
            embargo_seconds=0,
            minimum_train=10,
            minimum_validation=5,
            minimum_test=5,
            min_data_in_leaf=3,
            rounds=20,
        )
        model = train(
            chronological_split(tuple(samples), 0),
            learning,
            "UNIT_FIXTURE",
            stable_id(cfg.research.model_dump(mode="json")),
        )
        model_path = model.save(tmp_path / "models")
        cfg = ShadowConfig.model_validate(
            {
                **cfg.model_dump(),
                "ai_mode": "QUANT_ML_LLM",
                "model_path": str(model_path),
                "analyst_model_id": "UNIT_ANALYST_FIXTURE",
            }
        )
        ai = ShadowAI(cfg, tmp_path / "responses", HistoricalClock(frame.as_of), replay=True)

        class Provider:
            model_id = "UNIT_ANALYST_FIXTURE"
            calls = 0

            async def complete(self, request, schema):
                self.calls += 1
                if failure:
                    raise RuntimeError("INJECTED_LLM_FAILURE")
                return json.dumps(
                    {
                        "context_id": request["context_id"],
                        "as_of": request["context"]["as_of"],
                        "assessment": "ACCEPT",
                        "confidence": 60,
                        "reason_codes": ["CONTEXT_CONSISTENT"],
                    }
                )

        provider = Provider()
        ai.harness.provider = provider
        ai.harness.replay_only = False
        engine = ShadowEngine(cfg, ai)
        store = ShadowStore(tmp_path / "ai.sqlite")
        store.claim("ai-test-owner", frame.as_of)
        live = ShadowSession(store, engine)
        result = await live.process(frame)
        decision = result["decisions"][0]
        assert decision["ai"]["candidate"]["prediction"]["model_version"] == model.model_version
        assert provider.calls == 1
        assert decision["outcome"] == ("AI_REJECTED" if failure else "ACCEPTED")
        assert live.store.operations()[-1]["latency"]["llm_seconds"] >= 0
        if failure:
            # A later global cache entry must NOT turn the recorded failure into approval.
            snapshot = frame.snapshots[0]
            signal = MomentumBreakout(cfg.research, MarketEligibilityFilter(cfg.approved)).evaluate(
                snapshot, engine.portfolio(frame, ())
            )
            record_fixture(
                ai.harness.store,
                assemble_context(snapshot, signal, cfg.research),
                provider.model_id,
            )
        await live.process(later(frame))
        replay = await replay_decisions(
            store, tmp_path / "deliberately-empty-cache", HistoricalClock(frame.as_of)
        )
        assert replay["status"] == "MATCH"
        assert replay["llm_network_calls"] == 0
        assert provider.calls == 1

    asyncio.run(scenario())
