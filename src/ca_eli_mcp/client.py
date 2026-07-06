"""Async httpx client for the Justice Laws Website (laws-lois.justice.gc.ca).

Keyless. Every act and regulation is addressed by a stable "code" (e.g.
"C-46" or "SOR-2018-151") and served as XML at a predictable URL - no
free-text search API exists on the site itself, so this connector is
by-coordinate only, same as ie-eli-mcp.
"""

from __future__ import annotations

import anyio
import httpx

from .cache import HttpCache

DEFAULT_BASE_URL = "https://laws-lois.justice.gc.ca"
DEFAULT_TIMEOUT = httpx.Timeout(40.0, connect=10.0)
USER_AGENT = "ca-eli-mcp/0.1.0 (+https://github.com/matematicsolutions/ca-eli-mcp)"

_RETRY_STATUS = frozenset({429, 500, 502, 503, 504})
_MAX_ATTEMPTS = 3


class JusticeLawsClient:
    """Async client. Use as ``async with JusticeLawsClient() as c: ...``."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        cache: HttpCache | None = None,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._cache = cache or HttpCache()
        self._http = httpx.AsyncClient(
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept": "*/*"},
        )

    async def __aenter__(self) -> JusticeLawsClient:
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()
        self._cache.close()

    async def _get_xml(self, path: str, *, category: str) -> str:
        url = f"{self.base_url}{path}"
        cached = self._cache.get(url)
        if cached is not None and isinstance(cached, str):
            return cached
        last_exc: Exception | None = None
        for attempt in range(_MAX_ATTEMPTS):
            try:
                resp = await self._http.get(url)
                resp.raise_for_status()
                self._cache.set(url, resp.text, ttl=HttpCache.ttl_for(category))
                return resp.text
            except httpx.HTTPStatusError as exc:
                last_exc = exc
                if exc.response.status_code not in _RETRY_STATUS or attempt == _MAX_ATTEMPTS - 1:
                    raise
            except (httpx.TransportError, httpx.TimeoutException) as exc:
                last_exc = exc
                if attempt == _MAX_ATTEMPTS - 1:
                    raise
            await anyio.sleep(0.5 * (2**attempt))
        assert last_exc is not None
        raise last_exc

    async def get_xml(self, code: str, lang: str = "eng") -> str:
        return await self._get_xml(f"/{lang}/XML/{code}.xml", category="act")
