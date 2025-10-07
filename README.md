# UNS-ClaudeJP 2.0

Sistema Integral de Gestión de Personal Temporal para UNS-Kikaku

> ✅ **ACTUALIZACIÓN:** El sistema ahora inicializa automáticamente el usuario admin al arrancar. No más problemas de login al reiniciar Docker.

## 🎯 Características Principales

### 📋 Módulo de Reclutamiento (履歴書管理)
- ✅ **OCR automático de 在留カード** - Sistema híbrido con múltiples estrategias
- ✅ Extracción automática de foto del rostro (60px padding, face detection con OpenCV)
- ✅ Lectura automática de datos:
  - 氏名 (NAME) - Nombres japoneses y occidentales
  - 生年月日 (Birthday) - Formato YYYY-MM-DD
  - 年齢 (Age) - Cálculo automático desde fecha de nacimiento
  - 性別 (Gender) - 男性/女性
  - 国籍 (Nationality) - Con mapeo a japonés (ベトナム, ブラジル, etc.)
  - 住所 (Address)
  - 番号 (Card Number)
  - 在留資格 (Visa Type)
  - ビザ期間 (Visa Duration)
- ✅ **Sistema OCR Multi-Estrategia** (100% Offline & Gratis):
  - Tesseract OCR optimizado para tarjetas japonesas
  - 9 combinaciones de preprocesamiento (3 métodos × 3 PSM modes)
  - Upscaling 4x con interpolación LANCZOS4
  - CLAHE para mejor contraste
  - Detección inteligente de nombres (4 estrategias)
- ✅ Generación automática de ID (UNS-XXXXXX)
- ✅ Sistema de 入社届 automático
- ✅ Gestión de documentos (PDF/JPG, máx 10MB)

### 👥 Módulo de Personal
- ✅ Base de datos centralizada con 4 IDs:
  - **UNS-XXXX**: ID de Candidato/Rirekisho
  - **Hakenmoto ID**: ID interno (solo números)
  - **Factory-XX**: ID de Fábrica
  - **Hakensaki Shain ID**: ID del trabajador en fábrica (editable)

### 🏭 Módulo de Fábricas (20+ fábricas)
- ✅ Configuración JSON por fábrica
- ✅ Horarios personalizados (朝番/昼番/夜番)
- ✅ 時給単価 por fábrica/posición
- ✅ Premios y bonificaciones configurables

### ⏰ Módulo de Timer Cards
- ✅ Upload masivo (PDF/imágenes escaneadas)
- ✅ OCR con corrección manual
- ✅ Tabla Excel editable
- ✅ Múltiples formatos de fábricas

### 💰 Módulo de Nómina
- ✅ Cálculo automático con:
  - Horas normales/extras (25%/35%)
  - 深夜手当 (nocturno)
  - 休日出勤 (festivos)
  - Premios, gasolina, etc.
- ✅ Gestión de apartamentos con cálculo proporcional
- ✅ Comparativa 時給 vs 時給単価 (ganancia)

### 📋 Módulo de Solicitudes
- ✅ 有給休暇 (yukyu) + 半日有給
- ✅ 一時帰国 (salidas temporales)
- ✅ 退社報告 (taisha houkoku)
- ✅ Firma electrónica de contratos

### 📊 Dashboard & Reportes
- ✅ 3 niveles de usuarios:
  - **Super Admin**: Control total
  - **Admin**: Gestión por fábrica
  - **CO (Coordinadores)**: Vista de lectura
  - **Funcionarios**: Vista personal + solicitudes
- ✅ Ganancias por fábrica en tiempo real
- ✅ Historial completo de pagos
- ✅ Reportes exportables

### 🔔 Notificaciones
- ✅ Email automático
- ✅ LINE/WhatsApp/Messenger (opcional)

## 🛠 Stack Tecnológico

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: Python FastAPI
- **Database**: PostgreSQL
- **OCR**: Tesseract OCR + Google Cloud Vision API
- **Storage**: Local file system
- **Container**: Docker + Docker Compose
- **Deploy**: Synology NAS (Docker)

## 📦 Estructura del Proyecto

