# Documentación activa de JPUNS Claude 2.0

Este directorio contiene únicamente los documentos vigentes que complementan al manual principal `ANALISIS_Y_RECOMENDACIONES.md`. Los archivos históricos que estaban duplicados u obsoletos se eliminaron para evitar información contradictoria y credenciales antiguas en el repositorio.

## Guías disponibles

| Archivo | Propósito |
| --- | --- |
| `../ANALISIS_Y_RECOMENDACIONES.md` | Guía estratégica y técnica unificada del sistema. |
| `reviews/system_code_review.md` | Revisión arquitectónica y lista de riesgos abiertos. |
| `technical/INSTRUCCIONES_COLUMNAS.md` | Referencia sobre el mapeo de columnas para importaciones desde Excel. |
| `sessions/` | Bitácoras de trabajo que documentan las últimas iteraciones relevantes del proyecto. |

## Prácticas recomendadas

- Centraliza cualquier actualización de arquitectura o roadmap en `ANALISIS_Y_RECOMENDACIONES.md`.
- Si se crea documentación nueva, valida primero que no duplique información existente y enlázala desde esta tabla.
- Evita subir credenciales reales o datos sensibles; utiliza variables de entorno y secretos gestionados fuera del repositorio.

Con esta limpieza la base documental queda reducida a los materiales necesarios para operar y evolucionar la aplicación sin ruido heredado.
