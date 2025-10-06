# UNS-ClaudeJP 2.0 - RESUMEN COMPLETO DE CONFIGURACIÓN

**Sistema de Gestión de Personal para Trabajadores Temporales (派遣社員)**
Fecha: 2025-10-06

---

## 📋 ÍNDICE

1. [Información General](#información-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Credenciales de Acceso](#credenciales-de-acceso)
4. [Datos Importados](#datos-importados)
5. [Configuración de la Empresa](#configuración-de-la-empresa)
6. [Cómo Ejecutar el Sistema](#cómo-ejecutar-el-sistema)
7. [Estructura de Archivos](#estructura-de-archivos)
8. [Base de Datos](#base-de-datos)
9. [Próximos Pasos Pendientes](#próximos-pasos-pendientes)
10. [Troubleshooting](#troubleshooting)

---

## 📌 INFORMACIÓN GENERAL

### Sistema
- **Nombre:** UNS-ClaudeJP 2.0
- **Empresa:** ユニバーサル企画株式会社 (UNS-KIKAKU)
- **Representante:** 中山 雅和
- **Propósito:** Gestión integral de empleados temporales (派遣社員, 請負社員, スタッフ)

### Tecnologías
- **Frontend:** React 18 + TypeScript + Tailwind CSS
- **Backend:** Python FastAPI + SQLAlchemy + Pydantic
- **Base de Datos:** PostgreSQL 15
- **Containerización:** Docker + Docker Compose
- **OCR:** Tesseract (japonés + inglés)

---

## 🏗️ ARQUITECTURA DEL SISTEMA

### Servicios Docker

```yaml
1. Frontend (React)
   - Puerto: 3000
   - Container: uns-claudejp-frontend
   - URL: http://localhost:3000

2. Backend (FastAPI)
   - Puerto: 8000
   - Container: uns-claudejp-backend
   - URL: http://localhost:8000
   - Docs: http://localhost:8000/docs

3. Database (PostgreSQL)
   - Puerto: 5432
   - Container: uns-claudejp-db
   - Usuario: uns_admin
   - Contraseña: 57UD10R
   - Base de datos: uns_claudejp
```

### Ubicación del Proyecto
```
d:\JPUNS-app\JPUNS-CLAUDE2.0\
```

---

## 🔐 CREDENCIALES DE ACCESO

### Usuario Administrador
```
Username: admin
Password: admin123
Email:    admin@uns-kikaku.com
Rol:      SUPER_ADMIN
```

### Usuario Coordinador
```
Username: coordinator
Password: coord123
Email:    coordinator@uns-kikaku.com
Rol:      COORDINATOR
```

### Base de Datos PostgreSQL
```
Host:     localhost
Puerto:   5432
Usuario:  uns_admin
Password: 57UD10R
Database: uns_claudejp
```

---

## 📊 DATOS IMPORTADOS

### Resumen General

| Categoría | Cantidad | Estado |
|-----------|----------|--------|
| **Fábricas (派遣先)** | 102 | ✅ Importadas |
| **Empleados Totales** | 500 | ✅ Importados |
| - 派遣社員 (Dispatch) | 348 | ✅ Importados |
| - 請負社員 (Contract) | 133 | ✅ Importados |
| - スタッフ (Staff) | 19 | ✅ Importados |
| **Empleados Activos** | 167 | ✅ Verificado |
| **Empleados Inactivos** | 333 | ✅ Verificado |
| **Asignaciones Factory** | 138 | ✅ Asignadas |

### Estadísticas de Salarios (時給)

```
Promedio: ¥1,272/hora
Mínimo:   ¥850/hora
Máximo:   ¥1,600/hora
```

### Empresas con Más Empleados Asignados

1. **瑞陵精機株式会社** (Factory-01): 45 empleados
2. **株式会社川原鉄工所** (Factory-04): 37 empleados
3. **ピーエムアイ有限会社** (Factory-28): 25 empleados
4. **六甲電子株式会社** (Factory-100): 19 empleados
5. **株式会社オーツカ** (Factory-30): 7 empleados
6. **セイビテック株式会社** (Factory-08): 4 empleados
7. **株式会社美鈴工業** (Factory-102): 1 empleado

### Archivos Fuente de Datos

```
1. Empresas/Fábricas:
   - Archivo: config/KaishaInfo.xlsx
   - Registros: 102 fábricas
   - Ubicación: d:\JPUNS-app\JPUNS-CLAUDE2.0\config\

2. Empleados:
   - Archivo: config/employee_master.xlsm
   - Hojas: 派遣社員, 請負社員, スタッフ
   - Total registros: 1,201 (500 importados exitosamente)
   - Ubicación: d:\JPUNS-app\JPUNS-CLAUDE2.0\config\
```

---

## 🏢 CONFIGURACIÓN DE LA EMPRESA

### Información Corporativa (config/company.json)

```json
{
  "company": {
    "name_ja": "ユニバーサル企画株式会社",
    "name_en": "UNS-KIKAKU",
    "postal_code": "461-0025",
    "prefecture": "愛知県",
    "city": "名古屋市東区",
    "address": "徳川2-18-18",
    "phone": "052-938-8840",
    "mobile": "080-7376-1988",
    "email": "infoapp@uns-kikaku.com",
    "website": "www.uns-kikaku.com",
    "representative": "中山 雅和",
    "founded_date": "2019-06-21"
  }
}
```

### Licencias y Permisos

1. **労働者派遣事業** (Dispatch License): 派 23-303669
2. **登録支援機関** (Support Organization): 21登-006367
3. **古物商許可証** (Antique Dealer): 愛知県公安委員会 第541032001600号
4. **有料職業紹介事業** (Job Placement): 23-ユ-302989

### Configuración de Fábricas

- **Ubicación:** `config/factories/` (102 archivos JSON)
- **Índice:** `config/factories_index.json`
- **Estructura por Factory:**
  - Información de empresa cliente (派遣先)
  - Datos de planta/工場
  - Detalles de asignación (配属先/ライン)
  - Horarios y calendarios (就業時間)
  - Información de pagos y fechas
  - Supervisor y contactos
  - Tiempo単価 (hourly_rate)

---

## 🚀 CÓMO EJECUTAR EL SISTEMA

### Inicio Rápido

```bash
# 1. Navegar al directorio del proyecto
cd d:\JPUNS-app\JPUNS-CLAUDE2.0

# 2. Iniciar todos los servicios
docker-compose up -d

# 3. Verificar que estén corriendo
docker ps

# 4. Ver logs (opcional)
docker logs uns-claudejp-frontend
docker logs uns-claudejp-backend
docker logs uns-claudejp-db
```

### Acceso al Sistema

1. **Abrir navegador** en: http://localhost:3000
2. **Iniciar sesión** con:
   - Username: `admin`
   - Password: `admin123`
3. **Navegar** usando el menú lateral

### Detener el Sistema

```bash
# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar TODO (incluye volúmenes/datos)
docker-compose down -v
```

### Reiniciar un Servicio Específico

```bash
# Frontend
docker-compose restart frontend

# Backend
docker-compose restart backend

# Database
docker-compose restart db
```

---

## 📁 ESTRUCTURA DE ARCHIVOS

```
d:\JPUNS-app\JPUNS-CLAUDE2.0\
├── frontend/                    # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx      # ✅ Con menú lateral implementado
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx   # ✅ Con datos de ejemplo
│   │   │   ├── Login.tsx       # ✅ Funcional
│   │   │   ├── Employees.tsx   # ⚠️ En desarrollo
│   │   │   ├── Candidates.tsx  # ⚠️ En desarrollo
│   │   │   ├── Factories.tsx   # ⚠️ En desarrollo
│   │   │   ├── Salary.tsx      # ⚠️ En desarrollo
│   │   │   └── ...
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── models/
│   │   │   └── models.py       # ✅ Modelos SQLAlchemy
│   │   ├── services/
│   │   │   └── auth_service.py # ✅ Autenticación JWT
│   │   ├── schemas/
│   │   │   └── auth.py         # ✅ Schemas Pydantic
│   │   ├── core/
│   │   │   ├── database.py     # ✅ Configuración DB
│   │   │   └── config.py       # ✅ Variables de entorno
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── config/                      # Archivos de Configuración
│   ├── company.json            # ✅ Info de UNS-Kikaku
│   ├── factories_index.json   # ✅ Índice de 102 fábricas
│   ├── factories/              # ✅ 102 archivos JSON
│   │   ├── Factory-01.json
│   │   ├── Factory-02.json
│   │   └── ...
│   ├── KaishaInfo.xlsx         # ✅ Excel de empresas
│   └── employee_master.xlsm    # ✅ Excel de empleados
│
├── scripts/                     # Scripts de Python
│   ├── import_data.py          # ✅ Importar fábricas y empleados
│   ├── create_admin_user.py    # ✅ Crear usuarios
│   ├── assign_factory_ids.py   # ✅ Asignar empleados a fábricas
│   ├── verify_data.py          # ✅ Verificar datos
│   └── full_verification.py    # ✅ Verificación completa
│
├── docker-compose.yml          # ✅ Orquestación de servicios
├── .env                        # ✅ Variables de entorno
└── install-windows.bat         # ✅ Script de instalación
```

---

## 🗄️ BASE DE DATOS

### Tablas Principales

| Tabla | Descripción | Registros |
|-------|-------------|-----------|
| `users` | Usuarios del sistema | 2 |
| `factories` | Empresas cliente (派遣先) | 102 |
| `employees` | Empleados (派遣/請負/スタッフ) | 500 |
| `candidates` | Candidatos para contratación | 0 |
| `timer_cards` | Registro de horas trabajadas | 0 |
| `salary_calculations` | Cálculos de nómina | 0 |
| `requests` | Solicitudes (有給, 退社, etc.) | 0 |
| `contracts` | Contratos de empleados | 0 |
| `apartments` | Apartamentos de empresa | 0 |
| `documents` | Documentos escaneados | 0 |
| `audit_log` | Log de auditoría | 0 |

### Enums Definidos

```python
UserRole:
  - SUPER_ADMIN
  - ADMIN
  - COORDINATOR
  - EMPLOYEE

CandidateStatus:
  - PENDING
  - APPROVED
  - REJECTED
  - HIRED

DocumentType:
  - RIREKISHO (履歴書)
  - ZAIRYU_CARD (在留カード)
  - LICENSE
  - CONTRACT
  - OTHER

RequestType:
  - YUKYU (有給)
  - HANKYU (半休)
  - IKKIKOKOKU (一時帰国)
  - TAISHA (退社)

RequestStatus:
  - PENDING
  - APPROVED
  - REJECTED

ShiftType:
  - ASA (朝番)
  - HIRU (昼番)
  - YORU (夜番)
  - OTHER
```

### Campos Importantes en `employees`

```
- hakenmoto_id: ID único del empleado (社員№)
- full_name_kanji: 氏名
- full_name_kana: カナ
- jikyu: 時給 (salario por hora)
- factory_id: Referencia a factories (派遣先)
- contract_type: '派遣', '請負', 'スタッフ'
- is_active: TRUE/FALSE
- hire_date: 入社日
- termination_date: 退社日
- nationality: 国籍
- zairyu_expire_date: ビザ期限
```

### Campos Importantes en `factories`

```
- factory_id: 'Factory-01', 'Factory-02', etc.
- name: Nombre completo (empresa + planta)
- config: JSON con toda la información:
  - client_company (派遣先)
  - plant (工場)
  - assignment (配属先/ライン)
  - job (仕事内容, hourly_rate)
  - schedule (就業時間, 休憩時間)
  - payment (締日, 支払日)
  - dispatch_company (派遣元 = UNS-Kikaku)
```

### Scripts de Base de Datos

```bash
# Importar datos completos
docker exec uns-claudejp-backend python /app/scripts/import_data.py

# Asignar empleados a fábricas
docker exec uns-claudejp-backend python /app/scripts/assign_factory_ids.py

# Crear usuarios administradores
docker exec uns-claudejp-backend python /app/scripts/create_admin_user.py

# Verificar datos importados
docker exec uns-claudejp-backend python /app/scripts/verify_data.py

# Verificación completa del sistema
docker exec uns-claudejp-backend python /app/scripts/full_verification.py
```

---

## ⏭️ PRÓXIMOS PASOS PENDIENTES

### Funcionalidades a Implementar

#### 1. Gestión de Empleados (従業員管理)
**Prioridad: ALTA**

- [ ] Lista de empleados con datos reales del backend
- [ ] Búsqueda y filtros (por nombre, factory_id, activo/inactivo)
- [ ] Vista detallada de empleado
- [ ] Edición de datos de empleado
- [ ] Registro de nuevo empleado
- [ ] Historial de cambios

**Datos disponibles:**
- 500 empleados en base de datos
- Todos los campos completos (nombre, kana, 時給, factory, etc.)

#### 2. Gestión de Empresas (企業管理)
**Prioridad: ALTA**

- [ ] Lista de 102 fábricas/empresas
- [ ] Vista detallada con configuración completa
- [ ] Edición de configuración
- [ ] Lista de empleados asignados por factory

**Datos disponibles:**
- 102 factories con configuración JSON completa
- Todas las empresas cliente (派遣先)

#### 3. Cálculo de Nómina (給与計算)
**Prioridad: ALTA**

- [ ] Cálculo automático basado en:
  - 時給 individual del empleado
  - Horas trabajadas (timer cards)
  - Horas extras (con % de factory config)
  - Deducciones (apartamento, seguro social)
- [ ] Generación de recibos de pago
- [ ] Exportación a Excel
- [ ] Histórico de pagos

**Datos disponibles:**
- 時給 de cada empleado
- Configuración de horas extras por factory
- Fechas de cierre y pago por factory

#### 4. Gestión de Candidatos (候補者管理)
**Prioridad: MEDIA**

- [ ] Registro de nuevos candidatos
- [ ] Upload de 履歴書 (CV) con OCR
- [ ] Upload de 在留カード con OCR
- [ ] Proceso de aprobación
- [ ] Conversión a empleado

#### 5. Tarjetas de Tiempo (タイムカード)
**Prioridad: ALTA**

- [ ] Upload de tarjetas escaneadas por factory
- [ ] OCR para extraer horas
- [ ] Verificación y corrección manual
- [ ] Cálculo de horas (regulares, extras, nocturnas)
- [ ] Aprobación por coordinador

#### 6. Gestión de Solicitudes (申請管理)
**Prioridad: MEDIA**

- [ ] Solicitudes de 有給 (vacaciones pagadas)
- [ ] Solicitudes de 半休 (medio día)
- [ ] Solicitudes de 一時帰国 (regreso temporal)
- [ ] Solicitudes de 退社 (renuncia)
- [ ] Proceso de aprobación/rechazo
- [ ] Notificaciones

#### 7. Dashboard con Datos Reales
**Prioridad: MEDIA**

- [ ] Conectar estadísticas al backend
- [ ] Gráficas reales (empleados activos, por factory, etc.)
- [ ] Alertas reales (ビザ期限, contratos por vencer)
- [ ] Actividades recientes del sistema

#### 8. Reportes y Exportaciones
**Prioridad: BAJA**

- [ ] Reporte mensual de nómina
- [ ] Lista de empleados por factory
- [ ] Reporte de horas trabajadas
- [ ] Exportación a Excel/PDF

### Mejoras Técnicas Pendientes

#### Backend (API Endpoints)
```
Necesarios:
- GET  /api/employees (lista con filtros)
- GET  /api/employees/{id}
- POST /api/employees
- PUT  /api/employees/{id}
- GET  /api/factories
- GET  /api/factories/{id}
- POST /api/timer-cards
- POST /api/salary/calculate
- GET  /api/requests
- POST /api/requests
```

#### Frontend
```
- Conectar páginas al backend (axios/fetch)
- Manejo de estados con Context API o Redux
- Validación de formularios
- Manejo de errores
- Loading states
- Paginación de listas
```

#### Seguridad
```
- Implementar refresh tokens
- Verificación de permisos por rol
- Rate limiting
- CORS configuración
- HTTPS en producción
```

---

## 🔧 TROUBLESHOOTING

### El frontend no carga (ERR_EMPTY_RESPONSE)

```bash
# Verificar que el contenedor esté corriendo
docker ps

# Reiniciar frontend
docker-compose restart frontend

# Ver logs para errores
docker logs uns-claudejp-frontend

# Si hay errores de node_modules:
docker-compose down
docker-compose up --build
```

### Error "react-scripts: not found"

```bash
# Reconstruir sin caché
docker-compose build --no-cache frontend
docker-compose up
```

### Backend no conecta a la base de datos

```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# Verificar logs
docker logs uns-claudejp-db

# Reiniciar base de datos
docker-compose restart db
```

### Problemas con encoding japonés (文字化け)

```bash
# Ya está resuelto en:
# - frontend/src/pages/Dashboard.tsx
# - Todos los archivos JSON en config/

# Si aparece de nuevo, verificar que los archivos estén en UTF-8
```

### No puedo hacer login

```bash
# Verificar que existan usuarios
docker exec uns-claudejp-backend python -c "from app.core.database import SessionLocal; from app.models.models import User; db = SessionLocal(); print(f'Usuarios: {db.query(User).count()}'); db.close()"

# Recrear usuarios
docker exec uns-claudejp-backend python /app/scripts/create_admin_user.py
```

### Los empleados no tienen factory_id

```bash
# Ejecutar script de asignación
docker exec uns-claudejp-backend python /app/scripts/assign_factory_ids.py
```

### Reimportar todos los datos desde cero

```bash
# 1. Recrear tablas (BORRA TODO)
docker exec uns-claudejp-backend python -c "from app.core.database import engine, Base; from app.models.models import *; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); print('Tablas recreadas')"

# 2. Importar fábricas y empleados
docker exec uns-claudejp-backend python /app/scripts/import_data.py

# 3. Crear usuarios
docker exec uns-claudejp-backend python /app/scripts/create_admin_user.py

# 4. Asignar factory_id
docker exec uns-claudejp-backend python /app/scripts/assign_factory_ids.py

# 5. Verificar
docker exec uns-claudejp-backend python /app/scripts/full_verification.py
```

---

## 📞 INFORMACIÓN DE CONTACTO

### Empresa
- **Nombre:** ユニバーサル企画株式会社
- **Teléfono:** 052-938-8840
- **Móvil:** 080-7376-1988
- **Email:** infoapp@uns-kikaku.com
- **Dirección:** 〒461-0025 愛知県名古屋市東区徳川2-18-18

### Sistema
- **Versión:** 2.0
- **Fecha de configuración:** 2025-10-06
- **Estado:** Base funcional con datos reales importados

---

## ✅ CHECKLIST DE ESTADO ACTUAL

### Completado ✅

- [x] Instalación de Docker y contenedores
- [x] Configuración de base de datos PostgreSQL
- [x] Importación de 102 fábricas desde KaishaInfo.xlsx
- [x] Importación de 500 empleados desde employee_master.xlsm
- [x] Asignación de 138 empleados a sus fábricas
- [x] Configuración de empresa (company.json)
- [x] Creación de usuarios admin y coordinator
- [x] Frontend con menú de navegación lateral
- [x] Botón de cerrar sesión funcional
- [x] Sistema de autenticación JWT
- [x] Login funcional
- [x] Dashboard con datos de ejemplo

### Pendiente ⚠️

- [ ] Implementar páginas con datos reales del backend
- [ ] Crear endpoints de API REST
- [ ] Conectar frontend con backend (axios)
- [ ] Implementar gestión de empleados completa
- [ ] Implementar cálculo de nómina
- [ ] Implementar sistema de tarjetas de tiempo
- [ ] Upload y OCR de documentos
- [ ] Sistema de notificaciones
- [ ] Reportes y exportaciones

---

## 📝 NOTAS FINALES

1. **Datos Reales Importados:** El sistema tiene 102 fábricas y 500 empleados reales con todos sus datos (nombres, salarios, fechas, etc.)

2. **Solo Falta Frontend:** Las páginas están creadas pero muestran "En desarrollo" porque no están conectadas al backend

3. **Backend Funcional:** La API está lista, solo faltan los endpoints específicos para cada funcionalidad

4. **Prioridad:** Implementar primero la gestión de empleados y nómina, que son las funciones más críticas

5. **Excel Fuente:** Los archivos Excel originales están en `config/` y pueden ser actualizados. Se pueden reimportar ejecutando los scripts

6. **Próxima Sesión:** Continuar implementando las páginas con datos reales del backend

---

**FIN DEL RESUMEN**

Para continuar el desarrollo, usa este documento como referencia y comienza implementando las páginas pendientes conectándolas al backend.
