# Briefing pack — FASE-C

> **Artefacto generado. NO editar a mano.** Regenerar con:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
> La frescura la gobierna el sha256 de `sources[]` contra el arbol vigente:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check`.

- **plan**: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
- **fuente de lo declarado**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md` (bloque «Prompt de ejecucion»)
- **estado del pack**: `COMPLETO`
- **declaracion de lectura en el prompt**: `DECLARADA`
- **procedencia**: HEAD `6b02532` · generado `2026-09-26T16:04:13Z`
- **tokens**: estimados por divisor 4, no recuento de tokenizer

## Lectura aparte obligatoria (el pack **no** la sustituye)

- `.agents/workflows/phased_project_executor.md` — 108017 bytes (~27004 tokens). se lee aparte mientras la deuda **D3** no rebane el workflow por fase; copiarlo aqui seria rebanar `.agents/` por la puerta de atras (AC17).

## Que **no** incluye este pack

- 01-plan-maestro.md — 9879 bytes fuera de lo declarado (1, 4, 2)
- 00-lecciones-capitalizadas.md — 10426 bytes fuera de lo declarado (1, 2, 3, 4)
- dependencias-fases.md — 42883 bytes fuera de lo declarado (Conciliacion)

---

# Contenido declarado, copiado de su fuente

## Fuente: `05-prompt-inicio-sesion-fase-C.md` (documento completo)

# FASE-C — Capa de pertinencia sobre el índice de lecciones (aditiva, nunca filtro)

> **Estado de este prompt al 2026-09-24: CONTRACTUALMENTE PREPARADO, NO EJECUTADO.** FASE-C sigue
> siendo la sesión siguiente y **no** se corrió ni al conciliar FASE-B ni al redactar las enmiendas del
> bloque C de la orden de calidad. Contiene cinco enmiendas
> prospectivas ya resueltas por este plan (**E1–E5** en `04-contrato-ejecucion.md`, orden de calidad
> §4.C, con autorización local del operador sobre CONTEXTO/C): la elección de fuente de **AC11 está
> cerrada en la ruta (b)**, la pregunta binaria es **`choice` con `confidence` independiente**, las
> propuestas del proveedor falso **no** entran en §2 sin **revisión humana registrada**, el tramo
> semántico de **AC15** sigue `NO-EJERCITADO` con **D6 dormida**, y **C conserva el workflow canónico y
> el proceso común vigentes**. ⟦Actualizado el 2026-09-24⟧ el **bloque B está concluido
> contractualmente por su matriz §13** y el **bloque C de esa orden quedó autorizado solo como
> enmiendas prospectivas sobre los documentos de los cuatro planes**; **el piloto FASE-C —es decir,
> ejecutar este prompt— sigue sin autorización**. Fuente única de resultados y estados B/D1/S13:
> `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
> **§13, única matriz vigente**; §1–§12 y los dictámenes anteriores quedan como antecedentes
> rectificados, no aceptación actual. Evidencia de las enmiendas:
> `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`. Donde
> una instrucción de este archivo contradiga ese párrafo, manda el párrafo y está mal conciliado: decirlo.
>
> **Reconfirmación contra el cliente real (2026-09-24, sin renegociar).** E1 y E2 se volvieron a
> contrastar con `scripts/decision_client.py` y su forma sigue siendo la que asumen: `RespuestaEleccion`
> exige `confidence` en su validación y `RespuestaNoul` la fija en `None` con la puerta **rechazando**
> que un `noul` la reporte. Ninguna de las cinco enmiendas se mueve; lo que cambió en este bloque es lo
> que la fila `CONTEXTO/D` y `CONTEXTO/RELEASE` pedían, no la forma de la pregunta ni el destino de las
> propuestas.

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
4. `09-documentacion-post-proyecto.md` — Secciones A, B, D (fuente de métricas con enlace a la evidencia), E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas (o «sin lecciones nuevas»),
   análisis del delta por referencia a `09` §D, sin transcribir cifras; seguimientos y decisiones
   (incluida la de **no** dejar que el triaje filtre, y su alternativa rechazada).
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
- [ ] Post-ejecución completa e índice regenerado y comprobado sobre el mismo árbol final verificado.
      El commit es opcional, posterior y requiere autorización explícita; no condiciona ninguno de
      los cinco cortes del proceso común.

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
C conserva el workflow canonico y el proceso comun vigentes (E5): el proceso comun que dejo el bloque B
de ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md, cuyo estado se lee en la matriz §13 de la fuente unica
citada al inicio, no en los dictamenes retirados. No apliques dentro de la fase ninguna otra mejora
general de esa orden: el bloque C de la orden autorizo enmendar documentos, no cambiar el gobierno del
proceso. Este prompt no se autoriza a si mismo: si tu mandato no nombra explicitamente la ejecucion del
piloto FASE-C, para y deja checkpoint. No renumeres checks: AC16 es delta
0 contra el par pre/post que mide la propia fase, y el numero lo imprime la corrida.
Cero red en serio: si necesitas llamar a un servicio real, para y deja checkpoint (es la deuda D7,
fuera de este plan). No toques build_lesson_index.py, validate_lesson_capitalization.py,
validate_governance_numbers.py, decision_client.py, .agents/, run_all_validations.py, el hook ni ningun
plan vivo. Regenera y comprueba el indice de lecciones sobre el mismo arbol final verificado y registra
la fase con log_phase_completion.py. Los cinco cortes no requieren commit: es opcional, posterior y
necesita autorizacion explicita. Deja checkpoint si falta autorizacion.
Al cerrar, reconcilia la seccion §6 de ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md por referencia: la
casilla del piloto se cierra con la evidencia de esta fase (instrumento, unidad declarada y limites),
y marca expresamente que ni los cuatro planes ni sus deudas externas (D2, D3 completa, D6, D7, S10)
quedan terminados por haber corrido el piloto. No re-transcribas cifras: enlaza a 09 §D y a tu evidencia.
```


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md` · sha256 `ea361c4696797a9a36df482636378040e57c20797af5ec6efd1ef8fc37df0832` · 27571 bytes copiados de 27571 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `01-plan-maestro.md` §1

## 1. Medición que justifica el plan (no suposición)

**Estado del bloque B: consultar §13 de la fuente única enlazada abajo.** Está concluido
contractualmente por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes — **el piloto FASE-C de
este plan no lo está y no se ejecutó**. Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Las mediciones A1–A8 y el contrato original de FASE-A se conservan como históricos; no certifican
el árbol actual ni obligan a reproducir el rojo A1–A4 fuera de su contraejemplo congelado.

Cuatro aserciones sobre cuántos checks corren estaban vencidas al concebir el plan respecto del código que
las ejecutaba. Medido en aquella sesión con `grep -oE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py`
(fuente dinámica de verdad) contra lo que el workflow y el template afirman (texto estático).
**La lectura útil de ese grep no es la lista de etiquetas: es a qué `def _check_*` pertenece cada
una** — sin ese emparejamiento se confunde la del check de dependencias con la del write-back
(fue exactamente lo que pasó aquí, ver la nota de abajo).

| # | Aserción en documento de gobierno | Lo que dice | Lo que mide el código | Estado |
|---|-----------------------------------|-------------|------------------------|--------|
| A1 | `phased_project_executor.md`, párrafo «Verificador mecánico» de R2.2 | `validate_plan_citations.py` es «check **8** de `run_all_validations.py --quick»` | lo invoca `def _check_plan_citations`, que imprime `[9/11]` | **VENCIDA** |
| A2 | `phased_project_executor.md`, §0 «Verificación mecánica del output» | capitalización es check «`[9/9]»` de `--quick` | lo invoca `def _check_lesson_capitalization`, que imprime `[10/11]` | **VENCIDA** |
| A3 | `phased_project_executor.md`, párrafo «Verificador mecánico» de R2.10 | el write-back de QMind es check «`[12/12]»`, fuera de `--quick` | lo invoca `def _check_qmind_writeback`, que imprime `[15/15]` | **VENCIDA** |
| A4 | `templates/lecciones-capitalizadas-template.md` §4 | el verificador es «`[7/7]` del hook y `[10/10]` de `--quick`» | `[7/7]` **correcto** contra `scripts/git_hooks/pre-commit`; `[10/10]` **vencido** contra `[10/11]` | **PARCIAL** |

Lo que esto prueba no es que los números estén mal: es que **una aserción sobre un conteo no
sostenida por ningún check se desfasa sola**, y que el defecto ya tiene nombre en el corpus
(L-R.1, L-NC10). A4 es la señal más incómoda: el template cuyo §4 obliga a *declarar la
cobertura* lleva él mismo una cobertura vencida.

> **Rectificación datada (auditoría de la concepción, 2026-09-20).** La primera versión de esta
> fila publicaba como observado de A3 «la etiqueta real en el modo completo es `[12/15]` (total 15,
> no 12)». **Era falsa:** `[12/15]` es la etiqueta que imprime `def _check_dependencies`, no la del
> write-back. Re-medido dos veces (grep de las etiquetas de `run_all_validations.py` y lectura del
> método que imprime cada una) y corroborado por `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, que
> documenta el write-back como check `[15/15]`. El plan que existe para cazar aserciones vencidas
> publicó una vencida sobre su propia medición: es A6 golpeando al maestro §1, y la corrección se
> hizo aquí y en `10-analisis-post-implementacion.md` en la misma sesión.

> **A8 — la población bajo el patrón es mucho mayor que las cuatro aserciones.** Medido el
> 2026-09-20 sobre los documentos de gobierno: `grep -rnoE '\[[0-9]+/[0-9]+\]' .agents/` devuelve
> **22 instancias repartidas en 17 líneas** (16 del workflow y 1 del template) y
> `grep -rnoE 'check [0-9]+' .agents/` devuelve **2 sitios** con la forma «check 8». Las cuatro
> aserciones de la tabla viven en cuatro de esas líneas; el resto son `[6/7]` y `[7/7]` **correctos
> hoy**, y menciones **históricas congeladas a propósito**: el propio workflow, en la entrada
> `v2.24.0` de su changelog, declara que «las 5 referencias normativas al `[6/6]` se actualizan a
> `[6/7]` y las **4 menciones históricas** de medición (dos en R2.10, dos en el changelog) se
> conservan literales», y el changelog conserva además `[5/5]`, `[4/5]` y un `[9/9]` de su propia
> época. Consecuencia para el diseño: **AC1 no puede decir «exactamente A1–A4 y ninguna otra» sin
> una regla de población** que distinga aserción normativa viva, mención histórica congelada y
> verificación correcta; sin esa regla, un verificador que descubra sus aserciones escaneando (como
> exige L-NC10) produce más de cuatro hallazgos y el test se pone rojo por diseño, no por defecto.
> La regla y su publicación están en §4, AC1 y AC2.

Y dos mediciones más, obtenidas al redactar los propios artefactos de este plan:

> **A5** — `grep -icE "verificador mec" .opencode/LECCIONES-INDEX.md` devolvió **0** sobre un
> corpus donde sí existen verificadores nombrados. Un cero de grep **no distingue** «no existe» de
> «usé la palabra equivocada». La capa fría del Paso 0 es, por construcción, ciega a la pertinencia
> y frágil al término. Población medida del índice: 320 IDs con definición, 50 citados sin
> definición, 15 análisis + 36 `CONTEXT-*.md` y **402** `.md` como corpus de citas.

> **A6** — Al escribir este plan, esas tres últimas cifras **se volvieron vencidas contra sí
> mismas**: este maestro, su `00-`, su `05-…-fase-C.md` y su `09-` citaban 14 análisis, 49 IDs sin
> definición y 389 `.md` cuando el índice regenerado tras crear los archivos del plan pasó a decir
> 15, 50 y 401. La medición quedó refutada por el acto de reportarla. No es una anécdota: es el
> argumento más fuerte del plan, porque demuestra que **copiar una cifra de una fuente dinámica a un
> documento estático vence la aserción sin que nadie la edite**, y que la cura es un verificador o
> un writer, no el corrector. Las cifras de este documento son las re-medidas tras la regeneración y
> caducan la próxima vez que alguien escriba un `.md` con un ID. **Y caducaron otra vez dentro de la
> misma concepción**: al escribirse el prompt de FASE-D, el corpus de citas pasó de 401 a **402** `.md`
> y esta sección tuvo que re-medirse por segunda vez en la misma sesión.

### A7 — la carga de lectura de una sesión de fase

Medida al diagnosticar por qué la ejecución de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` resulta lenta.
Documentos medidos: **los de ese plan** (la sesión de su FASE-B) más el workflow canónico que esa
misma sesión declara leer. Comando literal: `stat -c %s` sobre cada documento que el prompt de la
fase declara leer, sumado. Tokens **estimados por divisor 4** — estimación declarada, no recuento de
un tokenizer.

La lista de lectura declarada son **ocho lecturas**: los siete documentos de la tabla y un archivo de
evidencia de FASE-0 (`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-0/resultados-y-observaciones.md`,
16.758 bytes) que **no entra en la suma**, como declara el pie de la tabla.

| Documento que la fase declara leer | Bytes al concebir | Bytes re-medidos 2026-09-20 | ~Tokens (re-medido) |
|---|---|---|---|
| `.agents/workflows/phased_project_executor.md` (workflow canónico) | 98.694 | 98.694 | 24.673 |
| `01-plan-maestro.md` | 64.031 | 64.031 | 16.008 |
| `06-checklist-implementacion.md` | 25.712 | **30.316** | 7.579 |
| `00-lecciones-capitalizadas.md` | 25.334 | **27.324** | 6.831 |
| `dependencias-fases.md` | 22.687 | **24.245** | 6.061 |
| `04-contrato-ejecucion.md` | 9.033 | 9.033 | 2.258 |
| `05-prompt-inicio-sesion-fase-B.md` | 8.519 | **10.330** | 2.583 |
| **Total, sin `evidence/` ni código** | **254.010** | **263.973** | **≈65.993** |

**A7 venció el mismo día en que se concibió el plan.** Los cuatro documentos en negrita crecieron
**+9.963 bytes** porque las fases `G` y `B` de `REFACTOR-WHATSAPP` se cerraron el 2026-09-20 y cada
cierre escribe en los archivos que la siguiente fase declara leer. Es la tercera vez que A6 se
cumple sobre este maestro y la primera vez que lo hace sobre un plan **ajeno al que se está
escribiendo**: la métrica de la premisa se mueve por el tráfico normal del plan medido. Por eso AC20
mide con el **mismo comando** en los dos lados y por eso el arranque de cada sesión ordena re-medir
antes de la primera tarea; el valor de referencia vigente es **263.973 bytes (≈65.993 tokens)**, con
su comando y su fecha, no 254.010.

**Lo que A7 dice**: ocho lecturas separadas contra un presupuesto de 60 `tool_use`, y cerca de un
quinto del volumen total en plantillas de documentación que una fase de implementación no consume.
**Lo que no dice**: que el cuello sea solo de tokens. La cadena es de doce fases secuenciales de una
sesión cada una y cada fase re-mide once validaciones; eso este plan **no lo toca**. FASE-D ataca la
mitad medible aquí y AC20 publica qué parte del delta consiguió realmente, incluida la posibilidad
de que sea cero.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 9218 bytes copiados de 51507 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `01-plan-maestro.md` §4

## 4. Criterios de aceptación

**Tabla de ACs** (forma que lee `validate_lesson_capitalization.py` en C4). Cada AC declara
**el artefacto y la clave donde un humano lo leería** (R2.4); el detalle sigue debajo.

| AC | Criterio | Artefacto e instrumento esperado |
|---|---|---|
| AC1 | `validate_governance_numbers.py` reproduce **las aserciones normativas vivas** —las cuatro de §1— y **ninguna otra** sobre árbol vigente, con la regla de población de A8 aplicada; A5, A6 y A7 quedan fuera de su alcance y son la motivación de FASE-C y FASE-D | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]` con `assertion_id`, `document`, `claimed`, `observed`, `occurrences[]` |
| AC2 | Publica denominador: población mirada, **regla de población y su exclusión histórica aplicada**, exenciones y familias no cubiertas | ídem → `coverage_basis` |
| AC3 | Expresa `SIN-HALLAZGOS` / `AUSENTE` / `LECTOR-FALLIDO` sin colapsar ninguno | ídem → `status` + tres tests por causa |
| AC4 | Mutation check **por aserción** sobre el símbolo real del guard | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con rojo y verde |
| AC5 | El conteo del quick y del hook se preserva como **delta 0** con par pre/post | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md` |
| AC6 | Ningún archivo fuera de la costura importa SDK ni adapter alguno | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` (conteo + población) |
| AC7 | Proveedor no configurado o respuesta ilegible fallan explícitos, nunca con decisión por defecto | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` → `provider_status` |
| AC8 | Contract test de forma con proveedor falso y versión pineada | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt` |
| AC9 | **Añadir un segundo proveedor es un cambio de un archivo**, demostrado con un proveedor falso adicional; ningún proveedor de pago se activa en este plan | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` → `files_changed_to_add_provider` |
| AC10 | El triaje **no elimina** ninguna fila anclada de §2 | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` → `removed: []` |
| AC11 | Índice ausente o vencido no se lee como «sin candidatos»; **`AUSENTE`, `VENCIDO` y `LECTOR-FALLIDO` son tres causas distinguibles y la frescura la comprueba el propio C** (⟦ruta (b) decidida 2026-09-23⟧) | ídem → `index_status` |
| AC12 | Umbral publicado con valor, base y acción por debajo, **aplicado a `confidence` de un `choice` de dos opciones** — no a `probabilidad_si` — y las propuestas van a **revisión humana**, no a §2 en automático (⟦decidido 2026-09-23⟧) | ídem → `threshold` |
| AC13 | ≥1 test contra corpus real archivado, con skip visible y declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` |
| AC14 | Mutation check sobre el guard real de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` |
| AC15 | Denominador del triaje con términos usados, ceros incluidos y familias no juzgadas, **más la aceptabilidad que dispara D6** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` |
| AC16 | El quick sigue en 11 checks y el hook en 7, en **todo** el plan | los cuatro `baseline-pre-post.md`, delta 0 |
| AC17 | `.agents/` intocado en escritura y límites de cobertura declarados | `coverage.json` → `families_not_covered[]` + `git status` sobre `.agents/` |
| AC18 | Capitalización, citas e índice verdes sobre los artefactos de este plan | salida de los tres verificadores sobre el mismo árbol final verificado (commit opcional posterior autorizado) |
| **AC19** | `build_phase_briefing.py` emite un pack por fase, **sin tocar `.agents/`**, declarando `no_incluye[]` y la lectura aparte obligatoria; **resuelve un plan también en su ruta archivada** (⟦bloque C 2026-09-24⟧: sin eso, el `--check` posterior al `git mv` del RELEASE no es ejecutable) | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` |
| AC20 | El **delta de carga total** de lectura se mide con el **mismo comando** antes y después, bytes exactos y tokens con el divisor declarado, contando **workflow obligatorio + coste de generar el pack + pack leído** (⟦bloque C 2026-09-24⟧ concatenar no es ahorrar) | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` + par pre/post con la resta |
| AC21 | Cada pack declara HEAD, fecha y sha por fuente; **la frescura la gobierna el sha de las fuentes relevantes, y HEAD es procedencia, no clave de caducidad** (⟦bloque C 2026-09-24⟧, para que el commit del propio generado no lo venza) | ídem → `provenance` ; prueba re-editando una fuente y re-midiendo en disco |
| AC22 | Sección declarada y no resuelta es un estado propio: **prohibido emitir un pack más corto en silencio** | ídem → `status ∈ {COMPLETO, SECCION-NO-RESUELTA, FUENTE-AUSENTE}` + tres tests |
| AC23 | Mutation check sobre el guard que impide el truncamiento silencioso | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/` con rojo y verde |

