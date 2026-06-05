# MarketLens

> A cited stock-**research** assistant — not an advice engine. Ask a question; MarketLens routes it to the right source (SEC filings, recent news, live market data, or your portfolio) and answers with **inline citations**. It never says buy/sell.

[![CI](https://github.com/sambosky/marketlens/actions/workflows/ci.yml/badge.svg)](https://github.com/sambosky/marketlens/actions/workflows/ci.yml)

<!-- Add a screenshot/GIF of the chat (with routing chips + citations) here. -->

## Why this project

It demonstrates a production-shaped agentic RAG stack end to end:

- **Google ADK** multi-agent orchestration — a planner that routes to skills, a composer that writes the cited answer. Model behind **LiteLLM**: **local Ollama by default (no API key), Claude by config**.
- **RAG over Postgres + pgvector** with **local `fastembed` embeddings** (keyless).
- **Dishka** dependency injection that owns open connections (DB engine, HTTP client, embedding model) with proper async scopes/lifecycle.
- **FastAPI** with SSE streaming; **Repository + Unit-of-Work** persistence.
- An **MCP server** that re-exposes the skills so MarketLens works as a tool inside **Claude Desktop / Cursor**.
- **Next.js** UI: streaming chat with visible routing + clickable citations, a Tools panel, and portfolio/watchlist/alerts/journal dashboards.
- **Real, free data**: SEC EDGAR filings + yfinance quotes/news — no API keys.

> ⚠️ Research/monitoring only. Not financial advice. The action skills (watchlist, alerts, trade journal) are **non-executing** — there is no brokerage integration.

## The skills (routing showcase)

| Question | Skill | Source |
|---|---|---|
| "What were NVDA's latest margins?" | `search_filings` | SEC filings (RAG) |
| "Why did TSLA move recently?" | `search_news` | recent news (RAG) |
| "What's AAPL's price and P/E?" | `get_quote` | live (yfinance) |
| "How's my MSFT position?" | `get_portfolio` | your holdings (read-only) |
| "Add NVDA to my watchlist" | `add_to_watchlist` | non-executing action |

## Quick start

```bash
cp .env.example .env
# set MARKETLENS_SEC_USER_AGENT to include your email (SEC requires a contact UA)

docker compose up --build          # db+pgvector, ollama (pulls the model), backend, frontend
docker compose run --rm ingest     # fetch + embed SEC filings/news, seed the demo portfolio
```

- UI → http://localhost:3000
- API docs → http://localhost:8000/docs
- Health → http://localhost:8000/health

No credentials are required to run. For **Claude-quality** answers, set
`MARKETLENS_LLM__PROVIDER=anthropic` and `ANTHROPIC_API_KEY` in `.env`.

## Use it from Claude Desktop / Cursor (MCP)

The same skills are exposed over MCP — see [`backend/mcp_server/README.md`](backend/mcp_server/README.md).
After the stack is up:

```bash
cd backend && pip install .
npx @modelcontextprotocol/inspector python -m mcp_server.server
```

Then call `ask_marketlens("what were NVDA's latest margins?")` or any granular skill.

## Project layout

```
backend/
  infra/        Dishka providers (db, embedding, llm, http, marketdata) + container + UoW
  core/         ORM models, repositories (securities/filings/news/portfolio/watchlist/alerts/journal)
  retrieval/    Retriever protocol + filings/news pgvector retrievers (cited Evidence)
  skills/       the 7 skills (shared core) + adk_tools (one registry → ADK + /tools + MCP)
  agents/       ADK planning + composition agents, runner (event→SSE bridge)
  api/          FastAPI app + routes (chat SSE, tools, portfolio/watchlist/alerts/journal)
  ingestion/    SEC EDGAR + yfinance → chunk → embed; demo seed; CLI
  mcp_server/   FastMCP external adapter
  alembic/      migrations (pgvector extension + HNSW indexes)
frontend/       Next.js (App Router) + Tailwind
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the request flow and design notes.

## Development

```bash
make help        # list targets
make test        # backend tests (cd backend && pytest)
make migrate     # alembic upgrade head
make ingest      # one-shot ingest
make mcp         # run the MCP server (stdio)
```

## Tech

Python · FastAPI · Dishka · SQLAlchemy 2.0 (async) · Postgres + pgvector ·
fastembed · Google ADK + LiteLLM (Ollama/Claude) · MCP · yfinance · SEC EDGAR ·
Next.js 15 · TypeScript · Tailwind · Docker Compose.
