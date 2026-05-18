import logging
from dataclasses import dataclass
from datetime import date

from agent.llm import summarize_articles
from agent.scraper import enrich_articles
from agent.search import gather_all_sources
from db.database import get_report_by_date, save_report

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ReportResult:
    report_id: int
    content: str
    created_new: bool


def generate_daily_report(force: bool = False) -> ReportResult:
    today = str(date.today())
    existing = get_report_by_date(today)
    if existing and not force:
        return ReportResult(
            report_id=int(existing["id"]),
            content=str(existing["content"]),
            created_new=False,
        )

    logger.info("Generating daily report for %s.", today)
    articles = gather_all_sources()
    if not articles:
        content = (
            f"Daily AI Report - {today}\n\n"
            "No fresh articles were found. Check internet connectivity or try /report later."
        )
        report_id = save_report(today, content)
        return ReportResult(report_id=report_id, content=content, created_new=True)

    articles = enrich_articles(articles)
    summary = summarize_articles(articles)
    content = f"Daily AI Report - {date.today().strftime('%B %d, %Y')}\n\n{summary}"
    report_id = save_report(today, content)
    logger.info("Report saved with id %s.", report_id)
    return ReportResult(report_id=report_id, content=content, created_new=True)
