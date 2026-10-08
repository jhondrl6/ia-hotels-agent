# FASE-A3 — Ruta con el plan archivado y la fuente de la era G (AC5, AC6)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-A3
**Objetivo:** gobernar por diente la resolución de rutas del `--upload` cuando el plan ya vive bajo `Archives/`, y
dictar la fuente que el registro no contable (`01a0bfc9-…`, era G) sin borrar nada.
**Dependencias:** FASE-A1 **y** FASE-A2 cerradas. AC6 tiene dependencia dura con A1: mientras la puerta de
vigencia corte `[VENCIDO]`, el bloque `DUPLICADO-VIGENTE` no se evalúa (los caminos anteriores terminan en
`continue`) — medido en la preparación, maestro §1.
**Complejidad:** MEDIA-ALTA. Aquí aparecen los primeros rojos **verdaderos** del check `[17/18]`.
**Skill:** `.agents/workflows/phased_project_executor.md`.
**Modo:** DIRECTO. **R3:** 4 tareas, 0 comandos largos. **Comandos remotos permitidos:** `qmind source list`
(censo) y `qmind source download` (verificación de promesa), con su racha contada y su crudo redactado.
**Prohibido:** `qmind source delete` y cualquier subida nueva (la de este plan es AC10, en RELEASE).

## Contexto

- **AC5, medido antes de diseñado.** `main()` compone una `--upload` relativa como `args.plans_dir / <argv>` sin
  exigir que exista, así que `--upload Archives/<PLAN>` **sí resuelve hoy** y `plan_dir.name` da la clave correcta
  del registro. Lo que no existe es el camino inverso: `--upload <PLAN>` a secas, tras el `git mv`, corta
  `[FAIL] Upload: el directorio no existe`. Y `cuerpo_del_plan()` ya prueba las dos raíces. **AC5 no construye esa
  capacidad: la fija por diente** y añade lo que falta — el rojo nombrado por su causa, no por red.
- **AC6, la fila huésped.** El notebook tiene tres fuentes del plan padre; la de la era G
  (`01a0bfc9-5f5a-783e-9492-16367bbff596`, `87b9b6664f945ac6…`, 39.422 B) nombra al plan y **no tiene entrada** en
  `.opencode/qmind-writeback/registro.json`. Con AC2 landed, el bloque `DUPLICADO-VIGENTE` la corta. La regla del
  mandato: **no se borra nada** — `source delete` es irreversible sobre contenido publicado y exige decisión
  escrita aparte. Las dos salidas están definidas en el maestro §2 DA-CIM.4 y la elegida por diseño es **dejar el rojo
  declarado con dueño**, salvo que el operador dé autorización literal para registrarla como `vigente-historica`.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| Preparación | ✅ 2026-10-08 |
| FASE-A1 | ⬜ Pendiente (requisito duro: `sha_cuerpo` y la puerta de vigencia) |
| FASE-A2 | ⬜ Pendiente (requisito: slug y `fuente_id`) |
| FASE-B, C, RELEASE | ⬜ Pendientes |

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-QW.4 | Un límite conocido y escrito no se cierra solo: necesita AC, dueño y disparador | AC6 se redacta con dueño escrito y disparador; la alternativa `vigente-historica` queda documentada con su condición, no como tarea silenciosa |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes | AC5: el cuerpo que no resuelve bajo la raíz publicada es abstención con ruta nombrada; AC6: la descarga que falla no dicta ausencia de fuente |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente | El censo puede responder 0 fuentes que nombren al plan y eso es un resultado, no un error; se publica con su población |
| L-ENT.14 | Una prueba de NO-existencia recortada por un `head` no prueba nada | El censo de `fetch_sources()` y el inventario de entradas del registro se publican completos, sin `head` ni tubería que recorte |
| L-V2.2 | Un verificador no apoya su conclusión en el artefacto de otro gate | El verde de esta fase no se certifica corriendo el check curado: se corre el modo completo y su crudo se archiva; la certificación de contenido es AC10 en RELEASE |
| L-V2.3 | Hay tests que pinean la **forma** del artefacto que vas a editar | Si esta fase necesita tocar `_check_qmind_writeback`, re-ata primero los dos dientes que leen la fuente del runner y solo entonces numera |
| L-T4A.5 | Un verde puede no alcanzar la rama | El diente de AC5 se ejercita con `--plans-dir` montado en `tmp_path` (raíz con y sin `Archives/`), no contra el árbol real del repo |

## Tareas

### Tarea 1 — PRE, censo y racha remota

Re-medir HEAD/status/quick; PRE de la selección de la familia. Correr `qmind source list` (censo del notebook
`01a04d98-b7bd-778c-8441-26fdc7e35f45`) y publicar: población total, fuentes que nombran al plan padre con su id,
título, `sha_metadata` y `fileSize`, y si están o no contables en el registro. **Sin `originUrl` ni `URI` en el
crudo.** Si el listado falla, registrar la racha (intentos, códigos) y cerrar AC6 en NO-EVALUABLE con dueño, sin
dictar ausencia.

