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
| FASE-A1 | ✅ **CERRADA, COMMITEADA Y EMPUJADA** 2026-10-08 — requisito duro landed: `sha_cuerpo` + schema 1.1 y la puerta de vigencia cuerpo contra cuerpo, con el gate de registro y el contrato D2 conservados. Banda empujada `d8a7d80..67b7e2f` (cura `63b944a`, sello `15f4fdd`, addenda `67b7e2f`; L3 **sin hallazgos** en las tres tandas). Crudos: `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/`. **Su consecuencia 1 —las entradas `1.0` salen por `continue` y nunca llegan al bloque huésped— quedó resuelta por DA-CIM.9 y es la subtarea 3b de este prompt** |
| FASE-A2 | ✅ **CERRADA, COMMITEADA Y EMPUJADA** 2026-10-08 — AC3 y AC4 landed: `slug_de_instantanea()` con huella reservada al final del nombre (el recorte cae sobre el prefijo, nunca sobre la firma) y `fuente_id_de_tabla()` + `verificar_por_censo()` + `publicar_en_registro()` en las dos ramas de `do_upload()`, sin re-subida. PRE 31 → POST 43 (resta 12) sin aserción rebajada; cinco mutantes con restauración por sha; cero escrituras remotas. Crudos: `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A2/`. La banda empujada y el tip vigente los imprime `git ls-remote origin refs/heads/master` |
| FASE-B, C, RELEASE | ⬜ Pendientes |

**Línea base de esta fase:** el tip que imprima `git ls-remote origin refs/heads/master` **al abrir la sesión**. Las
cifras de la tabla son históricas: la banda de A1 se cerró con la enmienda del 2026-10-08 y cualquier commit
posterior la mueve hacia adelante.

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

### Tarea 3b — AC6 por DA-CIM.9: gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9)

**Decisión del operador del 2026-10-08 (Caso A, vía a1), estampada en maestro §4 con su errata y en maestro §5
S-CIM-2.** Lo que A1 midió y declaró (`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/00-registro-de-fase.md`,
consecuencia 1): la guarda de migración termina en `continue`, así que las entradas `1.0` **no** recorren el bloque
`[DUPLICADO-VIGENTE]`. Con el registro como está hoy —solo dos entradas `1.0` del padre— el dictamen de la era G es
inalcanzable y `[17/18]` queda en NO-EVALUABLE sin fecha, no porque falte red sino porque falta el camino.

**Especificación (así se ejecuta, no se re-abre en la fase):**

- Extraer el bloque huésped a una función `_huespedes_sin_contabilidad(datos, fuentes, plan)` —recibe las fuentes
  del censo y el nombre del plan, devuelve las fuentes que nombran al plan sin entrada contable en el registro— y
  **llamarla también en la rama de migración, antes del `continue`**. El bloque deja de ser código suelto del final
  del bucle: lo llaman los dos caminos (entradas `1.1` y entradas `1.0`), y el `continue` de la abstención sigue
  donde estaba.
- **La capa D2 NO se levanta para entradas `1.0`.** Siguen en abstención con su motivo impreso; nunca un `[FRESCO]`
  sobre quien no tiene `sha_cuerpo`. Lo que se añade es la evaluación de la huésped, no una dictaminación de
  vigencia que el registro no puede sostener.
- **Dientes (los tres, con su población montada en `tmp_path`, cero escrituras remotas):**
  (i) huésped **roja** sobre una entrada `1.0` con `descargas == 0` —el rojo se imprime con id, título truncado
  legible y `sha_metadata` del censo, y el contador de descargas de la corrida sigue en 0;
  (ii) **rojo + abstención de migración en la misma corrida** —las dos líneas conviven y el EXIT es el del rojo;
  la abstención no tapa el hallazgo ni el hallazgo pinta de VENCIDO a la abstención (contrato D2, R2.9);
  (iii) `[CONTADOR]` **sigue cuadrando** con el rojo fuera de esa partición: `cuerpo + migracion + local == N`, la
  huésped se reporta aparte y no entra en la suma.
- **Mutante (R2.8):** apagar la llamada huésped en la rama de migración rompe el diente (i) y solo (i) — se ancla la
  aserción que pierde, no el token. Ejecutado sobre copia aislada, con el par copia-intacta-verde / mutada-rojo y
  la restauración verificada por sha256; el worktree vivo intacto antes y después.

**Fuera de esta subtarea, declarada:** la vía (a) del maestro §2 DA-CIM.4 (registrar la era G como
`vigente-historica`) y la vía a2 del mandato (re-publicar el `10-analisis` del padre como 1.1) siguen siendo
escrituras que requieren autorización literal propia; el operador no las dictó el 2026-10-08.

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
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A3 --fecha "$(date +%F)" \
    --desc "CURA-INSTRUMENTOS-QMIND-S15: ruta con plan archivado y fuente de la era G declarada con dueño" \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
