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
| **PATCH-B** | ⏳ Pendiente | - | - | - | - | - |
| **PATCH-C** | ⏳ Pendiente | - | - | - | - | - |
| **PATCH-RELEASE** | ⏳ Pendiente | - | - | - | - | - |

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

- [ ] **T1 — SOL-2**: Investigar pain_ids para Termales
  - [ ] Revisar diagnostico YAML de Termales: que pain_ids se detectaron
  - [ ] Verificar si `no_whatsapp_visible`, `no_og_tags`, y pain_ids de `optimization_guide` estan presentes
  - [ ] Confirmar si `asset_catalog.py` entries tienen los `promised_by` correctos
- [ ] **T2 — SOL-2**: Alinear propuesta con realidad
  - [ ] Modificar generador de propuesta para filtrar servicios segun pain_ids detectados
  - [ ] O modificar `PROPOSAL_SERVICE_TO_ASSET` para reflejar solo servicios activables
  - [ ] Verificar que propuesta no liste servicios sin asset generable
- [ ] **T3 — SOL-3**: Mejorar disclaimers Tier C
  - [ ] Agregar nota explicita en propuesta: "Assets son estimaciones basadas en benchmarks regionales"
  - [ ] Reforzar banner Tier C existente (lineas 100-103)
  - [ ] Verificar que disclaimer aparece en output de propuesta
- [ ] **T4 — SOL-5**: Documentar gate vs generator mismatch
  - [ ] Agregar docstring en `proposal_asset_alignment_gate.py` explicando que valida contrato estatico
  - [ ] Agregar comentario en generador de propuesta explicando filtrado dinamico
  - [ ] Actualizar `docs/GUIA_TECNICA.md` con nota sobre este comportamiento

### Criterios de Completitud

- [ ] Propuesta para Termales no promete servicios sin assets
- [ ] Disclaimer Tier C visible en propuesta generada
- [ ] Tests existentes pasan (0 regresiones)
- [ ] `dependencias-fases.md` actualizado: PATCH-B = ✅ Completada

---

## FASE-PATCH-C: Verificacion E2E (v4complete Termales)

### Tareas

- [ ] **T1 — Ejecutar v4complete**: `./venv/Scripts/python.exe main.py v4complete --url http://www.termales.com.co/`
  - [ ] Usar `terminal(timeout=600, notify_on_complete=True)` o subagente
  - [ ] Monitorear logs por errores
- [ ] **T2 — Evidencia proactiva**: Copiar archivos criticos inmediatamente despues de generacion
  - [ ] `mkdir -p evidence/FASE-PATCH-C/`
  - [ ] Copiar `01_DIAGNOSTICO_*.md`, `02_PROPUESTA_*.md`, `v4_audit/*.json`
- [ ] **T3 — Verificar SOL-1**: Coherence score unificado
  - [ ] Comparar `coherence_score` en YAML header vs `gate_report.coherence.value`
  - [ ] Deben coincidir (tolerancia < 0.01)
- [ ] **T4 — Verificar SOL-2/3**: Missing assets y disclaimers
  - [ ] `proposal_asset_alignment` gate: missing_count debe ser 0
  - [ ] Propuesta debe mostrar disclaimer Tier C
  - [ ] `delivery_ready_percentage` puede seguir bajo (estructural), pero propuesta no debe prometer lo inalcanzable

### Criterios de Completitud

- [ ] v4complete termina sin errores criticos
- [ ] Coherence YAML == Coherence gate (divergencia 0)
- [ ] Evidencia copiada en `evidence/FASE-PATCH-C/`
- [ ] `dependencias-fases.md` actualizado: PATCH-C = ✅ Completada

---

## FASE-PATCH-RELEASE: Documentacion Oficial

### Tareas

- [ ] **E1**: Ejecutar `log_phase_completion.py` para cada fase (PATCH-A, PATCH-B, PATCH-C)
- [ ] **E2**: Ejecutar `sync_versions.py`
- [ ] **E3**: Actualizar `CHANGELOG.md` con entrada PATCH
- [ ] **E4**: Actualizar `GUIA_TECNICA.md` con notas tecnicas por fase
- [ ] **E5**: Regenerar `SYSTEM_STATUS.md` via `doctor.py --status`
- [ ] **E6**: Validar `DOMAIN_PRIMER.md` via `doctor.py --context`
- [ ] **E7**: Ejecutar `run_all_validations.py --quick` (debe pasar 4/4)
- [ ] **E8**: Commit final

### Criterios de Completitud

- [ ] REGISTRY.md actualizado con 3 entradas de fase
- [ ] VERSION.yaml sincronizado (sin discrepancias)
- [ ] CHANGELOG.md formato correcto (Objetivo/Cambios/Archivos/Tests)
- [ ] GUIA_TECNICA.md tiene nota tecnica por fase
- [ ] `run_all_validations.py --quick` pasa
- [ ] `git diff --stat` muestra cambios esperados
