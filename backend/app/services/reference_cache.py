import logging

from app.database import SessionLocal
from app.models import CachedStation, CachedTrainType
from app.services.tdx import tdx_client

logger = logging.getLogger(__name__)


async def refresh_reference_data():
    """Fetch stations and train types from TDX and cache them in SQLite."""
    db = SessionLocal()
    try:
        await _refresh_stations(db)
        await _refresh_train_types(db)
        logger.info("Reference data refreshed successfully")
    except Exception:
        logger.exception("Failed to refresh reference data")
    finally:
        db.close()


async def _refresh_stations(db):
    stations = await tdx_client.get_stations()
    # Clear existing cache
    db.query(CachedStation).delete()
    for s in stations:
        name = s.get("StationName", {})
        db.add(CachedStation(
            station_id=s.get("StationID", ""),
            name_zh=name.get("Zh_tw", ""),
            name_en=name.get("En", ""),
        ))
    db.commit()


async def _refresh_train_types(db):
    train_types = await tdx_client.get_train_types()
    db.query(CachedTrainType).delete()
    for t in train_types:
        name = t.get("TrainTypeName", {})
        db.add(CachedTrainType(
            type_code=t.get("TrainTypeCode", ""),
            name_zh=name.get("Zh_tw", ""),
            name_en=name.get("En", ""),
        ))
    db.commit()
