"""
Simple OCR Service using Gemini 2.0 Flash
Replaces the complex hybrid pipeline with a straightforward implementation
"""
import os
import base64
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from pathlib import Path

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDL32fmwB7SdbL6yEV3GbSP9dYhHdG1JXw")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
else:
    logger.warning("GEMINI_API_KEY not found")


class SimpleOCRService:
    """Simple OCR service using only Gemini 2.0 Flash"""

    def __init__(self):
        self.model_name = "gemini-2.0-flash-exp"
        logger.info(f"SimpleOCRService initialized with model: {self.model_name}")

    def process_document(self, file_path: str, document_type: str = "zairyu_card") -> Dict[str, Any]:
        """
        Process document image with OCR

        Args:
            file_path: Path to image file
            document_type: Type of document (zairyu_card, rirekisho, license, etc.)

        Returns:
            Dictionary with extracted data
        """
        try:
            logger.info(f"Processing document: {file_path}, type: {document_type}")

            # Read image file
            with open(file_path, 'rb') as f:
                image_data = f.read()

            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Determine mime type
            extension = Path(file_path).suffix.lower()
            mime_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_type_map.get(extension, 'image/jpeg')

            # Process with Gemini
            result = self._process_with_gemini(image_base64, mime_type, document_type)

            logger.info(f"Document processed successfully: {document_type}")
            return result

        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "raw_text": f"Error: {str(e)}"
            }

    def _process_with_gemini(self, image_base64: str, mime_type: str, document_type: str) -> Dict[str, Any]:
        """Process image with Gemini API"""
        try:
            # Create the model
            model = genai.GenerativeModel(self.model_name)

            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_base64
            }

            # Create prompt based on document type
            prompt = self._get_prompt_for_document_type(document_type)

            logger.info(f"Calling Gemini API with model: {self.model_name}")

            # Generate content
            response = model.generate_content([prompt, image_part])

            # Extract text
            raw_text = response.text if hasattr(response, 'text') else str(response)

            logger.info(f"Gemini API response received, length: {len(raw_text)}")

            # Parse structured data based on document type
            parsed_data = self._parse_response(raw_text, document_type)

            return {
                "success": True,
                "raw_text": raw_text,
                **parsed_data
            }

        except Exception as e:
            logger.error(f"Gemini API error: {e}", exc_info=True)
            raise

    def _get_prompt_for_document_type(self, document_type: str) -> str:
        """Get appropriate prompt for document type"""

        prompts = {
            "zairyu_card": """
Extract all information from this Japanese Residence Card (在留カード).
Please provide the following information in a structured format:

1. Full Name (Kanji): 氏名
2. Full Name (Roman): Name in alphabet
3. Date of Birth: 生年月日
4. Gender: 性別
5. Nationality: 国籍・地域
6. Residence Status: 在留資格
7. Card Number: 在留カード番号
8. Expiry Date: 有効期限の満了日
9. Address: 住居地
10. Issue Date: 交付年月日

Extract any visible text even if you're not 100% sure. Return the data clearly.
            """,

            "rirekisho": """
Extract all information from this Japanese Resume (履歴書).
Please provide the following information:

1. Full Name (Kanji): 氏名
2. Full Name (Kana): フリガナ
3. Date of Birth: 生年月日
4. Gender: 性別
5. Address: 現住所
6. Phone: 電話番号
7. Email: メールアドレス
8. Education History: 学歴
9. Work History: 職歴
10. Qualifications: 資格

Extract all visible text.
            """,

            "license": """
Extract all information from this Japanese Driver's License (運転免許証).
Please provide:

1. Full Name: 氏名
2. Date of Birth: 生年月日
3. Address: 住所
4. License Number: 免許証番号
5. License Type: 免許の種類
6. Expiry Date: 有効期限

Extract all visible text.
            """
        }

        return prompts.get(document_type, prompts["zairyu_card"])

    def _parse_response(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""

        # For now, return raw text - we can add more sophisticated parsing later
        # The frontend can display the raw_text to the user

        data = {
            "document_type": document_type,
            "extracted_text": raw_text
        }

        # Try to extract key fields for zairyu_card
        if document_type == "zairyu_card":
            lines = raw_text.split('\n')
            for line in lines:
                line_lower = line.lower()

                # Try to find expiry date
                if '有効期限' in line or 'expiry' in line_lower or '満了日' in line:
                    # Extract date patterns (YYYY年MM月DD日 or YYYY/MM/DD)
                    import re
                    date_pattern = r'(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})'
                    match = re.search(date_pattern, line)
                    if match:
                        year, month, day = match.groups()
                        data['zairyu_expire_date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

                # Try to find card number
                if 'カード番号' in line or 'card number' in line_lower:
                    import re
                    # Residence card numbers are typically alphanumeric
                    number_pattern = r'[A-Z]{2}\d{10,}'
                    match = re.search(number_pattern, line)
                    if match:
                        data['zairyu_card_number'] = match.group()

        return data


# Create singleton instance
ocr_service = SimpleOCRService()
