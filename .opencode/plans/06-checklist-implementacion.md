# Checklist Maestro — REFACTOR-COHERENCIA-CASTILLAREAL

> **Regla**: Cada fase se ejecuta en UNA sesión nueva de agente. No múltiples fases por sesión.
> **Regla**: FASE-RELEASE solo cuando todas las anteriores están ✅.

---

## FASE-1-COH: Unificar CoherenceValidator ↔ CoherenceGate

- [x] T1: Leer `coherence_gate.py` L158-203 y confirmar `_validator` nunca se llama en `execute()`
- [x] T2: Implementar integración real: modificar `execute()` para consumir `_validator.validate()` o crear `execute_from_validator()`
- [x] T3: Modificar `main.py` L2225-2250, L2653, L2955-2960 para pasar datos completos al gate y unificar fuente de coherence_score
- [x] T4: Tests de integración: verificar que gate.consume_validator() produce mismo score que validator directo
- [x] T5: `log_phase_completion.py --fase FASE-1-COH`
- [x] Criterio: G1 (coherence_validation.score == gate.coherence.value) ✅
- [x] Criterio: G9 (CoherenceGate.execute() llama _validator.validate()) ✅
- [x] Criterio: Tests nuevos pasan, 0 regresiones
- [x] Criterio: `run_all_validations.py --quick` 4/4

---

## FASE-2-DEFAULT: Eliminar hardcoded defaults cross-hotel ✅ COMPLETADA

- [x] ~~T1: Modificar `open_graph_generator.py` L87: eliminar default 'Amazilia Hotel Campestre', validar explícitamente~~
- [x] ~~T2: Modificar `open_graph_generator.py` L94, L107: eliminar defaults de rating/reviews y URL de otro hotel~~
- [x] ~~T3: Modificar `conditional_generator.py` L523: usar `generator.generate()` en vez de métodos privados~~
- [x] ~~T4: Auditoría grep + tests: `grep -c "Amazilia" output/*/open_graph/*.html` → 0; tests de validación de inputs~~
- [x] ~~T5: `log_phase_completion.py --fase FASE-2-DEFAULT`~~ ✅ 2026-05-11
- [x] Criterio: G4 (open_graph sin "Amazilia") ✅ — grep 0/0
- [x] Criterio: G10 (0 defaults cross-hotel en generators) ✅ — 0 ocurrencias
- [x] Criterio: Tests nuevos pasan, 0 regresiones ✅ — 11/11 passed, 7 pre-existentes OK
- [x] Criterio: `run_all_validations.py --quick` 5/5 ✅

---

## FASE-3-CONTENT: Fix local_content + evidence_tier + all_aligned

- [ ] T1: Modificar `local_content_generator.py`: validar `hotel_data.get("city")` pre-LLM, fallback a "Colombia"
- [ ] T2: Unificar `evidence_tier`: computar UNA vez basado en `financial_sources`, propagar a JSON y YAML
- [ ] T3: Renombrar `all_aligned` → `all_covered` en `proposal_asset_alignment.py` con alias deprecado
- [ ] T4: Tests para los 3 cambios (local_content location, evidence_tier consistency, all_covered property)
- [ ] T5: `log_phase_completion.py --fase FASE-3-CONTENT`
- [ ] Criterio: G5 (local_content sin "Hotel en  -") ✅
- [ ] Criterio: G8 (financial_scenarios.evidence_tier == diagnostic.financial_evidence_tier) ✅
- [ ] Criterio: Tests nuevos pasan, 0 regresiones
- [ ] Criterio: `run_all_validations.py --quick` 4/4

---

## FASE-4-GATE: Gate asset_confidence hardening

- [ ] T1: Modificar gate `asset_confidence`: emitir BLOCKED (no WARNING) cuando 100% assets son ESTIMATED (confidence < 0.7)
- [ ] T2: Tests para nuevo comportamiento: 100% ESTIMATED → BLOCKED; mix ESTIMATED/VERIFIED → WARNING o PASSED según corresponda
- [ ] T3: Verificar backwards compatibility: deliveries existentes con confianza mixta no se rompen
- [ ] T4: `log_phase_completion.py --fase FASE-4-GATE`
- [ ] Criterio: asset_confidence BLOCKED cuando all(assets.confidence < 0.7) ✅
- [ ] Criterio: Tests nuevos pasan, 0 regresiones
- [ ] Criterio: `run_all_validations.py --quick` 4/4

---

## FASE-5-VERIFY: v4complete Hotel Castilla Real + análisis

- [ ] T1: Ejecutar `./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/`
- [ ] T2: Protocolo de Evidencia Proactiva: copiar diagnóstico, propuesta, audit JSONs a `evidence/FASE-5-VERIFY/`
- [ ] T3: Verificar G1-G10 contra el nuevo output (usar jq/grep/Python según corresponda)
- [ ] T4: Generar `evidence/FASE-5-VERIFY/analisis_ejecucion.md` con veredicto EFECTIVA/PARCIAL/NO EFECTIVA
- [ ] T5: `log_phase_completion.py --fase FASE-5-VERIFY`
- [ ] Criterio: v4complete termina sin errores críticos
- [ ] Criterio: G1-G10 verificados y documentados
- [ ] Criterio: Análisis de ejecución generado con conclusiones primero, evidencia después

---

## FASE-RELEASE-4.45.0: Documentación oficial y cierre

- [ ] E1: `version_consistency_checker.py` pasa sin discrepancias
- [ ] E2: `sync_versions.py` ejecutado (VERSION.yaml → 6 archivos)
- [ ] E3: CHANGELOG.md con entrada [4.45.0] formato correcto (Objetivo, Cambios, Archivos Nuevos, Modificados, Tests)
- [ ] E4: GUIA_TECNICA.md con nota técnica para v4.45.0 (módulos, problema, solución, backwards compat)
- [ ] E5: Skills/workflows listados en README
- [ ] E6: `doctor.py --status` regenera SYSTEM_STATUS.md
- [ ] E7: `doctor.py --regenerate-domain-primer` ejecutado
- [ ] E8: `run_all_validations.py --quick` pasa 4/4 + symlink intacto + git diff --stat razonable
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.45.0`
