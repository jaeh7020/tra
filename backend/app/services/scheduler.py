import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings
from app.services.checker import check_all_rules
from app.services.tdx import tdx_client
from app.services.reference_cache import refresh_reference_data

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def _run_async(coro_func):
    """Wrapper to run an async function from APScheduler."""
    async def wrapper():
        await coro_func()
    def sync_wrapper():
        asyncio.get_event_loop().run_until_complete(wrapper())
    return sync_wrapper


def start_scheduler():
    """Register jobs and start the scheduler."""
    # Check train delays every N minutes
    scheduler.add_job(
        check_all_rules,
        trigger=IntervalTrigger(minutes=settings.SCHEDULER_INTERVAL_MINUTES),
        id="check_train_delays",
        name="Check train delays and cancellations",
        replace_existing=True,
    )

    # Refresh reference data (stations, train types) daily
    scheduler.add_job(
        refresh_reference_data,
        trigger=IntervalTrigger(hours=24),
        id="refresh_reference_data",
        name="Refresh station and train type cache",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: checking every %d minutes", settings.SCHEDULER_INTERVAL_MINUTES)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
