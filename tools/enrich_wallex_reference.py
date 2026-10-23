"""Extract technical contracts from the official downloadable Swagger files."""

import argparse
import hashlib
import json
import urllib.parse
from pathlib import Path

from crawl_wallex_docs import Fetcher, HOST

REMOVE = {"description", "summary", "example", "examples", "x-codeSamples", "x-code-samples"}
MAPPING = {"properties", "definitions", "$defs", "schemas", "paths", "responses",
           "securitySchemes", "headers", "content", "requestBodies"}


def contract(value, names=False):
    if isinstance(value, list):
        return [contract(v) for v in value]
    if isinstance(value, dict):
        return {key: contract(item, key in MAPPING) for key, item in value.items()
                if names or key not in REMOVE}
    return value


def schema_lines(schema, prefix="", depth=0, document=None):
    if not isinstance(schema, dict) or depth > 8:
        return []
    result = []
    if "$ref" in schema:
        result.append(f"- `{prefix or '$'}` → `{schema['$ref']}`")
        ref = schema["$ref"]
        if document and ref.startswith("#/"):
            target = document
            for part in ref[2:].split("/"):
                target = target.get(part.replace("~1", "/").replace("~0", "~"), {})
            result += schema_lines(target, prefix, depth + 1, document)
        return result
    if schema.get("type") == "array":
        return schema_lines(schema.get("items", {}), prefix + "[]", depth + 1, document)
    required = schema.get("required", [])
    for name, child in schema.get("properties", {}).items():
        field = prefix + "." + name if prefix else name
        kind = child.get("type", "$ref" if "$ref" in child else "unspecified")
        enum = f"; enum={json.dumps(child['enum'], ensure_ascii=False)}" if "enum" in child else ""
        result.append(f"- `{field}`: `{kind}`; required={name in required}{enum}")
        result.extend(schema_lines(child, field, depth + 1, document))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("docs/wallex-reference"))
    parser.add_argument("--reuse-existing", action="store_true",
                        help="Reuse schemas with a successful record in the current manifest")
    args = parser.parse_args()
    root = args.root
    pages = json.loads((root / "pages.json").read_text(encoding="utf-8"))
    urls = sorted({u for p in pages for u in p["schema_download_links"]
                   if urllib.parse.urlsplit(u).hostname == HOST})
    out = root / "schemas"
    out.mkdir(exist_ok=True)
    fetch = Fetcher(0.5)
    report = {"assets_discovered": urls, "saved": [], "failures": []}
    previous = root / "swagger-manifest.json"
    prior = {entry["url"]: entry for entry in json.loads(previous.read_text(encoding="utf-8"))["saved"]} if previous.exists() else {}
    operations = []
    doc = ["# Official Swagger technical contracts", "",
           "Source schemas were read in full. Narrative descriptions and sample payload values",
           "are omitted; protocol fields, types, enums, required flags and references are retained.",
           "These contracts are documentary evidence, not runtime verification or trading permission.", ""]
    for url in urls:
        try:
            cached = prior.get(url)
            if args.reuse_existing and cached and (root / cached["file"]).is_file():
                spec = json.loads((root / cached["file"]).read_text(encoding="utf-8"))
                status, source_hash = cached["status"], cached["source_sha256"]
            else:
                status, body, _ = fetch.get(url)
                source_hash = hashlib.sha256(body.encode()).hexdigest()
                spec = None
            if spec is None and urllib.parse.urlsplit(url).path.endswith((".yaml", ".yml")):
                # Optional tooling dependency already present in this workspace;
                # never use YAML object constructors or add a production package.
                import yaml

                spec = yaml.safe_load(body)
            elif spec is None:
                spec = json.loads(body)
            if not isinstance(spec, dict) or not ("openapi" in spec or "swagger" in spec):
                raise ValueError("OPENAPI_DOCUMENT_REQUIRED")
            name = Path(urllib.parse.urlsplit(url).path).stem + ".json"
            cleaned = contract(spec)
            (out / name).write_text(json.dumps(cleaned, ensure_ascii=False, indent=2), encoding="utf-8")
            info = spec.get("info", {})
            report["saved"].append({"url": url, "file": "schemas/" + name, "status": status,
                                     "source_sha256": source_hash,
                                     "openapi": spec.get("openapi", spec.get("swagger")),
                                     "license": info.get("license"),
                                     "operation_count": sum(
                                         method.lower() in {"get", "post", "put", "patch", "delete", "head", "options"}
                                         for item in spec.get("paths", {}).values() for method in item
                                     )})
            doc += [f"## {name}", "", f"Source: {url}", "",
                    f"[Technical schema](schemas/{name})", ""]
            for path, item in cleaned.get("paths", {}).items():
                if not isinstance(item, dict):
                    continue
                for method, operation in item.items():
                    if method.lower() not in {"get", "post", "put", "patch", "delete", "head", "options"}:
                        continue
                    record = {"method": method.upper(), "path": path, "schema_source": url,
                              "operationId": operation.get("operationId"),
                              "parameters": item.get("parameters", []) + operation.get("parameters", []),
                              "requestBody": operation.get("requestBody"),
                              "responses": operation.get("responses"),
                              "security": operation.get("security", cleaned.get("security"))}
                    operations.append(record)
                    doc += [f"### `{method.upper()} {path}`", ""]
                    if record["operationId"]:
                        doc += [f"Operation ID: `{record['operationId']}`", ""]
                    for param in record["parameters"]:
                        doc += [f"- Parameter `{param.get('name', param.get('$ref', '?'))}`; "
                                f"in={param.get('in', '?')}; required={param.get('required', False)}; "
                                f"type={param.get('type', param.get('schema', {}).get('type', 'unspecified'))}"]
                        doc += schema_lines(param.get("schema", {}), document=cleaned)
                    for media, content in (record["requestBody"] or {}).get("content", {}).items():
                        doc += ["", f"Request content: `{media}`"]
                        doc += schema_lines(content.get("schema", {}), document=cleaned)
                    doc += ["", "Response status codes: " + ", ".join(
                        f"`{code}`" for code in (record["responses"] or {})
                    ), ""]
                    for status_code, response in (record["responses"] or {}).items():
                        if not isinstance(response, dict):
                            continue
                        if "schema" in response:
                            doc += [f"Response `{status_code}` fields:", ""]
                            doc += schema_lines(response["schema"], document=cleaned)
                        for media, content in response.get("content", {}).items():
                            doc += [f"Response `{status_code}` / `{media}` fields:", ""]
                            doc += schema_lines(content.get("schema", {}), document=cleaned)
                        doc.append("")
            print(f"Extracted {name}", flush=True)
        except Exception as error:
            report["failures"].append({"url": url, "error_type": type(error).__name__})
    (root / "swagger-manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "api-contracts.json").write_text(json.dumps(operations, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "API_CONTRACTS.md").write_text("\n".join(doc), encoding="utf-8")
    for filename in ("README.md", "WALLEX_REFERENCE.md"):
        path = root / filename
        if "## Official Swagger contracts" not in path.read_text(encoding="utf-8"):
            with path.open("a", encoding="utf-8") as output:
                output.write("\n## Official Swagger contracts\n\n"
                         "- [Readable technical contracts](API_CONTRACTS.md)\n"
                         "- [Structured operations](api-contracts.json)\n"
                         "- [Schema coverage/errors](swagger-manifest.json)\n")
    print(json.dumps({"schemas_saved": len(report["saved"]), "schema_failures": len(report["failures"]),
                      "operations": len(operations)}), flush=True)


if __name__ == "__main__":
    main()
