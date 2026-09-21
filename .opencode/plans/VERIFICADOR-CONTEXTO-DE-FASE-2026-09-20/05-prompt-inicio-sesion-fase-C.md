# FASE-C — Capa de pertinencia sobre el índice de lecciones (aditiva, nunca filtro)

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-C
**Objetivo**: escribir `scripts/triage_lesson_relevance.py`, la mitad que
`validate_lesson_capitalization.py` declara fuera de alcance: **si la lección capitalizada era la
pertinente y cuáles quedaron fuera**. Cubre AC10–AC15.
**Dependencias**: FASE-A ✅ (estados y denominador) y FASE-B ✅ (la costura es la única puerta al proveedor).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

El Paso 0 del executor produce `00-lecciones-capitalizadas.md` y su verificador corta en el
commit. Pero ese verificador dice de sí mismo, en su docstring, que un `[OK]` suyo significa
**«la forma exigida está», nunca «capitalicé bien»**: no puede saber si la lección que debía
capitalizarse era otra. Esta fase escribe exactamente esa otra mitad.

Y lo escribe con una restricción que nace de un hecho medido dos veces: un plan cuyo objetivo de
entrega era inalcanzable porque un hallazgo CRITICAL registrado en el corpus no lo cubría ninguna
fase, y hubo que crearle una fase y un AC nuevos. **Un filtro de pertinencia que descarte en
silencio una premisa carga-estructura reproduce ese fallo.** Por eso el triaje de este plan es
aditivo por construcción y eso es AC, no intención.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| FASE-A | ✅ — reutilizar `status` de tres estados y `coverage_basis` |
| FASE-B | ✅ — usar `decision_client.py`; prohibido importar el SDK directamente |

### Base técnica disponible

- Suelo determinista: `.opencode/lecciones_index.json`, generado por `scripts/build_lesson_index.py`.
  Población medida y **re-medida tras regenerar el índice al concebir el plan**: **320** IDs con
  definición detectada, **50** citados sin definición, 15 análisis + 36 `CONTEXT-*.md` como corpus
  de definiciones, **402** `.md` como corpus de citas. Las tres últimas cifras decían 14 / 49 / 389
  hasta que este propio plan entró al corpus (maestro §1, medición A6). El índice se regenera y
  `--check` lo corta en `[6/7]` del hook; **no se edita a mano**.
- Formatos a emular: `scripts/validate_lesson_capitalization.py` (checks C1–C8, R2.9 sobre sí
  mismo, reporta sin reescribir) y su artefacto de plan (§1 consultas, §2 capitalizadas con «qué
  cambia», §3 ≥3 descartes, §4 cobertura).
- Precedente del defecto que esta fase mide: al concebir el plan, `grep -icE "verificador mec"`
  devolvió **0** sobre el índice en un corpus que sí contiene verificadores nombrados con otras
  palabras. Un cero de grep no distingue «no existe» de «término equivocado».

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-R.3 | Un `[OK]` sin denominador no informa | Tarea 3 / **AC15**: población mirada, términos usados y cuántos IDs recibieron juicio |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC11**: un JSON del índice que reviente jamás devuelve «sin candidatos» |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC11**: `AUSENTE` y `VENCIDO` son estados propios, con ruta y comando de regeneración |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC10**: la comparación §2 antes/después es un delta, no una lista que deba coincidir |
| L-HF1 | Candado con cobertura equivocada pasa en verde mientras el artefacto miente | **AC15/AC17**: decir qué familias de lección no se juzgan (IDs numéricos, familias fuera de `L-*`/`DA-*`/`D-*`/`S-*`) |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Tarea 2 / **AC14**: mutation check sobre el guard real de AC10, no sobre un duplicado dentro del test |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: sin rojo, AC14 es ⚠️ |
| L-R.4 | Regla sin verificador es publicable solo si lo declara | **AC12**: el umbral se publica con valor, base y acción por debajo |
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | Restricción: esta fase no toca el quick (11) ni el hook (7) |

## Tareas

### Tarea 1: Leer el suelo determinista sin colapsar estados

**Objetivo**: cargar `lecciones_index.json`, distinguir presente/faltante/vencido, y derivar el
conjunto de candidatos **sin** quitar ninguna fila ya anclada.

