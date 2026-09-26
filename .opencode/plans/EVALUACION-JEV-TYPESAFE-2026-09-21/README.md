# EVALUACION-JEV-TYPESAFE-2026-09-21

**Estado: FASE-A EJECUTADA offline el 2026-09-21 (instrumento `scripts/evaluate_jev_pilot.py` + suite auto-verificada en verde; muestra en **BORRADOR**). Sin inferencias ejecutadas. Los artefactos de A quedaron **publicados en `origin/master`** (push `9665c57..51b0793`; 7/7 checks del hook).** Autorizado y hecho: ajustar el plan, commitear/empujar la preparación, instalar el SDK en entorno aislado para una sonda sin red, y ejecutar/commitear/empujar FASE-A offline. Sigue sin autorización: ejecutar FASE-B o posteriores, llamar a APIs de inferencia, write-back a QMind y archivado.

Objetivo: medir si Jev mejora el triaje aditivo de pertinencia frente a la búsqueda fría y **DeepSeek**, con corpus propio saneado y coste acotado. DeepSeek es el proveedor habilitado por defecto según confirmación del operador del 2026-09-21. **Anthropic no tiene API habilitada, queda fuera del piloto y no es un fallback.** No se modifica `modules/providers/llm_provider.py`.

## Qué cambió en la preparación

- Se distingue preparación offline de integración: A puede preparar la muestra; B requiere la costura del hermano y C implementada/verificada offline. No se exige aceptabilidad real para comenzar a medirla.
- El cierre offline de C del hermano puede conservar AC15 parcial y `acceptance = NO-EJERCITADO`. No se levanta su prohibición de inferencias ni se cambia su orden de fases.
- El comparador queda fijado en DeepSeek, con captura de usage/modelo efectivo detrás de la costura. El wrapper actual devuelve solo texto; no sirve como instrumento de coste y no se usa su selección automática.
- Se concretan muestra, saneamiento, aislamiento por plan, métricas, presupuesto, errores y los instrumentos que los producirán. Todos siguen sin implementar.
- La documentación actual de Jev sí publica límites de contexto; Noul no ofrece confidence separada y la calidad en español se debe medir, no heredar del inglés.
- Sonda ejecutada en el SDK real 0.7.0 (entorno aislado, `httpx2.MockTransport`, cero red): el transporte es inyectable, los reintentos por defecto dan **3 intentos** ante un 429 y un 200 sin `usage` lanza error de validación. Por eso AC8 exige `RetryPolicy(max_retries=0)` y AC9 aserta clases de error en lugar de `usage = null`. El SDK **no** se instaló en el `venv` del producto (resuelve pydantic 2.13.5 por encima del pin `2.12.5`). Corrección posterior del mismo día: el `venv` ya no está "intacto" en el sentido estricto — se alineó su pydantic al pin (`2.12.3`→`2.12.5`, core `2.41.4`→`2.41.5`, +`pydantic-settings 2.10.1`) para cerrar un desajuste preexistente entre `requirements.txt` y el entorno. `requirements.txt` y el aislamiento del SDK no se tocaron. Ver `10-analisis-post-implementacion.md` §Alineación de pydantic en el venv.
- D6 se evalúa por aceptabilidad y candidatos nuevos, aunque gane DeepSeek; adoptar Jev y modificar la deuda del hermano son decisiones distintas.
- Se subsana el Paso 0 ausente y se incorpora la preparación ejecutora. No se atribuye a la concepción original una consulta realizada después.

## Estados y dependencias

