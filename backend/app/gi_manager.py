"""Module to manage Gastos/Ingresos using SQLite."""
from datetime import date
from dateutil.relativedelta import relativedelta
from app.database import get_db
from app import cache


def add_record(fecha: str, descripcion: str, categoria: str, tipo: str, monto: float) -> dict:
    """Add a new gasto/ingreso record."""
    # Monto negativo para gastos, positivo para ingresos
    if tipo == "gasto":
        monto = -abs(monto)
    else:
        monto = abs(monto)

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO gastos_ingresos (fecha, descripcion, categoria, tipo, monto) VALUES (?, ?, ?, ?, ?)",
            (fecha, descripcion, categoria, tipo, monto)
        )
        record_id = cursor.lastrowid

    cache.invalidate("gi_records")

    return {
        "id": record_id,
        "date": fecha,
        "description": descripcion,
        "category": categoria,
        "type": tipo,
        "amount": monto
    }


def _purge_old_records():
    """Delete records older than 6 months."""
    today = date.today()
    cutoff = date(today.year, today.month, 1) - relativedelta(months=5)

    with get_db() as conn:
        conn.execute(
            "DELETE FROM gastos_ingresos WHERE fecha < ?",
            (cutoff.isoformat(),)
        )


def get_all_records() -> list[dict]:
    """Read all records. Cached for 5 minutes.
    Also triggers cleanup of records older than 6 months."""
    cached = cache.get("gi_records")
    if cached is not None:
        return cached

    _purge_old_records()

    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM gastos_ingresos ORDER BY fecha DESC"
        ).fetchall()

    records = []
    for row in rows:
        records.append({
            "id": row["id"],
            "date": row["fecha"],
            "description": row["descripcion"],
            "category": row["categoria"],
            "type": row["tipo"],
            "amount": row["monto"]
        })

    cache.set("gi_records", records, ttl_seconds=300)
    return records


def delete_record(record_id: int) -> bool:
    """Delete a record by ID."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM gastos_ingresos WHERE id = ?", (record_id,)
        )
        deleted = cursor.rowcount > 0

    if deleted:
        cache.invalidate("gi_records")
    return deleted
