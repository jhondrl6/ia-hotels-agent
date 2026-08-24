# Dependencias entre Fases — REFACTOR-COHERENCIA-NARRATIVA-2026-08-22

## Diagrama de Dependencias

```
                        ┌──────────────────────────────────────────────────────────┐
                        │  CONTEXTO (ya validado contra código vivo 2026-08-22)     │
                        │  7 bugs (B1-B7) · causa raíz: fosilización narrativa      │
                        └──────────────────────────────────────────────────────────┘
                                                   │
                     ┌─────────────────────────────┴─────────────────────────────┐
                     ▼                                                           ▼
           ┌──────────────────┐                                        ┌──────────────────┐
           │ FASE-R0-A (B2)   │                                        │ FASE-R0-D (B6+B7)│
           │ Quick Win #1     │   (archivos distintos, orden libre;     │ Propuesta        │
           │ DIRECTO          │    ejecución secuencial por R1)         │ condicional      │
           └────────┬─────────┘                                        └────────┬─────────┘
                    │ soft-dep (mismo archivo .py)                               │
                    ▼                                                            │
           ┌──────────────────┐                                                  │
           │ FASE-R0-B (B1+B4)│ ⚠️ MAYOR COMPLEJIDAD TÉCNICA                     │
           │ Sección 4        │                                                  │
           │ dinámica         │                                                  │
           │ DIRECTO          │                                                  │
           └────────┬─────────┘                                                  │
                    │ hard-dep (test estático de template requiere B1+B4 listo)  │
                    ▼                                                            │
           ┌──────────────────┐                                                  │
           │ FASE-R0-C (B3+B5)│                                                  │
           │ Título S1 + S6   │                                                  │
           │ DIRECTO          │                                                  │
           └────────┬─────────┘                                                  │
                    │                                                            │
                    └────────────────────────┬───────────────────────────────────┘
                                             ▼
                                  ┌─────────────────────────────┐
                                  │ FASE-R0-E (E2E)             │
                                  │ ÚNICA ejecución v4complete  │
                                  │ Zione · delegate_task       │
                                  │ DEP: A+B+C+D completas ✅   │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ FASE-R0-F (Verificación)    │
                                  │ AC1-AC12 + lecciones        │
                                  │ DEP: E completada ✅        │
                                  └──────────────┬──────────────┘
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │ FASE-RELEASE-4.72.1         │
                                  │ Docs + version bump         │
                                  │ DEP: TODAS completadas ✅   │
                                  └─────────────────────────────┘
```

## Tabla de Dependencias

| Fase | Depende de | Tipo | Motivo |
|------|-----------|------|--------|
| FASE-R0-A | — | — | Primera fase |
| FASE-R0-B | FASE-R0-A | Soft (orden) | Mismo archivo `v4_diagnostic_generator.py`, zona distinta (quick wins vs sección 4). Evita conflictos de edición |
| FASE-R0-C | FASE-R0-B | **Hard** | `test_template_no_hardcoded_fugas` (estático) exige que B1+B4 ya hayan retirado el texto hardcoded del template. Mismo template + render dict |
| FASE-R0-D | — (independiente por archivos) | Soft (orden) | `v4_proposal_generator.py` no depende de A/B/C; se ejecuta tras C solo por secuencia R1 |
| FASE-R0-E | A + B + C + D | **Hard** | La corrida E2E debe reflejar TODOS los fixes para la verificación |
| FASE-R0-F | FASE-R0-E | **Hard** | Verifica ACs contra el output generado en E |
| FASE-RELEASE-4.72.1 | A + B + C + D + E + F | **Hard** | El executor aborta RELEASE si alguna fase previa no está ✅ |

## Conflictos de Archivos (qué modifica cada fase)

| Archivo | R0-A | R0-B | R0-C | R0-D | R0-E | R0-F | RELEASE |
|---------|------|------|------|------|------|------|---------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | ✏️ L1883-88 | ✏️ nuevo método + render dict ~L919-923 | ✏️ variables título S1 | — | — | — | — |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | — | ✏️ L65-77 | ✏️ L29, L39, L89 | — | — | — | — |
| `modules/commercial_documents/v4_proposal_generator.py` | — | — | — | ✏️ L2195, L1455-57 (+callers) | — | — | — |
| `tests/commercial_documents/test_diagnostic_generator.py` | ➕ 1 test | ➕ 4 tests | — | — | — | — | — |
| `tests/commercial_documents/test_template_conditionals.py` | — | — | ➕ 3 tests | — | — | — | — |
| `tests/commercial_documents/test_proposal_dynamic.py` | — | — | — | ➕ 4 tests | — | — | — |
| `output/v4_complete/*` | — | — | — | — | 🆕 generación | (lectura) | — |
| `evidence/FASE-R0-E/` | — | — | — | — | 🆕 baseline + output | (lectura) | — |
| `10-analisis-post-implementacion.md` | ✏️ cierre | ✏️ cierre | ✏️ cierre | ✏️ cierre | ✏️ cierre | ✏️ matriz+lecciones | ✏️ checklist cierre |
| `VERSION.yaml`, `CHANGELOG.md`, `GUIA_TECNICA.md`, `README.md`, `AGENTS.md` | — | — | — | — | — | — | ✏️ (única) |

