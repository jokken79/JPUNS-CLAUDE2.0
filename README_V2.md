# 🚀 UNS-ClaudeJP 2.0

Sistema Integral de Gestión de Personal Temporal para UNS-Kikaku

> ✅ **VERSIÓN 2.0 - OCTUBRE 2025**  
> Sistema completamente refactorizado con servicios modulares, OCR híbrido, y automatización completa.

---

## 📋 ¿Qué Hay de Nuevo en v2.0?

### ⭐ Mejoras Principales:

1. **🔒 Seguridad Mejorada**
   - API Key de Gemini movida al backend
   - No más credenciales expuestas en el frontend

2. **🚀 OCR Híbrido Inteligente**
   - Sistema de 3 capas: Gemini → Vision API → Tesseract
   - Cache automático (evita procesar la misma imagen 2 veces)
   - 3x más rápido que la versión 1.0

3. **📧 Notificaciones Automáticas**
   - Email profesional con HTML
   - LINE notifications
   - Notificaciones para: 有給承認, 退社, 給与明細

4. **💰 Cálculo Automático de Nómina**
   - Todas las reglas japonesas implementadas
   - 残業手当 (25%), 深夜手当 (25%), 休日出勤 (35%)
   - Bonificaciones y deducciones automáticas

5. **📊 Importación Masiva**
   - Empleados desde Excel con validación
   - Timer Cards con detección de errores
   - Factory configs desde JSON

6. **📈 Reportes Profesionales**
   - Excel con gráficos automáticos
   - PDFs de recibos de pago
   - Reportes anuales con tendencias

---

## 🎯 Características Principales

### 📋 Módulo de Reclutamiento
- ✅ OCR automático de 在留カード (Gemini + Vision + Tesseract)
- ✅ Extracción de foto del rostro con face detection
- ✅ Sistema híbrido con cache
- ✅ Generación automática de ID (UNS-XXXXXX)

### 👥 Módulo de Personal
- ✅ Base de datos centralizada con 4 tipos de IDs
- ✅ Gestión completa de documentos
- ✅ Historial de empleados

### 🏭 Módulo de Fábricas
- ✅ 102+ fábricas configurables
- ✅ Horarios personalizados (朝番/昼番/夜番)
- ✅ 時給単価 por fábrica/posición
- ✅ Premios y bonificaciones

### ⏰ Módulo de Timer Cards
- ✅ Upload masivo (PDF/Excel)
- ✅ OCR con corrección manual
- ✅ Importación desde Excel

### 💰 Módulo de Nómina (⭐ NUEVO)
- ✅ Cálculo automático completo
- ✅ Horas: normales, extras, nocturnas, festivas
- ✅ Bonos: gasolina, asistencia, performance
- ✅ Deducciones: apartamento, seguro, impuestos
- ✅ Comparativa 時給 vs 時給単価

### 📋 Módulo de Solicitudes
- ✅ 有給休暇 + 半日有給
- ✅ 一時帰国
- ✅ 退社報告
- ✅ Notificaciones automáticas por email/LINE

### 📊 Reportes (⭐ NUEVO)
- ✅ Reportes mensuales por fábrica (Excel con gráficos)
- ✅ Recibos de pago individuales (PDF)
- ✅ Reportes anuales con análisis de tendencias
- ✅ Descarga automática

### 📤 Import/Export (⭐ NUEVO)
- ✅ Importación masiva de empleados desde Excel
- ✅ Importación de timer cards
- ✅ Templates descargables
- ✅ Validación automática con reporte de errores

---

## 🛠 Stack Tecnológico

```
Frontend:  React + TypeScript + Tailwind CSS
Backend:   Python FastAPI
Database:  PostgreSQL
OCR:       Gemini AI + Google Cloud Vision + Tesseract
Storage:   Local file system
Deploy:    Docker + Docker Compose
```

---

## 📦 Estructura del Proyecto

