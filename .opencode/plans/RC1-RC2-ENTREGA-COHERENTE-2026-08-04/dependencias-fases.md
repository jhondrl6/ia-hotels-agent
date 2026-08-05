# Dependencias de Fases — RC1-RC2-ENTREGA-COHERENTE-2026-08-04

> Actualizado: 2026-08-05 (FASE-E completada)

## Diagrama de Dependencias

```
FASE-A (triage tests patológicos)
   │  PREREQUISITO de B (los tests del área propuesta son los patológicos)
   ▼
FASE-B (RC1 — parametrización propuesta) ◄── MAYOR COMPLEJIDAD
   │
   ▼
FASE-C (RC2-a — gates N11/N15)
   │  (C no depende de B a nivel código, pero B primero por severidad ALTA
   │   y porque el run E2E verifica ambos)
   ▼
FASE-D (RC2-b — ZIP/S7/S5)  ←── tracks independientes internas (delegate_task)
   │
   ▼
FASE-E (RC3 — higiene documental)  ←── independiente de B/C/D a nivel código;
   │                                    va después para reflejar estado final
   ▼
FASE-F (E2E v4complete Zione + análisis post-implementación)
   │  requiere: A ✅ B ✅ C ✅ D ✅ (E puede estar en progreso,
   │  pero los fixes de código deben estar cerrados)
   ▼
FASE-RELEASE-4.71.0 (requiere A-F ✅)
```

## Tabla de Conflictos de Archivos

| Archivo | Fases que lo tocan | Conflicto |
|---------|--------------------|-----------|
| `modules/commercial_documents/v4_proposal_generator.py` | FASE-B | Ninguno (solo B) |
| `modules/commercial_documents/pain_solution_mapper.py` | FASE-B (lectura para mapa inverso) | Ninguno (solo lectura) |
| `modules/quality_gates/commercial_gate.py` | FASE-C | Ninguno (solo C) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | FASE-C | Ninguno (solo C — cableado tier) |
| `modules/delivery/delivery_packager.py` | FASE-D | Ninguno (solo D) |
| `main.py` (loader onboarding) | FASE-D (S7) | Ninguno |
| `modules/financial_engine/harness_handlers.py` L118 (occupancy label) | FASE-D (S5) | Ninguno |
| `pytest.ini` / `tests/_archived_broken_tests/` | FASE-A | Ninguno |
| `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/*` | FASE-E | Ninguno (solo MD) |
| `scripts/run_all_validations.py` | FASE-E (nuevo check `_check_prompts_no_release`) | Ninguno (solo E; stdlib-only, sin imports del proyecto) |
| CHANGELOG / VERSION / GUIA_TECNICA / AGENTS | FASE-RELEASE | Ninguno (solo RELEASE edita versión) |
| `tests/commercial_documents/test_*propuesta*` | FASE-B (nuevos), FASE-A (triage) | A aisla patológicos ANTES de que B agregue tests → sin conflicto por orden |

**Conclusión**: sin conflictos de archivos entre fases gracias al orden A→B→C→D→E→F.
No hay dos fases tocando el mismo archivo.

## Estados

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ✅ Completa | 2026-08-05 | Cuarentena 3 archivos (40 tests). Lista segura: 13 archivos PASS. Ver notas. |
| FASE-B | ✅ Completa | 2026-08-05 | RC1: tabla de servicios parametrizada desde opportunity_scores (N10/N17/N18/N19). 9 tests nuevos. Ver notas. |
| FASE-C | ✅ Completa | 2026-08-05 | RC2-a: CG-CLAIM-VS-EVIDENCE sin falsos positivos condicionales + CG-TIER-CONSISTENCY cableado (N11/N15). 20 tests nuevos. |
| FASE-D | ✅ Completa | 2026-08-05 | RC2-b: ZIP sin gate reports (N16) + filtro run (N21) + fallback loader (S7) + occupancy label (S5). 23 tests nuevos. |
| FASE-E | ✅ Completa | 2026-08-05 | RC3: prompts sin --release + enforcement `_check_prompts_no_release` + conteos fuente viva + evidencia N3 preservada. Delegable (solo docs). |
| FASE-F | ⬜ Pendiente | — | 1 solo v4complete (Zi One Luxury) |
| FASE-RELEASE-4.71.0 | ⬜ Pendiente | — | Delegable |

## Notas de Recuperación

- Si una fase queda ⏳ INCOMPLETA: registrar aquí checkpoint + qué falta + timestamp.
- La sesión siguiente lee esta tabla y continúa desde el checkpoint (no re-ejecuta lo ya hecho).

## Notas FASE-A

