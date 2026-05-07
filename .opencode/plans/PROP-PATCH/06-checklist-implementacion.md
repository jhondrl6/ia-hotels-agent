---
plan: PROP-PATCH
version: 1.0.0
updated_at: 2026-05-06
---

# Checklist de Implementacion — PROP-PATCH

## Progreso General

| Fase | Estado | Iteraciones | Fecha Inicio | Fecha Fin | Tests Nuevos | Regresiones |
|------|--------|-------------|--------------|-----------|--------------|-------------|
| **PATCH-A** | ✅ Completada | - | 2026-05-06 | 2026-05-06 | 0 | 0 |
| **PATCH-B** | ✅ Completada | 55 | 2026-05-06 | 2026-05-07 | 0 | 0 |
| **PATCH-C** | ✅ Completada | 47 | 2026-05-07 | 2026-05-07 | 0 | 0 |
|| **PATCH-RELEASE** | ✅ Completada | 45 | 2026-05-07 | 2026-05-07 | - | - |

---

## FASE-PATCH-A: Fixes de Coherencia y Precio

### Tareas

- [x] **T1 — SOL-1**: Modificar `main.py` L2447 para usar post-assets coherence score
  - [x] Localizar linea exacta donde se pasa `coherence_score` a `diagnostic_gen.generate()`
  - [x] Cambiar `pre_coherence_score` por `asset_result.coherence_report.overall_score if asset_result else pre_coherence_score`
  - [x] Verificar que `asset_result` y `coherence_report` estan disponibles en ese scope
- [x] **T2 — Verificacion SOL-1**: Asegurar que el cambio no rompe flujo cuando `asset_result` es None
  - [x] Revisar usos de `pre_coherence_score` posteriores a L2447
  - [x] Confirmar que `gate_status` tambien usa post-assets score si aplica
- [x] **T3 — SOL-4**: Investigar calculo de `price_matches_pain` en `coherence_validator.py`
  - [x] Revisar formula del ratio (precio / dolor)
  - [x] Verificar si `financial_value_central` para Tier C es mensual o anual
  - [x] Identificar si el threshold de 6.0x es apropiado para Tier C
- [x] **T4 — Fix SOL-4**: Implementar ajuste (formula, threshold dinamico, o ambos)
  - [x] Aplicar cambio minimo que eleve score >= 0.4
  - [x] Documentar razon del ajuste en comentario

### Criterios de Completitud

- [x] Tests existentes pasan (0 regresiones)
- [x] `run_all_validations.py --quick` pasa 4/4
- [x] `dependencias-fases.md` actualizado: PATCH-A = ✅ Completada

---

## FASE-PATCH-B: Alineacion de Assets y Disclaimers

### Tareas

- [x] **T1 — SOL-2**: Investigar pain_ids para Termales
  - [x] Revisar diagnostico YAML de Termales: que pain_ids se detectaron
  - [x] Verificar si `no_whatsapp_visible`, `no_og_tags`, y pain_ids de `optimization_guide` estan presentes
  - [x] Confirmar si `asset_catalog.py` entries tienen los `promised_by` correctos
- [x] **T2 — SOL-2**: Alinear propuesta con realidad
  - [x] Modificar generador de propuesta para filtrar servicios segun assets generados (no pain_ids)
  - [x] Poblar `pain_ids` en `DiagnosticSummary` desde `main.py`
  - [x] Verificar que propuesta no liste servicios sin asset generable
- [x] **T3 — SOL-3**: Mejorar disclaimers Tier C
  - [x] Agregar nota explicita en propuesta: "Assets son estimaciones basadas en benchmarks regionales"
  - [x] Reforzar banner Tier C existente con parrafo adicional sobre entregables
  - [x] Disclaimer dentro del bloque condicional `{{if financial_evidence_tier == "C"}}`
- [x] **T4 — SOL-5**: Documentar gate vs generator mismatch
  - [x] Agregar docstring en `publication_gates.py._proposal_asset_alignment_gate` explicando contrato estatico
  - [x] Agregar comentario en generador de propuesta explicando filtrado dinamico
  - [x] Ambos referencian FASE-PATCH-B para contexto cruzado

### Criterios de Completitud

- [x] Propuesta para Termales no promete servicios sin assets (filtro por assets_generated)
- [x] Disclaimer Tier C visible en propuesta generada (template actualizado)
- [x] Tests existentes pasan (0 regresiones — 27/27 proposal tests)
- [x] `dependencias-fases.md` actualizado: PATCH-B = ✅ Completada

---

## FASE-PATCH-C: Verificacion E2E (v4complete Termales)

### Tareas

- [x] **T1 — Ejecutar v4complete**: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
  - [x] Usar subagente (delegate_task) con notify_on_complete=True
  - [x] Completado: diagnostico + propuesta + 6 assets + coherence 0.891
- [x] **T2 — Evidencia proactiva**: Copiar archivos criticos inmediatamente despues de generacion
  - [x] `mkdir -p evidence/FASE-PATCH-C/`
  - [x] Copiados: 01_DIAGNOSTICO, 02_PROPUESTA, 11 JSONs (gate_report, coherence_validation, etc.)
- [x] **T3 — Verificar SOL-1**: Coherence score unificado
  - [x] YAML: 0.8911111111111112 == gate_report: 0.8911111111111112
  - [x] Divergencia: 0.0 (vs 2.67 pre-fix) — PASA
- [x] **T4 — Verificar SOL-2/3/4**: Missing assets, disclaimers, price_matches_pain
  - [x] SOL-3: Tier C disclaimer presente en lineas 94-96 ✅
  - [x] SOL-4: price_matches_pain.score = 0.8 >= 0.4 ✅
  - [x] SOL-2: **DISCREPANCIA CONOCIDA** — gate proposal_asset_alignment missing_count=3 (SEO Local, WhatsApp button, Open Graph). coherence_validator dice "todos implementados" (verifica assets generados vs ASSET_CATALOG). El gate valida el contrato estatico de 6 servicios; la propuesta solo promete 4. Divergencia documentada como esperada por PATCH-B docstring.

### Criterios de Completitud

- [x] v4complete termina sin errores criticos (exit_code 0)
- [x] Coherence YAML == Coherence gate (divergencia 0)
- [x] Evidencia copiada en `evidence/FASE-PATCH-C/`
- [x] `dependencias-fases.md` actualizado: PATCH-C = ✅ Completada

---

## FASE-PATCH-RELEASE: Documentacion Oficial

### Tareas

- [x] **E1**: Ejecutar `log_phase_completion.py` para cada fase (PATCH-A, PATCH-B, PATCH-C)
- [x] **E2**: Ejecutar `sync_versions.py`
- [x] **E3**: Actualizar `CHANGELOG.md` con entrada PATCH
- [x] **E4**: Actualizar `GUIA_TECNICA.md` con notas tecnicas por fase
- [x] **E5**: Regenerar `SYSTEM_STATUS.md` via `doctor.py --status`
- [x] **E6**: Validar `DOMAIN_PRIMER.md` via `doctor.py --context`
- [x] **E7**: Ejecutar `run_all_validations.py --quick` (debe pasar 4/4)
- [x] **E8**: Commit final

### Criterios de Completitud

- [x] REGISTRY.md actualizado con 3 entradas de fase
- [x] VERSION.yaml sincronizado (sin discrepancias)
- [x] CHANGELOG.md formato correcto (Objetivo/Cambios/Archivos/Tests)
- [x] GUIA_TECNICA.md tiene nota tecnica por fase
- [x] `run_all_validations.py --quick` pasa
- [x] `git diff --stat` muestra cambios esperados