```
uns-claudejp/
├── backend/           # API Python FastAPI
│   ├── app/
│   │   ├── api/      # Endpoints
│   │   ├── core/     # Configuración
│   │   ├── models/   # Modelos DB
│   │   ├── schemas/  # Schemas Pydantic
│   │   ├── services/ # Lógica de negocio
│   │   └── utils/    # Utilidades (OCR, etc)
│   └── tests/
├── frontend/          # React App
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   └── public/
├── database/          # Migraciones y seeds
├── docker/           # Dockerfiles
├── config/           # Configs JSON fábricas
└── docs/             # Documentación

## 🚀 Instalación

### Prerequisitos
- Docker
- Docker Compose
- Synology NAS con Docker instalado

### Pasos

1. Clonar el proyecto en Synology NAS
```bash
cd /volume1/docker
git clone [repository]
cd uns-claudejp
```

2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Levantar con Docker Compose
```bash
docker-compose up -d
```

4. Acceder a la aplicación
```
http://[synology-ip]:3000
```

## 📝 Configuración de Fábricas

Las configuraciones de fábricas se manejan en archivos JSON en `config/factories/`:

```json
{
  "factory_id": "Factory-01",
  "name": "Toyota Factory Aichi",
  "shifts": [
    {
      "name": "朝番",
      "start": "08:00",
      "end": "17:00",
      "jikyu_tanka": 1500,
      "night_premium": false
    },
    {
      "name": "夜番", 
      "start": "20:00",
      "end": "05:00",
      "jikyu_tanka": 1800,
      "night_premium": true,
      "premium_rate": 0.25
    }
  ],
  "bonuses": {
    "gasoline": true,
    "apartment": true
  }
}
```

## 🔐 Niveles de Acceso

| Rol | Permisos |
|-----|----------|
| Super Admin | Control total del sistema |
| Admin | Gestión de fábricas asignadas |
| CO (Coordinador) | Vista de lectura |
| Funcionario | Ver datos propios + solicitudes |

## 📱 Uso Móvil

La aplicación es **Progressive Web App (PWA)**, funciona en:
- ✅ Navegadores de escritorio
- ✅ Tablets
- ✅ Smartphones (iOS/Android)
- ✅ Puede instalarse como app nativa

## 📞 Soporte

Para soporte técnico:
- Email: support@uns-kikaku.com
- Web: https://uns-kikaku.com

## 🔬 Documentación Técnica - Sistema OCR

### Sistema de OCR para 在留カード (Tarjetas de Residencia)

#### Arquitectura del Sistema

**Ubicación del código:** `backend/app/services/ocr_service.py`

El sistema implementa una solución **100% offline, gratuita e ilimitada** usando Tesseract OCR con optimizaciones específicas para tarjetas de identificación japonesas.

#### Características Técnicas

**1. Extracción de Foto del Rostro**
```python
def extract_face_from_zairyu_card(image_path) -> base64
```
- Usa OpenCV face detection (Haar Cascade)
- Padding de 60px alrededor del rostro detectado
- Fallback a posición típica si no detecta rostro (top-right corner)
- Resize a 150x180px (tamaño estándar foto pasaporte)
- Retorna imagen en base64 para inserción directa en formulario

**2. Preprocesamiento Multi-Estrategia**

El sistema prueba **9 combinaciones diferentes**:

**Métodos de Preprocesamiento:**
- **Strategy 1**: High contrast upscale con Otsu threshold
- **Strategy 2**: CLAHE (Contrast Limited Adaptive Histogram Equalization)
- **Strategy 3**: Adaptive threshold Gaussian

**PSM Modes de Tesseract:**
- `PSM 6`: Uniform block of text (mejor para bloques de texto)
- `PSM 11`: Sparse text (mejor para texto disperso)
- `PSM 3`: Fully automatic (detección automática)

**Proceso de Selección:**
```python
# Cuenta caracteres significativos (excluye ruido)
meaningful_chars = len(re.findall(r'[a-zA-Z一-龯ぁ-んァ-ヶー0-9]', text))

# Selecciona el resultado con más caracteres legibles
if meaningful_chars > best_length:
    best_text = text
```

**3. Extracción y Parseo de Datos**

**Campos extraídos:**
- ✅ 氏名 (NAME) - 4 estrategias de detección
- ✅ 生年月日 (Birthday) - Conversión automática a YYYY-MM-DD
- ✅ 性別 (Gender) - Mapeo M/F → 男性/女性
- ✅ 国籍 (Nationality) - Mapeo inglés→japonés (VIETNAM→ベトナム)
- ✅ 住所 (Address) - Detección de patrones de dirección japonesa
- ✅ 番号 (Card Number) - Pattern: XX1234567890
- ✅ 在留資格 (Visa Status)
- ✅ ビザ期間 (Visa Duration) - Extracción de fecha "このカードは...まで有効"

**4. Estrategias de Detección de Nombres**

```python
# Strategy 1: Campo 氏名 directo
pattern = r'氏\s*名[：:\s　]*([^\n\s]{2,20})'

# Strategy 2: Campo NAME en inglés
# Busca "NAME" y lee las siguientes 3 líneas

# Strategy 3: Nombres occidentales (capitalización)
pattern = r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,2})$'

# Strategy 4: Caracteres japoneses (kanji/kana)
pattern = r'([一-龯ぁ-んァ-ヶー]{2,}(?:\s*[一-龯ぁ-んァ-ヶー]+)?)'
```

**5. Integración Frontend-Backend**

**Frontend:** `frontend/public/templates/rirekisho.html`
```javascript
// Llama al backend con FormData
const formData = new FormData();
formData.append('file', file);
formData.append('document_type', 'zairyu_card');