Un AC cuya clave no existe en el artefacto está incompleto **antes** de ejecutarse (R2.4).

### FASE-A — `validate_governance_numbers.py` (determinista, sin modelo)

- **AC1** — El script, invocado suelto, reproduce sobre el árbol vigente **exactamente** las
  cuatro aserciones de §1 y ninguna otra. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json`, clave
  `findings[]` con `assertion_id ∈ {A1,A2,A3,A4}`, `document`, `claimed`, `observed` y
  `occurrences[]` (sitios donde esa aserción está escrita).
  **Regla de población (A8 — sin esto AC1 es innavegable):** la familia de aserción es **la
  atribución resoluble**, una afirmación que liga un conteo a un check o documento **nombrado**,
  con el `claimed` que el texto sostiene. El escaneo encuentra **22 instancias `[N/M]` y 2 formas
  «check N»** en los documentos de gobierno; de esas, cada una cae en una de tres clases y la clase
  decide si es hallazgo:
  - **VIVA (normativa):** sostiene una regla vigente del propio documento. Debe cuadrar con la
    etiqueta que imprime el código; si no cuadra → **finding** (esto son A1, A2, A3 y el `[10/10]`
    de A4).
  - **CONGELADA (histórica):** mención de medición fechada, o dentro de una entrada de changelog.
    El **propio objeto auditado** declara esta clase: la entrada `v2.24.0` del workflow dice que
    «las 4 menciones históricas de medición (dos en R2.10, dos en el changelog) se conservan
    literales». No es hallazgo, **pero tampoco silencio**: se publica en `historical_excluded[]`
    con su conteo y la frase que la ampara (L-HF1: un candado que excluye sin decirlo es peor que
    un candado que falla).
  - **VIGENTE Y CORRECTA:**cuadra con la fuente (p. ej. `[7/7]` del hook, los `[6/7]` del índice).
    Entra en `assertions_checked` con su `observed`; no genera hallazgo.
  Un verde de AC1 sin las tres clases publicadas no informa: diría «el árbol está limpio» sobre una
  población que el script recortó a mano.
- **AC2** — El mismo artefacto publica denominador (L-R.3): clave `coverage_basis` con
  `documents_scanned`, `assertions_checked`, `families_not_covered[]`, y `excluded[]` con cuántos
  planes quedaron exentos y por qué. Ninguna salida `SIN-HALLAZGOS` puede emitirse sin esta clave.
  **Familias que NO cubre, declaradas y medidas el 2026-09-20** (la lista no es un «etcétera»):
  (i) prose de conteo sin patrón `[N/M]` ni «check N» («11 checks», «once validaciones» en prosa);
  (ii) aserciones de conteo **fuera de los documentos de gobierno**, que este plan no toca y que hoy
  también están vencidas — `AGENTS.md` («Validación final (10/10 checks en modo rápido; 14 en el
  completo)», que mide 11 y 15), `docs/GUIA_TECNICA.md` y `docs/contributing/REGISTRY.md` con sus
  «check 8»/`[9/9]`/`[10/10]` históricos; (iii) **los pins de conteo en `tests/`** (hay al menos
  `tests/test_validate_plan_closure.py`, que assertiona `[5/7]` dentro del hook); (iv) cualquier
  otra fuente dinámica que no sea una etiqueta impresa (umbrales, tamaños, conteos de tests).
  Las cuatro familias se listan con su medición de AC2 y **D1** decide sobre (i)–(iii); AC5/AC16
  barre (iii) al medir quién afirma el 11 y el 7 (L-V2.3).
- **AC3** — Los tres estados de R2.9 son legibles y **no colapsan**: `sin hallazgos` dice sobre
  qué midió; `ausente` dice la ruta buscada; `lector fallido` dice el motivo y **nunca** sale
  como favorable ni como 0. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` clave `status`, más tres
  tests nombrados por su causa, uno por estado.
