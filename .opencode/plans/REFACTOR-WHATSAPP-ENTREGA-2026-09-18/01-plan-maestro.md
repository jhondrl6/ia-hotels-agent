# Plan maestro — REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Estado: DISEÑADO, SIN IMPLEMENTAR.** Preparación del 2026-09-18 contra HEAD `7d91c9f`, versión 4.77.0. Objetivo de release propuesto: 4.78.0; no se cambia VERSION.yaml en esta sesión.

**Objetivo:** eliminar bloqueos espurios por promesas WhatsApp imposibles, impedir botones sin destino o sin verificación, conservar causas/evidencia de bloqueo y certificar el resultado con una sola ejecución final para Hotel Don Alfonso. No prometer READY a costa de ocultar bloqueos legítimos.

Fuente de partida: `.opencode/context/CONTEXT-BUG-WHATSAPP-VERIFIED-BLOQUEO-ENTREGA-2026-09-17.md`. Workflow canónico: `.agents/workflows/phased_project_executor.md` v2.24.0. La ruta recibida con directorio `iahcli` no existe; se usa `iah-cli`. No se altera el contexto histórico.

## 1. Revalidación y correcciones al contexto

La historia es insumo, no prueba del estado actual. No hubo cambios de código entre `38796da` y HEAD, pero varias afirmaciones del contexto ya eran incompatibles con ese código.

| Punto | Evidencia viva por símbolo | Consecuencia para el plan |
|---|---|---|
| F-A es un no-op como fix | `run_v4_complete_mode` produce campo al detectar HTML; `_check_whatsapp_verified` intenta rescatar campo ausente + HTML | No certificar esa combinación imposible. No agregar kwargs solo para volver verdes tests ficticios. |
| F-A' sí decide | `V4AssetOrchestrator.generate_assets` omite HTML al invocar `PainSolutionMapper.detect_pains`; main y `V4DiagnosticGenerator._identify_brechas` lo pasan | AC1 compara las tres rutas y su ledger. |
| F-F del contexto está incompleta | `PAIN_SOLUTION_MAP`, `ConditionalGenerator.PAIN_TO_ASSET`, `get_assets_for_pain` y `_solutions_to_asset_specs` también deciden; quitar `promised_by` no los cambia | B alinea todos los productores de promesas y sus identidades, no una línea aislada de catálogo. |
| CONFLICT no significa número publicable | El mapper promete botón + guía y fuerza `can_generate=True`; `CoherenceValidator._check_whatsapp_verified` convierte cualquier campo a 0.95 si SitePresence dice exists | No conservar automáticamente el botón para `whatsapp_conflict`; preservar el conflicto y retirar el boost que suplanta confianza del número. |
| El destino también puede sobrescribirse | `_extract_validated_fields` asigna `whatsapp=phone_web`; ConditionalGenerator prioriza esa clave | C garantiza que solo el campo validado del canal alimenta el href; teléfono web no prueba WhatsApp. |
| Ya existe guía de conflicto, no setup seguro | `WhatsAppConflictGuideGenerator`; `INVALID_MAPPINGS` prohíbe usarla como resolución de ausencia. La guía de instalación legacy genera placeholder numérico | Crear setup específico sin número. No renombrar la guía de conflicto para eludir la semántica ni usar el placeholder legacy. |
| F-P4.1 ya recibió corrección P6/P6-R | `DeliveryPackager.write` deriva `asset_zip_paths`; `AssetResponsibilityContract.generate_delivery_template`; `test_acg1_orden_publicado_usa_ruta_real_del_zip` | E revalida e integra el asset nuevo. No reconstruir el writer ni afirmar que hoy siempre entrega un stub de 468 bytes. |
| F-P4.2 sigue vigente | `run_v4_complete_mode` hace unlink de diagnóstico/propuesta antes del Tribunal; `resolve_latest` no recupera archivos borrados | E preserva snapshot interno no exportable y rutas explícitas por ejecución; conserva el enforcement. |
| F-P4.5 tiene prevención parcial implementada | `LLMMentionChecker._sanitize_text/_sanitize_error/_query_gemini`; `ValidationRunner._check_no_secrets` | F valida lo existente y cubre nuevas salidas locales. Revocación de key expuesta es comprobación operativa, no hecho inferible del código. |
| Don Alfonso: la URL del warehouse **no existe** | Medido 2026-09-19: `https://hoteldonalfonso.com/` → NXDOMAIN; `https://www.donalfonsohotel.com/` → 200 con redirección a `https://donalfonsohotel.com/` (WordPress). `tests/fixtures/donalfonsohotel_onboarding.yaml` ya declara la URL viva. `_normalize_url` no iguala ninguna de las dos | La URL de la corrida es la del usuario porque es la única alcanzable; no es un alias: se registra como corrección de identidad con procedencia. El onboarding derivado sigue aislado y el warehouse no se edita sin instrucción expresa. |
| El detector no puede ver el botón que existe | Comprobado con el código real (`SitePresenceChecker._check_html_element`, `check_methods: ["html"]`, búsqueda en texto/`<a href>`/clases): la home viva tiene **0** referencias a WhatsApp y `/contacto/` tiene **54**, todas dentro de `<style>`/`href`/`src` del plugin `creame-whatsapp-me` (JoinChat 6.3.2); ningún `wa.me` ni número en HTML estático, y un `except Exception` devuelve `{"found": False}` | F-F/F-A'/C no bastan: con esa señal B crearía el pain de ausencia sobre un hotel que sí tiene canal. AC19 gobierna la cobertura del lector y la regla "error o página no inspeccionada ≠ ausencia". |
| No existe flag de archivo onboarding | `build_parser`: `--output` y `--nombre`; `_load_latest_onboarding_data` busca YAML bajo clientes y fallback warehouse | No inventar `--onboarding-file` ni usar `--output-dir` de hook-pdf. |
| No hay runner con las tres garantías | Los runners examinados no reúnen reserva persistente, snapshot saneado y exit code | H prepara un runner acotado al plan; E2E lo invoca una vez. |

