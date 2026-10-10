# FASE-A1 — Las dos identidades del registro y la puerta de vigencia (AC1, AC2)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-A1
**Objetivo:** que `scripts/validate_qmind_writeback.py` pueda dictaminar vigencia de un plan cuyo cuerpo publicado
fue saneado, separando las dos preguntas: **el plan cambió** (cuerpo contra cuerpo) frente a **lo publicado casa
con el servidor** (instantánea contra `metadata.fileSha256` y descarga).
**Dependencias:** preparación cerrada 2026-10-08 contra HEAD `98c190e` (el HEAD de esta sesión es otro: re-medir).
**Complejidad:** ALTA — es el cambio de contrato del que dependen AC6 y AC10.
**Skill:** `.agents/workflows/phased_project_executor.md`.
**Modo:** DIRECTO con el agente principal. Delegable solo un inventario `read-only` (contrato §delegate_task).
**R3:** 4 tareas, 0 comandos largos externos. **Comando remoto:** ninguno en esta fase (no se sube nada).

## Contexto

El verificador compara `sha256(instantánea)` contra `sha256(cuerpo crudo del plan)` dentro de
`verificar_contenido()`. Como `--file` existe para subir una **copia saneada** y el writer no sanea, ningún plan
cuyo `10-analisis` lleve identidades sustituidas puede dar verde: el caso que el plan padre y su FASE-G obligan a
saneear. Medido en la preparación sobre el plan padre: cuerpo crudo `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e`
(124.280 B) contra publicado `1f0ee6e52f008e7413846039e244a8a242b472ba93e59bc933af2bb47e7286e0` (125.198 B), y el
crudo **sin editar** desde `83a6dc2` en adelante — o sea un falso VENCIDO estable, no un cierre desactualizado.

