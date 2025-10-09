"""Tests for settings configuration."""
from __future__ import annotations

from app.core.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.APP_NAME == "UNS-ClaudeJP"
    assert settings.APP_VERSION == "2.0"
    assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