- **AC4** — Mutation check (R2.8) sobre el símbolo real que guarda la detección, **por aserción**
  y no una vez por fase. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` con el rojo (guard desactivado) y
  el verde (guard activo). Sin el lado rojo, AC4 queda ⚠️ (R2.4). Un verde obtenido a la primera
  sin rojo previo se declara sospechoso (L-VUP-5). **Anclaje de la aserción (L-V2.1, medida en
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** mutar la guarda de A2 y obtener «un hallazgo»
  no prueba nada si otro guard produjo ese hallazgo; cada mutante se afirma sobre **el `assertion_id`
  y el mensaje de esa detección**, y el rojo debe nombrar la aserción mutada.
- **AC5** — El plan no altera ningún conteo: `run_all_validations.py --quick` sigue en 11 checks
  y el hook en 7, formulado como **delta** con par `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/*_baseline_pre.txt` /
  `*_baseline_post.txt` y la resta comprobada (R2.3, R2.7, L-D3, L-V2.3). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/baseline-pre-post.md`, delta esperado **0**; una resta 0 con tests nuevos
  declarados = baseline contaminado y la fase no cierra en ✅.

### FASE-B — `decision_client.py` (costura de proveedor neutro)

- **AC6** — Ningún archivo fuera de `decision_client.py` importa el SDK del proveedor ni el
  adapter. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/import_scanner.txt` con el conteo de coincidencias y la
  población escaneada (AC2 aplica: 0 sin denominador no es prueba).
- **AC7** — Proveedor no configurado **falla abierto a error explícito**, nunca a un resultado
  por defecto que pudiera leerse como decisión. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/informe.json` clave
  `provider_status ∈ {RESUELTO, NO-CONFIGURADO, ILEGIBLE}`, con un test por estado (R2.9).
- **AC8** — Un contract test con proveedor falso fija la **forma** de la respuesta (elección,
  score, binario, confianza, probabilidades) y la versión de modelo pineada. Subir el SDK sin
  tocar la costura debe romper este test, no a las fases. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/contract.txt`
  con el nombre del test y su salida. Prohibido pinear literales del conteo (L-V2.3).
- **AC9** — Con un solo proveedor en este plan, lo certificable no es «cuál gana» sino que **añadir
  el segundo sea un cambio de un archivo**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/costura.json` clave
  `files_changed_to_add_provider` (debe ser `1`, o explicarse) y `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/extensibilidad.txt`
  con el test que registra un **proveedor falso adicional** a través de la costura sin tocar ningún
  otro archivo. La comparación real entre proveedores queda como deuda **D7**: un AC que exigiera
  medirla ahora se cerraría declarando `NO-EJERCITADO` y certificaría humo.

### FASE-C — `triage_lesson_relevance.py` (capa de pertinencia, aditiva)

- **AC10** — El triaje es **aditivo por construcción**: ningún ID ya presente en §2 de un plan
  puede desaparecer. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/ac10_delta.json` con `anchored_before`,
  `anchored_after`, `removed` que **debe** ser `[]`; y un test que lo afirma.
- **AC11** — El suelo determinista es `lecciones_index.json`. Si falta, está vencido o no se puede
  leer, el script **no** emite «no hay candidatos»: emite `AUSENTE`, `VENCIDO` o `LECTOR-FALLIDO` con la
  ruta buscada y el comando de regeneración (L-PF6, L-PF10). Artefacto: clave `index_status` + tres
  tests, uno por causa.
  **Fuente de la decisión (Knowledge Center, `L-V2.2` de
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** «un verificador no debe apoyar su conclusión en
  el artefacto que genera otro gate» — ese plan lo capitalizó porque leer el JSON era lo obvio y el
  JSON lo produce `[6/7]`; la cura que implementó fue **calcular el índice en memoria** con
  `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — la elección queda CERRADA, no abierta para C⟧**
  **FASE-C elige la ruta (b): consumir el JSON con su propia comprobación de frescura.** Ya no hay
  elección que la sesión de C tenga que tomar; lo que tiene que implementar es esto, con su costo
  declarado:
  - C **ejecuta ella misma** la comprobación de frescura contra el árbol y a partir de ahí emite su
    estado. **`VENCIDO` es producto del check propio de C**, no de un `--check` ajeno, y por eso el
    estado sigue vivo (a diferencia de la ruta (a), que lo habría borrado).
  - **Prohibida la tercera vía**: leer el JSON confiando en que otro gate (el `[6/7]` del hook o la
    sesión anterior) lo regeneró. Que el archivo exista no es que esté fresco.
  - **Coste aceptado:** C es responsable de su suelo —si el árbol se movió después de la última
    regeneración, C lo dice aunque el hook esté verde— y mide dos lecturas del mismo JSON por corrida
    (la suya y la del check) en lugar de heredar un verde.
  - **Tres causas distinguibles, ninguna colapsable** (R2.9, y aquí con nombres propios porque el
    prompt las pide separadas): **`AUSENTE`** = no hay archivo en la ruta buscada → imprime la ruta y
    el comando de regeneración; **`VENCIDO`** = el archivo existe y se lee, pero **el check de frescura
    propio de C** no lo aprueba → imprime qué diff lo venció y el comando; **`LECTOR-FALLIDO`** = el
    archivo existe pero revienta al parsear o no es legible → imprime el motivo. **Un JSON roto jamás
    produce «sin candidatos» y `VENCIDO` no es `AUSENTE`.**
- **AC12** — El umbral de confianza se publica **con su valor y su efecto**, y los candidatos se
  separan en `propuesto` y `a-revisar-humano`. Ningún camino del código auto-filtra una lección.
  Artefacto: clave `threshold` con `value`, `basis`, `action_below`.
  - **⟦ENMENDADA el 2026-09-23 por la orden de calidad §4.C — forma de la pregunta binaria⟧**
  **La pregunta de pertinencia se formula como `choice` de dos opciones, no como `noul`.** Forma
  confirmada contra `scripts/decision_client.py` (no contra su documentación): `RespuestaEleccion`
  trae `eleccion` + `probabilidades` sobre **todas** las opciones + **`confidence` obligatoria**,
  mientras `RespuestaNoul` trae solo `probabilidad_si` y **`confidence = None` con su
  `confidence_motivo`** — la primitiva no la expone, y la puerta la **prohíbe** ahí.
  **Consecuencia operativa, que es el punto de la enmienda: la probabilidad de sí no es confianza y
  no pueden usarse indistintamente.** El `threshold` de AC12 se aplica a **`confidence`** (cuán seguro
  está el proveedor de haber leído bien la pregunta), y **`basis` debe nombrar el campo**; un umbral
  declarado sobre `probabilidad_si` sería otra cosa — cuánto se inclina por «sí» — y cerraría AC12 con
  una métrica que no es la que el AC describe. Publicar los dos números separados es válido y
  recomendado; **equipararlos, no**.
  - **⟦ENMENDADA el 2026-09-23 — qué se hace con las propuestas⟧**
  **Las propuestas del proveedor falso prueban mecánica y no entran en §2 en automático.** Con `D7`
  sin activar, quien contesta es un proveedor **falso determinista**: lo que su respuesta demuestra es
  que el camino funciona (aditividad, estados, umbral), **no** que la lección propuesta sea pertinente.
  Por eso ninguna fila propuesta puede escribirse en `00-lecciones-capitalizadas.md` §2 por el propio
  script ni por el cierre de la fase: **cada propuesta exige revisión humana explícita, y su
  aceptación o rechazo queda registrada con quién la decidió** (aceptada → entra con dueño y «qué
  cambia» reales; rechazada → se publica el rechazo con su motivo, no se borra). Esto es AC12 en su
  parte de `a-revisar-humano`, es AC10 (aditividad) del lado del documento, y es la familia de
  `VACUOUS_RECALL` que la matriz §2 ya descartó: **un verde con proveedor falso no es evidencia de
  pertinencia.**
- **AC13** — ≥1 test contra **corpus real archivado**, no contra fixture propio (R2.6). El skip
  por baseline ausente es `pytest.mark.skipif` explícito y la evidencia declara **si el test
  corrió o se saltó**. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` con el nombre del test y su marcador.
- **AC14** — Mutation check (R2.8) sobre el guard real de AC10 y AC11, con las dos salidas en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`.
- **AC15** — Denominador propio y **términos usados**: el artefacto imprime a cuántos de los 320
  IDs aplicó juicio, sobre qué población, con qué términos de búsqueda, y el conteo que arrojó la
  capa fría con esos términos (incluidos los ceros como en A5). Sin esto, el triaje repite el
  defecto que pretende curar. Publica además **aceptabilidad**: `acceptance` = candidatos propuestos
  que resultaron pertinentes sobre el total propuesto, con su muestra y su método. Ese número es el
  **disparador de la deuda D6** y lo único que decide si el lint de contradicciones se abre en este
  directorio o en uno nuevo. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json`.
  - **⟦DECLARADO el 2026-09-23 (orden §4.C): el tramo semántico de AC15 permanece NO-EJERCITADO, con
    motivo⟧** — y no es un descuido ni un ⚠️ prestado: con `D7` sin activar el único emisor de juicio es
    un proveedor **falso**, así que `acceptance` se publica como `NO-EJERCITADO` con el motivo literal y
    **D6 sigue dormida**. No se abre un lint de contradicciones semánticas sobre una base que nunca juzgó
    nada, y **no** se reemplaza el número por una aceptabilidad simulada con el falso para poder cerrar
    el AC: eso convertiría el disparador de una deuda en una cifra fabricada. Lo que C **sí** cierra con
    el falso es la mecánica —aditividad (AC10), estados del índice (AC11), umbral publicado (AC12),
    mutation check (AC14) y denominador con términos y ceros (AC15, su parte no semántica)— y lo que no,
    se declara con su nombre. **Re-evaluar D6 toca cuando exista un proveedor real, no antes.**

### FASE-D — `build_phase_briefing.py` (pack derivado y delta de lectura)

- **AC19** — El generador recorre los prompts de fase del plan, extrae la lista de lectura que cada
  uno **declara**, resuelve cada sección nombrada y emite un pack por fase. `.agents/` no se escribe
  ni se copia como sustituto. Artefacto: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` clave `packs[]` con
  `no_incluye[]` y `lectura_aparte_obligatoria[]` — el workflow canónico figura ahí, porque este plan
  no lo rebaná (D3).
- **AC20** — El delta de carga de lectura se mide con el **mismo comando** en los dos lados (`stat
  -c %s` por documento declarado; la estimación de tokens declara su divisor). Artefacto:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before`, `after`, `method` por fase y total, más el par
  `*_baseline_pre.txt` / `*_baseline_post.txt` con la resta comprobada (R2.3, R2.7). El delta se
  reporta sobre las fases de **este** plan; la fila de `REFACTOR-WHATSAPP` se publica como
  referencia, no como objetivo. **Un delta cero o negativo es un resultado válido y se explica**: lo
  prohibido es afirmarlo sin medir.
  - **⟦Carga total, añadida el 2026-09-24 por el bloque C de la orden §4.C, fila `CONTEXTO/D`⟧**
  La resta de AC20 se saca entre **cargas totales**, no entre «bytes de las fuentes» y «bytes del
  pack». Cada lado publica los tres sumandos definidos en el contrato (§Carga total y frescura del
  pack): `workflow_obligatorio` (lo que la fase sigue leyendo aparte, con el workflow canónico a la
  cabeza mientras D3 no lo rebane), `coste_de_generacion` (la corrida del generador que la sesión
  ejecuta para obtener el pack) y `pack_consumido`. **Prohibido describir la concatenación como
  ahorro**: unir N documentos no reduce la suma de sus bytes y puede subirla. Lo que AC20 puede
  acreditar es cuánto deja de leerse porque **no** entró al pack, y eso solo se ve si se publica
  también lo omitido (`no_incluye[]`). Si la carga total sube, el resultado es ese y se explica.
- **AC21** — Cada pack declara `provenance` con `head`, `generated_at` y `sha256` por fuente;
  `--check` falla contra un árbol modificado. La prueba se hace **editando una fuente y re-midiendo
  en disco**, no leyendo el objeto en memoria (L-V2.3, R2.4).
  - **⟦Frescura por entradas relevantes, añadida el 2026-09-24 (orden §4.C, fila `CONTEXTO/D`)⟧**
  El predicado de caducidad es **el sha256 de cada fuente listada en `sources[]` contra el árbol
  vigente**, con sus tres causas distinguibles (`FUENTE-AUSENTE` / sha distinto / fuente ilegible).
  `head` identifica de qué árbol salió el pack; **no** es la llave de caducidad. Razón: el pack es un
  generado versionado, de modo que si HEAD gobernara, el commit que lo guarda lo dejaría vencido en
  el mismo commit — invalidación circular. Consecuencias probables y con test: HEAD distinto con
  fuentes idénticas **no** produce `VENCIDO` (se informa como procedencia distinta); el pack no está
  en su propio conjunto de fuentes; y mover una fuente sí lo vence.
  - **⟦Traslado del plan, mismo bloque⟧** AC19 obliga al generador a resolver un plan **también bajo
    `Archives/`**, porque el cierre del RELEASE regenera y verifica el pack **después** del `git mv`.
    El rojo de un `--check` llamado sobre rutas ya movidas no se repara editando código: se repara
    regenerando con la ruta vigente (§Orden del cierre del contrato).
- **AC22** — Tres estados, ninguno colapsado: `COMPLETO`, `SECCION-NO-RESUELTA` (nombra la sección
  pedida y las rutas intentadas) y `FUENTE-AUSENTE` (ruta buscada). **Prohibido emitir un pack más
  corto en silencio**: el recorte no resuelto es un estado, no una reducción. Un `except` que devuelva
  el pack parcial está prohibido (L-PF6, L-PF10).
- **AC23** — Mutation check sobre el símbolo real que niega el truncamiento, con rojo y verde en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/`. Sin el lado rojo, AC23 queda ⚠️ (R2.4).

### Transversales

- **AC16** — El conteo de checks del `--quick` y del hook queda inalterado en **todo** el plan
  (delta 0, par pre/post por fase, resta comprobada). Es la AC que abre la puerta a que este plan
  corra mientras otro está en vuelo. **La medición de «quién afirma el 11 y el 7» barre también
  `tests/`**, no solo los documentos: L-V2.3 se capitalizó justamente porque el rojo vivo estaba en
  un contract test. Medido el 2026-09-20: `tests/test_validate_plan_closure.py` assertiona `[5/7]`
  dentro del hook, y `tests/test_validate_lesson_capitalization.py` ya quedó re-atado a coherencia
  estructural (grupo derivado de `run_all`, ordinales exactos `1..D`) en lugar del literal.
- **AC17** — Este plan **no** modifica `.agents/`. Declara además, en su propia salida, las
  familias de aserción que no cubre (L-HF1, L-R.4). Artefacto: `coverage.json` clave
  `families_not_covered[]`, con **las cuatro familias de AC2 nombradas una por una** (prosa sin
  patrón; conteos fuera de los documentos de gobierno —`AGENTS.md`, `docs/GUIA_TECNICA.md`,
  `docs/contributing/REGISTRY.md` con «check 8»/`[9/9]`/`[10/10]`/`10/10…14`—; pins de conteo en
  `tests/`; y toda fuente dinámica que no sea etiqueta impresa) y, para cada una, si queda como
  límite permanente o como trabajo de **D1**. Un `families_not_covered[]` genérico no cierra AC17.
- **AC18** — Los artefactos del plan pasan, sobre el mismo árbol final verificado,
  `validate_lesson_capitalization.py` (C1–C8), `validate_plan_citations.py` y
  `build_lesson_index.py --check`. El commit es opcional, posterior y requiere autorización explícita:
  no condiciona ninguno de los cinco cortes. Ningún AC ni prompt cita `archivo:número` (R2.2).

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 25266 bytes copiados de 51507 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `01-plan-maestro.md` §2

## 2. Matriz de decisión

| Decisión | Resuelto | Base |
|---|---|---|
| **¿Se toca `run_all_validations.py` o el hook para añadir checks?** | **NO.** Ninguna fase de este plan altera el número de checks | `REFACTOR-WHATSAPP` está en vuelo y pinea la cifra. **Sitios medidos el 2026-09-20** (no es el prompt de FASE-C, como decía la primera versión de esta fila): el bloque de arranque de FASE-B de su `README.md` («El quick son 11 checks.»), `06-checklist-implementacion.md` («el modo rápido pasó de 10 a **11 checks** y da 11/11»), `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`. Promover algo al set de 11 invalida la medición de fases ajenas. **⟦Re-medido el 2026-09-24 por el bloque C de la orden de calidad⟧**: el bloque de arranque de su `README.md` **ya no está en esa lista** —sus enmiendas lo sustituyeron por el comando que imprime la cifra—, y quienes la conservan (`06-`, `09-`, `10-`, su `dependencias-fases.md`, su prompt de FASE-G) son registros de fases cerradas. Eso **no debilita esta fila**: la razón de fondo sigue en pie, porque las mediciones ya publicadas son precisamente esas. Y **`run_all_validations.py` no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance (ver D10). Queda como deuda con disparador (§Deuda) |
| **¿Se edita `.agents/` para corregir A1–A4 a mano?** | **NO.** El verificador **reporta**, no reescribe | Quien corrige la frase a mano produce la fosilización siguiente (Q6: la cura es un writer o un verificador, no el edit). Precedente: `validate_plan_citations.py` reporta sin reescribir, decisión DA-HF3 |
| **¿Arquitectura de los nuevos verificadores?** | Script **standalone** en `scripts/`, invocable suelto; el set de 11 queda intacto | Es el patrón de la casa: `[9/11]` y `[10/11]` son wrappers de 4 líneas que delegan a `validate_plan_citations.py` y `validate_lesson_capitalization.py` |
| **¿Se construye un cliente HTTP propio del proveedor?** | **NO.** Costura neutra `decision_client.py` que resuelve al proveedor configurado; el SDK oficial o el adapter quedan detrás | **Origen declarado del dato:** el operador reportó el 2026-09-20 que el SDK del proveedor rompió compatibilidad dos veces en sus primeros nueve días de público (redefinió los criterios de una primitiva; migró de serializador). **No verificable desde este repo** — no hay registro ni changelog del SDK versionado aquí—, así que se cita como dato externo y la decisión no depende de él: nombrar la costura, no el proveedor, es la cura estructural tanto si el historial es de dos rupturas como de ninguna, y así añadir un proveedor nuevo después es **un** archivo |
| **¿El triaje de pertinencia puede filtrar?** | **NO. Solo propone.** La fila ya anclada en §2 nunca desaparece | El riesgo de un filtro que descarta en silencio una premisa carga-estructura ya cobró un plan: `VACUOUS_RECALL` obligó a crear FASE-0 y AC20 en la revisión 2 de `REFACTOR-WHATSAPP` |
| **¿Se activa FASE-VERIFY?** | **NO.** Etapas = 3 (Preparación → Implementación → RELEASE) | §4.6 exige **los tres** criterios. Se cumplen «≥3 fases de implementación» y «ACs que cruzan fases»; **no** existe fase con ejecución E2E (`v4complete`/`v4audit` prohibidos por este plan). Criterio 2 cae → no aplica |
| **¿Entra Jev en este plan?** | **NO, por decisión del operador del 2026-09-20.** El acceso existe y la API está habilitada; posponerlo es distinto de no poder usarlo | FASE-B deja la costura lista y AC9 verifica que **añadir** un segundo proveedor sea un cambio de un archivo. La activación queda como deuda **D7** con su disparador |
| **¿Se compara proveedores dentro de este plan?** | **NO.** Con un único proveedor configurable no hay elección que medir | Reformular AC9 era obligatorio: un AC que exige medir una comparación inexistente se cierra declarando `NO-EJERCITADO` y certifica humo. Es la familia de verde vacuo que AC20 cerró en el otro plan |
| **¿Dónde vive el pack generado por FASE-D?** | En `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, **dentro del plan** | `.agents/workflows/` tiene contadores de skills con `glob("*.md")` no recursivo: un `.md` ahí altera lo que reporta `validate_agent_ecosystem.py` y exige seguimiento en su `README.md`. Y AC17 prohíbe escribir en `.agents/` |
| **¿`confidence` es lo mismo que la probabilidad de sí? (⟦decidido el 2026-09-23, orden §4.C⟧)** | **NO.** La pregunta de pertinencia es `choice` de dos opciones, y el umbral de AC12 se aplica a `confidence` **nombrando el campo** en `basis` | Confirmado contra `scripts/decision_client.py`, no contra su docstring: `RespuestaEleccion` exige `confidence` y `RespuestaNoul` la trae en `None` con `confidence_motivo` —la primitiva no la expone—. Un umbral sobre `probabilidad_si` mediría otra cosa y cerraría AC12 con una métrica que el AC no describe |
| **¿El JSON del índice puede leerse confiando en que `[6/7]` lo regeneró? (⟦decidido el 2026-09-23⟧)** | **NO. AC11 toma la ruta (b):** C consume el JSON **tras ejecutar ella misma** la comprobación de frescura | L-V2.2 (`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`): un verificador no apoya su conclusión en el artefacto de otro gate. La ruta (a) (`build()` en memoria) habría **borrado** el estado `VENCIDO`; elegirla aquí sin decirlo dejaría un AC que pide tres estados sobre un diseño que solo produce dos. Coste aceptado: C es responsable de su suelo y mide dos lecturas por corrida |
| **¿Una lección propuesta por el proveedor falso entra en §2 del `00-`? (⟦decidido el 2026-09-23⟧)** | **NO, no en automático.** Propuesta ≠ pertinente: exige **revisión humana explícita** y su aceptación o rechazo **registrada** con quién decidió | Lo que prueba el falso es la mecánica del camino, no la pertinencia. Auto-triarse con respuestas sintéticas y escribir el resultado en §2 fabricaría la evidencia que AC15 declara `NO-EJERCITADO`, y rechazar en silencio es la familia del filtro que la matriz ya descartó arriba (`VACUOUS_RECALL`). El rechazo también se publica: una fila no desaparece |
| **¿La futura FASE-C aplica las mejoras generales de la orden de calidad? (⟦declarado el 2026-09-23⟧)** | **NO.** C conserva el **workflow canónico** y el **proceso común** vigentes: lee `.agents/workflows/phased_project_executor.md`, cierra con los seis pasos del contrato y no renumera nada (AC16 delta 0) | La orden `2026-09-22` autorizó y ejecutó su bloque A (conciliado, §5-ter) y su **bloque B, concluido contractualmente por su matriz §13, que es la única fuente de su estado**; el **bloque C** —estas enmiendas prospectivas— quedó autorizado el **2026-09-24** solo sobre los documentos de los cuatro planes, y el **piloto FASE-C sigue sin autorización**. Ejecutar una mejora de proceso dentro de la fase sería colar un cambio de gobierno por arrastre de una fase, y dejaría la medición de D3/A7 comparada contra dos reglas distintas. De C **sí** entra lo que este plan ya resolvió para sí: las cuatro enmiendas de AC11/AC12/AC15/propuestas |

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7` · 7144 bytes copiados de 51507 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `04-contrato-ejecucion.md` (documento completo)

# Contrato de ejecución — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no reemplaza**
`.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. **El bloque C de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; el piloto FASE-C de este
plan sigue sin autorizar y no se ejecutó al redactarlas.** Los permisos de este plan no amplían ese
mandato.
Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Permisos de la sesión

| Acción | ¿Autorizada? | Base |
|---|---|---|
| Escribir en `scripts/` (cuatro archivos nuevos) y `tests/` | **Sí** | Alcance §3 del maestro |
| Escribir en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | **Sí, solo FASE-D y solo como generado** | AC19; el directorio vive dentro del plan, no en `.agents/workflows/` |
| Leer `.agents/`, `output/`, `evidence/` de otros planes, `Archives/` | **Sí, lectura** | Necesaria para AC13, AC19 y para el denominador |
| Modificar cualquier archivo bajo `.agents/` | **No** | AC17. Configuración central, y es la fuente que el verificador auditó y que FASE-D lee |
| Reescribir un prompt de fase de otro plan | **No** | FASE-D los parsea. Reescribirlos es lo que D2/D3 postergan |
| Modificar `scripts/run_all_validations.py` o `scripts/git_hooks/pre-commit` | **No** (este plan los lee como fuente de verdad) | AC16: alteraría el conteo que otros planes publican. **Lectura actualizada el 2026-09-24 (bloque C de la orden §4.C):** en `REFACTOR-WHATSAPP` quedan pineados en sus **registros de fases cerradas** (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medidos el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra), que son evidencia histórica y no se reescribe; lo que las enmiendas de ese bloque convirtieron en «el valor lo imprime la corrida, con su comando» fueron las **instrucciones prospectivas** (su bloque de arranque y sus prompts pendientes). Eso **no** satisface el disparador de **D2**: D2 pide que deje de haber *fases en vuelo* que pineen el número, y esa decisión sigue con su dueño. **Y no es un archivo libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance, así que este plan no lo escribe pero **sí** debe re-leer su etiqueta `[15/15]` y la invocación del write-back en el cierre (deuda **D10**) |
| Ejecutar `v4complete`, `v4audit`, la pipeline o cualquier API de pago | **No** | §5 del maestro. Este plan no tiene corrida ni llamadas de red |
| **Llamadas reales a un proveedor de decisiones** | **No, en ninguna fase** | Decisión del operador del 2026-09-20: Jev no entra. AC9 certifica la **costura**, no al proveedor; activarlo es deuda **D7** |
| `git commit` / `git push` | **No implícito** | Cada fase deja el checkpoint; el commit requiere instrucción literal |
| **Escribir configuración central en el cierre** — lo que `sync_versions.py` (sin `--check`) reescribe según `scripts/sync_config.yaml`: `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`; `VERSION.yaml` (entrada, no salida); y `docs/contributing/REGISTRY.md` con su tracker `.last_doc_phase.json` cuando se pasa `--archivos-mod` | **No implícito.** Requiere autorización literal **por destino**, comprobada antes de escribir | **Rectificación 2026-09-25:** «cierre offline» y el mandato de RELEASE **no** otorgan este permiso. `--check` y `--help` leen, no escriben. Rige **C0** del `05-prompt-inicio-sesion-fase-RELEASE.md`. Alinear la política de `DOMAIN_PRIMER` es decisión aparte; tampoco la cubre un sync de cabeceras |
| Write-back a QMind | **No en fases de implementación.** En RELEASE **solo con autorización literal propia** | Orden R2.5/R2.10 lo sitúa antes del `git mv`; eso fija su *posición*, no su *permiso*. Es operación remota: ver §Dos momentos del cierre |
| Consulta a QMind (deuda D8 / consulta Q7) | **No por defecto.** Requiere la misma autorización literal | La regla «la consulta no concede permiso de subida» vale al revés: tampoco una subida autorizada concede lectura libre |

**Regla de cero red.** FASE-B y FASE-C se prueban contra proveedores **falsos**. Si una sesión
necesita llamar a un servicio real para avanzar, para y deja checkpoint: la llamada no se autoriza
por conveniencia. Consecuencia aceptada y escrita en el maestro: ningún AC de este plan mide calidad
de decisiones de un modelo real.

**Alcance de la regla (precisión del bloque C, 2026-09-24).** «Cero red» gobierna las **pruebas** de
proveedor de decisiones en las cuatro fases de implementación; no describe el cierre de FASE-RELEASE,
que por su orden R2.5/R2.10 contiene dos operaciones remotas (la consulta Q7 y el `--upload`). Decir
que RELEASE «no hace ninguna llamada de red» y a la vez ordenar esas dos era la contradicción que la
fila `CONTEXTO/RELEASE` de la orden de calidad §4.C pedía resolver. Se resuelve separando momentos, no
borcando ninguna de las dos mitades: ver §Dos momentos del cierre.

## Dos momentos del cierre (añadido por el bloque C de la orden de calidad §4.C)

| Momento | Qué contiene | Red | Autorización | Qué se publica si falta |
|---|---|---|---|---|
| **Cierre offline** | Lecturas y verificadores sin escritura; sync, documentos, registro y derivados únicamente sobre destinos autorizados | **No** | Mandato de RELEASE más autorización literal de los archivos escribibles, comprobada en C0 del prompt RELEASE | Detenerse antes de escribir si falta un destino necesario: `PENDIENTE-AUTORIZACION`, no cierre cumplido |
| **Aceptación remota** | re-corrida de la consulta Q7 (D8) y `--upload` del `10-analisis` antes del `git mv` (D9) | **Sí** | **Literal y propia para cada una**, con presupuesto escrito | Estado `PENDIENTE-AUTORIZACION` con su causa, **no** un PASS ni un `[OK]` por omisión |

**Rectificación 2026-09-25:** «cierre propio de la fase» no otorgaba permiso sobre configuración central.
Rige **C0 del `05-prompt-inicio-sesion-fase-RELEASE.md`**: releer los destinos reales antes de escribir.
`sync_versions.py --check` no escribe; el sync en escritura requiere autorización literal para sus
consumidores de `scripts/sync_config.yaml`. `VERSION.yaml` es entrada, con permiso propio para cambiarla.
La alineación de política de DOMAIN_PRIMER no se autoriza mediante el sync de cabeceras. Tampoco se
actualizan baselines para absorber errores. Sin permiso suficiente, checkpoint previo, no cierre completo.

El archivado (`git mv`) es un **tercer** momento y conserva su autorización separada: no la concede el
cierre offline ni la sustituye una subida pendiente. Con la aceptación remota pendiente, el plan
**puede** archivar solo si el operador lo autoriza expresamente sabiendo que la fuente no se publicó;
si no, deja checkpoint. Nunca se promueve un resultado parcial a éxito del cierre (§Orden del cierre).

## Enmiendas prospectivas ya resueltas para FASE-C (registradas el 2026-09-23)

Fuente: `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.C, fila `CONTEXTO/C`, con
autorización local del operador sobre **este** plan y solo sobre **estas** cinco decisiones. **Ninguna
se implementó todavía**: son contrato para la sesión de C, no trabajo hecho. No acompañan cambio de
versión, de `REGISTRY.md` ni de configuración central.

| # | Regla que C debe cumplir | Qué deroga o precisa |
|---|---|---|
| **E1** | La pregunta de pertinencia es **`choice` de dos opciones**, con `confidence` leída como campo **independiente** del umbral. **Prohibido equiparar `probabilidad_si` con confianza.** | Precisa AC12 y su `basis`; la forma está en `scripts/decision_client.py` (`RespuestaEleccion` / `RespuestaNoul.confidence = None`) |
| **E2** | C consume `.opencode/lecciones_index.json` **después de ejecutar ella misma** la comprobación de frescura. Prohibido apoyarse en que `[6/7]` del hook u otra sesión lo regeneró. `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` son tres causas con su test cada una | **Cierra la elección abierta de AC11** en la ruta (b); con la ruta (a) `VENCIDO` habría dejado de existir y el AC pediría tres estados a un diseño de dos |
| **E3** | Una propuesta del proveedor falso **no** entra en §2 de `00-lecciones-capitalizadas.md` por sí sola: pasa a `a-revisar-humano` y solo entra con **revisión humana explícita**, dejando la **aceptación o el rechazo registrado** con quién lo decidió. Un rechazo se publica, no se borra | Corrige el paso 6 de post-ejecución del prompt de C, que mandaba «aplicar lo que proponga» sin filtro humano |
| **E4** | El tramo **semántico** de AC15 se publica `NO-EJERCITADO` con su motivo y **D6 queda dormida**. No se simula una aceptabilidad con el falso para cerrar el AC | Refuerza lo ya escrito en el prompt de C; queda elevado a contrato para que no dependa de leer un párrafo |
| **E5** | C **conserva el workflow canónico y el proceso común vigentes**: lee `.agents/workflows/phased_project_executor.md`, cierra con los seis pasos de este contrato, y no renumera checks (AC16 delta 0 sobre los valores que imprime la corrida, no pineados) | Lo que C conserva es el proceso común **tal como lo deja el bloque B**, cuyo estado vigente es la matriz §13 de la fuente única indicada al inicio; los dictámenes anteriores se conservan retirados. Ejecutar dentro de C una mejora de proceso sería colar un cambio de gobierno por arrastre de una fase |

**Reconfirmación de E1 y E2 contra el cliente real (2026-09-24, bloque C de la orden de calidad).**
No es una renegociación: es el contraste que la fila pedía, hecho sobre el código que ejecuta C y no
sobre su documentación ni sobre la transcripción de este contrato. `scripts/decision_client.py` sigue
dando la forma que E1 asume — `RespuestaEleccion` declara `__slots__` con `confidence` y su validación
**exige** el número (`confidence ausente o fuera de [0,1] - sin ella no se puede…`), mientras
`RespuestaNoul` fija `confidence = None` en la propiedad de clase y **la puerta rechaza** que un `noul`
la reporte (`noul no debe reportar confidence`), con `a _en_rango` gobernando `probabilidad_si` por
separado. **Conclusión: E1 y E2 quedan coherentes con el cliente vigente y no se mueven.** La lectura
completa con sus anclas simbólicas está en la evidencia del bloque C.

**Invariante que ninguna enmienda mueve:** el triaje es **aditivo** (AC10, `removed: []` con su test),
todo conteo lleva su **denominador** (AC15/AC2), todo verificador de detección se cierra con su
**mutation check** sobre el símbolo real del guard (AC14), al menos un test corre sobre **corpus real**
archivado con su skip declarado (AC13), y **la red sigue prohibida** en las cuatro fases (§Regla de
cero red). Lo enmendado es la **forma de la pregunta, la fuente de la frescura y el destino de las
propuestas**; no el nivel de garantía.

**Antecedente de las enmiendas, no estado actual de D1/S13.** Los dos párrafos siguientes conservan
las declaraciones de la conciliación y de los dictámenes retirados de B; **no certifican** D1/S13:
su estado solo lo determina la matriz vigente §13 de la fuente única. La obligación de no pisar
históricos en AC14 se mantiene, sin trasladar a C la validación pendiente del arnés de B.

**Lo que NO se tocó al enmendar** (antecedente de aquella sesión): las deudas **S10** (dónde vivirá el
`import` del SDK) y **D7** (activar el proveedor) siguen pendientes y **no son bloqueantes artificiales
de una C offline** — C se cierra con proveedor falso por diseño; **D6** sigue dormida; y el **rojo
contractual** de A1–A4 (`validate_governance_numbers.py`, `exit 1`) sigue vivo porque es **D1** y pide
instrucción literal sobre `.agents/`. **⟦Rectificado el 2026-09-23 por el bloque B de la orden de
calidad, con instrucción literal del operador:⟧ D1 se ejecutó desde su fuente y el árbol real de
`.agents/` ya sale `SIN-HALLAZGOS` (`exit 0`); las cuatro aserciones quedaron como contraejemplo
congelado en `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes. Este contrato de C ya
no puede dar por vivo ese rojo. La conciliación de FASE-B con la remediación del bloque A está en
`dependencias-fases.md` §Conciliación y §Ejecución del bloque B.**

**S13 — dictamen anterior retirado; estado vigente solo en §13.** ⟦El dictamen del
2026-09-23 decía **«S13 resuelta por el bloque B y completada en su remediación el mismo día»**: el arnés
`test_governance_numbers_mutation_por_asercion.py` ya no escribe en
`evidence/…/FASE-A/mutation/`; su evidencia va a destino temporal explícito y **se observan las
operaciones de escritura** del escritor real (`tests/support_observador_escrituras.py`, alcance
declarado: proceso de pytest, no procesos hijos), con ancla positiva y con los tres controles
negativos del mandato sobre un expediente desechable (a escritor redirigido a destino protegido,
b bytes idénticos, c mtime restaurado). La comparación de contenido **y** metadatos del expediente
protegido se conserva además. El
párrafo siguiente sigue vigente como **regla para el mutation check propio de C (AC14)**, salvo su
última frase, que la remediación dejó corta: se reemplaza «por hash de objeto» por «por operaciones
de escritura observadas, más contenido y metadatos» — un `utime` restaurado deja el estado final
idéntico y solo el observador lo ve.⟧ **Antecedente del defecto original:** el arnés de mutación de FASE-A
(`test_governance_numbers_mutation_por_asercion.py`, por su constante `EVIDENCE` junto a `SCRIPT`) tenía el
**destino de escritura hardcodeado dentro de `evidence/…/FASE-A/mutation/`**: al re-evidenciar R2.8 el
2026-09-23 re-escribió 7 archivos cerrados de otra fase — sin daño, porque los 7 `git hash-object --path`
casaron con HEAD, pero con los `mtime` movidos, que es lo que hace invisible este patrón. Es la misma familia
que **S12 / L-VCF-12**, y aquella cura alcanzó a los dos verificadores, no al arnés. **Cuando C escriba su
mutation check de AC14 no puede heredar ese patrón**: su evidencia va a
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`, el destino se declara con la ruta del
propio cierre (no como constante apuntando al directorio de otra fase), y la prueba de que no pisó pasado
exige **operaciones de escritura observadas, más contenido y metadatos**, con el alcance del observador
declarado. La redacción anterior «por hash de objeto, no por `git status`» queda como antecedente
insuficiente: una reescritura de bytes idénticos puede no cambiar ninguno de los dos.

## Dónde se escribe la evidencia (corregido en la auditoría del 2026-09-20)

Toda la evidencia de este plan va a **`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`**.
La primera versión del plan escribía en `evidence/FASE-A/` … `evidence/FASE-D/` a secas, y eso **no
estaba libre**: esas cuatro rutas raíz existen desde `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y guardan
su evidencia con exactamente los nombres que produciría este plan (`faseA_baseline_pre.txt`,
`faseA_baseline_post.txt`, `faseB_baseline.txt`, …). Escribir ahí mezclará procedencia de dos planes y
podrá **sobrescribir evidencia de un plan archivado sin que salte ninguna validación** (`validate_opencode_refs.py`
solo mira rutas bajo `.opencode/`, y `evidence/` no entra). El convenio vigente es el subdirectorio por
plan, que ya usa `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.

**Excepción de lectura, no de escritura**: `evidence/FASE-D/measure_iterations.py` conserva su ruta
legada porque es el instrumento canónico que publica el executor; no es destino de nueva evidencia.

**Discrepancia de la plantilla, rectificada dentro del proceso B:** al concebir el plan,
`.agents/workflows/templates/prompt-fase-template.md` prescribía `evidence/fase-{N}/` sin namespace;
AC17 impedía corregirla desde estas fases y se registró bajo D1. La escritura documental acotada de B
corrige ahora sus destinos y su ejemplo a **`evidence/{NOMBRE-PLAN}/FASE-{N}/`**, alineados con los de
este contrato. Es corrección del proceso B **sujeta a validación en la matriz vigente §13** de la
fuente única, no certificación de D1/S13 ni trabajo trasladado a C/D2.

## Corte de presupuesto (R2.1)

Instrumento canónico: `evidence/FASE-D/measure_iterations.py` (ruta legado, ver arriba), corte **hasta
el commit de código** cuando el commit está autorizado; cuando no lo está, el corte utilizable es
**«hasta listo para revisión»** y se declara cuál de los dos se usó — el commit es una acción posterior
y separada del cierre documental, no un corte ni condición de ninguno (executor, *Cinco cortes*).
Este plan declara presupuesto y **declara además si el instrumento corrió**. Si no corre bajo la
política de permisos de la sesión, el auto-reporte se publica en la unidad usada (`tool_use`,
`ids únicos`) y se declara que **no es comparable** con las demás. Prohibido reportar cumplimiento
estimado o mezclar unidades. Sin instrumento, la métrica se retira y se declara fuera de servicio,
no se estima. **Precondición medida el 2026-09-20**: `find . -name "*.jsonl"` devuelve **0** dentro del
workspace — es la misma condición que documentó `D-V2.1` (`PASO0-…`/`TRIBUNAL-ENFORCEMENT-OBS`,
reproducida en cuatro fases seguidas), así que esta sesión **espera** caer en el auto-reporte con unidad
declarada y lo declara, en lugar de prometer una medición que no puede hacer.

## Cierres incrementales obligatorios por fase

1. **Par pre/post del conteo de checks** en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`
   (`*_baseline_pre.txt`,
   `*_baseline_post.txt`) y `baseline-pre-post.md` con la **resta** comprobada. Delta esperado: **0**
   en las cuatro fases de implementación (AC5, AC16). FASE-D añade además su propio par de **carga de
   lectura** (AC20), que sí espera un delta distinto de cero y que se reporta aunque sea cero.
2. **Selección de tests de la fase** ejecutada, publicada con su resultado, y los rojos preexistentes
   ajenos a la fase declarados como tales con dueño y causa, sin arrastrarlos ni maquillarlos.
3. `run_all_validations.py --quick` en verde, **sin** que la fase haya tocado su composición.
4. **Registro de la fase por sí misma**: `scripts/log_phase_completion.py` al terminar. FASE-RELEASE
   **no** registra fases ajenas.
5. `build_lesson_index.py` regenerado y comprobado **sobre el mismo árbol final verificado** tras las
   ediciones de `.md` bajo `plans/` que nombren un ID (R2.10). Aplica también a FASE-D. El commit es
   opcional, posterior y autorizado por separado; no condiciona los cinco cortes. Si se autoriza,
   incluye fuentes y par generado coherentes, como exige `[6/7]` del hook.
6. Actualización de `00-lecciones-capitalizadas.md` §2 (lo que **realmente** pasó), §4 (cobertura al
   estado real), `06-checklist-implementacion.md`, `dependencias-fases.md` y `README.md` del plan.
7. **FASE-D únicamente**: `build_phase_briefing.py --check` en verde contra el árbol final, y ningún
   pack emitido con `SECCION-NO-RESUELTA` sin decirlo (AC22).
8. **FASE-D únicamente — hereda el resultado NO medido de C y lo acepta.** D no reabre C ni lo
   renegocia: registra que el tramo semántico de AC15 salió `NO-EJERCITADO`, que **D6 sigue dormida**,
   y que su disparador solo se evalúa cuando exista proveedor real (D7). Lo que D **sí** hereda medido
   de C es su parte mecánica: los tres estados del índice, el umbral sobre `confidence`, la aditividad
   y el denominador con sus ceros. El pack puede exhibir los candidatos de pertinencia, pero no puede
   presentar esa exhibición como aceptabilidad obtenida (§E4).

## Reglas sobre el pack generado (FASE-D)

- El pack es **derivado, no autoritativo**. Ninguna lectura canónica desaparece: lo que el pack no
  incluye se declara en `no_incluye[]` y en `lectura_aparte_obligatoria[]`, donde figura el workflow
  canónico porque este plan **no** lo rebaná (D3).
- Un pack no puede achicarse en silencio: sección pedida y no resuelta es un estado propio con la
  ruta intentada (AC22, L-PF6, L-PF10).
- Lleva `provenance` con HEAD, fecha y sha por fuente, y `--check` lo vence contra el árbol (AC21).
  Un pack vencido se regenera; no se edita a mano.

## Carga total y frescura del pack (añadido por el bloque C de la orden de calidad §4.C)

Las tres reglas anteriores dejan abiertos dos puntos que la fila `CONTEXTO/D` cerró: **qué se cuenta
como carga** y **qué mueve la frescura**.

**Carga total (AC20), no «bytes del pack».** El pack unifica lecturas; no las elimina. La medición de
`carga.json` publica por fase los tres sumandos y la resta se saca entre los dos totales, no entre el
pack y la lista de documentos:

| Sumando | Qué entra | Por qué no puede faltar |
|---|---|---|
| `workflow_obligatorio` | Los bytes de lo que la fase **sigue** leyendo aparte (`lectura_aparte_obligatoria[]`): el workflow canónico mientras D3 no lo rebane, y toda fuente declarada y no incluida | Si no se cuenta, el pack aparece como ahorro cuando la fase lee lo mismo más el pack |
| `coste_de_generacion` | La corrida del generador que la sesión ejecuta para obtener el pack (invocación publicada y, si el instrumento corre, su coste) | Un artefacto que hay que producir no es gratis para quien lo consume |
| `pack_consumido` | Los bytes del pack que la fase efectivamente lee | Es el único sumando que el pack reemplaza |

**Prohibido presentar la concatenación como ahorro.** Juntar N documentos en un archivo no baja la
suma de sus bytes; puede subirla (encabezados, procedencia al pie, `no_incluye[]`). El ahorro real
solo puede venir de lo que **no** se copia al pack, y eso se mide declarando qué se omitió. Un delta
cero o negativo sigue siendo resultado válido y se publica igual (AC20). La fila D3 del maestro conserva
su dueño: el recorte de la fuente **no** es lo que mide esta resta.

**Frescura por entradas relevantes; HEAD es procedencia.** AC21 fija el criterio: `--check` vence el
pack comparando **el sha256 de cada fuente listada en `sources[]` contra el árbol vigente**, y fallando
por una de tres causas distinguibles (`FUENTE-AUSENTE` / fuente con sha distinto / fuente ilegible).
`provenance.head` se publica para identificar **de qué árbol salió** el pack, no para invalidarlo: si
el sha de HEAD gobernara la caducidad, el propio commit que guarda el pack generado lo dejaría vencido
en el instante de publicarse — circularidad que la orden §4.C nombró expresamente. Consecuencias
operativas:
- el pack **no** está en su propio conjunto `sources[]`, ni tampoco el commit que lo transporta;
- un HEAD distinto con las fuentes idénticas **no** vencifica el pack: se informa el desfase como
  procedencia distinta, no como `VENCIDO`;
- la invalidación la produce un cambio en una fuente gobernada, nunca el acto de versionar el generado.

**Regeneración y verificación tras el traslado.** El `git mv` del RELEASE cambia las rutas que el pack
declara como fuentes, así que **`--check` después del traslado sin regenerar tiene que fallar**: ese
rojo es un paso del cierre, no una reparación. El orden queda fijado en §Orden del cierre: regenerar
el pack con la ruta ya trasladada y **después** verificarlo. Regenerar un artefacto derivado con su
propio generador es operación de cierre autorizada a RELEASE; **modificar `build_phase_briefing.py`
para que el check pase no lo es** (§Restricciones del prompt de RELEASE: RELEASE no modifica código).

## Reglas de forma aplicadas a los artefactos de este plan

- **Símbolos, nunca `archivo:número`** en ACs, prompts y evidencia (R2.2). Antes de citar una región,
  confirmarla con `grep`/lectura; si difiere, corregir la cita y avisar.
- **Conteos como delta** con par de archivos, no números absolutos (R2.3, R2.7).
- **Todo AC de detección se cierra con mutation check** sobre el símbolo real del guard, con las dos
  salidas en evidencia (R2.8). Verde a la primera = sospechoso y explicado.
- **Todo lector expresa tres estados** y los publica (R2.9): `sin hallazgos` / `ausente` /
  `lector fallido`. Prohibido el `except` que devuelve el valor por defecto de «no encontrado».
- **AC no legible en el artefacto = ⚠️, nunca ✅** (R2.4). Prueba práctica: si el AC no responde
  *«¿dónde lo vería un humano que solo tiene el artefacto?»*, no está listo.
- El **reporte no reescribe**: ningún script de este plan edita `.agents/` ni los planes ajenos.
- Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha**, y se re-mide al
  cerrar la fase (medición A6 del maestro: las cifras de este plan vencieron al crearse el plan).

## Orden del cierre (R2.5 / R2.10, no permutable)

**Paso 0 (D10, añadido en la auditoría del 2026-09-20):** antes de correr el bloque, verificar la
interfaz del writer contra el árbol vigente — `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help`
— porque `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` puede haber añadido `--title`/`--file` o quitado la
degradación a PASS. Si cambió, se re-escribe este bloque **con su nota datada** antes de ejecutarlo.
Este paso es **de lectura**: corre aunque la aceptación remota siga sin autorizar.

**Cada línea lleva su momento (§Dos momentos del cierre).** Las marcadas `⟦remoto⟧` no se ejecutan con
el permiso del cierre documental: necesitan su autorización literal y su presupuesto, y si faltan se
declaran `PENDIENTE-AUTORIZACION` sin promover el cierre a éxito. La marcadas `⟦traslado⟧` requieren la
autorización propia del archivado.

```bash
# ⟦remoto⟧ — aceptación remota, autorización y presupuesto propios
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
# ⟦traslado⟧ — el archivado es un tercer momento, con autorización expresa
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
# Cola final tras todas las escrituras autorizadas: no modificar baselines para absorber errores.
./venv/Scripts/python.exe scripts/validate_opencode_refs.py
./venv/Scripts/python.exe scripts/validate_plan_citations.py
# Resolver cualquier corrección de corpus autorizada antes de regenerar los derivados.
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan>
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan> --check
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

El `--check` del pack **no** se corrige editando `build_phase_briefing.py` ni su `provenance`: se
corrige regenerando. Si tras regenerar el pack sigue rojo, eso es un defecto del generador y su dueño
es FASE-D, no RELEASE — RELEASE lo declara y deja el checkpoint, porque tiene prohibido modificar código
fuente (§Restricciones de su prompt).

*(Forma unificada el 2026-09-20: los prompts de fase ya usaban el intérprete del `venv`; este bloque
canónico decía `python`, que bajo Git Bash resuelve al intérprete sin dependencias del proyecto. El
orden y sus argumentos no cambiaron en aquella intervención.)*

**Rectificación 2026-09-25:** retiradas las escrituras automáticas `--fix` y `--update-baseline` de la
secuencia; requieren alcance propio y nunca absorben errores. La cola del prompt y del contrato queda
alineada: últimas escrituras autorizadas → packs → índice → checks, sin sustituir C0 ni los permisos
remotos y de traslado. Si no hubo archivado autorizado, verificar en la ruta actual y declararlo pendiente.

## FASE-VERIFY: no aplica, con la razón medida

§4.6 exige **los tres** criterios de activación. Se cumplen «≥3 fases de implementación» (ahora
cuatro: A, B, C, D) y «ACs que cruzan múltiples fases» (AC15, AC16 y AC17 cruzan fases). **No** se
cumple «existe al menos una fase con ejecución E2E (`v4complete`, `v4audit`, etc.)»: este plan tiene
prohibida la pipeline y prohibida la red. Criterio 2 cae → **3 etapas**, sin sesión de certificación.

Consecuencia declarada: ningún AC de este plan puede llegar a `SUPERADO EN E2E`. Su techo es
`VERIFICADO OFFLINE` con su mutation check, o `NO-EJERCITADO` cuando algo no se ejercitó — y
`NO-EJERCITADO` **no** es una salida disponible para AC9, porque AC9 ya no pide medir una
comparación.


> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5` · 29211 bytes copiados de 29211 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `00-lecciones-capitalizadas.md` §1

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado medido |
|---|------|------------------|------------------|
| Q1 | Índice generado (capa fría) | `for id in L-R.1 L-R.3 L-R.4 L-NC10 L-PF6 L-PF10 L-D3 L-V2.3 L-T4A.5 L-VUP-5; do grep -oE "\\| \\\`${id}\\\`.*" .opencode/LECCIONES-INDEX.md; done` | **10 de 10** devuelven fila con dueño y conteo de citas |
| Q2 | Índice generado — corpus **completo** por síntoma | `grep -icE "numer" .opencode/LECCIONES-INDEX.md` · `… "fosiliz"` · `… "renumer"` · `… "denominador"` · `… "cobertura medida"` · `… "falso verde"` | 20 · 7 · 1 · 1 · 2 · 2 |
| Q3 | Índice generado — término buscado, **cero coincidencias** | `grep -icE "verificador mec" .opencode/LECCIONES-INDEX.md` | **0** — medido en vivo, ver §3-descarte D5 y AC15 |
| Q4 | Población del índice (denominador) | `head -18 .opencode/LECCIONES-INDEX.md` | **Re-medido tras cada regeneración**: 15 análisis + 36 `CONTEXT-*.md` como definiciones; **320** IDs con definición detectada; **50** citados sin definición; **402** `.md` como corpus de citas. La fila decía 14 / 49 / 389 al concebirla, pasó a 15 / 50 / 401 al entrarse el plan y a **402** al escribirse el prompt de FASE-D — tres valores en una sesión; ver maestro §1, medición **A6** |
| Q5 | Fuente de verdad dinámica de los conteos | `grep -nE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py` | 11 etiquetas `[N/11]` (quick) y 4 `[N/15]` (full). **La lectura útil es la asociación etiqueta ↔ `def _check_*`, no la lista**: `[12/15]` es `def _check_dependencies` y `[15/15]` es `def _check_qmind_writeback`. Omitir ese emparejamiento produjo la medición vencida de A3 (ver maestro §1, rectificación de A3 y medición A8) |
| Q6 | Memoria de proyecto (capa caliente) | `MEMORY.md` → entradas *verificador-medido*, *no-implementar-aun*, *quien-produce-el-dato-publicado* | 3 entradas leídas; la tercera fija que la cura de una aserción vencida es un **writer o un verificador**, no el edit |
| Q7 | Notebook QMind `iah-cli-lecciones` | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "…" --format agent --non-interactive` | **Concebida como NO EJECUTADA** («el CLI no está disponible en esta sesión»); **ejecutada el 2026-09-20 en la auditoría de la concepción**, con el CLI disponible y autenticado (v3.3.0, 49 fuentes en el notebook). Cuatro consultas: conteos desfasados, carga de lectura por fase, pertinencia del Paso 0, presupuesto de iteraciones. **El comando original con el nombre (`--nb iah-cli-lecciones`) devuelve `error: Bad request`: `--nb` exige el ID** (medido con las dos formas). Resultados capitalizados abajo como L-V2.1, L-V2.2 y D-V2.1; deuda **D8** re-escrita |
| Q10 | Re-medición de la premisa al abrir **FASE-B** (2026-09-21) — el prompt de FASE-A dejaba la herencia y B no la asumió | `git rev-parse --short HEAD` · `git status --porcelain` · `grep -cE 'print\(f?"\[[0-9]+/11\]'` sobre `run_all_validations.py` · `grep -cE '^#   \[[0-9]+/[0-9]+\]'` sobre el hook · `git ls-files '*.py' \| wc -l` · `git grep -cE '^\s*(import\|from)\s+(typesafe\|jev\|httpx2)' -- '*.py'` · `python -c "import importlib.util as u; print([u.find_spec(m) is not None for m in ('typesafe','jev','httpx2','tenacity')])"` bajo el venv del producto · `find . -name '*.jsonl' \| wc -l` · `stat -c %s` sobre los siete documentos de A7 | HEAD ya no era `e3c4573` sino **`74d8ff5`** (dos commits de barrido documental de FASE-A encima), árbol con **dos rutas ajenas** preexistentes y ninguna creada por B; quick **11**, hook **7**; **0** imports del SDK en los 678 `.py` rastreados (692 en el árbol de trabajo al cerrar; 690 en el primer escaneo) y el SDK **AUSENTE** del venv del producto — pero **presente en el disco** bajo `tmp_test/venv-jev-sdk`, exclusión publicada con su conteo; `*.jsonl` = **0** (D-V2.1 reproducida de nuevo, el instrumento de presupuesto otra vez fuera de servicio); A7 **263.973 bytes ≈ 65.993 tokens**, sin cambio |
| Q11 | **Re-medición tras el commit de FASE-B (2026-09-22)** — el barrido de citas que ese mismo commit venció | `git rev-parse --short HEAD` · `git status --porcelain` · `git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git show --numstat --format="" 647f436 \| grep -cE '\\.py$'` · `git ls-files '*.py' \| wc -l` · `python scripts/decision_client.py --scan-imports` · `grep -cE 'print\\(f?"\\[[0-9]+/11\\]'` sobre `run_all_validations.py` · `grep -cE '^#   \\[[0-9]+/[0-9]+\\]'` sobre el hook · `find . -name '*.jsonl' -not -path './venv/*' \| wc -l` | HEAD **`647f436`** (el commit de B: 46 archivos, +4.412/−97, **13** de ellos `.py`) sobre `eecf246`, que **sigue sin empujar** — el remoto está en `74d8ff5`, paridad **`0/2`** a esa hora (`0/3` al cerrar el barrido que escribe esta fila: cada commit documental suma uno), con el push todavía sin autorizar a esa hora — **quedó hecho el mismo día: `origin/master` en `b764e8d`, paridad `0/0` re-medida tras `git fetch`, y el push publicó de paso el commit ajeno `eecf246`**; **una** ruta ajena sucia. El denominador que la fase publicó quedó refutado por su propio commit: `git ls-files '*.py'` **678 → 691**, mientras el escáner sigue viendo **692** y el numerador **no se mueve** (`SIN-HALLAZGOS`, 0 imports, 0 cargas dinámicas, 21 menciones). El residuo de 1 se **descompuso** con `comm` contra el `rglob` y es `.venv-wsl/bin/activate_this.py` → **S11** / **L-VCF-11**. Quick **11**, hook **7** (sin cambio), `*.jsonl` = **0** (sexta reproducción de D-V2.1, el instrumento de presupuesto sigue fuera de servicio); índice regenerado tras el barrido: **332** IDs definidos + 51 sin definición, **16** análisis y **416** `.md` citados (330 antes del barrido; el +2 son L-VCF-11 y L-VCF-12, y los análisis/.md se mueven por el plan hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`, entrado al corpus en `2c966f6` con 12 `.md`). **Y el propio re-muestreo pisó la evidencia cerrada de FASE-A** (`--report` con destino hardcodeado), medido y revertido → **L-VCF-12** / **S12** |
| Q13 | **Re-medición de la premisa al abrir FASE-D (2026-09-24) — la herencia de D no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git status --porcelain .agents/` · los dos `grep -cE` del quick (11) y del hook (7) · `python scripts/run_all_validations.py --quick` · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `stat -c %s .agents/workflows/phased_project_executor.md` · `python scripts/build_phase_briefing.py --listar-declarado --plan <este plan>` · recuento de prompts que declaran lectura: `Glob .opencode/plans/Archives/*/05-prompt-inicio-sesion-fase-*.md` filtrado por el parser · `python scripts/build_lesson_index.py --check` sobre un arbol extraido con `git archive HEAD` | HEAD **ya no era el `da382b1` que registro C: es `5817edd`** — el commit y el push del propio cierre de C movieron la cabecera despues de que C escribiera su evidencia (A6 sobre la fase anterior, medida al abrir la siguiente); paridad **`0 0`** verificada con `fetch` + `ls-remote`, no inferida. Arbol con **63 rutas sucias ajenas** al medir (ninguna creada por esta sesion al abrir) y **3 de ellas bajo `.agents/`** (executor y dos templates, del bloque B de la orden de calidad) — lo que hace **no verificable la casilla literal** «`git status .agents/` vacio al cerrar», reformulada como «cero bytes aportados por la fase» y afirmada con el observador de escrituras. Quick **11/11 `exit 0`** como par PRE y hook **7**. `*.jsonl` = **0** → **octava reproduccion** de la precondicion de **D-V2.1**, metrica retirada y auto-reporte con unidad declarada. **A7 vencida en su propio dato de entrada**: el workflow canónico pesa hoy **108.017 bytes**, no los **98.694** que publica el maestro §1 (+9.323 desde 2026-09-20, por las ediciones del bloque B), y la carga declarada de **este** plan es **5 fases · 34 fuentes**, con su total en `FASE-D/carga.json` (el número **no se copia aquí**: ver **L-VCF-19** — este `.md` entra en el pack que ese `stat` mide, y de hecho la corrida del cierre lo movió **dos veces**, una por cada barrido documental que se escribió después de medirlo). **Y la convencion que parsea el generador resulto minoritaria**: de **121** prompts archivados, **0** declaran su lectura con la cadena `Lee …`; los unicos **5** del repo estan en este plan → deuda **S16**. El `--check` del indice dio **FAIL** (`exit 1`) tambien sobre un arbol limpio extraido de `5817edd` con `git archive`; **regenerado en ese mismo arbol** paso a `exit 0` con **335** IDs — que es la firma de **S15**: 9 entradas con `fuente_fecha = mtime`, de modo que cada extraccion las vuelve a vencer y commitear el par desde otro arbol no lo cura. Nada del antecedente del prompt se copio como valor vigente |
| Q12 | **Re-medición de la premisa al abrir FASE-C (2026-09-24) — la herencia de C no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `python scripts/build_lesson_index.py --check` · `python scripts/run_all_validations.py --quick` · los dos `grep -cE` del quick (11) y del hook (7) · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `python scripts/decision_client.py --scan-imports` · `ls .opencode/plans/Archives/ \| wc -l` y `ls .opencode/plans/Archives/*/00-lecciones-capitalizadas.md` | HEAD **sin cambio** respecto del antecedente publicado y **paridad verificada contra el remoto** (`fetch` + `ls-remote` + `0 0`), no inferida de la frase del README; árbol con **62 rutas sucias de trabajo ajeno** (las del bloque B, del bloque C de la orden y de `EVALUACION-JEV`), ninguna creada por esta sesión al medir; índice **fresco** con su cifra leída del comando (no pineada en ningún artefacto de C); quick **11/11 `exit 0`** como par PRE de AC16 y hook **7**; `*.jsonl` = **0** → **séptima reproducción** de la precondición de **D-V2.1**, el instrumento de presupuesto sigue fuera de servicio y C declara auto-reporte con unidad propia; AC6 `SIN-HALLAZGOS` / `exit 0` **antes** de escribir C. **Y la premisa de AC13 resultó vencida en su ruta**: el prompt decía `Archives/`, el `archives/` de raíz **no contiene planes**, y el corpus efectivo es `.opencode/plans/Archives/` con **27** archivados de los que **2** tienen `00-` que triar. Nada del antecedente del prompt se copió como valor vigente |
| Q9 | **Re-medición de la premisa al abrir FASE-A (2026-09-21)** — el prompt ordenaba no asumir el árbol | `git rev-parse --short HEAD` · `git status --porcelain | wc -l` · `git ls-remote origin refs/heads/master` · `grep -nE '^[[:space:]]*(def _check|print.f?"\[[0-9]+/[0-9]+\])' scripts/run_all_validations.py` · `grep -nE '^#[[:space:]]+\[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit` · `stat -c %s` sobre los siete documentos de A7 · `grep -rhoE '\[[0-9]+/[0-9]+\]' <los dos documentos> | wc -l` | HEAD ya **no** era `2c9d0c1`: es `2deddee`, con once commits de `EVALUACION-JEV-TYPESAFE-2026-09-21` encima; árbol **limpio** y paridad `0/0` con `origin/master` **conservadas**. El emparejamiento etiqueta ↔ `def _check_*` reproduce A1–A3 (`validate_plan_citations` 9/11, `validate_lesson_capitalization` 10/11, `validate_qmind_writeback` **15/15** solo en el modo completo); el hook sigue en **7** pasos; A7 sigue en **263.973 bytes** y la población A8 se reprodujo **exacta**: 22 instancias con corchete en 17 líneas + 2 formas «check N». **Ninguna premisa del plan caducó en la ventana de A salvo el HEAD anunciado**, que es justo lo que el prompt ordenaba medir |
| Q8 | Carga de lectura de una sesión de fase (medición A7) | `for f en los 7 documentos sumados (más 1 de evidencia excluido) que declara leer 05-prompt-inicio-sesion-fase-B.md del plan en vuelo; do stat -c %s "$f"; done` y sumar | Al concebir: **254.010 bytes ≈ 63.502 tokens**. **Re-medido el 2026-09-20: 263.973 bytes ≈ 65.993 tokens** (+9.963; crecieron `06-checklist`, `00-lecciones`, `dependencias-fases` y el propio `05-…-fase-B.md` al cerrarse FASE-G y FASE-B del plan medido). Divisor 4 declarado. El workflow canónico aporta 98.694 bytes, de los cuales ~20 KB son plantillas de cierre |

**Regla**: la consulta debe ser copy-pasteable. Q1–Q6 y Q8 se re-ejecutan tal cual; **Q7 solo con el
ID del notebook** (la forma con el nombre que aparece en el workflow canónico devuelve `Bad request`,
medido el 2026-09-20). **Toda cifra de Q4
y Q8 caduca al escribir cualquier `.md` del corpus** — ver maestro §1, mediciones A6 y A7.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 12923 bytes copiados de 53192 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `00-lecciones-capitalizadas.md` §2

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-R.1 | Una regla que vive solo en el workflow y no en el artefacto que la fase rellena, se cumple por coincidencia | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | El plan existe porque las aserciones numéricas del workflow y de su template **no las sostiene ningún check**: se cumplen por coincidencia y hoy están vencidas | AC1 · FASE-A Tarea 1  · **aplicada el 2026-09-21 en FASE-A:** el verificador ahora contrasta contra la etiqueta impresa por el `def _check_*` que la ejecuta; las cuatro aserciones siguen vencidas sin que ningún gate las sostenga, y el guard existe (reporta, no reescribe) |
| L-R.3 | Un `[OK]` sin denominador no informa: el verificador publica la población que miró | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Ninguna salida del lint o del triaje puede decir «sin hallazgos» sin imprimir cuántas aserciones/IDs miró y quiénes quedaron exentos | AC2 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `coverage_basis` es obligatoria y el favorable está bloqueado sin ella (prueba `test_la_salida_favorable_no_existe_sin_denominador`); con denominador impreso: 24 miradas / 11 correctas / 8 congeladas / 0 no resueltas · **aplicada el 2026-09-21 en FASE-B (AC6/AC9):** el `0` de imports se publica con **dos** poblaciones (678 rastreados por `git grep` / 692 del árbol que ve el AST), los 4.379 nodos de import vistos, las 21 menciones-no-import aparte y los excluidos por directorio con su conteo; y el `1` de `files_changed_to_add_provider` sale de sha256 sobre la frontera copiada, no de una afirmación (L-VCF-8) · **aplicada el 2026-09-24 en FASE-D:** `coverage_basis` del informe imprime 5 packs por estado, 34 fuentes, 23 secciones pedidas / 23 resueltas y las cinco familias no cubiertas; y el corpus real se publica con su denominador de convencion (**0 de 121** prompts archivados declaran lectura) en lugar de un `[OK]` a secas |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Las tres reglas que este plan no cierra (promoción al quick, rebanado del workflow, arreglo de `.agents/`) se publican con dueño y disparador, no se callan | AC17 · `dependencias-fases.md` §Deuda  · **aplicada el 2026-09-21 en FASE-B:** la comparación de proveedores se declaró **fuera de alcance** en `extensibilidad.txt` con su porqué (D7) y la decisión de geometría que este plan **no** tomó salió con dueño y disparador nuevos: **S10** (L-VCF-9) |
| L-NC10 | Fosilización narrativa como clase de bug: templates con texto estático que ignoran la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22` | Mismo defecto, otro artefacto: el template fija «`[10/10]` de `--quick»` cuando el código emite `[10/11]`. La cura es comparar contra la fuente, no reescribir la frase | AC1 · AC4  · **aplicada el 2026-09-21 en FASE-A:** la lista de aserciones se **descubrió** escaneando los dos documentos (24 instancias: 22 con corchete + 2 formas «check N»), no hardcodeada; A1 apareció en dos sitios que el patrón nunca había visto juntos · **aplicada el 2026-09-24 en FASE-D:** el generador no recibe ninguna lista de lecturas por configuracion: parsea la que el propio prompt declara. El test confronta `parsear_lista_lectura(prompt)` contra las fuentes del pack emitido, y `no_incluye[]` publica los bytes que quedaron fuera de lo declarado |
| L-PF6 | Un lector roto leído como ausencia real produjo un pain falso HIGH con cifra económica | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El triaje lee `lecciones_index.json` y el lint lee `.agents/`: ambos publican los tres estados, y un parser que revienta jamás devuelve «sin candidatos» | AC3 · AC11  · **aplicada el 2026-09-21 en FASE-A:** cuatro caminos de `LECTOR-FALLIDO` con motivo propio (fuente sin etiquetas, hook sin pasos, documento sin patrones, sujeto ambiguo por alias); ninguno devuelve «sin hallazgos» · **aplicada el 2026-09-21 en FASE-B (AC7):** la prohibición del default es el eje del módulo — `evaluar()` sin proveedor **falla** con 5 `motivo_clase` que no colapsan, y el mutante `M-AC7-proveedor-por-defecto` muestra que ceder un default sí fabricaría una decisión. Coste propio descubierto al medir: la regla «nadie más importa el SDK» aplicada sin graduar producía **16 hallazgos ajenos** (L-VCF-7) · **aplicada el 2026-09-24 en FASE-D:** el lector de la lista declarada falla ruidoso y por causas separadas — `--plan` inexistente = exit 2 con sus tres rutas intentadas; fuente ausente = el pack **no se emite** (exit 1) con la ruta buscada; meta sin sha = `FUENTE-ILEGIBLE`, que no colapsa con `FUENTE-AUSENTE` ni con `SHA-DISTINTO` |
| L-PF10 | Vacío ≠ ausente: la lista quedó vacía **porque el fix funcionó**, y el extractor devolvía `None` igual que cuando el dato no existe | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El estado `SIN-HALLAZGOS` del lint es un resultado positivo y debe decir sobre qué midió; `AUSENTE` debe imprimir la ruta buscada y el comando de regeneración | AC3 · AC11 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `SIN-HALLAZGOS` imprime sobre qué midió y `AUSENTE` la ruta buscada; un documento no vacío con 0 instancias es fallo de lectura, no «limpio» · **aplicada el 2026-09-21 en FASE-B:** `respuestas: []` es `ILEGIBLE` con causa `respuesta-vacia:list` (no «cero decisiones favorables»), `usage=None` **no** es consumo cero, y `noul.confidence` es `None` **con su motivo escrito**, no un 0.0 que FASE-C leería como certeza · **aplicada el 2026-09-24 en FASE-D:** al trío de AC22 hubo que sumarle un cuarto estado, `SIN-DECLARACION` (pack emitido con cero fuentes gobernadas), y el `--check` lo imprime como `SIN-FUENTES` en lugar de `OK` — con test que prohíbe la palabra OK en esa salida. Motivo medido: 121 prompts archivados no declaran lectura, y llamarlos «completos» era el verde vacio de L-HF1 |
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El invariante «el quick sigue en 11 checks» se formula como **delta** con par `*_baseline_pre/post.txt`, no como número absoluto | AC5 · AC16 · AC20  · **aplicada el 2026-09-21 en FASE-A:** los conteos se publicaron como delta con par pre/post y la resta (quick 0, hook 0, población A8 0); la métrica que sí se movió (tests, +23) se declaró aparte en lugar de maquillarla · **aplicada el 2026-09-21 en FASE-B:** quick 11→11, completo 4→4, hook 7→7, `.agents/` 98.694/6.123 idénticos y población AC6 678 sin mover y 690→**692** en el árbol (+2 por los instrumentos de la propia fase: nota 3 en `FASE-B/baseline-pre-post.md`) — con **+48 funciones / 53 casos** de tests publicados por separado. Y una elección de unidad: no se publicó un `tool_use` aproximado, porque no era medible (R2.1) · **aplicada el 2026-09-24 en FASE-D:** la carga de lectura se goberno como delta con par `faseD_carga_pre/post.txt` (`stat -c %s`) y resta **entre cargas totales**; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (exit 0) y quick 11→11 / hook 7→7. Y un test planta una fuente diminuta para exigir que un delta **negativo** se publique con la misma identidad, no que se esconda |
| L-V2.3 | Renumerar el hook sin medir quién afirma el número de checks deja contrato huérfano | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Este plan **no renumera** nada: su AC5 y AC16 exigen medir la población que afirma los conteos antes de tocarla, y no pinear literales | AC5 · AC16 · AC8  · **aplicada el 2026-09-21 en FASE-A:** el barrido de `tests/` mostró que **esta fase añadió 4 pins del denominador 11** al fijar el contrato AC1 (L-VCF-5), declarados con dueño D1/D2 en vez de limar la aserción · **aplicada el 2026-09-21 en FASE-B (AC8):** el contract test afirma la **forma** y compara el modelo contra lo que el proveedor falso **declara**, nunca contra una cadena; el pin `jev-1.13.0` vive en `PIN_MODELO_DECLARADO` con `usado_por_el_codigo: false` y un test lo comprueba por AST (aparece una sola vez: su definición). FASE-B **no añadió** pins del 11 ni del 7 (4→4, medido) · **aplicada el 2026-09-24 en FASE-D:** AC21 se prueba **escribiendo la fuente en disco** y re-midiendo contra ese disco (y al revertir, verde); y AC23 se anclo con una cadena exclusiva del generador, porque «rutas intentadas» y «seccion pedida» ya vivian dentro de los documentos que el pack copia — un mutante anclado ahi daba rojo sin serlo |
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Cada mutante de AC4 y AC14 se afirma sobre el `assertion_id`/la detección que dice atacar, no sobre «el script devolvió un hallazgo»: el rojo tiene que nombrar la aserción mutada | AC4 · AC14 |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por **otro** gate | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | FASE-C lee `lecciones_index.json`, que produce `[6/7]`; la cura ya implementada por ese plan es **calcular el índice en memoria** con `build_lesson_index.build()` (0,30 s medidos). ⟦**Ruta CERRADA el 2026-09-23, contrato E2**: FASE-C consume el JSON **tras ejecutar él mismo** la comprobación de frescura, de modo que `VENCIDO` sea estado producido por su propio check y no por un `--check` ajeno; la ruta (a) queda descartada porque **borraría** el estado que AC11 exige, y sigue prohibida la tercera vía (leer el JSON confiando en que otro paso lo regeneró). Coste publicado: C es responsable de su suelo y hace dos lecturas del JSON por corrida⟧ | AC11 · AC15 |
| D-V2.1 | El instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el cliente actual; la medición se publica como auto-reporte con **unidad declarada** | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` (definida allí; **reproducida en cuatro fases seguidas** por `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`) | El `04-contrato-ejecucion.md` de este plan ya aplica el patrón (instrumento, corte, y si no corre: unidad declarada, «no comparable», o métrica retirada — nunca estimada). Verificado el 2026-09-20: `find . -name "*.jsonl"` devuelve **0** dentro del workspace, la misma precondición del incidente | **AC5** · **AC16** (par pre/post por fase) · `04-contrato-ejecucion.md` §Corte de presupuesto |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Todo AC de detección del plan se cierra con mutation check sobre el símbolo real del guard, con las dos salidas en evidencia | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** seis mutantes sobre los símbolos reales del guard, con verde y rojo en disco — y el primer intento de anclaje (id posicional) **no** observaba la rama que decía certificar: ver L-VCF-1 · **aplicada el 2026-09-24 en FASE-D:** mutation check con las dos salidas en disco — apagado `GUARD_NO_TRUNCAMIENTO_ACTIVO` el pack conserva el estado `SECCION-NO-RESUELTA` pero **pierde la declaracion del recorte** y se achica en silencio (los dos tamaños y su diferencia viven en `FASE-D/mutation/resumen.txt`; **no se transcriben aquí**: este `.md` entra en el pack que lo mide → **L-VCF-19**). Un test aparte exige que el mutante NO cambie el estado: si lo cambiara, el rojo vendria de otra rama (L-V2.1) |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30` | El verde de la primera corrida del lint se reporta **sospechoso** y se explica, nunca como éxito | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** el verde de la primera corrida **fue sospechoso y lo era**: la regla de población se rectificó dos veces y el mutation check nombraba a la aserción equivocada · **aplicada el 2026-09-21 en FASE-B:** la primera corrida de la selección dio **30 fallos** (f-string mal cerrado, `score` cayendo en `opciones` por argumento posicional, 8 aserciones mal apuntadas) y el primer mutante de forma apagaba la lista **entera**, que no aislaba a ningún guard (L-VCF-6). Rojos propios además de los buscados: AC8 guarda su `exit 1` en `contract.txt` |
| L-HF1 | Un candado con la cobertura equivocada pasa en verde mientras el artefacto miente | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El lint declara las familias de aserción que **no** cubre, una por una y medidas: prosa de conteo sin patrón, conteos fuera de los documentos de gobierno (`AGENTS.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), pins de conteo en `tests/` y toda fuente dinámica que no sea etiqueta impresa. Ese límite es AC, no nota al pie | AC2 · AC17  · **aplicada el 2026-09-21 en FASE-A:** `families_not_covered[]` salió de la AC y del script: las cuatro familias medidas en el informe (3 / 245 / 4 archivos / 4.330 funciones en disk), y `git status --porcelain .agents/` quedó vacío · **aplicada el 2026-09-21 en FASE-B:** el escáner publica sus cuatro límites medidos (carga no literal → 16 sitios contados y no callados; dependencias declaradas → no miradas, es D7; menciones en prosa → aparte; exclusiones → con su conteo) y `git status --porcelain .agents/` volvió a quedar vacío con 98.694/6.123 bytes idénticos · **aplicada el 2026-09-24 en FASE-D:** `no_incluye[]` no vacio es exigido por test fase por fase, y del medir salio una regla nueva: lo que vive **fuera** de `.opencode/` se declara lectura aparte y no se copia, porque copiarlo dentro del plan ampliaba la poblacion que escanea `validate_opencode_refs.py` y un artefacto derivado le devolvio rojo al quick ([8/11]) por referencias ajenas |

Dueños distintos representados: **6** — TRIBUNAL-OFFLINE, REFACTOR-COHERENCIA-NARRATIVA, SR-PIPELINE-FIXES, ESTABILIZACION-PRE-TRIBUNAL, PASO0-VERIFICADOR-CAPITALIZACION y VALIDADOR-URL-PROPIA. Satisface C8 (≥2) con holgura y no repite solo al predecesor. **Doble corrección del 2026-09-20**: la fila decía **7** cuando las once originales ya tenían **6** dueños nombrables (L-R.3 aplicado a este propio archivo: el conteo se re-mide, no se copia), y las tres lecciones nuevas de la capa tibia **no suman dueño** — `D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, no en `TRIBUNAL-ENFORCEMENT-OBS`, que es donde la **reproducen** cuatro fases seguidas. Lo detectó `validate_lesson_capitalization.py` con su checks `C7` (atribución contra el índice), no una lectura humana: es el verificador de forma de este mismo plan funcionando sobre su propio `00-`.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 14966 bytes copiados de 53192 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `00-lecciones-capitalizadas.md` §3

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-A6, L-V4, L-H4 | Son la familia «la cita de línea cadura». Este plan no introduce citas de línea en ACs ni prompts y **no reescribe** las ajenas: `validate_plan_citations.py` ya las gobierna con alcance hacia delante + delta, y su política está recogida como restricción en `04-contrato-ejecucion.md`, no como trabajo nuevo |
| DA-HF3 | Misma política de alcance (hacia delante + delta, reporta sin reescribir). Ya está implementada en el verificador de citas; este plan la **hereda** como diseño de AC16, no la reconstruye |
| L-SR3, L-SR5 | Fuente única de verdad del estado de un servicio y gate bloqueante que no solo loggea: son del dominio de producto (promesas/métricas del pipeline v4). Ninguna fase de este plan toca el pipeline ni sus gates |
| L-VUP-1 | La baseline «13 rojos» que midió 14 por un test orden-dependiente del audit: este plan no ejecuta el audit ni hereda esa selección de tests |
| **D5** (no es ID: medición propia) | `grep -icE "verificador mec"` devolvió **0** sobre el índice, y sí existen verificadores nombrados en el corpus. Un cero de grep **no distingue** «no existe» de «busqué la palabra equivocada» — es la variante léxica de L-PF6. Se descarta el grep como única puerta de pertinencia y se registra como la evidencia que justifica FASE-C (AC15 obliga a publicar la población y el término usado) |

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 1492 bytes copiados de 53192 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `00-lecciones-capitalizadas.md` §4

## 4. Cobertura declarada de este documento

- **Qué sí deja evidencia**: **catorce** consultas re-ejecutables (Q9 al abrir FASE-A; Q10 al abrir FASE-B; Q11 tras commitear B; Q12 al abrir FASE-C; **Q13 al abrir FASE-D, que es la que re-mide el workflow, la población de la convención `Lee …` y el índice sobre un árbol extraído con `git archive`**) — al concebir (Q9 el 2026-09-21 al abrir FASE-A; **Q10
  el 2026-09-21 al abrir FASE-B**, que es la que comprueba que la herencia de B no se asumió; **Q11 el
  2026-09-22 tras commitear B**, que desglosa la brecha entre las dos poblaciones de AC6) — al concebir
  eran ocho consultas re-ejecutables con su resultado medido, **catorce** lecciones con ID, dueño y un
  «qué cambia» que nombra un AC concreto (once al concebir + L-V2.1, L-V2.2 y D-V2.1, que trajo la capa
  tibia el 2026-09-20), cinco descartes con motivo y una medición propia (D5) que refuta el atajo obvio.
  **Al cerrar FASE-B se añaden cinco lecciones nuevas propias (L-VCF-6 a L-VCF-10, definidas con su
  medición en `10-analisis-post-implementacion.md`), dos más que escribieron el commit de la fase y su
  barrido (**L-VCF-11**: el denominador refutado al commitear; **L-VCF-12**: el verificador que pisó la
  evidencia de FASE-A por tener su destino hardcodeado), y deudas con dueño y disparador nuevos —
  **S10** (la geometría del `import` del SDK cuando D7 se active), **S11** (la exclusión no declarada del
  denominador) y **S12** (el default de `--report` sobre un registro cerrado; con guarda publicada en el
  README para que FASE-C no la re-pise, **guarda sin efecto desde el 2026-09-23** — ver la fila
  siguiente).**
- **Qué NO verifica el check mecánico**: la **pertinencia**. `validate_lesson_capitalization.py` comprueba forma y trazabilidad (C1–C8: consultas corpus-wide, ≥3 descartes, AC nombrado que existe, dueño publicado por el índice, ≥2 fuentes) y **ninguno de sus checks puede saber si la lección que debía capitalizarse era otra**. Un `[OK]` suyo significa «la forma exigida está». Ese límite declarado es exactamente el hueco que abre este plan.
- [x] **FASE-D cerró el 2026-09-24 con `build_phase_briefing.py` y sus 5 packs** dentro del plan
  (`…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`). Estado medido: **COMPLETO 4 ·
  SECCION-NO-RESUELTA 1 · FUENTE-AUSENTE 0** sobre 34 fuentes declaradas y 23 secciones pedidas
  (23 resueltas). La carga total de las cinco fases **bajó**, y el delta queda **muy por debajo del
  tercio** que el plan esperaba porque **el workflow canónico sigue entrando en los dos lados**: los
  dos totales, la resta y su comprobación los imprimen `FASE-D/carga.json` y `FASE-D/carga-pre-post.md`
  y su lectura métrica vive en `09` §D. **Aquí no se transcribe ninguna de esas cifras y eso es parte
  del hallazgo**: este documento entra en el pack que ese comando mide, así que copiar la carga en él
  la vence en el mismo gesto (**L-VCF-19**).
  Herencia de C aceptada sin reabrirla: la parte mecánica del triaje se exhibe en el pack, y su
  tramo semántico sigue `NO-EJERCITADO`, con **D6 dormida** (contrato E4). No se re-negoció E1–E5.
- [x] **La convención que parsea el generador es minoritaria y eso se midió, no se supuso**: de
  **121** prompts bajo `.opencode/plans/Archives/`, **0** declaran su lectura con la cadena
  `Lee …`; los únicos **5** del repo son los de este plan. Un test contra corpus real por eso
  afirma hoy el **corte** (el pack sale `SIN-DECLARACION` y su check `SIN-FUENTES`, no `OK`) y la
  escritura de la convención en `prompt-fase-template.md` quedó como deuda **S16**, con dueño y
  disparador, porque tocar `.agents/` es AC17/D1 y no compete a esta fase.
- [x] **El plan se auto-trió al cerrar FASE-C (2026-09-24), y el resultado NO se aplicó a sí mismo.**
  `scripts/triage_lesson_relevance.py` corrió sobre este propio `00-` con el **proveedor falso
  determinista** de la selección (el informe publica `coste.emisor = {nombre: falso-pertinencia,
  falso: true, credencial_env: null}`). Conteos del auto-triaje, con su artefacto:
  **propuestas aceptadas para §2: 0 · rechazadas: 0 · pendientes de revisión humana: 5**
  (`informe.json` → `buckets.propuesto`; 16 candidatos más quedaron en `a-revisar-humano` por
  `confidence` debajo del umbral o por rechazo confidente del emisor), y **11 de las 14 filas ancladas
  fueron juzgadas `no-pertinente` por el emisor y ninguna se borró** (`ac10_delta.json` →
  `removed: []`, `filas_cuestionadas_sin_borrar`). **Este §2 sigue teniendo las mismas catorce filas
  que tenía al cerrar FASE-B**, y esa invariancia es AC10, no olvido. Por qué cero aplicadas: una
  propuesta de un falso prueba la mecánica del camino, no la pertinencia (contrato **E3**), y aplicarla
  habría escrito aquí una fila cuya evidencia es sintética — lo que AC15 declara `NO-EJERCITADO`. Si
  alguna se revisa, entra con dueño, «qué cambia» real y la revisión que la avala registrada con quién
  decidió; si se rechaza, **se publica el rechazo con su motivo y la fila no desaparece**.
- [x] **Las cinco propuestas del piloto quedan declaradas PENDIENTES con su dueño (2026-09-25, cierre de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22`).** `L-VCF-10`, `L-VCF-11`, `L-VCF-12`, `L-VCF-13` y
  `L-VCF-14` son las cinco que publica `informe.json` → `revision_humana.propuestas_pendientes`
  (`n_pendientes: 5`, `registros: []`), definidas cada una con su medición en
  `10-analisis-post-implementacion.md`. **Dueño: el operador**, a través de la revisión humana que fija el
  contrato **E3** — no es una fase ni un script: `seccion_dos_editada_por_este_script: false` sigue siendo
  cierto después de esta sesión. **Ninguna se aceptó, se rechazó ni se copió a §2**, que conserva sus
  catorce filas (**AC10**). Lo que cada una necesita para entrar: un «qué cambia» real que nombre un AC de
  este plan, la revisión que la avala registrada con quién decidió, y una evidencia que no sea la de un
  emisor falso mientras **D7** esté inactiva — por eso se declaran pendientes en lugar de cerrarse.
- [x] **El hueco que este archivo declaraba fuera de alcance ya tiene instrumento**: la limitación del
  párrafo anterior («Qué NO verifica el check mecánico: la pertinencia») sigue siendo cierta de
  `validate_lesson_capitalization.py` — su `[OK]` jamás significó «capitalicé bien» —, pero desde el
  2026-09-24 existe la otra mitad: `triage_lesson_relevance.py` pregunta por pertinencia, publica su
  denominador con sus ceros y **propone sin filtrar**. Lo que **no** cierra: el juicio semántico real,
  que espera proveedor (deuda **D7**), y por eso **D6** sigue dormida.
- [x] Este archivo es verificado por `scripts/validate_lesson_capitalization.py` (`[7/7]` del hook versionado en `scripts/git_hooks/pre-commit`) y por `scripts/build_lesson_index.py --check` (`[6/7]` del mismo hook).
- [x] **Limitación del Paso 0 registrada y SUPERADA el 2026-09-20**: la capa tibia (QMind `iah-cli-lecciones`) **no se consultó** en la concepción porque el CLI no estaba disponible en esa sesión; se aplicó el fallback del executor (memoria de proyecto + índice generado) y quedó registrado aquí y en `dependencias-fases.md`. En la auditoría de la concepción del mismo 2026-09-20 el CLI **sí** estuvo disponible y autenticado: se ejecutó Q7 con cuatro consultas y sus resultados se capitalizaron arriba (L-V2.1, L-V2.2, D-V2.1). **El comando con el nombre de notebook no es re-ejecutable**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; el identificador válido es `01a04d98-b7bd-778c-8441-26fdc7e35f45`. Queda como verificación de **D8** re-corrida antes de RELEASE por si el corpus cambió. ⟦**Re-fechada el 2026-09-25, al cerrar FASE-RELEASE**: la re-corrida **no** se hizo. D8 es operación de red y el mandato del cierre la dejó explícitamente fuera (checkpoint C1, `PENDIENTE-AUTORIZACION`). Lo que se declara es que **la premisa «el corpus del notebook cambió desde el 2026-09-20» quedó no comprobada**, que no es lo mismo que «no cambió», y que la capitalización de §2 sigue apoyada en la consulta de aquella auditoría. La limitación del comando con nombre sigue vigente: no es re-ejecutable tal cual⟧.
- [x] **Actualizado al cierre de FASE-A (2026-09-21)** con el balance de §5, la consulta Q9 re-ejecutable y las cinco lecciones nuevas de esa fase.
- [x] **Actualizado al cierre de FASE-B (2026-09-21)** con el balance de §6, la consulta Q10 re-ejecutable, las cinco lecciones nuevas de B (L-VCF-6 a L-VCF-10) y la deuda **S10**. Ocho de las diez lecciones filtradas por su prompt se ejercitaron y las dos restantes quedaron asignadas y declaradas (L-V2.1 y L-V2.2: la primera se volvió a caer, la segunda es de FASE-C). Sigue **sin** cerrarse el plan: faltan C, D y RELEASE, y el write-back de QMind se ejecuta **antes** del `git mv` a `Archives/` en esa última sesión (orden R2.5 / R2.10, con la interfaz del writer re-leída por D10).
- [x] **Actualizado el 2026-09-22, al commitear FASE-B** (`647f436`): la consulta **Q11** re-ejecutable,
  la lección **L-VCF-11** y la deuda **S11**, las tres nacidas del propio commit — que refutó una cifra
  que la fase acababa de publicar (678 → **691** `.py` rastreados) y dejó ver, al desglosar la
  brecha con el escáner, una exclusión no declarada en el denominador. Es A6 golpeando otra vez, ahora
  sobre el instrumento de la fase: **un cero medido sobre una población que nadie definió del todo**.
- [x] **Conciliada el 2026-09-23 (solo lectura, sin nueva instrumentación).** Las dos lecciones que
  escribió el commit de B — **L-VCF-11** y **L-VCF-12** — tenían su deuda asociada (**S11**, **S12**)
  corregida en código **por otro trabajo**: el bloque A de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, commit **`fdd397f`**, que declaró explícitamente que lo
  suyo era *corrección técnica, no cierre contractual* porque la enmienda correspondía a este plan. **Esa
  enmienda es la que se registra ahora** en `dependencias-fases.md` §Conciliación, con las tres capas
  separadas: cierre original (`647f436`) / corrección (`fdd397f`, ajena) / aceptación (2026-09-23). Las
  lecciones **no caducan**: L-VCF-11 sigue siendo la regla de desglosar una brecha entre dos poblaciones
  archivo por archivo (hoy verificada por medición: 696 escaneados vs 691 rastreados → residuo 0) y
  L-VCF-12 sigue siendo la regla de mirar el default de escritura de un verificador antes de correrlo.
  Lo que sí se retira es su aplicación concreta: la guarda del README sobre `--report` sin destino, que
  S12 dejó sin objeto. Y **ninguna de las dos correcciones toca el rojo contractual**: A1–A4 siguen
  vencidas en `.agents/` (`exit 1` re-medido) porque ese es **D1**, con instrucción literal del operador.
  ⟦**Vencido ese cierre el 2026-09-25, con atribución**: el `exit 1` de A1–A4 describía el árbol antes de
  que el **bloque B** de la orden recibiera su autorización para editar `.agents/`. Re-medido en el cierre de
  FASE-RELEASE con el mismo instrumento y su modo de solo lectura
  (`validate_governance_numbers.py --report`, sin destino): **`status: SIN-HALLAZGOS`, `exit 0`**. El veredicto
  de **D1** no lo da esta línea ni ese número: lo da la **matriz §13** de la fuente única de B, donde aparece
  **CERRADA en su alcance**. Lo que la lección conserva intacta es su regla de procedimiento: **leer** el
  verificador no es **reparar** `.agents/`, y eso fue lo único que hizo este cierre⟧.
- [x] **Actualizado al cierre de FASE-RELEASE (2026-09-25, parte offline).** El plan cerró sus cinco fases:
  release **4.78.0** en la fuente única, cinco cabeceras por su writer, `DOMAIN_PRIMER.md` regenerado con el
  suyo, `[4.78.0]` en `CHANGELOG.md` y registro en `REGISTRY.md` por su **único** escritor. Sobre este
  archivo, lo que el cierre **no** tocó y lo que sí: **no** se aceptó ni se rechazó ninguna de las cinco
  propuestas de revisión humana (L-VCF-10…14 siguen `pendientes`, §2 conserva sus catorce filas — AC10 y
  contrato **E3**), y **no** se capitalizó por cuota. Lo que se re-fechó es la limitación de Q7/D8 (arriba)
  y la lectura de D1. El cierre deja dos defectos de instrumento declarados y sin cura en esta fase: los
  writers de texto que reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y la regla
  `readme_version_header`, que no goberna la fecha legible del `README.md`.
  ⟦**Ese «sin cura en esta fase» se cumplió y luego venció el mismo 2026-09-25**: el cierre no los curó
  (no tenía mandato de código) y quedaron registrados como **S17** y **S18**; una sesión posterior, con
  mandato de código del operador, los curo — tres escrituras con `newline="\n"` (la de `run_status`
  apareció al curar) y la regla de la fecha legible goberna y escribe por su escritor. Estado vigente:
  §S17/§S18 de `dependencias-fases.md`; prueba en
  `tests/test_sync_writers_lf_y_fecha_readme.py`. Ninguna de las dos fue una lección nueva de este
  archivo: no se capitalizó por cuota. Las reglas generales que las produjeron ya estaban escritas —
  mirar el default de escritura de un verificador antes de correrlo (**L-VCF-12**) y arreglar un dato
  en su escritor, no con un tercero que lo reescriba a mano⟧.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0` · 13385 bytes copiados de 53192 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

## Fuente: `dependencias-fases.md` §Conciliacion

## Conciliación con la remediación del bloque A — aceptación de S11 y S12 (2026-09-23)

**Qué se acepta y de dónde viene (procedencia, no atribución a esta sesión).** Las dos deudas
nacidas del commit de FASE-B fueron corregidas **fuera de este plan**, por las cuatro sesiones
autorizadas del **bloque A** de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, y el
código corregido entró al repo en **`fdd397f`** sobre la superficie
`scripts/decision_client.py`, `scripts/validate_governance_numbers.py`,
`tests/quality_gates/decision_client/` y `tests/quality_gates/governance_numbers/`. El resumen de esa
remediación (`evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/00-resumen-bloque-A.md` §4) dice de sí misma,
y se cita literal por ser el límite que esta fila respeta: **«lo aplicado es CORRECCIÓN TÉCNICA, no
cierre contractual»**, porque el traslado de S11/S12 a ese bloque exigía la enmienda registrada **en
este plan**, que era el pendiente. **Ese pendiente es lo que esta sección cierra**: el plan propietario
CONTEXTO acepta la remediación y registra el traslado. El mérito técnico es de esas sesiones y de `fdd397f`;
esta sesión **no** editó código ni tests.

**Alcance de lo aceptado** — solo S11 y S12, y solo en lo que el bloque A hizo:

| Deuda | Cura aceptada (en `fdd397f`) | Re-validación offline medida el 2026-09-23 |
|---|---|---|
| **S11** — `.venv-wsl` faltaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` y las exclusiones se solapan | La exclusión entra en la lista **y su conteo se publica**; dos pruebas de población sobre árbol plantado; el escaneo se comparte entre aserciones del mismo árbol | `python scripts/decision_client.py --scan-imports` → `SIN-HALLAZGOS`, **0** imports prohibidos, `exit 0`; población escaneada **696** vs `git ls-files '*.py'` = **696** → **residuo 0** (la resta que en B cerró en 692−691 ya no existe); `.venv-wsl` figura en `excluidos_por_directorio` con **582** archivos |
| **S12** — `--report` sin destino re-escribía `evidence/…/FASE-A/informe.json` | El destino por defecto desaparece de los dos verificadores: `--report` a secas **imprime y no escribe**; el aviso va a stderr y el stdout queda JSON puro; **seis** tests nuevos en `tests/quality_gates/governance_numbers/` ⟦rectificado el 2026-09-23: esta fila decía «cinco»; corridos por nombre dan **6 funciones / 6 casos** en `test_governance_numbers_s12_report_no_escribe.py`, y el directorio completo **35 funciones / 40 casos**, `40 passed` con `EXIT=0`⟧ | `python scripts/validate_governance_numbers.py --report` sin destino → **`exit 1`** con `status: HALLAZGOS` y `assertion_ids = [A1,A2,A3,A4]`; `sha256` de `evidence/…/FASE-A/informe.json` **idéntico** antes y después de la corrida; `git status --porcelain evidence/` **vacío** |

**Los tres momentos van separados, y así quedan:** (1) **cierre original de FASE-B** — `647f436`
(2026-09-22), que cerró AC6–AC9 y **produjo** S11/S12 al mover el denominador y al re-muestrear;
(2) **corrección posterior** — `fdd397f` (2026-09-22), bloque A de la orden, técnica y probada por su
dueño; (3) **aceptación** — esta sección, 2026-09-23, que además re-mide offline. Ninguna de las tres
se atribuye a las otras dos.

**Qué NO cerró aquella aceptación (antecedente fechado).** El rojo contractual A1–A4 seguía vivo:
`validate_governance_numbers.py` salía `exit 1` porque aquella sesión no editaba `.agents/` (AC17,
D1/S1); la remediación del bloque A no lo tocó. Después B recibió autorización de corrección, pero
su estado vigente remite a la **matriz §13** de la fuente única, no a ese rojo ni a verdes retirados.
Y siguen abiertas, con dueño, **sin** convertirse en bloqueantes artificiales de una
FASE-C offline: **S10** (dónde vivirá el `import` del SDK cuando D7 se active), **D7** (activar el
proveedor) y **D6** (lint semántico, **dormida** porque su disparador es el `acceptance` de AC15).

**AC9 queda declarado con su alcance real** (no solo su cifra): certifica **extensión local** —
registrar un proveedor **falso** del repo a través de la costura, sin red ni credenciales, medido por
sha256 (`files_changed_to_add_provider = 1`, re-medido el 2026-09-23 con `--costura`, `exit 0`). **No**
certifica el coste total de integrar un **SDK real** en un archivo: dependencias y autenticación no se
midieron ni pueden medirse bajo la regla de cero red. El propio `--costura` ya imprime esa acotación
en su clave `alcance_de_ac9`, y la ubicación futura de ese SDK es **S10**/D7, coordinada con el plan
hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`.

**Instrumentos reutilizados, no nuevos.** Esta conciliación no añadió instrumentación: corrieron los
existentes de B (`--scan-imports`, `--costura`, `--provider-status`) y de A (`--report`), más la
selección `tests/quality_gates/decision_client` (**87 passed**, `exit 0`). **No se repitió la suite
completa por rutina**: su estado vigente es el que publicó la sesión 4 del bloque A, y lo que aquí se
ejecutó es la selección pertinente, distinguible de los resultados históricos de B. Crudos, comandos y
códigos en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/`.

