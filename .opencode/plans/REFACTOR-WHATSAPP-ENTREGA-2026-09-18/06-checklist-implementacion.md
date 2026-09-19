# Checklist de implementación

**Estado documental inicial: todo PENDIENTE. Contador v4complete: 0/1. Siguiente sesión: A.** No se han ejecutado fases, validaciones o pruebas en esta escritura. Ningún casillero implica aprobación o certificación.

Contratos: [maestro](01-plan-maestro.md), [ejecución](04-contrato-ejecucion.md), [lecciones](00-lecciones-capitalizadas.md) y [dependencias](dependencias-fases.md). Las rutas de evidencia citadas son salidas futuras bajo `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-<ID>/`, no archivos cuya existencia se afirme aquí.

## Estados de las once sesiones

| Fase | Prerrequisito | Foco de aceptación | Estado | Evidencia de cierre |
|---|---|---|---|---|
| A | Mandato de sesión | Baseline, permisos, matriz ratificada, identidad/vigencia; AC14 | PENDIENTE | PENDIENTE |
| B | A cerrada | AC1, AC2, AC15, AC19 (consumo) | PENDIENTE | PENDIENTE |
| C | B cerrada | AC3, AC5, AC6, AC15, AC19 (lector) | PENDIENTE | PENDIENTE |
| D | C cerrada | AC4, AC5, AC8, AC9, AC15 | PENDIENTE | PENDIENTE |
| E | D cerrada | AC9, AC10, AC11, AC12, AC15 | PENDIENTE | PENDIENTE |
| F | E cerrada | AC13, AC15 | PENDIENTE | PENDIENTE |
| G | F cerrada | AC7, AC16, AC15 | PENDIENTE | PENDIENTE |
| H | G cerrada | AC9, AC12, AC13, AC14, AC15, AC17 offline | PENDIENTE | PENDIENTE |
| E2E | H cerrada y preflight favorable | AC17 real; preservación del único resultado para AC18 | PENDIENTE | PENDIENTE |
| VERIFY | E2E cerrada con evidencia | AC18; contraste transversal AC1–AC19, directo y sin ejecución | PENDIENTE | PENDIENTE |
| RELEASE | VERIFY cerrada y alcance de cierre explícito | Cierre documental autorizado y límites publicados | PENDIENTE | PENDIENTE |

Una fase por sesión y cadena estrictamente secuencial. Un checkpoint INCOMPLETA no habilita la siguiente. Registrar el estado observado sin sustituir un fallo legítimo por una aprobación documental.

## Matriz AC1–AC19

Todas las filas requieren evidencia del writer/consumidor real. Separar después resultado offline, ejercicio real E2E y dictamen de VERIFY; hoy los tres están PENDIENTES. Los casos no ejercitados no pasan a SUPERADO EN E2E por tener tests verdes.

