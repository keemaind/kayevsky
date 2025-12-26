from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from enum import Enum as PyEnum


class StatusEnum(str, PyEnum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class LabRequest(Base):
    __tablename__ = "lab_requests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    student_name = Column(String(255), nullable=False, index=True)
    deadline = Column(DateTime, nullable=False, index=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.active, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<LabRequest(id={self.id}, title={self.title}, status={self.status})>"
