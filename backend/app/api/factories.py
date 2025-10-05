"""
Factories API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.models import Factory, User
from app.schemas.factory import FactoryCreate, FactoryUpdate, FactoryResponse
from app.services.auth_service import auth_service

router = APIRouter()


@router.post("/", response_model=FactoryResponse, status_code=status.HTTP_201_CREATED)
async def create_factory(
    factory: FactoryCreate,
    current_user: User = Depends(auth_service.require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Create new factory"""
    existing = db.query(Factory).filter(Factory.factory_id == factory.factory_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Factory ID already exists")
    
    new_factory = Factory(**factory.model_dump())
    db.add(new_factory)
    db.commit()
    db.refresh(new_factory)
    return new_factory


@router.get("/", response_model=list[FactoryResponse])
async def list_factories(
    is_active: bool = True,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all factories"""
    query = db.query(Factory)
    if is_active is not None:
        query = query.filter(Factory.is_active == is_active)
    return query.all()


@router.get("/{factory_id}", response_model=FactoryResponse)
async def get_factory(
    factory_id: str,
    current_user: User = Depends(auth_service.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get factory by ID"""
    factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    return factory


@router.put("/{factory_id}", response_model=FactoryResponse)
async def update_factory(
    factory_id: str,
    factory_update: FactoryUpdate,
    current_user: User = Depends(auth_service.require_role("admin")),
    db: Session = Depends(get_db)
):
    """Update factory"""
    factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    
    for field, value in factory_update.model_dump(exclude_unset=True).items():
        setattr(factory, field, value)
    
    db.commit()
    db.refresh(factory)
    return factory


@router.delete("/{factory_id}")
async def delete_factory(
    factory_id: str,
    current_user: User = Depends(auth_service.require_role("super_admin")),
    db: Session = Depends(get_db)
):
    """Delete factory"""
    factory = db.query(Factory).filter(Factory.factory_id == factory_id).first()
    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")
    
    db.delete(factory)
    db.commit()
    return {"message": "Factory deleted successfully"}