La propuesta supera el alcance de F-F + F-A' en una sola fase porque incluye seguridad, coherencia, lectores y certificación. Se divide conforme a R3, no se empaquetan todos los fixes en una sesión.

## 2. Decisiones de diseño y alcance

### Matriz de decisión WhatsApp propuesta

A la ratifica antes de implementar; si se solicita una política diferente, actualizar B/C y los ACs antes de empezar.

| Entrada | Promesa y asset | Protecciones |
|---|---|---|
| Sin número ni evidencia del canal | `whatsapp_setup_guide`, instrucción/solicitud de validación, no botón operativo | Pain divulgado; cobertura como acción pendiente justificada, no canal ya instalado. Si la red falló, no afirmar ausencia observada. |
| Solo HTML/presencia, centinela | Informar presencia; no crear pain falso de ausencia ni un botón nuevo por esa señal | `can_use_in_assets=False`; nunca convertir presencia en número o verificación. |
| Canal existe pero el lector no lo observa (widget JS, botón fuera de la página inspeccionada) | Ninguno. Estado `no_verificado_en_sitio` con acción de revisión humana; ni botón nuevo ni pain de ausencia | Afirmación máxima permitida: "no observado en la ruta inspeccionada". Prohibido afirmar "el hotel no tiene WhatsApp". Una huella de plugin es evidencia de **presencia**, jamás de número utilizable. Si el fetch falló, es estado desconocido, no ausencia (AC19, AC9). |
| CONFLICT | `whatsapp_conflict_guide`, conflicto visible y acción de resolver | No elegir número por cantidad de reseñas, no prometer botón listo, no borrar hard contradictions existentes. |
| ESTIMATED | No prometer botón operativo; si se necesita acción, guía de confirmación sin promoción a VERIFIED | Umbral de WhatsApp permanece 0.9. |
| VERIFIED + forma válida + necesidad real | Botón con destino exactamente derivado del campo verificado | No exigir generar redundante si ya existe. Un teléfono alternativo no sobrescribe el destino. |
| Botón inseguro forzado en plan/ZIP | Error bloqueante, aun con SitePresence exists | AC3 es guardia de seguridad, no se sustituye por setup después de ocultar un fallo. |

