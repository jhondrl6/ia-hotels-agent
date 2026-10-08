# Documentación post-proyecto — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

Acumulador canónico de métricas por fase. **Este archivo es la fuente del número**: README, `10-analisis` y el
CHANGELOG lo **referencian**, no lo re-transcriben (executor, proceso común del bloque B). Creado en la preparación
con estructura vacía; cada fase llena sus filas al cerrar, con lo que midió, no con lo que esperaba.

Unidades declaradas: «funciones `def test_`» se cuenta con el método canónico del repo
(`grep -cE "^\s*def test_" <archivo>`), «casos collectados» con pytest, y **no son comparables** entre sí.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| — (ningún módulo nuevo; el plan cura instrumentos existentes) | | | |

## Sección B: Funcionalidades nuevas

| Feature | Módulo | Descripción | Fase |
|---|---|---|---|
| Identidad de cuerpo en el registro de publicaciones (`sha_cuerpo`, schema 1.1) | `scripts/validate_qmind_writeback.py` | Separa «el plan cambió» de «lo publicado casa con el servidor»; migración sin back-fill | ⬜ A1 (futura) |
| Puerta de vigencia cuerpo contra cuerpo | `scripts/validate_qmind_writeback.py` | `verificar_contenido()` dicta VENCIDO solo contra `sha_cuerpo`; conserva el gate de registro y el contrato D2 | ⬜ A1 (futura) |
| Slug de instantánea sin colisión | `scripts/validate_qmind_writeback.py` | Dos títulos con prefijo común ya no pisan el mismo byte-exacto | ⬜ A2 (futura) |
| `fuente_id` capturado de la tabla del CLI | `scripts/validate_qmind_writeback.py` | Parseo `Key: value` en las dos ramas de `do_upload()`; ante fallo, censo y no re-subida | ⬜ A2 (futura) |
| Rutas con el plan archivado fijadas por diente | `scripts/validate_qmind_writeback.py` | `Archives/<PLAN>` publica con clave `plan_dir.name`; `cuerpo_del_plan()` resuelve dos raíces | ⬜ A3 (futura) |
| Dictamen de la fuente de la era G | notebook `iah-cli-lecciones` + registro | `[DUPLICADO-VIGENTE]` con id, título y sha, declarado con dueño; nada borrado | ⬜ A3 (futura) |
| Control S15 estabilizado con diente intacto | `tests/test_build_lesson_index_s15_fecha_versionada.py` | La divergencia esperada queda gobernada sin re-anclar el control ni debilitar la aserción | ⬜ B (futura) |
| Cura de clasificación en el generador (condicional) | `scripts/build_lesson_index.py` | Solo si AC7 la exige; con su mutación y sus baterías | ⬜ C (condicional) |

## Sección D: Métricas acumulativas — **aquí vive el número**

| Métrica | Valor | Unidad e instrumento | Fase |
|---|---|---|---|
| Funciones `def test_` en `tests/test_validate_qmind_writeback_escritura.py` | 23 | `grep -cE "^\s*def test_"` sobre el archivo — **medido 2026-10-08 en la preparación** (línea base PRE, no producto del plan) | Preparación |
| Funciones `def test_` en `tests/test_build_lesson_index_s15_fecha_versionada.py` | 4 | idem — medido 2026-10-08 | Preparación |
| Funciones `def test_` en la familia del índice (16 + 36 hermanas) | 52 | idem sobre `tests/test_build_lesson_index.py` y `tests/test_verify_qmind_context_freshness.py` — medido 2026-10-08 | Preparación |
| Cases de la selección PRE de apertura | 1 failed / 26 passed (27 collectados) | pytest 9.0.2 con Python 3.13.3 del sistema; crudo en `E/FASE-0/pre_seleccion_apertura.txt`, EXIT=1 | Preparación |
| Checks del quick de apertura | todos verdes, con `EXIT=0` | `python scripts/run_all_validations.py --quick`; **el número lo imprime la corrida**, no se fija aquí — crudo `E/FASE-0/quick_apertura.txt` | Preparación |
| IDs definidos en el índice del corpus | 348 | salida de `build_lesson_index.py --check`, medido 2026-10-08 | Preparación |
| Distribución de fuentes de fecha del índice | 337 `nombre` / 11 `commit` / 0 `SIN-FUENTE` | línea `[fechas]` del writer; la FASE-B/C la re-mide | Preparación |
| Tests nuevos de cada fase | ⬜ pendiente | lo imprime su POST | A1, A2, A3, B, C |
| Checks del modo completo al cerrar | ⬜ pendiente | `run_all_validations.py` sin `--quick`, crudo archivado | RELEASE |
| Presupuesto `tool_use` por fase | ⬜ pendiente | **auto-reporte con unidad declarada** (instrumento canónico FUERA DE SERVICIO, R2.1) | todas |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/**` | Catorce documentos del plan creados en la preparación: ocho de gestión (00, 01, 04, dependencias, 06, 09, 10, README) y seis prompts de fase | Preparación |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/**` | Crudos de apertura (quick y selección PRE) y registro de fase | Preparación |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | Regenerados **con su escritor** como último paso de la preparación (esta sesión añadió `.md` que nombran IDs) | Preparación |
| `CHANGELOG.md` | Subsección de fase bajo `## [Sin publicar]` en cada fase; encabezado de versión solo en RELEASE | todas |
| `docs/GUIA_TECNICA.md` | Nota técnica por fase | todas |
| `docs/contributing/REGISTRY.md` | Una entrada por fase, escrita **por esa fase** con `log_phase_completion.py` | todas |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Regenerado con `doctor.py --regenerate-domain-primer` al cerrar fases de implementación, si la fase tiene mandato para escribirlo; verificado con `--context` en RELEASE | A1, A2, A3, B, C, RELEASE |
| `.opencode/qmind-writeback/instantaneas/README.md` | Prosa humana del directorio: describe la comparación que AC2 retira y el esquema de nombres que AC3 cambia | A1, A2 |
| `scripts/validate_qmind_writeback.py` | El instrumento curado | A1, A2, A3 |
| `tests/test_validate_qmind_writeback_escritura.py` | Dientes aditivos por AC | A1, A2, A3 |
| `tests/test_build_lesson_index_s15_fecha_versionada.py` | Cura del control | B |
| `scripts/build_lesson_index.py` | Solo si AC9 lo exige | C |
| `VERSION.yaml` | **No** en fases intermedias | RELEASE con mandato |
