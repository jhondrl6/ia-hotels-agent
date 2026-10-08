# FASE-H — Integración offline, onboarding derivado y runner de intento único

**Estado:** **COMPLETADA EN CONTRATOS OFFLINE (2026-10-06) y NO HABILITANTE DE LA ARISTA A E2E**, sin commit
(mandato de ejecución; los cinco cortes se sostienen sin él). ⟦**Commit + L3 + Push ejecutados el 2026-10-06 por
orden literal:** commit único **`1c20695`** (40 archivos, +6.780/−92, **8/8** checks del pre-commit sin saltar),
revisión **L3 sobre `ec8a272..1c20695`: 0 hallazgos**, push con paridad **0/0** verificada por `git ls-remote`
(remoto en `1c20695`). El sha se estampa aquí porque la propia orden hizo necesario un sello documental; lo anterior
describe el mandato de ejecución y se conserva como histórico. Sin autorización siguen: tag, QMind, `DOMAIN_PRIMER`,
rotación de credenciales y las erratas S-H10/S-H11/S-F7, todas al sello de RELEASE. **Nada de esto habilita E2E: el
veredicto `spawn_autorizado=false` sigue en pie por S-H1**⟧. El preflight que la fase emite es **NO FAVORABLE**:
12 requisitos favorables y 1 en contra (`consentimiento_datado_sobre_la_url_viva`), que solo emite el operador
(FASE-A decidió que el agente no puede). Cierre elegido por el operador entre tres opciones; la lectura literal
de «INCOMPLETA» de la Tarea 4 queda declarada en `evidence/…/FASE-H/resultados-y-observaciones.md` y es de estado
documental, no de medición. Contador v4complete **0/1**. **Dependencia inmediata: FASE-F cerrada**, según la cadena
`A → G → 0 → B → C → D → E → F → H` que publica `dependencias-fases.md`; comprobar además los cierres previos,
incluida la acreditación operativa de F. ⟦Rectificado el 2026-09-24 por el bloque C de la orden de calidad: esta
línea nombraba **G** como dependencia inmediata. G aporta el guard AST que protege las ediciones de B–F, pero no
es el predecesor de H; leerla como «G basta» habría permitido abrir H con F abierta⟧.
**Sello pendiente de RELEASE:** el sha y el rango de los commits de H no se estampan aquí (decisión de C/D/E/F).
**Complejidad técnica:** ALTA: identidad y frescura del input, integración real offline y reserva persistente antes del único proceso externo.
**Scope R3:** 4 tareas, 0 comandos largos externos. Una sesión exclusivamente para H, sin v4complete real.

## Contexto e inicio

