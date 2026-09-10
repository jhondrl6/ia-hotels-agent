# 01 — Plan Maestro: TRIBUNAL-OFFLINE-2026-09-09

> **Versión objetivo**: 4.76.0 · **Workflow**: `phased_project_executor.md` v2.20.0
> **Fuente**: `.opencode/context/Historico/CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` §5, §14, §15 (movido a Historico; lecciones QMind: notebook `iah-cli-lecciones` — write-back automatizado vía `scripts/validate_qmind_writeback.py`)
> **Anclaje**: `ROADMAP.md` v4.2 §7.2 (FASE T, tramo offline)
> **Reglas activas**: R1 (una fase/sesión) · R2.1 (presupuesto medido, corte en commit) · R2.2 (símbolos, no líneas) · R2.3 (delta pre/post) · R2.4 (AC legible en artefacto) · R2.5 (RELEASE archiva) · R3 (≤4 tareas ó 3+1 largo)

---

## 1. Secuencia y presupuesto

| # | Fase | Complejidad | Modo | Tareas (R3) | Presupuesto iter. | Depende de |
|---|------|-------------|------|-------------|-------------------|------------|
| 1 | FASE-T1 | **ALTA** | DIRECTO | 4 | 55 | — |
| 2 | FASE-T2-A | MEDIA | DIRECTO | 3 | 35 | T1 |
| 3 | FASE-T2-B | MEDIA | DIRECTO | 3 | 35 | T1 |
| 4 | FASE-T2-C | MEDIA | DIRECTO | 3 | 40 | T1 |
| 5 | FASE-T4-A | **ALTA** | DIRECTO | 4 | 50 | T1, T2-A, T2-B |
| 6 | FASE-T4-B | MEDIA | DIRECTO | 3 | 30 | T4-A |
| 7 | FASE-E2E | BAJA | MIXTO | 3 + 1 largo | 25 | T2-C, T4-B |
| 8 | FASE-VERIFY | MEDIA | DIRECTO | 4 | 40 | E2E |
| 9 | FASE-RELEASE-4.76.0 | BAJA | DELEGABLE | 4 | 25 | VERIFY |

**Total**: 9 sesiones. Presupuesto máximo teórico 335 iteraciones; corte fijo: commit de código (R2.1).

> [!IMPORTANT]
> **Modo DIRECTO (no delegable) en T2-A, T2-B, T2-C y T4-B**: ejecutor v2.20.0, branch «SI la fase requiere imports del proyecto (tests, integración) Y el proyecto usa venv Windows accedido desde WSL → DIRECTA… NO delegar a subagentes» (lección FASE-4 BUGS-ONBOARDING-ADR: ~40 iteraciones perdidas). Estas fases crean módulos **y corren tests que importan el proyecto**; el modo por defecto es DIRECTO. `delegate_task` queda solo como opción condicionada a demostrar que los tests son stdlib-only y corridos por el parent.

> [!WARNING]
> **Riesgo de split en T1 (55) y T4-A (50)**: la heurística `30 + tareas×10` los estima en ~70 (umbral deep-audit D14). Ambos traen **punto de partición predefinido** en `dependencias-fases.md` (T1-part1/2 y T4-A-part1/2); aplicar solo si el presupuesto se agota, registrando la decisión en `10-analisis`.

**Nota sobre presupuestos (lección §14.3.2 — recalibración)**: los números por fase son **orientativos**, no gate duro. El histórico medido del plan anterior fue ≥1.219 iteraciones en 9 fases (~3× los presupuestos escritos). El corte vinculante es el commit de código (R2.1); en fases sin código (E2E/VERIFY/RELEASE) el corte es el cierre documental de la fase.

**Instrumento de medición**: `evidence/FASE-D/measure_iterations.py`. Si no corre bajo la política de permisos, el auto-reporte se publica en la unidad usada y se declara no comparable (R2.1).

**Paralelismo**: FASE-T2-A, FASE-T2-B y FASE-T2-C son independientes en **contenido** (las tres dependen solo de T1; cualquier orden). **NUNCA en ejecución simultánea**: sesiones paralelas sobre el mismo working tree sobrescribieron evidencia en el plan anterior (QMIND-WRITE-BACK, lecciones de sesiones D/B simultáneas), y editan los mismos archivos (`__init__.py`, 09, 10, 06, README del plan) — **T2-C además comparte `main.py` con T1** → secuencial tras T1. Siempre secuenciales.

