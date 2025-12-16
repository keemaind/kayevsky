from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.sql import expression
from datetime import datetime
from app.database import Base


class LabRequest(Base):
    """Модель заявки на лабораторную работу"""
    __tablename__ = "lab_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    student_name = Column(String(255), nullable=False)
    deadline = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(50), default="active", nullable=False)

    # Временные метки
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    class Config:
        from_attributes = True
