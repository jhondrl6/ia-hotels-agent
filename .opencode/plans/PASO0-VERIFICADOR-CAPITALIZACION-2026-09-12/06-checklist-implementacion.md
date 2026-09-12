# 06 — Checklist de Implementación: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

> **Regla**: una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Iteraciones (L-R.1)**: la celda es bloqueante del ✅ — `ids` + `tool_use`, corte en el commit de código.
> **Este plan es el primer hijo del Paso 0 en la concepción**: su `00-` se escribió antes del maestro.

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones (ids + tool_use, corte = commit) | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 0 | Paso 0 (`00-lecciones-capitalizadas.md`) | ✅ Completada | 2026-09-12 | 2026-09-12 | auto-reporte **sin instrumento**: 10 consultas Q1–Q10; `tool_use` no comparable (ver Deuda D-V2.1) | Primera vez que el artefacto precede al diseño. 18 lecciones con dueño, 6 descartes, 5 hallazgos sin efecto |
| 1 | FASE-V1 — decisión y contrato | ✅ Completada | 2026-09-12 | 2026-09-12 | auto-reporte **sin instrumento**: unidad = peticiones al modelo con tool calls, conteo a mano no auditable; **no comparable** con las fases medidas por `measure_iterations.py` (D-V2.1) | Q1–Q5 decididas con medición; contrato C0–C8 fijado |
| 2 | FASE-V2 — verificador + tests + cableado | ✅ Completada | 2026-09-12 | 2026-09-12 | auto-reporte **sin instrumento** (D-V2.1): unidad = tool calls del orquestador, **no comparable** con `measure_iterations.py` | Script C0–C8, 29 tests, NR7 13/13, `[7/7]` con bloqueo ejecutado, `--quick` 9/9, resta R2.7 29 = 29 |
| 3 | FASE-V3 — cierre documental y archivado | ⬜ Pendiente | — | — | — | Sin bump de versión (Q5); orden R2.10 en el cierre |

---

## FASE-V1 — Decisión y contrato

- [x] `00-lecciones-capitalizadas.md` escrito **antes** del maestro, con ≥1 consulta al corpus completo y ≥3 descartes
- [x] Q1 (alcance) decidida con la población medida: 0 archivados en alcance, 6 exentos sin fecha, cobertura 3,8 %
- [x] Q2 (qué verifica) decidida: C0–C8 con forma mecánica y estado de no-evaluación por check
- [x] Q3 (dónde vive) decidida contra el dato de enforcement: `diff` del hook + la decisión registrada del 2026-08-29
- [x] Las 7 referencias al `[6/6]` clasificadas en normativas (5, se actualizan) e históricas (4, se conservan)
- [x] Q4 (límite declarado) fijada en los tres sitios exigidos
- [x] Q5 (cierre sin bump) fijada; `VERSION.yaml` intacto
- [x] AC-A1…AC-A5 con artefacto **y clave legible** (R2.4) en `01-plan-maestro.md` §6
- [x] Umbrales verificados contra el único artefacto real del repo (18/18 atribuciones, 5 dueños) — L-D3
- [x] `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md` creados (executor §4)
- [x] Prompts de FASE-V2 y FASE-V3 creados, con las lecciones de §2 copiadas por ID
- [x] Gate §2.5 del executor superado: el `00-` existe, está lleno y su §2 nombra ACs reales del maestro
- [x] `log_phase_completion.py --fase FASE-V1` ejecutado (SIN `--release`)
- [x] `run_all_validations.py --quick` TOTAL PASS
- [x] NO modificó código de producción
- [x] Commit de cierre de fase

## FASE-V2 — Verificador, tests y cableado

- [x] `scripts/validate_lesson_capitalization.py` con C0–C8, tri-estado (`SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO`) y **sin** `--fix` (AC-B1)
- [x] `--help` del script leído antes de citar cualquier comando suyo en docs o prompts (L-VUP-9): `--plans-dir`, `--context-dir`, `--cutoff`, `--quiet`
- [x] `tests/test_validate_lesson_capitalization.py`: **29** funciones, ≥1 test por detección nombrado por su causa y un test por estado de R2.9 (AC-B2)
- [x] Los tests usan el archivo real del repo **y** fixtures en `tmp_path` (L-B1), con un control positivo del artefacto conforme para que ningún rojo sea culpa del fixture
- [x] **NR7 por detección** (AC-B3): **13** guards revertidos sobre el archivo versionado, cada uno con su rojo y su verde en `evidence/FASE-V2/nr7-<id>-{rojo,verde}.txt` (runner: `run_nr7_capitalizacion.py`)
- [x] El mutation check reveló dos tests que no observaban su rama (C4a, C7a): ahora anclan el mensaje de la violación, y el runner **se niega** si una ancla desaparece (dos veces lo hizo, en vez de simular)
- [x] Cableado `[7/7]` en `scripts/git_hooks/pre-commit` (los seis anteriores renumerados a `/7`) y check `[9/9]` en `run_all_validations.py --quick` (AC-B4); hook reinstalado con `install_git_hooks.py`
- [x] El bloqueo se **ejecutó**, no se afirmó: `bash scripts/git_hooks/pre-commit` sobre un árbol con un plan en alcance sin `00-` devolvió `exit_code_del_hook=1` → `evidence/FASE-V2/hook-bloquea.txt` (S-H17)
- [x] La salida del script publica su población (AC-B5): línea `cobertura:` con los conteos de C0 y los nombres de los exentos
- [x] NR1/R2.7: par pre/post con la combinación exacta declarada (`--ignore` / `--exclude` del archivo nuevo), resta **29 = 29** en las dos bases, flaky `test_function_default_flags` declarado → `evidence/FASE-V2/baseline-pre-post.md` (L-T4B.5, L-VUP-1)
- [x] R2.2: 0 citas `archivo:123` en los archivos nuevos (check `[8/9]` de `--quick`: 743 históricas, 0 nuevas, 0 crecimientos)
- [x] Rojo **heredado y no declarado** encontrado y arreglado: `test_registrado_como_check_5_en_el_hook` asertaba `[5/5]` desde que el hook tiene seis checks (`4a066e1`); la posición 5 sigue siendo el contrato y el denominador pasa a `[5/7]` con nota
- [x] Dos tests de coherencia de numeración (hook y `--quick`) para que el próximo cambio de denominador no pueda repetir el rojo en silencio
- [x] `run_all_validations.py --quick` TOTAL PASS (9/9) y suite completa: 3 rojos, exactamente los ajenos ya publicados
- [x] `log_phase_completion.py --fase FASE-V2` ejecutado (SIN `--release`)
- [x] Iteraciones declaradas en la tabla de arriba (unidad usada y no comparabilidad escritas)
- [x] Commit de cierre de fase

