# Checklist de Implementacion — REFACTOR-ONBOARDING-CTA

## Estado General

| Aspecto | Estado |
|---------|--------|
| Plan | ✅ Preparado |
| Fases de implementacion | 🟡 1/3 completadas |
| Documentacion | 🟡 Pendiente |

## Fases

### FASE-REFACTOR-CTA-A (Fix Codigo + Tests)

**Descripcion:** Refactoriza el CTA de onboarding en diagnostico Tier C para listar explicitamente los 4 datos requeridos.

**Estado:** ✅ Completada (2026-05-05)

**Tareas:**
- [x] T1: Refactorizar string `show_onboarding_cta` en `v4_diagnostic_generator.py`
- [x] T2: Actualizar tests en `test_precision_rendering.py`
- [x] T3: Ejecutar tests y verificar que pasan (12/12 PASS)
- [x] T4: Actualizar estado de fase en plan

**Dependencias:** Ninguna (primera fase)

**Archivos:**
- `modules/commercial_documents/v4_diagnostic_generator.py`
- `tests/commercial_documents/test_precision_rendering.py`

---

### FASE-REFACTOR-CTA-B (v4complete + Verificacion)

**Descripcion:** Ejecuta v4complete sobre Hotel Castilla Real y verifica que el CTA refactorizado aparece correctamente en el diagnostico generado.

**Estado:** ✅ Completada (2026-05-05 20:27)

**Tareas:**
- [x] T1: Ejecutar `v4complete --url https://www.hotelcastillareal.com/`
- [x] T2: Guardar evidencia en `evidence/FASE-REFACTOR-CTA-B/`
- [x] T3: Verificar CTA en `01_DIAGNOSTICO_*.md` generado (Tier C confirmado — CTA presente con 4 datos)

**Resultado verificacion:**
- Hotel: hotelcastillareal, Tier C
- CTA: Linea 120 del diagnostico — "Complete el onboarding con sus datos reales: numero de habitaciones, reservas mensuales promedio, valor promedio de reserva (COP) y porcentaje de canal directo."
- 4 datos: habitaciones ✅, reservas ✅, reserva ✅, canal directo ✅
- Content Scrubber: 3 fixes aplicados
- Coherence: 0.74 (debajo umbral 0.8 — modo no-bloqueante)

**Dependencias:** FASE-REFACTOR-CTA-A ✅

**Archivos:**
- `output/v4_complete/01_DIAGNOSTICO_*.md` (lectura)
- `evidence/FASE-REFACTOR-CTA-B/` (escritura)

---

### FASE-REFACTOR-CTA-C (Documentacion Post-Fase)

**Descripcion:** Flujo documental obligatorio: REGISTRY, CHANGELOG, GUIA_TECNICA, validaciones finales.

**Estado:** ✅ Completada — 2026-05-05

**Tareas:**
- [x] T1: `log_phase_completion.py --fase FASE-REFACTOR-CTA-ONBOARDING ... --check-manual-docs` — REGISTRY OK, sin GAPs
- [x] T2: `sync_versions.py` + `version_consistency_checker.py` — All in sync
- [x] T3: Actualizar `CHANGELOG.md` (entrada [4.40.2]) y `GUIA_TECNICA.md` (nota tecnica)
- [x] T4: `run_all_validations.py --quick` (4/4) + `doctor.py --status` (OK)

**Dependencias:** FASE-REFACTOR-CTA-A ✅ y FASE-REFACTOR-CTA-B ✅

---

## Notas de Ejecucion

- 3 sub-fases — no requiere FASE-RELEASE separada (PATCH-level, bugfix de texto)
- R3: todas las fases dentro de scope
- Hotel de verificacion: Castilla Real (https://www.hotelcastillareal.com/)
