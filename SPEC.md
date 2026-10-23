# Wallex QuantPilot — authoritative specification

Phase 8 update: `src/dashboard` adds the React/TypeScript judge dashboard;
`quantpilot.dashboard` supplies read-only FastAPI projections and provisional
competition reports from catalog-approved local artifacts and SHADOW checkpoints.
DEMO is illustrative, BACKTEST simulated, SHADOW virtual, and LIVE exports are
operator-recorded rather than exchange-authenticated. Missing evidence is never
substituted with simulated performance. Docker Compose describes UI/API startup;
runtime Docker verification is unavailable on this host. Prior core/execution/AI
modules and LIVE activation restrictions remain unchanged. See `docs/phase8.md`,
`docs/PHASE8_VERIFICATION.md` and the judge-facing README. Stop after Phase 8.

Phase 7 update: `src/quantpilot/live` adds a separately authorized protected spot
execution adapter, durable order/fill recovery, account reconciliation, kill/loss
suspension and bounded final-liquidation ticks. LIVE remains disabled by default;
no real credentials or private exchange calls/orders were used for implementation.
Evidence is offline mocks, not exchange certification. Supported scope is dedicated
MAIN_SPOT, direct TMN settlement and capped LIMIT orders only. Credit/prop routing,
account permission introspection, USDT settlement and MARKET execution remain
blocked pending verified contracts. See `docs/phase7.md`, `docs/PHASE7_VERIFICATION.md`
and the separate `docs/LIVE_ACTIVATION_CHECKLIST.md`. Existing SHADOW/AI/web paths
retain their execution restrictions. Stop after Phase 7.

Phase 6 update: `src/quantpilot/shadow` adds public-data-only virtual trading,
durable market/decision journaling, restart recovery, read-only health, activity
exports and deterministic same-core replay. See `docs/phase6.md` and
`docs/PHASE6_VERIFICATION.md` for commands, checked behavior and limitations.
Short live public-feed checks passed; no exchange mutation/private credentials
or actual analyst-provider calls were used. This is SHADOW, not LIVE promotion.

Phase 5 update: optional hybrid AI research evaluation is implemented in
`src/quantpilot/ai`; see `docs/phase5.md` and `docs/AI_EVALUATION_REPORT.md`.
Purged LightGBM training, frozen inference, a bounded read-only LLM harness,
recorded-response historical replay and veto-only fusion reuse the Trading Core.
The delivered evidence is synthetic software verification, not validated real
market performance or real LLM efficacy. No AI deployment/LIVE gate is enabled.

Phase 4 update: offline event-driven replay and Decimal Toman portfolio
accounting are implemented in `src/quantpilot/backtest`, reusing unchanged
Phase 3 strategy/risk/lifecycle modules. See `docs/phase4.md` for CLI, contracts,
execution assumptions, reports and limitations. Synthetic checks establish
software/accounting behavior, not historical profitability. LIVE remains disabled.
The user's implementation phase numbering supersedes the initial audit plan.

Implementation status update: the user-authorized Phase 2 market-data scope is
documented in docs/phase2.md, including newly verified official public MCP/REST/
WebSocket contracts and explicit limitations. This supersedes the earlier phase
numbering for implementation work; it does not enable LIVE execution or validate
unverified trading/account contracts below.

Phase 0 baseline, 2026-10-22. This document governs future implementation. It does not assert that target capabilities already exist. Existing design notes are historical proposals where they conflict with this specification.

Evidence labels: **V** = verified by local inspection/checks; **U** = user-supplied competition information or runtime response, not independently verified against the exchange; **D** = product/engineering decision; **O** = unresolved assumption requiring evidence. Component status and check details are in `docs/current-state-audit.md`.

## 1. Mission and scope

**D:** Build an AI-assisted, explainable, spot-only cryptocurrency trading system for a three-day competition. Optimize evaluated net Toman performance subject to risk and operational constraints. Profit is an objective, never a guarantee. One shared core must support historical evaluation, continuous shadow observation, and explicitly enabled real execution. Preserve the current working data path while adding missing capabilities incrementally.

Out of scope: leverage, short selling, margin, withdrawals, unrelated bank/account mutation, guaranteed returns, and using generated narratives as execution authority. Phase 0 is documentation and verification only.

