# Contexto: D4 Fix + OpenRouter IAO Cost Tracking

**Fecha:** 2026-04-13
**Origen:** Post-FASE-RELEASE v4.29.0 E2E + análisis de log OpenRouter
**Estado:** Listo para planificación

---

## 1. HALLAZGO D4 — 3 Assets promised_by["always"] No Se Generan

### Evidencia (v4complete E2E 2026-04-13)

Gate 9 (`proposal_asset_alignment`) reporta:
```
aligned_count: 3  (solo hotel_schema con confidence 0.85)
missing_count: 3
low_quality_count: 3
missing: voice_assistant_guide, whatsapp_button, monthly_report
```

### Root Cause Confirmada

**Archivo:** `modules/asset_generation/v4_asset_orchestrator.py` línea 221:
```python
pains = self.pain_mapper.detect_pains(audit_result, validation_summary, analytics_data)
solutions = self.pain_mapper.map_to_solutions(pains)
asset_specs = self._solutions_to_asset_specs(solutions, pains)
```

El pipeline es **pain-driven**: solo genera assets si el `PainSolutionMapper` detecta un pain que los mapea. Los assets con `promised_by=["always"]` en `asset_catalog.py` se definieron correctamente pero NUNCA se agregan al plan porque no hay pain que los dispare.

### Assets Afectados

| Asset | Catalog Entry | promised_by | Handler existe? |
|-------|-------------|-------------|----------------|
| `voice_assistant_guide` | AssetCatalogEntry (línea 210) | ["always_aeo"] | ✅ `_generate_voice_assistant_guide()` |
| `whatsapp_button` | AssetCatalogEntry (línea 54) | ["always"] | ✅ `_generate_whatsapp_button()` |
| `monthly_report` | AssetCatalogEntry (línea 313) | ["always"] | ✅ `MonthlyReportGenerator` |

### Archivo: `modules/asset_generation/proposal_asset_alignment.py`
El mapeo `PROPOSAL_SERVICE_TO_ASSET` (líneas ~50-60) mapea correctamente los 7 servicios:
- Google Maps Optimizado → geo_playbook ✅
- Visibilidad en ChatGPT → indirect_traffic_optimization ✅
- Busqueda por Voz → voice_assistant_guide ❌
- SEO Local → optimization_guide ✅
- Boton de WhatsApp → whatsapp_button ❌
- Datos Estructurados → hotel_schema ✅
- Informe Mensual → monthly_report ❌

**El mapeo está bien. El problema es que el orchestrator no genera los 3 que faltan.**

---

## 2. HALLAZGO OPENROUTER — Cost Tracking en IAO

### Evidencia (OpenRouter Dashboard Log — 2026-04-13 22:02)

```json
{
  "model": "google/gemini-2.0-flash-001",
  "app": { "title": "IAH-CLI IAO Checker" },
  "generation_time": 8860,
  "latency": 1028,
  "tokens_prompt": 15,
  "tokens_completion": 1033,
  "usage": 0.0004107,
  "provider_name": "Google AI Studio",
  "finish_reason": "length"
}
```

### Dónde se consume OpenRouter

**Archivo:** `modules/auditors/llm_mention_checker.py`

- `_query_openrouter()` (línea 200-227): POST a `https://openrouter.ai/api/v1/chat/completions`
- Modelo: `google/gemini-2.0-flash-001` (línea 214)
- Costo: ~$0.00041 USD por query (tokens: 15 prompt + 1033 completion)
- Llamado desde: `LLMMentionChecker.check_mentions()` → `V4ComprehensiveAuditor` (línea 532-549)

### Pipeline de IAO en v4complete

```
FASE 2 (Audit):
  → V4ComprehensiveAuditor.audit()
    → Step 2.11: LLMMentionChecker.check_mentions()  [OPENROUTER aquí]
    → iao_snippet_tracker (SerpAPI si disponible)
    → ia_readiness_calculator (score compuesto)
```

### Costos Observados

| Query | Tokens (prompt+completion) | Costo Estimado USD |
|-------|---------------------------|-------------------|
| 1 query OpenRouter | 1048 | ~$0.00041 |
| IAO completo (3-5 queries) | ~5000 | ~$0.002 |

**Costo por ejecución v4complete: ~$0.002 USD** (aproximado, modelo google/gemini-2.0-flash-001)

### Problema: Sin Tracking en el Report

El JSON de facturacion NO se persiste en `v4_complete_report.json`. El costo real de IAO solo es visible en el dashboard de OpenRouter, no en los documentos de entrega al cliente.

---

## 3. RELACION ENTRE D4 y IAO

La propuesta promete 3 servicios que dependen de datos enriquecidos:
- `voice_assistant_guide` → necesita datos de GBP (horarios, teléfono) para readiness score real
- `whatsapp_button` → necesita `phone_web` del audit
- `monthly_report` → necesita KPIs del analytics

Cuando estos se generen con datos reales, el `indirect_traffic_optimization` (que SÍ se genera) debería mostrar el IAO score real como contexto para el cliente.

---

## 4. ARCHIVOS A MODIFICAR

### D4-FIX
| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/v4_asset_orchestrator.py` | Modificar `_solutions_to_asset_specs()` para incluir assets `promised_by=["always"]` |
| `modules/asset_generation/asset_catalog.py` | Verificar que `promised_by` tenga el formato correcto para el filtro |

### OpenRouter Cost Tracking
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/llm_mention_checker.py` | Retornar `LLMReport` con campos de costo (`cost_usd`, `tokens_used`) |
| `modules/auditors/v4_comprehensive.py` | Imprimir costo en el log de audit |
| `modules/commercial_documents/v4_proposal_generator.py` | Agregar seccion IAO cost transparency en propuesta |

---

*Contexto creado 2026-04-13 — basado en E2E v4complete + OpenRouter dashboard*
