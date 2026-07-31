# FASE-5: RELEASE — Version Bump, CHANGELOG, Docs Cascade, Pre-commit

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAGENTE (delegate_task)

## Contexto previo

FASE-1 a FASE-4 completadas:
- BUG-1 + NEW-1: ADR y occupancy del onboarding propagados al harness
- H1: Proposal generator usa ADR del onboarding
- H3: ValidationSummary deriva confidence de fuente real
- H2: Taxonomía de fuentes unificada
- BUG-2: CTAs condicionados a has_onboarding
- H4: Tests e2e escritos y pasando
- v4complete ejecutado para Hotel Don Alfonso: cifras correctas verificadas

## Objetivo de esta fase

Release formal del fix: version bump, CHANGELOG, documentación cascade, pre-commit validation.

### Tareas

- [ ] 5.1 Version bump en VERSION.yaml
  - Bump patch o minor según convención del repo
  - Verificar con `python3 scripts/sync_versions.py --check` (NO usar --bump, ver pitfall del skill)

- [ ] 5.2 CHANGELOG.md
  - Agregar entrada bajo `[Unreleased]` (o nueva versión):
    ```
    ### Fixed
    - BUG-1: ADR de onboarding ahora se propaga al harness financiero (antes: ignorado, usaba benchmark regional)
    - NEW-1: Occupancy_rate del onboarding ya no es sobrescrito por benchmark regional
    - H1: Proposal generator usa ADR del onboarding (antes: resolver paralelo con None)
    - H3: ValidationSummary confidence/sources ahora reflejan fuente real del valor
    - H2: Unificada taxonomía de fuentes (ADRSource enum) entre diagnóstico, propuesta y JSON
    - BUG-2: CTAs "Complete el onboarding" ahora condicionados a has_onboarding (7 superficies)
    - F3: adr_source en JSON ya no es placeholder "handler"
    ### Added
    - H4: Tests e2e onboarding → harness → JSON pipeline
    ```

- [ ] 5.3 Docs cascade: GUIA_TECNICA.md, AGENTS.md (si aplica)
  - Actualizar sección de onboarding/data propagation si existe
  - Actualizar "Estado Actual" en AGENTS.md

- [ ] 5.4 Pre-commit validation
  - `python3 scripts/run_all_validations.py --quick` (si existe)
  - O: pre-commit run --all-files
  - Si hay failures preexistentes (no relacionados), documentar y no bloquear

### Restricciones

- NO ejecutar v4complete (ya hecho en FASE-4)
- NO modificar código de fixes (ya hechos en FASE-1 a FASE-3)
- `sync_versions.py` NO acepta --bump (ver pitfall del skill: usar --check, --list, --validate)
- Editar VERSION.yaml manualmente, luego correr sync_versions.py sin args
- README.md counts (test count, module count) NO se sync con sync_versions.py — auditar manualmente

### Criterios de completitud

- [ ] VERSION.yaml bumped
- [ ] CHANGELOG.md tiene entrada con todos los fixes
- [ ] Pre-commit pasa (o failures son preexistentes documentados)
- [ ] `git log --oneline -5` muestra los commits de FASE-1 a FASE-5
- [ ] Commit final: `release: BUGS-ONBOARDING-ADR fixes v<version>`

### Próxima sesión

Plan completado. No hay próxima sesión. El análisis post-implementación está en 08-analisis-post-implementacion.md (completado en FASE-4).

---

## Prompt para delegate_task (auto-contenido)

```
Eres un subagente que trabaja en el proyecto iah-cli en /mnt/c/Users/Jhond/Github/iah-cli.

OBJETIVO: Release formal de los fixes BUGS-ONBOARDING-ADR-2026-07-22.

CAMBIOS REQUERIDOS:

A) Version bump:
   1. Leer VERSION.yaml
   2. Bump patch o minor version
   3. NO usar sync_versions.py --bump (no existe). Editar VERSION.yaml manualmente.
   4. Correr: python3 scripts/sync_versions.py --check (verificar consistencia)

B) CHANGELOG.md:
   Agregar entrada:
   ### Fixed
   - BUG-1: ADR de onboarding ahora se propaga al harness financiero
   - NEW-1: Occupancy_rate del onboarding ya no es sobrescrito por benchmark regional
   - H1: Proposal generator usa ADR del onboarding (no resolver paralelo)
   - H3: ValidationSummary confidence/sources reflejan fuente real del valor
   - H2: Unificada taxonomía de fuentes entre diagnóstico, propuesta y JSON
   - BUG-2: CTAs "Complete el onboarding" condicionados a has_onboarding
   - F3: adr_source en JSON ya no es placeholder "handler"
   ### Added
   - H4: Tests e2e onboarding → harness → JSON pipeline

C) Pre-commit validation:
   - python3 scripts/run_all_validations.py --quick (o pre-commit run --all-files)
   - Si hay failures preexistentes (55 tests que ya fallaban antes), documentar y no bloquear

D) Verificación final:
   - git log --oneline -5 (mostrar commits)
   - git diff --stat HEAD~5..HEAD (mostrar archivos tocados)

IMPORTANTE: sync_versions.py NO acepta --bump. Editar VERSION.yaml manualmente. README.md counts no se sync automáticamente — auditar si es necesario.
```
