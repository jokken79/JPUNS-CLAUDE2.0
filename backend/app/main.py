"""
UNS-ClaudeJP 2.0 - Main FastAPI Application
Sistema Integral de Gestión de Personal Temporal para UNS-Kikaku
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db
from app.core.middleware import LoggingMiddleware, ExceptionHandlerMiddleware

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="Sistema Integral de Gestión de Personal Temporal",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Exception Handler Middleware (debe ir primero)
app.add_middleware(ExceptionHandlerMiddleware)

# Logging Middleware
app.add_middleware(LoggingMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory if not exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

# Serve uploaded files
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.on_event("startup")
async def startup_event():
    """Startup event"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

    # Initialize admin user
    try:
        from init_db import init_database
        await init_database()
    except Exception as e:
        logger.error(f"Error initializing admin user: {e}")

    # Warm-up bcrypt to avoid timeout on first login
    try:
        from app.services.auth_service import pwd_context
        # Do a dummy hash with short password to initialize bcrypt (prevents 60s delay on first login)
        # Note: Using short password to avoid bcrypt's 72-byte limit
        _ = pwd_context.hash("warmup")
        logger.info("✅ Bcrypt warmed up successfully")
    except Exception as e:
        logger.error(f"Error warming up bcrypt: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    logger.info(f"Shutting down {settings.APP_NAME}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": settings.COMPANY_NAME,
        "website": settings.COMPANY_WEBSITE,
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Import and include routers
from app.api import (
    auth, candidates, employees, factories, timer_cards, salary, requests, dashboard,
    ocr, ocr_optimized, import_export, reports, notifications
)

# Import fixed OCR router
from app.api import ocr_fixed

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(factories.router, prefix="/api/factories", tags=["Factories"])
app.include_router(timer_cards.router, prefix="/api/timer-cards", tags=["Timer Cards"])
app.include_router(salary.router, prefix="/api/salary", tags=["Salary"])
app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# New routers (v2.0)
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(ocr_fixed.router, prefix="/api/ocr-fixed", tags=["OCR Fixed"])  # OCR con timeouts y manejo de errores
app.include_router(ocr_optimized.router, prefix="/api/ocr-optimized", tags=["OCR Optimized"])  # Sistema híbrido optimizado
app.include_router(import_export.router, prefix="/api/import", tags=["Import/Export"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
