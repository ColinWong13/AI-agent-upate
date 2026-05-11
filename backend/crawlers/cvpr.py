"""
CVPR paper crawler via CVF Open Access.
Source: https://openaccess.thecvf.com/
"""
import logging
from datetime import date

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

CVPR_URL = "https://openaccess.thecvf.com"


async def fetch_papers() -> list[dict]:
    papers = []
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(f"{CVPR_URL}/CVPR2025", headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                resp = await client.get(f"{CVPR_URL}/CVPR2024", headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            for dt in soup.select("dt")[:30]:
                link = dt.find("a")
                if not link:
                    continue
                title = link.text.strip()
                href = link.get("href", "")
                url = f"{CVPR_URL}/{href}" if href.startswith("/") else href

                papers.append({
                    "source": "cvpr",
                    "title": title,
                    "authors": [],
                    "abstract": "",
                    "url": url,
                    "pdf_url": url.replace(".html", ".pdf") if ".html" in url else url,
                    "published_date": date.today(),
                    "categories": ["cs.CV", "cs.AI"],
                })
    except Exception as e:
        logger.error(f"cvpr fetch failed: {e}")
        raise

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            existing = await db.execute(
                select(Paper.id).where(Paper.title == paper["title"], Paper.source == "cvpr")
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Paper(**paper))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("cvpr crawl started")
    papers = await fetch_papers()
    saved = await save_papers(papers)
    logger.info(f"cvpr crawl done: {len(papers)} fetched, {saved} new")
    return {"fetched": len(papers), "saved": saved}
