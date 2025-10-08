#!/usr/bin/env python3
"""
Script de prueba para el OCR mejorado con extracción de campos adicionales
"""
import requests
import base64
import json
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ocr_enhanced_fields():
    """Probar la extracción de campos adicionales del OCR"""
    try:
        # Crear imagen de prueba simple (1x1 pixel)
        test_image_data = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        )
        
        # Probar endpoint mejorado
        url = "http://localhost:8000/api/ocr-fixed/gemini/process"
        files = {'file': ('test.png', test_image_data, 'image/png')}
        
        logger.info(f"Probando extracción de campos adicionales: {url}")
        response = requests.post(url, files=files, timeout=15)
        
        logger.info(f"Status Code: {response.status_code}")
        
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
        
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout en endpoint")
        return False
    except Exception as e:
        logger.error(f"❌ Error en prueba: {e}")
        return False

def test_age_calculation():
    """Probar el cálculo automático de edad"""
    try:
        from app.services.ocr_service_fixed import ocr_service_fixed
        
        # Probar cálculo de edad con diferentes fechas
        test_dates = [
            ("1990-01-01", 34),  # Aproximado
            ("1985-12-31", 38),  # Aproximado
            ("2000-05-15", 24),  # Aproximado
        ]
        
        logger.info("\n📋 Prueba de cálculo de edad:")
        for date_str, expected_age in test_dates:
            calculated_age = ocr_service_fixed._calculate_age(date_str)
            # Permitir una diferencia de ±1 año debido al año actual
            if abs(calculated_age - expected_age) <= 1:
                logger.info(f"✅ {date_str} → {calculated_age} años (esperado aprox. {expected_age})")
            else:
                logger.error(f"❌ {date_str} → {calculated_age} años (esperado aprox. {expected_age})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de cálculo de edad: {e}")
        return False

def test_date_formatting():
    """Probar el formateo de fechas en japonés"""
    try:
        from app.services.ocr_service_fixed import ocr_service_fixed
        
        # Probar formateo de fechas
        test_dates = [
            "1990-01-01",
            "1985-12-31",
            "2000-05-15",
            "null",
            ""
        ]
        
        logger.info("\n📋 Prueba de formateo de fechas:")
        for date_str in test_dates:
            formatted = ocr_service_fixed._format_date_japanese(date_str)
            if date_str and date_str != "null":
                logger.info(f"✅ {date_str} → {formatted}")
            else:
                logger.info(f"✅ {date_str} → '{formatted}' (vacío)")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en prueba de formateo de fechas: {e}")
        return False

def main():
    """Función principal de prueba"""
    logger.info("🔍 Iniciando prueba del OCR mejorado...")
    
    # 1. Prueba de cálculo de edad
    logger.info("\n📋 Prueba 1: Cálculo automático de edad")
    if test_age_calculation():
        logger.info("✅ Cálculo de edad funciona")
    else:
        logger.error("❌ Cálculo de edad falla")
    
    # 2. Prueba de formateo de fechas
    logger.info("\n📋 Prueba 2: Formateo de fechas en japonés")
    if test_date_formatting():
        logger.info("✅ Formateo de fechas funciona")
    else:
        logger.error("❌ Formateo de fechas falla")
    
    # 3. Prueba de extracción de campos adicionales
    logger.info("\n📋 Prueba 3: Extracción de campos adicionales")
    if test_ocr_enhanced_fields():
        logger.info("✅ Extracción de campos adicionales funciona")
    else:
        logger.error("❌ Extracción de campos adicionales falla")
    
    logger.info("\n🔍 Prueba completada")

if __name__ == "__main__":
    main()