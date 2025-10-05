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

from app.core.config import settings


class OCRService:
    """Service for OCR processing"""
    
    def __init__(self):
        self.tesseract_lang = settings.TESSERACT_LANG
        
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR results
        """
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get black and white image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image using Tesseract OCR
        """
        try:
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
    
    def parse_zairyu_card(self, text: str) -> Dict:
        """
        Parse Zairyu Card and extract data
        """
        data = {
            "card_number": None,
            "name": None,
            "nationality": None,
            "date_of_birth": None,
            "expire_date": None,
            "status": None,
        }
        
        # Extract card number
        card_pattern = r"在留カード番号[：:\s]*([A-Z0-9]+)"
        card_match = re.search(card_pattern, text)
        if card_match:
            data["card_number"] = card_match.group(1).strip()
        
        # Extract nationality (国籍)
        nationality_pattern = r"国籍[：:\s]*([^\n]+)"
        nationality_match = re.search(nationality_pattern, text)
        if nationality_match:
            data["nationality"] = nationality_match.group(1).strip()
        
        # Extract expire date (有効期限)
        expire_pattern = r"有効期限[：:\s]*(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})"
        expire_match = re.search(expire_pattern, text)
        if expire_match:
            year, month, day = expire_match.groups()
            data["expire_date"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Extract status (在留資格)
        status_pattern = r"在留資格[：:\s]*([^\n]+)"
        status_match = re.search(status_pattern, text)
        if status_match:
            data["status"] = status_match.group(1).strip()
        
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
        
        # Extract text
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        else:
            text = self.extract_text_from_image(file_path)
        
        # Parse based on document type
        if document_type == "rirekisho":
            return self.parse_rirekisho(text)
        elif document_type == "zairyu_card":
            return self.parse_zairyu_card(text)
        elif document_type == "timer_card":
            return {"records": self.parse_timer_card(text)}
        else:
            return {"raw_text": text}


# Global instance
ocr_service = OCRService()
