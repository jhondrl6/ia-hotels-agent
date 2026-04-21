# Checklist de Implementación — Amaziliahotel Refactor v2
**Rediagnóstico post-RELEASE rechazado 2026-04-20**

## Resumen

| Fase | Descripción | Estado | Archivo Real |
|------|-------------|--------|--------------|
| FASE-1 | Fix Google Maps query en v4_comprehensive | ✅ Completada | `modules/auditors/v4_comprehensive.py` |
| FASE-2 | Fix hotel_schema con datos reales | ✅ Completada | `conditional_generator.py` + `v4_asset_orchestrator.py` |
| FASE-3 | Activar Content Scrubber | ✅ Completada | `content_scrubber.py` + `main.py` |
| FASE-4 | Fix ROI — eliminar 24X hardcodeado | ✅ Completada | `propuesta_v6_template.md` + `v4_proposal_generator.py` |
| FASE-5 | Fix faq_page JSON-LD + monthly_report blanks | ✅ Completada | `conditional_generator.py`, `monthly_report_generator.py` |
| FASE-6 | Fix Voice/AEO deprecated en propuesta | ✅ Completada | `propuesta_v6_template.md`, `proposal_asset_alignment.py` |
| FASE-7 | Fix capitalización region → .title() | ✅ Completada | `v4_proposal_generator.py` |
| FASE-8 | Validación E2E + Documentación | ✅ Completada (sin E2E real) | Varios |
| FASE-RELEASE | Validación E2E REAL | ❌ RECHAZADO | `v4complete` |
| FASE-PATCH-1 | Fix Places API FieldMask + lat/lng extraction | ⏳ Pendiente | `v4_comprehensive.py` + `conditional_generator.py` |
| FASE-PATCH-2 | Fix Scrubber timing — re-scrub post-gen | ✅ Completada (2026-04-20) | `main.py` L2478-2493 |
| FASE-PATCH-3 | Fix Region lowercase en serialization | ⏳ Pendiente | `main.py` |
| FASE-RELEASE-2 | Validación E2E FINAL post-patches + release | ⏳ Pendiente | `v4complete` + docs |

## Estados

- ⏳ Pendiente: No iniciada
- 🔄 En progreso: Siendo ejecutada
- ✅ Completada: Verificada y registrada
- ❌ Bloqueada/Falló: No cumple criterios

## Por qué PATCH-1/2/3 (no re-escribir FASE-1 a FASE-7)

Los fixes originales de FASE-1 a FASE-7 SÍ están en el código (verificados en pre-flight). El problema NO es que no se escribieron, sino que:

1. **FASE-1/2 escribieron en el módulo equivocado**: _build_search_queries funciona pero el FieldMask no pide `places.location`, así que el API nunca devuelve coords
2. **FASE-3 importó el scrubber pero el timing es incorrecto**: el scrubber corre antes de que la propuesta exista
3. **FASE-7 aplicó .title() solo en proposal_generator**: pero el audit_report se genera antes y en otro punto

Los PATCH corrigen la EJECUCIÓN de los fixes, no re-escriben los fixes.

## Criterios de Avance por PATCH

| Fase | Criterio de éxito |
|------|-------------------|
| FASE-PATCH-1 | `grep 'places.location' v4_comprehensive.py` = 1 match; `grep 'lat=0.0' v4_comprehensive.py` = 0 matches; `_is_valid` rechaza (0,0) |
| FASE-PATCH-2 | `grep 'Re-scrub proposal' main.py` = 1 match; `scrubber` en scope |
| FASE-PATCH-3 | 3 puntos de serialización con `.title()`; `feature_flags.py` NO modificado |
| FASE-RELEASE-2 | COP COP=0, coords!=0.0, region=Title Case, publication_ready=true |

## Secuencia de Ejecución

```
PATCH-1 (v4_comprehensive.py + conditional_generator.py)
    └─→ PATCH-2 (main.py ~L2476)
            └─→ PATCH-3 (main.py ~L2289/2538/2738)
                    └─→ FASE-RELEASE-2 (v4complete + docs)
```
