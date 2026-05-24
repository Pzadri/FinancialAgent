"""Tracks the last update date for data sections that come from Excel files."""
import json
from datetime import date, datetime
from pathlib import Path

TRACKER_FILE = Path(__file__).parent.parent.parent / "data" / "last_updates.json"


def _load() -> dict:
    if TRACKER_FILE.exists():
        try:
            return json.loads(TRACKER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save(data: dict):
    TRACKER_FILE.parent.mkdir(parents=True, exist_ok=True)
    TRACKER_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_last_update(section: str) -> str | None:
    """Returns the last update date for a section as 'YYYY-MM-DD', or None."""
    return _load().get(section)


def mark_updated(section: str) -> str:
    """Marks a section as updated today. Returns today's date string."""
    today = date.today().isoformat()
    data = _load()
    data[section] = today
    _save(data)
    return today


def is_monday() -> bool:
    """Returns True if today is Monday (weekday 0)."""
    return date.today().weekday() == 0


def needs_update(section: str) -> bool:
    """Returns True if today is Monday and the section hasn't been updated this Monday."""
    if not is_monday():
        return False
    last = get_last_update(section)
    if last is None:
        return True
    return last != date.today().isoformat()


def get_status(section: str) -> dict:
    """Returns full status info for a section."""
    today = date.today()
    last_str = get_last_update(section)
    last_date = datetime.strptime(last_str, "%Y-%m-%d").date() if last_str else None

    return {
        "section": section,
        "lastUpdate": last_str,
        "isMonday": today.weekday() == 0,
        "needsUpdate": needs_update(section),
        "daysSinceUpdate": (today - last_date).days if last_date else None,
    }
