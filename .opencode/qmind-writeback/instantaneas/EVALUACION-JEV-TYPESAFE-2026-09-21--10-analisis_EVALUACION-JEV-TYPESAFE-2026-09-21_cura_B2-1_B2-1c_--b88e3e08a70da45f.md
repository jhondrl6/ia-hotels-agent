# Análisis de ejecución — EVALUACION-JEV-TYPESAFE-2026-09-21

**Estado de ejecución (foto con la que se escribió esta línea, 2026-09-21): PENDIENTE.** ⟦Sello 2026-10-04 — vencido: este encabezado se escribió cuando el piloto no tenía ninguna fase de implementación ejecutada. **FASE-A se ejecutó el 2026-09-21 y FASE-B el 2026-10-03**, con su registro en `REGISTRY.md` del 2026-10-04; la fila de esa fase está en §Resumen de ejecución y su crudo completo en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/`. Lo que sigue pendiente es FASE-C y FASE-RELEASE⟧. Este archivo acumula evidencia desde la preparación; no afirma que el piloto se haya implementado. ⟦2026-10-04: esa segunda cláusula ya no se puede citar en presente — hay implementación certificada en A y B; se conserva la frase porque describe la política del documento, que sigue siendo que **el verde no se afirma leyendo este archivo sino sus artefactos**⟧

## Resumen de ejecución

| Fase | Estado | Evidencia / iteraciones |
|---|---|---|
| Preparación documental | AJUSTADA el 2026-09-21 | Lecturas, consultas QMind y validación documental; no es fase de código |
| FASE-A | **EJECUTADA offline el 2026-09-21** (checker + 7 tests en verde + selftest; muestra **BORRADOR**, AC3 parcial por falta de revisión humana) | ⟦Fila rectificada el 2026-09-24 por el bloque C de la orden de calidad: publicaba «PENDIENTE / Sin ejecución», contradicha por el propio §Ejecución de FASE-A de este archivo, por `06-checklist` (AC3 PARCIAL, AC10 FASE-A HECHA) y por `README.md`⟧. Su evidencia quedó commiteada y empujada (`9665c57..51b0793`) |
| FASE-B | **EJECUTADA el 2026-10-03 (OLA 2) y registrada en `docs/contributing/REGISTRY.md` el 2026-10-04 con `--fecha 2026-10-03`** — commits `be8ccec`, `dccbb6a`, `f884ada`, `bcd8d2a`, `4895d04`; rango publicado `4c113de..4895d04`. ⟦Sello 2026-10-04: esta fila abría con «BLOQUEADA POR DEPENDENCIA» y su segunda celda decía «Sin ejecución»; ambas quedaron vencidas por la tanda. El sello del 2026-10-01 que se conserva debajo acertó en el diagnóstico (no era una dependencia técnica sino P1, el *gap* y el mandato) y caducó en el estado: los tres se resolvieron entre el 2026-10-02 y el 2026-10-03⟧ ⟦Sello 2026-10-01 — la causa de esta fila quedó vencida: la dependencia técnica se entregó el 2026-09-24 (las dos rutas presentes). Lo que bloquea FASE-B hoy es P1 (revisión humana de la muestra), la decisión del gap de contrato y el mandato, no una dependencia técnica; ver README §Pendientes priorizados P3⟧ | **15 artefactos en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/`** (medido con `ls`): `import_scanner.txt` (población 822/9825 `.py`, `[SIN-HALLAZGOS]` en la puerta), `integracion.json`, `contract.txt` (estado por AC con su coordenada), `modelos.json`, `mutation.json` (par de mutación 10/10 con causa y restauración por sha256), `budget_tests.txt`, `entorno.json`, `requirements-pilot.txt`, `sdk_contract.txt`, `metrics_tests.txt`, `preflight.json` (401 y luego AUTENTICADA), `corrida_k8_2026-10-03.txt` (dos llamadas reales, `attempts` 1, `usage_normalized.estado = observado`) y la `00-nota-de-ronda-2026-10-03-ola2b.md` con su sello del quinto corte. **Lo que NO se ejecutó**: la comparación de tres brazos y la decisión, que son de C. Iteraciones: la nota de ronda §Cifra canónica publica árbol de trabajo y commiteado con su comando y su HEAD, y el paso 8 (disparo de S14) quedó **NO-EJERCITADO con sus tres crudos** en vez de un verde prestado |
| FASE-C | **EJECUTADA el 2026-10-04 y CERRADA INCOMPLETA** ⟦Sello 2026-10-05 de FASE-RELEASE: las dos celdas de esta fila decían «BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN» y «Sin ejecución»; ambas quedaron vencidas por la propia fase, que tuvo mandato, congelado y presupuesto literal. **Incompleto no es bloqueado ni es éxito**, y esta hoja no lo sube a verde⟧ | **42 artefactos** en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C/`. Estado terminal leído de sus artefactos: `run_status=INCOMPLETO`, `decision=null`, `transfer_status=PENDIENTE`. Tres brazos sobre el mismo conjunto elegible (6 filas de respuestas: 2 por brazo), cuatro envíos de inferencia de un techo de 12 y **cero** de conectividad; un envío de jev cayó por `TypeSafeAPIConnectionError` y su reserva no se liberó como cero. Sus cuatro cambios requeridos (CR-1..CR-4) los cerró FASE-B.2 el mismo día. Iteraciones: cuenta por etapa con proveniencia, no estimación |
| FASE-RELEASE | **EJECUTADA el 2026-10-05 — cierre documental con la deuda visible (checkpoint), no plan cerrado con decisión** | Expediente en `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-RELEASE/`: re-emisión mecánica de `report` y `decide` sobre los registros versionados de C (EXIT 0 y **EXIT 3** = emitido sin decisión), con `sha256_de_los_insumos` idéntico al de FASE-B.2, **0 claves de diferencial** estructural ignorando la fecha y dos corridas byte a byte; batería del piloto **126 passed** con el venv; protocolo **24 passed**; guard real del triaje **62 passed**; cifra canónica **4835** en el árbol y **4835** commiteada en el tip. AC por fila en `06-checklist` y en el §6 de su registro; deudas re-medidas y nuevas en §8 de esa hoja |

## Registro de preparación

La auditoría encontró disparadores B/B+C inconsistentes, circularidad potencial con AC15, comparador textual sin usage, coste sin distinción contable, Paso 0 ausente e índice vencido. El operador ordenó ajustar documentos y confirmó DeepSeek habilitado por defecto / Anthropic sin API. En ese momento no autorizó inferencias ni commits; después pidió explícitamente commitear la preparación antes de ejecutar nada, y entró como `2c966f6`.

Correcciones de diseño:

- A prepara localmente; B propia requiere costura y consumidor verificados offline, admitiendo AC15 semántico parcial. No se modifica el contrato de cero inferencias del hermano.
- DeepSeek queda fijado como comparador efectivo sin fallback. `llm_provider.py` no se modifica; telemetría por la frontera de decisiones.
- AC1–AC7 precisados y AC8–AC12 añadidos para presupuesto, SDK, instrumentos, preparación y estado operativo.
- Corpus humano/saneado, separación por plan, controles de fuga, preregistro, reproducción y costes observados/calculados/facturados diferenciados.
- D6 no exige que gane Jev; cambios de deuda requieren autorización adicional.
- Paso 0 realizado después de la concepción y antes de implementación; no atribuido retroactivamente. Dos consultas MCP a QMind funcionaron y se contrastaron con el corpus local.

## Sonda de instalación

El operador autorizó instalar el SDK el 2026-09-21; en ese momento no estaban autorizados FASE-B, inferencias ni push (el push se pidió y ejecutó después). La sonda corrió en un entorno aislado y **sin red**: `TYPESAFE_API_KEY` se eliminó del entorno del subproceso y se usó una clave literal sintética con `httpx2.MockTransport`, que intercepta la petición dentro del proceso. No se escribieron archivos de plan ni de evidencia: `requirements-pilot.txt` y `entorno.json` siguen siendo artefactos de FASE-B.

| Medición | Valor |
|---|---|
| Entorno | `tmp_test/venv-jev-sdk` (Python 3.13.3, ignorado por git, 28 MB); el SDK no se instaló en `venv/` del proyecto (su pydantic se alineó al pin más tarde ese día, ver §Alineación de pydantic en el venv) |
| SDK | `typesafe-sdk==0.7.0` |
| Resolución de dependencias | httpx2 2.13.0, httpcore2 2.13.0, anyio 4.15.1, pydantic 2.13.5, pydantic-core 2.46.5, tenacity 9.1.4, truststore 0.10.4, typing-extensions 4.16.0 |
| Conflicto que exige aislamiento | pydantic 2.13.5 resuelto contra el pin `pydantic==2.12.5` de `requirements.txt`; en el momento de la sonda el venv del producto tenía `2.12.3` (desajuste preexistente con el pin), alineado a `2.12.5` después — ver §Alineación de pydantic en el venv |
| Interfaz real | `TypeSafeClient(api_key, model, retry, timeout, headers, transport, http_client, base_url)`; `system_one(state, questions, model, retry, timeout, extra_headers, extra_body, response_model)` |
| Reintentos por defecto | `max_retries=2`, `backoff_initial=0.5`, `backoff_max=5.0`, `backoff_jitter=0.25`, `respect_retry_after=True`, `timeout=30.0` (presupuesto total de la llamada) |
| Intentos medidos ante 429 | 3 con defaults; 1 con `max_retries=0` |
| Sin API key | `TypeSafeError` antes de cualquier acceso de red |
| 401 / 429 | `TypeSafeAuthenticationError` / `TypeSafeRateLimitError`, ambos con `.status` |
| 200 sin `usage` | `TypeSafeAPIResponseValidationError`: `usage` es obligatorio en el modelo, no degrada a `null` |
| Noul | `NoulAnswer` expone solo `.noul` (sin confidence); respuestas indexadas por los IDs enviados; `resp.model` = `jev-1.13.0` |

Consecuencia en el diseño: AC8 fija `max_retries=0` como requisito y AC9 aserta clases de error y trata un 200 sin `usage` como fallo, no como coste cero. La reproducibilidad del pin `jev-1.13.0` queda corroborada en el SDK real, no solo en la documentación. La sonda **no** prueba autenticación, cuota, saldo ni calidad de decisiones: sigue vigente `NO-EJERCITADO` para esos aspectos.

## Alineación de pydantic en el venv (post-sonda, mismo día)

**Qué se corrigió:** desajuste preexistente entre `requirements.txt` y el `venv/` del producto, ajeno al SDK de Jev. `requirements.txt` pinea `pydantic==2.12.5` / `pydantic_core==2.41.5` / `pydantic-settings==2.10.1` (bump de seguridad, commit `967b13d`); el venv tenía `2.12.3` / `2.41.4` y `pydantic-settings` **sin instalar**.

**Dirección elegida:** sincronizar el venv **al pin**, no bajar el pin al venv. Bajarlo habría deshecho el parche de CVEs y habría dejado el venv por debajo de `pydantic>=2.12.0` que exige el SDK del hermano. Se verificó que `2.12.5` y `2.41.5` son versiones reales y coherentes (par `2.12.x`↔core `2.41.x`).

| paquete | antes (sonda) | después (alineado) | pin en `requirements.txt` |
|---|---|---|---|
| pydantic | 2.12.3 | 2.12.5 | 2.12.5 |
| pydantic_core | 2.41.4 | 2.41.5 | 2.41.5 |
| pydantic-settings | no instalado | 2.10.1 | 2.10.1 |

**Límites que esto NO cambia:**
- El SDK `typesafe-sdk` / `httpx2` / `tenacity` **sigue sin instalarse** en `venv/` del producto; vive aislado en `tmp_test/venv-jev-sdk`. Esta sonda y la prohibición de AC9/contrato de instalarlo en el entorno principal permanecen vigentes.
- `requirements.txt` **no se modificó**: el pin ya era correcto; lo que estaba desviado era el entorno.
- No se tocó el runtime de producción ni `modules/providers/llm_provider.py`.

**Efecto documental:** las afirmaciones "el venv quedó intacto / no se tocó" de esta preparación se leen ahora en dos sentidos: *SDK aislado* (SIGUE CIERTO) vs *venv sin tocar* (YA NO — se alineó su pydantic). Las citas antiguas quedan re-ancladas aquí y en README §Qué cambió / `09-documentacion-post-proyecto.md` §B.

**Verificación tras la alineación:** `pip freeze` coincide con las tres líneas de `requirements.txt`; `run_all_validations.py --quick` → 11/11 PASSED (sin regresión).

## Validaciones de preparación

Ejecutados el 2026-09-21 con el Python del proyecto y `PYTHONDONTWRITEBYTECODE=1`. No se ejecutó pytest ni el quick de runtime en este ajuste exclusivamente documental; se aplicaron los controles focalizados siguientes.

| Comando | Estado de auditoría anterior al ajuste | Resultado después del ajuste |
|---|---|---|
| `venv/Scripts/python.exe scripts/validate_lesson_capitalization.py` | FAIL: C1/AUSENTE del propio plan | OK: cuatro planes en alcance; este plan acredita cinco fuentes; forma y trazabilidad, no pertinencia |
| `venv/Scripts/python.exe scripts/build_lesson_index.py --check` | FAIL: par de índices vencido | OK: índice fresco, 320 IDs definidos |
| `venv/Scripts/python.exe scripts/validate_plan_citations.py` | No ejecutado en la auditoría anterior | OK: 743 citas históricas, cero nuevas y cero crecimientos; 79 archivos en inventario |
| `venv/Scripts/python.exe scripts/validate_opencode_refs.py` | No ejecutado en la auditoría anterior | PASS: referencias existentes |
| `venv/Scripts/python.exe scripts/validate_plan_closure.py` | No ejecutado en la auditoría anterior | OK: sin declaraciones de cierre contradictorias |

La regeneración mediante `venv/Scripts/python.exe scripts/build_lesson_index.py` produjo 320 IDs definidos, 50 sin definición, 16 análisis y 415 Markdown. Son cifras de este cierre de preparación, no un pin de tests futuros. Una comparación de conjuntos con el JSON de HEAD descartó introducir IDs sin definición: la primera escritura del regex de Q2 generó citas parciales falsas; se reagrupó/re-ejecutó el patrón antes de regenerar, sin editar el índice a mano.

También se comprobó por aserciones locales la igualdad exacta del conjunto AC1–AC12 en maestro/checklist, ausencia de duplicados, existencia de enlaces locales y post-fase/checklist en los cuatro prompts. La revisión cruzada adicional corrigió el literal FALLIDO, situó la congelación final dentro de C antes de evaluar y dejó el modelo efectivo real pendiente hasta las llamadas autorizadas.

Estos checks no verifican pertinencia, saldo, autenticación, exactitud de etiquetas ni que los controles futuros ya existan. La verificación de estructura de ACs/prompts complementa su cobertura limitada.

## Ejecución de FASE-A (offline, 2026-09-21)

Instrucción del operador: "Ejecutar FASE-A". Cero red, cero clientes, cero credenciales; `run`/`decide` se niegan con exit 2 sin instanciar nada (AC11).

**Artefactos creados (NUEVOS):**
- `scripts/evaluate_jev_pilot.py` — modos locales `prepare`/`check` + métricas deterministas. Solo stdlib.
- `tests/quality_gates/jev_pilot/test_jev_pilot_offline.py` — 7 tests; cada guard con par verde/rojo causal.
- `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/{muestra.json,etiquetas.json,protocolo.json}` y `FASE-A/{selftest.txt,muestra_check.json}`.

**Medido:**
- `pytest tests/quality_gates/jev_pilot -v` → **7 passed**; salida y exit code copiados a `selftest.txt`.
- `check` sobre la muestra → `check_status OK` en los 5 guards (schema, content_sha, split_disjoint, labels_not_in_payload, unreviewed_not_frozen).
- Muestra: **BORRADOR**, `counts = {total 4, dev 2, eval 2, excluidos 1}`. Unidad de conteo: parejas (plan, lección); corte: hash determinista de `target_plan` fija el split, garantizando que un plan no aparece en ambos sets.
- Métricas auto-verificadas con valores comprobables por otra vía: `score(3,4)=0.75`; `score(0,0)→ value None, motivo denominador_cero` (no 100 %).

**Frontera humana respetada:** las etiquetas son del agente como candidatos; `etiquetas.review_status = sin_revisar`, `label = null`. No se atribuyó al operador ninguna etiqueta (L-R.4). Los umbrales de `protocolo.json` están en `null` = a-decidir; eso **impide** FASE-C, no se rellenaron.

**No se declaró FASE-A plenamente verificada:** AC3 queda PARCIAL porque faltan revisión humana y umbrales acordados (los artefactos ya están publicados en `origin/master`, push `9665c57..51b0793`). El corpus de 4 pares es exploratorio, muy por debajo del objetivo 60–100 (L-P6.3), y `MUESTRA-INSUFICIENTE` sigue siendo el estado honesto para cualquier comparación.

## Decisiones de diseño y alternativas

| Tema | Decisión | Alternativa no elegida / motivo |
|---|---|---|
| Secuencia | Preparar offline y respetar B/C offline para integrar | API directa anticipada: posible, pero duplica integración y altera el alcance |
| Comparador LLM | DeepSeek explícito | Anthropic: API no habilitada; auto/fallback: contamina la comparación |
| Telemetría | Capturar por la costura la respuesta externa antes de reducirla a texto/decisión | Refactor del wrapper global: innecesario para este experimento y fuera de alcance |
| Calidad | Muestra humana, incertidumbre y salida insuficiente | Mock verde como calidad: solo prueba mecánica |
| Coste | Uso observado, cálculo tarifario y cargo facturado distintos | Precio de lista como coste de corrida: no es consumo medido |
| Semántica de errores | Ejecución fallida con decisión null | RECHAZAR por un 401/timeout: confunde disponibilidad con calidad |
| D6 | Elegibilidad independiente de victoria Jev | Exigir ACTIVAR Jev: no es el disparador original de D6 |

## Lecciones capitalizadas y límites

El efecto sobre el diseño y sus fuentes está en `00-lecciones-capitalizadas.md`. Todavía no hay lecciones de una implementación ejecutada ni cambios medidos en calidad del triaje. No inventar aprendizajes por fase pendiente.

La revisión separó tres contratos: proveedor habilitado, proveedor instrumentado y proveedor ejercitado. La confirmación del operador satisface el primero para DeepSeek, no los otros dos. El reporte de uso solo es fiable cuando sobrevive desde el response hasta el informe y queda atribuido al proveedor realmente usado.

## Seguimientos

Etiquetas/saneamiento humanos, criterios/umbrales, presupuesto, entorno aislado, versiones actuales y permisos: dueños y disparadores en `dependencias-fases.md`. Transferencia D7/D6 no ejecutada. No se dispone todavía de evidencia para adoptar o rechazar Jev. ⟦**Re-escrito el 2026-10-05 por FASE-RELEASE, sobre lo medido y no sobre lo recordado.** De esa lista hay que separar tres estados. **Ya resuelto por el operador**: las etiquetas y el saneamiento humanos (revisor `jhon`, `reviewed_at: 2026-10-02`, `etiquetas.json` en `revisada`), los criterios y umbrales (`protocolo.json` `CONGELADA`, con sus techos escritos teniendo la corrida delante) y las versiones actuales (`typesafe-sdk 0.7.0`, `jev-1.13.0` pedido y devuelto). **Resuelto solo a medias**: el presupuesto — hay techo de llamadas (12), de reintentos (`max_retries=0`) y de timeout (30 s), y no hay gobernanza de dinero (`limites_gasto.usd` es `null`, declarado FUERA DE GOBERNANZA). **Sigue abierto**: la transferencia D7/D6, que no podía ejecutarse sin línea literal que nombre archivos y alcance. Y la última frase quedó mal formulada: **sí hay evidencia para medir y hay instrumento para reproducirla** —los cuatro cocientes, con denominadores separados, emitidos desde los registros—; lo que no hay es **base para adoptar o rechazar**: `denominador_efectivo_de_la_comparacion: 1`, `cobertura_min` 0.5 contra un umbral congelado de 0.95 en los tres brazos, un brazo incompleto por un fallo de transporte y `decision=null`. No es lo mismo «no medido» que «no decidible», y confundirlo es exactamente lo que el contrato quiso evitar⟧

## Cierre del plan — PENDIENTE ⟦El titular se conserva como foto de la preparación; el cierre de 2026-10-05 está en la sección «Cierre FASE-RELEASE», al final de este archivo⟧

Sin inferencias, write-back ni archivado. La preparación quedó comiteada y **empujada** el 2026-09-21: base `99a33d8`, rango `2c966f6..99ac860` en `origin/master`, paridad `0/0` verificada con `git ls-remote` y 7/7 checks del hook en cada commit; la instalación del SDK quedó limitada a un entorno aislado. El cierre futuro exige la revisión de artefactos y los permisos del contrato; una decisión administrativa de no ejecutar debe conservar los AC no ejercitados.

⟦**Cierre documental ejecutado el 2026-09-27, por instrucción escrita del operador (orden de cierre, paso T3), y
solo en su parte documental.** El orden fue el que manda R2.10: write-back a QMind del `10-analisis` y del `CONTEXT`
con declaración durable con **título nuevo** —`10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre offline,
lecciones finales 2026-09-27)`—, verificado por **descarga + sha256 contra el archivo local** y no por el título,
porque el servidor no deduplica por título; después `build_lesson_index.py`, `git mv` a `Archives/`, regeneración
del índice, `validate_opencode_refs.py --fix`, `validate_plan_citations.py --update-baseline` y `--quick`. Se subió
con el CLI de QMind y no con `validate_qmind_writeback.py --upload` porque ese writer fija el título antiguo y
`is_ingested()` decide por nombre del plan, así que no puede publicar un cierre actualizado (límite ya registrado
como deuda en `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`).⟧

**Lo que este cierre NO afirma, y queda donde estaba**: la línea de arriba («Sin inferencias, write-back ni
archivado») describe la auditoría del 2026-09-21 y no se reescribe; las fases B y C de integración no se
ejecutaron; `acceptance` del piloto sigue **NO-EJERCITADO** (proveedor habilitado ≠ proveedor instrumentado ≠
proveedor ejercitado, los tres contratos que separó la revisión); **D7 sigue inactiva** por decisión del operador y
D6 conserva dueño y disparador. Los bloqueantes que sobreviven a este archivado son humanos y de permiso —revisión
de artefactos y consentimiento—, no de código.

⟦**Sello 2026-10-04, sobre el párrafo de arriba sin reescribirlo**: de sus cláusulas, «**las fases B y C de
integración no se ejecutaron**» quedó vencida a medias y hay que separarlas — **FASE-B se ejecutó el 2026-10-03**
(OLA 2; `be8ccec`, `dccbb6a`, `f884ada`, `bcd8d2a`, `4895d04`), con adaptadores y runner en producción de `scripts/`
y sus 15 artefactos en `FASE-B/`; **FASE-C sigue sin ejecutarse**, así que «no hay comparación de tres brazos ni
decisión» y «`acceptance` del piloto sigue NO-EJERCITADO como resultado medido» siguen siendo cierto: la corrida
k=8 del 2026-10-03 fueron **dos llamadas de instrumento** (preflight y techos), no la medición del piloto. Que el
SDK quedara ejercitado con proveedor real no equipara «instrumentado» a «ejercitado en la comparación»: la
distinción de los tres contratos que hizo esta revisión sigue en pie⟧

## Sello 2026-09-30 — las dos filas de §Hitos y evidencia de entrada de `dependencias-fases.md`, que esta sesión no pudo editar

`dependencias-fases.md` de este plan está **protegido** por la orden del 2026-09-21 (su sección «Orden de
cierre: hermano primero» es decisión del operador) y por la orden de esta tanda, que prohíbe editarlo. El
texto protegido no se tocó; lo que sigue es el sello con la medición, y su destino es este análisis por
mandato expreso.

Leídas las dos filas de la tabla de §Hitos y evidencia de entrada contra el árbol de trabajo de hoy, con
`ls` y sin inferir:

| Fila del archivo protegido | Lo que publica | Lo medido el 2026-09-30 |
|---|---|---|
| **Interfaz de decisiones** | `PENDIENTE; archivo ausente` | **el archivo existe**: `scripts/decision_client.py`, 69.503 bytes, con su selección `tests/quality_gates/decision_client/` en **87 passed** y su `--provider-status` respondiendo `NO-CONFIGURADO` (el estado propio de «resuelto sin credencial», no un fallo) |
| **Consumidor de pertinencia** | `PENDIENTE; archivo ausente` | **el archivo existe**: `scripts/triage_lesson_relevance.py`, 42.378 bytes, entregado por FASE-C del hermano `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`, cerrada en su parte offline el 2026-09-24 |

Y la frase con la que la orden de esta tanda señalaba este mismo archivo («no se toca la costura
inexistente») **no está en `dependencias-fases.md`**: está en `01-plan-maestro.md`, al final de §Permisos, y
ahí se selló. Se declara la deriva de la ancla en vez de reubicar la cita a mano sobre el archivo protegido.

**Lo que el sello NO afirma**: que los dos hitos estén cerrados. «Archivo existe» no es «hito verificado»: la
evidencia que esas dos filas piden sigue siendo `AC6–AC9` con scanner/contract/costura y tests reales en disco
para la primera, y `AC10–AC14` más la mecánica de `AC15` con su par verde/rojo para la segunda. Lo que cayó es
el literal «archivo ausente», que es la mitad más inestable de una fila de estado y la que engaña a quien
llega después. La corrección del archivo protegido queda pendiente de su dueño, con esta medición como insumo.

⟦**Espejo 2026-10-01 — deuda S37** («el estado de un plan solo se lee auditando»): su fila, su censo con comando y
fecha, su dueño y su disparador viven en `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md`
§S37, que es la **fuente única**; este plan no la re-transcribe, y como su propio `dependencias-fases.md` está
protegido por orden del operador el espejo viaja en este análisis⟧

## Cierre FASE-RELEASE (2026-10-05) — estado terminal, lecciones nuevas y seguimientos

**Estado terminal: CHECKPOINT DOCUMENTAL CON LA DEUDA VISIBLE**, uno de los dos terminales legítimos que
admite el mandato. No es «plan cerrado con evidencia plena», porque C cerró `run_status=INCOMPLETO` con
`decision=null` y el operador no emitió etiqueta de adopción en esta sesión. Y no es cierre por prosa: cada
magnitud de este párrafo tiene su instrumento y su crudo en
`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-RELEASE/`.

Lo que la certificación **sí** produjo, medido y no recordado:

- La re-emisión mecánica reproduce lo publicado. `report` (EXIT 0) y `decide` (EXIT 3) sobre
  `FASE-C/respuestas.jsonl` con las versiones congeladas de etiquetas, muestra y protocolo:
  `sha256_de_los_insumos` **idéntico** al de FASE-B.2 en sus cuatro insumos, **0 claves de diferencial**
  estructural ignorando la fecha, `decision.md` con **1** línea distinta sobre 42 (la de la fecha), y dos
  corridas de la misma invocación **byte a byte**. Los cocientes: recuperación 1/2 en los tres brazos,
  precisión 1/1 en jev y deepseek y **0/0 = None** en la capa fría, recall 1/1, extremo a extremo 1/2.
- La superficie se verificó con git, no con intención: cero bytes en `scripts/`, `tests/`, `config/`,
  `VERSION.yaml`, `AGENTS.md`, `.cursorrules`, `muestra.json`, `protocolo.json`, `etiquetas.json`,
  `FASE-C/` y los dos árboles del hermano. El sha de disco y el sha del blob de `protocolo.json` casan con
  las dos formas que publicó el registro de C, que es la manera fuerte de decir «no lo toqué».
- El atributo verificable a terceros se re-midió: `revisar_preflight` sobre el preflight de C devuelve
  `ok=true` para el brazo jev, y la selección `tests/quality_gates/lesson_relevance/` corre **62 passed**,
  o sea el guard real del triaje ajeno está ejercitado y no solo descripto.

### Lecciones nuevas de este plan (sesión FASE-RELEASE)

- **L-JEV.R1 — una fase que no tiene la escritura de la fila que niega su hecho deja el hecho ganado y la
  fila mintiendo.** FASE-C congeló `protocolo.json` el 2026-10-04 y su mandato no alcanzaba los documentos
  del plan; ocho frases en presente de seis archivos siguieron diciendo `BORRADOR` hasta este cierre. La
  corrección no es disciplina de quien escribió la fila: es **que el mandato de una fase que muta un
  artefacto gobernado incluya las filas que lo declaran, o declare explícitamente que no las incluye y
  nombre quién lo hará**.
- **L-JEV.R2 — un verificador que depende de la red necesita separar «no casa» de «no pude mirar».** Tres
  corridas del verificador de frescura en la misma sesión pintaron `VENCIDO` un gobernado fresco por cuatro
  descargas que fallaron, y en otra corrida el mismo artefacto salió `FRESCO` con su fuente casando. Contar
  `[SIN-DESCARGA]` antes de pronunciar el veredicto es mandato de esta hoja y la deuda B2-4 dejó de ser
  teórica. Un `NO-EVALUABLE` por instrumento ciego es más honesto que un `DIVERGE`.
- **L-JEV.R3 — un patrón de rango mal formado fabrica verdes vacíos.** Contar shas cortos con siete
  dígitos dio «0 rangos» en una fila que tiene dos. El control no es el conteo, es el patrón.
- **L-JEV.R4 — el preflight que exige «SDK instalado» a un brazo que no tiene SDK corta el brazo que otra
  cláusula declara obligatorio.** `ESTADOS_PREFLIGHT_OBLIGATORIOS` pide `sdk_instalado` verdadero; el
  comparador HTTP registra `NO-APLICA` y el guard lo rechaza. La regla de AC12 («indisponibilidad detiene o
  aplaza, no elimina un brazo») choca con su propio instrumento, y esto solo se ve **corriendo el guard
  contra el artefacto honesto**, no leyendo el artefacto.

### Seguimientos abiertos al cerrar (ninguno absorbido)

| # | Deuda | Dueño | Criterio que la pide |
|---|---|---|---|
| B2-1 | `report` no compara `usage_normalized` contra los techos ni publica `cost_calculated` / `cost_billed` | `scripts/evaluate_jev_pilot.py` (`report`) | AC4 |
| B2-1c | El exceso de `tokens_out` observado por C (145) contra el techo congelado (139) no lo publica ningún instrumento | `scripts/evaluate_jev_pilot.py` (`report`) | AC4 y H12 de FASE-B.2 |
| B2-2 | `metrics()` sin productor: 1 definición, 0 llamadas desde código | contrato de salida de FASE-A | AC10 |
| B2-3 | Margen apoyado en 1 par utilizable; el umbral 0.25 no discrimina con denominador 2 | re-apertura de C, decisión del operador antes de correr | AC5 |
| B2-4 | Descarga fallida pinta `VENCIDO` un gobernado fresco | `scripts/verify_qmind_context_freshness.py` | declarada por C y **materializada** en este cierre |
| B2-5 | Transferencia D7/D6 | `transfer_status: PENDIENTE`, solo con instrucción literal | AC7 |
| REL-1 | El guard del `run` corta el brazo comparador por pedir `sdk_instalado` verdadero | `scripts/evaluate_jev_pilot.py` (`revisar_preflight`) | AC12 |
| REL-2 | FASE-C y FASE-B.2 sin entrada en `REGISTRY.md`; el escritor corrió una sola vez, por FASE-RELEASE | operador, con la fecha real de cada cierre | Paso 4.5.1 del executor |
| REL-3 | Tres frases en presente sobre el congelado del protocolo, fuera del listado de ediciones de este mandato (`01-plan-maestro.md` y dos en `05-prompt-inicio-sesion-fase-B.md`) | documentos del plan | L-JEV.R1 |
| REL-4 | `05-prompt-inicio-sesion-fase-RELEASE.md` sigue en el índice del README sin señalar que el mandato de 2026-10-05 lo venció | README §Índice | §1 del mandato de RELEASE |
| REL-5 | Rojo dependiente del orden de colección: verde aislado, rojo en la suite completa (lo imprime el check [16/18], no el quick) | `tests/quality_gates/jev_pilot/` con su conftest | AC2 y AC12 |

**Permisos al cerrar esta hoja**: commit, push, escaneo L3 y write-back a QMind **no ejecutados y no
ofrecidos**; son actos del operador, cada uno con su instrucción escrita. Esta sesión no ofrece la fase
siguiente ni re-abre C.

⟦**Anotación aditiva del sello (mismo 2026-10-05)**: el operador autorizó «Git Commits» y el trabajo quedó
commiteado en `39717b1`, verificado en su propio árbol con un clon limpio. **Push, L3 y write-back siguen sin
ejecutar**, así que el resto del párrafo sigue vigente. El detalle medido vive en el §12 del registro de
FASE-RELEASE.⟧

---

⟦**Anotación dictada por el operador el 2026-10-05 (mandato CIERRE-DE-ABANICO, punto D3): la etiqueta de
adopción de AC5 se emite y es MUESTRA-INSUFICIENTE.**

La base no es una opinión nueva: es la que publica el propio instrumento. `FASE-RELEASE/decision.json`, en
`literales_y_su_estado`, tiene ese literal con estado «EXCLUIDA por la regla congelada; ponible por el
operador» y base «suficiencia_minima se cumple (0.5 >= 0.5) en el denominador congelado, pero el denominador
efectivo de la comparación es 1 par con elección utilizable en los dos brazos». El `informe_comparativa.json`
de la misma hoja mide el conjunto: 4 pares, 2 pertinentes, 2 importantes elegibles y denominador 2 en la
señal S3. Con un par utilizable el umbral no discrimina, que es exactamente lo que registra la fila B2-3 de
la tabla de arriba.

**La salida que manda la regla congelada está escrita en su propia nota:** «si el operador la emite aun así,
la salida es muestra nueva y nunca re-etiquetar la congelada». Por eso esta anotación no toca
`protocolo.json`, `muestra.json`, `etiquetas.json` ni el `decision.json` de FASE-C, ni re-indexa nada: lo que
queda abierto es la muestra, con su dueño ya declarado (re-apertura de C con decisión del operador antes de
correr). Ninguna recomposición de los pares publicados convierte 1 par utilizable en 2.

**Qué cambia en esta hoja y qué no.** La tabla de seguimientos queda intacta. Este párrafo sí vence la frase
«write-back sigue sin ejecutar» del párrafo anterior: la publicación de esta hoja por CLI está autorizada por
el mismo mandato (punto D3), y su verificación —descarga y sha256 de la fuente nueva, con las fuentes previas
intactas— queda consignada en el registro de FASE-RELEASE y en los crudos de la tanda CIERRE-DE-ABANICO,
porque un documento publicado no puede alojar la evidencia de su propia publicación.⟧

⟦**Anotación aditiva del sello (SESIÓN 2 del piloto JEV, 2026-10-09): B2-1, B2-1c, B2-1e y B2-1d quedan
curadas, y el exceso real era de DOS brazos.**

**Qué se estampa y cómo.** La tabla de «Seguimientos abiertos al cerrar» de arriba queda escrita como la
cerró FASE-RELEASE: la convención es anotar, no reescribir. Las cuatro filas que nacieron ahí, o en la hoja
de cura `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/CURA-B2-1-2026-10-09/`, están hoy cumplidas por el
instrumento, y cada una con su prueba en el árbol. B2-1, B2-1c y B2-1e se publicaron en el commit `ec69570`,
dentro del rango ya empujado `5249aed..fb13108`; B2-1d se cura en esta sesión y su sello viaja en los commits
que se autorizan abajo:

| fila | qué decía la deuda | qué hace el instrumento hoy | dónde está la prueba |
|---|---|---|---|
| B2-1 | `report` no comparaba `usage_normalized` contra los techos ni publicaba coste | `contabilidad_de_coste()` publica por brazo `tokens`, `contra_techos`, `cost_calculated` y `cost_billed` | `tests/quality_gates/jev_pilot/test_jev_pilot_report_coste_b2_1.py`, 24 funciones |
| B2-1c | el exceso de 145 contra el techo congelado de 139 no lo publicaba ningún instrumento | veredicto `EXCESO` con `exceso_sobre_el_techo`, las filas fuera nombradas y la señal mecánica `S6` | el mismo archivo, con su mutante M1 |
| B2-1e | `reservar_presupuesto` cortaba por llamadas y reintentos pero nunca comparaba los tokens observados antes del envío siguiente | corte `techo_rebasado_de_<campo>:<observado>><techo>`, comparación de tipo y valor, frontera `>` | `test_jev_pilot_run_guards.py`, 31 funciones, con el mutante M3 |
| B2-1d | la cuenta de etapa la persistía solo `run`: un brazo despachado por un arnés contaba en su memoria y no publicaba | `registrar_envio_en_cuenta()` suma y publica en el mismo acto, y por envío | `test_jev_pilot_cuenta_etapa_b2_1d.py`, 9 funciones; contrafactual corrido contra el runner versionado en `fb13108` → **7 rojos / 2 verdes**, restauración verificada por sha256 (`4a26552237be9c84`) |

**La corrección de fondo: el exceso era de dos brazos, no de uno.** La deuda B2-1c citaba un solo rebase
(jev 145 sobre 139, +6). Medido sobre los registros versionados de FASE-C, **dos** brazos rebasaron el techo
de salida: jev con 145 (+6) y el comparador deepseek con **158 (+19)**, en dos filas distintas. Ningún
instrumento lo decía. Crudo: `CURA-B2-1-2026-10-09/05-cuenta-publicada-vs-cuenta-al-cerrar.txt`.

**Y la cuenta publicada mentía a la baja: decía 2 llamadas cuando la real al cerrar era 4.** El brazo
comparador no pasó por `run`: lo despachó `FASE-C/12-arnes-correr-deepseek-eval.py`, que reimplementaba la
misma aritmética pero no escribía `consumo.json`. Medido en disco: la cuenta publicada quedó en
`llamadas_usadas: 2 / tokens_out_max: 145` (la foto del brazo jev) mientras `registro_deepseek.json` estampa
`cuenta_al_salir` con `llamadas_usadas: 4 / tokens_out_max: 158`. Esa divergencia es la fila B2-1d, y se cura
aquí: la suma y la publicación son un solo acto, así que contar sin quedarse en disco deja de ser un camino.
No se tocó la puerta del comparador (`scripts/decision_client.py`) ni `modules/providers/llm_provider.py`;
elegir «que el brazo pase por `run`» habría duplicado la costura, que el mandato de FASE-B prohíbe.

**Medición con la que se estampa.** `tests/quality_gates/jev_pilot` → **182 passed** (173 al abrir la sesión +
9 de la batería nueva); `scripts/validate_wiring.py --check` → EXIT 3 con `cobertura.archivos_en_alcance`
714 → 715 por el `.py` nuevo, re-publicado con el writer y vuelto a `--check` → **EXIT 0**;
`scripts/run_all_validations.py --quick` → **13/13**. Cero llamadas de inferencia: el guard de sockets del
`conftest.py` estuvo armado toda la sesión.

**Lo que esta anotación le hace a la hoja publicada en QMind, declarado.** El sha256 de disco **antes** de
editar era `ee40f5ee52ffd6a27ccce262509b235495cbf4feedc03e676cd968c7ace67755`; el de **después** no puede
vivir en esta hoja (un documento no aloja la evidencia de su propia publicación) y queda en
`CURA-B2-1-2026-10-09/11-crudo-estampado-y-frescura.txt`. Con este cuerpo nuevo,
`scripts/verify_qmind_context_freshness.py --strict` va a imprimir `[VENCIDO]` sobre `10-analisis`: **es el
vencido real**, el caso en que el cuerpo en disco ya no casa con la fuente publicada y la única salida es el
write-back (punto 4 del mandato). **Cifra re-anclada por medición, no por el mandato:** el mandato decía
«población 59 → 60», y medido con `scripts/verify_qmind_context_freshness.py --strict` el notebook
`iah-cli-lecciones` tiene **61 fuentes publicadas** (el servidor responde 4 la nombran por título y ninguna
casa con `sha_disco`), así que la subida de esta hoja va de **61 → 62**. El 59 es el antecedente publicado por
la tanda del 2026-10-08, no el estado de hoy. No es el falso vencido que curó B2-4: aquel era
`NO-EVALUABLE` cuando la fuente no se descargaba, y ese camino sigue abierto y etiquetado por su cuenta.
De hecho esta misma corrida trae **4 `[SIN-DESCARGA]`** junto al `[VENCIDO]`: el rojo manda sobre la
abstención, y la racha de descargas fallidas queda en el crudo.
Hasta que el write-back ocurra, el rojo es esperado y tiene dueño; no se apaga el verificador.⟧
