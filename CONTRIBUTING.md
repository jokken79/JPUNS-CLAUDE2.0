# Guía de Contribución - UNS-ClaudeJP 2.0

## Cómo Contribuir

### Reporte de Errores
1. Verifica si el error ya fue reportado
2. Crea un issue detallando:
   - Pasos para reproducir
   - Comportamiento esperado
   - Comportamiento actual
   - Logs relevantes

### Sugerencias de Mejoras
1. Abre un issue con la etiqueta "enhancement"
2. Describe la mejora propuesta
3. Explica por qué sería útil

### Pull Requests
1. Haz un fork del proyecto
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit tus cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

## Estándares de Código

### Backend (Python)
- Seguir PEP 8
- Usar type hints
- Documentar funciones y clases
- Manejar excepciones apropiadamente

### Frontend (TypeScript/React)
- Usar TypeScript estricto
- Seguir convenciones de React
- Componentes funcionales con hooks
- Documentar componentes

### Mensajes de Commit
- Use el presente imperativo: "Añadir feature" en vez de "Añadí feature"
- Límite de 50 caracteres para el título
- Describir qué y por qué, no cómo

## Flujo de Trabajo

1. Asignarse un issue o crear uno nuevo
2. Crear una rama desde `develop`
3. Desarrollar la funcionalidad
4. Añadir pruebas si es necesario
5. Actualizar documentación
6. Crear Pull Request a `develop`
7. Esperar revisión y aprobación

## Testing

### Backend
```bash
cd backend
python -m pytest
```

### Frontend
```bash
cd frontend
npm test
```

## Documentación

Actualiza la documentación relevante:
- README.md para cambios generales
- QUICK_START.md para cambios en el flujo de inicio
- Documentación de API para cambios en endpoints

## Agradecimientos

¡Gracias por contribuir a UNS-ClaudeJP 2.0!