---

## 2. Detalle de tareas por fase

### FASE-T1 — Juez Certificador (`tribunal/judge.py`)

**Complejidad: ALTA.** Decisión arquitectónica cross-module: elegir cuál de las tres rutas de bloqueo del ZIP alimenta el veredicto del Juez, diseñar el contrato de acta estable que T2/T4 consumen, e integrar en `main.py` junto a `delivery_quality_report`.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T1.1 | **Research**: identificar las 3 rutas de bloqueo del ZIP en `main.py` (`GATE_BLOCKING_ENABLED` kill switch + las 3 zonas de decisión), elegir la ruta de integración y documentar la decisión | `main.py` (zona `delivery_quality_report`), `modules/quality_gates/publication_gates.py` | AC1 |
| T1.2 | **Implementar** `modules/quality_gates/tribunal/judge.py`: clase `TribunalJudge` con veredicto determinista (APROBADO-PARA-ENTREGA / APROBADO-CONDICIONAL-PENDING-ONBOARDING / DEVOLVER-CORRECCIONES / BLOQUEADO). Regla de primer piso: `evidence_tier ∈ {B,C}` → máximo condicional, leído de `MANIFEST.json → quality_metadata` (en `deliveries_dir`). P6.6 se lee de `gate_report → gate_results[coherence] + [hard_contradictions]`, NO del flag `is_coherent` del validador. Resolución de `deliveries_dir` por glob. Cláusulas sin artefacto fuente → `NOT_EVALUABLE`. Writers: `acta_revision.json` + `acta_revision.md` | `modules/quality_gates/tribunal/__init__.py`, `modules/quality_gates/tribunal/judge.py`, `modules/quality_gates/tribunal/acta_writer.py` | AC1, AC2, AC3 |
| T1.3 | **Tests**: `tests/quality_gates/tribunal/test_judge.py` — retro sobre artefactos reales de SalenteReal (Tier B → veredicto condicional), test de primer piso, test de serialización del acta (R2.4) | `tests/quality_gates/tribunal/test_judge.py`, `tests/quality_gates/tribunal/test_acta_serialization.py` | AC2, AC3 |
| T1.4 | **Integración + Docs**: cablear el Juez en `main.py` junto a `delivery_quality_report`; el veredicto alimenta UNA ruta existente de bloqueo del ZIP. `log_phase_completion.py` | `main.py` | AC1, AC4 |

**Residuo abordado**: S-HF1 — el Juez decide qué mide `total_services` como criterio de narración (no de serialización).

**ACs de FASE-T1**:
- AC1: `acta_revision.json` existe en `output/<corrida>/v4_complete/<hotel>/v4_audit/` con clave `verdict` legible. Artefacto: `acta_revision.json`. Clave: `verdict`.
- AC2: Veredicto para Tier B/C es `APROBADO-CONDICIONAL-PENDING-ONBOARDING` (nunca `APROBADO-PARA-ENTREGA`). Artefacto: `acta_revision.json`. Clave: `verdict` + `evidence_tier`.
- AC3: `acta_revision.md` es legible por humano, incluye las 6 cláusulas P6 evaluadas con referencia al artefacto fuente. Artefacto: `acta_revision.md`. Clave: secciones P6.1-P6.6.
- AC4: El Juez NO añade una cuarta ruta de bloqueo del ZIP; alimenta una de las tres existentes. Artefacto: `main.py` (grep de rutas de bloqueo). Clave: una sola llamada a `tribunal/judge`.

---

### FASE-T2-A — Revisor de Diagnóstico (Bot 1)

**Complejidad: MEDIA.** Módulo determinista que lee artefactos existentes y produce hallazgos por severidad. Contrato de entrada/salida definido por T1.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T2A.1 | **Implementar** `tribunal/diagnosis_reviewer.py`: clase `DiagnosisReviewer`. Lee `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` + `coherence_validation.json` + `pain_ledger.json` + `pain_ledger_resolved.json`. Verifica: brechas con `pain_id` trazable, fuente declarada, cifras desde inputs declarados, `is_coherent` respetado. Salida: `revision_diagnostico.json` | `modules/quality_gates/tribunal/diagnosis_reviewer.py` | AC5 |
| T2A.2 | **Tests**: retro sobre artefactos de SalenteReal + FASE-I. Test de serialización (R2.4). Test de distinción recall fundado vs vacuo (S-I1) | `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` | AC5, AC6 |
| T2A.3 | **Docs**: `log_phase_completion.py` + actualizar `09-documentacion-post-proyecto.md` | — | — |

