# CONTEXT — Evaluación: dónde encajaría un modelo de decisiones tipadas (Jev) en iah-cli, y qué curar antes

**Fecha de la evaluación:** 2026-10-10. **Sesión:** análisis, sin implementación.
**Pregunta del operador:** si el piloto `EVALUACION-JEV-TYPESAFE-2026-09-21` podría integrarse al
repositorio —en particular dentro de una ejecución de `v4complete`—, dónde sería más útil, y si los
documentos externos `jev-llm-field-guide.md` y `SKILL.md` lo fortalecerían.

> **Qué es este archivo.** Una evaluación de costo/beneficio con evidencia anclada a `archivo:línea`, no
> un plan y no una decisión de adopción. No se escribió código, no se ejecutó `v4complete`, no se hizo
> ninguna llamada de inferencia y no se consumió saldo de ningún proveedor. Todo lo que aquí se afirma
> como defecto se re-midió en el árbol de trabajo en `0c29d23`.
>
> **No autodeclara lección durable.** Medido en el código del verificador
> (`scripts/verify_qmind_context_freshness.py:106-110` y `:213-218`), la entrada a la población gobernada
> depende de tres grafías concretas al inicio de línea —`Lección de forma:`, `Lección durable:`,
> `Lecciones capitalizadas`—, no del nombre del archivo ni de una marca entre corchetes. Este archivo no
> escribe ninguna de las tres, así que el verificador lo publica como `[EXCLUIDO]` con su razón
> (`:114-115`): la política del write-back es por aporte declarado, no por existencia. Tampoco se lo
> nombra desde `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` ni
> `dependencias-fases.md` de ningún plan archivado, que es la segunda vía por la que `:221-239` convierte
> un contexto en gobernado sin publicación y fabrica un rojo.
>
> **No acuña IDs nuevos.** El índice (`scripts/build_lesson_index.py:76`, `ID_RE`) solo reconoce tokens con
> prefijo de lección (`L`), señal (`S`), decisión (`D`) o deuda (`DA`) seguidos de guión. Esta nota cita
> `L-JEV.R1`, `L-JEV.R2`, `L-JEV.R4`, `L-JEV.C1` y `L-JEV.C3`, que ya están definidos; las deudas del
> piloto se nombran con su literal propio (`B2-1`, `REL-5`, `H1`), que el índice no ve. Contadores al
> escribir: **377 IDs**, `citados_sin_definicion` **108**.

---

## 0. Veredicto en una línea

**No integrar Jev ahora.** La costura de juicio semántico que el piloto quería habilitar **ya existe y ya
corre en producción dentro de `v4complete`**, servida por otro proveedor, y viola seis reglas nombradas en
los dos documentos externos. Curar eso es valor de producto puro, no necesita credencial ni presupuesto ni
muestra etiquetada, y es precondición técnica de cualquier comparación futura de proveedores.

---

## 1. Plano 1 re-medido: cero cableado del piloto (confirmado con comando)

```
grep -rlniE "jev|typesafe" modules/ agent_harness/ main.py .agents/
→ .agents/workflows/phased_project_executor.md     (1 archivo, prosa)
```

Cero referencias a `decision_client`, `triage_lesson_relevance` o al brazo Jev en `modules/`, `main.py`,
`agent_harness/` o hooks. Y no fue un olvido: el plan lo declaró fuera de alcance en su §No-alcance
(`01-plan-maestro.md:72`), que excluye explícitamente "producto hotelero" y dice "No se ejecuta
`v4complete` ni `v4audit`". `modules/providers/llm_provider.py` quedó intacto por la premisa P5
(`01-plan-maestro.md:17`).

**Consecuencia que re-encuadra la pregunta:** integrar el piloto en `v4complete` no es *continuar* el
piloto. Es abrir un frente que el piloto se prohibió a sí mismo. Eso no lo invalida, pero significa que
no hereda ninguno de sus criterios de aceptación ni de su regla de adopción pre-registrada.

También se midió la dirección de dependencia: **cero imports `modules/` → `scripts/`**
(`grep -rnE "^\s*(from|import)\s+scripts" modules/ agent_harness/ data_validation/ main.py` → vacío).

---

## 2. El hallazgo: ya hay un juicio semántico vivo en `v4complete`

El tribunal de certificación ejecuta, en cada corrida, un extractor LLM sobre texto no estructurado:

| Punto | Evidencia |
|---|---|
| Se instancia en el flujo de producción | `main.py:3430` → `_extractor = LLMPromiseExtractor()` |
| Alimenta **dos** de los cuatro revisores | `main.py:3445` (Bot 2 Alineación) y `main.py:3446` (Bot 4 Honestidad) |
| Bot 2 consume la extracción | `alignment_reviewer.py:77` |
| Bot 4 consume la extracción | `honesty_reviewer.py:171` → alimenta `OVER_PRESENTATION` (`:347`) |
| **Y cambia comportamiento** | `judge.py:511-512` (`verified_critical`/`verified_block` → `VERDICT_BLOCKED`) → `judge.py:49-51` `blocks_delivery_zip()` → gatea el rename del ZIP en cuarentena |
| La costura ya es un `Protocol` con dos implementaciones | `llm_extractor.py:43-56` (`PromiseExtractor`), `:59` (`LLMPromiseExtractor`), `:182` (`MockPromiseExtractor`) |

Esto es, punto por punto, el patrón que la guía de campo describe en §VI ("Put Jev After the LLM") y §X.B
("Layer the Gate"): un LLM genera el documento comercial, un juicio semántico acotado lo revisa, y código
determinista retiene la autoridad. **Jev sería una tercera implementación de `PromiseExtractor`, no una
arquitectura nueva.**

Y el módulo ya declara la separación correcta en su propio docstring (`llm_extractor.py:4-6`): "El
extractor SOLO propone; nunca emite veredicto. El veredicto lo aplica la capa determinista del revisor, y
el Juez lo certifica."

---

## 3. Seis defectos de la costura viva, contra los dos documentos externos

Esta es la parte de mayor valor inmediato: las dos guías sirven como **lista de verificación** sobre código
que ya está en producción, con o sin Jev.

