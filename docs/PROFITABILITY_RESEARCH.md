# Profitability investigation and target architecture

## What is established

Software tests establish mechanics, not investment returns. The existing baseline
produced no executions in the longer recorded test. Eight BUY signals were blocked
by the unchanged fee-aware risk gate. Recomputing the same price rounding, ATR
levels and costs gives gross target distances 0.2909% to 1.0260% and net reward/risk
from -0.1848 to 0.5763 under the original research fee assumptions (minimum is 1).
At the currently observed 0.3% taker fee plus configured slippage, none passes;
only one has positive target return even before considering outcome uncertainty.
This is a conditional payoff calculation, not an executed or guaranteed return.

Exact per-signal output: `data/readiness/cost-diagnosis.json`. Current fees are an
explicit scenario; they are not certified historical fees. No future news or LLM
forecast was used. The active trading configuration was not modified.

## One preregistered offline candidate

Design recorded before viewing the candidate's own backtest outcomes:

- 15-minute entry, 60-minute trend confirmation.
- Existing Momentum Breakout rules, ATR stop multiplier 2, target multiplier 6.
- Existing risk fractions, order cap, ownership and exposure rules retained.
- 0.3% entry/exit fees, existing spread/slippage assumptions, current observed
  quantity precision/minimum constraints as explicit historical scenarios.
- Real contiguous minute data aggregated to 1,583 completed 15-minute candles,
  2026-09-26 11:00 UTC through 2026-10-12 22:45 UTC; gaps are not filled.
- Earlier data warms the indicators. Research account starts 2026-10-05 UTC;
  a separate account evaluates 2026-10-09 onward, with no inherited positions.
- No parameter retuning based on final-period results; no ML or LLM in this trial.

This is retrospective research. The candidate design was informed by a later
baseline cost diagnosis, and current metadata is used as a scenario. The final
period is separated from this candidate's tuning, but is not a blind prospective
or independently validated out-of-sample result. Any apparent gains require fresh
forward SHADOW and additional independent windows before promotion.

Files: `data/research-cost-aware/design.json`, `input.json`, `run.py` and
`research/`, `holdout/` report folders. Reproduce from repository root:

```powershell
.venv\Scripts\python.exe data/research-cost-aware/run.py research
.venv\Scripts\python.exe data/research-cost-aware/run.py holdout
```

JSON/CSV reports use the existing shared risk, accounting and simulated execution
engines. No fabricated historical depth; spread/depth/volume-cap simulation remains
an assumption. All outcomes, including zero trades or losses, must be reported.

### Completed candidate outcomes

Research period: 384 HOLD, 1 BUY; the BUY failed FEES_ERASE_REWARD.
Separated final period: 375 HOLD, 5 BUY; all five failed FEES_ERASE_REWARD.
Both accounts finished at 5,000,000 TMN with zero trades, fees, return and drawdown.
The single candidate did not establish a tradable cost-adjusted opportunity in
these windows. No further retuning was made after these results and no research
configuration was deployed. Details: `data/research-cost-aware/summary.json`.

No production source/configuration changed in this investigation, and no real
orders or LLM calls were made. Automated implementation tests were not rerun;
these results are historical simulation/data analysis, not new unit-test evidence.

## Architecture acceptance path

1. Validate market history and account-specific metadata, preserving provenance.
2. Evaluate a fixed strategy after costs across independent windows with sufficient
   executions and adverse-cost sensitivity; report uncertainty and drawdown.
3. Build labels from eligible executable entries. Preserve chronological splits,
   purge/embargo and sufficient training/calibration/test data. Never train a supposed
   production model from synthetic data or nonexistent eligible samples.
4. Compare quant, quant+ML and quant+ML+recorded-analyst on identical windows.
   Add AI only when its contribution is measured; a successful LLM call is connectivity.
5. Run the selected frozen configuration in public-feed virtual SHADOW, including
   restart, interruption, replay, fills, fee and ledger checks.
6. Independently review credit key ownership, account routing, market permissions,
   authorization scope and the deployment environment. Keep unresolved evidence
   visible and LIVE disabled. The user decides whether and how to execute real trades.

The intended path is a reproducible strategy with measured net performance and
bounded risk. No architecture, ML model or LLM can guarantee real profits.
