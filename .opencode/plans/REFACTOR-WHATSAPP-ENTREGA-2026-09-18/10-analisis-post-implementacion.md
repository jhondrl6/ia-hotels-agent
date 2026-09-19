# Análisis post-implementación — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado: PREPARACIÓN; análisis creado desde la concepción conforme al executor. No hay resultados post-implementación ni fixes certificados. Versión base 4.77.0; versión objetivo propuesta 4.78.0, sujeta a confirmación al iniciar RELEASE.

## Resumen de ejecución

| Fase | Sesión | Estado | Iteraciones y unidad | delegate_task | Notas |
|---|---|---|---|---|---|
| Preparación | 2026-09-18 | En curso | No se declara cumplimiento estimado | Investigación read-only | Contexto y workflow cargados; no se ejecutó v4complete |
| A | Nueva sesión | PENDIENTE | Por medir | Solo recuperación independiente de evidencia | Contratos y prerrequisitos |
| B | Nueva sesión | PENDIENTE | Por medir | No | Promesa ejecutable y señal HTML |
| C | Nueva sesión | PENDIENTE | Por medir | No | Botón seguro y confianza |
| D | Nueva sesión | PENDIENTE | Por medir | No | Veredicto y diagnóstico de bloqueos |
| E | Nueva sesión | PENDIENTE | Por medir | No | Entrega y evidencia interna |
| F | Nueva sesión | PENDIENTE | Por medir | Solo pistas independientes sin secretos | Seguridad de salidas |
| G | Nueva sesión | PENDIENTE | Por medir | No | Verificador automático de cableado |
| H | Nueva sesión | PENDIENTE | Por medir | Preparación de inventarios sin imports | Integración offline y preflight |
| E2E | Nueva sesión | PENDIENTE | Por medir | Sí, si entorno y presupuesto lo permiten | Única corrida y snapshot |
| VERIFY | Nueva sesión | PENDIENTE | Por medir | No | Certificación directa, sin fixes |
| RELEASE | Nueva sesión | PENDIENTE | Por medir | Documentación con allowlist | Cierre y archivado |

## Matriz de verificación de hallazgos

Copiar la matriz completa de ACs del maestro al certificar y llenar una fila por AC, sin agrupar rojos con verdes.

| AC | Hallazgo | Expected | Real | Fuente y clave | Status |
|---|---|---|---|---|---|
| AC1–AC19 | Ver `01-plan-maestro.md` | Contratos del maestro | Sin medición post | Sin artefactos nuevos | PENDIENTE |

Estados: SUPERADO EN E2E, VERIFICADO OFFLINE, NO EJERCITADO EN E2E, FALLA, BLOQUEADO EXTERNO. Un offline verde no se convierte en SUPERADO EN E2E. La certificación global falla si un AC obligatorio carece de evidencia suficiente.

## Comparación histórica y post-implementación

| Dimensión | P4 histórico | Post de este plan | Límite causal |
|---|---|---|---|
| URL | Dominio histórico distinto del solicitado ahora | `https://www.donalfonsohotel.com/` | No es un experimento A/B equivalente |
| Datos financieros | Fuente warehouse según reportes históricos | Verificar selección exacta y procedencia | No completar campos ausentes |
| WhatsApp / pains / promesa | Releer JSON histórico saneado | Por medir | Red y fuentes pueden variar |
| IMPLEMENTATION_ORDER | Stub en corpus anterior a correcciones P6/P6-R | Leer writer actual y ZIP nuevo | No extrapolar stub histórico al HEAD |
| Score / veredicto | 0.8966666 / false documentados en P4 | Por medir sin confundir redondeo con cálculo distinto | Registrar todos los gates |
| Acta / revisores / entrega | ZIP suprimido | Por medir | Bloqueo legítimo no es fallo del enforcement |

## Lecciones aprendidas

### Lecciones capitalizadas de planes anteriores

Espejo semántico de `00-lecciones-capitalizadas.md` §2; anotar aquí aplicación real, no volver a decidir los IDs.

