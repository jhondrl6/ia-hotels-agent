# Briefing pack — FASE-C

> **Artefacto generado. NO editar a mano.** Regenerar con:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
> La frescura la gobierna el sha256 de `sources[]` contra el arbol vigente:
> `python scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check`.

- **plan**: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`
- **fuente de lo declarado**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md` (bloque «Prompt de ejecucion»)
- **estado del pack**: `COMPLETO`
- **declaracion de lectura en el prompt**: `DECLARADA`
- **procedencia**: HEAD `8810936` · generado `2026-10-01T17:42:08Z`
- **tokens**: estimados por divisor 4, no recuento de tokenizer

## Lectura aparte obligatoria (el pack **no** la sustituye)

- `.agents/workflows/phased_project_executor.md` — 115175 bytes (~28793 tokens). se lee aparte mientras la deuda **D3** no rebane el workflow por fase; copiarlo aqui seria rebanar `.agents/` por la puerta de atras (AC17).

## Que **no** incluye este pack

- 01-plan-maestro.md — 10634 bytes fuera de lo declarado (1, 4, 2)
- 00-lecciones-capitalizadas.md — 10426 bytes fuera de lo declarado (1, 2, 3, 4)
- dependencias-fases.md — 58832 bytes fuera de lo declarado (Conciliacion)

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
C:/Users/Jhond/Github/iah-cli//.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
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


> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-C.md` · sha256 `dc323ec36ea30927d473f4d347e0bdd839843a8b1bb18652564f106a9077cc50` · 27581 bytes copiados de 27581 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

## Fuente: `01-plan-maestro.md` §1

## 1. Medición que justifica el plan (no suposición)

**Estado del bloque B: consultar §13 de la fuente única enlazada abajo.** Está concluido
contractualmente por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes — **el piloto FASE-C de
este plan no lo está y no se ejecutó**.
⟦Nota datada 2026-09-28 — esta frase seguía en presente sin nota en el párrafo, mientras su rectificación vive en otra fila del mismo plan: ver `dependencias-fases.md` bajo **Estado de B**, que abre con «Rectificado el 2026-09-24 al cerrar FASE-C» y declara el piloto **autorizado y ejecutado con mandato propio y corte «hasta listo para revisión»**. Medido hoy contra disco: `git ls-files evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` devuelve **23 rutas** (18 en la raíz, 1 en `instrumentos/` y 4 en `mutation/`; `find -type f` sobre el mismo directorio da el mismo **23**), y `git merge-base --is-ancestor 7f2e9f9 HEAD` y `git merge-base --is-ancestor 5817edd HEAD` dan **sí** los dos — `5817edd` es precisamente «feat(triage): FASE-C del verificador de contexto — capa de pertinencia aditiva» y `scripts/triage_lesson_relevance.py` está versionado (`git ls-files`). Crudo: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/02-f2-piloto-fase-c-vcf.txt`. Lo que de esta frase queda en pie: el **bloque C** de la orden de calidad sí fue solo documental⟧
Fuente única de resultados y estados D1/S13:
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

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1aa85df124196041da411719e03baba1b9526392ba171516404b8d4f4862930d` · 10344 bytes copiados de 55159 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

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
| AC16 | El quick sigue en 11 checks y el hook en 7, en **todo** el plan | los cuatro `baseline-pre-post.md`, delta 0 ⟦**Vencido como cifra, cumplido como delta (2026-09-26).** D2 se ejecutó por instrucción expresa y el quick son **12** checks; el modo completo, **16**. Las cuatro aserciones de este plan siguen siendo verdades sobre **sus** fases: ninguna alteró un conteo, y el delta 0 que miden A, B, C y D se midió contra 11 y contra 7, que era el árbol de aquel día. Lo que ya no vale es leer «11» como estado vigente: eso lo publica la corrida con `run_all_validations.py --quick` y lo audita `validate_governance_numbers.py`, que desde esa fecha corre dentro del propio quick. Evidencia: `evidence/…/CIERRE-ORDEN-2026-09-25/18-d2-quick-doce.txt`.⟧ |
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
  ⟦**La forma sobrevivió a la cifra (2026-09-26).** D2 promovió `validate_governance_numbers.py` al quick y
  lo renumeró: el quick son **12** checks y el completo **16**. AC5 sigue siendo cierta donde gobierna — las
  cuatro fases de este plan no alteraron ningún conteo y su resta se midió contra 11 y contra 7 — y su
  lección resultó ser justo la de L-D3: formulado el invariante como **delta** con par de artefactos, la
  reenumeración no invalida la verificación de la fase, solo el número que alguien leyera como vigente.⟧

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

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1aa85df124196041da411719e03baba1b9526392ba171516404b8d4f4862930d` · 26466 bytes copiados de 55159 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

## Fuente: `01-plan-maestro.md` §2

## 2. Matriz de decisión

| Decisión | Resuelto | Base |
|---|---|---|
| **¿Se toca `run_all_validations.py` o el hook para añadir checks?** | **NO.** Ninguna fase de este plan altera el número de checks | `REFACTOR-WHATSAPP` está en vuelo y pinea la cifra. **Sitios medidos el 2026-09-20** (no es el prompt de FASE-C, como decía la primera versión de esta fila): el bloque de arranque de FASE-B de su `README.md` («El quick son 11 checks.»), `06-checklist-implementacion.md` («el modo rápido pasó de 10 a **11 checks** y da 11/11»), `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`. Promover algo al set de 11 invalida la medición de fases ajenas. **⟦Re-medido el 2026-09-24 por el bloque C de la orden de calidad⟧**: el bloque de arranque de su `README.md` **ya no está en esa lista** —sus enmiendas lo sustituyeron por el comando que imprime la cifra—, y quienes la conservan (`06-`, `09-`, `10-`, su `dependencias-fases.md`, su prompt de FASE-G) son registros de fases cerradas. Eso **no debilita esta fila**: la razón de fondo sigue en pie, porque las mediciones ya publicadas son precisamente esas. Y **`run_all_validations.py` no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance (ver D10). Queda como deuda con disparador (§Deuda) ⟦**D2 ejecutada el 2026-09-26, y este «NO» era alcance de plan, no prohibición permanente.** Ninguna fase de *este* plan tocó el runner — sigue siendo cierto, y AC16 lo midió como delta. La renumeración la ordenó el operador desde fuera del plan, sobre la fila D2, que es justo el dueño que esta reserva dejaba señalado. Lo que queda vigente de esta fila es su segunda mitad: el runner **no está libre**, `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance (D10), y quien lo edite debe re-leer esa fila antes de tocar el `--upload`.⟧ |
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

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` · sha256 `1aa85df124196041da411719e03baba1b9526392ba171516404b8d4f4862930d` · 7715 bytes copiados de 55159 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

## Fuente: `04-contrato-ejecucion.md` (documento completo)

# Contrato de ejecución — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no reemplaza**
`.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. **El bloque C de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; el piloto FASE-C de este
plan sigue sin autorizar y no se ejecutó al redactarlas.**
⟦Nota datada 2026-09-28 — estado presente vencido, sin nota en el párrafo. La rectificación existe y vive en `dependencias-fases.md` bajo **Estado de B** («Rectificado el 2026-09-24 al cerrar FASE-C»: el piloto quedó **autorizado con mandato propio y corte «hasta listo para revisión»**, cerrado sin commit ni push). Medido hoy: `git ls-files evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` = **23 rutas** de evidencia de esa fase, y `git merge-base --is-ancestor 5817edd HEAD` = **sí** (el commit que trae las 37 rutas del piloto, `scripts/triage_lesson_relevance.py` incluido, también versionado). Crudo: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/02-f2-piloto-fase-c-vcf.txt`. La cláusula que esta fila gobierna sigue vigente y no cambia con la nota: **los permisos de este plan no amplían ese mandato** — el piloto lo tuvo propio, y quien lea esta fila para pedir permiso para otra fase debe pedir el suyo⟧
Los permisos de este plan no amplían ese
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
git mv /.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
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


> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md` · sha256 `39c8b094489b3703ddd707d37fcf24bc5e907eb1db7c742fcee788bad8fe974d` · 30204 bytes copiados de 30204 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

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

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `445c34c4c9a3863bd04077a2e2e1260718dcb5373f7f4fc35b7391662c638de1` · 12923 bytes copiados de 65400 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

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
| L-VCF-10 | Una prohibición de proceso escrita como afirmación del informe no era verificable, y en pytest `conftest` no es un importable único bajo colecciones anidadas | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | El «cero llamadas de red» dejó de ser una frase del informe y pasó a dos pruebas: que `socket.socket()` bajo el fixture levante `RedProhibida`, y que la costura llegue a `RESUELTO` **con el guard armado**; la denegatoria AST y el `find_spec` del venv van declarados aparte | AC6 · AC16 · AC17 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a)** |
| L-VCF-11 | Dos poblaciones con cifras cercanas no son la misma población: la resta entre ellas se desglosa o se publica como no desglosada | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | El cero de AC6 se sostuvo por medición y no por suposición, y la brecha entre `git ls-files` y el `rglob` del escáner se desglosó archivo por archivo; la mitad que no se arregló quedó registrada como deuda con dueño (S11) en vez de limarse | AC6 · AC16 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a)** |
| L-VCF-12 | Un verificador que además es writer gobierna dos artefactos: cada corrida sin destino re-escribe el registro fechado de otra sesión | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | Todo re-muestreo de `validate_governance_numbers.py` se hace con destino explícito y se declara. Su cura (imprimir y no escribir si no hay ruta) ya está puesta: S12 se aceptó y se corrigió con el bloque A de la orden de calidad | AC6 · AC16 · deuda **S12** · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a)** |
| L-VCF-13 | Un candado aditivo probado sobre el conjunto vacío es la variante silenciosa de un verde vacío: el `[]` no mentía sobre el presente, mentía sobre la cobertura de la prueba | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | El test de AC10 exige `filas_cuestionadas_sin_borrar` **no vacío** como condición de su propio verde, y el rojo de AC14 nombra lo que desaparece (`removed == cuestionadas`) para que el mutante sea atribuible y no un rojo cualquiera | AC10 · AC14 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a)** |
| L-VCF-14 | Parseable no es conforme: un lector que cae sobre un artefacto válido pero de forma equivocada tiene que publicarse como estado, no como traceback | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | A las tres causas del contrato se sumó la cuarta medida, con validación de forma **dentro** del lector (`LECTOR-FALLIDO` con su motivo) y una sub-causa aparte para «el cálculo propio no pudo correr», que no es `AUSENTE` ni `VENCIDO` | AC11 · AC12 · AC3 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a)** |
| L-VCF-15 | Verde en mi árbol no es verde en mi commit: `[6/7]` lee el árbol de trabajo, y un derivado que sella fechas por `mtime` no sobrevive a otro checkout | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | La autosuficiencia de un commit se verifica en el árbol del commit. Con la cura de S15 puesta, el instrumento que esta fila recetaba (`git archive`) ya no sirve para ese contrato y su sustituto medido es un **clon**, que sí trae historial | AC13 · AC16 · AC21 · deuda **S15** (curada el 2026-09-26) · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a extendida a 15…19)** |
| L-VCF-16 | Un mutante hay que anclarlo al texto que el generador **produce**, no al que el generador **traslada**: en un derivado de un corpus casi cualquier cadena pertenece al corpus | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | El ancla de AC23 se re-escribió con una marca exclusiva del generador más una cadena que no aparece en ninguna fuente, y su resumen publica los dos tamaños: el rojo es reproducible sin leer el test | AC22 · AC23 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a extendida a 15…19)** |
| L-VCF-17 | Un artefacto derivado no es neutro respecto al directorio donde cae: pasa a ser corpus para todo verificador que lo recorra por patrón de ruta | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | Regla escrita en el generador a partir de la medición: toda fuente declarada **fuera** de `.opencode/` sale como `lectura_aparte` con su ruta y su motivo, y no se copia; y el par del índice se regenera **después** de los packs | AC18 · AC19 · AC22 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a extendida a 15…19)** |
| L-VCF-18 | Una cifra transcrita de memoria entra al documento con la misma apariencia que una medida: la resta era aritméticamente impecable sobre un minuendo que nadie midió | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | Ningún PRE entra en un documento de cierre sin su archivo de crudo; si no lo hubo se llama **reconstruido** y se dice con qué se contrasta. El par refutado se retiró y se re-publicó con su comando y sus cuatro variantes impresas | AC5 · AC16 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a extendida a 15…19)** |
| L-VCF-19 | La métrica de un derivado no cabe en el documento que ese derivado copia: el instrumento recorre el `.md` donde se transcribe su propia cifra | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | Ninguna cifra de carga o de tamaño de pack entra en un documento que el generador copia: se publican el comando, el artefacto y la identidad comprobada, y en el documento queda el orden de magnitud con su porqué | AC20 · AC21 · AC23 · **capitalizada el 2026-09-27 por decisión escrita del operador (D-d, opción a extendida a 15…19)** |

| L-VCF-20 | «No es fuente con sha» no es «no es fuente»: la proyección de una ruta —sus bytes y sus tokens impresos dentro del derivado— la gobierna igual que un hash | `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` | El agrupamiento de commits que se creyó inocuo no lo era: la línea de carga del pack imprime el tamaño del workflow, así que commitear corpus y packs antes que el workflow deja el árbol de ese commit sin reproducirse (rojo 12/13 con cinco `DIVERGE` cayendo los cinco en la misma línea) y el commit siguiente lo restaura. Regla operativa: al separar commits, leer lo que el generador **emite** de cada ruta y no solo su `sources[]`. Las cifras medidas no se copian aquí (**L-VCF-19**): las imprime la línea de carga del pack regenerado, y el hecho quedó en los mensajes de `f496914` y `5446cb7` | AC20 · AC21 · **capitalizada el 2026-09-27 por instrucción escrita del operador (tanda H1, sesión de commits de cierre)** |

**Cómo entraron estas diez (registro de la decisión, 2026-09-27).** Hasta aquí §2 era estrictamente **herencia**: filas copiadas de planes anteriores. Las diez de arriba son de **este** plan, y entran por instrucción escrita del operador — «Ejecuta: D-d (a) + incluir 15-19 en la misma decisión» —, que resuelve en **aceptar** el dosier de `L-VCF-10…14` (el piloto las dejó pendientes con dueño, contrato **E3**) y amplía la misma decisión a `L-VCF-15…19`, que **nunca fueron candidatas**: el pool del informe se congeló en la corrida del piloto y no incluye nada por encima de 14. Consecuencia que hay que saber leer: **el juicio que las avala es humano, no del instrumento**. `coverage.json` sigue publicando `acceptance = NO-EJERCITADO` con `valor: null` mientras **D7** esté inactiva, así que ninguna de estas diez filas puede citarse como «la pertinencia la midió el triaje». Lo que sí se cumplió al escribirlas es la condición que el propio archivo pedía para entrar: un «qué cambia» real que nombra un AC de este plan, la revisión registrada con quién decidió, y el ID definido en el corpus con su dueño (verificado contra el lector: `duenos_del_corpus()` publica `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` para las diez, y **C7** casa por subcadena). La auto-capitalización **no** aporta diversidad de fuentes en el sentido que **C8** busca — pasa de **6** a **7** dueños porque el séptimo es este plan, no un corpus nuevo, re-medido el 2026-09-27 — y esa diferencia se declara en vez de contarla como mérito.

Dueños distintos representados: **7** — TRIBUNAL-OFFLINE, REFACTOR-COHERENCIA-NARRATIVA, SR-PIPELINE-FIXES, ESTABILIZACION-PRE-TRIBUNAL, PASO0-VERIFICADOR-CAPITALIZACION, VALIDADOR-URL-PROPIA y **este propio plan** (las diez filas nuevas, re-measured 2026-09-27). Satisface C8 (≥2) con holgura y no repite solo al predecesor. **Doble corrección del 2026-09-20**: la fila decía **7** cuando las once originales ya tenían **6** dueños nombrables (L-R.3 aplicado a este propio archivo: el conteo se re-mide, no se copia), y las tres lecciones nuevas de la capa tibia **no suman dueño** — `D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, no en `TRIBUNAL-ENFORCEMENT-OBS`, que es donde la **reproducen** cuatro fases seguidas. Lo detectó `validate_lesson_capitalization.py` con su checks `C7` (atribución contra el índice), no una lectura humana: es el verificador de forma de este mismo plan funcionando sobre su propio `00-`.

