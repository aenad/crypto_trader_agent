# Separate LIVE activation checklist

**No item here has been approved by implementing Phase 7. Do not activate from
synthetic backtest/model results or possession of an API key alone.**

## External evidence — mandatory before configuration

- [ ] Confirm final competition rules, exact deadline/time zone, scoring currency,
  mandatory liquidation and approved market list with the organizer.
- [ ] Identify the funded account and account type independently. **Current adapter
  supports MAIN_SPOT only. A credit/prop/subaccount challenge account is blocked**;
  first verify and implement its official routing with separate mock tests.
- [ ] Verify official endpoints/response shapes using authorized private READS in
  a separate reviewed session. Check complete cumulative fills, timestamp formats,
  fees, open-order pagination, client-ID lookup and precision/max quantity fields.
- [ ] Verify FREE versus TOTAL balance value semantics, including locked funds,
  without placing an order as part of this implementation. Preserve secure evidence.
- [ ] Review restricted API key permissions in Wallex: read and spot trade only,
  withdrawal/transfer permissions disabled; restrict IPs where supported. Confirm
  the key really belongs to the intended dedicated account. The adapter cannot
  independently discover those permissions/account identity from verified APIs.
- [ ] Resolve any discrepancy between current official cancellation contracts and
  the documented query-parameter contract implemented here. No trial mutations.
- [ ] Confirm direct TMN settlement routes. USDT settlement is unsupported; do
  not bypass this restriction for a market the adapter cannot safely settle.
- [ ] Confirm the competition's residual-dust policy and fee-asset rules. Current
  liquidation reserves a possible base-asset fee and cannot guarantee zero dust.

## Research and operations review

- [ ] Freeze strategy/risk/config versions; retain out-of-sample and prospective
  SHADOW evidence. Review costs, gaps, latency, adverse fills and stop-gap exposure.
- [ ] Obtain separate explicit account/budget/order authorization from the operator.
  Set the initial capital, per-order budget, market minimums/steps/ticks, maximum
  accepted fee and liquidation lead time. Initial parameters are not claimed optimal.
- [ ] Use a dedicated account with the exact Toman cash budget, no imported crypto
  inventory, open orders, locks or unrelated activity. Bootstrap rejects other states.
- [ ] Protect local config/grant/DB/logs with OS permissions and backups. Keep the
  execution database separate from SHADOW/legacy data. Test restore/recovery offline.
- [ ] Review `config/live.example.json` as an **unverified disabled template**, replace
  constraints/deadline with verified values and save an ignored local copy.
- [ ] Create a separately reviewed AccountAuthorization with evidence reference,
  correct account type/label, config hash, credential fingerprint, permission flags,
  balance semantics and validity covering the deadline. Never commit actual grants.
- [ ] Keep the actual API key only in the dedicated execution environment variable
  `QUANTPILOT_WALLEX_LIVE_API_KEY`; never provide it to LLMs, frontends or test runners.
- [ ] Only after approval, set config `enabled=true` and separately set
  `QUANTPILOT_LIVE_AUTHORIZATION` to its exact resulting config ID. The unchanged
  legacy/web/core LIVE switches do not activate this adapter.

## Service supervision and rollout

- [ ] Wire a reviewed external execution loop to fresh public snapshots, explicit
  risk-authorized submission, status reconciliation and deadline liquidation ticks.
  Phase 7 supplies methods, not an automatically started LIVE service.
- [ ] Reconcile on startup. Never auto-resubmit SUBMITTING/UNKNOWN intents, even
  after a 404. Operator investigation is required if status cannot be established.
- [ ] Exercise the external kill command against a mock running writer; confirm
  new orders stop and existing exchange orders remain visible for explicit cancel.
- [ ] Alert on health not ready, stale data, unknown results, reconciliation failure,
  loss/drawdown suspension, overdue liquidation and untradeable residual dust.
- [ ] Confirm reducing exits continue under loss suspension with reliable data;
  hard kill still blocks all new orders. Do not add a risk bypass for AI output.
- [ ] Define human response for unknown orders, foreign balance changes and outages.
  Stop new exposure; reconcile safely. Never use an unrelated endpoint or guessed retry.
- [ ] After a hard kill, retain the journal and kill file. No automatic kill reset
  exists; only a separately reviewed operational recovery may clear persistent latches.

**Implementation authorization is not LIVE trading authorization. No real order
has been placed to complete or verify this checklist.**
