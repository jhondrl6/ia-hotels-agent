# Baseline FASE-T4-A — Revisor de Alineación NL (Bot 2)

> **Fecha**: 2026-09-11
> **Objetivo**: Implementar Bot 2 (AlignmentReviewer) + interfaz de extracción LLM (PromiseExtractor Protocol)
> **Residuo abordado**: S-C4 (tabla de assets técnicos como tercera superficie de promesa)

---

## Pre-condiciones (baseline FASE-T2-C)

| Métrica | Valor |
|---------|-------|
| Tests colectados | 3,990 |
| Tests tribunal acumulados | 46 (17 T1 + 10 T2-A + 12 T2-B + 7 T2-C) |
| Estado FASE-T2-C | ✅ Completada (S-E2 + S9 cerrados) |
| Validaciones `run_all_validations.py --quick` | 7/8 (Version Sync esperado) |

---

## Implementación

### Módulos creados

1. **`modules/quality_gates/tribunal/llm_extractor.py`** (199 líneas)
   - `VerbalPromise` dataclass: text, service_hint, location, confidence
   - `PromiseExtractor` Protocol (`@runtime_checkable`): interfaz intercambiable LLM/Mock
   - `LLMPromiseExtractor`: implementación real con cache SHA256 (default `.cache/tribunal/`)
   - `MockPromiseExtractor`: implementación fija para tests (sin dependencia LLM)
   - Parsing robusto de respuestas LLM: maneja bloques markdown con indentación variable

2. **`modules/quality_gates/tribunal/alignment_reviewer.py`** (400 líneas, estado tras fix post-auditoría)
   - `AlignmentReviewer`: revisor híbrido (LLM extrae + determinista clasifica)
   - Clasificación de promesas contra `proposal_asset_matrix.json`:
     - `ALINEADO`: LINKED + pain_id, o PRESENT_IN_PRODUCTION
     - `SIN-BRECHA-ASOCIADA`: LINKED sin pain_id
     - `PROMESA-SIN-MATRIZ`: promesa verbal sin entrada en matriz
     - `NO_BREACH` sin promesa: estado legítimo no prometido → info (`summary.no_breach_info`), no hallazgo; promesa que cae en una entrada NO_BREACH → `SIN-BRECHA-ASOCIADA` (§5.2)
   - Cruce bidireccional (fix post-auditoría): entradas de matriz sin promesa también se clasifican, con `verbal_promise_found=false` (`_cover_unmatched_entries()`)
   - Veredicto (fix post-auditoría): un hallazgo sustantivo (PROMESA-SIN-MATRIZ o SIN-BRECHA-ASOCIADA) → DEVOLVER-PRUEBAS; artefacto faltante → BLOQUEAR; S-C4 (INFO) no altera
   - Detección S-C4: regex sobre tabla de assets técnicos (`| Asset Técnico | Estado | Descripción |`)
   - Matching difuso por `service_hint`: normaliza lowercase + guiones bajos → espacios + substring matching
   - Output: `revision_alineacion.json` con `service_matrix[]`, `findings[]`, `summary`, `verdict_recommendation`

### Tests creados

1. **`tests/quality_gates/tribunal/test_llm_extractor.py`** (15 tests)
   - VerbalPromise serialization (from_dict, to_dict)
   - Protocol compliance (runtime_checkable, isinstance)
   - MockPromiseExtractor behavior (fixed promises, no LLM)
   - LLMPromiseExtractor con mock provider (cache hit/miss, markdown parsing, invalid JSON, invalid promise filtering)
   - Todos usan `tmp_path` como `cache_dir` para evitar colisiones

2. **`tests/quality_gates/tribunal/test_alignment_reviewer.py`** (13 tests, estado tras fix post-auditoría)
   - promise_without_matrix_detected (PROMESA-SIN-MATRIZ + veredicto DEVOLVER)
   - aligned_service_not_flagged (ALINEADO no es finding)
   - no_breach_associated_detected (SIN-BRECHA-ASOCIADA + finding top-level)
   - present_in_production_aligned (PRESENT_IN_PRODUCTION → ALINEADO)
   - s_c4_asset_table_detected (tercera superficie, severity INFO)
   - serialization_to_disk (R2.4: AC legible en artefacto)
   - summary_counts (cruce bidireccional: 4 filas con fixture de 3 entradas + 3 promesas)
   - verdict_bloquear_on_critical (artefacto faltante → BLOQUEAR)
   - verdict_aprobado_no_findings (fixture limpio sin S-C4 ni hallazgo → APROBADO)
   - no_breach_not_a_finding (NO_BREACH sin promesa: fuera de service_matrix, solo `no_breach_info`)
   - promise_on_no_breach_entry_flagged (promesa sobre NO_BREACH → SIN-BRECHA-ASOCIADA §5.2)
   - matrix_entries_covered_without_promise (cruce inverso, `verbal_promise_found=false`)
   - promise_without_matrix_escalates_verdict (1 hallazgo sustantivo → DEVOLVER-PRUEBAS)

