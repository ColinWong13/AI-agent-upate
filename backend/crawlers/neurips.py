"""
NeurIPS paper crawler via papers.nips.cc.
Scrapes the proceedings page for the most recent conference year.
"""
import asyncio
import logging
from datetime import date

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

PROCEEDINGS_URL = "https://papers.nips.cc"


async def fetch_papers() -> list[dict]:
    papers = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(PROCEEDINGS_URL)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Find the most recent year link
            year_links = soup.select("a[href*='/paper_files/paper/']")
            for link in year_links[:50]:  # limit to first 50 papers
                paper_url = link.get("href", "")
                title = link.text.strip()
                if not title or not paper_url:
                    continue

                full_url = paper_url if paper_url.startswith("http") else f"https://papers.nips.cc{paper_url}" if paper_url.startswith("/") else paper_url

                papers.append({
                    "source": "neurips",
                    "title": title,
                    "authors": [],
                    "abstract": "",
                    "url": full_url,
                    "pdf_url": "",
                    "published_date": date.today(),
                    "categories": ["cs.LG", "cs.AI"],
                })
    except Exception as e:
        logger.error(f"neurips fetch failed: {e}")
        raise

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            existing = await db.execute(
                select(Paper.id).where(
                    Paper.title == paper["title"],
                    Paper.source == "neurips",
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            db.add(Paper(**paper))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("neurips crawl started")
    try:
        papers = await fetch_papers()
        saved = await save_papers(papers)
        logger.info(f"neurips crawl done: {len(papers)} fetched, {saved} new")
        return {"fetched": len(papers), "saved": saved}
    except Exception as e:
        logger.error(f"neurips crawl failed: {e}")
        raise
