"""Unit tests for OCR service helpers."""
from __future__ import annotations

import base64

import pytest

from app.services.ocr_service import OCRService


class DummyService(OCRService):
    def __init__(self, cache_dir):  # type: ignore[override]
        super().__init__(cache_dir=cache_dir)
        self._memory_cache = {}

    def _load_cache(self, key: str):  # type: ignore[override]
        return self._memory_cache.get(key)

    def _save_cache(self, key: str, data):  # type: ignore[override]
        self._memory_cache[key] = data

    def clear_cache(self):  # type: ignore[override]
        self._memory_cache.clear()
        return {"success": True, "message": "Cleared 0 cache entries"}

    def _process_with_fallbacks(self, file_path: str, document_type: str, cache_key: str):
        return {"text": "dummy", "method": "dummy", "document_type": document_type, "cache_key": cache_key}


@pytest.mark.asyncio
async def test_process_document_uses_cache(tmp_path):
    service = DummyService(tmp_path)
    file_path = tmp_path / "sample.png"
    file_path.write_bytes(b"data")

    first = await service.process_document(str(file_path), "test")
    second = await service.process_document(str(file_path), "test")

    assert first == second
    assert service.cache_hits >= 1


@pytest.mark.asyncio
async def test_process_from_base64(tmp_path):
    service = DummyService(tmp_path)
    encoded = base64.b64encode(b"data").decode("utf-8")
    result = await service.process_from_base64(encoded, "image/png", "test")
    assert result["text"] == "dummy"
