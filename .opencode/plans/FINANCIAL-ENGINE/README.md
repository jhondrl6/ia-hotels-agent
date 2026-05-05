# Plan: Financial Evidence Engine + Regional Benchmark Fallback + Channel Prioritization

**Versión plan**: 1.2.0  
**Fecha creación**: 2026-05-03  
**Repo target**: iah-cli v4.39.0 → v4.40.0  
**Contexto**: `.opencode/context/Financing/FINANCIAL_ENGINE_PRECISION_CONTEXT.md`  
**Workflow**: `.agents/workflows/phased_project_executor.md` v2.10.0  
**Hotel E2E**: Hotel Castilla Real — https://www.hotelcastillareal.com/  
**Ejecuciones v4complete**: **1 (UNA)** — optimizado para minimizar costo API

---

## Objetivo

Eliminar la falsa precisión financiera ($2.610.000 COP/mes desde defaults) sin perder utilidad comercial, implementando tres capacidades:

1. **Financial Evidence Engine** → Metadata epistémica por campo + precision tiers + reglas de render
2. **Regional Benchmark Fallback Honesto** → Benchmarks regionales 2026 como estimación, no como dato exacto
3. **Evidence-Based Channel Prioritization** → Priorización de brechas ponderada por canal inferido con evidencia

## Criterio Rector

> Nunca mostrar dinero con más precisión que la evidencia que lo soporta; y nunca priorizar brechas por un canal que no fue inferido o confirmado con evidencia.

---

## Arquitectura de Fases (11 fases, 1 v4complete)

```
FIN-1A → FIN-1B → FIN-2A → FIN-2B → FIN-3 → CHAN-1 → CHAN-2 → FIN-4 → FIN-4A → FIN-4B → RELEASE
  │        │        │        │        │        │        │        │        │        │
  │        │        │        │        │        │        │        │        │        └── Docs + version
  │        │        │        │        │        │        │        │        └── PATCH: Integration fixes
  │        │        │        │        │        │        │        └── PATCH: Gap investigation
  │        │        │        │        │        │        └── E2E COMBINADO ⚡ (1 v4complete)
  │        │        │        │        │        └── Scorer integration
  │        │        │        │        └── Channel resolver
  │        │        │        └── Templates + rendering
  │        │        └── Flags + fallback chain
  │        └── Benchmark data source
  └── Validator + precision tier
```

| Fase | Tareas | Cmd largo | Modo Ejecución | Objetivo |
|------|:------:|:---------:|:--------------:|----------|
| **FIN-1A** | 4 | ❌ | DIRECTO ✅ | `FinancialEvidence` dataclass + propagación en data structures |
| **FIN-1B** | 4 | ❌ | DIRECTO ✅ | `NoDefaultsValidator` ampliado + `PrecisionValidator` |
| **FIN-2A** | 4 | ❌ | DIRECTO ✅ | `regional_adr_2026.json` + `RegionalADRResolver` con metadata |
| **FIN-2B** | 4 | ❌ | DIRECTO ✅ | `feature_flags.py` (Caribe) + fallback chain honesto |
| **FIN-3** | 4 | ❌ | DIRECTO ✅ | Templates + rendering: rangos, advertencias, CTA |
| **CHAN-1** | 3 | ❌ | DIRECTO ✅ | `channel_evidence_resolver.py` — inferencia sin hardcodear |
| **CHAN-2** | 4 | ❌ | DIRECTO ⏳ | `OpportunityScorer` con `channel_context` + multiplicadores |
| **FIN-4** | 3 | ✅ | Regla v4complete ✅ | **v4complete combinado**: validación financiera + comercial, Hotel Castilla Real |
| **FIN-4A** | 4 | ❌ | **DIRECTO** ⏳ | **PATCH**: Investigación de gaps (4 GAPs a file:line exacto) |
| **FIN-4B** | 4 | ❌ | **DIRECTO** ⏳ | **PATCH**: Implementación — cablear módulos al pipeline output |
| **RELEASE** | 5 | ❌ | **DIRECTO** ⏳ | Docs cascade, version bump, validaciones finales |

### Scope R3 por fase

Cada fase respeta: **máx 4 tareas + 0 comandos largos**, o **máx 3 tareas + 1 comando largo**.

---

## Optimización de Costos API

| Recurso | Original | Optimizado |
|---------|:--------:|:----------:|
| Ejecuciones v4complete | 2 (FIN-4 + CHAN-3) | **1 (FIN-4 combinado)** |
| Hotel E2E | hotelvisperas.com (2 veces) | **hotelcastillareal.com (1 vez)** |
| Fases totales | 10 | **11** (2 fases PATCH agregadas post-FIN-4) |
| Ahorro API | — | **~50% en costo v4complete** |

**Estrategia**: Todo el código se implementa primero (FIN-1A → CHAN-2, 7 fases). Al final, UNA sola ejecución de v4complete sobre Hotel Castilla Real valida simultáneamente:
- Precisión financiera (ADR ≠ $300K, rangos, advertencias, CTA)
- Priorización por canal (channel_context, multiplicadores, ranking ajustado)

**Resultado FIN-4**: ❌ 4 issues encontrados (ADR legacy persiste, precision_tier missing, channel_context/opportunity_scores vacíos en report JSON). Las fases FIN-4A (investigación) y FIN-4B (implementación) corrigen estos gaps sin requerir un segundo v4complete.

---

## Decisiones Arquitectónicas (pre-aprobadas)

| # | Decisión | Respuesta |
|---|---------|-----------|
| 1 | Fuente datos 2026 | Nuevo `data/benchmarks/regional_adr_2026.json` |
| 2 | Activación regional | Canary: `FINANCIAL_REGIONAL_ADR_ENABLED=true` |
| 3 | Cálculo de rangos | Escenarios conservador/realista/optimista |
| 4 | Precision tier | Por **peor fuente** |
| 5 | `LEGACY_DEFAULT_ADR` | Conservar como fallback invisible |
| 6 | Render advertencia | Generator inyecta variables; template decide render |
| 7 | `channel_evidence_resolver.py` | `modules/financial_engine/` |
| 8 | WhatsApp dominante | Solo con evidencia (onboarding 40%+ o web CTA único) |
| 9 | Anti dual-source | `channel_context` opcional en scorer |
| 10 | Hotel validación E2E | **Hotel Castilla Real** (`hotelcastillareal.com`) |

---

## Cómo Iniciar

### Fase actual (post-FIN-4): Investigación

```
Carga y ejecuta .opencode/plans/FINANCIAL-ENGINE/05-prompt-inicio-sesion-fase-FIN-4A.md 
siguiendo .agents/workflows/phased_project_executor.md
```

### Fase siguiente (después de FIN-4A): Implementación

```
Carga y ejecuta .opencode/plans/FINANCIAL-ENGINE/05-prompt-inicio-sesion-fase-FIN-4B.md 
siguiendo .agents/workflows/phased_project_executor.md
```