**Residuo abordado**: S-I1 — Bot 1 distingue `critical_recall` fundado (con `details.critical_issues_count` + `recall_basis`) de vacuo (`details: {}`). Nota: el gate YA serializa `details` en código v4.75.0 — en la corrida E2E no dispara; AC6 es test-level con fixture.

**ACs de FASE-T2-A**:
- AC5: `revision_diagnostico.json` existe en `v4_audit/` con clave `findings[]` (cada finding: `severity`, `clause`, `source_artifact`, `description`). Artefacto: `revision_diagnostico.json`. Clave: `findings`.
- AC6: Bot 1 marca `critical_recall` vacuo cuando `details` no declara `critical_issues_count`. Artefacto: `revision_diagnostico.json`. Clave: `findings[].clause == "P6.1"` + `finding_type == "VACUOUS_RECALL"`.

---

### FASE-T2-B — Revisor de Assets (Bot 3)

**Complejidad: MEDIA.** Módulo determinista que lee artefactos y archivos reales en `ASSETS/`. Contrato definido por T1.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T2B.1 | **Implementar** `tribunal/asset_reviewer.py`: clase `AssetReviewer`. Lee `asset_generation_report.json` + `delivery_quality_report.json` + `MANIFEST.json` + `IMPLEMENTATION_ORDER.md` (en `deliveries_dir`) + archivos en `ASSETS/` (en `deliveries_dir`). Clasifica: CON-ASSET / SIN-ASSET / ASSET-GENERICO / ASSET-ESTIMATED-NO-ETIQUETADO. Detecta `promised_assets_exist` que declara fuente catálogo estático en el `message` (P12: P6.3 no verificable desde el artefacto). Salida: `revision_assets.json` | `modules/quality_gates/tribunal/asset_reviewer.py` | AC7 |
| T2B.2 | **Tests**: retro sobre artefactos de SalenteReal. Test de serialización. Test P12 (fuente catálogo estático declarada en `message` → hallazgo; `via generated_assets` + archivo en disco → sin hallazgo) | `tests/quality_gates/tribunal/test_asset_reviewer.py` | AC7, AC8 |
| T2B.3 | **Docs**: `log_phase_completion.py` + actualizar `09-documentacion-post-proyecto.md` | — | — |

**Residuo abordado**: P12 — Bot 3 detecta que `promised_assets_exist` verificó via catálogo estático (fuente declarada en el `message`) y lo señala como P6.3 no verificable desde el artefacto; la verificación real de P6.3 la hace Bot 3 contra archivos en disco. NO se marca por score==1.0 (un run post-gen verificado también da 1.0).

**ACs de FASE-T2-B**:
- AC7: `revision_assets.json` existe en `v4_audit/` con clave `coverage_by_service[]` (cada entrada: `service`, `status`, `asset_path`, `finding`). Artefacto: `revision_assets.json`. Clave: `coverage_by_service`.
- AC8: Bot 3 señala `IMPLEMENTATION_ORDER.md` vacío como asset incompleto. Artefacto: `revision_assets.json`. Clave: `findings[].finding_type == "EMPTY_DELIVERY_TEMPLATE"`.

---

### FASE-T2-C — Limpieza de precondiciones heredadas (S-E2, S9)

**Complejidad: MEDIA.** Dos limpiezas acotadas en archivos ya identificados + tests de contrato. Absorbe los dos residuos que VERIFY del plan estabilizador asignó al tribunal (no re-diferibles, DA-V5).

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T2C.1 | **S-E2**: eliminar el `NameError` latente de `site_presence_report` (asignado solo dentro de `if generate_proposal:`, consumido bajo `except` amplio) + retirar los 3 bloques `presence_lookup` muertos y la instanciación muerta | `main.py`, `modules/commercial_documents/v4_proposal_generator.py`, `modules/asset_generation/v4_asset_orchestrator.py` | AC15 |
| T2C.2 | **S9**: certificar `INVALID_MAPPINGS` con test de contrato (claves ⊆ `PAIN_SOLUTION_MAP`, valores ⊆ `ASSET_CATALOG`) + verificar/curar el fósil V3 en `service_identity.py` | `modules/quality/asset_semantics_validator.py`, `modules/common/service_identity.py` | AC16 |
| T2C.3 | **Tests + Docs**: sondas S-E2 (régimen `generate_proposal=False`) + test de contrato S9 + `log_phase_completion.py` | `tests/quality_gates/tribunal/`, `tests/quality/` | AC15, AC16 |

