# FASE-B — Censo de la deuda era-G y decisión por fuente

**ID**: FASE-B (plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15)
**Objetivo**: producir el **censo** de las fuentes que mantienen el rojo `[DUPLICADO-VIGENTE]` y de las contadas como huéspedes sin contabilidad, y dejar **decisión escrita del Operador por fuente** con el mecanismo de la cura especificado. **No cura nada todavía. No borra nada. No toca código.**
**Dependencias**: FASE-A ✅ (el cierre documental no es estrictamente necesario para censar, pero la fase no arranca con el árbol sucio de la anterior).
**Duración estimada**: 1 sesión.
**Complejidad**: MEDIA — exige red (censo del notebook) y al Operador en el bucle para las decisiones; el resto es lectura y clasificación.
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

La corrida del 2026-10-15 de `scripts/validate_qmind_writeback.py` (crudo `19-writeback-post-cura.txt`, en `temp/` al concebir este plan) salió `EXIT 1` con **5 líneas `[DUPLICADO-VIGENTE]`** —fuentes del notebook que nombran a su plan y no están marcadas como reemplazadas— y un `[CONTADOR]` de 8 vigentes con **5 fuentes huéspedes sin contabilidad**. Es deuda de la era G: los planes `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (1 fuente) y `EVALUACION-JEV-TYPESAFE-2026-09-21` (4 fuentes) publicaron a lo largo de su vida más de una fuente vigente por plan, antes de que existiera el registro con marca de reemplazo.

El histórico de la deuda (recuperado de QMind, Q4 del Paso 0): dueño **Operador**, registrada como `S-CIM-2` en el cierre 4.80.0, con la vía «vigente-historica» sin ejecutar porque **requiere autorización literal** y porque borrar del notebook es irreversible. Esta fase produce lo que faltaba para decidir: el censo con cada fuente identificada, y la decisión por fuente.

**Lo que esta fase NO es**: no es la cura (FASE-C), no sube ni borra nada del notebook, y no edita el registro versionado. Su producto es un informe con decisiones.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación (Paso 0 + maestro + prompts) | ✅ Completada (2026-10-15) |
| FASE-A (cierre documental) | ✅ según `dependencias-fases.md` — si no está ✅, ABORTAR |

### Base Técnica Disponible

- `scripts/validate_qmind_writeback.py` (símbolos: `verificar_contenido`, `_huespedes_sin_contabilidad`, `_lineas_huesped`, `_fuente_nombral`, `fetch_sources`, `entradas_del_plan`, `is_ingested`, `cargar_registro`) — el instrumento que dicta el rojo, con su crudo.
- `.opencode/qmind-writeback/registro.json` (schema 1.1, 9 entradas al concebir el plan) y `.opencode/qmind-writeback/instantaneas/`.
- Notebook `iah-cli-lecciones`, id `01a04d98-b7bd-778c-8441-26fdc7e35f45` (68 fuentes al concebir el plan).
- La CLI de QMind (`qmind source list --nb <id> --all --format json`) para el censo de títulos, sha de metadata y fechas.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| D-QW-1 | La rama por defecto de `--upload` publica CONTEXT sin registrarlos: invisibles a las dos capas | T1: el censo debe declarar con qué predicado midió la población y si alguna fuente publicada pudo venir de esa rama (ninguna fuente `CONTEXT:` con plan asociado puede clasificarse sin esa comprobación) |
| D-QW-2 | Las dos copias del detector de autodeclaración divergen | T1: el censo no usa `scan_context_declarations()` como si fuera la población gobernada; si la cita, declara que es la copia estrecha del writer |
| L-QW.2 | Publicar con título distinto crea el duplicado: sin registro que marque la anterior, el duplicado es la vía fácil | T2: la tabla de decisión exige que la opción «marcar como reemplazada» diga **dónde** se marca (registro) y con qué evidencia, porque borrar no es la única vía y marcar preserva la contabilidad |

## Tareas

### Tarea 1 — Censo (AC3)

**Objetivo**: cada fuente que produce el rojo o el contador de huéspedes queda identificada y explicada.

**Criterios de aceptación**:
- [ ] Correr `python scripts/validate_qmind_writeback.py` **en esta sesión** y guardar el crudo completo (es el rojo-antes de AC5; sin este crudo la fase no cierra). Aviso medido: la corrida exige red y la descarga de `qmind` flaquea en rachas — si la corrida sale `NO-EVALUABLE` por descargas, se reintenta con criterio (racha dirigida) y se declara el número de intentos.
- [ ] Censo por el listado del notebook: para **cada** fuente de las 5 `[DUPLICADO-VIGENTE]` y de las 5 huéspedes, publicar `id`, título completo, `sha_metadata`, fecha de publicación si el listado la da, y si su título la ata a un plan (`is_ingested`/`_fuente_nombral`) o a un `CONTEXT:` (rama D-QW-1).
- [ ] Declarar la **relación entre las dos poblaciones**: cuántas fuentes están en ambas listas (el rojo y el contador pueden solaparse o no) — sin este cruce el censo no dice qué se cura con qué.
- [ ] Declarar por fuente **por qué no tiene contabilidad**: no existe entrada en el registro con su título / su entrada es `1.0` sin `sha_cuerpo` / la entrada existe pero su estado no es vigente / otra causa medida. La causa se lee del registro, no se supone.
- [ ] Comprobar y declarar si alguna de las 5 huéspedes es una fuente `CONTEXT:` (sería huella de `D-QW-1` en producción; hoy se cree que no — `scan_context_declarations()` = 0 medido el 2026-10-15 — pero el censo lo verifica por títulos, no por creencia).

### Tarea 2 — Decisión por fuente (AC4)

**Objetivo**: cada fila del censo tiene decisión escrita del Operador y mecanismo especificado.

**Criterios de aceptación**:
- [ ] Presentar al Operador la tabla del censo con **tres opciones por fuente**: (a) *marcar como reemplazada* — la fuente queda y el registro aprende su existencia histórica; (b) *borrar del notebook* — irreversible sobre contenido publicado; (c) *dejar con motivo declarado* — la fuente se declara huésped/excepción y el instrumento deja de señalarla como deuda.
- [ ] La respuesta del Operador se registra **en la sesión** (texto suyo) y se transcribe a la tabla de decisión con fecha. Ninguna fila queda «pendiente»: si alguna queda sin decisión, la fase cierra `⏳ INCOMPLETA` con checkpoint, no «completada con pendientes».
- [ ] El **mecanismo** de la cura queda especificado por opción elegida, con coste: (a) exige que el registro gane entradas para fuentes ya publicadas — medir si `registrar_publicacion()` puede hacerlo sin instantánea (hoy exige archivo) o si hace falta un primitivo nuevo (símbolo a nombre, coste en líneas y dientes); (b) exige `qmind source delete` por id (irreversible; declarar qué queda sin respaldo); (c) exige la política de excepción declarada (dónde vive, quién la lee).
- [ ] **Prohibido prometer el mecanismo sin medirlo** (L-CST-6): si la opción elegida exige código, FASE-B declara la firma propuesta y FASE-C la escribe con su diente; si no exige código, se declara «cero líneas» explícitamente.

### Tarea 3 — Informe y actualización documental

**Objetivo**: el censo y las decisiones son el entregable versionable de la fase.

**Criterios de aceptación**:
- [ ] `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/censo-era-g.md`: censo + cruce de poblaciones + tabla de decisiones con fecha y mecanismo + los crudos de la corrida.
- [ ] Si la decisión exige código, `dependencias-fases.md` de este plan se actualiza con lo que FASE-C editará exactamente (archivo/símbolo); si no, se declara que FASE-C queda de verificación y docs.
- [ ] Post-Ejecución 1-6 completa + registro de fase con `log_phase_completion.py --fase FASE-B --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> --tests 0`.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| (sin tests nuevos) | — | Fase de medición y decisión; su producto es el informe con el crudo del rojo-antes |

**Comando de validación**:
```bash
python scripts/validate_qmind_writeback.py          # crudo del rojo-antes (AC5)
python scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** — ver template §5. Al cerrar:

