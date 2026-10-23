# Spot-only enforcement ? implementation and verification

Date: 2026-10-23. Authority: ../SPEC.md permanent spot-only amendment.

## Scope and findings

The packaged project already used a shared Python Trading Core, Momentum Breakout +
regime detection, canonical risk recomputation, fee-aware cash sizing, owned-position exits,
a Decimal average-cost virtual wallet, partial/reserved simulated fills, AI entry vetoes,
public-only SHADOW, and separately authorized MAIN_SPOT/TMN/LIMIT execution.

No active packaged margin/short strategy was found. The legacy MCP client could call an
arbitrary discovered tool; simulated submission boundaries lacked independent market
permission checks. Historical terminal USDT conversion previously executed from a valuation
rate without terminal FX depth. SHADOW lacked a competition deadline policy. These gaps
were addressed incrementally. Imported FinanceAgent reference code is not an enabled
QuantPilot trading path and was not executed, removed or rewritten.

## Changes and reuse

| Area | Change | Existing behavior reused |
| --- | --- | --- |
| Permanent policy | Immutable SPOT/LONG_ONLY literals in mode configs | DomainModel, Decimal, explicit modes/config hashes |
| Wallet boundary | Shared spot/whitelist/fee/free-balance/precision/minimum checks | Risk sizing, exposure, loss/drawdown, slippage, separate reservations |
| Strategy | HOLD on position with no owned asset | Existing breakout windows, regime, ATR exits and timeframe rules |
| Simulation | Independent market guard; LIMIT budget reserves at least limit price | Next-event execution, shared depth, fees, partial fills and ledger |
| SHADOW | Optional absolute deadline/cutoff, reduce-only liquidation queue, residual report | Public feed, virtual wallet, atomic state rollback/commit, replay |
| BACKTEST settlement | Entry cutoff; terminal FX requires explicit route plus recorded depth | Conservative terminal auction, fee/precision/depth checks, residuals |
| LIVE | Same shared guard and read-only verified-fill settlement projection | Existing authorization, durable send boundary, reconciliation, kill, ambiguity handling |
| AI | Explicit spot prompt v2; spot guard included in artifact source identity | BUY-only after-cost labels, ML inference, closed local tools and veto-only fusion |
| Legacy MCP | Fixed read-only allowlist before connection | Existing read-only market/balance/order lookups; no order API activation |

## Files changed for this amendment

- `src/quantpilot/spot.py` (new): policy and shared guard.
- `src/quantpilot/models.py`, `src/quantpilot/config.py`: spot intent symbol contract/config.
- `src/quantpilot/trading/strategy.py`, `src/quantpilot/trading/risk.py`: ownership and boundary guard.
- `src/quantpilot/backtest/config.py`, `execution.py`, `history.py`, `replay.py`,
  `reports.py`, `cli.py`: guard, cutoff, explicit FX route/depth, settlement report/manifest.
- `src/quantpilot/shadow/domain.py`, `engine.py`, `execution.py`: deadline and virtual settlement.
- `src/quantpilot/live/domain.py`, `execution.py`, `settlement.py` (new): policy/guard/accounting.
- `src/quantpilot/ai/analyst.py`, `learning.py`: prompt version and implementation hash.
- `backend/mcp_client.py`: block arbitrary and mutation tools before network session creation.
- `tests/test_spot.py` (new), `tests/test_backtest.py`: regressions and corrected FX expectations.
- `SPEC.md`, `AGENTS.md`, `docs/architecture.md`, `docs/implementation-plan.md`,
  `docs/wallex-integration.md`, this document: additive policy/compatibility/evidence notes.

Unrelated existing workspace changes were preserved. No credentials or environment values
were printed or changed for this task. No production dependencies were introduced.

## Operational configuration and reporting

For competition SHADOW, set an organizer-approved timezone-aware absolute `deadline` and
`liquidation_seconds` (default 300). Omitting the deadline preserves continuous research
sessions; it does not constitute competition final settlement. Do not infer a calendar from
three trading days. The five-million-Toman default and zero crypto remain intact; tests may
explicitly use smaller capital.

At the cutoff, unfinished BUYs are canceled. Virtual asset sales require later fresh bid
observations to fill. The deadline cancels unresolved virtual orders and leaves crypto
explicitly recorded. Insufficient depth, stale data, minimums and dust never imply a sale.
Virtual FX settlement uses only its explicit enabled USDT/TMN route and fresh executable
bid capacity. Backtest's `fx_market` JSON input is explicit approval of that funding-asset
settlement route; ordinary strategy whitelist entries are separate.

Backtest adds `final_toman_balance_tmn`, `fully_settled_tmn` and `remaining_holdings`.
SHADOW frame `settlement` includes phase, actions, cash, return, remaining holdings and
`fully_settled`. Existing realized/unrealized PnL and fees remain separate top-level fields.
Protected LIVE exposes `settlement_report()` without network mutations; it requires fresh
reconciliation and bid marks, checks cash/inventory against journal fills, handles actual
base/quote fees and reports unresolved orders. `competition_complete` also requires the
deadline to have passed. This report is an adapter API; dashboard LIVE exports are not
automatically upgraded to exchange-certified accounting.

