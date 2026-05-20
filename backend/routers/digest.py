from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.weekly_digest import WeeklyDigest
from models.system_config import SystemConfig
from services.digest import generate_paper_digest, generate_news_digest

router = APIRouter(prefix="/api/digest", tags=["digest"])


@router.get("/{digest_type}")
async def list_digests(digest_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WeeklyDigest)
        .where(WeeklyDigest.digest_type == digest_type)
        .order_by(WeeklyDigest.created_at.desc())
    )
    digests = result.scalars().all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "content": d.content,
            "week_start": d.week_start.isoformat() if d.week_start else None,
            "week_end": d.week_end.isoformat() if d.week_end else None,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "is_latest": d.is_latest,
        }
        for d in digests
    ]


@router.get("/{digest_type}/latest")
async def get_latest_digest(digest_type: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WeeklyDigest)
        .where(WeeklyDigest.digest_type == digest_type, WeeklyDigest.is_latest == True)
    )
    digest = result.scalar_one_or_none()
    if digest is None:
        return None
    return {
        "id": digest.id,
        "title": digest.title,
        "content": digest.content,
        "week_start": digest.week_start.isoformat() if digest.week_start else None,
        "week_end": digest.week_end.isoformat() if digest.week_end else None,
        "created_at": digest.created_at.isoformat() if digest.created_at else None,
        "is_latest": digest.is_latest,
    }


@router.post("/{digest_type}/generate")
async def trigger_digest(digest_type: str):
    if digest_type == "paper":
        result = await generate_paper_digest()
    elif digest_type == "news":
        result = await generate_news_digest()
    else:
        return {"error": "invalid digest_type, use 'paper' or 'news'"}
    return result or {"status": "no data available for this period"}


@router.get("/config/llm")
async def get_llm_config_api(db: AsyncSession = Depends(get_db)):
    from services.llm import get_llm_config
    return await get_llm_config()


@router.put("/config/llm")
async def update_llm_config_api(body: dict, db: AsyncSession = Depends(get_db)):
    for key, value in body.items():
        db_key = f"llm_{key}"
        result = await db.execute(
            select(SystemConfig).where(SystemConfig.key == db_key)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.value = str(value)
        else:
            db.add(SystemConfig(key=db_key, value=str(value)))
    await db.commit()
    return {"status": "ok"}
