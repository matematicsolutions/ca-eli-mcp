# Sources

## Justice Laws Website (`laws-lois.justice.gc.ca`)

- **Origin**: Department of Justice Canada.
- **License**: Government of Canada material. No explicit reuse license was
  found on the site itself during discovery; treat as informational-use
  government material pending confirmation, same caution class as amtliche
  Werke in Germany (see `mcp-de-legal`'s THIRD_PARTY notes for the pattern).
  This connector fetches from the official live site directly - it does not
  vendor or redistribute the official GitHub mirror
  (`justicecanada/laws-lois-xml`, license field `NOASSERTION` on GitHub),
  which was used only as a confirmation that the XML corpus is officially
  maintained and actively updated (last push 2026-07-02).
- **Access**: keyless, direct XML at `/{lang}/XML/{code}.xml` (`lang` is
  `eng` or `fra`), confirmed live 2026-07-06 for both acts (e.g. `C-46`,
  the Criminal Code) and regulations (e.g. `SOR-2018-151`).
- **Coverage**: federal Acts and regulations only. No search endpoint - by
  code only.

## Not covered (out of scope for this connector)

- **CanLII** (case law) - terms of service forbid bulk redistribution,
  content API requires a per-identity key. An earlier scouting pass
  (2026-07-04) already ruled this out for the zero-cloud pattern this fleet
  follows; not revisited here.
- **Provincial/territorial legislation** - each province publishes
  separately; not surveyed in this pass.
- **GovInfo-style bulk archive** - the official GitHub mirror
  (`justicecanada/laws-lois-xml`) could support a future offline/bulk mode,
  but its license is unclear (GitHub reports `NOASSERTION`) - would need
  confirmation before vendoring.
