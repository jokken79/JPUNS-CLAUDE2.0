"""
OCR Service Optimizado para UNS-ClaudeJP 2.0
Sistema híbrido acelerado: Gemini + Vision API + Tesseract con procesamiento paralelo
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import re
from typing import Dict, Optional, List, Tuple, Union, Any
import os
from datetime import datetime
import base64
import requests
import logging
import hashlib
import json
from pathlib import Path
import asyncio
import concurrent.futures
from io import BytesIO
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(settings.UPLOAD_DIR) / "ocr_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Constantes de optimización
MAX_IMAGE_SIZE = 1600  # Tamaño máximo para cualquier dimensión
OCR_TIMEOUT = 60  # Tiempo máximo para OCR en segundos


class OptimizedOCRService:
    """Service for OCR processing with hybrid approach, parallel execution, and optimized preprocessing"""
    
    def __init__(self):
        self.tesseract_lang = settings.TESSERACT_LANG
        self.vision_api_key = settings.GOOGLE_CLOUD_VISION_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.cache = {}
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        
        # Performance monitoring
        self.total_requests = 0
        self.cache_hits = 0
        self.average_processing_time = 0
        
        # Cargar caché a memoria para acceso más rápido
        self._preload_cache_to_memory()
    
    def _preload_cache_to_memory(self):
        """Preload cache files to memory for faster access"""
        try:
            cache_files = list(CACHE_DIR.glob("*.json"))
            logger.info(f"Preloading {len(cache_files)} cache entries to memory")
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        image_hash = cache_file.stem
                        self.cache[image_hash] = json.load(f)
                except Exception as e:
                    logger.warning(f"Error loading cache file {cache_file}: {e}")
            
            logger.info(f"Preloaded {len(self.cache)} cache entries")
        except Exception as e:
            logger.error(f"Error preloading cache: {e}")
    
    def _get_image_hash(self, image_path: str) -> str:
        """Generate MD5 hash of image for caching"""
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_cache(self, image_hash: str) -> Optional[Dict]:
        """Load cached OCR result from memory first, then file if not found"""
        # Primero buscar en memoria
        if image_hash in self.cache:
            self.cache_hits += 1
            return self.cache[image_hash]
        
        # Luego buscar en archivo
        cache_file = CACHE_DIR / f"{image_hash}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                result = json.load(f)
                # Actualizar caché en memoria
                self.cache[image_hash] = result
                self.cache_hits += 1
                return result
        return None
    
    def _save_cache(self, image_hash: str, data: Dict):
        """Save OCR result to both memory and file cache"""
        # Guardar en memoria
        self.cache[image_hash] = data
        
        # Guardar en archivo
        cache_file = CACHE_DIR / f"{image_hash}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _validate_result(self, result: Dict) -> bool:
        """Validate that result has minimum required data"""
        if not result:
            return False
        return bool(result.get('name') and (result.get('birthday') or result.get('address')))
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics for monitoring"""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{(self.cache_hits / max(1, self.total_requests)) * 100:.2f}%",
            "cache_entries": len(self.cache),
            "average_processing_time": f"{self.average_processing_time:.2f}s",
            "cache_size_on_disk": f"{sum(os.path.getsize(f) for f in CACHE_DIR.glob('*.json')) / (1024*1024):.2f} MB"
        }
    
    def clear_cache(self) -> Dict:
        """Clear all cache entries"""
        try:
            # Limpiar caché en memoria
            self.cache = {}
            
            # Limpiar archivos de caché
            cache_files = list(CACHE_DIR.glob("*.json"))
            for f in cache_files:
                os.unlink(f)
            
            return {
                "success": True, 
                "message": f"Cleared {len(cache_files)} cache entries"
            }
        except Exception as e:
            return {"success": False, "message": f"Error clearing cache: {e}"}
    
    def optimize_image(self, image_path: str) -> str:
        """
        Optimize image for OCR processing:
        1. Resize if too large
        2. Enhance contrast
        3. Remove noise
        Returns path to optimized image
        """
        try:
            img = Image.open(image_path)
            
            # Comprobar si la imagen necesita redimensionarse
            width, height = img.size
            if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
                if width > height:
                    new_width = MAX_IMAGE_SIZE
                    new_height = int(height * (MAX_IMAGE_SIZE / width))
                else:
                    new_height = MAX_IMAGE_SIZE
                    new_width = int(width * (MAX_IMAGE_SIZE / height))
                
                # Redimensionar con alta calidad
                img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Guardar imagen optimizada como PNG para mantener calidad
            img_numpy = np.array(img)
            
            # Convertir a OpenCV para procesamiento
            if len(img_numpy.shape) == 3 and img_numpy.shape[2] == 3:
                # Imagen RGB
                img_cv = cv2.cvtColor(img_numpy, cv2.COLOR_RGB2BGR)
            elif len(img_numpy.shape) == 2:
                # Ya es escala de grises
                img_cv = img_numpy
            else:
                # RGBA o algún otro formato, convertir a BGR
                img_cv = cv2.cvtColor(img_numpy, cv2.COLOR_RGBA2BGR)
            
            # Mejorar el contraste con CLAHE
            if len(img_cv.shape) == 3:
                img_gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                img_gray = img_cv
                
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(img_gray)
            
            # Reducir ruido
            denoised = cv2.fastNlMeansDenoising(enhanced, None, 10, 7, 21)
            
            # Guardar imagen optimizada
            temp_path = f"{os.path.splitext(image_path)[0]}_optimized.png"
            cv2.imwrite(temp_path, denoised)
            
            return temp_path
        
        except Exception as e:
            logger.error(f"Error optimizing image: {e}")
            return image_path  # Si hay error, devolver la imagen original
    
    def extract_text_with_gemini_api(self, image_path: str, timeout: int = 30) -> Dict:
        """
        Extract structured data from image using Gemini API
        Returns dict with name, birthday, address, gender, nationality, etc.
        """
        try:
            # Optimizar imagen para reducir tamaño
            start_time = time.time()
            logger.info(f"Extracting text with Gemini API from {image_path}")
            
            # Verificar que tenemos una API key válida
            if not self.gemini_api_key or self.gemini_api_key == 'YOUR_API_KEY_HERE':
                logger.warning("Gemini API key not configured")
                return {}
            
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                
                # Verificar si la imagen es muy grande y comprimir si es necesario
                if len(image_content) > 1024 * 1024:  # Si es mayor a 1MB
                    img = Image.open(BytesIO(image_content))
                    output = BytesIO()
                    
                    # Comprimir con calidad progresivamente menor hasta llegar a un tamaño aceptable
                    quality = 85
                    max_size = 700 * 1024  # 700KB máximo para la API
                    
                    while len(output.getvalue()) > max_size and quality > 50:
                        output = BytesIO()
                        img.save(output, format='JPEG', quality=quality)
                        quality -= 10
                    
                    image_content = output.getvalue()
                
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={self.gemini_api_key}"

            schema = {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "description": "Full name in Japanese (Kanji/Kana) or Latin characters"},
                    "birthday": {"type": "STRING", "description": "Date of birth in YYYY-MM-DD format"},
                    "address": {"type": "STRING", "description": "Residential address in Japanese"},
                    "gender": {"type": "STRING", "description": "Gender: 男性 or 女性"},
                    "nationality": {"type": "STRING", "description": "Nationality in Japanese"},
                    "card_number": {"type": "STRING", "description": "Residence card number"},
                    "visa_type": {"type": "STRING", "description": "Visa status"},
                    "visa_expiry": {"type": "STRING", "description": "Card expiry date in YYYY-MM-DD format"}
                }
            }

            payload = {
                "contents": [{
                    "parts": [{
                        "text": """Extract information from this Japanese Residence Card (在留カード):
                        - name (氏名/NAME): Full name
                        - birthday (生年月日): Date in YYYY-MM-DD format
                        - address (住所): Full address
                        - gender (性別/SEX): 男性 or 女性
                        - nationality (国籍/NATIONALITY): Country in Japanese
                        - card_number (番号/NUMBER): Card number
                        - visa_type (在留資格/STATUS): Residence status
                        - visa_expiry: Expiry date in YYYY-MM-DD format
                        
                        If any field is not visible or unclear, leave it empty.
                        Return NULL for fields not found in the image."""
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

            logger.info("Calling Gemini API...")
            # Reducir timeout para evitar que se quede atascado
            response = requests.post(url, json=payload, timeout=timeout)

            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code}")
                return {}

            result = response.json()
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

            if not text_content:
                logger.warning("Gemini API returned empty content")
                return {}

            parsed_data = json.loads(text_content)
            logger.info(f"Gemini API success in {time.time() - start_time:.2f}s")
            return parsed_data

        except requests.exceptions.Timeout:
            logger.error(f"Gemini API timeout after {timeout}s")
            return {}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {}

    def extract_text_with_vision_api(self, image_path: str, timeout: int = OCR_TIMEOUT) -> str:
        """Extract text using Google Cloud Vision API with optimized image"""
        try:
            # Optimizar imagen para API
            start_time = time.time()
            logger.info(f"Extracting text with Vision API from {image_path}")
            
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                
                # Comprimir si es necesario
                if len(image_content) > 1024 * 1024:  # Si es mayor a 1MB
                    img = Image.open(BytesIO(image_content))
                    output = BytesIO()
                    img.save(output, format='JPEG', quality=85, optimize=True)
                    image_content = output.getvalue()
                
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.vision_api_key}"

            payload = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "imageContext": {"languageHints": ["ja", "en"]}
                }]
            }

            response = requests.post(url, json=payload, timeout=timeout)

            if response.status_code != 200:
                logger.error(f"Vision API error: {response.status_code}")
                return ""

            result = response.json()
            
            if 'responses' in result and len(result['responses']) > 0:
                if 'fullTextAnnotation' in result['responses'][0]:
                    text = result['responses'][0]['fullTextAnnotation']['text']
                    logger.info(f"Vision API extracted {len(text)} characters in {time.time() - start_time:.2f}s")
                    return text

            return ""

        except Exception as e:
            logger.error(f"Vision API error: {e}")
            return ""
    
    def extract_text_with_tesseract_multi(self, image_path: str, timeout: int = OCR_TIMEOUT) -> str:
        """Extract text using Tesseract OCR with multiple strategies in parallel"""
        try:
            start_time = time.time()
            logger.info(f"Extracting text with Tesseract (multi-strategy) from {image_path}")
            
            # Preprocesar la imagen
            img = cv2.imread(image_path)
            if img is None:
                return ""
            
            # Lista de estrategias de preprocesamiento
            preprocessing_strategies = []
            
            # Estrategia 1: Escalado 2x + CLAHE
            scaled_img = cv2.resize(img, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_LANCZOS4)
            gray = cv2.cvtColor(scaled_img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            preprocessing_strategies.append(enhanced)
            
            # Estrategia 2: Binarización con umbral adaptativo
            binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
            preprocessing_strategies.append(binary)
            
            # Estrategia 3: Desenfoque para reducir ruido
            blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
            preprocessing_strategies.append(blurred)
            
            # Modos PSM de Tesseract (Page Segmentation Modes)
            psm_modes = [3, 6, 11]  # Modos más efectivos para documentos
            
            # Ejecutar múltiples combinaciones en paralelo
            results = []
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                # Crear tareas para cada combinación de estrategia y PSM
                for img_processed in preprocessing_strategies:
                    for psm in psm_modes:
                        config = f'--oem 3 --psm {psm} -c preserve_interword_spaces=1'
                        
                        # Crear futuro
                        future = executor.submit(
                            pytesseract.image_to_string,
                            img_processed,
                            lang='jpn+eng',
                            config=config,
                            timeout=timeout
                        )
                        
                        futures.append(future)
                
                # Recoger resultados a medida que se completan
                for future in concurrent.futures.as_completed(futures):
                    try:
                        text = future.result()
                        
                        # Evaluar calidad del texto extraído
                        meaningful_chars = len(re.findall(r'[a-zA-Z一-龯ぁ-んァ-ヶー0-9]', text))
                        results.append((text, meaningful_chars))
                    except Exception as e:
                        logger.warning(f"Tesseract thread error: {e}")
            
            # Seleccionar el mejor resultado (con más caracteres significativos)
            if not results:
                logger.warning("No valid Tesseract results")
                return ""
                
            best_text = max(results, key=lambda x: x[1])[0]
            logger.info(f"Tesseract extracted {len(best_text)} characters in {time.time() - start_time:.2f}s")
            return best_text

        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return ""
    
    def parse_zairyu_card(self, text: str) -> Dict:
        """Parse Zairyu Card text with improved pattern matching"""
        data = {
            "card_number": None,
            "name": "",
            "nationality": None,
            "birthday": None,
            "gender": None,
            "address": None,
            "visa_type": None,
            "visa_expiry": None
        }

        # Normalizar espacios
        text = re.sub(r'\s+', ' ', text)
        text = text.replace('　', ' ')

        # Card Number (patrón mejorado)
        card_patterns = [
            r'([A-Z]{2}\s*\d{8}\s*[A-Z]{2})',  # Formato estándar
            r'番号\s*[:：]?\s*([A-Z]{2}\s*\d{8}\s*[A-Z]{2})',  # Con etiqueta 番号
            r'NUMBER\s*[:：]?\s*([A-Z]{2}\s*\d{8}\s*[A-Z]{2})'  # Con etiqueta en inglés
        ]
        
        for pattern in card_patterns:
            match = re.search(pattern, text)
            if match:
                data["card_number"] = re.sub(r'\s', '', match.group(1))
                break

        # Name (múltiples patrones)
        name_patterns = [
            r'氏\s*名\s*[:：]?\s*([^\s]{2,20}(?:\s+[^\s]+){0,3})',  # 氏名
            r'NAME\s*[:：]?\s*([^\s]{2,20}(?:\s+[^\s]+){0,3})',  # NAME en inglés
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})',  # Nombres occidentales (capitalización)
            r'([一-龯ぁ-んァ-ヶー]{2,}(?:\s*[一-龯ぁ-んァ-ヶー]+){0,3})'  # Caracteres japoneses
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text)
            if match:
                data["name"] = match.group(1).strip()
                break

        # Birthday (formatos múltiples)
        birthday_patterns = [
            r'生年月日\s*[:：]?\s*(\d{4})[\s年\./-]+(\d{1,2})[\s月\./-]+(\d{1,2})',  # Formato japonés
            r'生年月日\s*[:：]?\s*(\d{1,2})[\s月\./-]+(\d{1,2})[\s日\./-]+(\d{4})',  # Invertido
            r'DATE OF BIRTH\s*[:：]?\s*(\d{4})[\s\./-]+(\d{1,2})[\s\./-]+(\d{1,2})',  # Inglés
            r'(\d{4})[\s年\./-]+(\d{1,2})[\s月\./-]+(\d{1,2})[\s日]'  # Sólo fechas
        ]
        
        for pattern in birthday_patterns:
            match = re.search(pattern, text)
            if match:
                if int(match.group(3)) > 1900:  # Si el año es el tercer grupo
                    year, month, day = match.group(3), match.group(1), match.group(2)
                else:
                    year, month, day = match.group(1), match.group(2), match.group(3)
                
                # Validar fechas
                try:
                    if 1900 <= int(year) <= 2025 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
                        data["birthday"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    pass
                break

        # Gender
        gender_patterns = [
            r'性\s*別\s*[:：]?\s*(男|女)',  # Japonés
            r'SEX\s*[:：]?\s*(M|F|Male|Female)',  # Inglés
            r'\b(男性|女性)\b'  # Términos completos
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text)
            if match:
                gender = match.group(1)
                if gender in ['男', '男性', 'M', 'Male']:
                    data["gender"] = '男性'
                elif gender in ['女', '女性', 'F', 'Female']:
                    data["gender"] = '女性'
                break

        # Nationality
        nationality_patterns = [
            r'国籍[・]?地域\s*[:：]?\s*([^\s\d]+)',  # Japonés
            r'NATIONALITY\s*[:：]?\s*([^\s\d]+)'  # Inglés
        ]
        
        for pattern in nationality_patterns:
            match = re.search(pattern, text)
            if match:
                data["nationality"] = match.group(1).strip()
                break
        
        # Mapeo de nacionalidades en inglés a japonés
        nationality_map = {
            'VIETNAM': 'ベトナム',
            'CHINA': '中国',
            'PHILIPPINES': 'フィリピン',
            'INDONESIA': 'インドネシア',
            'NEPAL': 'ネパール',
            'BRAZIL': 'ブラジル',
            'PERU': 'ペルー'
        }
        
        # Si se encontró nacionalidad en inglés, intentar mapearla
        if data["nationality"] and data["nationality"].upper() in nationality_map:
            data["nationality"] = nationality_map[data["nationality"].upper()]

        # Address (más complejo)
        address_patterns = [
            r'住\s*所\s*[:：]?\s*([^\n]+?)\s*(?=在留|資格|番号|RESIDENCE|STATUS|NUMBER)',  # Hasta el siguiente campo
            r'ADDRESS\s*[:：]?\s*([^\n]+?)\s*(?=在留|資格|番号|RESIDENCE|STATUS|NUMBER)',  # En inglés
            r'住\s*所\s*[:：]?\s*([^\n]{10,})'  # Al menos 10 caracteres
        ]
        
        for pattern in address_patterns:
            match = re.search(pattern, text)
            if match:
                data["address"] = match.group(1).strip()
                break

        # Visa Type
        visa_patterns = [
            r'在留資格\s*[:：]?\s*([^\s\d]{2,})',  # Japonés
            r'STATUS\s*[:：]?\s*([^\s\d]{2,})',  # Inglés
            r'RESIDENCE STATUS\s*[:：]?\s*([^\s\d]{2,})'  # Completo en inglés
        ]
        
        for pattern in visa_patterns:
            match = re.search(pattern, text)
            if match:
                data["visa_type"] = match.group(1).strip()
                break

        # Visa Expiry
        expiry_patterns = [
            r'在留期間(?:満|期)?[限了]\s*[:：]?\s*(\d{4})[\s年\./-]+(\d{1,2})[\s月\./-]+(\d{1,2})',  # Japonés
            r'EXPIRATION\s*[:：]?\s*(\d{4})[\s\./-]+(\d{1,2})[\s\./-]+(\d{1,2})',  # Inglés
            r'このカード\s*[はの]\s*(\d{4})[\s年\./-]+(\d{1,2})[\s月\./-]+(\d{1,2})[\s日]?\s*まで\s*[有効]'  # Frase japonesa
        ]
        
        for pattern in expiry_patterns:
            match = re.search(pattern, text)
            if match:
                year, month, day = match.group(1), match.group(2), match.group(3)
                # Validar fechas
                try:
                    if 2000 <= int(year) <= 2050 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
                        data["visa_expiry"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                except ValueError:
                    pass
                break

        return data
    
    async def extract_face_from_zairyu_card_async(self, image_path: str) -> Optional[str]:
        """
        Extract face photo from Zairyu Card using face detection
        Async version for parallel processing
        """
        try:
            # Optimizar para ejecución en thread separado
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                self.thread_pool, 
                self._extract_face_from_image,
                image_path
            )
        except Exception as e:
            logger.error(f"Async face extraction error: {e}")
            return None
    
    def _extract_face_from_image(self, image_path: str) -> Optional[str]:
        """Internal method for face extraction (runs in thread)"""
        try:
            start_time = time.time()
            logger.info(f"Extracting face from {image_path}")
            
            img = cv2.imread(image_path)
            if img is None:
                return None

            # Convertir a escala de grises para detección facial
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Usar un detector de caras pre-entrenado (Haar Cascade)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                logger.info("No face detected, using fallback position")
                # Posición típica de la cara en una tarjeta de residencia (esquina superior derecha)
                height, width = img.shape[:2]
                x, y = int(width * 0.7), int(height * 0.1)
                w, h = int(width * 0.25), int(height * 0.35)
                face_img = img[y:y+h, x:x+w]
            else:
                # Seleccionar la cara más grande
                logger.info(f"Detected {len(faces)} faces")
                (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
                
                # Agregar padding para incluir toda la cara
                padding = 60
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2*padding)
                h = min(img.shape[0] - y, h + 2*padding)
                
                face_img = img[y:y+h, x:x+w]

            # Redimensionar al tamaño estándar de fotos de pasaporte
            face_img = cv2.resize(face_img, (150, 180))
            
            # Convertir a base64 para incluir en el resultado
            _, buffer = cv2.imencode('.jpg', face_img)
            face_base64 = base64.b64encode(buffer).decode('utf-8')

            logger.info(f"Face extracted in {time.time() - start_time:.2f}s")
            return f"data:image/jpeg;base64,{face_base64}"

        except Exception as e:
            logger.error(f"Face extraction error: {e}")
            return None
    
    async def process_zairyu_card_parallel(self, image_path: str) -> Dict:
        """
        Process Zairyu Card with parallel execution:
        1. Try all OCR methods simultaneously (Gemini, Vision, Tesseract)
        2. Use the first successful result
        3. Extract face photo in parallel
        """
        try:
            start_total = time.time()
            self.total_requests += 1
            
            # Verificar caché primero
            image_hash = self._get_image_hash(image_path)
            cached = self._load_cache(image_hash)
            if cached:
                logger.info(f"Using cached OCR result (hash: {image_hash[:8]}...)")
                return cached
            
            logger.info(f"Processing zairyu card (parallel): {image_path}")
            
            # Optimizar imagen para mejorar OCR
            optimized_path = self.optimize_image(image_path)
            
            # Iniciar extracción de rostro en paralelo con timeout
            try:
                face_task = asyncio.create_task(
                    self.extract_face_from_zairyu_card_async(optimized_path)
                )
                face_task = asyncio.wait_for(face_task, timeout=30)  # 30s timeout para face extraction
            except asyncio.TimeoutError:
                logger.warning("Face extraction timeout, continuing without photo")
                face_task = None
            
            # Iniciar todas las tareas OCR en paralelo con timeouts
            loop = asyncio.get_event_loop()
            ocr_tasks = []
            
            # Tarea 1: Gemini API (mejor calidad)
            if self.gemini_api_key and self.gemini_api_key != 'YOUR_API_KEY_HERE':
                gemini_task = loop.run_in_executor(
                    self.thread_pool,
                    self.extract_text_with_gemini_api,
                    optimized_path
                )
                ocr_tasks.append(('gemini', gemini_task))
            
            # Tarea 2: Vision API
            if self.vision_api_key and self.vision_api_key != 'YOUR_API_KEY_HERE':
                vision_task = loop.run_in_executor(
                    self.thread_pool,
                    self.extract_text_with_vision_api,
                    optimized_path
                )
                ocr_tasks.append(('vision', vision_task))
            
            # Tarea 3: Tesseract (offline) - siempre disponible
            tesseract_task = loop.run_in_executor(
                self.thread_pool,
                self.extract_text_with_tesseract_multi,
                optimized_path
            )
            ocr_tasks.append(('tesseract', tesseract_task))
            
            # Recopilar resultados con timeout general
            results = []
            raw_texts = []
            
            try:
                # Esperar por cualquier resultado con timeout global
                for task_name, task in ocr_tasks:
                    try:
                        # Timeout individual para cada tarea
                        result = await asyncio.wait_for(task, timeout=45)
                        
                        if task_name == 'gemini':
                            # Gemini ya devuelve datos estructurados
                            if self._validate_result(result):
                                result['ocr_method'] = 'gemini'
                                result['confidence'] = 100
                                results.append(result)
                                logger.info("Gemini API returned valid result")
                                break
                        else:
                            # Vision y Tesseract devuelven texto
                            if result and isinstance(result, str) and len(result) > 50:
                                raw_texts.append((task_name, result))
                                logger.info(f"Raw text extraction successful ({task_name})")
                    
                    except asyncio.TimeoutError:
                        logger.warning(f"{task_name} OCR timeout")
                    except Exception as e:
                        logger.error(f"{task_name} OCR error: {e}")
                
                # Si no hay resultado de Gemini, procesar los textos extraídos
                if not results and raw_texts:
                    for task_name, text in raw_texts:
                        try:
                            parsed_result = self.parse_zairyu_card(text)
                            
                            if self._validate_result(parsed_result):
                                parsed_result['ocr_method'] = task_name
                                parsed_result['confidence'] = 80 if task_name == 'vision' else 60
                                results.append(parsed_result)
                                logger.info(f"Parsed valid result from {task_name}")
                                break
                        except Exception as e:
                            logger.error(f"Error parsing text from {task_name}: {e}")
                
                # Si todavía no hay resultados, crear un resultado básico
                if not results:
                    logger.warning("All OCR methods failed, returning basic result")
                    basic_result = {
                        "name": "",
                        "birthday": "",
                        "address": "",
                        "nationality": "",
                        "gender": "",
                        "card_number": "",
                        "visa_type": "",
                        "visa_expiry": "",
                        "ocr_method": "fallback",
                        "confidence": 0,
                        "error": "No valid OCR results obtained"
                    }
                    
                    # Esperar a que la extracción de rostro termine (si está disponible)
                    if face_task:
                        try:
                            face_photo = await face_task
                            if face_photo:
                                basic_result['photo'] = face_photo
                        except Exception as e:
                            logger.warning(f"Face extraction failed in fallback: {e}")
                    
                    # Agregar metadatos
                    basic_result['processed_at'] = datetime.now().isoformat()
                    
                    # Guardar en caché para no reintentar
                    self._save_cache(image_hash, basic_result)
                    
                    return basic_result
                
                # Obtener el mejor resultado
                best_result = results[0]
                
                # Esperar a que la extracción de rostro termine (si está disponible)
                if face_task:
                    try:
                        face_photo = await face_task
                        if face_photo:
                            best_result['photo'] = face_photo
                    except Exception as e:
                        logger.warning(f"Face extraction failed: {e}")
                
                # Agregar metadatos
                best_result['processed_at'] = datetime.now().isoformat()
                
                # Guardar en caché
                self._save_cache(image_hash, best_result)
                
                # Actualizar tiempo promedio de procesamiento
                elapsed = time.time() - start_total
                self.average_processing_time = (self.average_processing_time * (self.total_requests - 1) + elapsed) / self.total_requests
                
                logger.info(f"OCR complete using {best_result['ocr_method']} in {elapsed:.2f}s (confidence: {best_result['confidence']}%)")
                return best_result
            
            except asyncio.TimeoutError:
                logger.error("Global OCR processing timeout")
                return {
                    "error": "OCR processing timeout",
                    "ocr_method": "timeout",
                    "confidence": 0
                }
        
        except Exception as e:
            logger.error(f"Parallel OCR processing error: {e}")
            return {
                "error": str(e),
                "ocr_method": "error",
                "confidence": 0
            }
    
    async def process_document(self, file_path: str, document_type: str) -> Dict:
        """Main method to process any document type"""
        logger.info(f"Processing document: {file_path}, type: {document_type}")

        if document_type == "zairyu_card" or document_type == "license":
            return await self.process_zairyu_card_parallel(file_path)
        
        # Para otros tipos de documentos, usar OCR básico
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            # Convertir PDF a imágenes y procesar
            loop = asyncio.get_event_loop()
            images = await loop.run_in_executor(
                self.thread_pool,
                convert_from_path,
                file_path
            )
            
            all_text = []
            for img in images:
                temp_path = f"/tmp/temp_ocr_image_{len(all_text)}.jpg"
                img.save(temp_path)
                
                text = await loop.run_in_executor(
                    self.thread_pool,
                    self.extract_text_with_tesseract_multi,
                    temp_path
                )
                
                all_text.append(text)
                try:
                    os.remove(temp_path)
                except:
                    pass
                
            return {"raw_text": "\n".join(all_text)}
        else:
            # Para imágenes, usar Tesseract mejorado
            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(
                self.thread_pool,
                self.extract_text_with_tesseract_multi,
                file_path
            )
            return {"raw_text": text}
    
    async def process_from_base64(self, image_base64: str, mime_type: str, document_type: str) -> Dict:
        """
        Process image from base64 string
        Used by frontend API endpoint
        """
        try:
            # Decodificar base64
            image_data = base64.b64decode(image_base64)
            
            # Guardar en archivo temporal
            temp_path = f"/tmp/ocr_temp_{int(time.time())}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            # Procesar como archivo normal (ahora es asíncrono)
            result = await self.process_document(temp_path, document_type)
            
            # Limpiar archivo temporal
            try:
                os.remove(temp_path)
            except:
                pass
                
            return result
            
        except Exception as e:
            logger.error(f"Base64 OCR error: {e}")
            return {
                "error": str(e),
                "ocr_method": "error",
                "confidence": 0
            }

# Global instance
optimized_ocr_service = OptimizedOCRService()