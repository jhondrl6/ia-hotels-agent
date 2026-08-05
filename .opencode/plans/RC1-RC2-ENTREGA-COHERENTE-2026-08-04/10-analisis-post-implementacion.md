# Análisis Post-Implementación — RC1-RC2-ENTREGA-COHERENTE

> **Estado**: FASE-A completada (2026-08-05) — prerrequisito de tests patológicos resuelto.
> **Plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04
> **Versión objetivo**: v4.71.0
> **Baseline auditado**: run 2026-08-04 12:44:43 (Zi One Luxury, coherence 0.9168, evidence_tier B+)
> **Run de verificación E2E**: FASE-F (pendiente) — `output/v4_verify_4.71.0`
> **Plan anterior**: COHERENCIA-MODULO-ENTREGA-2026-08-03 (15 lecciones aprendidas capitalizadas)

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-A | 2026-08-05 | ✅ | 1 sesión (~30/60) | No (directo) | Cuarentena 3 archivos patológicos (40 tests). Tests collected: 3215 → 3175. Lista segura: 13 archivos PASS. 2 archivos con fallos preexistentes (no patológicos). `pytest.ini` con `--ignore` específicos (CR-8). Ver L16-L17. |
| FASE-B | ⬜ Pendiente | — | — | No (directo, no delegable — DT-3) | |
| FASE-C | ⬜ Pendiente | — | — | No (directo) | |
| FASE-D | ⬜ Pendiente | — | — | Sí (3 tracks independientes) | |
| FASE-E | ⬜ Pendiente | — | — | Sí (solo docs, sin imports) | |
| FASE-F | ⬜ Pendiente | — | — | Sí parcial (v4complete background) | |
| FASE-RELEASE | ⬜ Pendiente | — | — | Sí (delegate_task) | |

### Evidencia v4complete FASE-F (llenar)

| Hotel | Output | evidence_tier | coherence | ZIP sin históricos | Onboarding inyectado |
|-------|--------|---------------|-----------|:---:|:---:|
| Zi One Luxury | ⬜ | ⬜ | ⬜ (≥ 0.8) | ⬜ | ⬜ |

---

## Matriz de Verificación de Causas Raíz (llenar en FASE-F)

### RC1 — Fuente de verdad de costos aplicada a medias

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N10 | Costos hardcodeados en propuesta | Costos desde `opportunity_scores` del run | ⬜ | ⬜ |
| N17 | Mapa inverso `asset_type → brecha_id` | Construido desde `pain_solution_mapper.PAIN_SOLUTION_MAP` | ⬜ | ⬜ |
| N18 | Hardcode L1250 (servicio fantasma) | Eliminado o parametrizado | ⬜ | ⬜ |
| N19 | `ASSET_TO_PAIN_ID` solo cubre 6/8 | Mapa inverso cubre 8/8 | ⬜ | ⬜ |

### RC2 — Gates comerciales con inputs no cableados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N11 | CG-CLAIM-VS-EVIDENCE falso positivo | No dispara con texto condicional "si...no aparece" | ⬜ | ⬜ |
| N15 | CG-TIER-CONSISTENCY pasa vacuo | Valida inputs reales o falla explícitamente | ⬜ | ⬜ |
| N16 | ZIP con `commercial_gates_report` BLOCKING | Sin reports BLOCKING junto a doc PASSED | ⬜ | ⬜ |
| N21 | ZIP con artefactos de runs anteriores | Solo artefactos del run actual | ⬜ | ⬜ |

### RC3 — Higiene documental sin enforcement

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| R3.1 | Prompts con `--release` en fases intermedias | Sin `--release` en A-F | ⬜ | ⬜ |
| R3.2 | Conteos desactualizados | Conteos desde fuente viva (L8) | ⬜ | ⬜ |
| R3.3 | Citas driftadas | Referencias verificadas | ⬜ | ⬜ |
| R3.4 | Evidencia no preservada | `evidence/FASE-F/` completo | ⬜ | ⬜ |

### Seguimientos heredados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| S5 | Occupancy label "regional" residual | Label coherente con fuente real | ⬜ | ⬜ |
| S7 | Loader onboarding sin fallback | Fallback a `output/clientes` con `--output` alternativo | ⬜ | ⬜ |

---

## Lecciones Aprendidas (llenar — mínimo 3 por fase completada)

Formato por lección: **qué pasó / por qué / qué lo previene** + evaluación de pertinencia para futuras releases.

### Lecciones capitalizadas del plan anterior (L1-L15)

Estas lecciones ya fueron aplicadas en el diseño de este plan:

| Lección | Aplicación en este plan |
|---------|------------------------|
| L1/L11: tests patológicos bloquean equipo | FASE-A: cuarentena; NUNCA suite completa de `commercial_documents`/`financial_engine` |
| L2: validaciones documentales ≠ fallos tests | Clasificar antes de re-ejecutar suites; Version Sync → `sync_versions.py` |
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

### Lecciones nuevas de este plan (L16+)

