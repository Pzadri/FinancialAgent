"""Module to read and manage Inversiones data from SQLite."""
import re
from app.database import get_db
from app import cache


def get_ahorro() -> list[dict]:
    """Read savings accounts from SQLite."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM ahorro").fetchall()

    accounts = []
    for row in rows:
        balance = row["balance"]
        annual_rate = row["annual_rate"]
        daily_gain = (balance * annual_rate / 100) / 365

        accounts.append({
            "name": row["name"],
            "description": row["description"],
            "color": row["color"],
            "balance": balance,
            "annualRate": annual_rate,
            "dailyGain": round(daily_gain, 4)
        })

    return accounts


def get_prestamos() -> list[dict]:
    """Read loans from SQLite and calculate interest and total return."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM prestamos").fetchall()

    loans = []
    for row in rows:
        principal = row["principal"]
        rate = row["rate"]
        term_str = row["term"]
        months = _parse_term_to_months(term_str)

        expected_interest = principal * (rate / 100) * (months / 12)
        total_return = principal + expected_interest

        status_raw = row["status"].lower().strip()
        is_active = status_raw in ["activo", "en curso", "vigente"]
        status_label = "Activo" if is_active else "Pagado"

        loans.append({
            "id": row["id"],
            "borrower": row["borrower"],
            "principal": principal,
            "rate": rate,
            "term": term_str,
            "expectedInterest": round(expected_interest, 2),
            "totalReturn": round(total_return, 2),
            "status": "activo" if is_active else "pagado",
            "statusLabel": status_label
        })

    return loans


def _parse_term_to_months(term_str: str) -> int:
    """Parse term string to number of months."""
    term_lower = term_str.lower().strip()

    numbers = re.findall(r'\d+', term_lower)
    if not numbers:
        return 12

    num = int(numbers[0])

    if 'año' in term_lower or 'year' in term_lower:
        return num * 12
    if 'mes' in term_lower or 'month' in term_lower:
        return num

    return num


def get_afore() -> dict:
    """Read afore data from SQLite."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM afore WHERE id = 1").fetchone()

    if not row:
        return {"balance": 0, "annualReturn": 0, "bimonthlyContribution": 0, "voluntaryContribution": 0}

    return {
        "balance": row["balance"],
        "annualReturn": row["annual_return"],
        "bimonthlyContribution": row["bimonthly_contribution"],
        "voluntaryContribution": row["voluntary_contribution"]
    }


def update_ahorro_balances(balances: dict) -> str:
    """Update savings account balances in SQLite.

    Args:
        balances: dict mapping account name to new balance, e.g. {"Revolut": 8753.5}

    Returns:
        Today's date string (ISO format).
    """
    from app.update_tracker import mark_updated

    with get_db() as conn:
        for name, balance in balances.items():
            conn.execute(
                "UPDATE ahorro SET balance = ? WHERE name = ?",
                (balance, name)
            )

    cache.invalidate("inversiones_all")
    return mark_updated("ahorro")


def update_afore_data(fields: dict) -> str:
    """Update afore data in SQLite.

    Args:
        fields: dict with keys like 'balance', 'annualReturn', 'bimonthlyContribution', 'voluntaryContribution'

    Returns:
        Today's date string (ISO format).
    """
    from app.update_tracker import mark_updated

    # Map API field names to DB column names
    field_map = {
        "balance": "balance",
        "annualReturn": "annual_return",
        "bimonthlyContribution": "bimonthly_contribution",
        "voluntaryContribution": "voluntary_contribution",
    }

    with get_db() as conn:
        for api_key, value in fields.items():
            col = field_map.get(api_key)
            if col:
                conn.execute(f"UPDATE afore SET {col} = ? WHERE id = 1", (value,))

    cache.invalidate("inversiones_all")
    return mark_updated("afore")


def update_prestamos_data(prestamos_updates: list[dict]) -> str:
    """Update prestamos data in SQLite.

    Args:
        prestamos_updates: list of dicts with 'id' and fields to update (principal, rate, term, status)

    Returns:
        Today's date string (ISO format).
    """
    from app.update_tracker import mark_updated

    with get_db() as conn:
        for update in prestamos_updates:
            row_id = update.get("id")
            if row_id is None:
                continue
            if "principal" in update:
                conn.execute("UPDATE prestamos SET principal = ? WHERE id = ?", (update["principal"], row_id))
            if "rate" in update:
                conn.execute("UPDATE prestamos SET rate = ? WHERE id = ?", (update["rate"], row_id))
            if "term" in update:
                conn.execute("UPDATE prestamos SET term = ? WHERE id = ?", (update["term"], row_id))
            if "status" in update:
                conn.execute("UPDATE prestamos SET status = ? WHERE id = ?", (update["status"], row_id))

    cache.invalidate("inversiones_all")
    return mark_updated("prestamos")


def get_all_inversiones() -> dict:
    """Get all investment data. Cached for 5 minutes."""
    cached = cache.get("inversiones_all")
    if cached is not None:
        return cached

    ahorro = get_ahorro()
    prestamos = get_prestamos()
    afore = get_afore()

    total_savings = sum(a["balance"] for a in ahorro)
    active_loans = [l for l in prestamos if l["status"] == "activo"]
    total_loans = sum(l["principal"] for l in active_loans)
    total_loan_interest = sum(l["expectedInterest"] for l in active_loans)
    avg_loan_rate = (sum(l["rate"] for l in active_loans) / len(active_loans)) if active_loans else 0

    result = {
        "ahorro": ahorro,
        "prestamos": prestamos,
        "afore": afore,
        "summary": {
            "totalSavings": total_savings,
            "totalLoans": total_loans,
            "totalLoanInterest": total_loan_interest,
            "avgLoanRate": round(avg_loan_rate, 1)
        }
    }

    cache.set("inversiones_all", result, ttl_seconds=300)
    return result
