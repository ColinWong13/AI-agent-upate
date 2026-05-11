"""
ICML paper crawler via PMLR (Proceedings of Machine Learning Research).
Source: https://proceedings.mlr.press/
"""
import logging
from datetime import date

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select

from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

PMLR_URL = "https://proceedings.mlr.press"


async def fetch_papers() -> list[dict]:
    papers = []
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            resp = await client.get(f"{PMLR_URL}/", headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Find ICML proceedings links
            for link in soup.select("a[href*='icml']")[:5]:
                vol_url = link.get("href", "")
                full_url = f"{PMLR_URL}{vol_url}" if vol_url.startswith("/") else vol_url
                # Fetch individual volume
                try:
                    vresp = await client.get(full_url)
                    vsoup = BeautifulSoup(vresp.text, "lxml")
                    for paper in vsoup.select(".paper")[:20]:
                        title_el = paper.find("p", class_="title")
                        if not title_el:
                            continue
                        title = title_el.text.strip()
                        papers.append({
                            "source": "icml",
                            "title": title,
                            "authors": [],
                            "abstract": "",
                            "url": full_url,
                            "pdf_url": "",
                            "published_date": date.today(),
                            "categories": ["cs.LG", "stat.ML"],
                        })
                except Exception:
                    pass
            if not papers:
                logger.warning("icml: no papers found on PMLR")
    except Exception as e:
        logger.error(f"icml fetch failed: {e}")
        raise

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            existing = await db.execute(
                select(Paper.id).where(Paper.title == paper["title"], Paper.source == "icml")
            )
            if existing.scalar_one_or_none():
                continue
            db.add(Paper(**paper))
            saved += 1
        await db.commit()
    return saved


async def crawl():
    logger.info("icml crawl started")
    papers = await fetch_papers()
    saved = await save_papers(papers)
    logger.info(f"icml crawl done: {len(papers)} fetched, {saved} new")
    return {"fetched": len(papers), "saved": saved}
