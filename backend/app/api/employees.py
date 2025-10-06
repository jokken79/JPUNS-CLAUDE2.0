"""
Employees API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.models import Employee, Candidate, User, CandidateStatus, Factory
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeTerminate, YukyuUpdate
)
from app.schemas.base import PaginatedResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: EmployeeCreate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Create employee from approved candidate (入社届)"""
    # Verify candidate is approved
    candidate = db.query(Candidate).filter(Candidate.uns_id == employee.uns_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.status != CandidateStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Candidate not approved")
    
    # Generate Hakenmoto ID
    last_employee = db.query(Employee).order_by(Employee.hakenmoto_id.desc()).first()
    hakenmoto_id = (last_employee.hakenmoto_id + 1) if last_employee else 1
    
    new_employee = Employee(
        hakenmoto_id=hakenmoto_id,
        **employee.model_dump()
    )
    
    candidate.status = CandidateStatus.HIRED
    
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee


@router.get("/")
async def list_employees(
    page: int = 1,
    page_size: int = 20,
    factory_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all employees"""
    query = db.query(Employee)

    if factory_id:
        query = query.filter(Employee.factory_id == factory_id)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    if search:
        query = query.filter(
            (Employee.full_name_kanji.ilike(f"%{search}%")) |
            (Employee.hakenmoto_id == search)
        )

    total = query.count()
    employees = query.offset((page - 1) * page_size).limit(page_size).all()

    # Convert to response models and add factory name
    items = []
    for emp in employees:
        emp_dict = EmployeeResponse.model_validate(emp).model_dump()
        # Get factory name
        if emp.factory_id:
            factory = db.query(Factory).filter(Factory.factory_id == emp.factory_id).first()
            emp_dict['factory_name'] = factory.name if factory else None
        items.append(emp_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get employee by ID"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Convert to dict and add factory name
    emp_dict = EmployeeResponse.model_validate(employee).model_dump()
    if employee.factory_id:
        factory = db.query(Factory).filter(Factory.factory_id == employee.factory_id).first()
        emp_dict['factory_name'] = factory.name if factory else None

    return emp_dict


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    for field, value in employee_update.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    return employee


@router.post("/{employee_id}/terminate")
async def terminate_employee(
    employee_id: int,
    termination: EmployeeTerminate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Terminate employee"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.is_active = False
    employee.termination_date = termination.termination_date
    employee.termination_reason = termination.termination_reason
    
    db.commit()
    return {"message": "Employee terminated successfully"}


@router.put("/{employee_id}/yukyu", response_model=EmployeeResponse)
async def update_yukyu(
    employee_id: int,
    yukyu_update: YukyuUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update employee yukyu balance"""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    employee.yukyu_total = yukyu_update.yukyu_total
    employee.yukyu_remaining = yukyu_update.yukyu_total - employee.yukyu_used
    
    db.commit()
    db.refresh(employee)
    return employee
