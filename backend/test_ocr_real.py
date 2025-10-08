#!/usr/bin/env python3
"""
Script para probar el OCR con una imagen real de tarjeta de residencia
"""
import requests
import base64
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ocr_with_real_image():
    """Probar el OCR con una imagen real de tarjeta de residencia"""
    try:
        # Descargar imagen de ejemplo
        url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Residence_card_of_Japan_sample.jpg/800px-Residence_card_of_Japan_sample.jpg'
        logger.info(f"Descargando imagen desde: {url}")
        
        response = requests.get(url)
        if response.status_code != 200:
            logger.error(f"Error descargando imagen: {response.status_code}")
            return False
        
        # Guardar imagen temporalmente
        image_path = 'test_zairyu_card.jpg'
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"Imagen guardada en: {image_path}")
        
        # Probar endpoint OCR
        api_url = "http://localhost:8000/api/ocr/gemini/process"
        
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/jpeg')}
            
            logger.info(f"Enviando imagen al endpoint: {api_url}")
            response = requests.post(api_url, files=files, timeout=15)
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    data = result.get('data', {})
                    
                    # Verificar campos adicionales
                    fields_to_check = [
                        'name', 'name_kana', 'birthday', 'age', 'address', 
                        'gender', 'nationality', 'card_number', 'visa_type', 
                        'visa_period', 'visa_expiry', 'issue_date'
                    ]
                    
                    logger.info("✅ Campos extraídos:")
                    for field in fields_to_check:
                        value = data.get(field, 'N/A')
                        logger.info(f"  - {field}: {value}")
                    
                    # Verificar formato japonés de fechas
                    if data.get('birthday_jp'):
                        logger.info(f"  - birthday_jp: {data['birthday_jp']}")
                    
                    return True
                else:
                    logger.error("❌ Endpoint devolvió error")
                    return False
            else:
                logger.error(f"❌ Endpoint falló con status: {response.status_code}")
                return False
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists('test_zairyu_card.jpg'):
            os.remove('test_zairyu_card.jpg')

if __name__ == "__main__":
    test_ocr_with_real_image()