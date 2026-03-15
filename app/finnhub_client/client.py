from datetime import date, timedelta

import finnhub


class FinnhubError(Exception):
    """Raised when the Finnhub API returns an error or the SDK raises."""


class FinnhubClient:
    def __init__(self, api_key: str) -> None:
        self._client = finnhub.Client(api_key=api_key)

    def search_symbol(self, query: str) -> dict:
        """Search for a stock symbol by company name or partial ticker."""
        try:
            return self._client.symbol_lookup(query)
        except Exception as exc:
            raise FinnhubError(f"Symbol search failed for query: {query}") from exc

    def get_basic_financials(self, symbol: str) -> dict:
        """P/E ratio, EPS, 52-week high/low, dividend yield, and other key metrics."""
        try:
            return self._client.company_basic_financials(symbol, "all")
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch financials for {symbol}") from exc

    def get_quote(self, symbol: str) -> dict:
        """Current price, daily change, volume for a stock symbol."""
        try:
            return self._client.quote(symbol)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch quote for {symbol}") from exc

    def get_company_profile(self, symbol: str) -> dict:
        """Company name, industry, market cap, country, exchange, website."""
        try:
            return self._client.company_profile2(symbol=symbol)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch company profile for {symbol}") from exc

    def get_company_news(self, symbol: str, from_date: str = "", to_date: str = "") -> list[dict]:
        """Recent news articles for a company. Dates in YYYY-MM-DD format."""
        if not to_date:
            to_date = date.today().isoformat()
        if not from_date:
            from_date = (date.today() - timedelta(days=7)).isoformat()
        try:
            return self._client.company_news(symbol, _from=from_date, to=to_date)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch news for {symbol}") from exc


