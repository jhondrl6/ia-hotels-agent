# FASE-RELEASE-4.81.0 — Cierre, documentación oficial y archivado del plan

**ID**: FASE-RELEASE-4.81.0 (plan CURA-COSTURA-TRIBUNAL-2026-10-11)
**Objetivo**: cerrar el plan: version bump 4.80.0 → **4.81.0**, sync, CHANGELOG, GUIA_TECNICA, validaciones finales, write-back QMind y archivado en `Archives/` con el orden R2.5/R2.10. **NO modifica código fuente. NO ejecuta v4complete.**
**Dependencias**: TODAS las fases previas ✅ (A, B, C, E2E, VERIFY) — si alguna falta, abortar.
**Duración estimada**: 1 sesión.
**Complejidad**: BAJA — solo YAML/MD y scripts; delegable a subagente.
**Skill**: `.agents/workflows/phased_project_executor.md` §7 (workflow canónico).

## Contexto

El plan cura la costura de juicio semántico del Tribunal (contrato de cuatro estados, cache versionada, recibo, revisores honestos, precedencia única, acta verdadera, reglas HARD visibles) y la valida con el run único de Don Alfonso. La versión sube porque hay cambios de comportamiento en gates y Tribunal (minor). La convención `FASE-RELEASE-4.81.0` activa el Version Sync Gate.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación / FASE-A / FASE-B / FASE-C / FASE-E2E / FASE-VERIFY | ✅ Todas completadas (verificar en `dependencias-fases.md` antes de empezar; si alguna no está ✅, ABORTAR) |

### Base Técnica Disponible

- `09-documentacion-post-proyecto.md` (fuente de los datos por fase — CHANGELOG y GUIA_TECNICA se generan desde aquí).
- `10-analisis-post-implementacion.md` (matriz completa, lecciones, seguimientos con dueño).
- `VERSION.yaml` (fuente única de versión) + `scripts/sync_config.yaml` (los archivos que sincroniza).
- Evidencia completa en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/`.

## Tareas (E1-E8 del executor)

- **E1 Diagnóstico**: `version_consistency_checker.py` + `main.py --doctor` sin errores críticos.
- **E2 Sync**: `sync_versions.py` (4.81.0 → los archivos de `sync_config.yaml`; REGISTRY no entra — su fecha la escribe el registro de la fase).
- **E3 CHANGELOG**: entrada `## [4.81.0] - Cura de la costura de juicio semántico del Tribunal — <fecha>` con Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests (referencia a evidence, sin re-transcribir cifras).
- **E4 GUIA_TECNICA**: nota «Notas de Cambios v4.81.0» (módulos afectados, problema/solución, backwards compatibility: la API checked reemplaza al wrapper; los consumidores internos son los únicos llamadores).
- **E5 Skills/Workflows**: sin huérfanos (`ls .agents/workflows/` vs README).
- **E6 SYSTEM_STATUS**: `doctor.py --status`.
- **E7 DOMAIN_PRIMER**: en RELEASE se **verifica** (`doctor.py --context`), no se regenera (eso ya se hizo por fase).
- **E8 Symlink + validación final**: `ls -la .agent/workflows` intacto; `run_all_validations.py --quick` verde; modo completo con `PYTHONUTF8=1` (el denominador lo imprime la corrida); `git diff --stat`.
- **E8b README audit**: test count y module count desde sus comandos; cada cifra del README desde su fuente.

## Cierre del plan (R2.5 + R2.10 — orden fijo, sin permutar)

```bash
python scripts/validate_qmind_writeback.py --upload CURA-COSTURA-TRIBUNAL-2026-10-11   # 1. con el plan aún en raíz
python scripts/build_lesson_index.py                                                    # 2. lecciones consultables
git mv .opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11 .opencode/plans/Archives/       # 3. archivar al final
python scripts/build_lesson_index.py                                                    # 3b. índice congela la ruta nueva
python scripts/validate_opencode_refs.py --fix
python scripts/validate_plan_citations.py --update-baseline
python scripts/run_all_validations.py --quick                                            # verde
```

El `10-analisis-post-implementacion.md` debe estar completo (matriz, lecciones, seguimientos, decisiones, checklist de cierre) ANTES del write-back: el script sube el 10-analisis al notebook `iah-cli-lecciones` y la verificación `--strict` confirma N/N archivados ingeridos.

