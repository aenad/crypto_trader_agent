# Phase 7 verification — 2026-10-23

## Executed checks

Environment: Windows, existing `.venv`, fake credentials supplied explicitly in
tests. No `.env` file or real API key was loaded by this implementation.

| Command | Observed result |
| --- | --- |
| `.venv\Scripts\python.exe -m pytest -q --junitxml=data/live/phase7-tests.xml` | **213 passed, 1 skipped**, 39.17 s |
| `.venv\Scripts\python.exe -m pytest tests/test_live.py -q` | **42 passed**, 4.05 s |
| `.venv\Scripts\python.exe -m ruff check src/quantpilot tests` | All checks passed |
| `.venv\Scripts\python.exe -m mypy` | Success, **60 source files** |
| `.venv\Scripts\python.exe -m quantpilot.live.cli --help` | status/kill/export help, successful exit |
| Disabled example parsed with `LiveConfig.model_validate_json` | Valid template; `enabled=False` |

The skipped test is the pre-existing PostgreSQL integration test, which requires
explicit `QUANTPILOT_RUN_POSTGRES_TEST=1`. No database server was started for Phase 7.
JUnit results are stored in ignored `data/live/phase7-tests.xml`.

## New offline coverage

- Default/separate activation, permission flags, account type, credential scope.
- Exact-intent canonical strategy/risk authorization; fabricated signals rejected.
- Idempotent submission, changed-intent client-ID collision, stale authorization.
- Committed send boundary, ambiguous submission, unresolved status, restart recovery
  and explicit resume without repeated POST.
- Cumulative partial fills, quote fees, base fees, identical legitimate fill rows,
  exact balance math, fill deduplication and missing history rejection.
- Cancellation, partial cancellation, cancel/final-fill races and lost cancel response.
- Foreign open orders, balance drift, precision changes, stale data and network failure.
- Transient read recovery/backoff, persistent kill and drawdown suspension.
- Deadline window, reducing final liquidation, residual dust, unknown cancel stops,
  stale/kill protection and refusal to submit after the deadline.
- Single-writer locking and audit-chain modification detection.
- Fixed host/header/path contracts, redacted failures and no mutation retry on
  404/409/429/500/redirect responses or timeout.
- Raw transport mutations disabled unless a separate durable mutation guard exists.
- Explicit FREE/TOTAL balance normalization, aligned account/market decision times
  without rewriting actual depth timestamps.
- Local status/export and an external kill file while the database writer is active.

## Evidence boundaries

All new exchange integration tests use an injected in-memory exchange or
`httpx.MockTransport`. They never connect to Wallex. The restricted-key values
in fixtures are deliberately fake. The implementation did not submit, cancel,
modify or withdraw anything on an exchange and did not call private read endpoints.

Official documentation search excerpts support the implemented endpoint subset;
direct page fetches failed. Current authenticated response shapes, real account
identity/key permissions, balance semantics and competition credit routing remain
unverified. The default template is not exchange-validated metadata.

Passing mocks validates the implemented safety behavior, not actual exchange
compatibility, real fill availability, trading profitability, real AI quality or
deployment readiness. Account/permission evidence is operator attestation, not
invented exchange introspection. See the separate
[LIVE activation checklist](LIVE_ACTIVATION_CHECKLIST.md).

Phase 7 stops here. LIVE was not activated and Phase 8 was not begun.
