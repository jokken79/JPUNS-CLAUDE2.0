"""
Base Schemas for UNS-ClaudeJP 1.0
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


class ResponseBase(BaseModel):
    """Base response schema"""
    success: bool = True
    message: str = "Success"
    

class ErrorResponse(BaseModel):
    """Error response schema"""
    success: bool = False
    message: str
    error: Optional[str] = None
    

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    

class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
