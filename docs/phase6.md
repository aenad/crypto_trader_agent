# Phase 6 — Live SHADOW and deterministic replay

## Boundary

`quantpilot.shadow` runs a persistent, single-writer virtual trading account on
public Wallex observations. It reuses the unchanged Phase 3 strategy, features,
risk and lifecycle; Phase 4 Decimal portfolio ledger and pending-order model;
and Phase 5 frozen LightGBM inference, analyst harness and veto-only fusion.
Existing historical CLI/API behavior is preserved. No real exchange execution
adapter is accepted by the shadow engine. `mode` accepts **SHADOW only**.

Every balance, reservation, fill, order and PnL is hypothetical. Initial capital
defaults to **5,000,000 Toman**, not IRR. This is prospective research infrastructure,
not LIVE deployment or evidence that a strategy/model is profitable.

## Commands

Install the existing optional extras and register the CLI:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,marketdata,ai]"
```

Copy `docs/examples/shadow-hybrid.example.json` to your own configuration. Its
precision/minimum/fee values are **paper-research placeholders**, not newly
verified exchange trading constraints or authenticated account permissions.
Supply explicitly approved competition pairs, reviewed constraints/fees, a
frozen model path, and the exact research parameters used to train that model.
Copy those research parameters from the training dataset manifest. The loader
rejects a model/feature-parameter mismatch instead of silently adapting it.

```powershell
# Foreground runner; keep this terminal open.
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli start --config shadow.json --db data/shadow/session.sqlite --responses data/shadow/responses

