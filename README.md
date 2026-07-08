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

## 5. Generate the budget spreadsheet

`scripts/build_budget.py` creates a new Google Sheet with the three core tabs (Budget
Planner, Smart Bill Calendar, Transactions Tracker — see `docs/SPEC.md` for the full
target). It calls the Sheets API directly using the same OAuth client from `.env`, so it
doesn't need the MCP server running.

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export $(grep -v '^#' .env | xargs)   # or just export GOOGLE_OAUTH_CLIENT_ID/SECRET
python scripts/build_budget.py "My 2026 Budget"
```

First run opens a browser for the Google OAuth consent flow and caches the token in
`token.json` (gitignored). It prints the new spreadsheet's URL when done.

Conventions used in the generated sheet:
- **Amount columns are signed** — income positive, bills/expenses/debt payments negative —
  so totals and running balances are plain sums.
- **Smart Bill Calendar** has one checkbox column per month; ticking a box includes that
  row's amount in that month's `Monthly Net Total`.
- **Transactions Tracker**'s running balance is a single `ARRAYFORMULA` in the first data
  row, not one formula per row.

Not yet built (tracked in `docs/SPEC.md`): Budget Template, Annual/Budget Dashboards, Debt
Payoff Tracker, Savings Tracker, Net Worth Tracker, 50/30/20 Tracker, No Spend Tracker,
and any charts.

Once the MCP server (steps 1-4) is connected to Claude, you can also ask Claude to read
back and adjust the generated sheet directly through the `sheets` tools — the script is
just the bootstrap.

## Status

- [x] Repo + self-hosted MCP server config
- [x] MVP: Budget Planner, Smart Bill Calendar, Transactions Tracker (`scripts/build_budget.py`)
- [ ] Dashboards, Debt Payoff / Savings / Net Worth trackers, 50/30/20, No Spend, charts (see `docs/SPEC.md`)
