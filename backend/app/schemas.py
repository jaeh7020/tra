from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- Auth ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str
    line_linked: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LineUserIdUpdate(BaseModel):
    line_user_id: str


# --- Watch Rules ---

class WatchRuleCreate(BaseModel):
    rule_type: str  # "train_number" | "time_period"
    train_number: str | None = None
    station_id: str | None = None
    start_time: str | None = None  # "HH:MM"
    end_time: str | None = None  # "HH:MM"
    days_of_week: str | None = None  # "0,1,2,3,4"


class WatchRuleUpdate(BaseModel):
    rule_type: str | None = None
    train_number: str | None = None
    station_id: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    days_of_week: str | None = None
    is_active: bool | None = None


class WatchRuleOut(BaseModel):
    id: int
    rule_type: str
    train_number: str | None
    station_id: str | None
    start_time: str | None
    end_time: str | None
    days_of_week: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Alerts ---

class AlertHistoryOut(BaseModel):
    id: int
    watch_rule_id: int
    train_number: str
    delay_minutes: int
    is_cancelled: bool
    detected_at: datetime
    notified: bool

    model_config = {"from_attributes": True}


# --- Trains (reference data) ---

class StationOut(BaseModel):
    station_id: str
    name_zh: str
    name_en: str | None

    model_config = {"from_attributes": True}


class TrainTypeOut(BaseModel):
    type_code: str
    name_zh: str
    name_en: str | None

    model_config = {"from_attributes": True}
