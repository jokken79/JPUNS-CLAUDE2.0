# Sesión de Desarrollo - 2025-10-06
## Sistema de Gestión de Empleados - UNS-ClaudeJP 2.0

---

## 📋 RESUMEN DE LO IMPLEMENTADO HOY

### 1. Sistema Completo de Gestión de Empleados

#### Backend (API) ✅ COMPLETADO
- **Ubicación:** `backend/app/api/employees.py`
- **Endpoints implementados:**
  - `GET /api/employees/` - Lista con paginación, búsqueda y filtros
  - `GET /api/employees/{id}` - Detalle de empleado
  - `POST /api/employees/` - Crear nuevo empleado
  - `PUT /api/employees/{id}` - Actualizar empleado
  - `POST /api/employees/{id}/terminate` - Dar de baja empleado

#### Frontend ✅ COMPLETADO

**Páginas creadas:**

1. **`Employees.tsx`** - Vista simple (8 columnas)
   - Lista de 500 empleados
   - Búsqueda por nombre o ID
   - Filtros: activo/inactivo, factory_id
   - Paginación (20 por página)
   - Botones: ver detalle, editar, nuevo

2. **`EmployeeDetail.tsx`** - Vista detallada de empleado
   - Información completa del empleado
   - Secciones: Personal, Contacto, Empleo, Apartamento
   - Card de有給 (yukyu)
   - Alerta de visa próxima a vencer
   - Quick actions

3. **`EmployeeForm.tsx`** - Formulario de edición/creación
   - Modo creación y modo edición
   - Validación de campos
   - Secciones organizadas
   - Integración con toast notifications

4. **`EmployeesExtended.tsx`** - Vista extendida (36 columnas) ✨ NUEVA
   - TODAS las columnas del sistema original
   - Tabla completa tipo Excel
   - Cálculo automático de edad
   - Alertas de visa
   - Scroll horizontal
   - 50 empleados por página

---

## 🗄️ CAMBIOS EN LA BASE DE DATOS

### Migración Ejecutada: `002_add_employee_extended_fields.sql`

**Nuevos campos agregados a la tabla `employees`:**

```sql
-- Información financiera
hourly_rate_charged INTEGER,      -- 請求単価
profit_difference INTEGER,         -- 差額利益
standard_compensation INTEGER,     -- 標準報酬
health_insurance INTEGER,          -- 健康保険
nursing_insurance INTEGER,         -- 介護保険
pension_insurance INTEGER,         -- 厚生年金
social_insurance_date DATE,        -- 社保加入日

-- Visa y documentos
visa_type VARCHAR(50),             -- ビザ種類
license_type VARCHAR(100),         -- 免許種類
license_expire_date DATE,          -- 免許期限
commute_method VARCHAR(50),        -- 通勤方法
optional_insurance_expire DATE,    -- 任意保険期限
japanese_level VARCHAR(50),        -- 日本語検定
career_up_5years BOOLEAN,          -- キャリアアップ5年目
entry_request_date DATE,           -- 入社依頼日
photo_url VARCHAR(255),            -- 写真URL (from rirekisho)
notes TEXT,                        -- 備考
postal_code VARCHAR(10),           -- 郵便番号
apartment_move_out_date DATE,      -- 退去日
```

**Índices creados:**
```sql
CREATE INDEX idx_employees_visa_expire ON employees(zairyu_expire_date);
CREATE INDEX idx_employees_license_expire ON employees(license_expire_date);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
```

---

## 📁 ESTRUCTURA DE ARCHIVOS MODIFICADOS/CREADOS

```
D:\JPUNS-app\JPUNS-CLAUDE2.0\

backend/
├── app/
│   ├── models/
│   │   └── models.py                          ✏️ MODIFICADO - Agregados nuevos campos
│   ├── schemas/
│   │   └── employee.py                        ✏️ MODIFICADO - Schema extendido
│   └── api/
│       └── employees.py                       ✅ Ya existía (funcionando)

frontend/
├── src/
│   ├── pages/
│   │   ├── Employees.tsx                      ✏️ MODIFICADO - Agregada navegación
│   │   ├── EmployeeDetail.tsx                 ✨ NUEVO - Vista detallada
│   │   ├── EmployeeForm.tsx                   ✨ NUEVO - Formulario completo
│   │   └── EmployeesExtended.tsx              ✨ NUEVO - Vista con 36 columnas
│   ├── components/
│   │   └── Layout.tsx                         ✏️ MODIFICADO - Agregado menú nuevo
│   └── App.tsx                                ✏️ MODIFICADO - Rutas actualizadas

database/
└── migrations/
    └── 002_add_employee_extended_fields.sql   ✨ NUEVO - Migración campos

DESARROLLO_SESION_2025-10-06.md                ✨ NUEVO - Este archivo
```

---

