import logging
from functools import lru_cache

import telebot

from agent.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_bot() -> telebot.TeleBot:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing.")
    return telebot.TeleBot(settings.telegram_bot_token, parse_mode="Markdown")


def _chunks(text: str, size: int = 3900) -> list[str]:
    return [text[index : index + size] for index in range(0, len(text), size)] or [""]


def send_message(text: str, chat_id: str | None = None) -> None:
    target = chat_id or settings.telegram_chat_id
    if not target:
        raise RuntimeError("TELEGRAM_CHAT_ID is missing.")

    bot = get_bot()
    for chunk in _chunks(text):
        try:
            bot.send_message(target, chunk, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Markdown send failed, retrying as plain text: %s", exc)
            bot.send_message(target, chunk, disable_web_page_preview=True)
