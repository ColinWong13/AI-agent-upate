"""
ICLR paper crawler via OpenReview API.
"""
import asyncio
import logging
from datetime import date

import httpx
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

OPENREVIEW_API = "https://api.openreview.net/notes"


async def fetch_papers() -> list[dict]:
    papers = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(OPENREVIEW_API, params={
                "invitation": "ICLR.cc/2025/Conference/-/Blind_Submission",
                "details": "replyCount",
                "limit": 50,
            })
            if resp.status_code != 200:
                logger.warning(f"OpenReview returned {resp.status_code}")
                return []

            data = resp.json()
            for note in data.get("notes", []):
                title = note.get("content", {}).get("title", "")
                abstract = note.get("content", {}).get("abstract", "")
                authors_list = note.get("content", {}).get("authors", [])
                if not title:
                    continue

                papers.append({
                    "source": "iclr",
                    "title": title,
                    "authors": authors_list if isinstance(authors_list, list) else [authors_list],
                    "abstract": abstract if abstract else "",
                    "url": f"https://openreview.net/forum?id={note.get('id', '')}",
                    "pdf_url": f"https://openreview.net/pdf?id={note.get('id', '')}",
                    "published_date": date.today(),
                    "categories": ["cs.LG", "cs.AI"],
                })
    except Exception as e:
        logger.error(f"iclr fetch failed: {e}")
        raise

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            existing = await db.execute(
                select(Paper.id).where(
                    Paper.title == paper["title"],
                    Paper.source == "iclr",
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            db.add(Paper(**paper))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("iclr crawl started")
    try:
        papers = await fetch_papers()
        saved = await save_papers(papers)
        logger.info(f"iclr crawl done: {len(papers)} fetched, {saved} new")
        return {"fetched": len(papers), "saved": saved}
    except Exception as e:
        logger.error(f"iclr crawl failed: {e}")
        raise
