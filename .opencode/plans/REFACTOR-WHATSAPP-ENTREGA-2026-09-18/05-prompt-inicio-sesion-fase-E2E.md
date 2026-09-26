# FASE-E2E — Única ejecución real para Hotel Don Alfonso

**Estado:** PENDIENTE. **Dependencia inmediata:** FASE-H completa con preflight favorable (`attempts=0`, hashes conformes, identidad y frescura aceptadas, revocación acreditada o pendiente registrado).
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

1. **Preflight real y autorización de spawn.** Verificar en disco: cierre de H **y cierre de FASE-0 con AC20 verde** — sin esa serialización el techo alcanzable ya está medido y consumiría el único intento—, `run_control.json` con `attempts=0`, hashes de código/runner/input conformes al preflight, YAML derivado y `onboarding_provenance.json` vigentes, las tres identidades fijadas por H (`hotel_id` de la URL, nombre del paquete, `canonical_url`) en lugar de una sola, output aislado del plan, permisos y entorno (`./venv/Scripts/python.exe`), red y credenciales disponibles sin imprimirlas. Verificar además los tres items de aislamiento que H debe haber dejado escritos: el **snapshot previo de `.agent/memory`**, la **rama que tomó `_load_latest_onboarding_data`** (YAML derivado / fallback de observations / `Using defaults`) y el valor efectivo de **`--permission-mode`** (default `auto`; con `chat` la corrida sigue con `audit_result=None` y no es la corrida que el plan quiere certificar). Registrar si `find_latest_analysis` encontró o no un análisis previo reutilizable para la URL canónica: si lo hay, la corrida no audita de cero y eso debe constar antes del spawn. Anotar el resultado del preflight en evidencia de E2E. **Cualquier rechazo detiene la fase sin spawn.**
2. **Corrida única y preservación.** Invocar el runner una sola vez (comando siguiente), con notificación de término y vigilancia del PID hasta finalización real. No relanzar ante timeout, pérdida de conexión del delegado ni fallo: verificar estado del PID y cerrar con checkpoint. Al terminar —exitoso, fallido o bloqueado— preservar de inmediato snapshot saneado, exit code, argv, timestamps, hashes, inventario, reportes, acta y ZIP publicado si existe. El **argv se registra literal y verbatim** (tal como lo construyó el runner, sin reescribirlo ni normalizarlo), porque es la única prueba de qué rama de permisos y de input corrió realmente. Registrar consumo **1/1** desde la creación del proceso. **La evidencia debe declarar por escrito por qué esta corrida no es una repetición de `output/TAREA7-2026-09-19/`** —mismo hotel, misma URL, ya archivada y usada como baseline medido del plan—: la ruta viva no ejercita la rama WhatsApp del plan (sin pain de WhatsApp, `whatsapp_button` fuera del plan, check `whatsapp_verified` en verde vacuo), así que el valor de la nueva corrida está en la cadena de entrega y en la serialización cambiada que aporta FASE-0, **no** en los AC de WhatsApp.
3. **Análisis preliminar y cierre.** Registrar el resultado observado sin remediarlo: veredicto del Tribunal, gates, ZIP publicado o suprimido, causa de bloqueo legítima si la hay y divergencias frente a lo esperado. **La expectación ya no es "READY":** el resultado esperado de esta fase es un **ZIP publicado con veredicto no bloqueante** — `APROBADO-CONDICIONAL-PENDING-ONBOARDING`— y acta con causas legibles. `readiness: READY_FOR_PUBLICATION` por sí solo no prueba nada: medido el 2026-09-19 convivieron READY, 13/13 gates verdes y el ZIP **suprimido**. Registrar también, **por proveedor**, cuál rama de LLM respondió realmente (`providers_used` de cada unidad, no el agregado), conforme a `L-ENT.9`: un proveedor configurado no es un proveedor ejercitado, y en corrida única la rama silenciada no tiene segunda oportunidad. Actualizar checklist (contador 1/1), dependencias, 09/10 con datos medidos y las observaciones que realmente existan — **sin cuota de lecciones nuevas**; ejecutar el cierre documental del contrato. Dejar a VERIFY la certificación; no marcar AC18 aquí.

## Comando largo único

```bash
# Única invocación externa autorizada del plan (runner preparado y congelado en H).
# Lanzar con notificación de término y esperar finalización real del PID.
./venv/Scripts/python.exe evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-H/run_once.py
```

El runner spawnea internamente, y una sola vez, el argv literal del maestro §5 (`main.py v4complete --url https://www.donalfonsohotel.com/ --nombre "Hotel Don Alfonso" --output output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18`). **Prohibido** ejecutar ese argv manualmente además del runner, ejecutarlo dos veces, añadir flags, usar force/deploy, desactivar el Tribunal o realizar una auditoría externa preliminar. Si H documentó una invocación de runner distinta en su cierre, usar la de H y registrar la diferencia; no inventar parámetros.

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

Actualizar estado de este prompt, checklist (contador 1/1), dependencias, índice del plan, 09/10 y 00 con observaciones medidas; subsección E2E en CHANGELOG bajo versión vigente y nota en `docs/GUIA_TECNICA.md`. Sustituir variables por datos medidos; registro propio sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-E2E --desc "REFACTOR-WHATSAPP-ENTREGA: única ejecución real Don Alfonso y evidencia preservada" --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

Confirmar REGISTRY sin GAP. No commit, push, tag, write-back ni release sin autorización expresa para esa acción.

## Presupuesto y checklist

Referencia **60 tool_use**; en esta fase el corte es **documental** (no hay commit de código propio): declararlo separado, sin fingir un corte de código y **sin tratar la ausencia de commit como un corte «no consumado»** — los cinco cortes se sostienen sin commit. Instrumento `evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`; sin transcript o con acceso denegado, **FUERA DE SERVICIO (R2.1)** y auto-reporte con su unidad.

- [ ] Preflight verificado en disco antes del spawn; cualquier rechazo dejó el contador en 0/1.
- [ ] Un solo proceso hijo, argv literal del maestro §5, sin flags añadidos ni comando manual adicional.
- [ ] `run_control.json` acredita `attempts=1`, PID, timestamps, hashes y exit code real.
- [ ] Evidencia saneada preservada antes del análisis; snapshot, inventario, reportes, acta y ZIP si existe.
- [ ] Resultado observado registrado aunque bloquee; sin remediación ni segunda corrida.
- [ ] Cierre incremental completo; VERIFY queda para otra sesión.
