# Dependencias entre Fases — Rediseño Motor Financiero (Opción C)

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha**: 2026-04-10
**Contexto**: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md`

---

## Diagrama de Dependencias

```
CICLO 1 (COMPLETADO):
FASE-A ──→ FASE-B ──→ FASE-E ──→ FASE-F ──→ FASE-G
  │           │                      ↑
  │           └──→ FASE-C ──────────┘
  │
  └──→ FASE-D (independiente, paralela a B y C)

FASE-H (validación regional, SHADOW — NO promovido a ACTIVE)

CICLO 2 (CAUSA RAIZ):
FASE-I ──────┐
             ├──→ FASE-K → v4complete validacion final
FASE-J ──────┘

FASE-I y FASE-J son INDEPENDIENTES → paralelizables via subagentes
FASE-K depende de AMBAS (I + J completadas)
```

## Tabla de Fases

### Ciclo 1: Rediseño Motor Financiero (Opcion C)

| Fase | Nombre | Archivos principales | Depende de | Estado |
|------|--------|---------------------|------------|--------|
| FASE-A | Data Structures + FinancialBreakdown | `data_structures.py` | Ninguna | ✅ 2026-04-10 |
| FASE-B | ScenarioCalculator narrativa por capas | `scenario_calculator.py`, `financial_calculator_v2.py` | FASE-A | ✅ 2026-04-11 |
| FASE-C | Pesos normalizados + DynamicImpact | `v4_diagnostic_generator.py` (pesos), `dynamic_impact.py` | FASE-A | ✅ 2026-04-11 |
| FASE-D | Scraper→ADR conexión | `adr_resolution_wrapper.py`, `web_scraper.py`, `main.py:1526` | FASE-A | ✅ 2026-04-11 |
| FASE-E | Consumidores actualización | `v4_proposal_generator.py`, `coherence_validator.py`, `asset_diagnostic_linker.py` | FASE-B, FASE-C | ✅ 2026-04-11 |
| FASE-F | Template diagnóstico + Evidence Tiers | `diagnostico_v6_template.md`, `v4_diagnostic_generator.py` (placeholders) | FASE-E | ✅ 2026-04-11 |
| FASE-G | Integración main.py + end-to-end | `main.py:1664-1910`, tests de regresión | FASE-F, FASE-D | ✅ 2026-04-11 |
| FASE-H | Activar RegionalADRResolver (SHADOW) | `feature_flags.py`, `regional_adr_resolver.py` | FASE-A..G | ✅ 2026-04-11 |

### Ciclo 2: Causa Raiz — Datos No Verificables

| Fase | Nombre | Archivos principales | Depende de | Estado |
|------|--------|---------------------|------------|--------|
|| FASE-I | Activar RegionalADRResolver por regiones validadas | `feature_flags.py`, `harness_handlers.py`, `main.py` | FASE-H | ✅ 2026-04-11 |
|| FASE-J | NoDefaultsValidator source-aware + template honesto | `no_defaults_validator.py`, `calculator_v2.py`, `diagnostico_v6_template.md`, `v4_diagnostic_generator.py` | FASE-F | ✅ 2026-04-11 |
|| FASE-K | Unificar camino dual + fix optimista negativo | `main.py`, `harness_handlers.py`, `scenario_calculator.py` | FASE-I, FASE-J | ⬜ Pendiente |

## Conflictos Potenciales (archivos compartidos) — Ciclo 2

| Archivo | FASE-I | FASE-J | FASE-K | Resolucion |
|---------|--------|--------|--------|------------|
| `feature_flags.py` | TOCA | - | - | Solo I |
| `harness_handlers.py` | TOCA (datos regionales) | - | TOCA (usar calc_v2) | K despues de I |
| `main.py L1600-1650` | TOCA | - | - | Solo I |
| `main.py L1720-1733` | - | - | TOCA | Solo K |
| `no_defaults_validator.py` | - | TOCA | - | Solo J |
| `calculator_v2.py` | - | TOCA | - | Solo J |
| `diagnostico_v6_template.md` | - | TOCA | - | Solo J |
| `v4_diagnostic_generator.py` | - | TOCA | - | Solo J |
| `scenario_calculator.py` | - | - | TOCA | Solo K |

**FASE-I y FASE-J son 100% independientes** → paralelizables via delegate_task.
FASE-K toca 2 archivos que I tambien toca (harness_handlers, main.py) → requiere que I termine primero.

## Orden de Ejecucion — Ciclo 2

```
Sesion 1: FASE-I + FASE-J en PARALELO (via delegate_task, 2 subagentes)
Sesion 2: FASE-K (requiere I + J completadas) + v4complete validacion final
```

**Alternativa secuencial** (si paralelo no es viable):
```
Sesion 1: FASE-I (regional ADR)
Sesion 2: FASE-J (validator + template)
Sesion 3: FASE-K (unificar + fix optimista) + v4complete
```

### Validacion Pre-Paralelo (CHECKLIST antes de ejecutar I+J en paralelo)
- [ ] FASE-I y FASE-J NO comparten archivos (verificado arriba)
- [ ] Ambas dependen solo de fases COMPLETADAS (A..H)
- [ ] Tests directories no se solapan
- [ ] Ambas tienen post-ejecucion INDEPENDIENTE (REGISTRY/log_phase)

---

## Criterios de Éxito Globales

1. Cada costo en COP es **rastreable** a una fuente (onboarding, scraping, benchmark)
2. Pesos de brechas **normalizados** (suma siempre = 100%)
3. Valores etiquetados como **VERIFIED** o **ESTIMATED**
4. **Hecho verificable** (comisión OTA real) como dato principal
5. Promesa README línea 63: "asigna un costo en COP a cada brecha detectada, y genera un paquete de assets técnicos listos para deploy con validación cruzada de coherencia"
