# FASE-C — Capa de pertinencia sobre el índice de lecciones (aditiva, nunca filtro)

> **Estado de este prompt al 2026-09-23: CONTRACTUALMENTE PREPARADO, NO EJECUTADO.** FASE-C sigue
> siendo la sesión siguiente y **no** se corrió al conciliar FASE-B. Contiene cuatro enmiendas
> prospectivas ya resueltas por este plan (**E1–E5** en `04-contrato-ejecucion.md`, orden de calidad
> §4.C, con autorización local del operador sobre CONTEXTO/C): la elección de fuente de **AC11 está
> cerrada en la ruta (b)**, la pregunta binaria es **`choice` con `confidence` independiente**, las
> propuestas del proveedor falso **no** entran en §2 sin **revisión humana registrada**, el tramo
> semántico de **AC15** sigue `NO-EJERCITADO` con **D6 dormida**, y **C conserva el workflow canónico y
> el proceso común vigentes** (los bloques B y C de la orden quedan **diferidos, no aplicados**). Donde
> una instrucción de este archivo contradiga ese párrafo, manda el párrafo y está mal conciliado: decirlo.

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
  **⟦Aviso añadido el 2026-09-23, familia A6⟧.** Esas cuatro cifras son **antecedentes fechados**, no el
  valor con el que se abre la sesión: al 2026-09-23 `build_lesson_index.py --check` reporta **332 IDs**
  definidas, y la cifra se mueve cada vez que alguien define un ID nuevo en cualquier `.md` del corpus —
  incluida esta sesión. **AC15 y AC11 calculan su denominador sobre la lectura que hace C de su propio
  check**, y publican cifra + comando + fecha; prohibido pinear 320/50/15/402 ni 332 en un test (L-V2.3).
  Comando de apertura: `python scripts/build_lesson_index.py --check`.
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
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC11**: `AUSENTE`, `VENCIDO` y `LECTOR-FALLIDO` son tres estados propios —el primero con ruta y comando de regeneración, el segundo con el check **propio** de C (⟦E2⟧), el tercero con el motivo del parseo |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto que genera **otro** gate | Tarea 1 / **AC11**, ⟦decisión cerrada el 2026-09-23⟧: C toma la **ruta (b)** — consume el JSON **tras** ejecutar él mismo la comprobación de frescura, con `VENCIDO` como estado propio y su costo publicado |
| L-VCF-12 | Antes de correr un verificador con `--report`/`--write`, mirar si su default toca evidencia commiteada | Cierre del plan: **la guarda particular cayó** (S12 aceptada el 2026-09-23; `validate_governance_numbers.py --report` sin destino ya imprime y no escribe), **la regla general sigue** — y aplica al `--report` del propio `triage_lesson_relevance.py`: C debe publicar el destino de su informe, no heredar una ruta por defecto dentro de la evidencia de otra fase |
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

**Elección de fuente — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E2)⟧: se toma la ruta (b).**
El suelo determinista es `.opencode/lecciones_index.json`, y **C ejecuta ella misma la comprobación de
frescura antes de apoyarse en él** (Knowledge Center, `L-V2.2` de
`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`: un verificador **no** apoya su conclusión en el artefacto
que genera otro gate — el JSON lo produce `[6/7]` del hook, y la cura que implementó ese plan fue
calcular el índice **en memoria** con `build_lesson_index.build()`, 0,30 s medidos). La elección ya está
tomada en el plan: C **no** decide de nuevo, **implementa** (b) y publica su costo:

- `VENCIDO` es **estado producido por el check propio de C**, no por un `--check` ajeno. (Con la ruta
  (a) este estado habría desaparecido y AC11 pediría tres estados a un diseño de dos — razón de cerrar
  la elección aquí y no en la sesión.)
- **Prohibida la tercera vía**: leer el JSON confiando en que otro paso lo regeneró. **Que el archivo
  exista no es que esté fresco.**
