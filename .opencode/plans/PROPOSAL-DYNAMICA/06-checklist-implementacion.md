# Checklist de Implementación - Propuesta Dinámica desde Pain Detection

> **Plan**: Resolver causa raíz arquitectónica — propuesta desde diccionario estático → pains dinámicos
> **Estado actualizado**: 2026-04-23
> **Nota**: Este plan resuelve la causa raíz (propuesta dinámica) vs la corrección sintomática de v4.34.0.

---

## Progreso General

| Fase | Estado | % Completado |
|------|--------|--------------|
| FASE-CAUSAL-DIAG | ✅ Completada | 100% |
| FASE-CAUSAL-REFACTOR | ✅ Completada | 100% |
| FASE-CAUSAL-VALIDATE | ⏳ Pendiente | 0% |
| FASE-RELEASE-X.Y.Z | ⏳ Pendiente | 0% |

---

## FASE-CAUSAL-DIAG: Diagnosticar Mapeo Pain→Servicio

### Tareas
- [x] Leer `pain_solution_mapper.py` y documentar todos los pains y sus soluciones
- [x] Leer `v4_proposal_generator.py` y documentar cómo se genera la propuesta
- [x] Leer `proposal_asset_alignment.py` y documentar `PROPOSAL_SERVICE_TO_ASSET`
- [x] Leer `propuesta_v6_template.md` y documentar estructura de tablas
- [x] Mapear cada pain → servicio(s) correspondiente(s)
- [x] Identificar qué servicios NO tienen pain asociado en el mapper
- [x] Identificar qué pains detectados NO tienen servicio en `PROPOSAL_SERVICE_TO_ASSET`
- [x] Documentar el gap: pains detectados vs servicios prometidos

### Criterios de Éxito
- [x] Mapeo completo pain→servicio documentado
- [x] Gap analysis hecho (pains sin servicio, servicios sin pain)
- [x] No se modifica ningún archivo (solo lectura)

### Entregable
- [x] Mapa completo pain→servicio en `context/mapeo-pain-servicio.md`

**Estado**: ✅ COMPLETADA — 2026-04-23

---

## FASE-CAUSAL-REFACTOR: Refactorizar Generador

### Tareas
- [x] Crear `SERVICE_CATALOG` con metadatos de servicios vendibles
- [x] Eliminar duplicación de `_generate_asset_quality_table` (líneas ~654 y ~1084)
- [x] Refactorizar `_generate_asset_quality_table` para iterar sobre pains detectados
- [x] Mantener backwards compatibility con `PROPOSAL_SERVICE_TO_ASSET` para gates
- [x] Actualizar template si es necesario (quitar hardcoding de tabla principal)
- [x] Verificar que la propuesta sigue funcionando sin errors

### Archivos Afectados
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/service_catalog.py` (nuevo)
- `modules/commercial_documents/templates/propuesta_v6_template.md`

### Criterios de Éxito
- [x] Propuesta se genera dinámicamente desde pains detectados
- [x] Tabla principal ya no es hardcodeada
- [x] Backwards compatible con gates de publicación existentes
- [x] Tests existentes siguen pasando

### Tests
- [x] `pytest tests/asset_generation/test_proposal_alignment.py -v` — 13/13 PASS
- [x] `run_all_validations.py --quick` — 4/4

**Estado**: ✅ COMPLETADA — 2026-04-23

---

## FASE-CAUSAL-VALIDATE: Verificación Unitaria (sin E2E v4complete)

### Tareas
- [x] Ejecutar tests de proposal_alignment (13/13 PASS)
- [x] Verificar SERVICE_CATALOG importable con >= 7 entradas y pain_id válido
- [x] Verificar que `_generate_asset_quality_table` acepta `detected_pain_ids` como parámetro
- [x] Crear `tests/commercial_documents/test_proposal_dynamic.py` que verifique filtrado por pains detectados
- [x] Ejecutar `run_all_validations.py --quick` (4/4)
- [x] **NO ejecutar v4complete E2E** (reservado para FASE-RELEASE)

### Criterios de Éxito
- [x] Tests pasan 13/13 (alignment)
- [x] SERVICE_CATALOG válido (7 entradas con pain_id)
- [x] Función refactorizada con firma correcta (`detected_pain_ids`)
- [x] test_proposal_dynamic.py pasa: solo servicios de pains detectados (14/14 PASS)
- [x] Validaciones 4/4 PASS
- [x] Sin llamadas a API (costo cero)

**Estado**: ✅ COMPLETADA — 2026-04-23

---

## FASE-RELEASE-X.Y.Z: Release y Documentación

### Tareas de Documentación (Flujo §4.5)
- [ ] Ejecutar `log_phase_completion.py` para cada fase
- [ ] Ejecutar `sync_versions.py`
- [ ] Validar formato de CHANGELOG.md
- [ ] Agregar nota técnica en GUIA_TECNICA.md
- [ ] **Ejecutar E2E v4complete (ÚNICA vez en todo el plan)** — amaziliahotel.com
- [ ] Ejecutar `run_all_validations.py --quick`
- [ ] Ejecutar `doctor.py --status`
- [ ] Commit y tag

### Criterios de Éxito
- [ ] REGISTRY.md actualizado con 4 fases
- [ ] VERSION.yaml sincronizado en 6 archivos
- [ ] CHANGELOG.md con entrada [X.Y.Z]
- [ ] GUIA_TECNICA.md con nota de la corrección arquitectónica
- [ ] E2E v4complete pasa (servicios dinámicos, coherence >= 0.8)
- [ ] Validaciones pasan 4/4

---

## Métricas Acumulativas (Post-Release)

| Métrica | Valor |
|---------|-------|
| Tests totales | ~2224+ |
| Coherence Score | TBD (post-validación) |
| Archivos modificados | 2-3 |
| Archivos nuevos | 0-1 |
| Nueva versión | X.Y.Z |
