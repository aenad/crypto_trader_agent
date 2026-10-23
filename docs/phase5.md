# Phase 5 — Hybrid AI signal evaluation

## Scope and safety boundary

`quantpilot.ai` adds independent LightGBM trade-quality and LLM Analyst
components, a bounded harness, and veto-only fusion. Phase 3 strategy, feature,
risk and position-lifecycle modules are unchanged. Phase 4 replay adds an optional
`SignalEvaluator` and `decision_start`; defaults preserve quant-only behavior.
The existing observation engine already accepts the same evaluator interface.

AI produces a structured `CandidateRecommendation`, never an order. BUY may become
HOLD; SELL/HOLD pass through unchanged. Replay gives the **original canonical
strategy signal** to the deterministic Risk Engine after AI evaluation. Risk
approval and AI acceptance are both required for a simulated BUY. Exits do not
depend on AI availability. No LIVE configuration, exchange mutations, account
credentials, AI-controlled sizing or automatic deployment is added.

## Setup and commands

AI dependencies are optional; normal core installation remains unchanged:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,ai]"
.\.venv\Scripts\python.exe -m quantpilot.ai.cli demo --output artifacts/ai-phase5
```

The demo trains actual CPU LightGBM on **synthetic prices**, writes a frozen model,
and replays **explicitly marked synthetic analyst fixtures**. It performs no LLM
network calls and establishes no real-world profitability or LLM effectiveness.
Its small indicator windows, lower research reward/risk threshold, participation
assumptions and reduced training minimums are test fixtures, not recommended
competition parameters. Global Phase 3 defaults are unchanged.

For real research data, use the same JSON history contract as Phase 4, with
completed **entry-timeframe source candles** (default 5m), explicit approved markets,
market constraints and point-in-time FX/recorded quotes where available. Resample
finer data explicitly before labeling; do not silently reinterpret a label bar.

```powershell
.\.venv\Scripts\python.exe -m quantpilot.ai.cli dataset --input history.json --config ai-config.json --output artifacts/ai-research/dataset.json
.\.venv\Scripts\python.exe -m quantpilot.ai.cli train --dataset artifacts/ai-research/dataset.json --output artifacts/ai-research
.\.venv\Scripts\python.exe -m quantpilot.ai.cli evaluate --input history.json --dataset artifacts/ai-research/dataset.json --model artifacts/ai-research/models/MODEL_HASH --responses artifacts/ai-research/responses --analyst-model-id YOUR_RECORDED_MODEL_ID --output artifacts/ai-evaluation
```

`--config` is optional; its JSON validates against `LearningConfig`. Defaults:
6 label bars, 900-second split embargo, 40 boosting rounds, 7 leaves, 10 samples
per leaf, 100/30/30 minimum train/calibration/test samples, probability threshold
0.55, seed 173. No hyperparameter or threshold search over the final test is run.
Too few samples or a single class in train/calibration fails explicitly.

Installed console command: `quantpilot-ai`. Optional gateway transport uses
httpx from the existing marketdata extra; offline AI evaluation needs no network
transport package. No OpenAI/vendor API contract is assumed.

## Dataset and labels

At each completed entry boundary, evaluate the exact strategy/risk against a
separately funded **flat research account**. Only eligible, risk-approved BUY
opportunities enter labeling. These independent opportunities are not an
investable portfolio; actual portfolio constraints are evaluated separately.

The feature schema has 12 allowlisted values: entry/trend EMA gaps normalized by
price, RSI, ATR fraction, ADX, relative volume, breakout fraction, trend ADX/ATR
fraction, spread, depth imbalance and UTC hour. Features use only the signal's
time-valid snapshot. No target, outcome, future price, news, source text or
private account field is exposed to inference.

Labels are a deliberately explicit research target: a fully executable entry at
the next bar open and fully executable fixed-horizon market exit after `label_bars`.
Use Phase 4 simulator/fees/ticks/spread/slippage/capacity and point-in-time FX.
Positive means strictly positive net TMN profit after entry/exit costs and, for
USDT, per-notional round-trip FX conversion fees. Net PnL/return remain Decimal.
Only the statistical ML matrix/probabilities/metrics use floats.

Partials, unfillable entries/exits and unavailable future bars are **censored**,
counted and excluded, never guessed as wins/losses. Therefore the target estimates
profit conditional on complete execution. It differs from Phase 3's stop/target/
EMA lifecycle; final trading ablation measures that exact lifecycle, not these
independent labels. Idle USDT gains and full-account funding costs are not added
to per-trade labels. Dataset counts/provenance disclose these selection limits.

## Leakage prevention and training

- Global 60/20/20 boundaries use distinct signal timestamps across all markets;
  simultaneous samples never straddle a split.
- Purge train intervals whose **label end** reaches calibration start minus
  embargo; purge calibration intervals reaching final-test start minus embargo.
  Strict inequalities remove boundary-touching labels too.
- Walk-forward development uses two expanding train/calibration/forward-test
  folds wholly before the final holdout. Inadequate folds are reported, not filled
  with invented scores. No final holdout labels train/calibrate/select a model.
- Inverse concurrent-label-count weights reduce overlapping training influence.
  They do not make those observations independent; temporal uncertainty remains.
- Fit binary LightGBM on training only. Fit temperature calibration on validation
  only using a fixed temperature grid. Validation metrics are explicitly fitted
  diagnostics; test calibration is the out-of-time evidence.
- Fixed fusion threshold is separate from predictive accuracy/precision/recall,
  which use the conventional 0.5 metric threshold.

Artifacts are versioned directories containing native `model.txt` and a JSON
manifest, not pickle. Identity includes model checksum, feature order/schema,
training/calibration sample IDs, source implementation hash, data/config IDs,
trained-through time, CPU parameters/seeds, and LightGBM/NumPy versions. Loading
checks hashes, feature order and exact runtime/code identity. Inference rejects
timestamps before all training/calibration labels were available. Keep the exact
source/environment and dataset alongside frozen artifacts; code upgrades require
an explicit versioned re-evaluation, not silent reuse. Checksums detect changes,
not malicious replacement by someone with write access.

Artifacts have `RESEARCH_FROZEN`, `research_only=true` predictions and
`live_enabled=false`. Freezing validates contracts/reproducibility, not trading
merit. No report automatically enables deployment.

## LLM provider, context and harness

`LLMProvider` exposes only `model_id` and asynchronous `complete(request,schema)`.
`JsonGatewayProvider` supports an explicit operator-controlled HTTPS gateway:

```text
POST {model, request, response_schema}
response {output: "<structured JSON string>"}
```

This is our gateway contract, **not a claimed vendor endpoint**. The adapter was
tested with a mock HTTP transport; no real provider/model configuration has been
supplied or verified. Inject only a dedicated LLM token. The provider never loads
`.env` or Wallex credentials. Tokens are header-only; redirects and environment
proxies are disabled; exchange destinations and credential/query URLs are rejected.
An in-process injected Python provider is trusted application code, not an OS
sandbox; operators must not pass trading clients/secrets into it.

`AnalystHarness` assembles a versioned prompt and numeric context with at most
eight completed bars. Local tool routing has exactly two read-only tools:
`market_features` and `recent_completed_bars`. No dynamic tools, shell/filesystem,
MCP writes, news retrieval, balances or order methods are exposed to the LLM.

Outputs require matching context hash/as-of, ACCEPT/VETO/ABSTAIN, strict integer
confidence 0–100 and bounded allowlisted reason codes. Extra fields, trading
commands, duplicate JSON keys, Markdown wrappers, invalid timestamps and malformed
output fail closed. Analyst confidence is not a calibrated trade probability.
Bounded configurable timeouts and a per-harness provider-call budget cover failures;
there are no automatic retries. Failure becomes abstention; hybrid entries then
stay HOLD unless already vetoed by ML. Both components are logged independently.

Cache keys include full prompt/version, schema, context and model ID. Valid
responses store the request/input snapshot, model, prompt, response, recorded time
and evidence type. First response wins through atomic exclusive file publication;
conflicts/checksum changes fail. Invalid raw text/errors are not saved or echoed
because they may contain private provider content. Structured failure traces are
retained. Harness traces and financial ledger remain separate.

Historical evaluation uses **replay-only** mode: cache misses abstain and cannot
call a model. To collect new responses outside historical evaluation, instantiate
the harness with an explicitly configured provider, clock, `replay_only=False`,
timeout and budget. Historical comparison requires those recorded responses.
Prompting cannot guarantee a pretrained LLM lacks future knowledge: retrospective
responses are flagged and do not establish historically valid efficacy. Even
timestamped prospective records require trusted provenance. No future news or
label/outcome fields are supplied; no real historical LLM benefit is claimed.

## Fusion, comparison and reports

`veto-only-v1`: quant BUY requires calibrated ML probability at least its frozen
threshold; variant C additionally requires LLM ACCEPT. VETO rejects, missing/
invalid/ABSTAIN produces HOLD. Neither component can invent BUY/SELL, change size,
alter stops, choose an account or authorize an order. SELL always bypasses AI.

Compare A quant, B quant+ML, C quant+ML+LLM on the **same final chronological
window** with identical input, warmup, universe, capital, deterministic strategy/
risk, execution costs, accounting and terminal liquidation. No pre-holdout
entries are allowed. Pre-holdout candles are feature warmup only: capital,
funding, FX exposure, equity and metrics begin at holdout start identically for
all variants, excluding training-period FX movements from test returns.

Outputs include dataset counts, `training-report.json` with development
walk-forward results, frozen model files, `ai-evaluation.json/.md`, separate
`analyst-traces.json`, per-variant `recommendations.json`, and full Phase 4 JSON/CSV
ledger/equity/order/decision/trade reports. Every prediction records features,
time, model version, raw and calibrated probabilities. Replay IDs include the
evaluator identity, response-cache hash and holdout start.
`holdout-predictions.csv` also exports every labeled test opportunity's features,
model scores and targets for offline auditing; targets never enter LLM context.

Predictive metrics: Brier, log loss, AUC (null for one class), accuracy, precision,
recall, calibration error/reliability bins, raw-vs-calibrated and training-prior
baseline. Trading metrics: net return, marked drawdown, trades, fees, exposure and
equity. Uncertainty uses deterministic paired UTC day-block bootstrapping of
return differences; fewer than five blocks is explicitly inconclusive. Serial
dependence, universe bias and censored samples remain limitations. Zero selected
trades cannot establish incremental LLM value. See `AI_EVALUATION_REPORT.md` for
the actual synthetic verification outcome.

## Verification and phase boundary

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check src/quantpilot tests
.\.venv\Scripts\python.exe -m mypy src/quantpilot
```

Tests cover hand-calculated cost-aware labels, censorship, time-valid features,
purging across markets, walk-forward isolation, holdout mutation invariance,
deterministic actual LightGBM training/reload, calibration arithmetic, artifact
tampering, LLM schema/timeout/budget/cache failures, private-context exclusion,
mock HTTP token boundaries, concurrent immutable cache writes, SELL preservation,
risk override prevention and reproducible A/B/C reports. AI tests requiring
LightGBM skip explicitly when the optional extra is absent.

Phase 5 ends here. Real data/recorded LLM evidence, prospective shadow validation,
promotion thresholds and authorization remain prerequisites for any future
deployment phase. No live trading was enabled.

## Official API references used

- [LightGBM training API](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.train.html)
- [Native model persistence/inference](https://lightgbm.readthedocs.io/en/stable/pythonapi/lightgbm.Booster.html)
- [Deterministic CPU parameters](https://lightgbm.readthedocs.io/en/stable/Parameters.html)
