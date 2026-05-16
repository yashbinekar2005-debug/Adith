import logging

import feedparser
from duckduckgo_search import DDGS

from agent.config import settings

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    "https://arxiv.org/rss/cs.AI",
    "https://huggingface.co/blog/feed.xml",
    "https://openai.com/blog/rss",
    "https://www.deepmind.com/blog/rss.xml",
    "https://machinelearningmastery.com/feed/",
]

SEARCH_QUERIES = [
    "latest AI news today",
    "large language model release today",
    "AI research breakthrough today",
    "machine learning tools release today",
]


def fetch_rss_feeds(limit_per_feed: int | None = None) -> list[dict[str, str]]:
    limit = limit_per_feed or settings.rss_limit_per_feed
    articles: list[dict[str, str]] = []
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source = feed.feed.get("title", feed_url)
            for entry in feed.entries[:limit]:
                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "text": entry.get("summary", ""),
                        "source": source,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            logger.warning("RSS fetch failed for %s: %s", feed_url, exc)
    return articles


def search_ddg(query: str, max_results: int | None = None) -> list[dict[str, str]]:
    limit = max_results or settings.ddg_results_per_query
    results: list[dict[str, str]] = []
    try:
        with DDGS(timeout=8) as ddgs:
            for result in ddgs.text(query, max_results=limit, timelimit="d"):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "text": result.get("body", ""),
                        "source": "DuckDuckGo",
                    }
                )
    except Exception as exc:  # noqa: BLE001
        logger.warning("DuckDuckGo daily search failed for %r: %s", query, exc)
        try:
            with DDGS(timeout=8) as ddgs:
                fallback_query = f"{query} AI technology news"
                for result in ddgs.text(fallback_query, max_results=limit):
                    results.append(
                        {
                            "title": result.get("title", ""),
                            "url": result.get("href", ""),
                            "text": result.get("body", ""),
                            "source": "DuckDuckGo",
                        }
                    )
        except Exception as fallback_exc:  # noqa: BLE001
            logger.warning("DuckDuckGo fallback search failed for %r: %s", query, fallback_exc)
    return results


def gather_all_sources() -> list[dict[str, str]]:
    articles: list[dict[str, str]] = []
    articles.extend(fetch_rss_feeds())
    for query in SEARCH_QUERIES:
        articles.extend(search_ddg(query))

    unique: list[dict[str, str]] = []
    seen: set[str] = set()
    for article in articles:
        url = article.get("url", "").strip()
        title = article.get("title", "").strip()
        key = url or title.lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(article)

    logger.info("Gathered %s unique source items.", len(unique))
    return unique[: settings.max_articles]
