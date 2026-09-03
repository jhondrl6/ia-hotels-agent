# 09 — Documentación Post-Proyecto

> **Plan**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03
> **Estado**: 🟡 EN CURSO — archivo creado **desde la concepción** del plan (executor §4). Se actualiza
> **incrementalmente al cierre de cada fase** (Post-Ejecución punto 3), NO al final.
> **Consumidor**: FASE-RELEASE lo lee para generar CHANGELOG y GUIA_TECNICA. Si este archivo está vacío,
> RELEASE produce documentación vacía.
> **Regla anti-reproceso**: cada fase vuela su propia fila; RELEASE solo consolida.

---

## Sección A — Módulos nuevos

> Módulos/archivos **creados** por el plan que no existían antes. Fuente: Post-Ejecución de cada fase.

| Fase | Módulo / archivo nuevo | Propósito | Estado |
|------|------------------------|-----------|--------|
| A | `modules/asset_generation/service_asset_registry.py` *(nombre a confirmar en A2)* | Fuente canónica única de identidad servicio↔asset↔pain — reemplaza los ≥9 registros dispersos | ⬜ Pendiente |
| A | `tests/asset_generation/test_canonical_registry_contract.py` | Contract tests narrativa↔fuente (L-NC10: relación, no valores fijos) | ⬜ Pendiente |
| B | `tests/commercial_documents/test_pain_bijection.py` | Guardián AST de la biyección mapa↔emisión (patrón SR-A, no regex) | ⬜ Pendiente |
| E | `modules/.../site_presence_writer.py` *(nombre a confirmar en E1)* | Persiste `site_presence_snapshot` en disco (mitad pendiente de DT4-R2) | ⬜ Pendiente |
| D | `tests/quality_gates/test_gate_severity.py` | Lock de regresión de la estructura 11 blocking + 2 advisory | ⬜ Pendiente |
| … | *(agregar filas si una fase crea archivos no previstos)* | | |

**Nota**: los nombres exactos los fija cada fase en su implementación; esta tabla se corrige al cierre de
fase con el nombre real. Lo importante para RELEASE es la **lista consolidada de archivos nuevos**.

---

## Sección B — Funcionalidades nuevas

> Comportamiento **nuevo o modificado** que el sistema gana con el plan.

| Fase | Funcionalidad | Hallazgo del dossier que cura | Estado |
|------|---------------|-------------------------------|--------|
| A | Fuente única de identidad servicio↔asset↔pain; drift «8 vs 7» corregido en 3 copias | V2, V3, V14 (§12.3); causa raíz §12.5 (≥9 registros) | ⬜ Pendiente |
| B | Biyección mapa↔emisión: cada pain o se emite o está justificado | V1 (9 pains muertos); §3 candado de biyección | ⬜ Pendiente |
| C | **Punto 8**: propuesta dinámica — solo promete servicios con brecha detectada (`no_breach = 0` por construcción) | §9.2 B1-B5; tautología de coverage; `is_coherent = false` estructural | ⬜ Pendiente |
| D | Severidad de gates: **11 blocking + 2 advisory** con piso explícito y WARNING a `human_checklist` | H10; §8.4; docstrings 10+3 vs código 13 | ⬜ Pendiente |
| E | A2: `site_presence_snapshot` persistido en disco + A6: `asset_path` poblado | A2, A6 (§9.1); H7; DT4-N2 mitad disco pendiente | ⬜ Pendiente |
| F | A4: oráculo único de presencia + A1: `skipped != passed` (`NOT_EVALUATED`) + N11: gate respeta `is_coherent` | A4, A1 (§9.1); V15; N11/P9 (deuda más grave) | ⬜ Pendiente |
| G | Ceguera de gates: `doc_audit_consistency` cableado + `critical_recall` expandido + escotillas V5/V9 cerradas sin reversar BUG-6 | §12.5 Nivel 3.7; V5, V9, V10 | ⬜ Pendiente |
| H | Quirúrgicos: V6 (`except Exception`), V7 (guard `__iter__`), V8 (dedup), V11 (residuos D6), V12 (doc OPS), V13 (gemelos `MetadataValidator`) | §12.5 Nivel 3.8; V6, V7, V8, V11, V12, V13 | ⬜ Pendiente |

---

## Sección C — Ejecución E2E (FASE-I)

> Resultado certificado de la **única** corrida `v4complete` del plan, sobre Hotel Salento Real.
> La llena FASE-I y la certifica FASE-VERIFY. **Valores reales, no de fixture.**

| Campo | Baseline (FASE-D 2026-08-31 12:28) | Corrida FASE-I | Delta | AC relacionado |
|-------|------------------------------------|----------------|-------|----------------|
| `no_breach` (proposal_asset_matrix) | 6 | *(pendiente)* | *(pendiente)* | AC5 |
| `coverage_ratio` | 1.000 (tautológico) | *(pendiente)* | *(pendiente)* | AC6 |
| `is_coherent` (3 artefactos / 6 copias) | `false` | *(pendiente)* | *(pendiente)* | AC6, AC12 |
| `coherence` score | 0.88 | *(pendiente)* | *(pendiente)* | NR2 |
| Gates ejecutados | 13 | *(pendiente: 11+2)* | *(pendiente)* | NR3 |
| `site_presence_snapshot` en disco | **ausente** | *(pendiente: presente)* | *(pendiente)* | AC9 |
| `asset_path` en entradas LINKED | `null` | *(pendiente)* | *(pendiente)* | AC9 |
| G9 (delivery_quality_report) | `skipped` contaba como `passed` | *(pendiente: NOT_EVALUATED)* | *(pendiente)* | AC11 |
| ZIP de delivery | generado | *(pendiente)* | *(pendiente)* | NR4 |

