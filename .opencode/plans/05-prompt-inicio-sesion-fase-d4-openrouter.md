# Prompt de Inicio de Sesion — FASE-D4-OPENROUTER

## Contexto

Ejecutar en paralelo dos fixes críticos:
1. **D4 Fix:** 3 assets promised_by no se generaban (voice_assistant_guide, whatsapp_button, monthly_report)
2. **OpenRouter Cost Tracking:** El costo de IAO no se muestra en la propuesta

## Ejecucion E2E Pre-Fix

Antes de tocar codigo, ejecutar v4complete para capturar baseline:
```bash
mkdir -p evidence/fase-d4-openrouter
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-d4-openrouter/baseline.log
```

Verificar en el log:
- Gate 9: `aligned_count: 3, missing_count: 3`
- Output: `Busqueda por Voz` y `Boton de WhatsApp` NO en assets generados

---

## FIX-D4-A: Modificar `_solutions_to_asset_specs()` para incluir assets always

**Archivo:** `modules/asset_generation/v4_asset_orchestrator.py`

**Problema:** La linea 534-562 solo agrega assets que vienen de `solutions` (pain-driven). Assets con `promised_by=["always"]` nunca se agregan.

**Solucion:** Antes de retornar `specs`, agregar un paso que revise `ASSET_CATALOG` por entries con `promised_by` conteniendo "always" y agregarlas al plan si no ya incluidas.

**Codigo a agregar** (despues de linea 562, antes de `return specs`):
```python
# D4-FIX: Include assets with promised_by=["always"]
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetCatalogEntry
from dataclasses import fields as dc_fields

for asset_type, entry in ASSET_CATALOG.items():
    # Skip if already in specs
    if any(s.asset_type == asset_type for s in specs):
        continue
    
    # Check promised_by for "always"
    promised = getattr(entry, 'promised_by', []) or []
    if not any(p in promised for p in ['always', 'always_aeo']):
        continue
    
    # Get priority from entry or default
    priority = getattr(entry, 'priority', 5)
    
    specs.append(AssetSpec(
        asset_type=asset_type,
        problem_solved=f"promised_by_catalog_{asset_type}",
        description=f"Asset prometido: {asset_type}",
        confidence_level="ESTIMATED",
        priority=priority,
        has_automatic_solution=True,
        pain_ids=[],
        confidence_required=getattr(entry, 'min_confidence', 0.5),
        can_generate=True
    ))
```

**Restricciones:**
- NO modificar PainSolutionMapper
- NO modificar conditional_generator.py
- Solo cambiar v4_asset_orchestrator.py

---

## FIX-D4-B: Verificar que `voice_assistant_guide` se incluye por `always_aeo`

El catalogo tiene:
- `voice_assistant_guide.promised_by = ["always_aeo"]`

Esto requiere que la propuesta haya prometido AEO. Verificar que el filtro en FIX-D4-A cubra `always_aeo`.

---

## FIX-OPENROUTER-A: Extender LLMReport con campos de costo

**Archivo:** `modules/auditors/llm_mention_checker.py`

**Problema:** `LLMReport` no tiene campos para costo o tokens.

**Solucion:** Agregar campos a `LLMReport` dataclass:
```python
@dataclass
class LLMReport:
    # ... existing fields ...
    cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    provider_name: Optional[str] = None
```

Modificar `_query_openrouter()` para extraer costo del response:
```python
# After getting data from response
native_data = data.get("native_tokens_completion", 0) + data.get("native_tokens_prompt", 0)
return LLMReport(
    # ... existing fields ...,
    cost_usd=data.get("usage", 0.0),
    tokens_used=native_data,
    provider_name="openrouter"
)
```

Modificar `_query_gemini()` y `_query_perplexity()` analogamente.

---

## FIX-OPENROUTER-B: Imprimir costo en V4ComprehensiveAuditor

**Archivo:** `modules/auditors/v4_comprehensive.py` linea ~544

Despues de print de providers_used, agregar:
```python
if llm_report.cost_usd:
    print(f"      Costo IAO: ${llm_report.cost_usd:.4f} USD")
    print(f"      Tokens: {llm_report.tokens_used}")
```

---

## FIX-OPENROUTER-C: Seccion de transparencia de IAO en propuesta

**Archivo:** `modules/commercial_documents/templates/propuesta_v6_template.md`

Agregar seccion `${iao_cost_transparency}` despues de la tabla de assets.

**Contenido模板:**
```
## Transparencia de IAO (Inteligencia Artificial Outside)

El análisis de IAO utiliza APIs de terceros (OpenRouter, Google AI, Perplexity) para evaluar si tu hotel aparece en recomendaciones de ChatGPT, Google AI Overviews y otros sistemas de IA.

| Proveedor | Queries | Costo Aprox. |
|-----------|---------|---------------|
| OpenRouter | {openrouter_queries} | ${openrouter_cost:.4f} USD |
| Gemini | {gemini_queries} | ${gemini_cost:.4f} USD |
| Perplexity | {perplexity_queries} | ${perplexity_cost:.4f} USD |
| **Total** | **{total_queries}** | **${total_cost:.4f} USD** |

*Este costo es Absorption por IAH-CLI y no se carga al cliente.*
```

Modificar `v4_proposal_generator.py` para injectar `${iao_cost_transparency}` con valores reales.

---

## Verificacion Post-Fix

1. **Regression tests:**
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py tests/quality_gates/test_proposal_alignment_gate.py -v --tb=short
```

2. **E2E v4complete:**
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-d4-openrouter/postfix.log
```

3. **Verificar en postfix.log:**
- Gate 9: `aligned_count >= 6` (antes 3)
- Gate 9: `missing_count <= 1` (idealmente 0, monthly_report puede seguir faltando)
- Costo IAO impreso en el log
- `${iao_cost_transparency}` renderizado en PROPUESTA_COMERCIAL.md

4. **Verificar en disco:**
```bash
ls output/v4_complete/amaziliahotel/whatsapp_button/
ls output/v4_complete/amaziliahotel/voice_assistant_guide/
ls output/v4_complete/amaziliahotel/monthly_report/
```

---

## Success Criteria

| Criterio | Antes | Despues |
|----------|-------|---------|
| aligned_count en Gate 9 | 3 | >= 6 |
| missing_count en Gate 9 | 3 | <= 1 |
| whatsapp_button en disco | NO | SI |
| voice_assistant_guide en disco | NO | SI |
| monthly_report en disco | NO | SI (o documentado como pendiente) |
| Costo IAO visible en log | NO | SI |
| Seccion IAO en propuesta | NO | SI |

---

## Archivos Afectados

| Archivo | Modificacion |
|---------|-------------|
| `modules/asset_generation/v4_asset_orchestrator.py` | FIX-D4-A |
| `modules/auditors/llm_mention_checker.py` | FIX-OPENROUTER-A |
| `modules/auditors/v4_comprehensive.py` | FIX-OPENROUTER-B |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | FIX-OPENROUTER-C |
| `modules/commercial_documents/v4_proposal_generator.py` | FIX-OPENROUTER-C |

**Restricciones:**
- NO romper la cadena financiera
- NO modificar tests existentes (solo agregar nuevos si necesario)
- Una fase por sesion si hay errores

---

*Prompt creado 2026-04-13*
