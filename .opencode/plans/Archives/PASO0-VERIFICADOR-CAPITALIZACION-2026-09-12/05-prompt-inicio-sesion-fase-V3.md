# 05 — Prompt de inicio de sesión: FASE-V3 (cierre documental)

> Pega esto en una sesión nueva. Plan: `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`.
> Precedente: FASE-V2 cerró el verificador, sus tests y el cableado `[7/7]` + `[9/9]`.

## Objetivo

Dejar que la documentación del repo diga la verdad sobre el verificador que ya existe, cerrar la deuda (i)
del plan predecesor y archivar este plan en el orden de R2.10. **Sin bump de versión** (decisión Q5).

## Lecciones capitalizadas que aplican a esta fase (copiadas de `00-lecciones-capitalizadas.md` §2)

| ID | Efecto en esta fase |
|----|---------------------|
| L-NC10 | El template y el executor declaran «no existe verificador»: eso ya es falso y hay que actualizarlo en el mismo plan que lo crea |
| L-R.4 | El límite de pertinencia se re-declara en §4 del `00-` ahora que el verificador existe (el check C6 lo exige) |
| L-V.2 | Antes de editar el executor, **re-leer** cuáles de sus menciones al `[6/6]` son normativas (5) y cuáles son medición histórica (4): las históricas no se reescriben |
| DA-V5 | La deuda (i) del predecesor se cierra con fecha y resultado en su propio checklist; nada se reasigna «a la fase que sigue» |
| R2.10 | Orden del cierre: write-back → índice → `git mv` → índice otra vez, con el paso 3b en el mismo commit |
| L-I1 | Las lecciones de V2 y V3 se escriben aquí con su formato completo, no se dejan en el aire |
| L-VUP-9 | Los comandos que se citen en template/executor se copian del `--help` real del script nuevo |

## Tareas

1. `.agents/workflows/templates/lecciones-capitalizadas-template.md`: la casilla «este documento **no tiene
   verificador mecánico** (hasta que exista)» pasa a nombrar `validate_lesson_capitalization.py`, y el
   checklist del orquestador se marca como verificado por C1–C8. Añadir nota de versión al changelog del
   template.
2. `.agents/workflows/phased_project_executor.md`: actualizar las **5 referencias normativas** al `[6/6]`
   (`[7/7]`, con nota datada de la renumeración), describir el Paso 0 con su verificador en §0 y en el
   gate §2.5, y subir la cabecera de reglas a la versión que refleje el cambio. **Conservar literales**
   las 4 menciones históricas de medición.
3. `00-lecciones-capitalizadas.md` de este plan: actualizar §4 (el verificador existe, nombra su límite) y
   las filas de §2 que V2 o V3 hayan dejado obsoletas. **Comprobar que el propio C6 pasa.**
4. Cierre de la deuda (i) en `.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md`
   con fecha, resultado y ACs certificados (AC-C2).
5. `CHANGELOG.md`: subsection de validación-only bajo la versión vigente; `VERSION.yaml` intacto (AC-A5).
6. `10-analisis-post-implementacion.md`: §1, §2 (lecciones nuevas con formato completo), §3 matriz de ACs,
   §4 métricas, §6 decisiones. Solo después, la cabecera de cierre.
7. Cierre en orden: `log_phase_completion.py --fase FASE-V3` → `validate_qmind_writeback.py --upload <PLAN>`
   → `build_lesson_index.py` → `git mv` a `Archives/` → `build_lesson_index.py` (paso 3b) →
   `validate_opencode_refs.py --fix` (diff revisado a mano) → `--quick` TOTAL PASS → commit único.

## Criterios de completitud

- AC-C1: el `git diff` muestra template y executor actualizados **y** las mediciones históricas intactas.
- AC-C2: la deuda (i) del predecesor figura cerrada con fecha y dueño ejecutado.
- AC-A5: `git diff VERSION.yaml` vacío.
- El `00-` de este plan pasa su propio verificador después del archivado (`--cutoff` explícito si hace falta).
- `run_all_validations.py --quick` TOTAL PASS post-archivado.

## Restricciones

- **Presupuesto**: sin instrumento canónico en esta máquina (D-V2.1); auto-reporte declarado, corte en el
  commit de cierre.
- Prohibido bump de versión, `git push` y `--no-verify`.
- Prohibido reescribir mediciones históricas del executor para que «cuadren» con la numeración nueva.
- El `--fix` de `validate_opencode_refs.py` se revisa a mano en el diff: ya destruyó comandos de planes
  archivados (ítem de deuda medido en el predecesor).
