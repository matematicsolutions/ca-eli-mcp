"""Live smoke test against the real Justice Laws Website. Network required."""

from __future__ import annotations

import pytest

from ca_eli_mcp.citations import build_citation, parse_metadata
from ca_eli_mcp.client import JusticeLawsClient


@pytest.mark.asyncio
async def test_get_act() -> None:
    async with JusticeLawsClient() as client:
        xml_text = await client.get_xml("C-46", "eng")
        doc = parse_metadata("C-46", "eng", xml_text)
        citation = build_citation(doc)

        assert doc.short_title == "Criminal Code"
        assert citation.human_readable_citation == "Criminal Code (C-46)"
        assert citation.lex_uri == "https://laws-lois.justice.gc.ca/eng/XML/C-46.xml"
        assert citation.source_url == "https://laws-lois.justice.gc.ca/eng/acts/C-46/index.html"


@pytest.mark.asyncio
async def test_get_regulation_uses_regulations_path() -> None:
    async with JusticeLawsClient() as client:
        xml_text = await client.get_xml("SOR-2018-151", "eng")
        doc = parse_metadata("SOR-2018-151", "eng", xml_text)
        citation = build_citation(doc)

        assert "regulations" in citation.source_url
