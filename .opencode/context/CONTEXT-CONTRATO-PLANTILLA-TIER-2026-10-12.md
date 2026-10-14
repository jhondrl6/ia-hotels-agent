# CONTEXT — Contrato entre la plantilla comercial, el `evidence_tier` y el techo del veredicto

**Fecha de la evaluación:** 2026-10-12. **Sesión:** documentación del hallazgo y definición de alcance, sin
implementación.
**Origen:** FASE-E2E del plan `CURA-COSTURA-TRIBUNAL-2026-10-11` — la corrida única de `v4complete` para Hotel Don
Alfonso (`https://www.donalfonsohotel.com/`), ejecutada el 2026-10-12 con EXIT 0.
**Pregunta del operador:** si el acceso a GA4+GSC es discrecional del hotel —y por tanto algo que el negocio no
controla—, ¿significa que ningún hotel puede ser tier A y, en consecuencia, que nunca hay entregable? Y si es
pertinente abrir un contexto nuevo como insumo de un plan.
**Decisión del operador (2026-10-12):** alcance **A + C** (contrato plantilla↔tier y nombre del veredicto); **B**
(ruta a tier A por evidencia propia) **fuera**, con su motivo medido en §4. Nombre aprobado:
`CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md`.

> **Qué es este archivo.** Una evaluación con evidencia anclada a símbolos del árbol de trabajo, **no un plan y no una
> decisión de diseño**. No se escribió código, no se ejecutó `v4complete` de nuevo y no se hizo ninguna llamada de
> inferencia. Árbol medido al escribir: HEAD `bce67bc` con **21 rutas sin commitear** pertenecientes al cierre de
> FASE-E2E del plan de origen; las cifras de código que aparecen aquí son del **árbol de trabajo**, no de un commit, y
> la sesión nueva debe re-medirlas antes de planificar (§6).
>
> **No autodeclara lección durable.** La entrada a la población gobernada por
> `scripts/verify_qmind_context_freshness.py` depende de tres grafías concretas al inicio de línea —las que el
> verificador lista en `MARCA_DURABLE`: «Lección de forma», «Lección durable» y «Lecciones capitalizadas»—, no del
> nombre del archivo. Este documento no escribe ninguna de las tres al inicio de línea, así que el verificador lo
> publica como `[EXCLUIDO]` con su razón: la política del write-back es por aporte declarado, no por existencia. Si
> algún día se le agrega una lección durable con esas grafías, pasa a estar gobernado y exige su fuente en QMind con
> sha coincidente.
>
> **No se lo nombra desde documentos de plan.** La segunda vía por la que un contexto pasa a estar gobernado sin
> publicación es ser citado desde `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` o
> `dependencias-fases.md` de un plan **archivado**. Por eso esta ruta no se cita desde los documentos de
> `CURA-COSTURA-TRIBUNAL-2026-10-11`, y el plan que nazca de aquí debe decidir conscientemente si lo referencia antes
> de archivarse.
>
> **No acuña IDs nuevos.** Los ítems se nombran **A**, **B** y **C** en prosa. Las deudas y lecciones que sí se citan
> ya están definidas en el plan de origen (`S-CST-1`, `L-CST-6`, `L-CST-7`) y viven en su
> `10-analisis-post-implementacion.md`; este archivo no crea familias nuevas en el índice.

---

## 0. Veredicto en una línea

**El techo de tier A es real y está fuera del control del negocio, pero no es lo que impide entregar**: lo que impide
entregar es que la plantilla comercial promete en registro de tier A —«Protección total», «Transparencia total»— y el
escaneo determinista de sobre-presentación se arma con cualquier tier que no sea A. Con la plantilla corregida, un
hotel B+ recibe su paquete con veredicto condicional, que **sí publica**.

---

## 1. El hecho medido: la ruta por defecto de producción no puede entregar

En la corrida única del 2026-10-12:

- `evidence_tier` = **`B+`**, publicado por el motor financiero en
  `financial_scenarios_20261012_165654.json → breakdown.evidence_tier`, y resuelto para el tribunal por el símbolo
  único `resolve_evidence_tier()` (`modules/quality_gates/tribunal/evidence_tier.py`, nacido en FASE-C del plan de
  origen: precedencia escenarios → MANIFEST → fallback `"C"`).
- Bot 4 (`honesty_reviewer.py`) emitió **2 CRITICAL** `OVER_PRESENTATION` sobre `02_PROPUESTA_COMERCIAL.md`, en
  «## 🛡️ GARANTÍAS: Protección total para usted» y «### 5. Transparencia total», con `evidence_tier_declared: "B+"`.
