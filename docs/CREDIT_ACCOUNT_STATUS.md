> **Automated read-only diagnosis:** the API-discovered active prop ID matches local
> configuration. Credit wallet reads work through both REST and MCP; fees/open-order
> reads work through REST. Both active-package and package-overview REST reads return
> 401, and the MCP package tool also fails. This is partial package-metadata access,
> not a blanket failed connection. No trading identity/permission grant was inferred.
> See [the complete diagnostic findings](CREDIT_DIAGNOSTICS.md).

> **Latest read-only diagnostic:** direct REST credit-wallet GET returned HTTP 200
> with `success: true`, using the configured sub-account context. MCP failed at the
> active-package-details tool with HTTP 401. Earlier blanket connection-failure wording
> is superseded by this stage-specific result. Read access is confirmed for that wallet
> request; account/key identity, trading permission and order routing remain unverified.
> See [REST diagnostics](WALLEX_ENV.md#isolating-mcp-versus-rest-authorization-errors).

> **New documentary evidence from the full /docs crawl:** official spot introduction
> requires the credit account's own API key and `sub-account-client-id`. Credit Swagger
> also declares that selector for wallet/package reads. The earlier statement that no
> selector contract was found is superseded by this evidence. Current key identity,
> successful selected-account access and MCP header forwarding remain unverified;
> no execution was enabled. See [findings](wallex-reference/FINDINGS_FA.md).

# Competition credit account connection status

## Confirmed operator scope

- Existing competition credit account only, SPOT / LONG_ONLY.
- Capital ceiling: 5,000,000 TMN; per-order ceiling: 500,000 TMN.
- Only BTC/TMN, subject to the package-specific current market approval.
- Deadline: end of 26 October 2026 in Asia/Tehran, represented as
  `2026-10-26T23:59:59+03:30` (20:29:59 UTC).
- Five-minute liquidation lead is a proposed local default, not a verified exchange rule.
- No new loans, package activation, wallet transfers, withdrawals or margin operations.

An ignored local intent is saved at `config/live-credit-intent.local.json`.
It is deliberately not a runnable MAIN_SPOT LiveConfig or an AccountAuthorization grant.
Existing MAIN_SPOT protections are unchanged. Do not change the account type label to
make a credit account pass MAIN_SPOT validation.

## Verified private read

Command (run locally with an existing key; does not accept arbitrary tool names):

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe
```

The command reads only WALLEX_API_KEY from the local environment or selected `.env`,
uses the fixed official `https://api.wallex.ir/mcp` host, verifies tools/list metadata and
schema, and calls only `wallex_credit_active_sub_accounts_list` with `{}`. It never
loads the key into a global dotenv context or gives it to the LLM. No raw account response,
identifier, balance, credential or exception body is printed or persisted.

Observed result on 2026-10-23: MCP connected; the account-list tool reported success.
The sandbox attempt encountered a connection error; the same authorized read succeeded
outside the network restriction. No exchange trading mutation was attempted. Account-list
success alone does not prove an active competition account, trade permission, balance
ownership or account-specific order routing. Those verification flags remain false.

## Remaining blocker

The verified account-list tool takes no account-selector argument. Existing spot order
schemas do not document a competition-credit account selector. The supported protected
adapter currently queries main-account balances, which official documentation explicitly
separates from credit wallets. A successful public or main-account call cannot be used as
proof of credit routing.

Required before implementing credit execution: an official contract for account-bound
credentials or an explicit selector/header/context applying consistently to balance,
submission, cancellation, open orders, per-client-ID status and fill queries. Also verify
package-specific eligible markets, available/locked balance semantics and key permissions.
Do not guess a header, activate a package, transfer assets or submit a trial order.

Official documentary references:

- https://developers.wallex.ir/basicservices/mainaccountwallet
- https://developers.wallex.ir/trade-credit/proppackagedetails
- Existing supplied MCP setup: `wallex-mcp-setup-fa.md` documents X-API-Key authentication,
  but supplies no credit account selection contract.

The next input needed from Wallex/competition organizers is the official **spot order
routing instructions for the funded competition credit account**. No additional budget
confirmation is needed; the operator already supplied it.

## Verification limits

Ruff and mypy were used for static checks. The authenticated read above is connection
evidence, not automated order-lifecycle coverage or certification of credit execution.
No tests or real orders were added/run for this connection step. The previous 268-test
result predates this new read-only command and is not reported as a fresh suite result.
Existing source-pinned journals/artifacts must retain their original implementation identity.
LIVE remains disabled while the credit routing contract is unresolved.

## Follow-up: account count and expanded read status

A fresh read-only listing returned an explicit result array with **one** credit account.
Only the count was exposed; no account identifiers or balance dumps were printed.
The diagnostic now supports:

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe --include-details
```

This adds only the discovered, schema-validated read tools
`wallex_credit_sub_account_balances_details` and
`wallex_credit_active_user_package_details` to the constant read-only allowlist.
No caller-supplied tool name or mutation can be invoked. The command reports statuses,
not account balances. It does not upgrade identity, permission or routing evidence from
an API success flag alone.

The expanded check failed; the final sanitized diagnostic reported **HTTP 401**.
No conclusion is drawn about which key permission, account-selection context or MCP
session requirement caused it. A prior successful account list does not establish access
to the required credit wallet/package operations. Do not label the entire account
integration healthy or activate trading from the successful list alone.

The locally stored intent now includes the fixed official API base
`https://api.wallex.ir` and MCP endpoint `https://api.wallex.ir/mcp`.
Budget/deadline/market authorization is unchanged and does not need reconfirmation.
Next required external evidence: account-scoped authentication/selection instructions
and the credit spot order/status/cancel contracts from Wallex or the competition organizer.

Ruff passed and mypy passed for 73 source files after these changes. No automated test
suite was run in this follow-up, and no exchange order, cancellation, transfer or package
activation was submitted. The earlier full-suite count is historical, not a fresh result.

## Explicit environment/account context wiring

The five WALLEX_* connection settings and --sub-account-context are now supported by the
read-only diagnostic. The operator-supplied ID is stored only in ignored .env. Existing
key values were preserved. MCP selector forwarding and key/order-account binding remain
unverified; balance equality is not used as proof. See [environment setup](WALLEX_ENV.md).
No LIVE activation, credit order submission, or fresh private network probe was performed
in this settings step.
