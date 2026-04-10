from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertHistory, User, WatchRule
from app.routers.auth import get_current_user
from app.schemas import AlertHistoryOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertHistoryOut])
def list_alerts(
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List recent alerts for the current user's watch rules."""
    user_rule_ids = db.query(WatchRule.id).filter(WatchRule.user_id == current_user.id).subquery()
    return (
        db.query(AlertHistory)
        .filter(AlertHistory.watch_rule_id.in_(user_rule_ids))
        .order_by(AlertHistory.detected_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/rule/{rule_id}", response_model=list[AlertHistoryOut])
def list_alerts_for_rule(
    rule_id: int,
    limit: int = Query(50, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List alerts for a specific watch rule."""
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id, WatchRule.user_id == current_user.id).first()
    if not rule:
        return []
    return (
        db.query(AlertHistory)
        .filter(AlertHistory.watch_rule_id == rule_id)
        .order_by(AlertHistory.detected_at.desc())
        .limit(limit)
        .all()
    )
