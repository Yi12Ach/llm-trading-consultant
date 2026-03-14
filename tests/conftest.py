from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_finnhub_client():
    client = MagicMock()
    client.get_quote.return_value = {
        "c": 189.84,
        "d": 2.34,
        "dp": 1.25,
        "h": 191.0,
        "l": 188.0,
        "o": 188.50,
        "pc": 187.50,
        "t": 1710000000,
    }
    client.get_company_profile.return_value = {
        "country": "US",
        "currency": "USD",
        "exchange": "NASDAQ",
        "ipo": "1980-12-12",
        "marketCapitalization": 2950000,
        "name": "Apple Inc",
        "shareOutstanding": 15400,
        "ticker": "AAPL",
        "weburl": "https://www.apple.com/",
        "logo": "https://static.finnhub.io/logo/87cb30d8-80df-11ea-8951-00000000092a.png",
        "finnhubIndustry": "Technology",
    }
    client.get_company_news.return_value = [
        {
            "category": "company news",
            "datetime": 1710000000,
            "headline": "Apple releases new product line",
            "id": 1,
            "image": "",
            "related": "AAPL",
            "source": "Reuters",
            "summary": "Apple Inc announced a new product line today.",
            "url": "https://example.com/news/1",
        }
    ]
    client.search_symbol.return_value = {
        "count": 1,
        "result": [
            {
                "description": "APPLE INC",
                "displaySymbol": "AAPL",
                "symbol": "AAPL",
                "type": "Common Stock",
            }
        ],
    }
    client.get_basic_financials.return_value = {
        "metric": {
            "peBasicExclExtraTTM": 28.5,
            "epsBasicExclExtraAnnual": 6.43,
            "52WeekHigh": 199.62,
            "52WeekLow": 164.08,
            "dividendYieldIndicatedAnnual": 0.5,
            "pbAnnual": 45.2,
        },
        "series": {},
    }
    return client


@pytest.fixture
def sample_history():
    return [
        {"role": "user", "content": "What is Apple's ticker?"},
        {"role": "assistant", "content": "Apple's ticker is AAPL."},
    ]