| Grupo | Aplicación esperada | Resultado observado |
|---|---|---|
| Cableado y narrativa | Igualdad entre productores, promesas y assets | Pendiente |
| Mutaciones y layout | Símbolo real y ZIP real | Pendiente |
| Ausencia y error | Estados no colapsados | Pendiente |
| Evidencia y certificación | Una corrida, snapshot antes de analizar, VERIFY sin fixes | Pendiente |

### Lecciones nuevas de este plan

Sin lecciones **post-implementación**: ninguna fase se ha ejecutado. Las nueve filas siguientes son lecciones de **preparación** (seis primeras, 2026-09-18 y 2026-09-19) y de la **intervención del 2026-09-19** sobre el prompt de Gemini/purga (tres últimas), sustentadas en mediciones reales de lectura y ejecución —código vivo, evidencia archivada de FASE-P4, el sitio público del hotel y la corrida de la tarea 7—, y se registran aquí para que VERIFY las contraste contra lo ejecutado, no para darlas por certificadas.

Al cierre de cada fase registrar al menos tres observaciones sustentadas: **qué pasó / por qué / qué lo previene**, con pertinencia INCLUIR o EXCLUIR. No inventar una novedad para cubrir una cuota: si se confirma una lección existente, registrar su confirmación medida como tal.

