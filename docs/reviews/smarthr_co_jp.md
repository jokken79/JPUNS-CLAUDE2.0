# Recomendaciones para SmartHR (smarthr.co.jp)

## Resumen ejecutivo
- El sitio transmite de forma efectiva la identidad de marca, pero existe margen para mejorar el rendimiento percibido y la accesibilidad.
- Se observan oportunidades de consolidación de recursos front-end y de adopción de mejores prácticas de internacionalización.

## Observaciones clave

### Rendimiento y experiencia de usuario
- **Carga inicial:** El sitio depende de paquetes JavaScript pesados que bloquean la interacción inicial. Se recomienda:
  - Analizar el bundle con herramientas como `webpack-bundle-analyzer` y habilitar *code splitting* para rutas secundarias.
  - Implementar *lazy loading* para componentes que se cargan por debajo del pliegue.
  - Servir imágenes responsivas en formato WebP/AVIF con `srcset` y `sizes` para reducir transferencia.
- **Optimización crítica de CSS:** Incluir *critical CSS* en el HTML inicial para acelerar el primer render, moviendo el resto a cargas diferidas.

### Accesibilidad
- **Contraste de color:** Algunas secciones combinan texto claro sobre fondos claros. Validar con `axe-core` o `Lighthouse` y ajustar variables SCSS para cumplir WCAG AA.
- **Navegación mediante teclado:** Asegurar que modales y menús móviles administren el foco correctamente (`focus-trap`, `aria-hidden`).
- **Etiquetas ARIA y semántica:** Revisar componentes reutilizables (tabs, carouseles) para añadir roles y `aria-label` coherentes. Priorizar HTML semántico antes de divs anidados.

### SEO e internacionalización
- **Metadatos dinámicos:** Implementar componentes `<Head>` (Next.js) o actualizaciones `meta` (React Helmet) por página para títulos y descripciones únicos.
- **Marcado estructurado:** Agregar `JSON-LD` para eventos, ofertas laborales y FAQ para mejorar rich snippets.
- **i18n:** Centralizar cadenas en archivos de localización (`en`, `ja`) y configurar detección de idioma automática; evita *hardcodes* en componentes.

### Recomendaciones de código específicas
- Adoptar un estilo de componentes funcionales con TypeScript estricto (`strictNullChecks`, `noImplicitAny`) para mejorar mantenibilidad.
- Configurar pruebas de regresión visual con Playwright + Percy para garantizar consistencia tras cambios de UI.
- Añadir *linting* específico de accesibilidad (`eslint-plugin-jsx-a11y`) y reglas de diseño (`eslint-plugin-react-hooks`).
- Implementar *Storybook* para documentar y probar componentes aislados, lo que facilita la colaboración entre diseño e ingeniería.

## Próximos pasos sugeridos
1. Ejecutar auditoría Lighthouse y priorizar acciones de rendimiento > 80/100.
2. Elaborar backlog de deuda técnica con responsables y métricas (LCP < 2.5s, CLS < 0.1).
3. Integrar métricas de usuario real (RUM) con herramientas como Google Analytics 4 o New Relic Browser.
4. Planificar sprints de refactorización gradual adoptando las prácticas descritas.

## Métricas recomendadas
- **Core Web Vitals:** LCP, FID, CLS monitoreados continuamente.
- **Accesibilidad:** Puntajes de axe-core > 90.
- **SEO:** Incremento del CTR orgánico y cobertura completa en Google Search Console.

## Referencias
- [Web.dev Performance Optimization](https://web.dev/fast/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [Google Structured Data](https://developers.google.com/search/docs/advanced/structured-data/intro-structured-data)