### Archivos en cuarentena (2026-08-05)
- `tests/_archived_broken_tests/commercial_documents/test_proposal_generator.py` (32 tests) — fuga memoria ~8GB
- `tests/_archived_broken_tests/commercial_documents/test_price_consistency.py` (4 tests) — cuelgue indefinido
- `tests/_archived_broken_tests/commercial_documents/test_proposal_generator_dict.py` (4 tests) — 16/38 fallos preexistentes
- `pytest.ini` actualizado con `--ignore` específicos (NO `norecursedirs` global — CR-8)
- Tests collected: 3215 → 3175 (diferencia exacta: 40 tests)

### Lista segura de tests del área propuesta (FASE-B puede correr estos)
| Archivo | Resultado |
|---------|-----------|
| `test_financial_coherence.py` | 11 passed ✅ |
| `test_fase_f_financial_placeholders.py` | 15 passed ✅ |
| `test_pain_solution_mapper.py` | 5 passed ✅ |
| `test_data_structures.py` | 4 passed ✅ |
| `test_coherence_generated_assets.py` | PASS ✅ |
| `test_precision_rendering.py` | PASS ✅ |
| `test_diagnostic_generator.py` | PASS ✅ |
| `test_diagnostic_brechas.py` | PASS ✅ |
| `test_template_conditionals.py` | PASS ✅ |
| `test_aeo_score.py` | PASS ✅ |
| `test_iao_score.py` | PASS ✅ |
| `test_proposal_fase4_h3_h4.py` | PASS ✅ |
| `test_hook_pdf_generator.py` | PASS ✅ |

### Archivos con fallos preexistentes (NO patológicos, solo aserciones)
- `test_proposal_confidence_disclosure.py`: 5 failed (fallos de aserción, no cuelgues)
- `test_proposal_dynamic.py`: 7 failed (fallos de aserción, no cuelgues)

## Notas FASE-B

### Cambios implementados (2026-08-05)
- `v4_proposal_generator.py`:
  - NUEVO `_build_dynamic_breach_map()`: mapa inverso asset_type → brecha viva del run
    (inversión de `pain_solution_mapper.PAIN_SOLUTION_MAP` + candidatos auditados por
    servicio; desempate multi-brecha por rank presente en opportunity_scores).
  - ELIMINADO `BREACH_BY_ASSET` estático (N10: costos factor 0.671×; N17: mapeo invertido).
  - ELIMINADO hardcode "Brecha #5: WhatsApp no coincide" (N18) → rank/label/costo vivos.
  - org_schema condicional sin cifras cuando `no_org_schema` no está en scores (N19).
  - Fallback explícito: sin opportunity_scores → tabla sin costos + warning (nunca inventa).
  - Nuevo parámetro `opportunity_scores` en `generate()` / `_prepare_template_data()` /
    `_generate_dynamic_services_table()`.
- `main.py` (FASE 3.5): calcula `opportunity_scores` vía
  `diagnostic_gen._compute_opportunity_scores()` y los pasa a `proposal_gen.generate()`.
- Backup forense: `temp/rc1_backup/v4_proposal_generator.py` (conservar hasta FASE-F).

### Evidencia (evidence/FASE-B/)
- `verify_breach_consistency_static.py` + salida: PASS contra run 20260804_124443
  (5 services con costo vivo, 2 sin costo, N17/N18 corregidos).
- `fase_b_test.txt`: 9 tests nuevos PASS.
- `fase_b_safe1/2/3.txt`: lista segura FASE-A — 208 passed, 0 regresiones.
- `fase_b_preexist.txt`: fallos preexistentes estables (7 + 5, áreas no tocadas).

### Para FASE-C y siguientes
- La propuesta ya consume opportunity_scores; el run E2E de FASE-F debe mostrar
  costos/numeración IDÉNTICOS en diagnóstico y propuesta (check de cierre).
- `temp/rc1_backup/` NO eliminar hasta cierre de FASE-F.

## Notas FASE-C

### Cambios implementados (2026-08-05)
- `commercial_gate.py`:
  - `_CONDITIONAL_MARKERS`: regex compilado con marcadores condicionales (si, siempre que, en caso de, podría, etc.).
  - `_check_claim_vs_evidence`: split por oraciones + filtro doble (antes del match + en toda la oración). Factual claim → evaluar place_found + gbp_rating; condicional → descartar.
  - `_check_tier_consistency`: ambos inputs None → FAIL explícito (no pasa vacuo). Un input None → FAIL con mensaje del faltante.
- `v4_diagnostic_generator.py`:
  - `_extract_text_tier()`: método estático que extrae tier del texto (regex `Tier X` / `nivel X`).
  - Cableado `frontmatter_tier` y `text_tier` en la invocación de `validate_diagnostic()`.
- Backup forense: `temp/rc2_backup/commercial_gate.py` + `v4_diagnostic_generator.py`.