| # | Regla | Fuente | Evidencia en el árbol |
|---|---|---|---|
| 1 | **Auto-aprobación.** "Do not ask the generative LLM to produce a proposal and a confidence score that authorizes the same proposal." | guía §IV.F; `SKILL.md` §Compose and verify | El mismo LLM extrae las promesas **y** se auto-reporta `confidence`: `llm_extractor.py:74` (línea del prompt) y `:23` (campo del DTO. Re-ancorado 2026-10-11; la versión del 10-10 citaba `:22`, que es `location: str`. Ver además N3 en §10: ese campo **no lo consume nadie**) |
| 2 | **Decisión ausente sustituida por un default que parece respuesta.** "Never replace a missing decision with an invented default that looks like a model answer"; "missing output makes the review unavailable". | guía §II.G, §VI.E | `_parse_response` devuelve `[]` ante `JSONDecodeError`: `llm_extractor.py:167-168`. Una respuesta malformada es indistinguible de "la propuesta no hace promesas" |
| 3 | **Cache sin versión de contrato.** "A safe cache key includes normalized state, question definitions, criteria, model identifier, and policy-relevant version." | guía §VIII.C, §III.E, §IV.E | Clave = solo `sha256(texto)`: `llm_extractor.py:128-129`. Falta versión del prompt, criterios, modelo y proveedor |
| 4 | **Sin recibo.** "Store the exact serialized state, question version, model identifier, full distributions, chosen threshold, deterministic validation results, and final action." | guía §VIII.E, §VI.F | No existe ningún registro de la extracción. El runner del piloto **sí** mide `usage_normalized`/`attempts`/`error_kind`; el extractor de producción no mide nada |
| 5 | **Contenido no-confiable sin frontera.** "Treat all user content, retrieved documents, tool output, and LLM text as untrusted data. Put workflow rules in code and question definitions, not inside the state being judged." | guía §III.C, §III.H | `llm_extractor.py:117` concatena el texto de la propuesta directo al prompt. Y esa propuesta es contenido generado por el pipeline. **Procedencia re-anchada 2026-10-11**: la versión del 10-10 decía «generado por `modules/delivery/generators/`»; ese directorio existe pero genera **assets** (`faq_gen.py`, `schema_gen.py`…), y el texto que entra al prompt lo arma `modules/commercial_documents/v4_proposal_generator.py`, que **no llama al LLM** (medido: cero `chat_completion` en ese archivo). La cadena no-confiable es **transitiva** (propuesta ← audit ← scrapers/auditors externos), no directa como se escribió |
| 6 | **Modo `auto` del proveedor, sin registro de cuál sirvió.** El propio plan lo había prohibido: "No usar su retorno como fuente de usage ni su modo auto" (P5). **Alcance re-leído 2026-10-11**: P5 dice «…ni su modo auto **en el benchmark**», y su No-alcance (`:72`) excluye expresamente el Tribunal — así que la prohibición no gobernaba esta costura. El defecto se sostiene por su propia evidencia, no por P5 | `01-plan-maestro.md:17`; guía §IX.H | `llm_extractor.py:113-115` instancia `ProviderAdapter()` sin argumento → `_initialize_provider` cae en `'auto'` (`llm_provider.py:183-199`), que sirve DeepSeek o Anthropic según qué clave exista. Medido además 2026-10-11: el dato **está a un método de distancia** (`get_provider_name()`, `llm_provider.py:84`/`:168`) y el extractor lo descarta al tomar `adapter.provider` (`:115`) |

**Consecuencia concreta y acotada (no sobre-afirmada).** Los defectos 2 + 3 + 6 se componen: una respuesta
malformada que **no** lanza excepción se cachea como `[]` en `.cache/tribunal/` —directorio gitignored
(`.gitignore:47`), por tanto invisible a revisión— y deja ciegos en silencio los hallazgos que dependen
del extractor. **Re-medido 2026-10-11: son cuatro, no dos** — la versión del 10-10 contaba
`PROMESA_SIN_MATRIZ` (Bot 2) y `OVER_PRESENTATION` (Bot 4); caen además el `SIN_BRECHA_ASOCIADA` **hacia
adelante** (la promesa que recae en una entrada `NO_BREACH` o `LINKED` sin `pain_id`,
`alignment_reviewer.py:96-101`) y `TIER_MISMATCH` (`honesty_reviewer.py:172-179`). El envenenamiento es
**persistente**: `_load_from_cache` (`:134-143`) devuelve `[]` porque es una lista válida, así que ese texto
de propuesta no se vuelve a extraer nunca, ni siquiera después de que el proveedor se recupere. Y el acta
**no lo registra como daño**: con `[]` y una matriz limpia, Bot 2 queda en `OK_NO_FINDINGS` con
`APROBADO` y Bot 4 en `OK_NO_FINDINGS` (`outcome.py:280-293`) — el acta se ve sana.

Tres precisiones que hay que conservar para no convertir esto en un falso verde universal. (La cabecera decía
«dos» y listaba tres viñetas; el conteo se corrige aquí, no el contenido.)

- El **cruce inverso sí sigue disparando**: `_cover_unmatched_entries` (`alignment_reviewer.py:271`) clasifica
  entradas de matriz sin promesa y emite `SIN_BRECHA_ASOCIADA`. Con `[]`, el veredicto de Bot 2 puede seguir
  siendo `DEVOLVER-PRUEBAS`. Es la única fuente de hallazgos de Bot 2 que sobrevive al envenenamiento: la
  dirección promesa→matriz muere entera.
- De los otros tres tipos de hallazgo de Bot 4, **dos** son independientes del extractor
  (`CG_WARNING_UNDISCLOSED`, `MISSING_SCENARIO`) y **uno no**: `TIER_MISMATCH` itera los claims que devolvió
  el LLM (`honesty_reviewer.py:172-179`), así que con `[]` tampoco se emite. La redacción del 10-10 lo contaba
  entre los independientes y con eso subestimaba el punto ciego.
- Una excepción del proveedor **sí** se propaga honestamente: `chat_completion` lanza (`llm_provider.py:18`,
  `:76`, `:148-160`, `:200`), `main.py:3453-3456` la captura como `READER_FAILED`, y `judge.py:525` impide
  `APROBADO-PARA-ENTREGA`. El punto ciego es solo la respuesta **legible pero no parseable**.

