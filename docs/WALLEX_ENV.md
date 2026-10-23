# Wallex connection environment

There are five settings (three public URLs, an API key and an optional sub-account ID):

| Setting | Value / role |
| --- | --- |
| WALLEX_API_BASE | https://api.wallex.ir |
| WALLEX_WS_URL | wss://api.wallex.ir/connection/websocket |
| WALLEX_MCP_URL | https://api.wallex.ir/mcp |
| WALLEX_API_KEY | Secret API key created for the intended account |
| WALLEX_SUB_ACCOUNT_CLIENT_ID | Private account selector, locally configured for credit/prop reads |

The official endpoints are fixed and validated; credentials are never sent to a configurable
third-party host. `MCP_URL` remains a compatibility alias; `WALLEX_MCP_URL` is canonical.
The local ID supplied by the operator was added only to ignored `.env`; the example is blank.
Existing nonempty settings and API key values were preserved. No key was generated/replaced.

## Implemented wiring

`quantpilot.live.settings.load_wallex_settings()` reads only the five allowlisted names plus
MCP_URL, with process settings taking precedence over file settings. Canonical process MCP
name wins over the process alias, then file canonical, then file alias. Parsing is literal:
no interpolation, global dotenv injection or shell evaluation. Duplicate settings, unsafe
header characters, malformed IDs and nonofficial endpoints fail closed with sanitized errors.
Key/ID fields are excluded from repr and serialization.

The read-only credit probe uses that loader. To explicitly send account context:

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe --include-details --sub-account-context
```

Without `--sub-account-context`, the probe sends only X-API-Key. With it, a nonempty
configured ID is required and sent as `sub-account-client-id`. Sending an HTTP header to
MCP does not itself verify that MCP forwards it to the downstream API.

Legacy backend Settings accepts all five names and the alias. `WallexMCP(settings,
sub_account_context=True)` explicitly enables the same read-only header context; its default
remains key-only. Legacy mutation tools stay blocked. The protected MAIN_SPOT transport
and activation/authorization variables are unchanged; these generic settings do not
activate LIVE or add credit execution support.

The API/WS values are connection metadata and fixed endpoint validation. This change does
not migrate every public market-data adapter or start a WebSocket/private streaming service.
The dashboard and LLM do not load these private settings.

## Key ownership and the operator's routing report

Official [key creation](https://developers.wallex.ir/docs/create-api-key) and
[spot introduction](https://developers.wallex.ir/docs/spot-intro) distinguish keys for
main and credit accounts; the spot introduction also specifies the credit selector header.
The operator reports that main-key order routing remained on the key's account despite
successful contextual reads. That report was not reproduced by placing an order here.
Neither the presence of a selector nor a successful wallet read proves order routing.

**Comparing TMN balances is not an identity check.** Different accounts can have equal
balances; the same account's balance can change between reads. The repository did not
contain the claimed `api_key_matches_sub_account` preflight. The diagnostic now explicitly
reports `api_key_matches_sub_account: "UNVERIFIED"`; it never grants trading access from
balance equality. Account-bound key/permission evidence and reconciliation remain required.

## Verification for this change

Ruff and mypy static checks were run; no unit tests, real provider requests or exchange
mutations were performed for this settings change. No production dependencies were added.
Source-pinned journal identities change with packaged code; preserve original-source
replay/new-session migration rules rather than rewriting stored hashes.

## Isolating MCP versus REST authorization errors

Read the selected credit wallet directly, bypassing MCP:

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe --rest --sub-account-context
```

This uses exactly GET `/v1/account/balances-detail` with the configured key and selector.
Without account context, REST mode uses the documented `/v1/account/balances` instead;
it does not assert that this wallet is the competition account. There are no arbitrary
URLs, redirects, retries or exchange mutation methods in this diagnostic.

Observed in the debugging session: the selected-wallet REST read returned HTTP 200 and
`success: true`. A parallel MCP diagnostic failed with 401 at
`MCP_CALL:wallex_credit_active_user_package_details`. The earlier generic READ_FAILED did
not identify that stage and must not be interpreted as proof the key is invalid.
MCP forwarding, account identity/key ownership and trading permissions remain unverified.

Failed MCP reports now include `failed_stage`, whether initialization completed, and
sanitized statuses of completed read tools. No account contents or error bodies are exposed.
Ruff/mypy were run; no unit tests or exchange mutations were performed for this debug step.

## Automated read-only diagnosis

Use `--diagnose --file-only` to discover and match the sub-account directly through the
API, then check wallet, fees, open-order reads and the documented package metadata paths.
`--report data/wallex/credit-diagnostic.json` writes a sanitized local report.
No order methods are available. The final observed state is partial package-metadata
access, with credit wallet reads working through both REST and MCP. See
[diagnostic findings](CREDIT_DIAGNOSTICS.md).