**Cómo entró L-VCF-20 (registro de la decisión, 2026-09-27, tanda H1).** Los dos párrafos de arriba registran el ingreso de **diez** filas por la decisión D-d y no se reescriben: siguen siendo exactos para esas diez. Con esta son **once** las filas de §2 debidas a este propio plan, y su procedencia es otra — instrucción escrita «Haz H1 y H2» sobre una lección que la sesión de commits **midió al commitear**, ya cerrado el dosier que avaló a las otras diez. El dueño no cambia, y el conteo se re-midió contra el lector en vez de copiar el párrafo anterior: `duenos_del_corpus()` sigue publicando **7** dueños distintos, porque una fila más de este plan no suma un octavo — el mismo motivo por el que las tres de la capa tibia no sumaron. Y una forma que hay que respetar para que el índice la reconozca: la **definición** va en `10-analisis-post-implementacion.md` §Lecciones nuevas, porque el corpus de definiciones del generador son los análisis (`09`/`10`), no este `.md`; escribirla solo aquí la habría registrado como ID citado sin definición, que es la familia de cita fantasma que este plan ya pagó.

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `445c34c4c9a3863bd04077a2e2e1260718dcb5373f7f4fc35b7391662c638de1` · 24489 bytes copiados de 65400 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

## Fuente: `00-lecciones-capitalizadas.md` §3

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-A6, L-V4, L-H4 | Son la familia «la cita de línea cadura». Este plan no introduce citas de línea en ACs ni prompts y **no reescribe** las ajenas: `validate_plan_citations.py` ya las gobierna con alcance hacia delante + delta, y su política está recogida como restricción en `04-contrato-ejecucion.md`, no como trabajo nuevo |
| DA-HF3 | Misma política de alcance (hacia delante + delta, reporta sin reescribir). Ya está implementada en el verificador de citas; este plan la **hereda** como diseño de AC16, no la reconstruye |
| L-SR3, L-SR5 | Fuente única de verdad del estado de un servicio y gate bloqueante que no solo loggea: son del dominio de producto (promesas/métricas del pipeline v4). Ninguna fase de este plan toca el pipeline ni sus gates |
| L-VUP-1 | La baseline «13 rojos» que midió 14 por un test orden-dependiente del audit: este plan no ejecuta el audit ni hereda esa selección de tests |
| **D5** (no es ID: medición propia) | `grep -icE "verificador mec"` devolvió **0** sobre el índice, y sí existen verificadores nombrados en el corpus. Un cero de grep **no distingue** «no existe» de «busqué la palabra equivocada» — es la variante léxica de L-PF6. Se descarta el grep como única puerta de pertinencia y se registra como la evidencia que justifica FASE-C (AC15 obliga a publicar la población y el término usado) |

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `445c34c4c9a3863bd04077a2e2e1260718dcb5373f7f4fc35b7391662c638de1` · 1492 bytes copiados de 65400 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

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
- **Al cerrar la orden, el 2026-09-27, §2 pasa de catorce a veinticuatro filas** por decisión escrita del
  operador sobre la deuda **D-d** («Ejecuta: D-d (a) + incluir 15-19 en la misma decisión»): entran
  `L-VCF-10…14`, las cinco que el piloto dejó pendientes con su dueño, y entran con ellas
  `L-VCF-15…19`, que no estaban en el `informe.json` porque su pool se congeló en `da382b1` antes de que
  existieran. Medido con el lector del propio verificador (`duenos_del_corpus()`, importado): **24** filas,
  **7** dueños, y las diez nuevas con dueño `Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`, que es como
  las publica el índice. Los límites que esta entrada **no** disfraza: el juicio sigue siendo humano —
  `coverage.json` mantiene `acceptance = NO-EJERCITADO` mientras **D7** esté inactiva — y la
  auto-capitalización no suma diversidad de corpus en el sentido que **C8** persigue, solo documenta que
  las diez lecciones propias de este plan quedaron revisadas y aceptadas por su dueño. La regla de forma
  que sí se verificó es **C7** (cada ID definido en el corpus y su dueño real aparece en «Definida en»),
  corrida contra este mismo archivo.
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
  que tenía al cerrar FASE-B**, y esa invariancia es AC10, no olvido. ⟦**Vencida esa invariancia el
  2026-09-27, y por decisión escrita del operador, no por olvido ni por cuota**: §2 pasó de catorce a
  **24** filas al entrar `L-VCF-10…19`. Lo que AC10 prohibía —que el triaje **borre** una fila anclada—
  no ocurrió y sigue prohibido: ninguna de las catorce se movió, la cuenta sube de a diez⟧ Por qué cero aplicadas: una
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
  catorce filas (**AC10**). ⟦**DECIDIDA el 2026-09-27 por el dueño, que es el operador, con la letra que
  este casillero pedía**: «Ejecuta: D-d (a) + incluir 15-19 en la misma decisión». **A** = aceptar las
  cinco, y la misma decisión amplía el lote a `L-VCF-15…19`, que no estaban en el informe porque su pool
  se congeló en `da382b1` antes de que existieran. Las diez entraron a §2 con su «qué cambia» nombrando AC
  de este plan y con la revisión registrada aquí, con quién decidió y con fecha. Lo que esta decisión
  **no** compra: el juicio del instrumento sigue `NO-EJERCITADO` mientras **D7** esté inactiva, así que
  estas filas valen como criterio humano fechado y no como pertinencia medida⟧ Lo que cada una necesita para entrar: un «qué cambia» real que nombre un AC de
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
  contrato **E3**), y **no** se capitalizó por cuota. ⟦**Vencido ese «siguen pendientes» el 2026-09-27 por
  instrucción escrita del operador**: las cinco se **aceptaron** y la misma decisión sumó a
  `L-VCF-15…19`, que nunca fueron candidatas del informe; §2 cierra en **24** filas. La frase de arriba se
  conserva literal porque describe el cierre de FASE-RELEASE, y capitalizar por cuota sigue sin hacerse:
  las diez entraron por criterio humano fechado, no para rellenar un número⟧ Lo que se re-fechó es la limitación de Q7/D8 (arriba)
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

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` · sha256 `445c34c4c9a3863bd04077a2e2e1260718dcb5373f7f4fc35b7391662c638de1` · 16070 bytes copiados de 65400 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

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
- ⟦**CURADA el 2026-09-27 por la familia D-b de la orden de calidad, con instrucción literal del operador
  sobre configuración central**: la forma canónica de la lista de lectura está escrita desde hoy en el dueño
  que esta fila le asignaba — `prompt-fase-template.md` §8 (template v1.7.0), con sus cinco reglas leídas del
  parseador y no de la memoria — y su regla hermana («tocar un generador obliga a regenerar sus derivados y
  commitearlos juntos», que es §S19) en el checklist post-fase del executor (v2.26.0). **La población de esta
  fila quedó vencida por el traslado y se re-mide, no se recalcula a ojo**: hoy hay **126** prompts de fase
  bajo `Archives/` y **5** declaran la lectura en la forma que el generador resuelve — los cinco de este
  plan, que ya están archivados, de modo que «0 de 121 archivados la usan» se lee al revés que cuando se
  escribió. Los que siguen sin declarar son **121** prompts ajenos, y no se reescriben: así lo decidió su
  FASE-RELEASE y sigue siendo corte del generador, no deuda. Medido con el lector real
  (`parsear_lista_lectura` del propio generador, importado) y no con una imitación del regex, en el
  instrumento `…/CIERRE-ORDEN-2026-09-25/GRUPO-B-P0-CONVENCION-2026-09-27/10-poblacion-s16-dos-criterios.py`.
  Un caso sirve de advertencia para quien vuelva a contar esto con `grep`: el único prompt ajeno que tiene
  una línea que arranca en `Lee ` es un `> Lee antes …` en la prosa de su encabezado, que el parseador no
  toma ni debe tomar — cuenta prompts con la línea, que no es la misma población que prompts resueltos⟧

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

**⟦Cuarta instancia de la misma familia, medida el 2026-09-27 al ejecutar D-c — NO curada, sigue abierta
bajo el dueño de esta fila⟧.** `scripts/validate_opencode_refs.py --fix` es un writer de texto sin
`newline="\n"`, y esta vez el daño lo hizo sobre **gobernado del propio plan**: tras el `git mv`, su corrida
re-escribió **13 archivos que HEAD almacena en LF** dejándolos en CRLF sobre el disco — `CR_disco`: 87 en
`plan_citations_baseline.json`, 636 en la orden de calidad, 194 a 383 en los seis prompts, y **1.551 a 3.645
en los cinco packs**. `git status` no lo distingue (guarda LF de todos modos), así que lo que se pierde no es
un rojo sino el **numstat**: sin normalizar, el commit del archivado habría aparecido como reescritura
completa de 13 archivos en vez de los 1–34 líneas por archivo que realmente cambió. Se normalizó por bytes
antes de commitear y el diff quedó simétrico (`17/17`, `34/34`, `3/3`), que es la firma de una reescritura de
rutas pura. **El detector no es un humano acordándose**: `tests/test_sync_writers_lf_y_fecha_readme.py` cubre
los tres escritores de la cura anterior y **no** a este, así que la familia volvió a colarse por la cuarta
puerta. La cura pedida es la misma de siempre (`newline="\n"`) más una aserción en esa batería que lo incluya.

Y un defecto segundo del mismo `--fix`, menor pero del mismo estilo de silencio: al reparar, **promueve la
forma minoritaria** de la ruta. Escribió `` `.opencode/plans/Archives/… `` en tres referencias de
`ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` que estaban en `` `.opencode/… ``, cuando el corpus marcado
versionado está en **518 contra 66** a favor de la forma sin barra (medido con `git grep -c` sobre `HEAD`,
contando el backtick como parte del patrón).
⟦Nota datada 2026-09-28 — **el par 518/66 no es reproducible con ninguna ancla, con ningún instrumento y ni siquiera en la revisión que lo escribió**, así que se declara aquí con las medidas que sí lo son, cada una con su población y su instrumento. Todo medido sobre el árbol limpio de `84c1aca` (`git status --porcelain -uno` = **0** líneas). **(i) Con el ancla de esta fila**, el literal `` `.opencode/plans/Archives `` sobre el corpus marcado versionado (**700** `.md` de `git ls-files`): **167 contra 29** ocurrencias, o **166 contra 29** líneas con el instrumento que esta fila nombra (`git grep -c -F` sobre `HEAD`). **(ii) Con ancla ancha**, el literal `` `.opencode `` sobre el mismo corpus: **604 contra 73** ocurrencias, **564 contra 73** líneas. **(iii) Con la población ampliada** a todos los ficheros versionados (**2.852**, no solo Markdown): **174 contra 32** con el ancla de la fila y **786 contra 77** con la ancha; sumando los ficheros **sin versionar** del árbol, **180 contra 36** y **799 contra 85**. Ninguna de esas combinaciones da 518/66, y la revisión que firmó esta cifra tampoco: `git log -S '518 contra 66' --oneline -- .opencode/plans` la pone en `3c2e6a3`, y medida **allí** con el instrumento de la fila da **147 contra 28** (ancla de la fila) y **524 contra 72** (ancha). **518 contra 66 queda como antecedente refutado.** Lo que la medición no tumba es la conclusión de la fila: la forma sin barra gana **5,8 a 1** con el ancla de esta fila y **8,3 a 1** con la ancha, así que «el `--fix` promueve la minoritaria» sigue en pie con su dueño. Crudos: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/05-f4-par-de-formas-s17.txt`, su gemelo por ocurrencias `06-f4-par-de-formas.txt`, el contraste de instrumentos `07-f4-divergencia-gitgrep-head-vs-disco.txt` y la tabla de los tres alcances `17-f4-tres-alcances.txt`. **Nota de instrumento**, para no volver a pagar el error de la quinta instancia: `git grep -c` cuenta **líneas**, no ocurrencias, y `git grep -F` con patrón que empieza por `/` sigue dando **0 falso** (medido hoy: `git grep -c -F` sobre el patrón `/.opencode/plans/Archives` = **0** líneas)⟧
El verificador acepta las dos, así que **no corta nada**: se
convirtió en una incoherencia de estilo dentro de un documento que usaba una sola forma. Se reescribieron a
mano las tres a la forma dominante —no hay pelea con la herramienta, porque `--fix` solo toca referencias
rotas— y quedó declarado aquí en vez de abrir un número nuevo: **S21 a S26 están todos usados en el corpus**
(el `S22` y `S23` de `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` son otra cosa), así que esta
observación vive como sub-punto de S17 y no como fila propia.

