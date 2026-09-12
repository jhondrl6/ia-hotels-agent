# evidence/FASE-V2 — Mediciones del verificador y de su cableado

Plan `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` · 2026-09-12.
Archivo entregado: `scripts/validate_lesson_capitalization.py` (checks C0–C8, tres estados,
sin `--fix`) con `tests/test_validate_lesson_capitalization.py`.

## Lo que dice la salida sobre el corpus real

Corrida `python scripts/validate_lesson_capitalization.py` (exit 0):

```
PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12: 5 fuentes capitalizadas ->
  Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03, Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22,
  Archives/SR-PIPELINE-FIXES-2026-08-27, Archives/TRIBUNAL-OFFLINE-2026-09-09,
  Archives/VALIDADOR-URL-PROPIA-2026-08-30
cobertura: 1 plan(es) en alcance (…) | 25 archivados excluidos |
  1 exentos por fecha anterior a 2026-09-12 | 0 exentos SIN FECHA PARSEABLE (—)
[OK] Capitalización del Paso 0: forma y trazabilidad verificadas | NO verifica pertinencia (…)
```

**Cobertura del gate, declarada como exige L-R.3**: 1 de 27 directorios de plan. El gate no
puede afirmar nada sobre los 25 archivados ni sobre el plan del 2026-09-11, y esa
proporción es consecuencia directa de la decisión Q1, no un olvido.

## El gate contra un segundo artefacto humano (medición, no proclama)

`--cutoff 2026-09-11` mete al predecesor en alcance (su `00-` se instanció a mano el
2026-09-12). Resultado: **1 sola violación, C6**, y es la verdadera — su §4 declara que el
verificador **no existe**, afirmación que este commit vuelve falsa. Las otras siete formas
(consultas corpus-wide, ACs existentes, ≥3 descartes, IDs definidos, dueños coincidentes,
≥2 fuentes) **pasan sobre un artefacto escrito por otra sesión**, lo que mide dos cosas a la
vez: que el listón no está inflado (L-D3) y que no es cosmético (detecta un defecto real).

Test versionado que fija esta medición: `test_medido_contra_el_predecesor_la_unica_violacion_es_su_limite_no_actualizado`.

## NR7 (R2.8) — 13 detecciones revertidas sobre el archivo versionado

Runner: `run_nr7_capitalizacion.py` (en este directorio). Reversión en bytes sobre el
símbolo real de cada guard, con ancla de aparición única; restaura y verifica que el archivo
quede byte a byte igual. Pares en `nr7-<id>-rojo.txt` / `nr7-<id>-verde.txt`.

| Detección | Guard mutado | Tests que sostiene |
|-----------|--------------|--------------------|
| C1a | `if not ruta.exists():` en `analizar_plan()` | artefacto ausente declarado con su ruta |
| C1b | `if texto is None:` en `analizar_plan()` | ilegible ≠ ausente |
| C2 | `if secciones[numero] is None:` | sección estructurales |
| C3a | `if any(t in fila[capa].lower() …)` | consulta solo al predecesor / consulta sin comando |
| C4a | `if not prometidos:` | fila sin AC nombrado |
| C4b | `if prometidos & acs:` | AC inventado que no existe en el maestro |
| C5 | `if len(datos) >= MIN_DESCARTES:` | menos de tres descartes |
| C6a | `if VERIFICADOR not in seccion:` | §4 que no nombra al verificador |
| C6b | `if not any(f in bajo for f in LIMIT_PHRASES):` | §4 sin declaración de límite |
| C7a | `if not LESSON_ID_RE.match(lid):` | celda que no es un ID |
| C7b | `if dueno is None:` | ID inexistente en el corpus |
| C7c | `if dueno not in publicada:` | dueño real distinto del publicado |
| C8 | `if len(duenos) < MIN_DUENOS:` | capitalización de una sola fuente |

## Dos rojos que el propio runner produjo antes de cerrar (y qué revelaron)

- **Ancla ambigua en C1a**: `if not ruta.exists():` aparece también en `acs_del_maestro()`.
  El runner la rechazó en vez de mutar al azar: el contador de apariciones es parte del
  contrato de la herramienta de mutación.
- **C4a y C7a sobrevivieron a su primera mutación** (`rojo=0`): dos ramas del mismo check
  producían violaciones intercambiables, así que el test «pasaba» por la otra rama. No era un
  problema del mutante sino de los tests, que miraban `v.check` y no el mensaje. Los dos
  tests ahora anclan su mensaje (`"no existen en la tabla de ACs"`, `"debe ser un ID del
  corpus"`) y cada mutación mata solo el suyo. Es L-VUP-5 en su forma útil: el verde sin rojo
  previo era el síntoma de un test que no observaba lo que decía observar.

## Cambios de contrato durante la implementación (registrados, no improvisados)

- **`AC_TOKEN_RE` ampliado a `\bAC-?[A-Z]{0,2}\d+\b`**: el contrato de V1 decía
  `AC-<letra><dígito>`, pero el repo usa además la forma sin guion (`AC8`, visible en el
  predecesor). Con la forma estrecha, C4 habría castigado a quien escribe la convención
  histórica (L-B1). Afecta a la fila C4 de `01-plan-maestro.md` §3, actualizada con la razón.
- **Un plan sin fecha en el nombre queda exento pero declarado** (no exigido): es la
  formulación de Q1 en V1 y el límite (5) de §4 del maestro. La salida los lista por su
  nombre para que la exención no sea muda.
- **`_limpiar()` conserva los backticks**: C3 necesita distinguir «comando copy-pasteable»
  de «revisé las lecciones», y en el template esa marca es el código inline. Quitarlos hacía
  el check insatisfacible; se compensa despojando los backticks del ID en C7.

## Cableado verificado

- `[7/7]` en `scripts/git_hooks/pre-commit` (los seis anteriores renumerados a `/7`):
  bloqueo demostrado en `hook-bloquea.txt`, ejecutado, no afirmado (S-H17).
- Check `[9/9] Lesson Capitalization` en `run_all_validations.py`, modo rápido; los checks
  del modo completo pasan a `[10/12]`, `[11/12]`, `[12/12]` y `[13/13]`.
- `--help` del script leído antes de citar sus flags (L-VUP-9): `--plans-dir`,
  `--context-dir`, `--cutoff`, `--quiet`. Sin `--fix` (AC-B1).
