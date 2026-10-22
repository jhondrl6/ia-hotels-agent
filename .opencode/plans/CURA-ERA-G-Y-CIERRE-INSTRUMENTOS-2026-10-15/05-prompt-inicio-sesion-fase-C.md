# FASE-C — Cura de la deuda era-G

**ID**: FASE-C (plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15)
**Objetivo**: ejecutar el mecanismo que FASE-B decidió —marcar en el registro, borrar del notebook o declarar la excepción— hasta que `scripts/validate_qmind_writeback.py` salga **sin `[DUPLICADO-VIGENTE]`** y con **0 huéspedes sin contabilidad**, con el par rojo-antes/verde-después en evidencia. Es la única fase del plan que puede tocar código.
**Dependencias**: FASE-A ✅ y FASE-B ✅ (el censo y las decisiones son el insumo; sin ellos, ABORTAR).
**Duración estimada**: 1 sesión.
**Complejidad**: MEDIA — depende del mecanismo elegido: primitivo nuevo del writer con dientes (si la decisión exige código) o verificación + docs (si no).
**Skill**: `.agents/workflows/phased_project_executor.md` (workflow canónico).

## Contexto

`verificar_contenido()` dictamina sobre las entradas vigentes del registro y, por separado, `_huespedes_sin_contabilidad()` cuenta las fuentes del censo que nombran a su plan y no tienen contabilidad. La deuda era-G es que 5 fuentes publicadas antes de que existiera la marca de reemplazo quedaron «vigentes» para el instrumento, y 5 aparecen como huéspedes. La cura no es un cambio de criterio del instrumento (su criterio se validó y se dienteó en su plan): es **dar contabilidad** a esas fuentes por la vía que FASE-B decidió.

**Advertencia de diseño (L-CST-6)**: no existe hoy un camino para registrar una fuente **ya publicada** como reemplazada —`registrar_publicacion()` exige archivo e instantánea— así que si la decisión es «marcar», es probable que esta fase escriba un primitivo nuevo. Su forma exacta la fijó FASE-B; este prompt no la promete.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Preparación / FASE-A / FASE-B | ✅ según `dependencias-fases.md` — si alguna no está ✅, ABORTAR |
| **Decisiones de FASE-B** | la tabla de decisión por fuente (leerla ANTES de escribir nada; es la especificación) |

### Base Técnica Disponible

- `scripts/validate_qmind_writeback.py` (símbolos de la capa de contenido: `verificar_contenido`, `_huespedes_sin_contabilidad`, `_fuente_nombral`, `registrar_publicacion`, `cargar_registro`, `guardar_registro`, `entradas_del_plan`, `ESTADO_VIGENTE`, `ESTADO_REEMPLAZADA`).
- `tests/test_validate_qmind_writeback_escritura.py` (63 funciones; el doble `QmindFalso` responde los cuatro comandos y **cuenta** subidas y bajadas — los dientes nuevos se montan sobre él, sin red).
- `.opencode/qmind-writeback/registro.json` (schema 1.1) — **solo lo escribe** `registrar_publicacion()` o el primitivo nuevo que esta fase añada; nunca a mano (regla de la casa: la cura es un writer o un verificador, no el edit).
- El crudo del rojo-antes (FASE-B) y la CLI de QMind si la decisión es borrar.
- **Absorción pendiente (determinación del Operador 2026-10-22)**: esta fase registra además la deuda del gate de secretos — ver §Determinación post-FASE-B de `dependencias-fases.md` (fuente única) —; es documental y de **cero código para el gate**.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-QW.2 | Publicar con título distinto crea el duplicado; sin registro que marque la anterior, el duplicado es la vía fácil | T1: la marca se escribe **en el registro** (no se borra del notebook) cuando la decisión es (a); el diente exige el par rojo/verde del `[DUPLICADO-VIGENTE]` antes y después |
| D-QW-1 | La rama por defecto publica CONTEXT sin registrarlos | T3: si el censo halló una fuente `CONTEXT:` huésped, su contabilidad sigue el mismo mecanismo; si no la halló, se declara el 0 y no se toca esa rama (sigue diferida en §5) |
| D-QW-2 | Dos copias del detector divergen | T2: los dientes del primitivo prueban el instrumento con su predicado real, no con una copia local en el test |
| L-V.2 | Se certifica re-leyendo artefactos, no heredando notas | T2: el verde de AC5 es la **corrida real** del writer con su crudo, no la lectura del diff |

## Tareas

### Tarea 1 — Implementar el mecanismo decidido (AC5; solo si exige código)

