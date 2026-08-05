# Checklist Maestro de Implementación — RC1-RC2-ENTREGA-COHERENTE-2026-08-04

> Regla R1: una fase por sesión. Regla R2: máx. 60 iteraciones. Regla R3: máx. 4 tareas o 3 tareas + 1 comando largo por fase.

## Estado de Fases

| # | Fase | Alcance | Estado | Delegable | Sesión | Fecha |
|---|------|---------|--------|-----------|--------|-------|
| 1 | FASE-A | Cuarentena tests patológicos (prerrequisito RC1) | ✅ Completada | ❌ | 1 | 2026-08-05 |
| 2 | FASE-B ⚠️ | RC1: tabla de servicios dinámica (N10/N17/N18/N19) — MAYOR COMPLEJIDAD | ✅ Completada | ❌ | 1 | 2026-08-05 |
| 3 | FASE-C | RC2-a: CG-CLAIM-VS-EVIDENCE + CG-TIER-CONSISTENCY (N11/N15) | ✅ Completada | ❌ | 1 | 2026-08-05 |
| 4 | FASE-D | RC2-b: ZIP entrega + loader onboarding + occupancy (N16/N21/S7/S5) | ✅ Completada | ✅ 3 tracks | 4 | 2026-08-05 |
| 5 | FASE-E | RC3: higiene documental R3.1-R3.4 | ✅ Completada | ✅ | 5 | 2026-08-05 |
| 6 | FASE-F | E2E v4complete Zi One Luxury + análisis post-implementación | ✅ Completada (V1-V10 10/10 tras recuperación S5b) | ✅ comando largo | 2 | 2026-08-05 |
| 7 | FASE-RELEASE-4.71.0 | Version bump + docs oficiales | ⬜ Pendiente | ✅ | — | — |

## Gate por Fase (resumen de criterios bloqueantes)

| Fase | Gate bloqueante |
|------|-----------------|
| A | 3 patológicos fuera de colección; lista segura documentada |
| B | 8/8 brechas resuelven costo correcto contra evidencia real |
| C | Condicional no dispara gate; tier gate no pasa vacuo |
| D | ZIP sin evidence BLOCKING; loader con fallback testeado |
| E | grep `--release` = 0 en prompts 02-05; check "Prompts No Release" PASS en `run_all_validations.py --quick`; validaciones TOTAL PASS |
| F | V1-V10 PASS + "Onboarding data loaded" en el run único + S7 verificado en aislamiento antes del run |
| RELEASE | validate_agents_md PASS + run_all_validations TOTAL PASS (incluye "Prompts No Release") + VERSION SYNC GATE verde |

## Verificación Pre-Creación de Prompts (§2.5 anti-deuda)

- [x] Cada fase A-F termina con `log_phase_completion.py` **SIN `--release`** (verificado en los 6 prompts)
- [x] FASE-RELEASE NO registra fases anteriores; solo sincroniza y valida
- [x] T1 de RELEASE ≠ "registrar FASE-A a FASE-F"
- [x] Template `prompt-fase-template.md` existe (v1.3.0) y se usó como base

## Verificación Post-Ejecución por Fase (anti-omisión de `10-analisis-post-implementacion.md`)

- [x] Prompt FASE-A incluye paso Post-Ejecución para `10-analisis-post-implementacion.md` (2026-08-05)
- [x] Prompt FASE-B incluye paso Post-Ejecución para `10-analisis-post-implementacion.md`
- [x] Prompt FASE-C incluye paso Post-Ejecución + no-regresión heredada de FASE-B
- [x] Prompt FASE-D incluye paso Post-Ejecución + no-regresión heredada de FASE-B
- [x] Prompt FASE-E incluye paso Post-Ejecución
- [x] Prompt FASE-F: T3 "Crear" → "Completar" + paso Post-Ejecución
- [x] Prompt FASE-RELEASE: sección Post-Ejecución nueva + check en Completitud

## Reglas Operativas Transversales (aplican a todas las sesiones)

1. NUNCA suite completa de `tests/commercial_documents`/`tests/financial_engine` (L1/L11).
2. Pytest redirigido a archivo (L6); si cuelga: `taskkill /F /IM python.exe /T`.
3. Backup `Copy-Item` antes de tocar archivos críticos; `git stash` DENEGADO (L4/L5).
4. Conteos desde fuente viva: `git diff tests/` patrón `^\+\s*def test_` (L8).
5. Verificación de texto/costos: Python UTF-8 o ripgrep, nunca Select-String (L15).
6. Tras intervención del usuario: `git diff --stat` + `git status --short` (L10).
7. UNA sola ejecución de `v4complete` en todo el plan (FASE-F).
8. Clasificar fallos antes de retry: infraestructura ≠ código (L14).
9. Verificar S7 loader en aislamiento ANTES de v4complete (CR-6, lección L13/L14).
10. V10: 0 blocking failures + READY_FOR_PUBLICATION (no exigir "12/12" — conteo dinámico).
11. Mapa inverso `asset_type → brecha_id` desde `pain_solution_mapper` (no desde `ASSET_TO_PAIN_ID` — CR-1).
12. Desde FASE-E: `run_all_validations.py --quick` incluye el check **"Prompts No Release"** (grep `--release` sobre prompts de fases intermedias, excluyendo `Archives/` y `*RELEASE*`) — enforcement permanente de L3/L9 (R3.1).
13. **Post-Ejecución de cada fase incluye SIEMPRE actualizar `10-analisis-post-implementacion.md`** (Resumen de Ejecución, Métricas, Decisiones Arquitectónicas si aplica, mínimo 3 Lecciones Aprendidas, Seguimientos abiertos, notas forenses). Regla transversal desde FASE-B (2026-08-05).
14. **No-regresión heredada de FASE-B**: `test_proposal_dynamic.py` (7 fallos preexistentes estables) y `test_proposal_confidence_disclosure.py` (5 fallos preexistentes estables) deben mantenerse en el conteo exacto documentado hasta que se diagnostiquen en release posterior.
