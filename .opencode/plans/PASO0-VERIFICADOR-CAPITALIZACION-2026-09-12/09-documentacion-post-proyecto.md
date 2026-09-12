# 09 — Documentación post-proyecto (acumulativa)

> **Plan**: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 · Se rellena al cierre de cada fase.
> Backup de datos para el cierre documental; la fuente canónica de cada fase es su sección en
> `CHANGELOG.md` y `GUIA_TECNICA.md`.

## A. Módulos / componentes nuevos

| Componente | Ruta | Fase | Tests | Nota |
|------------|------|------|-------|------|
| Verificador de capitalización del Paso 0 | `scripts/validate_lesson_capitalization.py` | FASE-V2 | — | Herramienta de validación, no módulo de producción |
| Suite del verificador | `tests/test_validate_lesson_capitalization.py` | FASE-V2 | — | Una familia por check C1–C8 + tri-estado R2.9 |

## B. Funcionalidades nuevas

- Check `[7/7]` del hook versionado `scripts/git_hooks/pre-commit`.
- Check `[9/9]` de `run_all_validations.py --quick` («Lesson Capitalization»).

## D. Métricas acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Funciones de test (canónico `grep -rE "^\s*def test_" tests --include=*.py`) | `—` pre / `—` post | V2 |
| Cobertura poblacional del verificador nuevo | `—` | V2 |
| Checks del hook antes / después | `6` → `—` | V2 |
| Checks de `--quick` antes / después | `8` → `—` | V2 |

## E. Archivos afiliados actualizados

| Archivo | Motivo | Fase |
|---------|--------|------|
| `.agents/workflows/templates/lecciones-capitalizadas-template.md` | §4 deja de declarar que el verificador no existe (L-NC10) | V3 |
| `.agents/workflows/phased_project_executor.md` | Referencias normativas al `[6/6]` y descripción del Paso 0 | V3 |
| `CHANGELOG.md` | subsection de validación-only (sin bump) | V3 |
| `.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md` | Ítem (i) de §Deuda cerrado con fecha | V3 |
