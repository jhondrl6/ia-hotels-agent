# Análisis post-implementación — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

Estado al 2026-09-24: **análisis vivo, cuatro fases cerradas con su fila y su evidencia** (A, G, 0 y B; B con deuda AC5 → dueño C-D) y **punto de reanudación en FASE-C**. ⟦Reconciliado por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`; la línea anterior describía la concepción («PREPARACIÓN; no hay resultados post-implementación») y quedó vencida por esas cuatro filas⟧. Versión base 4.77.0; versión objetivo propuesta 4.78.0, sujeta a confirmación al iniciar RELEASE. ⟦Puesta al día 2026-10-06: **4.78.0 quedó liberada** el 2026-09-25 por `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (`VERSION.yaml` `version: "4.78.0"`, `release_date: "2026-09-25"`; medido con `grep -nE "version|release_date" VERSION.yaml`), así que la propuesta de esta fila está vencida. La versión de este plan la decide el mandato de su FASE-RELEASE con el operador y se invoca como `--release "$VERSION_AUTORIZADA"`⟧.

**Revisión 2 (2026-09-19, HEAD `938f59f`).** Re-medición del diseño contra código vivo y contra la corrida real archivada en `output/TAREA7-2026-09-19/`. Consecuencias para este archivo: `L-ENT.1` y `L-ENT.2` quedan **rectificadas** (se conservan con la corrección a la vista), se definen `L-ENT.10` y `L-ENT.11`, y la tabla de seguimientos incorpora la causa de supresión que ninguna fase cubría.

## Resumen de ejecución

| Fase | Sesión | Estado | Iteraciones y unidad | delegate_task | Notas |
|---|---|---|---|---|---|
| Preparación | 2026-09-18 | En curso | No se declara cumplimiento estimado | Investigación read-only | Contexto y workflow cargados; no se ejecutó v4complete |
| **Revisión 2** | **2026-09-19** | Cerrada (documental) | Auto-reporte con unidad declarada; sin corte de código porque no hubo commit de código | Búsquedas read-only y ejecuciones de lectura (checker en memoria, `_compute_verdict` en memoria) | Cuatro premisas del §1 rectificadas; nacen AC20 y FASE-0; se definen `L-ENT.10` y `L-ENT.11`; QMind denegado por el clasificador |
| A | **2026-09-19 (HEAD `d4dacb4`)** | **CERRADA — commit `3e97d95` y push a `origin/master`** | **Métrica FUERA DE SERVICIO (R2.1)**: `measure_iterations.py` exige el transcript y su acceso no estuvo disponible. Auto-reporte con su propia unidad: ~50 intervenciones de herramienta, **corte documental** (A no produce código), tiempo de pared aparte. No comparable ni sumable al instrumento | Sin delegación: principal midió y decidió | 20 premisas re-medidas (`decisiones.md` §1); los 4 puntos de la revisión 2 ratificados sin reinterpretar (§3); P3 y P6 corrigen textos del plan; DOMAIN_PRIMER resuelto sin editar documentos centrales; QMind recuperado; quick 10/10; tests pertinentes 133 passed + 1 skipped offline; **contador v4complete sigue 0/1** |
| G | **2026-09-20 (HEAD de partida `d7ff932`)** | **CERRADA — commit `66e17bd` y push a `origin/master` (paridad 0/0)** | **Métrica FUERA DE SERVICIO (R2.1)**: el instrumento pide el transcript y no estuvo disponible. Auto-reporte con unidad contable propia (9 rutas tocadas: 5 modificadas +125/−21 y 4 nuevas; 2 corridas de baseline + 1 extendida; 7 mutaciones; 2 quicks), corte de código y corte documental separados, **sin comparar** con la referencia de 60 porque no es la unidad medida. Tiempo de pared aparte | Sin delegación: el inventario lo produjo el propio instrumento, no un subagente (así se evita repetir el episodio de la cifra 50/779 medida por subagente y nunca re-medida) | AC7 y AC16 verificados offline con sus rojos; quick 10/10 → **11/11**; 4.246 → **4.264** funciones canónicas; **la fila F-A' del plan quedó subdimensionada: son tres invocaciones divergentes, no una**; QMind recuperado por el eje de cierre (Q12, 6 aportes, 3 aplicados y medidos); rojo preexistente con causa raíz medida y conservado sin excluir. **Contador v4complete 0/1** |
| **0** | **2026-09-20 (HEAD de partida `ad0cc84`)** | **CERRADA con código de producto, commiteada y empujada el 2026-09-20 (`7c6e75f` → `origin/master`, paridad 0/0 verificada por `git ls-remote`, 7/7 checks del hook en verde sin saltarlos)** | **Métrica FUERA DE SERVICIO (R2.1)**: `measure_iterations.py` sigue pidiendo el transcript y no estuvo disponible. Auto-reporte con unidad propia: ~45 intervenciones de herramienta contadas a mano sobre el registro de la sesión, de las cuales ~28 hasta el último estado de código; **corte de código = no consumado** (no hay commit); tiempo de pared aparte: suite completa 232 s y 6 mutaciones ~12 s. No comparable con la referencia de 60 | Sin delegación: la causa raíz, el par contrafactual y la serie del gate son decisiones de arquitectura con evidencia en el worktree | AC20 **VERIFICADO OFFLINE** con el par `BLOQUEADO → APROBADO-CONDICIONAL-PENDING-ONBOARDING` medido sobre el acta archivada; AC12 **PARCIAL** (rama publish); quick 11/11; 4.264 → **4.285** funciones canónicas (+21); 6/6 mutaciones rojas por el guard con restauración por sha256; **contador v4complete 0/1** |
| B | **2026-09-20 (`473ed0f` + `05d0cc6` + `7553f51`)** | **CERRADA CON DEUDA REGISTRADA** — AC1 y AC2 **VERIFICADO OFFLINE**, AC19a-consumo cerrado; la **deuda AC5 (S-B1)** queda con dueño **C-D** como insumo suyo, no como prerrequisito que rehaga B. Commit de producto y push ejecutados con instrucción literal | **Métrica FUERA DE SERVICIO (R2.1)**, auto-reporte con unidad declarada | — | ⟦Fila rectificada el 2026-09-24 por el bloque C de la orden de calidad: publicaba «Nueva sesión / PENDIENTE», que estaba vencido; su evidencia y su cierre están en `06-`, `dependencias-fases.md` y `evidence/…/FASE-B/`⟧ |
| C | Nueva sesión | **PENDIENTE ← punto de reanudación** | Por medir | No | Botón seguro y confianza; **arrastra la deuda AC5 de B** |
| D | Nueva sesión | PENDIENTE | Por medir | No | Veredicto y diagnóstico de bloqueos |
| E | Nueva sesión | PENDIENTE | Por medir | No | Entrega y evidencia interna |
| F | Nueva sesión | PENDIENTE | Por medir | Solo pistas independientes sin secretos | Seguridad de salidas |
| H | **2026-10-06 (HEAD de partida `ec8a272`)** | **COMPLETADA EN CONTRATOS OFFLINE, SIN COMMIT; preflight NO FAVORABLE que bloquea la arista a E2E** — AC14/AC17/AC13/AC9 **VERIFICADOS OFFLINE** con 13/13 mutantes rojos por su guard y restaurados por sha256; AC12 **PARCIAL** (el par con writer/acta reales es de E y se re-ejecuto; H aporta el par permitir/bloquear del spawn) | **Fuera de servicio (R2.1)** con auto-reporte en unidad propia | No | Runner stdlib con hijo falso; onboarding derivado por el transformador real; rama del loader medida dos veces |
| E2E | Nueva sesión | PENDIENTE | Por medir | Sí, si entorno y presupuesto lo permiten | Única corrida y snapshot |
| VERIFY | Nueva sesión | PENDIENTE | Por medir | No | Certificación directa, sin fixes |
| RELEASE | Nueva sesión | PENDIENTE | Por medir | Documentación con allowlist | Cierre y archivado |

## Matriz de verificación de hallazgos

Copiar la matriz completa de ACs del maestro al certificar y llenar una fila por AC, sin agrupar rojos con verdes.

| AC | Hallazgo | Expected | Real | Fuente y clave | Status |
|---|---|---|---|---|---|
| AC1–AC20 | Ver `01-plan-maestro.md` | Contratos del maestro | Sin medición post, salvo AC7/AC15/AC16 | Artefactos de G | PENDIENTE, con tres filas medidas abajo |

| AC7 | Señal requerida omitible sin que nadie lo note | Población descubierta por AST sin lista fija; `wiring_report.json` en el quick | **169 llamadas / 70 gobernadas / 0 receptores sin resolver en producción**; check 11/11 verde y rojo con `--ignore-known` | `.opencode/wiring_report.json`: `poblacion`, `cobertura`, `politica`, `excepciones_aplicadas`, `limites` | **VERIFICADO OFFLINE en G** (rojos: caller nuevo, `**kwargs`, alias, `self`, homónimos, y la divergencia de hoy en TRES invocaciones) |

| AC15 | Par PRE/POST y mutación del símbolo real | Delta explicado; rojo causado por el guard | PRE 1.313/1/2 · POST-A 1.313/1/2 (delta 0) · POST-B 1.331/1/2 (+18); **7/7 mutaciones con rojo por el guard, 0 por syntax/import** | `tests_baseline_pre.txt`, `tests_baseline_post.txt`, `mutation_report.json` | **VERIFICADO OFFLINE en G** |

