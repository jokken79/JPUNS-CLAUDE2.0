#!/usr/bin/env python3
"""
Script para crear una imagen de prueba válida para el OCR
"""
import base64
from PIL import Image, ImageDraw, ImageFont
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_image():
    """Crear una imagen de prueba con texto"""
    # Crear imagen en blanco
    img = Image.new('RGB', (400, 200), color='white')
    draw = ImageDraw.Draw(img)
    
    # Añadir texto
    try:
        # Intentar usar una fuente estándar
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        # Si no está disponible, usar fuente por defecto
        font = ImageFont.load_default()
    
    draw.text((10, 10), "Test OCR Image", fill='black', font=font)
    draw.text((10, 40), "Name: Test User", fill='black', font=font)
    draw.text((10, 70), "Birthday: 1990-01-01", fill='black', font=font)
    draw.text((10, 100), "Address: Test Address", fill='black', font=font)
    
    # Guardar imagen
    img.save('test_ocr.png')
    logger.info("Imagen de prueba creada: test_ocr.png")
    
    return 'test_ocr.png'

def test_ocr_with_image():
    """Probar el OCR con una imagen real"""
    try:
        # Crear imagen de prueba
        image_path = create_test_image()
        
        # Probar endpoint
        url = "http://localhost:8000/api/ocr-fixed/gemini/process"
        
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/png')}
            
            logger.info(f"Probando OCR con imagen real: {url}")
            response = requests.post(url, files=files, timeout=15)
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    logger.info("✅ OCR con imagen real funciona")
                    return True
                else:
                    logger.error("❌ OCR con imagen real devolvió error")
                    return False
            else:
                logger.error(f"❌ OCR con imagen real falló con status: {response.status_code}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Error en prueba con imagen real: {e}")
        return False

if __name__ == "__main__":
    test_ocr_with_image()