- Fila 2 de la matriz de veredicto (`_compute_verdict` en `judge.py`) → **`BLOQUEADO`**; `blocks_delivery_zip()` True;
  `package_evidence` = `{suppressed: true, member_count: 56, sha256 dc00cdb9…}`; la cuarentena
  `donalfonsohotel_20261012.zip.tmp` fue borrada por `DeliveryPackager.suppress()`.
- El veredicto **previo** a la revisión fue `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, que **no** está en
  `BLOCKING_VERDICTS = {BLOQUEADO, DEVOLVER-CORRECCIONES}`: sin los 2 CRITICAL, esa misma corrida habría publicado el
  ZIP por la rama `else` de `main.py`, que llama a `packager.publish()` y registra la evidencia del paquete entregado.

Consecuencia sistémica: **mientras la plantilla v6 prometa totalidad, todo hotel que no sea tier A queda bloqueado de
entrega**, y tier A exige acceso a analytics del hotel. No es un fallo del tribunal: está haciendo exactamente lo que
se le pidió (no dejar salir un paquete que afirma «total» con evidencia B+). El defecto es de **contrato entre tres
piezas**, y solo una de ellas (la plantilla) está en control del negocio.

---

## 2. Las tres piezas del mecanismo, con su comando

| Pieza | Símbolo y archivo | Lo que dice |
|---|---|---|
| El tier | `_determine_evidence_tier()` en `modules/financial_engine/scenario_calculator.py` | Devuelve A **solo** si `ga4_enabled and gsc_enabled and has_verified_data`. Su docstring: «FASE-1: Sin GA4+GSC conectados, NUNCA devuelve A. Introduce B_PLUS para onboarding verificado sin analytics». Los flags no son configuración del repo: `ga4_enabled` sale de `analytics_data.get("use_ga4")` (`v4_diagnostic_generator.py`) y `gsc_enabled` se pone en `modules/onboarding/add_gsc_step.py` — **los dos dependen de que el hotel abra acceso** |
| El check | `honesty_reviewer.py` | El escaneo de sobre-presentación **se apaga entero** con tier A (`if evidence_tier == "A": return` antes de emitir el finding). Con cualquier otro tier queda armado, y dispara sobre los grupos de cuantificadores absolutos y de lenguaje de verificación, con el filtro estructural de FASE-B (fuera de fila de tabla y de línea con monto **solo** para el grupo de cuantificadores) |
| El techo | `FIRST_FLOOR_TIERS = {"B", "B+", "C"}` y `_compute_verdict()` en `judge.py` | Con tier no-A, la fila 6 («primer piso aplicado → condicional») topa el mejor veredicto posible en `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; la fila 7 (aprobado) exige tier A. **El condicional publica** — no está en `BLOCKING_VERDICTS` |

Mediciones de apoyo, reproducibles:

- Superficie de prosa absoluta en las plantillas:
  `grep -ric "total|absoluto|definitivo|100%|garantiz" modules/commercial_documents/templates/*.md` →
  `propuesta_v6_template.md` **7**, `diagnostico_v6_template.md` **5**, `propuesta_v4_template.md` 2,
  `diagnostico_v4_template.md` 0. De las 7 de la propuesta v6, **2** dispararon en esta corrida.
- Productor único del render de la propuesta: `v4_proposal_generator.py` (`self.template_path = template_dir /
  "propuesta_v6_template.md"`). Ese generador **ya tiene el tier en la mano**: el stdout de la corrida imprimió
  `Evidence tier: B+, disclaimer: Datos operativos verificados de su hotel…`.
- Población del warehouse: `data/hotel_observations/observations.json` tiene **6 observaciones, todas
  `epistemic_status: verified`, y ninguna con clave de analytics** (`ga4`/`gsc`/`search_console` no aparecen entre sus
  20 claves posibles). Es decir: 0 de 6 son candidatas a tier A. **El warehouse no es la población comercial** — ver §6.
- Ocurrencias vivas del literal del veredicto condicional: **8** (la constante `VERDICT_CONDITIONAL` en `judge.py`, la
  etiqueta de `acta_writer.py`, y 6 en `tests/`: `test_ac_g4_g5_multi_hotel_matrix.py` ×2,
  `test_fase_0_ac20_evidencia_veredicto.py`, `tribunal/test_judge.py`, `tribunal/test_acta_version_desde_yaml.py`,
  `tribunal/test_acta_serialization.py`). Las otras 5 que devuelve el grep están en `temp/release-2026-10-07/`, scratch
  gitignorado y fuera de alcance del verificador de cableado.