**⟦Quinta instancia de la misma puerta, medida el 2026-09-27 al ejecutar el archivado de JEV (paso T3 de la orden
de cierre) — el defecto sigue abierto bajo el dueño de esta fila⟧.** `validate_opencode_refs.py --fix` volvió a
escribir sin `newline="\n"`: **9** archivos del corpus pasaron a CRLF sobre disco (de 87 a 3.978 CR por archivo;
detalle y guarda de bytes en `evidence/…/CIERRE-ORDEN-2026-09-25/T3-ARCHIVADO-JEV-2026-09-27/`). Se normalizó por
bytes con las dos aserciones de rigor y los cinco packs se regeneraron con su escritor, que sí emite LF: el daño
es del `--fix`, no del generador de packs. Y promovió otra vez la forma minoritaria: **4** referencias quedaron
como `` `/.opencode/plans/Archives/… `` en `ORDEN-…md`, `CONTEXT-JEV-…md` y esta misma fila, y se devolvieron a la
forma dominante a mano, con el mismo criterio que la cuarta instancia. Dos precisiones medidas esta vez, para no
repetir el error de instrumeto de la anterior: (i) el recuento de formas **no** se puede hacer con
`git grep -F "/.opencode/plans/Archives"` —devuelve **0** incluso sobre archivos que el `grep` plano muestra
llenos de esa cadena—, hay que contar con `grep -o -F` sobre la ruta; y (ii) la promoción no es universal: en
`Archives/EVALUACION-JEV-…/README.md` y en los cinco packs quedaron ocurrencias con otro carácter delante, que
no son del `--fix` y **no se tocaron** (son contenido archivado y derivado, y la cura pedida sigue siendo la del
`newline="\n"` en el escritor, no reescribir corpus ajeno).

**⟦SEXTA INSTANCIA Y CIERRE POR EJECUCIÓN — medida y curada el 2026-09-27 en la sesión de curas fuera de
plans, con mandato literal del operador sobre `scripts/validate_opencode_refs.py`⟧.** Las dos escrituras del
guion llevan ahora `newline="\n"`: la del `--fix` sobre cada Markdown que repara y la de `--write-baseline`
sobre `.opencode/refs_baseline.txt`. La fila pedía «la misma cura de siempre más una aserción en esa
batería que lo incluya», y esa batería es `tests/test_sync_writers_lf_y_fecha_readme.py`, que pasó de **7**
a **10** pruebas corriendo el guion **real** sobre un espejo temporal (el `PROJECT_ROOT` del escritor sale de
su propio `__file__`, así que el espejo se arma copiando el guion a `espejo/scripts/` y el Markdown se planta
por bytes, porque re-escribirlo con `write_text` lo pasaría a CRLF por la misma traducción que se mide):

- **Tres controles nuevos, cada uno por su puerta**: `test_el_fix_de_refs_emite_lf_y_el_commiteado_escribe_crlf`
  (el Markdown reparado), `test_la_baseline_de_refs_emite_lf_y_la_commiteada_escribe_crlf` (el baseline — es la
  escritura que dejó los 87 CR de la cuarta instancia) y `test_el_guion_de_refs_no_toca_el_arbol_del_proyecto`
  (guard de destino **por operaciones observadas**, no por estado final: S13, y con ancla positiva de que el
  escritor sí escribe en el espejo).
- **Control negativo contra la versión commiteada**, leída con `git show` y ejecutada en scratch, sin
  `checkout` ni `stash`. Va anclada a `REV_CONTROL_DEFECTUOSO` (`5817edd`), **no** a `HEAD`: esta misma cura
  entra en el commit y desde ese árbol el control se quedaría sin rojo con el que compararse — la lección ya
  está escrita arriba, medida en `bdd1c4c`. Verificado con `git show 5817edd:scripts/validate_opencode_refs.py`:
  sus dos escrituras siguen sin el parámetro.
- **Dientes medidos por mutación (R2.8)**: quitado el parámetro en las dos escrituras, caen **exactamente**
  las dos pruebas nuevas del guion (`2 failed, 8 passed` — las de sync/doctor/S18 siguen verdes, así que el rojo
  es atribuible al parámetro y no al entorno), y restaurado el archivo el `sha256` sale idéntico
  (`f68dcfe1…`) con la batería en **10 passed**. Crudos: `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T2-S17-QUINTO-ESCRITOR/`.
- **Un defecto del instrumento propio, declarado**: el conteo de las escrituras no se podía hacer con
  `grep -c ', newline="\n")'` sobre el archivo mutado —el escape del patrón devuelve **0** y el mutante abortaba
  por ese falso cero—; hay que contar con `grep -o -F 'newline="\n"'`, que da **3** (dos escrituras y el
  comentario que las documenta).
- **Lo que NO cierra esta cura**: el segundo defecto del mismo `--fix` (promueve la forma minoritaria de la
  ruta) sigue sin cura, bajo el dueño de esta fila, con su medida de formas en la cuarta y quinta instancia.
  Y el residuo que el guion ya dejó en disco **no se normaliza aquí**: medido con
  `git ls-files --eol .opencode | awk '$1=="i/lf" && $2=="w/crlf"' | wc -l` salen **213** archivos (176 `md`,
  34 `json`, 1 `txt`), todos de planes archivados ajenos a esta sesión y todos invisibles a `git status` porque
  `core.autocrlf=input` normaliza al commitear. Normalizarlos es una reescritura masiva de corpus ajeno; queda
  declarado con su reparto en `…/T2-S17-QUINTO-ESCRITOR/23-residuo-crlf-opencode.txt`.

**Estado de la fila: CERRADA por ejecución el 2026-09-27** en su defecto de finales de línea (cinco puertas:
`sync_rule`, `run_regenerate_domain_primer`, `run_status`, y las dos de `validate_opencode_refs.py`), con el
sub-punto de la forma minoritaria de la ruta **abierto** bajo este mismo dueño.

⟦**Sello 2026-09-28 — C4 de la orden de curas en `scripts/` (sesión 2): el sub-punto de la forma minoritaria
queda CURADO, y con él la fila queda sin partes abiertas.** Las dos promociones de `fix_broken` en
`scripts/validate_opencode_refs.py` dejan de anteposer «/» a la ruta promovida: la del `archived_promotion` y
la del candidato único. `ref_target` no se toca y sigue aceptando las dos formas (`lstrip("/")`), así que la
cura cambia **lo que se escribe**, no **lo que se resuelve** — medida en el mismo espejo: `ref_target` de la
ruta con y sin barra dan el mismo `Path` que existe, y la ruta citada sigue estando rota antes del `--fix`,
que es lo que da oportunidad de promocionar.

Dientes medidos con el escritor **viejo** anclado a una revisión publicada fija, no a HEAD: la batería
`tests/test_sync_writers_lf_y_fecha_readme.py` corrió el guion vigente y el de `5817edd` sobre el mismo
plantado, y el control sigue promocionando la forma con barra mientras el vigente escribe la del corpus. La
batería pasó de **10** a **14** pruebas con las cuatro de este sub-punto (forma mayoritaria, idempotencia de
la segunda corrida, el control anclado y la aceptación de las dos formas), y el mutante **R2.8** —quitar
`newline="\n"` de las dos escrituras del guion— sigue tirando **exactamente** las dos pruebas de finales de
línea de ese guion (`2 failed, 12 passed`), no las cuatro nuevas: el rojo sigue siendo atribuible al parámetro
y no a la forma. Crudos: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/07-c4-bateria.txt`,
`08-c4-mutante-r28.txt`, `09-c4-espejo-forma.txt`.

Sobre el baseline: `validate_opencode_refs.py` deja **1** entrada congelada en `.opencode/refs_baseline.txt`
y **0** con forma de barra inicial — el conteo se lee con `grep -c -v '^#' .opencode/refs_baseline.txt` y el
de formas con `grep -o -F '|/' .opencode/refs_baseline.txt`, medidos en `10-c4-baseline-refs.txt`. El cambio de
forma **no mueve entradas**, porque `validate` guarda la referencia extraída (`REF_RE` arranca en `.opencode`,
la barra nunca entró en la clave). Y sobre el árbol real el guion en modo lectura sigue dando `[PASS]` con
**exit 0**: no hay referencias que re-promover.

