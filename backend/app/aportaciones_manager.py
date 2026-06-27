"""Module to manage weekly Aportaciones (contributions) using SQLite."""
from datetime import date, timedelta
from app.database import get_db
from app import cache

# Fallback config (used only if DB table is empty)
_DEFAULT_CONFIG = [
    {"category": "Ahorro Familiar", "amount": 200, "person": "Adrian", "color": "#f59e0b"},
    {"category": "Ahorro Familiar", "amount": 200, "person": "Karime", "color": "#f59e0b"},
    {"category": "Nu", "amount": 50, "person": "", "color": "#8b5cf6"},
    {"category": "GBM", "amount": 50, "person": "", "color": "#1da1f2"},
    {"category": "Afore", "amount": 60, "person": "", "color": "#10b981"},
]


def _get_aportaciones_config() -> list[dict]:
    """Get aportaciones config from DB, seeding defaults if empty."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM aportaciones_config").fetchall()
        if rows:
            return [{"category": r["category"], "amount": r["amount"], "person": r["person"], "color": r["color"]} for r in rows]

        # Seed defaults
        for c in _DEFAULT_CONFIG:
            conn.execute(
                "INSERT INTO aportaciones_config (category, amount, person, color) VALUES (?, ?, ?, ?)",
                (c["category"], c["amount"], c["person"], c["color"])
            )
    return list(_DEFAULT_CONFIG)


def _get_weeks_of_month(year: int, month: int) -> list[dict]:
    """Get all weeks (Sun-Sat) that overlap with the given month.
    Returns list of {week_start, week_end} as ISO date strings."""
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year, 12, 31)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    weeks = []

    # Find the Sunday on or before the first day of the month
    current = first_day
    # Go back to Sunday (weekday: Mon=0, Sun=6)
    days_since_sunday = (current.weekday() + 1) % 7
    week_start = current - timedelta(days=days_since_sunday)

    while week_start <= last_day:
        week_end = week_start + timedelta(days=6)
        # Only include if the week overlaps with the month
        if week_end >= first_day and week_start <= last_day:
            weeks.append({
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
            })
        week_start += timedelta(days=7)

    return weeks


def _purge_old_aportaciones():
    """Keep only 3 months of data: previous, current, and next month.
    Deletes anything older."""
    today = date.today()

    # First day of previous month
    if today.month == 1:
        prev_month_start = date(today.year - 1, 12, 1)
    else:
        prev_month_start = date(today.year, today.month - 1, 1)

    with get_db() as conn:
        conn.execute(
            "DELETE FROM aportaciones WHERE week_start < ?",
            (prev_month_start.isoformat(),)
        )

    cache.invalidate_prefix("aportaciones")


def ensure_month_records(year: int, month: int):
    """Ensure all aportacion records exist for the given month.
    Creates missing records with 'pendiente' status.
    Automatically marks past weeks as 'atrasada' if still 'pendiente'."""
    weeks = _get_weeks_of_month(year, month)
    today = date.today().isoformat()

    with get_db() as conn:
        for week in weeks:
            for config in _get_aportaciones_config():
                existing = conn.execute(
                    """SELECT id, status, week_end FROM aportaciones
                       WHERE category = ? AND week_start = ? AND person = ?""",
                    (config["category"], week["week_start"], config["person"])
                ).fetchone()

                if not existing:
                    # Auto-mark as atrasada if week already passed
                    status = "atrasada" if week["week_end"] < today else "pendiente"
                    conn.execute(
                        """INSERT INTO aportaciones (category, week_start, week_end, status, person)
                           VALUES (?, ?, ?, ?, ?)""",
                        (config["category"], week["week_start"], week["week_end"], status, config["person"])
                    )
                else:
                    # If still pendiente and week already passed, mark as atrasada
                    if existing["status"] == "pendiente" and existing["week_end"] < today:
                        conn.execute(
                            "UPDATE aportaciones SET status = 'atrasada' WHERE id = ?",
                            (existing["id"],)
                        )

    cache.invalidate_prefix("aportaciones")


def get_aportaciones(year: int, month: int) -> dict:
    """Get all aportaciones for a given month, organized by category.
    Only allows months from May 2026 onwards.
    Maintains a 3-month window: previous, current, next."""
    # No permitir meses anteriores a mayo 2026
    if year < 2026 or (year == 2026 and month < 5):
        return {"weeks": [], "categories": [], "month": month, "year": year}

    # Purge old data and ensure 3-month window
    _purge_old_aportaciones()

    # Ensure records for previous, current, and next month
    today = date.today()
    months_to_ensure = []
    for offset in [-1, 0, 1]:
        m = today.month + offset
        y = today.year
        if m < 1:
            m = 12
            y -= 1
        elif m > 12:
            m = 1
            y += 1
        if y > 2026 or (y == 2026 and m >= 5):
            months_to_ensure.append((y, m))

    for y, m in months_to_ensure:
        ensure_month_records(y, m)

    # Now fetch the requested month
    cached_key = f"aportaciones_{year}_{month}"
    cached = cache.get(cached_key)
    if cached is not None:
        return cached

    weeks = _get_weeks_of_month(year, month)

    with get_db() as conn:
        rows = conn.execute(
            """SELECT * FROM aportaciones
               WHERE week_start >= ? AND week_start <= ?
               ORDER BY week_start, category, person""",
            (weeks[0]["week_start"], weeks[-1]["week_start"])
        ).fetchall()

    # Organize by category
    categories = {}
    for row in rows:
        cat = row["category"]
        person = row["person"]
        key = f"{cat}|{person}" if person else cat

        if key not in categories:
            # Find amount from config
            amount = 0
            for c in _get_aportaciones_config():
                if c["category"] == cat and c["person"] == person:
                    amount = c["amount"]
                    break

            categories[key] = {
                "category": cat,
                "person": person,
                "amount": amount,
                "weeks": []
            }

        categories[key]["weeks"].append({
            "id": row["id"],
            "weekStart": row["week_start"],
            "weekEnd": row["week_end"],
            "status": row["status"],
        })

    result = {
        "weeks": weeks,
        "categories": list(categories.values()),
        "month": month,
        "year": year,
    }

    cache.set(cached_key, result, ttl_seconds=300)
    return result


def update_aportacion_status(aportacion_id: int, status: str) -> bool:
    """Update the status of an aportacion record.
    Only 'pendiente' and 'realizada' are valid user-set statuses.
    'atrasada' is set automatically by the system.
    """
    valid_statuses = ("pendiente", "realizada")
    if status not in valid_statuses:
        return False

    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE aportaciones SET status = ? WHERE id = ?",
            (status, aportacion_id)
        )
        updated = cursor.rowcount > 0

    if updated:
        cache.invalidate_prefix("aportaciones")
    return updated
