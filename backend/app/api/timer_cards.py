"""
Timer Cards API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import time as datetime_time
import os
import shutil

from app.core.database import get_db
from app.core.config import settings
from app.models.models import TimerCard, Employee, User
from app.schemas.timer_card import (
    TimerCardCreate, TimerCardUpdate, TimerCardResponse,
    TimerCardBulkCreate, TimerCardProcessResult,
    TimerCardUploadResponse, TimerCardApprove, TimerCardOCRData
)
from app.services.auth_service import auth_service
from app.services.ocr_service import ocr_service

router = APIRouter()


def calculate_hours(clock_in: datetime_time, clock_out: datetime_time, break_minutes: int = 0):
    """Calculate work hours"""
    from datetime import datetime, timedelta
    
    # Convert to datetime for calculation
    today = datetime.today().date()
    start = datetime.combine(today, clock_in)
    end = datetime.combine(today, clock_out)
    
    # Handle overnight shifts
    if end < start:
        end += timedelta(days=1)
    
    # Calculate total hours
    total_minutes = (end - start).total_seconds() / 60
    work_minutes = total_minutes - break_minutes
    work_hours = work_minutes / 60
    
    # Calculate regular and overtime
    regular_hours = min(work_hours, 8.0)
    overtime_hours = max(work_hours - 8.0, 0)
    
    # Calculate night hours (22:00-05:00)
    night_hours = 0.0
    # Simplified calculation - can be enhanced
    
    return {
        "regular_hours": round(regular_hours, 2),
        "overtime_hours": round(overtime_hours, 2),
        "night_hours": round(night_hours, 2),
        "holiday_hours": 0.0  # Needs holiday calendar
    }


@router.post("/", response_model=TimerCardResponse, status_code=201)
async def create_timer_card(
    timer_card: TimerCardCreate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create single timer card"""
    # Calculate hours
    hours = calculate_hours(timer_card.clock_in, timer_card.clock_out, timer_card.break_minutes)
    
    new_card = TimerCard(
        **timer_card.model_dump(),
        **hours
    )
    
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card


@router.post("/bulk", response_model=TimerCardProcessResult)
async def create_timer_cards_bulk(
    bulk_data: TimerCardBulkCreate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create multiple timer cards"""
    created_ids = []
    errors = []
    
    for record in bulk_data.records:
        try:
            hours = calculate_hours(record.clock_in, record.clock_out, record.break_minutes)
            new_card = TimerCard(**record.model_dump(), **hours)
            db.add(new_card)
            db.flush()
            created_ids.append(new_card.id)
        except Exception as e:
            errors.append(f"Error creating record for employee {record.employee_id}: {str(e)}")
    
    db.commit()
    
    return TimerCardProcessResult(
        total_records=len(bulk_data.records),
        successful=len(created_ids),
        failed=len(errors),
        errors=errors,
        created_ids=created_ids
    )


@router.post("/upload", response_model=TimerCardUploadResponse)
async def upload_timer_card_file(
    file: UploadFile = File(...),
    factory_id: str = None,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Upload timer card file and process with OCR"""
    # Save file
    upload_dir = os.path.join(settings.UPLOAD_DIR, "timer_cards")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process with OCR
    try:
        ocr_result = ocr_service.process_document(file_path, "timer_card")
        records = ocr_result.get("records", [])
        
        ocr_data = [TimerCardOCRData(**record) for record in records]
        
        return TimerCardUploadResponse(
            file_name=file.filename,
            records_found=len(records),
            ocr_data=ocr_data,
            message="File processed successfully. Please review and confirm data."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@router.get("/", response_model=list[TimerCardResponse])
async def list_timer_cards(
    employee_id: int = None,
    factory_id: str = None,
    is_approved: bool = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List timer cards"""
    query = db.query(TimerCard)
    
    if employee_id:
        query = query.filter(TimerCard.employee_id == employee_id)
    if factory_id:
        query = query.filter(TimerCard.factory_id == factory_id)
    if is_approved is not None:
        query = query.filter(TimerCard.is_approved == is_approved)
    
    return query.offset(skip).limit(limit).all()


@router.put("/{timer_card_id}", response_model=TimerCardResponse)
async def update_timer_card(
    timer_card_id: int,
    timer_card_update: TimerCardUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update timer card"""
    timer_card = db.query(TimerCard).filter(TimerCard.id == timer_card_id).first()
    if not timer_card:
        raise HTTPException(status_code=404, detail="Timer card not found")
    
    # Update fields
    for field, value in timer_card_update.model_dump(exclude_unset=True).items():
        setattr(timer_card, field, value)
    
    # Recalculate hours if time changed
    if timer_card_update.clock_in or timer_card_update.clock_out:
        hours = calculate_hours(timer_card.clock_in, timer_card.clock_out, timer_card.break_minutes)
        for key, value in hours.items():
            setattr(timer_card, key, value)
    
    db.commit()
    db.refresh(timer_card)
    return timer_card


@router.post("/approve", response_model=dict)
async def approve_timer_cards(
    approve_data: TimerCardApprove,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve multiple timer cards"""
    cards = db.query(TimerCard).filter(TimerCard.id.in_(approve_data.timer_card_ids)).all()
    
    for card in cards:
        card.is_approved = True
    
    db.commit()
    
    return {"message": f"Approved {len(cards)} timer cards"}


@router.delete("/{timer_card_id}")
async def delete_timer_card(
    timer_card_id: int,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Delete timer card"""
    timer_card = db.query(TimerCard).filter(TimerCard.id == timer_card_id).first()
    if not timer_card:
        raise HTTPException(status_code=404, detail="Timer card not found")
    
    db.delete(timer_card)
    db.commit()
    return {"message": "Timer card deleted"}
