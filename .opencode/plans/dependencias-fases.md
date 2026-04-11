# Dependencias entre Fases — Rediseño Motor Financiero (Opción C)

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha**: 2026-04-10
**Contexto**: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md`

---

## Diagrama de Dependencias

```
FASE-A ──→ FASE-B ──→ FASE-E ──→ FASE-F ──→ FASE-G
  │           │                      ↑
  │           └──→ FASE-C ──────────┘
  │
  └──→ FASE-D (independiente, paralela a B y C)
```

## Tabla de Fases

| Fase | Nombre | Archivos principales | Depende de | Estado |
|------|--------|---------------------|------------|--------|
| FASE-A | Data Structures + FinancialBreakdown | `data_structures.py` | Ninguna | ✅ 2026-04-10 |
| FASE-B | ScenarioCalculator narrativa por capas | `scenario_calculator.py`, `financial_calculator_v2.py` | FASE-A | ✅ 2026-04-11 |
| FASE-C | Pesos normalizados + DynamicImpact | `v4_diagnostic_generator.py` (pesos), `dynamic_impact.py` | FASE-A |
| FASE-D | Scraper→ADR conexión | `adr_resolution_wrapper.py`, `web_scraper.py`, `main.py:1526` | FASE-A |
| FASE-E | Consumidores actualización | `v4_proposal_generator.py`, `coherence_validator.py`, `asset_diagnostic_linker.py` | FASE-B, FASE-C |
| FASE-F | Template diagnóstico + Evidence Tiers | `diagnostico_v6_template.md`, `v4_diagnostic_generator.py` (placeholders) | FASE-E |
| FASE-G | Integración main.py + end-to-end | `main.py:1664-1910`, tests de regresión | FASE-F, FASE-D |

## Conflictos Potenciales (archivos compartidos)

| Archivo | Fases que lo tocan | Riesgo |
|---------|-------------------|--------|
| `data_structures.py` | A (crear campos), B (ajustar Scenario) | BAJO — A crea, B consume |
| `v4_diagnostic_generator.py` | C (pesos), F (placeholders/template) | MEDIO — distintas secciones |
| `main.py` | D (línea 1526), G (líneas 1664-1910) | BAJO — distintas zonas |
| `scenario_calculator.py` | B (rediseño completo) | BAJO — una sola fase |
| `v4_proposal_generator.py` | E (22 puntos de consumo) | BAJO — una sola fase |
| `coherence_validator.py` | E (línea 433) | BAJO — una sola fase |

## Orden de Ejecución

```
Sesión 1: FASE-A (fundación — nuevas estructuras de datos)
Sesión 2: FASE-B (motor de cálculo por capas) + FASE-D puede ejecutarse en paralelo
Sesión 3: FASE-C (normalización de pesos) [o FASE-D si no se hizo en paralelo]
Sesión 4: FASE-D (si no se ejecutó) o FASE-E (consumidores)
Sesión 5: FASE-E (consumidores) o FASE-F (template)
Sesión 6: FASE-F (template + evidence tiers)
Sesión 7: FASE-G (integración main.py + end-to-end)
```

**Nota**: FASE-B, C y D son parcialmente paralelas (no compiten por archivos).
La regla de "una fase por sesión" aplica estrictamente. El paralelismo es lógico, no temporal.

---

## Criterios de Éxito Globales

1. Cada costo en COP es **rastreable** a una fuente (onboarding, scraping, benchmark)
2. Pesos de brechas **normalizados** (suma siempre = 100%)
3. Valores etiquetados como **VERIFIED** o **ESTIMATED**
4. **Hecho verificable** (comisión OTA real) como dato principal
5. Promesa README línea 63: "asigna un costo en COP a cada brecha detectada, y genera un paquete de assets técnicos listos para deploy con validación cruzada de coherencia"
