# Documentación Post-Proyecto — REFACTOR-COHERENCIA-CASTILLAREAL

> **Propósito**: Backup acumulativo de datos para FASE-RELEASE. Cada fase completa su columna "Fase".
> **NO editar manualmente** — este archivo se alimenta de los outputs de `log_phase_completion.py` por fase.

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| — | — | — | — |

---

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| — | — | — | — |

---

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos | 7 (test_coherence_gate.py) | FASE-1-COH |
| Tests nuevos | — | FASE-2-DEFAULT |
| Tests nuevos | 8 tests (FASE-3-CONTENT) | FASE-3-CONTENT |
| Tests nuevos | 3 tests (FASE-4-GATE) | FASE-4-GATE |
|| Coherence score pre-fix | 0.81 / 0.83 / 0.85 / 0.81 (5 fuentes) | Baseline |
|| Coherence score post-fix FASE-1..4 | 0.81 (pre-gen) / 0.826 (gate) | FASE-5-VERIFY |
|| Coherence score post-hotfix | 0.8262 (gate_report post-geo) | FASE-6-HOTFIX |
|| Assets con confidence < 0.7 pre-fix | 7/7 (100%) | Baseline |
|| Assets con confidence < 0.7 post-fix FASE-1..4 | 12/12 (100% ESTIMATED) | FASE-5-VERIFY |
|| Assets con confidence < 0.7 post-hotfix | 0/12 (0% — 12 assets con confidence >= 0.7) | FASE-6-HOTFIX |
|| Defaults cross-hotel pre-fix | 3 ('Amazilia Hotel Campestre') | Baseline |
|| Defaults cross-hotel post-fix | 0 | FASE-2-DEFAULT |

---

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/quality_gates/coherence_gate.py` | Refactor: execute() integra _validator.validate() via execute_from_validator(); CoherenceGateResult gana checks/validator_errors/validator_warnings; nuevo método _validator_errors_to_gaps() | FASE-1-COH |
| `main.py` | Unificar fuente coherence_score: assessment dict incluye coherence_checks/errors/warnings; v4_complete_report usa single coherence_score | FASE-1-COH |
| `tests/quality_gates/test_coherence_gate.py` | 7 tests de integración gate↔validator (TestCoherenceGateValidatorIntegration) | FASE-1-COH |
|| `modules/quality_gates/publication_gates.py` | Hardening gate asset_confidence: BLOCKED cuando 100% assets ESTIMATED (confidence < 0.7), WARNING para mix, PASSED para todos >= 0.7 | FASE-4-GATE |
|| `tests/quality_gates/test_publication_gates.py` | 3 tests nuevos: all_estimated_blocked, mixed_estimated_warning, all_verified_passed; tests existentes actualizados | FASE-4-GATE |
| `main.py` | FASE-6-HOTFIX G1: Post-T4FIX, sobrescribir coherence_validation.json con score final post-geo | FASE-6-HOTFIX |
| `modules/asset_generation/conditional_generator.py` | FASE-6-HOTFIX G7: `_calculate_confidence_score` contexto por asset_type (whatsapp_conflict_guide con conflicto detectado -> 0.8); `_apply_naming_strategy` con effective_status para whatsapp_conflict_guide con WARNING -> sin prefijo ESTIMATED_ | FASE-6-HOTFIX |
| `modules/asset_generation/asset_catalog.py` | FASE-6-HOTFIX G7: `required_confidence` de 0.5 a 0.7 para whatsapp_conflict_guide | FASE-6-HOTFIX |
| `modules/asset_generation/v4_asset_orchestrator.py` | FASE-6-HOTFIX G1: L447 `post_coherence_report.save()` recibe path completo; docstring G6 documenta requerimiento onboarding | FASE-6-HOTFIX |
| `modules/commercial_documents/coherence_validator.py` | FASE-6-HOTFIX G1: `save()` acepta full file paths (detecta si path termina en .json) | FASE-6-HOTFIX |
| `evidence/FASE-6-HOTFIX/G6_WONT_FIX.md` | FASE-6-HOTFIX: Análisis causa raíz G6 (hotel_schema) — no es bug, requiere onboarding real | FASE-6-HOTFIX |
