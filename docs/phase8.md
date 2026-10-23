# Phase 8 — Trading dashboard and competition evaluation

## Delivered architecture

The new entry `src/dashboard-main.tsx` renders the React 18 + TypeScript dashboard.
Vite builds static assets; FastAPI `quantpilot.dashboard.api:app` serves only
read-only reporting routes. There are no order, withdrawal, activation or runner
control endpoints. Existing React/FastAPI legacy sources are retained, including
`legacy.html` and archived setup notes. They are not imported by the new app.

The Python core, Phase 3 risk/strategy, backtesting, AI inference/harness, SHADOW
runner and protected LIVE executor are unchanged. New code projects their existing
evidence. Python uses Decimal for financial aggregation; browser numbers only
format display and draw charts. TMN is Toman and is never relabeled IRR.

| Section | Evidence shown |
| --- | --- |
| Overview | Initial capital, equity, realized PnL, provisional net return, observed max drawdown |
| Market Monitor | Approved universe, recorded market freshness/status, BUY/SELL/HOLD, reasons |
| AI Analysis | Recorded ML score, LLM assessment, fusion, model version and linked prompt version |
| Orders | Order states, cumulative quantities, individual fills, rejection reasons, latency availability |
| Performance | Equity/drawdown curves, daily equity changes, closed-trade win rate, fees, comparison |
| Testing | Backtest/SHADOW/replay evidence, Quant/ML/LLM comparison, report downloads |
| System Health | Recorded connections, writer lease, mode, failures, processing latency, risk state |
| Competition Report | Provisional metrics/activity, execution counts, strategy, AI, risk and reproducibility |

## Data provenance and missing evidence

- `DEMO`: deterministic illustrative UI fixtures. No backtest or model inference
  generated these performance values. All sections/downloads label them simulated.
- `BACKTEST`: existing Phase 4 `report.json`. Performance is explicitly simulated,
  including when historical input came from an exchange.
- `SHADOW`: exported Phase 6 evidence or a consistent read-only SQLite transaction
  over its current schema. Money/orders remain virtual. Fixture-frame sessions
  additionally carry a **Simulated-market SHADOW** label.
- `LIVE`: explicit operator-provided Phase 7 audit export, not an exchange query.
  Missing certified initial capital, realized PnL, trade count and aggregate fees
  stay unavailable. Net return is not inferred from the first observed equity.

The dashboard never silently replaces an unavailable recorded run with DEMO. Run
changes clear the previous metrics immediately. Polls do not overlap and requests
have a 15-second timeout. Failed loads clear the view and offer Retry. Source
timestamps stay separate from response generation timestamps. SHADOW freshness
uses its recorded configuration; an old export is marked stale.

MCP reads are reported only as the last recorded operation/configured transport;
the API does not invent a permanent MCP connection or probe it. The current
SHADOW runner uses REST/MCP polling, so its WebSocket status is NOT USED. Missing
connections/errors/circuit data remain unknown, never an assumed green status.
Recorded frame/LLM processing time is distinguished from per-order API latency,
which existing producers do not measure and the dashboard does not guess.

## API and artifact catalog

Set `QUANTPILOT_DASHBOARD_ROOT` to a dedicated public reporting root. Default:
`data/dashboard`. No `.env` loader or exchange credential variable is used.

```
GET /api/dashboard/health
GET /api/dashboard/runs
GET /api/dashboard/runs/{id}
GET /api/dashboard/reports/{id}.json
GET /api/dashboard/reports/{id}.md
GET /api/dashboard/reports/{id}.csv
```

`/health` establishes dashboard service availability only, not exchange/runner
health. Sources come from an optional `catalog.json`; each entry has a validated
ID/title/kind/path, plus optional replay/comparison/health/analyst_traces paths.
See `config/dashboard.catalog.example.json`. The default demo requires no catalog.

Paths resolve inside the approved root; hidden/outside paths, unsupported file
types, invalid JSON, malformed databases and oversized sources fail closed with
sanitized errors. SQLite opens with `mode=ro` and `query_only`; the source checkpoint
digest is checked. This is not full journal-chain verification or a replay run.
Readers do not acquire an execution writer lock or import a real exchange adapter.
SQLite/WAL permissions still need to permit consistent read-only access.

Only explicit typed fields are projected. Credentials, raw provider requests,
arbitrary analyst responses, account dumps and local source paths are not returned.
Responses are not cached and routes do not enable CORS. Deploy only on localhost:
there is no user authentication or authorization layer for internet exposure.

## Accounting and evaluation

Net return and observed drawdown are recomputed from the loaded Decimal equity
history and recorded positive initial capital, not trusted summary percentages.
Daily PnL is sampled equity change grouped by Tehran calendar day, not a fabricated
daily realized-PnL series. Closed trades supply win rate; no closed trades means
unavailable win rate. Unknown metrics stay null, distinct from a measured zero.

Charts display at most 2,000 points after full-history metrics/daily totals are
computed. Orders/fills/rejections show bounded recent activity. Reports explicitly
disclose truncation and observed-day coverage. Three displayed calendar dates do
not certify three full competition days. Final values remain **PROVISIONAL / NOT
CERTIFIED**, since terminal-liquidation certification is not imported.

ML/analyst/fusion evidence is displayed from recorded decisions, never recomputed
by the reporting server. Optional analyst traces link prompt and analyst model
versions by trace ID; missing traces are not filled with the latest source-code
version. The comparison reader accepts Phase 5 hybrid-ablation reports, retaining
research limitations and promotion reasons. This is a separate historical
evaluation, not the currently selected account's performance or proof of AI benefit.

Report identity hashes the projected content excluding its generation timestamp.
It is an integrity identifier, not a digital signature or independent provenance
certificate. Artifact registration remains a trusted local operator action.

## Local, Docker and offline workflows

The [judge-facing README](../README.md) contains exact setup, UI, backtest, public
SHADOW, offline rehearsal, replay, comparison and report-generation commands.

Docker Compose starts `dashboard-api` and `dashboard-web` by default. Report mounts
are read-only, ports bind to localhost, containers drop capabilities and the
application network is internal. No `.env` file is copied or injected as an env_file.
Build contexts explicitly include application source and exclude credentials/data.
The earlier collector/PostgreSQL and offline engine services remain opt-in profiles.

Docker was unavailable on the implementation host. Native startup and local browser
rendering were checked; container image build/startup is not claimed verified.

## Compatibility and limitations

- No LIVE activation, exchange/private-account calls or real analyst-provider calls.
- No final scoring/organizer certification or new live financial ledger. Existing
  competition account routing/key-permission prerequisites remain unresolved.
- No new strategy, model training logic, risk rule or execution behavior was added.
- No multi-user security or authentication; keep sensitive financial exports local.
- Source files are bounded to 64 MiB each, active SQLite files to 512 MiB, and loaded
  projected SHADOW history to 64 MiB. Initial long-history reads may be slow. Larger
  histories need an offline reporting/aggregation workflow; they fail visibly.
- An active read-only SQLite mount must expose its WAL/checkpoint consistently.
  Missing/inaccessible/corrupt state is unavailable, not a simulated fallback.
- LIVE implementation fingerprints include packaged source: installing Phase 8
  can require reviewed migration before a prior execution journal will reopen.
  Do not clear those guards or mutate existing journal metadata to bypass them.
- Existing model and SHADOW implementation hashes exclude the additive dashboard
  modules; compatible recorded replay/model paths remain available unchanged.

Stop after Phase 8. See [verification results](PHASE8_VERIFICATION.md).
