# Plan maestro — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Objetivo**: dar a los dos artefactos de gobierno del repo (el workflow canónico y sus
templates) el mismo trato que `validate_plan_citations.py` da a las citas de línea — **un
verificador que compara la aserción contra su fuente dinámica** — y abrir, sobre el índice
ya generado, la capa de **pertinencia** que el verificador de capitalización declara
expresamente fuera de alcance.

**Este plan no es parte de la cadena `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.** No consume su
contador de corrida, no toca sus ACs, no ejecuta `v4complete`. Se concibe como plan hermano de
`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, que cerró la forma; este cierra la mitad que
aquel no pudo cerrar.

---

## 1. Medición que justifica el plan (no suposición)

Cuatro aserciones sobre cuántos checks corren están **hoy** vencidas respecto del código que
las ejecuta. Medido en esta sesión con `grep -oE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py`
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

## 2. Matriz de decisión

| Decisión | Resuelto | Base |
|---|---|---|
| **¿Se toca `run_all_validations.py` o el hook para añadir checks?** | **NO.** Ninguna fase de este plan altera el número de checks | `REFACTOR-WHATSAPP` está en vuelo y pinea la cifra. **Sitios medidos el 2026-09-20** (no es el prompt de FASE-C, como decía la primera versión de esta fila): el bloque de arranque de FASE-B de su `README.md` («El quick son 11 checks.»), `06-checklist-implementacion.md` («el modo rápido pasó de 10 a **11 checks** y da 11/11»), `09-documentacion-post-proyecto.md` y `10-analisis-post-implementacion.md`. Promover algo al set de 11 invalida la medición de fases ajenas. Y **`run_all_validations.py` no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance (ver D10). Queda como deuda con disparador (§Deuda) |
| **¿Se edita `.agents/` para corregir A1–A4 a mano?** | **NO.** El verificador **reporta**, no reescribe | Quien corrige la frase a mano produce la fosilización siguiente (Q6: la cura es un writer o un verificador, no el edit). Precedente: `validate_plan_citations.py` reporta sin reescribir, decisión DA-HF3 |
| **¿Arquitectura de los nuevos verificadores?** | Script **standalone** en `scripts/`, invocable suelto; el set de 11 queda intacto | Es el patrón de la casa: `[9/11]` y `[10/11]` son wrappers de 4 líneas que delegan a `validate_plan_citations.py` y `validate_lesson_capitalization.py` |
| **¿Se construye un cliente HTTP propio del proveedor?** | **NO.** Costura neutra `decision_client.py` que resuelve al proveedor configurado; el SDK oficial o el adapter quedan detrás | **Origen declarado del dato:** el operador reportó el 2026-09-20 que el SDK del proveedor rompió compatibilidad dos veces en sus primeros nueve días de público (redefinió los criterios de una primitiva; migró de serializador). **No verificable desde este repo** — no hay registro ni changelog del SDK versionado aquí—, así que se cita como dato externo y la decisión no depende de él: nombrar la costura, no el proveedor, es la cura estructural tanto si el historial es de dos rupturas como de ninguna, y así añadir un proveedor nuevo después es **un** archivo |
| **¿El triaje de pertinencia puede filtrar?** | **NO. Solo propone.** La fila ya anclada en §2 nunca desaparece | El riesgo de un filtro que descarta en silencio una premisa carga-estructura ya cobró un plan: `VACUOUS_RECALL` obligó a crear FASE-0 y AC20 en la revisión 2 de `REFACTOR-WHATSAPP` |
| **¿Se activa FASE-VERIFY?** | **NO.** Etapas = 3 (Preparación → Implementación → RELEASE) | §4.6 exige **los tres** criterios. Se cumplen «≥3 fases de implementación» y «ACs que cruzan fases»; **no** existe fase con ejecución E2E (`v4complete`/`v4audit` prohibidos por este plan). Criterio 2 cae → no aplica |
| **¿Entra Jev en este plan?** | **NO, por decisión del operador del 2026-09-20.** El acceso existe y la API está habilitada; posponerlo es distinto de no poder usarlo | FASE-B deja la costura lista y AC9 verifica que **añadir** un segundo proveedor sea un cambio de un archivo. La activación queda como deuda **D7** con su disparador |
| **¿Se compara proveedores dentro de este plan?** | **NO.** Con un único proveedor configurable no hay elección que medir | Reformular AC9 era obligatorio: un AC que exige medir una comparación inexistente se cierra declarando `NO-EJERCITADO` y certifica humo. Es la familia de verde vacuo que AC20 cerró en el otro plan |
| **¿Dónde vive el pack generado por FASE-D?** | En `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, **dentro del plan** | `.agents/workflows/` tiene contadores de skills con `glob("*.md")` no recursivo: un `.md` ahí altera lo que reporta `validate_agent_ecosystem.py` y exige seguimiento en su `README.md`. Y AC17 prohíbe escribir en `.agents/` |

## 3. Alcance y no-alcance

**Dentro**: cuatro scripts nuevos en `scripts/` (`validate_governance_numbers.py`,
`decision_client.py`, `triage_lesson_relevance.py`, `build_phase_briefing.py`), sus tests en
`tests/`, su evidencia en `evidence/`, el directorio generado `briefing/` dentro de este plan, y las
restricciones que impiden que toquen lo que no deben.

**Fuera, con dueño registrado** (§6): editar `.agents/` para corregir A1–A4; promover cualquier
check al set de 11 o al hook de 7; **el rebanado del workflow canónico por fase** (D3 — distinto del
pack de FASE-D: el pack no sustituye ninguna lectura, solo la unifica); el **lint de contradicciones
semánticas** entre prompts de fase y estado del plan (D6, disparado por el resultado del triaje de
FASE-C); **activar el proveedor de decisiones** ya habilitado (D7); y el write-back de este plan a
QMind.

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
| AC11 | Índice ausente o vencido no se lee como «sin candidatos» | ídem → `index_status` |
| AC12 | Umbral de confianza publicado con valor, base y acción por debajo | ídem → `threshold` |
| AC13 | ≥1 test contra corpus real archivado, con skip visible y declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/r26.txt` |
| AC14 | Mutation check sobre el guard real de no-filtrado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/` |
| AC15 | Denominador del triaje con términos usados, ceros incluidos y familias no juzgadas, **más la aceptabilidad que dispara D6** | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/coverage.json` |
| AC16 | El quick sigue en 11 checks y el hook en 7, en **todo** el plan | los cuatro `baseline-pre-post.md`, delta 0 |
| AC17 | `.agents/` intocado en escritura y límites de cobertura declarados | `coverage.json` → `families_not_covered[]` + `git status` sobre `.agents/` |
| AC18 | Capitalización, citas e índice verdes sobre los artefactos de este plan | salida de los tres verificadores, mismo commit |
| AC19 | `build_phase_briefing.py` emite un pack por fase, **sin tocar `.agents/`**, declarando `no_incluye[]` y la lectura aparte obligatoria | `…/briefing/FASE-X.md` + `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/informe.json` → `packs[]` |
| AC20 | El delta de carga de lectura se mide con el **mismo comando** antes y después, bytes exactos y tokens con el divisor declarado | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` → `before`, `after`, `method` + par pre/post con la resta |
| AC21 | Cada pack declara HEAD, fecha y sha por fuente; `--check` lo vence contra el árbol | ídem → `provenance` ; prueba re-editando una fuente y re-midiendo en disco |
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
- **AC11** — El suelo determinista es `lecciones_index.json`. Si falta o está vencido, el script
  **no** emite «no hay candidatos»: emite `AUSENTE` o `VENCIDO` con la ruta buscada y el comando
  de regeneración (L-PF6, L-PF10). Artefacto: clave `index_status` + tres tests por estado.
  **Fuente de la decisión (Knowledge Center, `L-V2.2` de
  `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`):** «un verificador no debe apoyar su conclusión en
  el artefacto que genera otro gate» — ese plan lo capitalizó porque leer el JSON era lo obvio y el
  JSON lo produce `[6/7]`; la cura que implementó fue **calcular el índice en memoria** con
  `build_lesson_index.build()` (0,30 s medidos) y fallar con nombre propio si el cálculo cae.
  FASE-C elige entre las dos rutas **y deja la elección escrita con su costo**: (a) correr
  `build_lesson_index.build()` en memoria — un solo lector, sin verde heredado; o (b) leer el JSON
  tras ejecutar él mismo la comprobación de frescura, en cuyo caso `VENCIDO` es un estado que
  produce su propio check y no un `--check` ajeno. Lo prohibido es la tercera vía: leer el JSON
  confiando en que otro paso lo regeneró.
- **AC12** — El umbral de confianza se publica **con su valor y su efecto**, y los candidatos se
  separan en `propuesto` y `a-revisar-humano`. Ningún camino del código auto-filtra una lección.
  Artefacto: clave `threshold` con `value`, `basis`, `action_below`.
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
- **AC21** — Cada pack declara `provenance` con `head`, `generated_at` y `sha256` por fuente;
  `--check` falla contra un árbol modificado. La prueba se hace **editando una fuente y re-midiendo
  en disco**, no leyendo el objeto en memoria (L-V2.3, R2.4).
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
- **AC18** — Los artefactos del plan pasan, en el mismo commit que los escribe,
  `validate_lesson_capitalization.py` (C1–C8), `validate_plan_citations.py` y
  `build_lesson_index.py --check`. Ningún AC ni prompt cita `archivo:número` (R2.2).

## 5. Única corrida y límites

Este plan **no ejecuta la pipeline**: no corre `v4complete`, no corre `v4audit`, no genera
`output/`, no publica ZIP, no consume el contador `v4complete: 0/1` de
`REFACTOR-WHATSAPP-ENTREGA-2026-09-18`. Su evidencia es estática (informes JSON de los
verificadores) y de tests. Ningún AC se certifica `SUPERADO EN E2E`.

## 6. Deuda con dueño y disparador

Los IDs coinciden con la tabla de `dependencias-fases.md`. Ninguna fila se cierra reinterpretando
en silencio una restricción del plan.

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o retirar las aserciones A1–A4 en `.agents/` (eliminar la aserción del documento y dejar que el verificador la imprima es la opción que no se desfasa) | Este plan, FASE-RELEASE, **solo con instrucción literal del operador**: `.agents/` es configuración central | Verificador verde y decisión escrita sobre la forma de la corrección |
| D2 | Promover `validate_governance_numbers.py` a un check adicional del `--quick`, renumerando de 11 a 12 y midiendo quién afirma el número (L-V2.3) | Plan propio, posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases en vuelo que pineen «11 checks» |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura por sesión: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B de `REFACTOR-WHATSAPP`; la cifra de concepción era 254.010 y venció el mismo día — ver A7) | Plan propio, posterior | Mismo disparador; exige medir qué parte del documento consume cada fase. **Distinto de FASE-D**: el pack unifica lecturas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** entre los prompts de fase y el estado real del plan (`validate_plan_semantics.py`): fila que sigue llamando PENDIENTE a una fase cerrada, dos ACs incompatibles, instrucción de fase que choca con una regla del executor. Con falsos positivos medidos contra los 27 archivados | Plan propio, posterior — **mismo directorio si el disparador se cumple dentro de la vigencia de este plan** | **Condicionado al resultado de FASE-C**: que el triaje de pertinencia entregue candidatos que el Paso 0 no ancló, con la aceptabilidad medida (propuestos que resultaron pertinentes sobre el total propuestos) publicada en el informe. Si el triaje sale inaceptable, D6 **no** se activa: no se apila un segundo consumidor sobre una base que no funcionó |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev): añadirlo como segundo proveedor detrás de `decision_client.py`, correr la comparación que AC9 ya no exige, y restituir «elegir midiendo» como AC | Plan propio posterior; el acceso existe desde 2026-09-20 por decisión del operador | Que AC9 haya cerrado en verde la costura y que algún consumidor real lo pida — el candidato natural es D6, porque es el único trabajo del lote genuinamente semántico |
| D8 | Re-ejecutar la consulta Q7 de QMind que esta concepción no pudo correr. **Premisa vencida y corregida el 2026-09-20: el CLI `qmind` v3.3.0 SÍ está disponible y autenticado** (cuatro `retrieve` reales contra el notebook, con hits de `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `TRIBUNAL-OFFLINE-2026-09-09`). **Y el comando registrado en `00-lecciones-capitalizadas.md` está mal:** `--nb iah-cli-lecciones` devuelve `error: Bad request`; `--nb` exige el **ID** `01a04d98-b7bd-778c-8441-26fdc7e35f45` (medido con las dos formas) | Este plan, sesión previa a FASE-RELEASE — o **antes**, ya es ejecutable | Fallback re-escrito en `00-lecciones-capitalizadas.md` §4 con el comando que funciona |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice obligatoria después |
| **D10** | **Re-leer la interfaz del write-back antes del cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al `FASE-RELEASE` de `REFACTOR-WHATSAPP`) declara dentro de su alcance `scripts/validate_qmind_writeback.py` **y su connection en `scripts/run_all_validations.py`**, y piensa añadir `--title`/`--file` y fin de la degradación a PASS. El orden de cierre de este plan (§`04-contrato-ejecucion.md`) invoca ese script | Este plan, FASE-RELEASE | Que al llegar el RELEASE se ejecute `validate_qmind_writeback.py --help` contra el árbol vigente y el orden se re-escriba si la interfaz cambió. **No** es dependencia de ejecución: este plan puede correr antes o después, y AC16 (delta 0) sigue protegiendo el conteo |

