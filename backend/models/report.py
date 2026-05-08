from sqlalchemy import JSON, Column, Integer, String, DateTime, func
from .base import Base


class ReportSection(Base):
    __tablename__ = "report_sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_key = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    content_json = Column(JSON, nullable=False, default=dict)
    sort_order = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
