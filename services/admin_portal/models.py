"""
SQLite access for admin portal. Minimal v1: no ORM.
"""
from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "portal.db"


def get_conn(db_path: Path | str | None = None) -> sqlite3.Connection:
    p = Path(db_path) if db_path else DEFAULT_DB_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = (Path(__file__).resolve().parent / "schema.sql").read_text()
    conn.executescript(schema)
    conn.commit()


def user_by_email(conn: sqlite3.Connection, email: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT id, email, display_name, status, created_at FROM brand_admin_users WHERE email = ? AND status = 'active'",
        (email.strip().lower(),),
    ).fetchone()
    return dict(row) if row else None


def user_grants(conn: sqlite3.Connection, user_id: str) -> list[str]:
    rows = conn.execute(
        "SELECT brand_id FROM brand_admin_grants WHERE user_id = ?",
        (user_id,),
    ).fetchall()
    return [r["brand_id"] for r in rows]


def packets_for_week(conn: sqlite3.Connection, week_key: str, brand_ids: list[str] | None = None) -> list[dict[str, Any]]:
    if brand_ids is not None and len(brand_ids) == 0:
        return []
    if not brand_ids:
        rows = conn.execute(
            "SELECT week_key, brand_id, r2_key, release_day, bytes, sha256, status FROM weekly_packets WHERE week_key = ?",
            (week_key,),
        ).fetchall()
    else:
        placeholders = ",".join("?" * len(brand_ids))
        rows = conn.execute(
            f"SELECT week_key, brand_id, r2_key, release_day, bytes, sha256, status FROM weekly_packets WHERE week_key = ? AND brand_id IN ({placeholders})",
            (week_key, *brand_ids),
        ).fetchall()
    return [dict(r) for r in rows]


def upsert_packet(conn: sqlite3.Connection, week_key: str, brand_id: str, r2_key: str, release_day: str, bytes_: int, sha256: str, status: str = "ready") -> None:
    uid = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO weekly_packets (id, week_key, brand_id, r2_key, release_day, bytes, sha256, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
           ON CONFLICT(week_key, brand_id) DO UPDATE SET r2_key=excluded.r2_key, release_day=excluded.release_day, bytes=excluded.bytes, sha256=excluded.sha256, status=excluded.status""",
        (uid, week_key, brand_id, r2_key, release_day, bytes_, sha256, status),
    )
    conn.commit()


def insert_audit(conn: sqlite3.Connection, user_id: str | None, brand_id: str | None, week_key: str | None, action: str, ip: str | None, user_agent: str | None, result: str = "ok") -> None:
    conn.execute(
        "INSERT INTO packet_access_audit (id, user_id, brand_id, week_key, action, ip, user_agent, result) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (str(uuid.uuid4()), user_id, brand_id, week_key, action, ip, user_agent, result),
    )
    conn.commit()


def recent_audit(conn: sqlite3.Connection, limit: int = 100) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT user_id, brand_id, week_key, action, ip, result, created_at FROM packet_access_audit ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def ensure_user_and_grants(conn: sqlite3.Connection, email: str, display_name: str | None, brand_ids: list[str]) -> str:
    email = email.strip().lower()
    row = conn.execute("SELECT id FROM brand_admin_users WHERE email = ?", (email,)).fetchone()
    if row:
        user_id = row["id"]
        conn.execute("DELETE FROM brand_admin_grants WHERE user_id = ?", (user_id,))
    else:
        user_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO brand_admin_users (id, email, display_name, status) VALUES (?, ?, ?, 'active')",
            (user_id, email, display_name or email),
        )
    for bid in brand_ids:
        conn.execute(
            "INSERT INTO brand_admin_grants (id, user_id, brand_id, role) VALUES (?, ?, ?, 'admin')",
            (str(uuid.uuid4()), user_id, bid),
        )
    conn.commit()
    return user_id
