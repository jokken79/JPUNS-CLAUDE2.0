# UNS-ClaudeJP API Examples

## Authentication
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"
```

## OCR Document Processing
```bash
curl -X POST http://localhost:8000/api/ocr/process \
  -H "Authorization: Bearer <token>" \
  -F "file=@/path/document.png" \
  -F "document_type=zairyu_card"
```

## Health and Metrics
```bash
curl http://localhost:8000/api/monitoring/health
curl http://localhost:8000/api/monitoring/metrics
```