Lo que el sub-punto **no** toca, declarado en la fila y re-confirmado hoy: las ocurrencias con barra que
quedan en corpus archivado (`Archives/DT4-RESIDUAL-FIXES`, `ASSET-ALIGNMENT-ZIONE-2026-07-23`,
`DELIVERY-ZIP-SINGLE-WRITE-2026-08-01` y el `README.md` de JEV) son contenido archivado y derivado, no obra del
`--fix`; reescribirlas sería la reescritura masiva de corpus ajeno que la sexta instancia rechazó. La medida de
formas de la cuarta instancia sigue valiendo tal como quedó rectificada el 2026-09-28: 518/66 **refutado**, y
la forma sin barra gana **5,8 a 1** con el ancla de la fila. **Estado de la fila: CERRADA por ejecución en sus
dos defectos (finales de línea y forma promovida), sin partes abiertas.**⟧

⟦**Sello 2026-09-28 — C7 y C5 de la misma orden (sesión 2): la séptima puerta de la familia y el residuo que
esta fila heredó.** Nota de procedencia para quien lea el índice: **D-H** y **D-C** son deudas definidas en el
expediente `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md`
(§5 y §9), fuera del corpus que recorre `build_lesson_index.py`; al nombrarlas aquí desde una fuente gobernada,
el índice las proyecta a los cinco packs y las publica como «citadas sin definición» (**52 → 54**, seis
menciones cada una). Eso es disclosure del instrumento, no un rojo: no se borra la referencia para achicar la
lista, se deja con su procedencia escrita. **C7 / D-H**: la escritura de `escribir_baseline` en `scripts/validate_plan_citations.py`
lleva ahora `newline="\n"`. Medido con el propio guion sobre una **ruta externa** (la orden prohíbe probar el
escritor contra el baseline real, y el guard `test_probar_el_escritor_no_toca_el_baseline_real` lo sostiene por
huella del archivo versionado): el escritor vigente emite **CR=0, LF=87** y el de `REV_INICIO` (`84c1aca`,
anclada y no HEAD, verificada con `git show` y ejecutada en scratch) emite **CR=87, LF=87, CRLF=87** sobre la
misma copia; idénticos salvo CR y la marca `created_at`. Es el **sexto** miembro de la serie (`sync_rule`,
`run_regenerate_domain_primer`, `run_status`, las dos de `validate_opencode_refs.py`, esta). Crudos:
`22-c7-pytest.txt`, `23-c7-escritor-baseline.txt`.

**C5 / D-C**: el residuo que la sexta instancia dejó declarado —**213** archivos bajo `.opencode` en `i/lf`
contra `w/crlf`— quedó normalizado por **escritor**, no por mano. La población se calculó con el comando
canónico de la casa y se re-midió hoy: **213**, sin deriva contra la cifra de la orden, reparto **178 `md` + 34
`json` + 1 `txt`** leído con `-z` y `core.quotePath=false` (las dos rutas `md"` del crudo 28- son los nombres
con escapes octales, que con esa lectura dejan de estar entrecomillados y el mismo conteo sale **213** por las
dos vías). El escritor **no normaliza nada que no case con su blob**: identidad `POST == git cat-file blob
HEAD:<ruta>` exigida antes de escribir y re-verificada después sobre las **213** rutas (**213 iguales, 0
distintos, 0 sin blob**), no sobre la muestra de tres que citaba la orden. POST con el mismo comando del PRE:
**0**. Mutante del criterio 5: una ruta fuera de la población se rechaza con exit propio (**4**) y el fixture
quedó intacto en CRLF.

Lo que la normalización reveló y se declara, no se esconde: al escribir las 213 rutas, `git status
--porcelain -uno` saltó de **18** a **231** líneas mientras `git diff --name-only` seguía dando **18** y el
`numstat` de esas rutas estaba **vacío**. Es cache de stat del índice, no contenido: con `core.autocrlf` del
ámbito de sistema en `true` y del repositorio en `input`, la vía «segura» de `git update-index --refresh`
rechaza el round-trip y avisa `needs update`; `--really-refresh` sobre las **213 rutas del informe del
escritor** (no sobre el resto del árbol) las sacó de `git status` y devolvió la población a **18** líneas.
`git diff --cached` sigue en **0**: el refresco tocó stat, no stapeó contenido. Crudos: `24-c5-pre-poblacion.txt`,
`26-c5-fix-y-post.txt`, `27-c5-post-y-refresco.txt`, `28-c5-identidad-post.txt`, `29-c5-cierre.txt`. Instrumentos
cazados mientras se medía, por la misma familia de siempre: `git ls-files --eol -z` parte la cabecera
`i/lf  w/crlf  attr/` como **un** campo separado por espacios (comparar `cols[0] == "i/lf"` sobre la cabecera
entera devolvía **0** rutas), y una ruta con escapes octales no resuelve en disco tal como la imprime el
`ls-files` con quoting por defecto (**OSError 22**). Ninguna de las dos es un rojo del árbol: son dos rojos del
instrumento.⟧

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

### S19 — la frescura de un pack no incluye al generador que lo imprime (nueva, 2026-09-26) — **CERRADA el 2026-09-27 en su parte gobernable; sobrevive solo por (c)** ⟦la (c) se cumplió el mismo 2026-09-27 con la instrucción literal de la familia D-b: la convención quedó escrita en `.agents/`; la fila baja declara lo que de (c) sigue siendo verdad estructural y qué queda aparte, en la (d)⟧

**Medido, no inferido.** Al ejecutar D2 cambié un literal dentro de `scripts/build_phase_briefing.py`
(`[8/11]` → `[8/12]`, en un comentario y en el mensaje que el propio script copia dentro de los packs).
Después de ese cambio, `build_phase_briefing.py --check` dio **`EXIT=0`** con la nota «FASE-C/D/RELEASE:
fuentes frescas *(procedencia distinta, no vence)*» y, sin embargo, regenerar **modificó los cinco packs**
(`10/10, 9/9, 13/13, 9/9, 18/18`). La causa está en el código, no en una corrida afortunada: la frescura la
gobierna el `sha256` de `sources[]` contra el árbol vigente — línea 688: «Frescura por sha de las fuentes
gobernadas. HEAD solo informa procedencia (AC21)» — y **el escritor no está entre sus propias fuentes**.

**Por qué importa.** Un derivado commiteado puede quedar con texto viejo mientras su verificador dice verde,
y el único que lo pone al día es quien editó el generador *acordándose*. Hoy me acordé y regeneré; el día que
no, el `--quick` pasa, el hook pasa, los 7/7 pasan, y el pack publicado miente sobre qué lo generó. Ninguna
batería lo cubre: no hay test que compare el literal del writer con el contenido del pack.

**Cure posible, y por qué no la aplico en esta sesión.** (a) Meter el sha del writer en la llave de frescura:
detecta el caso, pero re-vence **todos los packs en cada edición del script**, que es exactamente lo que AC21
evitó al sacar `head` de la llave. (b) Un gate que regenere en un scratch y compare contra el árbol — no
cambia la llave, cuesta una corrida y hace falta un verificador nuevo con su propia batería. (c) Convención, la que
se usó hoy: quien edita un generador regenera los derivados y los comitea en el mismo commit. Se registra con
dueño **decisión del operador** (ninguna de las tres es un cambio menor) y su disparador es la próxima edición
de un escritor que emita texto versionado. **No se número antes de esta fila: `S19` estaba libre, medido con
`grep -rn "S19" .opencode/` sobre el corpus activo.**

⟦**Decidida el 2026-09-26 sobre el árbol, sin esperar al disparador, y con los dos riesgos medidos.** La
evidencia completa está en `evidence/…/CIERRE-ORDEN-2026-09-25/19-s19-medicion-de-los-dos-riesgos.txt`; aquí va
el resultado, que reescribe el coste de cada cura. **(a) descartada con medición en contra, no solo con el
argumento AC21:** dos regeneraciones consecutivas sin ningún cambio entre ellas divergen en 16 a 32 líneas por
pack, todas el sello `generado` — gobernar al escritor fabricaría un rojo obligatorio de información nula en
cada edición del script. **(b) viable, y más barata de lo que esta fila suponía:** el destino alterno **ya
existe** (`--briefing-dir`, líneas 1002-1003 del propio script), así que no hay que editar al paciente para
operarlo; y el diff es determinista bajo una sola normalización — **53 líneas llevan el sello UTC en todo el
conjunto de packs, y ese conteo no se mueve entre corridas ni entre ediciones de corpus** (el denominador sí:
9.481 al medir por primera vez, 9.621 después de escribir esta misma anotación, o sea el ratio que ahí aparece
es un derivado condenado y no es la cifra que hay que gobernar). Al normalizar esas 53, los cinco packs quedan
idénticos entre corridas **y** idénticos al versionado. Lo que
viaja de esa verificación es el comando, no la cifra: `sed -E 's/· generado .[0-9TZ:.+-]+.//g;
s/"generated_at": "[0-9TZ:.+-]+"/"generated_at": "N"/g' <pack> | sha256sum` sobre los cinco packs, corrido dos
veces sin cambios entre ellas, da el mismo digest por pack. Los cinco valores que publiqué en el primer borrador
de esta anotación (`53f0d4f5a4a2` y compañía) **quedaron refutados por mi propia cola canónica** unos minutos
después de escribirlos: anotar esta fila es editar una fuente gobernada, y eso mueve el contenido de los cinco
packs. Queda como antecedente fechado el 2026-09-26 y su medición en
`evidence/…/CIERRE-ORDEN-2026-09-25/19-s19-medicion-de-los-dos-riesgos.txt` §8. Su forma es el patrón ya
probado en `scripts/verify_index_in_committed_tree.py`: materializar la revisión en un clon, regenerar a
scratch y comparar por sha normalizado, con controles anclados a una revisión publicada fija y nunca a HEAD.
**Sigue sin implementar: eso es código, y el dueño de esa decisión es el operador.** ⟦**Vencido el 2026-09-26
por la cura (b)**, que es código y se hizo con instrucción del operador; y vuelve a vencerse el 2026-09-27 con
**D-a**, que ata ese verificador al `--quick`. Lo que de esta frase sigue en pie es solo **(c)**: la convención
de cierre continúa sin escribirse en `.agents/` por falta de instrucción explícita, no por falta de
acuerdo.⟧ ⟦**S19 — cierre del libro: (a) descartada con medición en contra (`19-` §5); (b) implementada el
2026-09-26 en `scripts/verify_packs_in_committed_tree.py`; (c) vigente, dueña una instrucción literal sobre
`.agents/`, y casada con S16 porque son la misma superficie; (d) `generado_por_sha` medida el 2026-09-27 en el
expediente `22-` §3 y no aplicada — su coste es +1 línea por pack y exige un quinto patrón en `NORMALIZAR`, y
se probó que (b) **no** la necesita para atribuir el rojo. Con (b) cableada al rápido desde el 2026-09-27, S19
queda CERRADA en su parte gobernable y sobrevive solo por (c).**⟧
**(c) se
mantiene como puente y queda probada su insuficiencia:** el 2026-09-26 `--check` dio `EXIT=0` con los cinco
packs ya cambiados por una edición del escritor (244 inserciones / 99 supresiones, 6 líneas de pack citando el
`[8/12]` nuevo). Prueba estructural leída del artefacto: `sources[]` de FASE-A declara 4 rutas y **ninguna es
el escritor**, mientras el bloque meta ya publica `generado_por` — el pack nombra a su productor sin casarlo.
De ahí una cuarta opción que la medición hizo visible y no se aplica: sellar `generado_por_sha` como
procedencia **no gobernante** (coste ~el de la normalización, no re-vence nada, y (b) lo necesita para atribuir
el rojo). **No se toca `.agents/`**: la convención de cierre sigue sin escribirse en el executor por falta de
instrucción explícita, no por falta de acuerdo.⟧ ⟦**S19 queda CERRADA enteramente el 2026-09-27: se cumplió
la única mitad que le quedaba abierta, la (c).** La instrucción literal sobre `.agents/` llegó con la familia
D-b de la orden de calidad y se escribió en sus dos dueños — la convención de cierre en el checklist post-fase
del executor (v2.26.0) y la forma canónica `Lee …` en §8 del template de fase (v1.7.0), que es además la cura
de **S16** con la que esta fila estaba casada. Lo que la medición de (c) probó no se retira: la convención
**por sí sola** era insuficiente como gobernanza, porque `sources[]` no declara al escritor y el `--check`
verdeaba con los packs vencidos; eso sigue siendo cierto y por lo que existe la cura (b), cableada al rápido
por D-a. Lo que cambia es el estado del libro: **(c) deja de ser deuda**. La **(d)**, `generado_por_sha`, sigue
siendo una cuarta opción medida y no aplicada, con su coste y su dueño en el operador — cerrar (c) no la
absorbe ni la descarta⟧