| ID | Lección (qué pasó / por qué / qué lo previene) | Evidencia medida | Prevención asignada | Pertinencia |
|---|---|---|---|---|
| L-ENT.1 | **Un estado agregado archivado se hereda como si fuera causa.** Un snapshot de FASE-P4 registró `confidence 0.3, site_verified false` en los cinco probes; el plan heredó la lectura "el sitio era inalcanzable, la señal es falsa por honestidad". Re-medido hoy: el dominio del warehouse **no resuelve** y el sitio real responde 200 con el canal servido por un plugin. / Por qué: el artefacto guarda un resultado, no el modo de fallo, así que DNS vacío, respuesta sin cuerpo, HTML sin marcaje y excepción tragada comparten el mismo valor. / Qué lo previene: publicar alcance de observación y estado de lectura separados, nunca un único agregado. | `evidence/FASE-P4/corrida/run/v4_complete/hoteldonalfonso/v4_audit/site_presence_snapshot.json` + sonda HTTP del 2026-09-19 | AC19 y AC9 | INCLUIR |
| L-ENT.2 | **La pregunta no es "¿existe el canal?" sino "¿puede el lector observarlo, en qué ruta y en qué marcaje?".** La home del sitio vivo tiene 0 referencias a WhatsApp y `/contacto/` tiene 54, todas dentro de `<style>` o de `href`/`src` del plugin; ningún `wa.me` ni número en HTML estático y el método de detección devuelve `found: False` ante cualquier excepción. / Por qué: F-F y F-A' gobiernan promesas y cableado, pero el falso positivo nace aguas arriba, en la cobertura del detector; corregir el dato no cambia lo que el lector no mira. / Qué lo previene: gobernar el lector como parte del fix, y prohibir que una señal negativa sin alcance verificado se redacte como ausencia. | Sonda con el código real del checker sobre ambas URLs, 2026-09-19 | AC19 (lector en C, consumo en B); matriz §2 fila "canal existe pero el lector no lo observa" | INCLUIR |
| L-ENT.3 | **Un default de código se fosiliza como dato verificado cuando viaja por un fixture.** El fixture versionado del hotel fija canal directo 20.0 contra los 30.0 del warehouse, con `epistemic_status: verified, confidence: 0.95`; el 20.0 es el respaldo de un `datos.get(...)` del propio test e2e y el encabezado del fixture afirmaba "no introduce datos nuevos" tras enumerar solo tres campos comprobados. / Por qué: el metadato de confianza se copió del contenedor y no del productor del valor; un comentario humano no es un verificador. / Qué lo previene: procedencia por campo con su productor declarado, y la regla de no citar un default como verificado. | Comparación fixture ↔ `data/hotel_observations/observations.json` ↔ literal del test e2e | AC14; deuda §6 "Procedencia del dato Don Alfonso" | INCLUIR |
| L-ENT.4 | **Un rojo del working tree caduca: se hereda como prerrequisito y al re-medirlo ya no existe — y mi explicación del mecanismo también cayó.** El quick PRE del 2026-09-18 daba 9/10 por Version Sync y se registró en tres documentos como "A necesita autorización central". Hoy el quick da **10/10** sin que yo tocara nada: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados al abrir la sesión y ahora son idénticos a HEAD (mtime 11:06-11:10, revertidos fuera de esta sesión). Además, mi causa propuesta —"el check espera cuatro segmentos"— quedó **refutada** al leer `_check_version_sync` completa: solo ejecuta `sync_versions.py --check`, la misma herramienta que yo había visto pasar. / Por qué: heredé un estado transitorio del árbol y después inferí un mecanismo leyendo un fragmento del verificador; las dos cosas son atajos sobre mediciones incompletas. / Qué lo previene: re-medir los rojos al abrir cada fase y no convertirlos en prerrequisito de otra sesión; y antes de publicar una causa, leer el check completo, no la ventana que coincidía con mi hipótesis. | `git status` inicial frente al de hoy, mtimes de los 4 documentos, quick 10/19 10/10 y lectura de `scripts/run_all_validations.py::_check_version_sync` | §1, §6 y §7 del maestro corregidos; A ya no requiere autorización central | INCLUIR |
| L-ENT.5 | **Editar una tabla anclando en otra fila completa la reemplaza.** Al insertar AC19 en la matriz del checklist, el ancla fue la fila AC18 y el resultado quedó sin AC18. / Por qué: la coincidencia de texto no valida la estructura del documento; la pérdida era invisible sin contar. / Qué lo previene: conteo de miembros antes y después de editar, y comprobación de persistencia sobre el commit y no sobre el buffer. Detectado en la misma sesión y remediado. | Registro del error y su reparación en la sesión del 2026-09-19; matriz re-verificada con 19 filas AC en maestro y checklist | Proceso de edición, no producto | INCLUIR como límite de proceso |
| L-ENT.6 | **El consentimiento liga una identidad concreta, no un nombre comercial.** La autorización de FASE-P4 amparaba una corrida de diagnóstico sobre la URL del warehouse —hoy inexistente— y declaraba explícitamente que no era entrega a cliente; la corrida propuesta se lanzaría sobre un dominio distinto. / Por qué: el documento describe su objeto con la URL, y ese objeto ya no existe, de modo que la vigencia nominal del consentimiento no cubre el destino nuevo. / Qué lo previene: reemitir el consentimiento datado sobre la URL viva con su límite escrito, y verificar identidad única y hash de la fuente antes de consumir el único intento. | `evidence/FASE-P4/consentimiento-donalfonso.md` frente a la sonda DNS/HTTP del 2026-09-19 | AC14/AC17 (preflight de H); deuda §6 de procedencia | INCLUIR |
| L-ENT.7 | **Todo estado heredado caduca, incluido el que el prompt de apertura afirma como hecho — segunda confirmación medida del patrón de L-ENT.4, ya no solo de rojos.** El prompt de la intervención del 2026-09-19 daba por ciertos tres estados y los tres habían cambiado: los "3 commits SIN push" ya estaban pusheados (divergencia real 0/0), el árbol "sucio en `.opencode` por trabajo ajeno" estaba limpio (commits ajenos ya ingresados), y la revocación que mandaba pedir al operador "no su valor" ya estaba confirmada por este el día anterior. / Por qué: un prompt registra mediciones en el momento de redacción y se ejecuta después; el agente que no re-mide hereda comandos sobre hechos difuntos. / Qué lo previene: el primer bloque de toda sesión debe re-medir las premisas (git, registros externos, acreditaciones) antes de ejecutar la primera tarea; aquí la orden expresa "verifica antes de fiarte" salvó la sesión — la re-medición costó tres comandos. | `git rev-list --count origin/master..master` = 0, `git status --short` vacío, confirmación de rotación del operador 2026-09-18 | Apertura de A y de cada fase; FASE-A ya la aplica en su propia Tarea 3 reescrita | INCLUIR |
| L-ENT.8 | **Un hit de escáner es una forma, no una credencial: la naturaleza medida rebajó el nivel de contención de force-push a redacción de 8 líneas.** La key marcada para purga de historial (reescribiría todos los SHA y 7 tags, con blast radius máximo sobre master compartido) resultó ser el key estático firmado que Google incrusta en su propio HTML de Maps, capturado por scraping: sin coincidencia con ninguna key viva del `.env`, no funcional como credencial del operador. El cierre proporcional fue redacción en HEAD + riesgo residual documentado + condición de escalada explícita. / Por qué: los patrones detectan sintaxis; ownership, vigencia y explotabilidad son mediciones aparte que el plan de escalación heredó sin repetir. / Qué lo previene: antes de elegir nivel de contención, medir procedencia (quién escribió, coincide con viva, firmada, inerte) y documentar la condición por la cual sí escalaría. | Contexto `html_sample_end` en `archives/gbp_profiles.json`, contraste con claves del `.env` (0 coincidencias), cierre `a107f3c` con nota en AC-S3-S4 | F (seguridad de salidas): clasificar por naturaleza antes de costear contención | INCLUIR |
| L-ENT.9 | **Un proveedor configurado no es un proveedor ejercitado: la métrica agregada verde oculta qué rama corrió.** La corrida e2e salió verde (`source=llm_check`, 5/5 consultas medidas) con Gemini vigente en el `.env`, pero cero consultas lo alcanzaron: OpenRouter es prioridad 1 y el bucle rompe al primer proveedor que responde. Solo `providers_used` delató la rama no ejercitada, y hubo que verificar Gemini con una llamada directa (`gemini-flash-latest`, 864 tokens, coste $0.0021 derivado). / Por qué: la métrica agrega "hubo medición", no "con quién"; en un diseño de corrida única como este plan, la rama silenciada no tiene segunda oportunidad de manifestarse. / Qué lo previene: exigir evidencia por rama ejercitada (quién respondió cada unidad) en la certificación E2E/VERIFY, igual que se exige por AC; un verde agregado no convierte en SUPERADO EN E2E una ruta NO EJERCITADA. | `evidence/tarea7-corrida.log` línea 129 (`Providers: openrouter`), prueba directa `_query_gemini` del 2026-09-19 | E2E/VERIFY: matriz por rama de proveedor, no solo por AC | INCLUIR |

