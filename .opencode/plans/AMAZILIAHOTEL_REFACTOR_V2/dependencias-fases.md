# Dependencias de Fases — Amaziliahotel Refactor v2
**Corregido post-forense: dependencias reales vs artificiales**

## Diagrama de Dependencias

```
FASE-1 ──────────────────────────┐
  [Google Maps query v4_comprehensive] │
                                  ▼
FASE-2 ──────────────────────────►│
  [hotel_schema datos reales]      │
                                    │
FASE-3 ──────────────────────────►│
  [Content Scrubber dead code→activar] │
                                    │
FASE-4 ──────────────────────────►│
  [ROI template 24X→dinámico]     │
                                    │
FASE-5 ──────────────────────────►│
  [faq_page JSON-LD + blanks]     │
                                    │
FASE-6 ──────────────────────────►│
  [Voice/AEO deprecated]          │
                                    │
FASE-7 ──────────────────────────►│
  [Region .title() sanitization]  │
                                  ▼
FASE-8 ◄─────────────────────────┘
  [E2E validation + docs]
```

## Matriz de Conflictos de Archivos

| Fase | Archivos Modificados (REAL) | Riesgo Conflicto |
|------|----------------------------|------------------|
| FASE-1 | `modules/auditors/v4_comprehensive.py` | Bajo |
| FASE-2 | `modules/asset_generation/conditional_generator.py` | Medio |
| FASE-3 | `modules/postprocessors/content_scrubber.py`, `modules/orchestration_v4/v4_complete_orchestrator.py` | Medio |
| FASE-4 | `modules/commercial_documents/templates/propuesta_v6_template.md`, `modules/commercial_documents/v4_proposal_generator.py` | Alto |
| FASE-5 | `modules/asset_generation/conditional_generator.py`, template `monthly_report` | Medio |
| FASE-6 | `modules/commercial_documents/templates/propuesta_v6_template.md`, `modules/asset_generation/proposal_asset_alignment.py` | Alto |
| FASE-7 | `modules/commercial_documents/v4_proposal_generator.py` | Medio |
| FASE-8 | Scripts de validación, REGISTRY.md, CHANGELOG.md | N/A (documentación) |

## Conflictos Potenciales entre Fases

| Par | Archivo compartido | Acción |
|-----|-------------------|--------|
| FASE-2 + FASE-5 | `conditional_generator.py` | Distintos métodos (_generate_hotel_schema vs _generate_faq_page). Sin conflicto. |
| FASE-4 + FASE-6 + FASE-7 | `v4_proposal_generator.py` + template V6 | Mismo archivo, mismos modificadores. Secuenciar o merge cuidadoso. |

## Dependencias Reales

| Fase | Depende de | Por qué |
|------|-----------|---------|
| FASE-1 | - | Independiente |
| FASE-2 | FASE-1 | hotel_schema necesita datos del Places API (geo_score, coords) |
| FASE-3 | - | Scrubber es dead code, se activa independientemente |
| FASE-4 | - | Template + cálculo dinámico, no depende de otros fixes |
| FASE-5 | - | Handler de faq_page es autónomo |
| FASE-6 | - | Template/alineación de Voice es independiente |
| FASE-7 | - | Sanitización de region es independiente |
| FASE-8 | FASE-1 a FASE-7 | Validación final requiere todos los fixes aplicados |

**Paralelizables**: FASE-3, FASE-4, FASE-5, FASE-6, FASE-7 pueden ejecutarse en paralelo si se coordina el merge en `v4_proposal_generator.py` y template V6.

**Ruta crítica**: FASE-1 → FASE-2 → FASE-8 (3 fases obligatoriamente secuenciales)
