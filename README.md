# Stock Insights Assistant

A natural language interface for querying real-time stock data, powered by OpenAI function calling and Finnhub.io.

## Quick Start

```bash
cp .env.example .env
# Add your OPENAI_API_KEY and FINNHUB_API_KEY to .env
docker compose up
```

Open http://localhost:8501 in your browser.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `FINNHUB_API_KEY` | Your Finnhub API key (free tier at finnhub.io) |
| `OPENAI_MODEL` | Model to use (default: `gpt-4o-mini`) |

## Architecture

```
User (Streamlit UI)
      │
  app/ui/              ← chat rendering, sidebar
      │
  app/agent/           ← OpenAI agentic loop (orchestrator.py)
      │
  app/tools/           ← tool schemas (definitions.py) + dispatcher (executor.py)
      │
  app/finnhub/         ← Finnhub HTTP client (client.py)
      │
  Finnhub API / OpenAI API
```

**Data layer** (`app/finnhub/client.py`): A thin wrapper around the `finnhub-python` SDK. Each method maps 1:1 to one endpoint—no business logic. All SDK exceptions are re-raised as `FinnhubError` so upper layers stay decoupled from SDK internals.

**Tools layer** (`app/tools/`): `definitions.py` holds the OpenAI JSON schemas passed to `chat.completions.create`. `executor.py` dispatches tool calls to the Finnhub client and returns JSON strings ready for the `role: "tool"` message.

**Agent layer** (`app/agent/orchestrator.py`): Implements the standard OpenAI agentic loop. On each iteration, if the model requests tool calls, they are executed and results appended before the next completion request. A `max_iterations=5` guard prevents runaway loops. Only the final plain-text answer is returned to the UI—intermediate tool messages are discarded.

**UI layer** (`app/ui/`, `app/main.py`): Streamlit chat interface. Session state holds only user/assistant message pairs with plain text content.

## Running Locally (without Docker)

```bash
pip install ".[dev]"
cp .env.example .env  # fill in your keys
streamlit run app/main.py
```

## Running Tests

```bash
pip install ".[dev]"
pytest -v
```

All tests mock external API calls—no real keys required to run the test suite.

## Linting

```bash
ruff check .
```

## Example Questions

- "How is AAPL doing today?"
- "Compare TSLA and F"
- "What are Apple's key financial metrics?"
- "Any recent news about Microsoft?"
- "Find the ticker for Palantir"
- "What's NVDA's 52-week high?"

## Trade-offs & Decisions

**OpenAI function calling over rule-based parsing**: The LLM decides which Finnhub endpoints to call based on the user's question. This handles ambiguity naturally (e.g., company names vs tickers, multi-step comparisons) without maintaining a brittle query parser.

**Stateless orchestrator**: The `run_agent` function is pure—it takes history as an argument and returns a string. This keeps the agent testable without Streamlit and separates session management from AI logic.

**Intermediate tool messages discarded**: Only user/assistant plain-text pairs are stored in session state. The agentic loop's internal tool messages are transient. This keeps the UI clean and prevents raw JSON from appearing in the chat history.

**`finnhub-python` SDK over raw HTTP**: The official SDK handles auth and request formatting. It's wrapped behind `FinnhubClient` so tests can mock at the boundary without patching `httpx` or `requests`.

## What I'd Improve with More Time

- **Streaming responses**: Stream the final OpenAI answer token-by-token using `st.write_stream` for a better UX on longer responses.
- **Caching**: Add a short TTL cache (e.g., 60s) on Finnhub quote calls to reduce API usage when the same symbol is queried repeatedly in a session.
- **Rate limit handling**: Detect Finnhub 429 responses and surface a helpful message rather than a generic error.
- **Symbol validation**: Validate that a symbol exists before calling all endpoints, to give clearer errors for typos.
- **Charting**: Add a simple price history chart using `st.line_chart` for a richer visual experience.

## AI Tools Used

- **Claude (Anthropic)**: Used throughout development for architecture planning, implementation, test design, and review. Claude helped design the layered architecture, wrote initial implementations for each module, and suggested the agentic loop pattern with the `max_iterations` guard. All AI suggestions were reviewed and adjusted—particularly the tool description strings, which required iterative refinement to get correct tool selection behavior.