La decisión del operador está tomada y **no se reabre**: se cura por separación de las dos preguntas, no por un
`--sanear` en el writer. El que sanea sigue siendo quien documenta.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| Preparación (FASE-0) | ✅ Cerrada 2026-10-08, commiteada (`b536748` + sello `a19fa06`) y empujada hasta `origin/master`; L3 sin hallazgos |
| FASE-A1 | ✅ Cerrada y **commiteada** 2026-10-08 — commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`); la sesión abrió contra HEAD `d8a7d80` y el sha de su propio sello no se estampa aquí. AC1 y AC2 landed, PRE 23 passed → POST 31 passed, tres mutantes con su par intacto/mutado y restauración por sha256 |
| FASE-A2, A3, B, C, RELEASE | ⬜ Pendientes, en ese orden |

### Base técnica disponible

- `scripts/validate_qmind_writeback.py` (686 líneas leídas en la preparación): `verificar_contenido()`,
  `registrar_publicacion()`, `do_upload()`, `cuerpo_del_plan()`, `fetch_sources()`, `main()`.
- `tests/test_validate_qmind_writeback_escritura.py` — **23** funciones `def test_` (método canónico), medidas
  23/23 verdes en el PRE de la preparación (`E/FASE-0/pre_seleccion_apertura.txt`: 1 failed / 26 passed en la
  selección de dos archivos; el único rojo es de la familia S15 y no es de esta fase).
- `.opencode/qmind-writeback/registro.json` (2 entradas del padre, `fuente_id: ""`, sin `sha_cuerpo`) y
  `.opencode/qmind-writeback/instantaneas/` (1 archivo de datos + `README.md`).

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|---|---|---|
| L-QW.1 | Un verificador que comprueba la *clave* de una operación no detecta que el contenido detrás sea viejo | Es el AC2: la puerta deja de comparar instantánea contra crudo y pasa a cuerpo contra cuerpo. Su certificación es el diente contrario, no un verde |
| L-QW.3 | Un verde producido por la ausencia del instrumento es un rojo disfrazado | AC1 en la migración: entrada sin `sha_cuerpo` es NO-EVALUABLE por instrumento, nunca VENCIDO ni verde |
| L-PF10 | Una lista vacía válida no equivale a falta de fuente | AC1: `sha_cuerpo` ausente, `fuente_id: ""` y «no publicado» son tres estados publicados y distintos |
| L-T4A.5 | Un test verde puede no alcanzar la rama que dice certificar | Los mutantes se hacen sobre `verificar_contenido` y `registrar_publicacion` reales, no reimplementando el hueco en el test |
| L-V2.1 | Un test que solo mira qué check disparó queda verde por la rama equivocada | El diente contrario afirma la **línea de vigencia por cuerpo** y el mutante cae por esa aserción, no por la etiqueta |
| L-ENT.12 | El verde del verificador no probaba su propia cobertura | AC1/AC2 cierran con contador publicado: cuántas entradas por cuerpo, cuántas por metadata+descarga, cuántas NO-EVALUABLE por migración |
| L-G3 | Cambiar un contrato obliga a reescribir sus tests y su prosa en el mismo commit | `schema_version` 1.0 → 1.1; el `README.md` de `instantaneas/` describe la semántica que AC2 retira y viaja con esta fase |

## Tareas

### Tarea 1 — PRE y revalidación de anclajes

Re-medir HEAD, paridad y status; correr `run_all_validations.py --quick`; tomar PRE de la selección literal
`tests/test_validate_qmind_writeback_escritura.py` con intérprete declarado y `EXIT=$?` dentro del archivo.
Revalidar por símbolo los anclajes citados arriba y la firma del CLI (`--help`). Re-confirmar el par de shas del
padre midiendo en disco (no citando de memoria). Archivo: `E/FASE-A1/baseline-pre-post.md`,
`tests_baseline_pre.txt`.

**Criterios:** el PRE nombra selección, intérprete, exit code y sumas; los anclajes que difieren se corrigen en
el prompt y se consigna la deriva.

### Tarea 2 — AC1: `sha_cuerpo` en el registro, con migración honesta

`registrar_publicacion()` escribe en cada entrada nueva `sha_cuerpo` = sha256 del **cuerpo del plan** en el
momento de publicar (resuelto por `cuerpo_del_plan()`, no de la copia `--file`), y `cargar_registro` sube
`schema_version` a `1.1` tolerando entradas `1.0` sin el campo. **Prohibido** rellenar hacia atrás: calcular el
sha de hoy y escribirlo en una entrada vieja.

**Criterios:** legible en el artefacto — un humano que solo abra `.opencode/qmind-writeback/registro.json` ve
`sha_cuerpo` en la entrada nueva; las dos entradas del padre siguen intactas en sus claves y sin campo nuevo.

### Tarea 3 — AC2: la puerta de vigencia compara cuerpo contra cuerpo

En `verificar_contenido()`, el dictamen VENCIDO se decide por `sha(cuerpo actual) != sha_cuerpo publicado`; la
fidelidad remota sigue gobernada por `metadata.fileSha256` == sha(instantánea) y, si hubo descarga, la descarga
casa o corta `PROMESA-ROTA`. Se **conserva** el gate existente `e["sha256"] != sha_inst` (es lo que mantiene
verde el diente de instantánea editada) y el contrato D2 heredado: sin observación NO-EVALUABLE, la abstención
nunca es VENCIDO, el rojo manda sobre la abstención. Entradas sin `sha_cuerpo` → NO-EVALUABLE con motivo.

**Criterios:** los 23 dientes viejos verdes sin re-bajar aserción; el resumen publica el contador de AC1/AC2.

### Tarea 4 — Dientes y cierre

Dientes exigidos, cada uno con su mutante y restauración por sha256, ejecutados sobre el instrumento versionado:
1. **Contrario (el que prueba que el hueco existía):** subida de copia saneada con cuerpo crudo intacto → con el
   guard viejo cortaba `[VENCIDO]`, con la cura es vigente por cuerpo.
2. **Vigencia real:** cuerpo editado **después** de publicar → `[VENCIDO]`, y la línea nombra el cuerpo.
3. **Migración:** entrada sin `sha_cuerpo` → NO-EVALUABLE, nunca VENCIDO ni verde.
4. **No-colapso de estados (R2.9):** tres casos nombrados por su causa — sin hallazgos, ausente (con la ruta
   buscada), lector fallido (con el motivo).
5. **Rojo mandando sobre la abstención:** un dictamen VENCIDO y otro NO-EVALUABLE en la misma corrida → EXIT 1 y
   las dos líneas impresas.
6. Mutantes: apagar la comparación cuerpo-cuerpo rompe su grupo; apagar el gate de registro rompe el diente 3 de
   la familia vieja (`test_instanea_editada_sin_re_subir_es_vencido`).

Cierre incremental completo del contrato (paso 1 al 8), incluido el `README.md` de `instantaneas/` corregido por
su dueño humano y la regeneración del par del índice.

## Tests Obligatorios

| Superficie | Criterio de éxito |
|---|---|
| `tests/test_validate_qmind_writeback_escritura.py` | 23 funciones + los dientes nuevos, **sin re-bajar ninguna aserción vieja** |
| Dientes nuevos de AC1 y AC2 | cada uno con su mutante rojo y su restauración verificada por sha256 |
| `scripts/run_all_validations.py --quick` | todos sus checks (el número lo imprime la corrida) |
| Modo completo | **no** se corre aquí como certificación propia (L-V2.2); si la fase lo corre, su crudo se archiva y se declara que el `[17/18]` curado no se auditó a sí mismo |

## Post-ejecución (OBLIGATORIO)

1. Estados reales en `06-checklist-implementacion.md`, este prompt, `dependencias-fases.md` y `README.md`.
2. `09-documentacion-post-proyecto.md` §A/§B/§D/§E (D es la fuente del número) y
   `10-analisis-post-implementacion.md` (fila de A1, `L-CIM-n` nuevas o «sin lecciones nuevas», métricas
   referenciando 09 §D y la corrida, seguimientos, decisión DA-CIM.2 si se movió).
3. `00-lecciones-capitalizadas.md`: columna «Qué cambia» con lo realmente pasado en A1.
4. Subsección de fase bajo `## [Sin publicar]` en `CHANGELOG.md` y nota en `docs/GUIA_TECNICA.md`.
5. Registro propio, con medidas y sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A1 --fecha 2026-10-08 \
    --desc "CURA-INSTRUMENTOS-QMIND-S15: sha_cuerpo en el registro y puerta de vigencia cuerpo contra cuerpo" \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --archivos-nuevos "$ARCHIVOS_NUEVOS_MEDIDOS" \
    --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
