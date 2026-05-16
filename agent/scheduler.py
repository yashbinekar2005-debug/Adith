import logging
from datetime import datetime, time

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from agent.config import settings, validate_report_time
from agent.reporter import generate_daily_report
from bot.sender import send_message
from db.database import mark_run_failed, mark_run_started, mark_run_success, was_report_sent_today

logger = logging.getLogger(__name__)


def run_daily_report(force: bool = False) -> None:
    mark_run_started()
    try:
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
    hour, minute = validate_report_time()
    now = datetime.now()
    scheduled = time(hour=hour, minute=minute)
    if now.time() < scheduled:
        logger.info("Startup is before report time; no missed report check needed.")
        return
    if was_report_sent_today():
        logger.info("Today's report has already been sent.")
        return

    logger.info("Today's report was missed while laptop was off; running now.")
    run_daily_report(force=False)
