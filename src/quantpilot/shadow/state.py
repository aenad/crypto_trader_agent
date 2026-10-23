"""Explicit JSON state; never deserialize Python objects/pickle."""

from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from quantpilot.backtest.execution import Pending
from quantpilot.backtest.ledger import Holding, PortfolioLedger
from quantpilot.models import Fill, OrderIntent, OrderState, Position

from .execution import ShadowExecutionProvider

D = Decimal


def dump_ledger(ledger: PortfolioLedger) -> dict[str, Any]:
    return {
        "holdings": {
            a: {"quantity": str(h.quantity), "basis_tmn": str(h.basis_tmn)}
            for a, h in ledger.holdings.items()
        },
        "reserved": {a: str(q) for a, q in ledger.reserved.items()},
        "positions": {p: r.model_dump(mode="json") for p, r in ledger.positions.items()},
        "realized": str(ledger.realized),
        "fees": str(ledger.fees),
        "peak": str(ledger.peak),
        "daily_open": str(ledger.daily_open),
        "day": ledger.day.isoformat() if ledger.day else None,
        "halted": ledger.halted,
        "events": deepcopy(ledger.events),
        "trades": deepcopy(ledger.trades),
        "trade_pnl": {k: str(v) for k, v in ledger.trade_pnl.items()},
        "seen": dict(ledger.seen),
    }


def load_ledger(ledger: PortfolioLedger, state: dict[str, Any]) -> None:
    ledger.holdings = {
        a: Holding(D(h["quantity"]), D(h["basis_tmn"])) for a, h in state["holdings"].items()
    }
    ledger.reserved = {a: D(q) for a, q in state["reserved"].items()}
    ledger.positions = {p: Position.model_validate(r) for p, r in state["positions"].items()}
    ledger.realized = D(state["realized"])
    ledger.fees = D(state["fees"])
    ledger.peak = D(state["peak"])
    ledger.daily_open = D(state["daily_open"])
    ledger.day = date.fromisoformat(state["day"]) if state["day"] else None
    ledger.halted = state["halted"]
    ledger.events = deepcopy(state["events"])
    ledger.trades = deepcopy(state["trades"])
    ledger.trade_pnl = {k: D(v) for k, v in state["trade_pnl"].items()}
    ledger.seen = dict(state["seen"])
    if any(h.quantity < 0 or h.basis_tmn < 0 for h in ledger.holdings.values()) or any(
        q < 0 or q > ledger.holding(a).quantity for a, q in ledger.reserved.items()
    ):
        raise ValueError("Invalid persisted virtual balances")


def dump_orders(execution: ShadowExecutionProvider) -> dict[str, Any]:
    return {
        "used_books": dict(execution.used_books),
        "orders": {
            key: {
                "intent": o.intent.model_dump(mode="json"),
                "submitted": o.submitted.isoformat(),
                "atr": str(o.atr),
                "remaining": str(o.remaining),
                "reserved": str(o.reserved),
                "asset": o.asset,
                "budget_price": str(o.budget_price),
                "maximum_fx": str(o.maximum_fx),
                "state": o.state.value,
                "executions": [f.model_dump(mode="json") for f in o.executions],
            }
            for key, o in execution.orders.items()
        },
    }


def load_orders(execution: ShadowExecutionProvider, state: dict[str, Any]) -> None:
    execution.plans.clear()
    execution.orders = {
        key: Pending(
            OrderIntent.model_validate(o["intent"]),
            datetime.fromisoformat(o["submitted"]),
            D(o["atr"]),
            D(o["remaining"]),
            D(o["reserved"]),
            o["asset"],
            D(o["budget_price"]),
            D(o["maximum_fx"]),
            OrderState(o["state"]),
            [Fill.model_validate(f) for f in o["executions"]],
        )
        for key, o in state["orders"].items()
    }
    execution.used_books = dict(state["used_books"])
    expected: dict[str, Decimal] = {}
    for order in execution.active():
        expected[order.asset] = expected.get(order.asset, D(0)) + order.reserved
    if any(
        expected.get(asset, D(0)) != quantity
        for asset, quantity in execution.ledger.reserved.items()
    ) or any(
        execution.ledger.reserved.get(asset, D(0)) != quantity
        for asset, quantity in expected.items()
    ):
        raise ValueError("Persisted order reservations do not reconcile")