**Anomalías preexistentes** (no cuentan como regresión): *(FASE-I las clasifica; VERIFY las confirma)*.

---

## Sección D — Métricas acumulativas

> Se actualiza al cierre de **cada** fase. RELEASE cierra con el total final.

| Métrica | Valor inicial | Valor actual | Última fase que actualizó |
|---------|---------------|--------------|---------------------------|
| Tests totales (`def test_`) | 3,689 | *(pendiente)* | — |
| Tests quality_gates + asset_generation | 848 passed / 2 skipped | *(pendiente)* | — |
| Contract tests agregados | 0 | *(pendiente)* | — |
| Fases completadas | 0 / 11 | 0 / 11 | — |
| Versión | 4.74.1 | 4.74.1 | — |
| Registros de identidad consolidados | ≥9 dispersos | *(pendiente: 1)* | — |
| Gates blocking / advisory | 10 / 3 (declarado) · 13 plano (código) | *(pendiente: 11 / 2)* | — |

> **Conteos de tests** (memoria `conteos-tests-documentados-metodo-def_test`): documentar por
> `grep "def test_"`, no por `--collect-only` (3,631 vs 3,520). Actualizar README + AGENTS **juntos**.

---

## Sección E — Archivos afiliados actualizados

> Archivos de producción y documentación **modificados** por el plan. RELEASE los consolida en el
> CHANGELOG (`### Archivos Modificados`).

| Fase | Archivo modificado | Región / cambio | Estado |
|------|--------------------|-----------------|--------|
| A | `modules/asset_generation/proposal_asset_alignment.py` | `:22` `PROPOSAL_SERVICE_TO_ASSET`, `:219`, `:993` → consumen fuente canónica | ⬜ Pendiente |
| A | `modules/asset_generation/conditional_generator.py` | `:234-257` `PAIN_TO_ASSET`, `:314-326` | ⬜ Pendiente |
| A | `modules/asset_generation/pain_ledger.py` | `:52-94` `NORMALIZATION_RULES` / `PAIN_TO_PRESENCE_ASSET` | ⬜ Pendiente |
| A | `modules/commercial_documents/v4_diagnostic_generator.py` | `:135` `ELEMENTO_KB_TO_PAIN_ID`, `:160`, `:3067-3086` | ⬜ Pendiente |
| A | `modules/commercial_documents/v4_proposal_generator.py` | `:1332` drift «8 vs 7», `:1365-1372` `ASSET_TO_PAIN_ID` | ⬜ Pendiente |
| B | `modules/commercial_documents/pain_solution_mapper.py` | `:60` `PAIN_SOLUTION_MAP` (27), `:339` `detect_pains` | ⬜ Pendiente |
| C | `modules/commercial_documents/v4_proposal_generator.py` | `:1281-1289` `service_brecha_candidates` dinámico | ⬜ Pendiente |
| C | `modules/commercial_documents/templates/propuesta_v6_template.md` | `${dynamic_services_table}` | ⬜ Pendiente |
| C | `modules/asset_generation/proposal_asset_alignment.py` | `:575-659` y `:748-789` builders (A5: **uno** solo) | ⬜ Pendiente |
| D | `modules/quality_gates/publication_gates.py` | `:4`, `:162`, `:181`, `:239-249`, `:1967` severidad 11+2 | ⬜ Pendiente |
| D | `AGENTS.md` | tabla Módulos Activos + bloque FASE 4.5 → 11+2 | ⬜ Pendiente |
| E | `modules/quality_gates/alignment_result.py` | `asset_path` poblado (consumidor de A6) | ⬜ Pendiente |
| F | `modules/quality_gates/alignment_result.py` | `:62` `_presence_resolved` → oráculo único | ⬜ Pendiente |
| F | `modules/quality_gates/delivery_quality_report.py` | `:250-257`, `:310-319`, `:325` skipped≠passed | ⬜ Pendiente |
| F | `modules/commercial_documents/coherence_validator.py` | `:670`, `:689-700` (`score=1.0` hardcode), N11 | ⬜ Pendiente |
| G | `modules/quality_gates/publication_gates.py` | `:1244` `doc_audit_consistency`, `:1237-1242` V5, `:1295-1344` V9 | ⬜ Pendiente |
| G | `modules/auditors/v4_comprehensive.py` | `:1789` `_identify_critical_issues` (PageSpeed ERROR + GEO) | ⬜ Pendiente |
| H | `modules/commercial_documents/pain_solution_mapper.py` | `:453` V7, `:677-701` V8 | ⬜ Pendiente |
| H | `modules/commercial_documents/v4_diagnostic_generator.py` | `:3189-3194` V6, `:1945-1952` V11 | ⬜ Pendiente |
| H | `modules/auditors/v4_comprehensive.py` | `:1841` residuo D6 | ⬜ Pendiente |
| H | `data_validation/metadata_validator.py` + `modules/data_validation/metadata_validator.py` | V13 unificación de gemelos | ⬜ Pendiente |
| RELEASE | `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `REGISTRY.md`, `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `DOMAIN_PRIMER.md` | Cierre documental 4.75.0 | ⬜ Pendiente |

> **Archivos NO tocados** (decisión explícita del plan): `delivery_quality_report.py:289`
> `BLOCKING_GATE_NAMES` (rige el ZIP, régimen de delivery, no publicación — §8.4 punto 3); `.env`
> (V12 es decisión OPS, se documenta, no se edita).
