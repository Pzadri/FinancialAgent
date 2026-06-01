"""SQLite database module for Financial Dashboard."""
import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).parent.parent.parent / "data" / "financial.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row_factory set to dict."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize database schema."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS ahorro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                color TEXT DEFAULT '#1da1f2',
                balance REAL DEFAULT 0,
                annual_rate REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS prestamos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                borrower TEXT NOT NULL,
                principal REAL DEFAULT 0,
                rate REAL DEFAULT 0,
                term TEXT DEFAULT '',
                status TEXT DEFAULT 'activo'
            );

            CREATE TABLE IF NOT EXISTS afore (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                balance REAL DEFAULT 0,
                annual_return REAL DEFAULT 0,
                bimonthly_contribution REAL DEFAULT 0,
                voluntary_contribution REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS creditos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                color TEXT DEFAULT '#1da1f2',
                credit_limit REAL DEFAULT 0,
                debt REAL DEFAULT 0,
                available REAL DEFAULT 0,
                cutoff_date TEXT DEFAULT '',
                payment_date TEXT DEFAULT '',
                minimum_payment REAL DEFAULT 0,
                full_payment REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS gastos_ingresos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                descripcion TEXT DEFAULT '',
                categoria TEXT DEFAULT '',
                tipo TEXT DEFAULT '',
                monto REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS deudas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                deuda_total REAL DEFAULT 0,
                pago_periodo REAL DEFAULT 0,
                temporalidad TEXT DEFAULT 'mensual',
                dia_pago_1 INTEGER DEFAULT 1,
                dia_pago_2 INTEGER DEFAULT 0,
                pagos_restantes INTEGER DEFAULT 0,
                fecha_inicio_1 TEXT DEFAULT '',
                fecha_inicio_2 TEXT DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS gbm_nacional (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                section TEXT DEFAULT '',
                shares REAL DEFAULT 0,
                avg_cost REAL DEFAULT 0,
                market_price REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                gain_loss REAL DEFAULT 0,
                return_pct REAL DEFAULT 0,
                var_day_pct REAL DEFAULT 0,
                portfolio_pct REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS gbm_usa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                section TEXT DEFAULT '',
                shares REAL DEFAULT 0,
                avg_cost REAL DEFAULT 0,
                market_price REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                gain_loss REAL DEFAULT 0,
                return_pct REAL DEFAULT 0,
                var_day_pct REAL DEFAULT 0,
                cost_value REAL DEFAULT 0,
                portfolio_pct REAL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS update_tracker (
                section TEXT PRIMARY KEY,
                last_update TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS aportaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                week_start TEXT NOT NULL,
                week_end TEXT NOT NULL,
                status TEXT DEFAULT 'pendiente',
                person TEXT DEFAULT ''
            );
        """)