#### L16 (FASE-A) — Cuarentena con `--ignore` específicos vs `norecursedirs` global (CR-8)
- **Qué pasó**: se necesitaba excluir 3 archivos patológicos de la colección sin afectar los 22 archivos que YA estaban en `_archived_broken_tests/`.
- **Por qué**: añadir `norecursedirs = _archived_broken_tests` en `pytest.ini` habría excluido TODOS los archivos del directorio (incluyendo los 22 que sí se recolectan), reduciendo el conteo collected mucho más de lo esperado y rompiendo tests legítimos.
- **Qué lo previene**: usar `--ignore` específicos para cada archivo patológico en `addopts` de `pytest.ini`. Esto excluye solo los 3 archivos objetivo, manteniendo la recolección del resto de `_archived_broken_tests/`. Verificación: diferencia collected = 40 tests exactos (32 + 4 + 4), no más.
- **Pertinencia**: **INCLUIR** — aplica a cualquier cuarentena futura donde coexistan archivos rotos y legítimos en el mismo directorio.

#### L17 (FASE-A) — Diagnóstico de patológicos sin ejecutarlos completos
- **Qué pasó**: se necesitaba confirmar la causa probable de cada archivo patológico sin ejecutarlos (habría bloqueado el equipo).
- **Por qué**: los síntomas (fuga ~8GB, cuelgue indefinido, fallos en cascada) ya estaban documentados en L1/L11 del plan anterior, pero se requería confirmar el patrón causante específico de cada archivo.
- **Qué lo previene**: (a) leer el código de cada test (grep/read) para identificar el patrón (fixtures que instancian el generador completo, generación combinatoria, bucles); (b) si se necesita ejecutar algo, SOLO tests individuales con timeout corto (`pytest archivo.py::test_x -x --timeout=60 > temp/fase_a_diag.txt 2>&1`); (c) NUNCA ejecutar el archivo completo sin timeout.
- **Pertinencia**: **INCLUIR** — protocolo estándar para diagnosticar tests patológicos sin bloquear el equipo.

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Tests patológicos propuesta/precios | ✅ Cuarentena (FASE-A) | 3 archivos aislados en `_archived_broken_tests/commercial_documents/`. Lista segura: 13 archivos PASS. FASE-B puede agregar tests nuevos sin riesgo. |
| `test_proposal_confidence_disclosure.py` | ⚠️ 5 fallos preexistentes | Fallos de aserción (no patológicos). Diagnosticar en FASE-B o release posterior. |
| `test_proposal_dynamic.py` | ⚠️ 7 fallos preexistentes | Fallos de aserción (no patológicos). Diagnosticar en FASE-B o release posterior. |
| Prompts con `--release` en plantilla (L3/L9) | ⬜ Pendiente | FASE-E: enforcement `_check_prompts_no_release` en `run_all_validations.py` |
| S5: label `"occupancy": "regional"` residual | ⬜ Pendiente | FASE-D: `_occupancy_source` al bloque de fuentes del scenario calculator |
| S7: loader de onboarding sin fallback | ⬜ Pendiente | FASE-D: fallback a `output/clientes` con `--output` alternativo |
| (otros) | | |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests baseline (pre-plan) | 3,215 collected | — |
| Tests collected post-cuarentena | 3,175 collected (2026-08-05) | FASE-A |
| Tests nuevos FASE-B | ⬜ (desde `git diff tests/`) | FASE-B |
| Tests nuevos FASE-C | ⬜ (desde `git diff tests/`) | FASE-C |
| Tests nuevos FASE-D | ⬜ (desde `git diff tests/`) | FASE-D |
| Coherencia run E2E Zione | ⬜ (≥ 0.8 exigido) | FASE-F |
| Gates publicación run E2E | ⬜ (conteo dinámico) | FASE-F |
| Tests collected final | ⬜ (registrar en RELEASE) | FASE-RELEASE |

---

## Decisiones Arquitectónicas (llenar en FASE-B)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|------------------------|------|
| DEC-B1 | ⬜ | ⬜ | ⬜ | FASE-B |
| DEC-B2 | ⬜ | ⬜ | ⬜ | FASE-B |
| DEC-B3 | ⬜ | ⬜ | ⬜ | FASE-B |

---

## Notas de Forense y Regresión (llenar en FASE-B)

### Protocolo de verificación de regresiones (L4/L5)

1. Backup: `Copy-Item` de archivos de la fase a `temp/<fase>_backup/`
2. Reset: `git checkout HEAD -- <archivos>`
3. Test: correr tests contra HEAD (con timeout)
4. Restaurar: `Copy-Item` desde backup
5. Verificar: `git status --short` muestra archivos modificados

### Evidencia estática para tests patológicos (L7)

Mientras los tests patológicos sigan en cuarentena, usar `git show HEAD:` para verificar que el código modificado no afecta las áreas de los patológicos.

---

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Todas las causas raíz (RC1, RC2, RC3) verificadas en E2E
- [ ] Seguimientos S5 y S7 resueltos o documentados
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] `validate_agents_md.py` PASS
- [ ] CHANGELOG.md actualizado con formato CONTRIBUTING.md
- [ ] GUIA_TECNICA.md con notas técnicas por fase
- [ ] VERSION.yaml sincronizado (sync_versions.py)
- [ ] Lecciones aprendidas L16+ capitalizadas en memoria del agente
- [ ] Análisis post-implementación completo