**F-B diferida:** el warehouse seguirá sin transportar WhatsApp. No añadir PII ni tocar formulario/esquema sin decisión escrita de privacidad. El bloqueo estructural puede cerrarse con una entrega de setup honesta, sin afirmar que D1 desapareció.

**F-E diferida:** no cambiar ahora el modelo global CoherenceCheck/denominador; la distinción de lectura ausente/fallida sí es obligatoria para lectores nuevos. Dueño y AC futuro en §6.

**F-D':** retirar el argumento muerto `whatsapp_validation` de `AssessmentBuilder.with_validation` y sus callers, conservando el dato upstream que construye ValidationSummary. No inventar una segunda fuente dentro del builder. Se ejecuta en G con inventario de firma.

**F-A/F-C rechazadas:** no rescatar una rama imposible ni bajar thresholds o pasar WhatsApp a no bloqueante. El boost de mera presencia se elimina para la decisión sobre confianza del número; preservar el uso de presencia para no duplicar un asset realmente existente.

**Módulo legado:** `CommercialGate._check_whatsapp_verified` en `domain_gates.py` no es el check productivo. Conservarlo sin cambios en este plan y documentar su rol test/legacy; no archivarlo ni usar sus tests como certificación del fix productivo.

**Enforcement invariante:** no cambiar `TribunalJudge._compute_verdict`, flags de bloqueo ni los contratos de `write/publish/suppress`. Una ausencia inducida por retención no se presenta como otro fallo independiente, pero ausencias originales y errores de lectura siguen siendo hallazgos.

## 3. Fases y complejidad técnica

R1: cada fila corresponde a **una sesión nueva**. PRE/POST, tests y documentación incremental están dentro de sus cuatro tareas; no son trabajo invisible delegado a RELEASE. A–H no ejecutan comandos de auditoría externa. E2E es la última fase operativa; VERIFY y RELEASE van después porque así lo exige el workflow.

| Fase | Objetivo y cuatro tareas como máximo | Complejidad y razón | Delegación viable | Comandos largos externos |
|---|---|---|---|---|
| A | Revalidar baseline; ratificar matriz/alcance; resolver prerrequisitos de identidad, seguridad y documentación; cierre | ALTA: decisiones de producto y contratos cross-module | Principal decide; solo búsquedas independientes read-only | 0 |
| B | PRE; alinear pains/promesas sin afirmar ausencia con lector ciego y generar setup; POST/serialización/mutantes; cierre | ALTA: múltiples mapas, narrativa/coverage y consumo del estado AC19 | Directa | 0 |
| C | PRE; blindar dato y destino del botón y cubrir el lector de presencia (AC19); POST/mutantes de confianza/presencia; cierre | ALTA: precedencia del dato, protección contra falso VERIFIED y cobertura del detector | Directa | 0 |
| D | PRE; unificar veredicto y causas; POST/fail-fast/serialización; cierre | ALTA: gates y readers de assessment | Directa | 0 |
| E | PRE del writer/lectores; snapshot interno y enlace a revisión; POST ZIP/retención; cierre | ALTA: límite interno/cliente y orden temporal | Directa | 0 |
| F | PRE de redacción; cubrir salidas y confirmar revocación; POST/mutantes sin secretos; cierre | MEDIA-ALTA: límites de salida y credenciales externas | Solo inventarios independientes sin acceso a secretos | 0 |
| G | PRE/inventario de firmas; AST y limpieza de contrato muerto; POST/inyección de caller nuevo; cierre | ALTA: descubrimiento sin lista fija ni falsos verdes | Directa | 0 |
| H | PRE/integración offline; preparar onboarding y runner; POST/preflight sin CLI real; cierre | ALTA: entorno, identidad, reserva y evidencia antes de gastar el único intento | Inventarios read-only paralelos; principal ejecuta imports/tests | 0 |
| E2E | Validar preflight; lanzar una vez y preservar evidencia; cierre y análisis preliminar | MEDIA técnica / ALTA operativa: APIs, una sola oportunidad | delegate_task para corrida si comparte entorno; parent verifica | 1 v4complete |
| VERIFY | Leer artefactos; certificar matriz/diff; triar y extraer lecciones; cierre | ALTA: juicio transversal y límites causales | DIRECTA obligatoria; no delegar | 0 |
| RELEASE | Diagnóstico/versionado; docs oficiales; validación/write-back; archivado/cierre | MEDIA: sincronización y orden del cierre | delegate_task documental con allowlist autorizada | 0 |

