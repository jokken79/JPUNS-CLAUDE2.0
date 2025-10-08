"""
Authentication and Security Service for UNS-ClaudeJP 1.0
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """Authenticate user"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return False
        if not AuthService.verify_password(password, str(user.password_hash)):
            return False
        
        return user
    
    @staticmethod
    async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """Get current user from token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        
        return user
    
    @staticmethod
    async def get_current_active_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
    ):
        """Get current active user"""
        current_user = await AuthService.get_current_user(token, db)
        if not bool(current_user.is_active):
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user
    
    @staticmethod
    def require_role(required_role: str):
        """Dependency to check user role"""
        async def role_checker(current_user: User = Depends(AuthService.get_current_active_user)):
            allowed_roles = {
                'super_admin': ['SUPER_ADMIN'],
                'admin': ['SUPER_ADMIN', 'ADMIN'],
                'coordinator': ['SUPER_ADMIN', 'ADMIN', 'COORDINATOR'],
                'employee': ['SUPER_ADMIN', 'ADMIN', 'COORDINATOR', 'EMPLOYEE']
            }

            if current_user.role.name not in allowed_roles.get(required_role, []):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return current_user

        return role_checker


# Global instance
auth_service = AuthService()