- **Tres causas, tres tests, ninguna colapsable** (R2.9): `AUSENTE` (no hay archivo en la ruta buscada →
  imprime ruta y comando de regeneración) ≠ `VENCIDO` (existe y se lee, pero el check propio no lo
  aprueba → imprime qué lo venció y el comando) ≠ `LECTOR-FALLIDO` (existe pero revienta al parsear →
  imprime el motivo). Un JSON roto **jamás** devuelve «sin candidatos».
- **Coste declarado:** C es responsable de su suelo y hace dos lecturas del JSON por corrida (la del
  check y la del consumo) en lugar de heredar un verde.

**Archivos afectados**: `scripts/triage_lesson_relevance.py` (nuevo),
`tests/quality_gates/lesson_relevance/` (nuevo).

**Criterios de aceptación**: **AC11** (`index_status`; `AUSENTE` imprime la ruta buscada y el
comando de regeneración; `VENCIDO` imprime qué check del hook lo detecta) y **AC10** (artefacto
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`, `anchored_after`, `removed: []` y un
test que lo afirma).

### Tarea 2: Juicio de pertinencia aditivo, con umbral declarado

**Objetivo**: por candidato no capitalizado, una pregunta binaria a través de `decision_client.py`;
separar `propuesto` de `a-revisar-humano` por confianza. **Nunca autofiltrar.**

**Forma de la pregunta — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E1)⟧: `choice` de dos
opciones, y la confianza es un campo distinto de la probabilidad de sí.** Confirmado contra
`scripts/decision_client.py` (no contra su docstring): `RespuestaEleccion` lleva `eleccion` +
`probabilidades` sobre **todas** las opciones + **`confidence` obligatoria**, mientras `RespuestaNoul`
lleva solo `probabilidad_si` con **`confidence = None` y su `confidence_motivo`** — la primitiva no la
expone y la puerta la **prohíbe** ahí. Por eso:

- La pregunta de pertinencia **no** se formula como `noul`. Con `choice` de dos opciones se obtienen
  **los dos números por separado**: cuánto se inclina por «pertinente» y con cuánta confianza leyó la
  pregunta. Son cosas distintas y el AC12 pide una de las dos.
- El `threshold` se aplica a **`confidence`**, y su `basis` **nombra el campo**. Umbral sobre
  `probabilidad_si` = cerrar AC12 con una métrica que el AC no describe.
- Publicar ambos es válido y deseable (`por_si` y `confidence` en cada candidato); **equipararlos, no**.

**Qué se hace con lo propuesto — ⟦RESUELTA el 2026-09-23 (orden §4.C / contrato E3)⟧: nada en
automático.** Un candidato que sale del proveedor **falso** prueba la mecánica del camino, no que la
lección sea pertinente. Se va a `a-revisar-humano` y **sólo** entra en §2 del `00-` tras **revisión
humana explícita**, dejando **aceptación o rechazo registrados con quién lo decidió**. Un rechazo se
publica con su motivo: una fila de §2 no desaparece (AC10). El script **no** escribe §2.

**Criterios de aceptación**: **AC12** (clave `threshold` con `value`, `basis` —que nombra
`confidence`—, `action_below`) y **AC14** (mutation check sobre el símbolo real que impide el
filtrado: desactivado el guard, el test de AC10 debe ponerse rojo; evidencia en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`).

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