## 2. Competition rules and scoring

**U:** User-supplied challenge text specifies 5,000,000 Toman initial capital, one dedicated account, three trading days, algorithmic execution only, approved markets, no self-trading/coordinated/wash trading, source matching the traded version, decision logs, Markdown documentation, and an approximately five-minute mandatory demo video. UI is not a primary criterion. Funds are challenge funds; withdrawal is disabled according to the supplied brief. The user further specifies spot without leverage and 344 excluded credit-account pairs.

**U:** Proposed scoring totals 300: net return 90, drawdown control 30, regular reasonable activity 15, operational stability 15; strategy logic 40, meaningful AI use 35, risk/capital management 30, reproducibility 25, backtest/shadow evidence 20. Treat this as supplied proposed scoring, not independently confirmed final rules. Avoid trading merely to inflate activity.

**O:** Brief mentions both final marked equity/unrealized P&L and a stricter requirement to realize results in Toman. **D:** Plan end-of-competition liquidation to Toman and report both marked equity and realized performance. Confirm final scoring and exact liquidation deadline with organizers. A supplied numerical example says 6.5m from 5m is 25%; arithmetic is 30%. Use the formula `(final - initial) / initial * 100`, not the inconsistent example. Dates, eligible account routing, current excluded markets and final rules remain open.

## 3. Functional requirements

- FR1: Acquire public data and selected competition-account data through explicit, schema-validated adapters; record source and timestamps.
- FR2: Maintain a point-in-time universe intersecting exchange availability, account permissions, competition restrictions and liquidity criteria.
- FR3: Validate and persist closed candles; reject missing, duplicate, stale, malformed or out-of-order inputs according to documented policy.
- FR4: Generate versioned BUY/SELL/HOLD decisions with reasons, entry/exit conditions, feature evidence and proposed size.
- FR5: Maintain positions, open orders, reserved balances and fills; never infer a fill from order acceptance.
- FR6: Evaluate strategy, regime, optional LightGBM and optional LLM contributions; pass every candidate through deterministic risk controls.
- FR7: Execute the same core logic in BACKTEST, SHADOW and LIVE; only adapters and clocks differ.
- FR8: Save replayable decision bundles, accounting events, reports and operational failures.
- FR9: Reconcile after startup, timeout or disconnect before new live orders; provide kill switch and scheduled final liquidation.
- FR10: Dashboard must distinguish real observations, simulations and unavailable values; controls must reflect acknowledged backend state.

## 4. Non-functional requirements

**D:** Use Python for the core, FastAPI for API and LangGraph for bounded workflow orchestration. Keep financial calculations independent of LLM and web framework. Use UTC internally and Asia/Tehran for display. Represent money/quantity with Decimal or documented scaled integers, never binary float in the financial ledger. Same snapshots, configuration, model artifacts, clock and portfolio state must produce identical core decisions and accounting results.

**D:** Fail closed on unknown account state, stale inputs, risk failure or unrecorded order intent. Bound requests, retries, concurrency, model/tool calls and storage retention. Measure latency and success rates; exact service-level thresholds must be established from observed Wallex limits before LIVE approval. Single local process/SQLite is the initial deployment target; multi-worker trading requires tested locking/coordination. No new infrastructure is justified solely by the target diagram.

## 5. Target architecture

**D:** Shared Trading Core contains domain objects, point-in-time features, strategy, regime rules, fusion, sizing/risk, portfolio accounting and execution state transitions. MCP/REST/WebSocket are adapters, not competing sources of business logic. LangGraph coordinates calls, persistence and bounded AI analysis. The core cannot call exchange mutation tools directly. See `docs/architecture.md`.

## 6. Core domain models (target, not current schemas)

