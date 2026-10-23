"""Build a factual, source-linked reference from public Wallex docs (GET only).

No credentials, private API requests, code execution from pages, or prose mirroring.
Uses only the Python standard library. Run from the repository root.
"""

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import deque
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

HOST = "developers.wallex.ir"
ORIGIN = "https://" + HOST
ROOT = ORIGIN + "/docs"
VOID = {"br", "hr", "img", "meta", "link", "input", "source", "wbr", "area", "base"}
SKIP = {"script", "style", "nav", "aside", "footer", "button"}
METHOD = r"GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD"


class Node:
    def __init__(self, tag="", attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def descendants(self, tags):
        for child in self.children:
            if isinstance(child, Node):
                if child.tag in tags:
                    yield child
                yield from child.descendants(tags)

    def text(self):
        if self.tag in SKIP:
            return ""
        if self.tag == "br":
            return "\n"
        text = "".join(c.text() if isinstance(c, Node) else c for c in self.children)
        if self.tag in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4", "pre"}:
            return "\n" + text + "\n"
        return text


class DOM(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def normalize(url, base=ROOT):
    u = urllib.parse.urlsplit(urllib.parse.urljoin(base, url))
    if u.scheme != "https" or u.hostname != HOST or u.username or u.password:
        return None
    if u.path != "/docs" and not u.path.startswith("/docs/"):
        return None
    if any(u.path.lower().endswith(x) for x in (".png", ".jpg", ".svg", ".pdf", ".zip")):
        return None
    return ORIGIN + (u.path.rstrip("/") or "/docs")


class Fetcher:
    def __init__(self, delay):
        self.delay = delay
        self.last = 0.0

    def get(self, url):
        if urllib.parse.urlsplit(url).hostname != HOST:
            raise ValueError("OFF_HOST_FETCH_BLOCKED")
        for attempt in range(3):
            time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
            request = urllib.request.Request(url, headers={
                "User-Agent": "QuantPilot-Documentation-Reference/1.0",
                "Accept": "text/html,application/xml;q=0.9,*/*;q=0.5",
            })
            try:
                with urllib.request.urlopen(request, timeout=25) as response:
                    if urllib.parse.urlsplit(response.url).hostname != HOST:
                        raise ValueError("OFF_HOST_REDIRECT")
                    body = response.read(8 * 1024 * 1024 + 1)
                    if len(body) > 8 * 1024 * 1024:
                        raise ValueError("PAGE_TOO_LARGE")
                    charset = response.headers.get_content_charset() or "utf-8"
                    return response.status, body.decode(charset), response.url
            except urllib.error.HTTPError as error:
                if error.code not in (429, 502, 503, 504) or attempt == 2:
                    raise
                retry = error.headers.get("Retry-After", "")
                time.sleep(min(30, int(retry)) if retry.isdigit() else 2 ** (attempt + 1))
            except (urllib.error.URLError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(2 ** (attempt + 1))
            finally:
                self.last = time.monotonic()


def clean(text):
    return " ".join(text.replace("\u200b", "").split())


def facts(url, html):
    dom = DOM()
    dom.feed(html)
    articles = list(dom.root.descendants({"article"}))
    mains = list(dom.root.descendants({"main"}))
    content = articles[0] if articles else mains[0] if mains else dom.root
    titles = list(content.descendants({"h1"}))
    if not titles:
        titles = list(content.descendants({"h2", "h3"}))
    title = clean(titles[0].text()) if titles else url.rsplit("/", 1)[-1]
    text = content.text()
    endpoints = set()
    for method, path in re.findall(
        rf"\b({METHOD})\s+(https?://[^\s\"'<>`\\]+|/[A-Za-z0-9_/:{{}}?.=&%+\-]+)",
        text, re.I,
    ):
        endpoints.add((method.upper(), path.rstrip(",.;)")))
    for pre in content.descendants({"pre"}):
        code = pre.text()
        matches = re.findall(
            rf"(?:-X|--request)\s+[\"']?({METHOD})[\"']?[\s\\]{{1,50}}[\"']?(https?://[^\s\"'<>`\\]+)",
            code, re.I,
        )
        endpoints.update((method.upper(), path.rstrip(",.;)")) for method, path in matches)
    # Preserve protocol field facts, excluding the site's narrative descriptions/examples.
    parameters = []
    wanted = ("parameter", "name", "data type", "type", "required", "valid values",
              "پارامتر", "نام", "نوع", "اجباری")
    for table in content.descendants({"table"}):
        rows = list(table.descendants({"tr"}))
        if not rows:
            continue
        headers = [clean(c.text()) for c in rows[0].descendants({"th", "td"})]
        indices = [i for i, h in enumerate(headers) if h.lower() in wanted]
        if not indices:
            continue
        for row in rows[1:]:
            cells = [clean(c.text()) for c in row.descendants({"td", "th"})]
            data = {headers[i]: cells[i] for i in indices if i < len(cells)}
            if data:
                parameters.append(data)
    fields = sorted(set(re.findall(r'["\']([A-Za-z_][A-Za-z0-9_.\-]{0,80})["\']\s*:', text)))
    headers = sorted(set(re.findall(
        r"\b(?:sub-account-client-id|x-api-key|authorization|content-type|accept|retry-after)\b",
        text, re.I,
    )), key=str.lower)
    protocol_urls = sorted(set(re.findall(r"(?:https?|wss?)://[^\s\"'<>`\\)]+", text)))
    # Do not include incidental sample-image URLs or named people/example accounts.
    protocol_urls = [u for u in protocol_urls if (
        "api.wallex." in u or "socket.wallex." in u or "stream.wallex." in u
    )]
    links = sorted({u for n in dom.root.descendants({"a"})
                    if (u := normalize(n.attrs.get("href", ""), url))})
    assets = sorted({urllib.parse.urljoin(url, n.attrs.get("href", ""))
                     for n in dom.root.descendants({"a"})
                     if re.search(r"\.(?:json|ya?ml)(?:$|[?#])", n.attrs.get("href", ""))})
    return {
        "url": url, "title": title,
        "endpoints": [{"method": m, "path": p} for m, p in sorted(endpoints)],
        "parameter_tables": parameters, "json_field_names": fields,
        "header_names": headers, "protocol_urls": protocol_urls,
        "links": links, "schema_download_links": assets,
        "source_sha256": hashlib.sha256(html.encode()).hexdigest(),
        "content_characters_read": len(text),
    }


def filename(url):
    slug = urllib.parse.urlsplit(url).path.removeprefix("/docs").strip("/") or "index"
    return slug.replace("/", "__") + ".md"


def render(page):
    lines = [f"# {page['title']}", "", f"Source: {page['url']}", "",
             "This is an extracted technical reference, not an executable API integration.",
             "Descriptions and sample account values are not mirrored.", ""]
    if page["endpoints"]:
        lines += ["## Documented HTTP operations", ""]
        lines += [f"- `{e['method']} {e['path']}`" for e in page["endpoints"]]
    if page["header_names"]:
        lines += ["", "## Header names appearing in this page", "",
                  ", ".join(f"`{h}`" for h in page["header_names"])]
    if page["parameter_tables"]:
        lines += ["", "## Parameter facts", "", "```json",
                  json.dumps(page["parameter_tables"], ensure_ascii=False, indent=2), "```"]
    if page["json_field_names"]:
        lines += ["", "## JSON field names in documented examples", "",
                  ", ".join(f"`{k}`" for k in page["json_field_names"]), "",
                  "Field presence in an example does not establish requiredness, type, or nesting."]
    if page["protocol_urls"]:
        lines += ["", "## Documented protocol addresses (not called)", ""]
        lines += [f"- `{u}`" for u in page["protocol_urls"]]
    if page["schema_download_links"]:
        lines += ["", "## Official schema downloads", ""]
        lines += [f"- {u}" for u in page["schema_download_links"]]
    if not any(page[k] for k in ("endpoints", "parameter_tables", "json_field_names")):
        lines += ["", "This conceptual page has no automatically extracted HTTP/JSON contract.",
                  "Consult the source for its narrative guidance; see key findings in the main reference."]
    lines += ["", "## Internal documentation links", ""]
    lines += [f"- [{u.removeprefix(ROOT) or '/'}]({filename(u)})" for u in page["links"]]
    return "\n".join(lines) + "\n"


def write_reference(out, manifest, pages):
    by_url = {p["url"]: p for p in pages}
    lines = ["# Wallex API — مرجع فنی مستندات", "",
             f"مبدأ: {ROOT}", f"زمان دریافت (UTC): {manifest['started_at']}", "",
             "این سند بازنویسی و استخراج اطلاعات فنی صفحات است، نه بازنشر کامل متن سایت.",
             "فراخوانی API، سفارش، انتقال وجه یا استفاده از کلید حساب در این خزش انجام نشده است.", "",
             "## پوشش", "", f"- صفحات کشف‌شده: {len(manifest['discovered'])}",
             f"- صفحات خوانده‌شده: {len(pages)}", f"- خطاها: {len(manifest['failures'])}",
             f"- صف باقی‌مانده: {len(manifest['pending'])}", "",
             "کشف از sitemap و لینک‌های داخلی انجام شده؛ صفحات بدون لینک و بدون ورودی sitemap تضمین نمی‌شوند.",
             "پارامترهای استخراج‌شده و مثال‌ها باید با schema رسمی تطبیق داده شوند؛ نبود یک فیلد در این مرجع، نبود آن در API را ثابت نمی‌کند.", "",
             "## نکات اتصال حساب اعتباری", "",
             "- در صفحهٔ ساخت کلید، حساب اصلی و هر حساب اعتباری دارای کلید مخصوص خود معرفی شده‌اند.",
             "- برای اسپاتِ حساب اعتباری، صفحهٔ معرفی اسپات علاوه بر کلید همان حساب، هدر `sub-account-client-id` را لازم می‌داند.",
             "- صفحهٔ فهرست زیرحساب‌ها، شناسهٔ حساب را با فیلد `clientId` در مثال معرفی می‌کند؛ شکل واقعی پاسخ باید مستقل بررسی شود.",
             "- این شواهد روش اتصال را مستند می‌کنند؛ علت خطای قبلی 401 یا اعتبار کلید فعلی را ثابت نمی‌کنند.", "",
             f"منابع: [ساخت کلید]({ROOT}/create-api-key)، [اسپات]({ROOT}/spot-intro)، [فهرست حساب‌ها]({ROOT}/trade-credit-active-sub-account-list).", "",
             "## فهرست صفحات", ""]
    for url in sorted(by_url):
        page = by_url[url]
        lines.append(f"- [{page['title']}](pages/{filename(url)}) — [منبع]({url})")
    lines += ["", "## محتوای فنی همهٔ صفحات", ""]
    for url in sorted(by_url):
        page = by_url[url]
        body = render(page)
        # Combined document uses source URLs for navigation, not page-relative links.
        body = re.sub(r"\]\(([^():]+\.md)\)", r"](pages/\1)", body)
        lines += ["---", "", body]
    (out / "WALLEX_REFERENCE.md").write_text("\n".join(lines), encoding="utf-8")
    (out / "README.md").write_text(
        "# Wallex documentation reference\n\n"
        "- [Combined technical reference](WALLEX_REFERENCE.md)\n"
        "- [Coverage and failed URLs](manifest.json)\n"
        "- [Structured technical facts](pages.json)\n"
        "- [Unique documented HTTP operations](endpoints.json)\n\n"
        "Public documentation only; no account data, credentials, API calls or trading.\n"
        "Narrative text is not mirrored. Discovered scope and failures are explicit.\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/wallex-reference"))
    parser.add_argument("--delay", type=float, default=0.4)
    parser.add_argument("--max-pages", type=int, default=500)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "manifest.json").exists():
        raise SystemExit("Preserve the existing snapshot; use a new output directory.")
    (out / "pages").mkdir(exist_ok=True)
    fetch = Fetcher(max(0.25, args.delay))
    manifest = {"root": ROOT, "started_at": datetime.now(timezone.utc).isoformat(),
                "robots": {}, "sitemaps": [], "discovered": [], "failures": [], "pending": []}
    robots = urllib.robotparser.RobotFileParser()
    try:
        status, body, _ = fetch.get(ORIGIN + "/robots.txt")
        robots.parse(body.splitlines())
        manifest["robots"] = {"status": status, "sha256": hashlib.sha256(body.encode()).hexdigest()}
    except urllib.error.HTTPError as error:
        manifest["robots"] = {"status": error.code}
        if error.code not in (404, 410):
            raise SystemExit("Cannot establish robots policy; crawl not started.")
        robots.parse([])
    found = {ROOT}
    sitemap_queue = deque([ORIGIN + "/sitemap.xml"])
    seen_maps = set()
    while sitemap_queue:
        url = sitemap_queue.popleft()
        if url in seen_maps:
            continue
        seen_maps.add(url)
        try:
            status, body, _ = fetch.get(url)
            tree = ET.fromstring(body)
            manifest["sitemaps"].append({"url": url, "status": status})
            for node in tree.iter():
                if node.tag.endswith("}loc") and node.text:
                    if tree.tag.endswith("sitemapindex"):
                        if urllib.parse.urlsplit(node.text).hostname == HOST:
                            sitemap_queue.append(node.text)
                    elif (u := normalize(node.text)):
                        found.add(u)
        except Exception as error:
            manifest["sitemaps"].append({"url": url, "error_type": type(error).__name__})
    queue, visited, pages = deque(sorted(found)), set(), []
    while queue and len(visited) < args.max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        if not robots.can_fetch("QuantPilot-Documentation-Reference", url):
            manifest["failures"].append({"url": url, "reason": "ROBOTS_DISALLOW"})
            continue
        try:
            status, body, final = fetch.get(url)
            if normalize(final) is None:
                raise ValueError("DOCUMENTATION_REDIRECT_OUT_OF_SCOPE")
            page = facts(url, body)
            page["http_status"] = status
            pages.append(page)
            (out / "pages" / filename(url)).write_text(render(page), encoding="utf-8")
            for link in page["links"]:
                if link not in found:
                    found.add(link)
                    queue.append(link)
        except Exception as error:
            entry = {"url": url, "error_type": type(error).__name__}
            if isinstance(error, urllib.error.HTTPError):
                entry["http_status"] = error.code
            manifest["failures"].append(entry)
        if len(visited) % 10 == 0:
            print(f"Read {len(pages)} / visited {len(visited)}; queued {len(queue)}", flush=True)
    manifest["discovered"] = sorted(found)
    manifest["pending"] = sorted(set(queue) - visited)
    manifest["completed_at"] = datetime.now(timezone.utc).isoformat()
    manifest["pages_read"] = len(pages)
    for name, data in (("manifest.json", manifest), ("pages.json", pages)):
        (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    operations = {}
    for page in pages:
        for endpoint in page["endpoints"]:
            key = endpoint["method"] + " " + endpoint["path"]
            operations.setdefault(key, []).append(page["url"])
    (out / "endpoints.json").write_text(
        json.dumps(operations, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_reference(out, manifest, pages)
    print(json.dumps({"pages_read": len(pages), "discovered": len(found),
                      "failures": len(manifest["failures"]), "pending": len(manifest["pending"]),
                      "operations": len(operations), "output": str(out)}), flush=True)


if __name__ == "__main__":
    main()
