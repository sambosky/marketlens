"""yfinance-backed live market data (keyless).

yfinance is synchronous and occasionally rate-limited, so calls run in a worker
thread and failures degrade gracefully to ``None`` (the skill layer then reports
"live data unavailable" rather than crashing the answer).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from infra.marketdata.types import Quote


class YFinanceMarketData:
    async def get_quote(self, ticker: str) -> Quote | None:
        return await asyncio.to_thread(self._fetch, ticker)

    def _fetch(self, ticker: str) -> Quote | None:
        import yfinance as yf

        try:
            t = yf.Ticker(ticker)
            fast = dict(t.fast_info or {})
        except Exception:
            return None

        price = _num(fast.get("last_price") or fast.get("lastPrice"))
        prev = _num(fast.get("previous_close") or fast.get("previousClose"))

        # PE ratio isn't in fast_info; .info is slower and sometimes empty.
        pe = None
        try:
            info = t.get_info()
            pe = _num(info.get("trailingPE"))
        except Exception:
            info = {}

        change = (price - prev) if (price is not None and prev is not None) else None
        change_pct = (change / prev * 100.0) if (change is not None and prev) else None

        return Quote(
            ticker=ticker.upper(),
            price=price,
            currency=fast.get("currency"),
            previous_close=prev,
            change=change,
            change_percent=change_pct,
            market_cap=_num(fast.get("market_cap") or fast.get("marketCap")),
            pe_ratio=pe,
            day_high=_num(fast.get("day_high") or fast.get("dayHigh")),
            day_low=_num(fast.get("day_low") or fast.get("dayLow")),
            as_of=datetime.now(timezone.utc),
        )


def _num(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