| Model | Required semantics |
|---|---|
| MarketSpec | canonical pair, wire symbol, base/quote, permission evidence, min/step/precision limits, status and observation time |
| Candle / MarketSnapshot | event/open/close and received times, interval, OHLCV, source, completeness, bid/ask/depth where available |
| AccountSnapshot | explicit account/subaccount ID, free/reserved asset balances, orders, reconciliation time |
| FeatureSnapshot | schema/version, as-of time, lookback IDs, missingness and feature values |
| StrategySignal | version, action, reason codes, validity interval, entry/stop/target reference and rule evidence |
| AIReview | model/prompt/artifact version, validated bounded assessment, input hash, latency, fallback reason |
| RiskDecision | allow/reject, exact reason codes, size/currency, exposure and loss-limit evidence |
| OrderIntent / ExecutionReport | unique decision/client IDs, account, side/type, base quantity or explicit quote budget, lifecycle, cumulative fills, fee currency |
| Position / Portfolio | quantity, cost basis, reservations, realized/unrealized P&L, quote currencies and Toman valuation provenance |
| DecisionBundle / RunManifest | input hashes/snapshots, clock, versions, config, AI output, risk outcome, execution links and replay identity |

Current `Signal.confidence` is a hand-crafted score, not a calibrated probability. Current `OrderIntent.amount` is base quantity; it cannot express a guaranteed 100-USDT market spend. Preserve compatibility until a versioned replacement exists.

## 7. Module interfaces

**D:** Interfaces are proposed contracts, not existing implementation:

- MarketData: `markets(as_of)`, `candles(pair, interval, range)`, `quote(pair)`, `subscribe(events)`; return normalized data plus provenance.
- AccountAdapter: `snapshot(account_id)`, `orders(account_id)`, `fills(cursor)`; account identity is explicit.
- Strategy: `evaluate(features, portfolio, config, clock) -> StrategySignal`.
- Regime: `classify(features, config) -> regime + evidence`.
- ModelEvaluator/LLMAnalyst: `review(candidate, bounded_context) -> AIReview`; no order authority.
- Fusion: `combine(signal, regime, reviews, policy) -> candidate or HOLD`.
- RiskEngine: `check(candidate, market, account, portfolio, limits) -> RiskDecision`.
- Execution: `submit(intent)`, `lookup(client_id)`, `cancel(id)`, `reconcile()`; no automatic submit retry after unknown outcome.
- Audit: transactional `record(bundle)`, `record_execution(report)`, `load_for_replay(id)`.
- Clock: injected event time for historical/simulated execution; wall clock belongs to telemetry only.

## 8. Trading strategy

Phase 3 user-approved research defaults supersede the earlier timeframe proposal:
5-minute entries with 15-minute confirmation, 0.5% initial risk ceiling and at most
two concurrent/pending positions. The separately versioned Momentum Breakout and
risk implementation is documented in docs/phase3.md. These remain unoptimized
research assumptions. The earlier EMA12/26 baseline is preserved for comparison.

**V:** Current baseline is EMA12/26 with simple RSI14 and volume ratio. **D:** Retain it as benchmark; implement separately versioned `momentum_breakout_v1` after data contracts exist. Initial research parameters: 15-minute closed candles, at least 220 warm-up candles; EMA50 > EMA200; close above prior 20-candle high excluding current candle; RSI14 50–70; current volume >= 1.2 times prior 20-candle mean. These are hypotheses, not validated profitable settings.

**D:** ATR14 stop at actual fill minus 2 ATR, target at fill plus 3 ATR; exit on stop, target or closed candle below EMA50. Define Wilder/smoothing initialization and rounding in versioned config. Protect partial fills and gaps. No sell beyond available inventory. Missing data produces HOLD/reject. Stop/target execution semantics depend on verified exchange capabilities; local monitoring cannot guarantee protection during outage. Define precedence explicitly in Phase 2/3 tests.

## 9. AI responsibilities

**D:** Regime detection starts as deterministic trend/volatility/liquidity classification with explicit thresholds. LightGBM is a future optional evaluator trained on past-only features and cost-aware future labels. Fit transforms on training data only; use chronological splits, purge overlapping labels and reserve untouched final evaluation. Calibrate probability claims and compare net results to no-model baseline. Feature schema and artifacts must be pinned.

**D:** LLM Analyst consumes bounded validated snapshots and retrieved audit context, returns schema-validated assessment/reasons or abstains. It may veto/rank research candidates under a versioned fusion policy; it cannot set arbitrary prices/limits, override risk, select another account or authorize money movement. Timeout/malformed output defaults to abstention. For reproducibility persist its actual response and replay it; temperature zero is not a determinism guarantee. News is optional and must have publication/as-of evidence. Fusion requires an ablation report; absent/unvalidated AI must be reported as absent, not described as approval.

