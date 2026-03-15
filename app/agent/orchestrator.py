import json

from openai import OpenAI

from app.config import Settings, OpenAISettings
from app.finnhub_client.client import FinnhubClient
from app.tools.definitions import TOOL_DEFINITIONS
from app.tools.executor import execute_tool_call

_SYSTEM_PROMPT = """You are a professional stock market research assistant with access to \
real-time financial data. Answer user questions about stocks and companies clearly and concisely.

Guidelines:
- Always use the provided tools to fetch live data rather than relying on your training \
  knowledge for prices, metrics, or recent news—markets change constantly.
- If the user mentions a company by name and you don't know its ticker, use search_symbol first.
- When comparing multiple stocks, fetch data for each one and present a structured comparison.
- Synthesize tool results into a readable, human-friendly response. Avoid dumping raw JSON.
- If a tool returns an error or empty data, acknowledge it gracefully and offer alternatives.
- Keep responses concise but complete. Use bullet points or short tables for comparisons.
- Prices are in USD unless otherwise specified by the data."""

_MAX_TOOLS_TO_BE_USED = OpenAISettings().MAX_TOOLS_TO_BE_USED # currently set to 5
_MAX_HISTORY_MESSAGES = OpenAISettings().MAX_HISTORY_MESSAGES # currently set to 10
_FALLBACK_RESPONSE = (
    "I wasn't able to complete the analysis. Please try rephrasing your question or "
    "check that the stock symbol is valid."
)


def run_agent(user_message: str, history: list[dict], settings: Settings) -> str:
    """
    Run the OpenAI agentic loop for a single user turn.

    Args:
        user_message: The latest message from the user.
        history: Prior conversation turns (role: user/assistant with plain text content).
        settings: Application settings containing API keys and model name.

    Returns:
        The assistant's final text response.
    """
    openai_client = OpenAI(api_key=settings.openai_api_key)
    finnhub_client = FinnhubClient(api_key=settings.finnhub_api_key)

    messages: list = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        *history[-_MAX_HISTORY_MESSAGES:],
        {"role": "user", "content": user_message},
    ]

    for _ in range(_MAX_TOOLS_TO_BE_USED):
        response = openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

        choice = response.choices[0]

        if choice.finish_reason == "stop":
            return choice.message.content or _FALLBACK_RESPONSE

        if choice.finish_reason == "tool_calls":
            # Append the assistant message (with tool_calls) before processing results
            messages.append(choice.message)

            for tool_call in choice.message.tool_calls:
                arguments = json.loads(tool_call.function.arguments)
                result = execute_tool_call(tool_call.function.name, arguments, finnhub_client)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
        else:
            # Unexpected finish reason
            break

    return _FALLBACK_RESPONSE