**Elección de fuente, obligada y escrita (Knowledge Center, `L-V2.2` de
`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`)**: ese plan capitalizó que un verificador **no debe
apoyar su conclusión en el artefacto que genera otro gate** — el JSON se lo produce `[6/7]`—, y se
curó calculando el índice **en memoria** con `build_lesson_index.build()` (0,30 s medidos). FASE-C
elige una de las dos rutas y deja el costo medido: **(a)** `build()` en memoria, un solo lector y sin
verde heredado (el `VENCIDO` desaparece como estado, y hay que decirlo), o **(b)** leer el JSON
después de **ejecutar ella misma** la comprobación de frescura, de modo que `VENCIDO` sea producto de
su propio check. Prohibida la tercera: leer el JSON confiando en que otro paso lo regeneró.

**Archivos afectados**: `scripts/triage_lesson_relevance.py` (nuevo),
`tests/quality_gates/lesson_relevance/` (nuevo).

**Criterios de aceptación**: **AC11** (`index_status`; `AUSENTE` imprime la ruta buscada y el
comando de regeneración; `VENCIDO` imprime qué check del hook lo detecta) y **AC10** (artefacto
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`, `anchored_after`, `removed: []` y un
test que lo afirma).

### Tarea 2: Juicio de pertinencia aditivo, con umbral declarado

**Objetivo**: por candidato no capitalizado, una pregunta binaria a través de `decision_client.py`;
separar `propuesto` de `a-revisar-humano` por confianza. **Nunca autofiltrar.**

**Criterios de aceptación**: **AC12** (clave `threshold` con `value`, `basis`, `action_below`) y
**AC14** (mutation check sobre el símbolo real que impide el filtrado: desactivado el guard, el
test de AC10 debe ponerse rojo; evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`).

### Tarea 3: Denominador, términos y prueba contra corpus real

**Objetivo**: publicar a cuántos de los 320 IDs se aplicó juicio con qué términos, y probar al
menos un caso contra archivos **reales** de `Archives/`, no contra fixture propio.

**Criterios de aceptación**: **AC13** (test contra corpus real archivado con `skipif` explícito;
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` declara si el test **corrió o se saltó** — un skip silencioso es la
variante muda del mismo defecto) y **AC15** (`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` con población,
términos, ceros incluidos, familias no juzgadas y `acceptance`).

**Cómo se cierra AC15 sin proveedor activo** — y es el caso de este plan, porque el proveedor quedó
pospuesto (deuda D7): el triaje se ejercita contra el **proveedor falso determinista** que define
AC8/AC9 de FASE-B. Eso prueba la mecánica —aditividad, estados, umbral— pero **no** produce un número
de aceptabilidad real. Entonces `acceptance` se publica como `NO-EJERCITADO` con el motivo literal,
AC15 queda en ⚠️ y **D6 permanece dormida**: no se abre un lint de contradicciones sobre una base que
nunca juzgó nada. Re-evaluar D6 toca cuando exista proveedor real, no antes.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_triage_no_elimina_fila_anclada.py` | AC10; `removed == []` sobre §2 real de este plan |
| `test_triage_indices_ausente.py` | `AUSENTE` con ruta y comando; no «sin candidatos» |
| `test_triage_indices_vencido.py` | `VENCIDO` con el check del hook que lo detecta |
| `test_triage_umbral_publicado.py` | AC12 con valor, base y acción por debajo |
| `test_triage_corpus_real.py` | AC13, con `skipif` visible; la evidencia dice si corrió |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/lesson_relevance -v
./venv/Scripts/python.exe scripts/triage_lesson_relevance.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --report
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-C ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC10–AC15.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D, E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas, métricas reales,
   seguimientos, decisiones (incluida la de **no** dejar que el triaje filtre, y su alternativa rechazada).
6. `00-lecciones-capitalizadas.md` — **aplicar sobre este propio plan los candidatos que el triaje
   proponga**: si FASE-C propone una lección que el Paso 0 no ancló, se añade a §2 con su dueño y
   su «qué cambia» reales, y se registra en §4 que el propio plan se auto-trió. Una fila citada y
   no aplicada se marca como tal, no se borra.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C \
  --desc "triage_lesson_relevance.py: capa de pertinencia aditiva sobre el indice, umbral publicado y denominador (AC10-AC15)" \
  --archivos-mod "scripts/triage_lesson_relevance.py,tests/quality_gates/lesson_relevance" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] `ac10_delta.json` muestra `removed: []` y hay un test que lo afirma (AC10).