Reservar IDs propios —la serie `L-ENT.1` a `L-ENT.9`, verificada como libre— solo después de comprobar que no existan en el corpus: la búsqueda del 2026-09-19 en el índice devolvió cero coincidencias para ese prefijo, que entonces definía 305 IDs; la segunda pasada, tras la intervención del mismo día, verificó libres los tres tokens nuevos sobre un índice de 311.

**Efecto medido de registrarlas.** Las seis filas pasaron a contar como definiciones: el índice pasó de 305 a 311 IDs. Una redacción anterior que nombraba el patrón completo en prosa fabricó además una cita huérfana y elevó «citados sin definición» de 43 a 44; al reescribir la frase sin ese token, la métrica volvió a 43. Esto **no** se capitaliza como lección nueva del plan —la convención ya la declara el encabezado del propio generador— y queda aquí solo su confirmación medida: un enunciado en prosa es un ID a efectos del índice, así que un patrón se escribe con sus miembros concretos o en lenguaje llano. Las tres filas de la intervención del 2026-09-19 (verificadas al regenerar el índice) lo llevaron de 311 a 314 IDs sin crear ninguna cita huérfana: «citados sin definición» permaneció en 43.

## Seguimientos abiertos

| Tema | Estado | Dueño | Acción / condición de cierre |
|---|---|---|---|
| F-P4.3 / HALLAZGO-N4 / BUG-6 | Retomado, no duplicado | Orquestación + generación; onboarding conserva D1 | Cerrar bloqueo por promesa imposible, no afirmar que D1 queda implementado |
| F-B / contacto warehouse | DIFERIDO, no autorizado | Producto + privacidad + onboarding | Decisión escrita de campos comerciales permitidos, fuente y consentimiento antes de ampliar esquema/formulario/adaptador |
| F-E / no evaluable | DIFERIDO | Coherencia | Contrato serializado y tests vacío/ausente/error, sin bajar protección del botón |
| F-D / parámetro descartado | A resolver en A/D | AssessmentBuilder | Eliminar contrato muerto si no tiene consumidores; no reintroducir una segunda fuente de confianza |
| DomainGateEngine de WhatsApp | Fuera de la ruta del fix | Quality gates | Conservar documentado como legado mientras existan tests; no usarlo para certificar producción ni archivarlo sin autorización |
| F-P4.1 | Recalificar contra HEAD | Delivery | Distinguir corrección P6/P6-R de contenido histórico; fortalecer tests donde falte evidencia |
| F-P4.2 | En alcance | Orquestación + revisores | Preservar lectura de artefactos internos sin entregar bloqueados ni contar ausencias causadas por el propio borrado |
| F-P4.5 | **CERRADO POR ACREDITACIÓN DEL OPERADOR (registrado 2026-09-19)**: rotación de la key Gemini-local (AIzaSyDq…) confirmada por el operador el 2026-09-18, con ocasión de la intervención previa; registro en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md`. La key de `archives/gbp_profiles.json` no aplica a este cierre: es el key estático firmado de Google en HTML scrapeado, resuelto como higiene de HEAD (a107f3c) con riesgo residual documentado | Operador de credenciales + providers | A/F referencian el registro, no la vuelven a pedir; la prevención activa ya la validan los tests de redacción (48a242b). Acreditación = afirmación del operador, no inferible del repo |
| Version Sync del quick PRE | **CERRADO POR MEDICIÓN 2026-09-19**: el quick pasa 10/10. El rojo del 2026-09-18 venía de cuatro documentos sucios en el árbol (`AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md`, `REGISTRY.md`), hoy idénticos a HEAD tras una reversión externa a esta sesión. La explicación "desacuerdo verificador↔escritor" se retracta: `_check_version_sync` solo invoca `sync_versions.py --check` | Operador | Nada que autorizar en A. Verificar de nuevo el quick al abrir cada fase; si reaparece, leer el check completo antes de atribuirle una causa |
| Procedencia del dato del hotel (L-ENT.3, L-ENT.6) | **ARCHIVADO COMO PENDIENTE DE OPERADOR (cierre de sesión 2026-09-19, v4.77.3)**: la sesión no aportó el valor gobernante ni la reemisión del consentimiento; no cierra por medición | Datos/procedencia + operador | Valor gobernante declarado con productor; fixture corregido desde ahí y consentimiento re-emitido datado sobre la URL viva antes de consumir el intento. Reabir solo con entrada del operador |
| Una corrida insuficiente por fallo externo | Condicional | Operador | Conservar resultado; nueva corrida requiere ampliar expresamente presupuesto y plan |

## Métricas de ejecución

Registrar por fase funciones canónicas, casos pytest, passed/failed/skipped/xfailed, delta, hashes de PRE/POST, mutaciones por AC y tiempo real de ejecución. No sumar unidades incompatibles. Mantener contador único de invocaciones v4complete: actualmente 0, máximo autorizado en el diseño 1.

## Decisiones arquitectónicas

| Decisión | Rationale | Alternativas | Estado |
|---|---|---|---|
| Promesa condicionada por dato utilizable | Evitar colisión catálogo/coherencia sin bajar umbrales | F-C y rescate HTML muerto rechazados | Propuesta para ratificar en A |
| F-B y F-E diferidos con AC propio | No ampliar PII ni cambiar modelo sin necesidad | No confundir diferir con resolver | Propuesto |
| Evidencia interna distinta de entrega cliente | El Juez debe leer lo realmente generado antes de suprimir ZIP | Borrado previo produce hallazgos derivados | Contrato a cerrar en A/E |

## Checklist de cierre

- [ ] Todas las fases previas y sus cierres reales completos.
- [ ] Matriz por AC con artefacto, clave, alcance y limitaciones.
- [ ] Una sola corrida acreditada; no reintentos ocultos.
- [ ] Lecciones y deudas con dueño y condición de cierre.
- [ ] Write-back autorizado y contenido final comprobado antes de archivar.
- [ ] Índice regenerado antes y después del archivado.
- [ ] Validaciones verdes sin ocultar fallos previos.
- [ ] Cierre de RELEASE con versión confirmada, sin cambios de código.

## Cierre del plan

PENDIENTE. Este encabezado se completa únicamente en RELEASE después de la certificación; no anticipa éxito.
