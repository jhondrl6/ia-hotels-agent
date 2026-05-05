# Dependencias entre Fases — Financial Evidence Engine

**Plan**: FINANCIAL-ENGINE v1.2.0  
**Fecha**: 2026-05-03  
**Hotel E2E**: Hotel Castilla Real (hotelcastillareal.com)  
**v4complete**: 1 ejecución (FIN-4 combinado)

---

## Diagrama de Dependencias

```
FIN-1A (Epistemic Metadata Model)
  │
  ├──► FIN-1B (NoDefaultsValidator + Precision Tier)
  │      │
  │      ├──► FIN-2A (Regional Benchmark Data)
  │      │      │
  │      │      ├──► FIN-2B (Feature Flags + Fallback Chain)
  │      │             │
  │      │             ├──► FIN-3 (Rendering: Rangos + Advertencias)
  │      │                    │
  │      │                    ├──► CHAN-1 (Channel Evidence Resolver)
  │      │                           │
  │      │                           ├──► CHAN-2 (OpportunityScorer Integration)
  │      │                                  │
  │      │                                  ├──► FIN-4 (E2E COMBINADO) ⚡ 1 v4complete
  │      │                                         │
  │      │                                         ├──► FIN-4A (PATCH: Gap Investigation)
  │      │                                                │
  │      │                                                ├──► FIN-4B (PATCH: Integration Fixes)
  │      │                                                       │
  └──────┴───────────────────────────────────────────────────────┴──► RELEASE (Docs + Version)
```

---

## Orden de Ejecución Estricto

| # | Fase | Depende de | Tipo |
|---|------|-----------|------|
| 1 | FIN-1A | — | Código |
| 2 | FIN-1B | FIN-1A | Código |
| 3 | FIN-2A | FIN-1B | Código |
| 4 | FIN-2B | FIN-2A | Código |
| 5 | FIN-3 | FIN-2B | Código |
| 6 | CHAN-1 | FIN-3 | Código |
| 7 | CHAN-2 | CHAN-1 | Código |
| 8 | FIN-4 | CHAN-2 | **E2E COMBINADO** (1 v4complete) |
| 9 | FIN-4A | FIN-4 | **PATCH**: Investigación de gaps (código puro) |
| 10 | FIN-4B | FIN-4A | **PATCH**: Integración de fixes (código puro) |
| 11 | RELEASE | FIN-4B | Documentación |

---

## Tabla de Conflictos de Archivos

| Archivo | FIN-1A | FIN-1B | FIN-2A | FIN-2B | FIN-3 | CHAN-2 | FIN-4 | FIN-4B |
|---------|:------:|:------:|:------:|:------:|:-----:|:------:|:-----:|:------:|
| `financial_evidence.py` | **CREA** | — | — | — | — | — | — | — |
| `scenario_calculator.py` | MOD | — | — | — | — | — | — | MOD? |
| `calculator_v2.py` | MOD | — | — | — | — | — | — | — |
| `precision_validator.py` | — | **CREA** | — | — | — | — | — | — |
| `no_defaults_validator.py` | — | MOD | — | — | — | — | — | — |
| `regional_adr_2026.json` | — | — | **CREA** | — | — | — | — | — |
| `regional_adr_resolver.py` | — | — | MOD | — | — | — | — | — |
| `feature_flags.py` | — | — | — | MOD | — | — | — | MOD? |
| `adr_resolution_wrapper.py` | — | — | — | MOD | — | — | — | MOD? |
| `v4_diagnostic_generator.py` | — | — | — | — | MOD | MOD | — | MOD |
| `templates/*.md` | — | — | — | — | MOD | — | — | — |
| `channel_evidence_resolver.py` | — | — | — | — | — | — | *CHAN-1 crea | — |
| `opportunity_scorer.py` | — | — | — | — | — | MOD | — | — |
| `harness_handlers.py` | — | — | — | — | — | — | — | MOD? |
| `test_financial_4b_integration.py` | — | — | — | — | — | — | — | **CREA** |

### Reglas de conflicto

- `v4_diagnostic_generator.py`: Modificado por FIN-3 (render) y CHAN-2 (channel_context). CHAN-2 extiende sobre el estado post-FIN-3.
- `channel_evidence_resolver.py`: Creado en CHAN-1, consumido en CHAN-2. Sin conflicto.
- FIN-4 es solo validación: NO modifica código.

---

## Notas

- **8 fases de código** (FIN-1A a CHAN-2) antes del v4complete
- **1 fase E2E** (FIN-4) que valida TODO junto: financiero + canales
- **2 fases PATCH** (FIN-4A, FIN-4B) que corrigen los 4 GAPs encontrados en FIN-4
- **1 fase RELEASE** solo toca documentación
- El v4complete en FIN-4 se ejecutó con `FINANCIAL_REGIONAL_ADR_ENABLED=true` + `FINANCIAL_REGIONAL_ADR_MODE=active`
- FIN-4B NO ejecuta v4complete — solo código + tests
