"""
SQLite persistence for leads. Replaces JSONL for concurrent-write safety and query capability.
Use same DB path as APScheduler SQLAlchemyJobStore so jobs survive restarts.
"""
from __future__ import annotations

import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

APP_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = APP_DIR / "data" / "funnel.db"


def _get_connection(db_path: Path | None = None):
    path = db_path or Path(os.environ.get("DATABASE_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False, timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def get_database_url(db_path: Path | None = None) -> str:
    """URL for SQLAlchemy (APScheduler jobstore)."""
    path = db_path or Path(os.environ.get("DATABASE_PATH", str(DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


def init_db(db_path: Path | None = None) -> None:
    conn = _get_connection(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                lead_id TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                name TEXT,
                persona TEXT,
                exercise_name TEXT NOT NULL,
                second_exercise TEXT NOT NULL,
                hub TEXT NOT NULL,
                topic TEXT NOT NULL,
                created_at TEXT NOT NULL,
                e1_sent_at TEXT,
                unsubscribed INTEGER NOT NULL DEFAULT 0,
                unsubscribe_token TEXT,
                ghl_pushed INTEGER NOT NULL DEFAULT 0
            )
        """)
        try:
            conn.execute("ALTER TABLE leads ADD COLUMN ghl_pushed INTEGER NOT NULL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.execute("CREATE INDEX IF NOT EXISTS ix_leads_email ON leads(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_leads_unsubscribed ON leads(unsubscribed)")
        conn.commit()
    finally:
        conn.close()


@contextmanager
def get_cursor(db_path: Path | None = None):
    conn = _get_connection(db_path)
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


def insert_lead(
    email: str,
    exercise_name: str,
    second_exercise: str,
    hub: str,
    topic: str,
    name: str = "",
    persona: str = "unknown",
    unsubscribe_token: str | None = None,
    db_path: Path | None = None,
) -> str:
    import datetime
    lead_id = str(uuid.uuid4())
    created_at = datetime.datetime.utcnow().isoformat() + "Z"
    with get_cursor(db_path) as cur:
        cur.execute(
            """INSERT INTO leads (lead_id, email, name, persona, exercise_name, second_exercise, hub, topic, created_at, unsubscribed, unsubscribe_token, ghl_pushed)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, 0)""",
            (lead_id, email, name or "", persona, exercise_name, second_exercise, hub, topic, created_at, unsubscribe_token),
        )
    return lead_id


def update_ghl_pushed(lead_id: str, success: bool, db_path: Path | None = None) -> None:
    with get_cursor(db_path) as cur:
        cur.execute("UPDATE leads SET ghl_pushed = ? WHERE lead_id = ?", (1 if success else 0, lead_id))


def get_lead(lead_id: str, db_path: Path | None = None) -> dict | None:
    with get_cursor(db_path) as cur:
        cur.execute("SELECT lead_id, email, name, persona, exercise_name, second_exercise, hub, topic, created_at, e1_sent_at, unsubscribed FROM leads WHERE lead_id = ?", (lead_id,))
        row = cur.fetchone()
    if not row:
        return None
    return {
        "lead_id": row[0],
        "email": row[1],
        "name": row[2] or "",
        "persona": row[3] or "unknown",
        "exercise_name": row[4],
        "second_exercise": row[5],
        "hub": row[6],
        "topic": row[7],
        "created_at": row[8],
        "e1_sent_at": row[9],
        "unsubscribed": bool(row[10]),
    }


def get_lead_by_unsubscribe_token(token: str, db_path: Path | None = None) -> dict | None:
    with get_cursor(db_path) as cur:
        cur.execute("SELECT lead_id FROM leads WHERE unsubscribe_token = ? AND unsubscribed = 0", (token,))
        row = cur.fetchone()
    if not row:
        return None
    return get_lead(row[0], db_path)


def mark_e1_sent(lead_id: str, db_path: Path | None = None) -> None:
    import datetime
    sent_at = datetime.datetime.utcnow().isoformat() + "Z"
    with get_cursor(db_path) as cur:
        cur.execute("UPDATE leads SET e1_sent_at = ? WHERE lead_id = ?", (sent_at, lead_id))


def set_unsubscribed_by_token(token: str, db_path: Path | None = None) -> bool:
    """Mark lead(s) unsubscribed by unsubscribe_token. Returns True if any row updated."""
    with get_cursor(db_path) as cur:
        cur.execute("UPDATE leads SET unsubscribed = 1 WHERE unsubscribe_token = ?", (token,))
        return cur.rowcount > 0


def set_unsubscribed_by_email(email: str, db_path: Path | None = None) -> bool:
    with get_cursor(db_path) as cur:
        cur.execute("UPDATE leads SET unsubscribed = 1 WHERE email = ?", (email,))
        return cur.rowcount > 0


def is_unsubscribed(email: str, db_path: Path | None = None) -> bool:
    with get_cursor(db_path) as cur:
        cur.execute("SELECT 1 FROM leads WHERE email = ? AND unsubscribed = 1", (email,))
        return cur.fetchone() is not None
