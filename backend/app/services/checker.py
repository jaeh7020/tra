import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AlertHistory, WatchRule
from app.services.notifier import send_line_message
from app.services.tdx import tdx_client

logger = logging.getLogger(__name__)

# Taiwan is UTC+8
TW_TZ = timezone(timedelta(hours=8))


async def check_all_rules():
    """Main polling job: check all active watch rules against live TDX data."""
    db: Session = SessionLocal()
    try:
        now_tw = datetime.now(TW_TZ)
        current_day = str(now_tw.weekday())  # 0=Monday
        current_time = now_tw.strftime("%H:%M")

        active_rules = db.query(WatchRule).filter(WatchRule.is_active == True).all()  # noqa: E712
        if not active_rules:
            return

        # Fetch live data from TDX
        try:
            delays = await tdx_client.get_live_delays()
            alerts = await tdx_client.get_alerts()
        except Exception:
            logger.exception("Failed to fetch TDX data")
            return

        # Index delays by train number for fast lookup
        delay_map: dict[str, int] = {}
        for d in delays:
            train_no = d.get("TrainNo", "")
            delay_min = d.get("DelayTime", 0)
            if train_no:
                delay_map[train_no] = delay_min

        # Build set of cancelled train numbers from alerts
        cancelled_trains: set[str] = set()
        for alert in alerts:
            # Alert structure varies; look for cancellation indicators
            status = alert.get("Status", "")
            if "cancel" in status.lower() or "停駛" in alert.get("Title", ""):
                affected = alert.get("AffectedSection", {})
                train_no = affected.get("TrainNo", "")
                if train_no:
                    cancelled_trains.add(train_no)

        for rule in active_rules:
            # Check if rule applies today
            if rule.days_of_week and current_day not in rule.days_of_week.split(","):
                continue

            matched_trains: list[tuple[str, int, bool]] = []  # (train_no, delay_min, is_cancelled)

            if rule.rule_type == "train_number" and rule.train_number:
                tn = rule.train_number
                is_cancelled = tn in cancelled_trains
                delay_min = delay_map.get(tn, 0)
                if delay_min > 0 or is_cancelled:
                    matched_trains.append((tn, delay_min, is_cancelled))

            elif rule.rule_type == "time_period":
                # Check time window
                if rule.start_time and rule.end_time:
                    if not (rule.start_time <= current_time <= rule.end_time):
                        continue
                # For time-period rules, report all delayed/cancelled trains
                for tn, delay_min in delay_map.items():
                    if delay_min > 0:
                        matched_trains.append((tn, delay_min, tn in cancelled_trains))
                for tn in cancelled_trains:
                    if tn not in delay_map:
                        matched_trains.append((tn, 0, True))

            # Record and notify
            for train_no, delay_min, is_cancelled in matched_trains:
                await _record_and_notify(db, rule, train_no, delay_min, is_cancelled)

    except Exception:
        logger.exception("Error in check_all_rules")
    finally:
        db.close()


async def _record_and_notify(
    db: Session,
    rule: WatchRule,
    train_no: str,
    delay_min: int,
    is_cancelled: bool,
):
    """Record an alert and send notification if not already recorded recently."""
    now_tw = datetime.now(TW_TZ)
    # Avoid duplicate alerts: skip if same train+rule was recorded in the last 10 minutes
    ten_min_ago = now_tw - timedelta(minutes=10)
    existing = (
        db.query(AlertHistory)
        .filter(
            AlertHistory.watch_rule_id == rule.id,
            AlertHistory.train_number == train_no,
            AlertHistory.detected_at >= ten_min_ago,
        )
        .first()
    )
    if existing:
        return

    alert = AlertHistory(
        watch_rule_id=rule.id,
        train_number=train_no,
        delay_minutes=delay_min,
        is_cancelled=is_cancelled,
        detected_at=now_tw,
    )
    db.add(alert)
    db.commit()

    # Send LINE message if user has linked their LINE account
    user = rule.user
    if user and user.line_user_id:
        if is_cancelled:
            msg = f"🚫 列車 {train_no} 已停駛 (取消)"
        else:
            msg = f"⚠️ 列車 {train_no} 誤點 {delay_min} 分鐘"
        success = await send_line_message(user.line_user_id, msg)
        if success:
            alert.notified = True
            db.commit()
