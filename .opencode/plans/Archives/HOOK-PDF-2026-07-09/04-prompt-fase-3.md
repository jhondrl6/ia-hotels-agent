# FASE-3: Tests + Validaciones

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)

## Contexto previo
FASE-2 completada: `HookPDFGenerator` implementada con extract_data/validate_data/render_html/generate. Comando `hook-pdf` integrado en `main.py`. Imports verificados sin syntax errors.

## Objetivo de esta fase
Crear 8+ tests unitarios que cubran todos los métodos del generator, las 8 validaciones, formato COP, slug generation, glob pattern resolution, y tier detection.

### Tareas
- [ ] 3.1 Crear `tests/commercial_documents/test_hook_pdf_generator.py` con fixtures (archivos .md y .json de prueba en tmp_path)
- [ ] 3.2 Test extract_data: verifica que HookPDFData se llena correctamente desde fixtures
- [ ] 3.3 Test validate_data: verifica las 8 validaciones (placeholders sin llenar, campos obligatorios, formato COP, slug, tier)
- [ ] 3.4 Test render_html: verifica cero `{{...}}` restantes después del render
- [ ] 3.5 Test generate: verifica output .pdf existe y tiene contenido (dry-run no genera archivo)
- [ ] 3.6 Test formato COP: `3741696` → `"3.741.696"`
- [ ] 3.7 Test slug: `"Luxorhotel"` → `"luxorhotel"`, `"Hotel José"` → `"hotel_jose"`
- [ ] 3.8 Test glob pattern: localiza archivos con timestamp variable

### Restricciones
- Usar pytest con tmp_path para fixtures (NO contaminar con archivos del repo)
- Aplicar patrón Test Isolation: si HookPDFGenerator acepta path custom, NO auto-load archivos del repo
- Cada test debe ser independiente (no asumir orden de ejecución)
- Crear fixtures mínimas: un 01_DIAGNOSTICO_*.md, 02_PROPUESTA_*.md, v4_complete_report.json con datos del Luxorhotel (valores de MODULO-HOOK-PDF.md §3.2)
- NO ejecutar v4complete en esta fase (es FASE-4)

### Criterios de completitud
- [ ] `pytest tests/commercial_documents/test_hook_pdf_generator.py -v` pasa con 8+ tests verdes
- [ ] `pytest tests/commercial_documents/ -v` no regresa tests existentes
- [ ] Coverage de los 4 métodos de HookPDFGenerator (extract, validate, render, generate)
- [ ] Coverage de las 8 validaciones
- [ ] Test de formato COP verifica separador `.` y sin decimales
- [ ] Test de slug verifica lowercasing + strip acentos

### Próxima sesión
FASE-4: E2E con output real de Luxorhotel (localizar o re-ejecutar v4complete), generar PDF real, validar 2 páginas, cero placeholders, ≥24pt.

### Prompt para delegate_task

```
Goal: Eres un subagente trabajando en el repositorio iah-cli en /mnt/c/Users/Jhond/Github/iah-cli. Crea 8+ tests unitarios para HookPDFGenerator en tests/commercial_documents/test_hook_pdf_generator.py.

Contexto: FASE-1 y FASE-2 del plan HOOK-PDF-2026-07-09 están completas. La clase HookPDFGenerator está en modules/commercial_documents/hook_pdf_generator.py con métodos: extract_data() -> HookPDFData, validate_data(data) -> list[str], render_html(data) -> str, generate(force=False, dry_run=False) -> Path. El dataclass HookPDFData está en data_structures.py.

La especificación de validaciones está en /.opencode/context/Historico/MODULO-HOOK-PDF.md §3.4 (8 checks). Los valores de prueba del Luxorhotel están en MODULO-HOOK-PDF.md §3.2.

Crea tests para:
1. extract_data con fixtures (crear 01_DIAGNOSTICO_*.md, 02_PROPUESTA_*.md, v4_complete_report.json en tmp_path con datos del Luxorhotel)
2. validate_data: las 8 validaciones
3. render_html: cero {{...}} restantes
4. generate: output .pdf existe, dry-run no genera archivo
5. Formato COP: 3741696 → "3.741.696"
6. Slug: "Luxorhotel" → "luxorhotel", "Hotel José" → "hotel_jose"
7. Glob pattern: localiza archivos con timestamp variable
8. Tier detection: leer financial_evidence_tier del frontmatter

Usa pytest con tmp_path. NO contaminar con archivos del repo. Cada test independiente. Responder en español.
```
