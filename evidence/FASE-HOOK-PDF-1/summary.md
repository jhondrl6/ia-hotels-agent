# Evidence: FASE-HOOK-PDF-1 — Setup + Dataclass + Templates
**Fecha:** 2026-07-09
**Estado:** ✅ COMPLETADA

## Archivos creados
1. `templates/hook_template.md` — HTML template con 34 placeholders (191 líneas)
2. `templates/hook_styles.css` — CSS WeasyPrint, @page A4, hook figure 28pt (338 líneas)

## Archivos modificados
1. `modules/commercial_documents/data_structures.py` — +56 líneas (HookPDFData dataclass, línea 422)
2. `modules/commercial_documents/__init__.py` — +2 líneas (HookPDFData en import + __all__)

## Dependencias instaladas
- `weasyprint==69.0` en venv/Scripts/python.exe (Windows) + .venv-wsl (Linux)
- `pyyaml==6.0.3` en ambos venvs
- libsistema: libpango-1.0-0, libcairo2, libgdk-pixbuf2.0-0, libffi-dev (WSL)

## Verificaciones pasadas
- ✅ `import weasyprint` → 69.0
- ✅ `import yaml` → OK
- ✅ `HookPDFData()` → 34 campos
- ✅ `from modules.commercial_documents import HookPDFData` → OK
- ✅ 34 placeholders únicos en template (≥33 requeridos)
- ✅ `@page` en CSS (líneas 7, 12)
- ✅ REGISTRY.md actualizado vía log_phase_completion.py

## Placeholders en template (34 únicos)
AEO_REGIONAL, AEO_SCORE, BRECHA_1_COP, BRECHA_1_JUSTIFICACION, BRECHA_1_NOMBRE,
BRECHA_2_COP, BRECHA_2_JUSTIFICACION, BRECHA_2_NOMBRE, BRECHA_3_COP,
BRECHA_3_JUSTIFICACION, BRECHA_3_NOMBRE, COMISION_OTA_REAL, EVIDENCE_TIER,
FUGA_6M, FUGA_MAXIMA, FUGA_MENSUAL, FUGA_MINIMA, GBP_RATING, GBP_RESENAS,
GEO_REGIONAL, GEO_SCORE, HOTEL_DIRECCION, HOTEL_NOMBRE, HOTEL_REGION, HOTEL_URL,
IAO_REGIONAL, IAO_SCORE, PRECIO_EXPRESS, PRECIO_MENSUAL, RECUPERACION_6M, ROI,
SEO_REGIONAL, SEO_SCORE, SETUP_FEE

## Nota para FASE-2
- El venv WSL (.venv-wsl) fue creado por el subagente. El venv del proyecto (venv/Scripts/python.exe) es el que usa el CLI.
- weasyprint y pyyaml están en AMBOS venvs.
- HookPDFData tiene 34 campos (33 planificados + evidence_tier).
