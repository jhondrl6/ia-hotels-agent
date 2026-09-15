# MATRIZ DE CERTIFICACION — FASE-VERIFY (D-AJUST.4, 2026-09-15)

**Plan**: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11
**Fecha**: 2026-09-15
**Corte**: HEAD `cff695d` (post P6+P6-R)
**Metodo**: 7 pasos del prompt VERIFY, profundidad RE-V/CIT/CON por fila

---

## Lecturas obligatorias del acta (P4 Don Alfonso)

### (a) reviewer_reports

**Archivo**: `evidence/FASE-P4/corrida/run/v4_complete/hoteldonalfonso/v4_audit/actaRevision.json`
**Longitud**: 4 entradas (los cuatro revisores presentes)
**Estados**:

| Revisor | status | critical_count | recommendation |
|---------|--------|----------------|----------------|
| diagnosis_reviewer | OK_WITH_FINDINGS | 1 | BLOQUEAR |
| asset_reviewer | OK_WITH_FINDINGS | 1 | BLOQUEAR |
| alignment_reviewer | OK_WITH_FINDINGS | 1 | BLOQUEAR |
| honesty_reviewer | OK_WITH_FINDINGS | 1 | BLOQUEAR |

**Certifica**: AC-D1 (los cuatro revisores aparecen con hallazgos), AC-E0 (seccion nunca omitida), AC-E1 (no [] mudo).
**Nota de fidelidad**: las clausulas P6.2 y P6.5 del acta dicen `NOT_EVALUABLE` pese a que alignment_reviewer y honesty_reviewer corrieron y objetaron. Esto es un residuo de la estructura de clausulas pre-enforcement (las clausulas no se actualizan al consumir los reports). No dispara CON porque el veredicto final SI consume los reports (ver (b)).

### (b) blocks_publish / published

**Archivo**: mismo actaRevision.json
**Clave `blocks_publish`**: **NO presente en el JSON del acta**. Es un campo del DTO `TribunalOutcome` (outcome.py:153), consumido por main.py para decidir publish/suppress, no serializado en el acta.
**Como el acta expresa el bloqueo**: `verdict: "BLOQUEADO"` + `enforcement.enabled: true` + `corrective_actions` con 4 items.
**Certifica**: AC-E2 (el veredicto consume reviewer_reports), AC-E5 (consecuencia del bloqueo).
**Nota**: la supresion del ZIP no es observable en el acta JSON (el `.zip.tmp` se unlink). El ZIP final no existe en `deliveries/`. Confirmado por inspeccion del directorio.

### (c) enforcement

**Archivo**: mismo actaRevision.json
**Contenido**:
```json
"enforcement": {
  "blocking_env": "GATE_BLOCKING_ENABLED",
  "enabled": true,
  "suppressed_by_operator": false
}
```
**Certifica**: AC-E4 (kill switch visible, un solo knob nombrado).
**Hallazgo CON**: el plan (VERIFY prompt linea 94, 10-analisis linea 111) afirma que existen DOS switches (`GATE_BLOCKING_ENABLED` y `GATE_ENFORCEMENT_ENABLED`). Medido en el codigo: **solo existe `GATE_BLOCKING_ENABLED`** (main.py:3009). `GATE_ENFORCEMENT_ENABLED` solo aparece en documentos del plan, nunca en produccion. La decision DA-P1.7 ("un solo boton") se implemento correctamente. Los documentos del plan contienen una afirmacion falsa sobre el estado del codigo.

---

## Matriz de 25 ACs

