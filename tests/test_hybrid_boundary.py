import asyncio
from datetime import timedelta

import pytest
from test_hybrid_runtime import Evaluator
from test_live import fixture
from test_live_service import ready

from quantpilot.live.domain import Blocked


def hybrid_fixture(tmp_path):
    return fixture(
        tmp_path, ai={"mode": "QUANT_ML_LLM", "model_path": "FAKE", "analyst_model_id": "FAKE"}
    )


def test_direct_submit_cannot_skip_configured_ai(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = hybrid_fixture(tmp_path)
        try:
            await ready(a, snapshot)
            intent = (await a.strategy_cycle((snapshot,)))[0]
            with pytest.raises(Blocked, match="HYBRID_ACCEPTANCE_REQUIRED"):
                await a.submit(intent)
            assert exchange.submissions == 0
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("verdict", ["REJECT", "ABSTAIN"])
def test_veto_revokes_the_original_risk_grant(tmp_path, verdict):
    async def scenario():
        a, exchange, store, snapshot, _, _ = hybrid_fixture(tmp_path)
        try:
            await ready(a, snapshot)
            intent = (await a.strategy_cycle((snapshot,)))[0]
            assert not await a.evaluate_entry(intent, Evaluator(verdict))
            with pytest.raises(Blocked, match="ORDER_NOT_AUTHORIZED"):
                await a.submit(intent)
            assert exchange.submissions == 0
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


def test_reconciliation_invalidates_prior_ai_acceptance(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, _, _ = hybrid_fixture(tmp_path)
        try:
            await ready(a, snapshot)
            intent = (await a.strategy_cycle((snapshot,)))[0]
            assert await a.evaluate_entry(intent, Evaluator("ACCEPT"))
            await a.recover((snapshot,))
            with pytest.raises(Blocked, match="ORDER_NOT_AUTHORIZED"):
                await a.submit(intent)
            assert exchange.submissions == 0
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


def test_slow_ai_cannot_approve_stale_context(tmp_path):
    async def scenario():
        a, exchange, store, snapshot, clock, _ = hybrid_fixture(tmp_path)

        class SlowEvaluator(Evaluator):
            async def evaluate(self, signal, snapshot):
                clock.at += timedelta(seconds=60)
                return await super().evaluate(signal, snapshot)

        try:
            await ready(a, snapshot)
            intent = (await a.strategy_cycle((snapshot,)))[0]
            with pytest.raises(Blocked, match="STALE_EXECUTION_CONTEXT"):
                await a.evaluate_entry(intent, SlowEvaluator("ACCEPT"))
            assert intent.client_id not in a._authorizations
            assert exchange.submissions == 0
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())