### Tarea 2 — AC5: resolución de rutas fijada por diente

`--upload Archives/<PLAN>` publica dejando la clave del registro en `plan_dir.name` (sin prefijo); `--upload <PLAN>`
con el plan archivado corta `[FAIL]` **nombrando la ruta buscada**; `cuerpo_del_plan()` resuelve el cuerpo en las dos
raíces y su ausencia es NO-EVALUABLE, nunca VENCIDO. Todo se prueba con `--plans-dir` y `--registro` apuntando a un
montaje en `tmp_path`, sin tocar el registro real.

### Tarea 3 — AC6: la era G, declarada con dueño y sha

Dictado del censo más el dictamen del verificador. Sin autorización literal del operador, se cierra con la
**opción (b)**: el rojo queda impreso (id, título truncado legible, sha del censo) y el dueño escrito en
`dependencias-fases.md` y en `10-analisis` §Seguimientos, con el disparador (decisión de contenido publicado).
La **opción (a)** —registrarla como `vigente-historica` con su sha— solo se ejecuta si llega instrucción literal
para editar la contabilidad por una fuente ajena; entonces el rojo se retira **por contabilidad** y el censo de
fuentes vigentes del plan pasa de 2 a 1, declarando que no se borró nada.

### Tarea 4 — Dientes, contador y cierre

Mutantes (cada uno con restauración por sha256): quitar la segunda raíz de `cuerpo_del_plan()` convierte una
abstención honesta en `[VENCIDO]` falso; silenciar el bloque huésped hace desaparecer el rojo de AC6; y un
dictamen `VENCIDO` conviviendo con un `NO-EVALUABLE` debe seguir dando EXIT 1 con las dos líneas. Publicar el
**contador** heredado de A1 (entradas por cuerpo / por metadata+descarga / NO-EVALUABLE por migración / huéspedes)
y correr el modo completo archivando su crudo, declarando que este plan no se audita con el instrumento que acabó
de curar (L-V2.2).

## Tests Obligatorios

| Superficie | Criterio |
|---|---|
| `tests/test_validate_qmind_writeback_escritura.py` | los 23 + los de A1 + los de A2 + los de esta fase, sin aserción rebajada |
| Dientes AC5/AC6 | par rojo/verde archivado, restauración por sha, montaje en `tmp_path` |
| Modo completo con `--strict` en `[17/18]` | se corre y su crudo se archiva; el resultado esperado es **rojo verdadero** por AC6 si no hubo decisión, y eso se reporta como hallazgo con dueño, no como regresión |
| `run_all_validations.py --quick` | todos sus checks |

## Post-ejecución (OBLIGATORIO)

Conforme al contrato §cierre, sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A3 --fecha 2026-10-08 \
    --desc "CURA-INSTRUMENTOS-QMIND-S15: ruta con plan archivado y fuente de la era G declarada con dueño" \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] AC5 con sus dos rojos nombrados por causa (ruta no encontrada; abstención con raíz buscada) y su verde de clave `plan_dir.name`
- [ ] AC6 cerrada por una de sus dos vías **escrita en la evidencia**, con sha y dueño; si fue la (b), el rojo sigue imprimiéndose y ningún documento del plan lo describe como resuelto
- [ ] Nada fue borrado en el notebook; ninguna subida ejecutada; ningún enlace firmado persistido
- [ ] Los dientes de A1 y A2 siguen verdes; delta explicado por adiciones de ESTA fase
- [ ] Contador publicado y crudo del modo completo archivado con el estado de cada check
- [ ] Post-ejecución completo; quick verde; derivados regenerados con su escritor

## Restricciones

- Dependencia dura con A1: sin la puerta de vigencia landed, AC6 **no es evaluable** y la fase se detiene.
- Prohibido `qmind source delete`, prohibido re-subir, prohibido editar el registro a mano sin autorización literal.
- No tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow ni los hooks; no liberar versión.
- No iniciar FASE-B. Presupuesto 60 `tool_use` al corte autorizado; auto-reporte con unidad declarada.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-A3.md y el workflow canónico.

Ejecuta SOLO FASE-A3 del plan .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07, y solo si A1 y A2 cerraron.

OBJETIVO: gobernar por diente la ruta del --upload con el plan archivado y dictar la fuente de la era G sin borrar nada.

TAREAS: 1) PRE, censo del notebook y racha remota. 2) AC5 resolucion de rutas fijada por diente en tmp_path.
3) AC6 rojo declarado con dueño y sha, o registro como vigente-historica solo con autorizacion literal.
4) mutantes, contador publicado, modo completo con crudo y cierre.

CRITERIOS: el cuerpo ausente es NO-EVALUABLE y nunca VENCIDO, la fuente huesped corta DUPLICADO-VIGENTE con su id
y su sha, y el modo completo se archiva en vez de auditarse con el check recien curado.

RESTRICCIONES: sin source delete, sin subir, sin editar el registro a mano, sin tocar el plan padre, sin AGENTS ni
VERSION, sin commit salvo instruccion literal, sin iniciar B.

```
