# Phase 0 repository audit

Audit date: 2026-10-22. Scope: current local source, manifests, existing design notes, imported FinanceAgent reference and prior user-supplied runtime responses. No exchange requests, orders, credential-value inspection, production-database reads, dependency installation or implementation changes in this phase.

## Status definitions and evidence

- Working and verified: a specific local check or explicitly identified supplied runtime evidence supports the stated behavior, not blanket production readiness.
- Implemented but unverified: source exists, relevant execution not checked.
- Partial: subset implemented; essential behavior absent.
- Missing: no implementation found.
- Needs refactoring: existing implementation conflicts with target contracts or needs structural correction.

Evidence sources: L = local inspection; T = this audit's isolated check; U = user-supplied earlier runtime output. SPEC.md is authoritative for future behavior; older docs may describe a previous state.

## Repository and stack

Root: FastAPI entrypoint main.py; backend Python package; React/Vite src and index.html; requirements.txt; package.json; vite.config.js; ignored .env/.venv/data; docs; imported FinanceAgent-master/FinanceAgent-master plus archive. Git metadata exists but git status failed the ownership safety check in this environment. No safe.directory or Git configuration changes were made; tracked-file/secret-history status cannot be established here.

Declared: FastAPI, Uvicorn, MCP, Pydantic Settings, HTTPX, LangGraph and SQLite checkpointer; React 18, Vite 6, Recharts and Lucide. Python dependency ranges are not a reproducible lock. No node_modules or package lock was found during inspection. Existing venv versions: FastAPI 0.158.0, MCP 1.30.0, LangGraph 1.2.16, langgraph-checkpoint-sqlite 3.1.2. Presence is not security review or full compatibility verification.

## Component inventory

| Component / files | Status | Evidence and limitations |
|---|---|---|
| FastAPI routes, backend/main.py | Partial | L: route definitions and errors; synthetic graph check imports core modules; no full server acceptance test in this phase |
| MCP client, backend/mcp_client.py | Working and verified (narrow U path) | U: tools/list, recent BTC trades, candle-driven HOLD; L: Streamable HTTP initialized session. Current connectivity not retested |
| MCP private auth | Implemented but unverified | L: X-API-Key from SecretStr; tools/list/public calls do not prove private balance authorization |
| MCP stdio | Implemented but unverified | L: configurable process/args/env; not executed |
| Tool role mapping, market_data.py | Partial | Explicit read-only Wallex names; required/unknown key checks; no property-type validation, pagination or full response contracts |
| Direct REST / WebSocket | Missing | No application adapters/subscriptions found |
| Market data | Partial | U: BTC recent trades/candles; L: time ranges and nested market normalization; no durable dataset, freshness/gap/dedup policy or full universe verification |
| Market exclusions, market_rules.py/src/marketRules.js | Working and verified (static list only) | T: 344 loaded; OPUSDT rejected. Needs refactoring: backend regex-parses frontend JS; not live account eligibility |
| EMA/RSI/volume baseline, strategy.py | Working and verified (narrow calculations) | U: HOLD result; T: same synthetic inputs give same outputs excluding timestamp; no profitability or boundary coverage |
| Baseline SELL/sizing | Needs refactoring | held_base defaults to zero and caller never supplies it; sizing uses max_order_quote, not equity; quote currency/fees ignored |
| Momentum Breakout / regime | Missing | Design proposal exists, no application implementation |
| LLM / LightGBM / fusion | Missing in application | Reference demo has ChatOpenAI but is separate; no actual model node/artifacts in main backend |
| LangGraph harness, agent.py | Partial | T: synthetic end-to-end graph and checkpoint file creation passed; fixed nodes/StructuredTools; no LLM loop, scheduling or resume API |
| Risk management | Partial | Pair denylist, spot/leverage schema restrictions; max_daily_loss unused. execution_gate only returns analysis_only, not risk validation |
| BACKTEST | Missing | UI toast and design only |
| SHADOW | Partial | Request-driven real data analysis/logging; no autonomous observation or simulated fills/account |
| LIVE execution | Missing (fail-closed route present) | L: shadow returns rejected; live flags return 501; no MCP submit call. Preserve this guard |
| Order audit | Partial | Shadow rejections recorded; invalid-pair and live 501 paths not all audited; no order lifecycle/idempotency/reconciliation |
| Toman accounting / positions | Missing | No ledger, reservations, realized costs, conversion or portfolio accounting |
| Audit memory, memory.py | Working and verified (local persistence subset) | T: SQLite append_once uniqueness survives new instance; earlier tests covered notes. No input manifest/replay/tamper evidence |
| Checkpoint persistence | Partial | T: file created on graph run; cross-process checkpoint restore, restart recovery and retention unverified |
| Final liquidation | Missing | Design intent only |
| Dashboard | Partial / Needs refactoring | API polling exists; static equity/chart/market status/time and AI labels; local start/stop/mode controls do not control backend; no build/browser verification |
| Reports | Missing | No actual backtest report export; report control is a toast |
| Automated test suite / CI | Missing | No first-party checked-in tests or CI configuration found; ad hoc audit checks are not a maintained suite |
| Imported FinanceAgent | Needs refactoring; reference only | Static read/AST only, not executed or imported; not an application integration |