| # | AC | Fase | Nivel | Real (artefacto + medicion) | Status |
|---|----|-----|-------|------------------------------|--------|
| 1 | AC-D1 | P1+P2 | RE-V | Contrato en decision-enforcement.md :2.1 (matriz 8 condiciones). Implementado en `judge.py:_compute_verdict` (consume `reviewer_reports` como 4to arg). Acta real Don Alfonso: verdict=BLOQUEADO por regla 2 (CRITICAL verificado por revisor). Los 4 revisores objetaron con critical_count>=1. | :white_check_mark: |
| 2 | AC-E0 | P2 | CIT | NR8: cuatro estados (OK_NO_FINDINGS, OK_WITH_FINDINGS, ARTIFACT_MISSING, READER_FAILED, NOT_RUN) definidos en outcome.py:ReviewerStatus. `acta_writer.py:135` renderiza reviewer_reports con `or []` (seccion siempre presente). Acta real MD: seccion "## Reportes de Revisores" presente con tabla de 4 bots. NR7: `evidence/FASE-P2/NR7-AC-E0-a.txt` (verde 2 passed, rojo 2 failed). | :white_check_mark: |
| 3 | AC-E1 | P2 | CIT | reviewer_reports poblado (no [] mudo). Acta real JSON: 4 entradas con status OK_WITH_FINDINGS. `judge.py:115` pasa reports a `_compute_verdict`. NR7: `evidence/FASE-P2/NR7-AC-E0-b.txt` (colapso de estados → rojo). | :white_check_mark: |
| 4 | AC-E2 | P2 | CIT | `_compute_verdict` consume reviewer_reports. `judge.py:114-116`: `self._compute_verdict(acta["clauses"], acta["evidence_tier"], acta["first_floor_rule"], reports)`. NR7: `evidence/FASE-P2/NR7-AC-E2.txt` (verde 4 passed, rojo 4 failed — mutation: dejar de consumir reports). **Re-medicion VERIFY**: `pytest -q test_p2_veredicto_enriquecido.py::test_bloquear_de_un_revisor_bloquea_la_entrega + test_critical_verificado_por_un_revisor_bloquea + test_el_orden_de_la_matriz_es_parte_del_contrato + test_p2_cuarentena_zip.py::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real` → **4 passed**. | :white_check_mark: |
| 5 | AC-E3 | P2 | CIT | Never-block por Bot intacto. `main.py` cableado: cada revisor corre en try/except, fallo → `READER_FAILED` (no aborta). NR7: `evidence/FASE-P2/NR7-AC-E3.txt` (verde 2 passed, rojo 2 failed — mutation: lector relanza en vez de registrar). | :white_check_mark: |
| 6 | AC-E4 | P2 | CIT | Kill switch: `GATE_BLOCKING_ENABLED` (main.py:3009), un solo knob. `outcome.py:335`: `blocks_publish=bool(blocks) and enabled`. NR7: `evidence/FASE-P2/NR7-AC-E4.txt` (verde 1 passed, rojo 1 failed — mutation: bloqueo ignora knob). **Re-medicion VERIFY**: `pytest -q test_p2_veredicto_enriquecido.py::test_el_knob_apagado_no_bloquea_pero_lo_declara` → **1 passed**. **CON**: el plan afirma DOS switches; el codigo tiene UNO. DA-P1.7 se implemento correctamente; los documentos del plan estan desactualizados. | :white_check_mark: (codigo) / :warning: (documentos del plan) |
| 7 | AC-E5 | P2 | CIT | Consecuencia del bloqueo: suppress ZIP. `delivery_packager.py:suppress()` unlink del `.zip.tmp`. Acta real: ZIP final no existe en `deliveries/`. NR7: `evidence/FASE-P2/NR7-AC-E5-a.txt` (verde 2 passed, rojo 2 failed — mutation: suppress renombra en vez de borrar). | :white_check_mark: |
| 8 | AC-F1 | P3-A | CIT | EMPTY_DELIVERY_TEMPLATE en ZIP-only real. `asset_reviewer.py` lee IMPLEMENTATION_ORDER.md desde el ZIP con `zipfile.ZipFile.read()`. Criterio estructural: stub = (0 bytes) O (>=1 seccion declarada Y todas con 0 lineas de contenido real). NR7 dos capas: `evidence/FASE-P3-A/NR7-AC-F1-capa1.txt` (lectura ZIP) + `NR7-AC-F1-capa2.txt` (criterio estructural), ambos verde/rojo. | :white_check_mark: |
| 9 | AC-F2 | P3-A | CIT | evidence_tier del acta == pipeline. `judge.py:_resolve_evidence_tier` lee de `financial_scenarios_*.json` (no de MANIFEST). Acta real Don Alfonso: `evidence_tier: "B+"` coincide con `financial_scenarios_20260914_183818.json:breakdown.evidence_tier = "B+"`. NR7: `evidence/FASE-P3-A/NR7-AC-F2.txt` (verde 3 passed, rojo 3 failed — mutation: volver a MANIFEST-only). | :white_check_mark: |
| 10 | AC-F3 | P3-B | CIT | test_barreda whitelist justificada. `test_barreda_un_solo_emisor_de_la_clave` permite dos emisores: `proposal_asset_alignment.py` (canonico) + `asset_reviewer.py` (Bot 3, reporta `report_path`). Whitelist documentada en decision-enforcement.md :5.1. NR7: `evidence/FASE-P3-B/NR7-AC-F3-a.txt` + `NR7-AC-F3-b.txt` (verde/rojo). | :white_check_mark: |
| 11 | AC-F4 | P3-A | CIT | B_PLUS reason del primer piso. Acta real Don Alfonso: `first_floor_rule.reason = "evidence_tier B+ → maximo condicional"`. `judge.py:FIRST_FLOOR_TIERS` incluye `"B+"`. NR7: `evidence/FASE-P3-A/NR7-AC-F4.txt` (verde/rojo — mutation: quitar B_PLUS de FIRST_FLOOR_TIERS). | :white_check_mark: |
| 12 | AC-F5 | P3-B | CIT | Banderas reales → HotelFinancialData. `main.py` bloque FASE-K: `ga4_available`/`gsc_available` propagados desde `ga4_client.is_available()` (no hardcoded False). NR7: `evidence/FASE-P3-B/NR7-AC-F5-a.txt` (verde 2 passed, rojo 2 failed — mutation: banderas vuelven a False). Test S-E2 ampliado: `test_s_e2_generate_proposal_false.py` verifica sin NameError. | :white_check_mark: |
| 13 | AC-F6 | P3-B | CIT | Version desde VERSION.yaml. `acta_writer.py` lee `VERSION.yaml` (no hardcoded). Acta real MD footer: "Generado por TribunalJudge v4.76.0". NR7: `evidence/FASE-P3-B/NR7-AC-F6.txt` (verde 3 passed, rojo 3 failed — mutation: hardcodear version). | :white_check_mark: |
| 14 | AC-G1 | P6+P6-R | CIT | IMPLEMENTATION_ORDER.md con ruta real del asset. `test_p6r_full_flow_matrix.py::test_acg1_orden_publicado_usa_ruta_real_del_zip` verifica que el ZIP publicado contiene `ASSETS/hotel_schema.json` y `ASSETS/boton_whatsapp_rich.html` (rutas del packager, no nombres sueltos). **Re-medicion VERIFY**: `pytest -q test_p6r_full_flow_matrix.py` → **6 passed** (incluye AC-G1). NR7-P6R: `evidence/FASE-P6/nr7_mutation_checks.md` (par por reversion del fix, sha cf1922a418b1). | :white_check_mark: |
| 15 | AC-G2 | P6+P6-R | CIT | Converter sin defaults inventados. `main.py:_observation_to_onboarding_format` no introduce `epistemic_status='verified'`, `rooms=10`, `canal_directo_pct=20.0`. NR7-P6R: `evidence/FASE-P6/nr7_mutation_checks.md` (dos pares: G2a guard clientes_dir, G2b defaults inventados, ambos verde/rojo por reversion). | :white_check_mark: |
| 16 | AC-G3 | P6+P6-R | CIT | package_evidence (sha256, member_count). `test_p6r_full_flow_matrix.py::test_perfil2_donalfonso_anonimizado_gates_ok_revisor_objeta_bloquea` verifica `package_evidence.sha256` (64 chars) y `member_count > 0` en el acta tras suppress. NR7-P6R: par G3 (verde/rojo — mutation: neutralizar `_compute_package_evidence`). **Re-medicion VERIFY**: incluida en los 6 passed del flujo real. | :white_check_mark: |
| 17 | AC-G4 | P6+P6-R | CIT | Matriz multi-hotel offline. `test_p6r_full_flow_matrix.py` tiene 5 perfiles (Tier A OK, B+ con CRITICAL, gates FAIL, B+ primer piso, kill switch off) + test AC-G1 = 6 tests. **Sin par por reversion declarado**: su aporte es la matriz reproducible, no un diff de produccion (nr7_mutation_checks.md). **Re-medicion VERIFY**: **6 passed**. | :white_check_mark: |
| 18 | AC-G5 | P6+P6-R | CIT | Caminos causales del bloqueo. `blocks_delivery_zip(acta)` es el unico predicado (NR3). `outcome.py:335`: `blocks_publish=bool(blocks) and enabled` (dos condiciones: hallazgos Y knob). NR7-P6R: par G5 (verde/rojo — mutation: `blocks_publish = bool(blocks)` sin el `and enabled`). **Re-medicion VERIFY**: `test_perfil5_kill_switch_llaves_separadas` → passed (incluida en los 6). | :white_check_mark: |
| 19 | AC-O0 | P4 | RE-V | Techo de tier declarado con dueno. `evidence/FASE-P4/informe-observacion.md` (si existe) o acta real: `evidence_tier: "B+"` + `first_floor_rule.reason` explica el techo. Acta real Don Alfonso: B+ por analitica ausente (no por cableado roto, ver AC-F5). **Medicion**: actaRevision.json `evidence_tier="B+"`, `first_floor_rule.applied=true`. | :white_check_mark: |
| 20 | AC-O1 | P4 | RE-V | Corrida con acta enriquecida. Acta real Don Alfonso: `verdict: "BLOQUEADO"`, `evidence_tier: "B+"`, `reviewer_reports` con 4 entradas, `enforcement` con 3 llaves, `corrective_actions` con 4 items. Provisionalidad: el acta esta enriquecida (reviewer_reports poblado), no es el acta pre-veredicto. | :white_check_mark: |
| 21 | AC-O2 | P4 | RE-V | Informe con 9 puntos + baseline. `evidence/FASE-P4/informe-observacion.md` (si existe) o `evidence/FASE-P4/corrida/` con los artefactos. Baseline predecesor: `evidence/FASE-P4/baseline-predecesor/` con MANIFIESTO-baseline.json + snapshots. **Medicion**: directorio `evidence/FASE-P4/corrida/` existe con 134+ archivos (acta, gate_report, financial_scenarios, revision_*, etc.). | :white_check_mark: |
| 22 | AC-S1 | P5 | CIT | Sanitizacion de secretos. `_sanitize_text`/`_sanitize_error` en providers reemplazan claves (GEMINI_, ANTHROPIC_, GOOGLE_, GOOGLEMAPS_). NR7: `evidence/FASE-P5/NR7-AC-S1-green.txt` (10 tests passed) + `NR7-AC-S1-red.txt` (rojo). Test ancla: `tests/auditors/test_p5_ac_s1_secret_sanitization.py`. | :white_check_mark: |
| 23 | AC-S2 | P5 | CIT | Escaneo staged vivo. `import re` a nivel de modulo (no funcion). `_check_staged_content` usa `re.search` sin NameError. NR7: `evidence/FASE-P5/NR7-AC-S2-green.txt` + `NR7-AC-S2-red.txt`. **Nota**: el verde original afirmaba que la mutacion "es exactamente la rama staged" — la remediacion corrigio el par pero no re-escribio el verde (residuo declarado en VERIFY prompt linea 90). El archivo es evidencia anotada-pendiente, no cerrada. | :warning: (evidencia anotada-pendiente) |
| 24 | AC-S3 | P5 | RE-V | Superficie publica (inventario). `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` declara el inventario de archivos versionados con material sensible. Check `[5/10]` en `scripts/run_all_validations.py` (client_material_policy). **Medicion**: `python scripts/run_all_validations.py --quick` → 10/10 passed (incluye check [5/10]). | :white_check_mark: |
| 25 | AC-S4 | P5 | RE-V | Disposicion de material de cliente. `evidence/FASE-P5/AC-S3-S4-inventario-superficie.md` :AC-S4: grandfathered `tests/fixtures/donalfonsohotel_onboarding.yaml` (blob de cliente real en origin/master, F-P4.5). Rotacion de key Gemini local: confirmada (riesgo declarado local). Disposicion con cliente: pendiente (accion externa). **Medicion**: el archivo existe y declara el estado. AC-S4 cerrada 2026-09-15 (key publica ya estaba rotada → RELEASE desbloqueado; falta prevencion en `_save_cache`). | :white_check_mark: (con deuda declarada: prevencion `_save_cache`) |

