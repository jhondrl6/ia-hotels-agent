# ROICR — Refactorización Motor Financiero v3.0

**Versión**: v1.0.0 (plan)
**Target Release**: v4.55.0 — ROICR
**Creado**: 2026-05-27
**Origen**: `ROICR.md` (contexto unificado) — diagnóstico financiero + capa de ejecución comercial
**Objetivo**: Implementar los 4 pilares de refactorización financiera + gobernanza comercial + garantía auditable para que la propuesta de Hotel Castilla Real sea comercialmente viable (ROI SaaS 1.93X en vez de 0.3X).

---

## Resumen del Problema

El plan ROI-REFACTOR (FASE-0 a FASE-5, v4.54.0) corrigió problemas de **presentación** (alertas, jerga, placeholders). Pero el ROICR.md revela que persisten **6 problemas estructurales** que hacen que la propuesta sea comercialmente invendible:

| # | Problema | Severidad | Impacto |
|---|----------|-----------|---------|
| 1 | **Mapper produce alucinaciones semánticas** — une brechas a activos ilógicos | CRÍTICO | Propuesta miente al cliente |
| 2 | **ROI negativo** — precio $1.2M vs recovery $748K | CRÍTICO | Arbitraje negativo, ningún GM firma |
| 3 | **Assets redundantes sin migration_target** — deprecar rompe el mapper | PERTINENTE | UnmappedPainError al deprecar guías |
| 4 | **Gate permite propuestas con assets P1 NOT_READY** | CRÍTICO | Promesas falsas en PDF |
| 5 | **Garantía Día 55 sin trigger técnico** — pitch promete, código no audita | CRÍTICO | Riesgo reputacional |
| 6 | **+2,743 tests rompen** con cambios de pricing | CRÍTICO | CI/CD rechaza PR |

**Solución**: 4 Pilares (Pipeline Unificado + CAPEX/OPEX Desacoplado + Curva 4 Pilares + Gate de Confianza) + Semántica de Activos + Garantía Auditable.

---

## Fases del Plan

| Fase | Descripción | Tipo | Problemas | Prerrequisito |
|------|-------------|------|-----------|---------------|
| **FASE-1** | Semántica de activos: AssetSemanticsValidator + migration_target + narrativas dinámicas | Código+Tests | #1, #3 | Ninguno |
| **FASE-2** | Gate hardening: proposal_asset_alignment BLOCKING para P1 | Código+Tests | #4 | FASE-1 |
| **FASE-3** | Pipeline unificado pricing + CAPEX/OPEX desacoplado + curva 4 pilares | Código+Tests | #2 | FASE-2 |
| **FASE-4** | Arbitraje ético gate + Garantía Día 55 + comando validate-guarantee | Código+Tests | #5 | FASE-3 |
| **FASE-5** | Fixtures financieros + recalibración regression guardian + tests nuevos | Tests+Fixtures | #6 | FASE-4 |
| **FASE-6** | v4complete Hotel Castilla Real + análisis post-implementación 5 niveles | Ejecución | Todos | FASE-5 |
| **FASE-7** | RELEASE v4.55.0: docs sync, version bump, changelog, pre-commit | Docs+Sync | — | FASE-6 |

**Total**: 7 sesiones. 1 fase por sesión. 1 v4complete en FASE-6. FASE-7 = RELEASE.

---

## Métricas Base (pre-ROICR, post-ROI-REFACTOR)

| Métrica | Valor Actual |
|---------|-------------|
| Versión | v4.54.0 |
| Coherence Score | 0.83 |
| Publication Gates | 10/11 |
| Pain Ledger | 11 entries |
| ROI Castilla Real | -$5,367,168 COP / 0.3X |
| Pricing Floor | $1,200,000 COP (ciego) |
| CAPEX/OPEX | Mezclados en ROI |
| Mapper semántico | Sin validación |
| Garantía Día 55 | Solo en pitch, no en código |
| Assets redundantes | Sin migration_target |

