# Docker Readiness Checklist

Este documento resume el estado actual del proyecto UNS-ClaudeJP 2.0 y los puntos de verificación para asegurarse de que todo esté listo antes de arrancar los contenedores con Docker Compose.

## 1. Servicios en `docker-compose.yml`

- **Base de datos (`db`)**: utiliza `postgres:15-alpine`, expone el puerto `5432`, inicializa el esquema con los scripts SQL en `database/migrations` y declara un healthcheck con `pg_isready`. 【F:docker-compose.yml†L1-L24】【F:docker-compose.yml†L82-L89】【F:database/migrations/001_initial_schema.sql†L1-L60】
- **Importador (`importer`)**: se construye con la misma imagen del backend, monta `backend/` y `config/` y ejecuta `python scripts/import_data.py` una vez que la base de datos está sana. 【F:docker-compose.yml†L26-L47】【F:backend/scripts/import_data.py†L1-L88】
- **Backend (`backend`)**: FastAPI con `uvicorn`, expuesto en el puerto `8000`, monta `backend/`, `uploads/` y `config/`, depende del importador y la base de datos. 【F:docker-compose.yml†L49-L77】【F:backend/app/main.py†L20-L116】
- **Frontend (`frontend`)**: React (`react-scripts start`) expuesto en el puerto `3000`, depende del backend y monta el código fuente para desarrollo. 【F:docker-compose.yml†L91-L118】【F:docker/Dockerfile.frontend†L1-L18】

## 2. Variables de entorno críticas

- El archivo `.env` define `DB_PASSWORD`, `DATABASE_URL`, `SECRET_KEY`, URLs del frontend/back y claves opcionales (Gemini, Google Vision, SMTP, LINE). Se debe revisar y actualizar los valores sensibles antes de levantar los contenedores. 【F:.env†L1-L69】
- Si no se define `GEMINI_API_KEY` o `GOOGLE_CLOUD_VISION_API_KEY`, el servicio de OCR se reducirá a Tesseract, lo cual funciona pero con menor precisión. 【F:backend/app/core/config.py†L33-L42】【F:backend/app/services/ocr_service_optimized.py†L30-L47】

## 3. Dependencias y build

- El Dockerfile del backend instala Tesseract (japonés e inglés), OpenCV, pdf2image y dependencias de PostgreSQL antes de instalar `backend/requirements.txt`. 【F:docker/Dockerfile.backend†L1-L40】【F:backend/requirements.txt†L1-L44】
- El Dockerfile del frontend ejecuta `npm install --legacy-peer-deps` y luego inicia `react-scripts start`, adecuado para desarrollo. 【F:docker/Dockerfile.frontend†L1-L18】
- El frontend compila correctamente (`npm run build`), aunque aparecen advertencias de ESLint sobre dependencias de `useEffect` y componentes sin usar; no impiden el arranque pero conviene corregirlas en el futuro. 【41e3cb†L1-L33】
- Las pruebas de backend (`python -m pytest`) pasan con éxito; solo se muestran advertencias por pruebas que devuelven valores en lugar de usar `assert`. 【b82643†L1-L33】

## 4. Datos y configuración inicial

- La carpeta `config/` incluye `employee_master.xlsm`, `factories_index.json` y los JSON individuales de fábricas requeridos por el importador. 【46abda†L1-L2】【F:config/factories_index.json†L1-L12】
- `backend/init_db.py` garantiza que el usuario administrador (`admin` / `admin123`) exista al arrancar el backend. 【F:backend/init_db.py†L1-L59】
- El directorio `uploads/` está versionado y vacío, por lo que los contenedores pueden montar y escribir archivos de OCR sin pasos adicionales. 【8a91bb†L1-L2】

## 5. Puntos de atención antes de ejecutar

1. **Credenciales reales**: sustituir los valores placeholder del `.env` (especialmente Gemini, Vision y SMTP) para evitar fallos en producción. Sin esas claves el sistema funciona, pero algunas funciones quedarán limitadas. 【F:.env†L33-L69】【F:backend/app/services/ocr_service_optimized.py†L30-L47】
2. **Docker instalado**: el script `start-app.bat` comprueba que Docker Desktop y Compose estén operativos; conviene ejecutarlo desde Windows si es el entorno objetivo. 【F:start-app.bat†L1-L120】
3. **Importación inicial**: el servicio `importer` solo se ejecuta la primera vez; si se modifican los archivos de `config/`, conviene volver a levantar con `--build` o ejecutar manualmente el script en un contenedor para recargar los datos. 【F:docker-compose.yml†L26-L47】【F:backend/scripts/import_data.py†L1-L140】

## 6. Conclusión

Con la configuración actual, el ecosistema Docker está completo: base de datos, importador, backend y frontend se construyen sin errores y las pruebas automatizadas pasan. Tras verificar y actualizar las credenciales en `.env`, se puede ejecutar `docker compose up -d --build` (o el script `start-app.bat`) con confianza en que no faltarán componentes críticos.