Ejecución futura con mandato propio: leer `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `00-lecciones-capitalizadas.md`, checklist y workflow canónico.
Revalidar decisiones de A, estado de G, allowlist, entorno Windows/venv y símbolos del loader/parser; preservar cambios ajenos. No red, scraping ni auditoría preliminar.
Código nuevo acotado al runner stdlib `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py`; preferir tests existentes y no reconstruir el pipeline.
Evidencia de H solo en su directorio propio; onboarding derivado en `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/clientes/`. No tocar datos fuente ni evidencia histórica.

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | Congelar el argv exacto del maestro; no inventar flags para onboarding. |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes. | El preflight distingue ausencia, error de lectura y rechazo de frescura. |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente. | Los lectores preservan READ_OK vacío sin defaults que disimulen fuentes faltantes. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | AC17 controla el runner; no puede contabilizar comandos manuales externos. |
| L-VUP-12 | La evidencia se conserva antes de analizar. | El runner debe preservar snapshot saneado y exit code antes de entregar al análisis. |

## Tareas

1. **PRE e integración offline.** Medir baseline antes de cambios. Descubrir parser, `_load_latest_onboarding_data`, `_observation_to_onboarding_format`, `_normalize_url` y writers/lectores de E/F. Recorrer el flujo productivo con servicios externos sustituidos y red prohibida; comprobar permitir/bloquear sin invocar la CLI real. Verificar prerrequisitos de identidad, revocación y vigencia, con las tres identidades de la corrida fijadas, la rama que toma el loader y el snapshot previo de `.agent/memory` que se describen más abajo.
2. **Preparar onboarding y runner.** Derivar YAML del observations original con procedencia explícita y validar su consumo por el loader real. Implementar únicamente el runner stdlib previsto: reserva exclusiva, control persistente, observación del PID, redacción previa y snapshot. Congelar el comando hijo del maestro sin lanzarlo; no consumir el intento productivo para comprobarlo.
3. **POST, mutantes y preflight.** Repetir selección PRE y añadir pruebas de AC9/AC12/AC13/AC14/AC17 con child falso y controles temporales. Probar rechazos de identidad/frescura y segundo spawn incluso tras fallo/timeout. Emitir preflight con attempts=0 y hashes; cualquier requisito fallido detiene H sin bypass ni E2E anticipado.
4. **Cierre incremental.** Guardar evidencia, delta y límites; registrar ACs offline, documentación y validaciones conforme al contrato. Dejar H INCOMPLETA si algún prerrequisito no pasa; entregar a otra sesión la única invocación autorizable, sin lanzarla aquí.

## Onboarding: fuente y procedencia

- Fuente inmutable: `data/hotel_observations/observations.json`; selector exacto `hotel_name == "Hotel Don Alfonso"`, con un único resultado. Cero o múltiples coincidencias detienen preflight.
- Conservar fecha capturada **2026-07-22**, 11 habitaciones, 140 reservas/mes, valor de reserva 330000 COP y canal directo 30 %; no presentarlos como verificados hoy.
- Usar `_observation_to_onboarding_format`; conservar valores, `campos_confirmados` realmente presentes, confidence y fecha, sin rellenar supuestas confirmaciones ni defaults.
- Cambiar solo el vínculo `hotel.url` del derivado a `https://www.donalfonsohotel.com/`, URL indicada por el usuario; original `https://hoteldonalfonso.com/` permanece intacta. El YAML derivado **debe** llevar en `hotel.url` exactamente la URL de la corrida: `_load_latest_onboarding_data` hace el match contra `_normalize_url(hotel.url)` (su guard `if _normalize_url(yaml_url) != normalized_url` en la rama YAML) e **ignora el nombre del hotel**, que la propia sección Args de su docstring declara "solo para logging, no se usa para matching". Un `hotel.url` distinto o ausente produce fallback silencioso, no un rechazo.
- El preflight registra **qué rama tomó el loader real**, porque son tres salidas distintas y solo la primera es la deseada: la rama YAML de `clientes_dir` que resuelve `_load_latest_onboarding_data` (por defecto `output/clientes`), el fallback a `observations.json` dentro de la misma función (que re-convierte con `_observation_to_onboarding_format`) o `None` y el correspondiente `Using defaults` que imprime `run_v4_complete_mode`. Guardar la evidencia de la rama en el preflight, no deducirla después del informe.
- `_observation_to_onboarding_format` (con su mapa `_FIELD_MAP`) **solo propaga cuatro campos** — `rooms`, `monthly_reservations`, `avg_reservation_cop`, `direct_channel_percentage`— y **descarta `adr_cop` y `occupancy_rate`**, que sí existen en el observation. Esos dos se declaran `no_disponible` en `onboarding_provenance.json` y **nunca** se estiman ni se rellenan con valores plausibles (lección `DA-P1.9`: la frontera de H es transformación trazable, no llenada).
- `metadatos.fecha_captura` debe estar presente en el derivado: si falta, la verificación de frescura se **omite en silencio** aunque `ONBOARDING_FRESHNESS_HOURS` esté definida (el bloque de frescura de `_load_latest_onboarding_data` solo corre `if fecha_str:`). H implementa su propio control de frescura **fail-closed** (sin fecha → rechazo), porque la variable no está definida ni en `.env` ni en `.env.template`, de modo que el chequeo del loader simplemente no corre.
- `onboarding_provenance.json`: hash de fuente original, selector único, fechas, URL histórica/solicitada, atribución al usuario y ruta/hash del YAML derivado. No afirmar redirección comprobada ni equivalencia universal de dominios.
- Verificar hash original antes/después y el enlace de procedencia; fuente cambiada o selección ambigua impide certificar AC14. No editar warehouse, formulario ni alias global.
- El loader real debe seleccionar ese YAML bajo clientes para el output previsto y declarar fuente; inspeccionar resultado efectivo, no sustituir el loader por un mock de éxito ni aceptar fallback silencioso.
- Comprobar solo la configuración pertinente `ONBOARDING_FRESHNESS_HOURS`, sin volcar entorno ni secretos. Si está activa y el loader rechaza antigüedad, detenerse antes de consumir el intento.
- Prohibido fechar a hoy, desactivar frescura, forzar aceptación o caer a defaults. Una actualización real aportada por el usuario requiere fuente aparte y decisión registrada, no una edición encubierta.
- No inventar `--onboarding-file`, usar `--output-dir` de hook-pdf ni buscar el último archivo entre hoteles.
- **En la corrida hay tres identidades distintas, no una, y H fija las tres por escrito** (ya no "confirmar identidad `hotel_don_alfonso`"): el `hotel_id` que se le pasa al assessment sale de la **URL** (`"hotel_id": args.url` en `run_v4_complete_mode`), el nombre del **paquete** sale de `--nombre` o del slug derivado (la asignación `hotel_name = args.nombre or _extract_hotel_name_from_url(...)` en la misma función) y la identidad de memoria es el `canonical_url` normalizado (`_normalize_url(args.url)`). El preflight registra los tres valores efectivos y su correspondencia; si divergen, se declara la divergencia antes del spawn, no se resuelve por reportes a posteriori. ⟦**Rectificada por H el 2026-10-06, medido contra el artefacto:** el `hotel_id` que **escribe el reporte** no sale de `"hotel_id": args.url`. Esa asignación vive en `run_execution_mode` (la clave `analysis_path` de su payload de entrega) y en las llamadas de `run_v4_complete_mode` a `resolve_adr_with_shadow` y `calculate_price_with_shadow`. El reporte escribe `state.hotel_id`, producido por `OnboardingController.generate_hotel_id()` = `"hotel_" + netloc normalizado`, con el valor que ya publicó la corrida archivada (`hotel_donalfonsohotel.com`). La identidad de memoria sigue siendo `_normalize_url(args.url)` = `donalfonsohotel.com`, y hay una **cuarta** cadena que el plan no nombraba: el slug de rutas y ZIP, `hotel_name.lower()` → `hotel_don_alfonso`. El preflight fija las cuatro; las líneas concretas quedan en `evidence/…/FASE-H/integracion_offline.json`⟧.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Runner stdlib y evidencia