## 🎯 COLUMNAS EN VISTA EXTENDIDA (EmployeesExtended.tsx)

La nueva vista incluye las siguientes 36 columnas:

| # | Columna | Campo DB | Descripción |
|---|---------|----------|-------------|
| 1 | 現在 | photo_url | Icono si tiene foto |
| 2 | 社員№ | hakenmoto_id | ID del empleado |
| 3 | 派遣先 | factory_id | ID de la fábrica |
| 4 | 氏名 | full_name_kanji | Nombre en kanji |
| 5 | カナ | full_name_kana | Nombre en kana |
| 6 | 性別 | gender | Género |
| 7 | 国籍 | nationality | Nacionalidad |
| 8 | 生年月日 | date_of_birth | Fecha nacimiento |
| 9 | 年齢 | (calculado) | Edad calculada |
| 10 | 時給 | jikyu | Salario por hora |
| 11 | 請求単価 | hourly_rate_charged | Tarifa cobrada |
| 12 | 差額利益 | profit_difference | Diferencia/ganancia |
| 13 | 標準報酬 | standard_compensation | Compensación estándar |
| 14 | 健康保険 | health_insurance | Seguro médico |
| 15 | 介護保険 | nursing_insurance | Seguro enfermería |
| 16 | 厚生年金 | pension_insurance | Pensión |
| 17 | ビザ期限 | zairyu_expire_date | Fecha vencimiento visa |
| 18 | ｱﾗｰﾄ | (calculado) | Alerta visa (期限切れ/要更新/注意) |
| 19 | ビザ種類 | visa_type | Tipo de visa |
| 20 | 〒 | postal_code | Código postal |
| 21 | 住所 | address | Dirección |
| 22 | ｱﾊﾟｰﾄ | apartment_id | ID apartamento |
| 23 | 入居 | apartment_start_date | Fecha ingreso apartamento |
| 24 | 入社日 | hire_date | Fecha contratación |
| 25 | 退社日 | termination_date | Fecha terminación |
| 26 | 退去 | apartment_move_out_date | Fecha salida apartamento |
| 27 | 社保加入 | social_insurance_date | Fecha seguro social |
| 28 | 入社依頼 | entry_request_date | Fecha solicitud ingreso |
| 29 | 備考 | notes | Notas/observaciones |
| 30 | 免許種類 | license_type | Tipo licencia |
| 31 | 免許期限 | license_expire_date | Vencimiento licencia |
| 32 | 通勤方法 | commute_method | Método transporte |
| 33 | 任意保険期限 | optional_insurance_expire | Seguro opcional venc. |
| 34 | 日本語検定 | japanese_level | Nivel japonés |
| 35 | キャリアアップ5年目 | career_up_5years | Career up 5 años |
| 36 | 操作 | - | Botones ver/editar |

---

## 🚀 CÓMO USAR EL SISTEMA

### Iniciar el sistema

```bash
cd D:\JPUNS-app\JPUNS-CLAUDE2.0

# Iniciar todos los servicios
docker-compose up -d

# Verificar que estén corriendo
docker ps
```

### Acceso

1. **URL:** http://localhost:3000
2. **Login:**
   - Username: `admin`
   - Password: `admin123`

### Navegación

En el menú lateral encontrarás:
- **ダッシュボード** - Dashboard
- **候補者管理** - Gestión de candidatos
- **従業員管理** - Gestión empleados (vista simple - 8 columnas)
- **従業員管理（詳細）** ✨ - Gestión empleados (vista completa - 36 columnas)
- **企業管理** - Gestión de empresas
- **タイムカード** - Tarjetas de tiempo
- **給与計算** - Cálculo de nómina
- **申請管理** - Gestión de solicitudes

---

## 🔧 PROBLEMAS RESUELTOS EN ESTA SESIÓN

### 1. Error "Could not validate credentials"
**Problema:** Token de autenticación expirado/inválido
**Solución:**
- Usuario debe cerrar sesión y volver a iniciar
- El token se guarda en `localStorage.getItem('token')`

### 2. Error 500 en /api/employees
**Problema:** Schema Pydantic esperaba `uns_id` y `factory_id` como strings obligatorios, pero algunos empleados tienen NULL
**Solución:** Cambiar a `Optional[str]` en `employee.py:61-62`

### 3. Campos faltantes en la base de datos
**Problema:** La tabla employees solo tenía campos básicos
**Solución:** Migración `002_add_employee_extended_fields.sql` agregó 18 nuevos campos

### 4. Frontend no recargaba cambios
**Problema:** Docker no tiene volumen montado para desarrollo
**Solución:**
```bash
docker-compose stop frontend
docker-compose build frontend
docker-compose up -d frontend
```

---

## 📊 ESTADO ACTUAL DEL SISTEMA

