# Hybrid AI and credit Spot integration corrections

## Implemented and checked

- `live/domain.py`: explicit MAIN_SPOT/CREDIT_SPOT configuration. Credit requires
  a selector, separate key-scope and routing review references, and FREE semantics.
  References represent operator-reviewed evidence, not exchange introspection.
- `live/transport.py`: validates private headers and forwards the configured selector
  consistently. Credit wallet uses `/v1/account/balances-detail`, available/free,
  freeze/reserved, and verifies available + freeze = total. Account discovery rejects
  inactive/suspended/non-prop contexts. Normal mutation callback remains mandatory.
- `live/execution.py`: config/grant account type and selector must agree. Context
  checks run at initialization and reconciliation; account binding includes selector.
  Existing risk, precision, ownership, fee, balance, freshness and ambiguity gates
  still apply. No `.env` is implicitly converted into a LIVE grant.
- `ai/runtime.py`: builds the shared hybrid evaluator from a verified artifact and
  a dedicated analyst token. Replay is the default. No exchange transport/credential
  is given to the analyst. Feature/strategy identity checks are preserved.
- `live/service.py`: explicit hybrid mode requires an evaluator; no silent quant-only
  fallback. Research-only artifacts are rejected for protected LIVE. AI evaluates
  the same canonical signal/snapshot, can veto entries only and is audited. The
  execution boundary still checks risk/freshness before mutation.
- `ai/analyst.py`: BoxAPI's documented base URL maps to its Chat Completions route,
  using model/messages/stream=false and extracting a completed text choice. Other
  providers retain the private JSON gateway contract. Truncated, tool-calling or
  malformed responses fail closed; strict analyst schema/context validation remains.
- `ai/preflight.py`: optional one-call connection check and artifact-load check;
  reports no tokens, raw error bodies or account payloads, and exits nonzero on failure.

Official BoxAPI contract: https://boxapi.ir/docs/ai/

## Real read-only / LLM observations

The new adapter successfully verified active selected prop context and credit wallet
schema with authenticated GETs. This does not prove ownership of the key or order
routing. No exchange submission, cancellation or withdrawal was performed.
Report: `data/readiness/credit-adapter-read.json`.

The earlier 404 was caused by treating the BoxAPI base URL as a complete private
JSON gateway endpoint. After the documented protocol correction, a real connection
request returned valid JSON (`SCHEMA_VERIFIED`) using the configured model. It sent
only a connection-check prompt and dedicated LLM token, never Wallex credentials.
Report: `data/readiness/boxapi-connection.json`. This is not a historical trading
evaluation or proof all future analyst prompts/calls succeed.

```powershell
.venv\Scripts\python.exe -m quantpilot.ai.preflight --call-llm --report data/readiness/boxapi-connection.json
```

Equivalent manual PowerShell LLM connection request (uses existing private env token):

```powershell
'{"model":"gpt-5.6-luna","messages":[{"role":"user","content":"Reply with OK."}],"stream":false}' | Set-Content -Encoding ascii llm-request.json
curl.exe "https://ai.boxapi.ir/ai/v1/chat/completions" --header "Authorization: Bearer $env:QUANTPILOT_LLM_TOKEN" --header "Content-Type: application/json" --data-binary "@llm-request.json"
```

PowerShell does not automatically read `.env`. Do not paste tokens into commands,
chat or reports. Rotate credentials disclosed in chat before practical deployment.

## Models: fixed compatibility is not production validation

Old immutable artifacts were not edited or rehashed. A fresh seeded synthetic
dataset was generated and trained using the current code, with chronological
splits/calibration/walk-forward evaluation. A new artifact loads successfully:
`artifacts/ai-fixed-current/models/9005d839bc93f185025386cbb4b3b30ac4dec2d5f6a2b069149ee16f7ed06cb7`.
It remains RESEARCH_FROZEN, live_enabled=false, and belongs to the synthetic demo's
short-window research parameters, not the baseline 50/200 EMA strategy. It cannot
be substituted for the baseline model or promoted merely because it now loads.
Its A/B/C evaluation uses recorded synthetic analyst responses, not real historical
LLM calls. Compatibility report: `data/readiness/rebuilt-models.json`.

Real training was attempted with the unchanged 2,013-candle baseline input. Dataset
construction found 2,005 non-BUY decisions, eight risk-rejected BUY signals and
ZERO eligible labeled samples. The normal trainer rejected insufficient data;
no fake real-market model was produced and no risk threshold was weakened.
Reports: `data/readiness/real-ai-dataset.json`, `real-training-status.json`.

## Deployment preparation

`config/live-credit.example.json` is disabled and contains placeholders, not an
activation grant. Market precision/minimums/fees are research examples and must
be independently verified for the selected account before any live release.

An optional separate SHADOW hybrid image/Compose is prepared:
`Dockerfile.shadow-ai`, `compose.shadow-ai.yaml`, `config/shadow-ai.deploy.json`.
It installs the existing AI extras, mounts models read-only and reads only the
LLM settings secret, without any Wallex trading credential. A compatible BASELINE
artifact must first be placed at `artifacts/deployment-models/baseline` and a new
dedicated LLM token configured privately in `config/llm.server.env` (ignored by git).
Use `config/llm.server.env.example` as the template. Both files are excluded from
image build context by the existing allowlist, except the public JSON config.

Do NOT place the synthetic demo artifact there: the strategy identity is different.
Until the baseline artifact exists, startup correctly fails rather than faking ML.
On Ubuntu, after these prerequisites:

```bash
docker compose -f compose.shadow-ai.yaml up -d --build
docker compose -f compose.shadow-ai.yaml logs --tail=100 -f shadow-ai
```

The separate volume preserves the original quant-only SHADOW session. The hybrid
service remains virtual-only and LLM calls can incur provider costs. Docker build,
Ubuntu runtime and artifact/library compatibility in the image are not verified on
this Windows host. Preserve exact dependency/source versions with each artifact.

## Verification and remaining external prerequisites

- Python suite: **339 passed, 1 skipped** (optional PostgreSQL).
- Ruff passed; mypy passed for 81 source files.
- Tests cover credit context/grant mismatches, balances/reservations, mock submission,
  header isolation, hybrid veto/abstention, missing evaluator/research model rejection,
  BoxAPI wire format, truncation/tools/nontext failures, and existing execution safety.
- Real exchange mutation calls: ZERO. LIVE activation: NONE.

Not fixed by a configuration switch: baseline data sufficiency, independently
reviewed credit key ownership/order routing, validated model promotion and real
strategy profitability. LIVE remains disabled while these prerequisites are unmet.
Do not fabricate review evidence or bypass source/artifact checks. New source hashes
invalidate prior journal/artifact pins; preserve old evidence and start fresh sessions.