**Agregado estructural:** `judge.py:40-43` excluye P6.2 de `T1_CERTIFIABLE_CLAUSES` y `:286-296` la
hardcodea `NOT_EVALUABLE` con el comentario "requiere LLM" y "T4-A la implementará con extracción LLM" —
aunque Bot 2 ya existe y ya corre. O sea: la única cláusula *sobre* alineación semántica jamás puede
aportar un PASS; de Bot 2 solo cuentan sus negativos (vía `reviewer_reports`).

**Agravante medido 2026-10-11:** no es solo un diferido no re-ancorado — el `finding` que el acta publica
(`judge.py:295`) dice literalmente *"Requiere Bot 2 (alignment_reviewer) — no implementado en T1"*, y en esa
misma acta figura, en `reviewer_reports`, el informe que Bot 2 escribió en la corrida. El artefacto publicado
niega la existencia del revisor que acabó de ejecutar.

---

## 4. Dónde sería útil, y dónde sería puro coste

Criterio de orden: ¿cambia comportamiento? × ¿el espacio de respuestas es cerrado? × ¿ya hay costura?

1. **Bot 2 / Bot 4 (tribunal).** Costura existente (`PromiseExtractor`), ya gatea entrega, espacio cerrado
   (`ALINEADO` / `SIN-BRECHA-ASOCIADA` / `PROMESA-SIN-MATRIZ` es un `Choice`; "¿es una promesa de
   servicio?" y "¿sobre-presenta un valor ESTIMATED como verificado?" son `Noul`). **Advertencia de
   diseño:** extraer *spans* es una tarea generativa, así que no es drop-in. La forma honesta es el patrón
   "Select instead of generate" de `SKILL.md`: código propone candidatos por regex, el modelo juzga cada
   uno. Eso es cambio de contrato, no de implementación.
2. **`data_validation/contradiction_engine.py`** — la clasificación hard/soft es hoy por keywords, y
   alimenta un gate **blocking** (`hard_contradictions: count = 0`). "¿Se contradicen estas dos
   afirmaciones sobre el mismo hecho?" es un `Noul` limpio. Alta palanca, alto riesgo: un falso positivo
   bloquea una entrega.
3. **`pain_solution_mapper.py` / `opportunity_scorer.py`** — hoy tablas estáticas
   (`BRECHA_SEVERITY_MAP` en `opportunity_scorer.py:51`, `PAIN_SOLUTION_MAP`). Reemplazables por
   `Choice`/`Score`, pero alimentan `pricing_compliance` → dinero. Guía §X.A: los efectos secundarios
   siguen siendo un problema de política, no del modelo.

**Contra-recomendación expresa: las métricas advisory.** `citability_scorer.py` y
`ia_readiness_calculator.py` son el destino más *obvio* (un 0-100 pide un `Score`) y el peor. Son
advisory, AGENTS.md declara que "nunca bloquean publicación", y `grep -rn "citability" modules/quality_gates/
modules/orchestration_v4/` devuelve **cero** coincidencias: no tocan ningún gate. Su mecanismo actual es
aritmética estructural (`citability_scorer.py:96-111`, `score += 20/10/15` sobre propiedades del bloque).
Ahí aplica literal la guía §I.G: una capa de decisión que no altera ruteo, revisión ni contexto **es solo
latencia adicional**.

**Y el consumidor diseñado del piloto** (`scripts/triage_lesson_relevance.py`) es gobernanza de tiempo de
desarrollo, no `v4complete`. Es otra pista, no la misma.

---

## 5. Bloqueos estructurales de una integración real

| Bloqueo | Estado medido |
|---|---|
| Dirección de dependencia | `scripts/decision_client.py` es la única puerta al proveedor y vive en `scripts/`; cero imports `modules/` → `scripts/`. Cablear el producto exige invertir esa dirección o mudar la costura a `modules/providers/` |
| El aislamiento es un gate, no un estilo | `decision_client.py` trae su propio escáner (`es_import_prohibido:787`, `es_carga_dinamica_prohibida:800`, `escanear_aislamiento:844`) que impone "solo la puerta importa el SDK" |
| El SDK no entra en el venv del producto | Premisa P8 (`01-plan-maestro.md:20`): resuelve pydantic 2.13.5 contra el pin `2.12.5`. Vive aislado en `tmp_test/venv-jev-sdk`. Nadie ha respondido cómo lo consumiría el runtime de `v4complete` |
| Idioma | La guía §X.F y la premisa P9 coinciden: inglés es el de mejor precisión declarada. Todo el corpus es español hotelero. Calibrar umbrales ahí **es** el etiquetado humano de los 60 pares, que sigue pendiente |
| Dinero | `limites_gasto.usd` sigue `null`, declarado fuera de gobernanza por el operador |

**Lo que la costura ya ofrece y conviene no redescubrir.** `decision_client.py` habla nativamente el
vocabulario de los dos documentos: `Pregunta` (`:215`), `RespuestaEleccion` = Choice (`:246`),
`RespuestaNivel` = Score (`:260`), `RespuestaNoul` = Noul (`:274`), `evaluar(state, preguntas, entorno)`
(`:689`), `estado_proveedor()` (`:749`), `estimar_carga()` (`:766`), y excepciones tipadas
(`ProveedorNoConfigurado:156`, `RespuestaIlegible:165`, `LectorFallido:177`, `Ausente:181`). Es un
correspondencia 1:1 con la tabla de primitivas de `SKILL.md`. Esa puerta **ya está construida y probada**.

---

## 6. Lo que la evidencia del piloto NO autoriza a concluir

El piloto cerró con `run_status=INCOMPLETO`, `decision=null`, `transfer_status=PENDIENTE` y etiqueta de
adopción **MUESTRA-INSUFICIENTE** dictada por el operador el 2026-10-05. Dos datos duros:

- **H1 de FASE-C:** la recuperación fue 0.5 = 1/2 **idéntica en los tres brazos**, porque los tres miden la
  misma capa fría. La única métrica que se pudo medir **no discrimina**.
- **Denominador efectivo de la comparación: 1 par** con elección utilizable en los dos brazos, contra un
  objetivo de 60-100.

Por tanto: **no hay evidencia de que Jev supere a DeepSeek en nada dentro de este repositorio.** Adoptarlo
hoy sería adoptar sin la evidencia que el plan existía para producir. Ver `L-JEV.R1`..`L-JEV.R4` en
`10-analisis-post-implementacion.md` del plan archivado y `L-JEV.C1`/`L-JEV.C3` en
`Historico/CONTEXT-JEV-CURA-B2-1-2026-10-09.md`.

---

## 7. RECOMENDACIÓN (énfasis pedido por el operador)

Las cuatro opciones que se le presentaron eran: **A** auditoría de la costura viva contra las dos guías;
**B** diseño del contrato `PromiseExtractor` y de la decisión arquitectónica `modules/` → `scripts/`;
**C** re-medición en vivo con una corrida real de `v4complete`; **D** re-apertura de FASE-C con 60 pares
re-anchada a Bot 2/Bot 4.

### Recomendación: **A + B, en ese orden, como una sola fase documental. C después. D no, y no como re-apertura.**

**Por qué A primero.** Es lo más barato y lo de mayor valor: convierte los seis hallazgos de §3 de
"un asistente lo dijo" en un artefacto anclado con su costo de cura. No necesita credencial, ni
presupuesto, ni muestra etiquetada, ni decisión de proveedor. Y es **precondición** de todo lo demás: no
se puede diseñar la costura (B) sin saber qué defectos tiene el contrato vigente, y no se puede comparar
proveedores (C/D) sin el recibo que A identifica como ausente (defecto 4).

**Por qué B junto a A, y no después.** B es donde vive la decisión real, y es una decisión que solo el
operador puede tomar: la dirección de dependencia `modules/` → `scripts/` y cómo el runtime del producto
alcanza un SDK que no puede instalarse en su venv. A sin B deja los defectos conocidos pero la forma
indecidida; B sin A diseñaría sobre un contrato auditado a medias. Juntos producen un solo entregable
coherente: el defecto, su cura y la arquitectura que la hace posible.

**Por qué C no va ahora.** Requiere la credencial de DeepSeek, gasta dinero, y —lo decisivo— **no puede
producir un recibo porque el recibo no existe** (defecto 4). Una corrida antes de curar eso produce una
observación que no se puede reproducir ni atribuir a un proveedor. Además tiene efectos secundarios
reales: escribe en `output/` y en `.cache/tribunal/`, y puede envenenar la cache (§3). Su momento es
**después** de A+B, como línea base del modo *shadow* que prescribe la guía §X.C.

**Por qué D no, y por qué mi propia opción D estaba mal formulada.** Re-anclar la métrica de triaje de
lecciones a Bot 2/Bot 4 no es re-abrir FASE-C: es **otro experimento**. El §Pre-registro del maestro
(`01-plan-maestro.md:99`) lo dice explícitamente —"Un cambio inducido por resultados de evaluación exige
otra muestra de evaluación y nuevo protocolo, no reetiquetar el mismo resultado como confirmatorio"— y su
regla complementaria es que los criterios de adopción no se retocan según resultados. Sumado a que el
etiquetado humano de los 60 pares es obligatorio por protocolo y el agente prepara pero no etiqueta, D
solo tiene sentido como **plan nuevo**, después de que A+B digan si vale la pena medirlo.

### Forma sugerida de la fase A+B

Un solo entregable documental, sin código: (i) los seis defectos de §3 re-verificados uno a uno en el
árbol, cada uno con su par "qué rompe hoy / qué lo previene"; (ii) el contrato `PromiseExtractor` bajo
"código propone, modelo juzga", con la firma que admita un cuarto estado `NO-EVALUABLE` en vez de `[]`;
(iii) el recibo mínimo viable (state digest, versión de pregunta, modelo servido, latencia, resultado) y su
clave de cache versionada; (iv) las dos salidas de la decisión `modules/` → `scripts/` con su costo cada
una; (v) qué queda **fuera** y con dueño. La decisión de P6.2 (`judge.py:286-296`) entra como ítem propio:
hoy es un `NOT_EVALUABLE` permanente en el acta publicada.

### Un apunte sobre el valor formativo, separado del valor de producto

El trabajo de recibo + modo sombra + calibración por banda de probabilidad es evidencia de competencia en
automatización más defendible que "llamé una API de decisiones", porque es instrumentación y gobernanza de
incertidumbre, no consumo de un servicio. Se declara aquí como efecto secundario, no como criterio de la
recomendación.

---

## 8. Reubicación de los dos documentos externos (medido, no opinado)

Estado actual: ambos sueltos en `C:\Users\Jhond\Github\`, el directorio **padre** del repositorio, entre
carpetas no relacionadas (`DIAN2676/`, `Renta/`, `Procuraduría/`, `UCDM/`, `Automatización/`, etc.).

> **Re-medido 2026-10-11: este párrafo ya describe un estado que no existe.** Medido con `ls` y `sha256sum`
> sobre el directorio padre: `Github/SKILL.md` **no está** (queda solo el skill instalado,
> `~/.qoder/skills/typesafe-ai/SKILL.md`, 10.040 bytes, sha256 `de8b4c35a3801f12…` — el mismo valor que esta
> nota registró aquel día para la copia instalada); y la guía **no está suelta con nombre genérico**: es un
> archivo plano `Github/referencias-typesafejev-llm-field-guide-2026-09.md` (40.690 bytes, mtime 2026-09-25).
> Las dos recomendaciones de abajo fueron ejecutadas entre el 10-10 y el 10-11 por alguien fuera de esta
> sesión, y la de la guía quedó **mal escrita el destino**: el nombre de la carpeta y el del archivo salieron
> concatenados, sin el separador que pedía la recomendación 1.

### 8.1 `SKILL.md` — reubicar o eliminar; el problema es el nombre, no la carpeta

Medido:

```
C:/Users/Jhond/.qoder/skills/typesafe-ai/SKILL.md   10040 bytes  sha256 de8b4c35a3801f12…
C:/Users/Jhond/Github/SKILL.md                      10040 bytes  sha256 71ea90d7906c6554…
diff normalizando EOL → única diferencia: re-envío de línea del frontmatter (líneas 6-8)
```

O sea: la copia suelta es un **duplicado re-envuelto** del skill ya instalado, no una versión divergente.
El skill `typesafe-ai` está instalado y es lo que la sesión carga realmente; la copia en `Github/` aporta
cero información y sí aporta riesgo de divergencia futura (si el skill se actualiza, la copia queda
stale y sigue pareciendo autoritativa).

**Recomendación:** eliminar la copia suelta, o si se quiere conservar como referencia legible, moverla
dentro de una carpeta nombrada y con el nombre del producto en el archivo
(`referencias-typesafe/typesafe-ai-SKILL.md`). **No versionarla dentro de iah-cli:** una segunda copia de
la definición de un skill dentro de un proyecto es divergencia sin gobernanza.

> **Estado 2026-10-11:** ejecutada por la vía fuerte — la copia suelta fue **eliminada**, no reubicada. No
> queda nada que gobernar aquí.

### 8.2 `jev-llm-field-guide.md` — mantener fuera del repo, en carpeta nombrada; y a QMind si va a sostener decisiones

Es un documento de tercero, independiente, fechado en septiembre 2026, que se autodeclara educativo y sin
endorso (§XI.E) y que remite a los docs vivos como fuente de verdad (§XI.D: "verify live documentation
before deployment").

**Recomendación: NO versionarlo dentro de iah-cli.** La convención de la casa es que una afirmación sobre
el mundo externo lleva fecha y se re-consulta, no se congela: las premisas P2, P6 y P9 del propio plan
(`01-plan-maestro.md:14`, `:18`, `:21`) son el ejemplo de qué pasa cuando se congela — las tres quedaron
vencidas y hubo que re-medirlas con sello. Versionar la guía crearía exactamente el problema de cita
vencida que este repositorio gasta mucho aparato en combatir.

Lo que sí conviene, en orden:

1. **Moverlo a una carpeta nombrada** junto al skill, p. ej.
   `C:\Users\Jhond\Github\referencias-typesafe\`, con su fecha en el nombre
   (`jev-llm-field-guide-2026-09.md`). Suelto en `Github/` con nombre genérico no se sabe de qué proyecto
   es ni de cuándo.
2. **Publicarlo a QMind** si va a sostener decisiones de iah-cli. El notebook `iah-cli-lecciones` es el
   depósito de conocimiento que el agente ya sabe recuperar, y publicarlo le da fuente fechada y ruta de
   retrieval. Ojo con la regla medida del write-back: se sube con título nuevo y se verifica por
   **descarga + sha256**, nunca por título (`validate_qmind_writeback.py --strict` decide por título y da
   `[PASS]` antes y después de republicar, o sea su verde no informa del contenido).
3. **Citarlo desde este contexto y desde `evidence/…`**, que es donde el verificador de frescura no mira.
   Nunca desde los tres documentos que gobiernan contexts.

> **Estado de los tres ítems, medido 2026-10-11.** (1) **Ejecutado a medias y con defecto de forma**: la guía
> ya no está suelta con nombre genérico, pero quedó en un **archivo plano**
> `Github/referencias-typesafejev-llm-field-guide-2026-09.md` (40.690 bytes, mtime 2026-09-25) — el nombre de
> la carpeta pedido en este ítem se **concatenó** al del archivo en vez de volverse su contenedor. (2) **No
> ejecutado**: con `list_sources` sobre el notebook `iah-cli-lecciones` en sus dos páginas (`totalSize: 65`) no
> hay **ningún título** de la guía. Sigue sin ruta de retrieval, así que las citas a §III/§VI/§VIII de la guía
> que hacen los defectos 1-5 siguen siendo irrecuperables para otra sesión. (3) **Ejecutado**: este contexto la
> cita, y `evidence/` no entra en el barrido del verificador de frescura.

### 8.3 Regla general que sale de los dos casos

Un documento que describe un producto de tercero con ciclo de actualización propio **no se versiona en el
repo**: se referencia con fecha y se re-consulta. Un artefacto que ya está instalado y es autoritativo
**no se duplica**: se señala dónde vive.

---

## 9. Qué no se hizo en esta sesión, declarado

- Cero escrituras en `modules/`, `scripts/`, `tests/`, `config/`, `AGENTS.md`, `VERSION.yaml`.
- Cero llamadas de inferencia; no se leyó ni imprimió ninguna credencial.
- No se ejecutó `v4complete` ni `v4audit`.
- No se abrió ni se re-abrió ninguna fase del piloto; el plan sigue archivado con su estado terminal.
- No se commiteó ni se empujó nada. Este archivo es la única escritura de la sesión.
- Las opciones A/B/C/D siguen siendo del operador; nada de lo anterior las da por elegidas.

---

## 10. Re-verificación del 2026-10-11 (anotación aditiva, sin implementación)

**Qué es esto.** Una sesión distinta volvió a medir cada ancla de este documento contra el árbol de trabajo y
amplió el alcance. Lo que **refuta o re-ancha** un pasaje del 10-10 se escribió en su sitio (defectos 1, 5 y 6
de §3; el párrafo de composición y sus viñetas; el agregado de P6.2; §8) con el valor anterior dentro del
texto, para que el lector vea la medida vigente sin perder la original. Esta sección añade solo lo que el
10-10 no tenía: nueve hallazgos nuevos, el re-enmarque del blast radius, la causa raíz y el estado del
Knowledge Center. Cero código escrito, cero llamadas de inferencia, cero credenciales leídas, cero commits.

### 10.1 Balance: qué se sostuvo

| Bloque | Resultado | Como se midió |
|---|---|---|
| §2 — costura viva | **7/7 anclas confirmadas** (una re-anchada: el campo del DTO es `:23`, no `:22`) | lectura directa de `main.py:3420-3456`, `llm_extractor.py` completo, `alignment_reviewer.py:77`, `honesty_reviewer.py:171` y `:347`, `judge.py:40-51`/`:286-296`/`:511-512`/`:525`, `outcome.py:141-156` |
| §3 — seis defectos | **6/6 confirmados**, tres con la atribución o la procedencia corregidas | idem, más `llm_provider.py:183-199` y `.gitignore:47` |
| §1 y §4 — greps de alcance | reproducidos **exactos**: `jev\|typesafe` → 1 archivo de prosa (`.agents/workflows/phased_project_executor.md`); `citability` en `modules/quality_gates/` + `modules/orchestration_v4/` → **0 coincidencias**; imports `modules/`→`scripts/` → **0** | los tres comandos re-ejecutados tal como están escritos en el §1 y el §4 |
| §5 — `decision_client.py` | **14/14 anclas exactas** (`Pregunta:215`, `RespuestaEleccion:246`, `RespuestaNivel:260`, `RespuestaNoul:274`, `evaluar:689`, `estado_proveedor:749`, `estimar_carga:766`, `ProveedorNoConfigurado:156`, `RespuestaIlegible:165`, `LectorFallido:177`, `Ausente:181`, `es_import_prohibido:787`, `es_carga_dinamica_prohibida:800`, `escanear_aislamiento:844`) | `grep -n` de cada símbolo |
| §6 — estado terminal del piloto | **confirmado** contra el Knowledge Center: `MUESTRA-INSUFICIENTE` dictada el 2026-10-05, `run_status=INCOMPLETO`, `decision=null`, recuperación 1/2 en los tres brazos, denominador efectivo 1 par | `retrieve` sobre `iah-cli-lecciones` (chunks del `10-analisis` del piloto, score 0,87-0,93) y lectura del plan archivado `:14`/`:17`/`:20`/`:21`/`:72`/`:99` |
| Un segundo `def evaluar` en `:978` | **falsa alarma descartada**: vive dentro de `PLANTILLA_SEGUNDO_PROVEEDOR` (plantilla de string de AC9), no es una segunda definición que gane sobre `:689` | lectura de `decision_client.py:967-997` |

### 10.2 Nueve hallazgos nuevos (más uno menor)

| # | Hallazgo | Ancla | Relación con los seis |
|---|---|---|---|
| N1 | **Truncamiento sistemático → `[]` envenenada.** El extractor pide `max_tokens=2000` y ningún proveedor mira `finish_reason`; una respuesta cortada a media lista es JSON inválido → defecto 2 → cache permanente. En propuestas largas no es un caso excepcional: es la vía normal | `llm_extractor.py:118-122`; `llm_provider.py:128-164` (no inspecciona `finish_reason`) | amplifica el 2 |
| N2 | **Tres vías al `[]` silencioso**, el 10-10 nombra una: JSON decodificado con forma incorrecta (`not isinstance(data, list)` → `[]`), respuesta con prosa antes del JSON (el des-cercado solo actúa si el texto **empieza** con fence), y el `JSONDecodeError` ya citado | `llm_extractor.py:156-168` | amplifica el 2 |
| N3 | **La `confidence` es dato muerto.** Bot 2 no la copia a la fila de su matriz y Bot 4 solo lee `claim.text`. Se pide al LLM, se cachea, no la consume nadie | `alignment_reviewer.py:208-250`; `honesty_reviewer.py:328-384` | reformula el 1: auto-autorización **y** salida sin consumidor |
| N4 | **Bot 4 reusa el prompt de Bot 2 para otra pregunta.** Su propio docstring dice «extrae claims de sobre-presentación», pero llama el mismo `extract_verbal_promises` con el `EXTRACTION_PROMPT` de promesas de servicio. Hoy es inocuo (misma clave → mismo resultado); si Bot 4 recibe prompt propio, la clave `sha256(texto)` le servirá las respuestas viejas de Bot 2 | `honesty_reviewer.py:8-9` y `:171`; `llm_extractor.py:66-89` | modo de fallo latente del 3 |
| N5 | **Sin red determinista de texto completo para `OVER_PRESENTATION`:** el regex de lenguaje de verificación corre **solo sobre las citas que el LLM eligió**, nunca sobre la propuesta entera. La completitud de la extracción acota al hallazgo CRITICAL incluso con cache sana | `honesty_reviewer.py:342-344` | nuevo |
| N6 | **Dos precedencias para el mismo `evidence_tier` dentro del mismo acta:** el Juez lee escenarios→MANIFEST→fallback `"C"`; Bot 4 lee MANIFEST→escenarios→fallback `"UNKNOWN"`, y con `UNKNOWN` el check de sobre-presentación **ni siquiera corre**. Manifest `A` + escenarios `B`: Bot 4 se silencia mientras el Juez aplica primer piso | `judge.py:195-215`; `honesty_reviewer.py:304-326` y `:334` | nuevo |
| N7 | **Falso positivo con poder de bloquear:** `\b(100%\|total\|absoluto\|definitivo)\b` emite CRITICAL sobre la palabra «total» dentro de una cita elegida por el LLM → `BLOQUEAR` → `verified_critical` → ZIP suprimido. «total» es de uso común en prosa hotelera en español | `honesty_reviewer.py:337-340`; `judge.py:511-512` | nuevo (riesgo de signo opuesto al envenenamiento) |
| N8 | **`contradiction_engine` traga las excepciones de sus propias reglas HARD con un `print`:** una regla que revienta produce cero conflictos y deja `hard_contradictions` en verde. Antes de discutir un clasificador tipado ahí (§4.2), la capa vigente ya tiene modo de fallo silencioso | `data_validation/contradiction_engine.py:442-456` y `:472-478` | nuevo, afecta al candidato 2 del §4 |
| N9 | **Ni el artefacto de cache es un recibo:** el `.json` guarda solo la lista de promesas — sin fecha, sin modelo, sin versión de prompt, sin run; y no existe TTL ni invalidación en ningún camino del módulo | `llm_extractor.py:145-151` | confirma el 4 a nivel de storage |
| N10 | Menores: escritura no atómica (`open(path,"w")` + `json.dump`); `cache_dir` relativa al CWD; crecimiento sin techo | `llm_extractor.py:99`, `:148-149` | menores |

### 10.3 Re-enmarque del blast radius (medido, no inferido)

- **Toda la superficie LLM del producto es un punto.** `grep` de `chat_completion(` sobre `modules/`,
  `main.py`, `agent_harness/` y `data_validation/` devuelve cinco coincidencias: cuatro definiciones en
  `llm_provider.py` (`:32`, `:56`, `:100`, `:206`) y **una** sola llamada de producción, el extractor del
  tribunal (`llm_extractor.py:118`). No hay otro juicio LLM en el flujo.
- **Son además *una* llamada por corrida.** Bot 2 y Bot 4 comparten la misma instancia (`main.py:3430`,
  pasada en `:3445` y `:3446`) y leen la propuesta por el mismo resolvedor, así que el segundo revisor
  resuelve la misma clave y pega en cache. Un solo `[]` envenenado ciega a **los dos a la vez**.
- **Y el acta no registra el daño como daño.** Con cache envenenada y matriz limpia, Bot 2 queda en
  `OK_NO_FINDINGS` con recomendación `APROBADO` y Bot 4 en `OK_NO_FINDINGS` (`outcome.py:280-293`): el acta
  publicada **se ve sana**. La entrada envenenada es indistinguible de una propuesta sin promesas, que es
  exactamente lo que la guía prohíbe en §II.G.

### 10.4 Causa raíz

Los seis defectos y N1-N5 no son seis decisiones fallidas: se siguen de **dos** causas.

1. **El contrato de la costura colapsa cuatro estados en un canal.** `extract_verbal_promises → list` es la
   única salida, y en ese tipo «OK con promesas», «OK sin promesas», «respuesta ilegible» y «proveedor falló»
   no pueden distinguirse. De ahí se sigue el envenenamiento cacheable (defecto 2, N1, N2), el acta que se ve
   sana (§10.3), y que la única señal de calidad viva **dentro** del payload no confiable (defecto 1, N3).
2. **Cero versionado del contrato de extracción.** Ni la clave de cache ni ningún registro llevan versión de
   prompt, criterios, proveedor o modelo servido. De ahí la cache que sobrevive a cambios de prompt (defecto 3,
   N4), el recibo imposible aunque el dato esté a un método de distancia (defecto 4), y el modo `auto` sin
   rastro (defecto 6).

Consecuencia para el diseño: **cualquier cura que deje el tipo de retorno en `list` deja las dos causas
intactas**, se cambie o no de proveedor. Eso es lo que hace a esta cura precondición de la comparación, como
afirmaba el §7.

### 10.5 Knowledge Center: qué había y qué no se sabía

- **El colapso de estados ya estaba nombrado diecinueve días antes.** `CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21`
  (caso 4, en el árbol local: `Historico/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md:52`; publicado además
  en el notebook con dos títulos, fuentes `01a0efcc-3297…` y `01a0e4d9-e442…`): *«El parseo que transforma JSON
  inválido en lista vacía muestra un colapso de estados que el adaptador no debe repetir. Fuera del alcance
  actual.»* El defecto 2 no es un hallazgo del 10-10: es la re-derivación de una deuda que el propio corpus
  registró el 09-21 y dejó explícitamente fuera de alcance.
- **Tres notas publicadas del plan TRIBUNAL-OFFLINE-2026-09-09** (definidas en `LECCIONES-INDEX.md:203-205`)
  gobiernan lectura de esta costura: la cache de producción con default `.cache/tribunal/` es **decisión
  declarada** y los tests inyectan `tmp_path` (así que «invisible a revisión» no es un accidente, pero sigue
  siendo punto ciego de incidente); el `matching` difuso por `service_hint` es **deliberado** para no fabricar
  falsos `PROMESA-SIN-MATRIZ` — la dirección opuesta (una promesa encajada en la entrada equivocada por
  substring) no está medida; y la lección del test vacuo exige que el cruce cubra ambas direcciones.
- **La regla de write-back que cita el §8.2 está publicada** y verificada por otra sesión: se confirma por
  descarga + sha256, nunca por título. Su aplicación al caso de la guía sigue pendiente (§8.2, ítem 2).

### 10.6 Recomendación: la forma A+B se mantiene, con el checklist ampliado

La decisión de §7 sigue siendo la correcta en su orden y en su motivo. Lo que cambia es el contenido del
entregable, que ahora lleva nueve ítems más anclados:

1. **(i) Auditoría** de los seis defectos re-verificados uno a uno, **más N1-N9**, cada uno con su par
   «qué rompe hoy / qué lo previene».
2. **(ii) Contrato** con estado explícito de cuatro salidas (promesas / sin promesas / ilegible / fallido),
   usando el literal `NO-EVALUABLE` que la casa ya emplea en sus instrumentos, de modo que «ilegible» deje de
   compartir valor con «no hay promesas». Sin esto, el resto de la lista es cosmética (§10.4).
3. **(iii) Recibo mínimo** (digest del estado, versión de prompt, proveedor servido, modelo, latencia, usage
   cuando el proveedor lo dé, digest de la respuesta cruda) y **clave de cache versionada**
   `(versión_prompt, proveedor, modelo, sha256(texto))`, con la regla de no cachear nunca un estado no-OK.
   Nota de medición: hoy `llm_provider` descarta el `usage` antes de que el extractor pueda verlo, así que el
   recibo exige tocar esa capa.
4. **(iv) Unificar la lectura de `evidence_tier`** entre Juez y Bot 4: una sola precedencia compartida (N6).
5. **(v) Red determinista de texto completo** para el lenguaje de verificación y **medición de la superficie
   de falso positivo** del patrón `total/absoluto/definitivo`, que hoy puede suprimir un ZIP por una palabra
   (N5, N7).
6. **(vi) El texto vencido del acta P6.2** (`judge.py:295`) como ítem propio junto con la decisión de cláusula.
7. **(vii) La decisión `modules/` → `scripts/`** con sus dos salidas y su costo, como ya pedía el §7.

`C` después, por el mismo motivo: sin el recibo de (iii) una corrida real no es reproducible ni atribuible.
`D` solo como plan nuevo, por la regla de pre-registro que el §7 citó bien (`01-plan-maestro.md:99`).

### 10.7 Lo que esta anotación NO hace, declarado

- No acuña IDs: los `N1`-`N10` no llevan ninguno de los cuatro prefijos que reconoce `ID_RE`, y las citas a
  `L-T4A.3`/`L-T4A.4`/`L-T4A.5` son a IDs **ya definidos** en `LECCIONES-INDEX.md:203-205`, así que no mueven
  `citados_sin_definicion`.
- No re-mide los contadores del preámbulo con una cifra propia: **los re-midió el índice**. Medido hoy, después
  de escribir esta anotación, `build_lesson_index.build()` imprime **377 IDs con definición** y **108 citados sin
  definición** — los mismos dos números que el preámbulo registra «al escribir» el 2026-10-10, así que §10 no los
  movió. El comando recorre el corpus **en memoria y no escribe**: el par `LECCIONES-INDEX.md` +
  `lecciones_index.json` está modificado por trabajo de otras sesiones y queda intacto.

  ```
  PYTHONUTF8=1 python -c "import sys; sys.path.insert(0,'scripts'); import build_lesson_index as b; i,c=b.build(b.DEFAULT_PLANS,b.DEFAULT_CONTEXT); print(c['ids_con_definicion'], c['ids_citados_sin_definicion'])"
  ```

- El `[EXCLUIDO]` del preámbulo **ya no descansa en un grep propio**: la función que decide la población,
  `poblacion_del_context()`, es **enteramente local** (no invoca el CLI de QMind ni la red) y sobre el archivo ya
  editado responde `gobernados: []`, con este contexto en `excluidos` bajo `EXCLUSION_NO_DECLARA` (`:114-115` — la
  misma razón que transcribe el preámbulo) y `declara_durable() == False`. Medido también el glob que lo ve
  (`CONTEXT-*.md` de la raíz lo incluye) y la segunda vía del preámbulo: ningún plan archivado lo nombra, porque
  `citados_por_planes_archivados()` no lo devolvió.

  ```
  PYTHONUTF8=1 python -c "import sys; sys.path.insert(0,'scripts'); import verify_qmind_context_freshness as v; from pathlib import Path; g,x=v.poblacion_del_context(Path('.opencode/context'),Path('.opencode/plans')); print([p.name for p in g], v.declara_durable(Path('.opencode/context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md')))"
  ```

- **Lo único que sigue sin sostenerse, acotado con su camino de cierre:** la parte **de red** del verificador —
  la comparación de bytes de cada cuerpo gobernado contra el notebook, y por tanto el check `[17/18]` completo
  del runner— no se corrió. No lo requiere nada de esta nota: un archivo que la propia clasificación publica como
  `[EXCLUIDO]` no tiene cuerpo publicado contra el que casar. Quien necesite el verde del runner entero corre
  `python scripts/run_all_validations.py` con QMind disponible, y para el modo estricto de este archivo,
  `verify_qmind_context_freshness.py --strict`.

### 10.8 Énfasis para quien diseñe el plan de la fase A+B (lección de esta sesión, no del código)

> Al cerrar la re-verificación escribí dos límites a mano —«no puedo sostener que el verificador confirme el
> `[EXCLUIDO]`» y «tampoco re-medí los contadores del preámbulo»— y **los dos los cerraba el propio instrumento
> sin red, sin credencial y sin gastar nada**: `poblacion_del_context()` clasifica en local y `build()` re-mide
> los contadores en memoria. Tuve que preguntarme «¿el lector real puede invocarse en parte?» para descubrirlo, y
> esa pregunta no la hizo el documento que la debía.
>
> La regla que se lleva el plan, entonces: **antes de escribir «no se puede verificar X», enumerar las funciones
> del lector real y separar las que corren sin el insumo remoto de las que no** — un verificador no es un bloque
> indisoluble, y su parte local suele ser justamente la que decide el estado que se afirma. Y si un límite
> sobrevive, escribir **qué camino exacto** lo cerraría y con qué comando, en lugar de dejar un «no se corrió»
> que la siguiente sesión lee como «no se puede». El coste de no hacerlo no es una métrica ausente: es que el
> documento se vuelva insumo con una restricción falsa encima, que es la misma clase de premisa vencida que las
> P2, P6 y P9 del piloto dejaron escrita en su propio plan.
>
> **Y la regla se cobró esta misma nota, en el acto de escribirla.** La primera versión de la viñeta del
> `[EXCLUIDO]` transcribía la razón del verificador entre comillas; al re-envolverse el párrafo, un salto de
> línea dejó ese token **al inicio de línea**, que es justamente el predicado de `MARCA_DURABLE` (`:106-110`,
> que admite espacios y encabezado antes de la frase). Medido con el lector real: `declara_durable()` pasó a
> `True` y el archivo **entró en `gobernados`** — o sea, esta nota habría exigido un write-back a QMind y cortado
> el `[17/18]` en rojo sobre `master` compartido, sin que ninguna intención mia fuera de declarar una lección. Se
> reescribió la viñeta sin el literal contiguo y la clasificación volvió a `excluidos`. De ahí la forma fuerte de
> la regla: **no confiar en que «no escribí la grafía» — correr la función que decide**, que en este repo es
> local, instantánea y no gasta nada.

### 10.9 Estado del artefacto y del índice (pre-imagen para quien commitee o diseñe la fase)

Medido el **2026-10-11** sobre `master` en `0c29d23`, después de todas las escrituras de esta sesión:

- **Este contexto no está versionado.** `git cat-file -e HEAD:<ruta>` responde *«exists on disk, but not in
  HEAD»* y `git status` lo lista `??`. No es una anomalía de esta nota: el §9 del 10-10 ya declaraba «no se
  commiteó ni se empujó nada», y HEAD lo confirma — el archivo **nunca** entró en el historial. Consecuencia
  material: lo escrito aquí sobrevive solo en el árbol de trabajo, y un `git clean` de otro operador lo borra.
  Si la fase A+B va a citar esta evaluación, su primer acto debe ser versionarla (con el pathspec propio), no
  fiarse de que está.
- **El índice trae trabajo ajeno, sin commitear, de otra sesión.** Staged: **13 entradas** — los 12
  `briefing/FASE-*.md` de `Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` y
  `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`. Unstaged:
  `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` (los dos, artefactos **generados**, que esta
  sesión no regeneró ni tocó). Nada de eso es mío y nada se despegó ni se limpió para escribir esta nota.
- **Regla que esto activa, ya cobrada en la casa:** en este índice no se corre `git commit` ni `--amend` **sin
  pathspec**, porque el árbol staged no es de quien escribe. Y si la fase A+B estampa su fila en `REGISTRY.md`,
  la unidad contable se toma después de todo el cierre documental, con lo que imprime `git`, no con lo que el
  plan esperaba.

Re-medir la pre-imagen antes de commitear (una línea, sin efectos):

```
git rev-parse --short HEAD; git cat-file -e "HEAD:.opencode/context/CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md" && echo versionado || echo SIN-VERSIONAR; git diff --cached --name-only; git diff --name-only
```
- No tocó `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` ni `dependencias-fases.md` de
  ningún plan, que es la segunda vía por la que un contexto pasa a gobernado sin publicación.
- No escribió código ni tests ni configuración; no ejecutó `v4complete` ni `v4audit`; no hizo llamadas de
  inferencia ni leyó credenciales; no commiteó ni empujó nada. Las escrituras de esta sesión son **este
  archivo**.
