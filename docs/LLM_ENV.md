# LLM configuration from .env

`quantpilot.shadow.cli start` reads only the five dedicated LLM keys from `.env`
in the current working directory. Unrelated values, including Wallex credentials,
are not imported into the environment or passed to the analyst.

Priority: **process environment > .env > SHADOW JSON**. Empty non-secret values
leave JSON settings unchanged. An explicitly empty process token replaces a file
token. Quoted values and trailing comments are supported; values are literal,
without variable interpolation, shell execution or multiline strings.

| Environment key | Destination |
| --- | --- |
| `QUANTPILOT_LLM_TOKEN` | Dedicated provider token; never included in config/manifest output |
| `QUANTPILOT_LLM_GATEWAY` | `llm_gateway` |
| `QUANTPILOT_LLM_MODEL_ID` | `analyst_model_id` |
| `QUANTPILOT_LLM_TIMEOUT_SECONDS` | `llm_timeout_seconds`, 1–60 |
| `QUANTPILOT_LLM_CALL_BUDGET` | `llm_call_budget`, 1–10,000 |

The gateway must be HTTPS, without credentials/query/fragment in the URL, and
cannot target Wallex. It must implement the existing provider contract:
`POST {model, request, response_schema}` returning `{output: <JSON string>}`.
This is not automatically compatible with a vendor's Chat Completions endpoint.

### BoxAPI support

The documented BoxAPI base `https://ai.boxapi.ir/ai/v1` and full
`https://ai.boxapi.ir/ai/v1/chat/completions` now explicitly select the BoxAPI
Chat Completions wire format. This exception is limited to that exact hostname
and documented paths; other gateways retain the existing private JSON contract.
See https://boxapi.ir/docs/ai/ . The adapter sends model/messages/stream=false,
extracts the sole completed text choice and rejects truncation, tool calls and
nontext output. Analyst schema/context/time validation remains local and mandatory.
No exchange token/account state is sent to this provider.

Sanitized one-call connection check (may incur provider cost):

```powershell
.venv\Scripts\python.exe -m quantpilot.ai.preflight --call-llm --report data/readiness/boxapi-connection.json
```

`SCHEMA_VERIFIED` means this small connection request returned valid JSON. It does
not imply that historical analyst performance, every prompt or future calls work.
For artifact verification add `--model PATH_TO_FROZEN_MODEL`. Failures exit nonzero;
reports contain no tokens, provider error bodies or private URLs.

The SHADOW JSON must still specify `ai_mode: QUANT_ML_LLM`, a compatible frozen
LightGBM `model_path`, market approvals and risk settings. Environment variables
do not change mode or enable network access. Actual model calls additionally need
the explicit flag:

```powershell
.venv\Scripts\python.exe -m quantpilot.shadow.cli start --config shadow.json --env-file .env --db data/shadow/llm-env-session.sqlite --allow-llm-network
```

Use `--no-env-file` for process environment plus JSON only. Without
`--allow-llm-network`, the analyst uses recorded responses; the loaded token is not
passed to it. Replay/health/export commands do not read `.env` and keep recorded
configuration and analyst outcomes unchanged.

No actual LLM request or exchange order is made by configuring these settings.
The dashboard and legacy backend are not a SHADOW runner and do not gain LLM calls
from this change. Invalid settings fail with sanitized messages.

Changing SHADOW source or effective model/config settings can invalidate existing
journal version/config pins. Use a new session database; do not clear old journal
guards to bypass those checks. Historical source snapshots are required to replay
journals recorded with an older pinned implementation.
