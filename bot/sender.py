import logging
import time
from functools import lru_cache

import telebot

from agent.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_bot() -> telebot.TeleBot:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing.")
    return telebot.TeleBot(settings.telegram_bot_token)


def _chunks(text: str, size: int = 3900) -> list[str]:
    return [text[index : index + size] for index in range(0, len(text), size)] or [""]


def _send_chunk_with_retry(
    bot: telebot.TeleBot,
    target: str,
    chunk: str,
    parse_mode: str | None,
) -> None:
    attempts = max(1, settings.telegram_send_retries)
    for attempt in range(1, attempts + 1):
        try:
            if not parse_mode:
                bot.send_message(target, chunk, disable_web_page_preview=True)
                return

            try:
                bot.send_message(
                    target,
                    chunk,
                    parse_mode=parse_mode,
                    disable_web_page_preview=True,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("%s send failed, retrying as plain text: %s", parse_mode, exc)
                bot.send_message(target, chunk, parse_mode=None, disable_web_page_preview=True)
            return
        except Exception as exc:  # noqa: BLE001
            if attempt >= attempts:
                raise
            logger.warning(
                "Telegram send failed on attempt %s/%s. Retrying in %s seconds: %s",
                attempt,
                attempts,
                settings.telegram_retry_delay_seconds,
                exc,
            )
            time.sleep(settings.telegram_retry_delay_seconds)


def send_message(text: str, chat_id: str | None = None, parse_mode: str | None = None) -> None:
    target = chat_id or settings.telegram_chat_id
    if not target:
        raise RuntimeError("TELEGRAM_CHAT_ID is missing.")

    bot = get_bot()
    for chunk in _chunks(text):
        _send_chunk_with_retry(bot, target, chunk, parse_mode)
