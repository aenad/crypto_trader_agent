# Phase 2 — public Wallex data collection

Scope approved by user: MCP discovery, public REST/WebSocket adapters, validation,
collectors and Parquet/PostgreSQL persistence. This replaces the earlier plan's
Phase 2 strategy scope. No strategy, AI, financial execution or order submission
was added. Phase 1 ports/models and the legacy application remain intact.

## Install and run

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,marketdata]"
quantpilot-data discover
quantpilot-data scan --source mcp --whitelist config/markets.example.json
```

`discover` initializes https://api.wallex.ir/mcp, handles tools/list pagination,
and saves tool names/descriptions/JSON schemas with a verification timestamp to
data/marketdata/tools.json. The four callable operations are a fixed public-only
allowlist validated against current server schemas; the full catalog does not give
permission to execute other tools. No account keys are loaded or sent.

The example whitelist contains BTC/USDT only. Copy/edit it with the actual organizer
approved canonical symbols; inclusion in an example is not organizer approval.
The scanner intersects that file with returned spot markets and the 344 exclusions.
TMN is Toman; IRR is not silently treated as TMN. Phase 2 rejects unsupported quotes.

### Offline demonstration (no PostgreSQL required)

```powershell
quantpilot-data collect --source mock --whitelist config/markets.example.json --local-metadata --output data/offline-demo
```

This produces 30 synthetic closed candles in Parquet and explicitly local JSON
catalog metadata. The mock is not an exchange or a trading simulator. Without
--local-metadata, PostgreSQL is mandatory; there is no silent fallback.

### PostgreSQL storage

```powershell
docker compose --profile marketdata up -d postgres
$env:QUANTPILOT_POSTGRES_DSN = "postgresql://quantpilot:local-development-only@127.0.0.1:5432/quantpilot"
quantpilot-data collect --source mcp --whitelist config/markets.example.json --resolution 1 --bars 30
quantpilot-data collect --source rest --whitelist config/markets.example.json --kind book
quantpilot-data collect --source rest --whitelist config/markets.example.json --kind trades
```

Compose's password is a local development default, not a production credential.
Set QUANTPILOT_DB_PASSWORD for other deployments and match the process DSN. Avoid
printing DSNs. The CLI intentionally does not read the legacy .env. PostgreSQL
binds only to localhost in Compose. Do not use a production trading database for tests.

Container alternative: `docker compose --profile marketdata run --rm marketdata`.
Dockerfile.marketdata installs only the shared package plus marketdata dependencies;
no legacy backend, exchange API key or .env is copied. Docker was unavailable in
the agent environment; Compose/image execution has not been verified.

### History and streaming

```powershell
quantpilot-data collect --source rest --whitelist config/markets.example.json --start 2026-10-22T10:00:00Z --end 2026-10-22T11:00:00Z --resolution 1
quantpilot-data stream --source rest --whitelist config/markets.example.json --channel trade --duration 60 --events 10
quantpilot-data stream --source rest --whitelist config/markets.example.json --channel buyDepth --duration 60 --events 10
quantpilot-data stream --source rest --whitelist config/markets.example.json --channel 1m --resolution 1 --duration 60
```

HistoricalDataLoader/CandleCollector request bounded chunks and require complete
coverage before returning a valid history batch. `from` is inclusive and `to` is
one second before the exclusive range end. All ranges align to requested intervals.
Invalid symbols/quotes, duplicate/unordered timestamps, OHLC violations, incomplete
candles, missing bars and resolution mismatch cause rejection; no forward fill.
Collectors expose typed Candle/Trade/Book/Market results. CandleCollector implements
the Phase 1 MarketDataProvider snapshot port. It does not change the Phase 1 engine.

Stream uses documented Centrifugo raw JSON connect/subscribe acknowledgements,
application `{}` ping/pong, bounded reconnect/backoff, server limit error 106,
subscription checks, duplicate detection and time ordering. NDJSON frames supported.
The public WebSocket path is /connection/websocket, not legacy /ws. Channels:
public:SYMBOL@trade; orderbook:SYMBOL@buyDepth and @sellDepth; candle:SYMBOL@1m,
@1h and @1d only. Candle stream channel/resolution must match. Unknown channels
are rejected instead of inferred. Protocol errors fail closed; transient disconnects
retry up to four times. REST uses Retry-After for 429, retries transport/5xx failures,
and conservative 250-ms local pacing. This is not a claim about Wallex's rate limit.
MCP reconnects and rediscovers schemas on retried transport/rate-limit failures;
application tool errors are not silently retried. Only public reads can be retried.

## Data semantics and limitations

- Latest trades are recent executed trades, not guaranteed executable quotes or an
  exhaustive trade tape. They are sorted by exchange time; the latest must be within
  180 seconds by default. Illiquid markets may be rejected as stale. Content hashes
  deduplicate identical timestamp/price/size/side tuples because verified responses
  contain no unique trade ID; indistinguishable real trades may collapse. Do not use
  this feed as exact venue-volume accounting without an exchange identity contract.
- Depth REST responses and streamed sides lack exchange timestamps/verified sequence
  continuity. They are observation-time data, not freshness-proven matching-engine
  snapshots. Sides remain separate stream events and are never merged across epochs.
- Reconnects mark a new epoch with possible gaps. History is refreshed using the
  selected source, but missing historical trades/books cannot be recovered from OHLCV.
  Offset replay/exactly-once streaming is not claimed. Session dedup is bounded at
  10,000 events; reaching it fails explicitly rather than silently losing coverage.
- Open candle updates are stored only as stream observations with
  candle_complete=false, never as closed historical candles. Initial/reconnect history
  is loaded separately. Current candle updates can repeat timestamps; updates are not
  duplicate closed bars. A final sealed candle still requires a history refresh.
- Current source validation uses the collection's explicit as-of cutoff. A source
  event later than that cutoff fails; the next collection can retry with a fresh time.
- Live read verification found a 15-minute MCP request returning one-minute-spaced
  timestamps. Such data is rejected as resolution mismatch. One-minute REST and MCP
  collection passed. Other documented resolutions remain subject to validation and
  have not all been live-tested. The old backend's permissive parser is unchanged.
- Historical order-book endpoints and exhaustive historical trade pagination were not
  established in the official sources. Neither is implemented or fabricated.
- All prices and quantities normalize to Decimal. REST and MCP JSON text is parsed
  with Decimal. SDK structured-only numeric fallback preserves only exposed digits;
  original decimal precision cannot be recovered after a float conversion.

## Storage format and integrity

Parquet partitions: kind / BASE_QUOTE / content-addressed-dataset.parquet.
Columns: event_id, symbol and payload_json (versioned typed event JSON with exact
decimal strings/timestamps). This deliberately preserves nested book/stream records
without lossy Arrow float inference; it is not yet an analytical flattened schema.
Metadata includes kind, pair, path, row count, SHA-256, schema version and provenance.
PostgreSQL table quantpilot_datasets has dataset_id primary key and JSONB manifest.
Repeated identical batches register once. Duplicate IDs inside a batch are collapsed
only if identical; conflicting payloads fail. Overlapping historical batches may
contain the same event IDs and require event-ID deduplication when building a dataset;
files are observation artifacts, not an already globally unique analytical table.

Parquet files are fsynced to a temporary file then atomically renamed before catalog
registration. Catalog failure propagates; the CLI does not report success. An orphan
file may remain for retry/recovery. File/catalog writes are not a distributed transaction.
No existing dataset/database is deleted, and PostgreSQL inserts are additive/idempotent.
Paths are local storage references; shared deployment needs common mounts/object storage.

## Verification and evidence

Official documentation snapshots and publicly fetched response fixtures are under
docs/evidence. They contain public market data, not account information. tools/list
returned 52 tools. Sources: https://api.wallex.ir/llm.txt and
https://developers.wallex.ir/docs/basic-services-candles,
/basic-services-depth, /basic-services-latest-trades, /spot-active-markets,
/socket-raw-protocol, /socket-connection, /socket-migration and candle/trade/depth pages.

Public smoke tests: five validated one-minute candles stored via REST, five via MCP,
and one actual buyDepth stream event stored in Parquet. Offline mock collection stored
30 candles. No key, account tool or order was used.

Local tests include real Parquet roundtrip and an opt-in isolated PostgreSQL cluster,
schema validation, symbol/quote/whitelist, gaps/order/duplicates/OHLC, incomplete bars,
freshness, rate-limit retries, stream ack/heartbeat/disconnect/recovery and storage
failure. The database test creates its own cluster/temp port and never targets an
existing database. On Windows this requires permission for initdb restricted-token
handling. Run:

```powershell
python -m pytest -q
$env:QUANTPILOT_RUN_POSTGRES_TEST = "1"
python -m pytest -q
python -m ruff check src/quantpilot tests
python -m mypy
```

No strategy/AI/trading phases are started by this data collection tool.

Final verification: **30 tests passed** with the temporary PostgreSQL test enabled
(5.93 seconds). Default run: 29 passed, 1 explicitly skipped PostgreSQL test.
Ruff passed; strict mypy passed for 16 source files (third-party untyped Arrow and
JSON Schema libraries are explicitly excluded from stub analysis). Editable package
installation and installed quantpilot-data/quantpilot-demo commands passed. The
Phase 1 demo retained its deterministic decision ID and still submits nothing.
