# Orden de cambio — Calidad y coste del proceso de ejecución

**Estado: bloque A autorizado y ejecutado (ver §5-bis); B, C y piloto PENDIENTES de autorización.**
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
| CONTEXTO | `.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/` | A/B cerradas offline; remediación puntual de B por alcance separado; C, D y RELEASE pendientes. |
| WHATSAPP | `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/` | A/G/0/B cerradas, B con deuda AC5 asignada a C-D; adaptar C, D, E, F, H, E2E, VERIFY y RELEASE. El README y partes de dependencias aún presentan B pendiente, pero su prompt, su fila y el commit `473ed0f` corroboran el cierre. |
| JEV | `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/` | A ejecutada offline con muestra BORRADOR y revisión humana pendiente; B/C/RELEASE pendientes. El bloque de arranque todavía ofrece ejecutar A. |
| ESCRITURA-QMIND | `.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/` | Fase única pendiente; conservar su propiedad del writer y de su integración con validaciones. |

Reconciliar estados antes de elegir la siguiente fase; no repetir una implementación porque una cabecera está vencida. No modificar documentos ni evidencia bajo `Archives/` para hacerlos conformes a reglas nuevas.

Hay trabajo ajeno preexistente en `JEV/dependencias-fases.md`: 18 líneas locales sobre orden de cierre. Se preserva; no se trata como cambio de esta orden ni como contenido ya commiteado. Re-medir `git status --short` al retomar.

## 4. Bloques de cambio propuestos

### A. Remediación técnica focalizada, antes del consumidor de CONTEXTO

- Añadir regresiones de los cinco contraejemplos de la revisión; después corregir clasificación de fallos, validación estructural y unicidad de IDs, sin introducir decisiones por defecto ni capturar errores para devolver un favorable.
- Compartir el escaneo real entre aserciones independientes sobre el mismo árbol; mantener aisladas las pruebas que mutan el módulo o el árbol. Separar conceptualmente cliente y certificación; extraer archivos solo si el beneficio lo justifica, no como objetivo de volumen.
- Revisar que el CLI/informe no represente población ausente o lectura incompleta como comprobación favorable. Conservar la cobertura explícita y resolver el denominador observado en CONTEXTO/S11.
- Conservar el rojo contractual contra el mismo test; los instrumentos de evidencia deben comprobar resultados y códigos de salida, no solo imprimir relatos de verde/rojo. Evitar tests que obliguen a una partición exacta de validadores sin necesidad contractual.
- Declarar con precisión AC9: extensión local a un proveedor falso, no coste total certificado de integrar SDK, dependencias y autenticación. La ubicación futura del SDK sigue siendo CONTEXTO/S10 y D7, coordinada con JEV.
- Resolver CONTEXTO/S12 con destino de escritura explícito o salida sin escritura: volver a medir no puede sobrescribir evidencia cerrada. Su asignación actual a RELEASE choca con la prohibición de editar código allí; trasladar la ejecución del fix a este bloque mediante enmienda expresa.

**Superficie candidata:** `scripts/decision_client.py`, `tests/quality_gates/decision_client/`, `scripts/validate_governance_numbers.py` y sus pruebas. Los generadores existentes bajo la evidencia de B se leen como antecedente; no se reescribe el expediente cerrado. La evidencia de remediación tendrá ubicación propia y referencias al original.

### B. Proceso común e instrumentos, sin otra capa de burocracia

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
| CONTEXTO/C | Definir decisión binaria y confianza sin equiparar probabilidad de sí con confianza; recomendación: `choice` de dos opciones si se necesita confidence independiente. Propuestas de un falso no se incorporan como lecciones pertinentes sin revisión humana. Elegir lectura de JSON con frescura propia o construcción en memoria y alinear estados/tests: no exigir `VENCIDO` si la opción elegida lo elimina. AC15 semántico continúa no ejercitado y D6 dormida. |
| CONTEXTO/D | Medir carga total, incluido workflow obligatorio y coste del pack; no prometer ahorro por concatenación. Aceptar explícitamente el resultado no medido de C. Definir frescura por fuentes relevantes, con HEAD como procedencia, evitando invalidación circular por el commit del propio generado; acordar resolución y regeneración tras archivado. |
| CONTEXTO/RELEASE | Resolver «verificador verde» frente a D1 sin ejecutar; subida/consulta QMind frente a cero red; y `--check` posterior al traslado sin regeneración prevista. No convertir RELEASE en reparación de código. Mantener resultados parciales sin promoverlos a éxito. |
| WHATSAPP | Reconciliar el punto de reanudación en C y adaptar sus tramos pendientes al cierre común aprobado. Conservar deuda AC5, contratos aditivos, pruebas de botón seguro, aislamiento interno/cliente, corrida única y lectura directa de VERIFY. Resolver con la gobernanza común la discrepancia ya registrada sobre cuándo regenerar DOMAIN_PRIMER, sin tratar su generación y su validación como la misma operación. |
| JEV | Reconciliar arranque y disponibilidad real de la interfaz; integrar contra el contrato corregido, sin duplicar cliente ni acomodar silenciosamente el consumidor. B depende técnicamente de B+C offline de CONTEXTO, no de aceptabilidad semántica real; el orden de cierre/índice es gobernanza separada. Conservar muestra humana, congelación, comparador, reservas, cuotas, aislamiento del SDK y autorizaciones por etapa. |
| ESCRITURA-QMIND | Resolver consulta/ingesta real frente a prohibición de red y AC6 posterior al cierre de WHATSAPP frente a una sesión que debe precederlo. Separar entrega offline de aceptación remota posterior, con estado parcial explícito y propietario. Conservar verificación por contenido, saneamiento, no-PASS por instrumento ausente y tratamiento autorizado de fuentes vigentes. |

