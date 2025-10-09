"""Security tests for the simple OCR endpoint."""
from __future__ import annotations

from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient


def test_process_ocr_malicious_extension(client: TestClient) -> None:
    """Test that uploading a file with a malicious extension is handled safely."""
    with patch("app.api.ocr_simple.ocr_service.process_document") as mock_process_document:
        mock_process_document.return_value = {"status": "success"}
        file_content = b"fake image content"
        files = {"file": ("malicious.sh", file_content, "image/jpeg")}
        response = client.post("/api/ocr/process", files=files)

        assert response.status_code == 200
        mock_process_document.assert_called_once()

        # Check that the temporary file has a safe extension
        call_args, _ = mock_process_document.call_args
        temp_file_path = call_args[0]
        assert temp_file_path.endswith(".tmp")
