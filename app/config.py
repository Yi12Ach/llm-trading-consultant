from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    finnhub_api_key: str
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

class OpenAISettings(BaseSettings):
    MAX_TOOLS_TO_BE_USED: int = 5  # 5 since this is the maximum amount of tools that we can use
    MAX_HISTORY_MESSAGES: int = 20  # keep last 10 conversation turns (user+assistant pairs)

class ExecutorSettings(BaseSettings):
    MAX_NEWS_ITEMS: int = 10
    MAX_SEARCH_RESULTS: int = 10
    MAX_RESULT_CHARS: int = 10000  # hard cap on any single tool result

def get_settings() -> Settings:
    return Settings()
