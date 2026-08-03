# sheets-mcp — a minimal Google Sheets MCP server

A small [MCP](https://modelcontextprotocol.io/) server (Node.js, ~100 lines) that
gives Claude direct access to Google Sheets and Drive. Written because existing
options didn't cover one thing I needed daily: **reading the text of formulas**,
not just computed values.

## Tools

| Tool | What it does |
|---|---|
| `read_sheet` | Read a range. `valueRenderOption` picks the mode: `FORMATTED_VALUE` (as in the UI, default), `FORMULA` (**formula text** — for reviewing/fixing spreadsheet logic), `UNFORMATTED_VALUE` (raw). |
| `write_sheet` | Write a 2-D array to a range (`USER_ENTERED`, so formulas work). |
| `add_sheet` | Add a new sheet (tab) to a spreadsheet. |
| `list_drive_folder` | List files in a Drive folder (shared drives supported). |

## Setup

```bash
npm install @modelcontextprotocol/sdk googleapis zod
```

1. Create an OAuth client (Desktop) in Google Cloud Console, enable the Sheets
   and Drive APIs, download it as `credentials.json` next to `index.js`.
2. First run prints an auth URL; paste the code back — `token.json` is created
   and reused from then on.
3. Register in your MCP client config, e.g. for Claude Code (`.mcp.json`):

```json
{
  "mcpServers": {
    "google-sheets": { "command": "node", "args": ["/path/to/sheets-mcp/index.js"] }
  }
}
```

Paths are resolved relative to `index.js` (`__dirname`), so the same file runs
unchanged on Windows and macOS.

**Never commit `credentials.json` / `token.json`** — they are your keys.
