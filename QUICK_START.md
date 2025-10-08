# Inicio Rápido - UNS-ClaudeJP 2.0

## Pasos para Poner en Marcha el Sistema

### 1. Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd JPUNS-CLAUDE2.0
```

### 2. Configurar Variables de Entorno
```bash
cp .env.example .env
```

Edita el archivo `.env` y configura al menos estas variables:
```bash
DB_PASSWORD=una_contraseña_segura
SECRET_KEY=una_clave_secreta_muy_larga_y_aleatoria
GEMINI_API_KEY=tu_clave_de_gemini
```

### 3. Iniciar el Sistema
```bash
docker-compose up -d --build
```

### 4. Acceder al Sistema
- Frontend: http://localhost:3000
- API: http://localhost:8000
- Documentación: http://localhost:8000/api/docs

### 5. Iniciar Sesión
- Usuario: `admin`
- Contraseña: `admin123`

## Verificación de Funcionamiento

### 1. Verificar Backend
```bash
curl http://localhost:8000/
```
Debería retornar información del sistema.

### 2. Verificar Base de Datos
```bash
docker-compose exec db psql -U uns_admin -d uns_claudejp -c "\dt"
```
Debería mostrar todas las tablas.

### 3. Verificar Frontend
Abre http://localhost:3000 en tu navegador y deberías ver la pantalla de login.

## Problemas Comunes y Soluciones

### El backend no inicia
```bash
# Verificar logs
docker-compose logs backend

# Reiniciar backend
docker-compose restart backend
```

### Error de conexión a base de datos
```bash
# Verificar estado de la BD
docker-compose ps db

# Reiniciar BD
docker-compose restart db
```

### El frontend no carga
```bash
# Reconstruir frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

## Flujo de Trabajo Básico

### 1. Registrar un Candidato
1. Inicia sesión como admin
2. Ve a "Candidatos" → "Nuevo Candidato"
3. Completa los datos básicos
4. Sube el 履歴書 (CV) para procesamiento OCR

### 2. Aprobar Candidato
1. Ve a la lista de candidatos
2. Selecciona el candidato deseado
3. Haz clic en "Aprobar"
4. El sistema lo convertirá automáticamente en empleado

### 3. Registrar Tarjeta de Tiempo
1. Ve a "Tarjetas de Tiempo"
2. Selecciona el empleado y fecha
3. Registra horas de entrada y salida
4. El sistema calculará automáticamente las horas extras

### 4. Generar Nómina
1. Ve a "Salarios"
2. Selecciona mes y año
3. Haz clic en "Calcular Salario"
4. Revisa los resultados y genera el payslip

## Importación Masiva

### Importar Empleados desde Excel
1. Prepara un archivo Excel con las columnas requeridas
2. Ve a "Importar Datos" → "Importar Empleados"
3. Sube tu archivo Excel
4. Revisa los resultados de la importación

### Importar Tarjetas de Tiempo
1. Prepara un archivo Excel con las columnas: 日付, 社員ID, 出勤時刻, 退勤時刻
2. Ve a "Importar Datos" → "Importar Tarjetas de Tiempo"
3. Selecciona la fábrica, mes y año
4. Sube tu archivo Excel

## Configuración de OCR

El sistema tiene un sistema OCR híbrido:
1. **Gemini API** (primario) - Obtén tu clave en https://makersuite.google.com/app/apikey
2. **Google Vision API** (respaldo) - Configura en Google Cloud Console
3. **Tesseract** (local) - Funciona sin conexión, pero menor precisión

Para activar el OCR:
```bash
# En tu archivo .env
GEMINI_API_KEY=tu_clave_gemini
GOOGLE_CLOUD_VISION_API_KEY=tu_clave_vision
OCR_ENABLED=true
```

## Soporte y Ayuda

Para obtener ayuda:
1. Revisa los logs: `docker-compose logs [servicio]`
2. Consulta la documentación completa en README.md
3. Verifica la configuración en el archivo .env

## Resumen de Comandos Útiles

```bash
# Iniciar todo
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Detener todo
docker-compose down

# Reconstruir un servicio específico
docker-compose build --no-cache backend

# Acceder a la base de datos
docker-compose exec db psql -U uns_admin -d uns_claudejp

# Reiniciar un servicio
docker-compose restart [servicio]
```

¡Listo! Ahora deberías tener UNS-ClaudeJP 2.0 funcionando correctamente.