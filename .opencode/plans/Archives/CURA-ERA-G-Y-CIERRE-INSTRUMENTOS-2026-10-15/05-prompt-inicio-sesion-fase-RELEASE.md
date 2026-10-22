# FASE-RELEASE-4.81.1 — Cierre, documentación oficial y archivado del plan

**ID**: FASE-RELEASE-4.81.1 (plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15)
**Objetivo**: cerrar el plan: version bump 4.81.0 → **4.81.1**, sync, CHANGELOG con las **tres curas**, nota de ronda en `docs/cobertura-historia.md`, GUIA_TECNICA, validaciones finales, write-back QMind y archivado en `Archives/` con el orden R2.5/R2.10. **NO modifica código fuente. NO ejecuta v4complete.**
**Dependencias**: TODAS las fases previas ✅ (A, B, C) — si alguna falta, abortar.
**Duración estimada**: 1 sesión.
**Complejidad**: BAJA — solo YAML/MD y scripts.
**Skill**: `.agents/workflows/phased_project_executor.md` §7 (workflow canónico).

## Contexto

El plan cierra dos cosas en una sola unidad de versión (DEC-1 del maestro): el **cierre documental** de la tanda de instrumentos del 2026-10-15 (segunda vía de gobernación + reemplazo por documento; commits `2e048e6` y `1f95e84`, ya empujados **sin** entrada de versión) y la **cura de la deuda era-G** que mantenía el modo completo en rojo. El bump es **patch** (4.81.1): cambia el comportamiento observable de instrumentos (el veredicto de frescura de los CONTEXT y la semántica de reemplazo del write-back), sin cambios de producto. La convención `FASE-RELEASE-4.81.1` activa el Version Sync Gate.

**La nota de ronda que este cierre debe pagar**: los 9 tests nuevos de la tanda de instrumentos (5 de `tests/test_verify_qmind_context_freshness.py` y 4 de `tests/test_validate_qmind_writeback_escritura.py`) y los que haya añadido FASE-C — su nota va a `docs/cobertura-historia.md` con la fila y la cifra de cabecera de `AGENTS.md` §Cobertura actualizadas **desde el comando canónico**, no transcritas.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación / FASE-A / FASE-B / FASE-C | ✅ Todas completadas (verificar en `dependencias-fases.md` antes de empezar; si alguna no está ✅, ABORTAR) |

### Base Técnica Disponible

- `09-documentacion-post-proyecto.md` (fuente de los datos por fase — CHANGELOG y GUIA_TECNICA se generan desde aquí).
- `10-analisis-post-implementacion.md` (matriz, lecciones, seguimientos con dueño — completo **antes** del write-back).
- `VERSION.yaml` (fuente única) + `scripts/sync_config.yaml` (archivos que sincroniza; `REGISTRY.md` no entra — su fecha la escribe el registro de la fase).
- Evidencia completa en `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/`.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| D-V2.1 | El instrumento de R2.1 no alcanza el transcript | E8b y el cierre declaran sus cifras con el comando que las imprime; ninguna se transcribe a mano |
| L-V.2 | Se certifica re-leyendo artefactos | El cierre verifica `--strict` y el `[CONTADOR]` leyendo la corrida, no la nota de FASE-C |

## Tareas (E1-E8b del executor)

- **E1 Diagnóstico**: `version_consistency_checker.py` sin errores críticos.
- **E2 Sync**: `python scripts/sync_versions.py` (4.81.0 → 4.81.1 en los archivos de `sync_config.yaml`; `REGISTRY.md` no entra).
- **E3 CHANGELOG**: entrada `## [4.81.1] - Instrumentos de QMind: la segunda vía, el reemplazo por documento y la deuda era-G — <fecha>` con Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests (referencia a evidence, sin re-transcribir cifras). Debe nombrar las **tres** curas y los shas de la tanda empujada (`2e048e6`, `1f95e84`).
- **E4 GUIA_TECNICA**: nota «Notas de Cambios v4.81.1» (módulos afectados: `scripts/verify_qmind_context_freshness.py`, `scripts/validate_qmind_writeback.py` y lo que FASE-C haya tocado; problema/solución; compatibilidad: el registro schema 1.1 no cambia de forma salvo que FASE-C lo haya declarado).
- **E5 Cobertura**: nota de ronda en `docs/cobertura-historia.md` (formato de las rondas existentes) + las dos cifras de `AGENTS.md` §Cobertura que la ronda mueve, **medidas con el comando canónico** (`grep -rE "^\s*def test_" tests --include=*.py | wc -l` y sus variantes por módulo) y contrastadas contra `git grep -c -E "^\s*def test_" HEAD -- tests` en el árbol del commit.
- **E6 SYSTEM_STATUS**: `python scripts/doctor.py --status`.
- **E7 DOMAIN_PRIMER**: en RELEASE se **verifica** (`python scripts/doctor.py --context`), no se regenera (eso lo hizo FASE-C por ser de implementación).
- **E8 Symlink + validación final**: `ls -la .agent/workflows` intacto; `run_all_validations.py --quick` verde; modo completo con `PYTHONUTF8=1` corrido y su resultado publicado (los rojos preexistentes se declaran, no se atribuyen a este plan); `git diff --stat`.

