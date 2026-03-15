from datetime import date, timedelta

import finnhub


class FinnhubError(Exception):
    """Raised when the Finnhub API returns an error or the SDK raises."""


class FinnhubClient:
    def __init__(self, api_key: str) -> None:
        self._client = finnhub.Client(api_key=api_key)

    def search_symbol(self, query: str) -> dict:
        """Search for a stock symbol by company name or partial ticker.

        Used by the LLM to resolve company names to ticker symbols before making
        other API calls (e.g. "Apple" → "AAPL").

        Args:
            query: Company name or partial ticker string (e.g. "Apple" or "AAPL").

        Returns:
            dict with a "result" list, each item containing "symbol", "description",
            "type", and "displaySymbol".

            Example::

                {
                    "result": [
                        {
                            "description": "APPLE INC",
                            "displaySymbol": "AAPL",
                            "symbol": "AAPL",
                            "type": "Common Stock"
                        }
                    ]
                }
        """
        try:
            return self._client.symbol_lookup(query)
        except Exception as exc:
            raise FinnhubError(f"Symbol search failed for query: {query}") from exc

    def get_basic_financials(self, symbol: str) -> dict:
        """P/E ratio, EPS, 52-week high/low, dividend yield, and other key metrics.

        Args:
            symbol: Stock ticker symbol (e.g. "AAPL").

        Returns:
            dict with "metric" (key/value financial indicators) and "series"
            (historical time-series data per metric).

            Example::

                {
                    "metric": {
                        "peBasicExclExtraTTM": 28.5,
                        "epsBasicExclExtraAnnual": 6.11,
                        "52WeekHigh": 199.62,
                        "52WeekLow": 124.17,
                        "dividendYieldIndicatedAnnual": 0.55
                    },
                    "series": { ... }
                }
        """
        try:
            return self._client.company_basic_financials(symbol, "all")
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch financials for {symbol}") from exc

    def get_quote(self, symbol: str) -> dict:
        """Current price, daily change, volume for a stock symbol.

        Args:
            symbol: Stock ticker symbol (e.g. "AAPL").

        Returns:
            dict with "c" (current price), "d" (change), "dp" (percent change),
            "h" (day high), "l" (day low), "o" (open), "pc" (previous close),
            and "t" (timestamp).

            Example::

                {
                    "c": 189.43,
                    "d": 1.25,
                    "dp": 0.66,
                    "h": 190.12,
                    "l": 187.88,
                    "o": 188.50,
                    "pc": 188.18,
                    "t": 1711382400
                }
        """
        try:
            return self._client.quote(symbol)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch quote for {symbol}") from exc

    def get_company_profile(self, symbol: str) -> dict:
        """Company name, industry, market cap, country, exchange, website.

        Args:
            symbol: Stock ticker symbol (e.g. "AAPL").

        Returns:
            dict with "name", "ticker", "exchange", "ipo", "marketCapitalization",
            "shareOutstanding", "country", "currency", "industry", and "weburl".

            Example::

                {
                    "name": "Apple Inc",
                    "ticker": "AAPL",
                    "exchange": "NASDAQ/NMS (GLOBAL MARKET)",
                    "ipo": "1980-12-12",
                    "marketCapitalization": 2941485,
                    "shareOutstanding": 15441.88,
                    "country": "US",
                    "currency": "USD",
                    "industry": "Technology",
                    "weburl": "https://www.apple.com/"
                }
        """
        try:
            return self._client.company_profile2(symbol=symbol)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch company profile for {symbol}") from exc

    def get_company_news(self, symbol: str, from_date: str = "", to_date: str = "") -> list[dict]:
        """Recent news articles for a company. Dates in YYYY-MM-DD format.

        Args:
            symbol: Stock ticker symbol (e.g. "AAPL").
            from_date: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
            to_date: End date in YYYY-MM-DD format. Defaults to today.

        Returns:
            List of dicts, each with "headline", "summary", "url", "source",
            "datetime" (Unix timestamp), and "id".

            Example::

                [
                    {
                        "headline": "Apple Unveils New MacBook Pro Models",
                        "summary": "Apple announced updated MacBook Pro laptops...",
                        "url": "https://example.com/apple-macbook-pro",
                        "source": "Reuters",
                        "datetime": 1711382400,
                        "id": 120798372
                    }
                ]
        """
        if not to_date:
            to_date = date.today().isoformat()
        if not from_date:
            from_date = (date.today() - timedelta(days=7)).isoformat()
        try:
            return self._client.company_news(symbol, _from=from_date, to=to_date)
        except Exception as exc:
            raise FinnhubError(f"Failed to fetch news for {symbol}") from exc