Net return is `(final_equity / initial_capital - 1) * 100`. Unsold holdings contribute a
bid mark before potential future exit costs. They are not cash or realized profit. A full
TMN settlement is only reported with no residual non-TMN holdings or unresolved orders.
LIVE settlement remains bounded ticks requiring a separately authorized caller; no autonomous
scheduler, deadline bypass or liquidation guarantee was added.

## Offline verification

Commands:

```powershell
.venv\Scripts\python.exe -m ruff check src/quantpilot tests
.venv\Scripts\python.exe -m mypy
.venv\Scripts\python.exe -m pytest -q --tb=short
```

Final results on the final stable source revision:

- Pytest: **268 passed, 1 skipped**, 44.86 seconds. The skip is the optional PostgreSQL
  integration test requiring an explicitly opted-in isolated local server.
- Ruff: **all checks passed**.
- mypy: **no issues in 72 source files**.
- `tests/test_spot.py` adds **37** offline parameterized regression cases.

New regression coverage includes sufficient/insufficient BUY, fees consuming available
cash, owned/unowned/oversized SELL, negative balance rejection, immutable prohibition flags,
margin/leverage/short/derivative intent rejection, disabled/unknown market scope, adapter
whitelists, reserved asset/cash double-spend prevention, stale phantom-position HOLD,
queued-and-confirmed SHADOW liquidation with deterministic replay, deadline residuals,
verified terminal FX route/depth, quote/base-fee accounting, read-only protected settlement,
unknown account type, and eight unsafe MCP tool names blocked before connection.

Existing tests additionally cover canonical Risk Engine rejection, daily loss/drawdown,
liquidity/precision, partial fills/reservations, SHADOW isolation/restarts/failures, AI output
validation/tool restrictions, LIVE permission evidence/ambiguity/timeouts/recovery/kill,
and deadline liquidation failures. New fixtures use synthetic or mock data and fake keys.
No private exchange request, actual LLM call, live activation or real order was performed.
Public documentary browsing was the only exchange-related external verification in this task.
Frontend/container behavior was not retested because no UI or container code changed.

## Model and dataset compatibility

Inspected the label policy of the three local datasets: `artifacts/ai-demo/dataset.json`,
`artifacts/ai-phase5/dataset.json`, `artifacts/ai-phase5-final/dataset.json`. They describe
flat-account executable BUY round trips after costs. The label code starts with BUY and
exits by selling acquired inventory. No short/leverage label dependency was identified.
This is compatibility evidence, not proof of predictive quality or deployable profitability.

Five local artifact manifests were found in `ai-demo/models`, `ai-entrypoint/models`,
`ai-phase5/models`, and two in `ai-phase5-final/models`. All five have source identities
that differ from this revision. They remain blocked by existing frozen-model validation;
none was silently updated, promoted or retrained. Reviewed revalidation and a compatible
versioned artifact are prerequisites for inference with this source. Existing source-pinned
SHADOW/LIVE journals likewise require original-source replay or reviewed migration to a
new session. New analyst responses use `analyst-v2-spot`; old cache identities are not reused.
External/reference model assumptions remain unverified and are not used automatically.

## Unsupported capabilities and remaining verification

- Margin, leverage, borrowing, shorts, futures/derivatives, withdrawals and OTC execution
  are forbidden. Archived/reference implementations do not grant execution capability.
- LIVE remains disabled by default; protected scope is direct-TMN MAIN_SPOT LIMIT only.
  Live MARKET, conditional order semantics, credit/prop routing and USDT routing are not
  enabled. The competition's credit-account compatibility remains unresolved.
- Official documentation identifies concatenated spot symbols, TMN as Toman, and step/tick
  decimal counts. Current actual market status/precision/limits/fees must still be checked;
  examples are not fixed deployment parameters. See the linked official sources in
  `wallex-integration.md`.
- Account identity, key permissions, locked-balance semantics and current private response
  shapes were not remotely verified. Existing independently reviewed authorization evidence
  is still required; it is not invented exchange permission introspection.
- IRR remains a distinct unit, rejected as an execution quote. No implicit factor-of-ten
  conversion was introduced; a future IRR source needs an explicit verified unit adapter.
- Historical initial USDT funding retains its explicit research rate/fee assumption. Its
  terminal exit now requires executable evidence; reports flag unsold USDT. This is not
  equivalent to a verified live FX execution model.
- Static historical metadata and conservative OHLC auction assumptions do not establish
  real fill probability. Liquidation can fail; final cash and residual inventory must be
  inspected before claiming all competition profit was realized in Toman.

No unrelated development phase was started and LIVE was not activated.
