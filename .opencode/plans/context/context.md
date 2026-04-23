# CONTEXTO: PLAN PARA BUSCAR SOLUCIÓN DE RAÍZ AL DESALINEAMIENTO DIAGNÓSTICO-PROPUESTA

> **Última actualización**: 2026-04-22  
> **Estado**: PREPARACIÓN COMPLETA (fases generadas)

---

## RESUMEN EJECUTIVO DEL PROBLEMA

El diagnóstico identifica explícitamente **4 brechas críticas** que afectan la presencia digital y reservas directas:

| Brecha | Descripción | Costo Mensual |
|--------|-------------|---------------|
| **[BRECHA 1]** | Sin Schema de Hotel → Invisible para IA (ChatGPT, Gemini, Perplexity) | $1.186.245 COP |
| **[BRECHA 2]** | Sin FAQ para Rich Snippets → Google no muestra preguntas frecuentes | $569.502 COP |
| **[BRECHA 3]** | Metadatos por Defecto del CMS → Título y descripción genéricos | $474.498 COP |
| **[BRECHA 4]** | Sin Meta Tags Sociales (Open Graph) → Comparticiones en WhatsApp/Facebook poco atractivas | $379.755 COP |

**Total perdido: $2.610.000 COP/mes**

La propuesta comercial actual ofrece **5 servicios** (hardcoded en plantilla):
1. Google Maps Optimizado (GEO)
2. SEO Local (SEO)
3. Botón de WhatsApp
4. Datos Estructurados
5. Informe Mensual

**Faltan**: FAQ y Open Graph.

---

## ANÁLISIS DE ALINEACIÓN (DIAGNÓSTICO → PROPUESTA)

| Brecha | ¿Cubierta? | Evidencia |
|--------|-------------|-----------|
| [BRECHA 1] Schema Hotel | ✅ Sí | "Datos Estructurados" cubre schema Hotel |
| [BRECHA 2] FAQ Rich Snippets | ❌ **NO** | Ningún servicio menciona FAQ |
| [BRECHA 3] Metadatos CMS | ⚠️ Parcial | "SEO Local" podría incluir, no especificado |
| [BRECHA 4] Open Graph | ❌ **NO** | Sin mención a Open Graph |

---

## CAUSA RAÍZ IDENTIFICADA

### Evidencia del código

**1. Plantilla estática**: `modules/commercial_documents/templates/propuesta_v6_template.md` líneas 46-50 hardcodea los 5 servicios:

```
| **✅ Google Maps Optimizado** (GEO) | ...
| **✅ SEO Local** (SEO) | ...
| **✅ Botón de WhatsApp** | ...
| **✅ Datos Estructurados** | ...
| **✅ Informe Mensual** | ...
```

**2. Mapeo pains→assets YA EXISTE** en `modules/commercial_documents/pain_solution_mapper.py`:
- Línea 71-79: `no_faq_schema` → `faq_page` ✅
- Línea 237-245: `no_og_tags` → `open_graph` ✅

**3. Generadores YA EXISTEN**:
- `open_graph_generator.py` (FASE-4, 341 líneas) ✅
- `local_content_generator.py` incluye generación de FAQ pages ✅

**4. Mapeo propuesta→asset INCOMPLETO** en `modules/asset_generation/proposal_asset_alignment.py` líneas 20-26:
```python
PROPOSAL_SERVICE_TO_ASSET = {
    "Google Maps Optimizado": "geo_playbook",
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Datos Estructurados": "hotel_schema",
    "Informe Mensual": "monthly_report",
}  # FALTA: FAQ y Open Graph
```

**5. Orchestrator SÍ genera los assets correctos** pero la propuesta NO los lista.

---

## FLUJO ACTUAL vs FLUJO CORRECTO

```
ACTUAL (roto):
  Diagnóstico (4 brechas) ────────────────────────────────────────────────
        │                                                                   │
        ▼                                                                   │
  pain_solution_mapper.detect_pains()                                       │
        │                                                                   │
        ├── no_hotel_schema ──→ hotel_schema ✅ (generado)                   │
        ├── no_faq_schema ─────→ faq_page ✅ (generado)                     │
        ├── metadata_defaults ─→ optimization_guide ✅ (generado)            │
        └── no_og_tags ────────→ open_graph ✅ (generado)                    │
                                      │                                      │
                                      ▼                                      │
  Propuesta Comercial (5 servicios hardcoded) ← PROBLEMA AQUÍ               │
        │                                                                   │
        └── Lista: GEO, SEO, WhatsApp, Datos Estructurados, Informe        │
                                                                             │
CORRECTO:                                                                    │
  La propuesta debería listar 7 servicios incluyendo FAQ y Open Graph        │
```

---

## ARCHIVOS CRÍTICOS

| Rol | Archivo | Estado |
|-----|---------|--------|
| Plantilla propuesta | `modules/commercial_documents/templates/propuesta_v6_template.md` | **Hardcoded** |
| Mapeo pains→assets | `modules/commercial_documents/pain_solution_mapper.py` | ✅ Completo |
| Mapeo propuesta→asset | `modules/asset_generation/proposal_asset_alignment.py` | ❌ Incompleto |
| Generador OG | `modules/asset_generation/open_graph_generator.py` | ✅ Existe |
| Orchestrator | `modules/asset_generation/v4_asset_orchestrator.py` | ✅ Genera bien |
| Diagnóstico real | `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260421_173618.md` | 4 brechas |
| Propuesta real | `output/v4_complete/02_PROPUESTA_COMERCIAL_20260421_173621.md` | 5 servicios |

---

## PLAN DE FASES

| Fase | Objetivo | Dependencias |
|------|----------|--------------|
| **FASE-CAUSAL-DIAG** | Diagnosticar exactamente dónde se rompe el flujo | Ninguna |
| **FASE-CAUSAL-FIX** | Corregir proposal_asset_alignment.py + template | FASE-CAUSAL-DIAG |
| **FASE-CAUSAL-TEST** | Verificar con Amaziliahotel y tests | FASE-CAUSAL-FIX |
| **FASE-RELEASE-4.34.0** | Release con documentación completa | FASE-CAUSAL-TEST |

---

## REFERENCIAS

- Workflow: `.agents/workflows/phased_project_executor.md` v2.4.0
- Skills relacionadas: `iah-cli-plan-vs-reality-check`, `iah-cli-post-implementation-e2e-verification`
- Template fase: `.agents/workflows/templates/prompt-fase-template.md`

---

## ARCHIVOS DEL PLAN

```
.opencode/plans/
├── context/
│   └── context.md                    ← Este archivo (actualizado)
├── dependencias-fases.md             ← Dependencias entre fases
├── 05-prompt-inicio-sesion-fase-{N}.md  ← Prompts por fase
├── 06-checklist-implementacion.md    ← Checklist maestro
└── 09-documentacion-post-proyecto.md ← Estructura documentación
```
