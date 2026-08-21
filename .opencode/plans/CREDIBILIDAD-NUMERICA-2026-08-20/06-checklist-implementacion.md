# Checklist Maestro de Implementación — CREDIBILIDAD-NUMERICA-2026-08-20

> Actualizar en cada sesión. Estados: ⬜ Pendiente | 🔄 En progreso | ✅ Completada | ⏳ INCOMPLETA (con checkpoint)

## Etapa 1 — Preparación

- [x] Plan maestro creado (`01-plan-maestro.md`)
- [x] Prompts creados para todas las fases (11)
- [x] `dependencias-fases.md` con conflictos documentados
- [x] `09-documentacion-post-proyecto.md` con estructura base
- [x] `10-analisis-post-implementacion.md` creado DESDE LA CONCEPCIÓN
- [x] Fase de mayor complejidad identificada: `FASE-P1-D`
- [x] Revisión de exactitud contra código vivo (2026-08-20): línea base de tests documentada (22
      fallos preexistentes — §6 del maestro), decisiones D1-D8 unificadas, scope F5/F6/F12 ampliado
      con evidencia de líneas (ver README §Revisión-de-Exactitud)

## Etapa 2 — Implementación (1 fase por sesión)

| # | Fase | Fallos | Estado | Sesión | Iteraciones | Notas |
|---|------|--------|--------|--------|-------------|-------|
| 1 | FASE-P0-A — Fuente única de pricing + hook PDF dinámico | F1 | ✅ | 2026-08-20 | ~35 | DIRECTO; 3 tests nuevos contrato F1; 0 regresiones |
| 2 | FASE-P0-B — Gate `pricing_compliance` bloqueante | F1 | ✅ | 2026-08-21 | ~30 | DIRECTO; 18 tests nuevos pricing_compliance; gate floor-aware D1; AGENTS.md 12→13 gates; 0 regresiones |
| 3 | FASE-P0-C — Encoding utf-8 en writers de artefactos | F7 | ✅ | 2026-08-21 | ~15 | DIRECTO; 4 tests nuevos encoding; auditoría estática AST; 0 regresiones |
| 4 | FASE-P1-A — Benchmark maestro único (incluye Bogotá) | F2, F4 | ✅ | 2026-08-21 | ~45 | DIRECTO; 19 tests nuevos benchmark_master; normalización regiones; script sync; 0 regresiones vs baseline (10 preexistentes) |
| 5 | FASE-P1-B — Fallback región conservador + comisión OTA parametrizada | F3, F5 | ✅ | 2026-08-21 | ~45 | DIRECTO; 12 tests F3 + 12 tests F5; 0 regresiones vs baseline (148 auditors, 10 preexistentes financial_engine) |
| 6 | FASE-P1-C — Cableado benchmark→hook + cap de plausibilidad + trazabilidad Hook→Express | F6, F11 | ✅ | 2026-08-21 | ~30 | DIRECTO; cableado D4 antes del cap; 27 tests nuevos (14 cap/cableado + 13 trazabilidad); suite orchestration_v4 66→93 passed; cap ratio fijo 5.0 configurable (D7); 0 regresiones |
| 7 | **FASE-P1-D — Verdad del sitio vivo (sedes + site_verification)** | F12, F13 | ✅ | 2026-08-21 | ~35 | **MÁXIMA COMPLEJIDAD**, DIRECTO; 21 tests nuevos (11 F12 multi-sede + 10 F13 propagación); firma backwards-compatible; D8 (VERIFIED_IN_SITE primera clase); 0 regresiones |
| 8 | FASE-P2-A — Coherence acepta "verificado en producción" + occupancy label | F14, F8 | ✅ | 2026-08-21 | ~30 | DIRECTO; 11 tests nuevos F14; promised_assets_exist acepta site_presence_report; F8 auditoría sin rutas residuales; 0 regresiones |
| 9 | FASE-P2-B — Pre-carga GBP de prospectos + higiene docs comerciales | F9, F10 | ⬜ | — | — | DIRECTO |

## Etapa 2b — Verificación E2E

| # | Fase | Estado | Sesión | Iteraciones | Notas |
|---|------|--------|--------|-------------|-------|
| 10 | FASE-E2E-ZIONE — v4complete único Zi One Luxury (https://zione.co/) + matriz V1-V13 + lecciones | ⬜ | — | — | v4complete vía delegate_task (timeout=900); requiere fases 1-9 ✅ |

## Etapa 3 — Release

| # | Fase | Estado | Sesión | Iteraciones | Notas |
|---|------|--------|--------|-------------|-------|
| 11 | FASE-RELEASE-4.72.0 — Version bump, CHANGELOG, GUIA_TECNICA, validaciones | ⬜ | — | — | DELEGABLE opcional; requiere E2E ✅ |

## Gates de Entrada

- FASE-P0-B: no iniciar sin P0-A ✅.
- FASE-P1-B: no iniciar sin P1-A ✅.
- FASE-P1-C: no iniciar sin P1-B ✅.
- FASE-P2-A: no iniciar sin P1-D ✅.
- FASE-E2E-ZIONE: no iniciar sin fases 1-9 ✅.
- FASE-RELEASE-4.72.0: no iniciar sin FASE-E2E-ZIONE ✅.