| AC16 | Contrato muerto `whatsapp_validation` | Firma sin el parámetro, sin verdad paralela, dato upstream intacto | `with_validation(self, validation_summary)` leída por el verificador; 3 callers actualizados; las 8 líneas de `main.py` que construyen el dato, conservadas | `wiring_report.json` → `politica["AssessmentBuilder.with_validation"].firma_real` + `inventario-callers.md` §3 | **VERIFICADO OFFLINE en G** (rojos M5 y M6) |
| AC20 | La evidencia del veredicto viaja completa en las dos ramas (gate fundado, acta con causas, hash del paquete entregado) | `details.critical_issues_count`/`recall_basis` en el recall fundado; `findings` en `reviewer_reports`; `package_evidence` en publish; contrafactual medido sobre el acta archivada | **Productor y acta medidos sobre el artefacto real**: el camino del `1.0` es la rama `return 1.0  # All critical issues were detected` de `_extract_critical_recall` (identificado por símbolo, R2.2), reconstruido con el `AssessmentBuilder` real reproduce `value: 1.0, details: {}` del `gate_report` archivado; el par es `BLOQUEADO` → `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; hacer cero del conteo **sin** recalcular la recomendación sigue `BLOQUEADO` (verificado, no asumido) | `evidence/…/FASE-0/`: `pre_camino_gate.json`, `baseline_vs_contrafactual.json`, `mutation_report.json`, `thresholds.json` | **VERIFICADO OFFLINE en 0** (rojos M1–M4 por el guard; M5/M6 demuestran que los límites prohibidos están vigilados; **la rama E2E sigue sin ejercitar**) |
| AC12 | Decisión, hash y conteo del paquete en **las dos** ramas del acta | `enforcement` + `package_evidence` legibles tanto si publica como si suprime | Rama de supresión: ya estaba (AC-G3) y re-verificada en el acta archivada (sha `4847cc…`, 52 entradas). Rama de publicación: **cubierta offline en 0** sobre la ruta publicada (`suppressed: False`), en las dos salidas de `publish`; MD del acta sin cambio (+0 bytes) y JSON +1.151 bytes medidos | `main._record_published_package_evidence` + `tests/test_fase_0_ac20_evidencia_veredicto.py` | **PARCIAL (0)**: falta el par del flujo real, que aporta E2E |

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

Sin lecciones **post-implementación**: ninguna fase se ha ejecutado. Las once filas siguientes son lecciones de **preparación** (seis primeras, 2026-09-18 y 2026-09-19), de la **intervención del 2026-09-19** sobre el prompt de Gemini/purga (tres siguientes) y de la **re-medición de la revisión 2** (dos últimas: `L-ENT.10` y `L-ENT.11`), sustentadas en mediciones reales de lectura y ejecución —código vivo, evidencia archivada de FASE-P4, el sitio público del hotel y la corrida de la tarea 7—, y se registran aquí para que VERIFY las contraste contra lo ejecutado, no para darlas por certificadas.

Al cierre de cada fase registrar **las observaciones sustentadas que hayan existido**: **qué pasó / por qué / qué lo previene**, con pertinencia INCLUIR o EXCLUIR. **No hay cuota mínima**: «sin novedades» es un cierre válido y se registra con esa palabra. ⟦**Conciliación final 2026-09-25** — orden de calidad `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.B y su regla «permitir declarar que no hubo lecciones nuevas, sin fabricar una cuota»: esta fila seguía mandando «**al menos tres** observaciones», la cuota que el bloque B ya había retirado de las otras siete rutas del plan (contrato §`sin cuota de lecciones nuevas` y los prompts E, E2E, F, H, VERIFY). Se elimina el número; **no** se baja a otro número. Queda **otra** instancia sin barrer, fuera del permiso de esta sesión: el prompt cerrado `05-prompt-inicio-sesion-fase-G.md`, en su instrucción de Post-ejecución que manda «Actualizar … 00/09/10 con **al menos tres observaciones medidas**», con dueño⟧. **No** inventar una novedad para cubrir una cuota **y tampoco fabricar una confirmación para no quedar en cero**: si se confirma una lección existente, registrar su confirmación **medida** como tal; si no la hubo, decir que no la hubo.