- El único comando hijo es el literal del maestro, desde la raíz del repositorio y con `./venv/Scripts/python.exe`; H comprueba parser, argv y rutas sin ejecutar `main.py v4complete`.
- Preflight registra attempts=0 sin consumir la reserva productiva. `run_control.json` se reserva mediante creación exclusiva antes de spawn; nunca sobrescribir o borrar control existente para habilitar otra corrida.
- Control productivo y snapshot pertenecen a `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/`; en H usar controles aislados de test, sin lanzar ni simular allí un éxito real.
- **Aislamiento del estado persistente antes del spawn:** H toma snapshot de `.agent/memory` (inventariado con hash, sin modificarlo) y registra si la llamada a `find_latest_analysis` en `run_v4_complete_mode` (implementado en `MemoryManager.find_latest_analysis`, cuyo `output_dir = Path("output")` escanea un directorio **hardcodeado** relativo al cwd) encuentra o no un análisis previo reutilizable para la `canonical_url` de la corrida. Un hallazgo previo cambia el flujo real —se reutiliza en vez de auditar— y por eso se declara en el preflight, no se descubre después. ⟦**Medido por H el 2026-10-06:** el hallazgo **existe** (`output/TAREA7-2026-09-19/v4_complete`), pero por AST sobre `run_v4_complete_mode` la variable `discovered_analysis` tiene una asignación y dos lecturas sin consecuencia —el guard `if discovered_analysis:` y su `print`—; `consumos_que_cambian_el_flujo = []`. La reutilización real, `DeliveryContext.from_analysis_json`, está en `run_execution_mode`. Y el valor que devuelve el índice de sesiones es un **directorio**, no un `analisis_completo.json`, porque `memory.save_analysis_reference(...)` al final de `run_v4_complete_mode` guarda `analysis_path=output_dir` (deuda S-H7, dueño producto/VERIFY). Las líneas concretas de estos tres hechos las publica `evidence/…/FASE-H/integracion_offline.json`, no este prompt (R2.2 del executor: citar símbolos). La exigencia del preflight se mantiene intacta —declarar o excluir—, pero por contaminación de la evidencia de aislamiento (L-PF11), no por la reutilización afirmada⟧.
- **Congelar `--permission-mode`:** el default es `auto` (`build_parser`) y el argv del maestro no lo fija; con `chat` el gate `check_permission` de `run_v4_complete_mode` omite la auditoría externa y el pipeline sigue con defaults y `audit_result=None`, que es un resultado distinto con el mismo exit code. El valor efectivo queda escrito en el preflight y en el argv congelado.
- La corrida misma borra estado: `run_v4_complete_mode` invoca `memory.cleanup_old_sessions(days=20)` (`MemoryManager.cleanup_old_sessions`) y elimina archivos de sesión de más de 20 días. Por eso el snapshot de `.agent/memory` es **previo** al spawn y forma parte de la evidencia, no un paso posterior.
- Persistir `state` (estado/status), `attempts`, PID, argv, timestamps, source hashes, `exit_code` y referencia al snapshot; distinguir proceso activo, fallo y terminación, sin fabricar exit code.
- Consumir attempts=1 al crear proceso, incluso si falla después; reserva persistente impide un segundo spawn concurrente. Un fallo de spawn se registra sin borrar reserva ni reintentar automáticamente.
- Permitir observar/reanudar vigilancia del PID existente, nunca relanzar; un timeout del delegado o pérdida de conexión no concede otra ejecución. Control dudoso exige detenerse, no resetearlo.
- Congelar hashes del código, runner e input; divergencia respecto del preflight detiene autorización de spawn. No añadir dependencias, cambiar entorno ni usar git para congelar los archivos.
- Capturar stdout/stderr con redacción antes de consola/disco, reutilizando el contrato calificado en F sin importar providers ni cargar credenciales en el runner stdlib.
- Al terminar, preservar inmediatamente inventario, reportes, acta y ZIP publicado si existe, con hashes y snapshot saneado, antes del análisis; registrar faltantes y errores explícitamente.
- No copiar `.env`, caches o logs históricos crudos ni mantener ZIP suprimido contra O1. No exportar documentos internos retenidos ni cambiar write/publish/suppress o el Juez.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Tests obligatorios

