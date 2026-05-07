---
plan_id: PROP-PATCH
name: "PROP-PATCH: Correccion Post-Validacion Termales"
description: "Plan de refactorizacion por fases para corregir 4 gaps criticos y 2 hallazgos nuevos detectados en la validacion post-ejecucion v4complete de Termales Santa Rosa de Cabal (2026-05-06)."
version: 1.0.0
created_at: 2026-05-06
hotel_id: termales
url: http://www.termales.com.co/
source_context: .opencode/context/04_TERMINALES_VALIDATION_20260506.md
workflow: .agents/workflows/phased_project_executor.md v2.10.0
---

# PROP-PATCH: Correccion Post-Validacion Termales

> **Plan de refactorizacion por fases** siguiendo `phased_project_executor.md` v2.10.0.
> **Regla**: 1 fase por sesion. Maximo 60 iteraciones por fase.

---

## Objetivo

Corregir los gaps criticos y hallazgos nuevos detectados en la validacion post-ejecucion de Termales (2026-05-06):

1. **GAP 1 — Divergencia Coherence Score**: YAML header muestra score PRE-assets (0.8067), gate usa POST-assets (0.7844).
2. **GAP 2 — Delivery Readiness 0%**: 6/6 assets ESTIMATED (confianza 0.5) por falta de onboarding.
3. **GAP 3 — 3 Missing Assets**: Servicios prometidos sin asset generado (optimization_guide, whatsapp_button, open_graph).
4. **GAP 4 — Site Verification No Aplicada**: `site_verification_applied: false`.
5. **Hallazgo 5 — price_matches_pain = 0.0**: Precio 32.1x del dolor, principal contribuidor al fallo de coherencia.
6. **Hallazgo 6 — Gate vs Generator Mismatch**: Gate estatico (6 servicios) vs generador dinamico (filtrado por pain_ids).

---

## Arquitectura de Soluciones

| # | Solucion | Decision Arquitectonica | Fase |
|---|----------|------------------------|------|
| SOL-1 | Unificar coherence score | **Opcion A**: Usar post-assets score en YAML header (main.py L2447). Cambio de 1 linea. | PATCH-A |
| SOL-2 | Decision sobre assets faltantes | **Opcion A→C**: Investigar pain_ids; si no se activan, alinear propuesta para no prometerlos. | PATCH-B |
| SOL-3 | Address delivery readiness 0% | **Opcion A**: Mejorar disclaimers explicitos para Tier C en propuesta comercial. | PATCH-B |
| SOL-4 | Corregir price_matches_pain | **Opcion A**: Investigar calculo del dolor financiero para Tier C; ajustar si esta subestimado. | PATCH-A |
| SOL-5 | Alinear gate con generador | **Opcion C**: Documentar mismatch (gate valida contrato estatico; generador produce contenido dinamico). | PATCH-B |

---

## Fases

```
Etapa 2: Implementacion
|
├── FASE-PATCH-A: Fixes de coherencia y precio (SOL-1 + SOL-4)
|   ├── T1: Implementar SOL-1 (main.py L2447)
|   ├── T2: Verificar SOL-1 (no regressions)
|   ├── T3: Investigar SOL-4 (price_matches_pain calculo)
|   └── T4: Implementar fix SOL-4
|
├── FASE-PATCH-B: Alineacion de assets y disclaimers (SOL-2 + SOL-3 + SOL-5)
|   ├── T1: Investigar pain_ids para Termales
|   ├── T2: Alinear propuesta con assets generables (SOL-2)
|   ├── T3: Mejorar disclaimers Tier C (SOL-3)
|   └── T4: Documentar gate vs generator mismatch (SOL-5)
|
├── FASE-PATCH-C: Verificacion E2E con v4complete (Termales)
|   ├── T1: Ejecutar v4complete para Termales
|   ├── T2: Copiar evidencia proactiva
|   ├── T3: Verificar coherence_score unificado
|   └── T4: Verificar missing assets y disclaimers
|
Etapa 3: Cierre
|
└── FASE-PATCH-RELEASE: Documentacion oficial y version bump
    ├── E1-E8: Docs cascade (CHANGELOG, GUIA_TECNICA, REGISTRY, sync)
    └── run_all_validations.py --quick
```

---

## Dependencias

- FASE-PATCH-A no tiene dependencias (puede ejecutarse primero).
- FASE-PATCH-B no tiene dependencias de codigo con PATCH-A (cambia archivos diferentes).
- FASE-PATCH-C depende de PATCH-A y PATCH-B (necesita fixes aplicados para verificar).
- FASE-PATCH-RELEASE depende de PATCH-C.

---

## Conflictos de Archivos

| Archivo | FASE-PATCH-A | FASE-PATCH-B | FASE-PATCH-C | Nota |
|---------|--------------|--------------|--------------|------|
| `main.py` | ✅ Modifica | ❌ No toca | ❌ No toca | Solo L2447 |
| `modules/commercial_documents/coherence_validator.py` | ✅ Modifica | ❌ No toca | ❌ No toca | SOL-4 |
| `modules/asset_generation/proposal_asset_alignment.py` | ❌ No toca | ✅ Modifica | ❌ No toca | SOL-2 |
| `modules/commercial_documents/proposal_generator.py` | ❌ No toca | ✅ Modifica | ❌ No toca | SOL-3 disclaimers |
| `modules/quality_gates/proposal_asset_alignment_gate.py` | ❌ No toca | ✅ Modifica (docs) | ❌ No toca | SOL-5 docstring |

No hay conflictos de escritura concurrente entre PATCH-A y PATCH-B.

---

## Metricas de Exito

- [ ] Coherence score en YAML header = coherence score en gate_report (divergencia = 0)
- [ ] price_matches_pain >= 0.4 (para superar threshold 0.8)
- [ ] Propuesta no promete servicios cuyos assets no se generan
- [ ] Disclaimers Tier C visibles en propuesta
- [ ] v4complete para Termales ejecuta sin errores de gate
- [ ] Documentacion oficial actualizada (CHANGELOG, GUIA_TECNICA, REGISTRY)
- [ ] run_all_validations.py --quick pasa 4/4