**Objetivo**: dar contabilidad a las fuentes del censo por la vía decidida en FASE-B, con diente rojo-antes.

**Archivos afectados**:
- `scripts/validate_qmind_writeback.py` (solo si la decisión exige primitivo nuevo o política declarada)
- `tests/test_validate_qmind_writeback_escritura.py` (dientes nuevos)
- `.opencode/qmind-writeback/registro.json` (solo por el escritor, con su instantánea o su marca según el mecanismo)

**Criterios de aceptación**:
- [ ] **Diente rojo-antes (R2.8)**: el test nuevo que reproduce el hueco (la fuente histórica sin contabilidad) se escribe **antes** de la cura y se ejecuta contra el instrumento versionado en HEAD, con su rojo capturado como crudo. Sin el rojo no hay ✅.
- [ ] El primitivo nuevo (si aplica) se ejercita con el doble `QmindFalso` — sin red — y su nombre y firma coinciden con los que FASE-B especificó; si FASE-B especificó otra cosa, manda FASE-B y la diferencia se declara.
- [ ] Prohibido editar `registro.json` a mano: si el mecanismo necesita una entrada, la escribe el código.
- [ ] Si la decisión es (b) *borrar*: se ejecuta **solo** con la autorización por fuente ya registrada en FASE-B, se declara en el crudo el id borrado y qué queda sin respaldo, y no se borra ninguna fuente fuera de la tabla.
- [ ] Si la decisión es (c) *declarar*: la excepción vive donde FASE-B dijo, impresa en la salida del instrumento (una excepción silenciosa sería el defecto, no la cura).

### Tarea 2 — Verificación de AC5 con el instrumento real

**Objetivo**: el verde lo dicta el writer, no el diff.

**Criterios de aceptación**:
- [ ] Corrida de `python scripts/validate_qmind_writeback.py` en esta sesión: **0 líneas `[DUPLICADO-VIGENTE]`** y `0 fuente(s) huesped(s) sin contabilidad` en el `[CONTADOR]`; el crudo completo va a evidence junto al rojo-antes de FASE-B (AC5, par rojo/verde).
- [ ] La ingesta por título sigue verde: `N/N 10-analisis archivados ingested` con N = el de la corrida (no se fija aquí).
- [ ] Delta R2.3 con pares pre/post si hubo código (`suma_post − suma_pre == tests_nuevos`, resta 0 = baseline contaminado = no cierra).
- [ ] `run_all_validations.py --quick` verde.
- [ ] Si las descargas de `qmind` flaquean (rachas medidas), se aplica la racha dirigida y se declara el número de intentos; `NO-EVALUABLE` no es este verde.

### Tarea 3 — Documentación de fase

**Criterios de aceptación**:
- [ ] Post-Ejecución 1-6 completa, con `09` §D como fuente del número.
- [ ] `DOMAIN_PRIMER` regenerado (`python scripts/doctor.py --regenerate-domain-primer`) — es fase de implementación.
- [ ] `python scripts/log_phase_completion.py --fase FASE-C --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> --desc "<el mecanismo en una línea>" --archivos-mod "<rutas reales>" --tests <TESTS_NUEVOS> --check-manual-docs`
- [ ] `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/`: par rojo/verde de AC5, pares de delta, mutantes si hubo.

### Tarea 4 — Absorción documental de la determinación del gate de secretos

**Objetivo**: registrar la deuda del gate de secretos con ID propio, tal como determinó el Operador el 2026-10-22. **Cero código para el gate** (su cura es fase propia).

**Especificación**: los 5 pasos de §Determinación post-FASE-B de `dependencias-fases.md` (fuente única — no se re-transcriben aquí). Coste: ~5 tool calls.

**Criterios de aceptación**:
- [ ] La deuda queda **definida** (ID en primera celda de la fila, §5 del maestro) y no solo citada: `citados_sin_definicion` la deja de listar.
- [ ] El par `LECCIONES-INDEX.md` + `lecciones_index.json` regenerado y commiteado junto a la fila (`[6/8]` verde).
- [ ] Prohibido tocar los CONTEXT congelados (DEC-2/DEC-3), el `10-analisis` de CURA y cualquier doc registrado+publicado en el notebook; ningún código del gate.

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Diente del mecanismo (rojo antes, verde después) | `tests/test_validate_qmind_writeback_escritura.py` | Reproduce el hueco contra HEAD y cierra con la cura; sin red |
| Mutante del primitivo (si aplica) | ídem | Revertir el guard deja el diente rojo; restaurado, verde; ambas salidas en evidence |
| No-regresión de la batería del writer | ídem | Las funciones previas siguen verdes sin re-anclajes no declarados |