# In another terminal:
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli portfolio --db data/shadow/session.sqlite
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli health --db data/shadow/session.sqlite
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli stop --db data/shadow/session.sqlite
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli export --db data/shadow/session.sqlite --output artifacts/shadow-export
.\.venv\Scripts\python.exe -m quantpilot.shadow.cli replay --db data/shadow/session.sqlite --responses data/shadow/responses --output artifacts/shadow-export/replay.json
```

Installed equivalent: `quantpilot-shadow`. `start --max-cycles 2` provides a
bounded observation check. Same-config restart restores the same virtual account.
Use a new dedicated database for a different experiment; existing unrelated
database tables or config/source/model changes fail closed.

`QUANT_ONLY` is an explicit diagnostic mode requiring no model; it is never
presented as an AI-enabled run. `QUANT_ML` and default `QUANT_ML_LLM` require an
actual compatible frozen model. Research artifacts stay research-only.

### Analyst configuration

Without `--allow-llm-network`, the analyst uses recorded responses only. A cold
cache abstains and blocks hybrid entries. It does not fake an LLM response.
To collect real responses, supply the Phase 5 HTTPS JSON gateway contract,
`analyst_model_id`, and a dedicated **QUANTPILOT_LLM_TOKEN** environment variable,
then add `--allow-llm-network`. No token belongs in the JSON configuration.
The CLI never loads `.env` or reads Wallex/account credentials. No real analyst
provider has been configured or verified in this repository's public smoke run.

## Data path and freshness

The default REST path wraps existing verified public adapters with a transport
guard: only HTTPS GET to four approved public Wallex paths, no redirects,
Authorization/X-API-Key/cookie headers, private account reads or mutations.
`public_transport=MCP` uses the existing keyless MCP connection, session tool
discovery and fixed public-read tool mapping. A capability wrapper rejects all
non-public operation names before reaching either transport. The LLM receives
neither source/transport objects nor order methods.

The verified candle normalizer supports resolution `1`, so the live collector
requests completed **one-minute** candles and uses the shared past-only resampler
for entry/trend timeframes. It does not invent a five-minute API contract.
Bootstrap covers indicator warmup, starts on a trend boundary, then caches and
backfills only missing completed minutes. Missing coverage, malformed payloads
or unavailable approved spot markets reject a poll. No historical books are
derived from candles.

Depth is fetched after history. The verified public depth response has no exchange
timestamp; frames explicitly label **observation timestamps**, not guaranteed
exchange-generation freshness. Slow depth requests, aged quotes/candles/FX and
incomplete universes fail freshness checks. A fresh observation cannot prove
the server's underlying book is current. Approved markets are rescanned at least
every 60 seconds. Strategy permissions/precision/fees come from reviewed static
experiment configuration, not invented private-account discovery.

Network retries/backoff and 429 handling reuse Phase 2 transports. The outer
runner records a sanitized interruption, waits, reconnects and backfills. It
creates no market events/fills during outages and never executes missed historical
signals as if they had traded. Invalid timestamps or unrecoverable journal/state
errors stop processing rather than silently repairing financial history.

## Decision and fill sequence

For each recorded frame:

1. Validate the configured universe, market constraints and monotonic frame time.
2. Mark virtual inventory at observed bids with explicit TMN conversion. Stale
   marks remain last-known and are labeled stale, never presented as current.
3. Expire pending virtual orders. Cancel pending buys on stale portfolio context,
   a latched loss/drawdown stop, or an observed protective exit for a partial entry.
4. Fill earlier intentions only against a **later observed book**; no same-book
   decision fill, last-trade-price fill or OHLC fallback.
5. Evaluate the quant strategy once per new completed entry candle per pair.
   Quote-only polls are recorded but do not generate duplicate strategy decisions.
6. Run independent ML/analyst fusion for fresh BUY candidates. Missing/invalid AI
   abstains. Risk checks the original canonical signal last. SELL never depends
   on AI availability. Record HOLD, stale, risk/AI rejection, already-pending and
   accepted outcomes with original signals, model/candidate/analyst output and
   before-decision portfolio.
7. Reserve virtual funds for accepted intentions; atomically commit outputs and
   checkpoint. A later poll is required to fill the order.

The live simulator walks actual observed bid/ask levels, shares per-side capacity,
uses configured depth participation/adverse slippage/tick rounding and quote fees,
and handles partial fills/reservations/expiry. Buys cannot exceed approved price
or FX budgets. Re-reading the same book identity cannot replenish capacity.
Different later observations renew the participation cap: queue position,
unobserved turnover and market impact are not known or claimed. Only virtual
MARKET intentions are supported by this runner; historical limit simulation
remains in Phase 4. This pending-order/TTL policy is a disclosed paper model,
not an asserted Wallex market-order lifecycle contract.

For USDT pairs, configure `fx_market` with explicit `USDT/TMN` constraints. The
initial funding fraction can purchase virtual USDT at observed ask plus adverse
slippage/fees, capped by observed participation and rounded/minimum constraints.
Remaining cash stays TMN. Bid conversion values quote/base inventory; no USD peg,
automatic borrowing or unreviewed conversion rate is used. Funding is a separate
bounded initial paper allocation, not a strategy-authorized real order.

Existing closed-bar stop/target/EMA rules remain unchanged. Exits execute at a
later available live book, not at an idealized stop price. Outages/polling can miss
intermediate triggers; virtual protection and fill quality are not guaranteed.

## Persistence, stop and recovery

A dedicated SQLite database uses:

| Record | Purpose |
|---|---|
| Manifest | Full configuration, core/exclusion-policy versions and frozen model identity |
| Durable inbox | Exact compressed normalized market frame before evaluation |
| Frame result | Every decision, accepted/rejected candidates and recorded analyst outcomes |
| Checkpoint | Decimal balances/basis, positions, orders/fills, reservations, clock, risk latch, marks and processed candle keys |
| Operational log | Acquisition/processing/AI/LLM timings, interruptions and health events; separate from financial decisions |

One SQLite transaction commits a frame result and its checkpoint. JSON state
snapshots copy mutable lists/maps; rollback cannot leave orphan fills, seen IDs,
consumed books or processed-candle keys. Ambiguous local commit returns reload the
authoritative checkpoint. Incomplete inbox frames are recovered before new polls,
with analyst network calls disabled during recovery. Exact duplicate frames/order
IDs are idempotent. A writer lease plus heartbeat prevents concurrent account
writers; a hard-killed worker's lease expires after 60 seconds. This is local
virtual-account consistency, not a claim about exactly-once exchange execution.

`stop` requests a cooperative drain of an in-progress transaction. It does not
kill arbitrary processes or invent liquidation fills. Positions and pending
intentions remain persisted/frozen while stopped; restart applies expiry/freshness
before new fills. Feed calls and analyst timeouts are bounded, so stopping may
wait for an in-flight operation. No funds move at any point.

The journal has input/output/state hashes and a chain. Replay/export first take a
consistent SQLite backup, so a running writer cannot change their read window.
Frames and activity exports stream rather than loading a multi-day candle journal
at once; frames are compressed. Metadata/checkpoints are explicit JSON, not pickle.
Hashes detect accidental changes, not forgery by a filesystem administrator.
Retain original source/environment/model artifacts and back up the full experiment.

## Deterministic replay

Replay requires matching source/strategy/features/risk/exclusion-policy versions
and a compatible LightGBM artifact (`--model` may locate the identical artifact
elsewhere). It reconstructs the virtual account from initial capital and feeds
stored observations through the **same ShadowEngine**, independently recomputing
features, model scores, fusion, risk, orders and financial accounting.

Successful analyst outputs **and failures/abstentions** are frozen in each decision.
Replay uses those exact outcomes, not whatever later appeared in a global cache.
It validates context/schema/model identity and performs zero provider network
calls. Operational wall-clock durations/cache-delivery statuses are excluded
from decision hashes, while data times and model outputs remain included.

The comparison reports per-frame decision/output and state equality. `MATCH`
requires both; `DIVERGED` exits nonzero. Missing artifacts, version mismatch or
hash corruption fail explicitly rather than being labeled a match. Incomplete
uncommitted frames are counted separately and not presented as original decisions.

## Health and activity

`GET http://127.0.0.1:8766/health` (or the printed ephemeral port) is loopback-only,
read-only, and has no exchange credentials. POST is rejected. Healthy service
returns 200; stale/degraded/stopping/unavailable returns 503. The CLI also reports
STOPPED after the server shuts down.

Health distinguishes running lease, stop request, last market age, stale
observations, interruption state, AI status, recovery backlog, virtual portfolio
as-of and acquisition/processing/AI/LLM latency. Market health with AI
`NOT_YET_OBSERVED` does not verify a model/provider call; an unconfigured analyst
is explicitly recorded-response-only. `portfolio` includes reserved balances,
position/order state, realized TMN PnL, fees and last-known equity context.

`export` writes `frames.jsonl`, `operations.jsonl`, `manifest.json`, `portfolio.json`.
Frame results contain accepted/rejected decisions, fees/PnL/equity, orders and
staleness. No export claims that virtual PnL is competition-account performance.

## Verification and phase boundary

See [Phase 6 verification](PHASE6_VERIFICATION.md) for actual checks and limits.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src/quantpilot tests
.\.venv\Scripts\python.exe -m mypy src/quantpilot
```

Failure injection covers network loss, invalid/gapped feeds, stale depth, duplicate
frames, partial-fill restart, failures before/after commit, mutation/private-access
attempts, competing leases, state corruption, analyst failures and changed caches.
Full AI tests train real LightGBM against explicit synthetic fixtures, exercise
the harness/fusion/risk, and reproduce both successful and failed analyst outcomes.

Phase 6 stops here. No long-duration stability evidence, real LLM efficacy,
production model promotion, authenticated competition-account reconciliation or
LIVE order adapter is established or enabled.
