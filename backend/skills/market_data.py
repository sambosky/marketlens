from __future__ import annotations

from infra.marketdata.types import MarketData
from retrieval.interfaces import Citation
from skills.types import SkillResult

NAME = "get_quote"


class MarketDataSkill:
    """Live market data — current price, P/E, day range, market cap."""

    def __init__(self, market: MarketData) -> None:
        self._market = market

    async def run(self, ticker: str) -> SkillResult:
        quote = await self._market.get_quote(ticker)
        if quote is None:
            return SkillResult(
                skill=NAME,
                note=f"Live market data for {ticker.upper()} is unavailable right now.",
            )
        citation = Citation(source=quote.source, detail=f"as of {quote.as_of.isoformat()}")
        summary_bits = [f"{quote.ticker}"]
        if quote.price is not None:
            summary_bits.append(f"price {quote.price:.2f} {quote.currency or ''}".strip())
        if quote.change_percent is not None:
            summary_bits.append(f"{quote.change_percent:+.2f}% today")
        if quote.pe_ratio is not None:
            summary_bits.append(f"P/E {quote.pe_ratio:.1f}")
        return SkillResult(
            skill=NAME,
            summary=" · ".join(summary_bits),
            data=quote.model_dump(mode="json"),
            citations=[citation],
        )
