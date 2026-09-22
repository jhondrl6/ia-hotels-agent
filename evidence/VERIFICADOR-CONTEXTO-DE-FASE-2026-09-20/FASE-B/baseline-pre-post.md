# FASE-B — par pre/post del conteo (AC16) y lo que sí se movió

Plan: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` · Medido el **2026-09-21** sobre HEAD `74d8ff5`
(árbol con dos rutas ajenas preexistentes: `EVALUACION-JEV/dependencias-fases.md` modificado y
`.opencode/context/Refuerzo.md` sin trackear — ninguna las tocó esta fase, siguen excluidas de su
commit).

**Comandos idénticos en los dos lados** (R2.3/R2.7: la resta solo vale si el instrumento es el mismo).
Crudos: `faseB_baseline_pre.txt` · `faseB_baseline_post.txt` · `faseB_quick_pre.txt` ·
`faseB_quick_post.txt`.

```bash
grep -cE '^\s*print\(f?"\[[0-9]+/11\]' scripts/run_all_validations.py      # quick
grep -cE '^\s*print\(f?"\[[0-9]+/15\]' scripts/run_all_validations.py      # solo-completo
grep -cE '^#   \[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit             # hook
grep -rE '^\s*def test_' tests --include=*.py | wc -l                      # canonico (metodo grep)
grep -rE '^\s*def test_' tests/quality_gates/decision_client --include=*.py | wc -l
git ls-files '*.py' | wc -l                                                # poblacion AC6 (git)
git grep -cE '^\s*(import|from)\s+(typesafe|jev|httpx2)' -- '*.py'         # AC6 (git, import)
stat -c "%s %n" .agents/workflows/phased_project_executor.md \
  .agents/workflows/templates/lecciones-capitalizadas-template.md          # AC17
