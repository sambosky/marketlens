# MarketLens

> A cited stock-**research** assistant (not an advice engine). Ask a question; MarketLens routes it to the right source — SEC filings (RAG), recent news (RAG), live market data, or your portfolio — and answers with **inline citations**. It never says buy/sell.

Built to showcase a production-shaped RAG stack:

- **Google ADK** multi-agent orchestration (planning/router → composition) with the model behind LiteLLM — **local Ollama by default (no API key), swappable to Claude**.
- **RAG over Postgres + pgvector** with **local `fastembed` embeddings** (keyless).
- **Dishka** dependency injection that owns open connections (DB engine, HTTP clients, embedding model) with proper async lifecycle + scopes.
- **FastAPI** with SSE streaming; Repository + Unit-of-Work persistence.
- A **Model Context Protocol (MCP) server** that re-exposes the skills so you can use MarketLens as a tool inside **Claude Desktop / Cursor**.
- **Next.js** UI: chat with citations + a Tools panel + portfolio/watchlist/alerts/journal dashboards.
- **Real, free data**: SEC EDGAR filings + yfinance quotes/news (no API keys).

> ⚠️ Research/monitoring tool only. Not financial advice. Action skills (watchlist, price alerts, trade journal) are **non-executing** — there is no brokerage integration.

## The skills (routing showcase)

| Question | Skill | Source |
|---|---|---|
| "What were NVDA's latest margins?" | fundamentals | SEC filings (RAG) |
| "Why did TSLA move today?" | news | recent news (RAG) |
| "What's AAPL's price and P/E?" | market-data | live (yfinance) |
| "How's my MSFT position?" | portfolio | your holdings (read-only) |
| "Add NVDA to my watchlist" | watchlist/alerts/journal | non-executing actions |

## Quick start

```bash
cp .env.example .env          # defaults need NO credentials
# (set MARKETLENS_SEC_USER_AGENT to your email — SEC requires a contact UA)
docker compose up --build     # db + pgvector, ollama (pulls the model), backend, frontend
docker compose run --rm ingest   # fetch + embed SEC filings/news, seed demo portfolio
```

Then open <http://localhost:3000>. API docs at <http://localhost:8000/docs>.

For Claude-quality answers, set `MARKETLENS_LLM__PROVIDER=anthropic` and `ANTHROPIC_API_KEY` in `.env`.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md). Inspired by the patterns of a production multi-agent RAG system, re-implemented clean-room for the stock-research domain.
