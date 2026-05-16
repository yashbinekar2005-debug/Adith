import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    ollama_model: str
    ollama_base_url: str
    report_time: str
    db_path: Path
    max_articles: int
    rss_limit_per_feed: int
    ddg_results_per_query: int
    request_timeout_seconds: int


settings = Settings(
    telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
    telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
    ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1"),
    ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"),
    report_time=os.getenv("REPORT_TIME", "07:00"),
    db_path=Path(os.getenv("DB_PATH", "agent.db")),
    max_articles=_int_env("MAX_ARTICLES", 15),
    rss_limit_per_feed=_int_env("RSS_LIMIT_PER_FEED", 3),
    ddg_results_per_query=_int_env("DDG_RESULTS_PER_QUERY", 3),
    request_timeout_seconds=_int_env("REQUEST_TIMEOUT_SECONDS", 120),
)


def validate_report_time() -> tuple[int, int]:
    try:
        hour_raw, minute_raw = settings.report_time.split(":", 1)
        hour = int(hour_raw)
        minute = int(minute_raw)
    except ValueError as exc:
        raise RuntimeError("REPORT_TIME must use HH:MM format, for example 07:00") from exc

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise RuntimeError("REPORT_TIME hour/minute are out of range")
    return hour, minute


def validate_required_config() -> None:
    missing = []
    if not settings.telegram_bot_token:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not settings.telegram_chat_id:
        missing.append("TELEGRAM_CHAT_ID")
    validate_report_time()

    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"Missing required .env values: {names}. Copy .env.example to .env and fill them in."
        )
