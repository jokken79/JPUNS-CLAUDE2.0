"""Monitoring and health-check endpoints."""
from __future__ import annotations

import platform
import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from app.core.logging import app_logger
from app.services.ocr_service import ocr_service

router = APIRouter()


@router.get("/health", summary="Detailed health information")
async def detailed_health() -> Dict[str, Any]:
    try:
        started = getattr(ocr_service, "started_at", None)
        return {
            "status": "ok",
            "timestamp": time.time(),
            "system": {
                "platform": platform.platform(),
                "python": platform.python_version(),
            },
            "ocr": {
                "cache_entries": ocr_service.get_cache_stats().get("cache_entries", 0),
                "last_warmup": started,
            },
        }
    except Exception as exc:  # pragma: no cover - defensive
        app_logger.exception("Health endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/metrics", summary="Application metrics")
async def metrics() -> Dict[str, Any]:
    stats = ocr_service.get_cache_stats()
    return {
        "ocr_total_requests": stats.get("total_requests"),
        "ocr_cache_hits": stats.get("cache_hits"),
        "ocr_cache_hit_rate": stats.get("cache_hit_rate"),
        "ocr_average_processing_time": stats.get("average_processing_time"),
    }


@router.delete("/cache", summary="Clear OCR cache")
async def clear_cache() -> Dict[str, Any]:
    result = ocr_service.clear_cache()
    return result
