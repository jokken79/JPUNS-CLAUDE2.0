"""
Employees API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
from datetime import datetime
import io

from app.core.database import get_db
from app.models.models import Employee, Candidate, User, CandidateStatus, Factory, Document
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
    candidate = db.query(Candidate).filter(Candidate.rirekisho_id == employee.rirekisho_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if candidate.status != CandidateStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Candidate not approved")

    # Generate Hakenmoto ID
    last_employee = db.query(Employee).order_by(Employee.hakenmoto_id.desc()).first()
    hakenmoto_id = (last_employee.hakenmoto_id + 1) if last_employee else 1

    # Create employee with data from candidate
    employee_data = employee.model_dump()

    # Copy photo from candidate
    if candidate.photo_url:
        employee_data['photo_url'] = candidate.photo_url

    new_employee = Employee(
        hakenmoto_id=hakenmoto_id,
        **employee_data
    )

    # Mark candidate as hired
    candidate.status = CandidateStatus.HIRED

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    # Copy documents from candidate to employee
    candidate_documents = db.query(Document).filter(Document.candidate_id == candidate.id).all()
    for doc in candidate_documents:
        # Create a copy of the document for the employee
        employee_document = Document(
            employee_id=new_employee.id,
            candidate_id=None,  # Keep reference to original candidate if needed, or set to None
            document_type=doc.document_type,
            file_name=doc.file_name,
            file_path=doc.file_path,
            file_size=doc.file_size,
            mime_type=doc.mime_type,
            ocr_data=doc.ocr_data,
            uploaded_by=current_user.id
        )
        db.add(employee_document)

    db.commit()

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
        # Try to convert search to int for hakenmoto_id search
        try:
            search_int = int(search)
            query = query.filter(
                (Employee.full_name_kanji.ilike(f"%{search}%")) |
                (Employee.full_name_kana.ilike(f"%{search}%")) |
                (Employee.hakenmoto_id == search_int)
            )
        except ValueError:
            # If not a number, only search by name
            query = query.filter(
                (Employee.full_name_kanji.ilike(f"%{search}%")) |
                (Employee.full_name_kana.ilike(f"%{search}%"))
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


@router.post("/import-excel")
async def import_employees_from_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Import employees from Excel file"""

    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be Excel format (.xlsx or .xls)")

    try:
        # Read Excel file
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))

        # Track results
        created_count = 0
        updated_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Get or create hakenmoto_id
                hakenmoto_id = row.get('社員№')

                if pd.isna(hakenmoto_id) or not hakenmoto_id:
                    # Generate new hakenmoto_id
                    last_employee = db.query(Employee).order_by(Employee.hakenmoto_id.desc()).first()
                    hakenmoto_id = (last_employee.hakenmoto_id + 1) if last_employee else 1

                # Check if employee exists
                existing = db.query(Employee).filter(Employee.hakenmoto_id == int(hakenmoto_id)).first()

                # Parse dates
                def parse_date(value):
                    if pd.isna(value) or value == '' or value == '-':
                        return None
                    if isinstance(value, datetime):
                        return value.date()
                    try:
                        return pd.to_datetime(value).date()
                    except:
                        return None

                # Parse integer
                def parse_int(value):
                    if pd.isna(value) or value == '' or value == '-':
                        return None
                    try:
                        return int(value)
                    except:
                        return None

                # Parse boolean
                def parse_bool(value):
                    if pd.isna(value) or value == '':
                        return None
                    if isinstance(value, bool):
                        return value
                    if str(value).lower() in ['true', 'yes', '1', 'はい', '○']:
                        return True
                    return False

                # Determine if active based on 現在 column
                is_active = True
                status_value = row.get('現在')
                if not pd.isna(status_value):
                    if str(status_value) in ['退社', '退職', '×']:
                        is_active = False

                # Get factory name from 派遣先 column
                factory_name = row.get('派遣先')
                factory_id = None

                # Try to find factory by name
                if factory_name and not pd.isna(factory_name):
                    factory = db.query(Factory).filter(Factory.name.ilike(f'%{factory_name}%')).first()
                    if factory:
                        factory_id = factory.factory_id

                # Create employee data with ALL columns
                employee_data = {
                    'hakenmoto_id': int(hakenmoto_id),
                    'factory_id': factory_id,  # ID interno del sistema
                    'hakensaki_shain_id': row.get('派遣先ID'),  # ID que la fábrica da al empleado
                    'full_name_kanji': row.get('氏名'),
                    'full_name_kana': row.get('カナ'),
                    'gender': row.get('性別'),
                    'nationality': row.get('国籍'),
                    'date_of_birth': parse_date(row.get('生年月日')),
                    'jikyu': parse_int(row.get('時給')) or 0,
                    'hourly_rate_charged': parse_int(row.get('請求単価')),
                    'profit_difference': parse_int(row.get('差額利益')),
                    'standard_compensation': parse_int(row.get('標準報酬')),
                    'health_insurance': parse_int(row.get('健康保険')),
                    'nursing_insurance': parse_int(row.get('介護保険')),
                    'pension_insurance': parse_int(row.get('厚生年金')),
                    'zairyu_expire_date': parse_date(row.get('ビザ期限')),
                    'visa_type': row.get('ビザ種類'),
                    'postal_code': row.get('〒'),
                    'address': row.get('住所'),
                    'apartment_id': parse_int(row.get('ｱﾊﾟｰﾄ')),
                    'apartment_start_date': parse_date(row.get('入居')),
                    'hire_date': parse_date(row.get('入社日')),
                    'termination_date': parse_date(row.get('退社日')),
                    'apartment_move_out_date': parse_date(row.get('退去')),
                    'social_insurance_date': parse_date(row.get('社保加入')),
                    'entry_request_date': parse_date(row.get('入社依頼')),
                    'notes': row.get('備考'),
                    'license_type': row.get('免許種類'),
                    'license_expire_date': parse_date(row.get('免許期限')),
                    'commute_method': row.get('通勤方法'),
                    'optional_insurance_expire': parse_date(row.get('任意保険期限')),
                    'japanese_level': row.get('日本語検定'),
                    'career_up_5years': parse_bool(row.get('キャリアアップ5年目')),
                    'is_active': is_active
                }

                if existing:
                    # Update existing employee
                    for key, value in employee_data.items():
                        if value is not None and key != 'hakenmoto_id':
                            setattr(existing, key, value)
                    updated_count += 1
                else:
                    # Create new employee
                    new_employee = Employee(**employee_data)
                    db.add(new_employee)
                    created_count += 1

            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                continue

        db.commit()

        return {
            "success": True,
            "created": created_count,
            "updated": updated_count,
            "errors": errors,
            "total_processed": created_count + updated_count
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing Excel file: {str(e)}")
