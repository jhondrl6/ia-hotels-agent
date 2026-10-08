# FASE-E2E — Única ejecución real para Hotel Don Alfonso

**Estado:** ⟦**EJECUTADA el 2026-10-07 con su corrida única, SIN COMMIT** (el corte de la fase es documental). ⟦**Sello del 2026-10-07, añadido sin reescribir:** ese «SIN COMMIT» describía el mandato de ejecución y quedó vencido por la orden literal del operador «Commit + L3 + Push». La fase está **commiteada en `b05e620`** (25 archivos, +2.431/−49, **8/8** checks del pre-commit sin saltar), con **revisión L3 sin hallazgos** sobre el commit sin revisar, y **empujada en el rango `6fd39c2..b05e620`** con paridad **0/0** verificada por `git ls-remote`. `FASE-E2E/captura_stdout.txt` se **excluyó** del versionado por S-E2E-6 y entra en su lugar `captura_stdout_saneada.txt`; el crudo sigue en disco con el sha256 que referencia `run_control.json`. El sha y el rango de este sello se cobran en RELEASE, como en C, D, E, F y H⟧. El intento quedó **1/1**: `run_control.json` con `attempts: 1`, `pid: 30576`, `exit_code: 0` y 116 s. Veredicto observado **`APROBADO-CONDICIONAL-PENDING-ONBOARDING`** (tier B+, regla de primer piso aplicada), 13 gates con 11 PASSED + 2 WARNING y 0 fallidos, y **ZIP publicado** con 57 entradas y sha `487f5800…`. AC17 y AC20 ejercitados en flujo real; AC18 **no** se marca aquí. Evidencia y deuda con dueño: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/resultados-y-observaciones.md`. Siguiente sesión: **VERIFY**⟧. **Dependencia inmediata:** FASE-H completa con preflight favorable (`attempts=0`, hashes conformes, identidad y frescura aceptadas, revocación acreditada o pendiente registrado). ⟦**Cumplida el 2026-10-07**: H cerrada y empujada con el consentimiento **S-H1** emitido por el operador (`evidence/…/FASE-H/consentimiento-corrida.md`, commit `d571277`) y preflight **12/12 favorable** con `intentos=0`. **Ventana dura: el único intento se consume antes del 2026-10-20.** Desde el 21 la edad computada del dato (91) excede el techo de H y `run_once.py --spawn` se niega **antes** de reservar (b1-bis), así que la reserva queda intacta pero la fase cierra INCOMPLETA con causa⟧.
**Complejidad técnica:** MEDIA técnica / ALTA operativa: APIs externas, entorno real y **una sola oportunidad**.
**Scope R3:** 3 tareas + **1 comando largo externo** (el único del plan). Sin edición de código de producto.

## Contexto e inicio

Ejecución futura con mandato propio. Lee `01-plan-maestro.md` §4 (AC17, AC18) y §5 completo; `04-contrato-ejecucion.md` §"Corrida única"; `00-lecciones-capitalizadas.md`; checklist; dependencias y el cierre real de H.
Esta fase **no diseña ni repara**: consume el intento preparado por H mediante su runner y preserva la evidencia para VERIFY. Si el preflight falla, el contador queda 0/1 y la fase se cierra INCOMPLETA con causa y dueño; no se lanza el proceso "para ver qué pasa".
Evidencia propia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/` (control productivo, snapshot saneado, exit code, inventario y hashes).

### Lecciones capitalizadas aplicables

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-VUP-12 | La evidencia se conserva antes de analizar. | Snapshot, exit code, inventario y hashes se preservan inmediatamente al terminar, antes de cualquier lectura interpretativa. |
| L-VUP-9 | Los comandos delegados deben usar flags comprobados. | El argv del hijo es el literal congelado en el maestro §5; no se añaden flags, force, deploy ni desactivación del Tribunal. |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | El contador 1/1 lo acredita `run_control.json` del runner, no la narración de la sesión; un comando manual externo no es contabilizable y está prohibido. |
| L-VUP-17 | Los tests locales no certifican integración renderizada. | Lo que la corrida no ejercite se declara NO EJERCITADO; no se promueve a SUPERADO por tener tests verdes en B–H. |

