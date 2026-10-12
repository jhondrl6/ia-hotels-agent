# Documentación Post-Proyecto — CURA-COSTURA-TRIBUNAL-2026-10-11

> Fuente canónica de métricas por fase (§D). CHANGELOG, GUIA_TECNICA y README **referencian** este archivo; no re-transcriben sus cifras. Cada fase completa sus filas al cerrar.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno previsto — el plan cura módulos existentes; completar si una fase crea uno) | | | |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Contrato de extracción con cuatro estados | `modules/quality_gates/tribunal/llm_extractor.py` | API checked con `OK_CON_PROMESAS` / `OK_SIN_PROMESAS` / `NO_EVALUABLE` / `FALLIDO` — fin del `[]` que colapsa estados. El wrapper transicional cierra en FASE-B (AC1 con AC15) | FASE-A |
| Utilidad compartida de parsing | `modules/quality_gates/tribunal/llm_extractor.py` | El mapeo de estados y el des-cercado de fences Markdown fuera de `LLMPromiseExtractor` (L-T4A.2), preparado para una tercera implementación | FASE-A |
| Cache versionada sin envenenamiento | `modules/quality_gates/tribunal/llm_extractor.py` | Clave (`VERSION_PROMPT`, sha del prompt compuesto, sha del texto, proveedor configurado — el modelo **no** entra); nunca persiste no-OK; escritura atómica; un hit no construye proveedor | FASE-A |
| Recibo de extracción | `modules/quality_gates/tribunal/llm_extractor.py` + `modules/providers/llm_provider.py` | Digest del texto y del prompt compuesto, versión, proveedor servido, modelo **pedido** y **firmado**, latencia, usage, digest respuesta cruda, estado y motivo. Vía **aditiva** en el proveedor (DEC-A3) | FASE-A |
| Detección de sobre-presentación sobre texto completo | `modules/quality_gates/tribunal/honesty_reviewer.py` | N5: el regex ya no depende de las citas elegidas por el LLM | FASE-B |
| Estado no-OK que llega al acta | `modules/quality_gates/tribunal/outcome.py` + `acta_writer.py` | AC17: un revisor con extracción `NO_EVALUABLE`/`FALLIDO` no puede proyectar `OK_NO_FINDINGS` ni aprobar para entrega; miembro nuevo de `ReviewerStatus` con `blocks_approval=True` y su etiqueta | FASE-B |
| Contrato de claves del finding de Bot 4 | `modules/quality_gates/tribunal/honesty_reviewer.py` | AC18: `finding_type` (y `clause`/`source_artifact`) en lugar de `"type"`, para que el acta y `derive_corrective_actions` nombren el hallazgo | FASE-B |
| Precedencia única de evidence_tier | `judge.py` + `honesty_reviewer.py` | N6: un símbolo compartido, una precedencia y un fallback; la rama manifest/escenarios se declara no certificable en régimen ZIP-only (AC11) | FASE-C |
| Reglas HARD y SOFT sin fallo silencioso | `data_validation/contradiction_engine.py` | N8: estado visible en los cuatro sitios de captura, en lugar de `print`. El cableado motor→gate es la deuda `S-CST-1`, no una feature de este plan | FASE-C |