### S16 — la convención que parsea el generador no está escrita en ninguna fuente (nueva, 2026-09-24)

**Hecho medido al cerrar FASE-D**: `build_phase_briefing.py` extrae la lista de lectura del prompt
desde la cadena `Lee …` dentro de un bloque fenced de «Prompt de ejecución». Sobre el corpus
completo: **121** prompts de fase bajo `.opencode/plans/Archives/` y **0** la usan; **5** prompts la
usan en todo el repo y son los cinco de este plan. Consecuencia directa y probada: el pack de un
plan archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES` — el corte del
generador, no su defecto.

- **Dueño**: `.agents/workflows/templates/prompt-fase-template.md`, sección 8 (Prompt de Ejecución),
  y por arrastre los prompts de los planes vivos. **No es de FASE-D**: escribir en `.agents/` es
  AC17 y esa superficie es D1/con instrucción literal del operador.
- **Disparador**: la próxima vez que un mandato autorice tocar el template (precedente: el bloque B
  de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` autorizó `lecciones-capitalizadas-template.md` para
  retirar A4). Ahí se añade la forma canónica de la lista de lectura, y FASE-RELEASE de este plan
  **no** la reescribe.
- **Por qué se registra y no se calla**: sin esta fila, un lector de 2026-12 verá packs vacíos para
  los planes archivados y concluirá que el generador está roto. L-R.4: una regla de proceso sin
  verificador es publicable solo si la regla lo declara — y aquí lo declara el propio pack.
