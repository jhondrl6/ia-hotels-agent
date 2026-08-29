# FASE-1: Setup + Dataclass + Templates ✅ COMPLETADA (2026-07-09)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)

## Contexto previo
Plan greenfield: no existen fases anteriores. El repo iah-cli está en su estado actual (v4.48.x). Se verificó que ninguno de los archivos a crear existe.

## Objetivo de esta fase
Preparar toda la infraestructura estática del módulo: instalar dependencias, crear el dataclass `HookPDFData`, crear el template HTML y los estilos CSS. Al final de esta fase, todo el "código muerto" (estructura sin lógica) está listo para que FASE-2 lo conecte.

### Tareas
- [ ] 1.1 Instalar dependencias: `sudo apt install -y libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev` + `uv pip install weasyprint pyyaml`
- [ ] 1.2 Crear `HookPDFData` dataclass en `modules/commercial_documents/data_structures.py` con campos para todos los placeholders del catálogo §3.2 (datos del hotel, financieros, scores 4 pilares, 3 brechas, pricing) + `evidence_tier: str`
- [ ] 1.3 Exportar `HookPDFData` en `modules/commercial_documents/__init__.py`
- [ ] 1.4 Crear `templates/hook_template.md` — template HTML con placeholders `{{}}` (weasyprint renderiza HTML, no markdown; el archivo lleva extensión .md por convención del repo pero su contenido es HTML)
- [ ] 1.5 Crear `templates/hook_styles.css` — diseño de 2 páginas exactas, cifra gancho ≥24pt, sin números de página

### Restricciones
- NO crear `hook_pdf_generator.py` aún (es FASE-2)
- NO modificar `main.py` aún (es FASE-2)
- El template debe contener TODOS los placeholders del catálogo §3.2 de MODULO-HOOK-PDF.md: `{{HOTEL_NOMBRE}}`, `{{HOTEL_URL}}`, `{{HOTEL_REGION}}`, `{{HOTEL_DIRECCION}}`, `{{GBP_RESENAS}}`, `{{GBP_RATING}}`, `{{FUGA_MENSUAL}}`, `{{FUGA_MINIMA}}`, `{{FUGA_MAXIMA}}`, `{{COMISION_OTA_REAL}}`, `{{RECUPERACION_6M}}`, `{{ROI}}`, `{{FUGA_6M}}`, `{{SEO_SCORE}}`, `{{SEO_REGIONAL}}`, `{{GEO_SCORE}}`, `{{GEO_REGIONAL}}`, `{{AEO_SCORE}}`, `{{AEO_REGIONAL}}`, `{{IAO_SCORE}}`, `{{IAO_REGIONAL}}`, `{{BRECHA_1_NOMBRE}}`, `{{BRECHA_1_COP}}`, `{{BRECHA_1_JUSTIFICACION}}` (×3), `{{PRECIO_EXPRESS}}`, `{{PRECIO_MENSUAL}}`, `{{SETUP_FEE}}`
- El CSS debe usar `@page` con `size: A4` y `margin: 0` para control total de 2 páginas
- Re-leer `PROPUESTA_EMPAQUETADO_NO_TECNICO.md` §3 (estructura visual) antes de crear el template

### Criterios de completitud
- [ ] weasyprint importa sin error: `python3 -c "import weasyprint; print(weasyprint.__version__)"`
- [ ] pyyaml importa sin error
- [ ] `HookPDFData` instanciable con todos los campos del catálogo
- [ ] `from modules.commercial_documents import HookPDFData` funciona
- [ ] Template contiene los 30+ placeholders (verificar con grep `{{`)
- [ ] CSS tiene `@page` rule con `size: A4`
- [ ] Estructura visual del template coincide con §3.3 de MODULO-HOOK-PDF.md (página 1: header+cifra+brechas+tabla; página 2: explicación+proyección+CTA)

### Próxima sesión
FASE-2: Implementar `hook_pdf_generator.py` (clase HookPDFGenerator con extract/validate/render/generate) + integrar comando `hook-pdf` en `main.py`.

### Prompt para delegate_task

```
Goal: Eres un subagente trabajando en el repositorio iah-cli en /mnt/c/Users/Jhond/Github/iah-cli. Tu tarea es ejecutar FASE-1 del plan HOOK-PDF-2026-07-09.

Contexto: Estás implementando un módulo generador de PDFs gancho de 2 páginas para hoteleros. El plan maestro está en /.opencode/plans/Archives/HOOK-PDF-2026-07-09/01-plan-maestro.md. La especificación completa está en /.opencode/context/Historico/MODULO-HOOK-PDF.md (arquitectura) y output/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md (visual).

Tareas:
1. Instalar dependencias: sudo apt install -y libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev. Luego en el venv del proyecto: uv pip install weasyprint pyyaml. Verificar imports.
2. Crear dataclass HookPDFData en modules/commercial_documents/data_structures.py. Campos: hotel_nombre, hotel_url, hotel_region, hotel_direccion, gbp_resenas, gbp_rating, fuga_mensual, fuga_minima, fuga_maxima, comision_ota_real, recuperacion_6m, roi, fuga_6m, seo_score, seo_regional, geo_score, geo_regional, aeo_score, aeo_regional, iao_score, iao_regional, brecha_1_nombre, brecha_1_cop, brecha_1_justificacion, brecha_2_nombre, brecha_2_cop, brecha_2_justificacion, brecha_3_nombre, brecha_3_cop, brecha_3_justificacion, precio_express, precio_mensual, setup_fee, evidence_tier. Todos como str (los COP van formateados como string).
3. Exportar HookPDFData en modules/commercial_documents/__init__.py
4. Crear templates/hook_template.md con contenido HTML (no markdown) que será renderizado por weasyprint. Usar todos los placeholders del catálogo. Estructura: página 1 con header (nombre, dirección, GBP), cifra gancho grande, disclaimer, top 3 brechas, tabla 4 pilares. Página 2 con explicación, proyección (6M, ROI, fuga), CTA con precio Express.
5. Crear templates/hook_styles.css con @page size A4, cifra gancho font-size 24pt mínimo, 2 páginas exactas.

Restricciones: NO crear hook_pdf_generator.py ni modificar main.py. Responder en español.
```
