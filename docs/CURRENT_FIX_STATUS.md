# Current fixes and exact readiness

## Corrected defects

### Hybrid acceptance at the execution boundary

Previously the service checked AI but a direct call to the protected adapter could
submit an already risk-approved BUY without the configured AI assessment. The
adapter now requires hybrid acceptance bound to the exact authorized intent and
canonical signal. The service delegates evaluation to that boundary. Reject,
abstention, failure or cancellation revokes the grant. Recovery, kill, pause and
successful submission invalidate all temporary AI grants. Freshness is rechecked
after inference, so a slow model cannot authorize stale data. Risk and the common
Spot guard remain mandatory; liquidation/reduction does not gain an entry bypass.

Regression coverage: direct submit without AI, rejection/abstention followed by
submit, reconciliation after AI acceptance, and stale context after inference.

### Current exchange metadata versus research assumptions

Authenticated GET-only observations for the configured credit context returned:

| BTC/TMN field | Observed value |
|---|---|
| Maker fee | 0.0025 (0.25%) |
| Taker fee | 0.003 (0.3%) |
| Quantity step | 0.00000001 (8 decimals) |
| Price tick | 1 TMN |
| Minimum quantity | 0.00000001 BTC |
| Minimum notional | 50,000 TMN |

Report: `data/readiness/account-market-constraints.json`. These are current API
responses, not certified historical fee schedules or proof of key ownership.
The earlier 0.1% research fee is not the observed current taker fee.

The endpoint omitted `maxQty`. Reconciliation now checks a supplied maximum when
present and does not invent an exchange maximum when absent. Local order/equity
caps, risk sizing, funds and executable depth remain enforced. Missing required
precision/minimum/fee fields still fail closed.

### Disabled configuration preparation

`quantpilot.live.prepare` validates active credit context with GET, reads actual
fee/market metadata and creates a new disabled local candidate. It preserves the
existing approved BTC/TMN scope, budget, absolute cap and deadline. It does not
overwrite previous candidates or copy either exchange or LLM tokens. Account market
permission remains false pending review, rather than being inferred from a read.

```powershell
.venv\Scripts\python.exe -m quantpilot.live.prepare --intent config/live-credit-intent.local.json --output config/live-credit-next-candidate.local.json
```

Actual candidate created this run: `config/live-credit-reviewed-candidate.local.json`.
Its name matches gitignore's private LIVE config pattern. It is not an authorization
grant and is not suitable for immediate activation.

## One readiness command

```powershell
.venv\Scripts\python.exe -m quantpilot.readiness --config config/live-credit-reviewed-candidate.local.json --dataset data/readiness/real-ai-dataset.json --call-llm --report data/readiness/current-status.json
```

This checks the effective AI mode, model checksum/source/strategy compatibility,
strict LLM connection response and dataset checksum/sample count. It reports
SHADOW readiness separately from LIVE and never activates or mutates an exchange.
`--call-llm` makes one small paid-provider request; without it, connection status
remains unverified. Errors are sanitized. A nonzero exit when the model is missing
is an intentional prerequisite failure, not a claim that LLM connectivity failed.

Current observed result:

- BoxAPI connection: **SCHEMA_VERIFIED**.
- Baseline model path: missing; **not ready for hybrid SHADOW**.
- Real dataset: **zero eligible labeled samples**; not sufficient for training.
- Protected LIVE: disabled; account execution review and separate authorization
  remain required. No local assertion is treated as exchange introspection.

Training eligibility is a data/strategy result, not a coding exception. Do not
label rejected entries as eligible, change historical fees retroactively, promote
synthetic demo models, lower risk thresholds merely for samples, or rewrite hashes.
Existing compatible synthetic artifacts remain research-only and do not match the
baseline strategy. Long-duration real performance has not been established.

## Verification

- Full Python suite: **352 passed, 1 skipped** (optional isolated PostgreSQL).
- Ruff passed; mypy passed for **83 source files**.
- Credit metadata acquisition and BoxAPI connection were checked separately from
  offline mock tests. Candidate schemas validated without LIVE activation.
- No exchange orders, cancellations, transfers or withdrawals were submitted.
- No new production dependencies. Existing journals/model hashes were not rewritten.

Modified modules: `live/execution.py`, `live/service.py`, new `live/prepare.py`,
new root `readiness.py`; new tests cover hybrid boundary, metadata preparation,
scope/deadline preservation, secret exclusion and readiness classification.
Code changes require preserving old source/image versions for old LIVE journals.
