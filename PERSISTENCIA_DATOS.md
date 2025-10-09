# Persistencia de Datos - UNS-ClaudeJP 2.0

**Fecha:** 2025-10-09
**Versión:** 2.0

---

## ✅ Problema Resuelto: Los Datos SÍ Persisten

### Resumen
Los datos de la base de datos **SÍ se mantienen** entre reinicios de Docker gracias al uso de **volúmenes Docker persistentes**. El sistema está correctamente configurado para:

1. ✅ Guardar todos los datos en un volumen Docker
2. ✅ Cargar datos automáticamente al primer inicio
3. ✅ Detectar duplicados y no sobrescribir datos existentes
4. ✅ Mantener los datos aunque se detenga Docker

---

## 🔍 Cómo Funciona

### 1. Volumen Docker Persistente

En `docker-compose.yml` líneas 106-108:

```yaml
volumes:
  postgres_data:
    driver: local
```

Este volumen se almacena en el sistema de archivos del host y **NO se borra** cuando ejecutas `docker-compose down`.

### 2. Montaje del Volumen en PostgreSQL

Líneas 14-15:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

Todos los datos de PostgreSQL se guardan en este volumen persistente.

---

## 🚀 Proceso de Inicio

### Primera Vez (Datos Vacíos)

```
1. docker-compose up -d
   ↓
2. Contenedor 'db' (PostgreSQL) se inicia
   ↓
3. Contenedor 'importer' espera a que DB esté healthy
   ↓
4. Importer ejecuta: python scripts/import_data.py
   ↓
5. Se importan:
   - 21 Fábricas (de config/factories/)
   - 1027 Empleados 派遣社員 (de employee_master.xlsm)
   - ~X Empleados 請負社員
   - ~X Empleados スタッフ
   ↓
6. Importer termina (exit 0)
   ↓
7. Backend y Frontend se inician
```

### Reinicios Posteriores

```
1. docker-compose up -d
   ↓
2. PostgreSQL carga datos del volumen persistente
   ↓
3. Importer detecta duplicados y los salta:
   "⚠ 1027 duplicados omitidos"
   "⚠ 21 duplicados omitidos"
   ↓
4. Backend y Frontend se inician con datos intactos
```

---

## 📊 Verificación de Datos

### Ver Logs del Importer

```bash
docker logs uns-claudejp-importer
```

**Salida esperada en primer inicio:**
```
==================================================
RESUMEN DE IMPORTACIÓN
==================================================
Fábricas:           21
派遣社員:         1027
請負社員:          XXX
スタッフ:          XXX
──────────────────────────────────────────────────
TOTAL Empleados:  XXXX
==================================================
```

**Salida esperada en reinicios:**
```
✓ Importadas 0 fábricas a PostgreSQL
  ⚠ 21 duplicados omitidos

✓ Importados 0 empleados 派遣社員
  ⚠ 1027 duplicados omitidos
```

### Verificar Estado de Contenedores

```bash
docker ps
```

**Salida esperada:**
```
CONTAINER ID   IMAGE                     STATUS                    PORTS
887784ce788e   jpuns-claude20-frontend   Up 17 seconds             0.0.0.0:3000->3000/tcp
04fcb2c60a3c   jpuns-claude20-backend    Up 18 seconds             0.0.0.0:8000->8000/tcp
43a8f344abf6   postgres:15-alpine        Up 35 seconds (healthy)   0.0.0.0:5432->5432/tcp
```

### Consultar Datos Directamente

```bash
# Conectar a PostgreSQL
docker exec -it uns-claudejp-db psql -U uns_admin -d uns_claudejp

# Consultas SQL
SELECT COUNT(*) FROM employees;
SELECT COUNT(*) FROM factories;
SELECT COUNT(*) FROM candidates;

# Salir
\q
```

---

## 🔄 Comandos Docker

### Inicio Normal (Mantiene Datos)

```bash
docker-compose up -d
```

### Detener Servicios (Mantiene Datos)

```bash
docker-compose down
```

### Reiniciar con Rebuild (Mantiene Datos)

```bash
docker-compose down
docker-compose up -d --build
```

### ⚠️ ELIMINAR TODOS LOS DATOS (Cuidado)

