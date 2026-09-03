# 06 — Checklist Maestro de Implementación

> **Estado maestro** del plan ESTABILIZACION-PRE-TRIBUNAL-2026-09-03.
> Cada sesión actualiza este archivo en su Post-Ejecución (template §5, punto 2).
> **Regla**: no marcar una fase ✅ si algún criterio de completitud falla.

**Versión objetivo**: 4.75.0 · **Versión actual del repo**: 4.74.1
**Sesiones totales**: 11 (9 implementación + VERIFY + RELEASE)
**Sesiones completadas**: 0

---

## Progreso de fases

| # | Fase | Complejidad | Modo | Estado | Fecha | Iter. | Tests nuevos | ACs cerrados |
|---|------|-------------|------|--------|-------|-------|--------------|--------------|
| 1 | FASE-A — Fuente única de identidad | ALTA | DIRECTO | ⬜ Pendiente | — | —/55 | — | AC1, AC2, AC3 |
| 2 | FASE-B — Biyección mapa↔emisión | MEDIA-ALTA | DIRECTO | ⬜ Pendiente | — | —/40 | — | AC4 |
| 3 | FASE-C — Punto 8 propuesta dinámica | **MÁXIMA** | DIRECTO | ⬜ Pendiente | — | —/60 | — | AC5, AC6 |
| 4 | FASE-D — Severidad 11+2 (H10) | MEDIA | MIXTO | ⬜ Pendiente | — | —/35 | — | AC7, AC8 |
| 5 | FASE-E — A2 snapshot + A6 asset_path | MEDIA | DELEGADO | ⬜ Pendiente | — | —/30 | — | AC9 |
| 6 | FASE-F — A4 + A1 + N11 | MEDIA-ALTA | DIRECTO | ⬜ Pendiente | — | —/45 | — | AC10, AC11, AC12 |
| 7 | FASE-G — Ceguera de gates | MEDIA-ALTA | DIRECTO | ⬜ Pendiente | — | —/50 | — | NR1, NR2, NR3, NR4 |
| 8 | FASE-H — Quirúrgicos | BAJA-MEDIA | DELEGADO | ⬜ Pendiente | — | —/35 | — | V6, V7, V8, V11, V12, V13 |
| 9 | FASE-I — E2E única Salento Real | BAJA | MIXTO | ⬜ Pendiente | — | —/25 | — | NR6 + deltas AC5/AC6/AC9/AC12 |
| 10 | FASE-VERIFY — Certificación | MEDIA | DIRECTO | ⬜ Pendiente | — | —/40 | — | AC1-AC12 + NR1-NR12 |
| 11 | FASE-RELEASE-4.75.0 | BAJA | DELEGABLE | ⬜ Pendiente | — | —/25 | — | Cierre documental |

Leyenda: ⬜ Pendiente · 🟡 En curso · ✅ Completada · 🔴 Bloqueada · ⏸️ Suspendida

---

## Criterios de aceptación — estado

### ACs de refactorización

| AC | Descripción corta | Fase dueña | Estado | Evidencia |
|----|-------------------|-----------|--------|-----------|
| AC1 | Registro canónico único; 0 IDs fantasma | A | ⬜ | — |
| AC2 | Drift «8 vs 7» corregido en sus 3 copias + contract test | A | ⬜ | — |
| AC3 | `ASSET_TO_PAIN_ID["monthly_report"]` resuelto a favor del canónico | A | ⬜ | — |
| AC4 | Biyección mapa↔emisión fijada; 0 pains muertos sin decisión | B | ⬜ | — |
| AC5 | Propuesta solo promete servicios con brecha; `no_breach = 0` | C | ⬜ | — |
| AC6 | `is_coherent = false` estructural desaparece por el punto 8 | C | ⬜ | — |
| AC7 | Severidad explícita 11 blocking + 2 advisory; `asset_confidence` bloquea | D | ⬜ | — |
| AC8 | Docstrings + `AGENTS.md` corregidos **en el mismo commit** que AC7 | D | ⬜ | — |
| AC9 | `site_presence_snapshot` persistido; `asset_path` no nulo | E | ⬜ | — |
| AC10 | Un oráculo de presencia decide **y** narra | F | ⬜ | — |
| AC11 | `skipped ≠ passed` en G9 | F | ⬜ | — |
| AC12 | El gate de coherencia respeta `is_coherent` (o lo elimina con decisión) | F | ⬜ | — |

### ACs de no-regresión