| Fase | Objetivo | Estado |
|---|---|---|
| FASE-A | Muestra humana/saneada, protocolo y checker offline | **EJECITADA offline 2026-09-21**: checker+métricas en verde (AC10); muestra **BORRADOR** con etiquetas y umbrales pendientes de humano (AC3 parcial) |
| FASE-B | Jev/DeepSeek detrás de la costura, SDK y controles probados sin red | **SIN AUTORIZACIÓN PARA EJECUTARLA y sin sus dos bloqueantes humanos resueltos.** ⟦Re-medido el 2026-09-25 por la conciliación final de la orden de calidad: esta fila decía «BLOQUEADA POR DEPENDENCIA TÉCNICA … lo que falta es `triage_lesson_relevance.py` (FASE-C del hermano, sin mandato)». **Esa dependencia quedó entregada el 2026-09-24** (piloto FASE-C del hermano, `5817edd`)⟧. Lo que **sí** la bloquea hoy: la **decisión humana de revisión de la muestra** (P1), la **decisión del *gap* de interfaz** de §Dependencia y **su propio mandato**, que nadie ha dado. `acceptance = NO-EJERCITADO` del hermano **no** la bloquea y **no** se levanta su prohibición de inferencias |
| FASE-C | Comparación autorizada y decisión, sin cambios de código | BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN (necesita el congelado de B, el preflight de autenticación/cuota y presupuesto escrito) |
| FASE-RELEASE | Revisión de evidencia y cierre documental | PENDIENTE |

