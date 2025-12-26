from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models import StatusEnum


class LabRequestCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    student_name: str = Field(..., min_length=1, max_length=255)
    deadline: datetime
    description: Optional[str] = None


class LabRequestUpdate(BaseModel):
    title: Optional[str] = None
    student_name: Optional[str] = None
    deadline: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None


class LabRequestResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    student_name: str
    deadline: datetime
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
