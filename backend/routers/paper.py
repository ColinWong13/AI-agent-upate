from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.paper import Paper

router = APIRouter(prefix="/api/papers", tags=["papers"])


@router.get("")
async def list_papers(
    source: str | None = Query(None, description="arxiv / neurips / iclr"),
    keyword: str | None = Query(None, description="search in title and abstract"),
    date_from: date | None = Query(None, description="start date (YYYY-MM-DD)"),
    date_to: date | None = Query(None, description="end date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    q = select(Paper)

    if source:
        q = q.where(Paper.source == source)
    if keyword:
        pattern = f"%{keyword}%"
        q = q.where(
            (Paper.title.ilike(pattern)) | (Paper.abstract.ilike(pattern))
        )
    if date_from:
        q = q.where(Paper.published_date >= date_from)
    if date_to:
        q = q.where(Paper.published_date <= date_to)

    # Count total
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Paginate
    offset = (page - 1) * size
    q = q.order_by(Paper.published_date.desc(), Paper.id.desc()).offset(offset).limit(size)
    result = await db.execute(q)
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": p.id,
                "source": p.source,
                "title": p.title,
                "authors": p.authors,
                "abstract": p.abstract,
                "url": p.url,
                "pdf_url": p.pdf_url,
                "published_date": p.published_date.isoformat() if p.published_date else None,
                "categories": p.categories,
                "crawled_at": p.crawled_at.isoformat() if p.crawled_at else None,
            }
            for p in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.post("/crawl")
async def trigger_crawl():
    """Manually trigger all paper crawlers concurrently."""
    import asyncio
    import logging
    from crawlers import arxiv, neurips, iclr, icml, acl, cvpr

    logger = logging.getLogger(__name__)

    crawlers = {
        "arxiv": arxiv.crawl,
        "neurips": neurips.crawl,
        "iclr": iclr.crawl,
        "icml": icml.crawl,
        "acl": acl.crawl,
        "cvpr": cvpr.crawl,
    }

    async def _run(name, fn, results):
        try:
            results[name] = await fn()
        except Exception as e:
            logger.error(f"Crawler {name} failed: {e}")
            results[name] = {"error": str(e)}

    results = {}
    tasks = [_run(name, fn, results) for name, fn in crawlers.items()]
    await asyncio.gather(*tasks, return_exceptions=True)

    total_fetched = sum(r.get("fetched", 0) for r in results.values() if isinstance(r, dict))
    total_saved = sum(r.get("saved", 0) for r in results.values() if isinstance(r, dict))
    return {
        "status": "completed",
        "total_fetched": total_fetched,
        "total_saved": total_saved,
        "details": results,
    }


@router.get("/stats")
async def paper_stats(db: AsyncSession = Depends(get_db)):
    # Count by source
    source_result = await db.execute(
        select(Paper.source, func.count(Paper.id)).group_by(Paper.source)
    )
    by_source = {row[0]: row[1] for row in source_result}

    # Total count
    total = (await db.execute(select(func.count(Paper.id)))).scalar() or 0

    return {
        "total": total,
        "by_source": by_source,
    }


@router.get("/{paper_id}")
async def get_paper(paper_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if paper is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="论文不存在")

    return {
        "id": paper.id,
        "source": paper.source,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "url": paper.url,
        "pdf_url": paper.pdf_url,
        "published_date": paper.published_date.isoformat() if paper.published_date else None,
        "categories": paper.categories,
        "crawled_at": paper.crawled_at.isoformat() if paper.crawled_at else None,
    }
