# Revised implementation plan — eight development phases

Authority: ../SPEC.md. The plan below retains Phase 0's original phase numbering.

## Current implementation status — user-requested Phase 8

The read-only React/TypeScript + FastAPI dashboard, explicit artifact catalog,
provisional judge report exports, offline core rehearsal and Docker Compose
configuration are implemented. Native UI/API, offline replay and automated checks
are documented in [Phase 8 verification](PHASE8_VERIFICATION.md). Docker runtime
verification remains unavailable; production authentication, certified LIVE
financial reporting and unresolved account routing are not claimed implemented.
The existing Trading Core and guarded LIVE defaults are preserved. Stop at Phase 8.
The Phase 7/6 statuses below are historical and superseded by this status.

## Current implementation status — user-requested Phase 7

- Completed in the supported envelope: protected MAIN_SPOT/TMN LIMIT adapter,
  canonical risk gate, durable lifecycle, cumulative partial fills, conservative
  ambiguity/recovery, account reconciliation, kill/loss suspension, bounded
  liquidation ticks and offline failure tests.
- Retained unchanged: Phase 1 contracts, Phase 2 public data, Phase 3 strategy/risk,
  Phase 4 simulator, Phase 5 AI and Phase 6 SHADOW isolation/replay.
- Deployment prerequisites remain: verified funded account/routing and key
  permissions, current private response shapes, balance semantics, prospective
  strategy/model evidence and explicit separate live authorization. Credit accounts,
  USDT settlement and MARKET orders are blocked.
- See [Phase 7](phase7.md), [verification](PHASE7_VERIFICATION.md) and the
  [separate activation checklist](LIVE_ACTIVATION_CHECKLIST.md).
- Stop after Phase 7. No Phase 8 or live activation was performed.

The Phase 6 paragraph below is historical and superseded by this status.

User-authorized Phase 6 now implements persistent public-feed SHADOW operation
and deterministic same-core replay; see phase6.md and PHASE6_VERIFICATION.md.
Short public-feed/health/stop/replay checks passed. Stop after Phase 6. A longer
prospective shadow trial, reviewed model/provider/data assumptions, and explicit
authorization remain prerequisites before any future deployment work. No LIVE
orders or authenticated-account integration have been enabled.

Historical Phase 5 status (superseded by Phase 6 above):
User-authorized Phase 5 now adds optional offline hybrid-AI evaluation, frozen
LightGBM artifacts, replay-only historical LLM analysis and A/B/C reports. See
phase5.md and AI_EVALUATION_REPORT.md for verified behavior and evidence limits.
No real-world AI efficacy or deployment promotion is established. Stop after
Phase 5 until the next phase is explicitly requested. Before deployment research,
obtain adequate time-valid market data and prospectively recorded LLM evidence;
freeze promotion criteria and validate prospective SHADOW behavior separately.

Historical Phase 4 status (superseded by Phase 5 above):
User-authorized implementation phases 1–4 now provide the packaged core,
market-data adapters, deterministic strategy/risk, and offline historical replay/
Decimal ledger. See phase1.md through phase4.md for actual scope and evidence.
Phase 4 is complete subject to its documented simulation assumptions; LIVE is
disabled. Stop until the user explicitly requests the next implementation phase.
Next prerequisite: review Phase 4 data/execution assumptions before designing
continuous SHADOW scheduling, durable virtual-account recovery and reconciliation.

## Phase 1 — Shared domain and data contracts

Prerequisite: accept SPEC open questions as tracked blockers; no exchange writes. Reuse existing MCP client, exact tool map and denylist. Already present: canonical pair conversion, role names, Unix candle request translation, columnar parsing, baseline and synthetic graph path.

Tasks: additive typed domain models for money/quantity/currencies, closed Candle/MarketSnapshot, MarketSpec and account identity; explicit adapter normalization with event time, dedup, ordering and freshness; redacted fixture contract tests; inject clock into core. Plan neutral denylist migration preserving all 344 values and endpoint compatibility. Distinguish market eligibility from denylist membership. Do not train AI, build execution or change strategy logic here.

Acceptance: fixtures normalize markets/trades/candles without network; stale/malformed/duplicate inputs handled by documented policy; no float/quote-unit ambiguity in new domain contracts; no margin/write tool selection; baseline output compatibility documented; tests cannot open .env or production DB. Real account fixtures require explicit permission and redaction.

**Exact next task:** implement and test a normalized closed-candle contract for the currently working wallex_basic_candle_history adapter, retaining event timestamps and using an injected as-of clock. Cover columnar arrays, unequal lengths, duplicate/reversed times, invalid OHLC, current incomplete candle and gaps using synthetic fixtures; keep existing API response compatibility through an adapter. This is Phase 1 work and has not started.

## Phase 2 — Deterministic strategy, regime and risk core

Prerequisite: Phase 1 contracts accepted. Retain existing EMA12/26 baseline as versioned benchmark; do not rewrite it silently. Add Momentum Breakout configuration and indicator initialization, regime classification, strategy reason codes, position-aware exits, equity/unit-aware sizing and mandatory risk decisions. Defaults remain research-only until evaluated.

Acceptance: deterministic input/output with injected time; clear stop/target precedence; no future access, oversell or borrowed exposure; tests exercise stale conversion, fees/reservations, limits and insufficient inventory. Risk settings must demonstrably enforce behavior, not merely appear in config.

## Phase 3 — Portfolio ledger, simulator and historical backtest

