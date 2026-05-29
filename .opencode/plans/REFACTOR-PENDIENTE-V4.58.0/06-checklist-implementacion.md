# Checklist de Implementación — REFACTOR-PENDIENTE-V4.58.0

## Estado General

| Aspecto | Estado |
|---------|--------|
| Plan | ⚪ Preparación |
| Fases de implementación | 0/9 completadas |
| Documentación | ⚪ Pendiente |
| v4complete ejecutado | ⚪ Pendiente |
| Fixes verificados | 0/7 |

---

## FASE-0: Verificación y Preparación

**Descripción:** Confirmar estado actual del código contra claims de Pendiente.md

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Verificar IMP-03 (CAPEX breakdown sin consumir)
- [ ] T2: Verificar F7 (discrepancia entre gates)
- [ ] T3: Verificar MIN-02 (ADR no evidenciado)
- [ ] T4: Verificar MIN-01, MIN-03 y dead code

**Dependencias:** Ninguna (primera fase)

**Delegate:** ✅ Sí

---

## FASE-1A: IMP-03 (CAPEX Breakdown) + F7 (Gate Discrepancy)

**Descripción:** Añadir `${capex_breakdown_table}` al template + unificar lógica de gates

**Estado:** ✅ Completada

**Tareas:**
- [x] T1: Añadir `${capex_breakdown_table}` en `propuesta_v6_template.md`
- [x] T2: Unificar `financial_validity` gate para usar `evidence_tier` formal
- [x] T3: Tests de regresión — **PRE-EXISTING**: `test_identify_brechas_returns_all_detected` falla en baseline (no связано con cambios FASE-1A)
- [x] T4: Actualizar estado

**Dependencias:** FASE-0 ✅

**Delegate:** ✅ Sí

