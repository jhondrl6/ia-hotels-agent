# Dependencias entre Fases - Fix AEO Score

## Proyecto: Fix _calculate_aeo_score() "Pendiente de datos"

**Objetivo**: Implementar scoring completo AEO (Schema 25pts + FAQ 25pts + OG 25pts + Citabilidad 25pts), completitud de datos y tests.

---

## Diagrama de Dependencias

```
FASE-A (Data Foundation)
  │
  │  Implementa detección real de OG en seo_elements_detector.py
  │  Output: SEOElementsResult.open_graph funciona con datos reales
  │
  ├──→ FASE-B (AEO Scoring Rewrite) ✅ COMPLETADA
  │      │
  │      │  Reescribe _calculate_aeo_score() con 4 componentes × 25pts
  │      │  Output: AEO score calcula 0-100 en vez de "Pendiente de datos"
  │      │  Tests: 15/15 pasan. 0 regresiones.
  │      │
  │      ├──→ FASE-C (Integration & Validation)
  │             │
  │             │  Verifica templates, regresión, e2e
  │             │  Output: Fix completo, testeado, documentado
  │             │
  │             └──→ log_phase_completion.py + docs
```

---

## Tabla de Conflictos de Archivos

| Fase | Archivos Modificados | Conflicto Potencial |
|------|---------------------|-------------------|
| FASE-A | `modules/auditors/seo_elements_detector.py` | Ninguno (archivo aislado) |
| FASE-A | `tests/auditors/test_seo_elements_detector.py` (nuevo) | Ninguno |
| FASE-B | `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1324-1346) | Ninguno (método único) |
| FASE-B | `tests/commercial_documents/test_aeo_score.py` (nuevo) | Ninguno |
| FASE-C | Ninguno (solo validación) | Ninguno |

**Conclusión**: Sin conflictos entre fases. Cada fase modifica archivos distintos.

---

## Mapeo de Datos AEO

| Componente | Fuente de Datos | Estado Actual | Fase que lo Resuelve |
|---|---|---|---|
| Schema Hotel válido | `audit_result.schema.hotel_schema_valid` | ✅ Disponible | FASE-B (uso) |
| FAQ Schema válido | `audit_result.schema.faq_schema_valid` | ✅ Disponible | FASE-B (uso) |
|| Open Graph detectado | `audit_result.seo_elements.open_graph` | ✅ Implementado (BS4) | FASE-A (completado 2026-04-08) |
| Citabilidad | `audit_result.citability.overall_score` | ⚠️ Optional/ADVISORY | FASE-B (fallback graceful) |
