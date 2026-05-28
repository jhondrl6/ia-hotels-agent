# FASE-RELEASE-4.58.0: Documentación Oficial + Version Bump

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (estándar RELEASE phase)
> **Complejidad**: 🟢 BAJA

## Contexto previo

FASE-1 a FASE-4 completadas. v4complete verificado exitosamente con:
- Publication readiness = READY_FOR_PUBLICATION
- Proposal alignment ≥ 80%
- Los 3 issues de ROICRIII FASE-6 resueltos

**Version actual**: 4.57.0
**Version target**: 4.58.0

## Objetivo de esta fase

Bump de versión a 4.58.0, actualizar toda la documentación oficial, y ejecutar validaciones finales para cerrar el plan ROICRIIIF.

### Tareas

- [ ] **T1 — Version bump**:
  1. Editar `VERSION.yaml`: setear version a `4.58.0`
  2. Ejecutar `python scripts/sync_versions.py` (sin argumentos — sincroniza AGENTS.md, README.md)
  3. Verificar que `last_update` en AGENTS.md se actualizó
  4. NOTA: `sync_versions.py` usa `datetime.now()` para `{date}`, NO acepta `--bump minor --release-name`

- [ ] **T2 — CHANGELOG**:
  1. Añadir entrada en `CHANGELOG.md` para v4.58.0:
     - Fix: Gate recognizes pre-existing assets as present_in_production (GATE-PRESENCE)
     - Fix: Asset confidence enrichment for optimization_guide/faq_page (CONFIDENCE-LOW)
     - Fix: Removed pricing artifact "13%" from proposal template (SEMANTIC-13)
     - Verification: v4complete Hotel Castilla Real → publication READY

- [ ] **T3 — Docs cascade**:
  1. Actualizar `REGISTRY.md` con ROICRIIIF completado
  2. Actualizar `09-documentacion-post-proyecto.md` con resultados finales
  3. Actualizar este `06-checklist-implementacion.md` — todas las fases a ✅
  4. Actualizar `dependencias-fases.md` — todas las fases a ✅

- [ ] **T4 — Validaciones finales**:
  1. `python scripts/run_all_validations.py --quick` → debe pasar (si falla por pre-commit pre-existente, confiar en pre-commit hook)
  2. `pytest tests/ --timeout=60 -x` → sin regresiones (si --timeout no es válido, usar `pytest tests/ -x`)
  3. Pre-commit hook: `pre-commit run --all-files` (si disponible)

### Restricciones

- NO modificar código fuente — solo documentación y versionamento
- Si `run_all_validations.py --quick` falla con errores pre-existentes (no introducidos por ROICRIIIF), documentar y continuar
- Si `pytest --timeout=N` falla con "unrecognized argument", ejecutar sin --timeout (plugin no instalado)
- `sync_versions.py` README.md WARN es esperado y no bloqueante

### Criterios de completitud

- [ ] VERSION.yaml = 4.58.0
- [ ] CHANGELOG.md con entrada v4.58.0
- [ ] AGENTS.md last_update actualizado
- [ ] REGISTRY.md actualizado con ROICRIIIF
- [ ] 06-checklist-implementacion.md — todas fases ✅
- [ ] dependencias-fases.md — todas fases ✅
- [ ] 09-documentacion actualizado
- [ ] run_all_validations.py --quick sin errores nuevos
- [ ] pytest sin regresiones nuevas
- [ ] `log_phase_completion.py` ejecutado con `--fase RELEASE`

### Resumen final del plan

| Plan | Inicio | Fin | Versiones | Resultado |
|------|--------|-----|-----------|-----------|
| ROICRIII | FASE-1 | FASE-6 + RELEASE | 4.56.0 → 4.57.0 | 96% score, publication BLOCKED (3 issues) |
| ROICRIIIF | FASE-1 | FASE-4 + RELEASE | 4.57.0 → 4.58.0 | 3 issues fixed, publication READY |