## FASE-V3 — Cierre documental y archivado

- [ ] Template `.agents/workflows/templates/lecciones-capitalizadas-template.md`: la línea «no tiene verificador mecánico (hasta que exista)» pasa a nombrar `validate_lesson_capitalization.py` (AC-C1, L-NC10)
- [ ] Executor `.agents/workflows/phased_project_executor.md`: referencias **normativas** al `[6/6]` actualizadas y el Paso 0 descrito con su verificador; las **4 mediciones históricas** conservadas literalmente
- [ ] `00-lecciones-capitalizadas.md` §4 actualizado: el verificador ya existe y nombra su límite (C6 lo verifica)
- [ ] `evidence/FASE-V1/decision-verificador.md` ítem (i) de §Deuda del predecesor cerrado con fecha y resultado en su `06-checklist-implementacion.md` (AC-C2)
- [ ] `CHANGELOG.md` con subsection de validación-only; `VERSION.yaml` **sin tocar** (AC-A5)
- [ ] `docs/contributing/validation.md` y `AGENTS.md` si mencionan el conteo de checks
- [ ] ACs certificados contra artefacto real, con NR7 cumplido (patrón VERIFY)
- [ ] `python scripts/log_phase_completion.py --fase FASE-V3`
- [ ] Write-back **antes** de archivar: `python scripts/validate_qmind_writeback.py --upload <PLAN>` (R2.10)
- [ ] `python scripts/build_lesson_index.py` → `git mv` a `Archives/` → `build_lesson_index.py` otra vez (paso 3b)
- [ ] `run_all_validations.py --quick` TOTAL PASS post-archivado
- [ ] `git diff` del `validate_opencode_refs.py --fix` revisado a mano (no reescribió bloques de código)
- [ ] Iteraciones medidas y escritas

## Deuda que genera este plan (dueño explícito, nada se reasigna por inercia)

**D-V2.1 — El instrumento canónico de R2.1 no corre bajo el cliente actual**

- [ ] `evidence/FASE-D/measure_iterations.py` pide la ruta de un transcript `.jsonl` de sesión. Medido en
  esta sesión: ese transcript no vive dentro del workspace y el intento de localizarlo fuera fue bloqueado
  por la política de permisos, así que las fases de este plan se auto-reportan en una unidad **declarada y
  no comparable** (el fallback que la propia R2.1 autoriza, no una excepción a ella). Consecuencia: la
  cabecera del executor promete «Iteraciones medidas con `evidence/FASE-D/measure_iterations.py`» y eso hoy
  solo es cierto donde el transcript es alcanzable. **Dueño**: quien redacte la siguiente versión del
  executor — necesita una fuente de medición portable (o retirar la promesa de la cabecera).
- [ ] **Promoción a regla R2.11** del executor («ningún plan se concibe sin `00-` verificado»): requiere
  texto de medición propia y no es el encargo de este plan. Dueño: quien cierre la §Deuda del
  `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`.
- [ ] **§4 no cuadra con la tabla**: verificador de conteos declarados (el `00-` del predecesor dice 19
  lecciones y su §2 tiene 18 filas, medido). Dueño: FASE-P1 del predecesor, que es el plan que lo publica.
- [ ] **Prompts de fase vs §2 del `00-`**: el executor exige que cada prompt copie las filas pertinentes;
  ningún check lo comprueba (límite §4.3 del maestro). Dueño: futuro tramo de enforcement del executor.
- [ ] **`.pre-commit-config.yaml` inerte**: si se activara la Opción 2 (decisión del 2026-08-29 pendiente),
  el `[7/7]` debe migrar o duplicarse allí. Dueño: ese CONTEXT de decisión.