const response = await fetch('http://localhost:8000/api/candidates/ocr/process', {
    method: 'POST',
    body: formData
});
```

**Backend Endpoint:** `backend/app/api/candidates.py`
```python
@router.post("/ocr/process")
async def process_ocr_document(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    ocr_result = ocr_service.process_document(tmp_path, document_type)
    return {"success": True, "data": ocr_result}
```

#### Flujo de Procesamiento

```
1. Usuario sube 在留カード
   ↓
2. Frontend envía archivo al backend
   ↓
3. Backend guarda archivo temporal
   ↓
4. OCR Service:
   a. Extrae foto del rostro (OpenCV)
   b. Prueba 9 combinaciones OCR (Tesseract)
   c. Selecciona mejor resultado
   d. Parsea texto con 4 estrategias por campo
   ↓
5. Retorna JSON con datos + foto en base64
   ↓
6. Frontend auto-rellena formulario:
   - Coloca foto en preview
   - Rellena todos los campos
   - Calcula edad automáticamente
   - Convierte nombre a katakana (si aplica)
```

#### Optimizaciones Implementadas

**Preprocesamiento de Imagen:**
- ✅ Upscaling 4x con LANCZOS4 (mejor para texto pequeño)
- ✅ CLAHE para mejorar contraste en áreas oscuras
- ✅ Denoising con fastNlMeans (preserva bordes)
- ✅ Sharpening con kernel 5×5
- ✅ Otsu threshold adaptativo

**Configuración Tesseract:**
```python
config = '--oem 3 --psm X -c preserve_interword_spaces=1'
# --oem 3: Usa LSTM neural network (mejor precisión)
# --psm X: Page Segmentation Mode variable
# preserve_interword_spaces: Mantiene espacios entre palabras
```

#### Ventajas del Sistema Actual

| Característica | Gemini API | Vision API | Tesseract Optimizado |
|----------------|------------|------------|----------------------|
| **Costo** | Cuota 250/día | Cuota limitada | **100% Gratis** ✅ |
| **Offline** | ❌ Requiere internet | ❌ Requiere internet | **✅ Funciona offline** |
| **Velocidad** | ~2-3s | ~2-3s | **~1-2s** ✅ |
| **Precisión** | 95% | 85% | **75-85%** (depende de imagen) |
| **Ilimitado** | ❌ 250 req/día | ❌ Cuota limitada | **✅ Sin límites** |

#### Requisitos de Calidad de Imagen

Para mejores resultados, la imagen debe:
- ✅ Resolución mínima: 1200×800px
- ✅ Enfoque nítido (texto legible a simple vista)
- ✅ Iluminación uniforme (sin sombras)
- ✅ Sin reflejos en texto
- ✅ Ángulo perpendicular (0° de inclinación)
- ✅ Formato: JPG, PNG (máx 5MB)

#### Archivos Modificados

```
backend/app/services/ocr_service.py
├── preprocess_for_japanese_id()      # Preprocesamiento optimizado
├── extract_text_with_tesseract_optimized()  # OCR multi-estrategia
├── extract_face_from_zairyu_card()   # Extracción de foto
└── parse_zairyu_card()               # Parser inteligente

backend/app/api/candidates.py
└── POST /api/candidates/ocr/process  # Endpoint sin autenticación

frontend/public/templates/rirekisho.html
├── processOCR()                      # Manejador de upload
├── extractTextFromImage()            # Cliente API
└── Auto-fill logic                   # Mapeo de campos
```

## 📄 Licencia

Propiedad de UNS-Kikaku © 2025

---

## 📄 Nueva Implementación de OCR (Octubre 2025)

Se ha reemplazado el sistema de OCR basado en Tesseract por una nueva implementación que utiliza la **API de Gemini Pro** directamente desde el frontend.

### Detalles de la Nueva Implementación

*   **Tecnología:** Google Gemini Pro (`gemini-2.5-flash-preview-05-20`).
*   **Ubicación del Código:** La lógica principal se encuentra en `frontend/public/templates/rirekisho.html`.
*   **Arquitectura:** La nueva implementación es **100% frontend**. El navegador del cliente envía la imagen directamente a la API de Google, eliminando la necesidad de un endpoint de OCR en el backend.
*   **Extracción de Datos:** Se utiliza la funcionalidad de **salida estructurada (JSON)** de Gemini para garantizar una extracción de datos fiable. El esquema de extracción incluye:
    *   `name` (nombre)
    *   `birthday` (fecha de nacimiento)
    *   `address` (dirección)
    *   `photo` (foto del rostro en base64)
*   **Clave de API:** La clave de la API de Google está actualmente **hardcodeada** en el archivo `rirekisho.html`.

### TODO

*   **[IMPORTANTE]** Mover la clave de la API de Google desde el código del frontend a una variable de entorno en el backend y crear un nuevo endpoint que actúe como proxy. Esto es crucial para la seguridad y para evitar el abuso de la clave de API.

---

**Desarrollado con ❤️ por Claude & UNS-Kikaku Team**
```
#   J P U N S - C L A U D E 2 . 0  
 