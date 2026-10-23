# Credit account diagnosis and observed access

## Repeatable command

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe --diagnose --file-only --report data/wallex/credit-diagnostic.json
```

`--file-only` reads the selected .env without process environment overrides. Credentials
are never CLI arguments. The diagnostic saves sanitized statuses/booleans, not IDs,
keys, raw error bodies, wallet dumps or package records. A partial result intentionally
returns exit code 1; that does not mean every read failed.

## Account discovery

GET /sub-accounts is parsed against the documented array and explicit active/unsuspended
prop flags. A configured ID must occur in that eligible list. Without a configured ID,
only one unambiguous eligible account can be used in memory. Multiple, suspended,
unknown, malformed, duplicate or incompletely paginated results stop selection.
The selector is never guessed and a different configured account is never overwritten.

In the live read-only diagnosis, exactly one active prop account was returned and its
clientId matched the configured local ID. The ID itself is not included in this report.

## Observed endpoint results

| Read operation | Context | HTTP result |
| --- | --- | --- |
| GET /sub-accounts | Key only | 200, success=true |
| GET /v1/account/balances-detail | Selected credit ID | 200, success=true |
| GET /v1/account/balances | Key only | 200, success=true |
| GET /v1/account/fee | Selected credit ID | 200, success=true |
| GET /v1/account/openOrders | Selected credit ID | 200, success=true |
| GET /v1/prop/user/packages/active | Selected credit ID | 401 |
| GET /v1/prop/user/packages/overview | Key only, documented fallback | 401 |

Credit TMN available/freeze/total fields were valid and internally consistent. Free funds
covered the configured 500,000 TMN order ceiling. Key-only and selected-wallet values
were equal in this observation; equality is not proof that a key belongs to that account.
No identity, order routing or trading-permission grant is inferred from it.

The MCP follow-up separately reported:

- Initialization/connection completed.
- wallex_credit_active_sub_accounts_list: REPORTED_SUCCESS.
- wallex_credit_sub_account_balances_details: REPORTED_SUCCESS.
- wallex_credit_active_user_package_details: HTTP 401.

Therefore a generic READ_FAILED is not evidence that the entire MCP connection or credit
wallet access is broken. Both REST and MCP can read the credit wallet. The failing area
is package metadata access, reproduced independently through REST. The precise upstream
permission/account-scope reason is not exposed by these status codes. We did not replace
keys, invent headers, create a package, borrow funds or bypass authorization.

## Bounded recovery

Only seven fixed documented GET endpoints are callable by the matrix. A 429/502/503/504
may be retried once after a short bounded delay. A longer Retry-After is deferred, not
ignored. 401/403 are never retried. Redirects, proxies and arbitrary targets are disabled.
The package overview fallback is accepted only for an exact selected-account ID match;
metadata from another account cannot make the connection look ready.

When package metadata is still inaccessible, the status remains PARTIAL_READ_ACCESS.
The usable wallet path remains available through --rest --sub-account-context. No order
or execution adapter is injected into diagnostics, and LIVE remains off. Existing protected
execution is MAIN_SPOT-only; this debug step does not enable credit-account trading.

## Credential handling

The operator pasted a key into chat. It is not reproduced in source, logs, fixtures or
reports. Revoke/replace that disclosed credential in the Wallex panel, placing the new
account-specific key only in the ignored local .env. No automatic credential revocation
or replacement was performed by this diagnostic.

## Verification

30 offline MockTransport tests passed before the final full-suite run. They cover explicit
account selection, wrong/multiple/suspended accounts, partial pagination, malformed wallets,
no-negative/finite Decimal parsing, strict GET-only requests, context isolation, selector
matching in fallbacks, non-retryable 401, redirects, bounded 503 retry, Retry-After handling,
credential masking and the distinction between balance equality and key ownership.

Full-suite final result is recorded in the final report below. All fixtures use fake keys;
real credentials were used only for the explicitly authorized read-only diagnosis.
Source/config journal compatibility rules continue to apply.

### Final verification result

- Full Python suite: **298 passed, 1 skipped** in 49.35 seconds.
- Skip: optional PostgreSQL integration test requiring explicit isolated-server opt-in.
- Ruff: all checks passed.
- mypy: no issues in 75 source files.
- Real read-only endpoint observations are separate from the offline mock tests.
- Exchange mutations: zero. LIVE activation: none.

## Sanitized authentication-error diagnosis (2026-10-23)

The diagnostic now retains only bounded, allowlisted authentication messages and
numeric error codes. Arbitrary response text, HTML, credentials, account identifiers,
URLs and authentication realms are omitted. Error payloads are not dumped.

Run from the repository root:

```powershell
.venv\Scripts\python.exe -m quantpilot.live.credit_probe --diagnose --file-only --report data/wallex/credit-diagnostic.json
```

The repeated authorized read-only run returned HTTP 401 with server code `1201`
and the generic Persian message meaning "Please log in first" for both
`/v1/prop/user/packages/active` and `/v1/prop/user/packages/overview`.
Account discovery, credit wallet, key wallet, fees and open-order reads returned
HTTP 200 with reported success. This isolates the observed failure to package
metadata authentication; it does not establish whether its cause is route-specific
authentication, account scope or permissions. Wallet equality does not prove key
ownership or trading authorization. A browser error at the API root is not evidence
that these successful authenticated endpoints are unavailable.

For upstream support, supply the two endpoint paths, HTTP status, error code,
sanitized generic message and request time. Ask whether these package endpoints
support API-key authentication for the selected competition account and which
permissions are required. Never send the API key, cookies or full account payloads.
Do not bypass the check or activate LIVE to test authentication.

Verification of this update: 40 offline diagnostic tests passed; Ruff passed;
mypy passed for 75 source files. The 298-test full-suite result above predates this
update. The repeated network diagnosis submitted zero mutations and left LIVE off.
