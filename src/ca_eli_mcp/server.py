"""FastMCP entry point - Canadian federal legislation (Justice Laws Website) tools.

Run:

    python -m ca_eli_mcp.server

Configuration via env:

- ``CA_ELI_CACHE_DIR`` (default ``~/.matematic/cache/ca-eli``)
- ``CA_ELI_AUDIT_DIR`` (default ``~/.matematic/audit``)
- ``CA_ELI_BASE_URL`` (default ``https://laws-lois.justice.gc.ca``)
"""

from __future__ import annotations

import os

import httpx
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .audit import AuditLogger, hash_input, timer
from .citations import build_citation, parse_metadata
from . import runtime
from .client import DEFAULT_BASE_URL, JusticeLawsClient
from .coverage import Coverage, build_coverage

INSTRUCTIONS = """\
This MCP server exposes the Justice Laws Website (laws-lois.justice.gc.ca), the Department of Justice Canada's official consolidated Acts and regulations. Bilingual (English/French).

## Call order

1. `ca_get_document` - metadata (title, in-force status, last-consolidated date) for one act or regulation by its `code` (e.g. `"C-46"` for the Criminal Code, `"SOR-2018-151"` for a regulation).
2. `ca_get_text` - the full consolidated XML of the same document.

## Hard constraints

- **No free-text search** - the Justice Laws Website is addressed by code, not keywords (same limitation as ie-eli-mcp for Ireland). Discover a code from an external reference (a citation the user already has, or a known short title) before calling these tools.
- **Every response has `human_readable_citation` + `source_url`** - cite both to the user.
- **No full-text search across all Canadian law** - this is federal legislation only; provincial/territorial law is out of scope.
- **Audit log JSONL** - every tool call appends to `~/.matematic/audit/ca-eli-mcp.jsonl`.

## Error iteration

Tools return a structured error with a `[code]` prefix:
- `invalid_arg` - a parameter is missing or malformed.
- `not_found` - no act or regulation exists for that code.
- `upstream_error` - a Justice Laws Website error (HTTP, timeout). Retry once before surfacing.

## Response style

- Cite documents as `human_readable_citation`: "Criminal Code (C-46)".
- NEVER invent a code or title - take each from the tool output.
"""


class ToolError(Exception):
    """Structured error for ca-eli MCP tools - visible to the LLM with a [code] prefix."""

    VALID_CODES = frozenset({"invalid_arg", "not_found", "upstream_error"})

    def __init__(self, code: str, message: str):
        if code not in self.VALID_CODES:
            raise ValueError(f"Unknown ToolError code: {code}. Valid: {sorted(self.VALID_CODES)}")
        self.code = code
        super().__init__(f"[{code}] {message}")


READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=True,
)

mcp: FastMCP = FastMCP(name="ca-eli-mcp", instructions=INSTRUCTIONS)

_VALID_LANGS = frozenset({"eng", "fra"})


def _base_url() -> str:
    return os.environ.get("CA_ELI_BASE_URL", runtime.base_url("eli", DEFAULT_BASE_URL)).rstrip("/")


def _audit() -> AuditLogger:
    return AuditLogger()


def _check_args(code: str, lang: str) -> None:
    if not code or not code.strip():
        raise ToolError("invalid_arg", "code must be a non-empty string, e.g. 'C-46'.")
    if lang not in _VALID_LANGS:
        raise ToolError("invalid_arg", f"lang={lang!r} must be one of {sorted(_VALID_LANGS)}.")


def _map_upstream(exc: Exception) -> Exception:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code == 404:
        return ToolError("not_found", "No act or regulation found at that code on the Justice Laws Website.")
    if isinstance(exc, (httpx.HTTPStatusError, httpx.TransportError, httpx.TimeoutException)):
        return ToolError("upstream_error", f"Justice Laws Website error: {type(exc).__name__}: {exc}")
    return exc


