"""
Configuration settings for UNS-ClaudeJP 1.0
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "UNS-ClaudeJP"
    APP_VERSION: str = "1.0"
    COMPANY_NAME: str = "UNS-Kikaku"
    COMPANY_WEBSITE: str = "https://uns-kikaku.com"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://uns_admin:password@db:5432/uns_claudejp")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: list = ["pdf", "jpg", "jpeg", "png"]
    UPLOAD_DIR: str = "/app/uploads"
    
    # OCR Settings
    OCR_ENABLED: bool = True
    TESSERACT_LANG: str = "jpn+eng"
    GOOGLE_CLOUD_VISION_ENABLED: bool = False
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Email Settings
    EMAIL_ENABLED: bool = True
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS: bool = True
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASSWORD: Optional[str] = os.getenv("EMAIL_PASSWORD")
    EMAIL_FROM: str = "noreply@uns-kikaku.com"
    EMAIL_FROM_NAME: str = "UNS-Kikaku System"
    
    # LINE Notify (Optional)
    LINE_NOTIFY_ENABLED: bool = False
    LINE_NOTIFY_TOKEN: Optional[str] = os.getenv("LINE_NOTIFY_TOKEN")
    
    # WhatsApp (Optional)
    WHATSAPP_ENABLED: bool = False
    WHATSAPP_TOKEN: Optional[str] = os.getenv("WHATSAPP_TOKEN")
    WHATSAPP_PHONE_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_ID")
    
    # ID Configuration
    RIREKISHO_ID_PREFIX: str = "UNS-"
    RIREKISHO_ID_START: int = 1000
    FACTORY_ID_PREFIX: str = "Factory-"
    FACTORY_ID_START: int = 1
    
    # Salary Calculation
    OVERTIME_RATE_25: float = 0.25
    OVERTIME_RATE_35: float = 0.35
    NIGHT_SHIFT_PREMIUM: float = 0.25
    HOLIDAY_WORK_PREMIUM: float = 0.35
    
    # Yukyu Settings
    YUKYU_INITIAL_DAYS: int = 10
    YUKYU_AFTER_MONTHS: int = 6
    YUKYU_MAX_DAYS: int = 20
    HANKYU_ENABLED: bool = True
    
    # Apartment Management
    APARTMENT_CALC_ENABLED: bool = True
    APARTMENT_PRORATE_BY_DAY: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/uns-claudejp.log"
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
