from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import SecretStr

from quantpilot.live.domain import Blocked
from quantpilot.live.prepare import candidate
from quantpilot.live.settings import WallexConnectionSettings
from quantpilot.llm_settings import LLMSettings


def inputs():
    connection = WallexConnectionSettings(
        api_key=SecretStr("PRIVATE_TEST_KEY"), sub_account_client_id=SecretStr("TEST-PROP-ID")
    )
    llm = LLMSettings(
        token=SecretStr("PRIVATE_LLM_TEST_TOKEN"),
        overrides={"analyst_model_id": "TEST-MODEL", "llm_gateway": "https://ai.boxapi.ir/ai/v1"},
    )
    markets = {
        "BTCTMN": {
            "symbol": "BTCTMN",
            "baseAsset": "BTC",
            "quoteAsset": "TMN",
            "stepSize": 8,
            "tickSize": 0,
            "minQty": "0.00000001",
            "minNotional": "50000",
        }
    }
    fees = {"BTCTMN": {"makerFeeRate": "0.0025", "takerFeeRate": "0.003"}}
    intent = {
        "approved": ["BTC/TMN"],
        "capital_tmn": "5000000",
        "max_order_tmn": "500000",
        "deadline": "2026-10-26T23:59:59+03:30",
    }
    return connection, llm, markets, fees, intent


def test_candidate_is_disabled_preserves_scope_and_does_not_copy_secrets():
    c = candidate(*inputs())
    assert not c.enabled and c.account_type == "CREDIT_SPOT"
    assert c.deadline == datetime(2026, 10, 26, 20, 29, 59, tzinfo=timezone.utc)
    assert c.operating_profile.value == "COMPETITION"
    market = c.markets[0]
    assert market.quantity_step == Decimal(".00000001")
    assert market.minimum_notional == Decimal(50000) and market.taker_fee_rate == Decimal(".003")
    assert not market.account_enabled
    assert c.capital_tmn == Decimal(5000000) and c.max_order_tmn == Decimal(500000)
    assert "PRIVATE_TEST_KEY" not in c.model_dump_json()
    assert "PRIVATE_LLM_TEST_TOKEN" not in c.model_dump_json()


@pytest.mark.parametrize(
    "field,value", [("quoteAsset", "IRR"), ("stepSize", True), ("tickSize", 99)]
)
def test_candidate_rejects_bad_metadata(field, value):
    args = inputs()
    args[2]["BTCTMN"][field] = value
    with pytest.raises(Blocked):
        candidate(*args)


def test_candidate_cannot_expand_the_approved_scope():
    args = inputs()
    args[4]["approved"] = ["BTC/TMN", "ETH/TMN"]
    with pytest.raises(Blocked, match="SCOPE"):
        candidate(*args)
