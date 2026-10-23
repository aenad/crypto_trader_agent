# Wallex integration: observed contracts and unverified capabilities

Phase 7 adds a protected private **REST** adapter, separately authorized and isolated
from public MCP/SHADOW and the LLM. See [execution contracts and limitations](phase7.md)
and [documentation evidence](evidence/wallex-live-contracts.json). Private account/order
behavior has been checked with offline mocks only. Main-account APIs are not evidence
of competition credit routing. No private MCP order tool is automatically enabled.
The default LIVE prohibition and explicit account/deployment prerequisites remain.

Phase 2 update: official documentation and public calls have now been verified.
See [Phase 2 contracts, CLI and evidence](phase2.md). The content below retains the
Phase 0 audit history and must not override the newer verification record.

Phase 0: no network requests or orders performed. Authority: ../SPEC.md.

## Evidence

- Local code: backend/mcp_client.py supports Streamable HTTP and stdio, initializes sessions and reads structuredContent or JSON text. Sessions are opened for each operation.
- User-provided setup guide: public tools need no API key; private tools use X-API-Key. Current code implements this using SecretStr for WALLEX_API_KEY. Generic bearer setting remains plain str.
- User-provided runtime: health mcp_connected=true; tool inventory; successful BTCUSDT latestTrades response; valid baseline HOLD signal. These demonstrate those narrow calls at that time, not all tools or present connectivity.
- Local audit: fake MCP contract mapping and synthetic LangGraph run; no private account data fetched. Credentials were not read or printed.

## Current explicit read-only roles

| Role | Tool | Arguments / caveat |
|---|---|---|
| markets | wallex_spot_get_markets | {}; unwraps result/symbols/markets/data; account permission is not established |
| ticker | wallex_basic_get_latest_trades | symbol: BTCUSDT; recent trades, not an executable quote |
| candles | wallex_basic_candle_history | symbol, resolution, from, to (Unix seconds) |
| balance | wallex_basic_get_account_balances | {}; private access and competition-account correctness unverified |
| orders | wallex_spot_get_orders | optional filters; read-only, not submit |

Canonical pair BTC/USDT converts to BTCUSDT. Supported interval translations are 1m/5m/15m/30m/1h/4h/1d to 1/5/15/30/60/240/D. Request end is one second before current interval boundary; start is boundary minus count*interval. Adapter does not independently verify returned candle timestamps/completeness. Columnar t/o/h/l/c/v responses are accepted by strategy; row formats also accepted. Mixed schemas, duplicate events and stale data still need stronger validation.

## Exposed application routes

GET /api/health (calls tools/list), /api/mcp/tools, /api/markets, /api/ticker/{symbol}, /api/signals, /api/signals/{symbol}, /api/balance, /api/account/summary. POST /api/orders rejects in shadow and returns 501 in live; it does not call exchange submission. Memory routes read/store local data.

## Submission contract supplied by user, not implemented

Tool wallex_spot_post_account_orders was listed with string fields client_id, price, quantity, side, stop_Price, symbol, type; side/symbol/type required. Inventory does not establish exact market-buy quantity units, quote-budget support, rounding, partial-fill behavior or credit-account routing. Tool description requires explicit confirmation. Do not infer these semantics or submit a probe order. No exchange sandbox was established.

User inventory also lists public depth, spot open-order/client lookup and fees tools. These are potential read adapters, not currently implemented capabilities. Margin, OTC, transfer, banking and prop activation/cancellation tools must stay outside the approved trading toolset.

## REST and WebSocket

No direct Wallex market REST client or WebSocket subscriber exists in the application. HTTPX as MCP transport dependency and HTTP FastAPI routes do not constitute either integration. Verify official endpoints, schemas, credentials, sequencing/gap recovery and rate limits before future implementation. For now the supplied MCP tool inventory is the only available detailed contract; no exchange feature is inferred from generic API naming.

## Required integration checks before LIVE

Confirm account/subaccount identity, authenticated read access, current permissions/universe, fees/units, market minimums/steps, order types/protection semantics and client-ID idempotency. Capture redacted versioned fixtures for normalization and error behavior. Add timeout budgets, bounded reconnect/backoff, pagination and redacted nested exception diagnostics. Separate fresh event time from local received_at; reject stale data for execution.

## Spot-only verification amendment ? 2026-10-23

Official documentation checked through public web results (no authenticated calls):

- [Wallex API reference](https://api-docs.wallex.ir/): market metadata uses concatenated
  symbols, separate base/quote assets, minimum quantities/notional, and step/tick decimal
  counts. The balance example explicitly names TMN as Toman. Read the actual market
  metadata; do not hardcode the example precision or map an IRR response into TMN.
- [Active spot orders](https://developers.wallex.ir/spot/activeorders): documents active
  order queries and per-fill fee assets/cumulative quantities. Existing protected adapter
  remains conservative about response shape differences and ambiguous state.
- [Active market metadata](https://developers.wallex.ir/spot/activemarket): margin-related
  metadata can coexist with spot flags; its presence does not authorize margin execution.

This is documentary evidence, not verification of the user's account type, key permissions,
credit/competition routing, locked-balance semantics or current exchange payloads. IRR stays
a distinct unsupported execution quote; any future conversion needs an explicit reviewed
unit adapter. Protected LIVE still only permits direct-TMN spot LIMIT after independent
account/config authorization. MARKET and conditional LIVE semantics, credit routing,
borrowing, derivatives, margin, OTC execution and withdrawals remain blocked. The legacy
MCP client rejects all mutation tools even if tools/list returns their schemas. The packaged
MCP data adapter already verifies a fixed public read-only tool allowlist per session.

Backtest FX marks are valuation inputs. Final FX execution now additionally requires
`fx_market` metadata and fresh recorded USDT/TMN depth, with constrained simulated fills;
missing evidence leaves USDT explicitly unsettled. SHADOW uses its explicit FX route and
observed books. No real conversion or order was submitted during verification.

## Official /docs crawl ? 2026-10-23

The current canonical documentation was crawled from sitemap and internal links:
114 pages, no final page failures, plus five downloadable schemas. See
[combined technical reference](wallex-reference/WALLEX_REFERENCE.md),
[coverage](wallex-reference/manifest.json), and
[key findings](wallex-reference/FINDINGS_FA.md).

New documentary evidence resolves the previously missing REST selector: the official
spot introduction requires a credit-specific API key and `sub-account-client-id`.
The credit schema explicitly declares that header on balance/package reads. This
supersedes the earlier absence-of-contract finding, but does not establish the current
key's identity, successful selected-account access, or MCP forwarding semantics.
Cancellation alternatives and the legacy query adapter mismatch are recorded separately.
No production adapters, permissions, account credentials or LIVE gates changed in this crawl.
