import hashlib
import hmac
import base64
import logging

import httpx
from fastapi import APIRouter, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal
from app.models import LinkNonce, User
from app.services.notifier import send_line_message

LINE_REPLY_URL = "https://api.line.me/v2/bot/message/reply"
LINE_LINK_TOKEN_URL = "https://api.line.me/v2/bot/user/{user_id}/linkToken"

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
    """LINE Messaging API webhook."""
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

            elif event_type == "message":
                line_user_id = event.get("source", {}).get("userId")
                reply_token = event.get("replyToken")
                if line_user_id and reply_token:
                    # Check if already linked
                    existing = db.query(User).filter(User.line_user_id == line_user_id).first()
                    if existing:
                        await _reply_text(
                            reply_token,
                            f"您的 LINE 帳號已綁定至 {existing.email}。\n"
                            "如需解除綁定，請至網站 Settings 頁面操作。"
                        )
                    else:
                        # Start account linking flow: get a link token from LINE
                        await _send_linking_message(reply_token, line_user_id)

            elif event_type == "accountLink":
                line_user_id = event.get("source", {}).get("userId")
                link = event.get("link", {})
                result = link.get("result")
                nonce = link.get("nonce")

                if result == "ok" and nonce and line_user_id:
                    # Look up the nonce to find the user
                    link_nonce = db.query(LinkNonce).filter(LinkNonce.nonce == nonce).first()
                    if link_nonce:
                        user = db.query(User).filter(User.id == link_nonce.user_id).first()
                        if user:
                            user.line_user_id = line_user_id
                            db.delete(link_nonce)
                            db.commit()
                            logger.info("Account linked: LINE %s → user %d (%s)", line_user_id, user.id, user.email)

                            # Send confirmation
                            await send_line_message(
                                line_user_id,
                                "TRA Train Monitor 連結成功！\n"
                                f"已綁定帳號：{user.email}\n"
                                "當您監控的列車發生誤點或停駛時，將會透過 LINE 通知您。"
                            )
                        else:
                            logger.warning("Nonce %s points to missing user %d", nonce, link_nonce.user_id)
                    else:
                        logger.warning("Unknown nonce in accountLink event: %s", nonce)
                else:
                    logger.warning("Account link failed: result=%s", result)

            elif event_type == "unfollow":
                line_user_id = event.get("source", {}).get("userId")
                if line_user_id:
                    logger.info("LINE unfollow event from user: %s", line_user_id)
                    user = db.query(User).filter(User.line_user_id == line_user_id).first()
                    if user:
                        user.line_user_id = None
                        db.commit()
                        logger.info("Unlinked LINE user %s from user %d", line_user_id, user.id)
    finally:
        db.close()

    return {"status": "ok"}


async def _send_linking_message(reply_token: str, line_user_id: str):
    """Request a link token from LINE and send the user a linking URL."""
    try:
        async with httpx.AsyncClient() as client:
            # Step 1: Get a link token from LINE
            resp = await client.post(
                LINE_LINK_TOKEN_URL.format(user_id=line_user_id),
                headers={"Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}"},
            )
            if resp.status_code != 200:
                logger.warning("Failed to get link token: %d %s", resp.status_code, resp.text)
                await _reply_text(reply_token, "連結失敗，請稍後再試。")
                return

            link_token = resp.json().get("linkToken")

            # Step 2: Send linking URL to the user
            linking_url = f"{settings.APP_URL}/api/auth/link-line-page?linkToken={link_token}"

            await client.post(
                LINE_REPLY_URL,
                headers={
                    "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "replyToken": reply_token,
                    "messages": [
                        {
                            "type": "text",
                            "text": (
                                "請點擊以下連結綁定您的 TRA Train Monitor 帳號：\n\n"
                                f"{linking_url}\n\n"
                                "連結將在 10 分鐘後失效。"
                            ),
                        }
                    ],
                },
            )
    except Exception:
        logger.exception("Failed to send linking message")


async def _reply_text(reply_token: str, text: str):
    """Send a simple text reply."""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                LINE_REPLY_URL,
                headers={
                    "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
                    "Content-Type": "application/json",
                },
                json={
                    "replyToken": reply_token,
                    "messages": [{"type": "text", "text": text}],
                },
            )
    except Exception:
        logger.exception("Failed to reply")