---

## Post-condiciones (resultados)

| Métrica | Valor | Delta |
|---------|-------|-------|
| Tests colectados | 4,018 | +28 |
| Tests tribunal acumulados | 74 | +28 (17 T1 + 10 T2-A + 12 T2-B + 7 T2-C + 28 T4-A) |
| Tests T4-A verdes | 28/28 | 15 llm_extractor + 13 alignment_reviewer |
| Validaciones `run_all_validations.py --quick` | 8/8 TOTAL PASS | Resuelto en fix post-auditoría con `sync_versions.py` (arrastraba 7/8 por Version Sync) |

---

## ACs certificados

| AC | Descripción | Artefacto | Clave | Status |
|----|-------------|-----------|-------|--------|
| AC9 | `revision_alineacion.json` con `service_matrix[]` | `v4_audit/revision_alineacion.json` | `service_matrix` | ✅ (test-level) |
| AC10 | Promesa sin matriz → `PROMESA-SIN-MATRIZ` | test output | assertion | ✅ (test-level) |

**Nota**: AC9 y AC10 se verifican via tests de fixture, no via corrida E2E. En E2E el AlignmentReviewer leerá la propuesta real y la matriz real, pero el contrato ya está fijado por tests.

---

## Residuo S-C4

**Descripción**: La tabla de assets técnicos en la propuesta (inyectada vía `${technical_assets_table}` en el template, generada incondicionalmente por `v4_proposal_generator._generate_technical_assets_table()`) imprime el catálogo completo incondicionalmente, creando una tercera superficie de promesa verbal además de:
1. Tabla de servicios dinámicos (`${dynamic_services_table}`)
2. Tabla de calidad de assets (`${asset_quality_table}`)

**Detección**: `AlignmentReviewer._detect_technical_assets_table()` usa regex `r"\|\s*Asset Técnico\s*\|\s*Estado\s*\|\s*Descripción\s*\|"` para identificar la tabla en el markdown de la propuesta. Si está presente, genera un finding `S_C4_TECHNICAL_ASSETS_TABLE` de severidad `INFO` (se divulga al Juez sin alterar la recomendación de veredicto; política fijada en el fix post-auditoría — ver DA-T4A.2).

**Status**: ✅ Detectado y certificado por test `test_s_c4_asset_table_detected`.

---

## Decisiones de diseño (DA-T4A)

**Decisión**: Protocolo `PromiseExtractor` como interfaz de extracción.

**Rationale**:
- Permite intercambiar LLM real vs mock sin cambiar el llamador (`AlignmentReviewer`)
- `@runtime_checkable` habilita validación de tipo en tests (`isinstance(extractor, PromiseExtractor)`)
- Separa la responsabilidad de extracción (LLM) de la responsabilidad de clasificación (determinista)

**Alternativas rechazadas**:
- Hardcodear `LLMPromiseExtractor` en `AlignmentReviewer`: acopla tests a provider real, imposible CI offline
- Usar ABC en lugar de Protocol: más verboso, requiere herencia en lugar de duck typing

**Impacto en T4-B**: Bot 4 (HonestyReviewer) debe replicar el patrón:
1. Definir protocolo `HonestyExtractor` (o reutilizar `PromiseExtractor` si la interfaz coincide)
2. Implementar `LLMHonestyExtractor` (cache SHA256, parsing robusto)
3. Implementar `MockHonestyExtractor` para tests
4. Usar `tmp_path` como `cache_dir` en todos los tests

---

## Lecciones aprendidas