```

## La resta, por unidad

| Unidad (mismo comando en los dos lados) | PRE | POST | Resta | Esperado | Estado |
|---|---|---|---|---|---|
| Checks del `--quick` (`[N/11]` impresas) | 11 | 11 | **0** | 0 (AC16) | ✅ |
| Etiquetas del modo completo (`[N/15]`) | 4 | 4 | **0** | 0 (AC16) | ✅ |
| Pasos del hook versionado | 7 | 7 | **0** | 0 (AC16) | ✅ |
| Composición del `--quick` | 11/11 verde | 11/11 verde | 0 | verde sin tocar composición | ✅ |
| `git diff` de `run_all_validations.py`, el hook, `build_lesson_index.py` y `validate_governance_numbers.py` | — | **vacío** | 0 | esta fase no los escribe | ✅ |
| Bytes de los dos documentos de gobierno (AC17) | 98.694 / 6.123 | 98.694 / 6.123 | **0 / 0** | 0 (`.agents/` intocado) | ✅ |
| `git status --porcelain .agents/` | — | **vacío** | 0 | ✅ |
| Imports del SDK/adapter fuera de la puerta (AC6, `git grep`) | 0 | 0 | **0** | 0 | ✅ |
| Población AC6 rastreada por git (`.py`) | 678 | 678 | 0 | la fase no commitea `.py` | ✅ |
| Archivos `.py` del árbol de trabajo que **sí** escanea AC6 | **no medible en el PRE** (el instrumento nace en esta fase) | **692** | n/a | ver nota 1 y nota 3 | ⚠️ declarado |
| Nodos de import vistos por el escáner · menciones-no-import · cargas no resueltas | — | 4.379 · 21 · 16 | n/a | ídem | ✅ publicados |
| **Población AC6 dentro de la propia fase** | 690 (primer escaneo, tras escribir puerta y tests) | **692** (escaneo final) | **+2** | — | ⚠️ **se movió ella sola: ver nota 3** |
| **Selección de tests de FASE-B** (`tests/quality_gates/decision_client`) | 0 funciones | **48 funciones / 53 casos** | **+48** | distinto de 0: la fase agrega tests | ✅ declarado |
| Funciones de test canónicas del repo (método grep) | 4.330 | 4.378 | **+48** | coherente con la fila anterior | ✅ |
| Pins del denominador 11 en `tests/` (familia iii de AC2) | 4 (los añadió FASE-A) | 4 | **0** | esta fase no crea pins | ✅ |

AC16 pide resta 0 en los **conteos de checks** (11 y 7), y está. Las dos filas que sí se movieron son
de tests y se publican aparte en lugar de maquillarse (L-D3): pretender «delta 0» con 48 funciones
nuevas escritas aquí sería un baseline contaminado.

**Nota 1 — dos poblaciones para AC6, y por qué las dos.** `git grep` mira los 678 `.py` **rastreados**;
el escáner de la fase (`scripts/decision_client.py --scan-imports`) recorre el **árbol de trabajo** y
cuenta **692** `.py` tras excluir directorios declarados, cada uno con su conteo (`venv` 7.618,
`site-packages` 8.889, `tmp_test` 690 —donde el plan hermano aisló el SDK real—, `temp` 65,
`build` 14). La diferencia con el número de git son los archivos de esta fase, que aún no están
commiteados. Publicar una sola de las dos cifras dejaría al lector sin saber cuál sostiene el 0.

**Nota 1b — el SDK sí está en el disco.** `typesafe-sdk` fue instalado por `EVALUACION-JEV` en un
entorno aislado (`tmp_test/venv-jev-sdk`), no en el venv del producto. Eso no contradice AC6 (que
gobierna **imports**, no instalaciones) pero sí desmentiría un «no existe» afirmado: la exclusión está
publicada con su conteo y la ausencia en el venv del producto se mide con `find_spec`, no se infiere.

**Nota 3 — la población de AC6 se movió durante esta fase, y es el hallazgo del plan aplicado a sí
mismo.** El primer escaneo (tras escribir la puerta y sus tests) dijo 690 `.py`; el escaneo final dice
**692**. Lo que creció no es tráfico ajeno: son los **dos instrumentos** que esta propia fase escribió
bajo `instrumentos/` para poder generar su evidencia. Cada cifra copiada de una fuente dinámica caduca
al producirla (medición A6 del maestro, ya reproducida tres veces en la concepción), y aquí la
corrección no es borrar el instrumento —sin él la evidencia no es re-ejecutable— sino **re-medir al
cerrar y publicar el +2**, que es lo que hacen las filas de arriba.

**Nota 2 — quién afirma el 11 y el 7 (barrido de `tests/`, L-V2.3).** Esta fase no añadió ningún pin de
esos denominadores: sus pruebas afirman formas, estados y conteos propios (`files_changed…`, `48`), y
el único conteo de terceros que aparece en un assert es `len(VERIFICACIONES_DE_FORMA) == 6`, que es de
la puerta y no del `--quick`. Los 4 pins del 11 que quedan en `tests/` siguen siendo los de FASE-A,
con dueño **D1/D2** y su nota datada en `FASE-A/baseline-pre-post.md`.

## Rutas ajenas que aparecen en `git status` al cerrar (no son de este plan)

Medido con `stat -c %y` y con `git diff --numstat` el 2026-09-21, porque una sesión paralela está activa
sobre este mismo repo:

| Ruta | Estado | Qué es y cómo se sabe que no es de FASE-B |
|---|---|---|
| `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` | modificado, **preexistente al abrir la fase** (ya estaba en `git status` del `faseB_baseline_pre.txt`) | Es el plan hermano; esta fase no abrió ningún archivo de `EVALUACION-JEV` |
| ~~`.opencode/context/Refuerzo.md`~~ | apareció sin trackear durante la sesión (mtime 22:13) y **ya no está en `git status`**: lo commiteó la otra sesión | `git show --stat eecf246` lo incluye (268 líneas). No es de este plan y ya no es una ruta pendiente |
| ~~`ROADMAP.md`~~ | modificado durante la sesión (mtime 22:17:38), 323+/518− — **commiteado por la otra sesión en `eecf246`**, que hoy es el HEAD | Su contenido es la revisión v4.3 del roadmap (Tribunal certificado, implementación gestionada, TAREA7): `grep -c "decision_client\|VERIFICADOR-CONTEXTO" ROADMAP.md` = **0**. No toca ninguna línea de este plan |

**Regla aplicada**: en el commit de FASE-B queda **fuera** la única ruta ajena todavía sucia
(`EVALUACION-JEV/dependencias-fases.md`), y sobre ella no se hace `git checkout`: es trabajo en curso de
otra sesión, no basura que limpiar (precedente: FASE-A excluyó a propósito sus dos rutas ajenas).

**Consecuencia medida del HEAD compartido (rectificación datada, escrita en el tramo de commit).** Cuando
esta fase redactó la tabla anterior, las tres rutas estaban sucias en el árbol. Al abrir el tramo de
commit, `git show --stat eecf246` muestra que la otra sesión ya se llevó `ROADMAP.md` y
`.opencode/context/Refuerzo.md`, así que el HEAD del repo **dejó de ser `74d8ff5`** (sobre el que midieron
el PRE, el POST y las dos corridas del quick) y pasó a `eecf246`, con paridad `0/1` contra
`origin/master`: el commit de FASE-B se apoya sobre **un commit ajeno todavía sin empujar**. Nada de esto
mueve las restas —los cuatro archivos gobernados por AC16/AC17 no están en ninguno de los dos commits y
`git diff --numstat` sobre ellos sigue vacío—, pero sí invalida la lectura «el árbol de partida es solo
mío», que es justo el tipo de premisa que este plan caza (medición A6).

## Rojo propio intermedio, resuelto con su writer (segunda reproducción del conflicto de fechas)

Tras `log_phase_completion.py --fase FASE-B`, el `--quick` pasó de 11/11 a **10/11**: el check
`[3/11]` (`sync_versions.py --check`) puso

```
[-] Version Sync: Versions out of sync
      - FAIL: docs/contributing/REGISTRY.md (registry_last_update) - needs update
