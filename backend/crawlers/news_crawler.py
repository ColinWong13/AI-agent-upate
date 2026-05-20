"""
News crawler for AI industry news.
Strategy: RSS feeds + web scraping for Chinese AI news sites.
"""
import asyncio
import logging
from datetime import datetime, timezone

import feedparser
import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.news import NewsItem

logger = logging.getLogger(__name__)

# RSS sources (arXiv works globally, including China)
RSS_SOURCES = [
    {
        "name": "ArXiv CS.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "category": "学术资讯",
    },
    {
        "name": "ArXiv CS.CL",
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "category": "学术资讯",
    },
    {
        "name": "ArXiv CS.LG",
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "category": "学术资讯",
    },
]

# Chinese AI news sites to scrape (no API key needed)
SCRAPE_SOURCES = [
    {
        "name": "机器之心",
        "url": "https://www.jiqizhixin.com/",
        "category": "行业资讯",
        "item_selector": "article h2 a, .post-title a, a[href*='/articles/']",
        "base_url": "https://www.jiqizhixin.com",
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/",
        "category": "行业资讯",
        "item_selector": ".article-title a, .post-title a, a[href*='/article/']",
        "base_url": "https://www.qbitai.com",
    },
]


async def fetch_from_rss(source: dict) -> list[dict]:
    """Fetch entries from a single RSS feed."""
    items = []
    try:
        feed = feedparser.parse(source["url"])
        for entry in feed.entries[:15]:
            pub_date = datetime.now(timezone.utc)
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                except Exception:
                    pass

            title = (entry.title or "").strip()
            link = (entry.link or "").strip()
            if not title or not link:
                continue

            summary = ""
            if hasattr(entry, "summary") and entry.summary:
                summary = BeautifulSoup(entry.summary, "lxml").get_text()[:500].strip()
            elif hasattr(entry, "description") and entry.description:
                summary = BeautifulSoup(entry.description, "lxml").get_text()[:500].strip()

            items.append({
                "source_name": source["name"],
                "title": title,
                "summary": summary,
                "url": link,
                "category": source["category"],
                "published_date": pub_date,
            })
        logger.info(f"RSS {source['name']}: {len(items)} items")
    except Exception as e:
        logger.error(f"RSS {source['name']} failed: {e}")
    return items


async def fetch_from_web(source: dict) -> list[dict]:
    """Scrape headlines from a web page."""
    items = []
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers=headers) as client:
            resp = await client.get(source["url"])
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            links = soup.select(source["item_selector"])[:15]
            seen_urls = set()
            for a in links:
                title = a.get_text().strip()
                href = a.get("href", "")
                if not title or not href or len(title) < 6:
                    continue
                if href.startswith("/"):
                    href = source["base_url"].rstrip("/") + href
                if href in seen_urls:
                    continue
                seen_urls.add(href)

                items.append({
                    "source_name": source["name"],
                    "title": title,
                    "summary": "",
                    "url": href,
                    "category": source["category"],
                    "published_date": datetime.now(timezone.utc),
                })
            logger.info(f"Web {source['name']}: {len(items)} items")
    except Exception as e:
        logger.error(f"Web {source['name']} failed: {e}")
    return items


async def save_news_items(items: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for item in items:
            existing = await db.execute(
                select(NewsItem.id).where(NewsItem.url == item["url"])
            )
            if existing.scalar_one_or_none():
                continue
            db.add(NewsItem(**item))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("news crawl started")
    all_items = []

    # Phase 1: RSS (reliable)
    for source in RSS_SOURCES:
        items = await fetch_from_rss(source)
        all_items.extend(items)
        await asyncio.sleep(1)

    # Phase 2: Web scraping (Chinese sites)
    for source in SCRAPE_SOURCES:
        items = await fetch_from_web(source)
        all_items.extend(items)
        await asyncio.sleep(2)

    saved = await save_news_items(all_items)
    logger.info(f"news crawl done: {len(all_items)} fetched, {saved} new")
    return {"fetched": len(all_items), "saved": saved}
