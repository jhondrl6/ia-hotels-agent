# Plan Maestro: Coherencia Propuesta↔Diagnóstico + Gates + Entrega (RC1/RC2/RC3)

**ID del plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04
**Contexto fuente**: `/.opencode/context/Historico/CONTEXT-VALIDACION-COHERENCIA-PLAN-ENTREGA-2026-08-04.md`
**Workflow rector**: `.agents/workflows/phased_project_executor.md` v2.14.0
**Versión actual**: v4.70.0 → **Release objetivo: v4.71.0**
**Hotel de verificación E2E**: Zi One Luxury (https://zione.co/) — onboarding real en `output/clientes/zi-one-luxury_onboarding.yaml`
**Fecha de creación**: 2026-08-04
**Correcciones de causa raíz aplicadas**: 2026-08-05 (CR-1 a CR-8)

---

## 1. Objetivo

El plan anterior (COHERENCIA-MODULO-ENTREGA-2026-08-03, v4.70.0) cerró los 21 hallazgos D1-D12/N1-N9 con coherence 0.9168, pero la validación cruzada post-implementación reveló 3 causas raíz residuales:

1. **RC1 — Fuente de verdad de costos aplicada a medias (ALTA)**: la propuesta comercial usa `BREACH_BY_ASSET` hardcodeado (L1193-1206) con costos factor 0.671× respecto al diagnóstico. El pipeline YA produce `opportunity_scores` (8 entries, suma = escenario más probable $7.192.000) pero el generador de propuesta no los consume.
2. **RC2 — Gates comerciales con inputs no cableados + evidencia contradictoria (MEDIA)**: CG-CLAIM-VS-EVIDENCE dispara falso positivo con texto condicional; CG-TIER-CONSISTENCY pasa vacuo siempre; el ZIP de entrega transporta `commercial_gates_report` BLOCKING junto al doc PASSED.
3. **RC3 — Higiene documental sin enforcement (BAJA)**: prompts con `--release` en fases intermedias, conteos desactualizados, citas driftadas, evidencia no preservada.

**Regla de oro**: una fuente de verdad por concepto — oportunidad_scores (1), gates cableados (1), ZIP limpio (1).

---

## 2. Alcance

### INCLUIDO
- Fixes RC1 (N10, N17, N18, N19), RC2 (N11, N15, N16, N21), RC3 (R3.1-R3.4).
- Seguimientos heredados S5 (occupancy label) y S7 (loader onboarding fallback).
- Prerrequisito: triage de tests patológicos (3 archivos que bloquean el equipo).
- Tests por fix + verificación estática contra evidencia del run 124443.
- UNA sola ejecución de `v4complete` en todo el plan: FASE-F (verificación E2E), con onboarding real de Zi One Luxury.
- Análisis post-implementación + lecciones aprendidas (10-analisis-post-implementacion.md, se llena en FASE-F/RELEASE).

### EXCLUIDO (con razón)
- Re-ejecución de baselines: se usa como baseline los outputs del run 20260804_124443 ya auditados.
- Upgrade de gate N2 a BLOCKING (documentado como seguimiento; requiere catalogación previa).
- Fix de S6 (execution_trace duplicado pagespeed_api): mejora cosmética, no bloqueante.
- Fórmulas de `scenario_calculator.py` (valores centrales verificados correctos en v4.70.0).

---

## 3. Fases (1 fase = 1 sesión, regla R1)

| Fase | Hallazgos | Objetivo | Complejidad | Modelo de ejecución |
|------|-----------|----------|-------------|---------------------|
| **FASE-A** | Prerrequisito | Cuarentena de 3 tests patológicos + lista segura | **Baja-Media** | **DIRECTO** — infraestructura de tests (pytest.ini, mover archivos). Sin imports del proyecto. |
| **FASE-B** | RC1: N10, N17, N18, N19 | Parametrizar tabla de servicios desde `opportunity_scores` | **MÁXIMA** ⚠️ | **DIRECTO** — decisión arquitectónica cross-module (mapa inverso `pain_solution_mapper` → `opportunity_scores`). NO delegable (regla DT-3). |
| **FASE-C** | RC2-a: N11, N15 | Fix CG-CLAIM-VS-EVIDENCE + cablear CG-TIER-CONSISTENCY | **Media** | **DIRECTO** — 2 archivos secuenciales (commercial_gate.py + v4_diagnostic_generator.py). Tests de gates. |
| **FASE-D** | RC2-b: N16, N21, S7, S5 | Política ZIP + loader onboarding + occupancy label | **Media** | **DELEGABLE** (3 tracks independientes, archivos sin intersección). Fallback a directo si subagentes no pueden ejecutar tests del proyecto (venv). |
| **FASE-E** | RC3: R3.1-R3.4 | Higiene documental + enforcement `_check_prompts_no_release` | **Baja** | **DELEGABLE** — MD/YAML + 1 script stdlib-only (executor v2.14.0 §Regla decisión L231-241). Sin imports del proyecto. |
| **FASE-F** | E2E | **Única ejecución v4complete** Zi One Luxury + verificación V1-V10 + análisis post-implementación | **Media** | **DELEGADO parcial** — v4complete vía subagente (timeout=900); parent verifica V1-V10 + docs. |
| **FASE-RELEASE-4.71.0** | Docs | Version bump, CHANGELOG, GUIA_TECNICA, validaciones, flujo documental | **Baja** | **DELEGABLE** (executor Paso 7: solo YAML/MD + scripts, sin imports del proyecto). |

### Fase de mayor complejidad técnica: **FASE-B** (RC1)

Razones:
1. **Decisión arquitectónica cross-module**: construir mapa inverso `asset_type → brecha_id` invirtiendo `pain_solution_mapper.PAIN_SOLUTION_MAP[bid]["assets"]`, luego cruzar con `opportunity_scores` del run. `ASSET_TO_PAIN_ID` (L1185-1191) solo cubre 6/8 services; el mapa inverso cubre los 8.
2. **Riesgo de regresión comercial**: son cifras de fuga que ve el cliente; un error reproduce exactamente la incoherencia que el plan elimina.
3. **Zona con tests patológicos**: los tests del área de propuesta son los que causaron bloqueos reales (~8GB RAM, cuelgues) — por eso FASE-A es prerrequisito.
4. **Ambigüedad multi-brecha**: un `asset_type` puede resolver múltiples `brecha_id` (ej: `optimization_guide` ← `low_seo_score` o `low_content_length`); desempatar por presencia en `opportunity_scores`.
5. Requiere evidencia mixta dinámica+estática (L7) y forense de regresión con backup (L4/L5).

**NO es delegable** por la regla de decisión arquitectónica del executor (lección DT-3).

### Guía de selección de modelo por fase

| Complejidad | Fases | Modelo recomendado |
|-------------|-------|--------------------|
| **MÁXIMA** ⚠️ | B | Agente principal DIRECTO (decisión arquitectónica, contexto completo requerido) |
| **Media** | C, F | C: DIRECTO (2 archivos secuenciales). F: DELEGADO parcial (v4complete largo + verificación) |
| **Media** | D | DELEGABLE (3 tracks independientes) con fallback a directo si venv lo requiere |
| **Baja-Media** | A | DIRECTO (infraestructura de tests, sin overhead de subagente) |
| **Baja** | E, RELEASE | DELEGABLE (documental, sin imports del proyecto) |

---

## 4. Mapa de conflictos de archivos

| Archivo | Fases que lo tocan | Separación |
|---------|-------------------|------------|
| `modules/commercial_documents/v4_proposal_generator.py` | B | Único (BREACH_BY_ASSET L1193-1206, hardcode L1250) |
| `modules/commercial_documents/pain_solution_mapper.py` | B (lectura) | Único (mapa inverso PAIN_SOLUTION_MAP → asset_type) |
| `modules/quality_gates/commercial_gate.py` | C | Único (CG-CLAIM-VS-EVIDENCE L523-568, CG-TIER-CONSISTENCY L627-665) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | C | Único (invocación validate_diagnostic L627-649, cableado tier kwargs) |
| `modules/delivery/delivery_packager.py` | D | Único (política ZIP, freshness cutoff L286-304) |
| `main.py` | D (S7) | Único (loader onboarding L1746, fallback) |
| `modules/financial_engine/harness_handlers.py` | D (S5) | Único (occupancy label L118) |
| `pytest.ini` / `tests/_archived_broken_tests/commercial_documents/` | A | Único (cuarentena 3 archivos, --ignore específicos) |
| `/.opencode/plans/Archives/COHERENCIA-MODULO-ENTREGA-2026-08-03/*` | E | Único (solo MD, corrección R3.1-R3.3) |
| `scripts/run_all_validations.py` | E | Único (nuevo check `_check_prompts_no_release`, stdlib-only) |
| `evidence/FASE-F/` | F | Único (run E2E + verificación V1-V10) |
| `VERSION.yaml`, `CHANGELOG.md`, `docs/GUIA_TECNICA.md` | RELEASE | Único (bump 4.71.0 + docs oficiales) |

**Conclusión**: sin conflictos de archivos entre fases gracias al orden A→B→C→D→E→F→RELEASE. No hay dos fases tocando el mismo archivo.

Detalle completo y orden de ejecución → `dependencias-fases.md`.

---

## 5. Baseline y verificación E2E

- **Baseline auditado** (NO re-ejecutar): run 20260804_124443 — outputs en `output/v4_verify_4.70.0/v4_complete/`; coherence 0.9168, evidence_tier B+.
- **Ejecución E2E única** (FASE-F):
  ```bash
  ./venv/Scripts/python.exe main.py v4complete --url https://zione.co/ --output output/v4_verify_4.71.0
  ```
  **Pre-requisito FASE-F T0**: verificar S7 en aislamiento (invocar `_load_latest_onboarding_data` con `output_dir=output/v4_verify_4.71.0/clientes`) ANTES de lanzar v4complete. Si retorna None, el run no sirve (lección L13/L14).
  **Workaround L13**: copiar `output/clientes/zi-one-luxury_onboarding.yaml` a `output/v4_verify_4.71.0/clientes/` antes del run.
- **Verificación**: checklist V1-V10 (costos, gates, ZIP, occupancy, coherencia) + Protocolo de Evidencia Proactiva (`evidence/FASE-F/`).

---

## 6. Métricas base

| Métrica | Valor inicial | Fuente |
|---------|---------------|--------|
| Tests totales | 3,215 funciones collected | `pytest --collect-only -q` (2026-08-04) |
| Tests collected post-cuarentena | ⬜ (registrar en FASE-A) | FASE-A T2 |
| Coherence run baseline | 0.9168 (evidence_tier B+) | run 20260804_124443 |
| Hallazgos abiertos | 3 causas raíz (RC1, RC2, RC3) + 2 seguimientos (S5, S7) | contexto validación |
| Versión | v4.70.0 | VERSION.yaml |

---

## 7. Registro por fase (anti-deuda, executor §2.5)

CADA fase de implementación ejecuta su propio `log_phase_completion.py` al cerrar (nunca acumular en RELEASE):

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-X --desc "..." \
    --archivos-mod "paths" --tests "N" --check-manual-docs
```

**⚠️ SIN `--release`** en fases intermedias (A-F). Solo FASE-RELEASE-4.71.0 usa `--release 4.71.0` (lección L3/L9).

---

## 8. Riesgos operativos conocidos

| Riesgo | Mitigación |
|--------|------------|
| Suite completa 3,215 tests da timeout/cuelgue | NUNCA suite completa de `tests/commercial_documents`/`tests/financial_engine` (L1/L11); ejecutar por archivos individuales |
| Tests patológicos fuga ~8GB RAM | FASE-A: cuarentena + `--ignore` específicos (no `norecursedirs` global — CR-8) |
| v4complete 5-10 min agota sesión | FASE-F: subagente/background + notify + evidencia ANTES de verificar |
| Loader onboarding no encuentra YAML con `--output` alternativo | FASE-F T0: verificar S7 en aislamiento + workaround de copia (L13/L14) |
| Mapa inverso `asset_type → brecha_id` ambiguo | FASE-B: desempatar por presencia en `opportunity_scores`; fallback sin cifras inventadas |
| `git stash` denegado por sandbox | Usar backup `Copy-Item` + `git checkout HEAD --` + restauración obligatoria (L4/L5) |
| Pytest pipe cuelga captura | SIEMPRE redirigir a archivo `> temp/x.txt 2>&1` (L6) |
| Select-String con acentos da falso negativo | Usar Grep (ripgrep) o Python UTF-8 (L15) |
| Intervención del usuario cambia estado del disco | `git diff --stat` + `git status --short` antes de continuar (L10) |

---

## 9. Lecciones aprendidas capitalizadas (L1-L15 del plan anterior)

| Lección | Aplicación en este plan |
|---------|------------------------|
| L1/L11: tests patológicos bloquean equipo | FASE-A: cuarentena; NUNCA suite completa |
| L2: validaciones documentales ≠ fallos tests | Clasificar antes de re-ejecutar suites |
| L3/L9: `log_phase_completion` sin `--release` | Fases A-F: SIN `--release`; RELEASE: con `--release 4.71.0` |
| L4/L5: forense baseline + backup | Protocolo `Copy-Item` + `git checkout HEAD --` en FASE-B |
| L6: pytest → archivo, no pipe | Regla transversal en todos los prompts |
| L7: evidencia mixta dinámica+estática | FASE-B T3: verificación contra run 124443 |
| L8: conteo desde `git diff tests/` | Regla transversal (L8) |
| L10: `git diff` tras intervención usuario | Regla transversal (L10) |
| L12: tracks mismo archivo → integrar | FASE-D: 3 tracks tocan archivos distintos → delegable |
| L13/L14: loader + clasificar fallo antes retry | FASE-F T0: verificar S7 en aislamiento |
| L15: grep UTF-8 vs Select-String | Regla transversal (L15) |

---

## 10. Criterios de éxito globales

- [ ] `BREACH_BY_ASSET` estático eliminado; reemplazado por construcción dinámica desde `opportunity_scores` vía mapa inverso `pain_solution_mapper`.
- [ ] CG-CLAIM-VS-EVIDENCE no dispara falso positivo con texto condicional "si...no aparece".
- [ ] CG-TIER-CONSISTENCY valida inputs reales (o falla explícitamente; nunca pasa vacuo).
- [ ] ZIP de entrega sin `commercial_gates_report*` BLOCKING junto a doc PASSED, sin artefactos de runs anteriores.
- [ ] `v4complete` para Zione carga onboarding real ("Onboarding data loaded" en log, NO "Using defaults") y coherencia ≥ 0.8.
- [ ] Check de cierre OBLIGATORIO: costos/numeración de brechas IDÉNTICOS en diagnóstico Y propuesta del run E2E.
- [ ] `run_all_validations.py --quick` TOTAL PASS + `validate_agents_md.py` PASS en RELEASE.
- [ ] S7 verificado en aislamiento ANTES de lanzar v4complete.
- [ ] V10: 0 blocking failures + READY_FOR_PUBLICATION (no "12/12" — conteo dinámico).
- [ ] Análisis post-implementación con lecciones aprendidas en FASE-F.
