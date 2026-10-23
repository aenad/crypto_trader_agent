# Protected execution readiness review

Later correction: software-level CREDIT_SPOT scope and shared hybrid evaluator
construction have now been added and tested with mocks. BoxAPI connectivity was
verified with a non-trading request. This supersedes the MAIN_SPOT-only software
limitation below, but does not certify real credit routing or promote a research
model. See [hybrid/credit fixes](HYBRID_CREDIT_FIXES.md) for current evidence.

## Scope and changes

This review does not activate LIVE or authorize new exchange mutations.
`live/service.py` adds an injectable continuous execution coordinator around the
existing ProtectedExecution adapter. It loads no credentials and exposes no
activation CLI. The adapter must already have separate valid authorization,
initialization, reconciliation and explicit resume. Each cycle refreshes public
snapshots and reconciles account/orders before canonical strategy/risk proposals.
Ordinary submit rechecks freshness, risk authorization, funds, precision, lifecycle,
kill switch and fee-aware caps. Optional external entry evaluation only vetoes;
it cannot create orders, and missing AI validation is not represented as AI evidence.

The loop supports bounded offline tests and unbounded operation until an explicit
stop. Network/context/AI/submission failures latch suspension and stop the loop;
there is no blind POST retry or automatic resume. Existing adapter recovery uses
bounded read retries. An ambiguous order remains in its durable journal for GET
reconciliation after operator review. Shutdown releases transport resources without
selling positions or silently canceling exchange orders. A safely suspended service
is preferred to pretending an unknown account is ready. External monitoring and
deployment supervision are still needed for production uptime.

The cancellation request now follows the captured official spot Swagger:
`DELETE /v1/account/orders` with JSON `clientOrderId`, not a query parameter.
Its mutation callback uses the same JSON identity. Tested with MockTransport only;
no actual exchange cancellation was performed.

## Recorded evidence

- Before source modification, deterministic replay matched all 40 recorded frames
  and 3 decisions. Report: `data/shadow-continuous/pre-live-replay.json`.
- A later frozen SHADOW snapshot contained 44 frames and 4 HOLD decisions, no
  realized PnL or fees, equity 5,000,000 virtual TMN. Every signal failed trend,
  breakout, RSI and relative-volume entry conditions. No profitability evidence.
  Report: `data/readiness/shadow-summary.json`.
- The credit diagnostic still reads discovery/wallet/fees/open orders successfully;
  package active/overview still return 401, code 1201. Report:
  `data/wallex/pre-live-diagnostic.json`.
- GET lookup of the user's earlier manual order returned CANCELED with and without
  the selector. Neither response contains sub-account identity. Thus it verifies
  readable order state, not credit routing or key ownership. No fill/account dump
  or credential was exported. Report: `data/readiness/order-routing-read.json`.
- Existing protected account authorization remains MAIN_SPOT-only. Do not switch
  its account type or claim credit execution is certified based on these reads.

## Historical evaluation

662 recorded public 5-minute candles were extracted from the last frozen SHADOW
snapshot for an initial quant-only historical evaluation. This is a small, already
observed sample, not an independent out-of-sample validation. Historical depth is
unavailable. Fill scenarios therefore use documented OHLC spread/slippage/volume
assumptions, not reconstructed books. Fees and market metadata originate in the
research config and are not certified against this credit account.

Input: `data/readiness/historical-input.json`. JSON/CSV reports and sensitivity
scenarios are written under `data/readiness/backtest`. Even a favorable result
cannot satisfy live profitability/robustness acceptance by itself.

Completed results: baseline, doubled costs and halved execution capacity all
produced zero trades, zero return, zero fees and zero drawdown. These results
show no demonstrated trading edge; sensitivity is uninformative with no fills.
Do not tune entry thresholds merely to create trades or promote this to LIVE.

## Verification

- Full Python suite: **324 passed, 1 skipped** (optional isolated PostgreSQL).
- Ruff passed; mypy passed for 79 source files.
- Five added offline service tests: explicit resume required, periodic reconciliation
  and duplicate prevention, network-failure suspension, entry veto and shutdown
  without sales, preexisting stop without submission.
- Existing execution tests retain partial fills, ambiguous network outcomes,
  restart recovery, kill/drawdown gates, freshness, limits and final liquidation.
- Exchange mutation calls during this task: zero. LIVE activation: none.

## Remaining activation blockers

1. Independently reviewed credit key/account ownership and exact routing evidence.
   The API's successful balance/order reads do not provide that identity.
2. A credit execution contract and normalization must be reviewed and tested before
   extending MAIN_SPOT authorization. Current service does not bypass this limit.
3. Account-specific fees/minimums/permissions must match the executable config.
4. More historical and SHADOW evidence with trades, costs and drawdown is needed;
   four HOLD decisions cannot validate performance or AI contribution.
5. Source/config-bound grants require new review after this source change. The
   earlier disclosed key must not become a production credential.

Source identities changed. Existing running SHADOW processes may still hold old
code in memory; preserve their journals and stop cleanly before a new-code session.
Use a new database path for fresh sessions; never rewrite old model/journal hashes.
This report separates implemented execution infrastructure from unresolved exchange
identity evidence and strategy validation. It is not a live activation checklist pass.
