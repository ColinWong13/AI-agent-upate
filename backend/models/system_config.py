from sqlalchemy import Column, String, Text, DateTime, func
from .base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False, default="")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
