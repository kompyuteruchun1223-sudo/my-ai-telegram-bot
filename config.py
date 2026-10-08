import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Required environment variable '{name}' is missing. "
            "Create a .env file and add the required value."
        )
    return value


def optional_int_env(name: str) -> int | None:
    value = os.getenv(name, "").strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable '{name}' must be an integer.") from exc


def int_env(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable '{name}' must be an integer.") from exc


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    openai_api_key: str
    openai_model: str
    admin_id: int | None
    database_path: str
    max_history: int
    rate_limit_requests: int
    rate_limit_window_seconds: int
    max_user_message_chars: int
    log_level: str


settings = Settings(
    telegram_bot_token=required_env("TELEGRAM_BOT_TOKEN"),
    openai_api_key=required_env("OPENAI_API_KEY"),
    openai_model=os.getenv("OPENAI_MODEL", "gpt-6-luna").strip(),
    admin_id=optional_int_env("ADMIN_ID"),
    database_path=os.getenv("DATABASE_PATH", "bot.db").strip(),
    max_history=int_env("MAX_HISTORY", 20),
    rate_limit_requests=int_env("RATE_LIMIT_REQUESTS", 5),
    rate_limit_window_seconds=int_env("RATE_LIMIT_WINDOW_SECONDS", 30),
    max_user_message_chars=int_env("MAX_USER_MESSAGE_CHARS", 8000),
    log_level=os.getenv("LOG_LEVEL", "INFO").strip(),
)
