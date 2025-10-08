# 🚀 MEJORAS RECOMENDADAS - UNS-ClaudeJP 2.0

## 📊 ANÁLISIS DEL CÓDIGO ACTUAL

### ✅ Lo que funciona bien:
- Sistema de OCR funcionando (Gemini + Vision API + Tesseract)
- Backend en FastAPI bien estructurado
- Frontend en React con TypeScript
- Docker configurado correctamente
- Base de datos PostgreSQL con schema completo

### ⚠️ Problemas Críticos Detectados:

#### 1. **API KEY HARDCODEADA EN FRONTEND** 🔴 CRÍTICO
**Ubicación:** `frontend/public/templates/rirekisho.html` línea 139
```javascript
const API_KEY = "AIzaSyDL32fmwB7SdbL6yEV3GbSP9dYhHdG1JXw";
```

**Riesgos:**
- ❌ Visible en el código fuente del navegador
- ❌ Cualquiera puede usar tu cuota de Gemini
- ❌ Riesgo de abuso de la API
- ❌ Violación de mejores prácticas de seguridad

---

## 🔧 SOLUCIONES PROPUESTAS

### SOLUCIÓN 1: Mover API Key al Backend ⭐ PRIORIDAD ALTA

#### Paso 1: Crear nuevo endpoint en el backend

**Archivo:** `backend/app/api/ocr.py` (NUEVO)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import base64
import logging

from app.services.ocr_service import ocr_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/gemini/process", response_model=Dict)
async def process_with_gemini(file: UploadFile = File(...)):
    """
    Procesa imagen con Gemini API desde el backend
    Esto protege la API key y centraliza el procesamiento OCR
    """
    try:
        # Validar tipo de archivo
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Solo se aceptan imágenes")
        
        # Leer archivo
        content = await file.read()
        
        # Validar tamaño (máx 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Imagen muy grande (máx 10MB)")
        
        # Convertir a base64
        base64_image = base64.b64encode(content).decode('utf-8')
        
        # Procesar con Gemini
        logger.info(f"Processing image with Gemini: {file.filename}")
        result = ocr_service.extract_text_with_gemini_api_from_base64(
            base64_image=base64_image,
            mime_type=file.content_type
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="OCR falló")
        
        logger.info("OCR successful")
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```

#### Paso 2: Registrar el router en main.py

**Archivo:** `backend/app/main.py`

```python
# Agregar esta línea con los otros imports de routers
from app.api import ocr

