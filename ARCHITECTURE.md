# Architecture

MarketLens is a cited stock-**research** assistant. A question is routed to the
right source (SEC filings, news, live prices, or the user's portfolio), and the
answer is synthesized from **cited facts** — never advice.

## Request flow

```
Next.js UI ──POST /api/ask (SSE)──▶ FastAPI ──▶ ADK Runner
                                                   │
                              ┌────────────────────┴───────────────────┐
                              ▼                                         ▼
                    Planning agent (triage +              Composition agent
                    skill routing via FunctionTools)      (cited, non-advisory
                              │                            synthesis)
                              ▼
                 ┌──────── SHARED SKILL LAYER (7 skills) ───────┐
   fundamentals · news · market-data · portfolio · watchlist/alerts/journal
        │            │          │            │             │
   pgvector RAG   pgvector   yfinance    Postgres repos (Dishka) + Unit of Work
   (filings)      (news)     (live)
```

1. The browser POSTs the question; FastAPI streams Server-Sent Events back.
2. ADK runs a `SequentialAgent`: the **planner** triages the question and calls
   the relevant skill **FunctionTools**, writing cited findings to session
   state; the **composer** turns those into a grounded answer with inline `[n]`
   citations and a Sources list, refusing to give buy/sell advice.
3. The runner (`agents/runner.py`) translates ADK events into small SSE events:
   `routing` chips, collected `sources`, and the `final` answer.

The model behind ADK is `LiteLlm` — **local Ollama by default, Claude by
config** (`MARKETLENS_LLM__PROVIDER`). Nothing else changes when you switch.

## The skills are a shared core

`skills/adk_tools.py` defines each skill once as a typed async function. The same
functions are consumed three ways, with no duplicated logic:

- **ADK** loads them as `FunctionTool`s (the internal request path).
- The **`/tools` API** lists + invokes them (the UI Tools panel).
- The **MCP server** (`mcp_server/server.py`) re-exposes them — plus a top-level
  `ask_marketlens` tool — so the assistant is usable inside Claude Desktop /
  Cursor. MCP is an external add-on; it is never in the app's own request path.

## Dependency injection (Dishka)

`infra/container.py` builds one async container. APP-scoped providers own the
open connections and clean them up on shutdown via `AsyncIterable` `yield …
finally`:

| Provider | Owns | Cleanup |
|---|---|---|
| `DbProvider` | async engine, sessionmaker, UoW | `engine.dispose()` |
| `HttpClientProvider` | shared `httpx.AsyncClient` | `aclose()` |
| `EmbeddingProvider` | fastembed model (loaded once) | — |
| `LLMProvider` | ADK `LiteLlm` | — |
| `MarketDataProvider` | yfinance source | — |
| `RepositoryProvider` / skills | repos, retrievers, skills | — |

FastAPI routes receive dependencies via `FromDishka[...]` (request scope). The
agent tools resolve skills from the same container (APP scope), bound at startup.

## Persistence

- **Repository pattern** over SQLAlchemy 2.0 async (`core/**/repo.py`).
- **Unit of Work + `ContextVar`** (`infra/db/uow.py`): repos inside a UoW share
  one transaction; outside, each call opens-and-commits its own session
  (`core/sqlalchemy_repo.py`). The action skills wrap their writes in a UoW.
- **RAG corpus** lives in `filing_chunk` / `news_chunk` with `vector(384)`
  columns (HNSW cosine indexes); embeddings come from local `fastembed`.

## Ingestion

`ingestion/` fetches **real, free** data: SEC EDGAR filings (ticker→CIK→recent
10-K/10-Q/8-K→primary-doc text) and yfinance news, chunks + embeds them into
pgvector, and seeds a demo portfolio/watchlist. Run via `python -m ingestion.cli all`.

## Safety by design

- The composer prompt forbids buy/sell/hold recommendations and price
  predictions; advice questions get cited facts + a "not financial advice" note.
- Action skills (`watchlist`, `alerts`, `journal`) are **non-executing** — they
  write to the local DB only. There is no brokerage integration.