⟦**Sello 2026-09-28 — cambio C6 de la orden de curas en `scripts/` (sesión 2).** Se re-mide (d) y
queda **ABIERTA por la salida (c)**: requiere una superficie que esta orden no autoriza, y aquí queda
la justificación. Medido sobre `84c1aca` más la cura C2, con crudo en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/21-c6-s19d-coste-medido.txt`:
el verificador del árbol commiteado normaliza **cuatro** tokens inestables y **ninguno** cubre un
futuro `generado_por_sha`; el sha del propio escritor **sí** se mueve entre commits — cuatro
revisiones que lo tocaron más el árbol de trabajo dan **4 valores distintos sobre 5 mediciones** —,
así que publicarlo en el pack sin añadir el quinto patrón produciría `DIVERGE` entre revisiones
correctas: el mismo defecto de instrumento que **S20** documentó para el clon. El coste de la línea
nueva es **+1 por pack** (cinco packs en este plan) **más** ese patrón en
`scripts/verify_packs_in_committed_tree.py`, guion que la orden no nombra entre los cinco autorizados.
No la cubre tampoco la cura **C2** de esta misma tanda: gobernar la proyección de bytes del workflow
canónico no casa la identidad del generador, y la fila ya había medido que la cura (b) no necesita
(d) para atribuir el rojo. Dueño y disparador no cambian. Una nota de instrumento de esta medición:
el primer barrido de «¿está la clave?» se hizo por substring sobre el pack y dio **SI falso** en los
cinco — la prosa de esta misma fila viaja al pack y menciona `generado_por_sha` como texto. La clave
se lee en el bloque `BRIEFING-META`, no en el cuerpo; releída así, la clave no está publicada.⟧

### S20 — el clon del verificador hereda `autocrlf` de sistema y su `--check` de packs da rojo falso (nueva, 2026-09-26)

**Medido al verificar el commit `941530e` en su propio árbol.** `scripts/verify_index_in_committed_tree.py`
salió `EXIT=0` (`[OK] índice en el árbol de HEAD (565 rutas materializadas)`), pero al re-usar ese mismo clon
para el otro derivado, `build_phase_briefing.py --check` cortó **`EXIT=1`** con `SHA-DISTINTO` en siete rutas
gobernadas (`06-checklist-implementacion.md`, `dependencias-fases.md`, `10-analisis-post-implementacion.md` y
los cuatro `05-prompt-inicio-sesion-fase-*.md`). **El árbol no estaba mal**: los packs y el par del índice se
commitearon consistentes y el `--quick` del árbol de trabajo daba 12/12. Estaba mal el instrumento.

**Causa, medida por ámbitos de configuración** y no inferida: `core.autocrlf` vale **`true` en el ámbito
system** (`C:\Program Files\Git\etc\gitconfig`), no tiene valor en global, y vale **`input` en el config local
de este repositorio**. Un `git clone` **no copia** el `core.autocrlf` local de la fuente, así que el clon que
fabrica el verificador nace sin valor local y hereda el `true` de sistema. El `-c core.autocrlf=input` que el
script pasa al comando `clone` (en `revisar`, antes del `checkout`) solo gobierna ese proceso de clonado: el
`git checkout <rev> -- <rutas>` posterior corre dentro del clon, lee la config **del clon**, y convierte LF →
CRLF al materializar. Un verificador que compara `sha256` de bytes en disco pasa a comparar bytes re-escritos.

**Prueba de la atribución, sin tocar código:** clonar igual pero escribiendo `core.autocrlf=input` en la config
del clon **antes** del checkout. Sobre `941530e` con ese árbol, los dos verificadores dan verde:
`build_phase_briefing.py --check` → cinco líneas `[OK] … fuentes frescas (procedencia distinta, no vence)` con
`EXIT=0`, y `build_lesson_index.py --check` → `[OK] Índice de lecciones fresco (339 IDs)` con `EXIT=0`.

**Por qué el rojo salió en un derivado y en el otro no:** la comprobación del índice **parsea contenido**, así
que sobrevive al cambio de remates; la de los packs **compara shas de bytes**, así que el cambio la mata. Es la
misma familia de la trampa que obligó a poner `core.longpaths` **dentro** del clon (S15), pero con el síntoma
invertido: allí el árbol llegaba parcial (519 de 6.106) y el veredicto era ruido; aquí el árbol llega completo
y el veredicto es falso. Un verde o un rojo que dependen de los remates del sistema invitado no miden el
commit.

**Cura y coste.** Una línea: fijar `core.autocrlf=input` en la config del clon junto con `core.longpaths`, antes
del `checkout`, en `revisar()`. Su batería de pruebas necesita un caso que **no exista hoy**: un `--check` de
comparación byte-exacta corrido en el árbol del commit, porque el defecto es invisible para la batería actual
(que solo ejercita el índice, y el índice es tolerante). Es código, así que **dueño: decisión del operador**.
**Disparador:** la primera vez que alguien intente re-usar el verificador para un derivado que compare bytes —
que es exactamente lo que pide la cura (b) de S19, todavía sin implementar ⟦**vencido el 2026-09-26: se
implementó ese día; y el 2026-09-27 quedó atada al `--quick` por D-a**⟧. Las dos comparten árbol materializado
y las dos fallan silenciosamente si el árbol no es fiel.

**Nota de instrumento para la próxima numeración.** La fila S19 justifica su número con
`grep -rn "S19" .opencode/`, y ese comando barrido `node_modules`: medido hoy, `grep -rn 'S20' .opencode/` da
**10 coincidencias** todas dentro de `.opencode/node_modules/` (substrings en JS minificado), mientras que el
barrido acotado al corpus —
`grep -rn --exclude-dir=node_modules --exclude-dir=Archives 'S20' .opencode/plans .opencode/context` — da **0**,
que es la afirmación que importa. `S20` está libre. Los números en uso en este libro son
S1, S8, S10-S13, S16, S17, S18, S19 y esta misma S20. ⟦**Censo re-medido el 2026-09-27, que es la regla que
esta misma nota propone**: desde entonces se abrieron **S21** (los dos denominadores del runner) y **S29** (el
verificador de capitalización no ve a los archivados), así que los números con sección propia en este libro
son hoy **S16, S17, S18, S19, S20, S21 y S29**, y `S22`…`S28`/`S30` existen en **otros** libros
(`Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y compañía) — contar en el corpus, no en el libro, antes de
usar un número: `git grep -l -E "\bS29\b" HEAD -- '*.md'` devolvió **0** coincidencias antes de tomarlo⟧

⟦**S20 curada el 2026-09-26, por instrucción del operador de seguir el orden propuesto.** Aplicada en
`scripts/verify_index_in_committed_tree.py`: `clon_fiel()` fija `core.longpaths=true` **y**
`core.autocrlf=input` dentro del clon antes del `checkout`, y **lee el valor efectivo** — si no es `input`,
sale `EXIT=2` con motivo, porque un árbol infiel no puede dar ni verde ni rojo. Se separó el materializado
del `--check` porque hay un segundo consumidor: `scripts/verify_packs_in_committed_tree.py` (abajo). Verificado
sobre `c85dff9`, una revisión publicada fija: con `input` el `--check` de briefing da `EXIT=0` y los packs del
clon son **byte a byte** los del blob (`git ls-files --eol` dice `i/lf w/lf`, y el clone devolver `i/lf w/crlf`
era la firma del defecto); con `true` forzado el mismo commit da `EXIT=1` con `SHA-DISTINTO`. La batería vive en
`tests/test_verify_index_in_committed_tree.py` (9 funciones, cuatro nuevas) y su control negativo **ejerce** el
defecto en lugar de simularlo, con la advertencia de re-anclaje si el `--check` dejara de ser ciego. Detalle de
instrumento corregido en el camino: contar remates con `grep -c $'\r'` da **todas las líneas del archivo**, no
los retornos de carro; se cuenta por bytes (`b"\r\n"`) o con `tr -dc`.⟧

⟦**Cura (b) de S19 implementada el 2026-09-26**, en la misma instrucción: `scripts/verify_packs_in_committed_tree.py`
materializa la revisión con `clon_fiel`, regenera los packs con `--briefing-dir` hacia un scratch **dentro del
árbol del commit** (sin `--informe` ni `--carga`, que es la guarda de S12), y compara cada pack por `sha256`
**normalizado**. La normalización es la que dejó la medición de `19-`: el sello `· generado \`<UTC>\``,
`generated_at` y `head`, que AC21 ya declaró no gobernantes. Veredictos: `0` reproduce, `1` diverge, `2` no
evaluable — y esa tercera salida existe por una medición que hice mal primero: el clon materializaba solo
`scripts` y `.opencode`, así que FASE-RELEASE, que declara `docs/CONTRIBUTING.md`, salía como `PACK-AUSENTE` y
mi verificador lo contaba como divergencia. Amplié el materializado a `docs` y `.agents` (~1 s) y dejé la
clasificación honesta para lo que quede fuera. El control negativo no simula: muta en el clon el literal `[8/11]`
que el propio escritor copia al pack y exige **dos** cosas a la vez — que este verificador dé `EXIT=1` con la
diferencia señalada, y que `build_phase_briefing.py --check` dé `EXIT=0` sobre ese mismo árbol. Ese par es S19
convertido en máquina. `tests/test_verify_packs_in_committed_tree.py`: 5 funciones.⟧

⟦**D-a ejecutada el 2026-09-27 por instrucción escrita del operador** («Continuamos según tu recomendación»
sobre el dosier `22-` §5). El verificador de packs en el árbol del commit es el check **`[13/13]`** del rápido:
**12→13** en el modo rápido y **16→17** en el completo. Lo que costó, medido antes y no de memoria: **26
literales re-etiquetados en cinco rutas**, no los cinco pines que declaraba el parte — 16 dentro de
`scripts/run_all_validations.py` (doce del rápido y cuatro del completo, todos impresos como literal), 2 en
`scripts/build_phase_briefing.py` (uno de ellos un **mensaje que el escritor copia dentro de los cinco packs**,
que es por lo que esta edicion re-vence los derivados y obliga a la cola), 6 en
`test_governance_numbers_reproduce_A1_A4.py` (cuatro `observed` + el `total` de la base de cobertura + su nota
datada), 1 en `test_governance_numbers_mutation_por_asercion.py` y 1 en
`test_briefing_se_genera_por_fase.py`. **Dos cifras del parte quedan corregidas por medición**: (1) la **premisa**
del hallazgo A3 —la copia del workflow en el fixture de `governance_numbers`, la fila que afirma el `[12/12]`— **no
se mueve**: es lo que el test audita, y re-etiquetarla borraría el defecto que caracteriza; (2) las cuatro
menciones del corpus (la fila A3 de `01-plan-maestro.md`, la casilla A1–A4 de `06-checklist-implementacion.md`, la
fila A3 de `10-analisis-post-implementacion.md` y la nota del instrumento en este mismo libro) **tampoco**: son
antecedentes fechados, tres ya marcados VENCIDA o rectificada.

Tiempo añadido al rápido, re-medido hoy sobre la base de hoy: **+2,4 s** (23,99 s → 26,4 s, **+9,9 %**), con
un clon de 588 rutas. El costo real no fueron los segundos sino la **tercera ronda de re-anclaje** en once días.

Y la parte que el dosier dejaba sin gobernar, cerrada con código: los ordinales del runner son literales
**porque** `validate_governance_numbers.py` lee su registro de emisores casándolos en la fuente, así que
volverlos dinámicos cegaría al verificador. En su lugar quedó una **guarda en `_print_summary`**: exige que los
ordinales impresos sean exactamente `1..N`, que el último lleve denominador `N` y que en el rápido los N
denominadores coincidan con `len(self.results)`. No consume un ordinal a propósito: si lo consumiera, renumerar
podría apagar la propia guarda. Sus dos controles, en
`evidence/…/CIERRE-ORDEN-2026-09-25/D-A-QUICK-TRECE/01-controles-guarda.txt`: dejar el denominador viejo en el
check nuevo da rojo, y dejar el denominador viejo en **un check cualquiera** del rápido también da rojo; la
fuente sin mutar da verde. Derivación de la guarda, consignada en su docstring porque fue un rojo mío: la
primera versión filtraba por número de línea contra la barrera `if not self.quick:` (línea 95, dentro de
`run_all`), pero las etiquetas viven en los métodos (línea 118 en adelante), así que devolvía **cero etiquetas**
y cortaba rojo sobre una fuente correcta.

