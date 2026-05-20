import httpx
from app.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_telegram_message(message: str, chat_id: str = None) -> dict:
    """Send a message to a Telegram chat using the Bot API."""
    target_chat_id = chat_id or TELEGRAM_CHAT_ID

    if not target_chat_id:
        raise ValueError("No chat_id configured. Send /start to the bot first.")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": target_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
        )
        response.raise_for_status()
        return response.json()


async def get_bot_info() -> dict:
    """Get bot information to verify connection."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TELEGRAM_API_URL}/getMe")
        response.raise_for_status()
        return response.json()


async def get_updates() -> dict:
    """Get recent updates to find chat_id from users who messaged the bot."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TELEGRAM_API_URL}/getUpdates",
            params={"limit": 10, "offset": -10}
        )
        response.raise_for_status()
        return response.json()