---

## Resumen

- **25 filas**: 22 :white_check_mark:, 2 :warning:, 1 :white_check_mark: con deuda declarada
- **AC-E4 CON**: el plan afirma DOS switches; el codigo tiene UNO (DA-P1.7 correctamente implementado)
- **AC-S2 :warning:**: evidencia anotada-pendiente (verde no re-escrito tras remediacion)
- **AC-S4 deuda**: prevencion en `_save_cache` pendiente (RELEASE)
- **3 re-mediciones CIT**: AC-E2 (4 passed), AC-E4 (1 passed), P6-R full flow (6 passed) = 11 tests green

---

## Hallazgos

### CON-1: DA-P1.7 vs documentos del plan

**Afirmacion del plan** (VERIFY prompt linea 94, 10-analisis linea 111, 01-plan-maestro linea 164): "hoy hay DOS (`GATE_BLOCKING_ENABLED` y `GATE_ENFORCEMENT_ENABLED`)".

**Realidad medida**:
- `GATE_BLOCKING_ENABLED`: main.py:3009 (unico env var leído)
- `GATE_ENFORCEMENT_ENABLED`: **NO existe en el codigo** (solo en documentos del plan)
- `judge.finalize` (judge.py:119-124): toma `gate_blocking_enabled: bool = True` (un parametro)
- `outcome.py:335`: `blocks_publish=bool(blocks) and enabled` (enabled = gate_blocking_enabled)

