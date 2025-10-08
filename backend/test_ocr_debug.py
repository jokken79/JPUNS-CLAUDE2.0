#!/usr/bin/env python3
"""
Script de diagnóstico para el problema del OCR
"""
import requests
import base64
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_api_direct():
    """Probar la API de Gemini directamente"""
    try:
        from app.core.config import settings
        from app.services.ocr_service import ocr_service
        
        # Crear una imagen de prueba simple (1x1 pixel)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # Guardar imagen temporal
        temp_path = Path("temp_test.png")
        with open(temp_path, "wb") as f:
            f.write(test_image_data)
        
        logger.info("Probando OCR con Gemini API...")
        result = ocr_service.extract_text_with_gemini_api(str(temp_path))
        logger.info(f"Resultado: {result}")
        
        # Limpiar
        temp_path.unlink()
        return True
        
    except Exception as e:
        logger.error(f"Error en prueba directa: {e}")
        return False

def test_ocr_endpoint():
    """Probar el endpoint del OCR"""
    try:
        # Crear imagen de prueba
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # Probar endpoint
        url = "http://localhost:8000/api/ocr/gemini/process"
        files = {'file': ('test.png', test_image_data, 'image/png')}
        
        logger.info(f"Probando endpoint: {url}")
        response = requests.post(url, files=files, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error en prueba de endpoint: {e}")
        return False

def test_ocr_alternative_endpoint():
    """Probar el endpoint alternativo del OCR"""
    try:
        # Crear imagen de prueba
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # Probar endpoint alternativo
        url = "http://localhost:8000/api/ocr/process"
        files = {'file': ('test.png', test_image_data, 'image/png')}
        data = {'document_type': 'zairyu_card'}
        
        logger.info(f"Probando endpoint alternativo: {url}")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error en prueba de endpoint alternativo: {e}")
        return False

def check_backend_health():
    """Verificar si el backend está funcionando"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Backend está funcionando")
            return True
        else:
            logger.error(f"❌ Backend status: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ Error conectando al backend: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    logger.info("🔍 Iniciando diagnóstico del OCR...")
    
    # 1. Verificar backend
    if not check_backend_health():
        logger.error("❌ El backend no está funcionando. Inicia el servidor primero.")
        return
    
    # 2. Probar API directa
    logger.info("\n📋 Prueba 1: API directa de Gemini")
    if test_gemini_api_direct():
        logger.info("✅ API directa funciona")
    else:
        logger.error("❌ API directa falla")
    
    # 3. Probar endpoint principal
    logger.info("\n📋 Prueba 2: Endpoint principal /api/ocr/gemini/process")
    if test_ocr_endpoint():
        logger.info("✅ Endpoint principal funciona")
    else:
        logger.error("❌ Endpoint principal falla")
    
    # 4. Probar endpoint alternativo
    logger.info("\n📋 Prueba 3: Endpoint alternativo /api/ocr/process")
    if test_ocr_alternative_endpoint():
        logger.info("✅ Endpoint alternativo funciona")
    else:
        logger.error("❌ Endpoint alternativo falla")
    
    logger.info("\n🔍 Diagnóstico completado")

if __name__ == "__main__":
    main()