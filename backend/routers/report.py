from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.report import ReportSection

router = APIRouter(prefix="/api/report", tags=["report"])


@router.get("/sections")
async def list_sections(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReportSection).order_by(ReportSection.sort_order)
    )
    sections = result.scalars().all()
    return [
        {
            "id": s.id,
            "section_key": s.section_key,
            "title": s.title,
            "sort_order": s.sort_order,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in sections
    ]


@router.get("/sections/{section_key}")
async def get_section(section_key: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReportSection).where(ReportSection.section_key == section_key)
    )
    section = result.scalar_one_or_none()
    if section is None:
        raise HTTPException(status_code=404, detail="章节不存在")
    return {
        "id": section.id,
        "section_key": section.section_key,
        "title": section.title,
        "content_json": section.content_json,
        "sort_order": section.sort_order,
        "updated_at": section.updated_at.isoformat() if section.updated_at else None,
    }
