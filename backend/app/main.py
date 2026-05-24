from fastapi import FastAPI, HTTPException, UploadFile, File
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.telegram_bot import send_telegram_message, get_bot_info, get_updates
from app.gbm_reader import get_full_portfolio
from app.gi_manager import add_record, get_all_records, delete_record
from app.creditos_reader import get_credit_cards
from app.inversiones_reader import get_all_inversiones
from app.deudas_manager import get_all_deudas, add_deuda, delete_deuda
from app.config import TELEGRAM_CHAT_ID
from app.update_tracker import get_status, mark_updated

GBM_DIR = Path(__file__).parent.parent.parent / "data" / "gbm"

app = FastAPI(title="Financial Dashboard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TelegramMessage(BaseModel):
    message: str
    chat_id: str | None = None


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "Financial Dashboard API"}


@app.get("/api/telegram/status")
async def telegram_status():
    """Check Telegram bot connection status."""
    try:
        bot_info = await get_bot_info()
        updates = await get_updates()

        chat_id = TELEGRAM_CHAT_ID
        if not chat_id and updates.get("result"):
            for update in updates["result"]:
                msg = update.get("message", {})
                if msg.get("chat"):
                    chat_id = str(msg["chat"]["id"])
                    break

        return {
            "connected": True,
            "bot_name": bot_info["result"]["first_name"],
            "bot_username": bot_info["result"]["username"],
            "chat_id": chat_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/telegram/send")
async def send_alert(payload: TelegramMessage):
    """Send a message/alert via Telegram bot."""
    try:
        chat_id = payload.chat_id or TELEGRAM_CHAT_ID

        if not chat_id:
            updates = await get_updates()
            if updates.get("result"):
                for update in updates["result"]:
                    msg = update.get("message", {})
                    if msg.get("chat"):
                        chat_id = str(msg["chat"]["id"])
                        break

        if not chat_id:
            raise HTTPException(
                status_code=400,
                detail="No chat_id available. Please send /start to @finARG_bot on Telegram first."
            )

        result = await send_telegram_message(payload.message, chat_id)
        return {"success": True, "message_id": result["result"]["message_id"]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telegram/updates")
async def telegram_updates():
    """Get recent bot updates (useful for debugging)."""
    try:
        updates = await get_updates()
        return updates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gbm/portfolio")
async def gbm_portfolio():
    """Get GBM portfolio data from Excel files."""
    try:
        data = get_full_portfolio()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gbm/update-status")
async def gbm_update_status():
    """Check if GBM data needs to be updated (Mondays)."""
    return get_status("gbm")


@app.post("/api/gbm/upload")
async def gbm_upload(
    nacional: UploadFile = File(...),
    usa: UploadFile = File(...)
):
    """Upload new GBM Excel files. Replaces portafolio-nacional.xlsx and portafolio-usa.xlsx."""
    # Validar que sean .xlsx
    for f in [nacional, usa]:
        if not f.filename.lower().endswith(".xlsx"):
            raise HTTPException(status_code=400, detail=f"El archivo '{f.filename}' no es un .xlsx válido.")

    try:
        GBM_DIR.mkdir(parents=True, exist_ok=True)

        # Guardar nacional
        nacional_path = GBM_DIR / "portafolio-nacional.xlsx"
        content = await nacional.read()
        nacional_path.write_bytes(content)

        # Guardar usa
        usa_path = GBM_DIR / "portafolio-usa.xlsx"
        content = await usa.read()
        usa_path.write_bytes(content)

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
    return get_status("ahorro")


@app.post("/api/inversiones/mark-updated")
async def inversiones_mark_updated():
    """Mark savings data as updated today."""
    today = mark_updated("ahorro")
    return {"success": True, "updatedAt": today}


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
