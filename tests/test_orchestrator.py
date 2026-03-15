from unittest.mock import MagicMock, patch

import pytest

from app.agent.orchestrator import _FALLBACK_RESPONSE, run_agent
from app.config import Settings


@pytest.fixture
def settings():
    return Settings(
        openai_api_key="test-openai-key",
        finnhub_api_key="test-finnhub-key",
        openai_model="gpt-4o-mini",
    )


def _make_stop_response(content: str) -> MagicMock:
    """Build a mock OpenAI response that signals a final text answer."""
    response = MagicMock()
    response.choices[0].finish_reason = "stop"
    response.choices[0].message.content = content
    response.choices[0].message.tool_calls = None
    return response


def _make_tool_call_response(tool_name: str, arguments: str, call_id: str = "call_1") -> MagicMock:
    """Build a mock OpenAI response that requests a tool call."""
    tool_call = MagicMock()
    tool_call.id = call_id
    tool_call.function.name = tool_name
    tool_call.function.arguments = arguments

    response = MagicMock()
    response.choices[0].finish_reason = "tool_calls"
    response.choices[0].message.tool_calls = [tool_call]
    return response


@patch("app.agent.orchestrator.FinnhubClient")
@patch("app.agent.orchestrator.OpenAI")
def test_no_tool_call_returns_directly(MockOpenAI, settings):
    mock_create = MockOpenAI.return_value.chat.completions.create
    mock_create.return_value = _make_stop_response("Apple is at $189.")

    result = run_agent("How is AAPL?", [], settings)

    assert result == "Apple is at $189."
    assert mock_create.call_count == 1


@patch("app.agent.orchestrator.FinnhubClient")
@patch("app.agent.orchestrator.OpenAI")
def test_single_tool_call_round_trip(MockOpenAI, MockFinnhub, settings, mock_finnhub_client):
    MockFinnhub.return_value = mock_finnhub_client
    mock_create = MockOpenAI.return_value.chat.completions.create
    mock_create.side_effect = [
        _make_tool_call_response("get_stock_quote", '{"symbol": "AAPL"}'),
        _make_stop_response("AAPL is trading at $189.84, up 1.25% today."),
    ]

    result = run_agent("How is AAPL?", [], settings)

    assert "AAPL" in result
    assert mock_create.call_count == 2
    mock_finnhub_client.get_quote.assert_called_once_with("AAPL")


@patch("app.agent.orchestrator.FinnhubClient")
@patch("app.agent.orchestrator.OpenAI")
def test_max_iterations_guard(MockOpenAI, MockFinnhub, settings, mock_finnhub_client):
    MockFinnhub.return_value = mock_finnhub_client
    mock_create = MockOpenAI.return_value.chat.completions.create
    # Always return a tool call - should eventually hit the iteration limit
    mock_create.return_value = _make_tool_call_response("get_stock_quote", '{"symbol": "AAPL"}')

    result = run_agent("How is AAPL?", [], settings)

    assert result == _FALLBACK_RESPONSE
    assert mock_create.call_count == 5  # _MAX_ITERATIONS


@patch("app.agent.orchestrator.FinnhubClient")
@patch("app.agent.orchestrator.OpenAI")
def test_history_is_included_in_messages(MockOpenAI, MockFinnhub, settings, sample_history):
    mock_create = MockOpenAI.return_value.chat.completions.create
    mock_create.return_value = _make_stop_response("AAPL is at $189.")

    run_agent("What about the price now?", sample_history, settings)

    call_args = mock_create.call_args
    messages = call_args.kwargs["messages"]

    # Should have system prompt + 2 history messages + new user message
    roles = [m["role"] if isinstance(m, dict) else m.role for m in messages]
    assert roles[0] == "system"
    assert "user" in roles
    assert "assistant" in roles
    # Verify history content is present
    contents = [m["content"] if isinstance(m, dict) else m.content for m in messages]
    assert any("Apple's ticker" in str(c) for c in contents)


@patch("app.agent.orchestrator.FinnhubClient")
@patch("app.agent.orchestrator.OpenAI")
def test_multiple_tool_calls_in_single_response(
    MockOpenAI, MockFinnhub, settings, mock_finnhub_client
):
    MockFinnhub.return_value = mock_finnhub_client

    # Build a response with two tool calls
    tool_call_1 = MagicMock()
    tool_call_1.id = "call_1"
    tool_call_1.function.name = "get_stock_quote"
    tool_call_1.function.arguments = '{"symbol": "AAPL"}'

    tool_call_2 = MagicMock()
    tool_call_2.id = "call_2"
    tool_call_2.function.name = "get_company_profile"
    tool_call_2.function.arguments = '{"symbol": "AAPL"}'

    first_response = MagicMock()
    first_response.choices[0].finish_reason = "tool_calls"
    first_response.choices[0].message.tool_calls = [tool_call_1, tool_call_2]

    mock_create = MockOpenAI.return_value.chat.completions.create
    mock_create.side_effect = [
        first_response,
        _make_stop_response("Apple profile and quote fetched."),
    ]

    result = run_agent("Tell me about AAPL", [], settings)

    assert result == "Apple profile and quote fetched."
    mock_finnhub_client.get_quote.assert_called_once_with("AAPL")
    mock_finnhub_client.get_company_profile.assert_called_once_with("AAPL")
