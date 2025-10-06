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
    rirekisho_id: str  # Changed from uns_id
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
    rirekisho_id: Optional[str]  # Changed from uns_id
    factory_id: Optional[str]
    factory_name: Optional[str] = None  # Nombre de la fábrica
    hakensaki_shain_id: Optional[str]
    hire_date: Optional[date]  # Puede ser NULL
    jikyu: int
    photo_url: Optional[str] = None  # Added photo
    position: Optional[str]
    contract_type: Optional[str]

    # Financial
    hourly_rate_charged: Optional[int]
    profit_difference: Optional[int]
    standard_compensation: Optional[int]
    health_insurance: Optional[int]
    nursing_insurance: Optional[int]
    pension_insurance: Optional[int]
    social_insurance_date: Optional[date]

    # Visa and documents
    visa_type: Optional[str]
    license_type: Optional[str]
    license_expire_date: Optional[date]
    commute_method: Optional[str]
    optional_insurance_expire: Optional[date]
    japanese_level: Optional[str]
    career_up_5years: Optional[bool]
    entry_request_date: Optional[date]
    photo_url: Optional[str]
    notes: Optional[str]
    postal_code: Optional[str]

    # Apartment
    apartment_id: Optional[int]
    apartment_start_date: Optional[date]
    apartment_move_out_date: Optional[date]
    apartment_rent: Optional[int]

    # Yukyu
    yukyu_total: int
    yukyu_used: int
    yukyu_remaining: int

    # Status
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
