"""Module to manage Deudas (loan payments) using SQLite."""
from datetime import date, timedelta
from app.database import get_db
from app import cache


def calculate_next_payment_date(temporalidad: str, dia1: int, dia2: int = 0, start_date1: str = "", start_date2: str = "") -> str:
    """Calculate the next payment date based on frequency and payment days."""
    today = date.today()

    if temporalidad == "quincenal":
        days = sorted(set([dia1] + ([dia2] if dia2 > 0 else [])))

        # Find next occurrence of any payment day in current month
        for d in days:
            try:
                day_clamped = min(d, 28)
                candidate = date(today.year, today.month, day_clamped)
                if candidate > today:
                    return candidate.isoformat()
            except ValueError:
                continue

        # Next month
        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1

        for d in days:
            try:
                return date(next_year, next_month, min(d, 28)).isoformat()
            except ValueError:
                continue

    else:
        # Monthly
        if start_date1:
            try:
                start = date.fromisoformat(start_date1)
                if start > today:
                    return start.isoformat()
            except (ValueError, TypeError):
                pass

        try:
            candidate = date(today.year, today.month, min(dia1, 28))
            if candidate > today:
                return candidate.isoformat()
        except ValueError:
            pass

        next_month = today.month + 1
        next_year = today.year
        if next_month > 12:
            next_month = 1
            next_year += 1
        try:
            return date(next_year, next_month, min(dia1, 28)).isoformat()
        except ValueError:
            return date(next_year, next_month, 28).isoformat()

    return today.isoformat()


def add_deuda(nombre: str, deuda_total: float, pago_periodo: float, temporalidad: str, dia1: int, dia2: int = 0, start_date1: str = "", start_date2: str = "") -> dict:
    """Add a new debt record."""
    pagos_restantes = int(deuda_total / pago_periodo) if pago_periodo > 0 else 0

    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO deudas (nombre, deuda_total, pago_periodo, temporalidad, dia_pago_1, dia_pago_2, pagos_restantes, fecha_inicio_1, fecha_inicio_2)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nombre, deuda_total, pago_periodo, temporalidad, dia1, dia2, pagos_restantes, start_date1, start_date2)
        )
        record_id = cursor.lastrowid

    cache.invalidate("deudas_all")

    next_payment = calculate_next_payment_date(temporalidad, dia1, dia2, start_date1, start_date2)

    return {
        "id": record_id,
        "name": nombre,
        "totalDebt": deuda_total,
        "paymentAmount": pago_periodo,
        "frequency": temporalidad,
        "payDay1": dia1,
        "payDay2": dia2,
        "paymentsRemaining": pagos_restantes,
        "nextPaymentDate": next_payment
    }


def get_all_deudas() -> list[dict]:
    """Read all debts and calculate next payment dates. Cached for 5 minutes.
    Automatically decrements pagos_restantes and deuda_total when a payment date passes."""
    cached = cache.get("deudas_all")
    if cached is not None:
        return cached

    with get_db() as conn:
        rows = conn.execute("SELECT * FROM deudas").fetchall()

    today = date.today()
    deudas = []

    for row in rows:
        temporalidad = row["temporalidad"]
        dia1 = row["dia_pago_1"]
        dia2 = row["dia_pago_2"]
        fecha_inicio_1 = row["fecha_inicio_1"]
        fecha_inicio_2 = row["fecha_inicio_2"]
        pagos_restantes = row["pagos_restantes"]
        deuda_total = row["deuda_total"]
        pago_periodo = row["pago_periodo"]

        # Check how many payment dates have passed that haven't been accounted for
        # We count payment days that are <= today in the current month (and previous if quincenal)
        payments_due = _count_passed_payments(temporalidad, dia1, dia2, pagos_restantes, deuda_total, pago_periodo, row["id"])

        # Refresh values after potential update
        if payments_due > 0:
            pagos_restantes = max(0, pagos_restantes - payments_due)
            deuda_total = max(0, deuda_total - (pago_periodo * payments_due))
            with get_db() as conn2:
                conn2.execute(
                    "UPDATE deudas SET pagos_restantes = ?, deuda_total = ? WHERE id = ?",
                    (pagos_restantes, deuda_total, row["id"])
                )

            # Auto-delete when fully paid
            if pagos_restantes <= 0:
                with get_db() as conn3:
                    conn3.execute("DELETE FROM deudas WHERE id = ?", (row["id"],))
                continue

        next_payment = calculate_next_payment_date(temporalidad, dia1, dia2, fecha_inicio_1, fecha_inicio_2)
        next_date = date.fromisoformat(next_payment)
        days_until = (next_date - today).days

        deudas.append({
            "id": row["id"],
            "name": row["nombre"],
            "totalDebt": deuda_total,
            "paymentAmount": pago_periodo,
            "frequency": temporalidad,
            "frequencyLabel": "Quincenal" if temporalidad == "quincenal" else "Mensual",
            "payDay1": dia1,
            "payDay2": dia2,
            "paymentsRemaining": pagos_restantes,
            "nextPaymentDate": next_payment,
            "daysUntilPayment": max(days_until, 0)
        })

    cache.set("deudas_all", deudas, ttl_seconds=300)
    return deudas


def _count_passed_payments(temporalidad, dia1, dia2, pagos_restantes, deuda_total, pago_periodo, deuda_id) -> int:
    """Count how many payment dates have fully passed (date complete: day+month+year).
    Uses the next payment date logic: if nextPaymentDate is in the future, no payment has passed
    since last check. Only decrements when a full payment date is in the past."""
    from app.update_tracker import get_last_update, mark_updated

    tracker_key = f"deuda_decrement_{deuda_id}"
    last_decrement = get_last_update(tracker_key)
    today = date.today()

    if pagos_restantes <= 0 or deuda_total <= 0:
        return 0

    # Determine the start date for counting
    if last_decrement:
        start = date.fromisoformat(last_decrement) + timedelta(days=1)
    else:
        # First time: mark today as baseline, don't decrement anything
        mark_updated(tracker_key)
        return 0

    if start > today:
        return 0

    # Build list of actual payment dates (full dates, not just days) between start and yesterday
    # Today's payment hasn't happened yet, so we only count dates strictly before today
    count = 0
    if temporalidad == "quincenal":
        days = sorted(set([dia1] + ([dia2] if dia2 > 0 else [])))
    else:
        days = [dia1]

    # Iterate month by month from start to today
    current_year = start.year
    current_month = start.month

    while True:
        for d in days:
            try:
                payment_date = date(current_year, current_month, min(d, 28))
            except ValueError:
                continue

            # Only count if payment_date is >= start AND strictly before today
            if payment_date >= start and payment_date < today:
                count += 1

        # Move to next month
        if current_year == today.year and current_month == today.month:
            break
        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1

    if count > 0:
        mark_updated(tracker_key)

    return min(count, pagos_restantes)


def delete_deuda(record_id: int) -> bool:
    """Delete a debt by ID."""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM deudas WHERE id = ?", (record_id,))
        deleted = cursor.rowcount > 0

    if deleted:
        cache.invalidate("deudas_all")
    return deleted