| ID | Lección (qué pasó / por qué / qué lo previene) | Evidencia medida | Prevención asignada | Pertinencia |
|---|---|---|---|---|
| L-ENT.1 | **Un estado agregado archivado se hereda como si fuera causa.** Un snapshot de FASE-P4 registró `confidence 0.3, site_verified false` en los cinco probes; el plan heredó la lectura "el sitio era inalcanzable, la señal es falsa por honestidad". Re-medido hoy: el dominio del warehouse **no resuelve** y el sitio real responde 200 con el canal servido por un plugin. / Por qué: el artefacto guarda un resultado, no el modo de fallo, así que DNS vacío, respuesta sin cuerpo, HTML sin marcaje y excepción tragada comparten el mismo valor. / Qué lo previene: publicar alcance de observación y estado de lectura separados, nunca un único agregado. **Rectificación de la revisión 2:** el patrón se mantiene y se aplica a esta propia fila. El snapshot de P4 no registraba "el lector no vio el botón": registraba `verification_failed` en los **cinco** assets porque falló el *schema report* (la rama de `SitePresenceChecker._check_asset_presence` que lo consulta). La lectura de la home viva con el código del repo devuelve `found=True` por clase CSS. Un estado agregado me pasó factura dos veces: primero el de P4, después el mío propio | `evidence/FASE-P4/.../site_presence_snapshot.json` + `output/TAREA7-2026-09-19/.../site_presence_snapshot.json` + sonda HTTP y M1 del 2026-09-19 | AC19a y AC9 | INCLUIR, **rectificada** |
| L-ENT.2 | **La pregunta no es "¿existe el canal?" sino "¿puede el lector observarlo, en qué ruta y en qué marcaje?".** La home del sitio vivo tiene 0 referencias a WhatsApp y `/contacto/` tiene 54, todas dentro de `<style>` o de `href`/`src` del plugin; ningún `wa.me` ni número en HTML estático y el método de detección devuelve `found: False` ante cualquier excepción. / Por qué: F-F y F-A' gobiernan promesas y cableado, pero el falso positivo nace aguas arriba, en la cobertura del detector; corregir el dato no cambia lo que el lector no mira. / Qué lo previene: gobernar el lector como parte del fix, y prohibir que una señal negativa sin alcance verificado se redacte como ausencia. **Rectificación de la revisión 2 — el signo estaba invertido:** la pregunta correcta resultó ser "¿qué está viendo el lector cuando dice `exists`?". Medido con el checker real sobre la raíz viva: `found=True` por la sonda de clases CSS (`joinchat joinchat--left joinchat--btn`), no por texto visible ni `wa.me`. El riesgo no era fabricar una ausencia, era **certificar una presencia como si fuera un número** (`exists/0.85` → boost a 0.95 sobre un campo que no es teléfono). La lección sobrevive; la dirección del peligro no | M1 y M2 de `00-lecciones-capitalizadas.md` §1bis (checker ejecutado + snapshot archivado de la corrida del 2026-09-19) | AC19a (lector en C, consumo en B); matriz §2 fila "solo HTML/presencia, centinela" | INCLUIR, **rectificada** |
| L-ENT.3 | **Un default de código se fosiliza como dato verificado cuando viaja por un fixture.** El fixture versionado del hotel fija canal directo 20.0 contra los 30.0 del warehouse, con `epistemic_status: verified, confidence: 0.95`; el 20.0 es el respaldo de un `datos.get(...)` del propio test e2e y el encabezado del fixture afirmaba "no introduce datos nuevos" tras enumerar solo tres campos comprobados. / Por qué: el metadato de confianza se copió del contenedor y no del productor del valor; un comentario humano no es un verificador. / Qué lo previene: procedencia por campo con su productor declarado, y la regla de no citar un default como verificado. | Comparación fixture ↔ `data/hotel_observations/observations.json` ↔ literal del test e2e | AC14; deuda §6 "Procedencia del dato Don Alfonso" | INCLUIR |
| L-ENT.4 | **Un rojo del working tree caduca: se hereda como prerrequisito y al re-medirlo ya no existe — y mi explicación del mecanismo también cayó.** El quick PRE del 2026-09-18 daba 9/10 por Version Sync y se registró en tres documentos como "A necesita autorización central". Hoy el quick da **10/10** sin que yo tocara nada: `AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md` y `REGISTRY.md` estaban modificados al abrir la sesión y ahora son idénticos a HEAD (mtime 11:06-11:10, revertidos fuera de esta sesión). Además, mi causa propuesta —"el check espera cuatro segmentos"— quedó **refutada** al leer `_check_version_sync` completa: solo ejecuta `sync_versions.py --check`, la misma herramienta que yo había visto pasar. / Por qué: heredé un estado transitorio del árbol y después inferí un mecanismo leyendo un fragmento del verificador; las dos cosas son atajos sobre mediciones incompletas. / Qué lo previene: re-medir los rojos al abrir cada fase y no convertirlos en prerrequisito de otra sesión; y antes de publicar una causa, leer el check completo, no la ventana que coincidía con mi hipótesis. | `git status` inicial frente al de hoy, mtimes de los 4 documentos, quick 10/19 10/10 y lectura de `scripts/run_all_validations.py::_check_version_sync` | §1, §6 y §7 del maestro corregidos; A ya no requiere autorización central | INCLUIR |
| L-ENT.5 | **Editar una tabla anclando en otra fila completa la reemplaza.** Al insertar AC19 en la matriz del checklist, el ancla fue la fila AC18 y el resultado quedó sin AC18. / Por qué: la coincidencia de texto no valida la estructura del documento; la pérdida era invisible sin contar. / Qué lo previene: conteo de miembros antes y después de editar, y comprobación de persistencia sobre el commit y no sobre el buffer. Detectado en la misma sesión y remediado. | Registro del error y su reparación en la sesión del 2026-09-19; matriz re-verificada con 20 filas AC (AC1–AC20) en maestro y checklist —19 cuando se registró esta fila, antes de nacer AC20 | Proceso de edición, no producto | INCLUIR como límite de proceso |
| L-ENT.6 | **El consentimiento liga una identidad concreta, no un nombre comercial.** La autorización de FASE-P4 amparaba una corrida de diagnóstico sobre la URL del warehouse —hoy inexistente— y declaraba explícitamente que no era entrega a cliente; la corrida propuesta se lanzaría sobre un dominio distinto. / Por qué: el documento describe su objeto con la URL, y ese objeto ya no existe, de modo que la vigencia nominal del consentimiento no cubre el destino nuevo. / Qué lo previene: reemitir el consentimiento datado sobre la URL viva con su límite escrito, y verificar identidad única y hash de la fuente antes de consumir el único intento. | `evidence/FASE-P4/consentimiento-donalfonso.md` frente a la sonda DNS/HTTP del 2026-09-19 | AC14/AC17 (preflight de H); deuda §6 de procedencia | INCLUIR |
| L-ENT.7 | **Todo estado heredado caduca, incluido el que el prompt de apertura afirma como hecho — segunda confirmación medida del patrón de L-ENT.4, ya no solo de rojos.** El prompt de la intervención del 2026-09-19 daba por ciertos tres estados y los tres habían cambiado: los "3 commits SIN push" ya estaban pusheados (divergencia real 0/0), el árbol "sucio en `.opencode` por trabajo ajeno" estaba limpio (commits ajenos ya ingresados), y la revocación que mandaba pedir al operador "no su valor" ya estaba confirmada por este el día anterior. / Por qué: un prompt registra mediciones en el momento de redacción y se ejecuta después; el agente que no re-mide hereda comandos sobre hechos difuntos. / Qué lo previene: el primer bloque de toda sesión debe re-medir las premisas (git, registros externos, acreditaciones) antes de ejecutar la primera tarea; aquí la orden expresa "verifica antes de fiarte" salvó la sesión — la re-medición costó tres comandos. | `git rev-list --count origin/master..master` = 0, `git status --short` vacío, confirmación de rotación del operador 2026-09-18 | Apertura de A y de cada fase; FASE-A ya la aplica en su propia Tarea 3 reescrita | INCLUIR |
| L-ENT.8 | **Un hit de escáner es una forma, no una credencial: la naturaleza medida rebajó el nivel de contención de force-push a redacción de 8 líneas.** La key marcada para purga de historial (reescribiría todos los SHA y 7 tags, con blast radius máximo sobre master compartido) resultó ser el key estático firmado que Google incrusta en su propio HTML de Maps, capturado por scraping: sin coincidencia con ninguna key viva del `.env`, no funcional como credencial del operador. El cierre proporcional fue redacción en HEAD + riesgo residual documentado + condición de escalada explícita. / Por qué: los patrones detectan sintaxis; ownership, vigencia y explotabilidad son mediciones aparte que el plan de escalación heredó sin repetir. / Qué lo previene: antes de elegir nivel de contención, medir procedencia (quién escribió, coincide con viva, firmada, inerte) y documentar la condición por la cual sí escalaría. | Contexto `html_sample_end` en `archives/gbp_profiles.json`, contraste con claves del `.env` (0 coincidencias), cierre `a107f3c` con nota en AC-S3-S4 | F (seguridad de salidas): clasificar por naturaleza antes de costear contención | INCLUIR |
| L-ENT.9 | **Un proveedor configurado no es un proveedor ejercitado: la métrica agregada verde oculta qué rama corrió.** La corrida e2e salió verde (`source=llm_check`, 5/5 consultas medidas) con Gemini vigente en el `.env`, pero cero consultas lo alcanzaron: OpenRouter es prioridad 1 y el bucle rompe al primer proveedor que responde. Solo `providers_used` delató la rama no ejercitada, y hubo que verificar Gemini con una llamada directa (`gemini-flash-latest`, 864 tokens, coste $0.0021 derivado). / Por qué: la métrica agrega "hubo medición", no "con quién"; en un diseño de corrida única como este plan, la rama silenciada no tiene segunda oportunidad de manifestarse. / Qué lo previene: exigir evidencia por rama ejercitada (quién respondió cada unidad) en la certificación E2E/VERIFY, igual que se exige por AC; un verde agregado no convierte en SUPERADO EN E2E una ruta NO EJERCITADA. | `evidence/tarea7-corrida.log` línea 129 (`Providers: openrouter`), prueba directa `_query_gemini` del 2026-09-19 | E2E/VERIFY: matriz por rama de proveedor, no solo por AC | INCLUIR |
| L-ENT.10 | **Se re-midió el símbolo y no la ruta viva; el plan quedó bien construido sobre un caso que ya no ocurre.** La preparación verificó cada símbolo del contexto de 2026-09-17 contra el código (y acertó: F-A es no-op, F-A' sí decide, el centinela viaja como teléfono). Pero nunca ejecutó la cadena completa sobre la URL alcanzable, y ahí el cuadro cambia de signo: sin pain de WhatsApp, sin botón en el plan, `whatsapp_verified` en verde vacuo y los 13 gates pasando. / Por qué: un símbolo leído dice qué haría el código, no qué hizo la corrida; y el defecto que se buscaba era el del contexto viejo, no el del camino nuevo. / Qué lo previene: antes de cerrar un diseño, ejecutar el lector o el verificador afectado sobre la entrada real del objetivo —aquí costó dos comandos— y tratar toda premisa "el producto hoy hace X" como refutable por un artefacto ya archivado | M1-M4 de `00-lecciones-capitalizadas.md` §1bis frente a maestro §1 | Maestro §1, §2 y §4 re-anclados; AC19 dividido | INCLUIR |
| L-ENT.11 | **La consulta de lecciones se hizo por el síntoma y devolvió solo el síntoma; la causa del fracaso estaba en el índice desde once días antes.** `L-E2E.2` y `L-V.3` (2026-09-11) documentan el `critical_recall.details: {}` real y el CRITICAL que produce; `evidence/FASE-I/comparacion-vs-baseline.md` midió el delta de serialización en su sección «2. NRs verificados». Cerraron como "fix candidato fuera de este plan", sin dueño ni AC, y once días después eran la única causa de supresión de la corrida que este plan quería certificar. / Por qué: la recuperación por palabras del síntoma ("WhatsApp", "promesa") no alcanza la superficie donde vive la causa (acta, veredicto, cuarentena); y un hallazgo sin dueño ni AC no se cierra, se reencuentra. / Qué lo previene: capitalizar por **dos ejes** —síntoma y superficie de cierre— y prohibir la frase "fix candidato" sin fila con dueño y AC. Ahora FASE-0/AC20 | Q7-Q10 y las filas nuevas de `00-lecciones-capitalizadas.md` §1-§2 | FASE-0, AC20, deuda §6 "serialización de evidencia del veredicto" | INCLUIR |

| L-ENT.12 | **El verde del verificador no probaba su propia cobertura: el hueco estaba en su resolutor de tipos, y lo delató una cuenta que el verificador exige de sí mismo.** La primera versión escaneaba solo sentencias directas del cuerpo de una función, así que un `pain_mapper = PainSolutionMapper()` dentro de un `try` —el caller productivo de `_identify_brechas`— quedó `RECEPTOR_NO_RESUELTO`: el check estaba **verde** mientras gobernaba a menos. Reconstruido ese «antes» en memoria: **8 receptores productivos sin resolver**; tras descender por `try`/`if`/`with`, **0**, con gobernadas 67 → 70. / Por qué: un verificador de población describe lo que encontró, no lo que buscó; la ausencia de hallazgos y la ausencia de mirada se escriben igual en un JSON sin denominador. / Qué lo previene: que todo verificador de población publique **y aserte** su propio denominador (`cobertura.receptores_no_resueltos_en_produccion == 0`), como test y no como línea de reporte | `evidence/…/FASE-G/resultados-y-observaciones.md` obs. 3 (medición comparativa sin mutar el árbol) | Proceso de todo verificador posterior del plan (F gobernará `output/` y `logs/`; E, el resolvedor de artefactos) | INCLUIR |

| L-ENT.13 | **Un registro de excepciones sin regla de caducidad es un allowlist con mejor prosa.** AC7 exige «excepciones tipadas y justificadas», y G las necesitaba: tres hallazgos reales siguen abiertos con dueño en FASE-B, y un check rojo desde hoy no protege las ediciones de nadie. El peligro no era tenerlas, era **quedárselas**. Lo que las vuelve honestas son dos piezas medidas: una excepción que ya no ampara ningún hallazgo produce ella misma una violación (`EXCEPCION_VAGA`, mutación M4), y `--ignore-known` deja ver el total sin excepciones (4 violaciones en el árbol de hoy). / Por qué: el allowlist no nace de una decisión torpe, nace de una excepción razonable que sobrevive a su causa — el mismo mecanismo con el que `L-ENT.4` hizo caducar estados heredados. / Qué lo previene: apareamiento biunívoco (sobrantes en cualquiera de los dos lados = rojo) y una bandera que exhibe el total | `aplicar_excepciones()` en `scripts/validate_wiring.py`, `test_excepcion_que_ya_no_ampa_nada_es_en_si_una_violacion`, `mutation_report.json` M4 | FASE-B (retirar las tres al corregir, o registrar las que no corrija) y todo verificador con excepciones | INCLUIR |

| L-ENT.14 | **Una prueba de NO-existencia recortada por un `head` no prueba nada: afirmó en cuatro documentos commiteados que el verificador de write-back no existía.** Esta sesión midió `grep -rln "validate_qmind_writeback" . \| head -20`, el corte se comió el único archivo que la refutaba porque `scripts/` ordena después de `.agents/` y `.opencode/`, y la conclusión («saltárselo es silencioso», «no está en `run_all_validations.py`») entró al prompt de RELEASE, a 09, a 10, a dependencias y al registro de evidencia. Y el corpus ya la desmentía por otro eje: `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`, en su checklist de cierre de FASE-RELEASE, documenta el 2026-09-11 que el script «no tiene vía de actualización» y que `is_ingested` corta por título ⇒ `SKIP`. / Por qué: un corte de salida protege el contexto pero se lee idéntico a una ausencia, y una proposición universal negativa exige el conteo completo, no el primer pantallazo. / Qué lo previene: dos reglas — (1) en toda afirmación de ausencia, correr la búsqueda **sin corte** y publicar el conteo total junto al listado; (2) antes de escribir «no existe verificador», buscar el verificador por el artefacto que gobernaría, no por la cadena exacta que uno espera. | `run_all_validations.py` — método `run()`, rama `if not self.quick:`, y `_check_qmind_writeback()`, que lo lanza sin `--strict`; `grep -rln "validate_qmind_writeback" scripts/` → 2 archivos; retractación aplicada el 2026-09-20 en los cinco documentos citados | Proceso de medición propio; nace el mini-plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` | INCLUIR |
| L-ENT.15 | **Para medir el estado anterior no se usa `git stash` sobre trabajo sin commitear: existían `git grep <rev>` y `git archive`.** La sesión midió el conteo canónico de HEAD con `git stash push --include-untracked` y eso ponía el trabajo de la fase —cinco archivos modificados, sin commit— a merced de un pop fallido o de un hook. Se revirtió en la misma sesión con `git stash pop` y verificación símbolo a símbolo, y la medición se rehízo sin tocar el árbol: `git grep -h -E "^[[:space:]]*def test_" HEAD -- tests` (4.264) y `git archive HEAD` extraído en un temporal para ejecutar la suite nueva contra el código sin el fix. / Por qué: el `stash` es una operación sobre el estado del usuario, no una lectura; la pregunta «¿qué decía HEAD?» nunca necesitó modificarlo. / Qué lo previene: regla de instrumento — medir revisiones con comandos de revisión (`git grep <rev>`, `git show`, `git archive`), y reservar las destructivas para cuando exista instrucción expresa | Registro de la propia sesión y `tests_baseline_pre.txt` (bloque PRE-c); restauración verificada con `git status --porcelain` y los símbolos de la fase presentes | Proceso de medición propia; la fase ya usó copia temporal (`tempfile`) para las mutaciones | INCLUIR |
| **Confirmación medida, sin ID nuevo:** `L-ENT.15` se volvió a cumplir en la decisión A4, con un **tercer instrumento** de la misma familia: el PRE de la selección extendida se midió sobre `473ed0f` en `git worktree add --detach .a4-pre HEAD` (620 casos, 1 failed) mientras el árbol de trabajo conservaba el fix sin commitear; el worktree y su registro se eliminaron después (`git worktree remove`, `git worktree prune`) y `git status --porcelain` quedó con un solo archivo modificado. Ni `stash`, ni copia manual: la pregunta «¿qué marcaba HEAD?» se respondió con comandos de revisión. Sirve además como contrafactual del test re-anclado — con el dolor antiguo el `assert len(blocking) == 3` falla, así que el test no es decorativo | `git worktree list` tras la limpieza (solo el principal); `A4-decision.md` §Contrafactuales | Proceso de medición propia (instrumento: `git worktree --detach` sobre HEAD) | INCLUIR |
| **Confirmación medida, sin ID nuevo:** `L-V.3` («toda premisa que dependa de que el código hoy hace X cae contra el artefacto real») se cumplió sobre una fila del propio plan: F-A' del maestro §1 describe **una** invocación divergente (`generate_assets` → `detect_pains`) donde el AST midió **tres** (286, 309 y 447, dos sobre `CoherenceValidator.validate`). No se define fila nueva porque la convención ya existe y repetirla no cambia ninguna tarea; lo que cambia es el alcance de FASE-B, registrado en `inventario-callers.md` §1.2 |
| **Confirmación medida, sin ID nuevo:** `L-V2.3` («antes de cambiar un artefacto, ve a los tests que asertan sobre ese artefacto; si pinan una numeración o una forma, átalos a coherencia interna y no al literal») se cumplió por segunda vez dentro del plan, esta vez **dentro de la propia fase**: `test_reviewer_reports_refleja_los_cuatro_revisores` asertaba `set(entry) == {6 claves}` y cualquier clave nueva del acta la habría puesto rojo por forma, no por contrato. Se re-ató a superconjunto de las seis heredadas + subconjunto declarado + coherencia interna (`len(findings) <= findings_count`). No nace fila propia porque la convención ya existe y repetirla no cambia ninguna tarea |



Reservar IDs propios —la serie `L-ENT.1` a `L-ENT.13`, verificada como libre— solo después de comprobar que no existan en el corpus: la búsqueda del 2026-09-19 en el índice devolvió cero coincidencias para ese prefijo, y la de FASE-G (2026-09-20) devolvió **cero** coincidencias para `L-ENT.12` y `L-ENT.13` sobre un índice de 316 IDs que entonces definía `L-ENT.1`…`L-ENT.11`, que entonces definía 305 IDs; la segunda pasada, tras la intervención del mismo día, verificó libres los tres tokens nuevos sobre un índice de 311; la tercera pasada (revisión 2) verificó `L-ENT.10` y `L-ENT.11` sin coincidencias en el repo (solo `L-ENT.1`…`L-ENT.9` definidos) y los añadió sobre un índice de 314.

**Efecto medido de registrarlas.** Las seis filas pasaron a contar como definiciones: el índice pasó de 305 a 311 IDs. Una redacción anterior que nombraba el patrón completo en prosa fabricó además una cita huérfana y elevó «citados sin definición» de 43 a 44; al reescribir la frase sin ese token, la métrica volvió a 43. Esto **no** se capitaliza como lección nueva del plan —la convención ya la declara el encabezado del propio generador— y queda aquí solo su confirmación medida: un enunciado en prosa es un ID a efectos del índice, así que un patrón se escribe con sus miembros concretos o en lenguaje llano. Las tres filas de la intervención del 2026-09-19 (verificadas al regenerar el índice) lo llevaron de 311 a 314 IDs sin crear ninguna cita huérfana: «citados sin definición» permaneció en 43.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Seguimientos abiertos

| Tema | Estado | Dueño | Acción / condición de cierre |
|---|---|---|---|
| F-P4.3 / HALLAZGO-N4 / BUG-6 | Retomado, no duplicado | Orquestación + generación; onboarding conserva D1 | Cerrar bloqueo por promesa imposible, no afirmar que D1 queda implementado |
| F-B / contacto warehouse | DIFERIDO, no autorizado | Producto + privacidad + onboarding | Decisión escrita de campos comerciales permitidos, fuente y consentimiento antes de ampliar esquema/formulario/adaptador |
| F-E / no evaluable | DIFERIDO | Coherencia | Contrato serializado y tests vacío/ausente/error, sin bajar protección del botón |
| F-D' / parámetro descartado | **CERRADO POR FASE-G (2026-09-20)**: `AssessmentBuilder.with_validation` quedó en `(self, validation_summary)` y se retiró de sus 3 callers; el verificador lo declara `prohibido`, así que re-introducirlo en firma o caller hace rojo (M5/M6). El dato upstream de `main.py` sigue consumido por sus 8 líneas originales | AssessmentBuilder + `validate_wiring.py` | Cerrado; la no-regresión la sostiene el check 11 del quick, no un test suelto |

| **Nueva (FASE-G): tres invocaciones sin `whatsapp_html_detected` en `v4_asset_orchestrator.py`** | **CERRADO POR FASE-B del propio plan, y barrido como seguimiento vencido el 2026-09-25 por la conciliación final de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` — el cierre NO es de esta sesión ni suyo: lo produjo FASE-B con `473ed0f`/su checklist.** La señal se deriva **una vez** en `generate_assets` (`modules/asset_generation/v4_asset_orchestrator.py`, hoy ~292-295) y se propaga a `PainSolutionMapper.detect_pains` (~303) y a las **dos** pasadas de `CoherenceValidator.validate` (~329 y ~468, ambas anotadas `# FASE-B (AC1)`); las tres excepciones tipadas que amparaban las omisiones fueron **retiradas** de `scripts/validate_wiring.py`. Re-medido el 2026-09-25 con el verificador de la propia fila: `./venv/Scripts/python.exe scripts/validate_wiring.py --ignore-known` → **183 llamadas descubiertas · gobernadas 75 (conformes 21, omisiones 0) · amparadas por excepción 0 · violaciones 0 · `exit 0`**. Las líneas que esta fila citaba (286/309/447) son **anclas muertas**: el código se movió; las de arriba son las corrientes. Evidencia del cierre: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/resultados-y-observaciones.md` §1 filas 1-2 | **FASE-B** / AC1 — **cerrado** | Nada pendiente. Si vuelve una omisión, el verificador la imprime: ya no hay excepción tipada que la tape, así que el rojo es por causa y no por ausencia de guard |

| **Nueva (FASE-G): el guard llega al quick, no al hook** | Registrado como límite, no como logro: `Wiring` corre en `run_all_validations.py --quick` (check 11) y **no** en `scripts/git_hooks/pre-commit`, que además no invoca `run_all_validations.py` (`L-V3.1`, traído por QMind Q12). Tocar hooks está prohibido en fases intermedias | Operador / RELEASE | Si se quiere en cada commit hace falta instrucción expresa para editar el hook y su contract test de numeración. Mientras tanto el guard corre al validar, no al commitear |

| **Nueva (FASE-G): rojo preexistente del verificador de capitalización** | `test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-…]` en rojo **desde `9c4a001`** (RELEASE v4.77.0 archivó `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` y `clasificar_planes` solo recorre hijos directos de `.opencode/plans/`). G lo midió, lo atribuyó y lo dejó estar: no es de su alcance y no lo excluyó | Dueño: `validate_lesson_capitalization.py` (serie PASO0-VERIFICADOR) | Dos salidas no decididas aquí: que `clasificar_planes` también recorra `Archives/` para planes posteriores al corte, o re-anclear el test a un predecesor no archivado. Requiere sesión y alcance propios ⟦— **y la sesión y el alcance llegaron el 2026-09-27, con la primera de las dos salidas decididas**: se levantó el salto de `Archives/` para que sus hijos pasen por el mismo cutoff que los de raíz (decisión **(a-prima)** de S29, con su coste corrido y la salida (b) descartada en la fila §S29 de `…/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md`, fuente única). El test quedó verde **sin tocar su aserción**, que era la condición de la (a): re-ancalarlo habría sido la otra salida y no se hizo. Lo que G midió sigue siendo el diagnóstico vigente: `9c4a001` archivó el plan y el repartidor solo miraba hijos directos⟧ |

| **Nueva (FASE-G): los dos escritores de `REGISTRY.md` divergen** | **RESUELTO POR EL BLOQUE B DE LA ORDEN DE CALIDAD, y barrido como seguimiento vencido el 2026-09-25 por su conciliación final — la cura no es de esta sesión ni de FASE-G: la produjo el bloque B (`sync_config.yaml` + sus tests) y la orden la acepta en §6 casilla 3 con su matriz en §13 de la fuente única de B.** Antecedente tal como se midió en G (y **así ya no es**): `log_phase_completion.py` estampaba la fecha del día mientras `sync_versions.py`, con la regla `registry_last_update`, comparaba esa cabecera contra `VERSION.yaml` → quick rojo al día siguiente de loguear una fase. Hoy **no hay dos escritores**: `scripts/sync_config.yaml` lleva la sección explícita «**REGISTRY.md — SIN REGLA DE FECHA (a proposito)**» y su único escritor es `scripts/log_phase_completion.py`, que estampa la fecha de la **última entrada documental** (distinta de la fecha de release, que viaja por CHANGELOG/README). **La acción que esta fila ordenaba quedó imposible por diseño**: `sync_versions.py --rule registry_last_update` ya no tiene objeto —`tests/test_registry_fecha_documental.py` aserta que ninguna regla apunte a `REGISTRY.md` y que el id `registry_last_update` **no** esté en el config. Cabecera vigente en disco al medir: `> **Ultima actualizacion:** 2026-09-24` | ~~**FASE-RELEASE / operador**~~ → **cerrado por el bloque B de la orden** | Nada pendiente **de este plan**. Cada fase intermedia **ya no** re-abre ese rojo: el conflicto que G describía desapareció al retirarse la regla, no al reconciliarse dos fechas. Si algún día reaparece, el guard lo imprime ese test, no una lectura manual |
| **Nueva (FASE-G): deuda de política del verificador** | `CoherenceValidator.validate` también defaultea `site_presence_report=None`, y G **no** la exigió: gobernarla habría añadido un requisito que ninguna AC aprobó y dos hallazgos sin dueño | FASE-C / V-1 (maestro §2) | Al tocar el boost de presencia, decidir si entra en la política; si entra, con su AC y sus excepciones |
| **Nueva (FASE-G): `validate_qmind_writeback.py` no puede publicar un cierre actualizado** | El writer fija el título `10-analisis: <PLAN> (lecciones aprendidas y decisiones)` y **no expone `--title` ni `--file`** (medido en su `main()` el 2026-09-20). Como `is_ingested()` responde por título, la segunda ingesta del mismo plan devuelve **SKIP**: la misma idempotencia que evita duplicados deja la primera versión como verdad publicada y el contenido nuevo, obsoleto **sin señal**. Agrava: el check [17/18] de la validación completa sí lo invoca, pero solo en modo completo (ni en `--quick` ni en un hook), escanea solo `Archives/`, degrada a exit 0 sin CLI y decide por título ⟦re-anclado el 2026-10-06: la fila se escribió con la etiqueta `[15/15]`, la que le correspondía cuando el modo completo llegaba a 15; el denominador hoy es 18 porque nació el hermano `[18/18]` de frescura `CONTEXT` (`verify_qmind_context_freshness.py`), que tampoco corre en `--quick`⟧ | ABIERTO CON DUEÑO Y PLAN PROPIO | Mini-plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, creado el 2026-09-20 para ejecutarlo **antes** de FASE-RELEASE; operador si se decide no ejecutarlo | Ampliar el writer con `--title` y un saneador, y verificar por **descarga + sha256** en lugar de por título. Mientras no exista, la ingesta final se hace con `qmind source upload` directo y así debe decirse en el prompt de RELEASE (así lo hizo G: copia saneada + título canónico, `evidence/…/FASE-G/qmind-writeback-G.md`) |
| **Nueva (FASE-0): DEUDA-0.1 aliasing del assessment con el objeto del auditor** | `AssessmentBuilder.with_audit` asigna la **misma lista** de `audit_result.critical_issues` y `with_geo_flow` hace `.append` sobre ella: el geo-flow muta el objeto del auditor. Medido como O2 en `evidence/…/FASE-0/resultados-y-observaciones.md` (apareció porque el propio delta de la medición salía 0) | **FASE-E** (dueño del adaptador y de las rutas de artefactos) | Copia defensiva en el adaptador + assertions de identidad (`assessment["critical_issues"] is not audit_result.critical_issues`) y re-lectura del audit tras `with_geo_flow`. **No es un AC**: FASE-0 no lo gobierna porque es cambio de adaptación, no de serialización de evidencia, y abrir un AC en una fase ajena era reinterpretar el alcance |
| DomainGate de WhatsApp (`CommercialGate._check_whatsapp_verified`, `DomainGatesOrchestrator`, `quick_check_commercial`) | Fuera de la ruta del fix. **Corrección de nombre:** la fila anterior citaba `DomainGateEngine`, símbolo que **no existe** en el repo — nadie podía localizar la deuda | Quality gates | Conservar documentado como legado mientras existan tests; su severidad de fallo es `warning`, nunca `error`, así que no puede usarse como certificación de producción. No archivarlo sin autorización |
| **Nueva (revisión 2): serialización de evidencia del veredicto (`VACUOUS_RECALL`)** | **CERRADA POR FASE-0 el 2026-09-20 (offline, con su par medido)** y en cumplimiento de lo que `L-E2E.2`/`L-V.3` dejaron como "fix candidato sin fila". Los tres puntos están en el productor, en el DTO del acta y en las dos ramas de publish. **Reapertura honesta:** la supresión deja de estar causada por este hueco, pero eso no certifica que una corrida real publique — lo demuestra E2E | Quality gates/tribunal; FASE-0 cerró; **E2E/VERIFY** contrastan en flujo real | Cerrado con AC20 y su contrafactual; la no-regresión la sostienen M1–M4 del `mutation_report.json` y las 21 pruebas de `test_fase_0_ac20_evidencia_veredicto.py` |
| F-P4.1 | Recalificar contra HEAD | Delivery | Distinguir corrección P6/P6-R de contenido histórico; fortalecer tests donde falte evidencia |
| F-P4.2 | En alcance | Orquestación + revisores | Preservar lectura de artefactos internos sin entregar bloqueados ni contar ausencias causadas por el propio borrado |
| F-P4.5 | **CERRADO POR ACREDITACIÓN DEL OPERADOR (registrado 2026-09-19)**: rotación de la key Gemini-local (AIzaSyDq…) confirmada por el operador el 2026-09-18, con ocasión de la intervención previa; registro en `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md`. La key de `archives/gbp_profiles.json` no aplica a este cierre: es el key estático firmado de Google en HTML scrapeado, resuelto como higiene de HEAD (a107f3c) con riesgo residual documentado | Operador de credenciales + providers | A/F referencian el registro, no la vuelven a pedir; la prevención activa ya la validan los tests de redacción (48a242b). Acreditación = afirmación del operador, no inferible del repo |
| Version Sync del quick PRE | **CERRADO POR MEDICIÓN 2026-09-19**: el quick pasa 10/10. El rojo del 2026-09-18 venía de cuatro documentos sucios en el árbol (`AGENTS.md`, `VERSION.yaml`, `docs/GUIA_TECNICA.md`, `REGISTRY.md`), hoy idénticos a HEAD tras una reversión externa a esta sesión. La explicación "desacuerdo verificador↔escritor" se retracta: `_check_version_sync` solo invoca `sync_versions.py --check` | Operador | Nada que autorizar en A. Verificar de nuevo el quick al abrir cada fase; si reaparece, leer el check completo antes de atribuirle una causa |
| **Nueva (post-cierre de A, 2026-09-19): fuente pública de precios señalada por el operador** | Registrada en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-A/fuente-publica-precios-2026-09-19.md`. **Corrobora dos de los cuatro campos** del dato operativo con una fuente datada sobre la URL viva: `rooms` (11 productos de alojamiento, cero divergencia) y el punto de precio (330.000 es moda y mediana de una lista que corre de 249.900 a 395.000). **No** toca `monthly_reservations` ni `direct_channel_percentage`, y no sustituye el consentimiento | Datos/procedencia + **H** | H cita la fuente en `onboarding_provenance.json` como respaldo con URL, fecha y método, declarando que **no** generó ningún valor nuevo. No se convierte en "precio gobernante" sin productor declarado: tarifa de lista ≠ `adr_cop` ≠ `avg_reservation_cop`, y manda la regla "No Defaults in Money". El warehouse no se editó ni se edita por esta fila |
| Procedencia del dato del hotel (L-ENT.3, L-ENT.6) | **SIGUE PENDIENTE DE OPERADOR, y A lo re-confirma como requerimiento (2026-09-19).** A seleccionó exactamente el registro (`hotel_name == "Hotel Don Alfonso"` da 1 de 6), conservó `collected_at: 2026-07-22` y mido que `ONBOARDING_FRESHNESS_HOURS` no existe en `.env`, en la template ni en el entorno. **A decidió que hace falta reconfirmación** porque el consentimiento P4 ampara una corrida de observación sobre la URL hoy inexistente y declara que no es entrega a cliente | Datos/procedencia + operador | Valor gobernante declarado con productor; fixture corregido desde ahí y consentimiento re-emitido datado sobre la URL viva antes de consumir el intento. **Añadido por A:** el preflight de H debe gobernar los **dos relojes** — el de consentimiento y el activo de 20 días de `MemoryManager.cleanup_old_sessions(days=20)`, con 3 artefactos de memoria de Don Alfonso ya presentes (`L-PF11`) |
| **Nueva (FASE-A / QMind R5): reconciliador multi-sede no declarado en el plan** | `CrossValidator._reconcile_whatsapp_multisede` (`modules/data_validation/cross_validator.py`, rama "FASE-P1-D (F12)") ya cierra el falso positivo de cruce entre sedes que el corpus remoto documentaba, con suite propia (`tests/data_validation/test_whatsapp_multisede.py`). El plan no lo nombraba en ninguna de sus nueve filas de productores | Generación + validación cruzada; **B y C** | B/C **no** reimplementan ni eluyen ese reconciliador (`L-NC6`); AC6 debe enunciar que el "campo verificado" puede salir de una reconciliación por sede. No abre fase ni AC nuevo: es una dependencia que se cita |
| **Nueva (FASE-A / QMind R6): el acta no viaja en el ZIP de cliente** | `DeliveryPackager._INTERNAL_DOC_PREFIXES = ("acta_revision",)` (`modules/delivery/delivery_packager.py`, constante de clase): el acta queda solo en `v4_audit/`, y DA-P1.4 registra el círculo estricto (los bytes del ZIP nacen en `write()`, el acta se enriquece después) | Entrega + tribunal; **E** | El resolvedor único de AC11 no debe esperar `acta_revision.json` dentro del ZIP; "snapshot interno fuera del árbol exportado" pasa de disciplina a **construcción vigente** y así se redacta en su prompt |
| Una corrida insuficiente por fallo externo | Condicional | Operador | Conservar resultado; nueva corrida requiere ampliar expresamente presupuesto y plan |

