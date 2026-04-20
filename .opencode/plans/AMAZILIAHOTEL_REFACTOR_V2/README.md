# Plan de Refactorización Amaziliahotel E2E — v2
**Base**: Veredicto Forense E2E (`amazilia-e2e-20260420/Veredicto_Final.md`)
**Score actual**: 63.8/100
**Objetivo del plan**: Score >= 80/100
**GAPs**: 4/14 resueltos (28.6%), 5 nuevos GAPs detectados
**Flujo**: `.agents/workflows/phased_project_executor.md` v2.4.0

---

## OBJETIVO DEL PLAN (Declaración explícita)

> **Hipótesis central**: Los GAPs persistentes (G2, G4, G7, G10, G13, G14) y nuevos (NG1-NG5) son consecuencia de **dos problemas sistémicos** en el pipeline v4complete:
>
> 1. **Desacoplamiento entre catálogo y generador**: `v4_proposal_generator.py` tiene lógica propia (ROI, servicios, capitalización) que ignora `asset_catalog.py` y los datos de `geo_enriched/`.
> 2. **Query malformado para Google Maps**: La búsqueda de Places usa el dominio (`amaziliahotel`) como nombre de búsqueda → Google Maps no lo asocia como lugar físico → `geo_score=0` (NO es API key inválida).
>
> **Éxito del plan**: Si después de FASE-1 a FASE-8 ejecutamos `v4complete --url https://amaziliahotel.com/` y el veredicto forense muestra **score >= 80**, el plan habrá funcionado. Si el score se mantiene en ~63.8, la hipótesis es incorrecta y hay que re-diagnosticar.

---

## Contexto Ejecutivo

La ejecución v4complete sobre `amaziliahotel.com` reveló que los fixes aplicados al codebase NO se reflejan en el output porque:

1. **Pipeline/Data Flow**: El generador de propuesta (`v4_proposal_generator.py`) tiene lógica propia de ROI que ignora el catálogo centralizado.
2. **Google Maps Query Bug**: Se busca `"amaziliahotel"` (extraído del dominio) como nombre de hotel → Google Maps no lo encuentra → 0 resultados → `geo_score=0`.
3. **Content Scrubber es código muerto**: `ContentScrubber` existe pero NUNCA es importado ni invocado en el pipeline. No aplica a diagnóstico NI propuesta.
4. **faq_page handler**: Sigue generando `.csv` en lugar de JSON-LD.
5. **Template V6 hardcodeado**: Tiene "(24X en 6 meses)" fijo en el texto, sin importar el ROI calculado dinámicamente.

---

## GAPs a Resolver

### CRÍTICOS (bloquean entrega)

| Código | Descripción | Archivo(s) Real(es) | Severidad |
|--------|-------------|----------------------|-----------|
| NG4 | Google Maps query usa nombre derivado del dominio en vez de nombre+ubicación | `modules/auditors/v4_comprehensive.py` `_build_search_queries()` | 🔴 ALTO |
| G2 | hotel_schema con TODOS campos vacíos (tel, addr, geo) | `modules/asset_generation/conditional_generator.py` `_generate_hotel_schema()` | 🔴 ALTO |
| G7 | monthly_report tiene 27 "_____" blanks | Template en `modules/asset_generation/` | 🔴 ALTO |
| G10 | ROI "(24X en 6 meses)" hardcodeado en template V6 — ignora cálculo dinámico | `modules/commercial_documents/templates/propuesta_v6_template.md` + `v4_proposal_generator.py` | 🔴 ALTO |
| NG1 | Publication NOT_READY — COP COP en propuesta | `modules/postprocessors/content_scrubber.py` (código muerto) | 🔴 ALTO |
| NG5 | Content Scrubber NUNCA se ejecuta — es código muerto (0 imports) | `modules/postprocessors/content_scrubber.py`, `modules/orchestration_v4/v4_complete_orchestrator.py` | 🔴 ALTO |
| G4 | faq_page genera `.csv` en vez de JSON-LD | `modules/asset_generation/conditional_generator.py` handler faq_page | 🔴 ALTO |

### ALTOS (plan de seguimiento)

| Código | Descripción | Archivo(s) Real(es) | Severidad |
|--------|-------------|----------------------|-----------|
| G3 | Open Graph existe pero ESTIMATED, no verificado | `modules/asset_generation/` | 🟡 MEDIO |
| G9 | Voice/AEO eliminado del catálogo (DEPRECATED) pero sigue en propuesta | `modules/commercial_documents/templates/propuesta_v6_template.md`, `modules/asset_generation/proposal_asset_alignment.py` | 🟡 MEDIO |
| G13 | "eje_cafetero" lowercase → proposal generator NO sanitiza a Title Case | `modules/commercial_documents/v4_proposal_generator.py` (recibe region lowercase de `_infer_region_from_address()`) | 🟡 MEDIO |
| G14 | "COP COP" duplicado 5 veces en propuesta | Se resuelve activando scrubber (FASE-3) | 🟡 MEDIO |
| NG2 | 10 assets con "Insufficient confidence" | `modules/asset_generation/conditional_generator.py` | 🟡 MEDIO |
| NG3 | LLMs OpenRouter/Gemini fallaron (504/404) | Configuración de API keys | 🟡 MEDIO |

### NO ACCIONABLES (verificación forense descarta)

| Código | Descripción | Por qué no |
|--------|-------------|------------|
| G8 | WhatsApp en propuesta | WhatsApp SIGUE IMPLEMENTADO en asset_catalog — NO debe eliminarse |

---

## Arquitectura del Plan

```
FASE-1 ──── Fix Google Maps query en v4_comprehensive.py
FASE-2 ──── Fix hotel_schema (datos reales del audit)
FASE-3 ──── Activar Content Scrubber en pipeline (código muerto → integrar)
FASE-4 ──── Fix ROI — eliminar "24X" hardcodeado de template V6
FASE-5 ──── Fix faq_page → JSON-LD + monthly_report blanks
FASE-6 ──── Fix Voice/AEO deprecated en propuesta (NO tocar WhatsApp)
FASE-7 ──── Fix capitalización region → .title() en proposal generator
FASE-8 ──── Validación E2E con Amaziliahotel + documentación
```

**Dependencias revisadas (post-forense)**:
- FASE-1 es independiente.
- FASE-2 requiere FASE-1 (geo_score necesita datos del Places API).
- FASE-3 es independiente (el scrubber es código muerto, hay que activarlo desde cero).
- FASE-4 es independiente (template V6 + cálculo dinámico).
- FASE-5 es independiente (faq_page es un handler separado).
- FASE-6 es independiente (Voice en template/alineación).
- FASE-7 es independiente (region string sanitization).
- FASE-8 requiere TODAS las anteriores.

**NOTA**: La cadena de dependencias original era artificial. Solo FASE-2→FASE-1 y FASE-8→TODAS son dependencias reales. Las fases 3-7 son PARALELIZABLES entre sí.
