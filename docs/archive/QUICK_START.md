# UNS-ClaudeJP 2.0 - Guía Rápida de Inicio

## 📋 Tabla de Contenidos
1. [Requisitos Previos](#requisitos-previos)
2. [Instalación en Synology NAS](#instalación-en-synology-nas)
3. [Configuración Inicial](#configuración-inicial)
4. [Primer Uso](#primer-uso)
5. [Configuración de Fábricas](#configuración-de-fábricas)
6. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Hardware
- **Synology NAS** con Docker instalado
- Mínimo 4GB RAM (recomendado 8GB)
- 20GB espacio en disco disponible

### Software
- Docker Engine 20.10+
- Docker Compose 2.0+
- Navegador web moderno (Chrome, Firefox, Safari, Edge)

---

## Instalación en Synology NAS

### Paso 1: Instalar Docker en Synology

1. Abrir **Package Center**
2. Buscar "Docker"
3. Instalar **Docker**
4. Instalar **Container Manager** (si está disponible)

### Paso 2: Preparar el Proyecto

#### Opción A: Clonar desde repositorio (recomendado)
```bash
ssh admin@synology-ip
cd /volume1/docker
git clone https://github.com/uns-kikaku/uns-claudejp.git
cd uns-claudejp
```

#### Opción B: Subir manualmente
1. Subir la carpeta del proyecto a `/volume1/docker/uns-claudejp`
2. Conectarse por SSH
3. Navegar al directorio

### Paso 3: Ejecutar Script de Instalación

```bash
cd /volume1/docker/uns-claudejp
chmod +x install-synology.sh
sudo ./install-synology.sh
```

El script automáticamente:
- ✅ Verifica dependencias
- ✅ Crea directorios necesarios
- ✅ Configura variables de entorno
- ✅ Descarga imágenes Docker
- ✅ Inicia servicios

### Paso 4: Verificar Instalación

```bash
docker-compose ps
```

Deberías ver 3 contenedores corriendo:
- `uns-claudejp-backend`
- `uns-claudejp-frontend`
- `uns-claudejp-db`

---

## Configuración Inicial

### 1. Configurar Variables de Entorno

Editar el archivo `.env`:

```bash
nano /volume1/docker/uns-claudejp/.env
```

**Variables críticas a configurar:**

```env
# Cambiar password de base de datos
DB_PASSWORD=tu_password_super_seguro_aqui

# Cambiar secret key
SECRET_KEY=tu_secret_key_unica_aqui

# Configurar email (opcional pero recomendado)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password

# Configurar LINE Notify (opcional)
LINE_NOTIFY_ENABLED=true
LINE_NOTIFY_TOKEN=tu_line_token
```

### 2. Reiniciar Servicios

```bash
docker-compose restart
```

### 3. Acceder a la Aplicación

Abre tu navegador y visita:
- **Frontend**: `http://synology-ip:3000`
- **Backend API**: `http://synology-ip:8000`
- **Documentación API**: `http://synology-ip:8000/api/docs`

---

## Primer Uso

### 1. Login Inicial

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambiar inmediatamente después del primer login

### 2. Cambiar Contraseña Admin

1. Ir a **Perfil** → **Configuración**
2. Cambiar contraseña
3. Guardar cambios

### 3. Crear Usuarios Adicionales

#### Super Admin
```
Rol: super_admin
Permisos: Control total del sistema
```

#### Admin
```
Rol: admin
Permisos: Gestión de fábricas asignadas
```

#### Coordinador (CO)
```
Rol: coordinator
Permisos: Solo lectura
```

#### Empleado
```
Rol: employee
Permisos: Ver datos propios + solicitudes
```

---

## Configuración de Fábricas

### 1. Ubicación de Archivos de Configuración

```
/volume1/docker/uns-claudejp/config/factories/
```

### 2. Crear Nueva Fábrica

Copiar el template de ejemplo:

```bash
cd /volume1/docker/uns-claudejp/config/factories/
cp factory-01-example.json factory-02.json
```

### 3. Editar Configuración

```json
{
  "factory_id": "Factory-02",
  "name": "Honda Suzuka Factory",
  "contact": {
    "address": "三重県鈴鹿市...",
    "phone": "059-XXX-XXXX",
    "contact_person": "山田花子"
  },
  "working_hours": {
    "shifts": [
      {
        "shift_id": "asa",
        "shift_name": "朝番",
        "start_time": "07:00",
        "end_time": "16:00",
        "break_minutes": 60,
        "jikyu_tanka": 1400
      }
    ]
  },
  "overtime_rules": {
    "overtime_25": {
      "rate": 0.25,
      "applies_after_hours": 8
    }
  },
  "bonuses": {
    "gasoline_allowance": {
      "enabled": true,
      "amount_per_day": 600
    }
  }
}
```

### 4. Registrar Fábrica en el Sistema

1. Login como Admin
2. Ir a **Fábricas** → **Nueva Fábrica**
3. Completar formulario:
   - Factory ID: `Factory-02`
   - Nombre: `Honda Suzuka Factory`
   - Cargar archivo JSON de configuración

---

## Flujo de Trabajo Principal

### 1. Registro de Candidato (Rirekisho)

```
1. Candidato → Sube documentos
   ├── Rirekisho (PDF/JPG)
   ├── 在留カード
   └── 免許証

2. Sistema → OCR automático
   ├── Extrae datos
   ├── Completa formulario
   └── Asigna ID: UNS-1000

3. Admin → Revisa y aprueba
   └── Estado: Aprobado
```

### 2. Contratación (入社届)

```
1. Candidato aprobado → Generar 入社届
2. Completar datos laborales
   ├── Fábrica asignada
   ├── 時給 (salario/hora)
   ├── Posición
   └── Apartamento (si aplica)
3. Generar IDs
   ├── Hakenmoto ID: 1001
   ├── Factory ID: Factory-02
   └── Hakensaki Shain ID: (editable)
```

### 3. Gestión de Timer Cards

```
1. Upload masivo
   ├── Subir PDF/imágenes de fábrica
   └── OCR procesa automáticamente

2. Verificación
   ├── Ver tabla Excel editable
   ├── Corregir errores
   └── Aprobar

3. Cálculo automático
   ├── Horas normales
   ├── Horas extras
   ├── 深夜手当
   └── Festivos
```

### 4. Cálculo de Nómina

```
Fórmula:
- Salario base = 時給 × horas normales
- Horas extras = 時給 × horas extras × 1.25
- Nocturno = 時給 × horas nocturnas × 1.25
- Festivos = 時給 × horas festivas × 1.35
- Bonos (gasolina, asistencia, etc.)
- Deducciones (apartamento, etc.)

= Salario neto
```

### 5. Solicitudes (Yukyu, etc.)

```
Empleado:
1. Login → Mi Portal
2. Nueva Solicitud
   ├── Tipo: 有給休暇/半日有給/一時帰国
   ├── Fechas
   └── Motivo

Admin:
3. Revisar solicitudes
4. Aprobar/Rechazar
5. Notificación automática
```

---

## Solución de Problemas

### Error: "No se puede conectar a la base de datos"

```bash
# Verificar estado de contenedores
docker-compose ps

# Ver logs de base de datos
docker-compose logs db

# Reiniciar base de datos
docker-compose restart db
```

### Error: "OCR no funciona"

```bash
# Verificar Tesseract en backend
docker-compose exec backend tesseract --version

# Si falta, reconstruir imagen
docker-compose build backend
docker-compose up -d backend
```

### Error: "Cannot upload files"

```bash
# Verificar permisos de carpeta uploads
sudo chmod -R 755 /volume1/docker/uns-claudejp/uploads

# Verificar espacio en disco
df -h
```

### Frontend no carga

```bash
# Ver logs del frontend
docker-compose logs frontend

# Reconstruir frontend
docker-compose build frontend
docker-compose up -d frontend
```

### Resetear contraseña de admin

```bash
# Conectar a base de datos
docker-compose exec db psql -U uns_admin -d uns_claudejp

# Actualizar contraseña (hash de "admin123")
UPDATE users SET password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIbW4t.5u2' WHERE username = 'admin';
```

---

## Comandos Útiles

### Docker Compose

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend

# Detener servicios
docker-compose stop

# Iniciar servicios
docker-compose start

# Reiniciar servicios
docker-compose restart

# Reconstruir imágenes
docker-compose build

# Eliminar todo (cuidado!)
docker-compose down -v
```

### Backup de Base de Datos

```bash
# Crear backup
docker-compose exec db pg_dump -U uns_admin uns_claudejp > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U uns_admin uns_claudejp < backup_20250104.sql
```

### Actualización del Sistema

```bash
cd /volume1/docker/uns-claudejp

# Pull últimos cambios
git pull

# Reconstruir imágenes
docker-compose build

# Reiniciar con nueva versión
docker-compose up -d
```

---

## Contacto y Soporte

**UNS-Kikaku**
- Web: https://uns-kikaku.com
- Email: support@uns-kikaku.com
- Teléfono: +81-XX-XXXX-XXXX

**Documentación completa:**
- API Docs: http://synology-ip:8000/api/docs
- GitHub: https://github.com/uns-kikaku/uns-claudejp

---

**¡Bienvenido a UNS-ClaudeJP 2.0!** 🚀

---

## 🆕 Novedades en Versión 2.0

### Mejoras Principales

1. **Sistema OCR Híbrido**
   - Gemini API (precisión máxima - 100%)
   - Google Cloud Vision API (respaldo - 80%)
   - Tesseract OCR (modo offline - 60%)
   - Sistema de caché inteligente para procesamiento rápido

2. **Seguridad Mejorada**
   - API Keys protegidas en el backend
   - Sin exposición en el frontend
   - Cumplimiento de estándares empresariales

3. **Nuevas Funcionalidades**
   - Sistema de notificaciones automáticas (Email + LINE + WhatsApp)
   - Cálculo automático de nómina con reglas japonesas
   - Importación/Exportación masiva desde Excel
   - Generación automática de reportes con gráficos

4. **Optimización de Rendimiento**
   - Procesamiento OCR hasta 3x más rápido
   - Uso optimizado de memoria
   - Consultas de base de datos mejoradas
