# Cambios en Base de Datos - UNS-ClaudeJP 2.0

**Fecha:** 2025-10-09
**Versión:** 2.1

---

## ✅ Cambios Implementados

### 1. **Reestructuración de Base de Datos**

Se separaron los empleados en 3 tablas distintas según el tipo de contrato:

#### **Tabla: `employees`** (派遣元社員 - Dispatch Workers)
- **Total registros:** 348
- **Descripción:** Trabajadores派遣元 que van a fábricas con contratos estándar
- **Salario:** Por hora (時給)

#### **Tabla: `contract_workers`** (請負社員 - Contract Workers)
- **Total registros:** 133
- **Descripción:** Trabajadores con contrato請負, también van a fábricas pero con tipo de contrato diferente
- **Salario:** Por hora (時給)

#### **Tabla: `staff`** (スタッフ - Office/HR Personnel)
- **Total registros:** 19
- **Descripción:** Personal de oficina/RRHH (Kanrininsha), NO van a fábricas
- **Salario:** Mensual fijo

### 2. **Nuevos Roles de Usuario**

Actualización del enum `UserRole`:
```python
class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"                    # Administrador del sistema
    KANRININSHA = "KANRININSHA"       # Staff - Personal de oficina/RRHH
    EMPLOYEE = "EMPLOYEE"              # 派遣元社員 - Trabajadores dispatch
    CONTRACT_WORKER = "CONTRACT_WORKER"  # 請負 - Trabajadores con contrato
```

**Permisos por rol:**
- **ADMIN:** Acceso completo al sistema
- **KANRININSHA (Staff):** Puede gestionar rirekisho, empleados, etc.
- **EMPLOYEE / CONTRACT_WORKER:** Solo pueden ver sus propias nóminas y contratos digitales

---

## 📋 Nuevos Campos Agregados

Se agregaron TODOS los campos del Excel `employee_master.xlsm` para mantener compatibilidad completa:

### Campos de Asignación
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `assignment_location` | String(200) | 配属先 - Ubicación de asignación |
| `assignment_line` | String(200) | 配属ライン - Línea de asignación |
| `job_description` | Text | 仕事内容 - Descripción del trabajo |

### Campos de Fechas
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `current_hire_date` | Date | 現入社 - Fecha de entrada a fábrica actual (importante para cambios de fábrica) |
| `jikyu_revision_date` | Date | 時給改定 - Fecha de revisión de salario |
| `billing_revision_date` | Date | 請求改定 - Fecha de revisión de facturación |

### Todos los Campos del Excel

**Información Personal:**
- 氏名 (full_name_kanji)
- カナ (full_name_kana)
- 性別 (gender)
- 国籍 (nationality)
- 生年月日 (date_of_birth)

**Información Laboral:**
- 社員№ (hakenmoto_id)
- 派遣先ID (factory_id)
- 派遣先社員ID (hakensaki_shain_id)
- 配属先 (assignment_location) ⭐ NUEVO
- 配属ライン (assignment_line) ⭐ NUEVO
- 仕事内容 (job_description) ⭐ NUEVO
- 入社日 (hire_date)
- 現入社 (current_hire_date) ⭐ NUEVO
- 退社日 (termination_date)

**Información Salarial:**
- 時給 (jikyu)
- 時給改定 (jikyu_revision_date) ⭐ NUEVO
- 請求単価 (hourly_rate_charged)
- 請求改定 (billing_revision_date) ⭐ NUEVO
- 差額利益 (profit_difference)
- 標準報酬 (standard_compensation)

**Seguro Social:**
- 健康保険 (health_insurance)
- 介護保険 (nursing_insurance)
- 厚生年金 (pension_insurance)
- 社保加入 (social_insurance_date)

**Información de Visa:**
- ビザ期限 (zairyu_expire_date)
- ビザ種類 (visa_type)

**Otros:**
- 〒 (postal_code)
- 住所 (address)
- 入社依頼 (entry_request_date)
- 備考 (notes)
- 免許種類 (license_type)
- 免許期限 (license_expire_date)
- 通勤方法 (commute_method)
- 任意保険期限 (optional_insurance_expire)
- 日本語検定 (japanese_level)
- キャリアアップ5年目 (career_up_5years)

---

## 🎨 Nuevas Funcionalidades de UI

### 1. **Sistema de Alertas de Visa** (ビザ期限アラート)

Indicadores visuales automáticos basados en el vencimiento de visa:

| Estado | Días Restantes | Color | Indicador |
|--------|----------------|-------|-----------|
| **Vencido** | < 0 días | 🔴 Rojo | 3 círculos rojos + "期限切れ" parpadeante |
| **Crítico** | ≤ 10 días | 🔴 Rojo | 1 círculo rojo + ⚠️ exclamación |
| **Advertencia** | ≤ 30 días | 🔴 Rojo claro | 1 círculo rojo |
| **Precaución** | ≤ 90 días | 🟡 Amarillo | 1 círculo amarillo |
| **Bueno** | > 90 días | 🟢 Verde | 1 círculo verde |

**Implementación:**
- Componente: `frontend/src/components/VisaAlert.tsx`
- Cálculo automático basado en fecha actual vs zairyu_expire_date
- Muestra días restantes en badge

### 2. **Selector de Columnas Visibles/Ocultas**

Permite mostrar u ocultar columnas dinámicamente en la tabla de empleados:

**Características:**
- ✅ Dropdown con lista de TODAS las columnas disponibles (37+ columnas)
- ✅ Checkbox para cada columna
- ✅ Botones "全て表示" / "全て非表示"
- ✅ Contador de columnas visibles
- ✅ Estado persistente en localStorage
- ✅ Interfaz intuitiva con iconos 👁️ (visible) / 👁️‍🗨️ (oculto)

