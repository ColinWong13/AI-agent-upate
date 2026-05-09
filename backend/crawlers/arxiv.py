"""
arXiv paper crawler using the official arXiv API.
API docs: https://info.arxiv.org/help/api/
"""
import asyncio
import logging
from datetime import datetime, timedelta, date
from xml.etree import ElementTree as ET

import httpx
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from config import CRAWL_REQUEST_DELAY_SECONDS
from database import AsyncSessionLocal
from models.paper import Paper

logger = logging.getLogger(__name__)

ARXIV_API = "https://export.arxiv.org/api/query"
CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "stat.ML"]
MAX_RESULTS = 100

ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_NS = "http://arxiv.org/schemas/atom"


def _text(el, tag):
    child = el.find(f"{{{ATOM_NS}}}{tag}")
    return child.text.strip() if child is not None and child.text else ""


def _arxiv_tag(el, tag):
    child = el.find(f"{{{ARXIV_NS}}}{tag}")
    return child.text.strip() if child is not None and child.text else ""


async def fetch_papers(days_back: int = 1) -> list[dict]:
    papers = []

    for category in CATEGORIES:
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": MAX_RESULTS,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.get(ARXIV_API, params=params)
                resp.raise_for_status()
                parsed = _parse_response(resp.text, category)
                cutoff = date.today() - timedelta(days=days_back)
                parsed = [p for p in parsed if p["published_date"] >= cutoff]
                papers.extend(parsed)
                logger.info(f"arxiv {category}: fetched {len(parsed)} papers")
        except Exception as e:
            logger.error(f"arxiv {category} fetch failed: {e}")
            raise

        await asyncio.sleep(CRAWL_REQUEST_DELAY_SECONDS)

    return papers


def _parse_response(xml_text: str, category: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    entries = root.findall(f"{{{ATOM_NS}}}entry")
    papers = []

    for entry in entries:
        title = _text(entry, "title").replace("\n", " ").strip()
        summary = _text(entry, "summary").replace("\n", " ").strip()
        published_str = _text(entry, "published")
        article_id = _text(entry, "id")

        authors = []
        for author in entry.findall(f"{{{ATOM_NS}}}author"):
            name = _text(author, "name")
            if name:
                authors.append(name)

        primary_cat = _arxiv_tag(entry, "primary_category")
        cat_list = [c.get("term", "") for c in entry.findall(f"{{{ARXIV_NS}}}category")]
        cat_list = [c for c in cat_list if c]

        try:
            published_date = datetime.strptime(published_str[:10], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            published_date = date.today()

        arxiv_id = article_id.split("/abs/")[-1] if "/abs/" in article_id else ""
        url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else article_id
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}" if arxiv_id else ""

        papers.append({
            "source": "arxiv",
            "title": title,
            "authors": authors,
            "abstract": summary,
            "url": url,
            "pdf_url": pdf_url,
            "published_date": published_date,
            "categories": cat_list or [primary_cat, category],
        })

    return papers


async def save_papers(papers: list[dict]) -> int:
    saved = 0
    async with AsyncSessionLocal() as db:
        for paper in papers:
            # Check duplicate by title + published_date
            existing = await db.execute(
                select(Paper.id).where(
                    Paper.title == paper["title"],
                    Paper.published_date == paper["published_date"],
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            db.add(Paper(**paper))
            saved += 1
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
    return saved


async def crawl():
    logger.info("arxiv crawl started")
    try:
        papers = await fetch_papers(days_back=2)
        saved = await save_papers(papers)
        logger.info(f"arxiv crawl done: {len(papers)} fetched, {saved} new")
        return {"fetched": len(papers), "saved": saved}
    except Exception as e:
        logger.error(f"arxiv crawl failed: {e}")
        raise