| AC-NR | Descripción corta | Fase dueña | Estado | Evidencia |
|-------|-------------------|-----------|--------|-----------|
| NR1 | `doc_audit_consistency` cableado + acepta `gbp.reviews` int | G | ⬜ | — |
| NR2 | `_identify_critical_issues` cubre PageSpeed ERROR + banda GEO critical | G | ⬜ | — |
| NR3 | Escotilla V5 cerrada **sin revertir** BUG-6/N2 | G | ⬜ | — |
| NR4 | Escotilla V9 cerrada (ledger vacío ≠ PASS) | G | ⬜ | — |
| NR5 | Baseline 848 passed / 2 skipped preservado | todas | ⬜ | — |
| NR6 | Corrida FASE-I: coherence ≥ 0.80 + perfil de gates esperado | I | ⬜ | — |

> **Dos familias de NR** (auditoría del plan 2026-09-03): NR1-NR6 son «de hallazgo» (la tabla anterior);
> **NR7-NR12 son «de producto»** (tests, coherence, 13 gates, ZIP, `asset_confidence` blocking,
> anomalías — definidas en `10-analisis-post-implementacion.md` §3). VERIFY certifica ambas; FASE-I
> aporta la evidencia de las dos.

---

## Hallazgos del dossier — trazabilidad

Cada fila debe quedar en estado final explícito al cierre de VERIFY (tarea V3).

### Eje 1 — Caídas silenciosas (dossier §4)

| # | Caída | Fase que la aborda | Estado |
|---|-------|--------------------|--------|
| 1 | PageSpeed `status=ERROR` sin pain ni justificación | H3 (V11 + capa de pain (a)-(d)) | ⬜ |
| 2 | GEO crítico 29/100 sin pain | G2 (`_identify_critical_issues`) | ⬜ |
| 3 | `llm_report` mention_rate 0.0 / `aeo_snippets` 0/5 sin pain_id | B (biyección) | ⬜ |
| 4 | `missing_llmstxt` declarado, asset generado, 0 ramas lo emiten | B2 (caso confirmado) | ⬜ |
| 5 | Schema warnings invisibles en doc | B (biyección) | ⬜ |
| 6 | Fotos GBP 10/40 solo en tabla rota | H3 (V11 tabla sin header) | ⬜ |
| 7 | metadata `title=""`/`description=""` (narrativa «por defecto» equivocada) | H4 (V13 gemelos) | ⬜ |
| 8 | `low_ota_divergence` no puede disparar con valor numérico | H1 (V7 guard `__iter__`) | ⬜ |

### Eje 2 — Candados rotos (dossier §3)

| Candado | Defecto | Fase | Estado |
|---------|---------|------|--------|
| `coverage_no_silent_drop` | Tautología extremo a extremo (ledger y doc de la misma llamada) | A+B+C (cura) · G3/G4 (escotillas) | ⬜ |
| `doc_audit_consistency` | Llegó sin datos → PASSED con `value=null` | G1 | ⬜ |
| `critical_recall` | 1.0 vacuo | G2 | ⬜ |
| `hard_contradictions` | Fuera de alcance del motor | — (documentado como límite) | ⬜ |

### Eje 3 — Agujeros vivos A1-A6 (dossier §9.1)

| # | Agujero | Fase | Estado |
|---|---------|------|--------|
| A1 | G9 se salta **en verde** | F2 | ⬜ |
| A2 | Oráculo de presencia no se persiste en absoluto | E1 | ⬜ |
| A3 | `promised_assets_exist` pre-gen only (peso 2.0/7.5) | C4 (no apoyarse) + documentar P12 | ⬜ |
| A4 | Doble oráculo de presencia | F1 | ⬜ |
| A5 | Skip silencioso en los 2 builders de la matriz | C3 (esquivar la trampa) | ⬜ |
| A6 | `asset_path: null` | E2 | ⬜ |

### Eje 4 — Hallazgos nuevos V1-V16 (dossier §12.3)