## Tareas

1. **Preflight real y autorización de spawn.** Verificar en disco: cierre de H **y cierre de FASE-0 con AC20 verde** — sin esa serialización el techo alcanzable ya está medido y consumiría el único intento—, **ausencia de `run_control.json`** (la reserva virgen: el archivo no existe hasta el spawn, y es el preflight quien lo declara intacto), hashes de código/runner/input conformes al preflight, YAML derivado y `onboarding_provenance.json` vigentes, las tres identidades fijadas por H (`hotel_id` de la URL, nombre del paquete, `canonical_url`) en lugar de una sola, output aislado del plan, permisos y entorno (`./venv/Scripts/python.exe`), red y credenciales disponibles sin imprimirlas. Verificar además los tres items de aislamiento que H debe haber dejado escritos: el **snapshot previo de `.agent/memory`**, la **rama que tomó `_load_latest_onboarding_data`** (YAML derivado / fallback de observations / `Using defaults`) y el valor efectivo de **`--permission-mode`** (default `auto`; con `chat` la corrida sigue con `audit_result=None` y no es la corrida que el plan quiere certificar). Registrar si `find_latest_analysis` encontró o no un análisis previo reutilizable para la URL canónica: si lo hay, la corrida no audita de cero y eso debe constar antes del spawn. Anotar el resultado del preflight en evidencia de E2E. **No hace falta re-emitir el preflight a mano: `--spawn` revalida contra la fecha del día** (b1-bis, `run_once.revalidar_contra_la_fecha`) —consignando en su salida `revalidacion_del_spawn` la edad de hoy, la que declaraba el preflight guardado, el límite del consentimiento y quién lo emitió— y rechaza antes de reservar si la edad o el documento ya no amparan. **Cualquier rechazo detiene la fase sin spawn.**
2. **Corrida única y preservación.** Invocar el runner una sola vez (comando siguiente), con notificación de término y vigilancia del PID hasta finalización real. No relanzar ante timeout, pérdida de conexión del delegado ni fallo: verificar estado del PID y cerrar con checkpoint. Al terminar —exitoso, fallido o bloqueado— preservar de inmediato snapshot saneado, exit code, argv, timestamps, hashes, inventario, reportes, acta y ZIP publicado si existe. El **argv se registra literal y verbatim** (tal como lo construyó el runner, sin reescribirlo ni normalizarlo), porque es la única prueba de qué rama de permisos y de input corrió realmente. Registrar consumo **1/1** desde la creación del proceso. **La evidencia debe declarar por escrito por qué esta corrida no es una repetición de `output/TAREA7-2026-09-19/`** —mismo hotel, misma URL, ya archivada y usada como baseline medido del plan—: la ruta viva no ejercita la rama WhatsApp del plan (sin pain de WhatsApp, `whatsapp_button` fuera del plan, check `whatsapp_verified` en verde vacuo), así que el valor de la nueva corrida está en la cadena de entrega y en la serialización cambiada que aporta FASE-0, **no** en los AC de WhatsApp.
3. **Análisis preliminar y cierre.** Registrar el resultado observado sin remediarlo: veredicto del Tribunal, gates, ZIP publicado o suprimido, causa de bloqueo legítima si la hay y divergencias frente a lo esperado. **La expectación ya no es "READY":** el resultado esperado de esta fase es un **ZIP publicado con veredicto no bloqueante** — `APROBADO-CONDICIONAL-PENDING-ONBOARDING`— y acta con causas legibles. `readiness: READY_FOR_PUBLICATION` por sí solo no prueba nada: medido el 2026-09-19 convivieron READY, 13/13 gates verdes y el ZIP **suprimido**. Registrar también, **por proveedor**, cuál rama de LLM respondió realmente (`providers_used` de cada unidad, no el agregado), conforme a `L-ENT.9`: un proveedor configurado no es un proveedor ejercitado, y en corrida única la rama silenciada no tiene segunda oportunidad. Actualizar checklist (contador 1/1), dependencias, 09/10 con datos medidos y las observaciones que realmente existan — **sin cuota de lecciones nuevas**; ejecutar el cierre documental del contrato. Dejar a VERIFY la certificación; no marcar AC18 aquí.

