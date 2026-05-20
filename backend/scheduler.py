"""
APScheduler configuration for periodic crawling tasks.
"""
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from crawlers import arxiv, neurips, iclr, icml, acl, cvpr
from crawlers.news_crawler import crawl as news_crawl
from services.digest import generate_paper_digest, generate_news_digest

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

    # ICML: every Monday at 11:00 Beijing time (UTC 03:00)
    scheduler.add_job(
        icml.crawl,
        CronTrigger(day_of_week="mon", hour=3, minute=7),
        id="icml_weekly",
        name="ICML weekly crawl",
        replace_existing=True,
    )

    # ACL: every Monday at 12:00 Beijing time (UTC 04:00)
    scheduler.add_job(
        acl.crawl,
        CronTrigger(day_of_week="mon", hour=4, minute=7),
        id="acl_weekly",
        name="ACL weekly crawl",
        replace_existing=True,
    )

    # CVPR: every Monday at 13:00 Beijing time (UTC 05:00)
    scheduler.add_job(
        cvpr.crawl,
        CronTrigger(day_of_week="mon", hour=5, minute=7),
        id="cvpr_weekly",
        name="CVPR weekly crawl",
        replace_existing=True,
    )

    # News RSS crawl: every 6 hours at minute 17
    scheduler.add_job(
        news_crawl,
        CronTrigger(hour="0,6,12,18", minute=17),
        id="news_rss_periodic",
        name="News RSS crawl every 6 hours",
        replace_existing=True,
    )

    # Paper weekly digest: Sunday at 20:00 Beijing time (UTC 12:00)
    scheduler.add_job(
        generate_paper_digest,
        CronTrigger(day_of_week="sun", hour=12, minute=7),
        id="paper_digest_weekly",
        name="Weekly paper digest generation",
        replace_existing=True,
    )

    # News weekly digest: Sunday at 20:30 Beijing time (UTC 12:30)
    scheduler.add_job(
        generate_news_digest,
        CronTrigger(day_of_week="sun", hour=12, minute=37),
        id="news_digest_weekly",
        name="Weekly news digest generation",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: arxiv daily, neurips/iclr/icml/acl/cvpr weekly, paper/news digest weekly")


def shutdown():
    scheduler.shutdown(wait=False)
    logger.info("Scheduler stopped")
