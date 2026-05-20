from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, func
from .base import Base


class WeeklyDigest(Base):
    __tablename__ = "weekly_digests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    digest_type = Column(String(10), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    week_start = Column(Date, nullable=False)
    week_end = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    is_latest = Column(Boolean, nullable=False, default=True, index=True)
