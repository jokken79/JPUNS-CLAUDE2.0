"""
Candidate Schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from app.models.models import CandidateStatus


class CandidateBase(BaseModel):
    """Base candidate schema"""
    full_name_kanji: Optional[str] = None
    full_name_kana: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class CandidateCreate(CandidateBase):
    """Create candidate"""
    pass


class CandidateUpdate(CandidateBase):
    """Update candidate"""
    status: Optional[CandidateStatus] = None


class CandidateResponse(CandidateBase):
    """Candidate response"""
    id: int
    uns_id: str
    photo_url: Optional[str]
    status: CandidateStatus
    created_at: datetime
    updated_at: Optional[datetime]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class OCRData(BaseModel):
    """OCR extracted data"""
    full_name_kanji: Optional[str] = None
    full_name_kana: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    raw_text: Optional[str] = None


class DocumentUpload(BaseModel):
    """Document upload response"""
    document_id: int
    file_name: str
    file_path: str
    ocr_data: Optional[OCRData]
    message: str


class CandidateApprove(BaseModel):
    """Approve candidate"""
    notes: Optional[str] = None


class CandidateReject(BaseModel):
    """Reject candidate"""
    reason: str
