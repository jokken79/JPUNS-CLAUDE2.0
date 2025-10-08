# 🚀 GUÍA PASO A PASO - Fix Crítico (30 minutos)

## 🎯 OBJETIVO
Mover la API Key de Gemini del frontend al backend para mayor seguridad.

---

## PASO 1: Crear archivo backend/app/api/ocr.py (5 min)

### 1.1 Crear el archivo
```bash
cd D:\JPUNS-app\JPUNS-CLAUDE2.0\backend\app\api
```

### 1.2 Crear nuevo archivo `ocr.py` con este contenido:

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

✅ **Archivo creado:** `backend/app/api/ocr.py`

---

## PASO 2: Registrar router en main.py (2 min)

### 2.1 Abrir archivo
```bash
Abrir: D:\JPUNS-app\JPUNS-CLAUDE2.0\backend\app\main.py
```

### 2.2 Buscar la sección de imports de routers (aprox línea 10-20)
```python
# Imports actuales
from app.api import auth, candidates, employees, ...
```

### 2.3 Agregar esta línea:
```python
from app.api import auth, candidates, employees, ocr  # ← AGREGAR ocr
```

### 2.4 Buscar donde están los `include_router` (aprox línea 80-100)
```python
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["candidates"])
# ... más routers
```

### 2.5 Agregar esta línea:
```python
app.include_router(ocr.router, prefix="/api/ocr", tags=["OCR"])  # ← NUEVA LÍNEA
```

✅ **Archivo modificado:** `backend/app/main.py`

---

## PASO 3: Actualizar ocr_service.py (5 min)

### 3.1 Abrir archivo
```bash
Abrir: D:\JPUNS-app\JPUNS-CLAUDE2.0\backend\app\services\ocr_service.py
```

### 3.2 Buscar la clase `OCRService` (aprox línea 30)

### 3.3 Agregar este método NUEVO al final de la clase (antes del cierre):

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

            logger.info("Calling Gemini API from base64...")
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

✅ **Método agregado:** `extract_text_with_gemini_api_from_base64()`

---

## PASO 4: Actualizar rirekisho.html (10 min)

### 4.1 Abrir archivo
```bash
Abrir: D:\JPUNS-app\JPUNS-CLAUDE2.0\frontend\public\templates\rirekisho.html
```

### 4.2 ELIMINAR la línea con API_KEY (aprox línea 139):
```javascript
// BORRAR ESTA LÍNEA:
const API_KEY = "AIzaSyDL32fmwB7SdbL6yEV3GbSP9dYhHdG1JXw"; // ❌ ELIMINAR
```

### 4.3 Buscar la función `extractTextFromImage` (aprox línea 650)

### 4.4 REEMPLAZAR toda la función con:

```javascript
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
        
        console.log('✓ OCR exitoso desde backend');
        return result.data;
        
    } catch (error) {
        console.error('Error llamando al backend:', error);
        throw error;
    }
}
```

✅ **Archivo modificado:** `rirekisho.html`

---

## PASO 5: Reiniciar servicios (5 min)

### 5.1 Abrir terminal en la raíz del proyecto
```bash
cd D:\JPUNS-app\JPUNS-CLAUDE2.0
```

### 5.2 Reiniciar backend
```bash
docker-compose restart backend
```

### 5.3 Esperar 10 segundos

### 5.4 Verificar logs
```bash
docker logs uns-claudejp-backend --tail 20
```