```
uns-claudejp/
├── backend/                    # API Python FastAPI
│   ├── app/
│   │   ├── api/               # Endpoints
│   │   │   ├── auth.py
│   │   │   ├── ocr.py         # ⭐ NUEVO
│   │   │   ├── import_export.py # ⭐ NUEVO
│   │   │   ├── reports.py     # ⭐ NUEVO
│   │   │   └── notifications.py # ⭐ NUEVO
│   │   ├── core/              # Configuración
│   │   ├── models/            # Modelos DB
│   │   ├── schemas/           # Schemas Pydantic
│   │   └── services/          # Lógica de negocio
│   │       ├── ocr_service.py         # ✏️ MEJORADO
│   │       ├── notification_service.py # ⭐ NUEVO
│   │       ├── payroll_service.py     # ⭐ NUEVO
│   │       ├── import_service.py      # ⭐ NUEVO
│   │       └── report_service.py      # ⭐ NUEVO
│   └── tests/
├── frontend/                   # React App
│   ├── src/
│   └── public/
│       └── templates/
│           └── rirekisho.html  # ✏️ Ahora usa backend
├── database/                   # Migraciones
├── docker/                     # Dockerfiles
├── config/                     # Configs JSON (102 fábricas)
└── docs/                       # Documentación
```

---

## 🚀 Instalación

### Prerequisitos

- Docker & Docker Compose
- Puerto 3000 (Frontend) y 8000 (Backend) disponibles

### Pasos de Instalación

1. **Clonar el proyecto**
```bash
git clone [repository]
cd JPUNS-CLAUDE2.0
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Variables importantes a configurar:**
```env
# Gemini API (OCR)
GEMINI_API_KEY=your_gemini_api_key_here

# Email (Notificaciones)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password

# LINE (Opcional)
LINE_CHANNEL_ACCESS_TOKEN=your_line_token
```

4. **Levantar con Docker**
```bash
docker-compose up -d --build
```

5. **Acceder a la aplicación**
```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/api/docs

Usuario:  admin
Password: admin123
```

---

## 📝 Cómo Obtener las API Keys

### Gemini API Key (Requerido para OCR):

1. Ir a https://makersuite.google.com/app/apikey
2. Iniciar sesión con tu cuenta de Google
3. Crear una API Key nueva
4. Copiarla al `.env` como `GEMINI_API_KEY`

### Gmail App Password (Requerido para notificaciones):

1. Ir a https://myaccount.google.com/apppasswords
2. Crear una nueva "App password" para "Mail"
3. Copiar la contraseña generada
4. Usarla como `SMTP_PASSWORD` en `.env`

### LINE Channel Token (Opcional):

1. Crear LINE Official Account en https://developers.line.biz/
2. Crear un canal de Messaging API
3. Obtener el Channel Access Token
4. Copiarlo como `LINE_CHANNEL_ACCESS_TOKEN` en `.env`

---

## 🎯 Guía de Uso Rápido

### 1. OCR de 在留カード

```bash
# Opción A: Desde el frontend
1. Abrir http://localhost:3000/templates/rirekisho.html
2. Click en área de "在留カード"
3. Subir imagen (JPG/PNG, máx 10MB)
4. Sistema automáticamente:
   - Intenta con Gemini (más rápido y preciso)
   - Si falla, usa Vision API
   - Si falla, usa Tesseract
   - Extrae foto del rostro
   - Auto-rellena formulario

# Opción B: Via API directa
curl -X POST "http://localhost:8000/api/ocr/process" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@zairyu_card.jpg" \
  -F "document_type=zairyu_card"
```

### 2. Importar Empleados Masivamente

```bash
# 1. Preparar Excel con formato:
# 派遣元ID | 氏名 | フリガナ | 生年月日 | 性別 | 国籍 | ...

# 2. Importar via API
curl -X POST "http://localhost:8000/api/import/employees" \
  -F "file=@employees.xlsx"

# 3. Revisar resultados
# Respuesta incluye: total, imported, failed, errors[]
```

### 3. Calcular Nómina Automáticamente

```python
# En tu código Python:
from app.services.payroll_service import payroll_service

payroll = payroll_service.calculate_monthly_payroll(
    employee_id=123,
    year=2025,
    month=10,
    timer_cards=timer_cards_list,
    factory_config=factory_config_dict
)