Presupuesto por fase e instrumento: `04-contrato-ejecucion.md` §R2. Referencia 60 tool_use al commit de código; retirar métrica si no es medible, nunca reportar estimaciones. No es estimación de duración de pared ni autorización para completar varias fases.

## 4. Criterios de aceptación y pares de evidencia

Todo artefacto indicado como nuevo es **salida futura**, no existente ni certificado. E = `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/`. Los identificadores/keys propuestos quedan congelados en A y se propagan al writer y test. Pruebas offline no cuentan como corridas v4complete reales.

| AC | Contrato y evidencia verificable | Verde / rojo requerido | Fase |
|---|---|---|---|
| AC1 | Mismas entradas producibles producen mismos pain_ids en main, diagnostic y orquestador; `pain_ledger.json.entries` no contiene ausencia fantasma con HTML visible | Quitar señal en detect_pains reintroduce pain/divergencia y rompe test. Tras F-F no exigir que necesariamente bloquee: el rojo es el pain incorrecto, no el efecto histórico ya cambiado | B |
| AC2 | Propuesta + specs + `asset_generation_report.json` + matriz de servicios coinciden; sin número utilizable no prometen botón; setup entregado, ledger conserva el pain y no lo da por instalado | Reintroducir mapping botón para ausencia en productores vivos rompe contrato; probar catálogo y mapper, no solo una constante | B |
| AC3 | Botón forzado con confidence <0.9, CONFLICT, UNKNOWN o centinela queda en error; `coherence_validation*.json.checks` demuestra bloqueo incluso con presence exists | Test negativo debe pasar porque bloquea; mutar el guard/boost debe fallar. Guía no oculta hard contradictions | C |
| AC4 | `gate_report_*.json.gate_results[coherence].details.failed_check_names` y mensajes nombran todos los checks en error procedentes del reporte real | Dos errores conservan ambos nombres; omitir cable/serialización hace rojo. Lista vacía no equivale a reporte ausente | D |
| AC5 | Coherencia 0.8, WhatsApp 0.9, blocking=True y enforcement vigente; evidencia `thresholds.json` de pruebas con fuente de cada valor | Assertions de invariantes; no bajar catálogo/gate para dejar pasar ESTIMATED | C/D |
| AC6 | HTML y ZIP sin wa.me vacío, centinelas, placeholders ni sustitución por phone_web; destino de botón igual al canal verificado normalizado | Inyectar sin dígitos, solo separadores, dígitos no ASCII, longitud inválida y teléfono alternativo; revertir guard hace rojo | C |
| AC7 | `wiring_report.json`: población descubierta de callers validate/detect_pains, kwargs exigidos, fuentes y excepciones tipadas; check incluido en quick | Agregar caller nuevo en archivo nuevo, omitir señal y ocultarla en kwargs opacos debe romper; validar aliases/instancias self y excluir clases validate no relacionadas | G |
| AC8 | Reporte pre-gate persistido y log saneado con culpables; veredicto False bloquea antes de generar aunque score supere 0.8 | Spy de generador no invocado; restaurar regla por score hace rojo. También cubrir entrada directa del orquestador | D |
| AC9 | Nuevos lectores publican `read_status` y causa: READ_OK (incluye vacío), ABSENT, READ_ERROR; retención deliberada se registra aparte | Tres tests por lector más retención; no devolver 0/None favorable ante error; leer baseline real con skip visible si falta | D/E/H |
| AC10 | ZIP del writer real contiene IMPLEMENTATION_ORDER con tareas no vacías, rutas ASSETS existentes, setup/guía correctamente descritos y manifiesto coherente | Regresión P6-R más caso nuevo; desconectar rutas reales/stub hace rojo. No fijar éxito por tamaño solamente | E |
| AC11 | `review_input_manifest.json.documents` tiene run_id, fuente original, hash, ruta interna, read_status y disposition=retained_by_gate cuando aplica; revisores leen ese contenido | Restablecer borrado sin snapshot o perder ruta produce rojo; documentos nunca generados siguen AUSENTES. Snapshot fuera del árbol recursivo exportado | E |
| AC12 | `acta_revision.json.enforcement` y `package_evidence` conservan decisión/hash/conteo; solo publish permitido crea ZIP final; bloqueado suprime cuarentena | Pares permitir/bloquear del flujo real; no hay documento retenido en ZIP público ni hallazgo duplicado por el borrado propio | E/H |
| AC13 | Logs/snapshots nuevos con secretos sintéticos redactados antes de persistir, `sanitization_report.json` sin valores; `credential_status.json` acredita revocación o estado pendiente | Desactivar redacción produce rojo en consola/archivo. No se certifica revocación por un test ni por tener key nueva; el operador aporta evidencia sin secreto | F/H |
| AC14 | `onboarding_provenance.json` enlaza hash del observations original, selector único, URL histórica/solicitada y fechas; loader real usa el YAML derivado y output declara fuente | Nombre no encontrado/ambiguo, hash cambiado o frescura rechazada detienen preflight; ningún default silencioso sustituye los datos | A/H |
| AC15 | PRE/POST, mismo entorno/unidad, delta explicado y `mutation_report.json` por AC con guard/test/exit codes | No aceptar baseline tomado tras añadir tests, rojos por syntax/import en vez del guard, ni regresiones escondidas | Todas impl/H |
| AC16 | Inventario AST de with_validation sin argumento descartado; clasificación documentada del check legacy; sin reintroducir whatsapp_validation como verdad paralela | Inyectar caller con firma vieja rompe contrato; tests relevantes pasan; no borrar variable upstream todavía consumida | G |
| AC17 | `run_control.json` con state, attempts=1, PID, argv, timestamps, source hashes, exit_code y snapshot; el preflight registra attempts=0 | Segundo lanzamiento rechazado antes de crear proceso, incluso tras fallo/timeout; pruebas usan child falso, nunca otra v4complete | H/E2E |
| AC18 | Matriz final por AC en 10-análisis + `certificacion.json`, diff estructural, lecciones y límites; una sola corrida demuestra el camino realmente ocurrido | AC fallido o no ejercitado no se marca SUPERADO EN E2E. READY requiere gates y acta favorables y ZIP válido, no exit 0 | VERIFY |
| AC19 | El reporte de presencia publica `observation_scope` (qué rutas se inspeccionaron), `read_status` del fetch y `presence_evidence_kind` (`wa.me_href`, `plugin_fingerprint`, `ninguna`); mientras el estado sea `no_verificado_en_sitio` no se crea dolor de ausencia ni se promete botón | Fixture con el canal solo en página interna y fixture con huella de plugin sin `href`: ambos deben declarar presencia sin dolor de ausencia y sin número derivado; reducir el lector a la raíz, o que una excepción devuelva `found=False`, produce rojo. Don Alfonso es el caso real esperado por E2E, no un test | C (lector) y B (consumo en ledger y narrativa) |