---

## 3. Alcance aprobado: A y C

### A — Contrato plantilla↔tier (el núcleo)

La decisión de diseño que el plan debe tomar, y que este contexto **no** toma:

1. **Render condicionado al tier**: las frases de totalidad se emiten solo con tier A; con tier no-A se emite su
   variante honesta. Ventaja medida: el verde de Bot 4 pasa a ser **estructural** (el texto no puede contener lo que el
   check castiga), no depende de que alguien recuerde podar palabras. Coste: tocar el render en
   `v4_proposal_generator.py` y decidir la variante de cada una de las 7 líneas.
2. **Re-copy permanente**: reescribir la plantilla para que no afirme totalidad en ningún tier. Ventaja: un solo texto.
   Coste: es una decisión de **copy comercial** que necesita aprobación del dueño (`comercial`, que es el dueño que
   nombran las dos acciones correctivas de esta corrida), y deja el verde dependiente de que nadie vuelva a escribir
   «total».

En ambos casos el plan necesita: (i) el inventario exacto de las líneas candidatas con su texto, (ii) un diente que
demuestre que la propuesta renderizada con tier B+ **no** produce `OVER_PRESENTATION` y que con tier A el check sigue
apagado por diseño (no por accidente), y (iii) decidir qué pasa con `diagnostico_v6_template.md` (5 candidatas) — Bot 4
escanea la propuesta, pero el diagnóstico viaja en el mismo paquete y su texto también llega al hotel.

**Medición nueva (2026-10-14, FASE-VERIFY).** Sobre la propuesta renderizada de la corrida, el barrido del revisor
(patrón del módulo y bandera de su llamada) da **10 literales** del grupo de cuantificadores, **6** descartados por el
filtro estructural —fila de tabla o línea con monto— y **2 emitidos**: exactamente las dos líneas de prosa de garantía
que §0 nombra. Ese `10 → 6 → 2` es el objetivo mínimo del diente de (ii): la propuesta renderizada con tier B+ debe
emitir **0**, y la resta es la prueba de que no se logró apagando el escáner.

### C — Nombre del veredicto condicional

`APROBADO-CONDICIONAL-PENDING-ONBOARDING` describe mal el caso que gobierna hoy: para Don Alfonso el onboarding **sí**
llegó (4 campos confirmados, Tier A de fuente, `source: contacto_directo`) y lo que falta es analytics; y esa falta no
es «pendiente» sino **estructural** mientras el hotel no dé acceso. Un estado permanente con nombre de estado
transitorio es la misma familia que este repo cura desde hace meses (texto que niega o disfraza el mecanismo).
Superficie medida: 8 ocurrencias vivas, 6 de ellas en tests. La cura incluye la etiqueta humana de `acta_writer.py` y
debe declarar si el nombre nuevo distingue «pendiente de onboarding» de «techo por ausencia de analytics» — son dos
causas con dos remedios distintos.

---

## 4. Fuera de alcance: B (ruta a tier A por evidencia propia), con su motivo medido

**B no entra, y el motivo no es coste.** El check de sobre-presentación se apaga entero con tier A
(`if evidence_tier == "A": return`), así que «hacer A alcanzable sin analytics» es, en la práctica, **buscar el
interruptor que desactiva el control de honestidad**. Es la familia de defecto que el plan de origen existe para curar:
subir una etiqueta para que un control no dispare. Además el blast radius de B es mayor que el de A+C: el tier alimenta
`pricing_compliance`, el primer piso del veredicto, el disclaimer de la propuesta y lo que el paquete promete.

Lo que sí corresponde, y es barato porque no toca código: **medir antes de decidir**, con dueño el Operador.

- ¿Cuántos hoteles de la cartera comercial real tienen GA4 y/o GSC conectados? (El warehouse dice 0 de 6, pero el
  warehouse no es la cartera.)
- ¿Qué pierde comercialmente una propuesta en tier B+? ¿El `operational_floor` de `pricing_compliance` y el `pain_ratio`
  de esta corrida (0.1574 con WARNING) son aceptables como estado habitual de entrega?
- ¿Es viable vivir con `APROBADO-CONDICIONAL` como mejor resultado posible? Si la respuesta es sí, B no existe y el
  ítem C (nombre honesto) es toda la cura. Si es no, B se convierte en un plan propio de **taxonomía de evidencia**, con
  su decisión de qué cuenta como A sin analytics y qué cambia en el disclaimer.

---

## 5. Restricción de secuencia con `CURA-COSTURA-TRIBUNAL-2026-10-11`