## Strategy detail

Baseline: EMA12 > EMA26, RSI14 42–68 and five-candle average volume / preceding twenty-candle average >= 0.8 for buy when no holdings. Sell requires held_base>0 and bearish EMA or RSI>=75, but current caller never supplies holdings. Stop uses max(1.5%, 2*return-volatility), target max(2.5%, 3*volatility). No position tracks those levels and they are produced even for HOLD. RSI is simple-period gains/losses, not specified Wilder smoothing. EMA uses only last 50 closes. Missing volume defaults to zero and zero baseline ratio to 1. Input validation allows negative/malformed OHLC relationships, duplicates and unordered row arrays. Columnar response sorting exists but timestamps are dropped before analysis. confidence is handcrafted, not probability; wall-clock timestamp prevents literal output identity.

## Storage design

AgentMemory uses SQLite WAL with per-call connections and timeout=10. Tables: events(id, created_at, kind, symbol, JSON payload); notes(key PK, value, updated_at); recorded_runs(run_id PK, event_id). append_once uses BEGIN IMMEDIATE to deduplicate audit writes by run ID. Graph generates a new UUID every observation, so repeated polling is a different run; this does not deduplicate market decisions or orders. No foreign key constraint/index/migration version/archiving policy beyond primary keys. State checkpoints are in a separate SQLite database and can include input candles; audit events alone lack complete replay inputs/config/clock. Neither store is a financial ledger or immutable evidence system. Production DB contents were not inspected.

## Security and technical debt

| Priority | Finding | Required future action |
|---|---|---|
| High | Imported reference has a hardcoded external-service credential | Do not reproduce it; owner should rotate if active, remove from future tracked distributions; cannot verify Git history here |
| High before exposure | API has no authentication; notes mutation and account/memory reads exposed; broad allowed headers | Bind local for development; design authorization before remote deployment/live mutation |
| High before LIVE | No account/subaccount identity, reservation ledger, actual risk enforcement, idempotent submission or reconciliation | Block live promotion until validated; retain 501 behavior |
| High correctness | Static UI performance and operating-state claims mixed with API data | Replace/label mocks; backend-owned controls and truthful health |
| Medium | Raw exception strings forwarded into API/hold reasons | Redact secrets/headers/URLs and categorize nested MCP failures |
| Medium | Bearer config is plain str; arbitrary stdio command/env and configurable URL | Secret masking and operator trust boundary; constrain credential destinations |
| Medium | float money, unspecified units and max-order-based risk sizing | Introduce exact unit-aware domain values and equity-based sizing |
| Medium | GET signal polling writes audit/checkpoints every 30 sec, overlapping requests possible, stop button has no effect | Backend runner, stable event keys, bounded concurrency and read-only dashboard queries |
| Medium | Unlocked dependencies and incomplete imported manifest | Establish tested locks; no dependency changes in Phase 0 |
| Medium | Denylist parsed from JavaScript; old MCP_TOOLS settings ignored; error messages still suggest them | Neutral resource migration with parity tests; coherent config/docs |
| Medium | Unbounded audit/checkpoint growth and no tested restore | Retention/backup policy and restore drills |
| Medium | No scheduler, pagination/cursors, rate-limit budgets, structured tool errors | Explicit adapter lifecycle and recovery design |

Imported FinanceAgent also has hardcoded holdings/prices, mismatched asset names versus ticker filtering, printed rather than stored LLM result, no checkpointer, detached indicators, duplicated unreachable volume code, missing imported packages in its requirements and center=True/shift(-1) pivot calculations. These require delayed confirmation in historical evaluation; naive full-frame use can leak future information. Its temperature default is 0.7. Syntax validity does not establish runtime viability.

## Checks performed in Phase 0

One isolated Python script, using `.venv/Scripts/python.exe`, parsed 11 first-party Python files with ast.parse; reported installed package versions without reading credentials; constructed Settings with _env_file=None and blank keys; compared repeated synthetic baseline outputs excluding wall clock; checked 344 exclusions and OPUSDT rejection; used TemporaryDirectory for audit/checkpoint files; checked append_once duplicate run returns same event; ran TradingAgent on fake candle service; verified HOLD and checkpoint file existence. All these assertions passed. No exchange tool was called and no production database was opened.

`git status --short` was blocked by dubious ownership; Git safety was not overridden. `rg --files` test search found no first-party test suite. node_modules absent, so frontend build/browser validation was not run. No backtest, shadow accounting, real order, full restart recovery or model behavior was verified. Prior supplied live responses remain U evidence, not results of this audit.

## Recommendation and next action

Option B: gradual refactor; see architecture.md. Exact next implementation task is Phase 1 domain/data contracts with offline fixtures, not live submission, AI training or wholesale rewrite. Phase 0 stops at these documents.