Actualizar maestro, contrato, prompts pendientes y resúmenes que expresen las reglas afectadas; no hacer reemplazos globales ni copiar esta orden completa en cada plan. Las fases cerradas conservan su evidencia; los estados actuales incorrectos se rectifican con atribución, no se reconstruye el pasado.

## 5. Decisiones para aprobación y coordinación

| Decisión | Recomendación | Estado |
|---|---|---|
| Alcance de implementación | Aprobar A, B y C por bloques y archivos concretos; autorizar expresamente los cambios centrales/configuración necesarios | PENDIENTE |
| Encaje con deudas | Enlazar A con S11/S12 y B con D1/D3 de CONTEXTO, sin crear propietarios paralelos; mantener D2 y activación D7 fuera. Adelantar D3 respecto a su disparador actual requiere decisión expresa, no interpretación | PENDIENTE |
| Fecha de REGISTRY | Un único escritor para fecha de última entrada; fecha de release por separado, sin cambiar VERSION para reparar el registro | PENDIENTE |
| Entrega y permisos remotos | Entrega offline verificable, aceptación remota posterior con autorización y presupuesto propios; no fingir que una prohibición de red permite una subida | PENDIENTE |
| Piloto | FASE-C de CONTEXTO después de remediación y enmiendas, bajo mandato propio; no ejecutarla como parte de redactar o aprobar esta orden | PENDIENTE |

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
| Registrar en el plan CONTEXTO la aceptación de la remediación A de S11/S12 y actualizar la advertencia vencida de su README («nunca correr el default sobre el árbol vigente», que ya no aplica tras S12). No es un traslado desde asignación exclusiva: el propio plan ya contemplaba «quien toque el script antes» | Plan propietario CONTEXTO (fuera de la autorización de estas sesiones) |
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


## 6. Criterios de aceptación de la implementación futura

- [ ] Los contraejemplos quedan como regresiones: fallan en la revisión anterior por la causa esperada y pasan tras el fix; la suite existente conserva sus garantías. Fallos ajenos se atribuyen, no se ocultan.
- [ ] PRE/POST comparable demuestra reducción de escaneos repetidos, sin saltar comprobaciones ni reutilizar un resultado sobre entradas modificadas. Publicar tiempos reales aunque el ahorro sea nulo.
- [ ] Registrar una fase y verificar sincronización ya no genera por sí mismo el conflicto de fechas; re-medir un verificador no modifica evidencias históricas.
- [ ] Cada estado/métrica tiene fuente identificada; no se exige mantener manualmente el mismo dato en múltiples documentos. Las decisiones humanas siguen explícitas y no se fabrican mediante plantillas.
- [ ] Los cuatro planes tienen un punto de reanudación coherente y contratos prospectivos compatibles; permisos, propietarios y fronteras técnicas siguen distinguibles. Índice y validadores pertinentes se verifican sobre el árbol final sin relajar baselines para absorber errores.
- [ ] El piloto informa defectos, retrabajo, tiempos y coste documental con instrumento y límites declarados. No comparar su duración total con las tres horas de B como si fueran trabajos equivalentes ni atribuir causalidad a una sola muestra.

**Fuera de alcance:** producto hotelero, umbrales de seguridad/publicación, multiplicar corridas, nuevas inferencias, instalar SDKs, rotar credenciales, limpiar históricos, editar trabajo ajeno, publicar QMind, archivar, commit o push sin mandato separado. No modificar `.cursorrules` por arrastre de una sincronización no autorizada.

## 7. Arranque de la próxima sesión de revisión

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