Principal con `./venv/Scripts/python.exe`: suites descubiertas de onboarding, integración/orquestación, delivery y seguridad; red sustituida/prohibida. Ninguna prueba lanza la CLI real.
PRE/POST idénticos en selección/entorno, con exit codes y passed/failed/skipped/xfailed/xpassed; explicar delta de casos frente a funciones canónicas.
AC14: selector único, no encontrado/ambiguo, hash alterado, URL atribuida, fechas/valores conservados, fuente efectiva y rechazo real con frescura activa; mocks externos no anulan el loader.
AC17: child falso stdlib con éxito, fallo, timeout, vigilancia reanudada y dos lanzadores concurrentes; segundo intento rechazado antes de spawn, incluso tras fallo. No tocar el control productivo.
AC9: READ_OK vacío, ABSENT y READ_ERROR por lector nuevo; baseline real o skip visible y AC no certificado. AC12: pares permitir/bloquear con writer/acta reales y enforcement intacto.
AC13: salida sintética por stdout/stderr y snapshot saneados antes de persistir, sin marcadores filtrados; el informe no acredita revocación por sí solo.
Mutantes aislados: quitar reserva/redacción/procedencia o desconectar guard debe romper la aserción correspondiente; registrar símbolo, test, exit codes, causa y restauración en `mutation_report.json`.