**Comando de validación**:
```bash
python -m pytest tests/test_validate_qmind_writeback_escritura.py -v
python scripts/validate_qmind_writeback.py
python scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** — ver template §5. Al cerrar:

1. `dependencias-fases.md`: FASE-C ✅ con fecha y notas.
2. README del plan: progreso.
3. `09-documentacion-post-proyecto.md`: A/B/D/E (el número vive aquí).
4. `10-analisis-post-implementacion.md`: Resumen + lecciones nuevas (o «sin lecciones nuevas») + seguimientos + decisiones.
5. `00-lecciones-capitalizadas.md` §2: efecto real de las filas.
6. `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/`: par rojo/verde + delta + mutantes.
7. Registro de fase con `log_phase_completion.py` (ver T3).

## Criterios de Completitud (CHECKLIST)

- [ ] AC5 legible: crudo del rojo-antes (FASE-B) y del verde-después (esta fase), con el `[CONTADOR]` de la corrida final
- [ ] Diente rojo-antes capturado antes de la cura (R2.8); mutante si hubo código
- [ ] Delta R2.3 verificado restando (si hubo código); `--quick` verde
- [ ] `DOMAIN_PRIMER` regenerado; `log_phase_completion.py` ejecutado
- [ ] Cinco cortes declarados; commit/push solo con autorización + pathspec
- [ ] Post-ejecución 1-7 completa
- [ ] Determinación del gate de secretos absorbida (T4): deuda definida con ID propio + par del índice; cero código para el gate

## Restricciones

- **Presupuesto (R2.1)**: ~40 tool calls; unidad: auto-reporte en `tool calls`; corte: **hasta listo para revisión**.
- **No tocar**: el `10-analisis` de CURA (DEC-2), los dos CONTEXT publicados (DEC-3), el criterio de `verificar_contenido()` (no se re-baja: se da contabilidad a las fuentes), la rama por defecto del writer (D-QW-1/D-QW-2 siguen diferidas en §5), y `temp/` (no borrar crudos).
- **Borrar en el notebook**: solo con la autorización por fuente registrada en FASE-B; si falta alguna, se para y se pregunta en texto plano.
- Citas por símbolo, nunca `archivo:línea` (R2.2).

## Prompt de Ejecución

```
Actúa como agente de implementación del plan CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15.

Ejecuta únicamente FASE-C del plan .opencode/plans/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/
Lee 01-plan-maestro.md (§1 AC5/AC6 y §4), 00-lecciones-capitalizadas.md (§2 y §4), dependencias-fases.md, 09-documentacion-post-proyecto.md (fuente de datos) y el workflow canónico.

OBJETIVO: ejecutar el mecanismo decidido en FASE-B hasta que validate_qmind_writeback.py salga sin [DUPLICADO-VIGENTE] y con 0 huéspedes sin contabilidad, con el par rojo/verde en evidencia.

CONTEXTO:
- La tabla de decisión de FASE-B es la especificación: leerla antes de escribir nada
- El rojo-antes está en evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/
- registrar_publicacion() exige archivo e instantánea: si la decisión es "marcar", probablemente haga falta un primitivo nuevo — con diente rojo-antes y mutante
- Borrar del notebook es irreversible y exige la autorización por fuente ya registrada; si falta, PARAR y preguntar

TAREAS:
1. T1 Diente rojo-antes + implementación del mecanismo (código solo si FASE-B lo especificó; registro escrito solo por el writer)
2. T2 Corrida real del writer: 0 [DUPLICADO-VIGENTE], 0 huéspedes; par rojo/verde en evidence; delta R2.3 si hubo código; quick verde
3. T3 Docs de fase + DOMAIN_PRIMER regenerado + log_phase_completion FASE-C
4. T4 Absorción documental de la determinación del gate de secretos: definir la deuda con ID propio en §5 del maestro + regenerar el par del índice (spec en dependencias-fases.md §Determinación post-FASE-B); cero código para el gate

CRITERIOS:
- AC5/AC6 legibles en los crudos; el verde lo dicta el instrumento, no el diff

VALIDACIONES:
- python -m pytest tests/test_validate_qmind_writeback_escritura.py -v
- python scripts/validate_qmind_writeback.py
- python scripts/run_all_validations.py --quick
- python scripts/log_phase_completion.py --fase FASE-C --fecha <FECHA_DE_CIERRE_DE_ESTA_FASE> (la fase se registra a sí misma)
```
