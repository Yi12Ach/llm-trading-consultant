import json
from collections.abc import Callable
from typing import TYPE_CHECKING

from app.config import ExecutorSettings

if TYPE_CHECKING:
    from app.finnhub_client.client import FinnhubClient


def _news_handler(client: "FinnhubClient", args: dict) -> list[dict]:
    return client.get_company_news(
        args["symbol"],
        from_date=args.get("from_date", ""),
        to_date=args.get("to_date", ""),
    )


_DISPATCH: dict[str, Callable] = {
    "get_stock_quote": lambda c, args: c.get_quote(args["symbol"]),
    "get_company_profile": lambda c, args: c.get_company_profile(args["symbol"]),
    "get_company_news": _news_handler,
    "search_symbol": lambda c, args: c.search_symbol(args["query"]),
    "get_basic_financials": lambda c, args: c.get_basic_financials(args["symbol"]),
}


_MAX_NEWS_ITEMS = ExecutorSettings().MAX_NEWS_ITEMS
_MAX_SEARCH_RESULTS = ExecutorSettings().MAX_SEARCH_RESULTS
_MAX_RESULT_CHARS = ExecutorSettings().MAX_RESULT_CHARS # hard cap on any single tool result


def _truncate(result: str) -> str:
    if len(result) > _MAX_RESULT_CHARS:
        return result[:_MAX_RESULT_CHARS] + "\n... [truncated]"
    return result


def execute_tool_call(tool_name: str, arguments: dict, client: "FinnhubClient") -> str:
    """Execute a named tool with the given arguments and return a JSON string result."""
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = handler(client, arguments)
        if tool_name == "get_company_news" and isinstance(result, list):
            result = result[:_MAX_NEWS_ITEMS]
        if tool_name == "search_symbol" and isinstance(result, dict):
            result["result"] = result.get("result", [])[:_MAX_SEARCH_RESULTS]
        return _truncate(json.dumps(result))
    except Exception as exc:
        return json.dumps({"error": str(exc)})
