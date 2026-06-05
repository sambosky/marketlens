# MarketLens MCP server

Re-exposes the MarketLens skills as **Model Context Protocol** tools so you can
use the assistant from inside **Claude Desktop** or **Cursor**.

Tools exposed:

- `ask_marketlens(question)` — runs the full agent pipeline → a cited answer.
- `search_filings`, `search_news`, `get_quote`, `get_portfolio` — research skills.
- `add_to_watchlist`, `list_watchlist`, `set_price_alert`, `list_alerts`,
  `log_trade`, `list_journal` — non-executing action skills.

## Prerequisites

The stack must be running (the server talks to Postgres and, for `ask_marketlens`,
Ollama):

```bash
docker compose up -d db ollama
docker compose run --rm ingest    # populate filings/news/portfolio
```

Install the backend deps locally so the entrypoint is importable:

```bash
cd backend && pip install .
```

## Run / inspect

```bash
python -m mcp_server.server          # stdio
npx @modelcontextprotocol/inspector python -m mcp_server.server   # interactive
```

## Claude Desktop

Copy `claude_desktop_config.sample.json` into your Claude Desktop config
(`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS),
set the absolute `cwd` to this `backend/` directory, and restart Claude Desktop.
Then ask: *"Use marketlens to tell me NVDA's latest margins."*

## Cursor

Add the same server under **Settings → MCP → Add server** (command
`python -m mcp_server.server`, with the `cwd`/env from the sample).