El ítem C toca `modules/quality_gates/tribunal/judge.py` y `acta_writer.py`, y el seguimiento abierto del plan de
origen —`P6.5` sigue con `NOT_EVALUABLE` y `source_artifact: null` en el acta que **sí** nombra a Bot 4 como el que
bloqueó (`L-CST-7`)— se cura en ese mismo par de archivos. Dos planes sobre los mismos archivos en paralelo es el
conflicto que `dependencias-fases.md` existe para evitar.

**Recomendación:** este contexto puede versionarse ya (es documental), pero el plan que nazca de él **no arranca antes
de que CURA cierre** (FASE-VERIFY + FASE-RELEASE-4.81.0), o arranca con el conflicto de archivos declarado y el orden
fijado por el Operador.

**Actualización (2026-10-14).** FASE-VERIFY quedó ejecutada (19/19 AC certificadas, corte: listo para revisión, sin
commit; árbol medido con tip `82ec9a4` y 10 rutas sucias de la propia fase). El portón baja a
**FASE-RELEASE-4.81.0**, que es la única fase pendiente de `CURA-COSTURA-TRIBUNAL-2026-10-11`.

**Insumo para el plan: `P6.5` con su mecanismo medido (2026-10-14).** Para que la cláusula vecina entre al plan como
decisión y no como nota, queda definida así:

- **Mecanismo.** La fila `P6.5` está **hardcodeada** en el mapa de cláusulas de `judge.py`: status
  `NOT_EVALUABLE`, sin `source_artifact`, texto «Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a»; su etiqueta
  humana espejo vive en `acta_writer` («Honestidad Comercial (NL) — reservada Bot 4»); y `T1_CERTIFIABLE_CLAUSES` la
  excluye con su motivo escrito, igual que a `P6.2` — el veredicto máximo exige que las cláusulas de esa tupla estén en
  `PASS`, así que la exclusión es también una decisión de veredicto.
- **Contradicción medida, forma completa.** En el acta del run único el `verdict` es `BLOQUEADO`, con 2 CRITICAL y
  **las 2 acciones correctivas originadas en el revisor cuya fila dice "Reservada"** (report_path a
  `revision_honestidad.json`, `clause: P6.5`). No es solo texto vencido: la cláusula declarada no evaluable es la
  fuente del bloqueo.
- **Dos direcciones de cura, con coste distinto.** (a) Texto + `source_artifact` con el productor real: la familia de
  la cura de `P6.2`, barata y sin tocar gates. (b) Hacer la fila **derivada del report del revisor** en vez de literal
  — exige autorización para tocar `T1_CERTIFIABLE_CLAUSES`, ACs propias, y decidir si un insumo no-OK puede dejar la
  cláusula en `NOT_EVALUABLE` mientras el bloqueo de ese mismo revisor sigue vigente. Viajan pegadas a la decisión ya
  diferida «¿`P6.2` pasa a cláusula evaluable?»: son la misma familia.
- **Frontera de alcance.** `S-CST-1` (el gate blocking `hard_contradictions` no puede fallar en producción) queda
  **fuera** de este contexto: su superficie es `main.py`, `publication_gates.py` y `Conflict`, no el par
  `judge.py`/`acta_writer.py`. Su enunciado completo vive en el maestro §5 y en la deuda del
  `10-analisis-post-implementacion.md` del plan de origen; el plan que nazca de aquí no debe absorberlo sin una
  decisión propia del Operador.

---

## 6. Lo que la sesión nueva debe medir antes de planificar

1. **Dónde se fija `use_ga4`** realmente: ¿config por propiedad, credencial del cliente, o `AnalyticsStatus`? Sin eso
   no se puede decir qué se necesita para que un hotel sea candidato a A.
2. **Si `add_gsc_step` puede satisfacerse sin acceso del hotel** (por ejemplo con datos públicos): hoy se asume que no.
3. **El inventario exacto de las 7 líneas candidatas** de `propuesta_v6_template.md` y las 5 de `diagnostico_v6`,
   con su texto y con el comando que las produjo — no las líneas numeradas de este documento, que se desfasan.
4. **Qué lee Bot 4 del paquete**: la lista de artefactos que entran al ZIP (`_collect_files` de
   `delivery_packager.py`, con `_is_excluded_from_zip` y el filtro de `v4_audit` por frescura) — 56 miembros frente a los
   67 archivos que quedaron en disco en esta corrida. Si el diagnóstico viaja, su prosa también se escanea.
5. **Si existe algún test que afirme la prosa actual** de la plantilla (un verde que se rompa al reescribirla): medir
   antes de tocar, no después.