## FASE-B (2026-09-20) — métricas y seguimientos, medidos

**Métricas.** Selección literal de 25 archivos: PRE 537 → POST-A 539 (delta +2 = dos
casos nuevos de AC19a dentro de un archivo de la selección) → POST-B 552 con la suite
nueva (12 casos por 11 funciones, una parametrizada en dos). POST-C de la superficie de
matriz/gate tras A1: **83 passed / 0 failed**. Regresión completa: **4 failed / 4.261
passed / 41 skipped / 4 xfailed en 244 s**. Funciones canónicas
`grep -rE "^\s*def test_" tests --include=*.py`: **4.285 → 4.299 (+14)**, y tras la decisión
A4 **4.300 (+1)** (el test de caracterización de la deuda AC5). Quick **11/11**
antes y después. Guard de cableado: 174 llamadas / 614 archivos, gobernadas 75, conformes
**21**, omisiones **0**, violaciones 0, excepciones amparando 0. Mutantes **8/8 (M1–M8)**
rojos por el guard, restauración sha256 8/8. Diff: 22 archivos, **+543 / −218**. R2 **FUERA DE
SERVICIO (R2.1)**: auto-reporte de la sesión sin instrumento, unidad propia, no comparable
con el instrumento; los dígitos intermedios que figuraban aquí eran autocuentos a mitad de
sesión y quedan retirados por no haber medido el instrumento. Contador v4complete **0/1**.

