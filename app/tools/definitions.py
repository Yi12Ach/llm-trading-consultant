TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_quote",
            "description": (
                "Get the real-time price, daily percentage change, open/close/high/low prices, "
                "and trading volume for a stock. Use this when the user asks about the current "
                "price, how a stock is doing today, or its recent performance."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g. AAPL, TSLA, MSFT.",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_profile",
            "description": (
                "Get a company's profile including its full name, industry sector, market "
                "capitalisation, country, stock exchange, and website. Use this when the user "
                "asks about what a company does, its size, or its sector."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g. AAPL, TSLA, MSFT.",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_news",
            "description": (
                "Get recent news articles about a company. Use this when the user asks about "
                "recent news, events, or what is happening with a company. Returns headlines "
                "and summaries from the past 7 days by default."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g. AAPL, TSLA, MSFT.",
                    },
                    "from_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format. Defaults to 7 days ago.",
                    },
                    "to_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format. Defaults to today.",
                    },
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_symbol",
            "description": (
                "Search for a stock ticker symbol by company name or partial name. Use this "
                "when the user mentions a company by name but you do not know its ticker symbol, "
                "e.g. 'Palantir', 'the electric car company', 'the big oil company from Texas'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The company name or partial ticker to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_basic_financials",
            "description": (
                "Get fundamental financial metrics including P/E ratio, EPS, 52-week high/low, "
                "price-to-book ratio, dividend yield, and revenue growth. Use this when the user "
                "asks about valuation, fundamentals, financial health, or wants to compare "
                "companies on financial metrics."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol, e.g. AAPL, TSLA, MSFT.",
                    }
                },
                "required": ["symbol"],
            },
        },
    },
]
