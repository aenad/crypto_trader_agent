# Phase 5 AI evaluation — synthetic verification

Date: 2026-10-23. **Decision: NOT ENABLED for deployment.**

This is an executed software/accounting experiment, not a Wallex performance
claim. LightGBM was really trained; LLM outputs were explicitly synthetic
recorded fixtures. No real LLM calls, exchange credentials or orders were used.

## Reproduce

```powershell
.\.venv\Scripts\python.exe -m quantpilot.ai.cli demo --output artifacts/ai-phase5-final
```

Detailed generated report: `artifacts/ai-phase5-final/ai-evaluation.json` and `.md`.
Development walk-forward results: `training-report.json`. Per-variant directories
contain full Phase 4 reports/ledgers, and inference logs are in
`holdout-predictions.csv`, `recommendations.json`, and `analyst-traces.json`.
Generated datasets, caches and model artifacts are ignored by Git.

## Frozen experiment

- Dataset: `cabcd12d7ee17c9939a58f1d92015b723b4ffb0199496185b582aa5b2bace6ad`.
- Model: `3b263d2cfce1410ad3c662807a7dfc8e9255f69942dae7da99257e6ca76d5d27`.
- Environment: LightGBM 4.7.0, NumPy 2.5.4; native text artifact and manifest saved.
- 480 synthetic 5m bars; 76 eligible fully executable labeled opportunities.
- Chronological train/calibration/final test: **45 / 15 / 16** opportunities.
- Fixed-horizon target: two bars. Demo embargo: zero; opportunity intervals in
  this fixture do not cross split boundaries, so zero samples were purged.
  Separate tests verify purging/embargo with deliberately overlapping labels
  across multiple markets. Research defaults use a 900-second embargo.
- Two development walk-forward folds evaluated, with 24/36 training samples
  respectively and nine forward-test samples each; no final holdout labels used.
- Common test window: **2026-10-02 08:05–16:00 UTC**. Starting cash is exactly
  **5,000,000 Toman** for each variant at that boundary; earlier candles are
  feature warmup only.
- Trade threshold fixed at 0.55 before final evaluation. Calibration uses only
  validation labels. No final-test tuning was performed.

## Same-window portfolio comparison

| Variant | Net return % | Max drawdown % | Closed trades | Fees, Toman |
|---|---:|---:|---:|---:|
| A: Quant only | -0.85581521432 | 0.85581521432 | 16 | 15,904.046716 |
| B: Quant + LightGBM | 0 | 0 | 0 | 0 |
| C: Quant + LightGBM + LLM fixtures | 0 | 0 | 0 | 0 |

The quant account ended at 4,957,209.239284 Toman after 32 fills; its realized
PnL was -42,790.760716 Toman. At the unchanged 0.55 threshold, LightGBM rejected
all test entries. Both hybrid variants therefore stayed in cash. This does
**not** demonstrate robust ML profitability or incremental LLM value. Sixteen
analyst fixtures were replayed and validated, with zero historical network
calls; LLM assessments did not change the ML vetoes.

## Predictive and uncertainty diagnostics

- Final-test calibrated Brier: **0.1653674054**.
- ROC AUC: **0.6538461538** across only 16 labels.
- Expected calibration error: **0.2026822356**; probability quality remains weak
  and low-sample. Full reliability bins, raw scores, log loss and the training-
  prior benchmark are in the generated JSON.
- Only **one UTC day block** is available. Paired trading-return intervals are
  explicitly null with `INCONCLUSIVE_TOO_FEW_DAY_BLOCKS`, not fabricated tight
  confidence bounds. Synthetic and temporally dependent samples cannot establish
  generalization.

## Why deployment remains disabled

The data/responses are synthetic, the holdout is short, hybrid variants selected
zero trades, and there is no prospective SHADOW evidence. Real provider efficacy,
historically available pretrained knowledge, execution quality, market coverage
and generalization are unverified. Fixed-horizon full-fill labels also differ
from the strategy's realized stop/target lifecycle and exclude censored trades.

The implementation permits a real-data evaluation with recorded responses, but
requires adequate purged samples and exact source/config/environment identities.
Retrospective LLM responses are flagged: time-valid supplied context alone cannot
rule out future knowledge in model pretraining. Freeze research/promotion rules
before future evaluation, collect appropriate prospective evidence, and review
uncertainty before any deployment phase. A report never enables LIVE execution.

## Verification

Full suite: **135 passed, 1 skipped** (existing opt-in PostgreSQL integration).
Ruff passed. Strict mypy passed for 42 packaged source files. The installed
`quantpilot-ai train` command reproduced the same frozen model version from the
saved dataset. Tests include real LightGBM training/reload, holdout mutation
isolation, global purge/embargo, hand-calculated label costs, LLM validation,
timeouts/cache replay/concurrency, gateway token boundaries, risk vetoes,
SELL preservation, holdout FX isolation and repeated identical A/B/C reports.

See [Phase 5 implementation details](phase5.md) for exact contracts and limits.
