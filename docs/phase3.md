# Phase 3 — deterministic strategy and risk research

This phase adds pure shared-core calculations under `src/quantpilot/trading`.
It does not add exchange execution, AI models, LLM calls, a full backtester, or
financial accounting. Legacy backend strategy/API routes remain their earlier
experimental EMA12/26 baseline; the new research implementation is separate and
uses the Phase 1 TradingEngine ports. It is not silently activated on the website.

## Run offline

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,marketdata]"
.\.venv\Scripts\python.exe -m quantpilot.trading.demo
```

Installed entry point: `quantpilot-research`. Optional explicit configuration:

```powershell
quantpilot-research --parameters config/research.example.json --risk config/risk.example.json
```

The demo uses synthetic prices, a fixed UTC clock, mock inventory/market constraints,
an explicitly approved mock account and a synthetic USDT/TMN conversion. Its price
scale and conversion are test data, not actual BTC prices. It returns an explainable
BUY and risk assessment with quantity/protection levels under default parameters;
the engine never invokes an ExecutionProvider and remains NOT_SUBMITTED. The AI
evaluator remains an abstaining placeholder. The original quantpilot-demo also works.

## Configurable research assumptions

ResearchParameters and RiskParameters are frozen validated models, loadable from
JSON. Their complete values and SHA-256 identifiers are recorded in signals and
risk decisions, alongside the snapshot hash and indicator evidence. Initial values
are hypotheses, not optimized settings or evidence of profitability.

| Parameter | Default |
|---|---|
| Entry / confirmation | 300 / 900 seconds (5 / 15 minutes) |
| Trend EMA periods | 50 / 200 |
| RSI / ATR / ADX periods | 14 / 14 / 14 |
| Breakout / previous volume window | 20 / 20 |
| Entry RSI | inclusive 50–70 |
| Relative volume | at least 1.2 |
| Confirmation ADX | at least 20 |
| ATR fraction regime ceiling | 5% |
| Stop / target | 2 / 3 entry ATR |
| Maximum holding time | 24 hours |
| Initial risk / simultaneous positions | at most 0.5% Toman equity / 2 |
| Asset / aggregate exposure | 10% / 20% equity |
| Aggregate open risk | 1% equity, including reservations |
| Daily loss / peak drawdown halt | 3% / 5% |
| Maximum spread / slippage buffer | 0.3% / 0.1% |
| Visible depth participation | at most 5% within slippage band |
| Minimum net reward/risk | 1 |
| Account/book / FX age | 30 / 60 seconds |

All these values are configurable; risk_per_trade may be reduced but this phase
enforces a 0.5% research ceiling. Approval lists, actual fee rates, minimum quantities,
quantity steps, price ticks and quote conversion are explicit inputs, never guessed
from a symbol. tzdata is declared for portable Asia/Tehran session-date checks.

## Features and regime

- EMA: first period seeded with its SMA, followed by alpha=2/(period+1).
- RSI: Wilder-smoothed positive/negative close changes; flat history gives 50,
  all gains gives 100, all losses gives 0.
- ATR: true range=max(high-low, abs(high-previous close), abs(low-previous close));
  first bar uses high-low; Wilder smoothing with a period SMA seed.
- ADX: positive/negative directional movement and true ranges start at the second
  bar, Wilder-smoothed DI and DX, then Wilder ADX; at least 2*period bars required.
- Relative volume: current closed volume divided by prior-window mean, excluding
  current volume. Missing/zero baseline gives zero relative volume, not confirmation.
- Prior rolling high/low exclude the signal candle. Current high/low cannot move
  the threshold being broken on that same candle.
- Spread: (best ask-best bid)/midpoint; bid/ask depth sums price*quantity only
  inside the configured band. These are observed depth features, not guaranteed
  executable liquidity or historical matching-engine reconstruction.

Regime priority: excessive spread -> ILLIQUID; excessive trend ATR/close -> VOLATILE;
insufficient ADX -> RANGE; otherwise EMA ordering -> UPTREND or DOWNTREND.
Indicator and strategy/risk operations use a local Decimal precision of 34 so an
unrelated caller's Decimal precision does not change decisions. The documented
initialization is part of the version, not silently interchangeable with TA packages.

## Completed multi-timeframe inputs

Strategy accepts only closed, available, contiguous, aligned candles with correct
durations. Latest candles must cover the most recent completed interval boundary
within configured lag. Both entry and trend histories must satisfy feature warmup.
MarketSnapshot rejects future event/received times. Invalid inputs produce a HOLD
with a reason rather than a fabricated indicator.

Phase 2 did not verify a native 5-minute endpoint. `timeframes.research_snapshot`
can build both research series from verified closed one-minute history. Aggregation
uses first open, maximum high, minimum low, last close, summed volume, and recorded
source IDs/timestamps. Gaps/duplicate source rows/incomplete finished buckets fail;
an unfinished target bucket is excluded. No future bars are accessed or requested.
The caller must supply enough aligned one-minute history for confirmation warmup.
No new Wallex method or resolution was assumed.

## Signals and exits

A new BUY requires approved/eligible spot market and account flags, confirmation
UPTREND, close strictly above prior high, RSI in range, sufficient relative volume
and positive ATR with valid proposed stop. Feature values and failed predicates are
included in Signal.evidence and reason codes. Entry proposals are not orders.

For an existing long, exits have precedence over entries. A stop gap uses the bar
open; otherwise stop touch is checked before target touch, including bars touching
both. Target gaps use the better open; maximum holding time and close below the
entry-timeframe fast EMA are additional exit policies. No intrabar extremes from
before the position's entry are used. Protective stop/time exits work without a
complete confirmation history. Missing/invalid entry candles still fail closed.
These are closed-bar research signals, not a guarantee of intrabar execution.

`lifecycle.simulated_fill` creates mock MARKET fills from explicit price/time/size;
there is no order-matching or realistic slippage simulation. `apply_simulated_fill`
supports opening, partial accumulation, partial exits and closing long positions.
Protection is derived from actual mock fill price and captured entry ATR. Later
partial fills cannot widen the stop. Oversells, unsupported fee currencies, invalid
times and short entry are rejected. Exact fill replays are idempotent and conflicting
fill-ID reuse fails. Quote/base fees are represented; this is position state, not
a realized Toman P&L ledger or a backtesting engine.

## Risk decisions

DeterministicRiskEngine implements RiskManager and binds immutable market contexts
for the same observation time as the generated signal. It independently regenerates
the strategy signal and verifies snapshot/parameter identity; arbitrary BUY messages
cannot substitute for the configured strategy. Bind all open-position contexts when
evaluating a new entry, not just the candidate market.

Entries require approved account, fresh account/book state, market approval,
matching strategy, fresh dated daily equity baseline and fresh conversion to Toman.
USDT and TMN are distinct; no assumed USD peg or IRR/Toman substitution is used.
The candidate and pending positions are checked by base asset, so alternate quote
markets cannot bypass allocation limits. Max concurrent count includes pending
symbols. Free balances already exclude reserved funds and must not be double-counted.

Sizing takes the minimum of fee-adjusted free quote cash, asset allocation,
remaining marked aggregate exposure, visible depth participation and risk budget.
Existing position risk includes stop distance and fee/slippage buffers; missing
position context rejects new entries. Aggregate exposure uses the greater of supplied
gross exposure or conservative marked exposure, plus pending reservations.

Planned entry uses ask plus slippage, rounded up to tick; stop is entry minus ATR
distance rounded down; target is entry plus ATR distance rounded down. Unit risk
includes stop distance plus entry/stop fees and conservative slippage buffers. Size
is always rounded down to quantity step; it is never increased to meet minimums.
Net target reward must survive fees/buffers and meet the configured reward/risk ratio.
The resulting risk budget is an estimate at these prices, not a maximum-loss promise
under gaps or outages. Recheck at actual future fills before any live integration.

Daily loss uses marked Toman equity versus the Tehran trading day's opening equity;
drawdown uses supplied high-water equity. Thresholds are inclusive. A breached or
latched breaker denies new entries and sets halt_new_entries. TradingEngine records
the decision and saves risk_halted through the injected PortfolioRepository before
publication. Resets require explicit future operator/reconciliation policy; they are
not automatically cleared by a later recovery in equity or a date change. Demo
repositories are in-memory; durable account/ledger integration remains future work.

SELL assessment is reduce-only against position quantity and free inventory, with
liquidity, step and minimum constraints. Entry loss/drawdown limits do not forbid a
protective SELL. A halted/untradable market, unavailable inventory, stale book or
insufficient minimum-size liquidity can still prevent an executable exit; this is
reported as rejection, not claimed to have sold. Partial risk-approved exit size may
leave a remainder requiring subsequent observations.

## Boundaries and verification

All Phase 3 tests use synthetic fixtures and mock fills; no exchange reads, orders,
private account information, LightGBM or LLM are used. Tests cover known indicator
values, default BUY, HOLD rules, SELL policies, warmup/gaps/future data, timeframe
aggregation, risk sizing/buffers/rounding, approval/currency/freshness, fees, exposure,
loss/drawdown/persistent halt, reserved inventory, duplicate fills and shared-engine
no-submission behavior. Run pytest, Ruff and mypy using pyproject.toml.

Research results do not establish profitability. Full backtesting, live accounting,
exchange precision/fee adapters, market resynchronization and execution/reconciliation
remain later phases. LIVE remains blocked by existing core configuration and engine.

Final checks: **69 tests passed**, with one existing opt-in PostgreSQL cluster test
skipped. Ruff passed; strict mypy passed for 24 source files. The editable package
installation and installed quantpilot-research entry point were verified. Repeating
the example-config demo produced byte-equivalent parsed decision records, a BUY
with risk-approved size and NOT_SUBMITTED. The checks made no exchange requests.