### Evidencia (temp/)
- `fase_c_test.txt`: 54 tests PASS (34 existentes + 20 nuevos).
- `fase_c_gates_all.txt`: suite quality_gates 322 passed / 1 skipped / 0 failed.
- `fase_c_diag.txt`: tests diagnóstico 63 passed / 0 failed.
- `fase_c_safe.txt`: lista segura FASE-A 145 passed / 0 failed.
- `fase_c_preexist.txt`: fallos preexistentes estables (12 = 7+5).

### Para FASE-E y siguientes
- CG-TIER-CONSISTENCY ahora valida inputs reales; el run E2E debe mostrar comparación de tier (no "Sin datos").
- CG-CLAIM-VS-EVIDENCE ya no dispara falso positivo con texto condicional del diagnóstico.
- `temp/rc2_backup/` NO eliminar hasta cierre de FASE-F.

## Notas FASE-D

### Cambios implementados (2026-08-05)
- `delivery_packager.py`:
  - `_is_excluded_from_zip()`: excluye `commercial_gates_report*` del ZIP de cliente (N16).
  - `_get_latest_run_timestamp()`: cutoff basado en el run más reciente en v4_audit, no 24h fijo (N21).
  - `_collect_files()`: integra ambos filtros + log de exclusiones.
- `main.py`:
  - Fallback de loader onboarding: si `{--output}/clientes` no tiene YAML → intenta `output/clientes` (S7).
- `harness_handlers.py`:
  - Label de occupancy respeta prioridad de `"onboarding"` sobre `"regional"` (S5).
  - `HotelFinancialData` fallback recibe `occupancy_source` correctamente.
- Backup forense: `temp/fase_d_backup/` (3 archivos originales).

### Evidencia (temp/)
- `fase_d_delivery.txt`: 10 tests nuevos FASE-D delivery PASS.
- `fase_d_financial.txt`: 6 tests nuevos FASE-D occupancy PASS.
- `fase_d_loader.txt`: 7 tests nuevos FASE-D loader PASS.
- `fase_d_delivery_all.txt`: suite completa delivery 69 passed, 0 failed.
- `fase_d_safe.txt`: batch seguro 61 passed + 2 preexistentes estables (TestRecoveryFactorROI).
- `fase_d_quality.txt`: quality_gates 366 passed / 1 skipped / 0 failed.
- `fase_d_preexist.txt`: fallos preexistentes estables (12 = 7+5).
- `fase_d_validations.txt`: 5/5 TOTAL PASS.

### Para FASE-F y siguientes
- El ZIP ya no transporta `commercial_gates_report*` al cliente.
- El loader de onboarding tiene fallback a `output/clientes` si `--output` apunta a ruta alternativa.
- `breakdown.data_sources.occupancy` es coherente con la fuente real (onboarding > regional > default).
- `temp/fase_d_backup/` NO eliminar hasta cierre de FASE-F.

## Notas FASE-E

### Cambios implementados (2026-08-05)
- `.opencode/plans/COHERENCIA-MODULO-ENTREGA-2026-08-03/0{2,3,4,5}-prompt-*.md`:
  - Eliminado `--release 4.70.0` de los 4 prompts intermedios (R3.1).
  - Añadida nota "⚠️ NO usar `--release` en fases intermedias (L3/L9) — solo en FASE-RELEASE".
  - Verificación: grep `log_phase_completion.*--release` en los 4 archivos → 0 hits.
- `scripts/run_all_validations.py`:
  - Nuevo método `_check_prompts_no_release()`: escanea `0[2-5]-prompt*.md` en `.opencode/plans/` buscando `--release` en comandos `log_phase_completion.py`. Excluye Archives, RELEASE, y referencias documentales.
  - Registrado en `run_all()` tras `_check_document_integration` (ejecuta en `--quick`).
  - Verificación: `run_all_validations.py --quick` → 6/6 TOTAL PASS.
- `.opencode/plans/RC1-RC2-ENTREGA-COHERENTE-2026-08-04/09-documentacion-post-proyecto.md`:
  - Conteos fuente viva: 205 .py, 391 clases, 27 dirs __init__, 3,227 tests collected.
  - Lista D3 completa (8 valores, incluye 2º $1,198,906 de low_seo_score).
- `evidence/N3-diff/`: 14 JSON del run 123637 preservados + README (diff 97 líneas no reproducible).
- `.opencode/context/...CONTEXT-...-2026-08-04.md`: cita `_coverage_gate` → L1160 confirmada.

### Evidencia (evidence/N3-diff/)
- 14 archivos JSON del run 123637/123636 (gate_report, commercial_gates, schemas, metadata).
- README.md explicando la no-reproducibilidad del diff de 97 líneas (N20).

### Para FASE-F y siguientes
- `run_all_validations.py --quick` ahora incluye 6 checks (5 existentes + "Prompts No Release").
- El enforcement anti `--release` es permanente: cualquier plan futuro con `--release` en prompts intermedios será detectado.
- La evidencia N3 está preservada para referencia histórica.
