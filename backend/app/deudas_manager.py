"""Module to manage Deudas (loan payments) Excel file."""
import openpyxl
from pathlib import Path
from datetime import date, timedelta

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "deudas"
DEUDAS_FILE = DATA_DIR / "deudas.xlsx"

HEADERS = ["ID", "Nombre", "Deuda Total", "Pago por Periodo", "Temporalidad", "Dia Pago 1", "Dia Pago 2", "Pagos Restantes", "Fecha Inicio 1", "Fecha Inicio 2"]


def ensure_file_exists():
    """Create the Excel file with headers if it doesn't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DEUDAS_FILE.exists():
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Deudas"
        ws.append(HEADERS)
        wb.save(DEUDAS_FILE)


def get_next_id() -> int:
    """Get the next available ID."""
    ensure_file_exists()
    wb = openpyxl.load_workbook(DEUDAS_FILE)
    ws = wb.active
    max_id = 0
    for row in ws.iter_rows(min_row=2, max_col=1, values_only=True):
        if row[0] and isinstance(row[0], (int, float)):
            max_id = max(max_id, int(row[0]))
    wb.close()
    return max_id + 1


def calculate_next_payment_date(temporalidad: str, dia1: int, dia2: int = 0, start_date1: str = "", start_date2: str = "") -> str:
    """Calculate the next payment date based on frequency and payment days.
    Uses start dates to determine the correct recurring schedule."""
    today = date.today()

    if temporalidad == "quincenal":
        # Two payment days per month based on the day numbers
        days = sorted(set([dia1] + ([dia2] if dia2 > 0 else [])))
        
        # Check if start dates are in the future
        for sd in [start_date1, start_date2]:
            if sd:
                try:
                    candidate = date.fromisoformat(sd)
                    if candidate > today:
                        # Find the earliest future start date
                        pass
                except (ValueError, TypeError):
                    pass

        # Find next occurrence of any payment day
        # Check current month
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
        # Monthly - check if start_date1 is in the future
        if start_date1:
            try:
                start = date.fromisoformat(start_date1)
                if start > today:
                    return start.isoformat()
            except (ValueError, TypeError):
                pass

        # Find next occurrence of payment day
        try:
            candidate = date(today.year, today.month, min(dia1, 28))
            if candidate > today:
                return candidate.isoformat()
        except ValueError:
            pass
        
        # Next month
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
    ensure_file_exists()
    record_id = get_next_id()

    # Calculate payments remaining
    pagos_restantes = int(deuda_total / pago_periodo) if pago_periodo > 0 else 0

    wb = openpyxl.load_workbook(DEUDAS_FILE)
    ws = wb.active
    ws.append([record_id, nombre, deuda_total, pago_periodo, temporalidad, dia1, dia2, pagos_restantes, start_date1, start_date2])
    wb.save(DEUDAS_FILE)
    wb.close()

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
    """Read all debts and calculate next payment dates."""
    ensure_file_exists()

    wb = openpyxl.load_workbook(DEUDAS_FILE, read_only=True)
    ws = wb.active

    deudas = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        try:
            record_id = int(row[0])
            nombre = str(row[1]) if row[1] else ""
            deuda_total = float(row[2]) if row[2] else 0
            pago_periodo = float(row[3]) if row[3] else 0
            temporalidad = str(row[4]) if row[4] else "mensual"
            dia1 = int(row[5]) if row[5] else 1
            dia2 = int(row[6]) if row[6] else 0
            pagos_restantes = int(row[7]) if row[7] else 0
            start_date1 = str(row[8]) if len(row) > 8 and row[8] else ""
            start_date2 = str(row[9]) if len(row) > 9 and row[9] else ""

            next_payment = calculate_next_payment_date(temporalidad, dia1, dia2, start_date1, start_date2)

            # Days until next payment
            today = date.today()
            next_date = date.fromisoformat(next_payment)
            days_until = (next_date - today).days

            deudas.append({
                "id": record_id,
                "name": nombre,
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
        except (ValueError, TypeError, IndexError):
            continue

    wb.close()
    return deudas


def delete_deuda(record_id: int) -> bool:
    """Delete a debt by ID."""
    ensure_file_exists()
    wb = openpyxl.load_workbook(DEUDAS_FILE)
    ws = wb.active

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_col=1, values_only=True), start=2):
        if row[0] and int(row[0]) == record_id:
            ws.delete_rows(row_idx)
            wb.save(DEUDAS_FILE)
            wb.close()
            return True

    wb.close()
    return False
