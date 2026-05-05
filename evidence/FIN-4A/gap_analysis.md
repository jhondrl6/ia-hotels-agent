# Gap Analysis — Financial Engine Integration

> **Fase**: FIN-4A  
> **Hotel de prueba**: Hotel Castilla Real (hotelcastillareal.com)  
> **Sesión**: 2026-05-04  
> **Modo**: Investigación pura (no se ejecutó v4complete)

---

## GAP-1: ADR Legacy no usa feature flags

| Atributo | Valor |
|----------|-------|
| **file:line** | `modules/financial_engine/adr_resolution_wrapper.py:242` |
| **función** | `ADRResolutionWrapper._legacy_resolution()` |
| **fuente del valor** | `LEGACY_DEFAULT_ADR = 300000.0` (linea 49) |

### Causa raíz (2 problemas encadenados)

**Problema A — Feature flags deshabilitados por defecto:**
- `FinancialFeatureFlags()` sin env vars → `regional_adr_enabled=False`, `regional_adr_mode=SHADOW`
- `from_env()` SÍ lee las env vars correctamente cuando están presentes
- El wrapper NUNCA usa ADR regional porque el flag está en False

**Problema B — Incompatibilidad de case en region string:**
- Hotel Castilla Real tiene region `"Eje Cafetero"` (title case, extraído del DOM)
- `validated_regions = ("eje_cafetero", "antioquia", "caribe")` (lowercase)
- `should_use_regional_for("Eje Cafetero")` → `False` (comparación case-sensitive)
- Aunque se habiliten los flags, la comparación falla

### Cadena de resolución para Castilla Real

```
main.py:1735 → resolve_adr_with_shadow(region="Eje Cafetero")
  → ADRResolutionWrapper.resolve()
    → flags.should_use_regional_for("Eje Cafetero") → False
      → _legacy_resolution_with_scraping()
        → _legacy_resolution() → LEGACY_DEFAULT_ADR = 300000.0
```

### Fix requerido

1. **Habilitar env vars** antes de ejecutar v4complete:
   ```bash
   export FINANCIAL_REGIONAL_ADR_ENABLED=true
   export FINANCIAL_REGIONAL_ADR_MODE=active
   ```

2. **Normalizar region** en `feature_flags.py:should_use_regional_for()` o en el código que extrae la región:
   ```python
   # En should_use_regional_for(), hacer comparison insensible a mayúsculas:
   return region.lower() in [r.lower() for r in self.validated_regions]
   ```

---

## GAP-2: opportunity_scores en v4_complete_report.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:2946-2948` (escritura del JSON) |
| **fuente del cálculo** | `v4_diagnostic_generator.py:2848` |

### Causa raíz

`v4_complete_report.json` se construye en `main.py:2859-2944` y se escribe en `2946-2948`.

El dict `report` incluye:
- `phases.phase_3_scenarios` (conservative/realistic/optimistic values)
- `financial_data.scenarios`
- `coherence_score`, `seo_score`, `pricing`, `analytics`

**NO incluye** `opportunity_scores`.

Los scores SÍ se calculan en `_compute_opportunity_scores()` (v4_diagnostic_generator.py:2848), se pasan a `_inject_brecha_scores()` (2872), se inyectan al template como `brecha_N_score`, `brecha_N_severity`, etc. Pero NUNCA se persisten al JSON.

### Fix requerido

En `main.py:2944` (antes de `json.dump`), agregar:

```python
# GAP-2 fix: agregar opportunity_scores al report
'opportunity_scores': _get_opportunity_scores_from_diagnostic(diagnostic_gen, audit_result, financial_scenarios_obj),
```

O más directamente: que `diagnostic_gen.generate()` retorne un dict con `opportunity_scores` que se pase al report.

---

## GAP-3: channel_context en v4_complete_report.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:2946-2948` (escritura del JSON) |
| **fuente del cálculo** | `v4_diagnostic_generator.py:2845` |

### Causa raíz

`_resolve_channel_context()` se ejecuta dentro de `_compute_opportunity_scores()` (line 2845) y retorna un dict con `dominant_channel`, `confidence`, `channel_weights`.

