"""
OCR API Endpoints - UNS-ClaudeJP 2.0
Versión optimizada con procesamiento paralelo y manejo de caché
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
import time
import asyncio
from typing import Dict, Optional, List
import logging
import tempfile
import base64
import json
from pathlib import Path

from app.services.ocr_service_optimized import optimized_ocr_service
from app.core.config import settings

router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger(__name__)

@router.post("/process")
async def process_ocr_document(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    """
    Procesa un documento con OCR usando el servicio optimizado.
    Soporta zairyu_card (tarjeta de residencia), license (licencia de conducir) y documentos generales.
    """
    try:
        start_time = time.time()
        logger.info(f"Processing OCR document: {file.filename}, type: {document_type}")
        
        # Guardar archivo temporalmente
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        try:
            contents = await file.read()
            temp_file.write(contents)
            temp_file.close()
            
            # Procesar con el servicio OCR optimizado
            ocr_result = await optimized_ocr_service.process_document(
                temp_file.name, 
                document_type
            )
            
            elapsed = time.time() - start_time
            logger.info(f"OCR processing completed in {elapsed:.2f}s")
            
            return {
                "success": True, 
                "data": ocr_result,
                "processing_time": f"{elapsed:.2f}s"
            }
            
        finally:
            # Limpiar archivo temporal
            try:
                os.unlink(temp_file.name)
            except:
                pass
    
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error processing document: {str(e)}"}
        )

@router.post("/process-from-base64")
async def process_ocr_from_base64(request: Dict):
    """
    Procesa una imagen en base64 con OCR.
    Requiere: image_base64, mime_type, document_type
    """
    try:
        # Validar campos requeridos
        required_fields = ["image_base64", "mime_type", "document_type"]
        for field in required_fields:
            if field not in request:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Extraer campos
        image_base64 = request["image_base64"]
        mime_type = request["mime_type"]
        document_type = request["document_type"]
        
        # Procesar con el servicio OCR
        start_time = time.time()
        
        result = optimized_ocr_service.process_from_base64(
            image_base64, 
            mime_type, 
            document_type
        )
        
        elapsed = time.time() - start_time
        
        return {
            "success": True, 
            "data": result,
            "processing_time": f"{elapsed:.2f}s"
        }
    
    except Exception as e:
        logger.error(f"Base64 OCR processing error: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error processing image: {str(e)}"}
        )

@router.get("/cache-stats")
async def get_cache_statistics():
    """Obtener estadísticas del caché de OCR"""
    try:
        stats = optimized_ocr_service.get_cache_stats()
        return {"success": True, "stats": stats}
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error getting cache stats: {str(e)}"}
        )

@router.delete("/clear-cache")
async def clear_cache():
    """Limpiar todo el caché de OCR"""
    try:
        result = optimized_ocr_service.clear_cache()
        return result
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error clearing cache: {str(e)}"}
        )

@router.post("/warm-up")
async def warm_up_ocr_service(background_tasks: BackgroundTasks):
    """
    Iniciar el servicio OCR en segundo plano para evitar latencia en primera solicitud
    """
    def _warm_up():
        try:
            # Generar una imagen de prueba simple
            from PIL import Image, ImageDraw, ImageFont
            import numpy as np
            
            # Crear una imagen blanca con texto
            img = Image.new('RGB', (800, 600), color = (255, 255, 255))
            d = ImageDraw.Draw(img)
            
            # Agregar algunos caracteres japoneses y números
            d.text((100,100), "氏名: 山田太郎", fill=(0,0,0))
            d.text((100,150), "生年月日: 1990年01月01日", fill=(0,0,0))
            d.text((100,200), "住所: 東京都港区", fill=(0,0,0))
            
            # Guardar temporalmente
            temp_path = os.path.join(tempfile.gettempdir(), "ocr_warmup.jpg")
            img.save(temp_path)
            
            # Iniciar procesamiento
            logger.info("Warming up OCR service...")
            optimized_ocr_service.extract_text_with_tesseract_multi(temp_path)
            logger.info("OCR service warm-up complete")
            
            # Limpiar
            try:
                os.unlink(temp_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error during OCR warm-up: {e}")
    
    # Ejecutar en segundo plano
    background_tasks.add_task(_warm_up)
    return {"success": True, "message": "OCR warm-up started"}