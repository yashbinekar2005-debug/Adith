import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agent.config import settings, validate_report_time
from agent.ollama_runtime import start_ollama, stop_ollama
from agent.reporter import generate_daily_report
from bot.sender import send_message
from db.database import mark_run_failed, mark_run_started, mark_run_success, was_report_sent_today

logger = logging.getLogger(__name__)


def run_daily_report(force: bool = False) -> None:
    if not force and was_report_sent_today():
        logger.info("Today's report has already been sent; skipping scheduled run.")
        return

    mark_run_started()
    try:
        start_ollama()
        result = generate_daily_report(force=force)
        send_message(result.content)
        mark_run_success(result.report_id)
        logger.info("Daily report sent successfully.")
    except Exception as exc:  # noqa: BLE001
        logger.exception("Daily report job failed.")
        mark_run_failed(str(exc))
        try:
            send_message(f"Agent error while generating report: {exc}")
        except Exception:
            logger.exception("Could not send failure notice to Telegram.")
    finally:
        stop_ollama()


def start_scheduler() -> BackgroundScheduler:
    hour, minute = validate_report_time()
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_daily_report,
        trigger=CronTrigger(hour=hour, minute=minute),
        id="daily_report",
        name="Daily AI News Report",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started. Daily report time: %s.", settings.report_time)
    return scheduler


def maybe_run_missed_report() -> None:
    if was_report_sent_today():
        logger.info("Today's report has already been sent.")
        return

    logger.info("No report has been sent today; running startup report now.")
    run_daily_report(force=False)