| # | Lección | Fuente | Aplicación futura |
|---|---------|--------|-------------------|
| L-T4A.1 | El protocolo `PromiseExtractor` debe ser `runtime_checkable` para permitir `isinstance(extractor, PromiseExtractor)` en tests y validaciones. Sin `@runtime_checkable`, solo se puede verificar con `hasattr()` que es frágil ante cambios de nombre. | Diseño de `llm_extractor.py` | T4-B debe replicar el patrón: protocolo `runtime_checkable` + implementación LLM + implementación Mock |
| L-T4A.2 | El parsing de respuestas LLM debe manejar bloques markdown con indentación variable. El código inicial `lines[1:-1]` fallaba cuando el bloque iniciaba con ````json` indentado. La solución computa `start_idx` y `end_idx` dinámicamente. | Test `test_llm_extractor_parses_json_with_markdown` | T4-B y cualquier consumidor de respuestas LLM deben usar el mismo patrón de parsing robusto |
| L-T4A.3 | La cache SHA256 de extracciones LLM debe usar `tmp_path` en tests para evitar colisiones entre corridas. Los tests compartían `.cache/tribunal/` y hits de cache enmascaraban fallos del mock provider. | Tests `test_llm_extractor_cache_hit/miss` | Cualquier test que use cache en disco debe inyectar `tmp_path` |
| L-T4A.4 | La clasificación de promesas verbales contra la matriz requiere matching difuso por `service_hint`. El LLM puede generar hints como `"Optimización para asistentes de voz"` mientras la matriz usa `"voice_readiness"`. Sin fuzzy matching, varias promesas caían en `PROMESA-SIN-MATRIZ` falso. | Test `test_aligned_service_not_flagged` | T4-B debe replicar el patrón de matching difuso al buscar referencias a CG-* en el diagnóstico |

---

## Pendientes para T4-B

1. **Reutilizar `LLMPromiseExtractor`**: Si la interfaz de extracción de honestidad coincide (texto → lista de findings), Bot 4 puede reutilizar el mismo extractor. Si no, definir `HonestyExtractor` separado.
2. **Parsing robusto**: Extraer el patrón de parsing de markdown a utilidad compartida si hay terceros consumidores.
3. **Cache compartida**: Considerar si T4-A y T4-B deben compartir el mismo directorio de cache o tener subdirectorios separados.
4. **Matching difuso**: Evaluar si el patrón de `_find_matrix_entry()` puede generalizarse para buscar CG-* references en el diagnóstico.

---

## Fix post-auditoría (2026-09-11)

Auditoría forense de la fase ejecutoriada. Desvíos detectados y su estado:

1. **R2.1**: la fase estaba ejecutada pero **sin commit**; se commiteó como `feat` + `docs` (código tal como se ejecutó) y este fix va en commit aparte.
2. **NR3**: `run_all_validations.py --quick` daba 7/8 (Version Sync: AGENTS/.cursorrules/GUIA_TECNICA). Resuelto con `sync_versions.py` → **8/8 TOTAL PASS** verificado.
3. **R2.2**: referencias a números de línea ("template línea 76") eliminadas del docstring del revisor y de esta evidencia.
4. **Cruce bidireccional**: `service_matrix` iteraba solo promesas y `verbal_promise_found` estaba hardcodeado a `true` → entradas de matriz sin promesa quedaban sin auditar. Añadido `_cover_unmatched_entries()`.
5. **Semántica NO_BREACH**: sin promesa → info (`summary.no_breach_info`), no hallazgo; con promesa → `SIN-BRECHA-ASOCIADA` (§5.2). El test que la certificaba era vacuo (nunca alcanzaba la rama).
6. **Política de veredicto (DA-T4A.2)**: elimado el umbral arbitrario `warning>=3`; un solo hallazgo sustantivo escala a DEVOLVER-PRUEBAS; S-C4 pasa a INFO.
7. **`pain_ledger_resolved.json`**: se cargaba y no se usaba; ahora se divulga como `info.brechas_en_ledger`.
8. **Cache de tests**: `test_extractor_protocol_compliance` y la rama default de `review()` tocaban `.cache/tribunal` del repo; extractors con `tmp_path` en todos los tests y construcción lazy del default. Residuos `.cache/tribunal/*.json` (sha256 de inputs de mock, de la primera iteración previa al fix de L-T4A.3) eliminados.
9. **REGISTRY**: entradas FASE-T4-A duplicadas (`log_phase_completion.py` corrido 2 veces) fusionadas; contador 473→472.
10. **Inexactitudes de esta evidencia corregidas inline**: tipos de finding S-C4, método del protocolo (`extract_verbal_promises`), conteo de líneas (199/400 vs 180/220), precisiones no medibles ("40%"), etiquetas de tests de veredicto.

No violado (verificado): ningún LLM real en tests (28 tests offline en ~2s), `judge.py`/`main.py`/`ROADMAP.md` intactos, AC9/AC10/S-C4 certificados con tests reales.

---

## Evidencia

- Tests: `tests/quality_gates/tribunal/test_llm_extractor.py`, `tests/quality_gates/tribunal/test_alignment_reviewer.py`
- Código: `modules/quality_gates/tribunal/llm_extractor.py`, `modules/quality_gates/tribunal/alignment_reviewer.py`
- Documentación: `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/09-documentacion-post-proyecto.md`, `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`
