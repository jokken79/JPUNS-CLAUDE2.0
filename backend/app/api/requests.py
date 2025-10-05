"""
Requests API Endpoints (Yukyu, Ikkikokoku, Taisha, etc.)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date

from app.core.database import get_db
from app.models.models import Request, Employee, User, RequestType, RequestStatus
from app.schemas.request import RequestCreate, RequestUpdate, RequestResponse, RequestReview
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/", response_model=RequestResponse, status_code=201)
async def create_request(
    request_data: RequestCreate,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new request (yukyu, ikkikokoku, etc.)"""
    # Verify employee exists
    employee = db.query(Employee).filter(Employee.id == request_data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Check if employee can make request (only their own unless admin)
    if current_user.role.value == "employee":
        # Employee can only request for themselves
        # You'd need to link user to employee here
        pass
    
    # Calculate total days
    if not request_data.total_days:
        delta = request_data.end_date - request_data.start_date
        request_data.total_days = delta.days + 1
    
    # Check yukyu balance for yukyu/hankyu requests
    if request_data.request_type in [RequestType.YUKYU, RequestType.HANKYU]:
        if employee.yukyu_remaining < float(request_data.total_days):
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient yukyu balance. Available: {employee.yukyu_remaining}"
            )
    
    new_request = Request(**request_data.model_dump())
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request


@router.get("/", response_model=list[RequestResponse])
async def list_requests(
    employee_id: int = None,
    status: RequestStatus = None,
    request_type: RequestType = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List requests"""
    query = db.query(Request)
    
    if employee_id:
        query = query.filter(Request.employee_id == employee_id)
    if status:
        query = query.filter(Request.status == status)
    if request_type:
        query = query.filter(Request.request_type == request_type)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get request by ID"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.put("/{request_id}", response_model=RequestResponse)
async def update_request(
    request_id: int,
    request_update: RequestUpdate,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update request (before approval)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only update pending requests")
    
    for field, value in request_update.model_dump(exclude_unset=True).items():
        setattr(request, field, value)
    
    db.commit()
    db.refresh(request)
    return request


@router.post("/{request_id}/review", response_model=RequestResponse)
async def review_request(
    request_id: int,
    review_data: RequestReview,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Approve or reject request"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Request already reviewed")
    
    request.status = review_data.status
    request.reviewed_by = current_user.id
    request.reviewed_at = func.now()
    request.review_notes = review_data.review_notes
    
    # Update yukyu balance if approved
    if review_data.status == RequestStatus.APPROVED:
        if request.request_type in [RequestType.YUKYU, RequestType.HANKYU]:
            employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
            employee.yukyu_used += float(request.total_days)
            employee.yukyu_remaining -= float(request.total_days)
    
    db.commit()
    db.refresh(request)
    return request


@router.delete("/{request_id}")
async def delete_request(
    request_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete request (only pending requests)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status != RequestStatus.PENDING:
        raise HTTPException(status_code=400, detail="Can only delete pending requests")
    
    db.delete(request)
    db.commit()
    return {"message": "Request deleted"}
