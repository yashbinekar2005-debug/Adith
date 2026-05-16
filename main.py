import logging
import os
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from agent.config import settings, validate_required_config
from agent.scheduler import maybe_run_missed_report, start_scheduler
from bot.handlers import register_handlers
from bot.sender import get_bot
from db.database import init_db

LOCK_FILE = Path(".agent.lock")
_lock_handle = None


def acquire_process_lock() -> bool:
    global _lock_handle
    _lock_handle = LOCK_FILE.open("w", encoding="utf-8")
    try:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(_lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(_lock_handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False

    _lock_handle.write(str(os.getpid()))
    _lock_handle.flush()
    return True


def configure_logging() -> None:
    Path("logs").mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler("logs/agent.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main() -> int:
    configure_logging()
    logger = logging.getLogger(__name__)

    if not acquire_process_lock():
        logger.error("Another AI News Agent process is already running.")
        return 1

    try:
        validate_required_config()
    except RuntimeError as exc:
        logger.error(str(exc))
        return 1

    init_db()
    logger.info("Database initialized at %s", settings.db_path)

    bot = get_bot()
    register_handlers(bot)

    scheduler = start_scheduler()
    maybe_run_missed_report()

    def shutdown(signum, frame):  # noqa: ARG001
        logger.info("Shutdown signal received.")
        scheduler.shutdown(wait=False)
        bot.stop_polling()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    logger.info("Starting Telegram bot polling.")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