## Comando largo único

```bash
# Única invocación externa autorizada del plan (runner preparado y congelado en H).
# El flag es obligatorio: run_once.py SIN argumentos imprime el uso y sale con EXIT 2, sin spawnear.
# Lanzar con notificación de término y esperar finalización real del PID.
./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py --spawn
```

El runner spawnea internamente, y una sola vez, el argv literal congelado en H — el campo `argv_congelado` de `evidence/…/FASE-H/preflight.json`, que es el que `verificar_preflight` compara: `main.py v4complete --url https://www.donalfonsohotel.com/ --nombre "Hotel Don Alfonso" --output output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18 --permission-mode auto`. ⟦La cita anterior de este prompt omitía `--permission-mode auto`; el flag si está en el literal congelado y en el argv que el runner lanza⟧. **Prohibido** ejecutar ese argv manualmente además del runner, ejecutarlo dos veces, añadir flags, usar force/deploy, desactivar el Tribunal o realizar una auditoría externa preliminar. Si H documentó una invocación de runner distinta en su cierre, usar la de H y registrar la diferencia; no inventar parámetros.

## Delegación viable

`delegate_task`/`Agent` solo para la corrida si comparte entorno y permisos, con notificación de término (`run_in_background` en el cliente actual) y brief que prohíba relanzar, editar código o tocar el control. El principal verifica PID, `run_control.json` y artefactos preservados antes de aceptar el resultado: un timeout o un resumen delegado no es evidencia. VERIFY no se delega y no ocurre en esta sesión.

## Reglas de honestidad

- Un bloqueo legítimo conserva su veredicto. No se altera producto, umbrales ni datos para alcanzar READY_FOR_PUBLICATION.
- **No todo `BLOQUEADO` es un bloqueo legítimo:** si el veredicto sale bloqueado por un hueco de serialización de la evidencia que **FASE-0/AC20** debía haber cerrado —un `details` vacío, un `findings` sin causa, un `package_evidence` ausente en la rama publish—, eso es **fallo del plan, no bloqueo del hotel**, y se reporta como tal con su dueño (FASE-0), sin presentarlo como resultado defendible de la corrida.
- `exit_code == 0` no equivale a entrega aprobada; la decisión la acreditan gates, acta y ZIP válido.
- Prohibido editar el warehouse, fechar datos a hoy, desactivar frescura o caer a defaults para consumir la corrida.
- No copiar `.env`, caches ni logs históricos crudos; no conservar un ZIP suprimido contra O1; no exportar documentos internos retenidos.
- Si la corrida falla por red, credenciales, datos insuficientes o un defecto nuevo: conservar el resultado, registrar causa y dueño, y pedir modificación de alcance en otra sesión. Nunca un segundo E2E implícito.

## Post-ejecución

Actualizar estado de este prompt, checklist (contador 1/1), dependencias, índice del plan, 09/10 y 00 con observaciones medidas; subsección E2E en CHANGELOG **bajo `## [Sin publicar]`**, no bajo número de versión —fechar una release es acto de RELEASE (`04-contrato-ejecucion.md` paso 3)— y nota en `docs/GUIA_TECNICA.md`. Sustituir variables por datos medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E2E --desc "REFACTOR-WHATSAPP-ENTREGA: única ejecución real Don Alfonso y evidencia preservada" --fecha "$FECHA_CIERRE" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

