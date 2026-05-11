from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from database import get_db
from models.news import NewsItem

router = APIRouter(prefix="/api/news", tags=["news"])


class NewsCreate(BaseModel):
    source_name: str
    title: str
    summary: str = ""
    url: str
    category: str = ""


class NewsUpdate(BaseModel):
    source_name: str | None = None
    title: str | None = None
    summary: str | None = None
    url: str | None = None
    category: str | None = None


@router.get("")
async def list_news(
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    q = select(NewsItem)
    if category:
        q = q.where(NewsItem.category == category)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    offset = (page - 1) * size
    q = q.order_by(NewsItem.published_date.desc(), NewsItem.id.desc())
    q = q.offset(offset).limit(size)
    result = await db.execute(q)
    items = result.scalars().all()

    return {
        "items": [
            {
                "id": n.id,
                "source_name": n.source_name,
                "title": n.title,
                "summary": n.summary,
                "url": n.url,
                "published_date": n.published_date.isoformat() if n.published_date else None,
                "category": n.category,
            }
            for n in items
        ],
        "total": total,
        "page": page,
        "size": size,
    }


@router.get("/{news_id}")
async def get_news(news_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsItem).where(NewsItem.id == news_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="动态不存在")
    return {
        "id": item.id,
        "source_name": item.source_name,
        "title": item.title,
        "summary": item.summary,
        "url": item.url,
        "published_date": item.published_date.isoformat() if item.published_date else None,
        "category": item.category,
    }


@router.post("", status_code=201)
async def create_news(body: NewsCreate, db: AsyncSession = Depends(get_db)):
    from datetime import datetime
    item = NewsItem(
        source_name=body.source_name,
        title=body.title,
        summary=body.summary,
        url=body.url,
        category=body.category,
        published_date=datetime.utcnow(),
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": item.id, "title": item.title}


@router.put("/{news_id}")
async def update_news(news_id: int, body: NewsUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsItem).where(NewsItem.id == news_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="动态不存在")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    return {"id": item.id, "title": item.title}


@router.delete("/{news_id}")
async def delete_news(news_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(NewsItem).where(NewsItem.id == news_id))
    item = result.scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=404, detail="动态不存在")
    await db.delete(item)
    await db.commit()
    return {"deleted": news_id}
