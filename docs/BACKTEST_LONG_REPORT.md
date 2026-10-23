# Longer historical BTC/TMN evaluation

## Data selection

Public, unauthenticated Wallex REST UDF history was requested in 12-hour chunks,
using resolution `1`, from 2026-09-23 17:00 UTC to 2026-10-23 17:00 UTC.
Existing RestPublic retry/rate handling, candle normalization and completed-bar
resampling were reused. Source chunks are cached under `data/backtest-long/chunks`.
43,184 of 43,200 expected minute candles were returned; 16 missing minutes divide
the history into four contiguous segments. No prices, volume or books were invented
to bridge these gaps. Coverage: `data/backtest-long/coverage.json`.

To extend the earlier 662-bar test without changing trading logic, select the latest
contiguous segment containing at least seven days, retain its last seven days and
trim incomplete 15-minute boundary buckets. Selection uses data coverage only,
not returns. The resulting test has 2,013 five-minute bars, 2026-10-12 23:15 UTC
through 2026-10-19 23:00 UTC. The most recent week crosses a gap and is not used
as a fabricated continuous history. This is not a full 30-day backtest.

## Reproduction

```powershell
.venv\Scripts\python.exe -m quantpilot.backtest.cli --input data/backtest-long/input.json --output data/backtest-long/baseline
```

The exact input contains the unchanged baseline research/risk settings. Initial
capital is 5,000,000 TMN, risk per trade 0.5%, default absolute cap 500,000 TMN,
and configured fees 0.1% per side. The competition settlement profile is explicitly
selected to report terminal cash and residual holdings. No parameter optimization,
LightGBM inference or LLM calls are included. No exchange mutations were submitted.

## Interpretation limits

Indicator warmup consumes roughly the first 600 five-minute bars before the
200-period 15-minute trend becomes available. Report entry reasons and rejected
signals as well as fills. No historical order books are available: synthetic spread,
slippage and volume participation are documented execution assumptions, not measured
historical liquidity. Fee/precision/minimum constraints are research-config inputs,
not verified current credit-account permissions. A short, single-market retrospective
sample cannot establish future profitability or authorize live trading.

## Completed results

Baseline completed successfully: initial/final equity 5,000,000 TMN, net return
0%, realized PnL 0 TMN, zero fills/trades/fees and zero mark-to-market drawdown.
Of 2,013 decisions, 2,005 were HOLD and eight were BUY candidates. All eight
BUY candidates were rejected by the unchanged Risk Engine with FEES_ERASE_REWARD.
That reason covers nonpositive net reward or net reward/risk below the configured
minimum after fees/slippage; it is not evidence that a trade was executed at a loss.
599 decisions lacked completed/warm historical features. Reason counts overlap.

The distinction matters: this longer sample does contain breakout entry candidates,
but none passes cost-aware risk eligibility. The 500,000 TMN sizing cap is not the
recorded rejection reason. Do not weaken the risk gate simply to force fills.
Profit factor and win rate are undefined without trades; zero drawdown is not
evidence of an effective trading strategy. No sensitivity scenarios were rerun on
this interval and no AI comparison or parameter optimization was performed.

Artifacts: `data/backtest-long/baseline/report.json`, `decisions.csv`, `metrics.csv`,
and aggregate `data/backtest-long/summary.json`. Exchange mutations: zero.
