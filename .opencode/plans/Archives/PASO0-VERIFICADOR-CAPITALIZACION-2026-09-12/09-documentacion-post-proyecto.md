# 09 — Documentación post-proyecto (acumulativa)

> **Plan**: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 · Se rellena al cierre de cada fase.
> Backup de datos para el cierre documental; la fuente canónica de cada fase es su sección en
> `CHANGELOG.md` y `GUIA_TECNICA.md`.

## A. Módulos / componentes nuevos

| Componente | Ruta | Fase | Tests | Nota |
|------------|------|------|-------|------|
| Verificador de capitalización del Paso 0 | `scripts/validate_lesson_capitalization.py` | FASE-V2 | 29 | Herramienta de validación, no módulo de producción. Checks C0–C8, tres estados, sin `--fix` |
| Suite del verificador | `tests/test_validate_lesson_capitalization.py` | FASE-V2 | — | Una familia por detección + los tres estados de R2.9 + corrida contra el árbol real |
| Runner de mutation checks | `evidence/FASE-V2/run_nr7_capitalizacion.py` | FASE-V2 | — | 13 detecciones revertidas sobre el archivo versionado, con sus dos salidas |

## B. Funcionalidades nuevas

- Check `[7/7]` del hook versionado `scripts/git_hooks/pre-commit` (los seis anteriores renumerados a `/7`).
- Check `[9/9]` «Lesson Capitalization» de `run_all_validations.py --quick`; el modo completo pasa a `[10/12]`–`[13/13]`.

## D. Métricas acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Funciones de test (canónico `grep -rE "^\s*def test_" tests --include=*.py`) | `4.079` pre / `4.108` post (+29) | V2 |
| Cobertura poblacional del verificador nuevo | `1` plan en alcance de `27` directorios | V2 |
| Checks del hook antes / después | `6` → `7` | V2 |
| Checks de `--quick` antes / después | `8` → `9` | V2 |
| Detecciones con NR7 (rojo + verde) | `13/13` | V2 |

## E. Archivos afiliados actualizados

| Archivo | Motivo | Fase |
|---------|--------|------|
| `scripts/git_hooks/pre-commit` | `[7/7]` nuevo y renumeración | V2 |
| `scripts/run_all_validations.py` | `_check_lesson_capitalization()` y renumeración | V2 |
| `.opencode/LECCIONES-INDEX.md` y `lecciones_index.json` | regenerados en cada commit que toca `plans/` (R2.10) | V1, V2 |
| `docs/contributing/REGISTRY.md` | registro de FASE-V1 y FASE-V2 | V1, V2 |
| `.agents/workflows/templates/lecciones-capitalizadas-template.md` | §4 deja de declarar que el verificador no existe (L-NC10) | V3 |
| `.agents/workflows/phased_project_executor.md` | Referencias normativas al `[6/6]` y descripción del Paso 0 | V3 |
| `CHANGELOG.md` | subsection de validación-only (sin bump) | V3 |
| `.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md` | Ítem (i) de §Deuda cerrado con fecha | V3 |
