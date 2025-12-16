from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class LabRequestBase(BaseModel):
    """Базовая схема заявки"""
    title: str = Field(..., min_length=1, max_length=255, description="Название лабораторной работы")
    description: Optional[str] = Field(None, max_length=1000, description="Описание заявки")
    student_name: str = Field(..., min_length=1, max_length=255, description="ФИО студента")
    deadline: datetime = Field(..., description="Срок выполнения")

class LabRequestCreate(LabRequestBase):
    """Схема для создания заявки"""
    pass

class LabRequestUpdate(BaseModel):
    """Схема для обновления заявки"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    student_name: Optional[str] = Field(None, min_length=1, max_length=255)
    deadline: Optional[datetime] = None
    status: Optional[str] = None

class LabRequestReschedule(BaseModel):
    """Схема для переноса заявки"""
    new_deadline: datetime = Field(..., description="Новый срок выполнения")

class LabRequestResponse(LabRequestBase):
    """Схема ответа с полной информацией"""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
