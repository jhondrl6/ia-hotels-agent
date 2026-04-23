# Checklist de Implementación - FASE-CAUSAL Alignment Fix

> **Plan**: Corregir desalineamiento diagnóstico-propuesta (corrección sintomática)
> **Estado actualizado**: 2026-04-22
> **Nota**: Este plan resuelve el síntoma inmediato (FAQ/OG faltan en propuesta). La causa raíz sistémica (propuesta generada desde diccionario estático en vez de pains dinámicos) queda documentada para FASE futura.

---

## Progreso General

|| Fase | Estado | % Completado |
|------|--------|--------------|
| FASE-CAUSAL-DIAG | ✅ Completada | 100% |
| FASE-CAUSAL-FIX | ✅ Completada | 100% |
| FASE-CAUSAL-TEST | ⏳ Pendiente | 0% |
| FASE-RELEASE-4.34.0 | ⏳ Pendiente | 0% |

---

## FASE-CAUSAL-DIAG: Diagnosticar Causa Raíz

### Tareas
- [x] Leer `proposal_asset_alignment.py` y documentar mapeo actual (5 servicios)
- [x] Leer `pain_solution_mapper.py` y verificar mapeo pains→assets (FAQ, OG)
- [x] Leer `asset_catalog.py` y confirmar que `faq_page` y `open_graph` son IMPLEMENTED
- [x] Leer `propuesta_v6_template.md` y confirmar hardcoding de tabla principal (líneas 44-50)
- [x] Leer `v4_proposal_generator.py` y documentar `_generate_asset_quality_table` (tabla dinámica)
- [x] Documentar la DOBLE TABLA: principal hardcodeada + secundaria dinámica
- [x] Verificar ASSET_NAMES: confirmar gap en `open_graph` y `og_tags_guide`
- [x] Comparar pains detectados vs servicios prometidos en propuesta
- [x] Confirmar causa raíz con evidencia de código
- [x] Documentar disclaimer: corrección sintomática vs refactor sistémico

### Criterios de Éxito
- [x] Causa raíz identificada y documentada (incluyendo doble tabla)
- [x] Evidencia de código citada
- [x] No se modifica ningún archivo (solo lectura)

### Entregable
- Informe de causa raíz en contexto del plan, incluyendo análisis de 3 capas (detección → promesa → presentación)

---

## FASE-CAUSAL-FIX: Corregir Mapeo, ASSET_NAMES y Ambas Tablas

### Tareas
- [x] Actualizar `PROPOSAL_SERVICE_TO_ASSET` en `proposal_asset_alignment.py`
  - [x] Agregar entrada para "Pagina de FAQ" → "faq_page"
  - [x] Agregar entrada para "Meta Tags Sociales (Open Graph)" → "open_graph"
- [x] Corregir `ASSET_NAMES` en `pain_solution_mapper.py`
  - [x] Verificar "faq_page" → "Página de FAQ" (ya existía)
  - [x] Agregar "open_graph" → "Meta Tags Sociales (Open Graph)"
  - [x] Agregar "og_tags_guide" → "Guía de Open Graph"
- [x] Actualizar tabla principal en `propuesta_v6_template.md` (líneas 44-50)
  - [x] Agregar fila "Página de FAQ"
  - [x] Agregar fila "Meta Tags Sociales (Open Graph)"
- [x] Verificar tabla dinámica en `v4_proposal_generator.py`
  - [x] Confirmar que `_generate_asset_quality_table` itera sobre PROPOSAL_SERVICE_TO_ASSET
  - [x] Validar que muestra 7 servicios tras el cambio
- [x] Actualizar tests de proposal_alignment (hardcoded 5 → 7)

### Archivos Afectados
- `modules/asset_generation/proposal_asset_alignment.py`
- `modules/commercial_documents/pain_solution_mapper.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/commercial_documents/v4_proposal_generator.py` (verificación, no modificación)

### Criterios de Éxito
- [x] `PROPOSAL_SERVICE_TO_ASSET` incluye FAQ y Open Graph (7 entradas)
- [x] `ASSET_NAMES` incluye `open_graph` y `og_tags_guide`
- [x] Tabla principal del template tiene 7 filas
- [x] Tabla dinámica refleja 7 servicios
- [x] Tests existentes siguen pasando (13/13)
- [x] Tests de proposal_alignment actualizados a 7 servicios
- [x] Se documenta que esto es corrección sintomática

### Tests
- [x] `pytest tests/asset_generation/test_proposal_alignment.py -v` — 13/13 PASSED
- [x] `run_all_validations.py --quick` — 3/4 (version sync falla en VERSION.yaml, pendiente FASE-RELEASE)

---

## FASE-CAUSAL-TEST: Verificación End-to-End

### Tareas
- [ ] Regenerar propuesta comercial para Amaziliahotel (`v4complete`)
- [ ] Verificar tabla principal "Esto es lo que hacemos" tiene 7 servicios
- [ ] Verificar tabla "Estado de los Entregables" (`asset_quality_table`) tiene 7 servicios
- [ ] Confirmar que FAQ y Open Graph aparecen en AMBAS tablas
- [ ] Verificar consistencia entre tabla principal y tabla de entregables
- [ ] Ejecutar `run_all_validations.py --quick`
- [ ] Verificar coherencia del documento generado

### Criterios de Éxito
- [ ] Propuesta incluye FAQ y Open Graph en ambas tablas
- [ ] Servicios corresponden a brechas detectadas
- [ ] Validaciones pasan 4/4
- [ ] Se documenta resultado de verificación de doble tabla

---

## FASE-RELEASE-4.34.0: Release y Documentación

### Tareas de Documentación (Flujo §4.5)
- [ ] Ejecutar `log_phase_completion.py` para cada fase
- [ ] Ejecutar `sync_versions.py`
- [ ] Validar formato de CHANGELOG.md
- [ ] Agregar nota técnica en GUIA_TECNICA.md
- [ ] Ejecutar `run_all_validations.py --quick`
- [ ] Ejecutar `doctor.py --status`
- [ ] Commit y tag

### Criterios de Éxito
- [ ] REGISTRY.md actualizado con 4 fases
- [ ] VERSION.yaml sincronizado en 6 archivos
- [ ] CHANGELOG.md con entrada [4.34.0]
- [ ] GUIA_TECNICA.md con nota de la corrección
- [ ] Validaciones pasan 4/4

---

## Métricas Acumulativas (Post-Release)

| Métrica | Valor |
|---------|-------|
| Tests totales | ~2224+ |
| Coherence Score | 0.84 (umbral 0.8) |
| Archivos modificados | 3-4 |
| Archivos nuevos | 0 |
| Nueva versión | 4.34.0 |
