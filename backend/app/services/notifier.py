import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


async def send_line_message(line_user_id: str, message: str) -> bool:
    """Send a push message via LINE Messaging API. Returns True on success."""
    if not settings.LINE_CHANNEL_ACCESS_TOKEN:
        logger.warning("LINE_CHANNEL_ACCESS_TOKEN not configured, skipping notification")
        return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                LINE_PUSH_URL,
                headers={
                    "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "to": line_user_id,
                    "messages": [{"type": "text", "text": message}],
                },
            )
            if resp.status_code == 200:
                return True
            logger.warning("LINE Messaging API returned %d: %s", resp.status_code, resp.text)
            return False
    except Exception:
        logger.exception("Failed to send LINE message")
        return False
