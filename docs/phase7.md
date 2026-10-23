# Phase 7 — Protected spot execution

**Status:** implemented and tested with fake accounts and injected exchanges only.
LIVE is disabled by default. No credentials were loaded, no private exchange
endpoint was called, and no exchange order was submitted during implementation.
This is an additive execution adapter, not approval to deploy a trading service.
See [activation checklist](LIVE_ACTIVATION_CHECKLIST.md) before any activation.

## Architecture and compatibility

`quantpilot.live` is separate from SHADOW, the legacy web API and the analyst harness.
The existing `ExecutionProvider` signatures are implemented by `ProtectedExecution`.
`strategy_cycle` uses unchanged MomentumBreakout and DeterministicRiskEngine to
propose intents. `authorize` independently recomputes canonical risk; passing an
arbitrary intent or an AI recommendation to `submit` is insufficient. Authorizations
are short lived, bound to an exact intent and invalidated on reconciliation or send.
The first submission invalidates the other proposals: reconcile before the next.
Account observations and decision snapshot `as_of` are aligned after reconciliation;
actual book/candle timestamps are preserved. `decision_context` exposes that immutable
cut to external strategy callers, so normal network latency does not create a
future-account/old-signal mismatch. Source implementation hashes are pinned in the
journal; changing packaged core code requires a reviewed migration before restart.
There is deliberately no web/LLM order tool and no automatic LIVE runner.

| Module | Responsibility |
| --- | --- |
| `live/domain.py` | Disabled config, separate operator grant, immutable order evidence |
| `live/transport.py` | Fixed official HTTPS host and allowlisted spot REST contracts |
| `live/storage.py` | Dedicated single-writer SQLite journal, atomic fills/positions, audit chain |
| `live/execution.py` | Risk authorization, checks, execution/recovery, suspension/liquidation |
| `live/cli.py` | Local status, emergency kill file and audit export; no activation |

No new production dependencies. Private HTTP uses the existing `marketdata` extra.
The legacy EngineConfig's LIVE prohibition remains intact. BACKTEST, SHADOW,
strategy/risk source and frozen AI artifact implementation hashes are unchanged.
The existing pure position reducer consumes actual validated fills; its name
`apply_simulated_fill` is historical. It does not synthesize execution prices.

## Supported deployment envelope

- Dedicated **main spot account**, initialized with exactly the configured Toman
  capital and no crypto inventory, locked funds or open orders. Default capital
  is 5,000,000 TMN; TMN is Toman, never silently converted from IRR.
- Explicit approved direct `BASE/TMN` markets; the existing 344 excluded markets
  remain forbidden. Current exchange quantity/price precision, minimums, maximum
  quantity and account fee bounds must match pinned constraints on reconciliation.
- LIMIT orders with explicit base quantity and capped price. BUY sizing remains
  the existing risk sizing; execution additionally caps each order's notional,
  available funds plus worst-case fees, executable depth, freshness and slippage.
- One outstanding exchange order globally, while retaining the configured position
  count/exposure/risk limits. This conservative serialization avoids concurrent
  pending-order risk reservations being understated.
- SELL quantities are reduced for a possible base-asset fee. Residual dust is
  reported; liquidation never claims a guaranteed fully cash portfolio.

**Unsupported and fail-closed:** credit/prop/subaccount routing, margin, OTC,
withdrawals, imported inventory/cost basis, USDT settlement/conversion routes,
MARKET orders, conditional exchange stops, unrecognized order states or grouped
open-order response shapes. No undocumented endpoint has been guessed.

## Account and permission evidence

Official main-account balance APIs are not proof of competition-account routing.
No verified endpoint in the inspected contracts establishes key permissions or
competition account identity. `AccountAuthorization` is **operator evidence**:
account type, read/trade permissions, disabled withdrawals, credential fingerprint,
scope/config hash, evidence reference and validity interval. It is not presented
as exchange-attested permission introspection. Credit accounts cannot be enabled
through this grant. Live deployment remains blocked until this external evidence
is actually obtained and reviewed.

The docs describe `value` and `locked` without resolving whether value includes
locked funds. The grant must record experimentally verified FREE or TOTAL semantics;
there is no guessed default. Automated tests verify both normalizations offline.
Changing the credential/account/semantics binding requires a separately reviewed
migration, not silent reuse of a journal.

## Durable order lifecycle

1. Reconcile all unresolved local client IDs using GET. Fetch official constraints,
   fees, the complete open-order list and balances; compare against owned fills.
2. Verify market context and evaluate the unchanged strategy/risk core. Journal
   accepted/rejected risk decisions before authorizing an exact LIMIT intent.
3. Persist PREPARED, then SUBMITTING, **before** the single POST attempt.
4. Validate response identity, quantity/status consistency and complete cumulative
   fill quantities/costs/fees. Commit order, newly applied fills and position/balance
   updates atomically. No assumed fills at the last market price.
