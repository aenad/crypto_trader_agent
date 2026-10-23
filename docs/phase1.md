# Phase 1 — shared core skeleton

The new Python distribution is `wallex-quantpilot`; its import package is `src/quantpilot`.
The React source remains in src and is excluded from Python package discovery.
Existing backend/, LangGraph workflow, SQLite data and API contracts are preserved.
The new core is not yet wired into legacy FastAPI or Wallex adapters. Legacy float-based
schemas and baseline strategy are not promoted as the new domain contracts.

## Setup and offline demo

From repository root, using an existing or newly created virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\quantpilot-demo.exe
```

Portable alternative after installation: `python -m quantpilot.demo`.
Without package installation in an environment with Pydantic 2 available:

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python.exe -m quantpilot.demo
```

The demo uses one synthetic closed candle, a fixed UTC clock and 5,000,000 TMN of
mock account balance. Its placeholder always emits HOLD, AI always abstains and
risk always denies. Output is a decision JSON plus allowlisted structured logging.
This is neither a profitable strategy nor a simulated exchange/accounting engine.
In-memory decision storage deduplicates by deterministic decision ID. The simple
EventBus collects publications, with no durable delivery/exactly-once guarantee.

## Configuration

`QUANTPILOT_MODE=BACKTEST|SHADOW|LIVE`, default SHADOW.
`QUANTPILOT_LIVE_EXECUTION_ENABLED=false` is mandatory in Phase 1: true is rejected.
LIVE is a recognized configuration mode, but TradingEngine rejects it before any
provider access. Neither BACKTEST nor SHADOW invokes ExecutionProvider. These modes
are contract wiring only: full historical evaluation/shadow accounting are future work.

Core configuration reads only these names from process environment; it deliberately
does not load .env or secrets. .env.example documents them for local export/deployment.
Legacy TRADING_MODE/LIVE_TRADING_ENABLED configure only the existing backend, not the
new core. Never turn legacy flags on to try to enable this demo.

SHA-256 identifiers derive from sorted canonical JSON: config ID includes mode,
schema version and placeholder version; decision ID includes snapshots, portfolio,
signal, AI assessment and risk result. Representation is deterministic for identical
validated inputs, but numerically equivalent decimal spellings are not normalized
into a universal financial identity. These IDs are not an exchange idempotency contract.

## Contracts and orchestration

models.py: MarketEvent, Candle, MarketSnapshot, Signal, AIAnalysis, RiskDecision,
OrderIntent, OrderState, Fill, PortfolioState and DecisionRecord plus unit-bearing
Money and AssetBalance. Exact decimals reject float/bool/non-finite/negative monetary
inputs. TMN and IRR remain different currencies; no implicit conversion. UTC-aware
timestamps required; OHLC/time bounds and snapshot visibility/order validated.
Snapshot gaps are permitted at this layer; cadence/freshness/gap policies need later
adapter validation. Account positions, FX valuation and lifecycle transitions are not
implemented by these data models alone.

interfaces.py: typed Protocol ports for Clock, MarketDataProvider, ExecutionProvider,
Strategy, SignalEvaluator, RiskManager, PortfolioRepository, DecisionRepository and
EventBus. No core import depends on Wallex, LangGraph, FastAPI or an LLM SDK.

TradingEngine observes a snapshot and account state using an injected clock, checks
identity/as-of, calls injected strategy/evaluator/risk, records a deterministic audit
decision and publishes it. Persistence failure prevents publication. There is no
order-building or submit path. Future execution must add separately tested safety
and reconciliation contracts; merely injecting ExecutionProvider cannot execute.
LangGraph can coordinate this core later without duplicating financial logic.

## Tooling and container

pyproject.toml owns the new package and developer tooling configuration. Runtime
dependency is existing Pydantic 2. requirements.txt remains for the legacy backend.
Version ranges are declared; a complete reproducible lock is still future tooling work.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src/quantpilot tests
.\.venv\Scripts\python.exe -m mypy
docker compose run --rm offline-demo
```

Dockerfile builds only the new core, runs as an unprivileged user. Compose uses no
runtime network, no credentials/mounts/ports, a read-only filesystem and dropped
capabilities. Image build needs package-download access. Docker execution is not
verified unless explicitly reported. pytest/Ruff/mypy scope is the new core/tests;
they do not certify the legacy implementation or imported reference project.

## Verification results

- `python -m pytest -q`: 10 passed.
- `python -m ruff check src/quantpilot tests`: passed.
- `python -m mypy`: passed, strict checking of 7 source files.
- Editable build/install succeeded and the installed `quantpilot-demo` entry point ran
  successfully, returning HOLD / ABSTAIN / denied / NOT_SUBMITTED and JSON logging.
- Public PyPI was needed for developer/build tools because the default index returned
  no distributions. No credential file or exchange account was accessed by these checks.
- Docker executable was unavailable; image build and Compose execution were not tested.

## Phase boundary and deferred work

This authorized Phase 1 scope supersedes the earlier plan's narrower candle-first
task. No strategy, AI model, real order, simulator, Toman ledger, adapter migration
or background runner was implemented. SPEC.md remains the product authority.
