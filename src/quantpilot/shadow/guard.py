"""Transport defense: no private account reads, exchange writes or auth headers."""

import httpx

from quantpilot.marketdata.transport import PATHS


class PublicGetTransport(httpx.AsyncBaseTransport):
    def __init__(self, inner: httpx.AsyncBaseTransport | None = None):
        self.inner = inner or httpx.AsyncHTTPTransport()

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if (
            request.method != "GET"
            or request.url.scheme != "https"
            or request.url.host != "api.wallex.ir"
            or request.url.path not in PATHS.values()
            or request.url.port not in (None, 443)
            or any(h.lower() in ("authorization", "x-api-key", "cookie") for h in request.headers)
        ):
            raise PermissionError("SHADOW_EXCHANGE_MUTATION_OR_PRIVATE_ACCESS_BLOCKED")
        return await self.inner.handle_async_request(request)

    async def aclose(self) -> None:
        await self.inner.aclose()
