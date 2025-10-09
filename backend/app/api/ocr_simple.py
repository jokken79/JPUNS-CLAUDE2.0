"""
Simple OCR API Endpoint
Clean implementation for document OCR processing
"""
import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from app.services.ocr_simple import ocr_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Create temp directory for uploads
UPLOAD_DIR = Path(tempfile.gettempdir()) / "ocr_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.options("/process")
async def process_options():
    """Handle CORS preflight"""
    return JSONResponse(
        content={"success": True},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )


@router.post("/process")
async def process_ocr(
    file: UploadFile = File(...),
    document_type: str = Form("zairyu_card")
) -> Dict[str, Any]:
    """
    Process document with OCR

    Args:
        file: Uploaded image file
        document_type: Type of document (zairyu_card, rirekisho, license)

    Returns:
        OCR results with extracted data
    """
    temp_file_path = None

    try:
        logger.info(f"Received OCR request: document_type={document_type}, filename={file.filename}")

        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.content_type}. Only images are supported."
            )

        # Read file content
        content = await file.read()
        logger.info(f"File read successfully, size: {len(content)} bytes")

        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".tmp",
            dir=UPLOAD_DIR
        )
        temp_file.write(content)
        temp_file.close()
        temp_file_path = temp_file.name

        logger.info(f"Temporary file created: {temp_file_path}")

        # Process with OCR
        logger.info("Starting OCR processing...")
        result = ocr_service.process_document(temp_file_path, document_type)

        logger.info("OCR processing completed successfully")

        return {
            "success": True,
            "message": "Document processed successfully",
            "data": result
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"OCR processing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"OCR processing failed: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Temporary file deleted: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ocr_simple",
        "model": ocr_service.model_name
    }