```

**Causa**: los dos escritores de la fecha en `REGISTRY.md` siguen sin reconciliar —
`log_phase_completion.py` estampa el día de hoy y `sync_versions.py` valida contra su `date` anclado.
FASE-A ya lo había reproducido (lo cuenta en su `baseline-pre-post.md`); **FASE-B lo volvió a
reproducir**, lo que confirma que el fix no era el de una fase sino el del escritor. **No se editó
`REGISTRY.md` a mano**: se corrió `python scripts/sync_versions.py --rule registry_last_update` (salida
`OK: docs/contributing/REGISTRY.md (registry_last_update) - updated`) y la corrida volvió a **11/11**
(`faseB_quick_post.txt`, con su `exit 0`). Deuda: la reconciliación de los dos escritores no es de
este plan, y esta es la **segunda** fase que lo paga en su propio cierre.

## Rojos de la fase, declarados

* **Rojo propio y necesario (AC8)**: `contract.txt` guarda el verde de `-k contract_forma` (exit 0) y
  el rojo del **mismo** test contra una copia del proveedor falso a la que se le quitó `confidence`
  (exit 1, `RespuestaIlegible` con 2 motivos: `campos-conocidos` y `forma-choice`).
* **Rojos de mutation check (R2.8)**: nueve mutantes en `mutation/`, cada uno con su VERDE y su ROJO.
* **El verde no llegó a la primera (L-VUP-5)**: la primera corrida de la selección dio **30 fallos**
  (un f-string mal cerrado en el módulo, argumentos posicionales de `score` cayendo en `opciones` en
  el fixture y en dos call sites del propio módulo, y 8 aserciones mal apuntadas), y el primer mutante
  de forma apagaba la lista **entera**, que no aislaba a ningún guard. Detalle en
  `mutation/verde_baseline.txt`.
* **Rojos preexistentes ajenos**: ninguno se arrastró. La selección de esta fase corre sola y da
  53/53; el rojo ajeno documentado por FASE-A
  (`tests/test_validate_lesson_capitalization.py`, caso archivado en `RELEASE-4.77.0`) no toca ningún
  archivo de esta fase y sigue con su dueño (`REFACTOR-WHATSAPP-ENTREGA-2026-09-18`).

## Presupuesto (R2.1 / D-V2.1): instrumento, corte y unidad declarada

* **Instrumento canónico**: `evidence/FASE-D/measure_iterations.py` (ruta legado del executor), corte
  **hasta el commit de código**.
* **No corrió**, por la misma precondición que midieron cuatro fases del plan que lo capitalizó:
  `find . -name "*.jsonl"` devuelve **0** dentro del workspace (re-verificado hoy, no asumido) — el
  instrumento pide el transcript del cliente y esta sesión no lo tiene.
* **Métrica retirada y declarada fuera de servicio, no estimada.** No se publica un número de
  `tool_use` «aproximado»: contar bloques de herramienta desde dentro de la sesión no es medible sin
  el transcript que falta, y una cifra inventada sería exactamente lo que R2.1 prohíbe.
* **Unidad contable en disco, declarada no comparable** (rectificada a la cifra medida, no a la
  estimada al escribir el borrador): **11** archivos de código y tests escritos por la fase
  (`git status --porcelain --untracked-files=all -- scripts/decision_client.py
  tests/quality_gates/decision_client | wc -l` → 11: 1 puerta + 2 proveedores falsos + 6 archivos de
  tests + `conftest.py` + `__init__.py`) y **25** archivos de evidencia en este directorio
  (`find evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B -type f | wc -l`, incluidos los 10 de
  `mutation/` y los 2 de `instrumentos/`). **0** comandos de larga duración (R3: la fase declaró 3
  tareas de código y 0 comandos largos). No es comparable con las corridas que sí midieron `ids únicos`
  con el script, y así se lee. Los dos instrumentos que produjeron la evidencia quedaron en
  `instrumentos/` para que la fase sea re-ejecutable, no para que nadie la re-escriba a mano.
* No se ejecutó `v4complete`, `v4audit` ni ninguna API, y no hubo una sola llamada de red
  (`cero-red.txt`).
