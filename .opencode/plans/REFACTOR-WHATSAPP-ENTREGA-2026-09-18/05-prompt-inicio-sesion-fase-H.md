# FASE-H — Integración offline, onboarding derivado y runner de intento único

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-G completa; comprobar cierres previos, incluida acreditación operativa de F.
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
- **En la corrida hay tres identidades distintas, no una, y H fija las tres por escrito** (ya no "confirmar identidad `hotel_don_alfonso`"): el `hotel_id` que se le pasa al assessment sale de la **URL** (`"hotel_id": args.url` en `run_v4_complete_mode`), el nombre del **paquete** sale de `--nombre` o del slug derivado (la asignación `hotel_name = args.nombre or _extract_hotel_name_from_url(...)` en la misma función) y la identidad de memoria es el `canonical_url` normalizado (`_normalize_url(args.url)`). El preflight registra los tres valores efectivos y su correspondencia; si divergen, se declara la divergencia antes del spawn, no se resuelve por reportes a posteriori.

Anclas de línea medidas el 2026-09-19 en HEAD 938f59f: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/REVISION-2/anclajes_medidos.json`

## Runner stdlib y evidencia

- El único comando hijo es el literal del maestro, desde la raíz del repositorio y con `./venv/Scripts/python.exe`; H comprueba parser, argv y rutas sin ejecutar `main.py v4complete`.
- Preflight registra attempts=0 sin consumir la reserva productiva. `run_control.json` se reserva mediante creación exclusiva antes de spawn; nunca sobrescribir o borrar control existente para habilitar otra corrida.
- Control productivo y snapshot pertenecen a `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/`; en H usar controles aislados de test, sin lanzar ni simular allí un éxito real.
- **Aislamiento del estado persistente antes del spawn:** H toma snapshot de `.agent/memory` (inventariado con hash, sin modificarlo) y registra si la llamada a `find_latest_analysis` en `run_v4_complete_mode` (implementado en `MemoryManager.find_latest_analysis`, cuyo `output_dir = Path("output")` escanea un directorio **hardcodeado** relativo al cwd) encuentra o no un análisis previo reutilizable para la `canonical_url` de la corrida. Un hallazgo previo cambia el flujo real —se reutiliza en vez de auditar— y por eso se declara en el preflight, no se descubre después.
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

Actualizar prompt, checklist, dependencias, índice, 00/09/10, ACs y al menos tres observaciones medidas; CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`.
Sustituir variables por archivos/tests medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-H --desc "REFACTOR-WHATSAPP-ENTREGA: integración offline, onboarding trazable y runner único preparado" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/validate_document_integration.py
```

Confirmar REGISTRY sin GAP y TOTAL PASS dinámico; rojos o permisos faltantes implican checkpoint, no cambiar baselines/configuración para cerrar.
DOMAIN_PRIMER solo por writer según resolución de A; write-back durable solo autorizado y saneado, con frescura comprobada, o checkpoint explícito. No VERSION, commit, push ni release implícitos.

## Presupuesto y checklist

Referencia **60 tool_use hasta el commit de código**; instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`, duración de pared aparte.
Si no medible o denegado: **FUERA DE SERVICIO (R2.1)**; retirar métrica/comparación, auto-reporte separado sin estimaciones ni evasión. Medición válida permite recalibrar; sin commit autorizado, checkpoint sin fingir corte.
- [ ] G y prerrequisitos cerrados; PRE/POST y mutantes acreditan contratos offline, no una corrida real.
- [ ] YAML derivado conserva 2026-07-22 y valores; fuente/hash/URLs trazables, loader real acepta sin bypass.
- [ ] Runner stdlib y control exclusivo probados con child falso; attempts productivos siguen en 0.
- [ ] Snapshots/redacción y lectores calificados; O1/Juez/umbrales intactos, sin datos históricos alterados.
- [ ] Cierre incremental completo y R2 medido o retirado; E2E queda para otra sesión.
