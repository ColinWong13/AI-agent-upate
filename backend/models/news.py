from sqlalchemy import Column, Integer, String, Text, DateTime, func
from .base import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False, default="")
    url = Column(String(500), unique=True, nullable=False)
    published_date = Column(DateTime, nullable=False, index=True)
    category = Column(String(50), nullable=True, index=True)
    crawled_at = Column(DateTime, server_default=func.now())
