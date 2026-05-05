# Checklist de Implementación — SCORING-TRANSPARENCY

**Plan:** SCORING-TRANSPARENCY v1.0.0
**Actualizado:** 2026-05-05

---

## SCORING-A: Fix del filtrado en `_build_scoring_breakdown()`

**Estado:** ✅ Completada (2026-05-05)

### Tareas

- [x] **A1.** Leer `_build_scoring_breakdown()` en `v4_diagnostic_generator.py:276-285`
- [x] **A2.** Modificar la función: iterar TODO el checklist, marcar ✅ True / `~~nombre(peso%)~~` False
- [x] **A3.** Ejecutar v4complete para Hotel Castilla Real (hotelcastillareal.com, region=eje_cafetero)
- [x] **A4.** Verificar en el output: 6/6 factores GEO visibles (4✅ + 2~~tachado~~), score sigue 70/100
- [x] **A5.** `run_all_validations.py --quick` pasa 4/4
- [x] **A6.** Ejecutar `log_phase_completion.py --fase FASE-SCORING-A`

### Criterios de Aceptación

- [x] `_build_scoring_breakdown('geo', ...)` retorna string con TODOS los factores del checklist (no solo True)
- [x] Factores False aparecen con formato `~~nombre(peso%)~~`
- [x] Score calculado no cambia (sigue usando `calcular_score_*()`)
- [x] Diagnóstico de Hotel Castilla Real muestra breakdown GEO completo

---

## SCORING-B: Extensión del breakdown a los 4 pilares

**Estado:** ✅ Completada (2026-05-05)
**Dependencia:** SCORING-A ✅ Completada

### Tareas

- [x] **B1.** Leer `v4_diagnostic_generator.py` ~L697 y `diagnostico_v6_template.md`
- [x] **B2.** Agregar 3 asignaciones en generator: `seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown`
- [x] **B3.** Agregar 3 placeholders en template v6: `${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}`
- [x] **B4.** Ejecutar v4complete para Hotel Castilla Real (hotelcastillareal.com, region=eje_cafetero)
- [x] **B5.** Verificar: los 4 pilares tienen breakdown visible en el diagnóstico generado
- [x] **B6.** `run_all_validations.py --quick` pasa 4/4
- [x] **B7.** Ejecutar `log_phase_completion.py --fase FASE-SCORING-B`

### Criterios de Aceptación

- [x] Diagnóstico incluye `${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}` (además del GEO existente)
- [x] Cada uno muestra TODOS los factores del checklist correspondiente (herencia del fix de SCORING-A)
- [x] `scoring_methodology.md` y el output están alineados (4 pilares documentados = 4 pilares mostrados)
- [x] Diagnóstico de Hotel Castilla Real muestra los 4 breakdowns

---

## SCORING-C: Documentación Cascade

**Estado:** ✅ Completada (2026-05-05)
**Dependencia:** SCORING-A ✅ Completada + SCORING-B ✅ Completada

### Tareas

- [x] **C1.** Ejecutar `log_phase_completion.py` para SCORING-A
- [x] **C2.** Ejecutar `log_phase_completion.py` para SCORING-B
- [x] **C3.** Ejecutar `log_phase_completion.py` para SCORING-C (auto-referencia)
- [x] **C4.** Crear entrada en CHANGELOG.md para v4.40.1 (formato CONTRIBUTING.md)
- [x] **C5.** Agregar nota técnica en GUIA_TECNICA.md
- [x] **C6.** Ejecutar `sync_versions.py` (VERSION.yaml → 6 archivos)
- [x] **C7.** Ejecutar `run_all_validations.py --quick` (debe pasar 4/4)
- [x] **C8.** Ejecutar `doctor.py --status`

### Criterios de Aceptación

- [x] REGISTRY.md tiene las 3 entradas (SCORING-A, SCORING-B, SCORING-C)
- [x] CHANGELOG.md tiene entrada `[4.40.1]` con formato correcto
- [x] GUIA_TECNICA.md tiene nota técnica de scoring transparency
- [x] `run_all_validations.py --quick` pasa 4/4
- [x] `sync_versions.py` ejecutado sin errores
- [x] `version_consistency_checker.py` pasa
