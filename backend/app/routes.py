from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import LabRequest, StatusEnum
from app.schemas import (
    LabRequestCreate,
    LabRequestResponse,
    LabRequestUpdate
)
from datetime import datetime, timezone
from typing import List

router = APIRouter(prefix="/api/requests", tags=["requests"])


@router.get("", response_model=List[LabRequestResponse])
async def get_all_requests(
    db: AsyncSession = Depends(get_db),
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100
):
    """Получить все заявки"""
    query = select(LabRequest).offset(skip).limit(limit)

    if status_filter:
        try:
            status_enum = StatusEnum(status_filter)
            query = query.where(LabRequest.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )

    query = query.order_by(LabRequest.deadline)
    result = await db.execute(query)
    requests = result.scalars().all()
    return requests


@router.post("", response_model=LabRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: LabRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую заявку"""
    now_utc = datetime.now(timezone.utc)

    if request_data.deadline < now_utc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline cannot be in the past"
        )

    db_request = LabRequest(
        title=request_data.title,
        description=request_data.description,
        student_name=request_data.student_name,
        deadline=request_data.deadline,
        status=StatusEnum.active
    )

    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)

    return db_request


@router.get("/{request_id}", response_model=LabRequestResponse)
async def get_request(request_id: int, db: AsyncSession = Depends(get_db)):
    """Получить заявку по ID"""
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )

    return request


@router.put("/{request_id}", response_model=LabRequestResponse)
async def update_request(
    request_id: int,
    request_data: LabRequestUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить заявку"""
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )

    # Обновляем только переданные поля
    update_data = request_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)

    await db.commit()
    await db.refresh(request)

    return request


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(request_id: int, db: AsyncSession = Depends(get_db)):
    """Удалить заявку"""
    result = await db.execute(
        select(LabRequest).where(LabRequest.id == request_id)
    )
    request = result.scalar_one_or_none()

    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Request {request_id} not found"
        )

    await db.delete(request)
    await db.commit()
