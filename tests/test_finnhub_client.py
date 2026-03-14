from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.finnhub.client import FinnhubClient, FinnhubError


@pytest.fixture
def client_and_mock():
    with patch("app.finnhub.client.finnhub.Client") as MockSDK:
        mock_sdk = MagicMock()
        MockSDK.return_value = mock_sdk
        client = FinnhubClient(api_key="test-key")
        yield client, mock_sdk


def test_get_quote_returns_dict(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.quote.return_value = {"c": 189.84, "d": 2.34, "dp": 1.25}

    result = client.get_quote("AAPL")

    mock_sdk.quote.assert_called_once_with("AAPL")
    assert isinstance(result, dict)
    assert "c" in result


def test_get_company_profile_returns_dict(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_profile2.return_value = {"name": "Apple Inc", "ticker": "AAPL"}

    result = client.get_company_profile("AAPL")

    mock_sdk.company_profile2.assert_called_once_with(symbol="AAPL")
    assert result["name"] == "Apple Inc"


def test_get_company_news_defaults_dates(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_news.return_value = []

    client.get_company_news("AAPL", from_date="", to_date="")

    ticker, kwargs = mock_sdk.company_news.call_args
    assert ticker[0] == "AAPL"
    # if there ar eno dates provided the clients takes the today's date
    assert kwargs["_from"] != ""
    assert kwargs["to"] != ""

    # Verify the default from_date is within the last 8 days
    from_date = date.fromisoformat(kwargs["_from"])
    assert date.today() - timedelta(days=8) < from_date <= date.today()


def test_get_company_news_respects_explicit_dates(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_news.return_value = []

    client.get_company_news("AAPL", from_date="2024-01-01", to_date="2024-01-07")

    _, kwargs = mock_sdk.company_news.call_args
    assert kwargs["_from"] == "2024-01-01"
    assert kwargs["to"] == "2024-01-07"

    # Verify both dates are valid YYYY-MM-DD format
    date.fromisoformat(kwargs["_from"])
    date.fromisoformat(kwargs["to"])


def test_search_symbol_returns_dict(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.symbol_lookup.return_value = {"count": 1, "result": []}

    result = client.search_symbol("Apple")

    mock_sdk.symbol_lookup.assert_called_once_with("Apple")
    assert "count" in result
    assert result["count"] == 1


def test_get_basic_financials_returns_dict(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_basic_financials.return_value = {"metric": {}, "series": {}}

    result = client.get_basic_financials("AAPL")

    mock_sdk.company_basic_financials.assert_called_once_with("AAPL", "all")
    assert "metric" in result
    assert "series" in result
    assert result["metric"] == {}
    assert result["series"] == {}

# ============================ Exceptions tests ======================================

def test_get_quote_raises_finnhub_error_on_sdk_exception(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.quote.side_effect = RuntimeError("network error")

    with pytest.raises(FinnhubError, match="AAPL"):
        client.get_quote("AAPL")


def test_get_company_profile_raises_finnhub_error_on_sdk_exception(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_profile2.side_effect = RuntimeError("timeout")

    with pytest.raises(FinnhubError, match="TSLA"):
        client.get_company_profile("TSLA")


def test_search_symbol_raises_finnhub_error_on_sdk_exception(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.symbol_lookup.side_effect = RuntimeError("network error")

    with pytest.raises(FinnhubError, match="Apple"):
        client.search_symbol("Apple")


def test_get_basic_financials_raises_finnhub_error_on_sdk_exception(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_basic_financials.side_effect = RuntimeError("timeout")

    with pytest.raises(FinnhubError, match="AAPL"):
        client.get_basic_financials("AAPL")


def test_get_company_news_raises_finnhub_error_on_sdk_exception(client_and_mock):
    client, mock_sdk = client_and_mock
    mock_sdk.company_news.side_effect = RuntimeError("network error")

    with pytest.raises(FinnhubError, match="AAPL"):
        client.get_company_news("AAPL")