1. `dependencias-fases.md`: FASE-B ✅ con fecha y la nota de lo que FASE-C editará (o «cero código»).
2. README del plan: progreso; métricas por referencia al censo.
3. `09-documentacion-post-proyecto.md`: secciones A/B/D/E.
4. `10-analisis-post-implementacion.md`: fila de Resumen + decisiones tomadas en voz alta (las del Operador) + seguimientos.
5. `00-lecciones-capitalizadas.md` §2: anotar el efecto real de las tres filas.
6. `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/`: censo + crudos.
7. Registro de fase (T4 del prompt de FASE-A como modelo): `log_phase_completion.py --fase FASE-B --tests 0`.

## Criterios de Completitud (CHECKLIST)

- [ ] AC3 y AC4 legibles en el censo y en la tabla de decisiones (con la respuesta del Operador registrada en la sesión)
- [ ] El crudo del rojo-antes guardado (insumo de AC5)
- [ ] Ninguna fila del censo sin decisión (si alguna queda abierta: `⏳ INCOMPLETA`, no ✅)
- [ ] `log_phase_completion.py` ejecutado; cinco cortes declarados
- [ ] Post-ejecución 1-7 completa

## Restricciones

- **Presupuesto (R2.1)**: ~35 tool calls; unidad: auto-reporte en `tool calls`; corte: **hasta listo para revisión**.
- **No tocar**: el notebook (ninguna subida ni borrado), el registro versionado, el `10-analisis` de CURA (DEC-2), los CONTEXT publicados (DEC-3), ningún código.
- **Borrar es decisión del Operador, escrita** (DEC-4 y maestro §4 del writer): este prompt no borra nada ni con autorización implícita; la autorización es por fuente y en la sesión.
- Citas por símbolo, nunca `archivo:línea` (R2.2).

