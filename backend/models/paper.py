from sqlalchemy import Column, Integer, String, Text, Date, DateTime, func, UniqueConstraint, JSON
from .base import Base


class Paper(Base):
    __tablename__ = "papers"
    __table_args__ = (
        UniqueConstraint("title", "published_date", name="uq_paper_title_date"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(20), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON, nullable=False, default=list)
    abstract = Column(Text, nullable=False, default="")
    url = Column(String(500), nullable=False)
    pdf_url = Column(String(500), nullable=True)
    published_date = Column(Date, nullable=False, index=True)
    categories = Column(JSON, nullable=False, default=list)
    crawled_at = Column(DateTime, server_default=func.now())
