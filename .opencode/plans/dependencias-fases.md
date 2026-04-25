# Dependencias y Conflictos entre Fases

**Proyecto**: Corrección Trazabilidad "Calidad Garantizada" + Reconección Módulos→Diagnóstico
**Fecha preparación**: 2026-04-24
**Actualizado**: 2026-04-25 (v4 — incluye FASE-06 PATCH y FASE-07 SEO-SCORE)
**Auditoría origen**: `.opencode/context/auditoria_calidad_garantizada_20260424.md` + profundización 2026-04-25
**Decisiones**: `00-decisiones-deprecacion.md`
**Baseline evaluación**: `.opencode/context/fase-trazabilidad-patch-eval.md`

---

## Diagrama de Dependencias

```
┌─────────────────────────────────────────┐
│ FASE-TRAZABILIDAD-DOCS                  │
│ Correcciones documentales               │
│                                         │
│ README: 6→9 gates                       │
│ v4_complete.md: remover comando ghost    │
│ publication_gates.py: docstring 5→9     │
│ AGENTS.md: sincronizar                  │
│                                         │
│ Cubre: MENOR #5, MENOR #6              │
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
│   (BUG-02) — NO implementado, transferido│
│   → scope absorbido por PATCH-06 T1     │
│ ★ T1-T2: Cablear 9 gates en v4complete  │
│ ★ T3-T4: Trazabilidad en diagnóstico   │
│ ★ T4.1: Unificar SEO (DEP-01)           │
│   _calculate_web_score → CHECKLIST_SEO  │
│ ★ T4.2: Unificar IAO (DEP-02)           │
│   IAO = ia_readiness.overall_score      │
│ ★ T7: Restaurar IA metrics V6 (RES-01) │
│   + fila geo_flow_result (RES-03)       │
│ ★ T8: Fix crawler scale (BUG-01)        │
│ ★ T9: Positive findings (RES-02)        │
│ ★ T5: 16 tests                          │
│ ★ T11: Cleanup dead code               │
│                                         │
│ Cubre: CRÍTICA #1-4, NUEVA D11         │
│        MENOR #7-8, D12-D15              │
│        DEP-01/02/03, RES-01/02/03       │
│        BUG-01/02                        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│ FASE-TRAZABILIDAD-VALIDATE              │
│ Hotel: Amazilia Hotel                   │
│ ÚNICO test v4complete                  │
│ 18 criterios de verificación           │
│ 18 gates ejecutados + baseline doc.    │
└──────────────┬──────────────────────────┘
               │ (baseline en fase-trazabilidad-patch-eval.md)
               │ (4 issues abiertos identificados)
               │
┌──────────────▼──────────────────────────┐
│ FASE-TRAZABILIDAD-PATCH+SEO (06)        │
│ Corrección unificada: 5 issues          │
│ 1 sola ejecución v4complete al final    │
│                                         │
│ T1-BUG02: financial_validity WARNING    │
│   → implementación COMPLETA del path   │
│   → WARNING + financial_sources        │
│ T2-Secciones: encabezados faltantes    │
│   → "## 🔍 Trazabilidad de Brechas"    │
│   → "## ✅ Validación de Calidad"      │
│ T3-seo_score: ausente del JSON (D2)    │
│   → absorbido de FASE-07               │
│   → agregar seo_score a report dict    │
│ T4-geo_flow: timing (ya genera datos)  │
│ D1-WARNING: check_publication_readiness │
│   → diferido a sesión dedicada         │
│                                         │
│ Verificado con baseline en:            │
│ fase-trazabilidad-patch-eval.md         │
└─────────────────────────────────────────┘

NOTA: FASE-07 SEO-SCORE fue absorbida como T3 de esta fase.
Antes: 2 ejecuciones v4complete (PATCH + SEO separados).
Después: 1 sola ejecución v4complete (PATCH+SEO unificado).
```

---

## Tabla de Conflictos Potenciales

| Fase | Archivo | Tipo | Conflicto con |
|------|---------|------|---------------|
| DOCS | README.md L306 | Modificación | Ninguno |
| DOCS | v4_complete.md L95 | Modificación | Ninguno |
| DOCS | publication_gates.py L5-13 | Modificación docstring | **RAIZ toca mismo archivo L136-146 (gates dict) y L309+ (gate logic)** |
| RAIZ | v4_diagnostic_generator.py | Modificación extensa | Ninguno |
| RAIZ | pain_solution_mapper.py | Modificación (no_og_tags) | Ninguno |
| RAIZ | service_catalog.py | Verificación/Modificación | Ninguno |
| RAIZ | diagnostico_v6_template.md | Modificación (ia_metrics, positive_findings, gates) | Ninguno |
| RAIZ | publication_gates.py L309+ | Modificación lógica gate | **DOCS toca docstring L5-13 → sin overlap real** |
| RAIZ | main.py ~L2190 | Modificación | Ninguno |
| RAIZ | tests/quality_gates/ | Nuevo/Expandir | Ninguno |
| PATCH-06 | publication_gates.py | T1: implementar path WARNING + financial_sources | Ninguno (mismo archivo, distinto scope que RAIZ) |
| PATCH-06 | v4_diagnostic_generator.py | T2: agregar encabezados sección | Ninguno |
| PATCH-06 | diagnostico_v6_template.md | T2: agregar sección Validación de Calidad | Ninguno |
| PATCH-06 | main.py | T3: agregar seo_score al report JSON | Ninguno |

