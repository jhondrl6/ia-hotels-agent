# Orden de cambio — Calidad y coste del proceso de ejecución

**Estado: CERRADA EN SU ALCANCE APROBADO por decisión escrita del operador el 2026-09-25** — criterio y
límites en §6 («Criterio de cierre»), y las cuatro firmas que ese cierre pide están en la misma casilla:
bloque A **bajo «Sin publicar»**, `DOMAIN_PRIMER` **declarado y no alineado**, los dos defectos de writers
**con dueño y disparador como S17/S18** ⟦(curados el mismo 2026-09-25 en una sesión con mandato de código:
el cierre los declaró sin curar, que era lo pedido; ver §6, casilla 3 de «Firmas del cierre»⟧, y
`L-VCF-10…14` **pendientes con su dueño**. Cerrar la orden
**no** afirma commit ni push, ni termina los cuatro planes: lo que quedó sin permiso sigue siendo el
momento remoto (D8/D9), el archivado, el commit y el push.

Historial del alcance que se cierra: bloque A ejecutado y conciliado (§5-bis/§5-ter); B, exclusivamente
según §13 de su fuente única de resultados; bloque C AUTORIZADO Y EJECUTADO en su parte documental el
2026-09-24 (§4.C y `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`);
piloto FASE-C EJECUTADO Y CERRADO el 2026-09-24 con mandato propio (§6 y `evidence/…/FASE-C/`); FASE-D
EJECUTADA Y CERRADA el 2026-09-24 con mandato propio (`evidence/…/FASE-D/`) y FASE-RELEASE **EJECUTADA Y
CERRADA EN SU PARTE OFFLINE el 2026-09-25** con la release **4.78.0** (`evidence/…/FASE-RELEASE/`). Las
cinco fases del plan estaban corridas antes de este cierre.

**⟦Conciliación final 2026-09-25 — cuatro momentos que no se funden⟧.** Toda esta orden distingue, y
esta conciliación vuelve a exigir que se distinga, cuatro estados distintos por trabajo:
**(1) implementación ejecutada**, **(2) evidencia escrita en el árbol de trabajo**, **(3) commit**,
**(4) publicación (push / QMind)**. Decir «cerrada la fase» afirma (1) y (2) con su expediente; **no**
afirma (3) ni (4). Qué está en cada momento hoy, medido y no supuesto:

| Momento | Dónde se lee el estado vigente |
|---|---|
| (1) implementación | `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md`, tabla de fases (**A/B/C/D y RELEASE cerradas**, la última en su parte offline el 2026-09-25); `09-documentacion-post-proyecto.md` §D para las métricas por fase |
| (2) evidencia local | `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/<FASE>/` de cada fase, incluida `FASE-D/carga.json` |
| (3) commit | **se mide, no se cita de memoria**: `git status --short` y `git ls-files <ruta>`. Al 2026-09-25 `scripts/triage_lesson_relevance.py` está rastreado (entró en `5817edd`) y `scripts/build_phase_briefing.py` **no**: el producto de FASE-D vive solo en el árbol de trabajo. Los documentos de cierre de C, el par de índice y los `.md` de los cuatro planes también están fuera del commit |
| (4) publicación | **se mide**: `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD`. El antecedente empujado (`da382b1..5817edd`, 2026-09-24) no describe el remoto de hoy |

El resto del encabezado es historia de la orden: cada afirmación fechada se conserva como **antecedente**
y pierde su carácter de instrucción vigente donde la ejecución posterior la dejó vencida.

**El cierre de esta orden (2026-09-25) no mueve los momentos (3) ni (4)**: añade documentos y su
expediente, no commitea ni empuja. Que siga siendo cierto que el producto de FASE-D
(`scripts/build_phase_briefing.py`) **no** está rastreado y que los documentos de cierre de C, D y RELEASE,
el par del índice y esta propia orden están fuera del commit, se re-mide con los dos comandos de la tabla
anterior; ninguna fila de este documento lo fija como cifra vigente.

El dictamen de §12 del resumen también se retiró el 2026-09-24 por insuficiencia de evidencia.
El estado y la aceptación vigentes se deciden exclusivamente en **§13 de la fuente única de resultados**
(enlazada abajo); §1–§12 y los demás dictámenes retirados se conservan como antecedentes rectificados. El árbol de B sigue **SIN commitear** (el mandato prohíbe
commit/push). El bloque C (enmiendas prospectivas a los cuatro planes) se ejecutó el 2026-09-24 **solo
en su parte documental**; ⟦**antecedente vencido el mismo 2026-09-24**: «el piloto FASE-C sigue PENDIENTE
de su autorización y no se inició» describía el árbol antes de su propio mandato; el piloto se ejecutó y
cerró ese día (§6) y **FASE-D también**⟧.
B se autorizó y ejecutó el 2026-09-23 y dos dictámenes sucesivos lo declararon concluido; **ambos
quedan retirados** y se conservan únicamente como antecedentes rectificados (§4.B y
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/00-resumen-bloque-B.md`).
Su fuente única de resultados es ahora
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`.
**El árbol de B está SIN commitear (el mandato prohíbe commit/push).** El bloque C (enmiendas
prospectivas a los cuatro planes) se autorizó y ejecutó el **2026-09-24 en su parte documental**, sin
commit ni push (el mandato de esta sesión también los prohíbe); su resumen único está en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`.
El **piloto FASE-C de CONTEXTO** queda descrito por esta redacción solo hasta el momento de las enmiendas:
⟦**antecedente vencido el 2026-09-24**: «sigue PENDIENTE: no se ejecutó, no se autorizó»⟧ — se autorizó con
mandato propio y **se ejecutó y cerró el 2026-09-24**, con su expediente en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` y su lectura en §6. ⟦**Vencido el resto de esta
frase el 2026-09-25**: «Lo que **sí** sigue pendiente es FASE-RELEASE de ese plan, y con ella el cierre de esta
orden» — FASE-RELEASE se ejecutó y cerró **en su parte offline** ese mismo día con la release 4.78.0. Lo que
sigue pendiente ya no es una fase sino **permisos**: momento remoto (D8/D9), archivado, commit y push; y la
decisión de cierre de esta orden, que es del operador⟧.
**Fecha de la revisión:** 2026-09-22.
**Mandato original:** crear únicamente este documento; no ejecutar fases ni modificar código, configuración central o planes existentes. El §5-bis registra la autorización posterior que acotó la ejecución del bloque A.

## 1. Propósito y límites

Reducir trabajo repetido sin reducir garantías: corregir defectos observables, probar comportamiento antes que organización interna, reutilizar mediciones válidas y evitar registrar el mismo resultado manualmente en varios lugares.

Esta orden coordina cambios sobre contratos existentes; no crea un quinto plan ni sustituye sus propietarios. No impone cuotas de líneas, archivos, tests o lecciones como medida de calidad. Una fase larga no demuestra calidad; una fase corta tampoco.

La aprobación futura debe nombrar los bloques y archivos autorizados. Aprobar este documento como diagnóstico no autoriza por sí solo edición de `AGENTS.md`, `.agents/**`, configuración, llamadas externas, commits o publicaciones. Hasta una enmienda aprobada, siguen vigentes los contratos originales.

## 2. Base comprobada y límites de la evidencia

Las cifras siguientes son observaciones fechadas, no objetivos ni estado que deba mantenerse actualizado por cada commit.

| Observación | Evidencia y significado |
|---|---|
| FASE-B de CONTEXTO añadió 4.412 líneas y eliminó 97 en 46 archivos | `git show --numstat --format= 647f436`: cliente 1.084 líneas añadidas; pruebas/fixtures 986; evidencia y generadores 1.969; documentación/índices/registro 373. El volumen no equivale a tiempo ni demuestra desperdicio por sí solo. |
| Entre PRE y POST transcurrieron 2 h 59 min 18 s | Los encabezados de `faseB_quick_pre.txt` y `faseB_quick_post.txt` registran 2026-09-21 19:36:42 y 22:36:00. No hay reparto fiable de ese intervalo entre trabajo activo, herramientas, documentación y esperas. |
| La suite original registró 53 aprobados en 17,14 s; la revisión obtuvo 53 en 25,51 s | En la revisión, tres escaneos completos consumieron 24,18 s. Es repetición medible, no explicación suficiente de las casi tres horas. |
| Hay defectos pese al verde de la suite | Reproducciones en memoria: fallo de carga de proveedor traducido a `NO-CONFIGURADO`; `noul` admite campo desconocido; `tipo=[]` y `pregunta_id=[]` escapan como `TypeError`; dos preguntas con el mismo ID pueden obtener una sola respuesta y `RESUELTO`. |
| Parte del retrabajo fue evitable | El registro de B declara 30 fallos iniciales, rediseño de una mutación, falsos positivos del escáner y repetición del conflicto de fechas de REGISTRY. Son declaraciones del registro, no una reconstrucción independiente del transcript inicial. |
| La duplicación está prescrita | Executor y plantilla exigen múltiples cierres manuales; la plantilla publica quick `4/4`, AGENTS publica `10/10`, y las corridas observadas de B tienen 11 checks. No corregir esto copiando otra cifra dinámica. |

Fuentes de B: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/`, especialmente `run_tests.txt`, `baseline-pre-post.md`, `contract.txt` y `mutation/verde_baseline.txt`. Anclas de código: `resolver_proveedor`, `estado_proveedor`, `check_campos_conocidos`, `check_cobertura_de_preguntas`, `evaluar`, `escanear_aislamiento` y `medir_costura` en `scripts/decision_client.py`.

Comando de la corrida de revisión; se documenta para reproducibilidad, no se ordena ejecutarlo al leer esta propuesta:

```bash
PYTHONDONTWRITEBYTECODE=1 ./venv/Scripts/python.exe -m pytest tests/quality_gates/decision_client -q -p no:cacheprovider --durations=5
```

Los contraejemplos se reprodujeron en memoria, sin proveedor real; aún no son tests de regresión versionados. La revisión no ejecutó la pipeline, inferencias ni publicaciones. No atribuye a B los barridos posteriores al commit original.

## 3. Universo de adopción

Los alias de esta tabla se usan únicamente en esta orden; las rutas parten de la raíz del repositorio.

| Alias | Directorio | Estado observado y tramo a adaptar |
|---|---|---|
| CONTEXTO | `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/` | A/B cerradas offline; remediación puntual de B por alcance separado, **conciliada y aceptada por el plan propietario el 2026-09-23** (§5-ter: S11/S12 aceptadas, README rectificado, AC9 precisado); ⟦**antecedente vencido**: «C contractualmente preparada con E1–E5 y **no ejecutada**; D y RELEASE pendientes»⟧ — **C ejecutada y cerrada el 2026-09-24** (piloto, mandato propio; E1–E5 aplicados sin reabrirlos), **D ejecutada y cerrada el 2026-09-24** y **FASE-RELEASE ejecutada y cerrada en su parte offline el 2026-09-25** con la release **4.78.0**. Estado por fase: su `dependencias-fases.md`; métricas por fase: su `09` §D. **Lo que RELEASE dejó explícitamente pendiente**: momento remoto (D8/D9), archivado, `--fix`/`--update-baseline`, commit y push. Ninguna de sus cinco fases está **commiteada en su parte documental** y el producto de D (`scripts/build_phase_briefing.py`) sigue sin rastrear |
| WHATSAPP | `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` | A/G/0/B cerradas, B con deuda AC5 asignada a C-D; adaptar C, D, E, F, H, E2E, VERIFY y RELEASE. El README y partes de dependencias aún presentan B pendiente, pero su prompt, su fila y el commit `473ed0f` corroboran el cierre. ⟦**Conciliación 2026-09-25**: dos de sus «Seguimientos abiertos» estaban **resueltos y no barridos** — propagación `whatsapp_html_detected` (entregada por su FASE-B, medida con `validate_wiring.py --ignore-known`: 0 omisiones y 0 excepciones aplicadas) y los «dos escritores de REGISTRY» (la regla `registry_last_update` fue **retirada** por el bloque B de esta orden). Rectificados con atribución en su `10-analisis-post-implementacion.md`⟧ |
| JEV | `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/` | A ejecutada offline con muestra **BORRADOR** y revisión humana pendiente; **B, C y RELEASE pendientes y sin autorización para ejecutarlas**. ⟦**Antecedente vencido el 2026-09-25**: «el bloque de arranque todavía ofrece ejecutar A» describía el **HEAD**; en el árbol de trabajo ese bloque ya no ofrece ninguna fase, porque lo reescribió el bloque C de esta orden⟧. Su **dependencia técnica** del hermano quedó **entregada** el 2026-09-24 (`scripts/triage_lesson_relevance.py`, rastreado en `5817edd`), así que los bloqueantes reales de su FASE-B son ahora **la revisión humana de la muestra, la decisión del *gap* de interfaz y su propia autorización**, no la ausencia del triaje. El trabajo preexistente de 18 líneas en su `dependencias-fases.md` se conserva intacto y sin commit |
| ESCRITURA-QMIND | `.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/` | Fase única pendiente; conservar su propiedad del writer y de su integración con validaciones. |

Reconciliar estados antes de elegir la siguiente fase; no repetir una implementación porque una cabecera está vencida. No modificar documentos ni evidencia bajo `Archives/` para hacerlos conformes a reglas nuevas.

Hay trabajo ajeno preexistente en `JEV/dependencias-fases.md`: 18 líneas locales sobre orden de cierre. Se preserva; no se trata como cambio de esta orden ni como contenido ya commiteado. Re-medir `git status --short` al retomar.

## 4. Bloques de cambio propuestos

### A. Remediación técnica focalizada, antes del consumidor de CONTEXTO

**⟦Estado al 2026-09-23⟧.** Ejecutado en `fdd397f` (§5-bis) y **conciliado con su plan propietario**
(§5-ter): los tres bullets de abajo que pedían resolver S11, resolver S12 con destino explícito y
declarar AC9 con precisión están **hechos y aceptados**. Lo que sigue pendiente de este bloque es lo que
él mismo difería al bloque B (proceso común e instrumentos).

**⟦Estado documental al cierre, 2026-09-25⟧**: su remediación **permanece bajo «Sin publicar»** en
`CHANGELOG.md` y en la nota datada de `VERSION.yaml` — decisión escrita del operador, que rechaza
acreditarla a la entrada `[4.78.0]`. La entrada no se reescribe ni se promotea: lo único que cambia es que
el pendiente que ambas notas declaraban quedó respondido (ver §6, «Firmas del cierre», casilla 1).

- Añadir regresiones de los cinco contraejemplos de la revisión; después corregir clasificación de fallos, validación estructural y unicidad de IDs, sin introducir decisiones por defecto ni capturar errores para devolver un favorable.
- Compartir el escaneo real entre aserciones independientes sobre el mismo árbol; mantener aisladas las pruebas que mutan el módulo o el árbol. Separar conceptualmente cliente y certificación; extraer archivos solo si el beneficio lo justifica, no como objetivo de volumen.
- Revisar que el CLI/informe no represente población ausente o lectura incompleta como comprobación favorable. Conservar la cobertura explícita y resolver el denominador observado en CONTEXTO/S11.
- Conservar el rojo contractual contra el mismo test; los instrumentos de evidencia deben comprobar resultados y códigos de salida, no solo imprimir relatos de verde/rojo. Evitar tests que obliguen a una partición exacta de validadores sin necesidad contractual.
- Declarar con precisión AC9: extensión local a un proveedor falso, no coste total certificado de integrar SDK, dependencias y autenticación. La ubicación futura del SDK sigue siendo CONTEXTO/S10 y D7, coordinada con JEV.
- Resolver CONTEXTO/S12 con destino de escritura explícito o salida sin escritura: volver a medir no puede sobrescribir evidencia cerrada. Su asignación actual a RELEASE choca con la prohibición de editar código allí; trasladar la ejecución del fix a este bloque mediante enmienda expresa.

**Superficie candidata:** `scripts/decision_client.py`, `tests/quality_gates/decision_client/`, `scripts/validate_governance_numbers.py` y sus pruebas. Los generadores existentes bajo la evidencia de B se leen como antecedente; no se reescribe el expediente cerrado. La evidencia de remediación tendrá ubicación propia y referencias al original.

### B. Proceso común e instrumentos, sin otra capa de burocracia

**⟦Estado de B: exclusivamente en la matriz vigente §13 del resumen enlazado abajo⟧.** El último dictamen de §12 también
quedó retirado: no demostraba lectura de bytes de archivos limpios ni mediciones comparables con
salidas completas del consumidor. Los dictámenes anteriores y sus causas de retiro permanecen en
la fuente única. El checkout previo de REGISTRY fue no autorizado; no se restaura, borra ni
re-registra. Las operaciones config/commit/checkout de los fixtures históricos ocurrieron en
temporales: también estaban fuera del mandato y no deben repetirse. Matriz y evidencia vigentes:
**§13 del resumen**, enlazado abajo. No se sustituye aceptación contractual por una suite verde.
**Fuente única de resultados de B:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`**
— matrices, estados y evidencia. Esta fila no los transcribe.

- `AGENTS.md`: principios y referencias canónicas; retirar duplicaciones operativas y cifras volátiles, preservando los vínculos que verifican los validadores.
- `.agents/workflows/phased_project_executor.md` y `.agents/workflows/templates/prompt-fase-template.md`: comprobaciones proporcionales al cambio, lecturas pertinentes y cierres que reutilicen resultados; distinguir rojo deliberado de mutación de errores accidentales. Permitir declarar que no hubo lecciones nuevas, sin fabricar una cuota.
- Aprovechar los informes y registros existentes como fuentes por resultado; generar o referenciar sus resúmenes en vez de transcribirlos. No diseñar un framework general de reportes. Una reutilización solo vale si coinciden entradas, configuración y entorno relevantes; cualquier cambio que afecte la comprobación la invalida.
- Unificar la semántica y el propietario de la fecha de REGISTRY entre `scripts/log_phase_completion.py` y `scripts/sync_config.yaml`; recomendación a revisar: última entrada documental, distinta de fecha de release. Evitar la reparación manual repetitiva y cubrir la interacción con un test.
- Medir en adelante implementación, verificación y cierre con cortes explícitos; separar espera de autorización del punto «listo para revisión». Tiempos de comandos no equivalen a tiempo activo del agente. Sin transcript, no inventar tool calls ni reconstruirlos a partir del número de archivos.
- Alinear solamente las reglas afectadas en `docs/CONTRIBUTING.md`, `docs/contributing/documentation_rules.md`, `docs/contributing/validation.md` y `scripts/validate_document_integration.py` con sus tests, si el nuevo contrato lo requiere. No desactivar verificaciones para permitir el cambio.

**Frontera:** revisar consumidores antes de editar. `scripts/build_lesson_index.py`, `scripts/run_all_validations.py` y el hook no se cambian por comodidad. Renumerar o promover checks es CONTEXTO/D2, no esta simplificación; el writer QMind permanece bajo su plan propietario. Ajustar las referencias y tests vivos afectados por D1 sin borrar evidencia de la versión anterior ni debilitar aserciones para conseguir verde.

### C. Enmiendas prospectivas a los cuatro planes

| Plan | Ajustes de contrato que deben quedar resueltos antes de ejecutar el tramo afectado |
|---|---|
| CONTEXTO/C | **⟦RESUELTOS el 2026-09-23 como E1–E5 en el contrato del plan; ninguno implementado⟧** Definida la decisión binaria como `choice` de dos opciones con `confidence` independiente (la recomendación de esta fila es la que se adoptó, confirmada contra `decision_client.py`); las propuestas de un falso no se incorporan sin revisión humana; **E2** eligió lectura del JSON con frescura propia (ruta b) y alineó estados/tests/prompt — `VENCIDO` **no** se elimina: lo produce el check del propio C; AC15 semántico continúa `NO-EJERCITADO` y D6 dormida. ⟦**Cerrado el 2026-09-24**: «Queda por ejecutar la fase» era el estado al redactar la fila — el piloto se ejecutó con mandato propio y **aplicó E1–E5 tal como estaban resueltos**, sin reinterpretarlos; el techo alcanzable con D7 inactiva sigue siendo `acceptance = NO-EJERCITADO`⟧ |
| CONTEXTO/D | ⟦**EJECUTADO el 2026-09-24** — FASE-D cerró con estos cuatro puntos medidos, no escritos⟧ Medir carga total, incluido workflow obligatorio y coste del pack; no prometer ahorro por concatenación. Aceptar explícitamente el resultado no medido de C. Definir frescura por fuentes relevantes, con HEAD como procedencia, evitando invalidación circular por el commit del propio generado; acordar resolución y regeneración tras archivado. Su medición vive en `evidence/…/FASE-D/carga.json` y `carga-pre-post.md`; **esta fila no la transcribe** |
| CONTEXTO/RELEASE | **⟦PENDIENTE — es la única fila de §4.C que no se ejecutó⟧** Resolver «verificador verde» frente a D1 sin ejecutar; subida/consulta QMind frente a cero red; y `--check` posterior al traslado sin regeneración prevista. No convertir RELEASE en reparación de código. Mantener resultados parciales sin promoverlos a éxito. Las tres contradicciones de esta fila quedaron **resueltas documentalmente** por el bloque C (contract §Dos momentos del cierre) y siguen siendo **operación pendiente de su fase**: resuelta la letra, no corrida la fase. ⟦**Cuarta resolución añadida el 2026-09-25 en la conciliación final**: «offline» se estaba leyendo como permiso de escritura. Rige **C0** en el prompt de RELEASE y su contrato: antes de escribir hay que autorizar **los destinos reales** de cada writer — lo que `sync_versions.py` sin `--check` reescribe según `scripts/sync_config.yaml`, `VERSION.yaml` (entrada, no salida) y el par `REGISTRY.md` + `.last_doc_phase.json` del escritor de registro. Un mandato de fase **no** incluye editar configuración central, y sync de cabeceras **no** autoriza la alineación de `DOMAIN_PRIMER`. Tampoco se corre `--fix` ni `--update-baseline` para absorber rojos⟧ |
| WHATSAPP | Reconciliar el punto de reanudación en C y adaptar sus tramos pendientes al cierre común aprobado. Conservar deuda AC5, contratos aditivos, pruebas de botón seguro, aislamiento interno/cliente, corrida única y lectura directa de VERIFY. Resolver con la gobernanza común la discrepancia ya registrada sobre cuándo regenerar DOMAIN_PRIMER, sin tratar su generación y su validación como la misma operación. ⟦**Conciliación 2026-09-25**: la cuota de «tres observaciones» sigue viva en **dos** rutas de este plan —`10-analisis-post-implementacion.md:72`, barrida en esta conciliación, y `05-prompt-inicio-sesion-fase-G.md:52`, que **no** estaba en el permiso y queda como residuo con dueño⟧ |
| JEV | Reconciliar arranque y disponibilidad real de la interfaz; integrar contra el contrato corregido, sin duplicar cliente ni acomodar silenciosamente el consumidor. B depende técnicamente de B+C offline de CONTEXTO, no de aceptabilidad semántica real; el orden de cierre/índice es gobernanza separada. Conservar muestra humana, congelación, comparador, reservas, cuotas, aislamiento del SDK y autorizaciones por etapa. ⟦**Conciliación 2026-09-25**: la dependencia técnica **B+C** del hermano quedó **entregada** el 2026-09-24, así que la fila ya no describe un bloqueante de ejecución ajena; **no** por eso está autorizada la FASE-B de JEV, ni congelada su muestra, ni resuelta la decisión de interfaz que ella plantea⟧ |
| ESCRITURA-QMIND | Resolver consulta/ingesta real frente a prohibición de red y AC6 posterior al cierre de WHATSAPP frente a una sesión que debe precederlo. Separar entrega offline de aceptación remota posterior, con estado parcial explícito y propietario. Conservar verificación por contenido, saneamiento, no-PASS por instrumento ausente y tratamiento autorizado de fuentes vigentes. |

Actualizar maestro, contrato, prompts pendientes y resúmenes que expresen las reglas afectadas; no hacer reemplazos globales ni copiar esta orden completa en cada plan. Las fases cerradas conservan su evidencia; los estados actuales incorrectos se rectifican con atribución, no se reconstruye el pasado.

**⟦Estado del bloque C el 2026-09-24⟧** — las seis filas anteriores se resolvieron **solo documentalmente**
en los cuatro planes, sin código, sin tests, sin red y sin commit. La matriz fila por fila (requisito →
contrato vigente → consumidor → cambio → comprobación → estado) vive en su única fuente:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`.
Lo que **no** cerró este bloque: el piloto FASE-C de CONTEXTO (demanda de esas enmiendas, con mandato
propio), la activación de D7 y cualquier operación remota (QMind, inferencias, subida), que conservan su
autorización y presupuesto pendientes.

**⟦Vigencia de la nota anterior⟧**: describe el estado **al cerrar la sesión de enmiendas**. El piloto
FASE-C se ejecutó en una sesión **posterior del mismo 2026-09-24**, con mandato propio (§6); FASE-D cerró
en una tercera sesión ese día. Lo que la nota sigue afirmando en pie es lo demás: **D7 sin activar, el
aceptabilidad semántica no ejercitada, el `import` del SDK sin dueño de ruta (S10), las deudas D2/D3/D6
intactas y toda operación remota sin autorización ni presupuesto**.

## 5. Decisiones para aprobación y coordinación

| Decisión | Recomendación | Estado |
|---|---|---|
| Alcance de implementación | Aprobar A, B y C por bloques y archivos concretos; autorizar expresamente los cambios centrales/configuración necesarios | **PARCIAL**: A ejecutado+conciliado; **B autorizado; estado exclusivo en su fuente única** — retirado también el dictamen de la revalidación del 2026-09-23; el veredicto vigente se decide en §13 del resumen (§4.B; árbol sin commitear porque el mandato de B prohíbe commit/push); **C autorizado y ejecutado el 2026-09-24 en su parte documental** (los archivos concretos que nombraba su mandato; sin código, sin tests, sin `.agents/**`, sin `AGENTS.md`, sin commit ni push). ⟦**Antecedente vencido el 2026-09-24**: «El piloto sigue sin autorizar»⟧ — **el piloto FASE-C y después FASE-D se autorizaron y ejecutaron ese día, cada uno con su mandato propio y su permiso explícito de archivos**; ninguno de los dos trajo consigo FASE-RELEASE, que sigue **sin autorización** |
| Encaje con deudas | Enlazar A con S11/S12 y B con D1/D3 de CONTEXTO, sin crear propietarios paralelos; mantener D2 y activación D7 fuera. Adelantar D3 respecto a su disparador actual requiere decisión expresa, no interpretación | **PARCIAL**: el enlace A↔S11/S12 está hecho y aceptado (§5-ter). **B↔D1 ejecutado y revalidado** (D1 cerrado desde su fuente, con contraejemplo congelado y el árbol real `SIN-HALLAZGOS`). **S13: reabierto el 2026-09-23 por la remediación** — B movió el destino de escritura pero no observaba las operaciones de escritura; su estado vigente es el de la matriz de cierre. ⟦Rectificado 2026-09-23 (revalidación): ningún estado de D1/D3/S13 queda declarado desde esta fila — todos vuelven a la matriz §13 del resumen, que los re-examina tras el retiro del tercer cierre⟧ **D3 adelantado solo en la parte que B necesitaba**, sin declarar D3 cerrado y **sin mudar su dueño**, que sigue siendo el del maestro §6 («Plan propio, posterior»): la simplificación que B recibió expresamente NO se difiere a D2, al bloque C ni al piloto. D2 y D7 fuera, como pedía la fila. El mandato de B autorizó expresamente adelantar D3 respecto a su disparador. **⟦D2 sigue fuera, como pedía la fila: el bloque C documentó por qué su disparador literal se cumplió en parte y por qué eso no lo abre — ver la fila D2 de `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md`⟧** |
| Fecha de REGISTRY | Un único escritor para fecha de última entrada; fecha de release por separado, sin cambiar VERSION para reparar el registro | **PARCIAL al momento del retiro, demostrado en la remediación**: `registry_last_update` está retirada de `sync_config.yaml` y `VERSION.yaml` no se toca —eso sí estaba hecho—, pero el «cubierto por `tests/test_registry_fecha_documental.py`» **sobreafirmaba**: esas pruebas no redirigían las rutas del `SyncEngine` ni `VERSION.yaml` al mismo expediente temporal, corrían la sincronización solo en modo `--check` (que no escribe) y dejaban sin ejercer la interacción registro→sync en modo escritura, su repeticion, las fechas distintas release/entrada y el control negativo. Estado vigente: §13 del resumen en `evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md` (revalidación; la demostración previa de la remediación queda como antecedente §1–§11) |
| Entrega y permisos remotos | Entrega offline verificable, aceptación remota posterior con autorización y presupuesto propios; no fingir que una prohibición de red permite una subida | **ESCRITO, NO EJECUTADO (bloque C, 2026-09-24).** La separación ya es contrato en los tres planes que la necesitaban: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (§Momentos y la división **AC6-entrega / AC6-aceptación**), `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (`04-contrato-ejecucion.md` §Dos momentos del cierre) y `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (su FASE-RELEASE, con el momento remoto etiquetado `PENDIENTE-AUTORIZACION`). Ninguna subida ni consulta real se hizo ni se autoriza por esta redacción: sigue faltando permiso literal y presupuesto |
| Piloto | FASE-C de CONTEXTO después de remediación y enmiendas, bajo mandato propio; no ejecutarla como parte de redactar o aprobar esta orden | **EJECUTADO Y CERRADO el 2026-09-24**: las enmiendas que la fila pedía estaban resueltas y conciliadas como **E1–E5** (§5-ter) y se aplicaron **tal como estaban resueltas**, sin reinterpretarse dentro de la fase. ⟦Esta celda decía «**No se ejecutó FASE-C** — sigue necesitando su mandato propio»; quedó vencida por el mandato que el propio piloto recibió ese día⟧ Su expediente: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` (lectura por su `baseline-pre-post.md` §Presupuesto y su fila en `10-analisis-post-implementacion.md` de ese plan; **esta fila no transcribe sus cifras**). **Lo que el piloto no cerró**: el `acceptance` semántico sigue `NO-EJERCITADO` (E4), D6 dormida, y su métrica de iteraciones es **auto-reporte con unidad propia**, no comparable con las tres horas de B (§6, motivo 3) |

Orden recomendado: aprobar fronteras y resolver contradicciones; implementar A; adaptar proceso/instrumentos y contratos pendientes de forma coherente; validar; ejecutar el piloto autorizado. Son bloques de trabajo, no nuevas fases automáticas ni promesa de resolver todo en una sesión. Serializar escrituras y cierres sobre archivos compartidos; las lecturas independientes sí pueden hacerse en paralelo.

Si se aprueba solo una parte, el resto conserva su contrato y estado pendiente explícitos. No dejar una política nueva apuntando a plantillas o instrumentos incompatibles.

## 5-bis. Registro de autorización y estado real del bloque A (2026-09-22)

Dos sesiones ejecutaron el bloque A bajo autorización expresa y acotada del operador; este registro
es la corrección de la primera sesión, que declaró el bloque cerrado de forma prematura y subió
`VERSION.yaml` a 4.77.4 sin sincronizar consumidores.

**Alcance autorizado (lo único ejecutado):**

- Superficie técnica: `scripts/decision_client.py`, `scripts/validate_governance_numbers.py`,
  `tests/quality_gates/decision_client/` y `tests/quality_gates/governance_numbers/`.
- Normalización documental sin release: `VERSION.yaml`, `CHANGELOG.md`, este documento y el resumen
  `evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/00-resumen-bloque-A.md`.
- Límites respetados: sin tocar `AGENTS.md`, `.cursorrules`, `.agents/**`, hooks, `sync_config.yaml`,
  planes ajenos (incluido el trabajo preexistente de 18 líneas en `JEV/dependencias-fases.md`) ni
  producto hotelero; sin red, SDKs, pipeline, QMind, archivado, commit, tag ni push; sin crear otro
  plan ni framework de evidencia. El bloque B original, el bloque C y el piloto NO se iniciaron.

**Pendientes reales tras las tres sesiones (el bloque A NO está cerrado contractualmente):**

| Pendiente | Dueño |
|---|---|
| Registrar en el plan CONTEXTO la aceptación de la remediación A de S11/S12 y actualizar la advertencia vencida de su README («nunca correr el default sobre el árbol vigente», que ya no aplica tras S12). No es un traslado desde asignación exclusiva: el propio plan ya contemplaba «quien toque el script antes» | ~~Plan propietario CONTEXTO~~ → **HECHO el 2026-09-23**, ver §5-ter |
| Commit del árbol (con la decisión que implica para las cabeceras versionadas vía hook `version-sync`) y, si procede, push | Operador |
| Bloque B original, bloque C y piloto (FASE-C de CONTEXTO), cada uno con su autorización específica | Operador |

**Estado técnico medido al cierre de la sesión 3 (2026-09-22).** La auditoría del cierre de sesión 2
encontró tres sobreafirmaciones —veredicto de costura que aprobaba con solo contar el archivo,
fallos de componente que borraban lo ya medido, y una partición de validadores aún fijada por
igualdad de nombres contra la lista de seis— y las tres fueron corregidas con prueba por causa.
Veredicto actualizado: `evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/instrumentos/veredicto_cierre_a.py`
→ `cierre-a-antes-despues.txt`: **PRE 12/12 rojo-por-causa → POST 12/12, exit 0**, con el PRE
gateando el exit. *(Rectificado en sesión 4: en ese instrumento la causa se imprimía pero nadie la
comprobaba con un predicado — ver el párrafo siguiente.)* Selección afectada **150 passed,
exit 0**; suite completa **4.393 passed, 4 failed** — los mismos 4 fallos, con atribución de premisa
verificada y causa raíz pendiente de demostración (límite declarado, no tercero absuelto). Los
instrumentos y logs de sesiones 1 y 2 quedan como antecedente en sus destinos originales, sin
sobrescribir. No hay ningún conteo «10/10 → 8/11» vigente: esa comparación se retiró por carecer de
baseline (ver CHANGELOG, «Sin publicar»).

**Estado técnico medido en la sesión 4 (2026-09-22).** Una auditoría final de solo lectura encontró
tres defectos técnicos que el cierre de la sesión 3 no cubría, cada uno reproducido antes de
corregirse: (1) el instrumento contaba los rojos del PRE **sin comprobar la causa con un predicado** —
sabotajeando el fixture de C9 en una copia, certificaba «todos cayeron en PRE por su causa» con un
escenario que ya no existía y salía 0; (2) el contract test de forma anclaba el rojo a la partición
exacta de nombres de guard por igualdad — un guard extra legítimo que también detecta la mutación
producía un falso rojo (la atribución de causa L-V2.1 no exige esa partición); (3) en gobernanza una
ruta AUSENTE disparaba una puerta previa al análisis que descartaba los hallazgos del documento
legible y rompía el JSON por stdout (medido: doc legible → exit 1, JSON, 2 hallazgos; el mismo más
una ruta ausente → exit 2, prosa, hallazgos perdidos). Las tres correcciones tienen rojo/verde por
causa y logs en destinos propios de la sesión 4, sin sobrescribir antecedentes. Veredicto re-medido
con el instrumento fortalecido (13 criterios, +C11 de población mixta): **PRE 13/13
rojo-por-causa-comprobada → POST 13/13, exit 0** (`sesion4_veredicto_cierre_a.txt`); control
negativo: el mismo sabotaje del fixture de C9 → INSTRUMENTO SOSPECHOSO con exit 2
(`sesion4_control_negativo_causa.txt`). Selección afectada **153 passed, exit 0**.

**Cierre técnico ≠ cierre contractual.** Con la sesión 4, el cierre del bloque A está demostrado
técnicamente con causa comprobada por predicado. El cierre contractual sigue donde estaba: el
registro/aceptación de S11/S12 en el plan propietario CONTEXTO es de su dueño, el commit/push es
decisión del operador, y el bloque B original, el bloque C y el piloto no se iniciaron.

**Auto-auditoría del cierre de la sesión 4 (rectificación de los dos párrafos anteriores).** El
párrafo anterior se escribió antes de cerrar tres brechas propias y su afirmación era excesiva:
(1) el predicado de causa de C7 aceptaba **cualquier** `JSONDecodeError` —un exit 2 con `[AUSENTE]`,
causa distinta, pasaba como «su causa»—, de modo que «13/13 con causa comprobada» no cubría los
caminos `except` del instrumento; (2) la documentación del cierre aún no estaba conciliada; (3) los
4 fallos de la suite estaban atribuidos por **identidad de lista**, no por causa. Estado tras
cerrarlas: los predicados `except` (C7, C11) exigen la **firma positiva** del defecto nombrado con
sus precondiciones, y `_auto_test_predicados()` pasa observaciones sintéticas de las otras causas y
gatea el veredicto con exit 2. El control de mutación (restaurar el predicado permisivo en una
copia) deja la matriz leyendo «13/13 con causa comprobada» y es **solo** el auto-test el que lo
detecta; el auto-test además cazó un error propio en su primera corrida
(`sesion4_veredicto_cierre_a_v2.txt`). Instrumento final: **PRE 13/13 con causa-esperada OK,
POST 13/13, auto-test OK (43 casos), exit 0** (`sesion4_veredicto_cierre_a_v4.txt`,
`sesion4_controles_predicados.txt`).

La generalización de ese endurecimiento se midió, no se afirmó: los **13** predicados de causa son
funciones puras de la observación y el auto-test pasó a 43 casos sintéticos (firma baseline aceita +
firmas vecinas rechazadas, incluida la precondición del fixture apagada). Forzar cada predicado, de
uno en uno, a aceptar cualquier observación hace fallar el auto-test y señala ese criterio exacto:
**0 familias sin casos de rechazo, 0 falsos OK** (`sesion4_dientes_auto_test.txt`). Esta medición
retracta el residuo que la propia sesión había declarado («C1a…C10 sin observación sintética»): no
era un límite del árbol, era trabajo propio sin hacer.

De los 4 fallos de la suite, tres tienen causa demostrada: dos caen igual en HEAD extraído
(`test_diagnostic_geo_metrics`, `test_validate_lesson_capitalization[...TRIBUNAL-ENFORCEMENT-OBS...]`
por el archivado del plan), y `test_validate_wiring` contamina con `tmp_test/venv-jev-sdk/`
(0 ficheros rastreados, regla `.gitignore:28`) y pasa en una extracción sin ese directorio. El
cuarto, `test_function_default_flags`, **queda pendiente de mecanismo** (pasa aislado y en
`tests/financial_engine` completo, falla en las tres corridas completas). La extracción de HEAD con
`git archive` se declara **no comparable** como baseline de suite completa (17 failed + 18 errors
por estado local ignorado ausente). Ninguna de esas poblaciones importa `decision_client` ni
`validate_governance_numbers`.

**Afirmación vigente de cierre técnico**: los tres defectos encargados y los tres de la
auto-auditoría están corregidos con rojo reproducido y verde por causa, y el instrumento distingue
causa de síntoma también en sus caminos `except`. Persiste, declarado y fuera de la superficie
autorizada, el mecanismo del fallo de pricing flaky. El cierre **contractual** no cambia: registro
CONTEXTO de S11/S12, commit/push del operador y autorizaciones separadas para B, C y piloto.

> **⟦Rectificada parcialmente el 2026-09-23⟧** de los tres componentes que nombraba ese párrafo, **uno**
> cambió: el **registro CONTEXTO de S11/S12** se hizo ese día (ver §5-ter). Los otros dos siguen
> exactamente donde estaban — **commit/push es decisión del operador** y **los bloques B, C y el piloto
> conservan su autorización pendiente** — y el `fdd397f` que contiene la remediación **sí está commiteado
> y empujado** (medido el 2026-09-23: HEAD local = `fdd397f`, `git rev-list --count origin/master..HEAD`
> = **0**), de modo que «sin commit» ya no es una descripción vigente de la remediación técnica.
>
> **⟦Vencida en parte el 2026-09-25⟧**: de los «otros dos» que esta nota dejaba intactos, **el piloto ya no
> está entre ellos** — se autorizó y ejecutó el 2026-09-24 (§5, fila `Piloto`; §6, casilla 6). La nota sigue
> vigente en lo demás: **commit/push es decisión del operador** y **FASE-RELEASE conservaba su autorización
> pendiente** ⟦ese último punto se cumplió el 2026-09-25: RELEASE se autorizó y cerró en su parte offline con
> la release 4.78.0; commit y push siguen donde estaban⟧. Y la paridad que esta cita publicaba (`0`, medida el 2026-09-23) es un **antecedente fechado**,
> no el estado del remoto de hoy: se re-mide con `git fetch origin --quiet && git rev-list --left-right
> --count origin/master...HEAD`.

## 5-ter. Conciliación de CONTEXTO con el bloque A y enmiendas locales sobre CONTEXTO/C (2026-09-23)

Una sesión de solo documento, con autorización expresa del operador, cerró el pendiente contractual que
esta orden dejó abierto en §5-bis y preparó el contrato del piloto **sin ejecutarlo**. Los tres
momentos quedan separados en el plan propietario, no fundidos: **cierre original** de FASE-B
(`647f436`, que además *produjo* S11/S12), **corrección técnica** del bloque A (`fdd397f`, ajena a esta
sesión) y **aceptación** (2026-09-23).

**Qué se registró en el plan propietario CONTEXTO** (`dependencias-fases.md` §Conciliación, con eco en
`README.md`, `06-checklist-implementacion.md`, `09-`, `10-` y `00-`):

| Elemento | Estado tras la conciliación |
|---|---|
| **S11** (exclusión `.venv-wsl` no declarada en el denominador de AC6) | **Aceptada**, con re-validación offline: `--scan-imports` → `SIN-HALLAZGOS`, `exit 0`; escáner **696** `.py` vs `git ls-files '*.py'` **696** → **residuo 0**, y `.venv-wsl` publicado con 582 archivos excluidos |
| **S12** (`--report` sin destino pisaba la evidencia de FASE-A) | **Aceptada**: `--report` a secas → `exit 1` con A1–A4 en stdout JSON, aviso por stderr, `sha256` de `evidence/…/FASE-A/informe.json` **idéntico** y `git status --porcelain evidence/` **vacío** |
| Advertencia del README sobre el default de `--report` | **Rectificada** (queda sin efecto su aplicación a este script; la lección **L-VCF-12** permanece como regla general) |
| Fila de población AC6 (692/691 + residuo) | **Rectificada** como antecedente vencido |
| **AC9** | **Precisado**: extensión **local** con proveedor falso, no coste de integrar un SDK real con dependencias y autenticación |
| Prompt histórico de FASE-B | **Solo nota de cierre/rectificación**; sus instrucciones originales no se reconstruyeron |
| **Rojo contractual A1–A4** | **Antecedente fechado el 2026-09-23**: «vivo y no convertido en PASS: el verificador sigue saliendo `exit 1` porque `.agents/` no se edita» describía el árbol **antes** del bloque B, que recibió autorización para corregir `.agents/`. Re-medido el 2026-09-25 con el propio verificador y su modo de solo lectura (`validate_governance_numbers.py --report`, sin destino): **`status: SIN-HALLAZGOS`, `exit 0`** sobre el árbol de trabajo actual. El veredicto de **D1** no lo da esta fila ni este número: lo da la **matriz §13** de la fuente única de B (fila «D1 y S13», y `FINAL_gov_report_v3` / `VAL_gov_report_v2`, ambos `[SIN-HALLAZGOS]` exit 0), donde **D1 aparece CERRADA en su alcance**. Lo que sí conserva esta casilla es su regla de procedimiento: **leer** el verificador no es **reparar** `.agents/` |

**Decisiones locales sobre CONTEXTO/C (fila §4.C, «CONTEXTO/C»)** — autorizadas sobre **este** plan y
registradas como contrato **E1–E5** en su `04-contrato-ejecucion.md`, **sin implementar**:

- **E1** decisión binaria = **`choice` de dos opciones**, con `confidence` como campo **independiente**
  del umbral. **Forma confirmada contra `scripts/decision_client.py`**, no contra su docstring:
  `RespuestaEleccion` exige `confidence`; `RespuestaNoul` la trae en `None` con `confidence_motivo`.
  Consecuencia: `probabilidad_si` **no** es confianza y no gobierna el umbral de AC12.
- **E2** **AC11 cierra su elección abierta en la ruta (b)**: C consume el JSON del índice **tras
  ejecutar él mismo** la comprobación de frescura; `VENCIDO` es producto del check propio y no de
  `[6/7]`. Alineados AC11, la matriz §2, los estados, la tabla de tests y el prompt. Las tres causas
  (**`AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO`**) quedan distinguibles con su test.
- **E3** las propuestas del proveedor falso **no** entran en §2 de `00-lecciones-capitalizadas.md` en
  automático: **revisión humana explícita** con **aceptación o rechazo registrado**. Se reescribió el
  paso 6 del post-ejecución de C, que mandaba lo contrario — una nota al margen no basta contra una
  instrucción ejecutable vigente.
- **E4** AC15 semántico **NO-EJERCITADO con motivo**, prohibido simular la aceptabilidad con el falso;
  **D6 dormida**.
- **E5** la futura C **conserva el workflow canónico y el proceso común actualmente vigentes**.
  ⟦**Rectificado el 2026-09-23**: esta frase se escribió cuando el bloque B estaba diferido. B se
  autorizó y ejecutó el mismo día (ver §4.B y la evidencia `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/`).
  El proceso común vigente que C debe conservar es ya el que deja B (proporcionalidad, reuso con
  invalidación explícita y un-solo-escritor de la fecha de REGISTRY). Las declaraciones de cierre
  D1/S13 de esta nota son antecedentes: rige su revalidación en §13 de la fuente única de B.
  **El bloque C de esta orden y el piloto FASE-C siguen diferidos, no
  aplicados ni declarados cerrados.**⟧ ⟦**Esta última frase quedó vencida el 2026-09-24**: el **bloque C**
  se autorizó y ejecutó como enmiendas documentales (§4.C y su resumen único en
  `evidence/…/BLOQUE-C-ENMIENDAS-2026-09-24/`); **el piloto FASE-C sí sigue diferido**, y sigue siendo el
  «C» al que se refiere la frase anterior de esta nota cuando dice «el proceso común que **C** debe
  conservar» — ese C es una fase de CONTEXTO, no un bloque de esta orden.⟧ ⟦**Vencida también en su segunda
  parte el 2026-09-24**: el piloto FASE-C de CONTEXTO se autorizó con mandato propio y **se ejecutó y cerró
  ese día** (§5 fila `Piloto`, §6 casilla 6, `evidence/…/FASE-C/`). **La distinción que esta nota fija sigue
  siendo la que gobierna**: el «C» de «el proceso común que **C** debe conservar» es la **fase** del plan
  CONTEXTO, no el **bloque** C de esta orden — dos cosas distintas que se leyeron juntas en más de una
  sesión y cuyo choque de nombre esta conciliación no resuelve borrando ninguna de las dos⟧.
  Se aprovechó para rectificar dos frases del prompt de C que contradecían el propio
  contrato (el «tope de 200 llamadas», que no existe como licencia de red, y la referencia a una
  sección del contrato que no estaba).

**Límites de esta conciliación.** No modificó código, tests, configuración central, `AGENTS.md`,
`.cursorrules`, `.agents/**`, hooks ni validadores; no tocó los otros tres planes ni D/RELEASE de
CONTEXTO; no hubo red, QMind, fetch, SDKs, pipeline, archivado, commit ni push. No volvió a registrar
FASE-B en `REGISTRY.md` ni movió `VERSION.yaml`. La evidencia nueva vive en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/` y no
reemplazó ninguna anterior. **⟦Frase sobre commits/autorizaciones vencida parcialmente el 2026-09-23⟧**:

- **«sigue debiendo al operador: el commit de este árbol documental (y su consecuencia sobre las
  cabeceras vía `version-sync`)»** — **vencido**: la conciliación quedó commiteada en `cea8259` y la
  higiene documental en `d576368`/`da382b1`. No se publica aquí el HEAD ni la paridad como cifra
  operativa — el siguiente commit las invalida y una referencia local `origin/*` no prueba el estado
  remoto: se leen con `git rev-parse --short HEAD` y `git rev-list --count origin/master..HEAD`
  (última lectura fechada de esta orden: 2026-09-23, antes de la remediación de B, que no commitea).
  Los commits de higiene «vencen» esta cita literal, no borran el antecedente.
- **«las autorizaciones separadas de bloque B, bloque C y piloto»** — **parcialmente vencido**: el
  **bloque B se autorizó y ejecutó el 2026-09-23** (§4.B, evidencia
  `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/`); su árbol propio está **sin commitear** porque el mandato de
  B prohíbe commit/push (así queda la deuda vigente). **El bloque C y el piloto FASE-C conservan su
  autorización pendiente** y no se iniciaron. ⟦**Vencido en su primera parte el 2026-09-24**: el **bloque C**
  se autorizó y ejecutó como enmiendas documentales (fila `Alcance de implementación` de §5 y
  `evidence/…/BLOQUE-C-ENMIENDAS-2026-09-24/`), también **sin commitear** — su mandato prohíbe commit/push,
  igual que el de B —. Del piloto FASE-C esta frase **sigue vigente al pie de la letra**: sin autorización y
  sin iniciar.⟧ ⟦**Vencido en su tercera parte el 2026-09-24**: el **piloto FASE-C** recibió su mandato propio
  y **se ejecutó y cerró**, y **FASE-D** hizo lo mismo en una sesión posterior del mismo día. De las tres
  autorizaciones que esta fila separaba, **ninguna** sigue pendiente en B/C/piloto: lo que queda pendiente es
  una cuarta que esta redacción nunca otorgó — **FASE-RELEASE de CONTEXTO** —, más las dos remotas (D8, D9),
  el archivado, D7 y el commit/push. Estado por fase: la tabla de fases de
  `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md`⟧


## 6. Criterios de aceptación de la implementación futura

**Cómo se lee esta lista el 2026-09-24:** cada marca afirma **una** cosa y dice quién la satisfizo, por
referencia a su fuente. No hay aquí cifras transcritas: viven donde se midieron. Un criterio marcado **NO
EJECUTADO** no se da por hecho por haber redactado las enmiendas, y el hecho de que cuatro de los seis
estén cerrados por A/B y uno por C **no** cierra esta orden: hacía falta el piloto. **⟦Actualizado el 2026-09-24 al ejecutarse FASE-C (el piloto): la sexta casilla quedó satisfecha por referencia a su expediente, y la orden SIGUE ABIERTA — ver el párrafo «Estado de la orden tras el piloto», bajo la lista⟧**

- [x] Los contraejemplos quedan como regresiones: fallan en la revisión anterior por la causa esperada y pasan tras el fix; la suite existente conserva sus garantías. Fallos ajenos se atribuyen, no se ocultan. — **Satisfecho por A** (veredicto y logs de la sesión 4 en `evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/instrumentos/`, citados en §5-ter) **y por B** (matriz §13, fila «D1 y S13», con sus negativos por causa). El rojo preexistente `test_medido_contra_el_predecesor_entra_en_alcance…` sigue atribuido a su causa medida y con dueño en los registros de `REFACTOR-WHATSAPP` (FASE-G/0), sin ocultar ni tocar.
- [x] PRE/POST comparable demuestra reducción de escaneos repetidos, sin saltar comprobaciones ni reutilizar un resultado sobre entradas modificadas. Publicar tiempos reales aunque el ahorro sea nulo. — **Satisfecho por B**: matriz §13, fila «Mismo trabajo PRE/POST real» (`COMPARABILIDAD` exit 0), con cálculos, lecturas y tres tiempos por modo publicados en su propio expediente. No es un benchmark end-to-end ni tiempo activo, y la fila lo declara.
- [x] Registrar una fase y verificar sincronización ya no genera por sí mismo el conflicto de fechas; re-medir un verificador no modifica evidencias históricas. — **Satisfecho por A y B**: `registry_last_update` retirada de `scripts/sync_config.yaml` y tres rondas registro→sync→check en §13 (fila «REGISTRY↔sync», CUMPLIDO); la segunda parte es **S12** (`--report` sin destino no escribe), verificada de nuevo el 2026-09-24 en la pasada de solo lectura del bloque C (`03-validaciones-solo-lectura.txt`, `04-indice-lecciones.txt`).
- [x] Cada estado/métrica tiene fuente identificada; no se exige mantener manualmente el mismo dato en múltiples documentos. Las decisiones humanas siguen explícitas y no se fabrican mediante plantillas. — **Mecanismo por B** (`09` §D como fuente de métricas, `10` por referencia; cinco cortes sin commit) **y coherencia por C**: las cuatro parejas contrato↔prompt que contradecían ese principio se reconciliaron sin duplicar el dato, con su matriz en `…/BLOQUE-C-ENMIENDAS-2026-09-24/02-resultados-bloque-c.md`. Las etiquetas del piloto JEV y las decisiones del operador (D7, E3) siguen explícitas y sin fabricar.
- [x] Los cuatro planes tienen un punto de reanudación coherente y contratos prospectivos compatibles; permisos, propietarios y fronteras técnicas siguen distinguibles. Índice y validadores pertinentes se verifican sobre el árbol final sin relajar baselines para absorber errores. — **Satisfecho por C el 2026-09-24** (compatibilidad **documental**: ningún tramo se ejecutó). Comprobado sobre el árbol final con `build_lesson_index.py --check` en verde y la batería de solo lectura de `05-validaciones-post.txt`; las dos baselines (`plan_citations_baseline.json`, `refs_baseline.txt`) intactas y `git status --porcelain .opencode/plans/` sin altas ni bajas de ruta: solo contenido modificado en los cuatro planes.
- [x] El piloto informa defectos, retrabajo, tiempos y coste documental con instrumento y límites declarados. No comparar su duración total con las tres horas de B como si fueran trabajos equivalentes ni atribuir causalidad a una sola muestra. — **Satisfecho por FASE-C de CONTEXTO, cerrada el 2026-09-24, POR REFERENCIA a su expediente** (esta fila no re-transcribe cifras: viven donde se midieron). Instrumento, unidad declarada y límites: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/baseline-pre-post.md` §Presupuesto y su fila en `10-analisis-post-implementacion.md`. Lo que el piloto informó con medición, no con impresión: **defectos propios** (`cero-red.txt` §Rojos — un lector caído que se reportaba como traceback y no como estado, cuatro rojos de test al primer correr, y el rojo pedido por AC14), **retrabajo** (dos desviaciones declaradas y registradas: el corpus real de AC13 es `.opencode/plans/Archives/`, no `Archives/` a secas, y el proveedor falso solo existe montado por entorno dentro de `tests/quality_gates/lesson_relevance/`), **coste documental** (los seis documentos de cierre de esta sesión) y **límites**: la métrica de iteraciones **no** se midió con instrumento —`find . -name "*.jsonl"` volvió a dar 0, séptima reproducción de **D-V2.1**— y salió **auto-reporte con unidad propia** (`tool_use` con ids únicos), **no comparable** con las tres horas de B; y el juicio de pertinencia lo emitió un proveedor **falso**, así que `acceptance` es `NO-EJERCITADO` y **D6 sigue dormida**. **⟦Esta casilla NO cierra la orden: ver el párrafo siguiente, que dice por qué queda abierta y qué no queda terminado⟧**

**Estado de la orden tras el piloto (2026-09-24): los seis criterios de esta sección quedan satisfechos
y la orden NO queda cerrada.** Cuatro motivos, cada uno con su fuente:

1. **Quedaba una fase del plan que ejecutó el piloto.** ⟦Este motivo se escribió con **dos** fases
   pendientes —«FASE-D y FASE-RELEASE están PENDIENTES (filas 4 y 5 de su `dependencias-fases.md`)»—, luego
   con **una**: **FASE-D cerró el 2026-09-24** y **FASE-RELEASE cerró en su parte offline el 2026-09-25**
   con la release 4.78.0. Cerrar esta orden antes de eso habría dejado un criterio de aceptación apoyado en
   un plan a medias; **hoy la parte ejecutable del plan está corrida**, y lo que sigue pendiente de ese plan
   son permisos, no fases: momento remoto (D8/D9), archivado, `--fix`/`--update-baseline`, commit y push.
2. **La re-evaluación de las deudoras D1–D10 vive en el RELEASE de ese plan**, no aquí: esta orden
   aprobó enmiendas y un piloto, no el veredicto sobre las deudas del lote. ⟦**Cumplida en su lectura el
   2026-09-25**: FASE-RELEASE re-evaluó D1–D10 **leyendo** sus fuentes —D1 por la matriz §13 de B, D2/D3/D6/D7
   con estado explícito, D10 re-leyendo la firma del writer— y **sin reparar nada**: correr
   `validate_governance_numbers.py` fue leer el estado (`SIN-HALLAZGOS`, exit 0), no tocar `.agents/`. Las
   deudas siguen donde estaban, con su dueño; lo que cambia es que ahora hay una lectura fechada⟧.
3. **La métrica del piloto no es comparable con la de B.** Es auto-reporte de **una sola muestra** con
   unidad propia (`tool_use` con ids únicos, D-V2.1: el instrumento canónico no corrió porque
   `find . -name "*.jsonl"` volvió a dar 0). Su comparación con «las tres horas» del bloque B sería
   atribuir causalidad a números de unidades distintas, que es justo lo que esta casilla prohibía.
4. **El piloto juzgó con un proveedor falso.** `acceptance = NO-EJERCITADO` (contrato E4), así que de
   esta orden sale la **mecánica** verificada (aditividad, estados del suelo, umbral sobre `confidence`,
   mutation check, denominador con sus ceros) y **no** una medida de pertinencia real.

**Y ni los cuatro planes ni sus deudas externas quedan terminados por haber corrido el piloto**:
**D2** (promover el verificador de gobernanza al quick, renumerando), **D3 completa** (el rebanado del
workflow canónico por fase — lo que dejó el bloque B fue un adelanto parcial con dueño intacto),
**D6** (el lint de contradicciones semánticas, **dormida con causa**: su disparador es un `acceptance`
que aquí no se ejercitó), **D7** (activar el proveedor de decisiones) y **S10** (dónde vivirá el
`import` del SDK cuando D7 se active) siguen **abiertas, con su dueño y su disparador**, exactamente
como estaban antes del piloto. Ejecutar el piloto tampoco aplicó dentro de la fase ninguna mejora
general de esta orden (contrato **E5**): C leyó el workflow canónico vigente, no renumeró checks
(AC16 delta 0 contra su propio par pre/post) y no tocó el proceso común.

**Criterio de cierre de esta orden en su alcance aprobado (conciliación 2026-09-25; EJECUTADO el mismo
2026-09-25 por decisión escrita del operador).** La orden se cierra **solo** en los términos de su propio
§1 y §5, y ese cierre **no** afirma nada de lo que sigue:

- **Qué se cierra**: que los cuatro bloques que la orden proponía quedaron **resueltos en su alcance** — A
  ejecutado y conciliado (§5-bis/§5-ter), B con su matriz vigente en §13 de su fuente única, C resuelto
  documentalmente en los cuatro planes (§4.C), y el piloto que la fila `Piloto` pedía **ejecutado y
  cerrado** con mandato propio. Con eso no queda **ningún requisito de §6 sin dueño ni sin respuesta**.
- **Qué NO afirma ese cierre**: (1) que los **cuatro planes** estén terminados — CONTEXTO tiene sus cinco
  fases corridas, pero a `REFACTOR-WHATSAPP` le faltan C/D/E/F/H/E2E/VERIFY/RELEASE con AC5 debida, a JEV le
  faltan B/C/RELEASE y su muestra sigue **BORRADOR**, y ESCRITURA-QMIND no ejecutó su fase única; (2) que exista
  una **calidad semántica real medida** — el piloto juzgó con proveedor falso y AC15 sigue
  `NO-EJERCITADO`; (3) que las **deudas** D2, D3 completa, D6, D7, S10, S14, S15, S16, **S17** y **S18**
  estén cerradas — las dos últimas nacen **de** este cierre, con dueño y disparador, y no se curaron;
  ⟦**S17 y S18 se curaron después, en otra sesión con mandato propio (2026-09-25)**: siguen vivas D2, D3
  completa, D6, D7, S10, S14, S15 y S16⟧;
  (4) que el trabajo esté **commiteado o publicado** — ver la tabla de cuatro momentos del encabezado.
  ⟦**Precisión del mismo 2026-09-25, causada por la propia ejecución del cierre**: esta casilla decía «a
  CONTEXTO le falta FASE-RELEASE». FASE-RELEASE se ejecutó y cerró **en su parte offline** ese día con la
  release 4.78.0; lo que le falta a ese plan son permisos (momento remoto, archivado, commit, push), no
  fases. La frase se corrigió por exactitud, no para acercar el lote a un cierre que aún no ocurre⟧.
- **Condición para ejecutar el cierre**: que FASE-RELEASE de CONTEXTO haya cerrado **offline** y haya
  declarado su momento remoto como `PENDIENTE-AUTORIZACION` si no tuvo permiso. Un resultado parcial de
  RELEASE se reporta como parcial. ⟦**Esa condición quedó cumplida el 2026-09-25**, con la release 4.78.0,
  el sync de cabeceras, `DOMAIN_PRIMER` regenerado con su writer, `CHANGELOG` y `REGISTRY` por sus
  escritores, y D8/D9 declarados `PENDIENTE-AUTORIZACION` con la premisa de D8 **no comprobada**
  (`evidence/…/FASE-RELEASE/`). Aun así **esta orden no se cierra aquí**: cerrar un documento de política es
  decisión del operador, y los dos defectos de instrumento que el cierre encontró siguen abiertos y sin
  dueño asignado (los writers que reescriben en CRLF y la fecha legible del `README.md`, declarados en el
  CHANGELOG y en `06-checklist-implementacion.md` de CONTEXTO)⟧. ⟦**Vencidos esos dos remates el mismo
  2026-09-25**: el operador escribió el cierre de esta orden y a los dos defectos se les dio **dueño y
  disparador** como **S17** y **S18** en `dependencias-fases.md` de CONTEXTO (eco en su
  `10-analisis-post-implementacion.md` y en `06-checklist-implementacion.md`), **sin curarlos** — curarlos es
  editar `scripts/`, que ningún mandato dado hasta aquí autoriza. La firma completa está en la casilla
  «Firmas del cierre» de abajo⟧. ⟦**Vencido ese «ningún mandato» el mismo 2026-09-25**: llegó un mandato de
  código y la cura se hizo en una sesión aparte, con `README.md` autorizado además como destino de
  escritura. El cierre no se movió: firmó «declarar con dueño y no curar aquí»⟧.
- **S14, S15 y S16 con su estado conciliado** (definiciones y dueño en `10-analisis-post-implementacion.md`
  y `dependencias-fases.md` de CONTEXTO; esta orden no los re-transcribe): **S14** sigue **abierta** y su
  disparador **no** se dio por satisfecho — se comprobó, leyendo el texto definitorio y la CLI real, que
  el `git mv` del cierre dentro del propio repositorio **no** lo dispara (no llama al triaje con rutas
  trasladadas), de modo que la nota que lo daba por «justo el caso del RELEASE» queda rectificada;
  **S15** sigue **abierta** y su límite queda explícito: el verde local de `[6/7]` **no** certifica otro
  checkout, y reparar el generador (`build_lesson_index.py`, fuente de la fecha) es **alcance técnico
  separado** que ninguna fase de esta orden autoriza; **S16** sigue **abierta**, con dueño en
  `.agents/workflows/templates/prompt-fase-template.md` y disparador «la próxima vez que un mandato
  autorice editar el template».

- **Firmas del cierre (2026-09-25), cada una con su destino y su documento**:
  1. **Bloque A → permanece bajo «Sin publicar».** `CHANGELOG.md` conserva su entrada
     `[Sin publicar] - Remediación bloque A` sin reescribir y **sin** acreditar su contenido a `[4.78.0]`;
     `VERSION.yaml` lleva la decisión en su nota datada. No hay bump, sync de cabeceras ni re-registro en
     `REGISTRY.md` por este bloque.
  2. **`DOMAIN_PRIMER` → declarado, no alineado.** Sigue viva la divergencia de **cuándo** regenerar:
     `AGENTS.md` §Flujo Documental («se regenera en FASE-RELEASE (no manualmente)») contra
     `docs/CONTRIBUTING.md` Paso 5b («al cerrar cada fase de implementación regenerar», con validación solo
     en FASE-RELEASE). **No se editó configuración central** — es la prohibición de §1 y del contrato **C0**,
     y alinearlo pide mandato literal sobre esos dos documentos. Regenerar el archivo con su writer (lo que
     hizo RELEASE) y alinear su política **son dos operaciones distintas**: no fundirlas es exactamente lo que
     pedía la fila WHATSAPP de §4.C. Registro en `06-checklist-implementacion.md` de CONTEXTO.
  3. **Defectos de writers → S17 y S18**, con dueño (`scripts/sync_versions.py` + `scripts/doctor.py`;
     `scripts/sync_config.yaml` + su lector) y disparador (el próximo mandato que autorice editarlos),
     **declarados y no curados** en el acto del cierre. ⟦**Su disparador se cumplió el mismo 2026-09-25**:
     una sesión posterior, con mandato de código del operador, curó las tres escrituras de S17 (la de
     `run_status` apareció al curar) y la regla de S18; escribir la fecha de `README.md` se autorizó como
     destino aparte. Estado vigente: §S17/§S18 de `dependencias-fases.md` de CONTEXTO, y la prueba en
     `tests/test_sync_writers_lf_y_fecha_readme.py`. Que esto ocurra **después** del cierre no lo revoca:
     el cierre firmó «declarar con dueño, no curar aquí», y eso fue lo que se hizo⟧.
  4. **`L-VCF-10…14` → pendientes con su dueño: el operador**, por la revisión humana que fija el contrato
     **E3**. Ninguna entró al §2 del `00-` de CONTEXTO (**AC10**: sus catorce filas intactas) y ninguna se
     rechazó; el registro de los cinco estados está en §4 de ese `00-`.

  Qué corrió este cierre y su evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CIERRE-ORDEN-2026-09-25/`
  — baseline `--quick` **antes** de escribir, las escrituras documentales, y la cola derivada en su orden
  canónica (packs → par del índice → `--check` de ambos → `--quick`) con su exit impreso. Sin red, sin SDK,
  sin pipeline, sin archivado, sin commit y sin push: cada uno conserva su checkpoint.

  ⟦**Después del cierre, la misma 2026-09-25, el operador abrió la sesión de curación (opción B)**, y ese
  trabajo también vive en el mismo expediente: `06-sync-readme.txt` (el escritor de la fecha, con su destino
  autorizado aparte), `07-guard-idempotencia-sync.txt` (segunda corrida: ninguna de las diez rutas vigiladas
  se mueve), `08-seleccion-curacion.txt` (la selección en verde) y `08b-control-pre-cura.txt` (**los mismos
  tests contra los `scripts/` de `HEAD`: 5 failed, `exit 1`** — la prueba de que el verde viene de la cura y
  no del entorno) y `09-quick-post-curacion.txt`. La cura añade siete funciones de test al árbol sin
  commitear; no toca `AGENTS.md`, que sigue con su rojo de conteo declarado (`4.246` publicado contra
  `4.564` en disco medido al curar).⟧

**Fuera de alcance:** producto hotelero, umbrales de seguridad/publicación, multiplicar corridas, nuevas inferencias, instalar SDKs, rotar credenciales, limpiar históricos, editar trabajo ajeno, publicar QMind, archivar, commit o push sin mandato separado. No modificar `.cursorrules` por arrastre de una sincronización no autorizada.

## 7. Arranque de la próxima sesión de revisión

**⟦Conciliación final 2026-09-25: el texto de esta sección quedó vencido como instrucción y se conserva
como antecedente⟧.** Ya no hay un «bloque que se vaya a aprobar»: los tres bloques y el piloto se
autorizaron y ejecutaron. Lo único que la orden deja por delante es **una fase de un plan ajeno con mandato
propio**, y su arranque no se redacta aquí por primera vez — vive en su plan, que es su fuente única.

**⟦Estado tras el cierre del 2026-09-25⟧: la orden quedó cerrada en su alcance aprobado (§6, «Firmas del
cierre»), así que esta sección deja de ser un «arranque» y pasa a ser la **cola de permisos que el cierre
no toca**. Ninguna de sus casillas es trabajo pendiente de esta orden: son checkpoints de otros planes y de
otras autorizaciones.⟧

- **No hay fase que abrir**: FASE-RELEASE de CONTEXTO se ejecutó y cerró en su parte offline el 2026-09-25
  (release **4.78.0**). Lo que esta orden deja por delante son **permisos**, cada uno con su checkpoint:
  momento remoto (D8 consulta, D9 subida), archivado `git mv`, correcciones de corpus
  (`--fix`/`--update-baseline`), commit y push. Su lectura de estados y su evidencia:
  `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` y
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-RELEASE/`.
- **Dos defectos de instrumento que la release declaró y no curó** (son edición de `scripts/`, fuera de
  todo mandato dado hasta aquí): `scripts/sync_versions.py:161` y `scripts/doctor.py:590` escriben con
  `write_text` sin `newline="\n"` y re-CRLF-ean archivos que git almacena en LF (el detector de finales de
  línea del bloque B los cortó); y la regla `readme_version_header` de `scripts/sync_config.yaml` no
  goberna la fecha legible de `README.md`, que quedó desfasada respecto de `release_date`.
  ⟦**Cerrados como deuda el 2026-09-25, no como código**: son **S17** y **S18**, con dueño y disparador en
  `dependencias-fases.md` de CONTEXTO. Este cierre **no** los cura — esa edición sigue sin autorización —,
  y por eso su remedio vigente sigue siendo la normalización manual declarada en
  `evidence/…/FASE-RELEASE/12-normalizacion-lf.txt`⟧. ⟦**Y sí se curaron después, en una sesión aparte del
  mismo 2026-09-25 con mandato de código**: `newline="\n"` en las tres escrituras de la familia y
  `readme_version_header` goberna la fecha legible, que se alineó corriendo el escritor con `README.md`
  autorizado. La normalización manual queda como antecedente: el próximo cierre no la necesita. Prueba y
  estado vigente: §S17/§S18 de `dependencias-fases.md` y
  `tests/test_sync_writers_lf_y_fecha_readme.py`⟧.
- El prompt canónico de la fase ya corrida sigue siendo
  `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/05-prompt-inicio-sesion-fase-RELEASE.md`
  (conciliado y corregido el 2026-09-25: cuatro prompts nombrados, **C0** de destinos escribibles y cola de
  regeneración después de las últimas escrituras). La copia que esta conciliación entregó como texto pegable
  quedó en `evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/04-prompt-fase-release.md` y **se usó**: su C0 es
  el que gobernó el cierre.
- Este plan **no** autoriza RELEASE por el solo hecho de publicitar su prompt, y **no** decide las
  autorizaciones remotas (D8, D9), el archivado, el commit ni el push: cada uno es un checkpoint aparte.

Antecedente (el texto con el que la orden abrió su primera sesión, 2026-09-22 — «propuesta, no autorización»
era exacto entonces y hoy solo describe lo que falta):

```text
Revisa .opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md en
C:/Users/Jhond/Github/iah-cli. Es una propuesta, no autorización de implementación.
Re-mide git status y solo las anclas/dependencias necesarias para el bloque que se vaya a aprobar.
Preserva trabajo ajeno y evidencia histórica; no recrees un kit de planes ni repitas toda la auditoría.
Presenta el alcance exacto de archivos y las decisiones pendientes de esta orden.
Antes de implementar, solicita aprobación explícita de los bloques y cambios centrales/configuración.
No ejecutes fases de los planes, pipeline, APIs, subidas, archivado, commit ni push.
```

La creación de esta orden no cierra ninguna fase ni deuda, no registra una ejecución en REGISTRY y no afirma que los cambios propuestos estén implementados o medidos.

**⟦Vigencia del texto de arranque, 2026-09-24 — re-vencida el 2026-09-25⟧**: «no autorización de implementación» sigue siendo cierto
para lo que falta —el **piloto FASE-C** de CONTEXTO, D7, y toda operación remota—, pero ya no describe el
conjunto: A, B y la parte documental de C se autorizaron y ejecutaron en sesiones posteriores, cada una con
su mandato explícito. Releer esta línea como «nada está hecho» invalidaría el estado que declara el propio
encabezado; releerla como «el piloto ya está autorizado» es falso.

**⟦Rectificación de esta nota, conciliación 2026-09-25⟧**: de las tres cosas que esa nota daba por no
autorizadas, **una cambió de estado** — el **piloto FASE-C se autorizó y ejecutó el 2026-09-24**, y con él
también FASE-D. **FASE-RELEASE**, que esta nota aún listaba como sin mandato, **se autorizó y cerró en su
parte offline el 2026-09-25** (release 4.78.0) y con ello quedó cumplida la condición que el §6 ponía como
requisito previo del cierre. Siguen exactamente donde los dejó: **D7** inactiva y **toda operación remota**
sin autorización ni presupuesto; y son pendientes de **permiso**, no de fase, el momento remoto (D8/D9), el
archivado, el commit y el push. Lo que ya **no** es válido es
leer la nota como «la orden está a medias de implementación»: la implementación que la orden proponía está
hecha; lo que falta es **la firma del cierre por el operador, dos decisiones humanas (la alineación de
DOMAIN_PRIMER y las cinco propuestas del piloto) y un permiso técnico (D7)**.

⟦**Esa lista se cerró el 2026-09-25, en la misma fecha y por escrito**: la **firma del cierre** está en
§6 («Firmas del cierre»). Las **dos decisiones humanas** tomaron la forma «declarar, no aplicar»:
**`DOMAIN_PRIMER` queda declarado y no alineado** — no se editó configuración central, y alinearlo sigue
pidiendo mandato literal sobre `AGENTS.md` y `docs/CONTRIBUTING.md` — y **las cinco propuestas del piloto
(`L-VCF-10…14`) quedan pendientes con su dueño nombrado: el operador**, por la revisión humana del contrato
**E3**. De los tres componentes que esta nota pedía, **sobrevive uno**: **D7** inactiva. Y siguen en pie,
como permisos que esta orden nunca reclamó, D8, D9, el archivado, el commit y el push.⟧