**Residuos abordados**: S-E2 (NameError latente — precondición del régimen `generate_proposal=False`), S9 (`INVALID_MAPPINGS`, registro #14). Ambos con dueño «tribunal» asignado por VERIFY (2026-09-04).

**ACs de FASE-T2-C**:
- AC15: El camino `generate_proposal=False` no lanza `NameError` en `site_presence_report`. Artefacto: salida de la sonda/test. Clave: assertion (exit sin `NameError`).
- AC16: `INVALID_MAPPINGS` pasa test de contrato (claves `pain_id` ∈ `PAIN_SOLUTION_MAP`, valores ∈ `ASSET_CATALOG`). Artefacto: salida de test. Clave: assertion del contrato.

---

### FASE-T4-A — Revisor de Alineación NL (Bot 2) + Interfaz de Extracción LLM

**Complejidad: ALTA.** Define la arquitectura híbrida: LLM solo extrae promesas verbales, capa determinista verifica contra matriz. Establece el patrón de mock para tests que T4-B replica.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T4A.1 | **Diseñar + implementar interfaz de extracción LLM**: `tribunal/llm_extractor.py` — protocolo `PromiseExtractor` con método `extract_verbal_promises(proposal_text) → list[VerbalPromise]`. Implementación default usa el LLM del pipeline; mock para tests | `modules/quality_gates/tribunal/llm_extractor.py` | AC9 |
| T4A.2 | **Implementar** `tribunal/alignment_reviewer.py`: clase `AlignmentReviewer`. Lee `02_PROPUESTA_COMERCIAL.md` + `proposal_asset_matrix.json`. LLM extrae promesas verbales → determinista verifica contra matriz. Marca: `promesa-sin-matriz`, `SIN-BRECHA-ASOCIADA`, `ALINEADO`. Salida: `revision_alineacion.json` | `modules/quality_gates/tribunal/alignment_reviewer.py` | AC9, AC10 |
| T4A.3 | **Tests**: LLM mockeado. Test con propuesta que promete verbalmente servicio ausente de matriz → marcado. Test de serialización. Test S-C4 (tabla de assets técnicos como tercera superficie de promesa) | `tests/quality_gates/tribunal/test_alignment_reviewer.py`, `tests/quality_gates/tribunal/test_llm_extractor.py` | AC9, AC10 |
| T4A.4 | **Docs**: `log_phase_completion.py` + actualizar `09-documentacion-post-proyecto.md` | — | — |

**Residuo abordado**: S-C4 — la tabla de assets técnicos que imprime catálogo incondicional es una tercera superficie de promesa; Bot 2 la detecta.

**ACs de FASE-T4-A**:
- AC9: `revision_alineacion.json` existe en `v4_audit/` con clave `service_matrix[]` (cada entrada: `service`, `status` ∈ {ALINEADO, SIN-BRECHA-ASOCIADA, PROMESA-SIN-MATRIZ}, `verbal_promise_found`, `matrix_entry_found`). Artefacto: `revision_alineacion.json`. Clave: `service_matrix`.
- AC10: Test con propuesta que promete verbalmente "implementación de chatbot" sin entrada en matriz → `status: PROMESA-SIN-MATRIZ`. Artefacto: test output. Clave: assertion sobre `status`.

---

### FASE-T4-B — Revisor de Honestidad NL (Bot 4)

**Complejidad: MEDIA.** Replica el patrón de T4-A con diferentes inputs. Lee los 12 CG-* repartidos en DOS archivos comerciales.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| T4B.1 | **Implementar** `tribunal/honesty_reviewer.py`: clase `HonestyReviewer`. Lee `financial_scenarios_*.json` + `commercial_gates_report.json` + `commercial_gates_report_diagnostic_*.json` (AMBOS) + `02_PROPUESTA_COMERCIAL.md`. LLM extrae claims de sobre-presentación → determinista verifica contra tier labels + CG-*. Salida: `revision_honestidad.json` | `modules/quality_gates/tribunal/honesty_reviewer.py` | AC11 |
| T4B.2 | **Tests**: LLM mockeado. Test con ESTIMATED presentado como verificado → marcado. Test que lee AMBOS archivos comerciales (el canónico + el diagnóstico). Test de serialización | `tests/quality_gates/tribunal/test_honesty_reviewer.py` | AC11, AC12 |
| T4B.3 | **Docs**: `log_phase_completion.py` + actualizar `09-documentacion-post-proyecto.md` | — | — |

**ACs de FASE-T4-B**:
- AC11: `revision_honestidad.json` existe en `v4_audit/` con clave `findings[]` (cada finding: `type` ∈ {OVER_PRESENTATION, TIER_MISMATCH, CG_WARNING_UNDISCLOSED}, `claim_text`, `evidence_tier_declared`, `cg_reference`). Artefacto: `revision_honestidad.json`. Clave: `findings`.
- AC12: Bot 4 detecta `CG-WHATSAPP-LEAD` (WARNING) que vive en el archivo de diagnóstico, no en el canónico. Artefacto: `revision_honestidad.json`. Clave: `findings[].cg_reference == "CG-WHATSAPP-LEAD"`.

---

### FASE-E2E — Ejecución v4complete Hotel Salento Real

**Complejidad: BAJA.** Ejecución del pipeline completo con el tribunal integrado + colección de evidencia.

| # | Tarea | Archivos | AC |
|---|-------|----------|-----|
| E2E.1 | **Ejecutar** `v4complete --url https://www.hotelsalentoreal.com/` (COMANDO LARGO, subagente con timeout=900, notify_on_complete=True) | — | AC13 |
| E2E.2 | **Protocolo de Evidencia Proactiva**: copiar artefactos críticos a `evidence/FASE-E2E/` INMEDIATAMENTE después de que v4complete genera output | `evidence/FASE-E2E/` | AC13 |
| E2E.3 | **Verificar** que `acta_revision.json` + `acta_revision.md` existen en el output, que los 4 revisores produjeron sus JSONs, y que el veredicto es coherente con el tier. Comparar contra baseline FASE-D (delta, R2.3) | `output/v4_complete/hotelsalentoreal/v4_audit/` | AC13, AC14 |
| E2E.4 | **Docs**: `log_phase_completion.py` + actualizar `09-documentacion-post-proyecto.md` + `10-analisis-post-implementacion.md` | — | — |

**ACs de FASE-E2E**:
- AC13: `acta_revision.json` existe en `output/v4_complete/hotelsalentoreal/v4_audit/` con las 6 cláusulas P6 evaluadas. Artefacto: `acta_revision.json`. Clave: `clauses_evaluated` (count == 6).
- AC14: Los 4 reportes de revisión (`revision_diagnostico.json`, `revision_assets.json`, `revision_alineacion.json`, `revision_honestidad.json`) existen en `v4_audit/`. Artefacto: directorio `v4_audit/`. Clave: presencia de los 4 archivos.

---

### FASE-VERIFY — Certificación Formal de ACs

**Complejidad: MEDIA.** Verificación sin código: certifica AC1-AC16 contra output E2E real.

| # | Tarea | AC |
|---|-------|-----|
| V.1 | Leer output post-fix (`evidence/FASE-E2E/`) y baseline (`output/FASE-D_salentoreal_post_guard/`) | — |
| V.2 | Verificar cada AC (1-16) contra output real: lectura directa de JSONs, greps de claves, comparación de veredictos | AC1-AC16 |
| V.3 | Completar matriz de verificación en `10-analisis-post-implementacion.md` + diff antes/después | — |
| V.4 | Registrar lecciones aprendidas (mínimo 3) + `log_phase_completion.py` | — |

**Restricción**: NO modifica código. NO ejecuta v4complete. Si un AC falla → "Seguimientos abiertos".

---

### FASE-RELEASE-4.76.0 — Cierre y Documentación Oficial

**Complejidad: BAJA.** Solo documentación y validaciones. Delegable a subagente.

| # | Tarea |
|---|-------|
| R.1 | E1-E2: `version_consistency_checker.py` + `sync_versions.py` (VERSION.yaml → 4.76.0) |
| R.2 | E3-E4: CHANGELOG.md (formato CONTRIBUTING) + GUIA_TECNICA.md (nota técnica) |
| R.3 | E5-E8: Skills/workflows + SYSTEM_STATUS + DOMAIN_PRIMER + symlink + `run_all_validations.py --quick` + E8b README audit |
| R.4 | R2.5: Archivar plan (`git mv` a `Archives/` + `validate_opencode_refs.py --fix` + `validate_plan_citations.py --update-baseline` + `--quick` verde). Commit único cierra RELEASE + archivado |

---

## 3. Criterios de Aceptación del Plan (AC1-AC16)

| AC | Descripción | Fase | Artefacto | Clave |
|----|-------------|------|-----------|-------|
| AC1 | Acta existe en `v4_audit/` con veredicto legible | T1 | `acta_revision.json` | `verdict` |
| AC2 | Tier B/C → máximo `APROBADO-CONDICIONAL-PENDING-ONBOARDING` | T1 | `acta_revision.json` | `verdict` + `evidence_tier` |
| AC3 | `acta_revision.md` legible con 6 cláusulas P6 | T1 | `acta_revision.md` | secciones P6.1-P6.6 |
| AC4 | Juez alimenta UNA ruta de bloqueo, no añade cuarta | T1 | `main.py` | grep: una llamada a tribunal |
| AC5 | `revision_diagnostico.json` con `findings[]` | T2-A | `revision_diagnostico.json` | `findings` |
| AC6 | Bot 1 marca recall vacuo | T2-A | `revision_diagnostico.json` | `finding_type == "VACUOUS_RECALL"` |
| AC7 | `revision_assets.json` con `coverage_by_service[]` | T2-B | `revision_assets.json` | `coverage_by_service` |
| AC8 | Bot 3 señala `IMPLEMENTATION_ORDER.md` vacío (plantilla sin contenido por-hotel) | T2-B | `revision_assets.json` | `finding_type == "EMPTY_DELIVERY_TEMPLATE"` |
| AC9 | `revision_alineacion.json` con `service_matrix[]` | T4-A | `revision_alineacion.json` | `service_matrix` |
| AC10 | Promesa verbal sin matriz → `PROMESA-SIN-MATRIZ` | T4-A | test output | assertion `status` |
| AC11 | `revision_honestidad.json` con `findings[]` | T4-B | `revision_honestidad.json` | `findings` |
| AC12 | Bot 4 detecta CG-WHATSAPP-LEAD del archivo diagnóstico | T4-B | `revision_honestidad.json` | `cg_reference` |
| AC13 | Acta + 6 cláusulas en output E2E real | E2E | `acta_revision.json` | `clauses_evaluated` == 6 |
| 14 | AC14 | Los 4 reportes de revisión existen en `v4_audit/` | E2E | directorio | 4 archivos presentes |
| 15 | AC15 | S-E2: `generate_proposal=False` no lanza NameError | T2-C | sonda/test output | assertion |
| 16 | AC16 | S9: `INVALID_MAPPINGS` pasa test de contrato | T2-C | test output | assertion |

---

## 4. No-Regresiones (NR)

| NR | Invariante | Verificación |
|----|-----------|--------------|
| NR1 | `passed_post = passed_pre + tests nuevos de ESTA fase` (R2.3) | Par `*_baseline_pre.txt` / `*_baseline_post.txt` en `evidence/FASE-X/` |
| NR2 | `skipped_post == skipped_pre` | Idem |
| NR3 | `run_all_validations.py --quick` TOTAL PASS | Cada fase |
| NR4 | El tribunal NO reimplementa lógica de gates (regla arquitectónica) | Grep: no importa `publication_gates.py` internals |
| NR5 | Coherence del output E2E ≥ 0.80 (no regresión del pipeline) | `asset_generation_report.json` clave `coherence_score_final` |

---

## 5. FASE-VERIFY — Criterios de activación (§4.6)

| Criterio | ¿Se cumple? |
|----------|-------------|
| ≥3 fases de implementación | ✅ (T1, T2-A, T2-B, T2-C, T4-A, T4-B, E2E = 7) |
| Al menos una fase con ejecución E2E | ✅ (FASE-E2E: v4complete) |
| ACs que cruzan múltiples fases | ✅ (AC1-AC4 en T1 pero verificados en E2E; AC13-AC16 cruzan T1-T4-C) |

**Resultado**: FASE-VERIFY INCLUIDA.

---

## 6. Versión

- **4.76.0**: Tribunal offline (T1/T2/T4) — Juez certificador + 4 revisores + acta dual + integración main.py + limpieza de residuos heredados (S-E2, S9).