## 7. Nota final

La premisa del plan es incómoda de propósito: **el mecanismo que detecta aserciones vencidas en
los documentos de gobierno no existía, y el texto que lo pide estaba escrito en el mismo
documento cuyos números estaban vencidos.** Eso es L-R.1 aplicado al workflow, no a un plan.

Y la segunda premisa, también incómoda: la capa fría del Paso 0 ya se consulta con grep, y un
grep devolvió 0 sobre un corpus que sí contiene lo buscado con otras palabras. Antes de llamar a
eso «cobertura del verificador», hay que publicarlo como límite medido (AC15).

**Y una tercera, que la auditoría del 2026-09-20 añadió sobre este propio documento.** El plan se
justifica porque cuatro aserciones del workflow están vencidas; la auditoría encontró que **la quinta
aserción vencida era la del propio maestro §1** — A3 publicaba como observado `[12/15]`, que es la
etiqueta del check de dependencias, no la del write-back (`[15/15]`). No fue falta de lectura: fue leer
la **lista** de etiquetas sin emparejar cada una con el `def _check_*` que la imprime. Por eso la
medición A8 y la regla de población de AC1 existen como están escritas, y por eso el arranque de
FASE-A ordena emparejar antes de afirmar. Que un plan sobre detección de cifras vencidas publicara una
cifra vencida sobre sí mismo no debilita su premisa: **la confirma**, y es el caso de prueba más barato
que este verificador va a tener nunca.
