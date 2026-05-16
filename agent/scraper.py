import logging
import warnings

warnings.filterwarnings("ignore", category=SyntaxWarning, module=r"newspaper\..*")
from newspaper import Article

logger = logging.getLogger(__name__)


def scrape_article(url: str) -> str:
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()[:2500]
    except Exception as exc:  # noqa: BLE001
        logger.info("Could not scrape %s: %s", url, exc)
        return ""


def enrich_articles(articles: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for article in articles:
        current_text = article.get("text", "").strip()
        if len(current_text) < 400 and article.get("url"):
            scraped = scrape_article(article["url"])
            if scraped:
                article = {**article, "text": scraped}
        enriched.append(article)
    return enriched
