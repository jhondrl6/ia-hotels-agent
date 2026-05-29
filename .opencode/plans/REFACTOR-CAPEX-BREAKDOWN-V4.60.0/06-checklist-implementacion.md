# Checklist de Implementación — REFACTOR-CAPEX-BREAKDOWN v4.60.0

## Estado General: 🔄 EN PROGRESO (FASE-1 ✅)

| Fase | Finding(s) | Estado | Sesión | Completada |
|------|-----------|--------|--------|------------|
| **FASE-1** | F1: Tabla CAPEX corrupta | ✅ COMPLETADO | 2026-05-29 | 2026-05-29 |
| **FASE-2** | F7+F8: Keys huérfanas + Fallback | ⏳ Pendiente | — | — |
| **FASE-3** | F6: Coherence Checklist | ⏳ Pendiente | — | — |
| **FASE-4** | v4complete + Verificación | ⏳ Pendiente | — | — |
| **FASE-RELEASE** | v4.60.0 docs + sync | ⏳ Pendiente | — | — |

---

## Dependencias

```
FASE-1 → FASE-2 (independiente)
       → FASE-3 (independiente)
              ↓
         FASE-4 (depende de FASE-1 + FASE-2 + FASE-3)
              ↓
         FASE-RELEASE (depende de FASE-4)
```

**Paralelismo posible:** FASE-2 y FASE-3 son independientes entre sí y de FASE-1. Podrían ejecutarse en paralelo si se quisiera optimizar, pero la regla R1 (1 fase/sesión) lo impide.

---

## FASE-1: F1 — Tabla CAPEX Corrupta ✅ COMPLETADO (2026-05-29)

- [x] T1: Template `propuesta_v6_template.md` L152 eliminado
- [x] T1: Sección `### Desglose del Setup Fee (CAPEX)` agregada
- [x] T2: Test `TestCAPEXPipeIntegrity::test_capex_section_no_nested_tables` agregado
- [x] T3: `pytest tests/test_capex_rename.py -v` → 8/8 PASS
- [x] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado (postergado a FASE-RELEASE)
- [ ] GUIA_TECNICA.md actualizado (postergado a FASE-RELEASE)
- [x] 06-checklist-implementacion.md actualizado

**Archivos modificados esperados:**
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `tests/test_capex_rename.py`

---

## FASE-2: F7+F8 — Generator Cleanup

- [ ] F7: 9 keys huérfanas eliminadas del dict en `_prepare_template_data()`
- [ ] F7: Variables locales preservadas (no eliminadas)
- [ ] F8: Fallback de `_build_capex_breakdown_table()` con header
- [ ] Tests de CAPEX pasan sin regresiones
- [ ] delegate_task: Subagente para F7 completado
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado

**Archivos modificados esperados:**
- `modules/commercial_documents/v4_proposal_generator.py`

---

## FASE-3: F6 — Coherence Checklist

- [ ] Decisión tomada: Opción A (YAGNI) o B (integrar)
- [ ] T1: Acción ejecutada según decisión
- [ ] T2: Tests pasan sin regresiones
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado

**Archivos modificados esperados:**
- `modules/commercial_documents/v4_proposal_generator.py`
- (Opcional) `propuesta_v6_template.md` si Opción B

---

## FASE-4: v4complete + Verificación

- [ ] T1: v4complete ejecutado para Hotel Castilla Real
- [ ] Evidencia copiada a `evidence/FASE-4-CAPEX-VERIFY/`
- [ ] F1 verificado: Tabla CAPEX 5 pipes/fila + desglose independiente
- [ ] F6 verificado: `${coherence_checklist}` no literal + coherence ≥ 0.80
- [ ] F7 verificado: Cero placeholders sin sustituir
- [ ] F8 verificado: Tabla desglose con header
- [ ] Gates: ≥ 9/11 PASS sin nuevas regresiones
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado

**Hotel:** Hotel Castilla Real (https://www.hotelcastillareal.com/)
**Región:** eje_cafetero
**Comando:** `python.exe main.py execute https://www.hotelcastillareal.com/ --region eje_cafetero --plan v4complete`

---

## FASE-RELEASE v4.60.0

- [ ] T1: VERSION.yaml → version=4.60.0, codename=CAPEX-BREAKDOWN-FIX
- [ ] T2: sync_versions.py ejecutado
- [ ] T3: CHANGELOG.md validado (entrada [4.60.0] completa)
- [ ] T4: GUIA_TECNICA.md validado (nota v4.60.0)
- [ ] T5: run_all_validations.py ejecutado
- [ ] T6: git commit + tag v4.60.0 + push

---

## Notas de Sesión

| Fecha | Fase | Sesión ID | Notas |
|-------|------|-----------|-------|
| 2026-05-29 | FASE-1 | REFACTOR-CAPEX-BREAKDOWN | Template fix L152 + TestCAPEXPipeIntegrity. 8/8 tests PASS. |
| — | — | — | Plan creado, pendiente ejecución |