Dependencia externa: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. ⟦Re-medido el 2026-09-24 por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`; la premisa P2 de la concepción («no existen») quedó vencida **a medias** ese día y quedó **vencida del todo el 2026-09-24 con el piloto FASE-C del hermano** (re-medido y barrido en la conciliación final del 2026-09-25: hoy **las dos rutas existen**)⟧:

| Interfaz | Estado en el árbol al 2026-09-24 | Qué significa para JEV |
|---|---|---|
| `scripts/decision_client.py` | **existe** — entregada por FASE-B del hermano y remediada por su bloque A (`fdd397f`) | La puerta está. Su lectura vigente se hace con sus propios modos de solo lectura, no con este párrafo |
| `scripts/triage_lesson_relevance.py` | **existe y está versionada** — es el producto del piloto **FASE-C del hermano**, ejecutado y cerrado el **2026-09-24** con mandato propio; sus 37 rutas propias entraron en `5817edd` ⟦**esta celda decía «NO existe — FASE-C del hermano sigue sin ejecutar»; quedó vencida el 2026-09-24 y se barre en la conciliación final de la orden de calidad, 2026-09-25. La entrega es del hermano, no de JEV⟧ | **La puerta técnica B+C del hermano está entregada.** Su `acceptance = NO-EJERCITADO` (proveedor falso) sigue siendo **la entrada esperada**, no un bloqueo: AC15 semántico y D6 viajan así a cualquier comparación posterior. **Entregada la dependencia ≠ autorizada esta fase**: FASE-B propia sigue sin mandato, y sigue bloqueada por **P1 (revisión humana de la muestra)** y por la **decisión del *gap* de interfaz** de §Dependencia |

Comandos con los que se re-mide al abrir la fase (no copiar esta tabla): `ls scripts/decision_client.py scripts/triage_lesson_relevance.py`, `./venv/Scripts/python.exe scripts/decision_client.py --help`, y las selecciones `tests/quality_gates/decision_client/` del hermano. Un estado escrito no sustituye evidencia de tests y artefactos.

**Tres cosas que no son lo mismo y este plan mantiene separadas** (⟦orden §4.C, fila `JEV`⟧):

- **Dependencia técnica**: FASE-B propia necesita la puerta **y** el consumidor C del hermano implementados y verificados offline, con AC10–AC14 y la parte mecánica de AC15 con evidencia. **Hoy están los dos**: `decision_client.py` (FASE-B del hermano, remediada en `fdd397f`) y `triage_lesson_relevance.py` (piloto FASE-C, cerrado y versionado el 2026-09-24 en `5817edd`). ⟦Conciliación 2026-09-25: esta viñeta decía «Hoy falta C.»⟧ **Cumplida la dependencia técnica no se cumple ningún permiso**: sigue valiendo que esto «no se arregla adelantando trabajo ni duplicando la costura», y sigue valiendo que FASE-B propia **no está autorizada**.
- **Gobernanza (orden de cierre e índice)**: la regla del hermano que se cierra primero —`dependencias-fases.md` §Orden de cierre— serializa la pareja `.opencode/LECCIONES-INDEX.md` / `.opencode/lecciones_index.json` y el write-back. **No es una dependencia técnica nueva**: `D` y el `RELEASE` del hermano **no** son precondición de FASE-B propia, y postergar la integración hasta cerrar al hermano es cuestión de orden, no de posibilidad. Esta distinción la fijó el operador el 2026-09-21 y no se reinterpreta desde aquí.
- **Aceptabilidad semántica con proveedor real**: `acceptance = NO-EJERCITADO` y AC15 parcial del hermano **son la entrada esperada**, no un bloqueo circular. Lo semántico se mide en FASE-C propia, con su autorización y su presupuesto.

**Gap de contrato medido, declarado en vez de acomodado.** `01-plan-maestro.md` §Interfaz exige al piloto once campos por llamada. Contrastados el 2026-09-24 contra el `decision_client.py` vigente: la puerta **sí** expone lo efectivo (`proveedor`, `modelo`, `usage` con `input_tokens`/`output_tokens`, `request_id`), pero **no** expone `provider_requested`, `model_requested`, `usage_normalized`, `elapsed_ms`, `attempts` ni `error_kind`. Buena parte ya tiene respuesta dentro del propio plan: la tarea 5 de FASE-B asigna el **ledger de intentos** y la contabilidad al *runner* `evaluate_jev_pilot.py`, no a la puerta. Lo que queda como decisión es la pareja «pedido vs efectivo» y el uso normalizado: **extender la costura del hermano de forma aditiva y compatible con sus consumidores, o producir esos campos en el runner**. Ambas salidas tienen coste y ninguna es «escribir un segundo cliente» — eso está prohibido —, ni recortar AC1/AC2 del piloto para que el gap desaparezca. Al abrir FASE-B se lee la interfaz real, se documenta el delta y, si bloquea, **se deja checkpoint y se pide decisión** (maestro §Interfaz).

Dos fases de implementación (A/B) y una de medición (C): no aplica una FASE-VERIFY adicional por el criterio de número de implementaciones del executor. C y RELEASE sí revisan la evidencia cruzada.

## Pendientes priorizados (orden de ejecución)

Cada ítem conserva su puerta de autorización propia: "ejecutar" solo lo inmediatamente siguiente, nunca la cola. Re-medir HEAD/dependencias al abrir cada uno.

| # | Pendiente | Estado hoy | Puerta (qué lo desbloquea) | Tipo |
|---|---|---|---|---|
| P0 | Commitear la corrección del punto 4 + re-anclajes (README, `04-contrato`, `09-documentacion`, `10-analisis`) | **Completado** — corrección del punto 4 + pendientes publicados en `origin/master` (push `03b9929..60cce03`, hook 7/7) | Sin puerta pendiente | Higiene documental |
| P1 | FASE-A: muestra humana/saneada, protocolo y checker **offline** | **Parcialmente hecho**: checker+métricas en verde; muestra **BORRADOR** (4 pares), etiquetas `sin_revisar` y umbrales nulos; **publicado en `origin/master`** (push `9665c57..51b0793`) | Falta: designar revisor humano que etiquete y acordar umbrales del protocolo para congelar. No bloquea B/C para preparar, pero sí para congelar | Ejecución (offline) |
| P2 | Re-medir la dependencia externa `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (B/C offline, AC15 parcial) | **Re-medida el 2026-09-24, VUELTA A MEDIR el 2026-09-25 y re-medir al abrir B**: `decision_client.py` **entregada**; `triage_lesson_relevance.py` **entregada también** — el piloto FASE-C del hermano se ejecutó y cerró el 2026-09-24 y sus rutas están versionadas (`5817edd`), de modo que verificación por `ls` da **dos rutas presentes**. ⟦Esta fila afirmaba «`triage_lesson_relevance.py` **ausente** porque FASE-C del hermano no se ejecutó»; vencido⟧ Un estado escrito no sustituye tests: al abrir B se corre la selección del hermano, no se cita esta celda | Al abrir B. **Ya no falta ninguna ejecución ajena**: lo que falta es verificación propia + **P1 humano** + la decisión del gap + **el mandato de B** | Verificación |
| P3 | FASE-B: Jev/DeepSeek tras la costura, SDK y controles probados **sin red** | BLOQUEADA (por **P1 humano**, por la **decisión del gap de contrato** de §Dependencia y por **falta de mandato**: esta conciliación **no** la autoriza). ⟦Antes figuraba además «P2 — falta C del hermano»; esa dependencia se entregó el 2026-09-24⟧ | A con muestra/protocolo congelados + P2 verde; entorno aislado e instalación autorizados; `requirements-pilot.txt` y `entorno.json` se congelan aquí. **No se destraba duplicando la costura ni debilitando el piloto, y no se destraba sola porque el hermano haya cerrado** | Ejecución (offline) |
| P4 (portón de P5) | Preflight de autenticación/cuota/saldo de Jev (AC12/AC8, etiquetadas `B/C`) | **NO-EJERCITADO** (sonda con clave sintética y cero red) | No es fase propia: es el primer paso de FASE-C. Exige el cliente con `RetryPolicy(max_retries=0)` de B antes de llamar (defaults = 3 intentos ante 429, gastarían cuota sin contabilidad) + autorización literal y presupuesto | Medición (con red) |
| P5 | FASE-C: comparación autorizada fría/DeepSeek/Jev y decisión, sin cambios de código | BLOQUEADA (por P3, P4 y autorización) | Runner offline verificado; muestra/protocolo versionados; hashes y límites finitos | Medición (inferencias) |
| P6 | Write-back a QMind | SIN PERMISO | Tras evidencia de C; re-leer la interfaz del writer antes de publicar | Publicación |
| P7 | Archivado del plan + regeneración fresca del índice | SIN PERMISO | Después del write-back; nunca antes | Cierre |

