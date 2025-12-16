from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models import LabRequest
from app.schemas import (
    LabRequestCreate,
    LabRequestResponse,
    LabRequestReschedule,
    LabRequestUpdate
)
from datetime import datetime
from typing import List

router = APIRouter(prefix="/api/requests", tags=["requests"])


@router.get("", response_model=List[LabRequestResponse])
async def get_all_requests(
        db: AsyncSession = Depends(get_db),
        status_filter: str = None,
        skip: int = 0,
        limit: int = 100
):
    """
    Получить все заявки с опциональной фильтрацией по статусу.

    - **status_filter**: фильтр по статусу (active, completed, cancelled)
    - **skip**: количество пропускаемых записей
    - **limit**: максимальное количество записей
    """
    query = select(LabRequest).offset(skip).limit(limit)

    if status_filter:
        query = query.where(LabRequest.status == status_filter)

    query = query.order_by(LabRequest.deadline)

    result = await db.execute(query)
    requests = result.scalars().all()
    return requests


@router.post("", response_model=LabRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
        request_data: LabRequestCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    Создать новую заявку на лабораторную работу.

    Требуемые поля:
    - **title**: название работы
    - **student_name**: ФИО студента
    - **deadline**: срок выполнения (ISO 8601 формат)
    - **description**: описание (опционально)
    """
    # Валидация даты
    if request_data.deadline < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline не может быть в прошлом"
        )

    db_request = LabRequest(
        title=request_data.title,
        description=request_data.description,
        student_name=request_data.student_name,
        deadline=request_data.deadline,
        status="active"
    )

    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    return db_request


@router.get("/{request_id}", response_model=LabRequestResponse)
async def get_request(
        request_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Получить заявку по ID"""
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
        request_id: int,
        db: AsyncSession = Depends(get_db)
):
    """Удалить заявку"""
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )

    await db.delete(request)
    await db.commit()

    return None


@router.put("/{request_id}/reschedule", response_model=LabRequestResponse)
async def reschedule_request(
        request_id: int,
        reschedule_data: LabRequestReschedule,
        db: AsyncSession = Depends(get_db)
):
    """
    Перенести дедлайн заявки на новую дату.

    - **new_deadline**: новый срок (ISO 8601 формат)
    """
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заявка с ID {request_id} не найдена"
        )

    if reschedule_data.new_deadline < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Новый deadline не может быть в прошлом"
        )

    request.deadline = reschedule_data.new_deadline
    await db.commit()
    await db.refresh(request)

    return request


@router.get("/stats/count", response_model=dict)
async def get_stats(db: AsyncSession = Depends(get_db)):
    """Получить статистику по заявкам"""
    result = await db.execute(
        select(func.count(LabRequest.id)).select_from(LabRequest)
    )
    total = result.scalar()

    return {
        "total_requests": total,
        "timestamp": datetime.utcnow().isoformat()
    }