| AC | Fases responsables | Comprobación y evidencia esperada | Sensibilidad / límite obligatorio | Estado |
|---|---|---|---|---|
| AC1 | B; VERIFY contrasta | Main, diagnostic y orquestador producen los mismos pain_ids para entradas producibles; `pain_ledger.json.entries` sin ausencia fantasma ante HTML visible | Retirar HTML en detect_pains rompe igualdad/pain correcto; no exigir el bloqueo histórico si el mapping ya cambió | PENDIENTE |
| AC2 | B; VERIFY contrasta | Propuesta, specs, `asset_generation_report.json`, matriz de servicios y ledger coinciden; setup sin número utilizable, sin promesa de botón listo | Reintroducir botón para ausencia en mapper/catálogo/productores vivos rompe contrato; pain sigue visible como acción pendiente, no instalado | PENDIENTE |
| AC3 | C; VERIFY contrasta | Botón forzado con confianza menor que 0.9, CONFLICT, UNKNOWN o centinela queda en error en `coherence_validation*.json.checks`, aun con presence exists | El test negativo pasa cuando bloquea; debilitar guard/boost lo hace fallar. Guía no oculta hard contradictions | PENDIENTE |
| AC4 | D; VERIFY contrasta | `gate_report_*.json.gate_results[coherence].details.failed_check_names` y mensajes conservan todos los checks en error del reporte real | Dos errores conservan ambos nombres; quitar cable/serialización produce rojo. Vacío válido no equivale a fuente ausente | PENDIENTE |
| AC5 | C/D; VERIFY contrasta | `thresholds.json` documenta fuente y valor: coherencia 0.8, WhatsApp 0.9, blocking=True y enforcement intacto | Assertions de invariantes; no bajar gates/catálogo para aceptar ESTIMATED ni cambiar flags de bloqueo | PENDIENTE |
| AC6 | C; VERIFY contrasta | HTML y ZIP sin wa.me vacío, centinelas, placeholders o sustitución por phone_web; destino igual al canal verificado normalizado | Sin dígitos, separadores, dígitos no ASCII, longitud inválida y teléfono alternativo; revertir guard hace rojo | PENDIENTE |
| AC7 | G; VERIFY contrasta | `wiring_report.json` expone población descubierta de validate/detect_pains, kwargs, fuentes, excepciones tipadas y conexión al quick | Caller nuevo en archivo nuevo, señal omitida/kwargs opacos hacen rojo; cubrir aliases/self y excluir validate ajenos | PENDIENTE |
| AC8 | D; VERIFY contrasta | Reporte pre-gate persistido y log saneado con causas; veredicto False bloquea antes de generar aunque score supere 0.8 | Spy confirma generador no invocado, también en entrada directa del orquestador; restaurar decisión por score hace rojo | PENDIENTE |
| AC9 | D/E/H; VERIFY contrasta | Cada lector nuevo distingue READ_OK, incluido vacío, ABSENT y READ_ERROR con causa; retención deliberada registrada aparte | Tres casos por lector más retención; baseline real con skip visible si falta y AC sin certificar; no fallback favorable 0/None | PENDIENTE |
| AC10 | E; VERIFY contrasta | IMPLEMENTATION_ORDER dentro del ZIP real contiene tareas, rutas ASSETS existentes, setup/guía y manifiesto coherentes | Revalidar regresión P6-R y asset nuevo; desconectar rutas reales o recuperar stub hace rojo, no certificar por tamaño | PENDIENTE |
| AC11 | E; VERIFY contrasta | `review_input_manifest.json.documents` contiene run_id, fuente original, hash, ruta interna, read_status y disposition=retained_by_gate cuando corresponda; revisores leen snapshot | Borrado sin snapshot o pérdida de ruta hace rojo; nunca generado sigue ausente; snapshot fuera del árbol exportable | PENDIENTE |
| AC12 | E/H; VERIFY contrasta | `acta_revision.json.enforcement` y `package_evidence` conservan decisión/hash/conteo; solo publish permitido crea ZIP final y bloqueo suprime cuarentena | Pares permitir/bloquear del flujo real, sin snapshot retenido en ZIP público ni doble hallazgo por borrado propio; distinguir cuál ocurrió en E2E | PENDIENTE |
| AC13 | F/H; VERIFY contrasta | Consola, archivos y snapshots nuevos redactan antes de persistir; `sanitization_report.json` sin valores y `credential_status.json` con prueba operativa o pendiente | Desactivar redacción produce rojo con secretos sintéticos; tests o key nueva no prueban revocación | PENDIENTE |
| AC14 | A/H; VERIFY contrasta | `onboarding_provenance.json`: hash de observations original, selector único, URLs histórica/solicitada y fechas; loader real toma YAML derivado y output declara fuente | Nombre ausente/ambiguo, hash cambiado o frescura rechazada detienen preflight, sin defaults, alias global o fecha alterada | PENDIENTE |
| AC15 | Todas las implementaciones/H; VERIFY contrasta | PRE/POST con misma selección/entorno, exit codes y delta explicado; `mutation_report.json` por AC, guard y test | PRE antes de editar tests; rojo causado por guard y no syntax/import; no ocultar regresiones ni mezclar funciones con casos parametrizados | PENDIENTE |
| AC16 | G; VERIFY contrasta | Inventario AST de with_validation sin argumento descartado; check legacy clasificado; ValidationSummary conserva su dato upstream | Caller con firma vieja hace rojo; no crear verdad paralela whatsapp_validation ni borrar variable todavía consumida | PENDIENTE |
| AC17 | H/E2E; VERIFY contrasta | `run_control.json` con state, attempts, PID, argv, timestamps, hashes, exit_code y snapshot; preflight attempts=0, proceso único attempts=1 | Segundo lanzamiento rechazado antes de spawn aun tras fallo/timeout; pruebas con hijo falso, nunca otra v4complete | PENDIENTE |
| AC18 | VERIFY | Matriz final en `10-analisis-post-implementacion.md` y `certificacion.json`, diff estructural, lecciones, límites y dueños | Un resultado offline no demuestra rama E2E; READY exige gates/acta favorables y ZIP válido, no exit 0. Parcial/FALLA impide cerrar como éxito integral | PENDIENTE |
| AC19 | C (lector) y B (consumo); VERIFY contrasta | Reporte de presencia con `observation_scope`, `read_status` del fetch y `presence_evidence_kind`; señal negativa sin alcance verificado registra `no_verificado_en_sitio` y no crea dolor de ausencia confirmada | Reducir el lector a la raíz, tragar la excepción como `found=False` o derivar un número de la huella del plugin hace rojo. Don Alfonso es el caso real esperado, no un test | PENDIENTE |

