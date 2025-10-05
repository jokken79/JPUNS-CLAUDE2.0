"""
Factory Schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class FactoryBase(BaseModel):
    """Base factory schema"""
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None


class FactoryCreate(FactoryBase):
    """Create factory"""
    factory_id: str
    config: Optional[Dict[str, Any]] = None


class FactoryUpdate(BaseModel):
    """Update factory"""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    contact_person: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FactoryResponse(FactoryBase):
    """Factory response"""
    id: int
    factory_id: str
    config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class FactoryConfig(BaseModel):
    """Factory configuration"""
    factory_id: str
    shifts: list[Dict[str, Any]]
    overtime_rules: Dict[str, Any]
    bonuses: Dict[str, Any]
    holidays: Dict[str, Any]
    attendance_rules: Dict[str, Any]


class FactoryStats(BaseModel):
    """Factory statistics"""
    factory_id: str
    factory_name: str
    total_employees: int
    active_employees: int
    total_hours_current_month: float
    total_salary_current_month: int
    total_revenue_current_month: int
    profit_current_month: int
