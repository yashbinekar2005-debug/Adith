from datetime import date

import requests

from agent.config import settings
from db.database import get_recent_feedback


def build_system_prompt() -> str:
    feedback = get_recent_feedback()
    feedback_section = ""
    if feedback:
        feedback_section = "\n\nPast user feedback to apply:\n"
        feedback_section += "\n".join(f"- {item}" for item in feedback)

    return (
        f"You are an expert AI and technology news reporter. Today is {date.today()}.\n"
        "Create a concise Telegram-ready daily report from the provided articles.\n"
        "Use simple Markdown compatible with Telegram. Avoid unsupported tables.\n"
        "Structure the report with: top headlines, key details, why it matters, and links.\n"
        "Prefer concrete product names, model names, organizations, and dates.\n"
        "Do not invent facts. If the source text is thin, say what is known from the source.\n"
        "End with a short Today's Highlight section."
        f"{feedback_section}"
    )


def ask_llm(messages: list[dict[str, str]]) -> str:
    payload = {
        "model": settings.ollama_model,
        "messages": [{"role": "system", "content": build_system_prompt()}, *messages],
        "stream": False,
    }
    response = requests.post(
        f"{settings.ollama_base_url}/api/chat",
        json=payload,
        timeout=settings.request_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"].strip()


def summarize_articles(articles: list[dict[str, str]]) -> str:
    article_blocks = []
    for index, article in enumerate(articles, start=1):
        text = article.get("text", "").strip()[:1200]
        article_blocks.append(
            "\n".join(
                [
                    f"Article {index}",
                    f"Title: {article.get('title', 'Untitled')}",
                    f"Source: {article.get('source', 'Unknown')}",
                    f"URL: {article.get('url', '')}",
                    f"Text: {text}",
                ]
            )
        )

    content = (
        "Write today's AI/tech news report using these article notes. "
        "Rank the most important items first and include source links.\n\n"
        + "\n\n---\n\n".join(article_blocks)
    )
    return ask_llm([{"role": "user", "content": content}])


def check_ollama() -> tuple[bool, str]:
    try:
        response = requests.get(
            f"{settings.ollama_base_url}/api/tags",
            timeout=10,
        )
        response.raise_for_status()
        models = response.json().get("models", [])
        names = {model.get("name") for model in models}
        if settings.ollama_model in names:
            return True, f"Ollama is reachable and {settings.ollama_model} is installed."
        return True, (
            f"Ollama is reachable, but {settings.ollama_model} was not listed. "
            "The report may fail until you pull/select the model."
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"Ollama check failed: {exc}"
