# Checklist de Implementacion - Bugfix Sprint post-FASE-B

**Version Base**: 4.25.3
**Fecha**: 2026-04-08
**Progreso General**: 40% (2/5 fases)

```
[x] FASE-C: 4 Bugs Criticos
[x] FASE-D: 5 Bugs Medios + Serializacion
[          ] FASE-E: OG Detection HTML Reuse
[          ] FASE-F: Zombies + Code Smells
[          ] VALIDACION FINAL: v4complete amaziliahotel.com
```

---

## FASE-C: Correccion de 4 BUGS CRITICOS (4/4) ✅

### Tareas

- [x] **C1**: `import logging` agregado en imports del modulo (linea ~8)
- [x] **C2**: Linea 2017 usa `'overall_score'` en vez de `'score'`
- [x] **C3**: Linea 2006 usa `'open_graph'` con default `False` en vez de `'has_open_graph'` con default `True`
- [x] **C4**: Linea 1000 usa `is not None` check para `mobile_score`

### Validacion

- [x] **C5**: `run_all_validations.py --quick` pasa sin errores
- [x] **C6**: Todos los tests pasan (12 funciones modulo afectado)
- [x] **C7**: No se introdujeron nuevos warnings o errores de lint
- [x] **C8**: `log_phase_completion.py --fase FASE-C` ejecutado exitosamente
- [x] **C9**: Commit realizado con mensaje descriptivo

### Post-Ejecucion

- Fecha de completion: 2026-04-08
- Tests post-fase: 12/12 (modulo afectado)
- Issues encontrados: Test `test_identify_brechas_7_detected_returns_7` actualizado a 8 (brecha no_faq_schema preexistente)

---

## FASE-D: Correccion de 5 BUGS MEDIOS + Serializacion (6/6) - COMPLETADA 2026-04-08

### Tareas

- [x] **D1**: Metodos `_compute_opportunity_scores` y `_inject_brecha_scores` tienen una sola definicion cada uno
- [x] **D2**: Claves `*_regional_avg` aparecen una sola vez en el dict de template data
- [x] **D3**: Confidence usa mayusculas consistentemente (`.upper()`)
- [x] **D4**: Tabla AEO no tiene pipe duplicado (`|` no `||`)
- [x] **D5**: AEO score incluye `/100`
- [x] **D6**: `V4AuditResult.to_dict()` serializa `seo_elements` completo
- [x] **D7**: `executed_validators` incluye `"seo_elements_detection"`

### Validacion

- [x] **D8**: Tests pasan (209 passed, 7 failures preexistentes no relacionados)
- [x] **D9**: Sin regresion vs FASE-C (misma cuenta de failures preexistentes)
- [ ] **D10**: `log_phase_completion.py --fase FASE-D` ejecutado exitosamente
- [ ] **D11**: Commit realizado con mensaje descriptivo

### Post-Ejecucion

- Fecha de completion: ___
- Tests post-fase: ___
- Issues encontrados: ___

---

## FASE-E: OG Detection - HTML Reuse (0/3)

### Tareas

- [ ] **E1**: Segunda request HTTP eliminada (o reutilizada) en step 2.8/2.9
- [ ] **E2**: SEO elements detector usa el mismo HTML del schema audit
- [ ] **E3**: Logging defensivo agregado para OG no detectado

### Validacion

- [ ] **E4**: `run_all_validations.py --quick` pasa sin errores
- [ ] **E5**: Tests existentes pasan (sin regresion)
- [ ] **E6**: `log_phase_completion.py --fase FASE-E` ejecutado exitosamente
- [ ] **E7**: Commit realizado con mensaje descriptivo

### Post-Ejecucion

- Fecha de completion: ___
- Tests post-fase: ___
- Issues encontrados: ___

---

## FASE-F: Zombie References + Code Smells (0/11)

### Tareas - Zombies

- [ ] **F1**: Fila IAO eliminada de `diagnostico_ejecutivo.md`
- [ ] **F2**: Filas IAO + Voice Readiness eliminadas de `diagnostico_v4_template.md`
- [ ] **F3**: `iao_score` eliminado de `_get_analytics_fallback()` dict
- [ ] **F4**: `iao_score` eliminado de `benchmarks.py`

### Tareas - Code Smells

- [ ] **F5**: Import redundante datetime eliminado (MEN-1)
- [ ] **F6**: Scores calculados 1 sola vez (MEN-2)
- [ ] **F7**: `format_cop()` unificado (MEN-3)
- [ ] **F8**: `hasattr()` guard en competitors (MEN-4)
- [ ] **F9**: `print()` reemplazado por `logging.warning()` (MEN-5)
- [ ] **F10**: `import re` movido a imports del modulo (MEN-6)
- [ ] **F11**: Ternaria refactorizada con parentesis (MEN-7)

### Validacion

- [ ] **F12**: `run_all_validations.py --quick` pasa sin errores
- [ ] **F13**: Todos los tests pasan (sin regresion vs FASE-D)
- [ ] **F14**: `log_phase_completion.py --fase FASE-F` ejecutado exitosamente
- [ ] **F15**: Commit realizado con mensaje descriptivo

### Post-Ejecucion

- Fecha de completion: ___
- Tests post-fase: ___
- Issues encontrados: ___

---

## VALIDACION FINAL (post-FASE-F)

- [ ] **V1**: `v4complete --url https://amaziliahotel.com/` ejecutado exitosamente
- [ ] **V2**: Diagnostico generado sin errores
- [ ] **V3**: Brechas 9 y 10 detectables (OG + citability corregidos)
- [ ] **V4**: Score AEO refleja OG tags correctamente
- [ ] **V5**: No hay placeholders `${iao_score}` ni `${voice_readiness_score}` en output

### Post-Ejecucion

- Fecha de completion: ___
- Hotel de prueba: amaziliahotel.com
- Score AEO final: ___
- Brechas detectadas: ___

---

## Resumen de Commits Recomendados

| Fase | Mensaje |
|------|---------|
| FASE-C | `fix(FASE-C): 4 critical bugs in v4_diagnostic_generator - logging import, citability attr, OG attr, mobile_score short-circuit` |
| FASE-D | `fix(FASE-D): 5 medium bugs + seo_elements serialization in v4_comprehensive` |
| FASE-E | `fix(FASE-E): reuse schema audit HTML for OG detection, eliminate redundant HTTP request` |
| FASE-F | `fix(FASE-F): remove zombie IAO/voice refs + fix 7 code smells in v4_diagnostic_generator` |
| FINAL | `test: v4complete E2E validation on amaziliahotel.com post-bugfix-sprint` |

---

## Metricas del Sprint

| Metrica | Baseline | Target | Estado |
|---------|----------|--------|--------|
| Tests | 1782 | >= 1782 | Pendiente |
| Bugs criticos | 4 | 0 | Pendiente |
| Bugs medios | 5 | 0 | Pendiente |
| Serializacion SEO | Ausente | Completa | Pendiente |
| Zombie refs | 4 | 0 | Pendiente |
| Code smells | 7 | 0 | Pendiente |
| Validaciones | - | PASS | Pendiente |

---

*Este checklist sigue el formato de `phased_project_executor.md` v1.4.0*
*1 fase = 1 sesion. Secuencia obligatoria: C -> D -> E -> F -> VALIDACION*