Un rojo que la batería nueva encontró, y que no venía de mis ediciones:
`test_un_destino_relativo_no_escribe_dentro_del_clon`
moría en la **segunda pasada seguida** porque su destino es `temp/verif-ruta-<tmp_path.name>` y ese nombre es
**estable entre corridas**, mientras el `finally` limpia con `ignore_errors=True` — bajo bloqueo de Windows el
árbol queda y el `git clone` siguiente muere con «already exists and is not an empty directory», un fallo que no
medía al verificador. Se corrigió el **mecanismo de aislamiento** (limpiar antes de clonar, y `pytest.fail` con
el diagnóstico si el residuo persiste), no la aserción. Prueba: plantando el residuo a propósito la batería pasa
5/5, y dos pasadas seguidas dan 5/5 y 5/5. Queda como deuda de procedimiento **sin número** porque su cura ya
está en el árbol: otra prueba que derive su destino de un nombre estable bajo `temp/` caerá igual.⟧

⟦**Rectificado el mismo 2026-09-27, dos veces: la causa que di arriba era falsa y el control plantado era
débil.** (1) No es bloqueo ni camino largo —la ruta relativa más profunda mide **108** caracteres—: `git` deja
sus objetos de `.git/objects` **en solo lectura**, y `shutil.rmtree` en Windows levanta
`PermissionError: [WinError 5] Acceso denegado` sobre el objeto nombrado. Con `ignore_errors=True` ese error se
traga, así que el `finally` **nunca** había limpiado nada: el residuo era lo normal, no la excepción. (2) Mi
control «plantar el residuo» creaba un directorio **sin** el atributo de solo lectura, por eso daba 5/5 sobre un
caso que no era el real — plantar un árbol no reproduce la propiedad que lo hace irreborrable, y un control que
no reproduce el defecto no es un control. La cura verdadera es `shutil.rmtree(..., onexc=...)` quitando la
protección de escritura y reintentando ese nodo. (3) Lo que lo destapó fue **la suite completa**, no la batería
acotada: pasó de 4 rojos a **5** y el quinto era este test. Dos pasadas de una batería no prueban aislamiento
cuando el residuo lo fabrica la corrida anterior de esa misma batería.⟧

### S21 — el runner imprime dos denominadores distintos dentro del mismo modo (nueva, 2026-09-27)

**No confundir con `S21` de `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`**, que trata de concurrencia entre
sesiones y es asunto distinto: este es **S21 de este libro**, como `S19` y `S20` lo son.

En modo **completo** el runner ejecuta 17 checks, pero **trece** de sus líneas de progreso siguen diciendo `/13`
y solo las cuatro exclusivas del completo dicen `/17`. Leído del código (líneas 117-742 con `/13]` y 776-866 con
`/17]`) y no de una corrida: el modo completo invoca pytest y **no se corrió** para abrir esta fila. Existe desde
antes de D-a —era `/12` contra `/16`—, y la renumeración del 2026-09-27 lo **conserva sin agravarlo**: la
guarda nueva solo exige uniformidad de denominador en el modo rápido, porque gobernar la del completo sin tocar
los literales sería justo la cura dinámica que cegó al verificador.

- **Dueño:** este plan, o el siguiente que toque `run_all_validations.py`. No es bloqueante: ningún check, test
  ni documento afirma hoy el denominador del completo con forma `/N`, así que la contradicción es de **lectura
  humana** de la consola, y por eso se registra en vez de corregirse en silencio.
- **Disparador:** la próxima vez que alguien lea una corrida completa y crea el denominador que ve, o la próxima
  renumeración del runner.
- **Salidas, con su coste:** (a) re-etiquetar los doce del rápido también con `/17` en modo completo, lo que
  exige que el ordinal se componga al vuelo y **rompe** `PRINT_LABEL_RE` del verificador de gobernanza — la
  misma trampa que ya descartó la cura dinámica; (b) publicar en la cabecera de la corrida que el denominador
  impreso es **del modo rápido** y que el completo llega a 17, que es una línea y no toca ningún literal; (c)
  dejarlo y confiar en esta fila. La lectura recomendada es **(b)**.

⟦**Sello 2026-09-28 — C3 de la orden de curas en `scripts/` (sesión 2): CURADA con la salida (b), que es la
que esta misma fila recomendaba.** La cabecera de `_print_summary` publica ahora el modo de la corrida y a
qué modo pertenece el denominador impreso: «MODO: rapido — el denominador de las etiquetas impresas es el del
modo rápido (13); el modo completo llega a 17 y solo sus 4 exclusivas se etiquetan con ese numero». Los
literales de las etiquetas no se tocaron: de ellos vive el registro de emisores que lee
`validate_governance_numbers.py`, y la salida (a) lo cegaba (es la trampa que ya descartó la cura dinámica).
La lectura de la cabecera sale en ASCII, como el resto de las líneas impresas del runner, por la consola
cp1252.

Además, la **[GUARDA] corta también fuera del rápido**, que era el hueco que la fila dejó declarado: antes su
uniformidad dependía de `not self.quick`, así que en el modo completo un tercer denominador pasaba verde. Ahora
la guarda exige que los denominadores impresos estén dentro del par declarado por el modo (el del rápido y el
del total), con `len(orden_rapido)` leído del propio llamador por `_orden_del_modo()`, la misma lectura que
usa las etiquetas — así el denominador publicado y el gobernado salen de una sola lectura y no de dos cuentas
que puedan separarse.

