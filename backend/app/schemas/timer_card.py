"""
Timer Card Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal
from app.models.models import ShiftType


class TimerCardBase(BaseModel):
    """Base timer card schema"""
    employee_id: int
    factory_id: str
    work_date: date
    clock_in: Optional[time] = None
    clock_out: Optional[time] = None
    break_minutes: int = 0
    shift_type: Optional[ShiftType] = None
    notes: Optional[str] = None


class TimerCardCreate(TimerCardBase):
    """Create timer card"""
    pass


class TimerCardUpdate(BaseModel):
    """Update timer card"""
    clock_in: Optional[time] = None
    clock_out: Optional[time] = None
    break_minutes: Optional[int] = None
    shift_type: Optional[ShiftType] = None
    notes: Optional[str] = None
    is_approved: Optional[bool] = None


class TimerCardResponse(TimerCardBase):
    """Timer card response"""
    id: int
    regular_hours: Decimal
    overtime_hours: Decimal
    night_hours: Decimal
    holiday_hours: Decimal
    is_approved: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class TimerCardBulkCreate(BaseModel):
    """Bulk create timer cards"""
    records: list[TimerCardCreate]


class TimerCardProcessResult(BaseModel):
    """Timer card processing result"""
    total_records: int
    successful: int
    failed: int
    errors: list[str]
    created_ids: list[int]


class TimerCardOCRData(BaseModel):
    """OCR data from timer card"""
    employee_name: Optional[str] = None
    work_date: Optional[str] = None
    clock_in: Optional[str] = None
    clock_out: Optional[str] = None
    total_hours: Optional[str] = None
    notes: Optional[str] = None


class TimerCardUploadResponse(BaseModel):
    """Timer card upload response"""
    file_name: str
    records_found: int
    ocr_data: list[TimerCardOCRData]
    message: str


class TimerCardApprove(BaseModel):
    """Approve timer cards"""
    timer_card_ids: list[int]
    notes: Optional[str] = None
