# Stock Insights Assistant

Stock Insights Assistant is a conversational AI application that lets you research stocks using plain English. Instead of navigating complex financial platforms or writing code to query APIs, you simply ask a question in natural language and the assistant handles everything — fetching live market data, interpreting it, and responding in a clear, readable format.

It is built for anyone who wants fast, accurate stock information without needing a finance background or technical expertise. Whether you are a casual investor checking in on a position, a developer exploring LLM tool-use patterns, or a trader wanting a quick overview of a company, this app gives you a conversational interface backed by real-time data.

Under the hood, the app combines the reasoning capabilities of OpenAI's models with live market data from [Finnhub](https://finnhub.io). The LLM acts as an intelligent orchestrator — it reads your question, decides what data to fetch, calls the appropriate tools, and composes a human-friendly answer. You never interact with raw API responses or financial data structures directly.

> "How is AAPL doing today?" → The assistant fetches live data and responds conversationally.

---

## What it does

You type a question like *"Compare TSLA and Ford"* or *"What's NVDA's 52-week high?"* and the app:

1. Sends your question to an OpenAI model
2. The model decides which stock data to fetch (quotes, news, financials, etc.)
3. It calls the [Finnhub](https://finnhub.io) API to get the real-time data
4. Returns a plain-text answer back to you in the chat

---

## Running locally with Docker

This is the easiest way — no Python setup needed. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your machine (it includes Docker Compose).

**Step 1 — Get your API keys**

You need two free API keys:
- **OpenAI**: https://platform.openai.com/api-keys
- **Finnhub**: https://finnhub.io (free tier is enough)

**Step 2 — Create your `.env` file**

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys:

```
OPENAI_API_KEY=sk-...
FINNHUB_API_KEY=your_finnhub_key_here
OPENAI_MODEL=gpt-4o-mini
```

**Step 3 — Start the app**

```bash
docker compose up
```

Open http://localhost:8501 in your browser. That's it.

To stop it: `Ctrl+C`, then `docker compose down`.

---

## Running locally without Docker

**Step 1 — Create a virtual environment**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

**Step 2 — Install dependencies**

```bash
pip install -r requirements-dev.txt
```

**Step 3 — Create your `.env` file**

```bash
cp .env.example .env
```

Then open `.env` and fill in your keys:

```
OPENAI_API_KEY=sk-...
FINNHUB_API_KEY=your_finnhub_key_here
OPENAI_MODEL=gpt-4o-mini
```

**Step 4 — Run the app**

```bash
streamlit run app/main.py
```

Open http://localhost:8501 in your browser.

---

## Example questions to try

- "How is AAPL doing today?"
- "Compare TSLA and Ford"
- "What are Apple's key financial metrics?"
- "Any recent news about Microsoft?"
- "Find the ticker for Palantir"
- "What's NVDA's 52-week high?"

---

## How it works (architecture)

```mermaid
flowchart TD
    A([User types a question]) --> B[Streamlit UI]
    B --> C[Orchestrator]
    C --> D[OpenAI API]
    D --> E{Needs more data?}

    E -->|Yes - tool call| F[Tool Executor]
    F --> G[Finnhub Client]
    G --> H[(Finnhub API)]
    H --> G
    G --> F
    F --> C
    C --> D

    E -->|No - final answer| I[OpenAI generates response]
    I --> B
    B --> J([Answer displayed to user])
```

The orchestrator runs an agentic loop — it keeps asking OpenAI what to do next until the model has enough data to produce a final answer. OpenAI can invoke up to 5 tools per turn, each of which maps to a specific Finnhub endpoint (quote, profile, news, financials, symbol search). Once OpenAI signals it is done, the final text response is rendered in the chat UI.

---

## Running tests

```bash
pip install -r requirements-dev.txt
pytest -v
```

All tests mock external API calls — no real keys required.

---

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `FINNHUB_API_KEY` | Your Finnhub API key |
| `OPENAI_MODEL` | Model to use (default: `gpt-4o-mini`) |

---

## AI Assistants used

The following AI tools were used during the development of this project:

- **[Claude Code](https://claude.ai/code)** — Anthropic's CLI coding assistant, used for code generation, refactoring, and architecture decisions
- **[ChatGPT](https://chatgpt.com)** — Used for brainstorming, drafting, and general Q&A during development

---

## Project Limitations

### Functional

- **Max 5 tool calls per turn** — the orchestrator is hardcoded to a maximum of 5 Finnhub API calls per question, so very complex multi-stock queries may get cut short
- **Conversation history persistent** — chat history lives only in the Streamlit session; refreshing the page wipes it
- **US-centric data** — Finnhub's free tier has limited coverage for non-US exchanges
- **No data visualisation** — responses are text-only; no charts or graphs are rendered

### Architectural

- **Context window limit** — the full conversation history is sent to OpenAI on every turn. In long sessions, accumulated messages and large tool responses (e.g. news articles, financial metrics) can exceed the model's 128k token limit, resulting in a `context_length_exceeded` error. Keeping sessions shorter or clearing chat history avoids this
- **Sequential tool execution** — when OpenAI requests multiple tool calls in one turn, they run one after another rather than in parallel, making multi-stock queries slower
- **No caching** — every question hits the Finnhub API fresh, even if the same stock data was already fetched moments ago in the same session
- **No retry/backoff logic** — if Finnhub returns an error, the tool executor returns it as-is with no retry attempt
- **Tight coupling in orchestrator** — the OpenAI and Finnhub clients are instantiated directly inside `run_agent()`, making it harder to swap providers or mock in tests