`--fecha` = fecha real de cierre; si el registro es tardío, `--nota` con el motivo. `log_phase_completion.py::parse_args` la declara obligatoria junto con `--fase` y `--desc` y la valida como fecha de calendario, así que `$FECHA_CIERRE` es variable a sustituir — el comando sin la bandera se niega en lugar de estampar la fecha del reloj. ⟦Puesta al día 2026-10-06: este bloque se escribió antes de esa obligatoriedad y rompía al ejecutarse tal cual; la regla canónica vive en `docs/CONTRIBUTING.md` y en el executor §4.5.1, y no se re-transcribe aquí⟧.

Confirmar REGISTRY sin GAP. No commit, push, tag, write-back ni release sin autorización expresa para esa acción.

**Derivados vencidos: un rojo del quick al cerrar puede no ser del cambio.** Si la fase añadió evidencia `.py` o editó documentos del plan, correr el fixer del derivado que cayó y **re-correr el quick**:

- `[8/13]` OpenCode References → `./venv/Scripts/python.exe scripts/validate_opencode_refs.py --fix`
- `[9/13]` Plan Citations → `./venv/Scripts/python.exe scripts/validate_plan_citations.py --update-baseline` (acto visible: lo hace quien documenta; no silencia un rojo)
- `[11/13]` Wiring → `./venv/Scripts/python.exe scripts/validate_wiring.py --write-report`
- `[13/13]` Packs → `./venv/Scripts/python.exe scripts/build_phase_briefing.py`

Las cuatro etiquetas son las que imprime el **modo rápido**; en el modo completo solo sus cinco checks exclusivos se etiquetan con denominador 18. El número lo imprime la corrida: no se copia a ningún documento.

## Presupuesto y checklist

Referencia **60 tool_use**; en esta fase el corte es **documental** (no hay commit de código propio): declararlo separado, sin fingir un corte de código y **sin tratar la ausencia de commit como un corte «no consumado»** — los cinco cortes se sostienen sin commit. Instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; sin transcript o con acceso denegado, **FUERA DE SERVICIO (R2.1)** y auto-reporte con su unidad.

- [x] Preflight verificado en disco antes del spawn y revalidado por el runner contra la fecha del día (b1-bis); cualquier rechazo dejó el contador en 0/1. **El rechazo ocurrió y fue de hash, no de reloj:** `DivergenciaDeHash` en el propio runner por la enmienda `6fd39c2`. Curado con re-emisión que movió solo 2 campos; `--preflight` quedó en EXIT 0 y la revalidación del spawn consignó `revalidacion_del_spawn` con edad 77.
- [x] Un solo proceso hijo, argv literal del maestro §5, sin flags añadidos ni comando manual adicional. `--spawn` una vez; `argv` de 11 piezas con `--permission-mode auto`; `argv_sha256 b5748891…`.
- [x] `run_control.json` acredita `attempts=1`, PID, timestamps, hashes y exit code real. `pid: 30576`, `estado: FINALIZADO`, `exit_code: 0`, 116 s, los 10 `source_hashes` y el snapshot de memoria. **Hueco declarado (S-E2E-8):** `preflight.sha256` queda `null`.
- [x] Evidencia saneada preservada antes del análisis; snapshot, inventario, reportes, acta y ZIP si existe. `inventario_post_corrida.json`: 70 archivos, 0 errores, 0 faltantes; ZIP `PAQUETE_PUBLICADO` con sha y 57 entradas. **Caveat (S-E2E-6):** la captura arrastra 4 formas `prefijo…sufijo` de claves impresas por `config_checker._check_env_variables`; no comitear sin decidir su saneado.
- [x] Resultado observado registrado aunque bloquee; sin remediación ni segunda corrida. No bloqueó: `APROBADO-CONDICIONAL-PENDING-ONBOARDING`, tier B+, 11 PASSED + 2 WARNING y 0 fallidos. Se declaran NO EJERCITADOS la medición IAO (la unidad crasheó, S-E2E-1) y la rama WhatsApp.
- [x] Cierre incremental completo; VERIFY queda para otra sesión. Registro con `log_phase_completion.py`, índice de lecciones y quick; AC18 **no** se marca en esta fase.