## Prerrequisitos de entrada

- [ ] A re-mide el quick al inicio y registra el resultado observado. El 9/10 del 2026-09-18 quedó resuelto solo: eran cuatro documentos sucios en el árbol y el 2026-09-19 marca 10/10 con esos archivos ya idénticos a HEAD. No se arrastra como prerrequisito de autorización central.
- [ ] B/C gobernan AC19: el lector declara qué rutas inspeccionó y B no convierte una señal negativa sin alcance verificado en ausencia confirmada del canal.
- [ ] A resuelve el mandato documental de DOMAIN_PRIMER antes de regenerarlo; no cambia reglas centrales para eliminar la divergencia.
- [ ] A mantiene F-B privacidad/D1 diferida: no PII WhatsApp nueva en warehouse ni cambios de formulario/esquema sin decisión escrita. El setup no certifica cierre de esa deuda.
- [ ] A/H conservan fuente del 2026-07-22 y comprueban vigencia frente a `ONBOARDING_FRESHNESS_HOURS`, sin leer secretos ni falsear fecha o defaults.
- [ ] A/H registran binding local explícito: original `https://hoteldonalfonso.com/`, solicitada `https://www.donalfonsohotel.com/`; selector único y hash, sin alias universal ni redirección inferida.
- [ ] F/H acreditan revocación mediante evidencia operativa sin secreto, o mantienen pendiente AC13 y el cierre correspondiente; no inferirla de tests o key nueva.
- [ ] Se distingue QMind accesible para consulta de upload autorizado. Sin autorización de subida, no subir material ni declarar write-back exitoso; registrar checkpoint si bloquea el cierre requerido.

## Gates, contratos y no regresión

- [ ] WhatsApp conserva umbral 0.9; coherencia conserva 0.8. Presencia HTML informa presencia, no verificación de número ni permiso para usarlo en assets.
- [ ] CONFLICT, UNKNOWN, ESTIMATED no se promueven automáticamente a botón operativo; centinelas nunca son destino. Teléfono web no prueba WhatsApp.
- [ ] Hard contradictions, causas reales y blocking permanecen visibles; setup/guía no ocultan un botón inseguro forzado.
- [ ] Se mantienen `TribunalJudge._compute_verdict`, flags de bloqueo y contratos `write/publish/suppress`; solo decisión favorable permite publicación final.
- [ ] El ledger conserva el pain pendiente y la identidad de servicio entre productores; no convierte una instrucción de setup en canal implementado.
- [ ] Lectores distinguen vacío válido, ausencia original, error de lectura y retención inducida; no duplican hallazgos por borrado propio ni silencian fallos.
- [ ] AC19: el reporte de presencia declara `observation_scope`, `read_status` y `presence_evidence_kind`; una huella de plugin prueba presencia, nunca número, y ninguna señal negativa sin alcance verificado crea dolor de ausencia confirmada ni botón.
- [ ] Writer y revisores consumen rutas explícitas del mismo run_id; snapshot interno fuera del árbol exportado y sin escoger el archivo más reciente entre hoteles.
- [ ] `CommercialGate._check_whatsapp_verified` de domain_gates sigue clasificado test/legacy, no modificado ni usado como certificación del check productivo.
- [ ] PRE/POST y mutantes demuestran invariantes del código real con salidas serializadas. No excluir tests, cambiar expectativas o modificar baselines de validadores para ocultar rojos.