Para AC1–AC19, el writer produce evidencia y VERIFY la lee. Las keys propuestas de los reportes nuevos no deben quedarse únicamente en tests. Si una corrida correcta no ejercita un caso rojo, declarar VERIFICADO OFFLINE para ese caso, sin afirmar que Don Alfonso lo disparó.


**Meta E2E:** READY_FOR_PUBLICATION y entrega útil, si los datos y demás gates lo permiten. **Condición de honestidad:** un bloqueo legítimo conserva su veredicto; no se altera el producto para alcanzar esa meta. Si no se puede demostrar entrega, AC18 queda parcial/FALLA para esa meta y RELEASE no se cierra como éxito integral.

## 5. Única ejecución final para Hotel Don Alfonso

Fuente original inmutable: `data/hotel_observations/observations.json`. Selección exacta `hotel_name == "Hotel Don Alfonso"`, que debe dar una sola observación; fecha capturada 2026-07-22. Datos inspeccionados: 11 habitaciones, 140 reservas/mes, valor de reserva 330000 COP y canal directo 30 %. No se publican como verificados al día de ejecución.

H prepara YAML con `_observation_to_onboarding_format` en `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/`. Conserva valores, campos_confirmados realmente presentes, confidence y fecha. Enlaza `hotel.url` a la URL **indicada por el usuario** y registra en `onboarding_provenance.json` la URL original, la evidencia de que hoy no resuelve, la redirección `www.donalfonsohotel.com → donalfonsohotel.com` efectivamente observada el 2026-09-19 y la atribución de la corrección al operador. No modifica el JSON original ni crea un alias universal entre dominios: es una corrección de identidad trazable, no una equivalencia supuesta.

