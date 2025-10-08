"""
OCR API Endpoints for UNS-ClaudeJP 2.0
All OCR processing happens in backend
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
import shutil
from app.services.ocr_service import ocr_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ocr_temp"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/process")
async def process_ocr_document(
    file: UploadFile = File(...),
    document_type: str = "zairyu_card"
):
    """
    Process document with OCR (Gemini + Vision + Tesseract hybrid)
    
    Args:
        file: Uploaded image file
        document_type: Type of document (zairyu_card, license, etc.)
        
    Returns:
        Extracted data from document
    """
    temp_file = None
    
    try:
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Check file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Save file temporarily
        file_extension = Path(file.filename).suffix
        temp_file = UPLOAD_DIR / f"temp_{file.filename}"
        
        with open(temp_file, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Processing OCR for file: {file.filename}, type: {document_type}")
        
        # Process with OCR service
        result = ocr_service.process_document(str(temp_file), document_type)
        
        if not result:
            raise HTTPException(status_code=500, detail="OCR processing failed")
        
        logger.info(f"OCR processing completed successfully")
        
        return JSONResponse(content={
            "success": True,
            "data": result,
            "message": "Document processed successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing error: {str(e)}")
    finally:
        # Cleanup temporary file
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")


@router.post("/process-from-base64")
async def process_ocr_from_base64(
    image_base64: str,
    mime_type: str,
    document_type: str = "zairyu_card"
):
    """
    Process document from base64 image
    
    Args:
        image_base64: Base64 encoded image
        mime_type: MIME type of image
        document_type: Type of document
        
    Returns:
        Extracted data from document
    """
    import base64
    
    temp_file = None
    
    try:
        # Decode base64
        image_data = base64.b64decode(image_base64)
        
        # Save temporarily
        extension = mime_type.split('/')[-1]
        temp_file = UPLOAD_DIR / f"temp_{document_type}.{extension}"
        
        with open(temp_file, 'wb') as f:
            f.write(image_data)
        
        # Process with OCR
        result = ocr_service.process_document(str(temp_file), document_type)
        
        return JSONResponse(content={
            "success": True,
            "data": result,
            "message": "Document processed successfully"
        })
        
    except Exception as e:
        logger.error(f"Error processing base64 OCR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass


@router.get("/cache-stats")
async def get_cache_stats():
    """Get OCR cache statistics"""
    try:
        cache_dir = Path(settings.UPLOAD_DIR) / "ocr_cache"
        
        if not cache_dir.exists():
            return {"total_cached": 0, "cache_size_mb": 0}
        
        cache_files = list(cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            "total_cached": len(cache_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_directory": str(cache_dir)
        }
        
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"error": str(e)}


@router.delete("/clear-cache")
async def clear_ocr_cache():
    """Clear OCR cache"""
    try:
        cache_dir = Path(settings.UPLOAD_DIR) / "ocr_cache"
        
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            
        return {"success": True, "message": "Cache cleared successfully"}
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))
