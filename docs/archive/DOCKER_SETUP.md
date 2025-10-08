# Configuración Docker - UNS-ClaudeJP 2.0

## 📦 Contenedores

### 1. Backend (FastAPI + OCR)

**Dockerfile:** `docker/Dockerfile.backend`

**Imagen base:** `python:3.11-slim`

**Dependencias del sistema instaladas:**
```bash
# OCR (Optical Character Recognition)
tesseract-ocr          # Motor OCR principal
tesseract-ocr-jpn      # Datos de entrenamiento para japonés
tesseract-ocr-eng      # Datos de entrenamiento para inglés
libtesseract-dev       # Librerías de desarrollo

# OpenCV & Procesamiento de imágenes
libgl1-mesa-glx        # OpenGL para operaciones gráficas
libglib2.0-0           # Librería GLib (dependencia de OpenCV)
libsm6                 # Session Management Library
libxext6               # X11 extensions
libxrender-dev         # X Rendering Extension
libgomp1               # OpenMP runtime (paralelización)

# PDF Processing
poppler-utils          # Herramientas para convertir PDF a imágenes

# PostgreSQL
libpq-dev              # Librería PostgreSQL para compilar psycopg2

# Compilación
gcc                    # GNU C Compiler
g++                    # GNU C++ Compiler
```

**Puertos expuestos:**
- `8000`: API FastAPI

**Volúmenes montados:**
```yaml
volumes:
  - ./backend:/app                # Código fuente (hot reload)
  - ./uploads:/app/uploads        # Archivos subidos
  - ./config:/app/config          # Configuración
```

**Variables de entorno importantes:**
```bash
DATABASE_URL                      # Conexión a PostgreSQL
GOOGLE_CLOUD_VISION_API_KEY      # API key para Vision API (opcional)
GOOGLE_CLOUD_VISION_ENABLED      # true/false
OCR_ENABLED                      # true/false
TESSERACT_LANG                   # jpn+eng
```

---

### 2. Frontend (React)

**Dockerfile:** `docker/Dockerfile.frontend`

**Imagen base:** `node:18-alpine`

**Puertos expuestos:**
- `3000`: Servidor de desarrollo React

**Volúmenes montados:**
```yaml
volumes:
  - ./frontend:/app
  - /app/node_modules  # Previene conflictos con node_modules local
```

---

### 3. Database (PostgreSQL)

**Imagen:** `postgres:15-alpine`

**Puertos expuestos:**
- `5432`: PostgreSQL

**Volúmenes:**
```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data  # Datos persistentes
  - ./database/migrations:/docker-entrypoint-initdb.d  # Migrations iniciales
```

**Variables de entorno:**
```bash
POSTGRES_DB=uns_claudejp
POSTGRES_USER=uns_admin
POSTGRES_PASSWORD=${DB_PASSWORD}
```

---

## 🚀 Comandos Docker

### Construcción inicial
```bash
# Construir todos los servicios
docker-compose build

# Construir solo backend
docker-compose build backend

# Construir sin caché
docker-compose build --no-cache
```

### Ejecución
```bash
# Iniciar todos los servicios
docker-compose up -d

# Iniciar con logs visibles
docker-compose up

# Iniciar solo un servicio
docker-compose up -d backend
```

### Reiniciar servicios
```bash
# Reiniciar todos
docker-compose restart

# Reiniciar solo backend (después de cambios en código)
docker-compose restart backend

# Reiniciar con rebuild
docker-compose up -d --build backend
```

### Logs
```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs solo del backend
docker-compose logs -f backend

# Ver últimas 100 líneas
docker-compose logs --tail=100 backend
```

### Detener y limpiar
```bash
# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (¡CUIDADO! Borra la DB)
docker-compose down -v

# Detener y eliminar todo (imágenes, volúmenes, redes)
docker-compose down -v --rmi all
```

### Acceso a contenedores
```bash
# Entrar al contenedor backend
docker-compose exec backend bash

# Entrar al contenedor de base de datos
docker-compose exec db psql -U uns_admin -d uns_claudejp

# Ejecutar comando en backend sin entrar
docker-compose exec backend python -m pytest
```

---

## 🔧 Dependencias Python Críticas para OCR

En `backend/requirements.txt`:

