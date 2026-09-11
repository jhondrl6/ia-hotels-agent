# Documentación Post-Proyecto — TRIBUNAL-OFFLINE-2026-09-09

> **Versión objetivo**: 4.76.0
> **Propósito**: Acumular datos por fase para que FASE-RELEASE genere CHANGELOG y GUIA_TECNICA oficiales.

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| `modules/quality_gates/tribunal/` | `__init__.py`, `judge.py`, `acta_writer.py` | Juez certificador P6+P7, veredicto determinista, acta dual (JSON+MD) | T1 |
| `modules/quality_gates/tribunal/` | `diagnosis_reviewer.py` | Bot 1: revisor de diagnóstico interno (brecha→pain_id, fuente, is_coherent) | T2-A |
| `modules/quality_gates/tribunal/` | `asset_reviewer.py` | Bot 3: revisor de completitud de assets (CON-ASSET/SIN-ASSET/GENERICO/ESTIMATED) | T2-B |
| `modules/quality_gates/tribunal/` | `llm_extractor.py` | Interfaz de extracción LLM (protocolo + mock para tests) | T4-A |
| `modules/quality_gates/tribunal/` | `alignment_reviewer.py` | Bot 2: revisor de alineación NL (promesas verbales vs matriz) | T4-A |
| `modules/quality_gates/tribunal/` | `honesty_reviewer.py` | Bot 4: revisor de honestidad comercial (sobre-presentación vs tier + CG-*) | T4-B |
| *(limpieza)* | `main.py`, `v4_proposal_generator.py`, `v4_asset_orchestrator.py` | S-E2: cura del NameError latente (hoist) + guard de `presence_lookup` corregido (dict+dataclass; reactiva consumidores — desvío D-T2C-A1 en 10-analisis) + retiro de instanciación muerta | T2-C |
| *(certificación, sin cambios de código)* | `tests/common/test_service_identity_registry.py` (preexistente) | S9: contrato de `INVALID_MAPPINGS` (registro #14); `asset_semantics_validator.py` no se modificó | T2-C |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Acta de revisión dual | `tribunal/judge.py` + `acta_writer.py` | `acta_revision.json` (machine) + `acta_revision.md` (human/client) | T1 |
| Regla de primer piso | `tribunal/judge.py` | Tier B/C → máximo APROBADO-CONDICIONAL-PENDING-ONBOARDING | T1 |
| Política de bloqueo del ZIP | `tribunal/judge.py` (`BLOCKING_VERDICTS`, `blocks_delivery_zip`) | `BLOQUEADO` y `DEVOLVER-CORRECCIONES` impiden el ZIP desde un único punto (D-T1.1) | T1 |
| Veredicto máximo condicionado a evidencia | `tribunal/judge.py` (`T1_CERTIFIABLE_CLAUSES`, `_compute_verdict`) | `APROBADO-PARA-ENTREGA` exige Tier A + cláusulas certificables en PASS; sin artefactos degrada a condicional (D-T1.2) | T1 |
| Integración tribunal en pipeline | `main.py` | Juez ejecuta junto a `delivery_quality_report`, alimenta ruta de bloqueo ZIP | T1 |
| Revisión de diagnóstico | `tribunal/diagnosis_reviewer.py` | Hallazgos por severidad sobre P6.1 | T2-A |
| Revisión de assets | `tribunal/asset_reviewer.py` | Cobertura por servicio sobre P6.3/P6.4 | T2-B |
| Extracción NL de promesas | `tribunal/llm_extractor.py` | LLM propone, Juez decide (híbrido acotado) | T4-A |
| Revisión de alineación | `tribunal/alignment_reviewer.py` | P6.2: promesas verbales vs matriz | T4-A |
| Revisión de honestidad | `tribunal/honesty_reviewer.py` | P6.5: sobre-presentación vs tier labels + 12 CG-* (P6.5 liberada tras D-T1.3 opción a) | T4-B |
| Limpieza S-E2 | `main.py`, `v4_proposal_generator.py`, `v4_asset_orchestrator.py` | `generate_proposal=False` sin `NameError`; instanciación muerta retirada; bloques `presence_lookup` reactivados (cambian la propuesta en régimen `True` — desvío D-T2C-A1) | T2-C |
| Certificación S9 | `tests/common/test_service_identity_registry.py` (preexistente) | Contrato de `INVALID_MAPPINGS` (registro #14) — sin cambios de código | T2-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos (tribunal) | 17 (13 de T1 + 4 de la auditoría) | T1 |
| Tests nuevos (tribunal T2-A) | 10 (DiagnosisReviewer) | T2-A |
| Tests nuevos (tribunal T2-B) | 12 (AssetReviewer) | T2-B |
| Tests nuevos (tribunal T2-C) | 18 (7 de la fase + 11 de remediación D-T2C-A1, auditoría 2026-09-11) | T2-C |
| Tests nuevos (tribunal T4-A) | 28 (15 llm_extractor + 13 alignment_reviewer, incl. fix post-auditoría) | T4-A |
| Tests totales tribunal acumulados | 85 (17 T1 + 10 T2-A + 12 T2-B + 18 T2-C + 28 T4-A) | T2-C (remed.) |
| Tests colectados post-T4-A | 4,018 (3,990 T2-C + 28 T4-A) | T4-A |
| Tests colectados post-remediación D-T2C-A1 | 4,029 (4,018 + 11) | T2-C (remed.) |
| Tests totales post-plan | — | E2E |
| Coherence output E2E | — | E2E |
| Veredicto del Juez (Salento Real) | — | E2E |
| Cláusulas P6 evaluadas | 6, de las cuales 4 certificables por T1 (`P6.1`, `P6.3`, `P6.4`, `P6.6`); `P6.2` diferida a T4-A; `P6.5` liberada para T4-B tras D-T1.3 opción (a) — primer piso → `first_floor_rule` | T1 |
| Archivos nuevos en `v4_audit/` | 2 (`acta_revision.json`, `acta_revision.md`) | T1 |
| Archivos nuevos en `v4_audit/` (T2-A) | 1 (`revision_diagnostico.json`) | T2-A |
| Archivos nuevos en `v4_audit/` (T2-B) | 1 (`revision_assets.json`) | T2-B |
| Archivos nuevos en `v4_audit/` (T4-A) | 1 (`revision_alineacion.json`) | T4-A |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | Integración del Juez junto a `delivery_quality_report`; la decisión del ZIP consume `blocks_delivery_zip(acta)` en lugar de comparar strings de veredicto | T1 |
| `main.py` | S-E2: `site_presence_report` fuera del bloque condicional (o guard en el consumidor) | T2-C |
| `modules/commercial_documents/v4_proposal_generator.py` | S-E2: guard de `presence_lookup` corregido (dict canónico + dataclass) — reactiva consumidores; desvío D-T2C-A1 | T2-C |
| `modules/asset_generation/v4_asset_orchestrator.py` | S-E2: retiro de instanciación muerta | T2-C |
| `modules/quality/asset_semantics_validator.py` | S9: SIN cambios de código — contrato certificado por `test_invalid_mappings_valida_contra_capa1` (preexistente) | T2-C |
| `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` | 7 tests de contrato S-E2 (presence_lookup canónico + hoist); +11 tests `TestPresenceLookupLiveConsumers` (remediación D-T2C-A1, métodos reales, 2026-09-11) = 18 | T2-C |
| `evidence/FASE-T2-C/baseline-pre-post.md` | Baseline pre/post: 3,983→3,990 tests, AC15/AC16/NR1-NR4 | T2-C |
| `evidence/FASE-T2-C/evidencia-final.md` | Diff completo + resumen + métricas + lecciones | T2-C |
| `AGENTS.md` | Nuevo módulo `tribunal/` en tabla de Módulos Activos | RELEASE |
| `VERSION.yaml` | 4.75.0 → 4.76.0 | RELEASE |
| `CHANGELOG.md` | Entrada [4.76.0] | RELEASE |
| `docs/GUIA_TECNICA.md` | Nota técnica v4.76.0 | RELEASE |
| `README.md` | Test count + module count actualizados | RELEASE |

## Sección F: Residuos heredados del plan estabilizador (asignación VERIFY 2026-09-04)

| Residuo | Dueño asignado | Disposición en este plan |
|---------|----------------|--------------------------|
| S-HF1 | tribunal | FASE-T1 ⚠️ **abierto** — documentación contradictoria, sin efecto en el código del tribunal |
| S-I1 | tribunal | FASE-T2-A |
| P12 (estructura) | tribunal | FASE-T2-B |
| S-C4 | tribunal | FASE-T4-A |
| S-E2 | tribunal | FASE-T2-C |
| S9 | tribunal | FASE-T2-C |
| S-I3 · S-V7 · S-V8 | tribunal | Cubiertos por diseño (ver README del plan) |
| S-H2 | tribunal (decisión de producto previa) | Fuera de alcance — documentado, no tocado |
