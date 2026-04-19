from typing import Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.db.engine import SessionLocal
from src.db.models import Source
from src.core.crawler import crawl_source

_scheduler: Optional[BackgroundScheduler] = None


def get_scheduler() -> BackgroundScheduler:
    """Return the scheduler instance (does not auto-start)."""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def start_scheduler() -> BackgroundScheduler:
    """Start scheduler and load jobs. Idempotent."""
    scheduler = get_scheduler()
    if not scheduler.running:
        scheduler.start()
        _load_jobs()
    return scheduler


def shutdown_scheduler() -> None:
    """Gracefully shutdown the scheduler."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
    _scheduler = None


def _load_jobs():
    """Load active sources and schedule their crawl jobs."""
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.is_active == True).all()
        for source in sources:
            if source.schedule:
                add_crawl_job(source.id, source.schedule)
    finally:
        db.close()


def add_crawl_job(source_id: int, cron: str):
    """Add or update a crawl job for a source."""
    scheduler = get_scheduler()
    job_id = f"crawl_source_{source_id}"

    # Remove existing job if any
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)

    scheduler.add_job(
        crawl_source,
        trigger=CronTrigger.from_crontab(cron),
        id=job_id,
        args=[source_id],
        replace_existing=True,
    )


def remove_crawl_job(source_id: int):
    """Remove a crawl job."""
    scheduler = get_scheduler()
    job_id = f"crawl_source_{source_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
