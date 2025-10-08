"""Compatibility wrapper for the legacy OCR service interface.

This module re-exports the improved OCRService implementation used by
``ocr_service_fixed`` so that older imports continue working while
benefiting from the latest fixes (license parsing, enhanced validation,
Gemini/Vision/Tesseract handling, etc.).
"""
from app.services.ocr_service_fixed import OCRService as FixedOCRService, ocr_service_fixed

# Re-export the improved service under the original names expected by legacy code.
OCRService = FixedOCRService
ocr_service = ocr_service_fixed

__all__ = ["OCRService", "ocr_service"]