⟦Reafirmado el 2026-09-23 como contrato E4, para que no dependa de leer este párrafo⟧: **está
prohibido simular la aceptabilidad con el proveedor falso** para poder cerrar AC15 en verde. El
`acceptance` es el disparador medible de una deuda ajena (D6); fabricarlo convertiría un número
pendiente en evidencia falsa y, peor, abriría un lint semántico sobre una base que nunca juzgó nada.
Lo que C entrega aquí es la parte **no semántica** de AC15 —población, términos con sus ceros,
familias no juzgadas— y el `NO-EJERCITADO` con su motivo.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_triage_no_elimina_fila_anclada.py` | AC10; `removed == []` sobre §2 real de este plan |
| `test_triage_indices_ausente.py` | `AUSENTE` con ruta y comando; no «sin candidatos» |
| `test_triage_indices_vencido.py` | `VENCIDO` producido por **el check de frescura propio de C** (⟦E2⟧), no por un `--check` ajeno: árbol movido después de la última regeneración → `VENCIDO` con qué diff lo venció |
| `test_triage_indices_lector_fallido.py` | ⟦tercera causa, añadida el 2026-09-23⟧ JSON existente pero ilegible (roto / no-JSON) → `LECTOR-FALLIDO` con el motivo; **no** es `AUSENTE` ni `VENCIDO` ni «sin candidatos» |
| `test_triage_pregunta_es_choice_y_no_noul.py` | ⟦E1⟧ la pregunta de pertinencia se construye como `choice` de dos opciones; `basis` del umbral **nombra `confidence`** y hay una aserción de que `probabilidad_si` **no** es el campo gobernado |
| `test_triage_propuesta_no_escribe_seccion_dos.py` | ⟦E3⟧ con proveedor falso, una propuesta **no** toca `00-lecciones-capitalizadas.md` §2: va a `a-revisar-humano`, y el rechazo/aceptación queda registrado con quién lo decidió |
| `test_triage_umbral_publicado.py` | AC12 con valor, base y acción por debajo |
| `test_triage_corpus_real.py` | AC13, con `skipif` visible; la evidencia dice si corrió |
| `test_triage_acceptance_no_es_simulado.py` | ⟦E4⟧ sin proveedor real, `acceptance == NO-EJERCITADO` con su motivo; el test falla si la fase fabrica un número con el falso |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/lesson_relevance -v
./venv/Scripts/python.exe scripts/triage_lesson_relevance.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --report
./venv/Scripts/python.exe scripts/validate_lesson_capitalization.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

*(Tabla reemplazada el 2026-09-23: la versión de la concepción listaba cinco tests y ninguno cubría la
tercera causa del índice, la forma `choice` del umbral, el bloqueo de escritura en §2 ni la no-simulación
de `acceptance`.)*

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-C ✅ con fecha y notas.
2. `README.md` — progreso y estado real de AC10–AC15.
3. `06-checklist-implementacion.md` — casillas correspondientes.
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D, E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas, métricas reales,
   seguimientos, decisiones (incluida la de **no** dejar que el triaje filtre, y su alternativa rechazada).
6. `00-lecciones-capitalizadas.md` — ⟦RESCRITO el 2026-09-23 por la orden §4.C / contrato E3; la
   versión anterior mandaba «aplicar los candidatos que el triaje proponga», y esa instrucción ya **no**
   está vigente⟧. **El triaje se corre sobre el `00-` de este propio plan y se publica, pero sus
   propuestas no entran en §2 por sí solas.** Con proveedor **falso** una propuesta prueba la mecánica
   del camino, no que la lección sea pertinente; escribiría en §2 una fila cuya evidencia es sintética,
   que es justo lo que AC15 declara `NO-EJERCITADO`. El paso es ahora:
   - el script emite el informe con `propuesto` / `a-revisar-humano` y **no edita §2**;
   - cada propuesta recibe **revisión humana explícita**, y su **aceptación o rechazo queda registrada
     con quién la decidió** (fecha + motivo);
   - **aceptada** → entra en §2 con dueño y «qué cambia» reales, citando la revisión que la avala;
     **rechazada** → se publica el rechazo con su motivo. Una fila citada y no aplicada se marca como
     tal, **no se borra** (AC10);
   - en §4 se registra que el plan se auto-trió, con el conteo de propuestas aceptadas y rechazadas y su
     carácter de proveedor falso.
   Y una corrección de forma que este cierre dejó escrita: la guarda que el README publicaba sobre
   `validate_governance_numbers.py --report` **sin destino** quedó **sin efecto** al aceptarse **S12**
   (bloque A de la orden, `fdd397f`) — hoy imprimir sin escribir es el comportamiento por defecto. La
   regla general de la lección **L-VCF-12** sigue en pie.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-C \
  --desc "triage_lesson_relevance.py: capa de pertinencia aditiva sobre el indice, umbral publicado y denominador (AC10-AC15)" \
  --archivos-mod "scripts/triage_lesson_relevance.py,tests/quality_gates/lesson_relevance" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] `ac10_delta.json` muestra `removed: []` y hay un test que lo afirma (AC10).
- [ ] Los **tres** estados del índice tienen su test nombrado por la causa; ninguno cubre dos:
      `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO`. ⟦E2, 2026-09-23⟧ `VENCIDO` lo produce **el check de
      frescura propio de C**, no el `[6/7]` del hook, y `LECTOR-FALLIDO` no se colapsa con `AUSENTE`.
- [ ] `mutation/` tiene rojo y verde del guard de no-filtrado (AC14). Sin rojo, ⚠️.
- [ ] `r26.txt` declara si el test contra corpus real **corrió** o se saltó, con el motivo (AC13).
- [ ] `coverage.json` tiene población, términos usados con sus conteos (ceros incluidos), familias
  no juzgadas y `acceptance` real o `NO-EJERCITADO` con motivo (AC15).
- [ ] ⟦E1⟧ El umbral de AC12 está aplicado a **`confidence`** de una pregunta `choice` de dos opciones,
  su `basis` **nombra el campo**, y hay prueba de que `probabilidad_si` no gobierna el umbral.
- [ ] ⟦E3⟧ Ninguna propuesta del proveedor falso entró en §2 sin **revisión humana explícita**; cada
  aceptación y cada rechazo están registrados con quién los decidió, y el script no editó §2.
- [ ] Con proveedor falso, AC15 está en ⚠️, su `acceptance` es `NO-EJERCITADO` con el motivo **y no se
  simuló ninguna cifra** (⟦E4⟧); **D6 quedó declarada dormida** en `dependencias-fases.md`.
- [ ] ⟦E5⟧ C cerró **sin** aplicar las mejoras generales de la orden de calidad: sigue leyendo el
  workflow canónico vigente, no renumeró checks y no tocó el proceso común.
- [ ] `validate_lesson_capitalization.py` sigue verde sobre `00-lecciones-capitalizadas.md` **después**
  de aplicar solo los candidatos **aceptados** (AC18).
- [ ] `--quick` verde sin haber alterado su composición (AC16).
- [ ] Post-ejecución completa e índice regenerado en el mismo commit.

## Restricciones

- **El triaje propone; jamás descarta.** Ningún camino del código elimina una fila de §2 (AC10).
- ⟦E3, 2026-09-23⟧ **Y tampoco escribe §2 por su cuenta.** Proponer y aplicar son dos pasos: la aplicación
  exige revisión humana con su aceptación o rechazo registrado.
- No modificar `build_lesson_index.py`, `validate_lesson_capitalization.py`,
  `validate_governance_numbers.py`, `decision_client.py` (consúmalos), `.agents/**`,
  `run_all_validations.py` ni el hook.
- No escribir sobre los §2 de **otros** planes, vivos o archivados: el triaje corre sobre el plan
  que se le indique por argumento y su salida es un informe, no una edición.
- No enviar PII ni material del cliente de `REFACTOR-WHATSAPP` a ningún proveedor. Las entradas
  salen del corpus de lecciones del repo.
- ⟦Rectificada el 2026-09-23, porque contradecía el contrato⟧ **Cero red, en serio**: el contrato de
  ejecución no autoriza ninguna llamada real (§Permisos y §Regla de cero red), así que el «tope de 200
  llamadas por sesión» que publicaba esta fila **no es una licencia**: es el techo del `--report` contra
  el proveedor **falso** determinista, y sirve solo para acotar el costo de la corrida local. Si C
  necesita llamar a un servicio real, **para y deja checkpoint** (deuda D7, fuera de este plan).
- No commitear ni empujar sin instrucción literal.

**Deuda que C NO resuelve y no debe tomar como bloqueante** (⟦declarado el 2026-09-23⟧): **S10** (dónde
vivirá el `import` del SDK cuando D7 se active) y **D7** (activar el proveedor) son del tramo que
consume un proveedor **real**; **D6** está condicionada al `acceptance` semántico, que aquí es
`NO-EJERCITADO`. C cierra con proveedor falso **por diseño** del plan, y ninguna de las tres bloquea su
ejecución offline.

## Prompt de ejecución

```text
Ejecuta únicamente FASE-C del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Antes de la primera edicion: mide git status --porcelain, git rev-parse --short HEAD y la paridad con
origin/master con los comandos que publica el bloque «Inicio de la siguiente sesion» del README, y
re-medide el indice con `python scripts/build_lesson_index.py --check`. No copies cifras de este prompt:
son antecedentes fechados y la medicion A6 las mueve.
Lee 05-prompt-inicio-sesion-fase-C.md, 01-plan-maestro.md §1 (la medicion del grep con cero
coincidencias) y §4 (AC10-AC15, AC16, AC18) y §2 (las cuatro filas enmendadas el 2026-09-23),
04-contrato-ejecucion.md (permisos, regla de cero red y la seccion «Enmiendas prospectivas ya resueltas
para FASE-C» E1-E5), 00-lecciones-capitalizadas.md §1-§4, dependencias-fases.md (su fila de C y la
§Conciliacion) y el workflow canónico vigente.
Heredas de A los tres estados y coverage_basis, y de B la costura decision_client.py como unica
puerta al proveedor: no importes el SDK.
Escribe scripts/triage_lesson_relevance.py. Suelo determinista: .opencode/lecciones_index.json, pero
**C ejecuta ella misma la comprobacion de frescura antes de apoyarse en el** (E2; prohibido confiar en
que [6/7] del hook lo regenero). Distingue AUSENTE / VENCIDO / LECTOR-FALLIDO como tres causas con su
test cada una: un lector roto jamas devuelve «sin candidatos» y VENCIDO no es AUSENTE. Propone
candidatos de pertinencia que el Paso 0 no anclo. Es ADITIVO por construccion: ninguna fila de §2
puede desaparecer (AC10, con su test y su delta publicado) y el script tampoco escribe §2 (E3).
Pregunta binaria como `choice` de dos opciones, nunca `noul` (E1): el umbral de AC12 se aplica a
`confidence`, con `basis` que nombra el campo. **La probabilidad de si no es confianza**: son dos
numeros distintos y `RespuestaNoul` no expone confidence. Publication del umbral con valor, base y
accion por debajo. Mutation check sobre el simbolo real que impide el filtrado, con rojo y verde en
evidencia (AC14). Al menos un test contra planes reales de Archives/ con skipif visible, y la evidencia
dice si corrio o se salto (AC13).
Denominador con poblacion, terminos usados incluidos los ceros, familias no juzgadas y acceptance
(AC15). Como no hay proveedor activo, ejercita la mecanica con el proveedor falso determinista y
publica acceptance = NO-EJERCITADO con el motivo: **no simules una aceptabilidad con el falso** (E4);
AC15 queda en ⚠️ y la deuda D6 sigue dormida en dependencias-fases.md. No abras el lint de
contradicciones sobre una base que nunca juzgo nada.
Las propuestas del falso van a `a-revisar-humano` y **solo entran en §2 tras revision humana explicita,
con su aceptacion o rechazo registrado** (fecha, motivo, quien decidio). El rechazo se publica; una fila
no se borra.
C conserva el workflow canonico y el proceso comun vigentes (E5): no apliques las mejoras generales de
ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md. Sus bloques B y C estan **diferidos, no aplicados ni
cerrados**. No renumeres checks: quick 11 y hook 7, delta 0 (AC16).
Cero red en serio: si necesitas llamar a un servicio real, para y deja checkpoint (es la deuda D7,
fuera de este plan). No toques build_lesson_index.py, validate_lesson_capitalization.py,
validate_governance_numbers.py, decision_client.py, .agents/, run_all_validations.py, el hook ni ningun
plan vivo. Regenera el indice de lecciones en el mismo commit y registra la fase con
log_phase_completion.py. Deja checkpoint si falta autorizacion.
```
