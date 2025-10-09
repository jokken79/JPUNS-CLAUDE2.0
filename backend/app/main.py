"""FastAPI application entry point."""
from __future__ import annotations

from datetime import datetime
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import app_logger
from app.core.middleware import ExceptionHandlerMiddleware, LoggingMiddleware, SecurityMiddleware

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="""## UNS-ClaudeJP v2.0 - API de Gestión de Personal Temporal

### Características Principales
- **OCR Híbrido**: Gemini + Vision API + Tesseract con caché inteligente
- **Gestión de Personal**: Candidatos, empleados, fábricas y tarjetas de tiempo
- **Nóminas Automatizadas**: Cálculo según normativa laboral japonesa
- **Notificaciones**: Integración con Email y LINE
- **Monitoreo**: Endpoints de health check y métricas

### Autenticación
La API utiliza tokens JWT. Incluye el header: `Authorization: Bearer <token>`.

### Formato de Respuesta
Todas las respuestas retornan JSON estructurado con mensajes y códigos claros.
""",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    contact={
        "name": "UNS-Kikaku Support",
        "email": "support@uns-kikaku.com",
        "url": settings.COMPANY_WEBSITE,
    },
    license_info={"name": "Proprietary"},
    servers=[
        {"url": "http://localhost:8000", "description": "Development"},
        {"url": "https://api.uns-kikaku.com", "description": "Production"},
    ],
)

app.add_middleware(SecurityMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*" if settings.DEBUG else "uns-kikaku.com"])

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)

if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.on_event("startup")
async def on_startup() -> None:
    app_logger.info("Starting application", version=settings.APP_VERSION, environment=settings.ENVIRONMENT)
    try:
        init_db()
        app_logger.info("Database initialised")
    except Exception as exc:  # pragma: no cover - database might be unavailable in tests
        app_logger.exception("Database init failed", error=str(exc))


@app.on_event("shutdown")
async def on_shutdown() -> None:
    app_logger.info("Shutting down application")


@app.get("/")
async def root() -> dict:
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": settings.COMPANY_NAME,
        "website": settings.COMPANY_WEBSITE,
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Not found", "path": str(request.url)})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    app_logger.exception("Internal server error", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc) if settings.DEBUG else "An error occurred"},
    )


from app.api import (  # noqa: E402  pylint: disable=wrong-import-position
    auth,
    candidates,
    dashboard,
    employees,
    factories,
    import_export,
    monitoring,
    notifications,
    ocr,
    reports,
    requests,
    salary,
    timer_cards,
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(employees.router, prefix="/api/employees", tags=["Employees"])
app.include_router(factories.router, prefix="/api/factories", tags=["Factories"])
app.include_router(timer_cards.router, prefix="/api/timer-cards", tags=["Timer Cards"])
app.include_router(salary.router, prefix="/api/salary", tags=["Salary"])
app.include_router(requests.router, prefix="/api/requests", tags=["Requests"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
app.include_router(import_export.router, prefix="/api/import", tags=["Import/Export"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
