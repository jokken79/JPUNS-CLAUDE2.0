"""
OCR Service for UNS-ClaudeJP 2.0 - FIXED VERSION
Sistema híbrido: Gemini + Vision API + Tesseract con cache y manejo de errores mejorado
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import re
from typing import Dict, Optional, List, Tuple
import os
from datetime import datetime, date
import base64
import requests
import logging
import hashlib
import json
from pathlib import Path
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(settings.UPLOAD_DIR) / "ocr_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


class TimeoutException(Exception):
    """Excepción personalizada para timeouts"""
    pass


def timeout_handler(signum, frame):
    """Handler para la señal de timeout"""
    raise TimeoutException("Operación excedió el tiempo límite")


class OCRService:
    """Service for OCR processing with hybrid approach, caching, and improved error handling"""
    
    def __init__(self):
        self.tesseract_lang = settings.TESSERACT_LANG
        self.vision_api_key = settings.GOOGLE_CLOUD_VISION_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.cache = {}
        self.request_timeout = 10  # 10 segundos timeout para todas las peticiones
        
    def _get_image_hash(self, image_path: str) -> str:
        """Generate MD5 hash of image for caching"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_cache(self, image_hash: str) -> Optional[Dict]:
        """Load cached OCR result if exists"""
        cache_file = CACHE_DIR / f"{image_hash}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _save_cache(self, image_hash: str, data: Dict):
        """Save OCR result to cache"""
        cache_file = CACHE_DIR / f"{image_hash}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _validate_result(self, result: Dict, document_type: str = "zairyu_card") -> bool:
        """Validate that result has minimum required data depending on document type"""
        if not result:
            return False

        if document_type == "license":
            has_name = bool(result.get('name'))
            has_additional_data = any(
                result.get(field)
                for field in [
                    'birthday',
                    'license_number',
                    'license_expiry',
                    'license_type'
                ]
            )
            return has_name and has_additional_data

        return bool(result.get('name') and result.get('birthday'))
    
    def _calculate_age(self, birthday_str: str) -> int:
        """Calculate age from birthday string (YYYY-MM-DD)"""
        try:
            birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
            today = date.today()
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            return age
        except Exception as e:
            logger.error(f"Error calculating age: {e}")
            return 0
    
    def _format_date_japanese(self, date_str: str) -> str:
        """Convert YYYY-MM-DD to Japanese format (YYYY年MM月DD日)"""
        try:
            if not date_str or date_str == "null":
                return ""
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"
        except Exception as e:
            logger.error(f"Error formatting date: {e}")
            return date_str

    def _convert_japanese_era_to_year(self, era: str, era_year: int) -> Optional[int]:
        """Convert Japanese era year to Gregorian year"""
        era_mapping = {
            '令和': 2018,
            '平成': 1988,
            '昭和': 1925
        }

        base_year = era_mapping.get(era)
        if base_year is None:
            return None

        return base_year + era_year

    def _parse_japanese_date(self, raw: str) -> Optional[str]:
        """Parse Japanese date strings including era notation into YYYY-MM-DD"""
        if not raw:
            return None

        text = raw.strip()

        match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
        if match:
            year, month, day = match.groups()
            try:
                datetime(int(year), int(month), int(day))
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            except ValueError:
                return None

        match = re.search(r'(令和|平成|昭和)\s*(\d{1,2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', text)
        if match:
            era, era_year, month, day = match.groups()
            converted_year = self._convert_japanese_era_to_year(era, int(era_year))
            if converted_year:
                try:
                    datetime(converted_year, int(month), int(day))
                    return f"{converted_year:04d}-{int(month):02d}-{int(day):02d}"
                except ValueError:
                    return None

        match = re.search(r'(\d{4})[./-](\d{1,2})[./-](\d{1,2})', text)
        if match:
            year, month, day = match.groups()
            try:
                datetime(int(year), int(month), int(day))
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            except ValueError:
                return None

        return None
    
    def _make_request_with_timeout(self, url: str, payload: Dict, timeout: int = None) -> requests.Response:
        """
        Realiza una petición HTTP con timeout y manejo de errores mejorado
        """
        if timeout is None:
            timeout = self.request_timeout
            
        try:
            logger.info(f"Realizando petición a {url} con timeout {timeout}s")
            response = requests.post(
                url, 
                json=payload, 
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            # Log de respuesta para debugging
            logger.info(f"Respuesta recibida: Status {response.status_code}")
            
            # Verificar si la respuesta es exitosa
            if response.status_code != 200:
                logger.error(f"Error en API: Status {response.status_code}, Response: {response.text[:200]}")
                
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout en petición a {url} después de {timeout}s")
            raise TimeoutException(f"La petición a {url} excedió el tiempo límite de {timeout}s")
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión a {url}")
            raise TimeoutException(f"No se pudo conectar a {url}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en petición a {url}: {str(e)}")
            raise TimeoutException(f"Error en petición a {url}: {str(e)}")
    
    def extract_text_with_gemini_api(self, image_path: str, document_type: str = "zairyu_card") -> Dict:
        """
        Extract structured data from image using Gemini API
        Returns dict with name, birthday, address, gender, nationality, etc.
        """
        try:
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={self.gemini_api_key}"

            doc_type = (document_type or "zairyu_card").lower()
            if doc_type == "license_card":
                doc_type = "license"

            if doc_type == "license":
                schema = {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING", "description": "氏名 (full name)"},
                        "name_kana": {"type": "STRING", "description": "フリガナ (name in Katakana)"},
                        "birthday": {"type": "STRING", "description": "生年月日 in YYYY-MM-DD"},
                        "age": {"type": "INTEGER", "description": "Age calculated from birthday"},
                        "gender": {"type": "STRING", "description": "性別 (男性/女性)"},
                        "address": {"type": "STRING", "description": "住所"},
                        "postal_code": {"type": "STRING", "description": "郵便番号 (#####-###) if visible"},
                        "license_number": {"type": "STRING", "description": "免許証番号 (12 digits)"},
                        "license_expiry": {"type": "STRING", "description": "有効期限 YYYY-MM-DD"},
                        "issue_date": {"type": "STRING", "description": "交付年月日 YYYY-MM-DD"},
                        "license_type": {"type": "STRING", "description": "免許種類 (普通免許など)"},
                        "license_conditions": {"type": "STRING", "description": "条件等 (例: 眼鏡等)"}
                    }
                }

                instruction_text = """Extract all important information from this Japanese driver's license (運転免許証):
- name (氏名)
- name_kana (フリガナ)
- birthday (生年月日) formatted as YYYY-MM-DD
- age calculated from the birthday
- gender (男性 or 女性)
- address (住所) including prefecture and city
- postal_code if visible
- license_number (免許証番号) with 12 digits
- license_expiry (有効期限) in YYYY-MM-DD
- issue_date (交付年月日) in YYYY-MM-DD
- license_type (免許種類)
- license_conditions (条件等)"""
            else:
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
                        "issue_date": {"type": "STRING", "description": "Card issue date in YYYY-MM-DD format"},
                        "region": {"type": "STRING", "description": "Region/Zone (地域)"},
                        "permission_date": {"type": "STRING", "description": "Permission date (許可年月日)"},
                        "authorized_activity": {"type": "STRING", "description": "Authorized activity (就労活動の許可)"},
                        "employer_restriction": {"type": "STRING", "description": "Employer restriction (指定書就職活動の範囲)"},
                        "passport_number": {"type": "STRING", "description": "Passport number if visible"},
                        "passport_expiry": {"type": "STRING", "description": "Passport expiry date if visible"}
                    }
                }

                instruction_text = """Extract all information from this Japanese Residence Card (在留カード):
- name (氏名/NAME): Full name
- name_kana (氏名カナ): Name in Katakana/Hiragana if available
- birthday (生年月日): Date in YYYY-MM-DD format
- age: Calculate age from birthday
- address (住所): Full address including postal code
- gender (性別/SEX): 男性 or 女性
- nationality (国籍/NATIONALITY): Country in Japanese
- card_number (番号/NUMBER): Card number
- visa_type (在留資格/STATUS): Residence status
- visa_period (在留期間): Visa period
- visa_expiry: Expiry date in YYYY-MM-DD format
- issue_date (有効期間開始): Issue date
- region (地域): Region/Zone if visible
- permission_date (許可年月日): Permission date if visible
- authorized_activity (就労活動の許可): Work permission details if visible
- employer_restriction (指定書就職活動の範囲): Employer restrictions if visible
- passport_number: Passport number if visible
- passport_expiry: Passport expiry date if visible"""

            payload = {
                "contents": [{
                    "parts": [{
                        "text": instruction_text
                    }, {
                        "inlineData": {
                            "mimeType": mime_type,
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

            response = self._make_request_with_timeout(url, payload)
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code}")
                return {}

            result = response.json()
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

            if not text_content:
                logger.warning("Gemini API returned empty content")
                return {}

            parsed_data = json.loads(text_content)
            
            # Calculate age if birthday is available
            if parsed_data.get('birthday') and not parsed_data.get('age'):
                parsed_data['age'] = self._calculate_age(parsed_data['birthday'])
            
            # Format dates in Japanese format
            if parsed_data.get('birthday'):
                parsed_data['birthday_jp'] = self._format_date_japanese(parsed_data['birthday'])

            if doc_type == "license":
                if parsed_data.get('license_expiry'):
                    parsed_data['license_expiry_jp'] = self._format_date_japanese(parsed_data['license_expiry'])
                if parsed_data.get('issue_date'):
                    parsed_data['issue_date_jp'] = self._format_date_japanese(parsed_data['issue_date'])
                if parsed_data.get('birthday') and not parsed_data.get('age'):
                    parsed_data['age'] = self._calculate_age(parsed_data['birthday'])
            else:
                if parsed_data.get('visa_expiry'):
                    parsed_data['visa_expiry_jp'] = self._format_date_japanese(parsed_data['visa_expiry'])
                if parsed_data.get('issue_date'):
                    parsed_data['issue_date_jp'] = self._format_date_japanese(parsed_data['issue_date'])

            logger.info(f"Gemini API success: {parsed_data}")
            return parsed_data

        except TimeoutException as e:
            logger.error(f"Gemini API timeout: {e}")
            return {}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {}



    
    def extract_text_with_gemini_api_from_base64(
        self,
        base64_image: str,
        mime_type: str,
        document_type: str = "zairyu_card"
    ) -> Dict:
        """Extract structured data from base64 image using Gemini API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={self.gemini_api_key}"
    
            doc_type = (document_type or "zairyu_card").lower()
            if doc_type == "license_card":
                doc_type = "license"
    
            if doc_type == "license":
                schema = {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING", "description": "氏名"},
                        "name_kana": {"type": "STRING", "description": "フリガナ"},
                        "birthday": {"type": "STRING", "description": "生年月日 YYYY-MM-DD"},
                        "age": {"type": "INTEGER", "description": "Age calculated from birthday"},
                        "gender": {"type": "STRING", "description": "性別"},
                        "address": {"type": "STRING", "description": "住所"},
                        "postal_code": {"type": "STRING", "description": "郵便番号"},
                        "license_number": {"type": "STRING", "description": "免許証番号"},
                        "license_expiry": {"type": "STRING", "description": "有効期限 YYYY-MM-DD"},
                        "issue_date": {"type": "STRING", "description": "交付年月日 YYYY-MM-DD"},
                        "license_type": {"type": "STRING", "description": "免許種類"},
                        "license_conditions": {"type": "STRING", "description": "条件等"}
                    }
                }
    
                instruction_text = (
                    "Extract the following data from this Japanese driver's license (運転免許証): "
                    "name, name_kana, birthday (YYYY-MM-DD), age, gender, address, postal_code, "
                    "license_number, license_expiry (YYYY-MM-DD), issue_date (YYYY-MM-DD), license_type, "
                    "and license_conditions."
                )
            else:
                schema = {
                    "type": "OBJECT",
                    "properties": {
                        "name": {"type": "STRING", "description": "Full name from 氏名/NAME field"},
                        "name_kana": {"type": "STRING", "description": "Name in Katakana/Hiragana if available"},
                        "birthday": {"type": "STRING", "description": "Date of birth in YYYY-MM-DD format from 生年月日"},
                        "age": {"type": "INTEGER", "description": "Age calculated from birthday"},
                        "address": {"type": "STRING", "description": "Residential address from 住所"},
                        "gender": {"type": "STRING", "description": "Gender: 男性 or 女性 from 性別/SEX field"},
                        "nationality": {"type": "STRING", "description": "Nationality in Japanese from 国籍/NATIONALITY"},
                        "card_number": {"type": "STRING", "description": "Card number from 番号/NUMBER"},
                        "visa_type": {"type": "STRING", "description": "Visa status from 在留資格/STATUS field"},
                        "visa_period": {"type": "STRING", "description": "Visa period (在留期間)"},
                        "visa_expiry": {"type": "STRING", "description": "Expiry date in YYYY-MM-DD format"},
                        "issue_date": {"type": "STRING", "description": "Card issue date in YYYY-MM-DD format"},
                        "region": {"type": "STRING", "description": "Region/Zone (地域)"},
                        "permission_date": {"type": "STRING", "description": "Permission date (許可年月日)"},
                        "authorized_activity": {"type": "STRING", "description": "Authorized activity (就労活動の許可)"},
                        "employer_restriction": {"type": "STRING", "description": "Employer restriction (指定書就職活動の範囲)"},
                        "passport_number": {"type": "STRING", "description": "Passport number if visible"},
                        "passport_expiry": {"type": "STRING", "description": "Passport expiry date if visible"},
                        "postal_code": {"type": "STRING", "description": "Postal code from address"},
                        "photo": {"type": "STRING", "description": "Face photo as base64 string"}
                    }
                }
    
                instruction_text = (
                    "Extract all structured data from this Japanese Residence Card (在留カード) including name, name_kana, birthday "
                    "(YYYY-MM-DD), age, address, gender, nationality, card_number, visa_type, visa_period, visa_expiry "
                    "(YYYY-MM-DD), issue_date (YYYY-MM-DD), region, permission_date, authorized_activity, employer_restriction, "
                    "passport_number, passport_expiry, postal_code, and provide the face photo as a base64 string. Return only JSON."
                )
    
            payload = {
                "contents": [{
                    "parts": [{
                        "text": instruction_text
                    }, {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64_image
                        }
                    }]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "responseSchema": schema,
                    "temperature": 0.1
                }
            }
    
            response = self._make_request_with_timeout(url, payload)
    
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code}")
                return {}
    
            result = response.json()
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')
    
            if not text_content:
                logger.warning("Gemini API returned empty content")
                return {}
    
            parsed_data = json.loads(text_content)
    
            if parsed_data.get('birthday') and not parsed_data.get('age'):
                parsed_data['age'] = self._calculate_age(parsed_data['birthday'])
    
            if parsed_data.get('birthday'):
                parsed_data['birthday_jp'] = self._format_date_japanese(parsed_data['birthday'])
    
            if doc_type == "license":
                if parsed_data.get('license_expiry'):
                    parsed_data['license_expiry_jp'] = self._format_date_japanese(parsed_data['license_expiry'])
                if parsed_data.get('issue_date'):
                    parsed_data['issue_date_jp'] = self._format_date_japanese(parsed_data['issue_date'])
            else:
                if parsed_data.get('visa_expiry'):
                    parsed_data['visa_expiry_jp'] = self._format_date_japanese(parsed_data['visa_expiry'])
                if parsed_data.get('issue_date'):
                    parsed_data['issue_date_jp'] = self._format_date_japanese(parsed_data['issue_date'])
    
            return parsed_data
    
        except TimeoutException as e:
            logger.error(f"Gemini API timeout: {e}")
            return {}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {}

    def extract_text_with_vision_api(self, image_path: str) -> str:
        """Extract text using Google Cloud Vision API"""
        try:
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.vision_api_key}"

            payload = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "imageContext": {"languageHints": ["ja", "en"]}
                }]
            }

            response = self._make_request_with_timeout(url, payload)
            
            if response.status_code != 200:
                logger.error(f"Vision API error: {response.status_code}")
                return ""

            result = response.json()
            
            if 'responses' in result and len(result['responses']) > 0:
                if 'fullTextAnnotation' in result['responses'][0]:
                    text = result['responses'][0]['fullTextAnnotation']['text']
                    logger.info(f"Vision API extracted {len(text)} characters")
                    return text

            return ""

        except TimeoutException as e:
            logger.error(f"Vision API timeout: {e}")
            return ""
        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return ""
    
    def extract_text_with_tesseract(self, image_path: str) -> str:
        """Extract text using Tesseract OCR (offline fallback)"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return ""

            # Preprocessing
            scale = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(scale, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)

            config = '--oem 3 --psm 11'
            text = pytesseract.image_to_string(enhanced, lang='jpn+eng', config=config)
            logger.info(f"Tesseract extracted {len(text)} characters")
            return text

        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return ""
    
    def parse_zairyu_card(self, text: str) -> Dict:
        """Parse Zairyu Card text and extract structured data"""
        data = {
            "card_number": None,
            "name": "",
            "name_kana": "",
            "nationality": None,
            "birthday": None,
            "age": None,
            "gender": None,
            "address": None,
            "postal_code": None,
            "visa_type": None,
            "visa_period": None,
            "visa_expiry": None,
            "issue_date": None,
            "region": None,
            "permission_date": None,
            "authorized_activity": None,
            "employer_restriction": None,
            "passport_number": None,
            "passport_expiry": None
        }

        # Normalizar espacios para facilitar las expresiones regulares
        normalized = text.replace('\n', ' ').replace('　', ' ')
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Mantener una versión sin normalizar para casos extremos
        raw_text = text

        # Card Number
        card_patterns = [
            r'在留カード番号[:：]?\s*([A-Z]{2}\s*\d{6}\s*[A-Z]{2})',
            r'Card\s*No\.?[:：]?\s*([A-Z]{2}\s*\d{6}\s*[A-Z]{2})',
            r'番号[:：]?\s*([A-Z]{2}\s*\d{6}\s*[A-Z]{2})',
            r'([A-Z]{2}\s*\d{8}\s*[A-Z]{2})'
        ]
        for pattern in card_patterns:
            match = re.search(pattern, normalized, flags=re.IGNORECASE)
            if match:
                data["card_number"] = re.sub(r'\s', '', match.group(1)).upper()
                break

        # Name
        name_patterns = [
            r'氏\s*名(?!カナ|フリガナ)[:：]?\s*([^\s]+(?:\s+[^\s]+)*)',
            r'NAME[:：]?\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            r'Name[:：]?\s*([A-Za-z]+(?:\s+[A-Za-z]+)*)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, normalized)
            if match:
                data["name"] = match.group(1).strip()
                break

        if not data["name"]:
            # Fallback al texto original por si los espacios dobles fueron relevantes
            match = re.search(r'氏\s*名(?!カナ|フリガナ)[^\w\n]*([\S]+(?:\s+[\S]+)*)', raw_text)
            if match:
                data["name"] = ' '.join(match.group(1).split())

        # Name Kana
        kana_patterns = [
            r'氏\s*名\s*(?:カナ|フリガナ)[:：]?\s*([ァ-ンヴー\s]+)',
            r'(?:フリガナ|カナ)[:：]?\s*([ァ-ンヴー\s]+)'
        ]
        for pattern in kana_patterns:
            match = re.search(pattern, normalized)
            if match:
                data["name_kana"] = match.group(1).strip()
                break

        # Birthday
        match = re.search(r'生\s*年\s*月\s*日[:：]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if not match:
            match = re.search(r'(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if match:
            year, month, day = match.groups()
            data["birthday"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # Calculate age
            data["age"] = self._calculate_age(data["birthday"])

        # Gender
        match = re.search(r'性\s*別[:：]?\s*(男|女)', normalized)
        if match:
            data["gender"] = '男性' if match.group(1) == '男' else '女性'
        else:
            match = re.search(r'Sex[:：]?\s*(Male|Female)', normalized, flags=re.IGNORECASE)
            if match:
                data["gender"] = '男性' if match.group(1).lower() == 'male' else '女性'

        # Nationality
        match = re.search(r'国籍・地域[:：]?\s*([^\s]+)', normalized)
        if match:
            data["nationality"] = match.group(1).strip()
        else:
            match = re.search(r'Nationality[:：]?\s*([A-Za-z\s]+)', normalized)
            if match:
                data["nationality"] = match.group(1).strip()

        # Postal Code
        match = re.search(r'〒\s*(\d{3}-?\d{4})', normalized)
        if match:
            code = match.group(1).replace('-', '')
            if len(code) == 7:
                data["postal_code"] = f"{code[:3]}-{code[3:]}"

        # Address
        match = re.search(r'住\s*所[:：]?\s*([^\s]+(?:\s+[^\s]+)*?)(?=\s*在留資格)', normalized)
        if match:
            data["address"] = match.group(1).strip()
        else:
            match = re.search(r'Address[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
            if match:
                data["address"] = match.group(1).strip()

        # Visa Type
        match = re.search(r'在留資格[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["visa_type"] = match.group(1).strip()

        # Visa Period
        match = re.search(r'在留期間[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["visa_period"] = match.group(1).strip()

        # Visa Expiry
        match = re.search(r'在留期間.*?(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if match:
            year, month, day = match.groups()
            data["visa_expiry"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Issue Date
        match = re.search(r'有効期間開始[:：]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if match:
            year, month, day = match.groups()
            data["issue_date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Region
        match = re.search(r'地域[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["region"] = match.group(1).strip()

        # Permission Date
        match = re.search(r'許可年月日[:：]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if match:
            year, month, day = match.groups()
            data["permission_date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Authorized Activity
        match = re.search(r'就労活動の許可[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["authorized_activity"] = match.group(1).strip()

        # Employer Restriction
        match = re.search(r'指定書就職活動の範囲[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["employer_restriction"] = match.group(1).strip()

        # Passport Number (if visible)
        match = re.search(r'旅\s*行\s*番\s*号[:：]?\s*([A-Z0-9]+)', normalized)
        if match:
            data["passport_number"] = match.group(1).strip()
        else:
            match = re.search(r'Passport\s*No\.?[:：]?\s*([A-Z0-9]+)', normalized, flags=re.IGNORECASE)
            if match:
                data["passport_number"] = match.group(1).strip().upper()

        # Passport Expiry (if visible)
        match = re.search(r'旅\s*行\s*期\s*限[:：]?\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日', normalized)
        if match:
            year, month, day = match.groups()
            data["passport_expiry"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            match = re.search(r'Passport\s*Expiry[:：]?\s*(\d{4})[./-](\d{1,2})[./-](\d{1,2})', normalized, flags=re.IGNORECASE)
            if match:
                year, month, day = match.groups()
                data["passport_expiry"] = f"{int(year):04d}-{int(month):02d}-{int(day):02d}"

        return data

    def parse_license_card(self, text: str) -> Dict:
        """Parse Japanese driver's license text and extract structured data"""
        data = {
            "license_number": None,
            "name": "",
            "name_kana": "",
            "birthday": None,
            "age": None,
            "gender": None,
            "address": None,
            "postal_code": None,
            "issue_date": None,
            "license_expiry": None,
            "license_type": None,
            "license_conditions": None
        }

        normalized = text.replace('\n', ' ').replace('　', ' ')
        normalized = re.sub(r'\s+', ' ', normalized)

        # License number (12 digits)
        number_patterns = [
            r'免許証番号[:：]?\s*(\d{12})',
            r'番号[:：]?\s*(\d{12})',
            r'第\s*(\d{12})\s*号',
            r'\b(\d{12})\b'
        ]
        for pattern in number_patterns:
            match = re.search(pattern, normalized)
            if match:
                data["license_number"] = match.group(1)
                break

        # Name (Kanji/Latin)
        match = re.search(r'氏名\s*[:：]?\s*([^\s]+(?:\s+[^\s]+){0,3})', normalized)
        if match:
            data["name"] = match.group(1).strip()

        # Name Kana / Furigana
        match = re.search(r'(氏名カナ|氏名フリガナ|フリガナ|カナ)\s*[:：]?\s*([ァ-ンヴー\s]+)', normalized)
        if match:
            data["name_kana"] = match.group(2).strip()

        # Birthday (supports Japanese era)
        match = re.search(r'生年月日\s*[:：]?\s*([^\s]+(?:\s+[^\s]+){0,3})', normalized)
        if match:
            birthday = self._parse_japanese_date(match.group(1))
            if birthday:
                data["birthday"] = birthday
                data["age"] = self._calculate_age(birthday)

        # Gender
        match = re.search(r'性別\s*[:：]?\s*(男|女)', normalized)
        if match:
            data["gender"] = '男性' if match.group(1) == '男' else '女性'

        # Postal code
        match = re.search(r'〒\s*(\d{3}-?\d{4})', normalized)
        if match:
            code = match.group(1).replace('-', '')
            if len(code) == 7:
                data["postal_code"] = f"{code[:3]}-{code[3:]}"

        # Address (until next major field)
        match = re.search(r'住所\s*[:：]?\s*([^\s]+(?:\s+[^\s]+)*?)(?=\s*(有効期限|交付|第\s*\d|運転免許|条件等))', normalized)
        if match:
            data["address"] = match.group(1).strip()

        # Issue date
        match = re.search(r'(交付|交付年月日)\s*[:：]?\s*([^\s]+(?:\s+[^\s]+){0,3})', normalized)
        if match:
            issue_date = self._parse_japanese_date(match.group(2))
            if issue_date:
                data["issue_date"] = issue_date

        # Expiry date
        match = re.search(r'有効期限\s*[:：]?\s*([^\s]+(?:\s+[^\s]+){0,3})', normalized)
        if match:
            expiry = self._parse_japanese_date(match.group(1))
            if expiry:
                data["license_expiry"] = expiry

        # License conditions
        match = re.search(r'条件等\s*[:：]?\s*([^\s]+(?:\s+[^\s]+)*)', normalized)
        if match:
            data["license_conditions"] = match.group(1).strip()

        # License class/type detection
        class_keywords = [
            ('大型二輪', '大型二輪'),
            ('普通二輪', '普通二輪'),
            ('大型特殊', '大型特殊'),
            ('準中型', '準中型免許'),
            ('大型', '大型免許'),
            ('中型', '中型免許'),
            ('普通', '普通免許'),
            ('原付', '原付免許')
        ]

        detected_classes: List[str] = []
        for keyword, label in class_keywords:
            if keyword in normalized and label not in detected_classes:
                detected_classes.append(label)

        if detected_classes:
            data["license_type"] = '・'.join(detected_classes)

        return data

    def extract_face_from_zairyu_card(self, image_path: str) -> Optional[str]:
        """Extract face photo from Zairyu Card using face detection"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Usar la ruta correcta para el clasificador
            try:
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            except AttributeError:
                # Si cv2.data no está disponible, intentar ruta alternativa
                import pkg_resources
                cascade_path = pkg_resources.resource_filename('cv2', 'data/haarcascade_frontalface_default.xml')
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                # Fallback to typical position
                height, width = img.shape[:2]
                x, y = int(width * 0.7), int(height * 0.1)
                w, h = int(width * 0.25), int(height * 0.35)
                face_img = img[y:y+h, x:x+w]
            else:
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                padding = 60
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2*padding)
                h = min(img.shape[0] - y, h + 2*padding)
                face_img = img[y:y+h, x:x+w]

            face_img = cv2.resize(face_img, (150, 180))
            _, buffer = cv2.imencode('.jpg', face_img)
            face_base64 = base64.b64encode(buffer).decode('utf-8')

            return f"data:image/jpeg;base64,{face_base64}"

        except Exception as e:
            logger.error(f"Face extraction error: {e}")
            return None
    
    def process_zairyu_card_hybrid(self, image_path: str, document_type: str = "zairyu_card") -> Dict:
        """
        Process Zairyu Card using hybrid approach:
        1. Try Gemini API (fastest, best accuracy)
        2. Fallback to Vision API
        3. Fallback to Tesseract (offline)
        """
        doc_type = (document_type or "zairyu_card").lower()
        if doc_type == "license_card":
            doc_type = "license"

        # Check cache first
        image_hash = self._get_image_hash(image_path)
        cached = self._load_cache(image_hash)
        if cached:
            logger.info("Using cached OCR result")
            return cached

        results = []

        parser = self.parse_license_card if doc_type == "license" else self.parse_zairyu_card

        # Method 1: Gemini API
        if self.gemini_api_key and self.gemini_api_key != 'YOUR_API_KEY_HERE':
            try:
                logger.info("Intentando Gemini API...")
                gemini_result = self.extract_text_with_gemini_api(image_path, document_type=doc_type)
                if self._validate_result(gemini_result, doc_type):
                    results.append(('gemini', gemini_result, 100))
                    logger.info("Gemini API succeeded")
                else:
                    logger.warning("Gemini API returned invalid result")
            except TimeoutException:
                logger.warning("Gemini API timed out")
            except Exception as e:
                logger.warning(f"Gemini failed: {e}")

        # Method 2: Vision API
        if self.vision_api_key and self.vision_api_key != 'YOUR_API_KEY_HERE' and not results:
            try:
                logger.info("Intentando Vision API...")
                vision_text = self.extract_text_with_vision_api(image_path)
                if vision_text:
                    vision_result = parser(vision_text)
                    if self._validate_result(vision_result, doc_type):
                        results.append(('vision', vision_result, 80))
                        logger.info("Vision API succeeded")
            except TimeoutException:
                logger.warning("Vision API timed out")
            except Exception as e:
                logger.warning(f"Vision API failed: {e}")

        # Method 3: Tesseract (always available, offline)
        if not results:
            try:
                logger.info("Intentando Tesseract OCR...")
                tesseract_text = self.extract_text_with_tesseract(image_path)
                if tesseract_text:
                    tesseract_result = parser(tesseract_text)
                    if self._validate_result(tesseract_result, doc_type):
                        results.append(('tesseract', tesseract_result, 60))
                        logger.info("Tesseract succeeded")
            except Exception as e:
                logger.warning(f"Tesseract failed: {e}")

        if not results:
            logger.error("Todos los métodos OCR fallaron")
            # Devolver resultado vacío en lugar de lanzar excepción
            return {
                "error": "Todos los métodos OCR fallaron",
                "ocr_method": "none",
                "confidence": 0,
                "processed_at": datetime.now().isoformat()
            }

        # Select best result
        best_method, best_result, confidence = max(results, key=lambda x: x[2])

        if doc_type != "license":
            face_photo = self.extract_face_from_zairyu_card(image_path)
            if face_photo:
                best_result['photo'] = face_photo

        if best_result.get('birthday') and not best_result.get('age'):
            best_result['age'] = self._calculate_age(best_result['birthday'])
        if best_result.get('birthday'):
            best_result['birthday_jp'] = self._format_date_japanese(best_result['birthday'])
        if best_result.get('issue_date'):
            best_result['issue_date_jp'] = self._format_date_japanese(best_result['issue_date'])
        if doc_type == "license" and best_result.get('license_expiry'):
            best_result['license_expiry_jp'] = self._format_date_japanese(best_result['license_expiry'])
        if doc_type == "zairyu_card" and best_result.get('visa_expiry'):
            best_result['visa_expiry_jp'] = self._format_date_japanese(best_result['visa_expiry'])

        # Add metadata
        best_result['ocr_method'] = best_method
        best_result['confidence'] = confidence
        best_result['processed_at'] = datetime.now().isoformat()
        best_result['document_type'] = doc_type

        # Cache result
        self._save_cache(image_hash, best_result)

        logger.info(f"OCR complete using {best_method} (confidence: {confidence}%)")
        return best_result

    def process_document(self, file_path: str, document_type: str) -> Dict:
        """Main method to process any document type"""
        doc_type = (document_type or "zairyu_card").lower()
        if doc_type == "license_card":
            doc_type = "license"

        logger.info(f"Processing document: {file_path}, type: {doc_type}")

        if doc_type in {"zairyu_card", "license"}:
            return self.process_zairyu_card_hybrid(file_path, document_type=doc_type)
        
        # For other document types, use basic OCR
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            # Convert PDF to images and process
            images = convert_from_path(file_path)
            all_text = []
            for img in images:
                temp_path = "/tmp/temp_ocr_image.jpg"
                img.save(temp_path)
                text = self.extract_text_with_tesseract(temp_path)
                all_text.append(text)
                os.remove(temp_path)
            return {"raw_text": "\n".join(all_text)}
        else:
            text = self.extract_text_with_tesseract(file_path)
            return {"raw_text": text}


# Global instance
ocr_service_fixed = OCRService()