**A4 (2026-09-20), medición propia.** Selección extendida con
`tests/quality_gates/test_publication_gates.py` añadida a la pertinente: PRE sobre `473ed0f`
en `git worktree --detach` (árbol intacto) = **1 failed / 619 passed / 1 skipped** en 46,5 s
(620 casos); POST con el re-anclaje = **0 failed / 621 passed / 1 skipped** en 45,5 s (621
casos). Regresión completa tras A4: `FASE-B/tests_a4_postfull.txt`.

**Seguimientos abiertos con dueño.**
- **S-B1 (A4 / AC5, dueño C-D — DECIDIDO en B el 2026-09-20):** `test_publication_gates.py::test_get_blocking_issues`
  esperaba 3 gates bloqueantes y veía 2, porque `_proposal_asset_alignment_gate` toma el
  "PASS trivial (never-block)" cuando el único servicio comprometido por el ledger es
  condicional (`guia_configuracion_whatsapp`, no contado). A4 se decidió con **O5** en
  `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/A4-decision.md`: el fixture se
  re-ancla a `whatsapp_conflict` (dolor de WhatsApp que sigue prometiendo un servicio
  contado: `actionable_total=1`, `coverage_ratio=0.0`, `BLOCKED`) y se refuerza con
  `assert "proposal_asset_alignment" in blocking_names`; el caso perdido queda
  assertionado en `test_deuda_ac5_ledger_solo_condicional_pasa_trivial`, que **debe ponerse
  rojo cuando C/D gobierne la deuda**. Lo que recibe C/D no es un test roto sino la decisión
  de producto: ¿debe un servicio condicional comprometido bloquear la publicación si su
  entregable no se genera, y con qué denominador? Dueño vinculante **C-D** (maestro §4 AC5;
  filas C y D de la matriz) — el "D-E" del checkpoint y del resumen de §06 era un error de
  registro y quedó corregido.
- **S-B2 (AC6, dueño C):** `main.py` sigue registrando `can_use_in_assets=True` para el
  centinela `detected_via_html` (fuera de la allowlist de B), y `wa_button_gen` conserva
  el número de placeholder `573001234567` con dos `wa.me/` sin guarda en
  `local_content_generator`.
- **S-B3 (AC5, dueño C-D):** los cinco umbrales de WhatsApp quedan inventariados y sin
  gobernar (0.9 coherencia, 0.7 catálogo, **0.3** en `NEW_HOTEL_THRESHOLDS`, 0.5
  conflicto, 0.9 legado).
- **S-B4 (invariante verificada):** `counts_in_alignment=True` para un servicio condicional
  **no** es una alternativa viable: medido, obligaba a entregar la guía en hoteles sin la
  brecha y produjo 15 rojos. Registrar un servicio condicional exige la separación
  resolución/conteo que quedó en `proposal_asset_alignment.py`.

## FASE-C (2026-10-06) — ACs, lo medido y seguimientos