### Backend
- ✅ API REST funcionando
- ✅ Autenticación JWT
- ✅ 500 empleados en DB
- ✅ 102 fábricas en DB
- ✅ Todos los campos extendidos en modelo

### Frontend
- ✅ Vista simple de empleados (Employees.tsx)
- ✅ Vista extendida de empleados (EmployeesExtended.tsx)
- ✅ Vista detalle (EmployeeDetail.tsx)
- ✅ Formulario edición/creación (EmployeeForm.tsx)
- ✅ Búsqueda y filtros
- ✅ Paginación
- ✅ Navegación completa

### Pendiente (Próximas sesiones)
- [ ] Sistema OCR para rirekisho (履歴書)
- [ ] Upload y procesamiento de fotos
- [ ] Vincular photo_url con documentos escaneados
- [ ] Importación masiva desde Excel
- [ ] Exportación a Excel de vista extendida
- [ ] Cálculos automáticos (差額利益 = 請求単価 - 時給)
- [ ] Alertas automáticas por correo/LINE
- [ ] Dashboard con métricas reales
- [ ] Gestión de fábricas completa
- [ ] Sistema de nómina
- [ ] Tarjetas de tiempo (タイムカード)

---

## 🔄 PARA CONTINUAR EN LA PRÓXIMA SESIÓN

### 1. Sistema OCR para Rirekisho

**Objetivo:** Extraer automáticamente:
- Foto del empleado
- Nombre (氏名)
- Fecha nacimiento (生年月日)
- Dirección (住所)
- Historial laboral

**Archivos a crear:**
```
backend/app/services/ocr_service.py
backend/app/api/documents.py
frontend/src/pages/DocumentUpload.tsx
```

**Tecnología:**
- Tesseract (ya instalado)
- Google Cloud Vision API (opcional)
- PDF.js para PDFs

### 2. Importación Masiva desde Excel

**Objetivo:** Importar empleados desde employee_master.xlsm actualizado

**Script a mejorar:**
```
backend/scripts/import_data.py
```

**Agregar:**
- Validación de datos
- Detección de duplicados
- Log de errores
- Preview antes de importar

### 3. Cálculos Automáticos

**Campos a calcular automáticamente:**

```python
# En employee.py o crear calculated_fields.py
def calculate_profit(hourly_rate_charged, jikyu):
    """差額利益 = 請求単価 - 時給"""
    if hourly_rate_charged and jikyu:
        return hourly_rate_charged - jikyu
    return 0

def calculate_age(date_of_birth):
    """年齢計算"""
    if not date_of_birth:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )

def calculate_visa_alert(zairyu_expire_date):
    """ビザアラート: 期限切れ/要更新/注意"""
    if not zairyu_expire_date:
        return None
    days_left = (zairyu_expire_date - date.today()).days
    if days_left < 0:
        return "期限切れ"
    elif days_left <= 30:
        return "要更新"
    elif days_left <= 90:
        return "注意"
    return None
```

### 4. Exportación a Excel

**Objetivo:** Exportar vista extendida a Excel con formato

**Librerías a usar:**
- `openpyxl` o `xlsxwriter`

**Archivo a crear:**
```
backend/app/services/excel_export_service.py
```

**Endpoint:**
```python
@router.get("/export")
async def export_employees_to_excel():
    # Generar Excel con todas las columnas
    # Aplicar formato (colores, bordes)
    # Retornar archivo
    pass
```

---

## 🌐 RUTAS DEL SISTEMA

### Backend (http://localhost:8000)

```
GET  /                              - Info del sistema
GET  /api/health                    - Health check
GET  /api/docs                      - Documentación Swagger

# Auth
POST /api/auth/login                - Login
GET  /api/auth/me                   - Usuario actual

# Employees
GET  /api/employees/                - Lista empleados
GET  /api/employees/{id}            - Detalle empleado
POST /api/employees/                - Crear empleado
PUT  /api/employees/{id}            - Actualizar empleado
POST /api/employees/{id}/terminate  - Dar de baja
PUT  /api/employees/{id}/yukyu      - Actualizar yukyu

# Factories
GET  /api/factories/                - Lista fábricas
GET  /api/factories/{id}            - Detalle fábrica

# Candidates
GET  /api/candidates/               - Lista candidatos
POST /api/candidates/               - Crear candidato

# Dashboard
GET  /api/dashboard/stats           - Estadísticas
```

### Frontend (http://localhost:3000)

```
/login                              - Login
/dashboard                          - Dashboard principal
/candidates                         - Lista candidatos
/candidates/new                     - Nuevo candidato
/candidates/:id                     - Editar candidato
/employees                          - Lista empleados (simple)
/employees-extended                 - Lista empleados (extendida) ✨ NUEVA
/employees/new                      - Nuevo empleado
/employees/:id                      - Detalle empleado
/employees/:id/edit                 - Editar empleado
/factories                          - Lista fábricas
/timer-cards                        - Tarjetas tiempo
/salary                             - Cálculo nómina
/requests                           - Solicitudes
```

