# Phase 6 verification — 2026-10-23

## Executed checks

- Public unauthenticated Wallex GET checks returned 50 bid and 50 ask levels for
  BTC/TMN, a market list containing 373 spot markets including BTC/TMN, and 15
  consecutive completed one-minute BTC/TMN candles with full requested coverage.
  These are time-specific observations, not permanent market availability claims.
- An initial bounded run recorded two live frames and one decision and replayed
  with identical decisions and virtual financial state.
- After the mutable-checkpoint recovery fix, a final bounded owned subprocess
  started the hybrid-configured runner against actual public feeds. The localhost
  health endpoint returned **HTTP 200 / HEALTHY** after its first committed frame.
  The CLI stop request exited cleanly and released the writer lease.
- Final journal replay: **MATCH**, one committed frame, one strategy decision,
  matching output and virtual state, no pending recovery frames and zero LLM
  network calls. Export completed successfully.
- The live strategy decision was HOLD. No virtual fill occurred in this short
  live check; paper entry/partial/exit fills are verified by automated fixtures.
- A frozen Phase 5 LightGBM artifact loaded successfully. The analyst was
  **unconfigured/recorded-response-only**. The HOLD did not invoke the AI evaluator;
  actual live inference/provider efficacy is not claimed. Tests separately verify
  real LightGBM inference plus both analyst acceptance and failure paths.
- No Wallex/account key was loaded, no private-account endpoint was queried and
  no real exchange order/cancel/transfer was submitted.

Local generated evidence (ignored by Git):

```text
data/shadow/phase6-final/session.sqlite
data/shadow/phase6-final/health-observed.json
data/shadow/phase6-final/replay.json
data/shadow/phase6-final/export/
```

The experiment uses synthetic-trained research AI and explicitly supplied paper
fee/minimum/precision assumptions; it is not a validated competition configuration.
Earlier development smoke journals are retained and may require their exact source
revision for replay. The final journal matches the completed Phase 6 source.

## Automated verification

**171 tests passed; 1 skipped** (existing opt-in PostgreSQL server integration).
Ruff passed. Strict mypy passed for **54** packaged source files.

New failure/recovery checks include:

- Public GET/MCP capability allowlists block order, cancel, transfer, private-read
  and credential-header attempts before transport invocation.
- Real-book-only next-observation fills, shared depth partials, duplicate-book
  suppression, Toman fees/PnL and position/order restoration.
- Strategy decisions occur once per closed candle; quote-only frames remain
  journaled; stale observations cancel pending buys without fabricated fills.
- Temporary network loss recovers without invented market events. Malformed,
  missing and gapped data fail validation. HTTP health is read-only.
- Before-commit and after-commit injected failures recover the authoritative
  checkpoint. A failed fill commit leaves no orphan ledger events, seen-fill IDs,
  processed-candle keys, reservation changes or virtual depth consumption.
- Pending inbox recovery, writer lease exclusion, hash-chain corruption detection,
  consistent SQLite export snapshots, and CLI stop/portfolio/export/replay.
- Actual LightGBM inference, validated analyst fixtures/failures, fusion and final
  deterministic risk gate. Recorded failure outcomes replay identically even if
  the global response cache later acquires an approval.
- Observed-ask USDT funding respects depth capacity and preserves the Toman
  equity/realized/unrealized identity; a marked drawdown cancels partial entries.
- The health POST rejection test passed three repeated runs after a Windows
  socket-reset issue was fixed by draining bounded small request bodies before 405.

## Limits

This was a short public connectivity/recovery/software check, not a three-day
shadow soak test. Public depth timestamps are observation times, not independently
verified exchange-generation times. Queue position, market impact and real fill
quality are unknown. No real analyst provider or private competition account was
validated. AI deployment and LIVE execution remain disabled.