## Controles del intento único

- [ ] H solo prepara onboarding aislado, tests y runner: no añade flags CLI ni ejecuta main/v4complete como prueba.
- [ ] H verifica con hijo falso reserva exclusiva, contador persistente, rechazo de relanzamiento y captura saneada; preflight conserva attempts=0.
- [ ] E2E comprueba identidad, frescura, hashes, permisos, entorno y reserva antes del spawn; cualquier rechazo previo deja contador 0/1 y checkpoint.
- [ ] Solo E2E inicia el proceso real, mediante el runner; registra consumo 1/1 desde creación del proceso aun si falla o hay timeout.
- [ ] No hay comando manual adicional, segunda corrida, auditoría externa preliminar, force, deploy ni desactivación del Tribunal.
- [ ] Se preservan exit code, PID, argv, fechas, hashes, reportes/acta y ZIP publicado si existe; no secretos, logs crudos históricos o ZIP suprimido.
- [ ] VERIFY es directo, sin delegación, código nuevo, tests o ejecución de pipeline; analiza evidencia existente y registra hallazgos con dueño sin remediarlos.
- [ ] RELEASE es documental; no ejecuta v4complete ni repara código. Si la meta fue parcial/FALLA, lo publica como límite y no cierra como éxito integral.

## Cierre incremental y R2 por sesión

Aplicar dentro de la fase correspondiente, no diferir todo a RELEASE. Esta checklist no concede permiso para ejecutar ahora los pasos futuros del contrato.

- [ ] Se declara un máximo de cuatro tareas, incluyendo PRE/POST y cierre; E2E mantiene tres y un único comando largo externo.
- [ ] Se toma PRE antes de modificar código/tests, se espera terminación real y se registra selección, entorno, exit codes y conteos por unidad.
- [ ] Se registra POST comparable y delta explicado, junto con mutaciones del guard real, restauración y causa de cada rojo.
- [ ] Se actualizan prompt/índice/dependencias/checklist y documentos de cierre pertinentes con evidencia saneada y observaciones medidas; no se fabrica cumplimiento.
- [ ] Se realiza documentación incremental y registro de fase del contrato, sin anticipar versión nueva en fases intermedias ni tocar históricos P4.
- [ ] Se obtiene TOTAL PASS real de validaciones aplicables y ausencia de GAP dentro del alcance autorizado; si no, queda INCOMPLETA. El quick histórico 9/10 no se rebautiza verde.
- [ ] Write-back, configuración central, commit, push, tag y operaciones remotas tienen autorización específica cuando corresponda; consulta QMind no la sustituye.
- [ ] R2 registra presupuesto de referencia de 60 tool_use hasta el commit de código autorizado, instrumento `evidence/FASE-D/measure_iterations.py`, transcript y corte ISO; tiempo de pared separado.
- [ ] Si transcript no existe o se deniega acceso, se declara desde ese momento **FUERA DE SERVICIO (R2.1)**; auto-reporte con unidad separado, sin sumarlo/compararlo al instrumento ni estimar cumplimiento.
- [ ] Sin commit autorizado, no se declara consumado ese corte de R2. En fases sin código, se informa corte documental separado, nunca un commit de código ficticio.
- [ ] Presupuesto agotado o requisito pendiente producen checkpoint y nueva sesión para retomar; no se inicia otra fase ni se repite trabajo ya completado.
- [ ] VERIFY distingue SUPERADO, FALLA y NO EJERCITADO con régimen offline/E2E explícito. RELEASE refleja esa conclusión sin prometer certificación universal a partir de un hotel.

**Resumen inicial:** once estados PENDIENTES; AC1–AC19 PENDIENTES; intento 0/1; siguiente sesión A. Evidencia, permisos adicionales, validaciones y medición de ejecución permanecen pendientes.
