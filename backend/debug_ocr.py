#!/usr/bin/env python3
"""
Script para depurar errores del OCR
"""
import requests
import base64
import logging
import traceback
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ocr_with_image():
    """Depurar el OCR con una imagen de prueba"""
    try:
        # Probar endpoint OCR
        api_url = "http://localhost:8000/api/ocr/gemini/process"
        
        with open('test_zairyu_card.jpg', 'rb') as f:
            files = {'file': ('test_zairyu_card.jpg', f, 'image/jpeg')}
            
            logger.info(f"Enviando imagen al endpoint: {api_url}")
            response = requests.post(api_url, files=files, timeout=15)
            
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Headers: {dict(response.headers)}")
            logger.info(f"Response: {response.text}")
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
                except:
                    logger.error(f"Error response: {response.text}")
                
                # Intentar obtener más detalles del error
                logger.error("Intentando endpoint de prueba...")
                try:
                    test_response = requests.get("http://localhost:8000/api/ocr-fixed/test")
                    if test_response.status_code == 200:
                        logger.info(f"Test endpoint response: {test_response.json()}")
                    else:
                        logger.error(f"Test endpoint error: {test_response.status_code}")
                except Exception as e:
                    logger.error(f"Error calling test endpoint: {e}")
            
            return response.status_code == 200
        
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        logger.error(traceback.format_exc())
        return False

def test_direct_gemini_api():
    """Probar la API de Gemini directamente"""
    try:
        # Leer imagen
        with open('test_zairyu_card.jpg', 'rb') as f:
            image_content = f.read()
            image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Configuración de la API
        from app.core.config import settings
        api_key = settings.GEMINI_API_KEY
        
        if not api_key or api_key == 'YOUR_API_KEY_HERE':
            logger.error("❌ Gemini API key no configurada")
            return False
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        
        schema = {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING", "description": "Full name in Japanese (Kanji/Kana) or Latin characters"},
                "name_kana": {"type": "STRING", "description": "Name in Katakana/Hiragana if available"},
                "birthday": {"type": "STRING", "description": "Date of birth in YYYY-MM-DD format"},
                "age": {"type": "INTEGER", "description": "Age calculated from birthday"},
                "address": {"type": "STRING", "description": "Residential address in Japanese"},
                "gender": {"type": "STRING", "description": "Gender: 男性 or 女性"},
                "nationality": {"type": "STRING", "description": "Nationality in Japanese"},
                "card_number": {"type": "STRING", "description": "Residence card number (番号)"},
                "visa_type": {"type": "STRING", "description": "Visa status (在留資格)"},
                "visa_period": {"type": "STRING", "description": "Visa period (在留期間)"},
                "visa_expiry": {"type": "STRING", "description": "Card expiry date in YYYY-MM-DD format"},
                "issue_date": {"type": "STRING", "description": "Card issue date in YYYY-MM-DD format"}
            }
        }
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": """Extract information from this Japanese Residence Card (在留カード):
                    - name (氏名/NAME): Full name
                    - name_kana (氏名カナ): Name in Katakana/Hiragana if available
                    - birthday (生年月日): Date in YYYY-MM-DD format
                    - age: Calculate age from birthday
                    - address (住所): Full address
                    - gender (性別/SEX): 男性 or 女性
                    - nationality (国籍/NATIONALITY): Country in Japanese
                    - card_number (番号/NUMBER): Card number
                    - visa_type (在留資格/STATUS): Residence status
                    - visa_period (在留期間): Visa period
                    - visa_expiry: Expiry date in YYYY-MM-DD format
                    - issue_date (有効期間開始): Issue date"""
                }, {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": image_base64
                    }
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "temperature": 0.1
            }
        }
        
        logger.info("Llamando a Gemini API directamente...")
        response = requests.post(url, json=payload, timeout=15)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
            
            if text_content:
                parsed_data = json.loads(text_content)
                logger.info(f"✅ Datos extraídos: {json.dumps(parsed_data, indent=2)}")
                return True
            else:
                logger.error("❌ Gemini API devolvió contenido vacío")
                return False
        else:
            logger.error(f"❌ Error en Gemini API: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Error en prueba directa: {e}")
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("🔍 Iniciando depuración del OCR...")
    
    # 1. Probar endpoint del backend
    logger.info("\n📋 Prueba 1: Endpoint del backend")
    if debug_ocr_with_image():
        logger.info("✅ Endpoint del backend funciona")
    else:
        logger.error("❌ Endpoint del backend falla")
    
    # 2. Probar API de Gemini directamente
    logger.info("\n📋 Prueba 2: API de Gemini directamente")
    if test_direct_gemini_api():
        logger.info("✅ API de Gemini funciona")
    else:
        logger.error("❌ API de Gemini falla")
    
    logger.info("\n🔍 Depuración completada")