**Estado: COMPLETADA, sin commit** (mandato sin autorización de commit; HEAD de partida `5398a3a`,
contador v4complete 0/1). Cada cifra vive en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-C/` con su
instrumento; aqui se referencia el comando, no se re-transcribe el número.

| AC | Veredicto de C | Instrumento que lo imprime |
|---|---|---|
| AC3 | **VERIFICADO OFFLINE**: boost a 0.95 por mero `exists` retirado; bloqueo con y sin presencia sobre CONFLICT/UNKNOWN/ESTIMATED; VERIFIED válido pasa; umbral 0.9 y `blocking=True` intactos | `tests/asset_generation/test_fase_c_boton_seguro.py` (parametrizado, 6 corridas) + mutante **M4** |
| AC5 | **PARCIAL, dueño C-D**: seis barras leídas del código y ninguna bajada; el rojo de `NEW_HOTEL_THRESHOLDS=0.3` se gobernó anclando el **destino**, no la barra | `build_thresholds.py` → `thresholds.json`; test `test_cada_barra_con_su_valor_y_su_dueno` |
| AC6 | **VERIFICADO OFFLINE**: contrato de forma en el límite de emisión, campo validado exclusivo, `phone_web` fuera de la clave del botón, centinela no-utilizable **con lector**, href leído del HTML escrito por el writer real | batería nueva + mutantes **M1, M2, M3, M5** |
| AC19a | **COMPLETADA en modo aditivo**: tres claves nuevas + `details` conservado; forma exacta intacta cuando no hay observación; `READ_ERROR` nunca es ausencia; claves verificadas releyendo el snapshot del writer | batería nueva + mutantes **M6, M7, M8, M9** |
| AC15 | PRE/POST de la misma selección y entorno, delta explicado por adiciones de C, mutantes con restauración por sha256 | `tests_baseline_pre.txt`, `tests_baseline_post.txt`, `run_mutations.py` → `mutation_report.json` |
| AC19b | **NO INTENTADA** (deuda §6 del maestro, dueño quality gates/delivery/narrativa). No se declara hecha | — |

**Re-anclajes (nueve, cada uno con su justificación escrita dentro del test):**
`test_site_presence_adapter.py::test_whatsapp_exists_boost` (invertido y renombrado),
`test_whatsapp_button.py` (dos), `test_conditional_generator.py::test_generate_with_blocked_returns_error`,
`test_never_block_architecture/test_phase5_integration.py` (cuatro) y
`tests/asset_generation/test_datasource_gap.py::test_validated_data_has_phone_web_key` (reforzada: ahora
afirma que `whatsapp` **no** es `phone_web`). Ninguna aserción se afeitó; NEVER_BLOCK sigue rigiendo los
demás assets y la confianza baja.

**Seguimientos abiertos por C:**

- **S-C1 (dueño catálogo / RELEASE):** `ASSET_CATALOG["whatsapp_button"].fallback = "generate_basic_whatsapp"`
  sigue publicado sin implementador. Ninguna ruta lo ejecuta hoy, pero es una promesa de catálogo sin ruta.
- **S-C2 (dueño VERIFY):** `reason_code`/`rejection`/`destino` viajan en el resultado del generador y por
  `FailedAsset.reason`; si VERIFY exige el `rejection` completo en el JSON final, falta una pata de writer.
- **S-C3 (dueño C-D, es AC5):** gobernar la ruta que planifica el botón con barra 0.3 contra la exigencia 0.9
  de coherencia. C ancló el destino; la divergencia de barras sigue existiendo por diseño.
- **S-C4 (dueño AC19b):** migración de los 8 consumidores al tri-estado (`observation_scope`/`read_status`/
  `presence_evidence_kind` ya se publican; nadie los consume todavía para decidir ausencia/presencia).
- **S-C5 (desviación declarada, dueño maestro §2 AC19):** `presence_evidence_kind` se publicó con **cuatro**
  valores, no tres: la sonda de texto visible ya existía y produce `found=True`; reducirla a `plugin_fingerprint`
  la mal-atribuiría y a `ninguna` la contradiría. El literal del plan no se reescribió: se declara acá.

**R2:** métrica **FUERA DE SERVICIO (R2.1)** — `measure_iterations.py` pide el transcript del cliente y su
acceso se deniega. Auto-reporte con unidad declarada (tool_use hasta el corte «listo para revisión», commit no
autorizado): **≈150 contra un presupuesto de referencia de 60 → exceso medido**. No se estimó cumplimiento. **Lección de
proceso de la fase (orden del derivado):** se editó corpus del plan *después* de regenerar el índice de
lecciones y el triaje pasó a `SueloNoLeible: VENCIDO` con `build_lesson_index.py --check` dando **[OK] fresco**
— el check se corrió antes de las últimas ediciones. Los 18 rojos y 27 errores de dos corridas completas fueron
de ese orden, no del cambio; cure con los writers en el orden canónico (packs → índice → `--check` → refs →
citas → wiring) y verificación: 77 passed en la superficie afectada y regresión final **1 failed / 4.951
passed**, con el único rojo atribuido al plan hermano (su directorio aislado pasa 141/141). Detalle en
`evidence/…/FASE-C/resultados-y-observaciones.md §8`.

## FASE-D (2026-10-06) — ACs, lo medido y seguimientos

**Estado: COMPLETADA y commiteada/empujada en la misma sesión por orden literal del operador** (HEAD de partida `ea37732`,
contador v4complete 0/1). Cada cifra vive en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-D/`
con su instrumento; acá se referencia el comando, no se re-transcribe el número.

| AC | Veredicto de D | Instrumento que lo imprime |
|---|---|---|
| AC4 | **VERIFICADO OFFLINE**: los dos checks en error conservan nombre y mensaje en el JSON del writer real; sin whitelist (provocada con un nombre inexistente); `[]` publicado cuando el reporte está sano y **clave ausente** cuando el assessment legacy no trae reporte | `tests/quality_gates/test_fase_d_veredicto_canonico.py` + `build_evidencia_pre_gate.py` → `gate_report_coherence_ejemplo.json`; mutantes **M2, M3** |
| AC8 | **VERIFICADO OFFLINE**: el pre-gate decide por veredicto canónico, persiste `coherence_pre_gate_<ts>.json` antes de las consecuencias y **no entra a generar** con culpables en error aunque el score sea 0.88; cubierta la entrada directa del orquestador y el log con el número enmascarado | batería nueva (spy de `generate_assets`, verde complementario, None/True/False, score insuficiente, reporte ausente, lista vacía) + mutantes **M1, M4, M5, M6** |
| AC9 | **VERIFICADO OFFLINE para el lector nuevo de D**: `READ_OK` (incluye `checks: []`), `ABSENT` y `READ_ERROR` con causa, sobre el baseline real de la corrida 2026-09-19 con skip visible; la retención deliberada queda registrada en `with_coherence` | `read_coherence_report` + cinco pruebas; vocabulario en `whatsapp_contract` (`READ_ABSENT` nuevo) |
| AC5 | **INTACTO, deuda C-D abierta**: D no movió ninguna barra ni el flag `is_blocking("overall_coherence")`, que sigue **False**; el corte nuevo viene de los culpables de severidad error | `test_umbral_de_coherencia_intacto` (0.80 pasa / 0.79 no) y `test_score_insuficiente_sin_errores_respeta_el_flag_documentado` |
| AC15 | PRE/POST de la misma selección y entorno, delta explicado por las 33 funciones nuevas, mutantes con restauración por sha256 y árbol intacto | `tests_baseline_pre.txt`, `tests_baseline_post.txt`, `run_mutations.py` → `mutation_report.json`, `mutaciones_crudo.txt` |

**Cuatro defectos medidos antes de curar (no uno):** el pre-gate comparaba solo el score en dos
lugares; el reporte del pre-gate no se persistía por ninguna ruta; `with_coherence` recibía ese
reporte y no lo leía; y `v4_asset_orchestrator.py` cortaba la entrada directa con
`not is_coherent and score < 0.5`, que deja pasar el 0.88 con veredicto False. Los cuatro se
gobernaron en el caller y en la boca única de las causas, sin crear una segunda fuente del hecho.

**Símbolos del prompt revalidados:** `PublicationGateEngine` y su `_check_coherence` no existen en
el repo; la gate es `PublicationGatesOrchestrator._coherence_gate`, que ya consumía
`coherence_verdict_passes` desde FASE-F. La unificación pendiente estaba aguas arriba.

**Seguimientos abiertos por D:**

- **S-D1 (dueño piloto JEV, declarado fuera de alcance):**
  `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`
  falló en la corrida completa (`RedProhibida` en vez de `CredencialAusente`) y **pasa aislada**:
  contaminación de entorno entre tests, sin ruta por ningún símbolo que tocó D. No se curó
  (restricción: no corregir hallazgos ajenos).
- **S-D2 (dueño configuración central):** `AGENTS.md §Cobertura por Modulo` sigue con la cifra
  canónica vencida (4.850 publicados contra 4.875 en HEAD y 4.908 en el árbol tras D). Editar
  AGENTS.md pide instrucción literal expresa; se declara, no se toca.
- **S-D3 (dueño DOMAIN_PRIMER):** no se regeneró. Está versionado y el contrato condiciona la
  regeneración a autorización de escritura; checkpoint declarado.
- **S-D4 (dueño AC5, sigue de C):** gobernar la ruta `NEW_HOTEL_THRESHOLDS = 0.3` contra la barra
  0.9 de coherencia. D conservó el régimen no-bloqueante del score bajo sin errores; si se decide
  gobernarla, el flag `blocking` de `overall_coherence` es la palanca y **no** la barra.
- **S-D5 (dueño E/H):** AC9 declara lectores pendientes en su propio alcance (acta del tribunal,
  ZIP y snapshot del loader). Lo que D certificó es su lector; la fila AC9 no se cierra con D.

**R2:** métrica **FUERA DE SERVICIO (R2.1)** — `measure_iterations.py` pide el transcript del
cliente y su acceso se deniega. Auto-reporte con unidad declarada (llamadas de herramienta hasta
el corte **«listo para revisión»**, que es el que el mandato autoriza porque el commit no lo está):
**≈88 contra un presupuesto de referencia de 60 → exceso medido**, consecuencia de re-verificar
símbolos y de cuatro iteraciones de arnés propio (el fixture de `build()` sin `url`, el regex del
repórt de fallidos, el CRLF que introdujo el arnés de mutaciones y el rojo del AST pineado a
literales). No se estimó cumplimiento.

**Orden del derivado (lección de C aplicada en D):** las ediciones de corpus se hicieron **antes**
de correr los writers, y la verificación final se publicó sobre el árbol ya regenerado
(pack → índice → refs → citas → wiring → quick), no sobre un verde previo.


## FASE-E (2026-10-06) — ACs, lo medido y seguimientos

**AC9 VERIFICADO OFFLINE.** El lector nuevo publica READ_OK (con vacio valido), ABSENT, READ_ERROR y
NO_LEIDO siempre con `cause`; un paquete ilegable no devuelve favorable. Sobre baseline real
(`output/TAREA7-2026-09-19/`) con skip visible si falta.