```

6. Derivados con su escritor y como último paso: `build_lesson_index.py`, `validate_opencode_refs.py --fix` si
   entraron rutas nuevas, `validate_plan_citations.py --update-baseline` solo si añadieron citas (acto visible),
   `validate_wiring.py --write-report` solo si entran `.py` nuevos al árbol versionado,
   `doctor.py --regenerate-domain-primer` con mandato para escribirlo.
7. `validate_document_integration.py` + `run_all_validations.py --quick`.
8. Auto-reporte de presupuesto con unidad declarada y `git diff` revisado. **Sin commit salvo instrucción
   literal del operador en el chat de esta sesión.**

## Criterios de Completitud (CHECKLIST)

- [x] AC1 legible en `registro.json` con su clave `sha_cuerpo` y `schema_version` 1.1 (R2.4: sin clave legible, no hay ✅)
- [x] AC2 con los dos verdes nombrados (contrario y vigencia real) y su par de mutantes archivado
- [x] Los 23 dientes viejos verdes sin haber tocado una aserción (delta explicado por adiciones de ESTA fase, R2.3/R2.7)
- [x] Ninguna entrada del padre fue re-escrita ni rellenada hacia atrás
- [x] contador publicado por el verificador: entradas dictaminadas por cuerpo / por metadata+descarga / NO-EVALUABLE por migración
- [x] PRE/POST con resta comprobada y `EXIT=$?` dentro del archivo, esperando el PID real
- [x] Post-ejecución completo; quick verde; derivados regenerados con su escritor
- [x] El `README.md` de `instantaneas/` describe la semántica nueva y viaja en el mismo commit que la cura


**Nota de la sesión que la ejecutó (2026-10-08):** las ocho casillas se marcaron sobre el árbol de trabajo contra `d8a7d80`. La casilla del `README.md` de `instantaneas/` se cumple en contenido; su cláusula «viaja en el mismo commit que la cura» se cumplió cuando llegó la instrucción literal «Git Commit + L3 + Push»: el `README.md` entró en `63b944a`, el mismo commit que la cura.
## Restricciones

- No tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow ni los hooks. No liberar versión.
- No ejecutar ninguna subida, descarga ni borrado en QMind: AC10 es de RELEASE y AC4 de A2.
- No editar ningún documento del plan padre archivado ni su evidencia.
- No propagar identidades del cliente: fixtures con marcadores sintéticos.
- No re-numerar checks del runner sin re-atar antes los dos dientes que leen su fuente (contrato §tests).
- No iniciar FASE-A2. Presupuesto 60 `tool_use` al corte autorizado; instrumento canónico FUERA DE SERVICIO
  (R2.1), auto-reporte con unidad declarada.

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-A1.md y el workflow canónico.

Ejecuta SOLO FASE-A1 del plan .opencode/plans/Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07. No empieces A2.

OBJETIVO: que la puerta de vigencia del verificador de write-back compare cuerpo contra cuerpo y el registro
guarde las dos identidades, sin tocar el notebook.

TAREAS: 1) PRE y revalidacion de anclajes. 2) AC1 sha_cuerpo con schema 1.1 y migracion NO-EVALUABLE.
3) AC2 cuerpo contra cuerpo conservando el gate de registro y el contrato D2. 4) dientes con mutantes y cierre.

CRITERIOS: los 23 dientes viejos verdes sin rebajar asercion, el diente contrario que prueba que el hueco
existia, el caso de cuerpo editado despues de publicar, y el contador publicado por el verificador.

RESTRICCIONES: sin subida ni borrado remoto, sin editar el plan padre, sin AGENTS ni VERSION, sin commit salvo
instruccion literal en el chat, sin re-numerar checks del runner.

```