- [ ] Los tres estados del índice tienen su test nombrado por la causa; ninguno cubre dos.
- [ ] `mutation/` tiene rojo y verde del guard de no-filtrado (AC14). Sin rojo, ⚠️.
- [ ] `r26.txt` declara si el test contra corpus real **corrió** o se saltó, con el motivo (AC13).
- [ ] `coverage.json` tiene población, términos usados con sus conteos (ceros incluidos), familias
  no juzgadas y `acceptance` real o `NO-EJERCITADO` con motivo (AC15).
- [ ] Con proveedor falso, AC15 está en ⚠️ y **D6 quedó declarada dormida** en `dependencias-fases.md`.
- [ ] `validate_lesson_capitalization.py` sigue verde sobre `00-lecciones-capitalizadas.md` **después**
  de aplicar los candidatos (AC18).
- [ ] `--quick` verde sin haber alterado su composición (AC16).
- [ ] Post-ejecución completa e índice regenerado en el mismo commit.

## Restricciones

- **El triaje propone; jamás descarta.** Ningún camino del código elimina una fila de §2 (AC10).
- No modificar `build_lesson_index.py`, `validate_lesson_capitalization.py`,
  `validate_governance_numbers.py`, `decision_client.py` (consúmalos), `.agents/**`,
  `run_all_validations.py` ni el hook.
- No escribir sobre los §2 de **otros** planes, vivos o archivados: el triaje corre sobre el plan
  que se le indique por argumento y su salida es un informe, no una edición.
- No enviar PII ni material del cliente de `REFACTOR-WHATSAPP` a ningún proveedor. Las entradas
  salen del corpus de lecciones del repo.
- Tope de llamadas del contrato (200 por sesión). No commitear ni empujar sin instrucción literal.

## Prompt de ejecución

```text
Ejecuta únicamente FASE-C del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-C.md, 01-plan-maestro.md §1 (la medicion del grep con cero
coincidencias) y §4 (AC10-AC15, AC16, AC18), 04-contrato-ejecucion.md (permisos, tope de
llamadas), 00-lecciones-capitalizadas.md §1-§4, dependencias-fases.md y el workflow canónico.
Heredas de A los tres estados y coverage_basis, y de B la costura decision_client.py como unica
puerta al proveedor: no importes el SDK.
Escribe scripts/triage_lesson_relevance.py: lee .opencode/lecciones_index.json, distingue
presente/ausente/vencido sin colapsar nunca un lector roto en «sin candidatos», y propone
candidatos de pertinencia que el Paso 0 no anclo. Es ADITIVO por construccion: ninguna fila de §2
puede desaparecer y eso es AC10 con su test y su delta publicado.
Umbral de confianza con valor, base y accion por debajo (AC12). Mutation check sobre el simbolo
real que impide el filtrado, con rojo y verde en evidencia (AC14). Al menos un test contra planes
reales de Archives/ con skipif visible, y la evidencia dice si corrió o se saltó (AC13).
Denominador con poblacion, terminos usados incluidos los ceros, familias no juzgadas y acceptance
(AC15). Como no hay proveedor activo en este plan, exercisea la mecanica con el proveedor falso
determinista y publica acceptance = NO-EJERCITADO con el motivo: AC15 queda en ⚠️ y la deuda D6
queda dormida en dependencias-fases.md. No abras el lint de contradicciones sobre una base que nunca
juzgo nada.
Mide el triaje contra tu propio 00-lecciones-capitalizadas.md y aplica lo que proponga.
No toques build_lesson_index.py, validate_lesson_capitalization.py, decision_client.py, .agents/,
run_all_validations.py, el hook ni ningun plan vivo. Regenera el indice de lecciones en el mismo
commit y registra la fase con log_phase_completion.py. Deja checkpoint si falta autorizacion.
```
