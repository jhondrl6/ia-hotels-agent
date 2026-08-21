# Resumen de Ejecución — FASE-P1-D (Verdad del sitio vivo)

> Fecha: 2026-08-21 | Modo: DIRECTO | Iteraciones: ~35/60 | Estado: ✅ COMPLETADA

## Objetivo

Restaurar el estado de verdad del sitio vivo como fuente única:
- **F12**: el cross-validator distingue sedes en negocios multi-ubicación (caso Zione: falso
  conflicto BRECHA 1 que inflaba la fuga $1.198.906/mes).
- **F13**: propagación de `site_verification_applied` al pain_ledger y al diagnóstico
  (decisión D8: `VERIFIED_IN_SITE` como estado de primera clase — consumido por FASE-P2-A/F14).

## Resultados de tests

- +21 tests nuevos: 11 F12 (`tests/data_validation/test_whatsapp_multisede.py`) +
  10 F13 (`tests/asset_generation/test_site_verification_propagation.py`) — 21/21 PASAN
- Suites data_validation + asset_generation: **603 passed, 0 failed**
- Suites ampliadas (quality_gates, commercial_documents, orchestration_v4, auditors,
  reconciler, cross_validator): 843 passed con exactamente los 12 fallos preexistentes
  de la línea base (commercial_documents) — **0 regresiones**

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `modules/data_validation/cross_validator.py` | Firma backwards-compatible + `_reconcile_whatsapp_multisede` (matching por tokens ≥4 chars; dedup que fusiona labels) |
| `modules/auditors/v4_comprehensive.py` | `_extract_all_whatsapp_candidates` + `_extract_sede_label`; CrossValidationResult +2 campos |
| `main.py` | Caller `validate_whatsapp` (L1735) enriquecido |
| `modules/asset_generation/pain_ledger.py` | `STATUS_VERIFIED_IN_SITE` + `apply_site_verification` + `PAIN_TO_PRESENCE_ASSET` |
| `modules/asset_generation/v4_asset_orchestrator.py` | Cableado `apply_site_verification` antes de save |
| `modules/orchestration/post_orchestrator_reconciler.py` | `_resolve_status` preserva VERIFIED_IN_SITE |
| `modules/quality_gates/publication_gates.py` | VERIFIED_IN_SITE en `_JUSTIFIED_STATUSES` |
| `modules/commercial_documents/v4_diagnostic_generator.py` | `_load_verified_in_site_pain_ids` + filtrado de brechas |

## Decisión D8 (documentada en 10-analisis)

`VERIFIED_IN_SITE` como estado de primera clase en pain_ledger: cierra F13 sin alterar la
fórmula del coverage gate (cubiertas + justificadas == detectadas) y deja LISTO el estado
para F14 (FASE-P2-A consumirá este mismo estado en coherence_validator).

## Restricciones respetadas

- NO se resolvió F14 (es FASE-P2-A); solo se dejó LISTO el estado "verificado en producción"
- NO se tocaron benchmarks/pricing/rango del hook
- NO se ejecutó v4complete

## Errores encontrados y fixes durante la ejecución

1. Test C3 falló (ESTIMATED en vez de CONFLICT): la deduplicación descartaba el alterno
   completo perdiendo su label de sede → fix: adoptar el label del duplicado cuando el
   candidato existente no tiene label (lección L19).
2. Preventivo: matching de sede cambiado de substring completo a tokens (palabras ≥4 chars)
   antes del primer run (lección L20).

## Documentación actualizada

- `dependencias-fases.md`, `06-checklist-implementacion.md`, `README.md` del plan: FASE-P1-D ✅
- `09-documentacion-post-proyecto.md`: secciones B/D/E (tests acumulados 95 → 116)
- `10-analisis-post-implementacion.md`: fila de ejecución + lecciones L19-L22 + D8
- `docs/contributing/REGISTRY.md` vía `scripts/log_phase_completion.py`
- `CHANGELOG.md` + `docs/GUIA_TECNICA.md`: entradas FASE-P1-D
