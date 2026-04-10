from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    line_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    watch_rules: Mapped[list["WatchRule"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class WatchRule(Base):
    __tablename__ = "watch_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "train_number" | "time_period"
    train_number: Mapped[str | None] = mapped_column(String(10), nullable=True)
    station_id: Mapped[str | None] = mapped_column(String(10), nullable=True)
    start_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "HH:MM"
    end_time: Mapped[str | None] = mapped_column(String(5), nullable=True)  # "HH:MM"
    days_of_week: Mapped[str | None] = mapped_column(String(20), nullable=True)  # "0,1,2,3,4" (Mon=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="watch_rules")
    alert_history: Mapped[list["AlertHistory"]] = relationship(back_populates="watch_rule", cascade="all, delete-orphan")


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    watch_rule_id: Mapped[int] = mapped_column(Integer, ForeignKey("watch_rules.id"), nullable=False)
    train_number: Mapped[str] = mapped_column(String(10), nullable=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    notified: Mapped[bool] = mapped_column(Boolean, default=False)

    watch_rule: Mapped["WatchRule"] = relationship(back_populates="alert_history")


class CachedStation(Base):
    __tablename__ = "cached_stations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    station_id: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name_zh: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=True)


class CachedTrainType(Base):
    __tablename__ = "cached_train_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    name_zh: Mapped[str] = mapped_column(String(50), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=True)
