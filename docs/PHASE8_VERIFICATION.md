# Phase 8 verification — 2026-10-23

## Automated checks actually run

Host: Windows, existing Python 3.13 environment, Node v24.14.1. No real exchange
credentials were loaded and no exchange/private-account mutation or read was made.

| Command | Observed result |
| --- | --- |
| `python -m pytest -q --junitxml=data/phase8-check/tests.xml` | **231 passed, 1 skipped**, 42.40 seconds |
| `npm.cmd test` | **7 UI tests passed** |
| `npm.cmd run build` | Strict TypeScript check and Vite production build passed |
| `python -m ruff check src/quantpilot tests` | All checks passed |
| `python -m mypy` | Success, **69 source files** |

The single skipped test is the existing opt-in PostgreSQL integration check;
no PostgreSQL server was started. New dashboard Python coverage comprises 18 tests.
Existing strategy, risk, AI, backtest, SHADOW and protected execution tests passed.

## End-to-end checks

- Started the native FastAPI application on `127.0.0.1:18780` and Vite production
  preview on `127.0.0.1:18781`, using a dedicated synthetic verification reporting root.
- Through the frontend proxy, HTTP 200 was observed for the HTML page, service
  health, DEMO, a generated baseline backtest, a synthetic-core SHADOW session,
  and a Markdown competition report.
- Ran `quantpilot.dashboard.offline`: three fixture frames exercised the unchanged
  SHADOW/core machinery, creating a virtual account without network/provider calls.
- Ran the existing replay CLI: **MATCH**, three frames, one decision, all state and
  decision comparisons true; exchange mutations BLOCKED, LLM network calls **0**.
- Ran the existing backtest CLI against its explicitly synthetic input and projected
  its actual generated report. This establishes mechanics, not market profitability.
- Generated JSON/Markdown/CSV judge reports for the virtual session. All preserve
  simulation labels, source identity and provisional status.
- Captured and inspected the desktop UI in an isolated headless Edge profile.
- Used an actual emulated **390×844** viewport to verify the mobile layout:
  `innerWidth=390`, `clientWidth=390`, `body.scrollWidth=390`,
  `documentElement.scrollWidth=390` — no horizontal overflow.
- Browser automation opened the mobile navigation, selected Market Monitor and
  switched to the recorded BACKTEST source; the persistent source label updated
  to simulated historical backtest. This was additional to the DOM interaction tests.

Browser QA required a sandbox escalation because headless Edge initially failed
under Windows process/GPU restrictions. The successful checks used fresh isolated
profiles and localhost only, never the user's existing browser profile.

Local verification artifacts (ignored, not repository fixtures):

- `data/phase8-check/tests.xml`
- `data/phase8-check/dashboard.png`
- `data/phase8-check/dashboard-mobile.png`
- `data/phase8-check/replay.json`
- `data/phase8-check/judge-final/competition.{json,md,csv}`

## Coverage boundaries

Tests cover exact hand-calculated return/drawdown/win rate/daily changes; summary
percentage distrust; unavailable-versus-zero handling; typed credential-free
projection; read-only API/mutation rejection; invalid/future/unordered data;
active SHADOW versus export parity; stale state; corrupt checkpoints/databases;
linked analyst prompt/model versions; replay/comparison evidence labels; report
identity changes; offline core rehearsal; and report overwrite protection.

UI tests cover all eight sections, simulation labels, signal search/filtering,
orders/fills/rejections, downloads, source switching without stale metrics,
unavailable responses without demo substitution, provenance validation and
mobile navigation. They use simulated fixtures, not real performance.

## Docker and remaining limitations

Compose YAML was parsed and assertions checked UI/API services, localhost binding,
internal network and absence of `env_file` injection. **Docker is not installed on
this host. Image build, container startup, runtime file permissions and inter-container
networking are unverified.** Native app startup is verified; it is not a substitute
for Docker runtime verification.

No current Wallex MCP/WebSocket connection, private account response, real order,
real LLM provider, certified final liquidation or competition profitability was
verified in Phase 8. Such claims are deliberately absent from the dashboard.
Recorded health is not exchange uptime. LIVE initial capital/aggregate PnL/fees
are unavailable without a complete financial export; missing latency and unlinked
prompt versions are not guessed.

The dashboard is local and read-only, without multi-user authentication. Histories
and displayed rows are bounded; long initial reads may be slow. See
[Phase 8 architecture and limits](phase8.md) and the [README](../README.md).

LIVE remains disabled. Stop after Phase 8; no later phase was started.
