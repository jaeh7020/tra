import hashlib
import hmac
import base64
import logging

from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/line", tags=["line"])


def verify_signature(body: bytes, signature: str) -> bool:
    """Verify the request came from LINE using the channel secret."""
    if not settings.LINE_CHANNEL_SECRET:
        return False
    mac = hmac.new(
        settings.LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    )
    return hmac.compare_digest(base64.b64encode(mac.digest()).decode("utf-8"), signature)


@router.post("/webhook")
async def line_webhook(request: Request, x_line_signature: str = Header(...)):
    """
    LINE Messaging API webhook. Handles 'follow' events to capture user IDs.

    When a user adds the bot as a friend, LINE sends a follow event with the
    user's LINE User ID. We store it if a user with a matching (not yet linked)
    account exists — otherwise we log it for manual linking via the Settings page.
    """
    body = await request.body()

    if not verify_signature(body, x_line_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    payload = await request.json()
    events = payload.get("events", [])

    db: Session = SessionLocal()
    try:
        for event in events:
            event_type = event.get("type")
            if event_type == "follow":
                line_user_id = event.get("source", {}).get("userId")
                if line_user_id:
                    logger.info("LINE follow event from user: %s", line_user_id)
                    # Check if any user already has this LINE ID linked
                    existing = db.query(User).filter(User.line_user_id == line_user_id).first()
                    if existing:
                        logger.info("LINE user %s already linked to user %d", line_user_id, existing.id)
                    else:
                        logger.info(
                            "LINE user %s not yet linked. User can link via Settings page with this ID.",
                            line_user_id,
                        )
            elif event_type == "unfollow":
                line_user_id = event.get("source", {}).get("userId")
                if line_user_id:
                    logger.info("LINE unfollow event from user: %s", line_user_id)
                    # Optionally unlink the user
                    user = db.query(User).filter(User.line_user_id == line_user_id).first()
                    if user:
                        user.line_user_id = None
                        db.commit()
                        logger.info("Unlinked LINE user %s from user %d", line_user_id, user.id)
    finally:
        db.close()

    return {"status": "ok"}
