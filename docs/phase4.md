# Phase 4 — Historical replay and Toman accounting

## Scope

The additive `quantpilot.backtest` package directly uses Phase 3's unchanged
`MomentumBreakout`, `MarketEligibilityFilter`, `DeterministicRiskEngine` and
`apply_simulated_fill`. No strategy rewrite, AI, live adapter or production
dependency was added. The legacy API/UI is not connected to this offline runner.
Continuous SHADOW recovery remains future work.

Default capital is **5,000,000 TMN (Toman)**, not IRR. Financial calculations use
Decimal in an explicit 34-digit context. JSON represents monetary values as
strings. Synthetic examples verify mechanics, not profitability.

## Commands

Use the existing environment from the repository root:

```powershell
.\.venv\Scripts\python.exe -m quantpilot.backtest.cli --output artifacts/backtest-demo --sensitivity
.\.venv\Scripts\python.exe -m quantpilot.backtest.cli --input history.json --output artifacts/backtest-history --sensitivity
```

After `python -m pip install -e ".[dev,marketdata]"`, the equivalent installed
entry point is `quantpilot-backtest`. The marketdata extra is only needed for
optional Parquet import; JSON/demo backtesting needs no marketdata dependencies.

Generate a complete input example offline:

```powershell
.\.venv\Scripts\python.exe -c "import json; from pathlib import Path; from quantpilot.backtest.cli import demo_input; Path('history.json').write_text(json.dumps(demo_input(), indent=2), encoding='utf-8')"
```

### Input contract

| JSON key | Meaning |
|---|---|
| `candles` | Map canonical pair to chronological domain `Candle` objects |
| `markets` | Map pair to explicit Phase 3 `MarketConstraints` objects |
| `approved` | Explicit competition-approved pairs |
| `quotes` | Optional pair to chronological recorded `LiquiditySnapshot` objects |
| `fx` | Optional ordered `QuoteConversion` objects: quote USDT, tmn_per_unit, as_of |
| `research` / `risk` | Optional Phase 3 parameter overrides; defaults unchanged |
| `simulation` | Optional `SimulationParameters` overrides |

Phase 2 Parquet candle batches may replace the JSON candle map. Supply market,
approval, configuration and FX metadata in `--input`; repeat `--parquet` per file:

```powershell
.\.venv\Scripts\python.exe -m quantpilot.backtest.cli --input metadata.json --parquet data/candles/BTC_TMN/batch.parquet --output artifacts/backtest-history
```

The importer validates `payload_json` candles and sorts by open time. Overlapping
batches, duplicates and gaps fail rather than being silently merged.

## Event ordering

1. HistoricalClock advances monotonically through candle opens/closes.
2. Resting limits are evaluated at close, then inventory is marked and equity sampled.
3. Build completed point-in-time entry/trend snapshots with the Phase 3 resampler.
   Run the exact strategy and risk functions in sorted pair order; record every
   signal/risk outcome, including HOLD and rejection.
4. Reserve approved order funds. Buy reference price is a maximum, not a promised
   fill. Pending entry notional is conservatively reserved as both exposure and
   risk. Protective SELL cancels unfinished entries; risk halts cancel pending buys.
5. Execute markets at the following bar open. At shared timestamps, prior close
   decisions precede next open. A signal cannot fill in its generating candle.
6. Mark after opens/fills. At final close cancel pending orders, attempt explicit
   reduce-only liquidation, then convert free USDT to TMN.

Phase 3 stop/target/EMA/max-hold decisions are preserved, but fills occur at the
next available open, **not at the theoretical stop or target**. No resting
intrabar stop-order model is claimed. Final liquidation is a separate disclosed
simulation policy, not a fabricated canonical strategy SELL.

## Execution assumptions: engineering decisions, not exchange facts

| Available history | Fill policy |
|---|---|
| Fresh recorded book at open | Walk sorted levels; shared per-side participation capacity, adverse slippage/tick rounding |
| OHLCV market | Next bar open with adverse spread/slippage; **previous completed bar** volume participation cap |
| OHLCV limit | Must rest before open and penetrate limit by configured ticks; no improvement; shared close-time volume cap |
| Terminal recorded book | Best bid only; participation cap, adverse slippage and terminal haircut |
| Terminal OHLCV | Final close discounted by spread/slippage/haircut; final volume cap minus same-timestamp fills |

OHLC proxy spread/depth is explicitly assumed input to the unchanged risk engine,
never an observed/reconstructed historical book. Volume partial fills are scenario
assumptions, not claimed historical volume distribution. Books are sampled at
bar boundaries; intra-bar quote events, queue position and network latency are
not simulated. Buy price/FX gaps beyond approved budgets cancel orders; expiry
releases reservations. Quantity steps, adverse price ticks and minimum constraints
apply. Actual fills can be smaller than risk-approved size.