## Prompt de Ejecución

```
Actúa como agente de medición y decisión del plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15.

Ejecuta únicamente FASE-B del plan .opencode/plans/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/
Lee 01-plan-maestro.md (§1 AC3/AC4 y §4), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md, 09-documentacion-post-proyecto.md (fuente de datos) y el workflow canónico.

OBJETIVO: censar las fuentes de la deuda era-G (5 en [DUPLICADO-VIGENTE], 5 huéspedes sin contabilidad) y dejar decisión escrita del Operador por fuente con el mecanismo especificado.

CONTEXTO:
- El rojo se mide con scripts/validate_qmind_writeback.py (EXIT 1, crudo obligatorio de esta sesión)
- Notebook iah-cli-lecciones (01a04d98-b7bd-778c-8441-26fdc7e35f45), 68 fuentes al concebir el plan
- Dueño de la deuda: Operador. Borrar del notebook es irreversible y exige su decisión escrita POR FUENTE
- Esta fase no cura, no borra y no edita el registro

TAREAS:
1. T1 Censo: corrida del writer en esta sesión + listado del notebook; por fuente id/título/sha/fecha, causa de falta de contabilidad, y el cruce entre las dos poblaciones
2. T2 Decisión por fuente (a marcar / b borrar / c declarar) con la respuesta del Operador registrada en la sesión, y mecanismo especificado con su coste (primitivo nuevo del writer o cero líneas)
3. T3 Informe en evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/ + actualización de dependencias-fases.md si hay código + log_phase_completion FASE-B

CRITERIOS:
- AC3/AC4 legibles; ninguna fila sin decisión; el mecanismo no se promete sin medirlo (L-CST-6)

VALIDACIONES:
- python scripts/validate_qmind_writeback.py
- python scripts/run_all_validations.py --quick
- python scripts/log_phase_completion.py --fase FASE-B --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> (la fase se registra a sí misma)
```
