"""
News crawler for AI industry news.
Uses RSS feeds exclusively — web scraping proved unreliable due to JS-rendered pages.
All RSS feeds parsed with xml.etree.ElementTree for maximum compatibility.
"""
import asyncio
import logging
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.news import NewsItem

logger = logging.getLogger(__name__)

RSS_SOURCES = [
    {
        "name": "36氪",
        "url": "https://www.36kr.com/feed",
        "category": "行业资讯",
    },
    {
        "name": "量子位",
        "url": "https://www.qbitai.com/feed",
        "category": "行业资讯",
    },
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


def _parse_rss_date(date_str: str) -> datetime:
    """Parse an RSS pubDate string to UTC datetime. Falls back to now() on failure."""
    if not date_str:
        return datetime.now(timezone.utc)

    date_str = date_str.strip()

    # 1. RFC 2822: "Thu, 04 Jun 2026 03:43:37 +0000"
    try:
        return parsedate_to_datetime(date_str).astimezone(timezone.utc)
    except Exception:
        pass

    # 2. ISO 8601: "2026-06-04T07:13:46+00:00" or "2026-06-04T07:13:46.572304+00:00"
    try:
        return datetime.fromisoformat(date_str).astimezone(timezone.utc)
    except Exception:
        pass

    # 3. ISO-like with space: "2026-06-04 14:06:37 +0800"
    try:
        # Normalize to ISO format: replace space separator with T, handle tz offset
        normalized = date_str.replace(" ", "T", 1)
        # Handle "+0800" -> "+08:00"
        if normalized.endswith((" +0000", " +0800")) or any(
            normalized.endswith(f" {sign}{h:02d}{m:02d}")
            for sign in ("+", "-")
            for h in range(0, 24)
            for m in (0, 30)
        ):
            # Replace last 5 chars " +0800" with "+08:00"
            base = normalized[:-5]
            tz = normalized[-5:].replace(" ", "")
            normalized = base + tz[:3] + ":" + tz[3:]
        return datetime.fromisoformat(normalized).astimezone(timezone.utc)
    except Exception:
        pass

    # 4. Simple date: "2026-06-04"
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _strip_html(text: str) -> str:
    """Strip HTML tags and return plain text, truncated to 500 chars."""
    if not text:
        return ""
    try:
        return BeautifulSoup(text, "lxml").get_text()[:500].strip()
    except Exception:
        return text[:500].strip()


async def fetch_rss(source: dict) -> list[dict]:
    """Fetch entries from an RSS feed using ElementTree."""
    items = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers=headers) as client:
            resp = await client.get(source["url"])
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        # Handle both RSS 2.0 and Atom namespaces
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall(".//item") or root.findall(".//atom:entry", ns) or root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for entry in entries[:20]:
            # RSS 2.0
            title_el = entry.find("title")
            link_el = entry.find("link")
            desc_el = entry.find("description")
            date_el = entry.find("pubDate") or entry.find("published")

            # Fallback to Atom namespace
            if title_el is None:
                title_el = entry.find("{http://www.w3.org/2005/Atom}title") or entry.find("atom:title", ns)
            if link_el is None:
                link_el = entry.find("{http://www.w3.org/2005/Atom}link") or entry.find("atom:link", ns)
            if desc_el is None:
                desc_el = entry.find("{http://www.w3.org/2005/Atom}summary") or entry.find("atom:summary", ns)

            title = title_el.text.strip() if title_el is not None and title_el.text else ""
            if not title:
                continue

            # RSS <link> may be text or an href attribute
            url = ""
            if link_el is not None:
                url = (link_el.get("href") or link_el.text or "").strip()
            if not url:
                continue

            summary = _strip_html(desc_el.text) if desc_el is not None and desc_el.text else ""

            # Parse date
            date_text = date_el.text if date_el is not None and date_el.text else None
            pub_date = _parse_rss_date(date_text) if date_text else datetime.now(timezone.utc)

            items.append({
                "source_name": source["name"],
                "title": title,
                "summary": summary,
                "url": url,
                "category": source["category"],
                "published_date": pub_date,
            })

        logger.info(f"RSS {source['name']}: {len(items)} items")
    except Exception as e:
        logger.error(f"RSS {source['name']} failed: {e}")

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

    for source in RSS_SOURCES:
        items = await fetch_rss(source)
        all_items.extend(items)
        await asyncio.sleep(1)

    saved = await save_news_items(all_items)
    logger.info(f"news crawl done: {len(all_items)} fetched, {saved} new")
    return {"fetched": len(all_items), "saved": saved}