```python
# === CORE OCR STACK ===
pytesseract==0.3.10              # Python wrapper para Tesseract
opencv-python-headless==4.8.1.78 # Procesamiento de imágenes (sin GUI)
numpy==1.26.2                    # Operaciones matemáticas para OpenCV
Pillow==10.1.0                   # PIL - Python Imaging Library

# === DOCUMENTO PROCESSING ===
pdf2image==1.16.3                # PDF → Images para OCR

# === APIS EXTERNAS (OPCIONAL) ===
google-cloud-vision==3.4.5       # Google Cloud Vision API
requests==2.31.0                 # HTTP client para APIs
```

### Instalación en contenedor running
```bash
# Si necesitas agregar una dependencia nueva
docker-compose exec backend pip install nombre-paquete

# Y luego actualiza requirements.txt
docker-compose exec backend pip freeze > requirements.txt
```

---

## 🐛 Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'cv2'"
**Solución:**
```bash
docker-compose exec backend pip install opencv-python-headless
docker-compose restart backend
```

### Problema: "TesseractNotFoundError"
**Solución:** Verifica que Tesseract esté instalado en el contenedor
```bash
docker-compose exec backend tesseract --version
```

Si no está instalado, rebuild el contenedor:
```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Problema: OCR extrae texto basura
**Posibles causas:**
1. **Calidad de imagen mala** → Usar imagen de mejor calidad
2. **Idioma no instalado** → Verificar `tesseract --list-langs`
3. **Preprocesamiento inadecuado** → Revisar `ocr_service.py`

**Verificar idiomas instalados:**
```bash
docker-compose exec backend tesseract --list-langs
```

Debe mostrar:
```
List of available languages (3):
eng
jpn
osd
```

### Problema: Base de datos no conecta
**Solución:**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Ver logs de la base de datos
docker-compose logs db

# Verificar conexión desde backend
docker-compose exec backend python -c "from app.core.database import engine; print(engine)"
```

### Problema: Frontend no actualiza cambios
**Solución:**
```bash
# Limpiar caché y reconstruir
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

---

## 📊 Estructura de Volúmenes

```
D:\JPUNS-app\JPUNS-CLAUDE2.0\
├── backend/              → Montado en /app (backend container)
├── frontend/             → Montado en /app (frontend container)
├── uploads/              → Montado en /app/uploads (backend)
│   ├── candidates/       → 在留カード, 免許証
│   ├── rirekisho/        → PDFs de rirekisho
│   └── timer_cards/      → Timer cards escaneados
├── config/               → Montado en /app/config (backend)
│   └── gcp-credentials.json
└── database/
    └── migrations/       → Scripts SQL iniciales
```

---

## 🔐 Seguridad

### Archivos que NO deben estar en Git:
```
.env                      # Variables de entorno sensibles
config/gcp-credentials.json  # Credenciales de Google Cloud
uploads/*                 # Archivos subidos por usuarios
*.pyc                     # Python compiled
__pycache__/              # Python cache
node_modules/             # Node dependencies
```

### Variables sensibles en `.env`:
```bash
DB_PASSWORD=             # Password de PostgreSQL
SECRET_KEY=              # JWT secret key
GOOGLE_CLOUD_VISION_API_KEY=  # API key de Google
EMAIL_PASSWORD=          # Password de email
```

---

## 📝 Checklist de Deploy

- [ ] `.env` configurado con valores de producción
- [ ] `docker-compose.yml` usa versión correcta de imágenes
- [ ] Volúmenes de base de datos persistentes configurados
- [ ] Backups automáticos de PostgreSQL configurados
- [ ] Logs rotando correctamente (logrotate)
- [ ] Tesseract con idiomas japonés e inglés instalados
- [ ] OpenCV funcionando (face detection)
- [ ] API keys válidas y con cuotas suficientes
- [ ] Frontend compilado en modo producción
- [ ] CORS configurado correctamente
- [ ] SSL/HTTPS configurado (si aplica)

---

## 🔄 Actualización de la Aplicación

### Actualizar desde Git
```bash
# 1. Detener servicios
docker-compose down

# 2. Pull cambios
git pull origin main

# 3. Rebuild si hubo cambios en Dockerfile o requirements
docker-compose build

# 4. Reiniciar
docker-compose up -d

# 5. Verificar logs
docker-compose logs -f
```

### Migración de base de datos
```bash
# Si hay nuevas migrations
docker-compose exec backend alembic upgrade head
```

---

**Última actualización:** 2025-10-07
**Versión:** UNS-ClaudeJP 2.0
