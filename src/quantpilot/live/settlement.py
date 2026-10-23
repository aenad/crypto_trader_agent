"""Read-only direct-Toman settlement accounting for the dedicated spot account."""

from collections.abc import Mapping, Sequence
from decimal import Context, Decimal, localcontext

from quantpilot.models import Fill, PortfolioState

D = Decimal


def settlement_report(
    portfolio: PortfolioState,
    fills: Sequence[Fill],
    marks: Mapping[str, Decimal],
    initial: Decimal,
    unresolved_orders: int,
) -> dict[str, object]:
    """Reconstruct average cost from verified fills; reject unexplained inventory.

    This requires the existing dedicated-account bootstrap (zero initial crypto).
    A cash balance alone is never evidence of completed liquidation.
    """
    with localcontext(Context(prec=34)):
        quantities: dict[str, Decimal] = {}
        bases: dict[str, Decimal] = {}
        realized = fees = D(0)
        for fill in sorted(fills, key=lambda f: f.executed_at):
            base, quote = fill.symbol.split("/")
            if (
                quote != "TMN"
                or fill.price.currency != "TMN"
                or fill.fee.currency not in (base, "TMN")
            ):
                raise ValueError("UNSUPPORTED_SETTLEMENT_FILL")
            base_fee = fill.fee.amount if fill.fee.currency == base else D(0)
            quote_fee = fill.fee.amount if fill.fee.currency == "TMN" else D(0)
            fees += quote_fee + base_fee * fill.price.amount
            quantity, basis = quantities.get(base, D(0)), bases.get(base, D(0))
            gross = fill.base_quantity * fill.price.amount
            if fill.side == "BUY":
                quantities[base] = quantity + fill.base_quantity - base_fee
                bases[base] = basis + gross + quote_fee
            else:
                removed = fill.base_quantity + base_fee
                if removed > quantity or quantity <= 0:
                    raise ValueError("UNOWNED_SETTLEMENT_SALE")
                cost = basis * removed / quantity
                realized += gross - quote_fee - cost
                quantities[base], bases[base] = quantity - removed, basis - cost
        balances = {b.currency: b.free + b.reserved for b in portfolio.balances}
        for asset in set(balances) | set(quantities):
            if asset != "TMN" and balances.get(asset, D(0)) != quantities.get(asset, D(0)):
                raise ValueError("UNRECONCILED_SETTLEMENT_INVENTORY")
        residual = {a: q for a, q in quantities.items() if q > 0}
        if any(a not in marks or marks[a] <= 0 for a in residual):
            raise ValueError("MISSING_SETTLEMENT_VALUATION")
        cash = balances.get("TMN", D(0))
        value = sum((q * marks[a] for a, q in residual.items()), D(0))
        unrealized = value - sum((bases[a] for a in residual), D(0))
        equity = cash + value
        if initial <= 0 or abs(equity - initial - realized - unrealized) > D("1e-20"):
            raise ValueError("SETTLEMENT_CASH_RECONCILIATION_FAILED")
        return {
            "mode": "LIVE",
            "realized_pnl_tmn": str(realized),
            "unrealized_pnl_tmn": str(unrealized),
            "fees_tmn": str(fees),
            "remaining_holdings": {a: str(q) for a, q in sorted(residual.items())},
            "final_toman_balance_tmn": str(cash),
            "final_equity_tmn": str(equity),
            "net_return_pct": str((equity / initial - 1) * 100),
            "unresolved_orders": unresolved_orders,
            "fully_settled_tmn": not residual and unresolved_orders == 0,
            "valuation_basis": "FRESH_BID_MARK_BEFORE_POTENTIAL_EXIT_COSTS",
        }
