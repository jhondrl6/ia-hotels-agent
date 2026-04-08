# Checklist Maestro - Fix AEO Score "Pendiente de datos"

## Proyecto
Reemplazar `_calculate_aeo_score()` stub con scoring completo de 4 componentes:
Schema 25pts + FAQ 25pts + OG 25pts + Citabilidad 25pts.

## Root Cause
`_calculate_aeo_score()` en `v4_diagnostic_generator.py:1324` solo verifica
`performance.mobile_score`. Si PageSpeed API no retorna datos → "0 (Pendiente de datos)".
Los datos de Schema, FAQ, OG y Citabilidad existen en `V4AuditResult` pero no se usan.

---

## Estado de Fases

| Fase | Descripción | Estado | Fecha | Tests |
|------|-------------|--------|-------|-------|
|| FASE-A | Implementar detección real OG en `seo_elements_detector.py` | ✅ Completada | 2026-04-08 | 9/8 ||
| FASE-B | Reescribir `_calculate_aeo_score()` con 4 componentes | ⏳ Pendiente | — | 0/10 |
| FASE-C | Integración, regresión, documentación | ⏳ Pendiente | — | 0/verif |

---

## Métricas Acumulativas

| Métrica | Inicio | FASE-A | FASE-B | FASE-C |
|---------|--------|--------|--------|--------|
|| Tests nuevos | 0 | +9 | +10 | — ||
| Tests total (acumulado) | 1782 | 1790 | 1800 | 1800 |
| Archivos nuevos | 0 | +1 | +1 | — |
| Archivos modificados | 0 | +1 | +1 | — |
| AEO score típico | "0 (Pendiente de datos)" | — | "50" (hotel típico) | ✅ verificado |

---

## Dependencias

```
FASE-A ──→ FASE-B ──→ FASE-C
 (datos)   (scoring)   (validación)
```

Sin conflictos de archivos entre fases.

---

## Checklists por Fase

### FASE-A: Data Foundation ✅
- [x] `_detect_open_graph()` implementado con BeautifulSoup
- [x] `_detect_images_alt()` implementado
- [x] `_detect_social_links()` implementado
- [x] `detect()` conecta métodos reales
- [x] 9 tests pasan (8 obligatorios + 1 extra: no social links)
- [x] `run_all_validations.py --quick` pasa (3/4, version sync pre-existente)
- [x] `log_phase_completion.py --fase FASE-A` ejecutado

### FASE-B: AEO Scoring Rewrite
- [ ] `_calculate_aeo_score()` reescrito con 4 componentes × 25pts
- [ ] Docstring actualizado
- [ ] 10 tests pasan
- [ ] Compatibilidad con `_get_score_status()` verificada
- [ ] `run_all_validations.py --quick` pasa
- [ ] `log_phase_completion.py --fase FASE-B` ejecutado

### FASE-C: Integration & Validación
- [ ] Template v6 renderiza AEO como número
- [ ] 0 regresiones en tests existentes
- [ ] Benchmark regional verificado
- [ ] Documentación afiliada actualizada
- [ ] `log_phase_completion.py --fase FASE-C` ejecutado
- [ ] Fix verificado: output real ya no muestra "Pendiente de datos"
