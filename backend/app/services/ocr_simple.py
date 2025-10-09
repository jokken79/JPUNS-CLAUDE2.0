"""Simple OCR service powered by Gemini 2.0 Flash.

This module keeps the lightweight architecture introduced during the first
refactor, but it now guides Gemini to return structured JSON payloads that map
directly to the fields expected by the frontend forms.  The previous
implementation returned the raw text only, which meant the UI never detected a
successful extraction because keys such as ``name`` or ``card_number`` were
missing.  By enforcing a deterministic JSON schema per document type we can
populate the resume form automatically without further manual tweaking.
"""

import base64
import json
import logging
import os
import re
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict

try:  # pragma: no cover - exercised indirectly via integration tests
    import google.generativeai as genai
except ImportError:  # pragma: no cover - triggered in CI where dependency is optional
    genai = None

logger = logging.getLogger(__name__)

# Configure Gemini once at import time
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if genai and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
elif not genai:
    logger.warning(
        "google-generativeai not installed; SimpleOCRService will operate in offline stub mode."
    )
else:  # pragma: no cover - configuration error should be visible in logs
    logger.warning("Required configuration not found; SimpleOCRService running in offline stub mode")


def _build_prompt(example: Dict[str, str], instructions: str) -> str:
    """Generate a strict prompt for Gemini enforcing a JSON response."""

    schema_example = json.dumps(example, ensure_ascii=False, indent=2)
    return dedent(
        f"""
        You are an OCR extraction assistant. Analyse the provided document image
        and return **only** a JSON object with the exact keys shown below.

        Additional requirements:
        - Every field must exist in the JSON. Use an empty string when data is missing.
        - Dates must use ISO format (YYYY-MM-DD) when possible.
        - The `raw_text` field must contain the complete text you recognised.
        - Do not add markdown, comments or extra prose.

        Expected JSON structure:
        {schema_example}

        Extraction guidelines:
        {instructions}
        """
    ).strip()


DOCUMENT_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "zairyu_card": {
        "fields": {
            "name": "Applicant full name (kanji preferred, romaji if unavailable)",
            "name_kanji": "Full name in kanji characters",
            "name_kana": "Full name in katakana",
            "name_romaji": "Full name using the Latin alphabet",
            "birthday": "Birth date",
            "gender": "Gender as it appears on the card",
            "nationality": "Nationality or region",
            "address": "Registered address",
            "postal_code": "Postal code if visible",
            "card_number": "Residence card number",
            "residence_status": "Residence status / visa type",
            "visa_type": "Visa type or status (duplicate of residence_status if needed)",
            "visa_period": "Length of stay (e.g., 1 year, 3 years)",
            "visa_expiry": "Residence period expiry date",
            "issue_date": "Card issue date",
            "permission_date": "Date of permission for extra activities if shown",
            "authorized_activity": "Any authorised activity notes",
            "employer_restriction": "Employer restrictions, if any",
            "region": "Region/prefecture if stated",
            "photo": "Base64 photo if extraction is possible, otherwise empty",
            "raw_text": "Complete recognised text"
        },
        "instructions": "Extract every visible field from a Japanese Residence Card (在留カード).",
    },
    "license": {
        "fields": {
            "name": "License holder name",
            "name_kana": "Name in katakana if printed",
            "birthday": "Birth date",
            "gender": "Gender if shown",
            "address": "Address on the license",
            "license_number": "Driver's license number",
            "license_type": "Vehicle categories or type",
            "license_expiry": "Expiry date",
            "issue_date": "Issue date if visible",
            "license_conditions": "Any conditions or remarks",
            "photo": "Base64 photo if available, otherwise empty",
            "raw_text": "Complete recognised text"
        },
        "instructions": "Extract information from a Japanese driver's license (運転免許証).",
    },
    "rirekisho": {
        "fields": {
            "name": "Applicant name in kanji",
            "name_kana": "Applicant name in katakana",
            "birthday": "Birth date",
            "gender": "Gender",
            "address": "Current address",
            "postal_code": "Postal code",
            "phone": "Phone number",
            "mobile": "Mobile phone if listed",
            "email": "Email address",
            "education_history": "Education history as text",
            "work_history": "Employment history as text",
            "qualifications": "Qualifications or licences",
            "raw_text": "Complete recognised text"
        },
        "instructions": "Extract details from a Japanese resume (履歴書).",
    },
}