**Archivos:**
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/quality_gates/publication_gates.py`

---

## FASE-1B: F5 (ADR Checklist siempre [PENDING])

**Descripción:** Fix bug en `_build_coherence_checklist()` para buscar ADR en cascada

**Estado:** ✅ Completada

**Tareas:**
- [x] T1: Trazar flujo de datos de ADR — `validated_data.get('adr')` siempre None; `RegionalADRResolver` existe en `modules/financial_engine/regional_adr_resolver.py`
- [x] T2: Fix `_build_coherence_checklist()` + nuevo helper `_get_adr_from_benchmarks()` — Implementada cascada: validated_data → benchmarks regionales (via `RegionalADRResolver`) → None. ADR de `eje_cafetero` = $420,000 COP
- [x] T3: Tests de regresión — Pre-existing failures en `test_identify_brechas_returns_all_detected` y `test_proposal_generator.py::TestConfidenceToNivelSignificado` no связаны con cambios. Verificado manualmente que `_build_coherence_checklist()` muestra `[OK]` cuando benchmark tiene ADR
- [x] T4: Actualizar estado

**Dependencias:** FASE-0 ✅

**Delegate:** ✅ Sí

**Archivos:**
- `modules/commercial_documents/v4_proposal_generator.py` — nuevo `_get_adr_from_benchmarks()` + fix cascada ADR

---

## FASE-2: MIN-02 (ADR Evidenciado) ⭐ MÁS COMPLEJA

**Descripción:** ADR completo en propuesta: YAML benchmarks + código + template

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Añadir `adr` en `config/regional_benchmarks.yaml` (todas las regiones)
- [ ] T2: Inyectar `adr_display` y `adr_value` en el data dict
- [ ] T3: Añadir `${adr_display}` placeholder en template
- [ ] T4: Tests + verificación YAML

**Dependencias:** FASE-1B ✅

**Delegate:** ❌ NO (complejidad alta)

**Archivos:**
- `config/regional_benchmarks.yaml`
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

---

## FASE-3: MIN-01 (Status Quo vs Implementación)

**Descripción:** Nueva tabla comparativa con pérdida mensual vs ROI

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Implementar `_build_status_quo_table()`
- [ ] T2: Añadir `${status_quo_table}` en template
- [ ] T3: Inyectar en data dict
- [ ] T4: Tests + Estado

**Dependencias:** FASE-2 ✅

**Delegate:** ✅ Sí

**Archivos:**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

---

## FASE-4: MIN-03 (Closing Pitch Dinámico)

**Descripción:** Reemplazar texto estático con pitch basado en ROICR + payback

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Implementar `_build_closing_pitch()`
- [ ] T2: Reemplazar texto duro en template
- [ ] T3: Inyectar en data dict
- [ ] T4: Tests + Estado

**Dependencias:** FASE-3 ✅

**Delegate:** ✅ Sí

**Archivos:**
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

---

## FASE-5: Limpieza de Deuda Técnica

**Descripción:** Eliminar template embebido muerto L575-605

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Verificar 0 referencias activas (grep exhaustivo)
- [ ] T2: Eliminar bloque de template embebido
- [ ] T3: Tests de regresión + verificación generator
- [ ] T4: Actualizar estado

**Dependencias:** FASE-4 ✅

**Delegate:** ✅ Sí

**Archivos:**
- `modules/commercial_documents/v4_proposal_generator.py`

---

## FASE-6: v4complete Hotel Castilla Real (E2E)

**Descripción:** ÚNICA ejecución de v4complete + post-análisis de los 7 fixes

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Ejecutar v4complete (timeout 900s)
- [ ] T2: Guardar evidencia en `evidence/FASE-PENDIENTE-V4COMPLETE/`
- [ ] T3: Post-análisis: verificar cada fix en output real
- [ ] T4: Informe con métricas vs baseline

**Dependencias:** FASE-0 a FASE-5 ✅

**Delegate:** ✅ Sí (subagent con terminal para comando largo)

**Archivos:**
- `output/v4_complete/*` (lectura)
- `evidence/FASE-PENDIENTE-V4COMPLETE/` (creación)

---

## FASE-RELEASE: Documentación y Sincronización

**Descripción:** Cascade documental completo

**Estado:** ⚪ Pendiente

**Tareas:**
- [ ] T1: Log phase en REGISTRY.md
- [ ] T2: Bump versión + sync_versions.py
- [ ] T3: CHANGELOG.md + GUIA_TECNICA.md
- [ ] T4: Validación final

**Dependencias:** FASE-6 ✅

**Delegate:** ❌ NO (scripts con WSL quoting traps)

**Archivos:**
- `docs/contributing/REGISTRY.md`
- `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md`
- `AGENTS.md`, `README.md`, `.cursorrules`, `CONTRIBUTING.md`

---

## Tabla de Verificación Post-v4complete

| Fix | Esperado | Resultado |
|-----|----------|-----------|
| IMP-03 CAPEX breakdown | Tabla desglose en propuesta | ✅ FASE-1A |
| MIN-01 Status Quo | Tabla comparativa Sin/Con IAO | — |
| MIN-02 ADR evidenciado | Valor COP en benchmarks + propuesta | — |
| MIN-03 Closing pitch | Pitch dinámico con ROICR | — |
| F5 ADR checklist | Valor real (no "Pendiente") | — |
| F7 Gate discrepancy | Mismo tier en ambos gates | ✅ FASE-1A |
| Dead code | Sin errores de ejecución | — |

## Métricas vs Baseline

| Métrica | Baseline (pre) | Post-fix | Delta |
|---------|---------------|----------|-------|
| Coherence score | 0.83 | — | — |
| Publication Gates | 9/11 | — | — |
| Tier | B | — | — |
| Blocking issues | 0 | — | — |

---

## Notas de Ejecución

- 9 fases totales (0, 1A, 1B, 2, 3, 4, 5, 6, RELEASE)
- **FASE-2 NO delegar** — la más compleja (triple capa YAML+código+template)
- **FASE-RELEASE NO delegar** — WSL quoting traps en scripts
- 1 fase por sesión (R1)
- Máximo 60 iteraciones por fase (R2)
- v4complete único en FASE-6
