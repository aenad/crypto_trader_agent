# Momentum Breakout: cost-aware strategy research

Study date: 2026-10-23. Research ID: `wallex-momentum-cost-study-v1`.
Source: `research/strategy_study.py`. Frozen design:
`research/strategy-study-v1/plan.json`. Results: `data/strategy-research-v1-prepared/`.
SPOT/LONG_ONLY, shared engine, 5,000,000 TMN starting accounts; LIVE disabled.

## 1. Baseline verification and diagnosis

The original input and report still contain 2,013 completed BTC/TMN five-minute
candles, 8 BUY, 2,005 HOLD, zero risk approvals/orders/trades. All eight BUY fail
`FEES_ERASE_REWARD`. Original input/report and companion baseline CSVs are protected
by SHA256 values in the study manifest; they are not overwritten by this research.
The synthetic BUY/fill/SELL/fill test remains passing. Current local old-session
health still reports STOPPED; remote Ubuntu status is not established by it.

### All eight rejected entries

Exact amounts, rounding, stops, targets, fees and slippage allowances are in
`eight-buy-diagnosis.json` and `.csv`. Amounts are **TMN per one BTC**, not an
approved quantity: risk rejected before calculating order size. These exports
recompute the existing risk formula with Decimal precision 34 from the original
time-valid snapshots, rather than changing the risk decision.

| UTC timestamp | ATR / entry % | Net reward/risk: original costs | Net reward/risk: observed taker scenario | Observed-cost category |
|---|---:|---:|---:|---|
| Oct 15 04:40 | 0.17479 | 0.16466 | -0.24190 | A: non-positive reward |
| Oct 15 04:50 | 0.18548 | 0.20168 | -0.21016 | A |
| Oct 15 04:55 | 0.21863 | 0.30438 | -0.11876 | A |
| Oct 15 07:30 | 0.18569 | 0.20238 | -0.20955 | A |
| Oct 15 14:50 | 0.34201 | 0.57634 | 0.14982 | B: positive reward, insufficient ratio |
| Oct 15 19:35 | 0.14277 | 0.04008 | -0.34434 | A |
| Oct 15 19:45 | 0.13792 | 0.01915 | -0.36092 | A |
| Oct 16 11:10 | 0.09697 | -0.18475 | -0.51375 | A |

Required net reward/risk is **1**. Original 0.1% fees plus 0.1% slippage allowance:
1 category A, 7 category B. Observed 0.3% taker plus unchanged slippage allowance:
7 category A, 1 category B. The observed maker-fee bound also has 7 A / 1 B.
None passes the gate in any of those three diagnoses.

### What causes rejection?

The main demonstrated limitation is **target/stop geometry versus low ATR and
costs**, not the 500,000 TMN hard cap. Baseline stop is 2 ATR, target 3 ATR. For
entry P, stop S, target T, and `c = fee + slippage_allowance`, the risk engine uses:

```text
net_reward = T - P - c*(P + T)
net_planned_risk = P - S + c*(P + S)
```

Ignoring one-Toman rounding, with target multiplier a, stop multiplier b and
minimum net ratio 1, this requires:

```text
ATR / P >= 4*c / ((a-b)*(1-c))
```

With baseline a=3, b=2 and c=0.004, ATR must be about **1.6064%** of entry;
the rejected entries have only **0.0970%-0.3420%** ATR. Target 8 ATR, retaining
stop 2 ATR, reduces this necessary geometric threshold to about **0.2677%**.
It also makes targets harder to hit. Passing this gate never establishes positive
expected profit; realized outcomes and exit frequency must be measured.

No demonstrated arithmetic defect warrants bypassing the fee check. Its
conservative entry reference already includes spread/adverse slippage; the extra
cost allowance is also retained and exposed explicitly. Measuring that allowance
against recorded execution would be separate research. Historical OHLC cannot
determine true liquidity/queue costs or prove that entry timing caused these losses.
The extra entry-slippage allowance can be more conservative than the execution
model's already-adjusted entry basis. Formula agreement is not empirical cost
calibration; review that possible modeling overlap against captured books/fills,
rather than silently subtracting it to admit trades. The exported entry spread is
an OHLC proxy. Historical exit spread is unknown; the execution scenario assumes
the listed half-spread instead of claiming an observed exit quote.

## 2. Verified observations and assumptions

Authorized read-only refresh at `2026-10-23T19:50:54.888370Z` succeeded for
`GET /v1/account/fee` and `GET /v1/markets` with the configured account read context.
Only allowlisted numeric BTC/TMN metadata was stored, without account IDs or keys:

- Taker fee: **0.003 (0.3%)**; maker fee: **0.0025 (0.25%)**, per side.
- Minimum notional: **50,000 TMN**; minimum quantity and quantity step: **1e-8 BTC**.
- Price tick: **1 TMN**. Account-specific trade permission/routing is not verified.