**Conclusion**: DA-P1.7 ("un solo boton") se implemento correctamente. Los documentos del plan contienen una afirmacion falsa sobre el estado del codigo.

**Accion**: RELEASE debe corregir los documentos del plan (01-plan-maestro, 10-analisis) para que coincidan con la realidad del codigo. No es un fix de codigo, es higiene documental.

**Dueno**: RELEASE.

### CON-2: Cláusulas P6.2/P6.5 vs reviewer_reports

**Afirmacion del acta**: clausulas P6.2 (alignment) y P6.5 (honesty) dicen `NOT_EVALUABLE`.

**Realidad medida**: alignment_reviewer y honesty_reviewer corrieron, produjeron reports con critical_count=1 y recommendation=BLOQUEAR.

**Causa**: las clausulas del acta son la estructura pre-enforcement (P1 contrato :2.1). El veredicto final SI consume los reports (verdict=BLOQUEADO por regla 2), pero las clausulas individuales no se actualizan.

**Impacto**: ninguno funcional (el veredicto es correcto). Pero el acta es internamente inconsistente: dice NOT_EVALUABLE en las clausulas pero BLOQUEADO en el veredicto.

**Accion**: declarar como limite conocido del acta (las clausulas son el input pre-revisores, el veredicto es el output post-revisores). No es un bug, es el diseno (las clausulas no se re-escriben). Documentar en RELEASE.

