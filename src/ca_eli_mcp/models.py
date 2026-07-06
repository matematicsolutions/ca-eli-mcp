"""Plain dataclasses mirroring the Justice Laws Website consolidated XML header."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    code: str
    lang: str
    long_title: str | None
    short_title: str | None
    current_date: str | None
    in_force: str | None


@dataclass(frozen=True)
class Citation:
    lex_uri: str
    human_readable_citation: str
    source_url: str