# ---------------------------------------------------------------------------
# ca_get_document
# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def ca_get_document(code: str, lang: str = "eng") -> dict:
    """Fetch metadata for a Canadian federal act or regulation.

    Args:
        code: e.g. ``"C-46"`` (Criminal Code) or ``"SOR-2018-151"`` (a regulation).
        lang: ``"eng"`` or ``"fra"`` (default ``"eng"``).

    Returns:
        A dict with ``code``, ``lang``, ``long_title``, ``short_title``,
        ``current_date``, ``in_force``, ``lex_uri``, ``human_readable_citation``,
        ``source_url``.
    """
    audit = _audit()
    _check_args(code, lang)
    input_hash = hash_input({"code": code, "lang": lang})

    with timer() as t:
        try:
            async with JusticeLawsClient(base_url=_base_url()) as client:
                xml_text = await client.get_xml(code, lang)
        except Exception as exc:
            audit.log(tool="ca_get_document", input_hash=input_hash, output_count_or_size=0,
                      duration_ms=t.duration_ms if t.duration_ms else 0, status="error",
                      error=f"{type(exc).__name__}: {exc}")
            raise _map_upstream(exc) from exc

    doc = parse_metadata(code, lang, xml_text)
    citation = build_citation(doc)
    result = {
        "code": doc.code,
        "lang": doc.lang,
        "long_title": doc.long_title,
        "short_title": doc.short_title,
        "current_date": doc.current_date,
        "in_force": doc.in_force,
        "lex_uri": citation.lex_uri,
        "human_readable_citation": citation.human_readable_citation,
        "source_url": citation.source_url,
    }
    audit.log(tool="ca_get_document", input_hash=input_hash, output_count_or_size=1,
              duration_ms=t.duration_ms, status="ok")
    return result


# ---------------------------------------------------------------------------
# ca_get_text
@mcp.tool(annotations=READ_ONLY)
async def ca_coverage() -> Coverage:
    """Declare what this connector covers, how it is sourced, and what it does NOT cover.

    Call this before telling a user that the law "does not contain" something, and whenever
    a search comes back empty: the absence may be a gap in this connector rather than in the
    law. Every gap carries a fallback saying where to look instead.

    Returns:
        ``Coverage`` with families, an as-of note, and a non-empty list of known gaps.
    """
    return build_coverage()


# ---------------------------------------------------------------------------


@mcp.tool(annotations=READ_ONLY)
async def ca_get_text(code: str, lang: str = "eng") -> dict:
    """Fetch the full consolidated XML text of a Canadian federal act or regulation.

    Args:
        code: e.g. ``"C-46"``.
        lang: ``"eng"`` or ``"fra"`` (default ``"eng"``).

    Returns:
        A dict with ``code``, ``lang``, ``lex_uri``, ``human_readable_citation``,
        ``source_url``, ``content`` (raw XML), ``byte_size``.
    """
    audit = _audit()
    _check_args(code, lang)
    input_hash = hash_input({"code": code, "lang": lang})

    with timer() as t:
        try:
            async with JusticeLawsClient(base_url=_base_url()) as client:
                xml_text = await client.get_xml(code, lang)
        except Exception as exc:
            audit.log(tool="ca_get_text", input_hash=input_hash, output_count_or_size=0,
                      duration_ms=t.duration_ms if t.duration_ms else 0, status="error",
                      error=f"{type(exc).__name__}: {exc}")
            raise _map_upstream(exc) from exc

    doc = parse_metadata(code, lang, xml_text)
    citation = build_citation(doc)
    byte_size = len(xml_text.encode("utf-8"))
    result = {
        "code": code,
        "lang": lang,
        "lex_uri": citation.lex_uri,
        "human_readable_citation": citation.human_readable_citation,
        "source_url": citation.source_url,
        "content": xml_text,
        "byte_size": byte_size,
    }
    audit.log(tool="ca_get_text", input_hash=input_hash, output_count_or_size=byte_size,
              duration_ms=t.duration_ms, status="ok")
    return result


def main() -> None:
    """Run the MCP server over stdio (default for Claude Code)."""
    mcp.run()


if __name__ == "__main__":
    main()
