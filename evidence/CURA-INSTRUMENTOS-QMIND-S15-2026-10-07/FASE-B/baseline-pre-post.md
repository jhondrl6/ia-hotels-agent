# PRE / POST de FASE-B (R2.7) — 2026-10-09

**Interprete declarado en todas las corridas:** `./venv/Scripts/python.exe` (Python 3.13.3, venv del proyecto).
**Arbol:** worktree de `77e64ca` (HEAD == `origin/master`, medido por `git rev-parse` y `git ls-remote`).
**Estado del arbol al abrir:** 13 rutas staged de otra sesion (`Archives/REFACTOR-WHATSAPP-…/briefing/FASE-*.md` y
`evidence/REFACTOR-WHATSAPP-…/FASE-E2E/captura_stdout.txt`, deuda S-CIM-7): **no se tocaron, no se des-stagearon,
no entran en ningun conteo de esta fase**. Quick de apertura, leido en consola y **no archivado**: `13/13`,
`EXIT=0`. El quick de cierre si esta archivado: `08-quick_cierre.txt`, mismos 13/13.

## Selection literal de la fase

`tests/test_build_lesson_index_s15_fecha_versionada.py`

| Corte | Sumas | EXIT | Crudo |
|---|---|---|---|
| PRE (antes de editar) | **1 failed, 3 passed** | 1 | `tests_baseline_pre.txt` |
| POST (seleccion literal, mismo interprete) | **8 passed** | 0 | `tests_baseline_post.txt` |

**Resta comprobada:** 8 − (3 passed + 1 failed = 4 recolectados) = **4 funciones nuevas de ESTA fase**.
Medidas por el metodo canonico sobre el archivo: `grep -cE "^\s*def test_"` → **4 antes, 8 despues** (resta 4,
coincide). Rojos: 1 → 0.

## Aserciones tocadas (AC8 exige publicar la cita literal antes/despues)

`git diff -U0` sobre el archivo: **22 lineas `assert` agregadas, 2 eliminadas**. Las dos eliminadas, con su
re-emision:

1. `:119` (HEAD) `assert ruta.is_file(), f"{rel} no existe en el checkout {nombre}: el control no tendria que medir"`
   → `_revisar_materializacion()` (`pytest.fail` con `NO-EVALUABLE` + la ruta buscada, sin la palabra
   «divergencia»), y su diente `test_el_clon_que_no_materializa_declara_no_evaluable_con_la_ruta` con corte
   positivo sobre el arbol real. La propiedad (no se mide sobre un arbol incompleto) queda **mas fuerte**: antes
   era un rojo indistinto; ahora es un estado nombrado, y ese estado tiene su propia prueba.
2. `:211` (HEAD) `assert la[i]["fecha_plan"] == MTO_A[:10] and lb[i]["fecha_plan"] == MTO_B[:10], (`
   → `:319` `assert la[i]["fecha_plan"] == mto_a[:10] and lb[i]["fecha_plan"] == mto_b[:10], (`
   La igualdad y su mensaje quedan intactos; cambia que el expected es **el reloj que el fixture estampo** en vez
   de un literal pineado que el corpus puede dejar atras.

La asercion decisiva del control **no se toco** (texto identico antes y despues, medido por `grep -nF`):
`assert la[i]["fuente_fecha"] == "mtime" and lb[i]["fuente_fecha"] == "mtime"` — en HEAD linea 210, en el arbol
curado linea 318. Tampoco se toco `REV_CONTROL_DEFECTUOSO = "6b02532"` (ahora tiene diente propio en contra).

## Hermanas re-corridas (Tarea 4)

| Selection | Corrida | Funciones por el metodo canonico | Crudo |
|---|---|---|---|
| `tests/test_build_lesson_index.py` | **18 passed**, `EXIT=0` | `grep -cE "^\s*def test_"` = **16** (los 2 extra son parametrizacion: la corrida emite 18 casos, el conteo de funciones 16; se publican las dos cifras porque son instrumentos distintos) | `04-hermana-build_lesson_index.txt` |
| `tests/test_verify_qmind_context_freshness.py` | **36 passed**, `EXIT=0` | 36 | `05-hermana-qmind_freshness.txt` |

Ambas estan **intactas** en esta fase: `git diff --stat -- tests/test_build_lesson_index.py
tests/test_verify_qmind_context_freshness.py scripts/build_lesson_index.py` imprime **vacio**. Por eso no se les
tomo PRE aparte: sin edicion, PRE y POST son el mismo arbol, y declararlo vale mas que fingir una resta de 0 con
tests nuevos. La resta de la fase es la de la seleccion de arriba (4).

## Generador: `--check` con su linea `[fechas]` en verde y en rojo

| Via | Salida | EXIT | Crudo |
|---|---|---|---|
| verde (`--out-dir temp/s15_check`) | `[fechas] nombre=361 commit=11 sin_fuente=0` | 0 | `06-check-fechas-verde.txt` |
| roja (mismo directorio, MD generado vencido) | `[fechas] nombre=361 commit=11 sin_fuente=0` | 1 | `07-check-fechas-rojo.txt` |

Medido contra la fila de la preparacion (`nombre=337 commit=11 sin_fuente=0`): el tier `nombre` crece de 337 a
**361** por las definiciones que anadieron A1/A2/A3 en sus cierres; el tier `commit` sigue en **11** y
`SIN-FUENTE` en **0**. El par versionado `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` **no**
se toco en estas dos vias (el `--out-dir` apuntaba a `temp/`); su regeneracion con su escritor es el ultimo paso
del cierre (R2.10).

## Quick

`./venv/Scripts/python.exe scripts/run_all_validations.py --quick` → **13/13**, `EXIT=0` (`08-quick_cierre.txt`).
El denominador lo imprime la corrida; no se fija aqui.
