from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, WatchRule
from app.routers.auth import get_current_user
from app.schemas import WatchRuleCreate, WatchRuleOut, WatchRuleUpdate

router = APIRouter(prefix="/api/rules", tags=["watch_rules"])


@router.get("", response_model=list[WatchRuleOut])
def list_rules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(WatchRule).filter(WatchRule.user_id == current_user.id).order_by(WatchRule.created_at.desc()).all()


@router.post("", response_model=WatchRuleOut, status_code=201)
def create_rule(
    data: WatchRuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if data.rule_type not in ("train_number", "time_period"):
        raise HTTPException(status_code=400, detail="rule_type must be 'train_number' or 'time_period'")
    if data.rule_type == "train_number" and not data.train_number:
        raise HTTPException(status_code=400, detail="train_number is required for train_number rules")
    if data.rule_type == "time_period" and (not data.station_id or not data.start_time or not data.end_time):
        raise HTTPException(status_code=400, detail="station_id, start_time, and end_time are required for time_period rules")

    rule = WatchRule(user_id=current_user.id, **data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/{rule_id}", response_model=WatchRuleOut)
def get_rule(rule_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id, WatchRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=WatchRuleOut)
def update_rule(
    rule_id: int,
    data: WatchRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id, WatchRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id, WatchRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()


@router.patch("/{rule_id}/toggle", response_model=WatchRuleOut)
def toggle_rule(rule_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rule = db.query(WatchRule).filter(WatchRule.id == rule_id, WatchRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    return rule