**AC10 VERIFICADO OFFLINE.** `IMPLEMENTATION_ORDER.md` leido del ZIP que escribio `DeliveryPackager.write()`:
tareas con `### N.`, rutas `ASSETS/` que existen como miembros, manifiesto igual al `namelist()` y el asset
nuevo de B (`whatsapp_setup_guide.md`) con su ruta real. Estado de F-P4.1 revalidado con mutacion (M5): la
derivacion por `dest` sigue vigente y **no** es cierto que el writer entregue siempre un stub — pero tampoco
siempre un orden: sin assets planificados el miembro no existe (medido). El rojo extra de F-P4.9 tambien:
despues de `suppress()` el hash y el conteo vuelven None con error declarado.

**AC11 VERIFICADO OFFLINE.** `review_input_manifest.json` con run_id, fuente original, sha256, tamano,
momento, `read_status` y `disposition=retained_by_gate`; Juez y cuatro Bots consumen el resolvedor (AST en
la ruta de produccion); la retencion leida no suma hallazgo; lo nunca generado sigue ABSENT; documento
declarado e inalcanzable es NO_LEIDO, jamas lista vacia. Snapshot y manifiesto fuera del paquete:
comprobado con el writer real y con dos mutantes de guard (M6, M7).

**AC12 VERIFICADO OFFLINE.** Par permitir/bloquear sobre acta real (`ActaWriter` + `publish`/`suppress`):
`enforcement` y `package_evidence` (sha256 + member_count) en las dos ramas. `_compute_verdict` y los
contratos de cuarentena intactos, con prueba de paridad.

**Lecciones aplicadas (efectivas, no declarativas).** L-VUP-5: el writer ya verde se revalido por mutacion y
no se reimplemento. L-V.1: contenido y layout se midieron en el ZIP del writer, no en un MD fabricado.
L-NC10: el orden publicado se cotejo miembro por miembro contra el manifiesto y el `namelist()`. L-PF6:
`NO_LEIDO` existe precisamente porque "no lo alcance" no es "no existe".

**Leccion nueva (L-E-ESC, formulada al medir).** *Un guard de exclusion no se prueba contra la ruta que el
mismo construye.* El primer verde de la no-filtracion cotejaba el nombre del archivo contra la ruta dentro
del ZIP (`ASSETS/v4_audit/review_input_manifest.json`), y pasaba con el guard apagado: la exclusion funciona
por `Path.name`, asi que la asercion debia comparar `Path(miembro).name`. Un mutante lo demostro (M7 paso de
EXIT=0 a EXIT=1 solo al corregir el test, no el producto).

**Seguimientos abiertos por E.** (1) anclar por run_id los JSON timestamped — dueno FASE-H, contraste
VERIFY; (2) decidir si ABSENT de un insumo obligatorio debe subir de INFO — dueno VERIFY; (3) el fallback
`legacy-ancestor-walk` debe retirarse cuando H/E2E garanticen manifiesto en toda corrida — dueno H/E2E.

## FASE-F (2026-10-06) — AC13, lo medido y seguimientos

**Que se cerro.** Un sumidero unico de redaccion (`modules/utils/redaction.py`) y nueve rutas de salida
calificadas o cerradas contra el: consola, excepciones, `logs/`, `output/` y el artefacto nuevo de D. No se
reimplemento ningun provider y no se toco autenticacion, modelos, configuracion central ni politica de
reintentos. La pata de revocacion no es un test: es la afirmacion del operador, registrada con su referencia
no secreta.

**Lo que la fase midio, no preveio.**

| Concepto | Valor medido |
|---|---|
| Par PRE/POST (misma seleccion literal de 6 rutas) | 372 passed / 10 skipped → **373 passed / 10 skipped**, ambos EXIT 0; +1 = la funcion nueva del re-anclaje de AC-S1 |
| POST extendido (con `tests/utils/test_fase_f_sumidero_redaccion.py`) | 419 passed / 10 skipped, EXIT 0 |
| Funciones de test nuevas | 40 en el archivo de F (47 casos con parametrizacion) + 1 en AC-S1 = **41** |
| Funciones canonicas | 4.939 en HEAD → **4.980** en el arbol (+41) |
| Mutantes | **9/9 caen por fuga detectada** (ninguno por syntax/import), 9/9 restaurados y verificados por sha256, 9/9 verdes tras restaurar |
| Re-anclajes | 1 asercion (`test_none_keys_is_noop`, que pineaba la debilidad de `_sanitize_text`) y 2 literales de fixture re-anclados **por concatenacion**, no rebajando la regla |
| Brecha del verificador | `output/**` y `logs/**` nunca se leian (`git ls-files output logs` = 0 rutas); `sk-[A-Za-z0-9]{20,}` no cazaba `sk-or-v1-…` ni `sk-ant-…`; la rama de >5 MB citaba un global inexistente (NameError) |
| Medicion antes de activar la pata nueva | 1.041 archivos bajo `output/` y `logs/`, **0 hallazgos**; mayor archivo versionado 780.700 bytes (rama del NameError inexecutable hoy) |
| Contador v4complete | 0/1 (ninguna corrida; AC13 se verifico offline con transporte sustituido) |
| Sello de regresion completa (arbol definitivo) | **1 failed / 5.064 passed / 41 skipped / 4 xfailed en 390,64 s, EXIT 1**. El unico rojo es el ajeno y orden-dependiente del piloto JEV (`test_jev_pilot_deepseek_brazo.py`), que en aislado pasa **15/15**; C y D declararon el mismo. Una primera corrida (1 failed / 5.062 passed) quedo **vencida por edicion propia** a mitad de fase y se archiva como tal, no se reutiliza |
| Quick final | 13/13 con EXIT 0 sobre el arbol definitivo; el Secrets Check leyo **1.057 salidas** bajo `output/` y `logs/`, 0 hallazgos |

**Tres observaciones de instrumento (de la fase sobre su propio trabajo, no del producto).**
(1) **Leccion nueva (L-F-RED, formulada al medir): un detector ampliado choca con el corpus viejo por via del
fixture, no del producto.** Al anadir el
patrón `sk-or-/sk-ant-`, el quick puso rojo `tests/auditors/test_p5_ac_s1_secret_sanitization.py`: su
`SYNTHETIC_OPENROUTER_KEY` (prefijo `sk-or-` mas 26 caracteres legibles) es literal con forma de credencial en un archivo
versionado. Los patrones viejos los esquivaban por azar (la clase `[A-Za-z0-9]` no tragaba guiones), no por
diseno. Se resolvio por construccion —concatenar prefijo y cuerpo, el recurso que ya usa
`test_p5_ac_s2_remediacion.py:33`— y **no** rebajando el patron: el valor en memoria conserva la forma y ahi
es donde los tests la prueban. Un verde que depende de que el detector no sepa mirar es un verde prestado.
(2) **La rama que nadie ejercita puede estar rota desde su escritura.** El `f"{_MAX_SCAN_BYTES}"` de
`_check_no_secrets` citaba un global inexistente desde AC-S2: con ningun archivo tracked >5 MB en el repo, la
linea era inexecutable y por eso nunca dio rojo. Sus dos dientes nuevos (`test_archivo_grande_*_sin_name_error`)
fabrican el archivo en `tmp_repo`: un verde sin oportunidad de perder no certificaba nada.
(3) **Redactar despues de recortar es la mitad del defecto.** `HttpClient._sanitize_error` recortaba a 100 y
dejava el prefijo de una key larga al descubierto; el orden correcto se afirma con un test que primero
demuestra que el recorte a ciegas dejaba `AIzaSy` visible (`largo[:97]`) y despide exige la ausencia.

**Seguimientos abiertos por F.** (1) **S-F1** `scripts/preload_prospects_gbp.py` persiste
`PlaceData.error_message` en markdown y JSON: llega redactado desde el cliente, pero el script esta fuera de
la allowlist de F — dueno H/VERIFY. (2) **S-F2** `_query_perplexity` no tiene `try/except` propio y su rama de
consola no tiene diente propio — dueno VERIFY. (3) **S-F3** la pata nueva del verificador lee el instante de la
validacion: un archivo que aparezca despues queda fuera hasta la siguiente corrida, y los 8 checks del
pre-commit leen HEAD mientras `output/`/`logs/` nunca entran al index — dueno RELEASE o deuda declarada.
(4) **S-F4** la allowlist de cuarentena (`archives`, `evidence`, `.opencode`) de P5 no se amplio ni se redujo —
dueno operador. (5) La **integracion con captura/snapshot del runner** (consola y stdout/stderr reales) es
prueba de H, no de F; F definio el contrato que H consume.

## FASE-H (2026-10-06) — AC13/AC14/AC17 offline, runner e intento único

**Que se cerro.** El onboarding de la corrida se derivo con el transformador real del repo
(`main._observation_to_onboarding_format`), cambiando **una sola** clave (`hotel.url`) y declarando el resto con
productor por campo; el recorrido offline camino parser, puerta de permisos, loader, frescura, pre-gate de D,
lector AC9 de D sobre el baseline real, resolvedor de E y snapshot previo de `.agent/memory` con la red cortada y
prueba de que el corte tiene diente; y se implemento el runner stdlib previsto (`run_once.py`) con reserva por
creacion exclusiva antes del spawn, estados terminales, vigilancia del PID sin relanzamiento, captura redactada
con el contrato de F y preservacion de evidencia con hash. **No se lanzo `main.py v4complete` y no se creo el
control productivo de FASE-E2E**: lo assertiona un test de la bateria.

**El veredicto que la fase produce es NO FAVORABLE y eso es su resultado, no un fallo suyo.** El preflight
mide 12 requisitos favorables y 1 en contra: `consentimiento_datado_sobre_la_url_viva`. FASE-A decidio que ese
acto corresponde solo al operador (el consentimiento de FASE-P4 ampara otra URL y declara expresamente que no es
entrega a cliente), y el dato tiene **76 dias** al cerrar la fase. El operador eligio cerrar H con el preflight
en contra, no saltarselo. Consecuencia gobernable: `run_once.py --spawn` se niega **antes** de reservar, de modo
que la arista a E2E queda cerrada y el contador sigue en **0/1**.

**Verificado offline por H.** AC14 (selector unico 1 de 6, hash de fuente identico antes y despues, URL
atribuida sin afirmar equivalencia de dominios, `fecha_captura` exigida y fail-closed, `adr_cop`/`occupancy_rate`
declarados `no_disponible`, **rama del loader medida dos veces** y el contrafactual de la URL historica cayendo a
`Using defaults`, `monkeypatch` del transformador que no anula al loader, rechazo real con la variable de frescura
activa). AC17 (reserva exclusiva con dos hilos y barrera, consumo del intento tras fallo y tras timeout, `exit_code`
`None` en timeout porque no se observo terminacion, vigilancia reanudable, `DUDOSO` terminal, `attempts` que no
baja, argv y hashes congelados cotejados contra el preflight). AC13 (S-F5 y S-F8: `assert_redacted` tiene por fin
lamador en el producto y la captura del runner no escribe crudo). AC9 (lector nuevo `leer_control` con `READ_OK` de
vacio valido, `ABSENT` y `READ_ERROR` con causa, y baseline real = el `preflight.json` de la fase). AC12 **parcial**:
H re-ejecuto el par con writer/acta de E y aporto el suyo propio (favorable → proceso; en contra → ni proceso ni
control), sin tocar `write/publish/suppress`, el Juez ni `outcome.py`.

