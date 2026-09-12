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
| `modules/quality_gates/tribunal/` | `artifact_paths.py` | Resolución compartida de rutas de artefactos (propuesta en `v4_complete/`, timestamped por mtime). Una sola fuente para los revisores; consumida por `honesty_reviewer.py` y `alignment_reviewer.py` | T4-B (remediación R1) |
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
| Revisión de honestidad | `tribunal/honesty_reviewer.py` | P6.5: sobre-presentación vs tier labels + CG-* de ambos archivos (12 entradas = 10 gate_ids distintos). Divulgación de WARNINGs por frases que nombran el problema (`DISCLOSURE_PHRASES_BY_GATE`), tier del MANIFEST propagado al acta y extractor obligatorio (P6.5 liberada tras D-T1.3 opción a) | T4-B (+ remediación R1/R6/R8) |
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
| Tests nuevos (tribunal T4-B) | 7 (HonestyReviewer) | T4-B |
| Tests de la remediación D-T4B-A1 | 22 (7 retro sobre baseline real + 4 contrato de ubicación + 11 fidelidad de salida) | T4-B (remed.) |
| Tests totales tribunal acumulados | 92 al cierre de T4-B (17 T1 + 10 T2-A + 12 T2-B + 18 T2-C + 28 T4-A + 7 T4-B) → **114** tras la remediación | T4-B (remed.) |
| Tests colectados post-T4-A | 4,018 (3,990 T2-C + 28 T4-A) | T4-A |
| Tests colectados post-remediación D-T2C-A1 | 4,029 (4,018 + 11) | T2-C (remed.) |
| Tests colectados post-T4-B | **4,036** (4,029 + 7). ⚠️ Rectificado: la fase registró 4,025 partiendo de 4,018, lo que omitía los +11 de D-T2C-A1 y no coincide con `pytest tests/ --collect-only -q` | T4-B |
| Tests colectados post-remediación D-T4B-A1 | **4,058** (4,036 + 22); `passed` 3,998 → 4,020 | T4-B (remed.) |
| Tests totales post-plan | — (E2E añade 0 tests; 4,058 colectados sin cambio) | E2E |
| Coherence output E2E | **0.83** (`coherence_score_final`; gate coherence PASS 0.8333 ≥ 0.80 — NR5; baseline FASE-D 0.88, delta −0.05) | E2E |
| Veredicto del Juez (Salento Real) | **APROBADO-CONDICIONAL-PENDING-ONBOARDING** (exit 0; ZIP creado; 13/13 gates). ⚠️ El acta lee `evidence_tier: C` (el Juez corre antes del packaging; MANIFEST real = B) — primer piso aplica igualmente | E2E |
| Cláusulas P6 evaluadas | 6, de las cuales 4 certificables por T1 (`P6.1`, `P6.3`, `P6.4`, `P6.6`); `P6.2` diferida a T4-A; `P6.5` liberada para T4-B tras D-T1.3 opción (a) — primer piso → `first_floor_rule`. En la corrida E2E P6.2/P6.5 siguen `NOT_EVALUABLE` en el acta (diseño T1: el Juez no consume `reviewer_reports`; ver L-E2E.3 en `10-analisis`), pero los 4 `revision_*.json` SÍ existen y sus recomendaciones quedan registradas | T1 / T4-B / E2E |
| Archivos nuevos en `v4_audit/` | 2 (`acta_revision.json`, `acta_revision.md`) | T1 |
| Archivos nuevos en `v4_audit/` (T2-A) | 1 (`revision_diagnostico.json`) | T2-A |
| Archivos nuevos en `v4_audit/` (T2-B) | 1 (`revision_assets.json`) | T2-B |
| Archivos nuevos en `v4_audit/` (T4-A) | 1 (`revision_alineacion.json`) | T4-A |
| Archivos nuevos en `v4_audit/` (T4-B) | 1 (`revision_honestidad.json`) — ✅ **producido en FASE-E2E** (corrida 2026-09-11): los 4 `revision_*.json` existen en output real tras el cableado Q1/Vía A (commit `7e1bbc3`) | T4-B / E2E |
| Hallazgos del tribunal en la corrida E2E | Bot 1: 1 CRITICAL (recall vacuo, `details: {}` real) → BLOQUEAR · Bot 2: 0 findings, 4/4 ALINEADO → APROBADO · Bot 3: 4/4 CON-ASSET (coverage 1.0) + 1 WARNING P12 → APROBADO · Bot 4: 1 CG_WARNING_UNDISCLOSED (`CG-WHATSAPP-LEAD`, AC12 en artefacto real) → DEVOLVER-PRUEBAS · Juez: condicional (no consume reportes — diseño T1) | E2E |
| **Certificación FASE-VERIFY** | **AC1-AC16: 15 ✅ + 1 ❌ (AC8** — `EMPTY_DELIVERY_TEMPLATE` no detectado en régimen real ZIP-only; causa raíz fijada por sonda read-only, routed a seguimientos, D-V.4**)**. ACs propuestos (dueño VERIFY): AC17 ✅ (D-V.2 corrige nota E2E: `breakdown.evidence_tier: B` sí existe) / AC18 ✅ / AC19 ⚠️ (dos bases de pérdida). Greps residuales 0 matches en 4/4. NR4 ✅ · NR5 ✅ (coherence 0.83). Delta verificado: +6 artefactos tribunal, `is_coherent` false→true, `no_breach` 6→0. **VERIFY añade 0 tests y 0 cambios de código** | VERIFY |
| Suite completa en el corte de RELEASE | **4,024 passed / 3 failed / 31 skipped / 4 xfailed** en 156 s. Los 3 fallos son exactamente los preexistentes de `aba517a` (`test_function_default_flags` flaky, `test_barreda_un_solo_emisor_de_la_clave` → deuda D-V.1, `test_diagnostic_includes_geo_metrics`) → **0 regresiones** | RELEASE |
| Conteo post-plan | **4,063** funciones por el método canónico (`grep -rE "^\s*def test_" tests --include=*.py`) / **4,061** colectadas sobre **293** archivos `test_*.py`. Delta comparable en la misma base: **3,944 → 4,061 colectados = +117** (114 del tribunal + 3 del fix de `doctor.py`) | RELEASE |
| Ceguera documental curada | `scripts/doctor.py` leía `VERSION.yaml` sin encoding explícito (defecto desde `082c9e1`) → `--status` y `--regenerate-domain-primer` fallaban y `.agent/SYSTEM_STATUS.md` + `.agent/knowledge/DOMAIN_PRIMER.md` llevaban **sin regenerarse desde v4.75.0**. Fix + 3 tests que anclan la lectura UTF-8 | RELEASE |
| Auditoría E8b (README/AGENTS) | Correcciones medidas: banner del README a 11-Sep, paso 5 "Certifica" + acta del tribunal, `modules/` 24→**23** directorios y `tests/` 25→**24** subdirectorios (21 con pruebas); AGENTS.md: conteo 4,060→4,063 con filas que cuadran exactamente, +fila de `tribunal/`, +árbol `tribunal/` | RELEASE |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | Integración del Juez junto a `delivery_quality_report`; la decisión del ZIP consume `blocks_delivery_zip(acta)` en lugar de comparar strings de veredicto | T1 |
| `main.py` | Cableado de los 4 revisores del tribunal tras el packaging (FASE 7) — Q1/Vía A: extractor LLM compartido (`LLMPromiseExtractor`) + never-block por Bot; revisan MANIFEST/ASSETS de la corrida actual | E2E |
| `main.py` | S-E2: `site_presence_report` fuera del bloque condicional (o guard en el consumidor) | T2-C |
| `modules/commercial_documents/v4_proposal_generator.py` | S-E2: guard de `presence_lookup` corregido (dict canónico + dataclass) — reactiva consumidores; desvío D-T2C-A1 | T2-C |
| `modules/asset_generation/v4_asset_orchestrator.py` | S-E2: retiro de instanciación muerta | T2-C |
| `modules/quality/asset_semantics_validator.py` | S9: SIN cambios de código — contrato certificado por `test_invalid_mappings_valida_contra_capa1` (preexistente) | T2-C |
| `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` | 7 tests de contrato S-E2 (presence_lookup canónico + hoist); +11 tests `TestPresenceLookupLiveConsumers` (remediación D-T2C-A1, métodos reales, 2026-09-11) = 18 | T2-C |
| `evidence/FASE-T2-C/baseline-pre-post.md` | Baseline pre/post: 3,983→3,990 tests, AC15/AC16/NR1-NR4 | T2-C |
| `evidence/FASE-T2-C/evidencia-final.md` | Diff completo + resumen + métricas + lecciones | T2-C |
| `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/` | `MATRIZ-CERTIFICACION.md` (matriz firmada AC1-16 + AC17-19 + delta + greps), `verify_probe_ac8.py`/`_out.txt` (sonda read-only causa raíz AC8), `greps_residuales.txt` (0/4), `grep_ac4_main.txt`, `baseline_delta_greps.txt`, `verify_tests_tribunal.txt` (123 passed) | VERIFY |
| `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/{10-analisis,06-checklist,dependencias-fases,README}.md` | Matriz de verificación completa + 4 lecciones L-V.1–.4 + decisiones D-V.1–D-V.4 + seguimientos (AC8 ❌, barreda D-V.1, §5.1/§5.4/§5.5, executor D-V.3) + estado 8/9. **Cero código de producción** | VERIFY |
| `AGENTS.md` | Nuevo módulo `tribunal/` en tabla de Módulos Activos | RELEASE |
| `modules/quality_gates/tribunal/__init__.py` | Export de `HonestyReviewer` (import + `__all__`) — contrato de `dependencias-fases.md` que T4-B no había cumplido (R2) | T4-B (remed.) |
| `modules/quality_gates/tribunal/alignment_reviewer.py` | `_load_proposal` delega en el resolutor compartido: T4-A arrastraba el mismo defecto de ubicación (R1) | T4-B (remed.) |
| `modules/quality_gates/tribunal/honesty_reviewer.py` | R1 (rutas), R6 (`DISCLOSURE_PHRASES_BY_GATE`), R8 (conteos, tier propagado, `Path` resuelto una vez, `all_gates` reducido), R3.2 (extractor obligatorio) | T4-B (remed.) |
| `tests/quality_gates/tribunal/test_honesty_reviewer_retro_reales.py` | 7 tests retro sobre `output/FASE-D_salentoreal_post_guard/`, con skip si falta el baseline (R1.2) | T4-B (remed.) |
| `tests/quality_gates/tribunal/test_tribunal_propuesta_ubicacion.py` | 4 tests del contrato de **ubicación** de la propuesta (R1) | T4-B (remed.) |
| `tests/quality_gates/tribunal/test_honesty_reviewer_fidelidad_salida.py` | 11 tests de fidelidad de salida y contrato NR4 (R6/R8/R9) | T4-B (remed.) |
| `evidence/FASE-T4-B/rectificacion-NR1.md` + `tests_baseline_pre_T4B_fase_real.txt` + `tests_baseline_post_T4B_remediacion.txt` | Recomposición de NR1 con baseline medido; el par original se conserva intacto (R4) | T4-B (remed.) |
| `.opencode/plans/TRIBUNAL-OFFLINE-2026-09-09/{06,09,10,README,dependencias-fases}.md` | Correcciones factuales de R5, estado ⚠️ de T4-B, decisiones DA-T4B.1–.6 (Q1–Q4) | T4-B (remed.) |
| `VERSION.yaml` | 4.75.0 → 4.76.0 + codename "Tribunal certificador P6+P7" + release_date 2026-09-11 + bloque de comentarios por fase | RELEASE |
| `CHANGELOG.md` | Entrada `[4.76.0]` con formato CONTRIBUTING (Objetivo / Cambios Implementados / Archivos Nuevos / Archivos Modificados / Tests) | RELEASE |
| `docs/GUIA_TECNICA.md` | Header v4.76.0 + 5 bloques de nota técnica (uno por fase del tribunal y el RELEASE) | RELEASE |
| `README.md` | Auditoría E8b: fecha del banner, paso "Certifica" + acta del tribunal, conteos de directorios medidos, `quality_gates/tribunal/` en el árbol | RELEASE |
| `AGENTS.md` | Nuevo módulo `tribunal/` en Módulos Activos, conteo canónico 4,063 / 293 con filas que cuadran, árbol con `tribunal/`, fila de mejoras | RELEASE |
| `scripts/doctor.py` | Lecturas de `VERSION.yaml` y aledaños con encoding UTF-8 explícito — defecto preexistente desde `082c9e1` | RELEASE |
| `tests/test_doctor_reads_are_utf8_pinned.py` | 3 tests nuevos que anclan la lectura con encoding explícito | RELEASE |
| `.agent/SYSTEM_STATUS.md` · `.agent/knowledge/DOMAIN_PRIMER.md` | Regenerados por `doctor.py` — imposibles desde v4.75.0 por el defecto de encoding | RELEASE |
| `docs/contributing/REGISTRY.md` | Entrada FASE-RELEASE-4.76.0 (477 fases) | RELEASE |
| `.cursorrules` · `docs/CONTRIBUTING.md` | Sincronizados desde VERSION.yaml por `sync_versions.py` | RELEASE |

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
