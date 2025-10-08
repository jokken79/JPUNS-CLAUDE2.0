# UNS-ClaudeJP 2.0 - Sistema de Gestión de Personal Temporal

## Descripción General
UNS-ClaudeJP 2.0 es un sistema integral de gestión de personal temporal diseñado para UNS-Kikaku. Permite administrar candidatos, empleados, fábricas, tarjetas de tiempo, salarios y notificaciones de manera eficiente.

## Características Principales
- Gestión completa de candidatos y empleados
- Sistema de OCR híbrido (Gemini + Vision API + Tesseract)
- Importación masiva de datos desde Excel
- Gestión de fábricas y asignaciones
- Cálculo automático de salarios
- Sistema de notificaciones por email y LINE
- Dashboard con métricas clave

## Arquitectura
- **Backend**: FastAPI con Python 3.11
- **Frontend**: React con TypeScript
- **Base de datos**: PostgreSQL 15
- **OCR**: Sistema híbrido con múltiples APIs

## Requisitos Previos
- Docker y Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)

## Configuración Inicial

### 1. Variables de Entorno
Copia el archivo `.env.example` a `.env` y configura las siguientes variables:

```bash
# Database
DB_PASSWORD=tu_contraseña_segura
DATABASE_URL=postgresql://uns_admin:tu_contraseña_segura@db:5432/uns_claudejp

# Security
SECRET_KEY=tu_clave_secreta_aleatoria

# OCR APIs
GEMINI_API_KEY=tu_clave_gemini
GOOGLE_CLOUD_VISION_API_KEY=tu_clave_vision_api

# Email (opcional)
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_contraseña_app
```

### 2. Iniciar la Aplicación
```bash
# Construir e iniciar contenedores
docker-compose up --build

# O en modo detached
docker-compose up -d --build
```

### 3. Acceder a la Aplicación
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/api/docs

### 4. Usuario por Defecto
- Username: `admin`
- Password: `admin123`

## Estructura del Proyecto
```
JPUNS-CLAUDE2.0/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── api/            # Endpoints de API
│   │   ├── core/           # Configuración y base de datos
│   │   ├── models/         # Modelos SQLAlchemy
│   │   ├── schemas/        # Esquemas Pydantic
│   │   └── services/       # Lógica de negocio
│   └── requirements.txt
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas principales
│   │   └── services/       # Servicios API
│   └── package.json
├── database/               # Migraciones de BD
├── config/                 # Configuraciones de fábricas
├── docker-compose.yml      # Configuración Docker
└── README.md
```

## Endpoints de API Principales

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `GET /api/auth/me` - Obtener usuario actual

### Candidatos
- `GET /api/candidates` - Listar candidatos
- `POST /api/candidates` - Crear candidato
- `POST /api/candidates/{id}/upload` - Subir documento con OCR

### Empleados
- `GET /api/employees` - Listar empleados
- `POST /api/employees` - Crear empleado
- `GET /api/employees/{id}` - Obtener detalles

### Importación
- `POST /api/import/employees` - Importar empleados desde Excel
- `POST /api/import/timer-cards` - Importar tarjetas de tiempo

## Flujo de Trabajo Típico

### 1. Registrar Candidato
1. Crear nuevo candidato en el sistema
2. Subir documentos (履歴書, 在留カード)
3. El sistema procesa automáticamente con OCR
4. Revisar y aprobar candidato

### 2. Convertir a Empleado
1. Aprobar candidato
2. Asignar a fábrica específica
3. Configurar salario y beneficios
4. Generar contrato

### 3. Gestión Continua
1. Registrar tarjetas de tiempo diarias
2. Importar masivamente desde Excel
3. Calcular salarios mensuales
4. Enviar notificaciones y payslips

## Configuración de Fábricas
Las fábricas se configuran mediante archivos JSON en `config/factories/`:
- Factory-01: 瑞陵精機株式会社_恵那工場
- Factory-04: 株式会社川原鉄工所_本社工場
- Y otros...

## Sistema de OCR
El sistema utiliza un enfoque híbrido:
1. **Gemini API** (primario) - Mejor precisión
2. **Google Vision API** (respaldo) - Buena precisión
3. **Tesseract** (local) - Sin conexión a internet

## Troubleshooting Común

### Problemas de Base de Datos
```bash
# Reiniciar contenedor de BD
docker-compose restart db

# Verificar logs
docker-compose logs db
```

### Problemas de OCR
```bash
# Verificar configuración de APIs
docker-compose logs backend | grep -i ocr
```

### Problemas de Frontend
```bash
# Reconstruir contenedor
docker-compose build --no-cache frontend
```

## Desarrollo Local

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Seguridad
- Las claves API deben configurarse en variables de entorno
- No exponer claves en el código
- Usar HTTPS en producción
- Rotar claves periódicamente

## Soporte
Para problemas o preguntas:
1. Revisar logs de Docker
2. Consultar documentación de API en `/api/docs`
3. Verificar variables de entorno

## Licencia
Copyright © 2025 UNS-Kikaku. Todos los derechos reservados.