5. On timeout, malformed response, cancellation or HTTP failure: retain UNKNOWN,
   latch suspension and require reconciliation. Even 404/409/422 is not a license
   to resubmit. Reusing a client ID with another intent is rejected. Repeating the
   same intent returns local state and never POSTs again.
6. Cancellation persists CANCELING before DELETE, then queries actual status.
   A cancel/fill race may end FILLED. Ambiguous cancellation is resolved by GET
   before another cancel action; no automatic repeated DELETE.

Docs expose cumulative fill details without immutable trade IDs. The adapter
assigns canonical content + occurrence IDs per order, preserving legitimate
identical fills. Previously observed fills may not disappear/change. Incomplete
history halts execution rather than reconstructing fictitious fills from averages.
This is conservative local idempotency, **not** an exchange exactly-once guarantee.

## Recovery, reconciliation and stops

Recovery retries reads only (bounded 1–5 attempts with exponential backoff);
POST/DELETE are never retried automatically. The transport serializes/throttles
requests below the documented submission limit; 429 suspends rather than bursts.
Successful recovery does not auto-clear a suspension. An operator can explicitly
resume only with fresh reconciliation and no persistent drawdown/daily-loss latch.

Reconciliation requires exact total balances from the initial account plus owned
fills, accounted base inventory, the exact set of owned active client IDs and
explained locked balances. External deposits/trades/orders, precision/fee changes,
missing/duplicate pagination rows, stale depth and unknown order state stop entries.
Asynchronous exchange reads are not a transactional snapshot: a fill occurring
between reads may conservatively cause a suspension and another read cycle.

Virtual positions are not substituted for exchange inventory. Real cumulative fills
reconstruct owned positions (including base/quote fees); observed free/locked account
balances are reconciled before reusing them for risk. Mark-to-bid Toman equity,
daily opening equity and high-water mark persist; configured daily loss/drawdown
thresholds latch suspension. Reliable risk-approved reducing exits remain possible
under loss suspension; a hard kill blocks new orders including liquidation.

The kill file works across processes without acquiring the execution writer lock.
It is checked on each mutation gate. A kill cannot recall an already in-flight
request or cancel exchange-resident orders by itself; cancellation remains an
explicit authenticated owned-order operation. Recovery/status queries are allowed.
After a hard kill, inspect/reconcile and cancel owned open orders explicitly.

## Deadline liquidation

`final_liquidation(snapshots)` is a bounded, resumable tick, called by the operator's
execution service with fresh data. It begins only inside the configured lead window
and stops at the exact configured deadline. It cancels owned open orders, resolves
their terminal states, reconciles balances, then submits fee-buffered reducing LIMIT
sales into observed bids. This dedicated deterministic reduction policy bypasses
entry-loss suspension, not activation/account/market/kill/reliability gates.
Unknown cancel status, stale data, missing liquidity or insufficient minimum order
size prevents a sale. Repeated ticks reconcile actual residuals; they never assume
completion or use undocumented liquidation/transfer APIs. An external scheduler is
required; no unattended live process was started or installed in Phase 7.

## Operational commands (local only)

```powershell
python -m quantpilot.live.cli status --config config/live.local.json --db data/live/execution.sqlite
python -m quantpilot.live.cli kill --config config/live.local.json --db data/live/execution.sqlite
python -m quantpilot.live.cli export --config config/live.local.json --db data/live/execution.sqlite --output data/live/audit.jsonl
python -m pytest tests/test_live.py -q
```

The installed equivalent is `quantpilot-live` after `pip install -e ".[dev,marketdata]"`.
Status/export require the writer to be stopped; kill works while it is running.
Export creates a new file, never overwrites one, and contains account-sensitive
decision/financial evidence. Protect the execution directory with OS ACLs and backups.
SQLite's hash chain detects edited audit rows; it is not cryptographically signed
external evidence and cannot prevent a privileged user replacing the entire database.

Programmatic activation is intentionally separate: load reviewed LiveConfig and
AccountAuthorization files, create LiveStore and an injected Clock, then call
`activated_adapter`. It checks the dedicated environment variables
`QUANTPILOT_WALLEX_LIVE_API_KEY` and `QUANTPILOT_LIVE_AUTHORIZATION` (the exact enabled
config hash). Bootstrap only the reviewed empty account, recover fresh snapshots,
then explicitly submit authorized intents. Close the REST client and store on exit.
Do not pass this adapter or credential mapping into any analyst/harness object.

## Evidence and limitations

Endpoint evidence is [recorded separately](evidence/wallex-live-contracts.json).
Official documentation/search excerpts were inspected; direct documentation page
fetches returned errors. No authenticated response shape, account type/permissions,
key restriction, server client-ID uniqueness guarantee or real cancellation/fill
behavior was verified. This phase provides deterministic software safeguards, not
production certification, financial performance evidence or deployment authorization.
See [verification report](PHASE7_VERIFICATION.md) for exact offline checks.