**Rectificaciones medidas por H, con el artefacto delante (`L-V.3`, cuarta ocurrencia en este plan).** (1) El
`hotel_id` que escribe el reporte **no** sale de `"hotel_id": args.url`: esa asignacion vive en `run_execution_mode`
(clave `analysis_path` de su payload de entrega) y en las llamadas de `run_v4_complete_mode` a
`resolve_adr_with_shadow` y `calculate_price_with_shadow`; el reporte escribe `state.hotel_id`, que produce
`OnboardingController.generate_hotel_id()` (`"hotel_" + netloc normalizado`). Y hay una cuarta cadena que el plan
no nombraba: el slug de rutas y ZIP (`hotel_don_alfonso`). (2) El analisis previo **no** cambia el flujo de
`run_v4_complete_mode`: por AST, `discovered_analysis` tiene 1 asignacion y 2 lecturas sin consecuencia (el guard
`if discovered_analysis:` y su `print`); la reutilizacion real, `DeliveryContext.from_analysis_json`, vive en
`run_execution_mode`. El hallazgo
existe y contamina la evidencia de aislamiento (devuelve un **directorio**, no un `analisis_completo.json`), asi
que la exigencia del preflight se mantiene, pero por la razon medida.

**Seguimientos abiertos por H.** **S-H1** consentimiento datado sobre la URL viva — duenio **operador**, bloquea
E2E y **tiene ventana cerrada: ultimo dia util 2026-10-20** (limite admitido [76, 90] dias con `EDAD_MAXIMA_DIAS = 90`;
desde el 2026-10-21 la edad 91 exige una captura nueva del hotel, que el maestro SS5 no puede sustituir editando la fecha). **S-H2** anclaje por `run_id` de los JSON timestamped (deuda que E asigno a H; la cura es de
`review_inputs.py`, fuera del allowlist de H) — duenio **E2E/VERIFY**. **S-H3** `legacy-ancestor-walk` sigue
siendo el fallback sin manifiesto — duenio **E2E/VERIFY**. **S-H4** `tests/e2e/conftest.py` inyecta un stub de
`selenium` en `sys.modules` y rompe la coleccion de las rutas que lo siguen **en cualquier orden de argumentos**
(medido en los dos ordenes y con cada ruta aislada) — duenio **arnes de tests**; mientras, la seleccion se mide en
dos unidades y se declara. **S-H5** el argv congelado fija `--permission-mode auto`, que autoriza llamadas
externas de pago (~0,03 USD por auditoria) — duenio **operador**, antes del spawn. **S-H6** el spawn borraria
**8 de 10** sesiones de `.agent/memory` por `cleanup_old_sessions(days=20)` — duenio **E2E** (respaldo o
aceptacion explicita; el snapshot previo ya esta en `preflight.json`). **S-H7** `find_latest_analysis` devuelve un
directorio porque `memory.save_analysis_reference(...)`, al final de `run_v4_complete_mode`, guarda
`analysis_path=output_dir` — duenio **producto/VERIFY**. Las lineas concretas las publica
`evidence/…/FASE-H/integracion_offline.json` (R2.2 del executor: en los documentos se citan simbolos). **S-H8** la
normalizacion de URL vive en dos definiciones (`main._normalize_url` y una copia privada en
`OnboardingController.generate_hotel_id`) — duenio **identidad/calidad**. **S-H9** `DOMAIN_PRIMER` no se
regenero (checkpoint arrastrado desde C). **S-H10** erratas de registro heredadas (S-F7 y la de C) siguen
esperando el sello de RELEASE.

**Cierre de la fase con deuda declarada, no con verde agregado.** El contador v4complete sigue en **0/1** y E2E
no se inicio (asi lo exige R1 y el propio preflight).

## Métricas de ejecución

Registrar por fase funciones canónicas, casos pytest, passed/failed/skipped/xfailed, delta, hashes de PRE/POST, mutaciones por AC y tiempo real de ejecución. No sumar unidades incompatibles. Mantener contador único de invocaciones v4complete: actualmente 0, máximo autorizado en el diseño 1.

### FASE-0 (2026-09-20) — medidas, no previstas

| Métrica | Valor | Cómo se midió |
|---|---|---|
| Funciones canónicas del repo | **4.264 → 4.285 (+21)** | `grep -rE "^\s*def test_" tests --include=*.py`; el lado HEAD con `git grep -h -E "^[[:space:]]*def test_" HEAD -- tests` (sin tocar el árbol, ver `L-ENT.15`) |
| Pasos de la selección focalizada | PRE 189 · POST-B 189 (**delta 0**) · POST-A 210 | pytest `-q` sobre la selección literal de 12 archivos que guarda `.selection.txt`; mismo intérprete y entorno |
| Suite nueva contra HEAD sin el fix | 16 failed, 3 passed, 2 skipped | `git archive HEAD` extraído en temporal + pytest (bloque PRE-c de `tests_baseline_pre.txt`); 13 rojos por aserción y 3 por `ImportError` del helper nuevo, declarados |
| Regresión completa | **3 failed, 4.247 passed, 41 skipped, 4 xfailed** en 232 s | `pytest tests/ -q`; los 3 rojos preexistentes con dueño (dos registrados en `AGENTS.md`, uno heredado de G) |
| Skipped / xfailed | 1 / 0 en la selección focalizada; 41 / 4 en la completa | salida archivada; los 2 skips del bloque PRE-c son el baseline `output/`, que no está versionado |
| Contrafactual | `BLOQUEADO` → `APROBADO-CONDICIONAL-PENDING-ONBOARDING`; mutante de solo-cero-conteo: sigue `BLOQUEADO` | `TribunalJudge._compute_verdict` en memoria sobre copia temporal del acta archivada (`contrafactual_ac20.py`) |
| Crecimiento del acta | JSON 1.362 → 2.513 bytes (**+1.151, +84 %**); MD **+0 bytes**; `revision_*.json` de la corrida 9.155 bytes | `ActaWriter.write` sobre el acta real en temporal y `json.dumps` con la misma indentación |
| Mutaciones | **6/6 con rojo por el guard**, 0 por syntax/import; worktree restaurado y verificado por sha256 (`todo_restaurado: true`) | `run_mutations.py` → `mutation_report.json` |
| Invariantes congelados | 0.9 / 0.8 / 0.95; `BLOCKING_VERDICTS = {BLOQUEADO, DEVOLVER-CORRECCIONES}`; `T1_CERTIFIABLE_CLAUSES` de 4; `judge.py`, `diagnosis_reviewer.py` y `delivery_packager.py` sin diferencia contra HEAD | `build_thresholds.py` → `thresholds.json` (lee los símbolos y el `git diff --numstat`) |
| Modo rápido | **11/11 al abrir y al cerrar** | `run_all_validations.py --quick` |
| Contador v4complete | **0 / 1** | ni esta fase ni ninguna anterior lo consumió |

### FASE-G (2026-09-20) — medidas, no previstas

| Métrica | Valor | Cómo se midió |
|---|---|---|
| Funciones canónicas del repo | **4.246 → 4.264 (+18)** | `grep -rE "^\s*def test_" tests --include=*.py` (método canónico), mismo criterio en los dos lados |
| Pasos de la selección focalizada | PRE 1.313 · POST-A 1.313 · POST-B 1.331 | pytest `-q` sobre la selección literal que guarda el txt; venv Python 3.13.3, pytest 9.0.0, sin plugin de orden |
| Skipped / xfailed / xpassed | 2 / 0 / 0, idénticos en PRE y POST | salida archivada |
| Fallos | 1 en PRE y 1 en POST, **el mismo y preexistente** | atribuido a `9c4a001` leyendo `clasificar_planes`; 0 regresiones causadas por G |
| Población gobernada | 169 llamadas · 70 gobernadas · 0 receptores sin resolver en producción | `scripts/validate_wiring.py` sobre el árbol |
| Mutaciones | 7/7 con rojo por el guard · 0 por syntax/import · árbol restaurado y verificado por sha256 | `temp/mutaciones_fase_g.py` → `mutation_report.json` |
| Modo rápido | 10/10 al abrir (10 checks) · **11/11 al cerrar (11 checks)** | `run_all_validations.py --quick` |
| Tiempo de pared | verificador ~10,8 s por corrida · suite nuevo 45 s · POST-B 63,7 s | cronometrado en la sesión |
| Contador v4complete | **0 / 1** | ni esta fase ni ninguna anterior lo consumió |

### FASE-H (2026-10-06) — medidas, no previstas

| Metrica | Valor medido | Instrumento |
|---|---|---|
| Funciones canonicas | **4.982 en HEAD → 5.040 en el arbol (+58)** | `git grep -c -E "^\s*def test_" HEAD -- tests` y el grep canonico del arbol |
| PRE S1 (10 rutas) | **367 passed / 0 failed / EXIT 0** sobre 325 funciones canonicas (42 casos de parametrizacion) | `tests_baseline_pre.txt` |
| POST S1 (misma seleccion) | **367 passed / EXIT 0 · delta 0** | `tests_baseline_post.txt` |
| POST extendido | **425 passed / EXIT 0** (+58 de las dos baterias nuevas) | `tests_post_extended.txt` |
| S2 `tests/e2e` (unidad aislada) | 17 passed / 4 skipped / EXIT 0 en **PRE y POST**, delta 0 | `tests_baseline_pre/post_e2e_aislado.txt` |
| Mutantes | **13 aplicados / 13 rojos por su guard y su causa impresa / 13 restaurados por sha256 / 0 por import o sintaxis / 0 anclajes no unicos** | `run_mutations.py` → `mutation_report.json`, crudo en `mutaciones_crudo.txt` |
| Preflight | `intentos: 0`, 12 requisitos favorables y **1 en contra** (`consentimiento_datado_sobre_la_url_viva`), 10 hashes congelados, 4 cadenas de identidad, snapshot previo de 21 archivos de `.agent/memory` | `run_once.py --emitir-preflight` → `preflight.json` |
| Sello de regresion completa | **1 failed / 5.122 passed / 41 skipped / 4 xfailed / EXIT 1** · el unico rojo es el ajeno del piloto JEV (15/15 en su archivo aislado, 141/141 en su directorio) · dos corridas anteriores desechadas por superponerse, archivadas con su numero real | `tests_postfull_regresion.txt` y `descartados_por_superposicion_de_corridas/` |
| Rama efectiva del loader | `YAML_DE_DIR_CLIENTES`, medida dos veces (derivacion y recorrido offline) y decidida **por contenido**, no por la clave `fuente` | `derivar_onboarding.py` + `integracion_offline.py` |
| Edad del dato | **76 dias** (captura 2026-07-22) con `ONBOARDING_FRESHNESS_HOURS` ausente del entorno, `.env` y `.env.template` | `integracion_offline.json §frescura` |
| Red | cortada despues de los imports, con prueba de diente (`AssertionError` al conectar) | `integracion_offline.json §red` |
| Producto modificado | **0 archivos**: el codigo nuevo queda acotado al runner y a la evidencia de la fase | `git diff --name-only HEAD` |
| Contador v4complete | **0 / 1** | ni el recorrido ni la bateria invocarion `main.py v4complete` |

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