Hecho fuera de git y sin puerta pendiente: la alineación del pydantic del `venv/` al pin (`2.12.3`→`2.12.5`, core `2.41.4`→`2.41.5`, +`pydantic-settings 2.10.1`); `requirements.txt` y `llm_provider.py` intactos, SDK sigue aislado en `tmp_test/venv-jev-sdk`.

## Índice

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): consultas, ocho lecciones aplicadas al diseño, tres descartes y límites.
- [Plan maestro](01-plan-maestro.md): premisas, AC1–AC12, APIs, protocolo y contabilidad.
- [Contrato](04-contrato-ejecucion.md): permisos, errores, presupuesto y post-fase.
- [Dependencias](dependencias-fases.md): hitos, decisiones pendientes y conflictos.
- [Checklist](06-checklist-implementacion.md): AC, fase, artefacto y estado.
- Prompts: [A](05-prompt-inicio-sesion-fase-A.md), [B](05-prompt-inicio-sesion-fase-B.md), [C](05-prompt-inicio-sesion-fase-C.md), [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md).
- [Documentación acumulativa](09-documentacion-post-proyecto.md) y [análisis de ejecución](10-analisis-post-implementacion.md).
- [Contexto de evaluación](../../context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md): fuentes, alternativas y revisión de viabilidad.

## Límites

Fuera de alcance: Tribunal, gates, hooks, `run_all_validations.py`, VERSION.yaml, `.agents/`, configuración central, pipeline hotelera, material del cliente y cambios al proveedor LLM de producción. La exactitud del write-back de QMind no se evalúa con Jev.

No se edita ningún plan vivo ajeno. AC7 solo contempla una transferencia futura, con instrucción literal y alcance delimitado para D7/D6. Sin permiso, permanece PENDIENTE aquí.