Dientes y cifras medidas: con un denominador foráneo reintroducido en una etiqueta del rápido, la guarda cortó
en **ambos** modos (rojo documentado en la batería nueva); y apagando la comparación —volviendo la condición
a su forma anterior— el mismo escenario del modo completo **volvió a verde**, que es exactamente el rojo falso
que esta fila registró. La batería `tests/test_run_all_validations_denominador_por_modo.py` (cinco pruebas, con
los denominadores leídos del runner y no pineados) quedó en verde, el quick en **13/13** con `[GUARDA]` verde,
y `validate_governance_numbers.py --report` en **EXIT=0** después del cambio: el lector sigue resolviendo 13
del rápido y 17 del completo, y el número de etiquetas del archivo no cambió (**17**, igual que en `REV_INICIO`)
porque la cabecera nueva no es una etiqueta. El modo completo **no se corrió como corrida real**: invoca la
suite de pytest, prohibida en esta orden; su cabecera y su guarda se imprimieron por la vía offline. Crudos:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/11-c3-quick-post.txt`,
`15-c3-cabecera-por-modo.txt`, `14-c3-mutante.txt`. **Estado de la fila: CERRADA por ejecución en su salida (b),
con el hueco de la guarda del completo cerrado en la misma tanda.**⟧

### S29 — el verificador de capitalización excluye `Archives/` por estructura, y este `00-` se quedó sin gate (nueva, 2026-09-27)

**No confundir con ningún número vecino**: el censo del 2026-09-27 sobre `HEAD -- '*.md'` marca usados
**S1…S28 y S30**, y **S29** devuelve **cero** coincidencias — es libre, y esta fila lo toma. (El enunciado de
la orden decía «S21 a S26 están usados»; se queda corto, ver el expediente `25-` §1.)

**Hecho medido con el propio código, no deducido.** `validate_lesson_capitalization.py` reparte el corpus en
`clasificar_planes()`, y esa función **salta el directorio `Archives/` antes de mirar el cutoff**: los 28
planes archivados van al grupo `archivados`, que `verificar()` **nunca iterar** — el bucle recorre solo
`grupos["alcance"]`. Con el cutoff de casa (`2026-09-12`) la línea de cobertura publicó
`alcance 3 · archivados 28 · exento_fecha 0 · sin_fecha 0`. **Este plan está en el grupo de 28.**

**Consecuencia para esta orden, que es por lo que se abre la fila y no por curiosidad**: D-d capitalizó diez
filas en el §2 de este `00-` **después** de que D-c moviera el plan a `Archives/` (2026-09-26). Desde ese
traslado, el `[10/13]` del rápido **no lee este archivo**, así que su `[OK]` no dice nada de las diez filas.
El green de una tanda que toca un plan archivado es, respecto a ese archivo, un verde vacío: no es que el
check encuentre bien las filas, es que **no llega a mirarlas**. Lo mismo vale para cualquier plan cerrado: de
los 28 archivados, **3** tienen `00-lecciones-capitalizadas.md` y ninguno está bajo gate.

- **Dueño**: `scripts/validate_lesson_capitalization.py`, o sea **código** — no le toca a esta sesión, que no
  tiene mandato de `scripts/`. Le corresponde al operador con instrucción literal, o al plan que toque ese
  verificador. Esta fila registra el estado del instrumento, no propone la cura.
- **Disparador**: la próxima vez que alguien cite el `[OK]` de `Lesson Capitalization` como evidencia sobre un
  plan **archivado**, o la próxima capitalización posterior a un cierre — que es exactamente la forma que
  tomó D-d.
- **Salidas, con el coste corrido y no predicho** (crudo `…/GRUPO-B-P0-CONVENCION-2026-09-27/26-coste-de-ampliar-el-detector.txt`):
  **(a)** quitar la exclusión de `Archives/` — ~2 líneas, y **fabrica 25 hallazgos `C1/AUSENTE`**, uno por cada
  plan archivado anterior a la regla del Paso 0 que no tiene `00-` (el primero que imprime la corrida:
  `Archives/ASSET-ALIGNMENT-ZIONE-2026-07-23: no existe 00-lecciones-capitalizadas.md`). Ampliar un detector sin
  gobernar su población tira el árbol, que es la lección que esta casa ya pagó. **(b)** una bandera explícita
  (`--incluir-archivados`, o el `--cutoff` hacia atrás) que audite **solo** los archivados con artefacto presente
  y publique su población en C0: medido sobre los **3** que sí lo tienen, darían **0 violaciones** — o sea la cura
  es pequeña y su verde es comprobable antes de commitearla; ~10-15 líneas más su test. **(c)** dejar el
  instrumento y gobernarlo por procedimiento: toda edición post-cierre de un `00-` archivado **cita la corrida
  explícita** del verificador sobre ese plan, que es lo que esta sesión hizo y lo que quedó en el propio `00-`.
- **Lo que sí se hizo en lugar del gate, y su techo**: se importó `duenos_del_corpus` y se corrió
  `analizar_plan()` sobre este plan archivado → **C1…C8 sin hallazgos**, 7 dueños, crudo
  `…/GRUPO-B-P0-CONVENCION-2026-09-27/22-c1-c8-sobre-el-plan-archivado.txt`. Eso prueba la forma **una vez y
  a mano**: no es verificable en el árbol y no protege la siguiente edición.

**⟦DECIDIDA Y EJECUTADA el 2026-09-27 por instrucción escrita del operador (orden de cierre, paso T1). La salida
es la (a) con el cutoff vigente, no la (a) desnuda que esta fila medía: se llama (a-prima)⟧**

`clasificar_planes()` dejó de saltar `Archives/` como estructura y sus hijos pasan por **la misma regla de cutoff**
que los de raíz; `grupos["archivados"]` se conserva como marcador de corpus y `verificar()` publica además cuántos
archivados quedaron en alcance (clave nueva `archivados_en_alcance`). `_linea_de_cobertura()` ya no imprime
«archivados excluidos»: imprime «N archivados en el corpus, M de ellos en alcance».

- **Por qué prima y no exclusión a secas** (crudo `…/GRUPO-B-P0-CONVENCION-2026-09-27/26-coste-de-ampliar-el-detector.txt`,
  re-confirmado el 2026-09-27 con las funciones del propio módulo): quitar la exclusión **sin cutoff** fabricaba 25
  `C1/AUSENTE`; **con** cutoff, 0. De los 28 archivados, 2 son posteriores al corte y entran, 20 quedan exentos **por
  su fecha** y 6 sin fecha parseable. La fila (a) de arriba describía el coste de la variante sin gobernar; la prima
  conserva ese cutoff como única regla de entrada.
- **Población nueva al cutoff de casa**, con su comando exacto — `python scripts/validate_lesson_capitalization.py`:
  `cobertura: 5 plan(es) en alcance (…) | 28 archivados en el corpus, 2 de ellos en alcance | 20 exentos por fecha
  anterior a 2026-09-12 | 6 exentos SIN FECHA PARSEABLE (…)` → exit 0, **0 violaciones**. Antes de la cura la misma
  corrida publicaba `3 plan(es) en alcance · 28 archivados excluidos`.
- **Dientes** (crudos `…/S29-A-PRIMA-2026-09-27/`): `02-` es el parche de la cura y `03-` el mutante — revertido el
  script real, caen 4 tests (`test_archives_no_se_excluye_por_estructura_sino_por_su_fecha`, `test_b5_…`, el
  parametrizado `test_medido_contra_el_predecesor…[2026-09-11-…]` y el nuevo anclado a revisión fija
  `test_el_plan_archivado_posterior_al_corte_entra_en_alcance_sobre_revision_fija`, materializado con `git archive`
  sobre `9c4a001`, donde la raíz de `plans/` no tiene ningún plan con fecha) y los otros 26 pasan igual; bytes
  restaurados con sha256 igual antes y después (`e2529b32…`). `04-`/`05-` dan el POST por población: **46 → 45 rojos,
  cae exactamente el de capitalización, cero nuevos**.
- **Lo que la cura NO toca**: el workflow `phased_project_executor.md` §2.5 sigue escribiendo en su «Alcance hacia
  delante» que el gate aplica a planes «que no estén en `Archives/`», y su fixture copia en
  `tests/quality_gates/governance_numbers/fixtures/` repite la frase. Esa prosa es **norma**, y promoverla pide su
  propia entrada de changelog de workflow: queda declarada vencida por el código y pendiente de la instrucción que
  la reescriba.
- **Dueño y disparador de la fila**: se retiran los dos pendientes que la abrían (el mandato de `scripts/` y la
  cita de un `[OK]` vacío sobre archivados). Lo que queda en pie de su texto es la advertencia: un verde del rápido
  sobre un plan archivado solo dice algo **desde esta cura**.
- **Alternativa descartada**: promover un check nuevo al `--quick` que audite el `00-` de los archivados. No
  toca el fondo — el fondo no es la falta de un check, es el **reparto de población** que comparten todos los
  checks de esa familia; un check extra con el mismo reparto hereda la misma ceguera y además cuesta un
  re-numerado (eso es D2 y su familia de pins).

**⟦Sexta cosa que esta fila gobierna, medida el 2026-09-27 en la sesión de curas fuera de plans⟧.** La cura
a-prima cambió el comportamiento y dejó **la prosa del executor describiendo la regla vieja**: el §2.5
«Alcance hacia delante» publicaba todavía «y que no estén en `Archives/`» y un conteo de archivados, y su
copia del contraejemplo congelado repetía la frase. Se curo el texto (executor **v2.27.0**, con su entrada
de changelog y su copia alineada a mano porque **no hay writer** que sincronice ese fixture — medido con
`git grep -ln "governance_numbers/fixtures" HEAD -- scripts tests`, 0 resultados).

- **Lo que quedó medido y sigue abierto**: revertir el párrafo a la frase vencida **no produce rojo** —
  `validate_governance_numbers.py` sale `SIN-HALLAZGOS` (19 instancias), las dos baterías de gobernanza y
  capitalización dan 79 passed y el `--quick` 13/13. Crudos:
  `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T1-PROSA-WORKFLOW/11-…` y `12-…`.
  Es decir: gobernar el **comportamiento** no gobierna la **descripción** del comportamiento, y nadie avisa
  cuando la descripción se desfasa. Dueño propuesto: el mismo de esta fila
  (`scripts/validate_lesson_capitalization.py`, que es quien conoce el reparto real), con un check de
  consistencia texto↔código; **disparador**: el próximo mandato de código sobre ese script, porque abrir un
  check nuevo es re-numerar y eso es D2.
- **Por qué no se absorbe aquí**: curarlo pide editar `scripts/` y esta sesión tenía mandato literal sobre
  tres cosas concretas (`validate_opencode_refs.py`, los seis arneses y la prosa), no sobre el verificador de
  capitalización. Queda como sub-punto con dueño en vez de fila nueva: **S33 está libre**
  (`git grep -l -E "\bS33\b" HEAD -- '*.md'` = 0) y se deja sin tomar, porque el asunto no es un defecto
  distinto sino la sexta cara del mismo reparto de población que gobierna esta fila.

### S31 — los arneses de FASE-C y FASE-D pinean la ruta de raíz del plan y D-c la archivó (nueva, 2026-09-27)

**No confundir con ningún número vecino**: el censo del 2026-09-27 sobre `HEAD -- '*.md'` con
`git grep -l -E "\bS31\b" HEAD -- '*.md'` devuelve **0** coincidencias — es libre, y esta fila lo toma. (S29 se
tomó el mismo día por la orden de calidad; S30 existe en **otro** libro, ver la nota de censo en §S20.)

**Hecho medido, no deducido.** El `git mv` de D-c (`3c2e6a3`, 2026-09-26) sacó este plan de la raíz de
`.opencode/plans/` y lo puso bajo su hijo `Archives/`. Cinco constantes de
los arneses de FASE-C y FASE-D resolvían la ruta de raíz a pelo, sin pasar por `resolver_plan()` del escritor,
así que desde ese commit sueltan `FileNotFoundError` y **42 rojos** entran a la suite por causa del traslado,
no por un defecto de producto: **36** en `tests/quality_gates/lesson_relevance/` y **6** en
`tests/quality_gates/phase_briefing/`. Crudo de la población: `…/S29-A-PRIMA-2026-09-27/05-atribucion-post-t1.txt`
(POST de T1: 46 → 45 rojos; estos 42 son exactamente lo que queda aparte de los 3 atribuidos el 2026-09-25).

**Las constantes** (todas se llaman `PLAN`; la orden las listaba por número de línea, aquí se citan por símbolo
porque la línea rota en cuanto se edita el archivo):

| Archivo del arnés | Símbolo |
|---|---|
| `tests/quality_gates/lesson_relevance/conftest.py` | `PLAN` |
| `tests/quality_gates/lesson_relevance/test_triage_mutation_aditividad.py` | `PLAN` |
| `tests/quality_gates/lesson_relevance/test_triage_propuesta_no_escribe_seccion_dos.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/conftest.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/test_briefing_carga_total_tres_sumandos.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/test_briefing_se_genera_por_fase.py` | `PLAN` — **sexta, medida al ejecutar: no estaba en la lista de cinco de la orden** |

- **Dueño**: los arneses de **FASE-C** (`lesson_relevance/`) y **FASE-D** (`phase_briefing/`) de **este plan** —
  es instrumento de este plan, no deuda de un tercero. Se abre aquí porque la produjo su propio cierre R2.5.
- **Disparador**: ya sonó. Toda lectura de «la suite da N rojos» sobre un árbol donde este plan está archivado
  incluye estos 42 hasta que la fila se cierre.
- **Estado al abrir la fila**: **abierta, con la cura autorizada** por la orden de cierre del 2026-09-27 (paso
  T2). Se re-ancla cada constante a `plans/Archives/<PLAN>` y se ejerce con control negativo: revertida una de
  ellas, su archivo de arnés vuelve a rojo **por la misma causa** (`FileNotFoundError`), restaurada vuelve a
  verde. Crudos en `evidence/…/CIERRE-ORDEN-2026-09-25/`.
- **Lo que NO es esta cura**: no se toca el generador ni `resolver_plan()`. La lección de fondo ya está escrita
  (la de D-c: el verificador de packs montaba la ruta a pelo y quedó ciego tras el archivado; la cura ahí fue
  reutilizar `resolver_plan()` del propio escritor). Aquí se re-anclan literales de fixture, así que **la
  fragilidad estructural sigue**: un próximo `git mv` de este plan volvería a tirar estas seis constantes. Se
  declara en vez de absorberla, porque gobernarla es un cambio de arnés con su propio alcance.

**⟦CERRADA el 2026-09-27, paso T2 de la orden de cierre, con su POST por población⟧**

- **Seis constantes re-ancladas, no cinco.** La orden listaba cinco; la sexta (el `PLAN` de
  `tests/quality_gates/phase_briefing/test_briefing_se_genera_por_fase.py`) apareció al ejecutar: con las cinco
  curadas ese archivo seguía dando **4 rojos**. Control de residuo:
  `grep -rn '"plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"' tests --include=*.py` devuelve **0**, y las seis
  rutas bajo `Archives/` devuelven **6**. Quedan en el árbol otras menciones de la ruta vieja que **no** producen
  rojo y no se tocaron: un `assert ... not in` (línea 122 del mismo archivo), dos docstrings
  (`test_build_lesson_index_s15_fecha_versionada.py`, `test_sync_writers_lf_y_fecha_readme.py`) y dos constantes de
  `test_verify_index_in_committed_tree.py` que resuelven contra el árbol versionado, no contra el de trabajo. La
  frase de arriba decía «estas cinco constantes» y se corrigió a seis en la misma sesión, antes de commitear.
- **Causa por población, medida sobre el PRE (`…/S29-A-PRIMA-2026-09-27/00-suite-pre.txt`)**: 36 de los 42 son
  `FileNotFoundError` sobre la ruta de raíz; los otros 6 muestran otra cara del mismo hecho —**1 `IndexError` y
  3 `AssertionError` («informe sin packs no responde AC19») en `se_genera_por_fase`, y 2 en `carga_total`**— porque
  esos arneses listen el directorio en vez de abrirlo. Publicar «la causa es FileNotFoundError» sin el desglose
  habría hecho buscar una traza que ahí no está.
- **Control negativo** (crudo `evidence/…/CIERRE-ORDEN-2026-09-25/S31-RUTA-ARCHIVADAS-2026-09-27/01-…`): revertida
  la sexta, su archivo vuelve a **4 failed** con la misma firma que el PRE (2× «informe sin packs no responde AC19»,
  1× «list index out of range»); restaurado, **8 passed**, y el sha256 del archivo es idéntico antes y después
  (`cbc32233…`).
- **POST por población**: `python -m pytest -q -ra` → **3 failed, 4613 passed, 41 skipped, 4 xfailed, 0 errors**,
  exit 1. Contra el POST del paso T1 caen **exactamente 42** (36 `lesson_relevance` + 6 `phase_briefing`) y entran
  **0 nuevos**. Los 3 que quedan son los atribuidos el 2026-09-25 y no son de esta fila:
  `test_function_default_flags`, `test_diagnostic_includes_geo_metrics` y
  `test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`.
- **Arneses verdes por separado**: `tests/quality_gates/lesson_relevance` **57 passed** exit 0 y
  `tests/quality_gates/phase_briefing` **49 passed** exit 0. El `--quick` quedó en **13/13** exit 0 tras regenerar
  lo que la edición de esta fila vence.
- **Estado de la fila**: **cerrada por ejecución**, con la fragilidad estructural declarada arriba como límite y
  no como pendiente de esta tanda.

**⟦Fragilidad estructural CERRADA el 2026-09-27, segunda tanda de la misma fila, con mandato literal de la orden
de curas fuera de plans⟧.** La cura que arriba se declaraba fuera de alcance («la forma durable sería reutilizar
`resolver_plan()` del propio escritor, y eso no entra aquí») entra ahora por su puerta: los seis arneses dejan de
armar la ruta y preguntan al escritor.

- **Cómo**: un puente, `tests/support_resolucion_plan.py`, que carga `scripts/build_phase_briefing.py` por ruta
  (el mismo oficio de los dos `conftest.py`) y expone `ruta_plan()`, delegando en `resolver_plan()` del escritor.
  Las seis constantes `PLAN` pasan por él. No se reimplementó la resolución: una sola copia de la regla, en el
  escritor — y no se tocó `resolver_plan()` ni el generador, que era el límite de la tanda anterior.
- **Semántica de error conservada**: el arnés pineado fallaba con `FileNotFoundError` al leer la ruta que ya no
  estaba; `ruta_plan()` levanta **ese mismo error** nombrando las rutas intentadas (por `rutas_intentadas()` del
  propio escritor), en vez de un `None` que revienta tres líneas más tarde con un `AttributeError` que no nombra
  el plan (R2.9).
- **Dientes anclados a revisión FIJA**, con el precedente de la cura de D-c para el verificador de packs: la
  revisión testigo es `44f53c2`, el **padre** del `git mv` de D-c, verificado con
  `git ls-tree --name-only 44f53c2:.opencode/plans | grep -c VERIFICADOR-CONTEXTO` = **1** en raíz y **0** bajo
  `Archives/`. Sobre un `git archive` de esa revisión el escritor resuelve el plan **en raíz**, y sobre el árbol
  de trabajo **bajo `Archives/`** — las dos aserciones en **un solo test**
  (`test_el_escritor_resuelve_el_plan_en_raiz_y_bajo_archives_en_la_misma_prueba`), porque separarlas permitiría
  apagar una mitad sin que el verde se note. El árbol versionado se afirma primero (`05-prompt-…` presente en
  raíz y ausente bajo `Archives/` en esa revisión): si la revisión dejara de ser testigo, el test lo dice.
- **Control anti-literal**, con su defecto declarado: la primera versión del predicado buscaba solo la cadena
  `"Archives" / "<PLAN>"` y **dejo pasar** `PLAN = ARCHIVES / NOMBRE_PLAN` — un verde vacío contra la forma más
  probable de reintroducirse, medido con el mutante T3-b. Fortalecido a dos cortes (exigir el paso por
  `ruta_plan(` y prohibir la aritmética de rutas sobre `ROOT`/`ARCHIVES`/`PLANS`), el mutante cae **rojo** y
  restaurado vuelve a verde.
- **Control negativo (R2.8)**: mutado el puente para resolver la raíz a pelo —la ruta vieja, donde el plan ya no
  vive— las dos selecciones dan **17 failed + 26 errors** con `FileNotFoundError` sobre
  `plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` (la ruta del error va escrita
  sin el prefijo `.opencode/` a propósito: publicada con él, `validate_opencode_refs.py` la lee como referencia
  del árbol y da rojo — es la prosa del corpus viajando a los cinco packs, que fue como se cobró esta misma
  tanda—); restaurado,
  `sha256` idéntico (`6fd87384…`) y **109 passed**. Precisión de fidelidad: revertir al literal **actual**
  (`plans/Archives/<PLAN>`) **no** da rojo hoy, porque el plan sí está ahí; la fragilidad no es del día que se
  escribe el literal, es del próximo traslado. Crudos en
  `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T3-S31-RESOLVER-PLAN/`.
- **POST por población de la tanda**: `lesson_relevance` + `phase_briefing` = **109** recogidas (eran 106: **+2**
  del archivo nuevo de esta fila y **+1** que **no** es de esta sesión — el archivado de JEV metió un caso en el
  parametrizado `test_triage_sobre_plan_archivado_real[EVALUACION-JEV-TYPESAFE-2026-09-21]`). Suite completa:
  **3 failed, 4619 passed, 41 skipped, 4 xfailed**, exit 1, con los mismos tres rojos atribuidos el 2026-09-25 y
  **0 nuevos**; `--quick` en **13/13** con `[GUARDA]`.
- **Lo que NO cubre la cura**: el control anti-literal gobierna los **seis** archivos nombrados de estas dos
  selecciones, no un arnés futuro de un tercero; y `scripts/triage_lesson_relevance.py` conserva su propio
  `resolver_plan()` (el puente usa el del generador de packs, que es el que la orden nombraba).

**Estado de la fila: cerrada por ejecución también en su fragilidad estructural**, con el sub-punto anterior
gobernado por control y no por disciplina.

### S32 — el pack publica los bytes del workflow sin que el workflow sea fuente gobernable (nueva, 2026-09-27)

**Número libre, medido antes de tomarlo**: `git grep -l -E "\bS32\b" HEAD -- '*.md'` devuelve **0**
coincidencias (y 0 también bajo `scripts` y `tests`). Se toma aquí, no como sub-punto de otra fila, porque
su dueño es otro archivo y su disparador no coincide con el de §S19, que es el vecino más cercano por tema
(frescura de un derivado).

**Hecho medido al commitear la prosa del §2.5** (tanda `e2e44cd` → `6068f40`, la misma sesión). El pack de
cada fase publica en su bloque de lectura aparte el tamaño y los tokens estimados de
`.agents/workflows/phased_project_executor.md`, pero ese archivo **no** está en `sources[]` del pack — y no
está por contrato: `test_briefing_se_genera_por_fase` afirma que copiar el workflow al pack sería
«rebanar `.agents/` por la puerta de atrás (AC17/D3)». Con el workflow editado y ya commiteado, el
`--check` del escritor dio **verde** (mira las shas de `sources[]`, y ahí el workflow no figura) mientras
`--quick` cortó en su verificador del árbol commiteado con la firma `DIVERGE` en la línea del tamaño
(`109998 bytes → 112986`). Crudo con las dos corridas:
`evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T4-POST-POBLACION/47-hallazgo-pack-publica-bytes-del-workflow.txt`.

- **Dueño**: `scripts/build_phase_briefing.py`, en su par de funciones de lectura aparte y de verificación
  de frescura. Es edición de `scripts/`, **no** de este plan: la misma restricción de mandato de código que
  ya gobierna §S17 y §S18.
- **Disparador**: el próximo mandato que autorice literalmente editar el generador de packs. Mientras no
  suene, el único corte real es `[13/13]` del quick — que sí lo ve, pero **después** del commit que mueve
  el workflow, no en el `--check` de quien lo edita.
- **Dos salidas medidas, ninguna aplicada**: (a) que el `--check` del escritor gobierne también la lectura
  aparte (sha o al menos tamaño del workflow por fase), para que el rojo salga en el instrumento de quien
  edita y no solo en el del árbol commiteado; (b) dejar de publicar el tamaño en el pack y moverlo a la
  salida del verificador. (b) es más chica pero toca lo que AC17/D3 decidió a propósito, así que no se hace
  por omisión.
- **Alternativa descartada**: re-generar los packs en el árbol de trabajo cada vez que se mueva el
  workflow. Eso es exactamente lo que mezcló la tanda: las anotaciones datadas de §S17 y §S31, todavía sin
  commitear, habrían viajado dentro del pack. La cura del árbol se hizo clonando HEAD con la config ya
  documentada (`--no-checkout`, `core.longpaths`, `core.autocrlf=input` **dentro** del clon) y generando
  ahí — que es un procedimiento, no un instrumento, y por eso queda esta fila.
- **Lo que NO verifica nadie hoy**: que un derivado publique datos de un archivo que no declaró como
  fuente. La regla de §S19 («la frescura mira las shas de sus fuentes») no alcanza este caso porque la
  fuente no está en la lista.

**Estado de la fila: abierta, con dueño y disparador.** Se abre aquí y no en otro libro porque la población
del defecto es el escritor de packs de **este** plan y su evidencia está en el subdirectorio de esta orden.

**Antecedente que esta sesión NO leyó antes de caer, y por eso se consigna: `L-VCF-20`**, capitalizada en
§Decisiones de FASE-D de `10-analisis-post-implementacion.md` (dueño: este mismo plan) exactamente sobre
esto — «la proyección de una ruta depende de su contenido igual que un sha: `sources[]` no la gobierna, pero
la línea de carga del pack imprime su `N bytes (~M tokens)`». Su instrucción era justamente la que le faltó al
agrupamiento de esta tanda: *«si una fuente de proyección queda en otro commit, nombrar en el mensaje cuál
deja el árbol reproducible»*. La lección estaba publicada e indexada (fila `L-VCF-20` de
`.opencode/LECCIONES-INDEX.md`, 13 citas solo en el plan dueño) y no se consultó: el mandato de esta sesión
arrancaba en el estado de partida y no pedía Paso 0, y el Paso 0 no es opcional cuando el trabajo planea
commits sobre derivados. La diferencia entre aquella vez y esta es solo el instrumento que lo cazó: entonces
`[13/13]` dio rojo después del commit, y ahora también.

**Qué agrega esta fila a `L-VCF-20` y por qué no es duplicado**: la lección goberna **la conducta de quien
agrupa commits**; esta fila goberna **el hueco del instrumento** (que el `--check` del escritor no mire las
proyecciones, o que el pack deje de publicarlas), que la lección explícitamente no cierra —su «INCLUIR» pide
tratar toda métrica publicada como fuente, y eso en el guion hoy no lo hace nadie.

⟦**Sello 2026-09-28 — C2 de la orden de curas en `scripts/` (sesión 2): CURADA con la salida (a), la que
la fila dejaba medida y no aplicada.** El `--check` de `scripts/build_phase_briefing.py` contrasta ahora la
proyección publicada de bytes **y** de tokens derivados del workflow canónico contra el archivo real en
disco; la puerta es `proyecciones_de_lectura_aparte`, llamada desde `verificar` en el mismo recorrido que ya
miraba las shas. El workflow **no** entra en `sources[]` (AC17/D3 intacto: `test_briefing_se_genera_por_fase`
pasa sin cambios y sigue afirmando que el workflow es lectura aparte, no fuente) y el tamaño **no** deja de
publicarse: la salida (b) quedó rechazada porque toca lo que AC17/D3 decidió a propósito.

Dientes medidos. Con el workflow aumentado en **43** bytes y los packs **sin** regenerar, el `--check` de
los cinco packs del plan salió `EXIT=1` nombrando la proyección vencida y sus dos números
(`publicados 112986 bytes / 28246 tokens; en árbol 113049 / 28262`) — el rojo salió en el instrumento de
quien edita, que es lo que la fila pedía; al restaurar el archivo por `sha256` (idéntico) el mismo comando
volvió a `EXIT=0`. Crudo: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/17-c2-check-y-mutante.txt`.
Aparte, la batería `tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py`
(seis pruebas sobre el escritor real con un plan plantado en temporal) afirma el verde, el rojo, el
`silent drop`, que `docs/CONTRIBUTING.md` **no** entra en el contraste por bytes, y —mutante del control—
que apagando la comparación el mismo escenario vuelve a verde falso: `EXIT=1` con la cura, `EXIT=0` sin
ella, `EXIT=1` de nuevo al encenderla. La selección completa de `phase_briefing` quedó en **57 passed**
(51 preexistentes + 6) con el quick en **13/13**.

Lo que esta cura **no** cierra: la fila sigue publicando el tamaño de un archivo que no está entre sus
fuentes, y ahora se corta; pero el hueco general —«un derivado publica datos de un archivo que no declaró
como fuente», la otra mitad de `L-VCF-20`— sigue sin gobernar a los demás documentos proyectados, y por eso
el criterio 5 de la orden dejó fuera `docs/CONTRIBUTING.md`: su cifra es un reclamo de tamaño publicado como
texto, no una proyección casable contra disco desde este guion. **Estado de la fila: CERRADA por ejecución
en el hueco del instrumento (salida a), con el límite de alcance declarado arriba.**⟧

> **Procedencia**: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` · sha256 `e3300ab51712e96098063da4e594c3229c8c9dfecdb0c3f76f6646edd26d5021` · 85033 bytes copiados de 143865 del documento · HEAD `8810936` · generado `2026-10-01T17:42:08Z`

---

<!-- BEGIN BRIEFING-META
{
  "generado_por": "scripts/build_phase_briefing.py",
  "generado_por_sha": "38340ebd08f97c9f42e47de8e8753d8fb967f38a4846636caa890685b8f4149c",
  "plan": "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20",
  "fase": "C",
  "estado": "COMPLETO",
  "declaracion": "DECLARADA",
  "provenance": {
    "head": "8810936",
    "generated_at": "2026-10-01T17:42:08Z"
  },
  "no_incluye": [
    "01-plan-maestro.md — 10634 bytes fuera de lo declarado (1, 4, 2)",
    "00-lecciones-capitalizadas.md — 10426 bytes fuera de lo declarado (1, 2, 3, 4)",
    "dependencias-fases.md — 58832 bytes fuera de lo declarado (Conciliacion)"
  ],
  "lectura_aparte_obligatoria": [
    ".agents/workflows/phased_project_executor.md"
  ],
  "sources": [
    {
      "ruta": ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md",
      "sha256": "1aa85df124196041da411719e03baba1b9526392ba171516404b8d4f4862930d",
      "documento": "01-plan-maestro.md",
      "secciones": [
        "1",
        "4",
        "2"
      ],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/04-contrato-ejecucion.md",
      "sha256": "39c8b094489b3703ddd707d37fcf24bc5e907eb1db7c742fcee788bad8fe974d",
      "documento": "04-contrato-ejecucion.md",
      "secciones": [],
      "en_pack": true
    },
    {
      "ruta": ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md",
      "sha256": "445c34c4c9a3863bd04077a2e2e1260718dcb5373f7f4fc35b7391662c638de1",
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
      "ruta": ".opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md",
      "sha256": "e3300ab51712e96098063da4e594c3229c8c9dfecdb0c3f76f6646edd26d5021",
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
