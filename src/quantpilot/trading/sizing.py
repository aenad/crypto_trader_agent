"""Time-independent sizing kernel. Inputs are validated by the Risk Engine."""

from decimal import Decimal


class AdaptivePositionSizer:
    @staticmethod
    def quantity(
        *,
        price: Decimal,
        loss_per_unit: Decimal,
        risk_budget: Decimal,
        quote_to_tmn: Decimal,
        notional_cap: Decimal,
    ) -> Decimal:
        if min(price, loss_per_unit, quote_to_tmn) <= 0:
            raise ValueError("Invalid sizing basis")
        return max(
            Decimal(0), min(notional_cap / price, risk_budget / (quote_to_tmn * loss_per_unit))
        )