## Delegación viable

`delegate_task` solo para inventarios read-only independientes, sin imports, tests, secretos ni archivos compartidos; arquitectura y preparación efectiva quedan con el principal.
Brief: objetivo, allowlist de código/tests, prohibidos datos sensibles/imports/red, contrato decidido, inventario esperado y criterios; prohibir lanzar runner, CLI o fases futuras.
`Agent` es equivalente si disponible y permitido; si WSL no accede al venv Windows, no reinstalar dependencias. Principal ejecuta imports/tests y verifica diff y artefactos.

## Post-ejecución

Actualizar prompt, checklist, dependencias, índice, 00/09/10, ACs y las observaciones medidas que realmente existan — **sin cuota de lecciones nuevas**; CHANGELOG **bajo `## [Sin publicar]`**, no bajo número de versión —fechar una release es acto de RELEASE (`04-contrato-ejecucion.md` paso 3)— y nota en `docs/GUIA_TECNICA.md`.
Sustituir variables por archivos/tests medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-H --desc "REFACTOR-WHATSAPP-ENTREGA: integración offline, onboarding trazable y runner único preparado" --fecha "$FECHA_CIERRE" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

`--fecha` = fecha real de cierre; si el registro es tardío, `--nota` con el motivo. `log_phase_completion.py::parse_args` la declara obligatoria junto con `--fase` y `--desc` y la valida como fecha de calendario, así que `$FECHA_CIERRE` es variable a sustituir — el comando sin la bandera se niega en lugar de estampar la fecha del reloj. ⟦Puesta al día 2026-10-06: este bloque se escribió antes de esa obligatoriedad y rompía al ejecutarse tal cual; la regla canónica vive en `docs/CONTRIBUTING.md` y en el executor §4.5.1, y no se re-transcribe aquí⟧.

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico; rojos o permisos faltantes implican checkpoint, no cambiar baselines/configuración para cerrar.
DOMAIN_PRIMER **regenerado** solo por su writer según la resolución de A (regenerar cierra esta fase; **verificar** con `doctor.py --context` es operación de RELEASE — dos operaciones distintas), **y solo si el mandato de la fase autoriza escribir** `.agent/knowledge/DOMAIN_PRIMER.md`: está versionado, cada regeneración ensucia el árbol, y sin esa autorización se declara el checkpoint en vez de tocarlo (regla canónica en `04-contrato-ejecucion.md` paso 4). Write-back durable **solo con su autorización literal propia** y saneado, con la frescura comprobada por descarga y sha —no por título—, o checkpoint explícito con `PENDIENTE-AUTORIZACION`. No VERSION, commit, push ni release implícitos.

**Derivados vencidos: un rojo del quick al cerrar puede no ser del cambio.** Si la fase añadió evidencia `.py` o editó documentos del plan, correr el fixer del derivado que cayó y **re-correr el quick**:

- `[8/13]` OpenCode References → `./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix`
- `[9/13]` Plan Citations → `./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline` (acto visible: lo hace quien documenta; no silencia un rojo)
- `[11/13]` Wiring → `./venv/Scripts/python.exe scripts/validate_wiring.py --write-report`
- `[13/13]` Packs → `./venv/Scripts/python.exe scripts/build_phase_briefing.py`

Las cuatro etiquetas son las que imprime el **modo rápido**; en el modo completo solo sus cinco checks exclusivos se etiquetan con denominador 18. El número lo imprime la corrida: no se copia a ningún documento.

