# 05 — Prompt de inicio de sesión: FASE-V2

> Pega esto en una sesión nueva. Plan: `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`.
> Lee antes `01-plan-maestro.md` §3 (contrato C0–C8) y §6 (ACs), y `evidence/FASE-V1/decision-verificador.md`.

## Objetivo

Implementar `scripts/validate_lesson_capitalization.py` con sus tests, cerrar el **NR7 por check** y
cablearlo en los dos puntos decididos en Q3. **No** tocar código de producción del pipeline.

## Contexto de la fase anterior (V1, cerrada 2026-09-12)

- Alcance: planes cuyo nombre lleva fecha `≥ 2026-09-12` y que no viven bajo `Archives/`; los exentos se
  listan en la salida. Sin fecha parseable ⇒ exento y reportado.
- Contrato: C0 (población) … C8 (diversidad de dueños), cada uno con su estado de no-evaluación
  (`SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO`).
- El verificador calcula el índice con `build_lesson_index.build()` **en memoria** (0,30 s medidos), no lee
  `.opencode/lecciones_index.json`.
- Cableado elegido: `[7/7]` del hook versionado `scripts/git_hooks/pre-commit` **y** check `[9/9]` de
  `run_all_validations.py --quick`.

## Lecciones capitalizadas que aplican a esta fase (copiadas de `00-lecciones-capitalizadas.md` §2)

| ID | Efecto en esta fase |
|----|---------------------|
| L-HF1 | Escribir los checks sobre la **propiedad** (el AC existe en el maestro; el dueño es el del índice) y publicar la población mirada (AC-B5) |
| L-R.3 | Ningún `[OK]` sin denominador: la línea `cobertura:` con los 5 conteos |
| L-R.4 | El límite de pertinencia va en el docstring **y** en la última línea de la salida |
| DA-HF3 | Hacia delante + delta; el script **reporta, no reescribe** — sin `--fix` |
| L-D3 | Umbrales ya medidos contra el único `00-` real (18 filas, 5 dueños, 6 descartes): un artefacto correcto debe pasarlos |
| L-B1 | Parsear la **tabla** por celdas, no regex suelta; test contra el archivo real del repo y contra fixtures en `tmp_path` |
| L-VUP-5 · L-T2C.4 | NR7 (R2.8) **por check**, revirtiendo el guard real del archivo versionado; dos salidas a `evidence/FASE-V2/` |
| L-T4B.5 · L-VUP-1 | Par pre/post con `--ignore` del archivo de tests nuevo y la resta de R2.7; `test_function_default_flags` declarado como flaky orden-dependiente |
| L-PF10 | R2.9 sobre el propio verificador: tres estados distinguibles y ningún verde desde `LECTOR-FALLIDO` |
| L-NC10 | Si un check cambia lo que el `00-` debe declarar, la declaración se actualiza en el mismo plan (esa pata es V3) |
| L-VUP-9 | Leer el `--help` real del script nuevo **antes** de citar comandos suyos en el template o en el executor |
| S-H17 | El bloqueo del hook se ejecuta y se guarda su salida; no se afirma |
| L-V.4 | Si un check resulta inejecutable sobre un artefacto legítimo, se registra con dueño; **prohibido** rebajar el umbral para que dé verde |
| L-C2 | Buscado antes de tocar: 0 contract tests afirman el número de checks de `run_all_validations.py` |

## Tareas

1. `scripts/validate_lesson_capitalization.py`: docstring con POR QUÉ EXISTE / QUÉ VERIFICA / LÍMITE
   DECLARADO / uso; funciones `_check_c1_presencia()` … `_check_c8_diversidad()`; `main()` con
   `--plans-dir`, `--cutoff`, `--quiet`; exit codes `0/1/2` (parámetros: verificar con `--help`).
2. `tests/test_validate_lesson_capitalization.py`: una clase o familia por check, con el nombre escrito por
   su causa, más tres tests de estado (`AUSENTE`, `SIN-HALLAZGOS`, `LECTOR-FALLIDO`) y un test que corra el
   script contra el árbol real del repo.
3. **NR7 por check**: por cada C1…C8, desactivar el guard en una copia temporal del archivo versionado,
   ejecutar el test y guardar la salida roja; restaurar y guardar la verde. Pares en
   `evidence/FASE-V2/nr7-C<n>-{rojo,verde}.txt`.
4. Cableado: `[7/7]` en `scripts/git_hooks/pre-commit` (con `[1/6]`…`[6/6]` → `[1/7]`…`[7/7]`) y
   `_check_lesson_capitalization()` en `run_all_validations.py` como check `[9/9]` del modo rápido, con la
   renumeración de los del modo completo.
5. Ejecutar el hook sobre un árbol defectuoso (plan de prueba con `00-` incompleto en `tmp_path` o un plan
   falso versionado solo para la corrida) y guardar salida + exit code en `evidence/FASE-V2/hook-bloquea.txt`.
6. `run_all_validations.py --quick` TOTAL PASS y `evidence/FASE-V2/baseline-pre-post.md` con la resta de R2.7.

## Documentación post-fase

- `09-documentacion-post-proyecto.md` §A/§B/§D/§E con las cifras reales.
- `10-analisis-post-implementacion.md` §1 fila de V2, §2 lecciones nuevas (formato qué pasó / por qué / qué
  lo previene / pertinencia) y §4 métricas.
- `CHANGELOG.md`: NO abre versión (decisión Q5); la entrada se acumula para V3.

## Post-ejecución (obligatorio, no delegable a FASE-V3)

```bash
python scripts/log_phase_completion.py --fase FASE-V2 \
  --desc "validate_lesson_capitalization.py con C0-C8, tests, NR7 por check y cableado [7/7] + [9/9]" \
  --archivos-mod "scripts/validate_lesson_capitalization.py,tests/test_validate_lesson_capitalization.py,scripts/git_hooks/pre-commit,scripts/run_all_validations.py" \
  --tests "<suma de def test_ nuevos>" --check-manual-docs
```

**Sin `--release`** (lo comprueba el check `[6/8]`→`[6/9]` de `run_all_validations.py`).

## Criterios de completitud

- AC-B1…AC-B5 leídos en su artefacto (R2.4), no afirmados.
- 8/8 checks con su par rojo/verde en `evidence/FASE-V2/`.
- `--quick` TOTAL PASS y hook bloqueando de verdad (evidencia ejecutada).
- NR1 con la resta de R2.7 publicada y el flaky declarado.
- Ninguna cita `archivo:123` en los archivos nuevos.

## Restricciones

- **Presupuesto**: sin instrumento canónico en esta máquina (D-V2.1) → auto-reporte en la unidad usada,
  declarado y no comparable. Corte: hasta el commit de código.
- Prohibido `--no-verify`, prohibido `git push`, prohibido tocar `VERSION.yaml`.
- Prohibido auto-fix: el script reporta.
- Prohibido rebajar un umbral para que un artefacto pase: se registra el caso con dueño (L-V.4).
- No modifica `main.py` ni ningún módulo bajo `modules/`.
