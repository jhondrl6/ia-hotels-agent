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

1. **`modules/quality_gates/tribunal/llm_extractor.py`** (180 líneas)
   - `VerbalPromise` dataclass: text, service_hint, location, confidence
   - `PromiseExtractor` Protocol (`@runtime_checkable`): interfaz intercambiable LLM/Mock
   - `LLMPromiseExtractor`: implementación real con cache SHA256 (default `.cache/tribunal/`)
   - `MockPromiseExtractor`: implementación fija para tests (sin dependencia LLM)
   - Parsing robusto de respuestas LLM: maneja bloques markdown con indentación variable

2. **`modules/quality_gates/tribunal/alignment_reviewer.py`** (220 líneas)
   - `AlignmentReviewer`: revisor híbrido (LLM extrae + determinista clasifica)
   - Clasificación de promesas contra `proposal_asset_matrix.json`:
     - `ALINEADO`: LINKED + pain_id, o PRESENT_IN_PRODUCTION
     - `SIN-BRECHA-ASOCIADA`: LINKED sin pain_id
     - `PROMESA-SIN-MATRIZ`: promesa verbal sin entrada en matriz
     - `NO_BREACH`: no es finding (promesa ya satisfecha)
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

2. **`tests/quality_gates/tribunal/test_alignment_reviewer.py`** (10 tests)
   - promise_without_matrix_detected (PROMESA-SIN-MATRIZ)
   - aligned_service_not_flagged (ALINEADO no es finding)
   - no_breach_associated_detected (SIN-BRECHA-ASOCIADA)
   - present_in_production_aligned (PRESENT_IN_PRODUCTION → ALINEADO)
   - s_c4_asset_table_detected (tercera superficie)
   - serialization_to_disk (R2.4: AC legible en artefacto)
   - summary_counts (contadores correctos)
   - verdict_bloquear_on_critical (PROMESA-SIN-MATRIZ → DEVOLVER)
   - verdict_aprobado_no_findings (sin findings → APROBADO)
   - no_breach_not_a_finding (NO_BREACH no cuenta como finding)

---

## Post-condiciones (resultados)

| Métrica | Valor | Delta |
|---------|-------|-------|
| Tests colectados | 4,015 | +25 |
| Tests tribunal acumulados | 71 | +25 (17 T1 + 10 T2-A + 12 T2-B + 7 T2-C + 25 T4-A) |
| Tests T4-A verdes | 25/25 | 15 llm_extractor + 10 alignment_reviewer |
| Validaciones `run_all_validations.py --quick` | 7/8 | Version Sync esperado (se resuelve en RELEASE) |

---

## ACs certificados

| AC | Descripción | Artefacto | Clave | Status |
|----|-------------|-----------|-------|--------|
| AC9 | `revision_alineacion.json` con `service_matrix[]` | `v4_audit/revision_alineacion.json` | `service_matrix` | ✅ (test-level) |
| AC10 | Promesa sin matriz → `PROMESA-SIN-MATRIZ` | test output | assertion | ✅ (test-level) |

**Nota**: AC9 y AC10 se verifican via tests de fixture, no via corrida E2E. En E2E el AlignmentReviewer leerá la propuesta real y la matriz real, pero el contrato ya está fijado por tests.

---

## Residuo S-C4

**Descripción**: La tabla de assets técnicos en la propuesta (`${technical_assets_table}` en `propuesta_v6_template.md` línea 76) imprime el catálogo completo incondicionalmente, creando una tercera superficie de promesa verbal además de:
1. Tabla de servicios dinámicos (`${dynamic_services_table}`)
2. Tabla de calidad de assets (`${asset_quality_table}`)

**Detección**: `AlignmentReviewer._detect_technical_assets_table()` usa regex `r"\|\s*Asset Técnico\s*\|\s*Estado\s*\|\s*Descripción\s*\|"` para identificar la tabla en el markdown de la propuesta. Si está presente, genera un finding `S-C4_THIRD_PROMISE_SURFACE` de severidad `ADVISORY` (no bloquea, pero alerta al Juez).

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
| L-T4A.4 | La clasificación de promesas verbales contra la matriz requiere matching difuso por `service_hint`. El LLM puede generar hints como `"Optimización para asistentes de voz"` mientras la matriz usa `"voice_readiness"`. Sin fuzzy matching, el 40% de las promesas caen en `PROMESA-SIN-MATRIZ` falso. | Test `test_aligned_service_not_flagged` | T4-B debe replicar el patrón de matching difuso al buscar referencias a CG-* en el diagnóstico |

---

## Pendientes para T4-B

1. **Reutilizar `LLMPromiseExtractor`**: Si la interfaz de extracción de honestidad coincide (texto → lista de findings), Bot 4 puede reutilizar el mismo extractor. Si no, definir `HonestyExtractor` separado.
2. **Parsing robusto**: Extraer el patrón de parsing de markdown a utilidad compartida si hay terceros consumidores.
3. **Cache compartida**: Considerar si T4-A y T4-B deben compartir el mismo directorio de cache o tener subdirectorios separados.
4. **Matching difuso**: Evaluar si el patrón de `_find_matrix_entry()` puede generalizarse para buscar CG-* references en el diagnóstico.

---

## Evidencia

- Tests: `tests/quality_gates/tribunal/test_llm_extractor.py`, `tests/quality_gates/tribunal/test_alignment_reviewer.py`
- Código: `modules/quality_gates/tribunal/llm_extractor.py`, `modules/quality_gates/tribunal/alignment_reviewer.py`
- Documentación: `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/09-documentacion-post-proyecto.md`, `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`