## Presupuesto y checklist

Referencia **60 tool_use hasta el corte que la sesión tenga autorizado** («hasta el commit» solo si el commit lo está; si no, «hasta listo para revisión», declarando cuál se usó — **los cinco cortes se sostienen sin commit**); instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`, duración de pared aparte.
Si no medible o denegado: **FUERA DE SERVICIO (R2.1)**; retirar métrica/comparación, auto-reporte separado sin estimaciones ni evasión. Medición válida permite recalibrar; sin commit autorizado, checkpoint sin fingir corte.
- [x] G y prerrequisitos cerrados; PRE/POST y mutantes acreditan contratos offline, no una corrida real. **Hecho:** cadena A→G→0→B→C→D→E→F cerrada y empujada (F en `20a07ae`/`ec8a272`); PRE S1 367/EXIT 0 → POST S1 367/EXIT 0 (delta 0) y POST extendido 425; S2 (`tests/e2e`) medida aparte en las dos unidades por la contaminación de `selenium` de su conftest (deuda S-H4); **13/13 mutantes rojos por su guard y restaurados por sha256**; nada lanzó `main.py v4complete` y el control productivo de FASE-E2E sigue inexistente (aserción de la batería).
- [x] YAML derivado conserva 2026-07-22 y valores; fuente/hash/URLs trazables, loader real acepta sin bypass. **Hecho:** `onboarding_provenance.json` con hash de la fuente antes y después (idéntico), selector 1 de 6, productor por campo, `adr_cop`/`occupancy_rate` declarados `no_disponible`, y **rama del loader medida dos veces** (derivación y recorrido) ambas en `YAML_DE_DIR_CLIENTES`; el contrafactual con la URL histórica devuelve None → `Using defaults` silencioso. Sin fecha de captura, la derivación **rechaza** (fail-closed propio; `ONBOARDING_FRESHNESS_HOURS` no está en el entorno, `.env` ni `.env.template`).
- [x] Runner stdlib y control exclusivo probados con child falso; attempts productivos siguen en 0. **Hecho:** `run_once.py` (reserva `O_CREAT|O_EXCL` antes del spawn, estados terminales, `attempts` que no baja, vigilancia reanudable, `DUDOSO` terminal, exit code solo si se observó la terminación, captura redactada con el contrato de F, snapshot previo de memoria, `preservar_resultado`); preflight publicado con `intentos: 0`, argv congelado con `--permission-mode auto`, 10 hashes y las cuatro cadenas de identidad. **El preflight es NO FAVORABLE** por S-H1, así que `--spawn` se niega antes de reservar.
- [x] Snapshots/redacción y lectores calificados; O1/Juez/umbrales intactos, sin datos históricos alterados. **Hecho:** `write/publish/suppress`, `judge.py` y `outcome.py` sin diferencia contra HEAD y dentro del inventario que el spawn coteja; `data/hotel_observations/observations.json` y `evidence/FASE-P4/` intactos (hash declarado); el lector nuevo `leer_control` distingue `READ_OK` con vacío válido, `ABSENT` y `READ_ERROR` con causa.
- [ ] Cierre incremental completo y R2 medido o retirado; E2E queda para otra sesión. **Cierre: hecho** (prompt, checklist, dependencias, 00/09/10, CHANGELOG bajo `## [Sin publicar]`, GUIA_TECNICA, `log_phase_completion.py` sin GAP, derivados regenerados). **R2: FUERA DE SERVICIO (R2.1)** con auto-reporte en unidad propia (~78 intervenciones al corte «listo para revisión»). **E2E queda bloqueado y para otra sesión**: primero S-H1 (consentimiento del operador), luego re-emitir el preflight en la sesión de E2E. **Y con fecha límite medida: el consentimiento solo es válido hasta el 2026-10-20** (ventana [76, 90] días sobre la captura 2026-07-22; `EDAD_MAXIMA_DIAS = 90`).
