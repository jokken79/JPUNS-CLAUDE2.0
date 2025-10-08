# Guía de Uso Diario - UNS-ClaudeJP 2.0

## Para Iniciar la Aplicación

### Primera Vez (Solo una vez)
1. Ejecuta `install-windows.bat`
2. Configura tu archivo `.env` cuando te lo pida
3. Espera a que termine la instalación

### Uso Diario (Cada vez que prendes tu PC)
1. **Doble clic en `start-app.bat`**
2. Espera a que veas el mensaje "UNS-ClaudeJP 2.0 is Ready!"
3. La aplicación se abrirá automáticamente en tu navegador

### Para Detener la Aplicación
1. **Doble clic en `stop-app.bat`**
2. Espera a que veas "Application stopped successfully"

## Acceso a la Aplicación

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs

### Datos de Acceso
- **Usuario**: admin
- **Contraseña**: admin123

## Si Tienes Problemas

### La aplicación no inicia
1. Asegúrate que Docker Desktop esté abierto
2. Espera 2-3 minutos después de iniciar Docker
3. Vuelve a ejecutar `start-app.bat`

### Error de "Docker no encontrado"
1. Instala Docker Desktop desde: https://www.docker.com/products/docker-desktop
2. Reinicia tu PC
3. Ejecuta `install-windows.bat` nuevamente

### La página no carga
1. Espera 1-2 minutos más
2. Refresca el navegador (F5)
3. Si aún no funciona, ejecuta `stop-app.bat` y luego `start-app.bat`

## Flujo de Trabajo Básico

1. **Registrar Candidato**: Ve a "Candidatos" → "Nuevo Candidato"
2. **Aprobar Candidato**: Selecciona el candidato y haz clic en "Aprobar"
3. **Registrar Tiempo**: Ve a "Tarjetas de Tiempo" y registra las horas
4. **Generar Salario**: Ve a "Salarios" y calcula el salario mensual

## Recomendaciones

- Cierra la aplicación con `stop-app.bat` antes de apagar tu PC
- No cierres la ventana de Docker mientras usas la aplicación
- Si no usarás la aplicación por varios días, usa `stop-app.bat`

¡Listo! Con esto puedes usar tu aplicación diariamente sin problemas.