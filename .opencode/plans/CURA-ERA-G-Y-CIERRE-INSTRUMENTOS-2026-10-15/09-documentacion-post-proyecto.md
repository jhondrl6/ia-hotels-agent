# Documentación Post-Proyecto — CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15

> **Acumulador canónico de métricas por fase** (lo consume FASE-RELEASE). Un conteo o resultado se registra **una vez** aquí (o en el informe/crudo que lo produce) y los demás documentos lo **referencian**; no se re-transcribe.

## Sección A: Módulos Nuevos

| Fase | Módulo | Función |
|------|--------|---------|
| FASE-A | — | Sin módulos nuevos: cierre documental, cero código |
| FASE-B | — | Sin módulos nuevos: medición y decisión, cero código |
| FASE-C | — | Sin módulos nuevos: la cura vive en `scripts/validate_qmind_writeback.py` (primitivo `registrar_historica()` + puerta CLI `--mark-historic`) |

## Sección B: Funcionalidades Nuevas

| Fase | Funcionalidad | Descripción |
|------|---------------|-------------|
| FASE-A | — | Sin funcionalidades nuevas: solo evidencia versionada y docs de cierre |
| FASE-B | — | Sin funcionalidades nuevas: censo de la deuda era-G y decisiones del Operador (informe) |
| FASE-C | Marcaje de fuentes históricas (era-G) | Primitivo `registrar_historica()` + puerta CLI `--mark-historic` de `scripts/validate_qmind_writeback.py`: registra como `reemplazada` una fuente ya publicada —sin instantánea ni `sha_cuerpo`, fuera del bucle de vigencia— con `fuente_id` + `sha_metadata` como evidencia; idempotente por título/`fuente_id`, sin red. Cierra a la vez `[DUPLICADO-VIGENTE]` y huéspedes (misma población, censo §3) |

## Sección D: Métricas Acumulativas

| Fase | Tests nuevos | Delta R2.3 (pre → post) | `--quick` | Notas |
|------|--------------|-------------------------|-----------|-------|
| FASE-A | 0 (sin código) | — | 13/13 (venv canónico) | Crudos: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/` (verde en `03b-quick-venv-canonico.txt`; el 9/13 del `.venv-wsl` 3.11 queda en `03-quick.txt` como contaminación de intérprete) |
| FASE-B | 0 (medición) | — | 13/13 (venv canónico, `04-quick-cierre.txt`) | Censo + crudos: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/` (rojo-antes `EXIT 1` en `01-`, intento 1 de 1 con 3 abstenciones de descarga declaradas) |
| FASE-C | 4 (3 dientes mínimos del censo §5.1: contabilidad, no-vigencia, idempotencia + 1 de la puerta CLI) | 63 → 67 (`67−63==4` ✓, resta ≠ 0; pares en `05-delta-pre-collect.txt` / `06-delta-post-collect.txt`) | 13/13 (venv canónico, `09-quick-cierre.txt`) | Crudos: `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/` — dientes rojo-antes (`01-`, 4 failed/63 passed contra HEAD) y verde (`02-`, 67 passed); mutante del guard de idempotencia (`03-`, solo el diente iii rojo) y restaurado (`04-`); marcaje por el writer (`07-`, 5 marcas + 1 re-marcaje idempotente; registro 9→14, 8 vigentes intactas); AC5 par rojo/verde: rojo `../FASE-B/01-writeback-rojo-antes.txt` (copia byte-exacta `00-writeback-rojo-antes-FASE-B.txt`) vs verde `08c-writeback-intento-3.txt` — racha dirigida de **3 intentos** (`08-`, `08b-`, `08c-`) por descargas flaqueantes; en los 3: 0 `[DUPLICADO-VIGENTE]` y `0 fuente(s) huesped(s)` sobre 8/8; el `NO-EVALUABLE` residual del EXIT 2 es la abstención estructural de la entrada `1.0` sin `sha_cuerpo` («no se rellena hacia atrás»), ajena a AC5 y ya presente bajo el rojo de FASE-B. Ingesta por título: `18/18 10-analisis archivados ingested` |
| FASE-RELEASE-4.81.1 | 0 | — | (lo imprime la corrida) | Cifras de cobertura de la ronda medidas con el comando canónico |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Fase | Cambio |
|---------|------|--------|
| `dependencias-fases.md`, README del plan, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` §2 | FASE-A | Post-Ejecución 1-6 del cierre (2026-10-21) |
| `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-A/` | FASE-A | Acta del cierre + 12 crudos de verificación de la sesión |
| `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/15-…` a `26-…` | FASE-A | 12 crudos de la tanda persistidos en `77dea21` |
| `docs/contributing/REGISTRY.md`, `.agent/SYSTEM_STATUS.md` | FASE-A | Registro de fase (`log_phase_completion.py --tests 0`) |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | FASE-A | Par regenerado como derivado de la post-ejecución (lo exige el `[6/8]` del hook) |
| `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-B/` | FASE-B | Censo `censo-era-g.md` + 4 crudos (rojo-antes, listado del notebook, respaldos byte-exactos, quick de cierre) |
| `dependencias-fases.md`, README del plan, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` §2 | FASE-B | Post-Ejecución 1-6 del censo y la decisión (2026-10-22) |
| `docs/contributing/REGISTRY.md`, `.agent/SYSTEM_STATUS.md` | FASE-B | Registro de fase (`log_phase_completion.py --fase FASE-B --fecha 2026-10-22 --tests 0`) |
| `scripts/validate_qmind_writeback.py` | FASE-C | Primitivo `registrar_historica()` + wiring CLI `--mark-historic` (con guardas de `--upload`/`--file`/datos faltantes/UUID) |
| `tests/test_validate_qmind_writeback_escritura.py` | FASE-C | 4 dientes del mecanismo era-G (sección nueva al final) |
| `.opencode/qmind-writeback/registro.json` | FASE-C | 5 entradas `reemplazada` escritas **por el writer** vía `--mark-historic` (9→14 entradas) |
| `01-plan-maestro.md` §5 | FASE-C | Fila `S-SEC-1` definida (absorción T4 de la determinación del gate de secretos) |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | FASE-C | Par regenerado (`build_lesson_index.py`) tras la definición de `S-SEC-1` |
| `dependencias-fases.md`, README del plan, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` §2 | FASE-C | Post-Ejecución 1-6 de la cura (2026-10-22) + backfill de la fila FASE-B que quedó ⬜ en `06-checklist` |
| `evidence/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/FASE-C/` | FASE-C | Par rojo/verde de AC5 + pares de delta + mutante + marcaje + quick |
| `docs/contributing/REGISTRY.md`, `.agent/knowledge/DOMAIN_PRIMER.md` | FASE-C | Registro de fase (`log_phase_completion.py --fase FASE-C --fecha 2026-10-22 --tests 4`; entrada verificada en el árbol: `## FASE-C - 2026-10-22 (CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15)`) + `DOMAIN_PRIMER` regenerado (211 archivos, 396 clases, 25 módulos). `.agent/SYSTEM_STATUS.md` **no** lo escribió el script en esta corrida (verificado: sin entrada FASE-C) — no se afirma su actualización |