## 10. Risk-management policy

**D:** Always enforce spot, no leverage/shorting, approved account and market, available balances including fees/reservations, min notional/precision, fresh quote/candles, spread/depth/slippage limits, maximum allocation and aggregate exposure, daily loss/drawdown stop, cooldown, duplicate-intent prevention, open-order limits and emergency halt. Stops cannot expand to bypass limits.

Research defaults proposed, not approved LIVE limits: risk budget 0.5% of Toman equity per trade, at most 10% allocation per asset, 3% daily loss stop. Define daily boundary in Tehran and persist its opening equity; both realized loss and conservative marked loss must be considered. Reserve USDT/TMN conversion and fee buffers. Current `max_daily_loss` is unused and current sizing based on max order quote is not portfolio-risk sizing. Hard LIVE budgets need explicit account-specific approval after evaluation.

## 11. Execution modes

| Mode | Data and clock | Execution |
|---|---|---|
| BACKTEST | frozen historical inputs/event clock | simulator only, future data inaccessible |
| SHADOW | current feeds/observed event clock | logged intentions; optional simulated ledger clearly marked hypothetical |
| LIVE | current feeds + reconciled account | explicitly enabled adapter, approved configuration and per-action authorization policy |

Current mode string is not these engines: current SHADOW is request-driven analysis and rejection, with no continuous runner or fills. UI selection must never silently activate LIVE.

## 12. Wallex integrations

**U/V:** MCP URL is `https://api.wallex.ir/mcp`; application supports Streamable HTTP with `X-API-Key` for private tools and public calls without key. Public response and signal execution were supplied by the user; this audit makes no network requests. Tool inventory supplied by user identifies spot markets, recent trades, candles, balance and order tools. See `docs/wallex-integration.md` for exact names and limitations.

**O:** REST endpoints, WebSocket channels/authentication, sequencing, reconnect protocol, rate limits, server time, candle completeness, precision/minimums, stop semantics, account routing and market-buy quote budgets must be verified from current official contracts. Do not invent them. Listing tools does not establish private account authorization. Current MCP connection lifecycle reconnects per call and pagination is not handled.

## 13. Backtesting

**D:** Shared strategy/risk/accounting on immutable historical snapshots. Signal on closed t, execution no earlier than t+1 open; include taker/maker costs as justified, spread, slippage, min size and liquidity constraints. If stop and target touch within one candle without finer data, use conservative stop-first convention and disclose it. Include gaps, insufficient funds, forced end liquidation and fee currencies. Unknown depth must use explicit conservative assumptions, not fabricated historical order books.

**D:** Compare baseline, breakout, and buy-and-hold with identical universe/capital/costs. Walk-forward selection is separate from final holdout. Report net return, realized Toman P&L, max drawdown, closed trade count, win rate, fee/slippage totals, exposure, rejected decisions and turnover. No-trade/low-sample results are inconclusive. Require replay identity and future-perturbation tests before trusting performance.

## 14. Shadow testing

**D:** A backend scheduler independent of browser polling observes fresh closed candles exactly once per configured strategy/account/pair/time key. Record decisions and optional hypothetical fills with explicit simulated slippage; never exchange mutations. Run restart, feed outage, stale quote and order-reconciliation drills. Compare shadow logs against offline replay on the exact same snapshots. Required duration and promotion thresholds must be agreed after data availability and competition timing are known.

## 15. Real trading safety

**D:** LIVE requires working ledger/risk/reconciliation, account/subaccount verification, passing evaluation gates, explicit user authorization and enforceable spending limits. Neither environment flags nor free-form prompts alone constitute sufficient validation. Existing order API remains fail-closed until a later authorized phase. Record intent before submit; ambiguous timeout means UNKNOWN and lookup/reconcile, not blind retry. Persist accepted/partial/filled/canceled/rejected/unknown states. A LangGraph retry/checkpoint is not exchange exactly-once execution. Restrict tools to approved spot actions; never expose transfer/withdrawal/bank/margin tools to the harness.

## 16. Financial accounting