Este dict se usa internamente para pasar a `OpportunityScorer.score_brechas()` (line 2852) como `channel_context`, pero **el resultado NUNCA se persiste al JSON**.

El `v4_complete_report.json` no tiene campo `channel_context`.

### Fix requerido

Igual que GAP-2: persiste el resultado de `_resolve_channel_context()` al report dict en `main.py`.

---

## GAP-4: precision_tier en financial_scenarios.json

| Atributo | Valor |
|----------|-------|
| **file:line** | `main.py:1876-1896` (escritura del JSON) |
| **cálculo existe** | `v4_diagnostic_generator.py:1069` (`PrecisionValidator.validate()`) |

### Causa raíz

`PrecisionValidator.validate()` SÍ se ejecuta (line 1069) dentro de `_prepare_financial_template_vars()`, y retorna `precision_tier` y `can_show_exact_money` que se usan para:
- `monthly_loss_display` (cifra exacta vs rango)
- `precision_warning`
- `show_onboarding_cta`

PERO `financial_scenarios.json` se escribe en `main.py:1876-1896` con estructura:
```json
{
  "hotel": ...,
  "url": ...,
  "input_data": { "rooms", "adr_cop", "occupancy_rate", "direct_channel_percentage" },
  "scenarios": ...,
  "expected_monthly_cop": ...,
  "breakdown": ...,
  "pricing": ...
}
```

**NO incluye** `precision_tier` ni `can_show_exact_money`.

### Fix requerido

En `main.py:1895` (dentro del dict de `json.dump`), agregar:
```python
'precision_tier': _get_precision_tier_from_validator(),
'can_show_exact_money': _get_can_show_exact_from_validator(),
```

O usar `FinancialEvidence.to_dict()` que ya incluye estos campos (financial_evidence.py:101-103).

---

## Resumen para FIN-4B

| GAP | Archivo a modificar | Tipo de cambio | Estimado líneas |
|-----|---------------------|:--------------:|:---------------:|
| 1 | `modules/financial_engine/feature_flags.py` | Normalizar case en `should_use_regional_for()` | ~2 |
| 1 | Env vars | Habilitar `FINANCIAL_REGIONAL_ADR_ENABLED=true` | N/A |
| 2 | `main.py` (cerca de line 2944) | Agregar `opportunity_scores` al dict del report | ~3 |
| 3 | `main.py` (cerca de line 2944) | Agregar `channel_context` al dict del report | ~3 |
| 4 | `main.py` (cerca de line 1895) | Agregar `precision_tier` y `can_show_exact_money` al JSON | ~3 |

### Notas de implementación

- **GAP-1**: El fix de case-sensitivity en `should_use_regional_for()` es el más robusto. Alternativa: normalizar la región cuando se extrae del hotel (en onboarding o detección).
- **GAP-2 y GAP-3**: Ambos requieren pasar datos del `V4DiagnosticGenerator` al scope de `main.py` donde se construye el report. Actualmente `diagnostic_gen` existe pero no se extraen estos campos.
- **GAP-4**: `FinancialEvidence.to_dict()` (financial_evidence.py:94-103) ya tiene la serialización correcta. Solo falta invocarla y agregar al JSON.

---

## Evidencia de verificación

```bash
# Verificar GAP-1: ADR = 300000 en financial_scenarios.json
cat output/v4_complete/financial_scenarios.json | jq '.input_data.adr_cop'
# → 300000.0

# Verificar GAP-2/3: No opportunity_scores ni channel_context en report
cat output/v4_complete/v4_complete_report.json | jq 'keys'
# → ["analytics","assets_generated","coherence_score","financial_data",
#     "hotel_id","hotel_name","modules_used","phases","pricing",
#     "region","seo_score","url","v4_complete"]
# → NO opportunity_scores NI channel_context

# Verificar GAP-4: precision_tier ausente de financial_scenarios.json
cat output/v4_complete/financial_scenarios.json | jq 'has("precision_tier")'
# → false
```
