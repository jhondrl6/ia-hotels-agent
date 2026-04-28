# FASE-1-AMAZILIA-CORRECCION — Plan Padre (Division R3)

**ID**: FASE-1-AMAZILIA-CORRECCION
**Objetivo**: Corregir los 5 hallazgos verificados del contexto post-VALIDATE-v2 y ejecutar v4complete para https://amaziliahotel.com/ validando que los errores no persisten.
**Dependencias**: FASE-PREP (plan maestro generado)
**Duracion estimada**: 3 sesiones (FASE-1-A completada, FASE-1-B y FASE-1-C pendientes)
**Skill**: `phased_project_executor.md` v2.9.0

---

## Division en Sub-Fases (R3 Scope)

| Sub-fase | Sesion | Objetivo | Estado |
|----------|--------|----------|--------|
| FASE-1-A | Sesion 1 | Investigar + Fixes (M3, H1, N1, M4, slug bug) | ✅ Completada |
| FASE-1-B | Sesion 2 | T4 fix arquitectural + v4complete + verificacion | ✅ Completada (2026-04-28) |
| FASE-1-C | Sesion 3 | Docs cascade (log + sync + 06/09 + validaciones) | ✅ Completada (2026-04-28) |"

**FASE-RELEASE solo se ejecuta cuando FASE-1-A, FASE-1-B y FASE-1-C esten ✅.**

---

## Contexto Global

Este proyecto corrige hallazgos verificados contra codigo real y outputs JSON del diagnostico v4complete para Amazilia Hotel.

**Contexto fuente**: `.opencode/context/post-validate-v2-hallazgos-pendientes-CORREGIDO.md` (v4.36.0)

## Estado de Fases Anteriores

| Fase | Estado | Fecha |
|------|--------|-------|
| FASE-PREP (plan maestro) | ✅ Completada | 2026-04-27 |
| FASE-1-A (fixes) | ✅ Completada | 2026-04-28 |
| FASE-1-B (T4 + v4complete) | ✅ Completada | 2026-04-28 |
| FASE-1-C (docs cascade) | ✅ Completada | 2026-04-28 |"

### Base Tecnica Disponible

- Archivos: `v4_diagnostic_generator.py`, `v4_asset_orchestrator.py`, `asset_metadata.py`, `conditional_generator.py`
- Tests base: 2224 funciones, 140 archivos, 0 regresion
- Output v4complete existente: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260428_092202.md`
- Evidence: `evidence/fase-1-amazilia-correccion/`

---

## Resumen — Hallazgos y su Estado Global

| Finding | Sub-fase | Estado | Evidencia |
|---------|----------|--------|-----------|
| M3 (can_use unificado) | FASE-1-A | ✅ Corregido | `asset_metadata.py` L151-173 usa `preflight_status != "BLOCKED"` |
| H1 (local_content_page) | FASE-1-A | ✅ Corregido + verificado | 13/13 assets; `conditional_generator.py` L621 fix slug |
| N1 (header dual) | FASE-1-A | ✅ Corregido en codigo | `v4_diagnostic_generator.py` L1307 comentario "N1 FIX" |
| M4 (forward slashes) | FASE-1-A | ✅ Corregido | path normalization verificado |
| T4 (GEO timing) | FASE-1-B | ✅ Corregido + verificado | "Salud Técnica GEO" 23/100 en diagnostico final |
| Verificacion N1 (visual) | FASE-1-B | ✅ Confirmado | Solo 1 header "Métricas de Acceso para IA" |
| Verificacion M4 (JSON paths) | FASE-1-B | ✅ Confirmado | 0 backslash paths, forward slashes |
| Verificacion M3 (can_use) | FASE-1-B | ✅ Confirmado | 13/13 can_use=True, summary.can_use=13 |
| Docs cascade | FASE-1-C | ⏳ Pendiente | log_phase + sync + 06/09 + validaciones |

---

## Evidencia Acumulada (evidence/fase-1-amazilia-correccion/)

```
evidence/fase-1-amazilia-correccion/
  01_DIAGNOSTICO_Y_OPORTUNIDAD_20260428_092202.md  (sesion 1)
  02_PROPUESTA_COMERCIAL_20260428_092204.md         (sesion 1)
  asset_generation_report.json                       (sesion 1)
  coherence_validation.json                          (sesion 1)
  geo_flow_result.json                               (sesion 1)
```

---

## Archivos Modificados (累积 — todas las sub-fases)

```
modules/asset_generation/conditional_generator.py  (FASE-1-A: slug fix)
modules/asset_generation/asset_metadata.py          (FASE-1-A: can_use unificado)
modules/orchestration/v4_diagnostic_generator.py   (FASE-1-A: N1 fix)
modules/orchestration/v4_asset_orchestrator.py     (FASE-1-A: H1 handler)
```

---

## Criterios para FASE-RELEASE

Cuando FASE-1-A, FASE-1-B y FASE-1-C esten ✅:

- "Salud Tecnica GEO" aparece en ia_metrics_table del diagnostico final
- 4/4 validaciones pasan (`run_all_validations.py --quick`)
- REGISTRY.md, CHANGELOG.md, GUIA_TECNICA.md actualizados
- Todos los hallazgos de VALIDATE-v2 verificados como corregidos

---

## Planes Hijos

| Plan | Ruta |
|------|------|
| FASE-1-B | `.opencode/plans/05-prompt-inicio-sesion-fase-1-B-amazilia-correccion.md` |
| FASE-1-C | `.opencode/plans/05-prompt-inicio-sesion-fase-1-C-amazilia-correccion.md` |

**Importante**: Ejecutar FASE-1-B primero. FASE-1-C solo se ejecuta cuando FASE-1-B muestre ✅ en todos sus criterios de aceptacion.