## Commits (posterior y separado — requiere autorización explícita del operador)

Ningún `git commit` sin autorización escrita del operador en la sesión, y **siempre con pathspec** (el índice trae trabajo ajeno staged: 13 archivos de REFACTOR-WHATSAPP que no se tocan ni se despegan). Si el operador autoriza: commit único del cierre (RELEASE + archivado, derivados junto a su generador, índice regenerado en el mismo commit), verificando antes qué entra con `git status`.

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-RELEASE-4.81.0 ✅; plan CERRADO.
2. README del plan: estado final.
3. `09-documentacion-post-proyecto.md` / `10-analisis-post-implementacion.md`: checklist de cierre completo (el 10-analisis antes del write-back).
4. Registro de release (auto-detecta `--release` por el nombre de la fase):
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-RELEASE-4.81.0 --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> \
       --desc "Release 4.81.0 - cura de la costura de juicio semantico del tribunal" \
       --archivos-mod "VERSION.yaml,CHANGELOG.md,docs/GUIA_TECNICA.md" \
       --check-manual-docs
   ```
5. Pregunta de aporte durable de cualquier `CONTEXT-*.md` escrito en la sesión.

## Criterios de Completitud (CHECKLIST)

- [ ] Todas las fases previas ✅ (verificado, no asumido)
- [ ] E1-E8b completos; `--quick` verde; modo completo corrido con `PYTHONUTF8=1` y su resultado publicado
- [ ] CHANGELOG 4.81.0 con formato CONTRIBUTING; GUIA_TECNICA con nota técnica
- [ ] Write-back `--upload` retorna 0 y `--strict` confirma la ingesta; orden write-back → índice → `git mv` → índice respetado
- [ ] `log_phase_completion.py` ejecutado; cinco cortes declarados; commit solo con autorización + pathspec

## Restricciones

- **Presupuesto (R2.1)**: ~40 tool calls; unidad `tool calls`; corte: hasta listo para revisión.
- NO código fuente, NO `v4complete`, NO `ROADMAP.md`.
- El plan termina en `Archives/` dentro del cierre (R2.5) — archivarlo después sería el reproceso que la regla elimina.
- **Delegable a subagente** (TIP del executor: solo edita YAML/MD y corre scripts) — si el operador o la sesión lo prefieren directo, también es válido; el write-back y el archivado son pasos con orden fijo que el delegatario debe seguir literalmente.

## Prompt de Ejecución

```
Actúa como agente de cierre (RELEASE) del plan CURA-COSTURA-TRIBUNAL-2026-10-11.

Ejecuta únicamente FASE-RELEASE-4.81.0 del plan .opencode/plans/Archives/CURA-COSTURA-TRIBUNAL-2026-10-11/
Lee 01-plan-maestro.md (§4 y §5), 00-lecciones-capitalizadas.md (§4), dependencias-fases.md, 09-documentacion-post-proyecto.md (fuente de datos), 10-analisis-post-implementacion.md y el workflow canónico.

OBJETIVO: Release 4.81.0 con documentación oficial, validaciones finales, write-back QMind y archivado del plan en Archives/ con el orden R2.5/R2.10.

CONTEXTO:
- Fases previas completadas: Preparación, A, B, C, E2E, VERIFY (verificar en dependencias-fases.md; si falta alguna, abortar)
- Sin código fuente, sin v4complete, sin ROADMAP
- Commits solo con autorización escrita del operador y siempre con pathspec

TAREAS:
1. E1-E8b: diagnóstico, sync 4.81.0, CHANGELOG, GUIA_TECNICA, skills, SYSTEM_STATUS, DOMAIN_PRIMER --context, symlink + validaciones (quick + modo completo con PYTHONUTF8=1), README audit
2. Cierre R2.5/R2.10: write-back --upload → build_lesson_index → git mv a Archives/ → build_lesson_index → refs --fix → citas --update-baseline → quick verde
3. log_phase_completion FASE-RELEASE-4.81.0

CRITERIOS:
- 4.81.0 sincronizada; quick verde; plan archivado con write-back previo; checklist de cierre del 10-analisis completo

VALIDACIONES:
- version_consistency_checker.py; run_all_validations.py --quick; validate_qmind_writeback.py --strict
```
