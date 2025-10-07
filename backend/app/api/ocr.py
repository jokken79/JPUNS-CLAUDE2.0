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
from pydantic import BaseModel
import httpx
import json

from app.services.ocr_service import ocr_service
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "ocr_temp"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Pydantic model for the proxy request
class GeminiProxyRequest(BaseModel):
    image_base64: str
    mime_type: str

@router.post("/gemini-proxy")
async def gemini_proxy(request: GeminiProxyRequest):
    """
    Acts as a secure proxy to the Google Gemini API.
    The API key is handled on the backend and not exposed to the client.
    """
    if not settings.GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY is not configured on the server.")
        raise HTTPException(
            status_code=500,
            detail="The OCR service is not configured correctly. Please contact support."
        )

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={settings.GEMINI_API_KEY}"

    # Structured output schema, same as the one previously in the frontend
    schema = {
        "type": "OBJECT",
        "properties": {
            "name": { "type": "STRING", "description": "Full name in Japanese (Kanji/Kana) or Latin characters if foreign." },
            "birthday": { "type": "STRING", "description": "Date of birth in YYYY-MM-DD format." },
            "address": { "type": "STRING", "description": "Residential address in Japanese." },
            "photo": { "type": "STRING", "description": "The person's face photo as a base64 encoded string." }
        },
        "propertyOrdering": ["name", "birthday", "address", "photo"]
    }

    payload = {
        "contents": [{
            "parts": [{
                "text": "Extract the name (氏名), birthday (生年月日 in YYYY-MM-DD format), address (住所), and the person's face photo from this Japanese ID card image (Residence Card or Driver's License). Return only the JSON object with the photo as a base64 encoded string."
            }, {
                "inlineData": {
                    "mimeType": request.mime_type,
                    "data": request.image_base64
                }
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": schema,
            "temperature": 0.1
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(api_url, json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

            # Directly return the successful response from Gemini
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Gemini API request failed with status {e.response.status_code}: {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error from OCR provider: {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"An error occurred while requesting Gemini API: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to connect to OCR service: {e}"
            )
        except Exception as e:
            logger.error(f"An unexpected error occurred in the Gemini proxy: {e}")
            raise HTTPException(
                status_code=500,
                detail="An unexpected error occurred."
            )


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
