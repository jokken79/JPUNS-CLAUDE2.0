"""
Candidates API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import shutil
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Candidate, Document, User, CandidateStatus, DocumentType
from app.schemas.candidate import (
    CandidateCreate, CandidateUpdate, CandidateResponse,
    CandidateApprove, CandidateReject, DocumentUpload, OCRData
)
from app.schemas.base import PaginatedResponse
from app.services.auth_service import auth_service
from app.services.ocr_service import ocr_service

router = APIRouter()


def generate_uns_id(db: Session) -> str:
    """Generate next UNS ID"""
    # Get last candidate
    last_candidate = db.query(Candidate).order_by(Candidate.id.desc()).first()
    
    if last_candidate and last_candidate.uns_id:
        # Extract number from UNS-XXXX
        last_num = int(last_candidate.uns_id.split('-')[1])
        next_num = last_num + 1
    else:
        next_num = settings.RIREKISHO_ID_START
    
    return f"{settings.RIREKISHO_ID_PREFIX}{next_num}"


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Create new candidate
    """
    # Generate UNS ID
    uns_id = generate_uns_id(db)
    
    new_candidate = Candidate(
        uns_id=uns_id,
        **candidate.model_dump()
    )
    
    db.add(new_candidate)
    db.commit()
    db.refresh(new_candidate)
    
    return new_candidate


@router.get("/", response_model=PaginatedResponse)
async def list_candidates(
    page: int = 1,
    page_size: int = 20,
    status_filter: Optional[CandidateStatus] = None,
    search: Optional[str] = None,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all candidates with pagination
    """
    query = db.query(Candidate)
    
    # Apply filters
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    
    if search:
        query = query.filter(
            (Candidate.full_name_kanji.ilike(f"%{search}%")) |
            (Candidate.full_name_kana.ilike(f"%{search}%")) |
            (Candidate.uns_id.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    candidates = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "items": candidates,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get candidate by ID
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Update candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Update fields
    for field, value in candidate_update.model_dump(exclude_unset=True).items():
        setattr(candidate, field, value)
    
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.delete("/{candidate_id}")
async def delete_candidate(
    candidate_id: int,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Delete candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    db.delete(candidate)
    db.commit()
    
    return {"message": "Candidate deleted successfully"}


@router.post("/{candidate_id}/upload", response_model=DocumentUpload)
async def upload_document(
    candidate_id: int,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Upload document for candidate with OCR processing
    """
    # Verify candidate exists
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower().replace('.', '')
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory if not exists
    upload_dir = os.path.join(settings.UPLOAD_DIR, "candidates", str(candidate_id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process with OCR
    ocr_data = None
    if document_type in ["rirekisho", "zairyu_card"]:
        try:
            ocr_result = ocr_service.process_document(file_path, document_type)
            ocr_data = OCRData(**ocr_result)
            
            # Auto-fill candidate data if rirekisho
            if document_type == "rirekisho" and ocr_data:
                if ocr_data.full_name_kanji:
                    candidate.full_name_kanji = ocr_data.full_name_kanji
                if ocr_data.full_name_kana:
                    candidate.full_name_kana = ocr_data.full_name_kana
                if ocr_data.address:
                    candidate.address = ocr_data.address
                if ocr_data.phone:
                    candidate.phone = ocr_data.phone
                if ocr_data.email:
                    candidate.email = ocr_data.email
                if ocr_data.date_of_birth:
                    candidate.date_of_birth = ocr_data.date_of_birth
                if ocr_data.gender:
                    candidate.gender = ocr_data.gender
                
                db.commit()
        except Exception as e:
            print(f"OCR processing error: {e}")
            ocr_data = OCRData(raw_text=f"Error processing: {str(e)}")
    
    # Save document record
    document = Document(
        candidate_id=candidate_id,
        document_type=DocumentType[document_type.upper()],
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        mime_type=file.content_type,
        ocr_data=ocr_data.model_dump() if ocr_data else None,
        uploaded_by=current_user.id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return DocumentUpload(
        document_id=document.id,
        file_name=file.filename,
        file_path=file_path,
        ocr_data=ocr_data,
        message="Document uploaded and processed successfully"
    )


@router.post("/{candidate_id}/approve", response_model=CandidateResponse)
async def approve_candidate(
    candidate_id: int,
    approve_data: CandidateApprove,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Approve candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    candidate.status = CandidateStatus.APPROVED
    candidate.approved_by = current_user.id
    candidate.approved_at = func.now()
    
    db.commit()
    db.refresh(candidate)
    
    return candidate


@router.post("/{candidate_id}/reject", response_model=CandidateResponse)
async def reject_candidate(
    candidate_id: int,
    reject_data: CandidateReject,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Reject candidate
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    
    candidate.status = CandidateStatus.REJECTED
    candidate.approved_by = current_user.id
    candidate.approved_at = func.now()
    
    db.commit()
    db.refresh(candidate)
    
    return candidate
