# ca-eli-mcp

<!-- mcp-name: io.github.matematicsolutions/ca-eli-mcp -->

MCP server for Canadian federal legislation via the Justice Laws Website
(laws-lois.justice.gc.ca), the Department of Justice Canada's official
source for consolidated Acts and regulations. Bilingual (English/French).

## What this is not

- **No free-text search** - the Justice Laws Website has no search API of
  its own. This connector is by-code only (the same limitation as
  `ie-eli-mcp` for Ireland): you need to already know the code (e.g.
  `"C-46"` for the Criminal Code) or a short title to look one up.
- **Federal only** - provincial and territorial legislation is out of scope.
- **No case law** - CanLII's terms of service forbid bulk redistribution and
  its content API requires a per-identity key, which breaks the
  zero-cloud pattern this connector otherwise follows. Not attempted here.

## Tools

| Tool | Purpose |
|---|---|
| `ca_get_document` | Metadata (title, in-force status, last-consolidated date) for one act or regulation |
| `ca_get_text` | Full consolidated XML text of the same document |

Every response carries `lex_uri` (the XML source), `source_url` (the public
HTML page), and `human_readable_citation` (e.g. `"Criminal Code (C-46)"`).

## Install

```bash
pip install ca-eli-mcp
```


### Windows 11 ze Smart App Control

Smart App Control blokuje niepodpisane pliki wykonywalne, a `uvx.exe`, `pip.exe`
i generowany przy instalacji `ca-eli-mcp.exe` podpisane nie sa. `python.exe`
z python.org jest podpisany przez Python Software Foundation, wiec uruchomienie
przez modul omija blokade:

```bash
python -m pip install ca-eli-mcp
python -m ca_eli_mcp
```

```json
{ "mcpServers": { "ca-eli-mcp": { "command": "python", "args": ["-m", "ca_eli_mcp"] } } }
```

Nie wylaczaj Smart App Control, zeby to obejsc - wylaczenia nie da sie cofnac
bez ponownej instalacji systemu.

## Configuration

| Env var | Default |
|---|---|
| `CA_ELI_CACHE_DIR` | `~/.matematic/cache/ca-eli` |
| `CA_ELI_AUDIT_DIR` | `~/.matematic/audit` |
| `CA_ELI_BASE_URL` | `https://laws-lois.justice.gc.ca` |

## License

Apache-2.0 (code). Justice Laws Website content is Government of Canada
material (see [SOURCES.md](SOURCES.md)).
