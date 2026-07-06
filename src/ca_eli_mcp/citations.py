"""Citation contract for ca-eli-mcp.

The Justice Laws Website has no formal ELI/ECLI identifier, but every act and
regulation has a stable "code" (e.g. "C-46" for the Criminal Code, "SOR-2018-151"
for a regulation) that resolves to both a machine-readable XML document and a
public HTML page at predictable URLs. We use the code directly rather than
inventing anything. Metadata is extracted by regex from the header block - the
same tolerant approach as ie-eli-mcp, since the LIMS namespace/attribute style
is easier to pull out this way than via a full namespace-aware XML parse.
"""

from __future__ import annotations

import re

from .models import Citation, Document

_XML_URL = "https://laws-lois.justice.gc.ca/{lang}/XML/{code}.xml"
_HTML_URL = "https://laws-lois.justice.gc.ca/{lang}/{kind}/{code}/index.html"

_REGULATION_PREFIXES = ("SOR-", "SI-", "C.R.C.")


def _kind_for(code: str) -> str:
    return "regulations" if code.upper().startswith(_REGULATION_PREFIXES) else "acts"


def parse_metadata(code: str, lang: str, xml_text: str) -> Document:
    long_title_m = re.search(r"<LongTitle[^>]*>(.*?)</LongTitle>", xml_text, re.S)
    short_title_m = re.search(r"<ShortTitle[^>]*>(.*?)</ShortTitle>", xml_text, re.S)
    current_date_m = re.search(r'lims:current-date="([^"]+)"', xml_text)
    in_force_m = re.search(r'\bin-force="([^"]+)"', xml_text)

    def _clean(m: re.Match[str] | None) -> str | None:
        if not m:
            return None
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() or None

    return Document(
        code=code,
        lang=lang,
        long_title=_clean(long_title_m),
        short_title=_clean(short_title_m),
        current_date=current_date_m.group(1) if current_date_m else None,
        in_force=in_force_m.group(1) if in_force_m else None,
    )


def build_citation(d: Document) -> Citation:
    xml_url = _XML_URL.format(lang=d.lang, code=d.code)
    html_url = _HTML_URL.format(lang=d.lang, kind=_kind_for(d.code), code=d.code)
    title = d.short_title or d.long_title or d.code
    human = f"{title} ({d.code})"
    return Citation(lex_uri=xml_url, human_readable_citation=human, source_url=html_url)
