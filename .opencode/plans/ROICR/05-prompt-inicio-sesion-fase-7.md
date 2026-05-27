# FASE-7: RELEASE v4.55.0 — Documentation Sync + Version Bump + Final Validation

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (docs + sync)
> **Plan**: ROICR
> **Prerrequisito**: FASE-6 completada (v4complete exitoso + análisis post-implementación)

## Contexto previo

FASE-1: Validator semántico. FASE-2: Gate P1 BLOCKING. FASE-3: Pipeline unificado + CAPEX/OPEX. FASE-4: Arbitraje + Garantía. FASE-5: Tests + Fixtures. FASE-6: v4complete Hotel Castilla Real + análisis de 6 niveles.

Esta fase NO toca código. Valida documentación, sincroniza versiones, y cierra el release.

## Objetivo de esta fase

Cerrar el release v4.55.0 con documentación sincronizada y pre-commit validado.

### Tareas

- [ ] **7A**: Version bump
  - Editar `VERSION.yaml`: versión → `4.55.0`, release_name → `ROICR`
  - Ejecutar `sync_versions.py` (sin args — el script lee VERSION.yaml)
  - Verificar que CHANGELOG.md, REGISTRY.md, y AGENTS.md se actualicen
  - **PITFALL**: `sync_versions.py` NO acepta `--bump` ni `--release-name`. Solo `--check`, `--list`, `--validate`, `--rule`, o sin args.

- [ ] **7B**: CHANGELOG.md
  - Agregar entrada v4.55.0 con resumen de cambios ROICR:
    - Pipeline unificado de pricing (3 pasos)
    - CAPEX/OPEX desacoplado
    - Curva de maduración 4 pilares
    - AssetSemanticsValidator
    - Gate P1 BLOCKING
    - Arbitraje ético
    - Garantía Día 55 (`validate-guarantee`)
    - Fixtures recalibrados

- [ ] **7C**: REGISTRY.md
  - Registrar última fase completada: `FASE-RELEASE` (o el nombre que use la convención del repo)
  - Actualizar checklist si existe

- [ ] **7D**: Domain primer regeneration
  - Ejecutar `doctor.py --regenerate-domain-primer`
  - **PITFALL**: El script usa `datetime.now()` como fecha, ignora `release_date` de VERSION.yaml. Esto es esperado.

- [ ] **7E**: Pre-commit + validaciones finales
  - Ejecutar `pre-commit run --all-files`
  - Si `run_all_validations.py --quick` falla pero pre-commit pasa → confiar en pre-commit
  - **PITFALL**: `pytest --timeout=120` NO funciona (pytest.ini no tiene pytest-timeout). Usar `pytest` sin `--timeout`.
  - **PITFALL**: README.md siempre falla en `sync_versions.py` (formato de header diferente). Es pre-existente, no es regresión.

- [ ] **7F**: log_phase de cada fase
  - Cada fase (1-6) debe registrar su ejecución. Si no se hizo durante la ejecución de cada fase, registrar aquí.
  - **PITFALL**: En WSL, `cmd.exe /c` con paths relativos falla. Usar full Windows path para venv.

- [ ] **7G**: Documentar resultado final en `09-documentacion-post-proyecto.md`
  - Cerrar sección de "Veredicto Final"
  - Listar todos los archivos nuevos/modificados
  - Confirmar que el release está listo para merge

### Restricciones

- NO tocar código — solo documentación y sync
- NO ejecutar v4complete (ya se hizo en FASE-6)
- Si pre-commit falla por algo que NO es del plan ROICR → documentar como pre-existente, NO fixear
- `sync_versions.py` no acepta `--bump` — editar VERSION.yaml manualmente y correr el script sin args

### Criterios de completitud

- [ ] `VERSION.yaml` dice `4.55.0`
- [ ] `CHANGELOG.md` tiene entrada v4.55.0
- [ ] `REGISTRY.md` actualizado
- [ ] Pre-commit pasa (o fallos son pre-existentes documentados)
- [ ] `09-documentacion-post-proyecto.md` tiene veredicto final
- [ ] Checklist `06-checklist-implementacion.md` 100% completo

### Criterio de Cierre del Plan

> El plan ROICR está cerrado cuando: (1) v4complete produjo output comercialmente viable para Castilla Real, (2) los 6 niveles de éxito están superados, (3) la documentación está sincronizada, y (4) pre-commit pasa.