## Cierre del plan (R2.5 + R2.10 — orden fijo, sin permutar)

```bash
python scripts/validate_qmind_writeback.py --upload CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15   # 1. con el plan aún en raíz
python scripts/build_lesson_index.py                                                              # 2. lecciones consultables
git mv .opencode/plans/Archives/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15 .opencode/plans/Archives/      # 3. archivar al final
python scripts/build_lesson_index.py                                                              # 3b. índice congela la ruta nueva
python scripts/validate_opencode_refs.py --fix
python scripts/validate_plan_citations.py --update-baseline
python scripts/run_all_validations.py --quick                                                     # verde
```

El `10-analisis-post-implementacion.md` debe estar completo ANTES del write-back. El write-back publica el `10-analisis` del plan y su verificación `--strict` confirma la ingesta (el censo de `N/N` lo imprime la corrida; no se fija aquí).

## Commits (posterior y separado — requiere autorización explícita del Operador)

Ningún `git commit` sin autorización escrita del Operador en la sesión, y **siempre con pathspec** (L-SECF.2: `git commit -- <ruta>` no toma untracked). Si el Operador autoriza: commit del cierre (RELEASE + archivado, derivados junto a su generador, índice regenerado en el mismo commit) y **el push va después de la L3**, que cubre el rango de commits nuevos.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-RELEASE-4.81.1 ✅; plan CERRADO.
2. README del plan: estado final.
3. `09` / `10-analisis`: checklist de cierre completo (el 10-analisis antes del write-back).
4. Registro de release (auto-detecta `--release` por el nombre de la fase):
   ```bash
   python scripts/log_phase_completion.py \
       --fase FASE-RELEASE-4.81.1 --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Release 4.81.1 - instrumentos QMind: segunda via, reemplazo por documento y era-G" \
       --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md,docs/cobertura-historia.md" \
       --check-manual-docs
   ```
5. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

- [ ] Todas las fases previas ✅ (verificado, no asumido)
- [ ] E1-E8 completos; `--quick` verde; modo completo corrido con `PYTHONUTF8=1` y su resultado publicado
- [ ] AC7 legible: 4.81.1 sincronizada, CHANGELOG con las tres curas, nota de ronda con sus cifras medidas, DOMAIN_PRIMER verificado
- [ ] Write-back `--upload` retorna 0 y `--strict` confirma la ingesta; orden write-back → índice → `git mv` → índice respetado
- [ ] `log_phase_completion.py` ejecutado; cinco cortes declarados; commit solo con autorización + pathspec

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls; unidad: auto-reporte en `tool calls`; corte: **hasta listo para revisión**.
- NO código fuente, NO `v4complete`, NO `ROADMAP.md`.
- El plan termina en `Archives/` dentro del cierre (R2.5).
- No tocar el `10-analisis` de CURA (congelado, DEC-2) ni los dos CONTEXT publicados (congelados, DEC-3).

## Prompt de Ejecución

```
Actúa como agente de cierre (RELEASE) del plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15.

Ejecuta únicamente FASE-RELEASE-4.81.1 del plan .opencode/plans/Archives/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/
Lee 01-plan-maestro.md (§4 y §5), 00-lecciones-capitalizadas.md (§4), dependencias-fases.md, 09-documentacion-post-proyecto.md (fuente de datos), 10-analisis-post-implementacion.md y el workflow canónico.

OBJETIVO: release 4.81.1 con las tres curas documentadas, nota de ronda, validaciones finales, write-back QMind y archivado del plan con el orden R2.5/R2.10.

CONTEXTO:
- Fases previas completadas: Preparación, FASE-A, FASE-B y FASE-C (verificar en dependencias-fases.md; si falta alguna, abortar)
- Sin código fuente, sin v4complete, sin ROADMAP
- Commits solo con autorización escrita del operador y siempre con pathspec; el push va después de la L3

TAREAS:
1. E1-E8: diagnóstico, sync 4.81.1, CHANGELOG con las tres curas, nota de ronda de cobertura con sus cifras medidas, GUIA_TECNICA, SYSTEM_STATUS, DOMAIN_PRIMER --context, symlink y validaciones (quick + modo completo con PYTHONUTF8=1)
2. Cierre R2.5/R2.10: write-back --upload → build_lesson_index → git mv a Archives/ → build_lesson_index → refs --fix → citas --update-baseline → quick verde
3. log_phase_completion FASE-RELEASE-4.81.1

CRITERIOS:
- 4.81.1 sincronizada; quick verde; plan archivado con write-back previo; checklist de cierre del 10-analisis completo

VALIDACIONES:
- version_consistency_checker.py; run_all_validations.py --quick; validate_qmind_writeback.py --strict
```