class SimpleOCRService:
    """Simple OCR service using only Gemini 2.0 Flash when available."""

    def __init__(self) -> None:
        self._online = bool(genai and GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash-exp" if self._online else "offline-stub"
        if self._online:
            self._model = genai.GenerativeModel(self.model_name)
        else:
            self._model = None
        logger.info(
            "SimpleOCRService initialised",
            extra={"model": self.model_name, "online": self._online},
        )

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

            # Process with Gemini or offline stub
            result = self._process_with_gemini(image_base64, mime_type, document_type)

            logger.info(
                "Document processed successfully",
                extra={"document_type": document_type, "online": self._online},
            )
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
            if not self._online:
                logger.info(
                    "Returning offline OCR stub payload",
                    extra={"document_type": document_type},
                )
                return self._offline_payload(document_type)

            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_base64
            }

            # Create prompt based on document type
            prompt = self._get_prompt_for_document_type(document_type)

            logger.info(f"Calling Gemini API with model: {self.model_name}")

            # Generate content
            response = self._model.generate_content(
                [prompt, image_part],
                generation_config={
                    "temperature": 0.1,
                    "top_p": 0.1,
                    "top_k": 32,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                },
            )

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
        """Return the strict prompt for the requested document type."""

        definition = DOCUMENT_DEFINITIONS.get(document_type, DOCUMENT_DEFINITIONS["zairyu_card"])
        fields = definition["fields"]
        instructions = definition["instructions"]
        example = {key: "" for key in fields.keys()}
        return _build_prompt(example, instructions)

    def _parse_response(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Parse Gemini response into structured data"""

        parsed = self._parse_json_block(raw_text, document_type)
        if not parsed:
            parsed = self._fallback_parse(raw_text, document_type)

        # Normalise key aliases for the frontend
        parsed.setdefault("name", parsed.get("name_kanji") or parsed.get("full_name") or "")
        parsed.setdefault("visa_type", parsed.get("residence_status", ""))
        parsed.setdefault("extracted_text", parsed.get("raw_text", raw_text))
        parsed.setdefault("document_type", document_type)
        if parsed.get("visa_expiry") and "zairyu_expire_date" not in parsed:
            parsed["zairyu_expire_date"] = parsed["visa_expiry"]
        if parsed.get("card_number") and "zairyu_card_number" not in parsed:
            parsed["zairyu_card_number"] = parsed["card_number"]
        parsed.setdefault("raw_text", raw_text)
        parsed.setdefault("postal_code", "")

        return parsed

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _offline_payload(self, document_type: str) -> Dict[str, Any]:
        """Return deterministic payload when Gemini is unavailable."""

        definition = DOCUMENT_DEFINITIONS.get(document_type, DOCUMENT_DEFINITIONS["zairyu_card"])
        payload = {key: "" for key in definition["fields"].keys()}
        message = (
            "Offline OCR stub: install google-generativeai and provide GEMINI_API_KEY "
            "to enable live extraction"
        )
        payload.update(
            {
                "success": False,
                "error": message,
                "raw_text": message,
                "extracted_text": message,
                "document_type": document_type,
            }
        )
        return payload

    def _parse_json_block(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Attempt to parse Gemini response as JSON."""

        try:
            payload = json.loads(raw_text)
            if isinstance(payload, dict):
                # Ensure every expected field exists
                definition = DOCUMENT_DEFINITIONS.get(document_type, DOCUMENT_DEFINITIONS["zairyu_card"])
                for key in definition["fields"].keys():
                    payload.setdefault(key, "")
                return {key: (value.strip() if isinstance(value, str) else value) for key, value in payload.items()}
        except json.JSONDecodeError:
            logger.debug("Gemini response is not JSON", extra={"document_type": document_type})
        return {}

    def _fallback_parse(self, raw_text: str, document_type: str) -> Dict[str, Any]:
        """Fallback regex-based parser when JSON decoding fails."""

        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        text = "\n".join(lines)
        data: Dict[str, Any] = {
            "raw_text": raw_text,
            "extracted_text": raw_text,
            "document_type": document_type,
        }

        def search(pattern: str, flags: int = 0) -> str:
            match = re.search(pattern, text, flags)
            return match.group(1).strip() if match else ""

        def search_in_lines(keyword: str) -> str:
            for line in lines:
                if keyword in line:
                    return line.split(keyword, 1)[-1].strip()
            return ""

        # Common fields
        data["name"] = search(r"氏名[:：\s]*([\w\dぁ-んァ-ヶ一-龯・ー\s]+)") or search_in_lines("氏名")
        data["birthday"] = self._extract_iso_date(search(r"生年月日[:：\s]*([0-9年月日./-]+)"))
        gender = search(r"性別[:：\s]*([男女MaleFemale]+)", re.IGNORECASE)
        data["gender"] = gender
        data["nationality"] = search(r"国籍[・:：\s]*([^\n]+)")
        address = search(r"住所[:：\s]*([^\n]+)") or search(r"住居地[:：\s]*([^\n]+)")
        data["address"] = address
        data["postal_code"] = search(r"(\d{3}-\d{4})")

        if document_type == "zairyu_card":
            data["card_number"] = search(r"([A-Z]{2}\d{10,})")
            data["visa_expiry"] = self._extract_iso_date(search(r"有効期限[の満了日]*[:：\s]*([0-9年月日./-]+)"))
            data["issue_date"] = self._extract_iso_date(search(r"交付年月日[:：\s]*([0-9年月日./-]+)"))
            data["residence_status"] = search(r"在留資格[:：\s]*([^\n]+)")
            data["visa_period"] = search(r"在留期間[:：\s]*([^\n]+)")
            data["permission_date"] = self._extract_iso_date(search(r"許可年月日[:：\s]*([0-9年月日./-]+)"))
        elif document_type == "license":
            data["license_number"] = search(r"(\d{4}-\d{6}-\d{2})") or search(r"免許証番号[:：\s]*([0-9-]+)")
            data["license_expiry"] = self._extract_iso_date(search(r"有効期限[:：\s]*([0-9年月日./-]+)"))
            data["license_type"] = search(r"免許の種類[:：\s]*([^\n]+)")
            data["issue_date"] = self._extract_iso_date(search(r"交付[:：\s]*([0-9年月日./-]+)"))
            data["license_conditions"] = search(r"条件[:：\s]*([^\n]+)")
        else:  # rirekisho
            data["phone"] = search(r"電話[:：\s]*([0-9-]+)")
            data["email"] = search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

        return data

    def _extract_iso_date(self, text: str) -> str:
        """Convert Japanese date strings to ISO format if possible."""

        if not text:
            return ""

        pattern = r"(\d{4})[年/\-.](\d{1,2})[月/\-.](\d{1,2})"
        match = re.search(pattern, text)
        if match:
            year, month, day = match.groups()
            return f"{year}-{int(month):02d}-{int(day):02d}"
        return text.strip()


# Create singleton instance
ocr_service = SimpleOCRService()