| V# | Hallazgo | Nivel | Fase | Estado |
|----|----------|-------|------|--------|
| V1 | 9 pains muertos, no 1 | 1 | B | ⬜ |
| V2 | 6 IDs fantasma en `ELEMENTO_KB_TO_PAIN_ID` | 1 | A | ⬜ |
| V3 | ≥9 registros, no 6 (+ perla `monthly_report → no_faq_schema`) | 1 | A | ⬜ |
| V4 | Atribución de brechas excluye por diseño el pain real | 1 | C | ⬜ |
| V5 | `ASSET_GENERATED` = segunda escotilla (⚠️ anti-reversión BUG-6) | 2-3 | G3 | ⬜ |
| V6 | `except Exception` silencioso | 3 | H2 | ⬜ |
| V7 | Guard `__iter__` triple defecto | 3 | H1 | ⬜ |
| V8 | Dedup `low_organic_visibility` | 3 | H3 | ⬜ |
| V9 | Ledger vacío PASS vs BLOCKED | 2-3 | G4 | ⬜ |
| V10 | (ver dossier §12.3) | — | según nivel | ⬜ |
| V11 | Residuos D6 | 3 | H3 | ⬜ |
| V12 | Placeholder `.env` inválido (decisión **OPS**) | 3 | H4 (documentar) | ⬜ |
| V13 | Dos `MetadataValidator` gemelos | 3 | H4 | ⬜ |
| V14 | Drift «8 vs 7» tercera copia | 1 | A | ⬜ |
| V15 | Mecanismo 6→3 de `no_breach` resuelto | 2 | F1 (vía A4) | ⬜ |
| V16 | `is_coherent: false` en `asset_generation_report.json` | 2 | F3 (vía N11) | ⬜ |

### Eje 5 — Deudas del ROADMAP v4.2 §13

| Deuda | Descripción | Fase | Estado |
|-------|-------------|------|--------|
| **P9** | El gate ignora `is_coherent` (la más grave abierta) | F3 | ⬜ |
| **P10** | ≥9 registros de identidad (extendido por A5) | A | ⬜ |
| **P11** | `precision_tier` degrada a `"C"` bajo `except` desnudo | H2 (misma familia) | ⬜ |
| **P12** | `promised_assets_exist` pre-gen only | C4 (documentar alcance) | ⬜ |
| **H7** | Nombres timestamped sin índice + oráculo no persistido | E1 | ⬜ |
| **H8** | `publication_state.py` huérfano | F3 (decisión conectar/eliminar) | ⬜ |
| **H9** | Tres rutas de bloqueo + kill switch + G9 en verde | F2 | ⬜ |
| **H10** | Docstrings 10+3 vs código 13 | D3 | ⬜ |

---

## Checklist de cierre de cada sesión (obligatorio)

Cada fase, al terminar, debe haber hecho **todo** lo siguiente (template §5 + §6):

- [ ] Tests nuevos pasan (lotes pequeños, salida a archivo `> temp/x.txt 2>&1`)
- [ ] Baseline preservado: 848 passed / 2 skipped en `tests/quality_gates` + `tests/asset_generation`
- [ ] `python scripts/run_all_validations.py --quick` → 7/7
- [ ] `python scripts/validate_agents_md.py` → 6 PASS / 0 FAIL
- [ ] `log_phase_completion.py --fase FASE-X --desc "..." --check-manual-docs` **SIN `--release`**
- [ ] `dependencias-fases.md` actualizado (fase ✅ + fecha + notas)
- [ ] `README.md` del plan actualizado (tabla de progreso)
- [ ] **Este archivo** actualizado (fila de fase + ACs + trazabilidad de hallazgos)
- [ ] `09-documentacion-post-proyecto.md` actualizado (secciones A, B, D, E)
- [ ] `10-analisis-post-implementacion.md` actualizado (ejecución, lecciones, métricas, seguimientos, decisiones)
- [ ] `evidence/FASE-X/` poblado si aplica
- [ ] Commit con mensaje que referencia la fase

**NO esperar a la siguiente sesión para documentar** (anti-deuda §2.5 del executor).

---

## Riesgos abiertos

| Riesgo | Probabilidad | Impacto | Mitigación | Estado |
|--------|--------------|---------|------------|--------|
| FASE-C agota R2 (60 iteraciones) | Media | Alto | Punto de partición C1/C2 predefinido en `01-plan-maestro.md` §1 | ⬜ |
| A5 (skip silencioso) produce Δ = 0 en C y parece que no hizo nada | Media | Alto | C4 mide el delta explícitamente contra artefactos reales | ⬜ |
| G3 re-introduce BUG-6 al cerrar V5 | Baja | Alto | Test anti-reversión obligatorio en G3 | ⬜ |
| F3 voltea veredictos indebidamente en el corpus histórico | Media | Medio | F4 mide impacto sobre las 27 corridas antes de cerrar | ⬜ |
| Run FASE-I contaminado por infraestructura (gemini 403, PageSpeed key) | Media | Medio | I1 pre-flight verifica `.env`; clasificar como anomalía preexistente | ⬜ |
| D3 (docs) se commitea separado de D1 (código) | Baja | Alto | Checklist de D exige mismo commit; VERIFY lo audita | ⬜ |
