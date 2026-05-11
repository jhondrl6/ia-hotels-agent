# FASE-RELEASE: Documentación Oficial — v4.44.0

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA (sin comandos largos, solo scripts y docs)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~40 trabajo + ~15 docs = ~55.
>
> **REGLA DE DEPENDENCIA**: Esta fase SOLO se ejecuta cuando FASE-1 a FASE-5 tienen ✅ en `dependencias-fases.md`.

## Contexto previo

Todas las fases de implementación completadas:
- FASE-1: H6 — Coherence post-generación
- FASE-2: H1/H5/H8 — Propuesta completa + Gate robusto
- FASE-3: H7 — Monthly report fail-safe
- FASE-4: H3/H4 — Corrección financiera
- FASE-5: Verificación E2E con v4complete para Termales

## Objetivo de esta fase

Cerrar el ciclo de refactorización: version bump, documentación oficial, validaciones finales. **NO modificar código fuente** — solo docs, registro y sync.

### Tareas

- [ ] **T1: Registrar fases en REGISTRY.md**
  - Ejecutar por cada fase implementada (1 a 5):
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-1 --desc "Coherence post-generación: _validate_post_generation() en v4_asset_orchestrator.py + main.py" \
      --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py,main.py,modules/commercial_documents/coherence_validator.py" \
      --tests "3" --check-manual-docs
  ```
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-2 --desc "Propuesta completa + Gate robusto: 8 servicios, assets técnicos, threshold 0.8" \
      --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/service_catalog.py,modules/quality_gates/publication_gates.py" \
      --tests "3" --check-manual-docs
  ```
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-3 --desc "Monthly report fail-safe: try/except+retry, disclaimer, bug fix" \
      --archivos-mod "modules/asset_generation/conditional_generator.py,modules/asset_generation/monthly_report_generator.py,modules/commercial_documents/v4_proposal_generator.py" \
      --tests "3" --check-manual-docs
  ```
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-4 --desc "Corrección financiera: normalización brechas + separación pain_ratio/recovery" \
      --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
      --tests "3" --check-manual-docs
  ```
  ```bash
  ./venv/Scripts/python.exe scripts/log_phase_completion.py \
      --fase FASE-5 --desc "Verificación E2E: v4complete Termales + análisis de ejecución" \
      --archivos-nuevos "evidence/FASE-5-VERIFICACION/analisis_ejecucion.md" \
      --check-manual-docs
  ```

- [ ] **T2: Version bump y sync**
  - Actualizar `VERSION.yaml`: `version: "4.43.0"` → `version: "4.44.0"`
  - Actualizar `codename`: `"TERMALES-REFACTOR"` → `"TERMALES-COHERENCE-FIX"` (o similar)
  - Actualizar `release_date`: `"2026-05-09"`
  - Ejecutar: `./venv/Scripts/python.exe scripts/sync_versions.py`
  - Verificar: `./venv/Scripts/python.exe scripts/version_consistency_checker.py`

- [ ] **T3: Actualizar CHANGELOG.md y GUIA_TECNICA.md**
  - CHANGELOG.md: Añadir entrada `[4.44.0]` con formato CONTRIBUTING.md:
    - ### Objetivo
    - ### Cambios Implementados
    - ### Archivos Nuevos
    - ### Archivos Modificados
    - ### Tests
  - GUIA_TECNICA.md: Añadir nota técnica para FASE-1 a FASE-5 con:
    - Módulos afectados
    - Problema/solución
    - Backwards compatibility
    - Tests

- [ ] **T4: Validación final**
  - Ejecutar: `./venv/Scripts/python.exe scripts/run_all_validations.py --quick`
  - Ejecutar: `./venv/Scripts/python.exe scripts/doctor.py --status`
  - Verificar 4/4 checks pasan
  - Actualizar `dependencias-fases.md`: marcar FASE-1 a FASE-5 como ✅, FASE-RELEASE como ✅

### Restricciones

- **NO** modificar código fuente (solo VERSION.yaml que es metadata)
- **NO** ejecutar v4complete en esta fase
- **NO** crear nuevos tests (deben existir de fases anteriores)
- Si `version_consistency_checker.py` reporta FAIL, investigar si es R14 (sync_config regex drift) antes de "fixear" documentos

### Criterios de completitud

- [ ] REGISTRY.md tiene entradas para FASE-1 a FASE-5
- [ ] VERSION.yaml = 4.44.0, sincronizado en AGENTS.md/README/.cursorrules/CONTRIBUTING/GUIA_TECNICA/REGISTRY
- [ ] CHANGELOG.md tiene entrada `[4.44.0]` con formato correcto
- [ ] GUIA_TECNICA.md tiene notas técnicas para las 5 fases
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `doctor.py --status` ejecutado sin errores
- [ ] `dependencias-fases.md` actualizado con todos los ✅

### Cierre del proyecto

Este es el fin del plan de refactorización de coherencia. Si el usuario solicita nueva sesión, será un proyecto diferente o mantenimiento.
