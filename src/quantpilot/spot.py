"""Permanent spot policy and wallet checks shared by risk and execution boundaries."""

import re
from collections.abc import Collection, Mapping
from decimal import Decimal
from typing import Literal

from quantpilot.models import DomainModel, MarketConstraints

D = Decimal


class SpotPolicy(DomainModel):
    market_type: Literal["SPOT"] = "SPOT"
    strategy_direction: Literal["LONG_ONLY"] = "LONG_ONLY"
    initial_capital_toman: Literal[5000000] = 5000000
    quote_currency: Literal["TMN"] = "TMN"
    margin_enabled: Literal[False] = False
    leverage_enabled: Literal[False] = False
    short_selling_enabled: Literal[False] = False
    borrowing_enabled: Literal[False] = False
    derivatives_enabled: Literal[False] = False
    buy_requires_available_balance: Literal[True] = True
    sell_requires_owned_asset: Literal[True] = True
    final_settlement_currency: Literal["TMN"] = "TMN"


def validate_spot_order(
    symbol: str,
    side: str,
    quantity: Decimal,
    price: Decimal,
    market: MarketConstraints,
    approved: Collection[str],
    free: Mapping[str, Decimal],
    fee_rate: Decimal,
    *,
    reserve_base_fee: bool = False,
) -> None:
    """Check only freely available funds, never total or borrowed balances.

    Simulators charge quote fees. LIVE conservatively reserves possible base fees
    as well, until the exchange reports the actual fee asset.
    """
    match = re.fullmatch(r"([A-Z0-9]+)/(TMN|USDT)", symbol)
    if not match or match[1] == match[2] or match[1] in ("TMN", "IRR"):
        raise ValueError("INVALID_SPOT_SYMBOL")
    if (
        symbol not in approved
        or market.symbol != symbol
        or market.quote != match[2]
        or not market.spot_enabled
        or not market.account_enabled
    ):
        raise ValueError("SPOT_MARKET_NOT_APPROVED_OR_ENABLED")
    if side not in ("BUY", "SELL"):
        raise ValueError("SPOT_BUY_OR_REDUCE_ONLY_SELL_REQUIRED")
    values = (quantity, price, fee_rate, *free.values())
    if any(not value.is_finite() or value < 0 for value in values):
        raise ValueError("INVALID_SPOT_BALANCE_OR_AMOUNT")
    if quantity <= 0 or price <= 0 or not 0 <= fee_rate < 1:
        raise ValueError("INVALID_SPOT_AMOUNT_OR_FEE")
    if (
        quantity % market.quantity_step
        or price % market.price_tick
        or quantity < market.minimum_quantity
        or quantity * price < market.minimum_notional
    ):
        raise ValueError("SPOT_SIZE_OR_PRECISION")
    asset = market.quote if side == "BUY" else match[1]
    required = (
        quantity * price * (1 + fee_rate)
        if side == "BUY"
        else quantity * (1 + fee_rate if reserve_base_fee else D(1))
    )
    if required > free.get(asset, D(0)):
        raise ValueError("INSUFFICIENT_FREE_SPOT_BALANCE")