Prerequisite: tested core and adequate historical data. Build exact multi-currency ledger, fee/conversion accounting and execution simulator. Same strategy/risk functions consume frozen history; use next-bar execution, conservative intrabar precedence, costs and final liquidation. Add baseline comparison and replay bundles.

Acceptance: balance conservation including fees, realized/unrealized separation, reproducible reports, time-series split and future-perturbation tests; no mock equity presented as actual performance. Historical gaps and insufficient-liquidity assumptions disclosed. Existing SQLite audit retained with additive migrations; it is not reused as a guessed ledger.

## Phase 4 — Continuous SHADOW and recovery

Prerequisite: simulator and replay passing; read-only source stable. Already present: request-driven signal analysis, audit log, checkpoint file and idempotent per-run event recording. Reuse these; add backend event scheduler, stable closed-candle decision keys, bounded polling/retries, portfolio simulation and snapshot capture. Implement explicit restart/restore/reconciliation state without browser dependence.

Acceptance: zero exchange mutations under any shadow path; duplicate feed events/restarts do not duplicate virtual trades; offline replay matches recorded observations; stale feeds halt new entries; error and restart drills pass. Agree trial duration and measurable promotion gates before beginning observation.

## Phase 5 — AI evaluation, LLM Analyst and fusion

Prerequisite: chronological dataset, baseline evaluation and supplied LLM config. Existing application has no model integration; imported FinanceAgent is reference only. Add LightGBM only after validating package/compute need, past-only training and label horizon; add bounded schema-validated LLM review in existing LangGraph harness and versioned fusion. Model failure/abstention must be explicit.

Acceptance: untouched holdout and ablation show measurable benefit after costs, model outputs calibrated if called probabilities, artifacts/prompts/config recorded, tool budgets and timeout behavior tested. Stored model output supports replay; LLM cannot bypass risk or access financial mutation tools. If benefit is absent, retain baseline and report AI's limited role honestly.

## Phase 6 — Verified exchange adapters and gated LIVE

Prerequisite: phases 1–5 applicable gates, explicit authorization, correct funded account identity and official order contract. Already present: Streamable HTTP MCP public reads; order endpoint fails closed. Preserve it until replacement passes acceptance. Verify REST/WebSocket contracts first, then implement only justified transports and sequencing/reconnect behavior. Add read-only account/fees/depth/order reconciliation before submission. Implement client-ID lifecycle, unknown-outcome recovery and budget confirmation.

Acceptance: synthetic adapter tests cover rejection/partial fills/timeouts/restarts/cancel races and no blind resubmit; authenticated account routing independently verified; shadow/live safety boundaries cannot be bypassed by env flags, UI or LLM. Real-order validation needs separate explicit user authorization and a concrete bounded action. No assumed testnet or exchange idempotency semantics.

## Phase 7 — Competition operations and final liquidation

Prerequisite: confirmed official timing and liquidation rules; tested execution/accounting/recovery. Add deadline-aware state machine: stop entries, resolve open orders, unwind approved assets to Toman, reconcile fills/fees and report residual dust/unfilled exits. Add kill switch, operator runbook, backup/restore and reconciliation monitoring.

Acceptance: simulated deadline/outage/no-liquidity/partial-fill drills terminate safely and report unresolved assets; no forced minimum-violating or unauthorized orders; final realized Toman report and marked equity both reconcile. Exact finish buffer chosen from venue limits and liquidity evidence.

## Phase 8 — Truthful dashboard, reports and delivery rehearsal

Prerequisite: real source-of-truth APIs; UI shell can be retained now without rewriting. Already present: Persian responsive layout, API proxy and partial polling. Replace static chart/market/AI/operating claims, wire acknowledged backend controls and mode states, display hypothetical results clearly. Add report export, reproducible run manifest and competition demo workflow.

Acceptance: frontend build and browser checks pass; displayed values reconcile to ledger; stopping controls actually halt runner; no API keys reach browser; authentication/redaction verified for deployment. Source/config/model versions match competition execution; produce required demo and documentation. No profitability claim without recorded out-of-sample evidence.

## Migration safeguards

Keep working read paths and existing APIs behind compatibility adapters. Preserve source and existing databases; apply versioned additive migrations only after backup. Do not import or execute FinanceAgent reference on application startup. Do not equate implemented settings, UI controls, checkpoint writes or supplied public responses with verified private/live capabilities.

## Completed amendment ? permanent spot-only boundaries (2026-10-23)

- Reused the existing shared core, Momentum Breakout/regime engine, fee-aware risk sizing,
  ledger, execution lifecycles, AI veto pipeline, replay and protected LIVE gates.
- Added immutable spot policy and shared independent boundary validation; blocked legacy
  arbitrary MCP calls; retained unsupported/private routes as closed.
- Added deadline-driven virtual settlement, terminal FX route/depth evidence, explicit cash
  and residual reporting, and a read-only verified-fill LIVE accounting projection.
- Updated offline regression coverage; see [verification](SPOT_ONLY_VERIFICATION.md).
- No new dependencies, strategy replacement, real orders, private probes, LIVE activation,
  model promotion or unrelated development phase.

Prerequisites for a competition rehearsal: reviewed approved spot markets/fees/precision,
absolute three-trading-day deadline, current source-compatible artifact/cache/journal,
explicit SHADOW deadline, fresh public books, and successful residual-aware replay.
Acceptance requires no overspend/oversell including fees and reservations, no short/margin
capability, matched virtual replay, separate realized/cash/residual totals, and fail-closed
unknown account/market/permission/status behavior. LIVE prerequisites remain the separate
activation checklist; credit-account compatibility remains unresolved, not inferred.