- **Alternativa descartada**: hacer que el generador adivine la lectura por heurística de rutas
  (`*.md` citados en el prompt). Convertiría `SECCION-NO-RESUELTA` en una invención silenciosa, que
  es la familia de defecto que L-PF6/L-PF10 trajeron a este plan.

### S17 — los writers de texto reescriben en CRLF archivos que git almacena en LF (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: la escritura final de `SyncEngine.sync_rule` en
`scripts/sync_versions.py` y la de `run_regenerate_domain_primer` en `scripts/doctor.py` cierran con
`write_text(..., encoding="utf-8")` **sin** `newline="\n"`. En Windows eso re-escribe en CRLF un
archivo que git almacena en `i/lf`. Medido en la corrida: **6** archivos quedaron
`[FAIL] Line endings` tras el sync y la regeneración (lo cortó el detector de finales de línea que el
bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` añadió a `validate_document_integration.py`), y
el expediente `FASE-RELEASE/12-normalizacion-lf.txt` registra la normalización byte a byte con
`git diff -U0` comprobando que el delta seguía siendo solo tokens de versión/fecha/codename. El
antecedente de la cura correcta vive en el propio repo: `scripts/log_phase_completion.py` pasa
`newline="\n"` y lo documenta junto a la escritura.

- **Dueño**: `scripts/sync_versions.py` y `scripts/doctor.py`. Es edición de `scripts/`, **no** de este
  plan ni de la orden: FASE-RELEASE tiene prohibido modificar código, y ese fue el motivo exacto por el
  que aquí se declaró el defecto en lugar de curarlo.
- **Disparador**: el próximo mandato que autorice literalmente editar esos dos writers. La cura es el
  parámetro en la escritura, no la normalización posterior del árbol.
- **Remedio vigente (provisional y declarado)**: normalizar por bytes al cerrar. No es la cura — deja el
  defecto en el escritor, que es la regla que este plan ya aplica a los datos: *un dato con escritor se
  arregla en el escritor o con un verificador, no con un tercero que lo reescriba a mano*.
- **Alternativa descartada**: fixedear los finales de línea en cada llamada desde los dos cierres del
  RELEASE sin tocar el writer (sería el mismo remiendo en dos sitios más) y reconfigurar `text`/`eol`
  de git: eso cambiaría el árbol de trabajo de archivos ajenos a este plan para tapar un defecto local.

**⟦CURADA el 2026-09-25 en una sesión aparte, con mandato de código del operador⟧.** El disparador de
arriba se cumplió ese mismo día: se autorizó editar `scripts/sync_versions.py` y `scripts/doctor.py` más
sus tests. Estado de la cura:

- **Tres escrituras**, no dos. Al curar apareció una tercera de la misma familia en el mismo archivo:
  `run_status` escribe `.agent/SYSTEM_STATUS.md`, y estaba dejando el árbol en `w/crlf` contra su propio
  `i/lf` (medido con `git ls-files --eol` antes de tocar nada). Las tres llevan ahora `newline="\n"`:
  `SyncEngine.sync_rule`, `run_regenerate_domain_primer` y `run_status`.
- **Prueba por comportamiento, no por parámetro**: `tests/test_sync_writers_lf_y_fecha_readme.py` corre
  los **escritores reales** sobre repositorios temporales y afirma sobre los bytes emitidos. Su control
  negativo ejecuta la versión **commiteada** de cada script (`git show HEAD:…`, sin `checkout` ni
  `stash`): el viejo escribe CRLF y el nuevo LF en el mismo entorno, así que la diferencia es
  atribuible al parámetro y no a la máquina.
- **Límite declarado**: la traducción `\n` → `\r\n` es propiedad del SO. La prueba **mide** si este SO
  traduce (`_traduce_a_crlf()`) y, donde no traduzca, las tres comprobaciones de bytes se saltan con
  motivo en vez de dar un verde que no observó nada. Las de S18 son portables.
- Con la cura hecha, el `--check` del sync volvió a `All files in sync` y la normalización manual por
  bytes del cierre de RELEASE (`12-normalizacion-lf.txt`) queda como antecedente: el próximo cierre no
  la necesita. No se re-escribió ese expediente cerrado (**S12**).

### S18 — `readme_version_header` no goberna la fecha legible de `README.md` (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: después del sync de cinco cabeceras, la línea de estado de
`README.md` seguía diciendo `Actualizado 11 Septiembre 2026` con `release_date: 2026-09-25` ya en la
fuente única. La regla `readme_version_header` de `scripts/sync_config.yaml` tiene patrón para el token
de versión pero no para esa etiqueta de fecha; la regla hermana `guia_tecnica_header` sí la goberna, y
`docs/GUIA_TECNICA.md` movió su fecha en la misma corrida.

- **Corte de cobertura declarado, no deducido**: el quick `[3/11] Version Sync` dio **PASS** con el
  README desfasado, así que la comprobación vigente no mira esa etiqueta. El rojo solo lo ve un lector
  humano — que es lo que lo encontró — y por eso se registra con deuda en vez de con un verde.
- **Dueño**: `scripts/sync_config.yaml` y el lector de esa regla en `scripts/sync_versions.py`.
- **Disparador**: el próximo mandato que autorice editar el config de sync o sus patrones de header; o
  la próxima release, si se quiere que la fecha del README salga por su escritor.
- **Alternativa descartada**: editar esa línea del README a mano. Crearía un segundo escritor sobre un
  dato que ya tiene uno — la familia exacta de la que `scripts/sync_config.yaml` retiró la regla
  `registry_last_update` el 2026-09-23.

**⟦CURADA el 2026-09-25, en la misma sesión que S17 y con el mismo mandato de código⟧.**

- El patrón llega ahora hasta la fecha (`… | Actualizado[^\n|]*`) y el template emite `{date_text}`, la
  forma larga que `_interpolate` ya sabía producir: «25 Septiembre 2026». **No** entra un ISO en la
  cabecera — hay prueba que lo prohíbe, porque cambiar el formato que el documento mostraba no era lo
  que pedía la deuda. `[^\n|]*` no cruza la línea ni el separador, así que no alcanza otras menciones
  de «Actualizado» (hay una línea de contexto con esa palabra como señuelo en la prueba).
- El corte de cobertura quedó cerrado en el árbol real, y se midió antes de celebrarlo: con la regla
  vigente, el `--check` del sync pasó de `IN_SYNC` a **`FAIL: README.md (readme_version_header) - needs
  update`** sobre el README que dejó la release. Ese rojo es la detección funcionando, no una regresión.
- Escribir `README.md` es destino central y no estaba en el mandato de código: se pidió y se autorizó
  aparte (`python scripts/sync_versions.py --rule readme_version_header`, 2026-09-25). Delta real: la
  **línea 5** (fecha). `git diff --numstat` contra `HEAD` marca 2/2 porque la cabecera de versión ya
  la movió la release; la separación se comprobó con `git diff -U0` y con huellas antes/después en
  `evidence/…/CIERRE-ORDEN-2026-09-25/07-guard-idempotencia-sync.txt`, donde una segunda corrida del
  mismo comando no mueve **ninguna** de las diez rutas vigiladas.
- El espejo de prueba allana **las dos** líneas que goberna la regla: con solo la cabecera allanada, el
  `FAIL` llegaba por la segunda sustitución y no por la fecha. Medido, y por eso está escrito.

> **Procedencia**: `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` · sha256 `a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723` · 13885 bytes copiados de 56768 del documento · HEAD `6b02532` · generado `2026-09-26T16:04:13Z`

---

<!-- BEGIN BRIEFING-META
{
  "generado_por": "scripts/build_phase_briefing.py",
  "plan": "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
  "fase": "C",
  "estado": "COMPLETO",
  "declaracion": "DECLARADA",
  "provenance": {
    "head": "6b02532",
    "generated_at": "2026-09-26T16:04:13Z"
  },
  "no_incluye": [
    "01-plan-maestro.md — 9879 bytes fuera de lo declarado (1, 4, 2)",
    "00-lecciones-capitalizadas.md — 10426 bytes fuera de lo declarado (1, 2, 3, 4)",
    "dependencias-fases.md — 42883 bytes fuera de lo declarado (Conciliacion)"
  ],
  "lectura_aparte_obligatoria": [
    ".agents/workflows/phased_project_executor.md"
  ],
  "sources": [
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md",
      "sha256": "1872761743009e43998c568717282545ac7a106cc86acfd1285078e995a0b3b7",
      "documento": "01-plan-maestro.md",
      "secciones": [
        "1",
        "4",
        "2"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md",
      "sha256": "c4d18dc91998a0086c93fef0182f8f82a48367b7afcd8aa799bed43577fe06e5",
      "documento": "04-contrato-ejecucion.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md",
      "sha256": "f6c1a005848008424dfe9128d48500a0fdff0fa5ba3a967c73b8b5c6eb0b8ec0",
      "documento": "00-lecciones-capitalizadas.md",
      "secciones": [
        "1",
        "2",
        "3",
        "4"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
      "sha256": "a38da8ea12a6a54ef5598925e54e6132881306439236419c6b597d2dd4696723",
      "documento": "dependencias-fases.md",
      "secciones": [
        "Conciliacion"
      ],
      "en_pack": true
    }
  ],
  "divisor_tokens": 4
}
END BRIEFING-META -->
