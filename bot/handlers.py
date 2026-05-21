import logging
from datetime import date

from agent.config import settings
from agent.llm import check_ollama
from agent.reporter import generate_daily_report
from agent.scheduler import run_daily_report
from bot.sender import send_message
from db.database import (
    get_daily_run,
    get_last_report_id,
    get_latest_report,
    save_feedback,
)

logger = logging.getLogger(__name__)

HELP_TEXT = """*AI News Reporter*

/report - Generate or refresh today's report now
/last - Send the latest saved report
/feedback <text> - Save feedback for future reports
/status - Show agent status
/help - Show this help message
"""


def register_handlers(bot) -> None:
    @bot.message_handler(commands=["start", "help"])
    def cmd_help(message):
        bot.reply_to(message, HELP_TEXT, parse_mode="Markdown")

    @bot.message_handler(commands=["status"])
    def cmd_status(message):
        ok, ollama_message = check_ollama()
        run = get_daily_run(str(date.today()))
        run_status = run["status"] if run else "not run today"
        latest = get_latest_report()
        latest_date = latest["report_date"] if latest else "none"
        if ok:
            status = "OK"
        elif settings.stop_ollama_after_report:
            status = "OK"
            ollama_message = "Ollama is stopped to save RAM. It will start automatically for reports."
        else:
            status = "Needs attention"
        bot.reply_to(
            message,
            (
                f"*Agent Status*: {status}\n"
                f"*Model*: {settings.ollama_model}\n"
                f"*Report time*: {settings.report_time}\n"
                f"*Today*: {run_status}\n"
                f"*Latest report*: {latest_date}\n"
                f"*Ollama*: {ollama_message}"
            ),
            parse_mode="Markdown",
        )

    @bot.message_handler(commands=["report"])
    def cmd_report(message):
        bot.reply_to(message, "Generating today's report. This can take a few minutes.")
        run_daily_report(force=True)

    @bot.message_handler(commands=["last"])
    def cmd_last(message):
        latest = get_latest_report()
        if not latest:
            bot.reply_to(message, "No saved report yet. Use /report to create one.")
            return
        send_message(str(latest["content"]), str(message.chat.id))

    @bot.message_handler(commands=["feedback"])
    def cmd_feedback(message):
        text = message.text or ""
        feedback = text.partition(" ")[2].strip()
        if not feedback:
            bot.reply_to(message, "Send feedback like: /feedback Make it shorter and focus on open source models.")
            return
        report_id = get_last_report_id()
        save_feedback(feedback, report_id)
        bot.reply_to(message, "Feedback saved. I will apply it to future reports.")

    @bot.message_handler(func=lambda message: True)
    def cmd_unknown(message):
        logger.info("Ignoring non-command message from chat %s.", message.chat.id)
        bot.reply_to(message, "Use /help to see available commands.")
