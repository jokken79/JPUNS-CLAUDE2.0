"""OCR API endpoints consolidating hybrid pipeline."""
from __future__ import annotations

import asyncio
import base64
import tempfile
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.logging import app_logger
from app.schemas.responses import CacheStatsResponse, ErrorResponse, OCRResponse
from app.services.ocr_service import ocr_service

router = APIRouter()
UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ocr_temp"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post(
    "/process",
    response_model=OCRResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def process_ocr_document(
    file: UploadFile = File(..., description="Imagen a procesar"),
    document_type: str = Form("zairyu_card", description="Tipo de documento"),
) -> Dict[str, Any]:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are supported")
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds limit")
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix, dir=UPLOAD_DIR)
    temp_file.write(content)
    temp_file.close()
    try:
        result = await ocr_service.process_document(temp_file.name, document_type)
        return {"success": True, "data": result, "message": "Document processed successfully"}
    except Exception as exc:  # pragma: no cover - fallback
        app_logger.exception("OCR processing failed", document_type=document_type)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        Path(temp_file.name).unlink(missing_ok=True)


@router.post(
    "/process-from-base64",
    response_model=OCRResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def process_ocr_from_base64(
    image_base64: str = Form(..., description="Imagen en base64"),
    mime_type: str = Form(..., description="Tipo MIME"),
    document_type: str = Form("zairyu_card"),
) -> Dict[str, Any]:
    if not image_base64:
        raise HTTPException(status_code=400, detail="image_base64 is required")
    try:
        result = await ocr_service.process_from_base64(image_base64, mime_type, document_type)
        return {"success": True, "data": result, "message": "Document processed successfully"}
    except Exception as exc:  # pragma: no cover
        app_logger.exception("OCR base64 failed", document_type=document_type)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/cache/stats", response_model=CacheStatsResponse)
async def get_cache_statistics() -> Dict[str, Any]:
    return {"success": True, "stats": ocr_service.get_cache_stats()}


@router.delete("/cache", response_model=Dict[str, Any])
async def clear_ocr_cache() -> Dict[str, Any]:
    return ocr_service.clear_cache()


@router.post("/warm-up")
async def warm_up_ocr_service(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    def _warm_up() -> None:
        try:
            app_logger.info("OCR warm-up started")
            # Create tiny blank image for pipeline warm-up
            import io
            from PIL import Image

            image = Image.new("RGB", (10, 10), color="white")
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
            asyncio.run(ocr_service.process_from_base64(encoded, "image/png", "warmup"))
            app_logger.info("OCR warm-up completed")
        except Exception as exc:  # pragma: no cover
            app_logger.warning("Warm up failed", error=str(exc))

    background_tasks.add_task(_warm_up)
    return {"success": True, "message": "OCR warm-up started"}
