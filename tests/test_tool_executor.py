import json

from app.tools.executor import execute_tool_call

def test_execute_get_stock_quote_calls_correct_method(mock_finnhub_client):
    execute_tool_call("get_stock_quote", {"symbol": "AAPL"}, mock_finnhub_client)
    mock_finnhub_client.get_quote.assert_called_once_with("AAPL")


def test_execute_get_company_profile_calls_correct_method(mock_finnhub_client):
    execute_tool_call("get_company_profile", {"symbol": "MSFT"}, mock_finnhub_client)
    mock_finnhub_client.get_company_profile.assert_called_once_with("MSFT")


def test_execute_get_company_news_passes_optional_dates(mock_finnhub_client):
    execute_tool_call(
        "get_company_news",
        {"symbol": "AAPL", "from_date": "2024-01-01", "to_date": "2024-01-07"},
        mock_finnhub_client,
    )
    mock_finnhub_client.get_company_news.assert_called_once_with(
        "AAPL", from_date="2024-01-01", to_date="2024-01-07"
    )


def test_execute_get_company_news_defaults_dates_when_absent(mock_finnhub_client):
    execute_tool_call("get_company_news", {"symbol": "AAPL"}, mock_finnhub_client)
    mock_finnhub_client.get_company_news.assert_called_once_with(
        "AAPL", from_date="", to_date=""
    )


def test_execute_search_symbol_calls_correct_method(mock_finnhub_client):
    execute_tool_call("search_symbol", {"query": "Palantir"}, mock_finnhub_client)
    mock_finnhub_client.search_symbol.assert_called_once_with("Palantir")


def test_execute_get_basic_financials_calls_correct_method(mock_finnhub_client):
    execute_tool_call("get_basic_financials", {"symbol": "NVDA"}, mock_finnhub_client)
    mock_finnhub_client.get_basic_financials.assert_called_once_with("NVDA")


def test_execute_returns_json_string(mock_finnhub_client):
    result = execute_tool_call("get_stock_quote", {"symbol": "AAPL"}, mock_finnhub_client)
    assert isinstance(result, str)
    parsed = json.loads(result)
    assert isinstance(parsed, dict)


def test_execute_unknown_tool_returns_error_json(mock_finnhub_client):
    result = execute_tool_call("does_not_exist", {}, mock_finnhub_client)
    parsed = json.loads(result)
    assert "error" in parsed
    assert "does_not_exist" in parsed["error"]


def test_execute_handles_client_exception_gracefully(mock_finnhub_client):
    from app.finnhub.client import FinnhubError

    mock_finnhub_client.get_quote.side_effect = FinnhubError("API down")

    result = execute_tool_call("get_stock_quote", {"symbol": "AAPL"}, mock_finnhub_client)
    parsed = json.loads(result)
    assert "error" in parsed
