# Checklist de Implementación — REFACTOR-COHERENCIA-NARRATIVA-2026-08-22

> **Regla**: marcar ✅ SOLO cuando el checklist de completitud del prompt de la fase esté 100% cumplido y `log_phase_completion.py` haya sido ejecutado por esa fase.
> **Regla anti-deuda (executor §2.5)**: cada fase registra SU PROPIA ejecución de `log_phase_completion.py` al cerrar. FASE-RELEASE NO registra fases anteriores.

## Estado Maestro de Fases

| # | Fase | Bugs/Alcance | Prompt | Estado | Tests | log registrado |
|---|------|--------------|--------|--------|-------|----------------|
| 1 | FASE-R0-A | B2 Quick Win condicional | `05-prompt-inicio-sesion-fase-R0-A.md` | ✅ COMPLETADA | +1 | ✅ |
| 2 | FASE-R0-B ⚠️ **mayor complejidad** | B1+B4 Sección 4 dinámica | `05-prompt-inicio-sesion-fase-R0-B.md` | ✅ COMPLETADA (2026-08-24, Sesión 2) | +4 | ✅ |
| 3 | FASE-R0-C | B3+B5 títulos/contadores | `05-prompt-inicio-sesion-fase-R0-C.md` | ✅ COMPLETADA (2026-08-24, Sesión 3) | +3 | ✅ |
| 4 | FASE-R0-D | B6+B7 propuesta condicional | `05-prompt-inicio-sesion-fase-R0-D.md` | ✅ COMPLETADA (2026-08-24, Sesión 4) | +4 | ☐ |
| 5 | FASE-R0-E | E2E única v4complete Zione | `05-prompt-inicio-sesion-fase-R0-E.md` | ✅ COMPLETADA (2026-08-24, Sesión 5 + recuperación) | +6 (recovery) | ✅ |
| 6 | FASE-R0-F | Verificación AC1-AC12 + análisis | `05-prompt-inicio-sesion-fase-R0-F.md` | ✅ COMPLETADA (2026-08-24, Sesión 6) | 0 (12/12 ACs) | ✅ |
| 7 | FASE-RELEASE-4.72.1 | Docs oficiales + bump | `05-prompt-inicio-sesion-fase-RELEASE.md` | ⏳ PENDIENTE | 0 | ☐ (auto-detect) |

## Gates de Entrada/Salida por Fase

### FASE-R0-A → R0-B
- **Entrada**: v4.72.0 estable; tests base 3,360.
- **Salida**: Quick Win #1 condicionado a `whatsapp_conflict`; 1 test nuevo; AC12 grep limpio; `log_phase_completion.py` ejecutado SIN `--release`.

### FASE-R0-B → R0-C ⚠️ (fase de mayor complejidad técnica)
- **Entrada**: R0-A ✅ (quick win ya condicionado).
- **Salida**: `_build_fugas_principales_section()` operativo (reutiliza narrativa dinámica de `_pain_to_brecha()` — D-NC6, sin tabla estática nueva); template L65-77 reemplazado por `${fugas_principales_section}`; título "LAS {N} FUGAS" con N = `len(brechas_destacadas)` (D-NC1); filtro VERIFIED_IN_SITE respetado (`_identify_brechas()` L3043-3044); 4 tests nuevos; `log_phase_completion.py` SIN `--release`.

### FASE-R0-C → R0-D
- **Entrada**: R0-B ✅ (sección 4 ya dinámica).
- **Salida**: título Sección 1 condicional vía variable de canales (D-NC4); contador Sección 6 reutilizando `${brechas_total_count}` (D-NC5); 3 tests nuevos; `log_phase_completion.py` SIN `--release`.

### FASE-R0-D → R0-E
- **Entrada**: R0-C ✅.
- **Salida**: plan 30 días condicional a `whatsapp_conflict` (cableado a `_build_30_day_plan`); botón de WhatsApp fuera de "Servicios adicionales" cuando no hay brecha ni conflicto (signal `breach_by_asset`, sin claim de presencia); 4 tests nuevos (total plan: 12); `log_phase_completion.py` SIN `--release`.

### FASE-R0-E → R0-F
- **Entrada**: A+B+C+D ✅ TODAS (gate duro — la corrida debe reflejar todos los fixes).
- **Salida**: baseline anómalo 20260821_175706 preservado en `evidence/FASE-R0-E/baseline/`; **única ejecución** `v4complete --url https://zione.co/` (vía delegate_task); evidencia proactiva en `evidence/FASE-R0-E/`; smoke S1-S7 ✅; `log_phase_completion.py` SIN `--release`.

### FASE-R0-F → RELEASE
- **Entrada**: R0-E ✅ (output post-fix + evidencia disponibles).
- **Salida**: matriz AC1-AC12 completa (12/12 PASA esperado); mínimo 3 lecciones nuevas; `10-analisis-post-implementacion.md` COMPLETO; `log_phase_completion.py` SIN `--release`.

### FASE-RELEASE-4.72.1 (final)
- **Entrada**: TODAS las fases ✅ (regla de dependencia del executor — si alguna no está ✅: ABORTAR).
- **Salida**: VERSION.yaml 4.72.1 + sync 6 archivos; CHANGELOG `[4.72.1]`; GUIA_TECNICA "Notas de Cambios v4.72.1"; SYSTEM_STATUS + DOMAIN_PRIMER regenerados; README/AGENTS audit (test count 3,372); Version Sync Gate OK; commit de release.

## Verificación Anti-Deuda (executor §2.5) — check pre-ejecución

- [x] FASE-R0-A a FASE-R0-F: cada prompt termina con `log_phase_completion.py` SIN `--release` (verificado en preparación 2026-08-22).
- [x] FASE-RELEASE-4.72.1: NO registra fases anteriores — solo sincroniza y valida.
- [x] Ningún prompt intermedio contiene `--release` (check "Prompts No Release" de `run_all_validations.py`).

## Métricas de Progreso (actualizar al cierre de cada fase)

| Métrica | Base (v4.72.0) | Actual | Objetivo |
|---------|----------------|--------|----------|
| Tests totales | 3,360 | 3,378 | 3,372 (+12) + 6 recovery |
| Bugs B1-B7 abiertos | 7 | 0 | 0 |
| AC1-AC12 certificados | 0/12 | 12/12 PASA (10 con verificación E2E + 2 por unit test exclusivo) | 12/12 |
| Coherence E2E Zione | 0.9485 (anómalo narrativo) | 0.9485 (corrida 20260824_113525, narrativa dinámica verificada) | ≥ 0.8 con narrativa correcta |
| Gates | 13/13 (12 PASSED + 1 WARNING) | 12 PASSED + 1 WARNING (idéntico baseline, tier B+) | mismo estado (sin regresión) |
