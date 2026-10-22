"""Challenge market restrictions. Denylisted credit-account pairs are excluded."""
from pathlib import Path
import re

_SOURCE = Path(__file__).resolve().parents[1] / "src" / "marketRules.js"


def _load_excluded() -> frozenset[str]:
    text = _SOURCE.read_text(encoding="utf-8")
    match = re.search(r"const excludedMarketText = `([\s\S]*?)`;", text)
    if not match:
        raise RuntimeError(f"Could not find excluded market list in {_SOURCE}")
    return frozenset(line.strip().upper() for line in match.group(1).splitlines() if line.strip())


EXCLUDED_CREDIT_MARKETS = _load_excluded()


def normalize_pair(pair: str) -> str:
    normalized = pair.strip().upper().replace("-", "/").replace("_", "/")
    if "/" not in normalized:
        for quote in ("USDT", "TMN"):
            if normalized.endswith(quote) and len(normalized) > len(quote):
                return f"{normalized[:-len(quote)]}/{quote}"
    return normalized


def check_market(pair: str) -> tuple[bool, str]:
    symbol = normalize_pair(pair)
    if not re.fullmatch(r"[A-Z0-9]+/(?:TMN|USDT)", symbol):
        return False, "جفت‌ارز نامعتبر است؛ فقط قالب BASE/TMN یا BASE/USDT پذیرفته می‌شود."
    if symbol in EXCLUDED_CREDIT_MARKETS:
        return False, f"{symbol} در حساب اعتباری غیرفعال است."
    return True, "در فهرست ارسالی غیرفعال نیست؛ وضعیت مجاز بودن باید از MCP هم تأیید شود."


def parse_pair(pair: str) -> tuple[str | None, str | None]:
    normalized = normalize_pair(pair)
    if "/" not in normalized:
        return None, None
    return tuple(normalized.split("/", 1))  # type: ignore[return-value]