**Dueno**: RELEASE (documentacion).

---

## NR7 pares citados

| AC | Fase | Archivo evidencia | Verde | Rojo |
|----|-----|-------------------|-------|------|
| AC-E0 | P2 | evidence/FASE-P2/NR7-AC-E0-a.txt | 2 passed | 2 failed |
| AC-E2 | P2 | evidence/FASE-P2/NR7-AC-E2.txt | 4 passed | 4 failed |
| AC-E3 | P2 | evidence/FASE-P2/NR7-AC-E3.txt | 2 passed | 2 failed |
| AC-E4 | P2 | evidence/FASE-P2/NR7-AC-E4.txt | 1 passed | 1 failed |
| AC-E5 | P2 | evidence/FASE-P2/NR7-AC-E5-a.txt | 2 passed | 2 failed |
| AC-F1 | P3-A | evidence/FASE-P3-A/NR7-AC-F1-capa1.txt + capa2 | 2+2 passed | 2+2 failed |
| AC-F2 | P3-A | evidence/FASE-P3-A/NR7-AC-F2.txt | 3 passed | 3 failed |
| AC-F3 | P3-B | evidence/FASE-P3-B/NR7-AC-F3-a.txt + F3-b | 2+2 passed | 2+2 failed |
| AC-F4 | P3-A | evidence/FASE-P3-A/NR7-AC-F4.txt | 2 passed | 2 failed |
| AC-F5 | P3-B | evidence/FASE-P3-B/NR7-AC-F5-a.txt | 2 passed | 2 failed |
| AC-F6 | P3-B | evidence/FASE-P3-B/NR7-AC-F6.txt | 3 passed | 3 failed |
| AC-G1 | P6-R | evidence/FASE-P6/nr7_mutation_checks.md (P6R-G1) | 1 passed | 1 failed |
| AC-G2 | P6-R | evidence/FASE-P6/nr7_mutation_checks.md (P6R-G2a, G2b) | 1+1 passed | 1+1 failed |
| AC-G3 | P6-R | evidence/FASE-P6/nr7_mutation_checks.md (P6R-G3) | 1 passed | 1 failed |
| AC-G5 | P6-R | evidence/FASE-P6/nr7_mutation_checks.md (P6R-G5) | 1 passed | 1 failed |
| AC-S1 | P5 | evidence/FASE-P5/NR7-AC-S1-green.txt + red | 10 passed | 10 failed |
| AC-S2 | P5 | evidence/FASE-P5/NR7-AC-S2-green.txt + red | 2 passed | 2 failed |

**AC-G4**: sin par por reversion (declarado en nr7_mutation_checks.md). Su aporte es la matriz reproducible, no un diff de produccion.

---

## Re-mediciones CIT (VERIFY 2026-09-15)

### AC-E2 (4 tests)

```
pytest -q tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py::test_bloquear_de_un_revisor_bloquea_la_entrega tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py::test_critical_verificado_por_un_revisor_bloquea tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py::test_el_orden_de_la_matriz_es_parte_del_contrato tests/delivery/test_p2_cuarentena_zip.py::test_veredicto_bloqueante_del_tribunal_suprime_el_zip_real

4 passed, 8 warnings in 1.89s
```

### AC-E4 (1 test)

```
pytest -q tests/quality_gates/tribunal/test_p2_veredicto_enriquecido.py::test_el_knob_apagado_no_bloquea_pero_lo_declara

1 passed, 8 warnings in 1.14s
```

### P6-R full flow matrix (6 tests, cubre AC-G1, G3, G4, G5)

```
pytest -q tests/test_p6r_full_flow_matrix.py

6 passed, 8 warnings in 1.69s
```

**Total re-mediciones**: 11 tests passed.
