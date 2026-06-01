"""Tracks the last update date for data sections using SQLite."""
from datetime import date, datetime
from app.database import get_db


def get_last_update(section: str) -> str | None:
    """Returns the last update date for a section as 'YYYY-MM-DD', or None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT last_update FROM update_tracker WHERE section = ?", (section,)
        ).fetchone()
        return row["last_update"] if row else None


def mark_updated(section: str) -> str:
    """Marks a section as updated today. Returns today's date string."""
    today = date.today().isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO update_tracker (section, last_update) VALUES (?, ?)",
            (section, today)
        )
    return today


def is_monday() -> bool:
    """Returns True if today is Monday (weekday 0)."""
    return date.today().weekday() == 0


def is_first_of_month() -> bool:
    """Returns True if today is the 1st day of the month."""
    return date.today().day == 1


def is_fifteenth() -> bool:
    """Returns True if today is the 15th day of the month."""
    return date.today().day == 15


# Map of schedule types to their check functions
SCHEDULE_CHECKS = {
    "monday": is_monday,
    "first_of_month": is_first_of_month,
    "fifteenth": is_fifteenth,
}


def needs_update(section: str, schedule: str = "monday") -> bool:
    """Returns True if today matches the schedule and the section hasn't been updated today.

    schedule: 'monday' | 'first_of_month' | 'fifteenth'
    """
    check_fn = SCHEDULE_CHECKS.get(schedule, is_monday)
    if not check_fn():
        return False
    last = get_last_update(section)
    if last is None:
        return True
    return last != date.today().isoformat()


def get_status(section: str, schedule: str = "monday") -> dict:
    """Returns full status info for a section."""
    today = date.today()
    last_str = get_last_update(section)
    last_date = datetime.strptime(last_str, "%Y-%m-%d").date() if last_str else None

    schedule_labels = {
        "monday": "isMonday",
        "first_of_month": "isFirstOfMonth",
        "fifteenth": "isFifteenth",
    }

    check_fn = SCHEDULE_CHECKS.get(schedule, is_monday)

    return {
        "section": section,
        "lastUpdate": last_str,
        schedule_labels.get(schedule, "isMonday"): check_fn(),
        "needsUpdate": needs_update(section, schedule),
        "daysSinceUpdate": (today - last_date).days if last_date else None,
    }