## Sección D: Métricas Acumulativas (aquí vive el número)

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos FASE-A | **+46** funciones `def test_` (unidad canónica del repo: `grep -rE "^\s*def test_" tests --include=*.py \| wc -l`; 5207 → 5253, y en la selección del tribunal 207 → 253). La corrida `pytest tests/quality_gates/tribunal/` da 250 passed / 9 skipped / 0 failed sobre 259 recopilados | FASE-A |
| Tests nuevos FASE-B | **+27** funciones `def test_` (unidad canónica `grep -rE "^\s*def test_" tests --include=*.py \| wc -l`; 5253 → 5280, verificado restando en `evidence/…/FASE-B/07_baseline_delta_R2.3.txt`: 26 en el archivo nuevo `test_fase_b_consumidores_contrato.py` + 1 neto en `TestSinWrapperAC15`, que con 4 pruebas reemplaza las 3 del wrapper). Re-anclados, no cuentan: 12 llamadas al wrapper en `test_llm_extractor.py` y **10** lecturas de la clave del finding en 4 archivos de Bot 4 (la AC18 declaraba 8; medido 10, ver `10-analisis` §Lecciones). La corrida `pytest tests/quality_gates/tribunal/ -q` da **277 passed / 9 skipped / 0 failed** sobre 286 recopilados | FASE-B |
| Superficie de falso positivo medida (AC10) | Run de referencia (propuesta 2026-10-07, 14.690 caracteres): grupo cuantificador **10 literales / 10 matcheadas con el patrón curado / 2 emitidas** tras el filtro estructural (antes de la cura: 5 matcheadas, 3 de ellas totales financieros o de tabla). Grupo lenguaje: 1/1/1. Corpus de 6 propuestas: cuantificador 56/56/12, lenguaje 5/5/5. Manda `evidence/…/FASE-B/medicion-falso-positivo.md` | FASE-B |
| Tests nuevos FASE-C | (completar) | FASE-C |
| Coherence del run Don Alfonso | (completar desde el gate report de la corrida) | FASE-E2E |
| Proveedor servido en el run (del recibo) | (completar; nunca valores de credenciales) | FASE-E2E |
| Duración del run | (completar) | FASE-E2E |
| ACs certificados X/18 | (completar en FASE-VERIFY) | FASE-VERIFY |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/quality_gates/tribunal/llm_extractor.py` | Contrato de cuatro estados, utilidad compartida de parsing, cache versionada con guard único en `_save_to_cache`, escritura atómica, `cache_dir` anclado a la raíz, recibo por extracción, prompt sin self-confidence y con delimitadores. El wrapper `extract_verbal_promises` queda transicional (DEC-A1) | FASE-A |
| `modules/providers/llm_provider.py` | `ChatCompletionDetail` + `chat_completion_detailed` **aditivos** (DEC-A3): exponen `finish_reason`, modelo pedido/firmado y usage sin cambiar el retorno de `chat_completion` | FASE-A |
| `tests/quality_gates/tribunal/test_llm_extractor_contrato_cuatro_estados.py` | **Nuevo**, 46 funciones: estados por causa, truncamiento, clave versionada, hit sin proveedor, recibo, forma del prompt, wrapper | FASE-A |
| `tests/quality_gates/tribunal/test_llm_extractor.py`, `test_alignment_reviewer.py`, `test_honesty_reviewer.py`, `tests/test_p6r_full_flow_matrix.py` | Re-anclados al DTO sin `confidence` y al arnés de proveedor con la vía detallada (AC6); ninguno perdió aserciones de fondo | FASE-A |
| `.opencode/wiring_report.json` | Regenerado con `validate_wiring.py --write-report`: el archivo nuevo movió `cobertura.archivos_en_alcance` de 717 a 718 y el `--check` cortaba rojo | FASE-A |
| `modules/quality_gates/tribunal/alignment_reviewer.py` | Bot 2 consume `extract_checked` y publica `extraccion` (estado, motivo, promesas leídas, vía); **el default `extractor=None → LLMPromiseExtractor()` fuera** (un llamador offline ya no puede disparar una llamada real); el cruce inverso matriz→promesa sigue emitiendo `SIN_BRECHA_ASOCIADA` bajo no-OK; bajo no-OK la recomendación nunca es `APROBADO` | FASE-B |
| `modules/quality_gates/tribunal/honesty_reviewer.py` | Bot 4 ídem estados; `VERIFICATION_GROUP_*` y `VERIFICATION_SCAN_GROUPS` a nivel de módulo (AC10: la medición importa el patrón del código); frontera del `%` curada (`(?<!\d)100[ \t]*%`); filtro por fila de tabla y monto solo para el grupo de cuantificadores; sobre-presentación sobre **texto completo** (N5); findings con `finding_type`/`clause`/`source_artifact` (AC18) | FASE-B |
| `modules/quality_gates/tribunal/outcome.py` | `ReviewerStatus.INPUT_NOT_EVALUABLE` (`blocks_approval=True`), bloque `extraccion` escrito por `bloque_extraccion()` y leído por `collect_reviewer_reports`; `ReviewerReport.extraccion_estado/motivo` viajan al acta JSON solo cuando el revisor los declara (DEC-A2) | FASE-B |
| `modules/quality_gates/tribunal/acta_writer.py` | Etiqueta `⬜ insumo no evaluable` en `_STATUS_LABELS`: sin ella el MD imprimía el símbolo crudo por la reserva `.get(status, status)` | FASE-B |
| `modules/quality_gates/tribunal/llm_extractor.py` | **Borrado** del wrapper `extract_verbal_promises` del protocolo, de `LLMPromiseExtractor` y de `MockPromiseExtractor`, y del párrafo del docstring que lo documentaba (AC15; la API checked es la única vía — cierra AC1) | FASE-B |
| `tests/quality_gates/tribunal/test_fase_b_consumidores_contrato.py` | **Nuevo**, 26 funciones: estados por causa de Bot 2/Bot 4, cita omitida detectada, par frontera/tabla, AC17 atravesando `collect_reviewer_reports` + `_compute_verdict` con su control aprobable, AC18 proyectado en un acta generada, rama real `BLOQUEAR → verified_critical → ZIP suprimido`, y dos tests contra el **baseline real versionado** `evidence/FASE-I/corrida/hotelsalentoreal` | FASE-B |
| `tests/quality_gates/tribunal/test_llm_extractor.py`, `test_llm_extractor_contrato_cuatro_estados.py`, `test_alignment_reviewer.py`, `test_honesty_reviewer.py`, `test_honesty_reviewer_fidelidad_salida.py`, `test_honesty_reviewer_retro_reales.py`, `test_tribunal_propuesta_ubicacion.py`, `test_fase_e_snapshot_resolvedor.py` | Re-anclados a la API checked y al contrato de claves (AC18, 10 lecturas medidas); `TestWrapperTransicional` pasa a `TestSinWrapperAC15` con un diente de grep sobre `modules/`; `_ExtractoraVacia` implementa `extract_checked`; el test de artefacto ausente de Bot 2 usa una extractora que estalla si alguien la llama | FASE-B |
| `.opencode/wiring_report.json` | Republicado con `validate_wiring.py --write-report`: el archivo nuevo de tests movió `cobertura.archivos_en_alcance` de 718 a 719 y `--check` cortaba rojo | FASE-B |
| `output/<clientes_dir>/hotel_don_alfonso_onboarding.yaml` | **Creado** por `derivar_onboarding.py` (productor versionado de FASE-H): derivado del warehouse con `hotel.url` canónica; no se versiona (`output/*/` en `.gitignore`), su copia y `onboarding_provenance.json` quedan en `evidence/…/FASE-E2E/` | FASE-E2E |
| `data/hotel_observations/observations.json` | **NO se toca** (DEC-A4): la edición del campo `website` que estaba prevista queda revocada; su sha256 antes y después se publica en `pre-vuelo.md` y debe casar | FASE-E2E |
| Los 13 `.md` del plan | Auditoría aplicada (Preparación-2, 2026-10-11): rename `JEV-`→`CURA-`, AC13 partida con deuda `S-CST-1`, re-enunciados de AC1/AC4/AC5/AC10/AC11/AC13/AC14, AC17 y AC18 nuevas, FASE-B con orden T3→T2→T1→T4 y `outcome.py`/`acta_writer.py` obligatorios, T0 de E2E sustituido, L-T4A.2 capitalizada | Preparación-2 |
| `CHANGELOG.md` | Entrada 4.81.0 | FASE-RELEASE |
| `docs/GUIA_TECNICA.md` | Notas de Cambios v4.81.0 | FASE-RELEASE |
| `VERSION.yaml` + sincronizados por `sync_config.yaml` | 4.80.0 → 4.81.0 | FASE-RELEASE |
