# Dependencias de Fases — Fix geo_enriched → Delivery Bridge + Assets Completos

**Proyecto:** AUDIT-PIPELINE-DESALINEACIONES-ASSETS
**Fecha:** 2026-04-12
**Estado:** Planificación completada (v2 — ampliado con D4/R9)

---

## Diagnóstico del Problema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE ACTUAL (ROTO) — DOS RUPTURAS                    │
│                                                                             │
│  RUPTURA 1: geo_enriched → delivery (D2, D3, D8)                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────────────────┐   │
│  │  Hook    │───▶│ Validation │───▶│ Scenarios │───▶│ 4. Publication     │   │
│  └──────────┘    └──────────┘    └──────────┘    └─────────────────────┘   │
│                                                           │                 │
│                                                           ▼                 │
│                                               ┌─────────────────────┐       │
│                                               │ 5. V4AssetOrchestrator│     │
│                                               │ (genera 10 assets)    │     │
│                                               └─────────────────────┘       │
│                                                           │                 │
│                                                           ▼                 │
│                                               ┌─────────────────────┐       │
│                                               │ DELIVERY PACKAGE    │     │
│                                               │ ❌ NO incluye        │       │
│                                               │ geo_enriched/       │       │
│                                               │ ❌ confidence 0.5    │       │
│                                               └─────────────────────┘       │
│                                                                             │
│  RUPTURA 2: propuesta → assets (D4) — RESUELTA ✅                               │
│  ┌─────────────────────────┐    ┌──────────────────────────────────┐       │
│  │ PROPUESTA (7 servicios) │    │ ASSETS GENERADOS (7/7)           │       │
│  │ ✅ Google Maps           │───▶│ geo_playbook ✅                   │       │
│  │ ✅ ChatGPT               │───▶│ indirect_traffic_opt. ✅          │       │
│  │ ✅ Busqueda por Voz      │───▶│ voice_assistant_guide ✅          │       │
│  │ ✅ SEO Local             │───▶│ optimization_guide ✅             │       │
│  │ ✅ Boton WhatsApp        │───▶│ whatsapp_button ✅                │       │
│  │ ✅ Datos Estructurados   │───▶│ hotel_schema ✅                   │       │
│  │ ✅ Informe Mensual       │───▶│ monthly_report ✅ (NEW)           │       │
│  └─────────────────────────┘    └──────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Fases del Proyecto

| Fase | ID | Nombre | Dependencias | Prioridad |
|------|----|--------|---------------|-----------|
| 1 | FASE-GEO-BRIDGE | geo_enriched → asset enrichment bridge | Ninguna (root fix) | ALTA | ✅ 2026-04-13 |
| 2 | FASE-CONF-GATE | Asset confidence gate en publication | FASE-GEO-BRIDGE | ALTA | ✅ 2026-04-13 |
| 3 | FASE-LLMSTXT-FIX | Fix llms.txt generator + fallback | FASE-GEO-BRIDGE | ALTA |
|| 4 | FASE-ASSETS-VALIDACION | Propuesta → Assets: 7/7 servicios | FASE-GEO-BRIDGE | ALTA | ✅ 2026-04-13 |
| 5 | FASE-CONFIDENCE-DISCLOSURE | Transparencia calidad en propuesta | FASE-ASSETS-VALIDACION | MEDIA |
| 6 | FASE-TEMPLATE-DEBT | Sincronizar embebido vs V6 + typo | Ninguna | MEDIA | ✅ 2026-04-13 |
| 7 | FASE-CONTENT-SCRUBBER | Fix self-replacement + spacing | Ninguna | MEDIA | ✅ 2026-04-13 |
| 8 | FASE-RELEASE | v4.29.0 release + docs + validación | Fases 1-7 | ALTA |

---

## Diagrama de Dependencias

