"""
ACL Anthology paper crawler.
Source: https://aclanthology.org/
"""
import logging
from datetime import date

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

ACL_URL = "https://aclanthology.org"


async def fetch_papers() -> list[dict]:
    papers = []
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            # Get recent papers from the main page
            resp = await client.get(f"{ACL_URL}/", headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Find paper entries
            for item in soup.select("p.align-items-center")[:30]:
                link = item.find("a")
                if not link:
                    continue
                title = link.text.strip()
                href = link.get("href", "")
                url = f"{ACL_URL}{href}" if href.startswith("/") else href

                papers.append({
                    "source": "acl",
                    "title": title,
                    "authors": [],
                    "abstract": "",
                    "url": url,
                    "pdf_url": url.rstrip("/") + ".pdf" if url else "",
                    "published_date": date.today(),
                    "categories": ["cs.CL", "cs.AI"],
                })
    except Exception as e:
        logger.error(f"acl fetch failed: {e}")
        raise

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            existing = await db.execute(
                select(Paper.id).where(Paper.title == paper["title"], Paper.source == "acl")
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Paper(**paper))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("acl crawl started")
    papers = await fetch_papers()
    saved = await save_papers(papers)
    logger.info(f"acl crawl done: {len(papers)} fetched, {saved} new")
    return {"fetched": len(papers), "saved": saved}
