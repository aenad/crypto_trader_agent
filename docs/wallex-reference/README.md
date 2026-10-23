# Wallex documentation reference

- [Combined technical reference](WALLEX_REFERENCE.md)
- [Coverage and failed URLs](manifest.json)
- [Structured technical facts](pages.json)
- [Unique documented HTTP operations](endpoints.json)

Public documentation only; no account data, credentials, API calls or trading.
Narrative text is not mirrored. Discovered scope and failures are explicit.

## Official Swagger contracts

- [Readable technical contracts](API_CONTRACTS.md)
- [Structured operations](api-contracts.json)
- [Schema coverage/errors](swagger-manifest.json)

## Reproduce the public crawl

```powershell
.venv\Scripts\python.exe tools/crawl_wallex_docs.py --output docs/wallex-reference-NEW
.venv\Scripts\python.exe tools/enrich_wallex_reference.py --root docs/wallex-reference-NEW
```

The HTML crawler uses the standard library. The enrichment tool additionally uses the
already installed PyYAML safe parser for the official credit YAML download. No project
production dependency was added. Use a new directory to preserve the current snapshot.
The HTML snapshot does not execute client-side JavaScript; API forms are supplemented
by downloadable schemas. Official prose, images and sample account values are not mirrored.

## Findings

[FINDINGS_FA.md](FINDINGS_FA.md)
