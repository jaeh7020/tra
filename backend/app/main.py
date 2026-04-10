import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import alerts, auth, line_webhook, trains, watch_rules
from app.services.reference_cache import refresh_reference_data
from app.services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create tables
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting TRA Monitor...")
    start_scheduler()
    # Refresh reference data on startup (run in background)
    asyncio.create_task(refresh_reference_data())
    yield
    # Shutdown
    stop_scheduler()
    from app.services.tdx import tdx_client
    await tdx_client.close()


app = FastAPI(
    title="TRA Train Monitor",
    description="Monitor Taiwan Railway trains for delays and cancellations",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(watch_rules.router)
app.include_router(trains.router)
app.include_router(alerts.router)
app.include_router(line_webhook.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