6. **El árbol**: re-medir HEAD y rutas sucias. Al escribir esto, FASE-E2E estaba cerrada **sin commit**; si la tanda ya
   se publicó, las cifras de §2 siguen siendo del código, no del commit.

**Aviso de instrumento (2026-10-14, FASE-VERIFY).** «Con el comando que las produjo» no basta si se copia el patrón:
en el revisor las **banderas viven en la llamada** (`re.IGNORECASE`), no en el patrón. Medido al certificar: sin la
bandera, el mismo barrido dio **8** literales donde el código ve **10** y un **falso 0** en el grupo de lenguaje del
documento de 2026-10-07 (su coincidencia, «Verificado», va en mayúscula). El inventario de §6.3 se mide **invocando la
función del revisor** (`coincidencias_lenguaje_de_verificacion`), no los patrones sueltos, y el crudo debe publicar la
pasada equivocada con su contraste.

---

## 7. Lo que no se hizo en esta sesión, declarado

- No se escribió código, no se editó ninguna plantilla, no se cambió ningún veredicto ni se re-corrió `v4complete`. La
  corrida única del plan de origen **ya está gastada** (1/1) y no se repitió para probar nada de lo anterior.
- No se creó el plan ni sus prompts: este archivo es insumo del Paso 0 de la sesión que lo lea.
- No se registró nada en los documentos del plan de origen (para no convertir este contexto en gobernado por la segunda
  vía, y porque el maestro de CURA declara «fuera de alcance» todo lo que no sean sus 6 defectos + 9 nuevos).
- **No se barren** los cuatro hallazgos que ya tienen dueño en `10-analisis-post-implementacion.md` §Seguimientos de
  CURA: `S-CST-1` (el gate blocking `hard_contradictions` no puede fallar en producción), `P6.5` que niega al revisor
  que corrió (`L-CST-7`), la fila nueva de AC19 no ejercitada en flujo real (la extracción salió `OK_CON_PROMESAS`), y
  la celda «(Verificado)» que no salió CRITICAL donde la medición de FASE-B anticipaba que saldría. Pertenecen a
  FASE-VERIFY o a su tanda propia.

**Actualización (2026-10-14, FASE-VERIFY ejecutada).** El **cuarto ítem quedó cerrado sin hallazgo**: la propuesta del
run contiene **0** literales del grupo de lenguaje de verificación —re-medido con el patrón del módulo y la bandera de
su llamada— y la predicción de FASE-B estaba bien medida sobre **otro** documento, la propuesta del 2026-10-07, que sí
contiene «Verificado». No es detección perdida ni filtro estructural: es el dato. Los ítems 1, 2 y 3 siguen abiertos:
los dos primeros con dueño Operador, y la fila de AC19 re-confirmada como límite declarado —ejercitarla en producción
exigiría otra inferencia pagada, y su prueba sigue siendo el par rojo/verde de FASE-C2—. Evidencia de la certificación
(19/19 AC legibles, 0 fallos) en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-VERIFY/`.

---

## 8. Insumos y precedentes

- Evidencia de la corrida (todo bajo `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`): `pre-vuelo.md` y
  `preflight.json` (13/13 requisitos favorables), `nota-de-cierre.md`, `stdout-corrida.txt` y su copia redactada,
  `inventario_post_corrida.json` (67 archivos, `faltantes: []`), `corrida/` con 26 artefactos (acta JSON y MD, gate
  report, los cuatro `revision_*.json`, los dos documentos comerciales, `v4_complete_report.json`) y `recibos/` con los
  dos recibos de extracción (`proveedor_servido: deepseek`, pedido `deepseek-chat` / firmado `deepseek-flash`, usage
  5250/3190/8440, estado `OK_CON_PROMESAS` con 42 promesas).
- Plan de origen: `.opencode/plans/CURA-COSTURA-TRIBUNAL-2026-10-11/` — su maestro (§1 ACs, §4 restricciones y
  «fuera de alcance»), `00-lecciones-capitalizadas.md` y `10-analisis-post-implementacion.md` (§Lecciones nuevas
  `L-CST-6` y `L-CST-7`, §Seguimientos).
- Precedente de formato y de autodeclaración: `.opencode/context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md`, que
  originó el plan de origen y documenta el mismo mecanismo de gobierno (`MARCA_DURABLE`, IDs del índice, segunda vía por
  cita desde documentos de plan archivado).
- Flujo canónico para convertir esto en plan: `.agents/workflows/phased_project_executor.md` (Paso 0 = lecciones
  capitalizadas **antes** del maestro) y `docs/CONTRIBUTING.md`.