**D:** Track base quantities, free/reserved quote, fills, fees in original currency, and cost basis consistently (weighted-average initial choice). Toman is the reporting currency; USDT is not Toman and not assumed identical to USD. Store conversion source/as-of time and fees; reject stale conversion for sizing. Separate realized P&L, marked unrealized P&L, net equity and external capital flows. Reconcile ledger balances with exchange after each execution cycle and restart. No guessed fees or float rounding may be presented as final realized competition return.

## 17. Logging and reproducibility

**D:** Decision bundle records market/account snapshots, input hashes, closed-candle IDs, versions, canonical configuration, model artifacts and response, risk checks and execution references. Retain original timestamps but inject analysis clock. Snapshot inputs and commit/config identity must be sufficient for offline replay. Audit is append-only by policy with migration versions and bounded retention; current SQLite tables are not tamper-proof. Checkpoints are workflow recovery, not the financial ledger. Keep audit/model context free of credentials; memory text is untrusted data, never policy.

## 18. Security

**D:** Local `.env` is ignored; keys stay server-side and masked/redacted everywhere, including nested exceptions and HTTP logs. No withdrawal privileges. Authenticate administrative/mutation endpoints before any exposure beyond local development; protect account data and notes, validate origin/CSRF policy if session authentication is introduced. Gate arbitrary stdio command execution to trusted operator config. Restrict MCP URL/auth destinations. Archive/reference code must not execute on import. Remove embedded secrets from future distributions; rotate any active embedded key. Pin/review dependencies and establish safe backup/restore procedures. See audit for current findings; no security fixes implemented in Phase 0.

## 19. Testing and acceptance criteria

**D:** Offline contract tests for observed redacted MCP fixtures; strategy/risk boundary tests; Decimal accounting and fee-currency tests; deterministic replay/future-data isolation; simulator gaps/stop precedence; duplicate submit/unknown response/restart reconciliation; cross-mode parity; checkpoint reload and audit idempotency; API authorization/redaction and dashboard truthfulness. Network integration tests are opt-in/read-only; real-order tests require explicit authorization and a verified venue/account workflow, never presumed sandbox support.

Acceptance: all domain-critical tests pass on frozen dependencies; reproduced report matches recorded inputs; no margin/write tools in analysis; no browser-dependent runner; no fake performance; deployment runbook includes halt, reconciliation, recovery and liquidation. Exact profitability/sample-size promotion thresholds remain research decisions and must be frozen before final holdout, not selected afterward.

## 20. Known assumptions and unresolved questions

- **O:** Final competition scoring, deadline/timezone, approved universe updates and contradictory valuation text.
- **O:** Which authenticated account/subaccount receives funded competition balances? Current basic balance tool is not proof of correct account routing.
- **O:** Official REST/WebSocket contracts, fee units, order-size meaning, precision and account permissions.
- **O:** Available historical duration/depth, event timestamps, inactive/delisted-market handling and survivorship bias.
- **O:** LLM provider/model credentials and data-sharing permission; no model configuration provided for the main application.
- **O:** LightGBM label horizon, training sample adequacy, hardware, retraining/promotion policy and costs.
- **O:** Protective-order support and recovery during outages; liquidation dust/minimums and exit liquidity.
- **D:** Recommend gradual refactoring (option B); preserve existing code and baseline. No Phase 1 implementation is authorized by this document.

## Permanent spot-only amendment ? 2026-10-23

This amendment supersedes incompatible earlier targets while retaining the shared Trading Core,
Momentum Breakout, regime detector, risk policy and hybrid AI pipeline.

```yaml
trading:
  market_type: SPOT
  strategy_direction: LONG_ONLY
  initial_capital_toman: 5000000
  quote_currency: TMN
  margin_enabled: false
  leverage_enabled: false
  short_selling_enabled: false
  borrowing_enabled: false
  derivatives_enabled: false
  buy_requires_available_balance: true
  sell_requires_owned_asset: true
  final_settlement_currency: TMN
execution:
  allowed_modes: [BACKTEST, SHADOW, LIVE]
  live_enabled: false
```

**Product decisions.** `SpotPolicy` is immutable and embedded in engine, simulation,
SHADOW and LIVE configuration. Its competition capital is fixed; explicit research fixtures
may override simulation capital. Monetary calculations use Decimal. TMN is the canonical
accounting unit; verified USDT spot routes remain optional, with dated TMN valuations.
IRR input never silently becomes TMN. Three trading days require an organizer-provided
absolute deadline/calendar; there is no invented exchange trading-day schedule.

