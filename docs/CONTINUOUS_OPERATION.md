# Continuous operation and compatibility

## Configuration

Use existing JSON files and configuration models, not a second YAML/env loader.
`operating_profile` is independent of BACKTEST/SHADOW/LIVE. The default is
CONTINUOUS. Core env configuration also accepts `QUANTPILOT_OPERATING_PROFILE`.
Neither profile enables LIVE; dedicated authorization still controls that.

Default profile fields:

```json
{
  "operating_profile": "CONTINUOUS",
  "starts_at": null,
  "deadline": null,
  "entry_cutoff": null,
  "force_final_liquidation": false
}
```

In backtests these fields belong to `simulation`; in SHADOW/LIVE they belong
to the existing root configuration. SHADOW's nested simulation contains fill
assumptions, not a second effective operating schedule. Do not configure a
conflicting nested operating schedule.

Competition settings use timezone-aware timestamps. Opt in explicitly with
`operating_profile: COMPETITION` and `force_final_liquidation: true` when desired.
A competition backtest without a deadline uses the last historical event as
its terminal boundary. Continuous exhaustion of a historical dataset only
ends replay; it does not sell remaining holdings. Reported equity still includes
marked holdings and is not necessarily settled Toman cash.

Legacy configs with a deadline and no profile infer COMPETITION with liquidation
enabled. Supplying CONTINUOUS together with a deadline is rejected. Legacy
backtests with no deadline must explicitly opt into terminal competition settlement.

## Sizing and caps

RiskParameters now includes `max_order_equity_fraction` (default decimal string
`0.10`) and nullable `absolute_order_hard_cap_tmn` (default `500000`). Fractions
use 0.005 for 0.5%, not 0.5. Asset/portfolio/risk limits remain independent.
Risk determines size from current equity and free funds, reserved exposure/risk,
ATR stop, costs and observed book depth; it never uses time remaining.
Regime remains a strategy eligibility gate, and AI can veto entries. No new
unvalidated model confidence, regime or drawdown sizing multipliers were added.

For LIVE, `max_order_tmn` is the legacy alias synchronized with
`risk.absolute_order_hard_cap_tmn`; contradictory values are rejected. Explicit
null removes only that absolute cap, preserving percentage/exposure/risk guards.
Changing any safety configuration invalidates previous config-bound grants.
The execution boundary includes its conservative max-fee allowance in the cap.

## Lifecycle

Protected LIVE execution persists STARTING/RUNNING/STOPPING/STOPPED controls
in its existing single-writer journal. The lifecycle abstraction also represents
DEGRADED and RISK_PAUSED. STARTING follows every construction/restart. Explicit
`resume_after_reconciliation()` checks fresh account state, nonambiguous orders,
authorization and risk/kill latches. A known open order is not an unknown order;
normal outstanding-order guards still prevent duplicate submissions.

`control('STOP_NEW_ENTRIES')` permits reductions while blocking buys.
`control('PAUSE_TRADING')` blocks ordinary submissions.
`control('GRACEFUL_SHUTDOWN')` blocks new ordinary orders; `close()` releases
transport resources and records STOPPED. None requests selling or cancels orders
automatically. Existing orders may remain at the exchange and must be reconciled.
No control clears a kill switch or a risk latch.

Existing position exits still use the same strategy/risk/Spot guard. Full automatic
deadline liquidation is available only under opted-in competition policy. A new
manual forced-close or portfolio-liquidation API is not exposed in this migration;
such commands must not be represented as shutdown or bypass order risk.

## Operational limits

The existing SHADOW polling service supports an unbounded run and reconnects,
with atomic position/order checkpoints and deterministic replay. LIVE remains a
protected adapter with proposal/reconciliation cycles, not a newly deployed 24/7
daemon. This change does not certify long-duration uptime, credit routing or add
LLM/LightGBM to LIVE's existing quant-only proposal helper. It preserves existing
AI integration in SHADOW/backtest. Expired LIVE grants fail closed even without
a competition deadline; renew through the separate reviewed activation process.

Old source/config-pinned journals and model artifacts must use their original
implementation or reviewed migration/revalidation. Never edit pins to force reuse.
No network/private exchange mutation is needed for this migration's tests.

## Modified components and verification

- `profiles.py`, core `config.py`, simulation/SHADOW/LIVE config models: shared
  timing policy and independent profile defaults, legacy deadline migration.
- `trading/sizing.py`, `trading/config.py`, `trading/risk.py`: extracted sizing
  kernel, fee-aware equity and optional hard caps.
- `backtest/replay.py`, `backtest/reports.py`, SHADOW reducer/execution: opt-in
  calendar settlement and profile entry checks; continuous retains inventory.
- `lifecycle.py`, `live/execution.py`: journaled controls, explicit resume,
  shutdown without sales and fee-aware execution cap. Existing ambiguity,
  idempotency, Spot and kill checks remain mandatory.
- `config/live.example.json`: disabled continuous example, no deadline.
- `SPEC.md`, `AGENTS.md`, architecture/implementation-plan and this document:
  corrected scope and migration considerations.
- `tests/test_profiles.py`: cross-product, indefinite policy, optional settlement,
  dynamic sizing and durable control tests. Existing LIVE setup tests explicitly
  resume after reconciliation; settlement tests explicitly select competition.

Offline full suite after functional migration: **319 passed, 1 skipped**.
The skipped test requires explicit isolated PostgreSQL opt-in. Ruff passed;
mypy passed for 78 source files. Fake exchange fixtures only; no LIVE activation
and no real exchange order submission. This is software verification, not proof
of indefinite production uptime or profitable trading.
