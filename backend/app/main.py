from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.gbm_reader import get_full_portfolio, parse_nacional_excel, parse_usa_excel, save_gbm_data
from app.gi_manager import add_record, get_all_records, delete_record, update_record
from app.creditos_reader import get_credit_cards
from app.inversiones_reader import get_all_inversiones
from app.deudas_manager import get_all_deudas, add_deuda, delete_deuda
from app.update_tracker import get_status, mark_updated
from app.database import init_db
from app import cache
from app import auth_manager

app = FastAPI(title="Financial Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
init_db()
# Ensure an auth password exists (seeds default if none set)
auth_manager.init_auth()


# ===== Autenticación =====

class LoginPayload(BaseModel):
    password: str


class ChangePasswordPayload(BaseModel):
    currentPassword: str
    newPassword: str


@app.get("/api/auth/status")
async def auth_status():
    """Indica si hay una contraseña configurada."""
    return {"passwordSet": auth_manager.is_password_set()}


@app.post("/api/auth/login")
async def auth_login(payload: LoginPayload):
    """Valida la contraseña contra el hash almacenado en la base de datos."""
    if not auth_manager.verify_password(payload.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
    token = auth_manager.create_token()
    return {"success": True, "token": token}


@app.post("/api/auth/change-password")
async def auth_change_password(payload: ChangePasswordPayload):
    """Cambia la contraseña tras verificar la actual."""
    if not auth_manager.verify_password(payload.currentPassword):
        raise HTTPException(status_code=401, detail="La contraseña actual es incorrecta.")
    try:
        auth_manager.set_password(payload.newPassword)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Financial Dashboard API"}


@app.get("/api/dashboard")
async def dashboard_data():
    """Consolidated endpoint for the Dashboard view.
    Returns all data needed in a single request instead of 5 separate calls."""
    try:
        gbm = get_full_portfolio()
        creditos = get_credit_cards()
        inversiones = get_all_inversiones()
        gi_records = get_all_records()
        deudas = get_all_deudas()

        total_debt = sum(d["totalDebt"] for d in deudas)

        return {
            "gbm": gbm,
            "creditos": creditos,
            "inversiones": inversiones,
            "gi": {"records": gi_records},
            "deudas": {"deudas": deudas, "totalDebt": total_debt}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gbm/portfolio")
async def gbm_portfolio():
    """Get GBM portfolio data from SQLite."""
    try:
        data = get_full_portfolio()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gbm/update-status")
async def gbm_update_status():
    """Check if GBM data needs to be updated (Fridays)."""
    return get_status("gbm", "friday")


@app.post("/api/gbm/upload")
async def gbm_upload(
    nacional: UploadFile = File(...),
    usa: UploadFile = File(...)
):
    """Upload new GBM Excel files. Parses them and replaces data in SQLite."""
    # Validar que sean .xlsx
    for f in [nacional, usa]:
        if not f.filename.lower().endswith(".xlsx"):
            raise HTTPException(status_code=400, detail=f"El archivo '{f.filename}' no es un .xlsx válido.")

    try:
        # Leer contenido de los archivos
        nacional_content = await nacional.read()
        usa_content = await usa.read()

        # Parsear los Excel
        nacional_data = parse_nacional_excel(nacional_content)
        usa_data = parse_usa_excel(usa_content)

        # Guardar en SQLite (borra datos anteriores y pone los nuevos)
        save_gbm_data(nacional_data, usa_data)

        # Marcar como actualizado
        today = mark_updated("gbm")

        return {
            "success": True,
            "updatedAt": today,
            "files": {
                "nacional": nacional.filename,
                "usa": usa.filename
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Gastos / Ingresos =====

class GIRecord(BaseModel):
    date: str
    description: str
    category: str
    type: str  # "ingreso" or "gasto"
    amount: float


@app.get("/api/gi/records")
async def gi_get_records():
    """Get all gastos/ingresos records from Excel."""
    try:
        records = get_all_records()
        return {"records": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gi/records")
async def gi_add_record(payload: GIRecord):
    """Add a new gasto/ingreso record to Excel."""
    try:
        record = add_record(
            fecha=payload.date,
            descripcion=payload.description,
            categoria=payload.category,
            tipo=payload.type,
            monto=payload.amount
        )
        return {"success": True, "record": record}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/gi/records/{record_id}")
async def gi_delete_record(record_id: int):
    """Delete a gasto/ingreso record by ID."""
    try:
        deleted = delete_record(record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/gi/records/{record_id}")
async def gi_update_record(record_id: int, payload: GIRecord):
    """Update a gasto/ingreso record by ID."""
    try:
        updated = update_record(
            record_id=record_id,
            fecha=payload.date,
            descripcion=payload.description,
            categoria=payload.category,
            tipo=payload.type,
            monto=payload.amount
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Record not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Créditos =====

@app.get("/api/creditos")
async def creditos_get():
    """Get credit card data from Excel."""
    try:
        data = get_credit_cards()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/creditos/update-status")
async def creditos_update_status():
    """Check if credit card data needs to be updated (Mondays)."""
    return get_status("creditos", "monday")


class CreditCardUpdate(BaseModel):
    name: str
    debt: float | None = None
    available: float | None = None
    cutoffDate: str | None = None
    paymentDate: str | None = None
    minimumPayment: float | None = None
    fullPayment: float | None = None
    creditLimit: float | None = None


@app.post("/api/creditos/update-card")
async def creditos_update_card(payload: CreditCardUpdate):
    """Update fields for a specific credit card."""
    from app.creditos_reader import update_credit_card
    try:
        fields = {k: v for k, v in payload.model_dump().items() if k != "name" and v is not None}
        today = update_credit_card(payload.name, fields)
        return {"success": True, "updatedAt": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Inversiones =====

@app.get("/api/inversiones")
async def inversiones_get():
    """Get all investment data from Excel files."""
    try:
        data = get_all_inversiones()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inversiones/update-status")
async def inversiones_update_status():
    """Check if savings data needs to be updated (Mondays)."""
    return get_status("ahorro", "monday")


@app.get("/api/inversiones/afore/update-status")
async def afore_update_status():
    """Check if afore data needs to be updated (1st of month)."""
    return get_status("afore", "first_of_month")


@app.post("/api/inversiones/afore/mark-updated")
async def afore_mark_updated():
    """Mark afore data as updated today."""
    today = mark_updated("afore")
    return {"success": True, "updatedAt": today}


class AforeUpdate(BaseModel):
    balance: float | None = None
    annualReturn: float | None = None
    bimonthlyContribution: float | None = None
    voluntaryContribution: float | None = None


@app.post("/api/inversiones/afore/update-data")
async def afore_update_data(payload: AforeUpdate):
    """Update afore fields in the Excel file."""
    from app.inversiones_reader import update_afore_data
    try:
        fields = {k: v for k, v in payload.model_dump().items() if v is not None}
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        today = update_afore_data(fields)
        return {"success": True, "updatedAt": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inversiones/prestamos/update-status")
async def prestamos_update_status():
    """Check if prestamos data needs to be updated (15th of month)."""
    return get_status("prestamos", "fifteenth")


@app.post("/api/inversiones/prestamos/mark-updated")
async def prestamos_mark_updated():
    """Mark prestamos data as updated today."""
    today = mark_updated("prestamos")
    return {"success": True, "updatedAt": today}


class PrestamoUpdate(BaseModel):
    id: int
    principal: float | None = None
    rate: float | None = None
    term: str | None = None
    status: str | None = None


class NuevoPrestamoPayload(BaseModel):
    principal: float
    rate: float
    termMonths: int


@app.post("/api/inversiones/prestamos")
async def prestamos_create(payload: NuevoPrestamoPayload):
    """Create a new loan (prestamo)."""
    from app.inversiones_reader import create_prestamo
    try:
        loan = create_prestamo(
            principal=payload.principal,
            rate=payload.rate,
            term_months=payload.termMonths
        )
        return {"success": True, "loan": loan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PrestamosUpdatePayload(BaseModel):
    updates: list[PrestamoUpdate]


@app.post("/api/inversiones/prestamos/update-data")
async def prestamos_update_data(payload: PrestamosUpdatePayload):
    """Update prestamos data in the Excel file."""
    from app.inversiones_reader import update_prestamos_data
    try:
        updates = [u.model_dump(exclude_none=True) for u in payload.updates]
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        today = update_prestamos_data(updates)
        return {"success": True, "updatedAt": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inversiones/mark-updated")
async def inversiones_mark_updated():
    """Mark savings data as updated today."""
    today = mark_updated("ahorro")
    return {"success": True, "updatedAt": today}


class AhorroBalances(BaseModel):
    balances: dict[str, float]  # {"Revolut": 8753.5, "Didi": 6149.7, ...}


@app.post("/api/inversiones/update-balances")
async def inversiones_update_balances(payload: AhorroBalances):
    """Update savings account balances in the Excel file."""
    from app.inversiones_reader import update_ahorro_balances
    try:
        today = update_ahorro_balances(payload.balances)
        return {"success": True, "updatedAt": today}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Deudas =====

class DeudaRecord(BaseModel):
    name: str
    totalDebt: float
    paymentAmount: float
    frequency: str  # "mensual" or "quincenal"
    payDay1: int
    payDay2: int = 0
    startDate1: str = ""
    startDate2: str = ""


@app.get("/api/deudas")
async def deudas_get():
    """Get all debts."""
    try:
        deudas = get_all_deudas()
        total_debt = sum(d["totalDebt"] for d in deudas)
        return {"deudas": deudas, "totalDebt": total_debt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deudas")
async def deudas_add(payload: DeudaRecord):
    """Add a new debt."""
    try:
        deuda = add_deuda(
            nombre=payload.name,
            deuda_total=payload.totalDebt,
            pago_periodo=payload.paymentAmount,
            temporalidad=payload.frequency,
            dia1=payload.payDay1,
            dia2=payload.payDay2,
            start_date1=payload.startDate1,
            start_date2=payload.startDate2
        )
        return {"success": True, "deuda": deuda}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/deudas/{record_id}")
async def deudas_delete(record_id: int):
    """Delete a debt by ID."""
    try:
        deleted = delete_deuda(record_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Debt not found")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Aportaciones =====

class AportacionStatusUpdate(BaseModel):
    id: int
    status: str  # "pendiente" | "realizada" | "atrasada"


@app.get("/api/aportaciones")
async def aportaciones_get(year: int | None = None, month: int | None = None):
    """Get aportaciones for a given month (defaults to current month)."""
    from app.aportaciones_manager import get_aportaciones
    from datetime import date as d
    try:
        today = d.today()
        y = year or today.year
        m = month or today.month
        data = get_aportaciones(y, m)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/aportaciones/update-status")
async def aportaciones_update_status(payload: AportacionStatusUpdate):
    """Update the status of an aportacion."""
    from app.aportaciones_manager import update_aportacion_status
    try:
        updated = update_aportacion_status(payload.id, payload.status)
        if not updated:
            raise HTTPException(status_code=400, detail="Invalid ID or status")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===== Configuración =====

# --- Ahorro CRUD ---

class AhorroCreate(BaseModel):
    name: str
    description: str = ""
    annualRate: float = 0
    color: str = "#1da1f2"
    rateCap: float = 0
    excessRate: float = 0


class AhorroUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    annualRate: float | None = None
    color: str | None = None
    rateCap: float | None = None
    excessRate: float | None = None


@app.get("/api/config/ahorro")
async def config_ahorro_list():
    """List all savings accounts."""
    from app.database import get_db
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM ahorro").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/config/ahorro")
async def config_ahorro_create(payload: AhorroCreate):
    """Create a new savings account."""
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO ahorro (name, description, color, balance, annual_rate, rate_cap, excess_rate) VALUES (?, ?, ?, 0, ?, ?, ?)",
            (payload.name, payload.description, payload.color, payload.annualRate, payload.rateCap, payload.excessRate)
        )
        new_id = cursor.lastrowid
    cache.invalidate("inversiones_all")
    return {"success": True, "id": new_id}


@app.put("/api/config/ahorro/{account_id}")
async def config_ahorro_update(account_id: int, payload: AhorroUpdate):
    """Update a savings account."""
    from app.database import get_db
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    field_map = {"name": "name", "description": "description", "annualRate": "annual_rate", "color": "color", "rateCap": "rate_cap", "excessRate": "excess_rate"}
    with get_db() as conn:
        for api_field, value in fields.items():
            col = field_map.get(api_field)
            if col:
                conn.execute(f"UPDATE ahorro SET {col} = ? WHERE id = ?", (value, account_id))
    cache.invalidate("inversiones_all")
    return {"success": True}


@app.delete("/api/config/ahorro/{account_id}")
async def config_ahorro_delete(account_id: int):
    """Delete a savings account."""
    from app.database import get_db
    with get_db() as conn:
        result = conn.execute("DELETE FROM ahorro WHERE id = ?", (account_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Account not found")
    cache.invalidate("inversiones_all")
    return {"success": True}


# --- Creditos CRUD ---

class CreditoCreate(BaseModel):
    name: str
    color: str = "#1da1f2"


class CreditoConfigUpdate(BaseModel):
    name: str | None = None
    color: str | None = None


@app.get("/api/config/creditos")
async def config_creditos_list():
    """List all credit cards (config fields only)."""
    from app.database import get_db
    with get_db() as conn:
        rows = conn.execute("SELECT id, name, color FROM creditos").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/config/creditos")
async def config_creditos_create(payload: CreditoCreate):
    """Create a new credit card."""
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO creditos (name, color) VALUES (?, ?)",
            (payload.name, payload.color)
        )
        new_id = cursor.lastrowid
    cache.invalidate("creditos_cards")
    return {"success": True, "id": new_id}


@app.put("/api/config/creditos/{card_id}")
async def config_creditos_update(card_id: int, payload: CreditoConfigUpdate):
    """Update a credit card's config fields."""
    from app.database import get_db
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    with get_db() as conn:
        for field, value in fields.items():
            conn.execute(f"UPDATE creditos SET {field} = ? WHERE id = ?", (value, card_id))
    cache.invalidate("creditos_cards")
    return {"success": True}


@app.delete("/api/config/creditos/{card_id}")
async def config_creditos_delete(card_id: int):
    """Delete a credit card."""
    from app.database import get_db
    with get_db() as conn:
        result = conn.execute("DELETE FROM creditos WHERE id = ?", (card_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Card not found")
    cache.invalidate("creditos_cards")
    return {"success": True}


# --- Aportaciones Config CRUD ---

class AportacionConfigCreate(BaseModel):
    category: str
    amount: float
    person: str = ""
    color: str = "#1da1f2"


class AportacionConfigUpdate(BaseModel):
    category: str | None = None
    amount: float | None = None
    person: str | None = None
    color: str | None = None


@app.get("/api/config/aportaciones")
async def config_aportaciones_list():
    """List all aportaciones config entries."""
    from app.database import get_db
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM aportaciones_config").fetchall()
    return [dict(row) for row in rows]


@app.post("/api/config/aportaciones")
async def config_aportaciones_create(payload: AportacionConfigCreate):
    """Create a new aportacion config."""
    from app.database import get_db
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO aportaciones_config (category, amount, person, color) VALUES (?, ?, ?, ?)",
            (payload.category, payload.amount, payload.person, payload.color)
        )
        new_id = cursor.lastrowid

        # Sync Afore voluntary contribution
        if payload.category.lower() == "afore" and not payload.person:
            conn.execute("UPDATE afore SET voluntary_contribution = ? WHERE id = 1", (payload.amount,))
            cache.invalidate("inversiones_all")

    cache.invalidate_prefix("aportaciones")
    return {"success": True, "id": new_id}


@app.put("/api/config/aportaciones/{config_id}")
async def config_aportaciones_update(config_id: int, payload: AportacionConfigUpdate):
    """Update an aportacion config entry."""
    from app.database import get_db
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    with get_db() as conn:
        for field, value in fields.items():
            conn.execute(f"UPDATE aportaciones_config SET {field} = ? WHERE id = ?", (value, config_id))

        # Sync Afore voluntary contribution if amount changed
        if "amount" in fields:
            row = conn.execute("SELECT category, person FROM aportaciones_config WHERE id = ?", (config_id,)).fetchone()
            if row and row["category"].lower() == "afore" and not row["person"]:
                conn.execute("UPDATE afore SET voluntary_contribution = ? WHERE id = 1", (fields["amount"],))
                cache.invalidate("inversiones_all")

    cache.invalidate_prefix("aportaciones")
    return {"success": True}


@app.delete("/api/config/aportaciones/{config_id}")
async def config_aportaciones_delete(config_id: int):
    """Delete an aportacion config entry."""
    from app.database import get_db
    with get_db() as conn:
        result = conn.execute("DELETE FROM aportaciones_config WHERE id = ?", (config_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Config not found")
    cache.invalidate_prefix("aportaciones")
    return {"success": True}


# ===== Patrimonio Neto =====

@app.get("/api/patrimonio")
async def patrimonio_get():
    """Get patrimonio neto history (last 6 months).
    Automatically takes a snapshot on the 1st of the current month if not already done."""
    from app.database import get_db
    from datetime import date as d

    today = d.today()
    current_month_key = f"{today.year}-{str(today.month).zfill(2)}"

    # Auto-snapshot on the 1st (or first access of the month)
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM patrimonio_neto WHERE month = ?", (current_month_key,)
        ).fetchone()

    if not existing:
        # Calculate current patrimonio neto
        try:
            inversiones = get_all_inversiones()
            gbm = get_full_portfolio()
            creditos = get_credit_cards()

            total_savings = sum(a["balance"] for a in inversiones.get("ahorro", []))
            total_loans = inversiones.get("summary", {}).get("totalLoans", 0)
            gbm_total = gbm.get("summary", {}).get("totalValueMXN", 0)
            afore_balance = inversiones.get("afore", {}).get("balance", 0)
            total_portfolio = total_savings + total_loans + gbm_total + afore_balance

            total_credit_debt = creditos.get("summary", {}).get("totalDebt", 0)
            patrimonio = total_portfolio - total_credit_debt

            with get_db() as conn:
                conn.execute(
                    "INSERT INTO patrimonio_neto (month, value) VALUES (?, ?)",
                    (current_month_key, round(patrimonio, 2))
                )
        except Exception:
            pass

    # Return last 6 months
    with get_db() as conn:
        rows = conn.execute(
            "SELECT month, value FROM patrimonio_neto ORDER BY month DESC LIMIT 6"
        ).fetchall()

    # Reverse to chronological order
    history = [{"month": row["month"], "value": row["value"]} for row in reversed(rows)]
    return {"history": history}


@app.post("/api/patrimonio/snapshot")
async def patrimonio_snapshot():
    """Force a patrimonio neto snapshot for the current month (creates or updates)."""
    from app.database import get_db
    from datetime import date as d

    today = d.today()
    current_month_key = f"{today.year}-{str(today.month).zfill(2)}"

    try:
        inversiones = get_all_inversiones()
        gbm = get_full_portfolio()
        creditos = get_credit_cards()

        total_savings = sum(a["balance"] for a in inversiones.get("ahorro", []))
        total_loans = inversiones.get("summary", {}).get("totalLoans", 0)
        gbm_total = gbm.get("summary", {}).get("totalValueMXN", 0)
        afore_balance = inversiones.get("afore", {}).get("balance", 0)
        total_portfolio = total_savings + total_loans + gbm_total + afore_balance

        total_credit_debt = creditos.get("summary", {}).get("totalDebt", 0)
        patrimonio = total_portfolio - total_credit_debt

        with get_db() as conn:
            conn.execute(
                """INSERT INTO patrimonio_neto (month, value) VALUES (?, ?)
                   ON CONFLICT(month) DO UPDATE SET value = ?""",
                (current_month_key, round(patrimonio, 2), round(patrimonio, 2))
            )

        return {"success": True, "month": current_month_key, "value": round(patrimonio, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
