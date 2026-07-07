# sheets-budget

Self-hosted setup for [`google_workspace_mcp`](https://github.com/taylorwilsdon/google_workspace_mcp),
scoped to Google Sheets (+ Drive, needed to create/find spreadsheets), for use with Claude.
Goal: give Claude tools to build and maintain an annual budget spreadsheet in Google Sheets.

See [`docs/SPEC.md`](docs/SPEC.md) for the target spreadsheet spec — not yet built, that's
the next step once the MCP server is wired up.

## 1. Create a Google Cloud OAuth client

1. In the [Google Cloud Console](https://console.cloud.google.com/), create (or reuse) a project.
2. Enable the **Google Sheets API** and **Google Drive API** for that project.
3. Under **APIs & Services → Credentials**, create an **OAuth client ID**.
   - Application type: "Desktop app" for local/stdio use, or "Web application" with an
     `http://localhost:8000/oauth2callback` redirect URI for HTTP mode.
4. Copy the client ID and client secret.

## 2. Configure

```bash
cp .env.example .env
# fill in GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET
```

`WORKSPACE_MCP_TOOLS` is set to `sheets,drive` — only those two Google services are loaded.

## 3. Run

```bash
docker compose up --build
```

This builds and runs `google_workspace_mcp` in streamable-HTTP mode on
`http://localhost:8000/mcp`. On first use of a tool, the server will prompt you through the
Google OAuth consent flow.

## 4. Connect Claude

**Claude Code:**

```bash
claude mcp add --transport http google-sheets http://localhost:8000/mcp
```

**Claude Desktop** (stdio, no Docker — runs the server via `uvx` instead):

```json
{
  "mcpServers": {
    "google-sheets": {
      "command": "uvx",
      "args": ["workspace-mcp", "--tools", "sheets", "drive"],
      "env": {
        "GOOGLE_OAUTH_CLIENT_ID": "...",
        "GOOGLE_OAUTH_CLIENT_SECRET": "...",
        "OAUTHLIB_INSECURE_TRANSPORT": "1"
      }
    }
  }
}
```

## Status

- [x] Repo + self-hosted MCP server config
- [ ] Build the annual budget spreadsheet (see `docs/SPEC.md`)