```
                         ┌──────────────────────────┐
                         │     FASE-GEO-BRIDGE      │  (root cause fix)
                         │  geo_enriched → assets   │
                         └────────────┬─────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                  │
                    ▼                 ▼                  ▼
          ┌─────────────────┐ ┌──────────────┐  ┌──────────────────┐
          │  FASE-CONF-GATE │ │ FASE-LLMS-   │  │ FASE-ASSETS-     │
          │ confidence >=0.7│ │ TXT-FIX      │  │ VALIDACION       │
          │ gate #8         │ │ fallback a   │  │ 7/7 servicios    │
          └────────┬────────┘ │ geo_enriched │  │ con asset        │
                   │          └──────┬───────┘  └────────┬─────────┘
                   │                 │                    │
                   │                 │                    ▼
                   │                 │          ┌──────────────────┐
                   │                 │          │ FASE-CONFIDENCE- │
                   │                 │          │ DISCLOSURE       │
                   │                 │          │ tabla calidad en │
                   │                 │          │ propuesta        │
                   │                 │          └────────┬─────────┘
                   │                 │                   │
                   └─────────────────┼───────────────────┘
                                     │
                                     ▼
                           ┌─────────────────────┐
                           │   FASE-RELEASE      │
                           │   v4.29.0 + docs    │
                           │   VALIDACIÓN FINAL  │
                           └─────────────────────┘

          ┌─────────────────────────────────┐
          │       FASE-TEMPLATE-DEBT         │  (paralelo, independiente)
          │   sincronizar embebido + V6      │
          └─────────────────────────────────┘

          ┌─────────────────────────────────┐
          │     FASE-CONTENT-SCRUBBER        │  (paralelo, independiente)
          │   self-replacement + spacing    │
          └─────────────────────────────────┘
```

---

## Conflictos Potenciales de Archivos

| Archivo | Fases que lo modifican | Riesgo |
|---------|----------------------|--------|
| `modules/asset_generation/conditional_generator.py` | GEO-BRIDGE, LLMSTXT-FIX, ASSETS-VALID | ALTO — 3 fases |
| `modules/asset_generation/asset_catalog.py` | ASSETS-VALID | BAJO |
| `modules/quality_gates/publication_gates.py` | CONF-GATE, ASSETS-VALID | MEDIO — 2 fases |
| `modules/commercial_documents/propuesta_v6_template.md` | CONFIDENCE-DISC, TEMPLATE-DEBT | MEDIO — 2 fases |
| `modules/commercial_documents/v4_proposal_generator.py` | CONFIDENCE-DISC | BAJO |
| `modules/geo_enrichment/geo_enrichment_layer.py` | GEO-BRIDGE (solo lectura) | BAJO |
| `modules/asset_generation/llmstxt_generator.py` | LLMSTXT-FIX | BAJO |

**RECOMENDACIÓN**: Ejecutar FASE-GEO-BRIDGE primero, luego ASSETS-VALIDACION antes de LLMSTXT-FIX y CONF-GATE para reducir conflictos en conditional_generator.py.

---

## Restricciones del Proyecto

1. **No romper la cadena financiera** — cualquier cambio NO debe alterar los cálculos financieros ya validados
2. **No tocar el template V6 de diagnóstico** — los 4 pilares están correctos
3. **Mantener backward compat** — si se elimina template embebido, asegurar que V6 siempre exista
4. **Testing** — 385+ tests deben seguir pasando después de cambios
5. **Trazabilidad** — cada fase requiere log_phase_completion.py + REGISTRY.md
6. **Costo API** — NO ejecutar v4complete innecesariamente para testing
7. **Una fase por sesión** — no implementar todas las correcciones de una vez

---

## Criterio de Éxito Global

Después de FASE-RELEASE, al ejecutar `v4complete --url https://amaziliahotel.com/`:

### Presencia — Que no falte nada
1. `assets_generated` contiene TODOS los tipos: hotel_schema, geo_playbook, optimization_guide, llms_txt, indirect_traffic_optimization, voice_assistant_guide, whatsapp_button, monthly_report, faq_page, review_plan, review_widget, org_schema, analytics_setup_guide
2. Cada servicio ✅ de la propuesta tiene un asset en disco

### Efectividad — Que materialice soluciones
3. `hotel_schema` contiene `name: "Amaziliahotel"` (no "Hotel")
4. `llms_txt` contiene URL real `https://amaziliahotel.com/` y servicios reales
5. `voice_assistant_guide` tiene checklist Google Assistant + Apple + Alexa
6. `whatsapp_button` tiene número de teléfono o disclaimer claro de pendiente
7. `monthly_report` tiene plantilla con KPIs definidos

### Calidad — Que sea usable
8. Todos los assets tienen `confidence_score >= 0.7`
9. Propuesta incluye tabla de calidad de assets (nivel de cada entregable)
10. Publication gates = 9 gates (incluye asset_confidence + proposal_alignment)

### Integridad
11. Los 385+ tests siguen pasando
12. Cadena financiera intacta (mismos valores en diagnóstico, propuesta, financial_scenarios.json)