These are observations now, not a certified fee schedule for all historical dates
or all markets. Official contracts: [account fees](https://developers.wallex.ir/docs/basic-services-account-fee)
and [public candles](https://developers.wallex.ir/docs/basic-services-candles).

| Scenario | Per-side fee | Slippage / risk cost allowance | Half-spread | Prior-volume participation |
|---|---:|---:|---:|---:|
| Primary taker | 0.30% | 0.10% | 0.05% | 1% |
| Conditional maker-fee bound | 0.25% | 0.10% | 0.05% | 1% |
| Adverse | 0.50% | 0.20% | 0.10% | 0.5% |

All historical spreads, slippage and capacity are assumptions, separately versioned
in the frozen plan and each report manifest. No historical books were reconstructed.
The shared replay submits MARKET intents: the maker-fee scenario only substitutes
the observed maker rate as an optimistic **conditional fee bound** with the same
adverse market-fill mechanics. It does not implement passive limit placement,
guarantee maker fills, model queue priority or justify a deployable maker strategy.
It cannot be the basis for promotion. Production settings were not changed.

## 3. Expanded data coverage

The existing UDF cache has 43,184 actual minute observations out of 43,200 requested
between Sep 23 17:00 and Oct 23 17:00 UTC. Rather than reusing only the old seven-day
input, the study validates all four contiguous segments and aggregates completed
five-minute candles. Conflicting duplicate timestamps abort; identical duplicate
source boundaries are counted; missing intervals are split, never interpolated.

| Segment | Aligned start UTC | End UTC | Completed 5-minute bars |
|---|---|---|---:|
| 0 | Sep 23 17:00 | Sep 26 10:55 | 791 |
| 1 | Sep 26 11:00 | Oct 12 22:55 | 4,751 |
| 2 | Oct 12 23:00 | Oct 19 23:05 | 2,017 |
| 3 | Oct 19 23:30 | Oct 23 17:00 | 1,074 |

Total: **8,633 five-minute candles**. Source-file SHA256s, dataset identities,
missing-minute totals and trimmed boundaries are in `manifest.json`. Partial
leading 15-minute trend buckets and trailing five-minute buckets are trimmed.
The cache lacks original download receipt timestamps, so replay explicitly assumes
publication at candle close. It does not certify historical network latency or
absence of exchange revisions. All comparisons use UTC and completed candles.

EMA200 on 15-minute trend needs roughly 600 five-minute bars per new contiguous
segment. Indicators can use earlier data from the same segment as warmup; accounts
do not inherit earlier trades. No feature, fill or balance is carried across a gap.
The available final segment is short, and much of it is warmup: a material limit
on test power. Historical data outside the cache was not fabricated or assumed.

## 4. Prespecified variants

| Variant | Changes from original baseline | Rationale |
|---|---|---|
| A_baseline | None to strategy; observed fee/constraint scenario for fair new comparisons | Immutable strategy reference |
| B_target8 | Target 8 ATR, stop remains 2 ATR; entry/trend/hold duration unchanged | Test wider cost-adjusted payoff geometry |
| C_confirmed_target8 | B plus ADX >=25 and relative volume >=1.5 | Test stronger trend/volume confirmation against false breakouts |

All retain 5-minute entry, 15-minute trend, EMA50/200, RSI50-70, breakout20,
24-hour maximum holding period, Spot ownership and the existing risk engine.
The 0.5% maximum trade risk, two-position limit, exposure/daily-loss/drawdown
controls, minimum sizes, fee-aware ratio 1 and 500,000 TMN cap remain intact.
Adverse-cost risk slippage estimates increase consistently with simulated costs.

Two one-dimensional neighbors (target 7 and 9 ATR) are validation-only sensitivity
checks, not an expanded parameter search. No variant changes thresholds in the
production configuration. Alternative strategy family D was not justified by one
market and this limited sample. Earlier 15m/1h target6 trial already failed cost
eligibility and is documented in `PROFITABILITY_RESEARCH.md`; it was not retuned
or presented as an independent discovery here.

## 5. Chronological methodology and selection discipline

- Research/train: Sep 23 17:00 through Oct 6 00:00 UTC.
- Validation: Oct 6 00:00 through Oct 12 22:45 UTC.
- Descriptive fixed-parameter walk-forward blocks: Sep 29-Oct 2 and Oct 2-Oct 6.
  They do not retrain a model or optimize parameters per fold.
- Final holdout: Oct 20 00:00 through Oct 23 17:00 UTC.
- Windows use `[start,end)` decision timestamps and only earlier same-segment
  warmup. Every account starts with its own 5,000,000 TMN. Unsettled assets are
  marked conservatively; they are not converted into fictitious final fills.
- Oct 12-19 is quarantined from parameter selection because its baseline outcomes
  informed this design. Original diagnostics remain available separately.

Candidate support requires at least 20 train and 10 validation closed trades,
positive train and validation net return, and drawdown at most 5%. Selection ranks
passing candidates by validation return, then train return, then name. If none
passes, the baseline is frozen as the final-test reference with **no winner**.
Selection is saved before opening the final period; the runner refuses to reopen
the final test for tuning. A distinct supported candidate would be evaluated once
alongside the baseline benchmark. Final evidence also needs at least 30 trades.

This is retrospective hypothesis research: prior baseline and earlier trials are
known, and recent public-market snapshots were previously inspected. The final
period is held out from variant outcome selection, not a blind prospective trial.
Three candidates and predefined sensitivity cases provide no automatic statistical
significance. No best-in-sample return is claimed as a robust edge.

All cases use `HistoricalReplay`, `MomentumBreakout`, `DeterministicRiskEngine`,
`SimulatedExecutionProvider` and the same Decimal portfolio ledger. Decisions use
completed candles and prior breakout windows. Fills use the next eligible bar event
with adverse spread/slippage and prior completed volume capacity, not last trade
price. Same-boundary next-bar execution assumes no processing latency; adverse cost
scenarios test some execution uncertainty, but cannot establish real latency/fills.

For compute limits only, `research/prepared_history.py` pre-aggregates the same
completed series once, then exposes prefixes by close-time bisect. It changes no
strategy, risk, execution or accounting code. Tests compare all reports/decisions/
fills/PnL/manifests on a complete synthetic round trip and compare snapshots at
several prefixes, including future-candle mutation isolation. The already-completed
791-bar actual historical report also matches the original provider's report
exactly. The original slow attempt and its runner are retained under
`data/strategy-research-v1/`, marked compute-interrupted before selection or final
evaluation. Plan, parameters and data are unchanged; the new study manifest pins
both research runner and prepared-provider source. No old source hash was rewritten.

Disconnected segment returns are reported separately; their sum is a research
comparison statistic, **not a compounded continuous portfolio**. Profit factor,
win rate, average holding time, realized/unrealized PnL, exposure, fees, open
holdings, full trade PnLs and equity curves remain available per segment.

## 6. Results

Results are being computed under the frozen plan. Final conclusions and common
comparison tables are added only after those runs finish.

## 7. AI, SHADOW and deployment policy

No experimental LightGBM is trained or substituted for the missing validated
baseline. The existing dataset builder labels only risk-eligible strategy BUY.
Training requires at least 100 train, 30 validation and 30 test samples, plus
purging/embargo and quality/promotion checks. Missing eligible observations cannot
be replaced with synthetic labels or relaxed thresholds.
The existing label horizon is six entry bars (30 minutes at five-minute entry),
while this strategy can hold for 24 hours. A future ML study must explicitly assess
that target/horizon alignment; a new ATR target alone does not validate the labels.

A research result with insufficient support is not exported into a deployed
SHADOW session. Existing SHADOW databases and service configuration remain intact.
If a candidate later qualifies, use a new source/config-pinned virtual session,
measure actual bid/ask/spread/latency, verify accounting/recovery and replay, and
compare forward signal frequency without requiring trades to occur.

Before any LIVE consideration: obtain sufficient independent positive-after-cost
outcomes, validate any ML model chronologically, measure hybrid contribution on
identical data, complete forward SHADOW evidence, independently review credit key
scope/routing/permissions and market constraints, reconcile account/open orders,
verify kill/recovery controls, and separately authorize an exact LIVE configuration.
This research does not activate LIVE, submit real orders, cancel existing orders,
transfer funds or expose credentials to AI.

## 8. Reproduction

Commands from the repository root, using existing optional dependencies:
Reproduction requires the preserved public candle cache and baseline artifacts;
these runtime datasets are not bundled as production source. Use a separate clean
workspace/output copy of the pinned study when rerunning from scratch, preserving
the original results.

```powershell
.venv\Scripts\python.exe -m research.strategy_study metadata
.venv\Scripts\python.exe -m research.strategy_study prepare
.venv\Scripts\python.exe -m research.strategy_study diagnose
.venv\Scripts\python.exe -m research.strategy_study select
.venv\Scripts\python.exe -m research.strategy_study sensitivity
.venv\Scripts\python.exe -m research.strategy_study final
.venv\Scripts\python.exe -m research.strategy_summary
```

`metadata` is the only network command and performs two authorized GET reads;
skip it to use the explicitly labeled prior-metadata scenario. Other commands use
existing local data only. Prepared studies refuse source/plan/baseline identity
changes; outputs are not overwritten. Final evaluation has a one-use opening seal.
Use the pinned source/data for reproduction; a new experiment needs a reviewed new
study identity and destination, not deletion of the old results or hash edits.

Verification: **362 tests passed, 1 optional PostgreSQL integration skipped**;
Ruff/mypy checks cover the existing production source; research checks are recorded
separately. Mypy passed for 84 production source files. Seven new research tests
cover gap/duplicate handling, incomplete terminal minutes, immutable risk controls,
no-final-data selection, no forced winner, common-engine summary behavior, prepared
snapshot equivalence/future isolation and complete shared-engine report equivalence.