**Leyenda**: ✏️ modifica · ➕ agrega tests · 🆕 crea · — no toca

## Nota sobre Desplazamiento de Líneas

Los números de línea citados en los prompts provienen del CONTEXT validado el 2026-08-22 sobre v4.72.0 **sin los fixes de este plan**. Tras cada fase, las líneas pueden desplazarse (±15 líneas acumuladas tras A, B y C). **Anclar siempre por contenido (texto/símbolo), no por número de línea.**

## Regla de Ejecución

- **R1 (executor)**: una fase por sesión. El orden canónico es A → B → C → D → E → F → RELEASE.
- **R0-D es reubicable**: si una sesión de A/B/C quedara incompleta y R0-D estuviera lista para ejecutar en una sesión fresca (sus archivos no dependen de las anteriores), puede ejecutarse antes sin romper dependencias. Documentar el reordenamiento en este archivo si ocurre.

## Estado de Ejecución (actualizar al cierre de cada fase)

| Fase | Estado | Checkpoint / Notas |
|------|--------|--------------------|
| FASE-R0-A | ✅ Completada | 2026-08-22 — Fix B2: texto Quick Win #1 ahora corresponde a condición `not hotel_schema_detected` (datos/Schema en Google, sin WhatsApp). 1 test nuevo. 59/59 tests pasan. |
| FASE-R0-B | ✅ Completada | 2026-08-24 — Fix B1+B4: nuevo `_build_fugas_principales_section()` (narrativa dinámica de `_pain_to_brecha()`, D-NC6) + template L65-77 → `${fugas_title}` + `${fugas_principales_section}` + inyección en render dict junto a contadores. D-NC1/2/3/6 implementadas; extensión menor de D-NC1: título vía `${fugas_title}` con pluralización (SIN FUGAS / LA FUGA / LAS N FUGAS). 4 tests nuevos (total 3,365). Suites: 27 diagnostic_generator + 42 brechas + 6 template_conditionals + 26 regression pasan. Greps AC7/B1 limpios (0 resultados). |
| FASE-R0-C | ✅ Completada | 2026-08-24 — Fix B3+B5: título S1 condicional a conflicto WhatsApp real vía helper compartido `_has_whatsapp_conflict()` (D-NC4); cláusula L39 condicional; contador S6 dinámico `${brechas_total_count}` (D-NC5). 3 tests nuevos (total 3,368). Suites: 9 template_conditionals + 27 diagnostic_generator + 26 regression pasan. |
| FASE-R0-D | ✅ Completada | 2026-08-24 — Fix B6+B7: plan 30 días condicional a `whatsapp_conflict` (parámetro cableado a `_build_30_day_plan()`); botón WhatsApp fuera de "Servicios adicionales" cuando no hay brecha ni conflicto (signal `breach_by_asset` + `whatsapp_conflict`, sin claim de presencia). 4 tests nuevos (total 3,372). Suites: proposal_dynamic + breach_consistency + 26 regression pasan. |
| FASE-R0-E | ✅ Completada | 2026-08-24 — Corrida inicial: gate `tier_c_onboarding_required` BLOCKED falso (causa raíz: commit 3e88251 "FIX V6" usó `FinancialFactors()` en bloque FASE-K de main.py sin import en `run_v4_complete_mode` → NameError atrapado → breakdown=None → tier default "C"). **Sesión de recuperación (autorizada, misma sesión)**: import agregado + 6 tests anti-regresión (`test_fase_r0e_recovery_financial_factors.py`) + re-ejecución autorizada (timestamp 20260824_113525). Resultado: coherence 0.9485 (idéntico baseline), gates 12 PASSED + 1 WARNING (idéntico baseline), tier B+, READY_FOR_PUBLICATION, 7 pain_ids sin WhatsApp. Smoke S1-S7: 7/7 ✅. Narrativa E2E verificada: "LAS 7 FUGAS PRINCIPALES", título S1 sin WhatsApp, contador dinámico, plan 30 días sin WhatsApp, botón fuera de adicionales. Baseline + output en `evidence/FASE-R0-E/`. |
| FASE-R0-F | ⏳ Pendiente | — |
| FASE-RELEASE-4.72.1 | ⏳ Pendiente | — |
