"""Module to read Creditos Excel file and return structured data."""
import openpyxl
from pathlib import Path
from datetime import date

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "creditos"
CREDITOS_FILE = DATA_DIR / "tarjetas.xlsx"


def get_credit_cards() -> dict:
    """Read credit card data from Excel."""
    if not CREDITOS_FILE.exists():
        return {"cards": [], "summary": {}}

    wb = openpyxl.load_workbook(CREDITOS_FILE, read_only=True)
    ws = wb.active

    cards = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue

        try:
            name = str(row[0])
            color = str(row[1]) if row[1] else "#1da1f2"
            credit_limit = float(row[2]) if row[2] else 0
            debt = float(row[3]) if row[3] else 0
            available = float(row[4]) if row[4] else 0
            cutoff_date = str(row[5]) if row[5] else ""
            payment_date = str(row[6]) if row[6] else ""
            minimum_payment = float(row[7]) if row[7] else 0
            full_payment = float(row[8]) if row[8] else 0

            usage_percent = round((debt / credit_limit) * 100) if credit_limit > 0 else 0

            # Calculate days until payment
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
                "name": name,
                "color": color,
                "creditLimit": credit_limit,
                "debt": debt,
                "available": available,
                "usagePercent": usage_percent,
                "cutoffDate": cutoff_date,
                "paymentDate": payment_date,
                "minimumPayment": minimum_payment,
                "fullPayment": full_payment,
                "daysUntilPayment": days_until
            })
        except (ValueError, TypeError, IndexError):
            continue

    wb.close()

    # Summary
    total_credit = sum(c["creditLimit"] for c in cards)
    total_debt = sum(c["debt"] for c in cards)
    total_available = sum(c["available"] for c in cards)
    total_payment = sum(c["fullPayment"] for c in cards)
    total_usage = round((total_debt / total_credit) * 100) if total_credit > 0 else 0

    return {
        "cards": cards,
        "summary": {
            "totalCredit": total_credit,
            "totalDebt": total_debt,
            "totalAvailable": total_available,
            "totalPayment": total_payment,
            "usagePercent": total_usage
        }
    }
