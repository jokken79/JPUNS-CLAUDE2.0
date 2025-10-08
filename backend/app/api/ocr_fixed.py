"""
OCR API Endpoints for UNS-ClaudeJP 2.0 - FIXED VERSION
All OCR processing happens in backend with improved error handling and timeouts
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import logging
import os
from pathlib import Path
import shutil
from app.services.ocr_service_fixed import ocr_service_fixed
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ocr_temp_fixed"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/process")
async def process_ocr_document(
    file: UploadFile = File(...),
    document_type: str = "zairyu_card"
):
    """
    Process document with OCR (Gemini + Vision + Tesseract hybrid) - FIXED VERSION
    
    Args:
        file: Uploaded image file
        document_type: Type of document (zairyu_card, license, etc.)
        
    Returns:
        Extracted data from document
    """
    temp_file = None
    
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Check file size (max 10MB)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Save file temporarily
        file_extension = Path(file.filename or "temp.jpg").suffix
        temp_file = UPLOAD_DIR / f"temp_{file.filename}"
        
        with open(temp_file, 'wb') as f:
            f.write(file_content)
        
        logger.info(f"Processing OCR for file: {file.filename}, type: {document_type}")
        
        # Process with OCR service (fixed version)
        result = ocr_service_fixed.process_document(str(temp_file), document_type)
        
        if not result:
            raise HTTPException(status_code=500, detail="OCR processing failed")
        
        # Check if there was an error in the result
        if 'error' in result:
            logger.warning(f"OCR processing completed with errors: {result['error']}")
            return JSONResponse(content={
                "success": True,
                "data": result,
                "message": "Document processed with errors",
                "warning": result['error']
            })
        
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
    Process document from base64 image - FIXED VERSION
    
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
        
        # Process with OCR (fixed version)
        result = ocr_service_fixed.process_document(str(temp_file), document_type)
        
        # Check if there was an error in the result
        if 'error' in result:
            logger.warning(f"OCR processing completed with errors: {result['error']}")
            return JSONResponse(content={
                "success": True,
                "data": result,
                "message": "Document processed with errors",
                "warning": result['error']
            })
        
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


@router.post("/gemini/process", response_model=dict)
async def process_with_gemini(file: UploadFile = File(...)):
    """
    Procesa imagen con Gemini API desde el backend - FIXED VERSION
    Esto protege la API key y centraliza el procesamiento OCR
    """
    try:
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Solo se aceptan imágenes")
        
        # Leer archivo
        content = await file.read()
        
        # Validar tamaño (máx 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagen muy grande (máx 10MB)")
        
        # Convertir a base64
        import base64
        base64_image = base64.b64encode(content).decode('utf-8')
        
        # Procesar con Gemini (fixed version)
        logger.info(f"Processing image with Gemini: {file.filename}")
        result = ocr_service_fixed.extract_text_with_gemini_api_from_base64(
            base64_image=base64_image,
            mime_type=file.content_type or "image/jpeg"
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="OCR falló")
        
        logger.info("OCR successful")
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


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


@router.get("/test")
async def test_ocr_service():
    """Test OCR service status"""
    try:
        return {
            "status": "healthy",
            "service": "ocr_fixed",
            "gemini_api_key": bool(ocr_service_fixed.gemini_api_key),
            "vision_api_key": bool(ocr_service_fixed.vision_api_key),
            "timeout": ocr_service_fixed.request_timeout
        }
    except Exception as e:
        logger.error(f"Error testing OCR service: {e}")
        raise HTTPException(status_code=500, detail=str(e))