# Agregar esta línea donde están los otros routers
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])
```

#### Paso 3: Actualizar el servicio OCR

**Archivo:** `backend/app/services/ocr_service.py`

Agregar este método nuevo:

```python
def extract_text_with_gemini_api_from_base64(
    self, 
    base64_image: str, 
    mime_type: str
) -> Dict:
    """
    Extract structured data from base64 image using Gemini API
    Similar al método existente pero acepta base64 directamente
    """
    try:
        # Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={self.vision_api_key}"

        # Schema para salida estructurada
        schema = {
            "type": "OBJECT",
            "properties": {
                "name": {
                    "type": "STRING", 
                    "description": "Full name from 氏名/NAME field"
                },
                "birthday": {
                    "type": "STRING", 
                    "description": "Date of birth in YYYY-MM-DD format from 生年月日"
                },
                "address": {
                    "type": "STRING", 
                    "description": "Residential address from 住所"
                },
                "gender": {
                    "type": "STRING", 
                    "description": "Gender: 男性 or 女性 from 性別/SEX field"
                },
                "nationality": {
                    "type": "STRING", 
                    "description": "Nationality in Japanese from 国籍/NATIONALITY"
                },
                "card_number": {
                    "type": "STRING", 
                    "description": "Card number from 番号/NUMBER"
                },
                "visa_type": {
                    "type": "STRING", 
                    "description": "Visa status from 在留資格/STATUS field"
                },
                "visa_expiry": {
                    "type": "STRING", 
                    "description": "Expiry date in YYYY-MM-DD format"
                },
                "photo": {
                    "type": "STRING", 
                    "description": "Face photo as base64 string"
                }
            }
        }

        payload = {
            "contents": [{
                "parts": [{
                    "text": """Extract all information from this Japanese Residence Card (在留カード).
                    Include: name, birthday, address, gender, nationality, card number, visa type, and expiry date.
                    Also extract the person's face photo as a base64 encoded string.
                    Return only the JSON object."""
                }, {
                    "inlineData": {
                        "mimeType": mime_type,
                        "data": base64_image
                    }
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": schema,
                "temperature": 0.1
            }
        }

        logger.info("Calling Gemini API...")
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code != 200:
            logger.error(f"Gemini API error: {response.status_code}")
            return {}

        result = response.json()
        text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

        if not text_content:
            logger.warning("Gemini API returned empty content")
            return {}

        # Parse JSON
        import json
        parsed_data = json.loads(text_content)
        logger.info(f"Gemini API extracted: {list(parsed_data.keys())}")

        return parsed_data

    except Exception as e:
        logger.error(f"Error with Gemini API: {e}")
        return {}
```

#### Paso 4: Actualizar el frontend (rirekisho.html)

**Archivo:** `frontend/public/templates/rirekisho.html`

Reemplazar la función `extractTextFromImage`:

```javascript
// ELIMINAR LA CONSTANTE API_KEY
// const API_KEY = "AIzaSy...";  ❌ BORRAR ESTA LÍNEA

// NUEVA FUNCIÓN - Llama al backend en lugar de Gemini directamente
async function extractTextFromImage(base64Image, mimeType) {
    try {
        // Convertir base64 a Blob
        const response = await fetch(`data:${mimeType};base64,${base64Image}`);
        const blob = await response.blob();
        
        // Crear FormData
        const formData = new FormData();
        formData.append('file', blob, 'document.jpg');
        
        // Llamar al backend
        console.log('Enviando imagen al backend...');
        const apiResponse = await fetch('http://localhost:8000/api/ocr/gemini/process', {
            method: 'POST',
            body: formData
        });
        
        if (!apiResponse.ok) {
            const errorData = await apiResponse.json();
            throw new Error(errorData.detail || 'Error en el servidor');
        }
        
        const result = await apiResponse.json();
        
        if (!result.success) {
            throw new Error('OCR falló en el servidor');
        }
        
        return result.data;
        
    } catch (error) {
        console.error('Error llamando al backend:', error);
        throw error;
    }
}
```

---

### SOLUCIÓN 2: Sistema OCR Híbrido con Fallback ⭐ PRIORIDAD MEDIA

**Objetivo:** Usar Gemini primero, si falla usar Vision API, si falla usar Tesseract

**Archivo:** `backend/app/services/ocr_service.py`

Agregar este método:

```python
async def process_zairyu_card_hybrid(self, image_path: str) -> Dict:
    """
    Sistema híbrido: Intenta Gemini → Vision API → Tesseract
    Usa el mejor resultado disponible
    """
    logger.info("Starting hybrid OCR processing")
    
    results = []
    
    # 1. Intentar con Gemini (más rápido y preciso)
    try:
        logger.info("Trying Gemini API...")
        gemini_result = self.extract_text_with_gemini_api(image_path)
        
        if self._validate_result(gemini_result):
            gemini_result['method'] = 'gemini'
            gemini_result['confidence'] = 95
            results.append(gemini_result)
            logger.info("✓ Gemini successful")
        else:
            logger.warning("✗ Gemini returned incomplete data")
            
    except Exception as e:
        logger.warning(f"✗ Gemini failed: {e}")
    
    # 2. Intentar con Vision API (backup)
    try:
        logger.info("Trying Vision API...")
        vision_text = self.extract_text_with_vision_api_direct(image_path)
        vision_result = self.parse_zairyu_card(vision_text)
        
        if self._validate_result(vision_result):
            vision_result['method'] = 'vision_api'
            vision_result['confidence'] = 85
            results.append(vision_result)
            logger.info("✓ Vision API successful")
        else:
            logger.warning("✗ Vision API returned incomplete data")
            
    except Exception as e:
        logger.warning(f"✗ Vision API failed: {e}")
    
    # 3. Fallback a Tesseract (offline, siempre disponible)
    try:
        logger.info("Trying Tesseract...")
        tesseract_text = self.extract_text_with_tesseract_optimized(image_path)
        tesseract_result = self.parse_zairyu_card(tesseract_text)
        
        if self._validate_result(tesseract_result):
            tesseract_result['method'] = 'tesseract'
            tesseract_result['confidence'] = 70
            results.append(tesseract_result)
            logger.info("✓ Tesseract successful")
        else:
            logger.warning("✗ Tesseract returned incomplete data")
            
    except Exception as e:
        logger.warning(f"✗ Tesseract failed: {e}")
    
    # 4. Seleccionar mejor resultado
    if not results:
        raise Exception("All OCR methods failed")
    
    # Ordenar por confianza
    results.sort(key=lambda x: x.get('confidence', 0), reverse=True)
    best_result = results[0]
    
    logger.info(f"Selected best result from {best_result['method']} "
                f"(confidence: {best_result['confidence']}%)")
    
    # 5. Extraer foto si es imagen
    if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        try:
            face_photo = self.extract_face_from_zairyu_card(image_path)
            if face_photo:
                best_result['photo'] = face_photo
        except Exception as e:
            logger.warning(f"Face extraction failed: {e}")
    
    return best_result

def _validate_result(self, result: Dict) -> bool:
    """
    Valida que el resultado tenga datos mínimos
    Considera válido si tiene al menos nombre Y fecha de nacimiento
    """
    has_name = bool(result.get('name'))
    has_birthday = bool(result.get('birthday') or result.get('date_of_birth'))
    
    return has_name and has_birthday
```

---

### SOLUCIÓN 3: Cache de Resultados OCR ⭐ PRIORIDAD BAJA

Para evitar reprocesar la misma imagen:

```python
# En backend/app/services/ocr_service.py

class OCRService:
    def __init__(self):
        self.tesseract_lang = settings.TESSERACT_LANG
        self.use_vision_api = True
        self.vision_api_key = settings.GOOGLE_CLOUD_VISION_API_KEY
        
        # NUEVO: Cache en memoria
        self.cache = {}
        
    def _get_image_hash(self, image_path: str) -> str:
        """Calcula hash MD5 de la imagen para cache"""
        import hashlib
        
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        return file_hash
    
    async def process_zairyu_card_hybrid(self, image_path: str) -> Dict:
        """Sistema híbrido con cache"""
        
        # 1. Verificar cache
        image_hash = self._get_image_hash(image_path)
        
        if image_hash in self.cache:
            logger.info(f"Cache hit for image {image_hash}")
            return self.cache[image_hash]
        
        # 2. Procesar (código anterior)
        result = # ... procesar con Gemini/Vision/Tesseract
        
        # 3. Guardar en cache
        self.cache[image_hash] = result
        
        return result
```

---

## 📦 OTRAS MEJORAS RECOMENDADAS

### 4. Sistema de Notificaciones Automáticas 📧

**Archivo:** `backend/app/services/notification_service.py` (NUEVO)

```python
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

from app.core.config import settings


class NotificationService:
    """Servicio centralizado de notificaciones"""
    
    def send_email(self, to: str, subject: str, body: str):
        """Enviar email usando SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_FROM
            msg['To'] = to
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_line_notification(self, user_id: str, message: str):
        """Enviar notificación por LINE Messaging API"""
        try:
            url = "https://api.line.me/v2/bot/message/push"
            headers = {
                "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            data = {
                "to": user_id,
                "messages": [{"type": "text", "text": message}]
            }
            
            response = requests.post(url, headers=headers, json=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Error sending LINE notification: {e}")
            return False
    
    def notify_yukyu_approval(self, employee_id: int, status: str):
        """Notificar aprobación/rechazo de yukyu"""
        from app.models import Employee
        from app.database import SessionLocal
        
        db = SessionLocal()
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            return
        
        # Email
        subject = "有給申請の結果通知"
        body = f"""
        <html>
            <body>
                <h2>{employee.full_name_kanji}様</h2>
                <p>有給休暇の申請が<strong>{status}</strong>されました。</p>
                <p>詳細はシステムをご確認ください。</p>
            </body>
        </html>
        """
        
        if employee.email:
            self.send_email(employee.email, subject, body)
        
        # LINE
        if employee.line_user_id:
            line_message = f"有給休暇の申請が{status}されました。詳細はシステムをご確認ください。"
            self.send_line_notification(employee.line_user_id, line_message)
        
        db.close()


# Instancia global
notification_service = NotificationService()
```

**Configurar variables en .env:**

```bash
# Email SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=notifications@uns-kikaku.com

# LINE Messaging API
LINE_CHANNEL_ACCESS_TOKEN=your-line-channel-access-token
```

---

### 5. Importación Masiva desde Excel 📊

**Archivo:** `backend/app/services/import_service.py` (NUEVO)

```python
import pandas as pd
from typing import List, Dict
from datetime import datetime

from app.models import Employee
from app.database import SessionLocal


class ImportService:
    """Servicio para importación masiva de datos"""
    
    def import_employees_from_excel(self, file_path: str) -> Dict:
        """
        Importa empleados desde Excel con validación
        
        Formato esperado del Excel:
        | 派遣元ID | 氏名 | フリガナ | 生年月日 | 性別 | 国籍 | ... |
        """
        try:
            # Leer Excel
            df = pd.read_excel(file_path)
            
            results = {
                "success": [],
                "errors": [],
                "warnings": [],
                "total": len(df)
            }
            
            db = SessionLocal()
            
            for index, row in df.iterrows():
                try:
                    # Validar datos requeridos
                    validation_errors = self._validate_employee_data(row)
                    
                    if validation_errors:
                        results["errors"].append({
                            "row": index + 2,  # +2 para header
                            "errors": validation_errors
                        })
                        continue
                    
                    # Verificar si ya existe
                    existing = db.query(Employee).filter(
                        Employee.hakenmoto_id == str(row['派遣元ID'])
                    ).first()
                    
                    if existing:
                        results["warnings"].append({
                            "row": index + 2,
                            "message": f"Empleado ya existe: {row['氏名']}"
                        })
                        continue
                    
                    # Crear empleado
                    employee = Employee(
                        hakenmoto_id=str(row['派遣元ID']),
                        full_name_kanji=row['氏名'],
                        full_name_kana=row['フリガナ'],
                        date_of_birth=pd.to_datetime(row['生年月日']),
                        gender=row['性別'],
                        nationality=row['国籍'],
                        phone_mobile=str(row.get('携帯電話', '')),
                        address=row.get('住所', ''),
                        # ... más campos según tu schema
                    )
                    
                    db.add(employee)
                    db.commit()
                    
                    results["success"].append({
                        "row": index + 2,
                        "name": employee.full_name_kanji,
                        "id": employee.id
                    })
                    
                except Exception as e:
                    db.rollback()
                    results["errors"].append({
                        "row": index + 2,
                        "error": str(e)
                    })
            
            db.close()
            
            return results
            
        except Exception as e:
            return {
                "success": [],
                "errors": [{"error": f"Error leyendo archivo: {str(e)}"}],
                "warnings": [],
                "total": 0
            }
    
    def _validate_employee_data(self, row: pd.Series) -> List[str]:
        """Valida los datos de un empleado"""
        errors = []
        
        # Campos requeridos
        required_fields = ['派遣元ID', '氏名', 'フリガナ', '生年月日', '性別']
        
        for field in required_fields:
            if pd.isna(row.get(field)):
                errors.append(f"Campo requerido faltante: {field}")
        
        # Validar formato de fecha
        if not pd.isna(row.get('生年月日')):
            try:
                pd.to_datetime(row['生年月日'])
            except:
                errors.append("Formato de fecha inválido en 生年月日")
        
        # Validar género
        if row.get('性別') not in ['男性', '女性', None]:
            errors.append("性別 debe ser '男性' o '女性'")
        
        return errors


# Instancia global
import_service = ImportService()
```

**Endpoint para usar:**

```python
# backend/app/api/import_export.py (NUEVO)

from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.import_service import import_service

router = APIRouter()


@router.post("/import/employees")
async def import_employees(file: UploadFile = File(...)):
    """Importa empleados desde Excel"""
    
    # Validar extensión
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Solo archivos Excel (.xlsx, .xls)")
    
    # Guardar temporalmente
    import os
    temp_path = f"/tmp/{file.filename}"
    
    try:
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Importar
        results = import_service.import_employees_from_excel(temp_path)
        
        return results
        
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_path):
            os.remove(temp_path)
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

### Prioridad CRÍTICA (Hacer Ya):
- [ ] Mover API Key de Gemini al backend
- [ ] Crear endpoint `/api/ocr/gemini/process`
- [ ] Actualizar `rirekisho.html` para usar backend
- [ ] Probar que OCR funciona desde backend
- [ ] Eliminar API Key del frontend

### Prioridad ALTA (Esta Semana):
- [ ] Implementar sistema OCR híbrido con fallback
- [ ] Agregar validación de resultados OCR
- [ ] Implementar cache de resultados
- [ ] Agregar logging detallado

### Prioridad MEDIA (Próximas 2 Semanas):
- [ ] Sistema de notificaciones (Email)
- [ ] Importación masiva desde Excel
- [ ] Agregar tests unitarios para OCR
- [ ] Documentar APIs nuevas

### Prioridad BAJA (Futuro):
- [ ] Notificaciones LINE/WhatsApp
- [ ] Reportes automáticos mensuales
- [ ] Dashboard en tiempo real
- [ ] Sistema de auditoría

---

## 🧪 CÓMO PROBAR LAS MEJORAS

### 1. Probar OCR desde Backend:

```bash
# Terminal 1: Levantar backend
cd backend
docker-compose up backend

# Terminal 2: Probar endpoint
curl -X POST "http://localhost:8000/api/ocr/gemini/process" \
  -F "file=@/path/to/zairyu_card.jpg"
```

### 2. Probar desde Frontend:

```bash
# Abrir en navegador
http://localhost:3000/templates/rirekisho.html

# Subir imagen de 在留カード
# Verificar en consola del navegador que llama al backend
```

### 3. Verificar Logs:

```bash
# Ver logs del backend
docker logs uns-claudejp-backend -f --tail 50

# Deberías ver:
# "Processing image with Gemini: document.jpg"
# "OCR successful"
```

---

## 📞 SOPORTE

Si necesitas ayuda implementando alguna de estas mejoras:

1. Lee primero la documentación de cada sección
2. Verifica que tienes las dependencias instaladas
3. Revisa los logs para encontrar errores específicos
4. Contacta al equipo de desarrollo

---

**Última actualización:** 2025-10-07
**Versión:** 2.0
**Estado:** Pendiente de Implementación