**Implemented controls.** `validate_spot_order` checks explicit eligibility, symbol/quote,
precision, minimums, available balance and fee budget independently at risk and execution
boundaries. Reserved balances cannot fund another order. SELL reduces owned crypto;
missing asset ownership produces HOLD even if a stale position record exists. Risk still
recomputes canonical strategy decisions and controls ATR sizing, portfolio limits, daily
losses, drawdown, liquidity and slippage. Existing BUY-only AI labels represent executable
long round trips after costs. Fusion cannot authorize execution; the analyst has no order
or credential tools. Prompt identity is now `analyst-v2-spot`.

**Execution support.** BACKTEST supports simulated MARKET/LIMIT. SHADOW supports virtual
MARKET only. Protected LIVE remains separately disabled and MAIN_SPOT/direct-TMN/LIMIT
only; unsupported account routes, unknown permission evidence or ambiguous exchange states
fail closed. The legacy MCP caller is read-only with a fixed spot/basic allowlist; discovered
margin metadata is not an enabled capability. No withdrawal functionality is introduced.

**Settlement.** Historical replay derives its deadline from the last event and stops new
entries/cancels unfinished BUYs `simulation.liquidation_seconds` beforehand (default 300).
Its terminal auction is explicitly simulated, liquidity/minimum/precision/fee constrained,
and retains residuals. A terminal USDT sale requires an explicit `fx_market` (USDT/TMN) and
fresh recorded FX bids; a rate alone does not execute a conversion. Historical initial USDT
funding remains a declared research rate/fee assumption, not verified exchange execution.
SHADOW competition runs must set `deadline` and `liquidation_seconds`; without a deadline
it is a continuous research session, not a competition settlement run. At the cutoff it
cancels BUYs, queues reduce-only sales, and requires later fresh books for fills. At the
deadline it cancels remaining virtual orders and preserves unsold holdings. Explicit FX
settlement uses fresh observed depth and retains dust. LIVE retains cancel/reconcile/sell
bounded ticks before the deadline and never overrides kill, permission or ambiguity gates.

Reports distinguish realized PnL, unrealized PnL, fees, remaining crypto, final TMN cash,
marked equity and `(final_equity / initial_capital - 1) * 100`. Fully settled means no
non-TMN holdings and no unresolved orders. Residual equity is a bid mark before possible
future selling costs, not realized cash profit. The new LIVE read-only settlement projection
reconstructs direct-TMN average cost from verified fills including base/quote fees, rejects
unexplained balances, and requires fresh reconciliation/marks. It is mock-tested, not
exchange-certified, and is not automatically promoted into dashboard LIVE exports.

**Verified documentation versus deployment assumptions.** Official public documentation
identifies TMN as Toman, concatenated symbols such as BTCTMN/BTCUSDT, and decimal-count
step/tick fields. Actual market approval, current limits and fee/balance semantics still
require current evidence. No private requests or orders were made for this amendment.
See [spot enforcement report](docs/SPOT_ONLY_VERIFICATION.md) and
[Wallex integration](docs/wallex-integration.md).

**Compatibility.** Source/config identifiers change. Old frozen LightGBM artifacts and
SHADOW/LIVE journals must remain associated with their original source; no automatic
migration, artifact promotion or retraining was performed. Existing project-generated labels
are long-only, so no short/leverage label retraining was identified; imported external
artifacts remain unverified. Operational reuse on this revision requires reviewed revalidation
and compatible manifests/new journals, not bypassing version checks.

## Operator-confirmed credit competition intent ? 2026-10-23

The operator selected the competition credit account, a 5,000,000 TMN total ceiling,
500,000 TMN per-order ceiling, BTC/TMN only, and end of 2026-10-26 in Asia/Tehran
(`2026-10-26T23:59:59+03:30`). This authorizes preparation within those limits;
it does not supply missing exchange routing evidence. The private read-only MCP account
list reported success, but account identity, balance ownership, trading permissions and
credit order selection remain unverified. MAIN_SPOT is not relabeled or used as fallback.
LIVE remains disabled pending the official credit spot routing contract. See
[credit connection status](docs/CREDIT_ACCOUNT_STATUS.md).
