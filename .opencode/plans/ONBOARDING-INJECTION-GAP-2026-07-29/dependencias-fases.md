# Dependencias de Fases — ONBOARDING-INJECTION-GAP-2026-07-29

> **Plan maestro**: `01-plan-maestro.md`
> **Ultima actualizacion**: 2026-07-29 (post-auditoria C1-C8)

---

## Grafo de Dependencias

```
┌─────────────────────────────────────────────────┐
│ FASE-0-A: Loader rewrite + normalize_url        │
│           + frescura configurable               │
│ Archivos: main.py (1 funcion reescrita + 1 new) │
│ Bugs: B1, B2, N3                                │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│ FASE-0-B: CAMBIO A (persistir hotel.url)        │
│           + CAMBIO B (pasar output_dir)          │
│           + template url:None                    │
│ Archivos: main.py (2 puntos) + data_loader.py   │
│ Bugs: N4, N5 (completa B1)                       │
└────┬──────────────────┬─────────────────────────┘
     │                  │
     ▼                  ▼
┌──────────────┐  ┌───────────────────────────────┐
│ FASE-1       │  │ FASE-2                        │
│ Taxonomia    │  │ observations.json fallback    │
│ + deprecacion│  │ Archivos: main.py +           │
│ Archivos:    │  │  observations.json            │
│  scenario_   │  │ Bugs: §10c                    │
│  calculator  │  │                               │
│  .py +       │  │ ⚠️ DEPENDE de FASE-0-A        │
│  main.py     │  │ (modifica funcion reescrita)  │
│ Bugs: §10a,  │  │                               │
│  §10b        │  │                               │
│              │  │                               │
│ ✅ INDEPEN-  │  │                               │
│  DIENTE de   │  │                               │
│  FASE-0-A/B  │  │                               │
└──────┬───────┘  └──────────┬────────────────────┘
       │                     │
       └──────────┬──────────┘
                  ▼
       ┌─────────────────────┐
       │ FASE-3: Tests       │
       │ Archivos:           │
       │  tests/test_onboard │
       │  ing_injection.py   │
       │                     │
       │ ⚠️ DEPENDE de       │
       │ FASE-0-A+0-B+1+2    │
       └──────────┬──────────┘
                  ▼
       ┌─────────────────────────────────────────┐
       │ FASE-RELEASE-A: v4complete + verificacion│
       │ Archivos: output/v4_complete/            │
       │ ⚠️ DEPENDE de TODAS las fases            │
       └──────────┬──────────────────────────────┘
                  ▼
       ┌─────────────────────────────────────────┐
       │ FASE-RELEASE-B: Version bump + CHANGELOG │
       │ Archivos: VERSION.yaml, CHANGELOG.md,    │
       │           AGENTS.md, GUIA_TECNICA.md      │
       │ ⚠️ DEPENDE de RELEASE-A                   │
       └──────────┬──────────────────────────────┘
                  ▼
       ┌─────────────────────────────────────────┐
       │ FASE-RELEASE-C: Analisis + cierre        │
       │ Archivos: 08-analisis, 09-documentacion  │
       │ ⚠️ DEPENDE de RELEASE-B                   │
       └─────────────────────────────────────────┘
```

---

## Matriz de Conflictos de Archivos

| Archivo | 0-A | 0-B | 1 | 2 | 3 | REL-A | REL-B | REL-C |
|---------|-----|-----|---|---|---|-------|-------|-------|
| `main.py:_load_latest_onboarding_data()` | ✅ REWRITE | ❌ | ❌ | ✅ MOD | ❌ | ❌ | ❌ | ❌ |
| `main.py:_normalize_url()` | ✅ CREATE | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `main.py:run_onboard_mode()` | ❌ | ✅ MOD (CAM A) | ✅ MOD (L1113/8) | ❌ | ❌ | ❌ | ❌ | ❌ |
| `main.py:run_v4_complete_mode()` | ❌ | ✅ MOD (CAM B) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `main.py:_observation_to_onboarding_format()` | ❌ | ❌ | ❌ | ✅ CREATE | ❌ | ❌ | ❌ | ❌ |
| `modules/onboarding/data_loader.py` | ❌ | ✅ MOD (url:None) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `modules/financial_engine/scenario_calculator.py` | ❌ | ❌ | ✅ MOD | ❌ | ❌ | ❌ | ❌ | ❌ |
| `data/hotel_observations/observations.json` | ❌ | ❌ | ❌ | ✅ MOD | ❌ | ❌ | ❌ | ❌ |
| `tests/test_onboarding_injection.py` | ❌ | ❌ | ❌ | ❌ | ✅ CREATE | ❌ | ❌ | ❌ |
| `VERSION.yaml` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ MOD | ❌ |
| `CHANGELOG.md` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ MOD | ❌ |
| `AGENTS.md` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ MOD | ❌ |
| `GUIA_TECNICA.md` | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ MOD | ❌ |
| `output/v4_complete/` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ CREATE | ❌ | ❌ |

---

## Notas de Conflicto

### `main.py` — 5 fases tocan el mismo archivo

Todas las modificaciones son en **diferentes funciones o lineas no solapantes**:

| Fase | Funcion | Lineas |
|------|--------|--------|
| FASE-0-A | `_load_latest_onboarding_data()` | ~3396-3445 (rewrite) |
| FASE-0-A | `_normalize_url()` (nueva) | ~3447+ |
| FASE-0-B | `run_onboard_mode()` | ~1073 (CAMBIO A) |
| FASE-0-B | `run_v4_complete_mode()` | ~1739 (CAMBIO B) |
| FASE-1 | `run_onboard_mode()` | ~1113, ~1118 |
| FASE-2 | `_load_latest_onboarding_data()` | misma funcion que FASE-0-A |
| FASE-2 | `_observation_to_onboarding_format()` (nueva) | ~3460+ |

**Sin conflicto real**: Las modificaciones son en funciones diferentes y los patches por contenido (`old_string`/`new_string`) no generan conflictos.

---

## Tabla de Estados

| Fase | Estado | Depende de | Bloquea a |
|------|--------|------------|-----------|
| FASE-0-A | COMPLETADA (2026-07-29) | — | FASE-0-B, FASE-2, FASE-3 |
| FASE-0-B | COMPLETADA (2026-07-29) | FASE-0-A | FASE-3, FASE-RELEASE-A |
| FASE-1 | COMPLETADA (2026-07-29) | — | FASE-3, FASE-RELEASE-A |
| FASE-2 | COMPLETADA (2026-07-29) | FASE-0-A | FASE-3, FASE-RELEASE-A |
| FASE-3 | COMPLETADA (2026-07-29) | FASE-0-A, FASE-0-B, FASE-1, FASE-2 | FASE-RELEASE-A |
| FASE-RELEASE-A | COMPLETADA (2026-07-30) | FASE-0-A, 0-B, 1, 2, 3 | FASE-RELEASE-B |
| FASE-RELEASE-B | BLOQUEADA | FASE-RELEASE-A | FASE-RELEASE-C |
| FASE-RELEASE-C | BLOQUEADA | FASE-RELEASE-B | — |
