"""
ISO week helpers: normalize week_start to Monday, then derive YYYY-WW.
Avoids timezone/week-boundary drift by treating week_start as nominal and
returning the Monday of that week before computing ISO week.
"""
from __future__ import annotations

from datetime import datetime, timedelta


def normalize_week_start_to_monday(week_start: str) -> str:
    """Return Monday (YYYY-MM-DD) of the ISO week containing week_start. week_start is YYYY-MM-DD."""
    dt = datetime.strptime(week_start, "%Y-%m-%d")
    # ISO weekday: 1 = Monday, 7 = Sunday
    weekday = dt.isoweekday()
    monday = dt - timedelta(days=weekday - 1)
    return monday.strftime("%Y-%m-%d")


def iso_week_from_week_start(week_start: str) -> str:
    """Derive YYYY-WW from week_start after normalizing to Monday."""
    monday = normalize_week_start_to_monday(week_start)
    dt = datetime.strptime(monday, "%Y-%m-%d")
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"
