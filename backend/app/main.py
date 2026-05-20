from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.telegram_bot import send_telegram_message, get_bot_info, get_updates
from app.config import TELEGRAM_CHAT_ID

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