```

> **Nota de preparación (2026-10-09):** la fecha se auto-evalúa (`$(date +%F)`) para que valga la real de la sesión de
> A3 y no la de preparación (contrato §Cierre.5). Los prompts hermanos (B, C, RELEASE) conservan el literal
> `2026-10-08` y se corrigen al prepararse cada uno.

## Criterios de Completitud (CHECKLIST)

- [x] AC5 con sus dos rojos nombrados por causa (ruta no encontrada; abstención con raíz buscada) y su verde de clave `plan_dir.name`
- [x] AC6 cerrada por una de sus dos vías **escrita en la evidencia**, con sha y dueño; si fue la (b), el rojo sigue imprimiéndose y ningún documento del plan lo describe como resuelto
- [x] DA-CIM.9 landed: `_huespedes_sin_contabilidad(datos, fuentes, plan)` llamada en la rama de migración antes del `continue`, con el diente (i) rojo sobre entrada `1.0` y `descargas == 0`, el diente (ii) rojo + abstención en la misma corrida, el diente (iii) `[CONTADOR]` cuadrando con la huésped fuera de la suma, y el mutante con restauración por sha256
- [x] Nada fue borrado en el notebook; ninguna subida ejecutada; ningún enlace firmado persistido
- [x] Los dientes de A1 y A2 siguen verdes; delta explicado por adiciones de ESTA fase
- [x] Contador publicado y crudo del modo completo archivado con el estado de cada check
- [x] Post-ejecución completo; quick verde; derivados regenerados con su escritor
    > *(el post-ejecución quedó en `listo para revisión`: el commit no se autorizó en el chat de esta sesión)* ⟦**Sello:** la autorización llegó después — commit `4fec5d0`, L3 con **0 hallazgos** sobre `b32a5ad..4fec5d0` y push con paridad **0**. La frase de arriba no se re-escribe: registra el instante del cierre.⟧

> **Sello de la sesión (2026-10-09).** AC5 landed con 5 dientes y AC6 cerrada por la **opción (b)**: el rojo
> queda impreso con su id, su título truncado y su `sha_metadata` del censo, y su dueño escrito está en
> `dependencias-fases.md` (fila 3) y en `10-analisis-post-implementacion.md` §Seguimientos. La vía (a)
> (`vigente-historica`) **no** se ejecutó: no llegó autorización literal para editar la contabilidad por una
> fuente ajena. Dos desviaciones declaradas con su medición: (1) el mutante de `cuerpo_del_plan()` no produce
> el `[VENCIDO]` falso que predecía el prompt — **0** líneas `[VENCIDO]` en la copia mutada; produce lo inverso
> (abstención donde había medición) y tumba 40 pruebas por una sola causa, así que el ancla del diente es la
> unidad del lector (`test_cuerpo_del_plan_resuelve_las_dos_raices_y_su_ausencia_no_es_ninguna`). (2) El modo
> completo murió en esta máquina al decodificar la salida de un subprocess con cp1252; se re-corrió con
> `PYTHONUTF8=1` y la variable queda estampada en el crudo (deuda S-CIM-10).


## Restricciones

- Dependencia dura con A1: sin la puerta de vigencia landed, AC6 **no es evaluable** y la fase se detiene.
- Prohibido `qmind source delete`, prohibido re-subir, prohibido editar el registro a mano sin autorización literal.
- No tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow ni los hooks; no liberar versión.
- No iniciar FASE-B. Presupuesto **90 `tool_use`** al corte autorizado (la referencia por fase y su base medida
  viven en `04-contrato-ejecucion.md` §R2); auto-reporte con unidad declarada.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-A3.md y el workflow canónico.

Ejecuta SOLO FASE-A3 del plan .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07, y solo si A1 y A2 cerraron.

OBJETIVO: gobernar por diente la ruta del --upload con el plan archivado y dictar la fuente de la era G sin borrar nada.

TAREAS: 1) PRE, censo del notebook y racha remota. 2) AC5 resolucion de rutas fijada por diente en tmp_path.
3) AC6 rojo declarado con dueño y sha, o registro como vigente-historica solo con autorizacion literal.
3b) gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9): extraer
_huespedes_sin_contabilidad(datos, fuentes, plan), llamarla en la rama de migracion antes del continue, sin
levantar D2 para entradas 1.0, con los tres dientes y su mutante.
4) mutantes, contador publicado, modo completo con crudo y cierre.

CRITERIOS: el cuerpo ausente es NO-EVALUABLE y nunca VENCIDO, la fuente huesped corta DUPLICADO-VIGENTE con su id
y su sha tambien cuando la entrada es 1.0 y la corrida no descarga nada, y el modo completo se archiva en vez de
auditarse con el check recien curado.

RESTRICCIONES: sin source delete, sin subir, sin editar el registro a mano, sin tocar el plan padre, sin AGENTS ni
VERSION, sin commit salvo instruccion literal, sin iniciar B.

INDICE: si el indice de esta maquina trae rutas staged ajenas (al 2026-10-09 son 13, del hermano
REFACTOR-WHATSAPP: briefing/ y una evidencia), NO se comitean ni se des-stagean; los commits van por pathspec y el
pre-vuelo de packs (hook [8/8]) se corre sobre el arbol del pathspec (HEAD + rutas propias), no sobre el indice
completo. Si su dueno ya las commiteo, esta linea no aplica.

```
