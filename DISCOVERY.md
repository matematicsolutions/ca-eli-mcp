# Discovery notes - Canada

Date: 2026-07-06.

## Why Canada, and why now

An earlier scouting pass (2026-07-04) only looked at CanLII (case law) for
Canada and ruled it out on ToS grounds. It did not check the Justice Laws
Website for legislation. Live probing on 2026-07-06 found it works exactly
like the cleanest connectors in this fleet: keyless, direct XML per
document, bilingual, both acts and regulations on the same URL pattern.
Market size (the Federation of Law Societies of Canada's own "About Us"
page, flsc.ca/about-us/, states law societies regulate "more than 136,000
lawyers" - a standing figure, not verified against a specific year during
this session) combined with this architecture made it the clear pick over
Mexico in this round - Mexico's federal law
portals (`diputados.gob.mx/LeyesBiblio`, `ordenjuridico.gob.mx`,
`dof.gob.mx`) returned connection failures on every endpoint tried and have
no documented API; still DEFER, as in the earlier sweep.

## What's confirmed live

- `https://laws-lois.justice.gc.ca/eng/XML/C-46.xml` - 200, well-formed XML,
  `lims` namespace, consolidation date attributes, no external DTD (unlike
  Ireland's ISB, which needed the DTD workaround).
- `https://laws-lois.justice.gc.ca/fra/XML/C-46.xml` - French version, 200.
- `https://laws-lois.justice.gc.ca/eng/XML/SOR-2018-151.xml` - a regulation
  on the same path pattern, 200.
- `https://laws-lois.justice.gc.ca/eng/acts/C-46/index.html` and
  `https://laws-lois.justice.gc.ca/eng/regulations/SOR-2018-151/index.html`
  - the public HTML pages, both 200 (note: acts and regulations live under
  different path segments, `acts/` vs `regulations/` - this connector
  detects which one to use from the code prefix).

## Not resolved

- No confirmed reuse license for Justice Laws Website content beyond "it is
  the official public consolidation, meant for public use" - flagged in
  SOURCES.md, same caution class as other Crown/amtliche-Werke-style
  government legal text. Does not block a keyless-fetch connector (we are
  not redistributing a bulk copy), but should be confirmed before any
  bulk/offline mode.
- `laws-lois-api.justice.gc.ca`, referenced in some older documentation
  found via web search, returned 404 on every path tried - likely retired
  or never public. Not used.
