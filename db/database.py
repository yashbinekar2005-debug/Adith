import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

from agent.config import settings


def _connect() -> sqlite3.Connection:
    db_path = Path(settings.db_path)
    if db_path.parent != Path("."):
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id INTEGER,
                feedback_text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            );

            CREATE TABLE IF NOT EXISTS daily_runs (
                run_date TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                report_id INTEGER,
                error TEXT,
                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                finished_at TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(id)
            );
            """
        )


def save_report(report_date: str, content: str) -> int:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO reports (report_date, content)
            VALUES (?, ?)
            ON CONFLICT(report_date) DO UPDATE SET
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP
            """,
            (report_date, content),
        )
        row = conn.execute(
            "SELECT id FROM reports WHERE report_date = ?",
            (report_date,),
        ).fetchone()
        return int(row["id"])


def get_report_by_date(report_date: str) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM reports WHERE report_date = ?",
            (report_date,),
        ).fetchone()
    return dict(row) if row else None


def get_latest_report() -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM reports ORDER BY report_date DESC, updated_at DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def get_last_report_id() -> int | None:
    report = get_latest_report()
    return int(report["id"]) if report else None


def save_feedback(feedback_text: str, report_id: int | None = None) -> int:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO feedback (report_id, feedback_text) VALUES (?, ?)",
            (report_id, feedback_text),
        )
        return int(cur.lastrowid)


def get_recent_feedback(limit: int = 20) -> list[str]:
    with _connect() as conn:
        rows = conn.execute(
            "SELECT feedback_text FROM feedback ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [str(row["feedback_text"]) for row in rows]


def mark_run_started(run_date: str | None = None) -> None:
    run_date = run_date or str(date.today())
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO daily_runs (run_date, status, started_at)
            VALUES (?, 'running', CURRENT_TIMESTAMP)
            ON CONFLICT(run_date) DO UPDATE SET
                status = 'running',
                error = NULL,
                started_at = CURRENT_TIMESTAMP,
                finished_at = NULL
            """,
            (run_date,),
        )


def mark_run_success(report_id: int, run_date: str | None = None) -> None:
    run_date = run_date or str(date.today())
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO daily_runs (run_date, status, report_id, finished_at)
            VALUES (?, 'sent', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(run_date) DO UPDATE SET
                status = 'sent',
                report_id = excluded.report_id,
                error = NULL,
                finished_at = CURRENT_TIMESTAMP
            """,
            (run_date, report_id),
        )


def mark_run_failed(error: str, run_date: str | None = None) -> None:
    run_date = run_date or str(date.today())
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO daily_runs (run_date, status, error, finished_at)
            VALUES (?, 'failed', ?, CURRENT_TIMESTAMP)
            ON CONFLICT(run_date) DO UPDATE SET
                status = 'failed',
                error = excluded.error,
                finished_at = CURRENT_TIMESTAMP
            """,
            (run_date, error[:1000]),
        )


def get_daily_run(run_date: str | None = None) -> dict[str, Any] | None:
    run_date = run_date or str(date.today())
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM daily_runs WHERE run_date = ?",
            (run_date,),
        ).fetchone()
    return dict(row) if row else None


def was_report_sent_today() -> bool:
    run = get_daily_run(str(date.today()))
    return bool(run and run["status"] == "sent")
