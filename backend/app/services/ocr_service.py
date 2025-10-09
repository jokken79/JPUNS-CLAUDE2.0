"""Consolidated OCR service with hybrid processing pipeline."""
from __future__ import annotations

import asyncio
import base64
import concurrent.futures
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
import pytesseract
import requests
from PIL import Image

from app.core.config import settings
from app.core.logging import app_logger, log_ocr_operation

DEFAULT_CACHE_DIR = Path(settings.UPLOAD_DIR) / "ocr_cache"
DEFAULT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

MAX_IMAGE_SIZE = 1600
OCR_TIMEOUT = 60


class OCRService:
    """Hybrid OCR service with caching and fallbacks."""

    def __init__(self, cache_dir: Path | None = None) -> None:
        self.tesseract_lang = settings.TESSERACT_LANG
        self.vision_api_key = settings.GOOGLE_CLOUD_VISION_API_KEY
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
        self.total_requests = 0
        self.cache_hits = 0
        self.average_processing_time = 0.0
        self.started_at = time.time()
        self.cache_dir = Path(cache_dir) if cache_dir else DEFAULT_CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._preload_cache()
        app_logger.info("OCR service initialised")

    def _preload_cache(self) -> None:
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with cache_file.open("r", encoding="utf-8") as handle:
                    self.cache[cache_file.stem] = json.load(handle)
            except Exception as exc:  # pragma: no cover
                app_logger.warning("Failed to preload cache entry", file=str(cache_file), error=str(exc))

    def _hash_file(self, path: str) -> str:
        with open(path, "rb") as handle:
            return hashlib.md5(handle.read()).hexdigest()

    def _load_cache(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            return self.cache[key]
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with cache_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                self.cache[key] = data
                return data
        return None

    def _save_cache(self, key: str, data: Dict[str, Any]) -> None:
        self.cache[key] = data
        cache_file = self.cache_dir / f"{key}.json"
        with cache_file.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)

    def clear_cache(self) -> Dict[str, Any]:
        removed = len(list(self.cache_dir.glob("*.json")))
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)
        self.cache.clear()
        return {"success": True, "message": f"Cleared {removed} cache entries"}

    def get_cache_stats(self) -> Dict[str, Any]:
        total = self.total_requests or 1
        size = sum(f.stat().st_size for f in self.cache_dir.glob("*.json")) / (1024 * 1024)
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": f"{(self.cache_hits / total) * 100:.2f}%",
            "cache_entries": len(self.cache),
            "average_processing_time": f"{self.average_processing_time:.2f}s",
            "cache_size_on_disk": f"{size:.2f} MB",
        }

    async def process_document(self, file_path: str, document_type: str) -> Dict[str, Any]:
        start = time.perf_counter()
        self.total_requests += 1
        cache_key = self._hash_file(file_path)
        cached = self._load_cache(cache_key)
        if cached is not None:
            self.cache_hits += 1
            log_ocr_operation(source="cache", document_type=document_type, cache_key=cache_key)
            return cached

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            self.thread_pool, self._process_with_fallbacks, file_path, document_type, cache_key
        )

        self._save_cache(cache_key, result)

        elapsed = time.perf_counter() - start
        self.average_processing_time = ((self.average_processing_time * (self.total_requests - 1)) + elapsed) / self.total_requests
        log_ocr_operation(source="fresh", processing_time=elapsed, document_type=document_type, cache_key=cache_key)
        return result

    async def process_from_base64(self, image_base64: str, mime_type: str, document_type: str) -> Dict[str, Any]:
        extension = mime_type.split("/")[-1]
        temp_file = self.cache_dir / f"temp_{time.time_ns()}.{extension}"
        temp_file.write_bytes(base64.b64decode(image_base64))
        try:
            return await self.process_document(str(temp_file), document_type)
        finally:
            temp_file.unlink(missing_ok=True)

    def extract_text_with_gemini_api_from_base64(self, base64_image: str, mime_type: str) -> Dict[str, Any]:
        if not self.gemini_api_key:
            raise RuntimeError("Gemini API key is not configured")
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": "Extract textual information from this document."},
                        {"inline_data": {"mime_type": mime_type, "data": base64_image}},
                    ]
                }
            ]
        }
        response = requests.post(f"{endpoint}?key={self.gemini_api_key}", headers=headers, json=payload, timeout=OCR_TIMEOUT)
        response.raise_for_status()
        return response.json()

    # Internal helpers -----------------------------------------------------
    def _process_with_fallbacks(self, file_path: str, document_type: str, cache_key: str) -> Dict[str, Any]:
        optimised_path = self._optimise_image(file_path)
        processors = [self._process_with_gemini, self._process_with_vision, self._process_with_tesseract]
        try:
            for processor in processors:
                try:
                    result = processor(optimised_path, document_type)
                    if result:
                        result.update({"method": processor.__name__, "document_type": document_type, "cache_key": cache_key})
                        self._save_cache(cache_key, result)
                        return result
                except Exception as exc:  # pragma: no cover - fallback
                    app_logger.warning("OCR fallback failed", processor=processor.__name__, error=str(exc))
        finally:
            Path(optimised_path).unlink(missing_ok=True)
        raise RuntimeError("All OCR methods failed")

    def _optimise_image(self, path: str) -> str:
        image = Image.open(path)
        width, height = image.size
        if width > MAX_IMAGE_SIZE or height > MAX_IMAGE_SIZE:
            scale = MAX_IMAGE_SIZE / max(width, height)
            image = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)
        temp_path = f"{os.path.splitext(path)[0]}_opt.png"
        image.save(temp_path)
        return temp_path

    def _process_with_tesseract(self, path: str, document_type: str) -> Optional[Dict[str, Any]]:
        img = cv2.imread(path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = pytesseract.image_to_data(gray, lang=self.tesseract_lang, output_type=pytesseract.Output.DICT)
        text = " ".join(result.get("text", [])).strip()
        if not text:
            return None
        confidences = [c for c in result.get("conf", []) if isinstance(c, (int, float)) and c > 0]
        confidence = float(np.mean(confidences)) if confidences else None
        return {"text": text, "confidence": confidence}

    def _process_with_vision(self, path: str, document_type: str) -> Optional[Dict[str, Any]]:
        if not self.vision_api_key:
            return None
        with open(path, "rb") as handle:
            image_content = base64.b64encode(handle.read()).decode("utf-8")
        payload = {
            "requests": [
                {
                    "image": {"content": image_content},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        response = requests.post(
            "https://vision.googleapis.com/v1/images:annotate",
            params={"key": self.vision_api_key},
            json=payload,
            timeout=OCR_TIMEOUT,
        )
        response.raise_for_status()
        annotations = response.json().get("responses", [{}])[0].get("fullTextAnnotation")
        if not annotations:
            return None
        return {"text": annotations.get("text", ""), "confidence": annotations.get("pages", [{}])[0].get("confidence")}

    def _process_with_gemini(self, path: str, document_type: str) -> Optional[Dict[str, Any]]:
        if not self.gemini_api_key:
            return None
        with open(path, "rb") as handle:
            base64_image = base64.b64encode(handle.read()).decode("utf-8")
        result = self.extract_text_with_gemini_api_from_base64(base64_image, "image/png")
        candidates = result.get("candidates", [])
        if not candidates:
            return None
        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text")
        return {"text": text}


ocr_service = OCRService()

__all__ = ["OCRService", "ocr_service"]
