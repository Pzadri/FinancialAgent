"""Module to read and manage Creditos data from SQLite."""
from datetime import date
from app.database import get_db
from app import cache


def get_credit_cards() -> dict:
    """Read credit card data from SQLite. Cached for 5 minutes."""
    cached = cache.get("creditos_cards")
    if cached is not None:
        return cached

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM creditos").fetchall()

    cards = []
    for row in rows:
        credit_limit = row["credit_limit"]
        debt = row["debt"]
        available = row["available"]
        payment_date = row["payment_date"]

        usage_percent = round((debt / credit_limit) * 100) if credit_limit > 0 else 0

        days_until = 0
        if payment_date:
            try:
                pay_date = date.fromisoformat(payment_date.split(" ")[0])
                today = date.today()
                days_until = (pay_date - today).days
                if days_until < 0:
                    days_until = 0
            except (ValueError, TypeError):
                days_until = 0

        cards.append({
            "name": row["name"],
            "color": row["color"],
            "creditLimit": credit_limit,
            "debt": debt,
            "available": available,
            "usagePercent": usage_percent,
            "cutoffDate": row["cutoff_date"],
            "paymentDate": payment_date,
            "minimumPayment": row["minimum_payment"],
            "fullPayment": row["full_payment"],
            "daysUntilPayment": days_until
        })

    # Summary
    total_credit = sum(c["creditLimit"] for c in cards)
    total_debt = sum(c["debt"] for c in cards)
    total_available = sum(c["available"] for c in cards)
    total_payment = sum(c["fullPayment"] for c in cards)
    total_usage = round((total_debt / total_credit) * 100) if total_credit > 0 else 0

    result = {
        "cards": cards,
        "summary": {
            "totalCredit": total_credit,
            "totalDebt": total_debt,
            "totalAvailable": total_available,
            "totalPayment": total_payment,
            "usagePercent": total_usage
        }
    }

    cache.set("creditos_cards", result, ttl_seconds=300)
    return result


def update_credit_card(name: str, fields: dict) -> str:
    """Update fields for a specific credit card in SQLite.

    Args:
        name: Card name to update.
        fields: Dict with any of: debt, available, cutoffDate, paymentDate,
                minimumPayment, fullPayment, creditLimit.

    Returns:
        Today's date string (ISO format).
    """
    from app.update_tracker import mark_updated

    # Map API field names to DB column names
    field_map = {
        "creditLimit": "credit_limit",
        "debt": "debt",
        "available": "available",
        "cutoffDate": "cutoff_date",
        "paymentDate": "payment_date",
        "minimumPayment": "minimum_payment",
        "fullPayment": "full_payment",
    }

    with get_db() as conn:
        for api_field, value in fields.items():
            col = field_map.get(api_field)
            if col:
                conn.execute(
                    f"UPDATE creditos SET {col} = ? WHERE name = ?",
                    (value, name)
                )

    cache.invalidate("creditos_cards")
    return mark_updated("creditos")