**Conclusión**: Sin conflictos reales. DOCS toca docstring de publication_gates.py (L5-13), RAIZ toca lógica interna (L136+ y L309+), PATCH-06 opera en scopes separados incluyendo el absorbido de FASE-07.

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
   - Baseline documentado en `fase-trazabilidad-patch-eval.md`
4. **FASE-TRAZABILIDAD-PATCH+SEO (06)** — 5 issues unificados, 1 sola ejecución v4complete
   - T1/T2/T4 de VALIDATE + T3 (D2 seo_score absorbido de FASE-07)

---

## Hallazgos Diferidos (Post-VALIDATE/PATCH)

| # | Desconexión | Impacto | Complejidad | Razón diferimiento |
|---|-------------|---------|-------------|-------------------|
| 10 | Benchmarks sin trazabilidad en output | Baja | Media | No afecta coherencia módulo→diagnóstico |
| 17 | Competidores stub/placeholder | Baja | Alta (requiere fix en Places API) | Depende de API externa |
| 18 | Financial sources matiz | Baja | Trivial | Documentado, no requiere código |
| D1 | WARNING en readiness (check_publication_readiness) | Media | Media | Sesión dedicada requerida — decisión negocio |

---

## Resumen de Deprecaciones y Reconexiones

### Deprecaciones (Eliminar redundancia)
| ID | Descripción |
|----|-------------|
| DEP-01 | `_calculate_web_score()` custom → wrapper de `calcular_score_seo()` |
| DEP-02 | CHECKLIST_IAO standalone → `ia_readiness.overall_score` primario |
| DEP-03 | Umbrales duplicados en `_identify_brechas()` → `detect_pains()` fuente única |

### Reconexiones (Aprovechar capacidad instalada)
| ID | Descripción |
|----|-------------|
| RES-01 | IA metrics (`_build_geo_problems_table()`) → visible en V6 via `${ia_metrics_table}` |
| RES-02 | Hallazgos positivos → nueva sección `${positive_findings}` en V6 |
| RES-03 | geo_flow_result → fila "Salud Técnica GEO" en tabla de métricas IA |

### Bugs corregidos
| ID | Descripción | Archivo | Línea |
|----|-------------|----------|-------|
| BUG-01 | Escala crawler: `> 50` → `> 0.5` (1 línea) | v4_diagnostic_generator.py | ~L1251 |
| BUG-02 | financial_validity: pasar `sources` a NoDefaultsValidator | publication_gates.py | L318-389 |

---

## Issues Post-Validate (FASE-06 PATCH)

| Issue | Descripción | Estado | Fix |
|-------|-------------|--------|-----|
| T1-BUG02 | financial_validity FALSE POSITIVE | PENDIENTE | Implementación COMPLETA del path WARNING + financial_sources |
| T2-Secciones | Encabezados faltantes en diagnóstico | PENDIENTE | "## 🔍 Trazabilidad de Brechas" + "## ✅ Validación de Calidad" |
| T3-seo_score | seo_score ausente del JSON (D2) | PENDIENTE | Agregar seo_score al report dict en main.py (absorbido de FASE-07) |
| T4-geo_flow | Timing geo_flow_result.json | PENDIENTE | Ya genera datos — verificar timing post-assets |
| D1-WARNING | check_publication_readiness ignora WARNING | DIFERIDO | Sesión dedicada |

---

## Criterios de Verificación por Fase (del baseline)

### FASE-TRAZABILIDAD-PATCH+SEO (06)

| Criterio | Esperado | Fuente |
|----------|----------|--------|
| financial_validity status | WARNING | gate_report.json |
| Gate message | Contiene "Tier C" o "default" | gate_report.json |
| Gate details.default_sources | Presente con campos affected | gate_report.json |
| Encabezado brechas | "## 🔍 Trazabilidad: Brechas Identificadas" | diagnóstico .md |
| Encabezado calidad | "## ✅ Validación de Calidad" | diagnóstico .md |
| seo_score en JSON | Presente, numérico 0-100 | v4_complete_report.json |
| geo_flow_result.json existe | SÍ | output/v4_complete/amazilia_hotel/v4_audit/ |
| Ejecuciones v4complete | 1 sola para verificar todo | — |
