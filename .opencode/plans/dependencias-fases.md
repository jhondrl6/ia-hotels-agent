# Dependencias y Conflictos entre Fases

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Fecha preparación**: 2026-04-24
**Actualizado**: 2026-04-25 (v3 — 18 hallazgos, 3 deprecaciones, 3 reconecciones, 2 bugs)
**Auditoría origen**: `.opencode/context/auditoria_calidad_garantizada_20260424.md` + profundización 2026-04-25
**Decisiones**: `00-decisiones-deprecacion.md`

---

## Diagrama de Dependencias

```
┌─────────────────────────────────────────┐
│ FASE-TRAZABILIDAD-DOCS                  │
│ Correcciones documentales               │
│                                         │
│ README: 6→9 gates                       │
│ v4_complete.md: remover comando ghost   │
│ publication_gates.py: docstring 5→9     │
│ AGENTS.md: sincronizar                  │
│                                         │
│ Cubre: MENOR #5, MENOR #6               │
└──────────────┬──────────────────────────┘
               │ (independiente, sin conflictos)
               │
┌──────────────▼──────────────────────────┐
│ FASE-TRAZABILIDAD-RAIZ                  │
│ UNIFICACIÓN + CABLEADO + RECONEXIÓN     │
│                                         │
│ ★ T0: Unificar detectores (DEP-03)      │
│   _identify_brechas → detect_pains()    │
│   + nuevos pain_ids estructurales       │
│   + no_og_tags bidireccional            │
│ ★ T1.1: financial_validity source check │
│   (BUG-02: pasar sources a validator)   │
│ ★ T1-T2: Cablear 9 gates en v4complete  │
│ ★ T3-T4: Trazabilidad en diagnóstico    │
│ ★ T4.1: Unificar SEO (DEP-01)           │
│   _calculate_web_score → CHECKLIST_SEO  │
│ ★ T4.2: Unificar IAO (DEP-02)           │
│   IAO = ia_readiness.overall_score      │
│ ★ T7: Restaurar IA metrics V6 (RES-01)  │
│   + fila geo_flow_result (RES-03)       │
│ ★ T8: Fix crawler scale (BUG-01)        │
│ ★ T9: Positive findings (RES-02)        │
│ ★ T5: 16 tests                          │
│ ★ T11: Cleanup dead code                │
│                                         │
│ Cubre: CRÍTICA #1-4, NUEVA D11         │
│        MENOR #7-8, D12-D15              │
│        DEP-01/02/03, RES-01/02/03       │
│        BUG-01/02                        │
└──────────────┬──────────────────────────┘
               │ (depende de FASE-TRAZABILIDAD-RAIZ)
               │
┌──────────────▼──────────────────────────┐
│ FASE-TRAZABILIDAD-VALIDATE              │
│ ÚNICO test v4complete                   │
│ Hotel: Amazilia Hotel                   │
│                                         │
│ Verificar (18 criterios):               │
│  - 9 gates ejecutados                   │
│  - financial_validity reporta sources   │
│  - Trazabilidad brechas→servicios       │
│  - Número brechas ≈ número pains        │
│  - SEO unificado (no dual)              │
│  - IAO = ia_readiness.overall_score     │
│  - ★ Tabla IA metrics visible           │
│  - ★ Crawlers bloqueados mencionados    │
│  - ★ geo_flow_result referenciado       │
│  - ★ Sección "Lo que ya funciona"       │
│  - ★ Crawler scale bug corregido        │
│  - Gate 9 alignment PASS                │
└─────────────────────────────────────────┘
```

---

## Tabla de Conflictos Potenciales

| Fase | Archivo | Tipo | Conflicto con |
|------|---------|------|---------------|
| DOCS | README.md L306 | Modificación | Ninguno |
| DOCS | v4_complete.md L95 | Modificación | Ninguno |
| DOCS | publication_gates.py L5-13 | Modificación docstring | **RIZA toca mismo archivo L136-146 (gates dict) y L309+ (gate logic)** |
| RAIZ | v4_diagnostic_generator.py | Modificación extensa | Ninguno |
| RAIZ | pain_solution_mapper.py | Modificación (no_og_tags) | Ninguno |
| RAIZ | service_catalog.py | Verificación/Modificación | Ninguno |
| RAIZ | diagnostico_v6_template.md | Modificación (ia_metrics, positive_findings, gates) | Ninguno |
| RAIZ | publication_gates.py L309+ | Modificación lógica gate | **DOCS toca docstring L5-13 → sin overlap real** |
| RAIZ | main.py ~L2190 | Modificación | Ninguno |
| RAIZ | tests/quality_gates/ | Nuevo/Expandir | Ninguno |

**Conclusión**: Sin conflictos reales. DOCS toca docstring de publication_gates.py (L5-13), RAIZ toca lógica interna (L136+ y L309+) — sin overlap.

---

## Orden de Ejecución

1. **FASE-TRAZABILIDAD-DOCS** — Corrige la superficie documental (MENOR #5, #6)
2. **FASE-TRAZABILIDAD-RAIZ** — Ataca la raíz completa:
   - Unifica detección (DEP-03)
   - Cablea 9 gates + financial sources (BUG-02)
   - Unifica SEO (DEP-01) + IAO (DEP-02)
   - Reconecta template V6 (RES-01/02/03)
   - Corrige bug escala crawler (BUG-01)
   - Agrega hallazgos positivos
   - 16 tests
3. **FASE-TRAZABILIDAD-VALIDATE** — 1 solo test v4complete con 18 criterios de verificación

---

## Hallazgos Diferidos (Post-VALIDATE)

| # | Desconexión | Impacto | Complejidad | Razón diferimiento |
|---|-------------|---------|-------------|-------------------|
| 10 | Benchmarks sin trazabilidad en output | Baja | Media | No afecta coherencia módulo→diagnóstico |
| 17 | Competidores stub/placeholder | Baja | Alta (requiere fix en Places API) | Depende de API externa |
| 18 | Financial sources matiz | Baja | Trivial | Documentado, no requiere código |

---

## Resumen de Deprecaciones y Reconexiones

### Deprecaciones (Eliminar redundancia)
| DEP-01 | `_calculate_web_score()` custom → wrapper de `calcular_score_seo()` |
| DEP-02 | CHECKLIST_IAO standalone → `ia_readiness.overall_score` primario |
| DEP-03 | Umbrales duplicados en `_identify_brechas()` → `detect_pains()` fuente única |

### Reconexiones (Aprovechar capacidad instalada)
| RES-01 | IA metrics (`_build_geo_problems_table()`) → visible en V6 via `${ia_metrics_table}` |
| RES-02 | Hallazgos positivos → nueva sección `${positive_findings}` en V6 |
| RES-03 | geo_flow_result → fila "Salud Técnica GEO" en tabla de métricas IA |

### Bugs corregidos
| BUG-01 | Escala crawler: `> 50` → `> 0.5` (1 línea) |
| BUG-02 | financial_validity: pasar `sources` a NoDefaultsValidator |
