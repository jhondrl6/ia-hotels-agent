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
| *(limpieza)* | `main.py`, `v4_proposal_generator.py`, `v4_asset_orchestrator.py` | S-E2: cura del NameError latente + retiro de bloques `presence_lookup` muertos | T2-C |
| *(certificación)* | `modules/quality/asset_semantics_validator.py` | S9: contrato de `INVALID_MAPPINGS` (registro #14) | T2-C |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Acta de revisión dual | `tribunal/judge.py` + `acta_writer.py` | `acta_revision.json` (machine) + `acta_revision.md` (human/client) | T1 |
| Regla de primer piso | `tribunal/judge.py` | Tier B/C → máximo APROBADO-CONDICIONAL-PENDING-ONBOARDING | T1 |
| Integración tribunal en pipeline | `main.py` | Juez ejecuta junto a `delivery_quality_report`, alimenta ruta de bloqueo ZIP | T1 |
| Revisión de diagnóstico | `tribunal/diagnosis_reviewer.py` | Hallazgos por severidad sobre P6.1 | T2-A |
| Revisión de assets | `tribunal/asset_reviewer.py` | Cobertura por servicio sobre P6.3/P6.4 | T2-B |
| Extracción NL de promesas | `tribunal/llm_extractor.py` | LLM propone, Juez decide (híbrido acotado) | T4-A |
| Revisión de alineación | `tribunal/alignment_reviewer.py` | P6.2: promesas verbales vs matriz | T4-A |
| Revisión de honestidad | `tribunal/honesty_reviewer.py` | P6.5: sobre-presentación vs tier labels + 12 CG-* | T4-B |
| Limpieza S-E2 | `main.py`, `v4_proposal_generator.py`, `v4_asset_orchestrator.py` | `generate_proposal=False` sin `NameError`; código muerto retirado | T2-C |
| Certificación S9 | `modules/quality/asset_semantics_validator.py` | Contrato de `INVALID_MAPPINGS` (registro #14) | T2-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos (tribunal) | — | T1-T4B |
| Tests totales post-plan | — | E2E |
| Coherence output E2E | — | E2E |
| Veredicto del Juez (Salento Real) | — | E2E |
| Cláusulas P6 evaluadas | — | E2E |
| Archivos nuevos en `v4_audit/` | — | E2E |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | Integración del Juez junto a `delivery_quality_report` | T1 |
| `main.py` | S-E2: `site_presence_report` fuera del bloque condicional (o guard en el consumidor) | T2-C |
| `modules/commercial_documents/v4_proposal_generator.py` | S-E2: retiro de bloques `presence_lookup` muertos | T2-C |
| `modules/asset_generation/v4_asset_orchestrator.py` | S-E2: retiro de instanciación muerta | T2-C |
| `modules/quality/asset_semantics_validator.py` | S9: contrato de `INVALID_MAPPINGS` | T2-C |
| `AGENTS.md` | Nuevo módulo `tribunal/` en tabla de Módulos Activos | RELEASE |
| `VERSION.yaml` | 4.75.0 → 4.76.0 | RELEASE |
| `CHANGELOG.md` | Entrada [4.76.0] | RELEASE |
| `docs/GUIA_TECNICA.md` | Nota técnica v4.76.0 | RELEASE |
| `README.md` | Test count + module count actualizados | RELEASE |

## Sección F: Residuos heredados del plan estabilizador (asignación VERIFY 2026-09-04)

| Residuo | Dueño asignado | Disposición en este plan |
|---------|----------------|--------------------------|
| S-HF1 | tribunal | FASE-T1 |
| S-I1 | tribunal | FASE-T2-A |
| P12 (estructura) | tribunal | FASE-T2-B |
| S-C4 | tribunal | FASE-T4-A |
| S-E2 | tribunal | FASE-T2-C |
| S9 | tribunal | FASE-T2-C |
| S-I3 · S-V7 · S-V8 | tribunal | Cubiertos por diseño (ver README del plan) |
| S-H2 | tribunal (decisión de producto previa) | Fuera de alcance — documentado, no tocado |