Quote-currency fees use the greater of configured entry/exit fee and explicit
market taker fee. Rebates, maker tiers and base-currency fees are unsupported.
Defaults: half-spread 0.05%, slippage 0.1%, entry/exit 0.1%, volume participation
1%, recorded-book participation 10%, expiry 900 seconds, limit penetration one
tick, terminal haircut 0.2%, FX fee 0.1%. All are configurable research scenarios,
not asserted Wallex measurements. Sensitivity scenarios double spread/slippage/
entry/exit fees and separately halve volume/book participation. No optimization
or recommendation is implied by these tests.

## Historical integrity and FX

- Reject open, gapped, duplicate, overlapping, unordered and mismatched candles.
  Markets must share first open/final close. Publication must equal candle close;
  downloaded receipt time is replaced by this declared publication time.
  Latency-aware publication replay is unsupported and fails explicitly.
- One route per base asset; cross-quote routing is unsupported. USDT/TMN funding
  uses explicit FX history rather than a strategy market.
- Market permissions/fees/constraints are explicitly supplied and static during
  the run. Point-in-time changes require separate inputs/runs.
- USDT markets require fresh point-in-time USDT/TMN history throughout the run;
  no assumed peg, present-day conversion or forward lookup.
- Default USDT funding converts 25% of starting TMN once, with fee; fraction is
  configurable, including zero. Supplied FX is assumed executable. FX spread/
  impact beyond that rate/fee and automatic cash rebalancing are not modeled.
- Reports include warmup/funding costs. The input's final close is the competition
  deadline; select the intended three-day window explicitly.
- Unfillable dust/terminal capacity shortfall is reported as residual inventory,
  never claimed to have been liquidated. Final marked equity and realized PnL
  remain separate.

## Accounting and reports

The ledger tracks total/free/reserved balances, average TMN cost basis, long
positions and fill IDs. Exact duplicate fills are idempotent; conflicting replays,
overspend/oversell and reserved-fund spending fail. Entry fees enter base basis;
net sell proceeds minus allocated basis realize PnL. Spending/converting USDT
realizes its FX gain/loss against original TMN basis. Sale proceeds acquire basis
at contemporaneous FX; this avoids double-counting currency gains.

Equity is cash plus bid-marked inventory. Unrealized PnL is marked value minus
remaining basis. Peak equity includes unrealized movements; daily baselines use
Asia/Tehran dates. Round trips aggregate partial exits, including entry/exit fees.
FX conversion PnL/fees affect the account but are not counted as strategy trades.

Outputs: `report.json`, `metrics.csv`, `equity_curve.csv`, `ledger.csv`, `trades.csv`,
`decisions.csv`, `orders.csv`; sensitivity subdirectories contain the same files.
Reports include config/input/run hashes, engine version and assumptions. Retain
exact input and source revision for replay.

Metrics: net return %, realized/unrealized TMN PnL, marked max drawdown %, win
rate, profit factor, closed round-trip count, fill count, average closed-trade
holding time, total fees, time-weighted/max exposure, equity curve. Win rate counts
strictly positive closed trades. No-trade win rate/holding time are null. Profit
factor is null with `NO_REALIZED_LOSSES` when its denominator is zero. Exposure
excludes uninvested USDT and is piecewise constant between sampled events.

## Checks and phase boundary

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src/quantpilot tests
.\.venv\Scripts\python.exe -m mypy src/quantpilot
```

Tests cover hand-calculated TMN/FX basis and fees, weighted partial exits,
reservations/atomic rejection, replay conflicts, market/limit simulation, shared
capacity, book walking, adverse gaps, expiry, actual-trade deterministic replay
and future append invariance, metrics, terminal residuals and CLI sensitivity
exports. PostgreSQL remains an opt-in Phase 2 test. Backtesting uses no database,
credentials or network. Phase 4 ends here; no continuous SHADOW, AI or LIVE gate
is enabled by backtest results.

Verified locally on 2026-10-23: **90 passed, 1 skipped** (the existing opt-in
PostgreSQL server test); 21 Phase 4 tests passed. Ruff passed and strict mypy
passed for all 32 packaged source files. The full synthetic demo and both
sensitivity scenarios generated reports in `artifacts/backtest-final` (ignored
generated artifacts). Baseline closed one synthetic round trip with three fills;
half-capacity scenario used five fills; doubled costs produced no approved
trades. These outcomes verify plumbing/parameter sensitivity only. Editable
installation with `--no-deps` succeeded using isolated build requirements; no
production dependency was added.