No se imprimen ni persisten credenciales. Tener acceso a una API no autoriza llamadas. Instalación, inferencias, commit, push, write-back y archivado se solicitan por separado. No hay presupuesto de inferencias aprobado ni muestra versionada en esta preparación.

## Inicio de la siguiente sesión

⟦Reescrito el 2026-09-24 por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`⟧. **Este bloque
ofrecía todavía «Ejecuta únicamente FASE-A» con la advertencia de no crear `decision_client.py` por
adelantado, cuando A está ejecutada desde el 2026-09-21 y la costura la entregó el hermano.** Un arranque
así no estaba desactualizado de adorno: abría una sesión a repetir una fase cerrada y a evitar un archivo
que ya existe. La cabecera de este README y la fila de fases de `dependencias-fases.md` sí decían la
verdad; el bloque pegable, no. **Precisión sobre el archivo protegido** (no se edita, se declara): su
cabecera se auto-fecha («Estado **al ajustar el 2026-09-21**») y su tabla de hitos se auto-etiqueta
«**Estado inicial**», así que ninguna de las dos afirma nada sobre hoy y ninguna queda refutada por la
ejecución de A. Lo que de él sigue vigente es lo que no depende del calendario: su §Cadena, el §Orden de
cierre (hermano primero) y sus §Decisiones pendientes con dueño y condición.

**Ninguna fase de este plan es ejecutable hoy**, y las razones son de tres tipos distintos (ver §Tres
cosas que no son lo mismo arriba). Lo que sí tiene dueño y no requiere red ni SDK es la decisión humana
de la muestra. Texto para una sesión de **preparación y decisión**, no de ejecución de fase:

```text
Trabaja en C:/Users/Jhond/Github/iah-cli sobre el plan
.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/.
No ejecutes ninguna fase de este plan: FASE-A ya está ejecutada offline (2026-09-21, muestra en
BORRADOR) y FASE-B sigue bloqueada.
Re-mide antes de escribir nada: git status --porcelain, git rev-parse --short HEAD,
`ls scripts/decision_client.py scripts/triage_lesson_relevance.py`,
`./venv/Scripts/python.exe scripts/decision_client.py --help` y la selección
`tests/quality_gates/decision_client/`. No copies el estado de este bloque: es un antecedente fechado.
Lo que puedes hacer en esta sesión, cada cosa con su puerta:
1) Preparar la decisión humana de P1: dejar disponible la muestra BORRADOR con sus etiquetas `sin_revisar`
   y los umbrales del protocolo propuestos y justificados, para que una persona designada etiquete y
   acuerde. No te atribuyas una etiqueta humana ni congeles la muestra: sin revisión humana explícita
   queda BORRADOR.
2) Documentar el delta de contrato de §Gap de contrato medido (campos que el piloto exige y la puerta no
   expone) con dos salidas y sus costes, para que el operador elija: extender la costura del hermano de
   forma aditiva y compatible con sus consumidores, o mover el ledger de intentos y el tiempo por llamada
   al runner propio de JEV. Prohibido: crear una segunda costura, duplicar `decision_client.py`, o
   recortar AC1/AC2 del piloto para que el gap desaparezca.
3) Verificar la exclusión de Git del entorno aislado (`tmp_test/venv-jev-sdk`) con `git ls-files tmp_test`
   y el check de wiring que lo toca. No instales nada.
No llames a ninguna API, no actives proveedor, no autentiques credenciales, no instales SDKs, no
escribas credenciales ni sus valores en documentos, no hagas commit ni push, no toques
`modules/providers/llm_provider.py`, `requirements.txt` ni `VERSION.yaml`.
No edites `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`: su sección
«Orden de cierre: hermano primero» es decisión del operador del 2026-09-21 y ese archivo esta protegido.
Deja checkpoint con lo pendiente y su dueño.
```