```bash
# Detener servicios
docker-compose down

# Eliminar volúmenes (BORRA TODOS LOS DATOS)
docker volume rm jpuns-claude20_postgres_data

# O detener y eliminar volúmenes en un solo comando
docker-compose down -v
```

---

## 📁 Ubicación de los Datos

### En el Contenedor Docker

```
/var/lib/postgresql/data/
├── base/
├── global/
├── pg_wal/
└── [archivos de PostgreSQL]
```

### En el Host (Windows)

El volumen Docker se guarda en:
```
C:\ProgramData\Docker\volumes\jpuns-claude20_postgres_data\_data\
```

**Nota:** Esta ubicación es manejada automáticamente por Docker.

---

## 🔧 Solución de Problemas

### Problema: "No se cargan los datos después de reiniciar"

**Diagnóstico:**
```bash
# 1. Verificar que el volumen existe
docker volume ls | grep postgres_data

# 2. Ver logs del importer
docker logs uns-claudejp-importer

# 3. Verificar salud de PostgreSQL
docker ps
```

**Solución:**
- Si el volumen existe → Los datos están ahí
- Si el importer muestra "duplicados omitidos" → Los datos ya están cargados
- Si PostgreSQL está "healthy" → Todo funciona correctamente

### Problema: "Quiero empezar con datos frescos"

**Solución:**
```bash
# 1. Detener todo
docker-compose down -v

# 2. Iniciar desde cero
docker-compose up -d --build
```

### Problema: "Error de permisos en el volumen"

**Solución en Windows:**
```bash
# Dar permisos a Docker Desktop
# Settings → Resources → File Sharing
# Agregar: D:\JPUNS-app\JPUNS-CLAUDE2.0
```

---

## 📝 Archivos de Datos Fuente

### Empleados

Archivo: `config/employee_master.xlsm`

**Hojas:**
- `派遣社員` (Dispatch) - ~1027 registros
- `請負社員` (Contract) - ~XXX registros
- `スタッフ` (Staff) - ~XXX registros

### Fábricas

Directorio: `config/factories/`

**Archivos JSON:**
- Factory-01.json, Factory-02.json, etc.
- Total: ~21 fábricas activas

**Índice:** `config/factories_index.json`

---

## 🛡️ Respaldo de Datos

### Exportar Base de Datos

```bash
# Crear backup
docker exec uns-claudejp-db pg_dump -U uns_admin uns_claudejp > backup_$(date +%Y%m%d).sql

# Comprimir
gzip backup_$(date +%Y%m%d).sql
```

### Restaurar Base de Datos

```bash
# Detener servicios
docker-compose down

# Eliminar datos antiguos
docker volume rm jpuns-claude20_postgres_data

# Iniciar solo PostgreSQL
docker-compose up -d db

# Esperar a que esté healthy
docker ps

# Restaurar backup
gunzip backup_20251009.sql.gz
docker exec -i uns-claudejp-db psql -U uns_admin uns_claudejp < backup_20251009.sql

# Iniciar servicios completos
docker-compose up -d
```

---

## ✅ Checklist de Inicio

- [ ] `docker-compose up -d` ejecutado
- [ ] PostgreSQL está "healthy" (`docker ps`)
- [ ] Importer terminó exitosamente (`docker logs uns-claudejp-importer`)
- [ ] Backend está corriendo en puerto 8000
- [ ] Frontend está corriendo en puerto 3000
- [ ] Navegador en `http://localhost:3000` muestra login
- [ ] Login funciona (admin / admin123)
- [ ] Datos de empleados visibles en `/employees`

---

## 🎯 Conclusión

**Los datos SÍ persisten correctamente entre reinicios de Docker.**

El mensaje "duplicados omitidos" es **NORMAL y ESPERADO** en reinicios, ya que indica que el sistema detectó que los datos ya existen y **NO los sobrescribe**, preservando cualquier cambio manual que hayas hecho.

Para verificar que todo funciona:
1. Inicia sesión en http://localhost:3000
2. Ve a "従業員管理"
3. Deberías ver ~1027+ empleados
4. Los widgets muestran estadísticas correctas

---

**Última actualización:** 2025-10-09
**Estado:** ✅ Funcionando correctamente
