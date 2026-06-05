from __future__ import annotations

from retrieval.filings_retriever import FilingsRetriever
from skills.types import Fact, SkillResult

NAME = "search_filings"
EXCERPT_CHARS = 700


class FundamentalsSkill:
    """RAG over SEC filings — fundamentals, margins, segment detail, risks."""

    def __init__(self, retriever: FilingsRetriever) -> None:
        self._retriever = retriever

    async def run(
        self, query: str, *, tickers: list[str] | None = None, limit: int = 6
    ) -> SkillResult:
        evidence = await self._retriever.retrieve(query, tickers=tickers, limit=limit)
        facts = [Fact(text=e.text[:EXCERPT_CHARS], citation=e.citation) for e in evidence]
        note = None if facts else "No matching filing excerpts in the local corpus (try ingesting first)."
        return SkillResult(
            skill=NAME,
            facts=facts,
            citations=[f.citation for f in facts],
            note=note,
        )
