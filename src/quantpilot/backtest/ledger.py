"""Average-cost, multi-currency ledger. No exchange account is involved."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Context, Decimal, localcontext
from typing import Any
from zoneinfo import ZoneInfo

from quantpilot.config import stable_id
from quantpilot.models import AssetBalance, Fill, PortfolioState, Position, QuoteConversion
from quantpilot.trading.config import ResearchParameters
from quantpilot.trading.lifecycle import apply_simulated_fill

D = Decimal


@dataclass
class Holding:
    quantity: Decimal = D(0)
    basis_tmn: Decimal = D(0)


class PortfolioLedger:
    def __init__(self, capital: Decimal, research: ResearchParameters):
        if capital <= 0:
            raise ValueError("Positive capital required")
        self.initial = capital
        self.research = research
        self.holdings = {"TMN": Holding(capital, capital)}
        self.positions: dict[str, Position] = {}
        self.reserved: dict[str, Decimal] = {}
        self.realized = D(0)
        self.fees = D(0)
        self.peak = capital
        self.daily_open = capital
        self.day: Any = None
        self.halted = False
        self.events: list[dict[str, Any]] = []
        self.trades: list[dict[str, Any]] = []
        self.trade_pnl: dict[str, Decimal] = {}
        self.seen: dict[str, str] = {}

    def holding(self, asset: str) -> Holding:
        return self.holdings.setdefault(asset, Holding())

    def free(self, asset: str) -> Decimal:
        return self.holding(asset).quantity - self.reserved.get(asset, D(0))

    def reserve(self, asset: str, quantity: Decimal) -> None:
        if quantity < 0 or quantity > self.free(asset):
            raise ValueError("Insufficient free balance")
        self.reserved[asset] = self.reserved.get(asset, D(0)) + quantity

    def release(self, asset: str, quantity: Decimal) -> None:
        if quantity < 0 or quantity > self.reserved.get(asset, D(0)):
            raise ValueError("Invalid release")
        self.reserved[asset] -= quantity

    def _remove(self, asset: str, quantity: Decimal) -> Decimal:
        holding = self.holding(asset)
        if quantity < 0 or quantity > self.free(asset):
            raise ValueError("Overspend or reserved funds")
        basis = (
            holding.basis_tmn
            if quantity == holding.quantity
            else holding.basis_tmn * quantity / holding.quantity
        )
        holding.quantity -= quantity
        holding.basis_tmn -= basis
        return basis

    def _add(self, asset: str, quantity: Decimal, basis: Decimal) -> None:
        row = self.holding(asset)
        row.quantity += quantity
        row.basis_tmn += basis

    def convert(
        self,
        quote: str,
        quantity: Decimal,
        rate: Decimal,
        fee_rate: Decimal,
        at: datetime,
        to_toman: bool = False,
    ) -> None:
        if quote != "USDT" or quantity <= 0 or rate <= 0 or not 0 <= fee_rate < 1:
            raise ValueError("Explicit positive USDT/TMN conversion required")
        with localcontext(Context(prec=34)):
            gross = quantity * rate
            fee = gross * fee_rate
            if to_toman:
                basis = self._remove(quote, quantity)
                self._add("TMN", gross - fee, gross - fee)
                pnl = gross - fee - basis
            else:
                self._remove("TMN", gross + fee)
                self._add(quote, quantity, gross + fee)
                pnl = D(0)
            self.realized += pnl
            self.fees += fee
            self.events.append(
                {
                    "kind": "FX",
                    "at": at.isoformat(),
                    "asset": quote,
                    "quantity": str(quantity),
                    "rate": str(rate),
                    "to_toman": to_toman,
                    "fee_tmn": str(fee),
                    "realized_tmn": str(pnl),
                }
            )

    def apply_fill(self, fill: Fill, fx: Decimal, atr: Decimal) -> None:
        with localcontext(Context(prec=34)):
            digest = stable_id(fill.model_dump(mode="json"))
            if fill.fill_id in self.seen:
                if self.seen[fill.fill_id] != digest:
                    raise ValueError("Conflicting fill replay")
                return
            base, quote = fill.symbol.split("/")
            if fill.price.currency != quote or fill.fee.currency != quote or fx <= 0:
                raise ValueError("Quote fee and explicit FX required")
            if quote == "TMN" and fx != 1:
                raise ValueError("TMN conversion must equal one")
            cost = fill.base_quantity * fill.price.amount
            previous = self.positions.get(fill.symbol)
            opened = previous if previous and previous.state == "OPEN" else None
            updated = apply_simulated_fill(opened, fill, atr, self.research)
            if fill.side == "BUY":
                if cost + fill.fee.amount > self.free(quote):
                    raise ValueError("Insufficient quote funds")
                basis = self._remove(quote, cost + fill.fee.amount)
                fx_pnl = (cost + fill.fee.amount) * fx - basis if quote != "TMN" else D(0)
                self._add(base, fill.base_quantity, (cost + fill.fee.amount) * fx)
                pnl = D(0)
            else:
                if fill.base_quantity > self.free(base):
                    raise ValueError("Insufficient inventory")
                net = cost - fill.fee.amount
                if net < 0:
                    raise ValueError("Fees exceed proceeds")
                basis = self._remove(base, fill.base_quantity)
                self._add(quote, net, net * fx)
                pnl = net * fx - basis
                fx_pnl = D(0)
                assert opened is not None
                self.trade_pnl[opened.position_id] = (
                    self.trade_pnl.get(opened.position_id, D(0)) + pnl
                )
                if updated.state == "CLOSED":
                    self.trades.append(
                        {
                            "position_id": opened.position_id,
                            "symbol": fill.symbol,
                            "opened_at": opened.opened_at.isoformat(),
                            "closed_at": fill.executed_at.isoformat(),
                            "pnl_tmn": str(self.trade_pnl.pop(opened.position_id)),
                            "holding_seconds": str(
                                D(str((fill.executed_at - opened.opened_at).total_seconds()))
                            ),
                        }
                    )
            self.positions[fill.symbol] = updated
            self.realized += pnl + fx_pnl
            self.fees += fill.fee.amount * fx
            self.seen[fill.fill_id] = digest
            self.events.append(
                {
                    "kind": "FILL",
                    **fill.model_dump(mode="json"),
                    "fx_tmn_per_quote": str(fx),
                    "realized_tmn": str(pnl + fx_pnl),
                    "fee_tmn": str(fill.fee.amount * fx),
                }
            )

    def valuation(self, marks: dict[str, Decimal]) -> tuple[Decimal, Decimal, Decimal]:
        with localcontext(Context(prec=34)):
            equity = unrealized = exposure = D(0)
            for asset, holding in self.holdings.items():
                if holding.quantity == 0:
                    continue
                rate = D(1) if asset == "TMN" else marks[asset]
                value = holding.quantity * rate
                equity += value
                unrealized += value - holding.basis_tmn
                if asset not in ("TMN", "USDT"):
                    exposure += value
            return equity, unrealized, exposure

    def snapshot(
        self,
        now: datetime,
        marks: dict[str, Decimal],
        rates: tuple[QuoteConversion, ...],
        pending: tuple[str, ...] = (),
        reserved_exposure: Decimal = D(0),
        reserved_risk: Decimal = D(0),
    ) -> PortfolioState:
        equity, _, exposure = self.valuation(marks)
        day = now.astimezone(ZoneInfo("Asia/Tehran")).date()
        if self.day != day:
            self.day = day
            self.daily_open = max(equity, D("0.00000001"))
        self.peak = max(self.peak, equity)
        return PortfolioState(
            account_id="backtest",
            as_of=now,
            balances=tuple(
                AssetBalance(
                    currency=asset, free=self.free(asset), reserved=self.reserved.get(asset, D(0))
                )
                for asset in sorted(self.holdings)
            ),
            positions=tuple(self.positions.values()),
            equity_tmn=equity,
            daily_open_equity_tmn=self.daily_open,
            peak_equity_tmn=self.peak,
            trading_day=day,
            gross_exposure_tmn=exposure,
            reserved_exposure_tmn=reserved_exposure,
            reserved_risk_tmn=reserved_risk,
            pending_symbols=pending,
            conversions=rates,
            risk_halted=self.halted,
        )
