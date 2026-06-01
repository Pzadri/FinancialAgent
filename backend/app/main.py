from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.gbm_reader import get_full_portfolio, parse_nacional_excel, parse_usa_excel, save_gbm_data
from app.gi_manager import add_record, get_all_records, delete_record
from app.creditos_reader import get_credit_cards
from app.inversiones_reader import get_all_inversiones
from app.deudas_manager import get_all_deudas, add_deuda, delete_deuda
from app.update_tracker import get_status, mark_updated
from app.database import init_db
from app import cache

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
    """Check if GBM data needs to be updated (Mondays)."""
    return get_status("gbm", "monday")


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
