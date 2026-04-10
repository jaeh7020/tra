from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CachedStation, CachedTrainType
from app.schemas import StationOut, TrainTypeOut

router = APIRouter(prefix="/api/trains", tags=["trains"])


@router.get("/stations", response_model=list[StationOut])
def list_stations(db: Session = Depends(get_db)):
    return db.query(CachedStation).order_by(CachedStation.station_id).all()


@router.get("/types", response_model=list[TrainTypeOut])
def list_train_types(db: Session = Depends(get_db)):
    return db.query(CachedTrainType).order_by(CachedTrainType.type_code).all()


@router.get("/stations/search", response_model=list[StationOut])
def search_stations(q: str, db: Session = Depends(get_db)):
    return (
        db.query(CachedStation)
        .filter(CachedStation.name_zh.contains(q) | CachedStation.name_en.ilike(f"%{q}%"))
        .limit(20)
        .all()
    )