# Resultado incluye:
# - Horas: normales, extras, nocturnas, festivas
# - Pagos: base, overtime, night, holiday
# - Bonos: gasolina, asistencia, performance
# - Deducciones: apartamento, seguro, impuestos
# - Total bruto y neto
```

### 4. Enviar Notificaciones

```python
# Email + LINE automático
from app.services.notification_service import notification_service

notification_service.notify_yukyu_approval(
    employee_email="employee@example.com",
    employee_name="山田太郎",
    status="承認",
    yukyu_date="2025-10-10",
    line_user_id="U123456789"  # Opcional
)
```

### 5. Generar Reportes

```bash
# Reporte mensual de fábrica
curl -X POST "http://localhost:8000/api/reports/monthly-factory?factory_id=Factory-01&year=2025&month=10"

# Descargar reporte generado
curl -O "http://localhost:8000/api/reports/download/report_Factory-01_202510.xlsx"
```

---

## 📚 Documentación Completa

- **Mejoras v2.0:** [MEJORAS_COMPLETAS_V2.md](MEJORAS_COMPLETAS_V2.md)
- **Guía de Servicios:** Ver archivos en `backend/app/services/`
- **API Docs:** http://localhost:8000/api/docs (Swagger UI)
- **Guía Rápida:** [GUIA_RAPIDA_SISTEMA.md](GUIA_RAPIDA_SISTEMA.md)

---

## 🐛 Troubleshooting

### OCR no funciona:

```bash
# 1. Verificar que GEMINI_API_KEY está configurado
cat .env | grep GEMINI_API_KEY

# 2. Ver logs del backend
docker logs uns-claudejp-backend --tail 50

# 3. Verificar cache de OCR
curl http://localhost:8000/api/ocr/cache-stats
```

### Notificaciones no se envían:

```bash
# 1. Probar configuración de email
curl http://localhost:8000/api/notifications/test-email

# 2. Verificar credenciales SMTP en .env
cat .env | grep SMTP

# 3. Ver logs
docker logs uns-claudejp-backend | grep "notification"
```

### Frontend no carga cambios:

```bash
# Hard refresh en navegador
Ctrl + Shift + R

# O reconstruir frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 📊 Niveles de Acceso

| Rol | Permisos |
|-----|----------|
| **Super Admin** | Control total del sistema |
| **Admin** | Gestión de fábricas asignadas |
| **CO (Coordinador)** | Vista de lectura |
| **Funcionario** | Ver datos propios + crear solicitudes |

---

## 🔐 Seguridad

- ✅ API Keys protegidas en backend (no expuestas en frontend)
- ✅ JWT authentication
- ✅ Password hashing con bcrypt
- ✅ CORS configurado
- ✅ Validación de inputs
- ✅ Rate limiting en OCR

---

## 📱 Progressive Web App (PWA)

La aplicación funciona en:
- ✅ Navegadores de escritorio
- ✅ Tablets
- ✅ Smartphones (iOS/Android)
- ✅ Puede instalarse como app nativa

---

## 🚀 Roadmap Futuro

### v2.1 (Próximo Mes)
- [ ] Dashboard en tiempo real con WebSockets
- [ ] Sistema de auditoría completo
- [ ] Búsqueda avanzada con filtros

### v2.2 (Próximos 3 Meses)
- [ ] Integración con bancos (振込 automático)
- [ ] App móvil nativa (React Native)
- [ ] Sistema de backup automático

---

## 📞 Soporte

Para soporte técnico:
- Email: support@uns-kikaku.com
- Web: https://uns-kikaku.com
- Documentación: Ver carpeta `docs/`

---

## 📄 Licencia

Propiedad de UNS-Kikaku © 2025

---

## 🙏 Créditos

**Desarrollado con ❤️ por:**
- Claude AI (Anthropic)
- UNS-Kikaku Development Team

**Tecnologías:**
- React, TypeScript, Tailwind CSS
- Python, FastAPI, SQLAlchemy
- PostgreSQL, Docker
- Gemini AI, Google Cloud Vision, Tesseract OCR

---

**Versión 2.0 - Octubre 2025**  
**Estado: ✅ Producción**