A decide si hace falta reconfirmación de vigencia de los datos. H comprueba `ONBOARDING_FRESHNESS_HOURS` sin leer secretos: si está activo y rechaza los datos, se detiene antes del intento. Prohibido actualizar la fecha a hoy, desactivar frescura o caer a defaults para consumir la corrida. Si el usuario aporta actualización real, registrar esa fuente aparte.

**Comando hijo único, ejecutado solamente por el runner de H durante E2E, desde la raíz del repositorio:**

```bash
./venv/Scripts/python.exe main.py v4complete --url https://www.donalfonsohotel.com/ --nombre "Hotel Don Alfonso" --output output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18
```

No ejecutar ese comando manualmente además del runner. Sin force, deploy, auditoría preliminar independiente ni desactivación del Tribunal. El nombre esperado es `hotel_don_alfonso`; confirmar rutas reales con los reportes, no elegir el archivo más reciente entre hoteles.

Runner nuevo acotado: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py`. Reserva por creación exclusiva de control antes de spawn, escribe PID/estado y admite observar/reanudar vigilancia, **no relanzar**. Congela hashes de código/input y contador. Captura stdout/stderr con redacción antes de disco; los writers internos se validan en F. Tras terminar conserva inmediatamente inventario, reportes, acta y ZIP publicado si existe, con hashes. No copia `.env`, caches o logs históricos crudos; no mantiene un ZIP suprimido contra O1.

**Orden final:** A–H → E2E (única ejecución) → VERIFY (análisis formal) → RELEASE (docs). Es la única interpretación compatible con la regla del workflow de que VERIFY y RELEASE no corren v4complete.

## 6. Deudas y decisiones de producto

| Tema | Estado elegido en el diseño | Dueño | AC de futura aceptación / disparador |
|---|---|---|---|
| F-B / D1 contacto warehouse | DIFERIDO, requiere ratificación en A | Producto/privacidad + onboarding | Definir canal comercial almacenable y consentimiento por escrito; luego formulario/esquema/adaptador/ValidationSummary alineados, sin defaults ni exposición pública |
| F-E triestado global de coherencia | DIFERIDO, no prerequisite para F-F | Coherencia | Estado no evaluable serializado con denominador explicado y consumidores actualizados; conflicto real sigue bloqueando |
| Check legacy domain_gates | CONSERVADO, no fix productivo | Quality gates | Archivar solo con inventario y autorización; actualizar doc para que nadie certifique WhatsApp con ese módulo |
| F-P4.1 | CORREGIDO EN CÓDIGO, recalificación pendiente | Delivery | Probar writer real nuevo con setup, no editar evidencia histórica |
| F-P4.3 | RETOMADO por mismo ID | Generación/orquestación; onboarding retiene D1 | Cerrar falso positivo sin atribuir cierre del transporte de contacto |
| F-P4.2 | EN ALCANCE | Orquestación/tribunal readers | AC11/AC12 |
| F-P4.5 | Prevención parcial existente; operación sin acreditar | Operador + auditor LLM | Revocación de la key expuesta, pruebas de salidas nuevas y no propagación del valor |
| Rojos quick PRE | **Corregido por medición 2026-09-19**: no es deriva de contenido. `sync_versions.py --check` y `version_consistency_checker.py` pasan (exit 0, 7 campos in sync); `run_all_validations._check_version_sync` compara las cabeceras contra `full_version: 4.77.2.0` mientras el escritor gobernaría `4.77.2`. Desacuerdo verificador↔escritor | Operador + quality gates | Decidir cuál de los dos representa el contrato vigente y alinear el otro. No reescribir AGENTS/.cursorrules/GUIA a mano para satisfacer un regex; no bloquea el pre-commit. |
| Procedencia del dato Don Alfonso | Dos hechos medidos: (i) `tests/fixtures/donalfonsohotel_onboarding.yaml` fija `canal_directo_pct: 20.0` cuando el warehouse dice 30.0 — el 20.0 es el default de `tests/e2e/test_onboarding_to_harness_pipeline.py` (`datos.get("canal_directo_pct", 20.0)`) cristalizado con `epistemic_status: verified, confidence: 0.95`; (ii) `evidence/FASE-P4/consentimiento-donalfonso.md` amparaba una corrida sobre `hoteldonalfonso.com`, hoy inexistente, con el dato a 59 días y `ONBOARDING_FRESHNESS_HOURS` sin definir | Datos/procedencia + operador | Un default nunca es fuente: el valor gobernante se declara con procedencia y el fixture se corrige desde ahí. El consentimiento se re-emite datado sobre la URL viva y con límite escrito antes de consumir el intento E2E. |

F-P4.4/F-P4.6 u otros resultados de la corrida no se convierten automáticamente en implementación. Si impiden AC18, se trian y requieren sesión de recuperación autorizada; nunca un segundo E2E implícito. No se duplica F-P4.3 ni se reescribe su informe original.

## 7. Preparación, trazabilidad y permisos

`00-lecciones-capitalizadas.md` se creó antes de este maestro. QMind y código vivo obligaron a corregir F-P4.1 y ampliar F-F; el resultado de esos cotejos no se presenta como tests ejecutados. No se ejecutó ninguna v4complete en preparación.

`run_all_validations.py --quick` PRE: 9/10. El único rojo es Version Sync y **no** es deriva documental: `sync_versions.py --check` y `version_consistency_checker.py` exit 0 sobre los 7 campos gobernados, y el pre-commit `[1/7]`/`[2/7]` pasa, de modo que no bloquea commits ni exige tocar AGENTS.md/.cursorrules. La causa es el desacuerdo verificador↔escritor registrado en §6. A decide a quién le toca alinearse.

Durante la preparación se consultó el sitio público del hotel indicado por el usuario (HTTP y HTML estático) y se releyó la evidencia de FASE-P4; no se ejecutó v4complete ni ninguna auditoría externa del pipeline, y ningún valor de secreto fue leído o impreso.

No se genera código en preparación, ni se toca VERSION, datos reales, workflow, secretos o evidencia P4. Solo documentos de este plan y el par generado del índice. Todos los prompts y su cierre se validan antes de entregar. Commit/push no solicitados: no se ejecutan.
