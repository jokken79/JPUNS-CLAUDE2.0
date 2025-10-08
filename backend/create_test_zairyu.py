#!/usr/bin/env python3
"""
Script para crear una imagen de prueba de tarjeta de residencia
"""
from PIL import Image, ImageDraw, ImageFont
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_zairyu_image():
    """Crear una imagen de prueba de tarjeta de residencia"""
    try:
        # Crear imagen en blanco (tamaño de tarjeta de residencia)
        img = Image.new('RGB', (854, 540), color='white')
        draw = ImageDraw.Draw(img)
        
        # Intentar usar una fuente estándar
        try:
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except:
            # Si no está disponible, usar fuente por defecto
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Dibujar borde
        draw.rectangle([(10, 10), (844, 530)], outline='#000000', width=2)
        
        # Añadir texto simulando tarjeta de residencia
        draw.text((30, 30), "在留カード", fill='black', font=font_large)
        draw.text((30, 70), "RESIDENCE CARD", fill='black', font=font_medium)
        
        # Foto placeholder
        draw.rectangle([(650, 80), (800, 280)], outline='#cccccc', width=2)
        draw.text((700, 170), "PHOTO", fill='gray', font=font_medium)
        
        # Información personal
        draw.text((30, 120), "氏名 NAME", fill='black', font=font_medium)
        draw.text((30, 150), "山田 太郎", fill='black', font=font_large)
        draw.text((30, 180), "YAMADA TARO", fill='black', font=font_medium)
        
        draw.text((30, 220), "生年月日 DATE OF BIRTH", fill='black', font=font_medium)
        draw.text((30, 250), "1990年01月01日", fill='black', font=font_large)
        draw.text((30, 280), "1990-01-01", fill='black', font=font_medium)
        
        draw.text((30, 320), "性別 SEX", fill='black', font=font_medium)
        draw.text((30, 350), "男性", fill='black', font=font_large)
        
        draw.text((30, 390), "国籍・地域 NATIONALITY/REGION", fill='black', font=font_medium)
        draw.text((30, 420), "ベトナム", fill='black', font=font_large)
        
        draw.text((30, 460), "在留資格 STATUS OF RESIDENCE", fill='black', font=font_medium)
        draw.text((30, 490), "技術・人文知識・国際業務", fill='black', font=font_large)
        
        # Información adicional
        draw.text((430, 120), "番号 CARD NUMBER", fill='black', font=font_medium)
        draw.text((430, 150), "AB12345678CD", fill='black', font=font_large)
        
        draw.text((430, 220), "有効期間 PERIOD OF STAY", fill='black', font=font_medium)
        draw.text((430, 250), "2025年04月01日", fill='black', font=font_large)
        draw.text((430, 280), "2025-04-01", fill='black', font=font_medium)
        
        # Guardar imagen
        img.save('test_zairyu_card.jpg')
        logger.info("Imagen de prueba de tarjeta de residencia creada: test_zairyu_card.jpg")
        
        return 'test_zairyu_card.jpg'
        
    except Exception as e:
        logger.error(f"Error creando imagen de prueba: {e}")
        return None

def test_ocr_with_created_image():
    """Probar el OCR con la imagen creada"""
    try:
        # Crear imagen de prueba
        image_path = create_test_zairyu_image()
        if not image_path:
            return False
        
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

if __name__ == "__main__":
    test_ocr_with_created_image()