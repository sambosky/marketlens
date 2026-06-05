from __future__ import annotations

from retrieval.news_retriever import NewsRetriever
from skills.types import Fact, SkillResult

NAME = "search_news"
EXCERPT_CHARS = 600


class NewsSkill:
    """RAG over recent news — "why did it move?", sentiment, catalysts."""

    def __init__(self, retriever: NewsRetriever) -> None:
        self._retriever = retriever

    async def run(
        self, query: str, *, tickers: list[str] | None = None, limit: int = 6
    ) -> SkillResult:
        evidence = await self._retriever.retrieve(query, tickers=tickers, limit=limit)
        facts = [Fact(text=e.text[:EXCERPT_CHARS], citation=e.citation) for e in evidence]
        note = None if facts else "No matching news in the local corpus (try ingesting first)."
        return SkillResult(
            skill=NAME,
            facts=facts,
            citations=[f.citation for f in facts],
            note=note,
        )