---

## Métricas Objetivo (post-ROICR)

| Métrica | Objetivo |
|---------|----------|
| ROI SaaS (6m) | 1.28X (→ 1.93X maduro) |
| Pricing final Castilla Real | $654,796 COP (limitado por Value-Capture Cap) |
| ROI SaaS / CAPEX | Métricas desacopladas |
| Mapper | AssetSemanticsValidator bloquea alucinaciones |
| Gate P1 | BLOCKING si asset NOT_READY |
| Garantía | `validate-guarantee` ejecutable |
| Tests | +2,743 sin regresiones |

---

## Criterio de Éxito Final (FASE-6)

Al completar FASE-6, el output de v4complete para Hotel Castilla Real debe satisfacer:

- [ ] **Nivel 1 — Pricing Ético**: Pipeline unificado de 3 pasos produce $654,796 COP (no $1.2M). Value-Capture Cap funciona. Pain Ratio no produce arbitraje negativo.
- [ ] **Nivel 2 — CAPEX/OPEX Desacoplado**: Propuesta muestra Tabla CAPEX (único $2.5M) y Tabla OPEX (mensual $654K) separadas. ROI SaaS independiente > 1.0X.
- [ ] **Nivel 3 — Curva 4 Pilares**: Proyección 6 meses usa `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]` no lineal. Mes 3 = punto de equilibrio.
- [ ] **Nivel 4 — Gobernanza Comercial**: Mapper no produce alucinaciones. Assets DEPRECATED tienen migration_target. Gate P1 es BLOCKING.
- [ ] **Nivel 5 — Garantía Auditable**: `python main.py validate-guarantee --url https://www.hotelcastillareal.com/` ejecuta sin errores.
- [ ] **Nivel 6 — CI/CD**: pytest completo sin regresiones. Fixtures actualizados.

---

## Archivos del Plan

| Archivo | Propósito |
|---------|-----------|
| `README.md` | Este archivo — índice del plan |
| `dependencias-fases.md` | Diagrama de dependencias entre fases |
| `05-prompt-inicio-sesion-fase-1.md` | Prompt para FASE-1 (Semántica de Activos) |
| `05-prompt-inicio-sesion-fase-2.md` | Prompt para FASE-2 (Gate Hardening) |
| `05-prompt-inicio-sesion-fase-3.md` | Prompt para FASE-3 (Pipeline + CAPEX/OPEX + Curva) |
| `05-prompt-inicio-sesion-fase-4.md` | Prompt para FASE-4 (Arbitraje + Garantía) |
| `05-prompt-inicio-sesion-fase-5.md` | Prompt para FASE-5 (Tests + Fixtures) |
| `05-prompt-inicio-sesion-fase-6.md` | Prompt para FASE-6 (v4complete + Análisis) |
| `05-prompt-inicio-sesion-fase-7.md` | Prompt para FASE-7 (RELEASE) |
| `06-checklist-implementacion.md` | Checklist maestro de implementación |
| `09-documentacion-post-proyecto.md` | Acumulador de documentación post-fase |

---

## Lo que este plan NO hace

- ❌ NO repite los fixes del plan ROI-REFACTOR (ya completados: alertas, jerga, placeholders, etc.)
- ❌ NO modifica la fórmula base del ROI — solo la presenta correctamente (desacoplada)
- ❌ NO infla recovery_factor — usa 35% (realista con 4 pilares)
- ❌ NO toca el plan PROPUESTA-COMERCIAL ni ROI-REFACTOR

---

## Lo que SÍ se preserva

- ✅ Puente dual CROSS-1 (fuga bruta ↔ recuperación efectiva)
- ✅ Mapping brecha→servicio CROSS-2
- ✅ Gate blocking CROSS-6
- ✅ Decisión comercial Opción E (FASE-0 de ROI-REFACTOR)
- ✅ Todos los fixes de presentación (ROI-REFACTOR FASE-1 a FASE-4)
