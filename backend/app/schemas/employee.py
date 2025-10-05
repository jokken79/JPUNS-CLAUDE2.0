"""
Employee Schemas
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import date, datetime


class EmployeeBase(BaseModel):
    """Base employee schema"""
    full_name_kanji: str
    full_name_kana: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    zairyu_card_number: Optional[str] = None
    zairyu_expire_date: Optional[date] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    """Create employee from candidate"""
    uns_id: str
    factory_id: str
    hakensaki_shain_id: Optional[str] = None
    hire_date: date
    jikyu: int
    position: Optional[str] = None
    contract_type: Optional[str] = None
    apartment_id: Optional[int] = None
    apartment_start_date: Optional[date] = None
    apartment_rent: Optional[int] = None


class EmployeeUpdate(BaseModel):
    """Update employee"""
    full_name_kanji: Optional[str] = None
    full_name_kana: Optional[str] = None
    factory_id: Optional[str] = None
    hakensaki_shain_id: Optional[str] = None
    jikyu: Optional[int] = None
    position: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    apartment_id: Optional[int] = None
    apartment_rent: Optional[int] = None
    zairyu_expire_date: Optional[date] = None


class EmployeeResponse(EmployeeBase):
    """Employee response"""
    id: int
    hakenmoto_id: int
    uns_id: str
    factory_id: str
    hakensaki_shain_id: Optional[str]
    hire_date: date
    jikyu: int
    position: Optional[str]
    contract_type: Optional[str]
    apartment_id: Optional[int]
    apartment_start_date: Optional[date]
    apartment_rent: Optional[int]
    yukyu_total: int
    yukyu_used: int
    yukyu_remaining: int
    is_active: bool
    termination_date: Optional[date]
    termination_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class EmployeeTerminate(BaseModel):
    """Terminate employee"""
    termination_date: date
    termination_reason: str


class YukyuUpdate(BaseModel):
    """Update yukyu balance"""
    yukyu_total: int
    notes: Optional[str] = None
