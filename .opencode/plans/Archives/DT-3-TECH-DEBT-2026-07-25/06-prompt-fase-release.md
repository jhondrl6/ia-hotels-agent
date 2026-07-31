# FASE-RELEASE: Documentación + Version Bump v4.64.0

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAJENTE (delegate_task viable — solo YAML/MD editing + scripts de validación)
> **Complejidad**: BAJA
> **Iteraciones máx**: 60
> **Depende de**: FASE-3 ✅ (v4complete verificado)
> **Bloquea a**: — (fase final)

---

## Objetivo

Ejecutar el cascade de documentación post-implementación para el release v4.64.0:

1. Actualizar VERSION.yaml → 4.64.0
2. Actualizar CHANGELOG.md con entries de DT-3
3. Actualizar GUIA_TECNICA.md
4. Sincronizar versiones (sync_versions.py)
5. Crear git tag v4.64.0
6. Validación final (run_all_validations.py --quick)

---

## Contexto de Fases Anteriores

**FASE-0**: BUG-1 corregido — `_get_pipeline_path()` helper + 3 rutas flat → per-hotel.

**FASE-1**: BUG-2 + BUG-3 corregidos — G9 dual-list fix + status-based evaluation.

**FASE-2**: BUG-4 / P-04 — `AssetAlignmentMatrix` unificado reemplaza ProposalAssetMatrix + AlignmentReport.

**FASE-3**: v4complete Zi One verificado — delivery NO bloqueado, ZIP generado, bugs superados.

---

## Tareas

### T1: Version bump + sync

1. Actualizar `VERSION.yaml`: `version: "4.64.0"`, `release_date: "2026-07-25"`
2. Ejecutar `sync_versions.py` (sin args — NO usar `--bump`)
3. Verificar que 6 archivos se actualizaron

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

### T2: CHANGELOG + GUIA_TECNICA

1. Agregar entry `[4.64.0]` en CHANGELOG.md con:
   - BUG-1: Fix sistémico de rutas flat → per-hotel (3 archivos)
   - BUG-2: Fix G9 dual-list (BLOCKING_GATE_NAMES constante)
   - BUG-3: Fix G9 status-based evaluation (NO_BREACH ≠ FAIL)
   - BUG-4: Unificación ProposalAssetMatrix + AlignmentReport → AssetAlignmentMatrix
2. Agregar nota en GUIA_TECNICA.md sobre el nuevo helper `_get_pipeline_path()` y `AssetAlignmentMatrix`

### T3: Crear git tag

1. `git add` todos los archivos modificados
2. `git commit -m "release: v4.64.0 — DT-3 tech debt resolution (BUG-1, BUG-2, BUG-3, P-04 unification)"`
3. `git tag -a v4.64.0 -m "v4.64.0: DT-3 — systemic path fix, G9 status-based eval, AssetAlignmentMatrix unification"`
4. Verificar: `git log --oneline v4.64.0 -1` debe apuntar al commit de código (no al REGISTRY)

### T4: Validación final

1. Ejecutar pre-commit:
   ```bash
   ./venv/Scripts/python.exe scripts/version_consistency_checker.py
   ```
2. Ejecutar validación rápida:
   ```bash
   ./venv/Scripts/python.exe scripts/run_all_validations.py --quick
   ```
3. Verificar README.md post-release (line-by-line audit):
   - Test count: `pytest --collect-only -q | tail -1`
   - Module count: `find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l`
   - Gate classification actualizada (G9 ahora en blocking_gates)

---

## Criterios de Completitud

- [ ] VERSION.yaml: 4.64.0
- [ ] sync_versions.py ejecutado sin errores
- [ ] CHANGELOG.md: entry [4.64.0] con los 4 bugs resueltos
- [ ] GUIA_TECNICA.md: nota sobre _get_pipeline_path() y AssetAlignmentMatrix
- [ ] Git tag v4.64.0 creado (annotated)
- [ ] version_consistency_checker.py: PASS
- [ ] run_all_validations.py --quick: PASS (o fallos pre-existentes documentados)
- [ ] README.md line-by-line audit: counts actualizados

---

## Restricciones

- **NO modificar código fuente** — solo docs, version, changelog
- **NO usar `sync_versions.py --bump`** — el script no acepta ese flag; editar VERSION.yaml manualmente
- **NO crear tag antes del commit de código** — tag debe apuntar al último commit de código, no al REGISTRY
- **Unicode en codename**: Si el codename tiene `→`, usar `->` para evitar crash de sync_versions.py en Windows CP1252

---

## delegate_task Prompt (para subagente)

```
GOAL: Execute RELEASE phase for iah-cli v4.64.0 — documentation cascade and version bump.

CONTEXT:
Project: /mnt/c/Users/Jhond/Github/iah-cli
Target version: 4.64.0
Current version: 4.63.2
Plan: DT-3-TECH-DEBT-2026-07-25

Completed phases:
- FASE-0: BUG-1 fix — _get_pipeline_path() helper, 3 flat paths → per-hotel
- FASE-1: BUG-2 + BUG-3 fixes — G9 dual-list + status-based eval
- FASE-2: BUG-4 / P-04 — AssetAlignmentMatrix unification
- FASE-3: v4complete Zi One verified — delivery unblocked, bugs resolved

TASKS:
1. Edit VERSION.yaml: change version to "4.64.0", set release_date to today
2. Run sync_versions.py (no --bump flag — it doesn't exist)
3. Add [4.64.0] entry to CHANGELOG.md with 4 bugs resolved
4. Add GUIA_TECNICA.md note about _get_pipeline_path() and AssetAlignmentMatrix
5. Git add + commit + tag:
   git add -A
   git commit -m "release: v4.64.0 — DT-3 tech debt resolution"
   git tag -a v4.64.0 -m "v4.64.0: DT-3 — systemic path fix, G9 status eval, AssetAlignmentMatrix"
6. Run pre-commit: version_consistency_checker.py
7. Run quick validation: run_all_validations.py --quick
8. Audit README.md for stale numerical counts

RESTRICTIONS:
- Do NOT modify source code (only docs, VERSION.yaml, CHANGELOG)
- Do NOT use sync_versions.py --bump (doesn't exist)
- Tag MUST point to code commit, not REGISTRY update commit
- Avoid Unicode in codenames (use -> not →)
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-RELEASE --plan DT-3-TECH-DEBT-2026-07-25 --desc release_v4.64.0 --force-skip-docs --skip-reason GUIA_TECNICA_actualizada_manualmente_en_FASE-RELEASE"
```

---

## Fin del Plan

Tras FASE-RELEASE, completar `08-analisis-post-implementacion.md` con:
- Resumen de ejecución de las 6 sesiones
- Lecciones aprendidas
- Deuda técnica remanente (si aplica)