---

## 📝 COMANDOS ÚTILES

### Docker

```bash
# Ver logs
docker logs uns-claudejp-backend
docker logs uns-claudejp-frontend
docker logs uns-claudejp-db

# Reiniciar servicios
docker-compose restart backend
docker-compose restart frontend

# Reconstruir frontend con cambios
docker-compose stop frontend
docker-compose build frontend
docker-compose up -d frontend

# Acceder al contenedor
docker exec -it uns-claudejp-backend bash
docker exec -it uns-claudejp-frontend sh

# Base de datos
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp
```

### Base de Datos

```bash
# Ejecutar migración
docker exec -i uns-claudejp-db psql -U uns_admin -d uns_claudejp < database/migrations/002_add_employee_extended_fields.sql

# Consultas útiles
docker exec uns-claudejp-backend python -c "
from app.core.database import SessionLocal
from app.models.models import Employee
db = SessionLocal()
print(f'Total empleados: {db.query(Employee).count()}')
print(f'Activos: {db.query(Employee).filter(Employee.is_active==True).count()}')
db.close()
"

# Ver estructura tabla
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "\d employees"
```

### Scripts Python (dentro del contenedor)

```bash
# Verificar datos
docker exec uns-claudejp-backend python /app/scripts/verify_data.py

# Importar datos
docker exec uns-claudejp-backend python /app/scripts/import_data.py

# Crear usuarios
docker exec uns-claudejp-backend python /app/scripts/create_admin_user.py

# Verificación completa
docker exec uns-claudejp-backend python /app/scripts/full_verification.py
```

---

## 🎨 ESTILOS Y COLORES

### Alertas de Visa
```javascript
期限切れ (Expirado): bg-red-100 text-red-800
要更新 (Requiere renovación): bg-orange-100 text-orange-800
注意 (Atención): bg-yellow-100 text-yellow-800
```

### Estados de Empleado
```javascript
在籍中 (Activo): bg-green-100 text-green-800
退社済 (Inactivo): bg-gray-100 text-gray-800
```

### Tipos de Contrato
```javascript
派遣社員: bg-blue-100 text-blue-800
請負社員: bg-purple-100 text-purple-800
スタッフ: bg-yellow-100 text-yellow-800
```

---

## 📞 INFORMACIÓN DE CONTACTO

### Sistema
- **Versión:** 2.0
- **Fecha sesión:** 2025-10-06
- **Estado:** Gestión de empleados completamente funcional

### Empresa
- **Nombre:** ユニバーサル企画株式会社 (UNS-KIKAKU)
- **Representante:** 中山 雅和
- **Teléfono:** 052-938-8840
- **Email:** infoapp@uns-kikaku.com

---

## ⚠️ NOTAS IMPORTANTES

1. **Logout obligatorio después de cambios en backend**
   - Cuando el backend se reinicia, los tokens anteriores pueden ser inválidos
   - Siempre hacer logout y volver a iniciar sesión

2. **Reconstruir frontend después de cambios**
   - El frontend en Docker no tiene hot-reload automático
   - Usar: `docker-compose build frontend && docker-compose up -d frontend`

3. **Campos calculados**
   - 年齢 (edad) se calcula en frontend
   - ｱﾗｰﾄ (alerta visa) se calcula en frontend
   - Considerar moverlos al backend para consistencia

4. **Fotos de empleados (photo_url)**
   - Actualmente el campo existe pero no hay sistema de upload
   - Pendiente: implementar upload y procesamiento de rirekisho

5. **Performance**
   - Vista extendida carga 50 empleados por página
   - Con 500 empleados, hay 10 páginas
   - Considerar virtualización para mejorar rendimiento con más datos

---

## 🔐 CREDENCIALES

### Usuarios del Sistema
```
Admin:
Username: admin
Password: admin123
Role: SUPER_ADMIN

Coordinator:
Username: coordinator
Password: coord123
Role: COORDINATOR
```

### Base de Datos
```
Host: localhost
Port: 5432
Database: uns_claudejp
User: uns_admin
Password: 57UD10R
```

---

## ✅ CHECKLIST ANTES DE TERMINAR SESIÓN

- [x] Verificar que todos los servicios estén corriendo
- [x] Hacer commit de cambios importantes
- [x] Documentar cambios en este README
- [x] Probar login y navegación básica
- [x] Verificar que la vista extendida funcione
- [ ] Hacer backup de base de datos (si hay datos importantes)
- [x] Guardar este archivo

---

**FIN DEL DOCUMENTO - SESIÓN 2025-10-06**

Para continuar, lee este documento completo y sigue con las tareas pendientes en la sección "PARA CONTINUAR EN LA PRÓXIMA SESIÓN".