**Columnas visibles por defecto:**
- 現在 (status)
- 社員№ (hakenmoto_id)
- 氏名 (full_name_kanji)
- カナ (full_name_kana)
- 派遣先ID (factory_id)
- 配属先 (assignment_location)
- 時給 (jikyu)
- ビザ期限 (zairyu_expire_date) con alertas visuales
- 入社日 (hire_date)
- 現入社 (current_hire_date)
- アクション (actions)

**Implementación:**
- Componente: `frontend/src/components/ColumnSelector.tsx`
- Página: `frontend/src/pages/EmployeesExtended.tsx` (従業員管理（詳細）)

---

## 🔄 Script de Importación Actualizado

El script `backend/scripts/import_data.py` fue completamente actualizado para:

1. **Leer TODOS los campos del Excel** usando `row.get()` con nombres de columnas exactos
2. **Funciones helper** para parseo seguro:
   - `parse_date()` - Convierte fechas de Excel a objetos Date
   - `parse_int()` - Convierte números de Excel a enteros
   - `get_str()` - Obtiene strings de forma segura
3. **Detección de duplicados** usando `hakenmoto_id` (employees), `staff_id` (staff)
4. **Manejo de errores** individual por fila para no perder toda la importación por un error

**Resultados de última importación:**
```
Fábricas:          21
派遣社員:         348
請負社員:         133
スタッフ:          19
──────────────────────────────────
TOTAL Empleados:  500
```

---

## 🗄️ Esquema de Base de Datos

### Tabla `employees`
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    hakenmoto_id INTEGER UNIQUE NOT NULL,
    factory_id VARCHAR(20),
    hakensaki_shain_id VARCHAR(50),

    -- Personal info
    full_name_kanji VARCHAR(100) NOT NULL,
    full_name_kana VARCHAR(100),
    date_of_birth DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),

    -- Employment
    hire_date DATE,
    current_hire_date DATE,      -- NUEVO
    jikyu INTEGER NOT NULL,
    jikyu_revision_date DATE,    -- NUEVO

    -- Assignment
    assignment_location VARCHAR(200),  -- NUEVO
    assignment_line VARCHAR(200),      -- NUEVO
    job_description TEXT,              -- NUEVO

    -- Financial
    hourly_rate_charged INTEGER,
    billing_revision_date DATE,  -- NUEVO
    profit_difference INTEGER,
    standard_compensation INTEGER,
    health_insurance INTEGER,
    nursing_insurance INTEGER,
    pension_insurance INTEGER,

    -- ... más campos ...

    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Tabla `contract_workers`
Misma estructura que `employees` pero para trabajadores請負.

### Tabla `staff`
Similar a `employees` pero con:
- `staff_id` en lugar de `hakenmoto_id`
- `monthly_salary` en lugar de `jikyu` (salario mensual en vez de por hora)
- Sin campos relacionados a fábricas (no van a fábricas)

---

## 📊 Widgets de Estadísticas

En la página **従業員管理（詳細）**:

```
┌─────────────────┬─────────────────┬─────────────────┐
│ 総従業員数      │ 在籍中         │ 退社済         │
│    500          │    348          │    152          │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## 🔧 Comandos de Mantenimiento

### Ver datos en base de datos
```bash
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
  SELECT COUNT(*) FROM employees;
  SELECT COUNT(*) FROM contract_workers;
  SELECT COUNT(*) FROM staff;
"
```

### Reimportar datos
```bash
docker restart uns-claudejp-importer
docker logs uns-claudejp-importer --tail 50
```

### Crear usuario admin
```bash
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
  INSERT INTO users (username, email, password_hash, role, full_name, is_active)
  VALUES ('admin', 'admin@uns-kikaku.com', '\$2b\$12\$xyGWtUHQKgXoPdOavoEL9O7M6MYEzLkr5t8qy7/FVHW6G51b2uRo2', 'ADMIN', 'System Administrator', true)
  ON CONFLICT (username) DO UPDATE SET role = 'ADMIN';
"
```

Credenciales: `admin` / `admin123`

---

## 📝 Archivos Modificados

### Backend
- `backend/app/models/models.py` - Agregados campos nuevos a Employee, ContractWorker, Staff
- `backend/scripts/import_data.py` - Actualizado para importar TODOS los campos del Excel

### Frontend
- `frontend/src/components/VisaAlert.tsx` - Nuevo componente para alertas de visa
- `frontend/src/components/ColumnSelector.tsx` - Nuevo componente para selector de columnas
- `frontend/src/pages/EmployeesExtended.tsx` - Actualizado con nuevas funcionalidades

---

## ✅ Testing

### Verificar importación correcta
```bash
docker exec uns-claudejp-db psql -U uns_admin -d uns_claudejp -c "
  SELECT
    hakenmoto_id,
    full_name_kanji,
    assignment_location,
    current_hire_date,
    jikyu_revision_date,
    zairyu_expire_date
  FROM employees
  LIMIT 10;
"
```

### Verificar alertas de visa
1. Ir a http://localhost:3000/employees-extended
2. Login con `admin` / `admin123`
3. Ver la columna "ビザ期限"
4. Verificar colores según días restantes

### Verificar selector de columnas
1. Click en botón "列表示" (arriba derecha)
2. Seleccionar/deseleccionar columnas
3. Verificar que la tabla se actualiza en tiempo real

---

## 🚀 Próximos Pasos

1. ✅ Implementar búsqueda avanzada por múltiples campos
2. ✅ Exportar a Excel con formato
3. ✅ Gráficos de estadísticas de visas
4. ✅ Notificaciones automáticas de visas por vencer
5. ✅ Dashboard con alertas en tiempo real

---

**Última actualización:** 2025-10-09
**Estado:** ✅ Funcionando correctamente
**Versión:** 2.1