**Deberías ver:**
```
✅ Usuario admin actualizado exitosamente
✅ Bcrypt warmed up successfully
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ **Backend reiniciado correctamente**

---

## PASO 6: Probar que funciona (3 min)

### 6.1 Abrir navegador
```
http://localhost:3000/templates/rirekisho.html
```

### 6.2 Hard refresh (limpiar cache)
```
Ctrl + Shift + R
```

### 6.3 Abrir consola del navegador
```
F12 → Console
```

### 6.4 Subir imagen de 在留カード

### 6.5 Verificar en consola:
```
✓ Enviando imagen al backend...
✓ OCR exitoso desde backend
```

### 6.6 Verificar que el formulario se auto-rellena

✅ **Sistema funcionando desde el backend**

---

## PASO 7: Verificar seguridad (2 min)

### 7.1 En el navegador, presiona F12

### 7.2 Ve a la pestaña "Sources" o "Fuentes"

### 7.3 Abre `rirekisho.html`

### 7.4 Busca (Ctrl+F): "AIzaSy"

### 7.5 Verificar:
```
❌ NO debe aparecer la API Key
✅ Solo debe haber la llamada al backend
```

✅ **API Key protegida**

---

## ✅ CHECKLIST FINAL

- [ ] Archivo `backend/app/api/ocr.py` creado
- [ ] Router registrado en `main.py`
- [ ] Método `extract_text_with_gemini_api_from_base64()` agregado
- [ ] API Key eliminada de `rirekisho.html`
- [ ] Función `extractTextFromImage()` actualizada
- [ ] Backend reiniciado
- [ ] Frontend probado con imagen real
- [ ] OCR funciona correctamente
- [ ] API Key NO visible en código fuente
- [ ] Logs muestran "Processing image with Gemini"

---

## 🐛 TROUBLESHOOTING

### Problema 1: "Module 'ocr' has no attribute 'router'"
**Solución:**
```bash
# Verificar que ocr.py existe
ls backend/app/api/ocr.py

# Verificar que tiene router = APIRouter()
cat backend/app/api/ocr.py | grep "router = APIRouter"

# Reiniciar
docker-compose restart backend
```

### Problema 2: "404 Not Found" al llamar /api/ocr/gemini/process
**Solución:**
```bash
# Verificar que el router está registrado
docker logs uns-claudejp-backend | grep "OCR"

# Debería aparecer:
# INFO: Route: POST /api/ocr/gemini/process
```

### Problema 3: Frontend sigue usando API Key vieja
**Solución:**
```bash
# Hard refresh en navegador
Ctrl + Shift + R

# O limpiar cache completo
Ctrl + Shift + Delete → Limpiar caché
```

### Problema 4: "OCR falló en el servidor"
**Solución:**
```bash
# Ver logs detallados
docker logs uns-claudejp-backend -f

# Verificar que Gemini API Key está en .env
cat .env | grep GOOGLE_CLOUD_VISION_API_KEY
```

---

## 📊 RESULTADO ESPERADO

### Antes:
```javascript
// Frontend
const API_KEY = "AIzaSy..."; // ❌ Público
fetch('https://generativelanguage.googleapis.com/...')
```

### Después:
```javascript
// Frontend
// ✅ Sin API Key
fetch('http://localhost:8000/api/ocr/gemini/process')

// Backend (privado)
// ✅ API Key en settings/env
ocr_service.extract_text_with_gemini_api_from_base64(...)
```

**Ventajas:**
- ✅ API Key protegida
- ✅ Control de acceso centralizado
- ✅ Logs de uso
- ✅ Rate limiting posible
- ✅ Cache futuro
- ✅ Fallback a otros OCR

---

## 🎉 ¡FELICITACIONES!

Si llegaste hasta aquí y todo funciona:

✅ **Tu sistema es ahora mucho más seguro**
✅ **API Key está protegida en el backend**
✅ **Preparado para mejoras futuras**

---

## 📚 PRÓXIMOS PASOS

1. **Leer documento completo:** `docs/MEJORAS_RECOMENDADAS.md`
2. **Implementar cache de OCR** (1 hora)
3. **Sistema OCR híbrido** (2 horas)
4. **Notificaciones automáticas** (3 horas)

---

**Tiempo total:** ~30 minutos
**Dificultad:** ⭐⭐ (Fácil)
**Impacto:** 🔥🔥🔥 (Alto)
**Prioridad:** 🔴 CRÍTICA

---

¡Éxito con la implementación! 🚀
