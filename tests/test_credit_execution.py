"""Fake exchange integration only; no credentials, orders or network access."""

import asyncio
from decimal import Decimal

import httpx
import pytest
from pydantic import SecretStr, ValidationError
from test_live import Exchange, fixture

from quantpilot.live.domain import AccountAuthorization, Blocked, LiveConfig
from quantpilot.live.execution import ProtectedExecution, require_activation
from quantpilot.live.storage import LiveStore
from quantpilot.live.transport import WallexSpotREST

SELECTOR = "TEST-PROP-ONLY"


class CreditExchange(Exchange):
    scope_checks = 0

    async def verify_account_context(self, selector):
        assert selector == SELECTOR
        self.scope_checks += 1


def test_credit_config_requires_selector_and_review_evidence(tmp_path):
    a, _, store, _, _, _ = fixture(tmp_path)
    try:
        raw = a.config.model_dump()
        raw["account_type"] = "CREDIT_SPOT"
        with pytest.raises(ValidationError):
            LiveConfig.model_validate(raw)
        grant = a.grant.model_dump()
        grant.update(account_type="CREDIT_SPOT", sub_account_client_id=SELECTOR)
        with pytest.raises(ValidationError):
            AccountAuthorization.model_validate(grant)
    finally:
        store.close()


def test_credit_mock_bootstrap_reconciliation_and_risk_submission(tmp_path):
    async def scenario():
        old, _, prior, snapshot, clock, env = fixture(tmp_path)
        cfg = LiveConfig.model_validate(
            {
                **old.config.model_dump(),
                "account_type": "CREDIT_SPOT",
                "sub_account_client_id": SELECTOR,
            }
        )
        grant = AccountAuthorization.model_validate(
            {
                **old.grant.model_dump(),
                "config_id": cfg.config_id,
                "account_type": "CREDIT_SPOT",
                "sub_account_client_id": SELECTOR,
                "key_scope_review_reference": "FAKE-KEY-REVIEW",
                "credit_routing_review_reference": "FAKE-ROUTING-REVIEW",
            }
        )
        prior.close()
        env["QUANTPILOT_LIVE_AUTHORIZATION"] = cfg.config_id
        store = LiveStore(tmp_path / "credit.sqlite", cfg.config_id)
        exchange = CreditExchange(cfg, clock)
        a = ProtectedExecution(cfg, grant, store, clock, exchange, env)
        try:
            await a.bootstrap()
            await a.recover((snapshot,))
            a.resume_after_reconciliation()
            proposals = await a.strategy_cycle((snapshot,))
            assert len(proposals) == 1
            await a.submit(proposals[0])
            assert exchange.submissions == 1 and exchange.scope_checks >= 3
            bad = grant.model_copy(update={"sub_account_client_id": "ANOTHER-ACCOUNT"})
            with pytest.raises(Blocked, match="CONTEXT_MISMATCH"):
                require_activation(cfg, bad, clock.now(), env)
        finally:
            await a.close()
            store.close()

    asyncio.run(scenario())


@pytest.mark.parametrize("invalid_total", [False, True])
def test_credit_headers_and_free_locked_balance_contract(invalid_total):
    async def scenario():
        seen = []

        def handler(request):
            seen.append(request)
            assert request.headers["sub-account-client-id"] == SELECTOR
            return httpx.Response(
                200,
                json={
                    "success": True,
                    "result": {
                        "TMN": {
                            "available": "1000",
                            "freeze": "200",
                            "total": "1201" if invalid_total else "1200",
                        }
                    },
                },
            )

        client = WallexSpotREST(
            SecretStr("FAKE-KEY"),
            sub_account_client_id=SecretStr(SELECTOR),
            transport=httpx.MockTransport(handler),
        )
        try:
            if invalid_total:
                with pytest.raises(Blocked, match="TOTAL_MISMATCH"):
                    await client.balances("FREE")
            else:
                b = (await client.balances("FREE"))[0]
                assert b.free == Decimal(1000) and b.reserved == Decimal(200)
                assert seen[0].url.path == "/v1/account/balances-detail"
            with pytest.raises(Blocked, match="SEMANTICS_REQUIRED"):
                await client.balances("TOTAL")
            assert all(r.method == "GET" for r in seen)
        finally:
            await client.close()

    asyncio.run(scenario())
