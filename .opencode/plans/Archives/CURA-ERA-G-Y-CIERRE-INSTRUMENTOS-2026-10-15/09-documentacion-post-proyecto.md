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
| FASE-RELEASE-4.81.1 | 0 | — (la fase no escribe código ni tests; el delta R2.3 es 0: medido 5.334 en el árbol y 5.334 en `HEAD`) | 13/13 (venv canónico, `08-quick-cierre.txt`). El **primer** intento dio **12/13, EXIT 1**: el bump 4.81.1 vencía al `DOMAIN_PRIMER` y cortaba `Document Integration` (crudo `03-`) | Bump 4.81.0 → 4.81.1 (patch; DEC-1: las tres curas en una unidad). Nota de ronda **+13** atribuida contra **revisiones fijas** (crudo `02-`): `2e048e6` = 5.321 → `1f95e84` = **5.330** (+9: frescura 36→41 y write-back 59→63) → `2e4ba97` = **5.334** (+4 de FASE-C: write-back 63→67); en `AGENTS.md` se mueven la cabecera (5.334) y la fila `root test files` (1241→1254), con el cuadre de la tabla verificado por `validate_agents_md`. Modo completo **16/18** con `PYTHONUTF8=1` (crudo `04-`, EXIT 1): los dos rojos son **preexistentes y con dueño** — `Tests` (PydanticDeprecatedSince20 en `data_models/canonical_assessment.py`, el mismo rojo que `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/03-modo-completo-PYTHONUTF8-16-de-18.txt`) y `QMind Write-back` `NO-EVALUABLE` por la invocación sin `--strict` (`S-CIM-1`) sobre la racha de descargas flaqueantes. Write-back: **intento 1 EXIT 1** (`QMind network request failed`, crudo `05-`) y **intento 2 EXIT 0** (crudo `05b-`), con `--strict` dictando `[FRESCO]` sobre la fuente de este plan y `[CONTADOR] 9 vigente(s): 8 dictaminada(s) por cuerpo, 6 con fidelidad remota medida, 1 NO-EVALUABLE por migracion, 0 sin observacion local; 0 fuente(s) huesped(s) sin contabilidad … sobre 9/9` (crudo `06-`; su `EXIT 2` es la abstención estructural de la entrada `1.0`, declarada en FASE-C, no un rojo de este plan). Archivo: el `10-analisis` **se congeló con la subida**, así que su verificación se estampa aquí y en los crudos, no dentro del documento publicado |

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
| `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md`, `docs/cobertura-historia.md`, `AGENTS.md` §Cobertura | FASE-RELEASE | Bump 4.81.1 con su codename y fecha, la entrada del CHANGELOG con las **tres** curas y los shas de la tanda (`2e048e6`, `1f95e84`), la nota de cambios v4.81.1 y la nota de ronda con sus cifras medidas |
| `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, cabecera de `AGENTS.md` | FASE-RELEASE | Escritos por `sync_versions.py` desde `VERSION.yaml` (Result: All files in sync, EXIT 0) |
| `.agent/SYSTEM_STATUS.md`, `.agent/knowledge/DOMAIN_PRIMER.md` | FASE-RELEASE | `doctor.py --status` (1 skills, 1340 shadow logs, 4 sesiones) y `doctor.py --regenerate-domain-primer` (211 archivos Python, 396 clases, 25 módulos) porque el bump lo vencía; verificación después con `doctor.py --context` (All validations passed) |
| `.opencode/plans/Archives/CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15/` | FASE-RELEASE | `git mv` del plan completo a `Archives/` — **11 renombres** contado por `git`, cada uno con sus dos rutas en el pathspec del commit |
| `10-analisis`, `09`, `README`, `06-checklist`, `dependencias-fases.md` del plan | FASE-RELEASE | Post-Ejecución 1-5 del cierre y las referencias internas apuntando a `Archives/` |
| `.opencode/qmind-writeback/registro.json` y su instantánea | FASE-RELEASE | Entrada del write-back escrita **por el writer**: `fuente_id` `01a165aa-5e5d-7ba5-9171-06aa78b41e10`, sha256 `d35b81786511daaa2b4a557294f3ae34337b73835fe819fc3d8a6f852fdaa100`, verificada `[FRESCO]` por metadata del servidor y promesa por descarga+sha256 |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` + `.opencode/plans/plan_citations_baseline.json` | FASE-RELEASE | Derivados regenerados tras el archivado: índice **390 IDs** (dos pasadas: antes y después del `git mv`), `validate_opencode_refs.py --fix` con **5 referencias reparadas** en 4 archivos del plan y `validate_plan_citations.py --update-baseline` fijado a **81 archivos / 745 citas**. `refs_baseline.txt` **no** cambió en esta tanda (verificado en `git status`) |
| `docs/contributing/REGISTRY.md`, `docs/contributing/.last_doc_phase.json` | FASE-RELEASE | Registro de release con `log_phase_completion.py --fase FASE-RELEASE-4.81.1 --tests 0` (el total de fases lo imprime el escritor; sus filas de archivos se declaran como rutas) |
