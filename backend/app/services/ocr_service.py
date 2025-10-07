"""
OCR Service for UNS-ClaudeJP 1.0
Processes Rirekisho, Zairyu Card, License, and Timer Cards
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from pdf2image import convert_from_path
import re
from typing import Dict, Optional, List
import os
from datetime import datetime
import base64
import requests

from app.core.config import settings


class OCRService:
    """Service for OCR processing"""
    
    def __init__(self):
        self.tesseract_lang = settings.TESSERACT_LANG
        self.use_vision_api = getattr(settings, 'GOOGLE_CLOUD_VISION_ENABLED', False)
        self.vision_api_key = getattr(settings, 'GOOGLE_CLOUD_VISION_API_KEY', None)
        
    def preprocess_for_japanese_id(self, image_path: str) -> np.ndarray:
        """
        Optimized preprocessing specifically for Japanese ID cards (在留カード)
        """
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise Exception(f"Failed to read image: {image_path}")

        # Upscale significantly for small text
        scale_factor = 4.0
        img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LANCZOS4)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(enhanced, h=10, templateWindowSize=7, searchWindowSize=21)

        # Sharpen
        kernel_sharpen = np.array([[-1,-1,-1,-1,-1],
                                   [-1, 2, 2, 2,-1],
                                   [-1, 2, 8, 2,-1],
                                   [-1, 2, 2, 2,-1],
                                   [-1,-1,-1,-1,-1]]) / 8.0
        sharpened = cv2.filter2D(denoised, -1, kernel_sharpen)

        # Binary threshold - use Otsu's method
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Morphological operations to connect text
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        return morph

    def extract_text_with_tesseract_optimized(self, image_path: str) -> str:
        """
        Extract text using Tesseract with optimized settings for Japanese ID cards
        Uses multiple PSM modes and combines results
        """
        try:
            # Read original image
            img = cv2.imread(image_path)
            if img is None:
                return ""

            # Try multiple preprocessing strategies and combine results
            results = []

            # Strategy 1: High contrast upscale
            scale1 = cv2.resize(img, None, fx=4.0, fy=4.0, interpolation=cv2.INTER_LANCZOS4)
            gray1 = cv2.cvtColor(scale1, cv2.COLOR_BGR2GRAY)
            _, binary1 = cv2.threshold(gray1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Strategy 2: CLAHE enhanced
            gray2 = cv2.cvtColor(scale1, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced2 = clahe.apply(gray2)

            # Strategy 3: Adaptive threshold
            gray3 = cv2.cvtColor(scale1, cv2.COLOR_BGR2GRAY)
            adaptive3 = cv2.adaptiveThreshold(gray3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY, 11, 2)

            # Try different PSM modes
            psm_modes = [
                (6, '--oem 3 --psm 6'),  # Uniform block of text
                (11, '--oem 3 --psm 11'), # Sparse text
                (3, '--oem 3 --psm 3')   # Fully automatic
            ]

            best_text = ""
            best_length = 0

            for strategy_img in [binary1, enhanced2, adaptive3]:
                for psm_id, config in psm_modes:
                    try:
                        text = pytesseract.image_to_string(
                            strategy_img,
                            lang='jpn+eng',
                            config=config
                        )

                        # Count meaningful characters (exclude noise)
                        meaningful_chars = len(re.findall(r'[a-zA-Z一-龯ぁ-んァ-ヶー0-9]', text))

                        if meaningful_chars > best_length:
                            best_length = meaningful_chars
                            best_text = text
                            print(f"DEBUG: Better result with PSM {psm_id}, {meaningful_chars} meaningful chars")

                    except Exception as e:
                        continue

            print(f"DEBUG: Best Tesseract result: {best_length} meaningful characters out of {len(best_text)} total")
            return best_text if best_text else ""

        except Exception as e:
            print(f"Error with Tesseract OCR: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def extract_text_with_gemini_api(self, image_path: str) -> Dict:
        """
        Extract structured data from image using Gemini API (like index.html)
        Returns dict with name, birthday, address, gender, nationality, etc.
        """
        try:
            # Read image and convert to base64
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            # Detect MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'

            # Gemini API endpoint
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={self.vision_api_key}"

            # Schema for structured output (extended from index.html version)
            schema = {
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING", "description": "Full name in Japanese (Kanji/Kana) or Latin characters from 氏名/NAME field"},
                    "birthday": {"type": "STRING", "description": "Date of birth in YYYY-MM-DD format from 生年月日"},
                    "address": {"type": "STRING", "description": "Residential address in Japanese from 住所"},
                    "gender": {"type": "STRING", "description": "Gender: 男性 or 女性 from 性別/SEX field"},
                    "nationality": {"type": "STRING", "description": "Nationality in Japanese (ベトナム, ブラジル, etc.) from 国籍/NATIONALITY"},
                    "card_number": {"type": "STRING", "description": "Residence card number from 番号/NUMBER"},
                    "visa_type": {"type": "STRING", "description": "Visa status from 在留資格/STATUS field"},
                    "visa_expiry": {"type": "STRING", "description": "Card expiry date in YYYY-MM-DD format from このカードは...まで有効"}
                },
                "propertyOrdering": ["name", "birthday", "address", "gender", "nationality", "card_number", "visa_type", "visa_expiry"]
            }

            payload = {
                "contents": [{
                    "parts": [{
                        "text": """Extract information from this Japanese Residence Card (在留カード):
                        - name (氏名/NAME): The person's full name
                        - birthday (生年月日): Date of birth in YYYY-MM-DD format
                        - address (住所): Full address
                        - gender (性別/SEX): Male (男性) or Female (女性)
                        - nationality (国籍/NATIONALITY): Country in Japanese (ベトナム, ブラジル, ペルー, etc.)
                        - card_number (番号/NUMBER): The card number
                        - visa_type (在留資格/STATUS): The residence status
                        - visa_expiry: The expiry date in YYYY-MM-DD format

                        Return only the JSON object with these fields."""
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

            print("DEBUG: Calling Gemini API with structured output...")
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"Gemini API error: {response.status_code} - {response.text}")
                return {}

            result = response.json()

            # Extract the JSON response
            text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

            if not text_content:
                print("WARNING: Gemini API returned empty content")
                return {}

            # Parse JSON
            import json
            parsed_data = json.loads(text_content)
            print(f"DEBUG: Gemini API extracted data: {parsed_data}")

            return parsed_data

        except Exception as e:
            print(f"Error with Gemini API: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def extract_text_with_vision_api_direct(self, image_path: str) -> str:
        """
        Extract text using Vision API DOCUMENT_TEXT_DETECTION (no preprocessing)
        """
        try:
            # Read original image (no preprocessing)
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')

            # Vision API endpoint
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.vision_api_key}"

            payload = {
                "requests": [{
                    "image": {"content": image_base64},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "imageContext": {
                        "languageHints": ["ja", "en"]
                    }
                }]
            }

            response = requests.post(url, json=payload, timeout=30)

            if response.status_code != 200:
                print(f"Vision API error: {response.status_code}")
                return ""

            result = response.json()

            # Extract text
            if 'responses' in result and len(result['responses']) > 0:
                if 'fullTextAnnotation' in result['responses'][0]:
                    text = result['responses'][0]['fullTextAnnotation']['text']
                    print(f"DEBUG: Vision API extracted {len(text)} characters")
                    return text
                elif 'textAnnotations' in result['responses'][0] and len(result['responses'][0]['textAnnotations']) > 0:
                    text = result['responses'][0]['textAnnotations'][0]['description']
                    return text

            return ""

        except Exception as e:
            print(f"Vision API error: {e}")
            return ""

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using Google Cloud Vision API or Tesseract OCR
        """
        # Try Vision API first if enabled
        if self.use_vision_api and self.vision_api_key and self.vision_api_key != 'YOUR_API_KEY_HERE':
            print("Using Google Cloud Vision API for text extraction")
            text = self.extract_text_with_vision_api_direct(image_path)
            if text:
                return text
            print("Vision API failed, falling back to Tesseract")

        # Fallback to Tesseract
        try:
            print("Using Tesseract for OCR")
            # Preprocess image
            processed_img = self.preprocess_image(image_path)

            # Run OCR
            text = pytesseract.image_to_string(processed_img, lang=self.tesseract_lang)

            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            all_text = []
            for img in images:
                # Convert PIL image to numpy array
                img_array = np.array(img)
                
                # Save temporarily
                temp_path = "/tmp/temp_ocr_image.jpg"
                img.save(temp_path)
                
                # Extract text
                text = self.extract_text_from_image(temp_path)
                all_text.append(text)
                
                # Clean up
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            return "\n".join(all_text)
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def parse_rirekisho(self, text: str) -> Dict:
        """
        Parse rirekisho text and extract structured data
        """
        data = {
            "full_name_kanji": None,
            "full_name_kana": None,
            "date_of_birth": None,
            "gender": None,
            "address": None,
            "phone": None,
            "email": None,
        }
        
        # Extract name (氏名)
        name_pattern = r"氏名[：:\s]*([^\n]+)"
        name_match = re.search(name_pattern, text)
        if name_match:
            data["full_name_kanji"] = name_match.group(1).strip()
        
        # Extract furigana (フリガナ)
        kana_pattern = r"フリガナ[：:\s]*([^\n]+)"
        kana_match = re.search(kana_pattern, text)
        if kana_match:
            data["full_name_kana"] = kana_match.group(1).strip()
        
        # Extract date of birth (生年月日)
        dob_pattern = r"生年月日[：:\s]*(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})"
        dob_match = re.search(dob_pattern, text)
        if dob_match:
            year, month, day = dob_match.groups()
            data["date_of_birth"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Extract gender (性別)
        if "男" in text:
            data["gender"] = "男性"
        elif "女" in text:
            data["gender"] = "女性"
        
        # Extract address (住所)
        address_pattern = r"住所[：:\s]*([^\n]+)"
        address_match = re.search(address_pattern, text)
        if address_match:
            data["address"] = address_match.group(1).strip()
        
        # Extract phone (電話番号)
        phone_pattern = r"電話[：:\s]*(\d{2,4}[-\s]?\d{2,4}[-\s]?\d{4})"
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            data["phone"] = phone_match.group(1).strip()
        
        # Extract email
        email_pattern = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        email_match = re.search(email_pattern, text)
        if email_match:
            data["email"] = email_match.group(1).strip()
        
        return data
    
    def extract_face_from_zairyu_card(self, image_path: str) -> Optional[str]:
        """
        Extract face photo from Zairyu Card using face detection
        Returns base64 encoded image of the face
        """
        try:
            import base64

            # Load the image
            img = cv2.imread(image_path)
            if img is None:
                return None

            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Load OpenCV's pre-trained face detector
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            # Detect faces
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) == 0:
                # If no face detected, try to extract from typical position (top-right corner of card)
                height, width = img.shape[:2]
                # Typical position of photo on Zairyu card is top-right
                # Adjust these coordinates based on actual card layout
                x = int(width * 0.7)
                y = int(height * 0.1)
                w = int(width * 0.25)
                h = int(height * 0.35)
                face_img = img[y:y+h, x:x+w]
            else:
                # Get the largest face
                (x, y, w, h) = max(faces, key=lambda face: face[2] * face[3])
                # Add more padding for better cropping (60px for more space)
                padding = 60
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img.shape[1] - x, w + 2*padding)
                h = min(img.shape[0] - y, h + 2*padding)
                face_img = img[y:y+h, x:x+w]

            # Resize to standard passport photo size (approx 150x180)
            face_img = cv2.resize(face_img, (150, 180))

            # Convert to base64
            _, buffer = cv2.imencode('.jpg', face_img)
            face_base64 = base64.b64encode(buffer).decode('utf-8')

            return f"data:image/jpeg;base64,{face_base64}"

        except Exception as e:
            print(f"Error extracting face from Zairyu card: {e}")
            return None

    def parse_zairyu_card(self, text: str) -> Dict:
        """
        Parse Zairyu Card and extract data
        """
        data = {
            "card_number": None,
            "name": "",  # Will be extracted or left empty
            "nationality": None,
            "date_of_birth": None,
            "birthday": None,  # Alias for compatibility
            "gender": None,
            "address": None,
            "expire_date": None,
            "status": None,  # 在留資格 (visa type)
            "visa_duration": None,  # ビザ期間
        }

        print(f"DEBUG: Extracted text from card (first 500 chars):\n{text[:500] if text else '(empty)'}")  # Debug print

        # If text is empty or very short, likely OCR failed
        if not text or len(text.strip()) < 10:
            print("WARNING: OCR extracted very little text from card")
            # Return with photo only, user can fill manually
            return data

        # Clean and normalize text
        text = text.replace('\x00', '').strip()
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        # Extract name - improved strategy
        name_found = False

        # Strategy 1: Look for 氏名 field directly in text
        name_pattern1 = r'氏\s*名[：:\s　]*([^\n\s]{2,20}(?:\s+[^\n\s]{2,20})?)'
        name_match1 = re.search(name_pattern1, text)
        if name_match1:
            data["name"] = name_match1.group(1).strip()
            name_found = True
            print(f"DEBUG: Found name via 氏名 pattern: {data['name']}")

        # Strategy 2: Look for NAME field in English
        if not name_found:
            # Find NAME marker and get next meaningful text
            for i, line in enumerate(lines):
                if re.search(r'\bNAME\b', line, re.IGNORECASE):
                    # Check next few lines for the actual name
                    for j in range(i+1, min(i+4, len(lines))):
                        potential = lines[j]
                        # Clean up
                        potential = re.sub(r'[^\w\s一-龯ぁ-んァ-ヶー]', '', potential).strip()
                        # Skip if it's another field label
                        if any(word in potential.upper() for word in ['SEX', 'DATE', 'BIRTH', 'NATIONALITY', 'CARD']):
                            continue
                        if len(potential) >= 3 and len(potential) <= 40:
                            data["name"] = potential
                            name_found = True
                            print(f"DEBUG: Found name after NAME: {data['name']}")
                            break
                    if name_found:
                        break

        # Strategy 3: Look for capital letter names (Western style)
        if not name_found:
            for line in lines:
                # Skip common labels
                if any(word in line for word in ['NAME', 'SEX', 'CARD', 'NUMBER', 'DATE', 'PERIOD', 'STATUS']):
                    continue
                # Look for 2-3 capitalized words
                caps_match = re.match(r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,2})$', line)
                if caps_match:
                    data["name"] = caps_match.group(1)
                    name_found = True
                    print(f"DEBUG: Found Western name: {data['name']}")
                    break

        # Strategy 4: Japanese name characters
        if not name_found:
            for line in lines:
                # Look for Japanese characters (kanji/kana)
                jp_match = re.search(r'([一-龯ぁ-んァ-ヶー]{2,}(?:\s*[一-龯ぁ-んァ-ヶー]+)?)', line)
                if jp_match:
                    potential = jp_match.group(1).strip()
                    # Validate it's not a common word
                    if len(potential) >= 2 and len(potential) <= 15:
                        data["name"] = potential
                        print(f"DEBUG: Found Japanese name: {data['name']}")
                        break

        # Extract card number (番号) - look for pattern or after 番号
        card_patterns = [
            r"番号[：:\s]*([A-Z]{2}\d{10,14})",  # After 番号 label
            r"([A-Z]{2}\d{10,14})",  # Standalone pattern
        ]
        for pattern in card_patterns:
            card_match = re.search(pattern, text)
            if card_match:
                data["card_number"] = card_match.group(1).strip()
                print(f"DEBUG: Found card number: {data['card_number']}")
                break

        # Extract nationality (国籍) - both Japanese and English
        nationality_patterns = [
            r"国籍[：:\s]*([^\n]+)",
            r"NATIONALITY[：:\s]*([A-Z]+)",
        ]
        for pattern in nationality_patterns:
            nationality_match = re.search(pattern, text, re.IGNORECASE)
            if nationality_match:
                nationality = nationality_match.group(1).strip()
                # Map common English names to Japanese
                nationality_map = {
                    'VIETNAM': 'ベトナム',
                    'VIET NAM': 'ベトナム',
                    'BRAZIL': 'ブラジル',
                    'PERU': 'ペルー',
                    'INDONESIA': 'インドネシア',
                    'PHILIPPINES': 'フィリピン',
                    'CHINA': '中国',
                    'MYANMAR': 'ミャンマー',
                }
                data["nationality"] = nationality_map.get(nationality.upper(), nationality)
                print(f"DEBUG: Found nationality: {data['nationality']}")
                break

        # Extract gender (性別)
        gender_patterns = [
            r"性別[：:\s]*(男|女|男性|女性)",
            r"SEX[：:\s]*(M|F|Male|Female)",
        ]
        for pattern in gender_patterns:
            gender_match = re.search(pattern, text, re.IGNORECASE)
            if gender_match:
                gender_text = gender_match.group(1).strip().upper()
                # Normalize to Japanese
                if gender_text in ['M', 'MALE', '男']:
                    data["gender"] = '男性'
                elif gender_text in ['F', 'FEMALE', '女']:
                    data["gender"] = '女性'
                else:
                    data["gender"] = gender_text
                print(f"DEBUG: Found gender: {data['gender']}")
                break

        # Extract date of birth (生年月日) - more flexible patterns
        dob_patterns = [
            r"(\d{4})[年/\-\.\s](\d{1,2})[月/\-\.\s](\d{1,2})",
            r"(\d{2})[/\-\.](\d{2})[/\-\.](\d{4})",  # MM/DD/YYYY
        ]
        for pattern in dob_patterns:
            dob_match = re.search(pattern, text)
            if dob_match:
                if len(dob_match.group(1)) == 4:  # YYYY-MM-DD
                    year, month, day = dob_match.groups()
                else:  # MM-DD-YYYY
                    month, day, year = dob_match.groups()

                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                data["date_of_birth"] = formatted_date
                data["birthday"] = formatted_date  # Alias
                print(f"DEBUG: Found date: {formatted_date}")
                break

        # Extract address (住所) - look for Japanese address patterns
        address_patterns = [
            r"住所[：:\s]*([^\n]+)",
            r"([^0-9\n]{2,}[都道府県][^0-9\n]{2,}[市区町村][^\n]+)",
        ]
        for pattern in address_patterns:
            address_match = re.search(pattern, text)
            if address_match:
                data["address"] = address_match.group(1).strip()
                break

        # Extract expire date (有効期限)
        expire_pattern = r"有効期限[：:\s]*(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})"
        expire_match = re.search(expire_pattern, text)
        if expire_match:
            year, month, day = expire_match.groups()
            data["expire_date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        # Extract status (在留資格 / ビザ種類)
        status_patterns = [
            r"在留資格[：:\s]*([^\n]+)",
            r"STATUS[：:\s]*([^\n]+)",
        ]
        for pattern in status_patterns:
            status_match = re.search(pattern, text, re.IGNORECASE)
            if status_match:
                data["status"] = status_match.group(1).strip()
                print(f"DEBUG: Found visa status: {data['status']}")
                break

        # Extract visa duration (このカードは YYYY年MM月DD日まで有効)
        visa_duration_patterns = [
            r"このカードは[^\d]*(\d{4})年(\d{1,2})月(\d{1,2})日まで有効",
            r"(\d{4})年(\d{1,2})月(\d{1,2})日まで有効",
        ]
        for pattern in visa_duration_patterns:
            duration_match = re.search(pattern, text)
            if duration_match:
                year, month, day = duration_match.groups()
                data["visa_duration"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"DEBUG: Found visa duration: {data['visa_duration']}")
                break

        # If not found, try to extract from expire_date as fallback
        if not data["visa_duration"] and data.get("expire_date"):
            data["visa_duration"] = data["expire_date"]

        return data
    
    def parse_timer_card(self, text: str, factory_id: str = None) -> List[Dict]:
        """
        Parse timer card and extract attendance data
        Returns list of daily records
        """
        records = []
        
        # Different patterns for different factory formats
        # This is a basic implementation - needs to be customized per factory
        
        # Pattern 1: Date | Name | Clock In | Clock Out
        pattern1 = r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})\s+([^\s]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})"
        matches = re.finditer(pattern1, text)
        
        for match in matches:
            date, name, clock_in, clock_out = match.groups()
            
            record = {
                "work_date": date,
                "employee_name": name,
                "clock_in": clock_in,
                "clock_out": clock_out,
            }
            records.append(record)
        
        # Pattern 2: More complex factory formats
        # Can be extended based on actual timer card formats
        
        return records
    
    def process_document(self, file_path: str, document_type: str) -> Dict:
        """
        Main method to process any document type
        """
        # Determine file type
        file_ext = os.path.splitext(file_path)[1].lower()

        # Parse based on document type
        if document_type == "rirekisho":
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            else:
                text = self.extract_text_from_image(file_path)
            return self.parse_rirekisho(text)

        elif document_type == "zairyu_card":
            # Use optimized Tesseract OCR (free, fast, offline)
            print("Using optimized Tesseract OCR for Zairyu Card")
            text = self.extract_text_with_tesseract_optimized(file_path)

            # Parse extracted text
            data = self.parse_zairyu_card(text)

            # Extract face photo from zairyu card
            if file_ext in ['.jpg', '.jpeg', '.png']:
                face_photo = self.extract_face_from_zairyu_card(file_path)
                if face_photo:
                    data['photo'] = face_photo

            return data

        elif document_type == "timer_card":
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            else:
                text = self.extract_text_from_image(file_path)
            return {"records": self.parse_timer_card(text)}
        else:
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            else:
                text = self.extract_text_from_image(file_path)
            return {"raw_text": text}


# Global instance
ocr_service = OCRService()
