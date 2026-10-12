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
| Tests nuevos FASE-B | (completar) | FASE-B |
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
| `output/<clientes_dir>/hotel_don_alfonso_onboarding.yaml` | **Creado** por `derivar_onboarding.py` (productor versionado de FASE-H): derivado del warehouse con `hotel.url` canónica; no se versiona (`output/*/` en `.gitignore`), su copia y `onboarding_provenance.json` quedan en `evidence/…/FASE-E2E/` | FASE-E2E |
| `data/hotel_observations/observations.json` | **NO se toca** (DEC-A4): la edición del campo `website` que estaba prevista queda revocada; su sha256 antes y después se publica en `pre-vuelo.md` y debe casar | FASE-E2E |
| Los 13 `.md` del plan | Auditoría aplicada (Preparación-2, 2026-10-11): rename `JEV-`→`CURA-`, AC13 partida con deuda `S-CST-1`, re-enunciados de AC1/AC4/AC5/AC10/AC11/AC13/AC14, AC17 y AC18 nuevas, FASE-B con orden T3→T2→T1→T4 y `outcome.py`/`acta_writer.py` obligatorios, T0 de E2E sustituido, L-T4A.2 capitalizada | Preparación-2 |
| `CHANGELOG.md` | Entrada 4.81.0 | FASE-RELEASE |
| `docs/GUIA_TECNICA.md` | Notas de Cambios v4.81.0 | FASE-RELEASE |
| `VERSION.yaml` + sincronizados por `sync_config.yaml` | 4.80.0 → 4.81.0 | FASE-RELEASE |
