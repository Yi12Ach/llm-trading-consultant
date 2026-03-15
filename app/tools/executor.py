import json
from collections.abc import Callable
from typing import TYPE_CHECKING

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


def execute_tool_call(tool_name: str, arguments: dict, client: "FinnhubClient") -> str:
    """Execute a named tool with the given arguments and return a JSON string result."""
    handler = _DISPATCH.get(tool_name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = handler(client, arguments)
        return json.dumps(result)
    except Exception as exc:
        return json.dumps({"error": str(exc)})
