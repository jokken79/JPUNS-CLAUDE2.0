#!/usr/bin/env python3
"""
Script de prueba para el OCR corregido
"""
import requests
import base64
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ocr_fixed_endpoint():
    """Probar el nuevo endpoint del OCR corregido"""
    try:
        # Crear imagen de prueba simple (1x1 pixel)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # Probar endpoint corregido
        url = "http://localhost:8000/api/ocr-fixed/gemini/process"
        files = {'file': ('test.png', test_image_data, 'image/png')}
        
        logger.info(f"Probando endpoint corregido: {url}")
        response = requests.post(url, files=files, timeout=15)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                logger.info("✅ Endpoint corregido funciona correctamente")
                return True
            else:
                logger.error("❌ Endpoint corregido devolvió error")
                return False
        else:
            logger.error(f"❌ Endpoint corregido falló con status: {response.status_code}")
            return False
        
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout en endpoint corregido")
        return False
    except Exception as e:
        logger.error(f"❌ Error en prueba de endpoint corregido: {e}")
        return False

def test_ocr_fixed_status():
    """Probar el endpoint de estado del OCR corregido"""
    try:
        url = "http://localhost:8000/api/ocr-fixed/test"
        
        logger.info(f"Probando endpoint de estado: {url}")
        response = requests.get(url, timeout=5)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            logger.info("✅ Endpoint de estado funciona correctamente")
            return True
        else:
            logger.error(f"❌ Endpoint de estado falló con status: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de endpoint de estado: {e}")
        return False

def main():
    """Función principal de prueba"""
    logger.info("🔍 Iniciando prueba del OCR corregido...")
    
    # 1. Probar endpoint de estado
    logger.info("\n📋 Prueba 1: Endpoint de estado")
    if test_ocr_fixed_status():
        logger.info("✅ Endpoint de estado funciona")
    else:
        logger.error("❌ Endpoint de estado falla")
    
    # 2. Probar endpoint principal
    logger.info("\n📋 Prueba 2: Endpoint principal /api/ocr-fixed/gemini/process")
    if test_ocr_fixed_endpoint():
        logger.info("✅ Endpoint principal funciona")
    else:
        logger.error("❌ Endpoint principal falla")
    
    logger.info("\n🔍 Prueba completada")

if __name__ == "__main__":
    main()