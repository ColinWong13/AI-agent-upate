"""
APScheduler configuration for periodic crawling tasks.
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from crawlers import arxiv, neurips, iclr

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start():
    # arXiv: daily at 08:00 Beijing time (UTC+8 → UTC 00:00)
    scheduler.add_job(
        arxiv.crawl,
        CronTrigger(hour=0, minute=7),
        id="arxiv_daily",
        name="arXiv daily crawl",
        replace_existing=True,
    )

    # NeurIPS: every Monday at 09:00 Beijing time (UTC 01:00)
    scheduler.add_job(
        neurips.crawl,
        CronTrigger(day_of_week="mon", hour=1, minute=7),
        id="neurips_weekly",
        name="NeurIPS weekly crawl",
        replace_existing=True,
    )

    # ICLR: every Monday at 10:00 Beijing time (UTC 02:00)
    scheduler.add_job(
        iclr.crawl,
        CronTrigger(day_of_week="mon", hour=2, minute=7),
        id="iclr_weekly",
        name="ICLR weekly crawl",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: arxiv daily, neurips/iclr weekly")


def shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
