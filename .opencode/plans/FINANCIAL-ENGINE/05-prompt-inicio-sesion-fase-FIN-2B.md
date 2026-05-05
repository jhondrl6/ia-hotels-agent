# 05-prompt-inicio-sesion-fase-FIN-2B

**Fase**: FIN-2B — Feature Flags + Fallback Chain Honesto  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅, FIN-1B ✅, FIN-2A ✅  
**Bloquea a**: FIN-3  

---

## Objetivo

Ajustar `feature_flags.py` para incluir Caribe en regiones validadas, y modificar `ADRResolutionWrapper` para que propague `epistemic_status` y `can_show_exact` a través de toda la cadena de fallback. Esta fase es el punto de integración: conecta el modelo epistémico (FIN-1A/B) con los datos regionales (FIN-2A) en el wrapper que usa `main.py`.

---

## Contexto de Fases Anteriores

- FIN-1A: `FinancialEvidence`, `EpistemicStatus`, `build_financial_evidence()` existen
- FIN-1B: `classify_source()`, `determine_precision_tier()`, `PrecisionValidator` existen
- FIN-2A: `regional_adr_2026.json` existe, `RegionalADRResult` tiene `epistemic_status` y `can_show_exact`

---

## Tareas

### T1: Agregar Caribe a `validated_regions`

**Archivo**: `modules/financial_engine/feature_flags.py`

```python
# ANTES (L48):
validated_regions: tuple = ("eje_cafetero", "antioquia")

# DESPUÉS:
validated_regions: tuple = ("eje_cafetero", "antioquia", "caribe")
```

También en `from_env()` (L49-61) actualizar el default de `validated_regions` si se construye desde env. Actualmente el dataclass tiene el default en el field; `from_env()` no lo pisa → no necesita cambio adicional.

Verificar que `should_use_regional_for(region)` acepte "caribe".

### T2: Extender `ADRResolutionResult` con metadata epistémica

**Archivo**: `modules/financial_engine/adr_resolution_wrapper.py`

Agregar campos a `ADRResolutionResult`:

```python
@dataclass
class ADRResolutionResult:
    adr_cop: float
    source: str
    confidence: str
    used_new_calculation: bool
    shadow_comparison: Optional[ShadowComparison] = None
    metadata: Optional[Dict[str, Any]] = None
    # NUEVOS:
    epistemic_status: str = "defaulted"
    can_show_exact: bool = False
    occupancy_rate: Optional[float] = None  # Del resolver regional
```

### T3: Propagar metadata en la cadena de fallback

En el método `resolve()` de `ADRResolutionWrapper`, cada camino debe setear `epistemic_status` correctamente:

| Camino | `epistemic_status` | `can_show_exact` |
|--------|-------------------|-------------------|
| `user_provided_adr` | `"measured"` | `True` |
| `web_scraping_adr` | `"observed"` | `True` |
| Regional benchmark | `"regional_benchmark"` | `False` |
| `LEGACY_DEFAULT_ADR` | `"defaulted"` | `False` |

Modificar estos métodos:
- `_web_scraping_result()` → agregar `epistemic_status="observed"`, `can_show_exact=True`
- `_legacy_resolution()` → agregar `epistemic_status="defaulted"`, `can_show_exact=False`
- `_new_resolution_with_scraping()` → cuando cae a regional, usar `epistemic_status="regional_benchmark"` y `can_show_exact=False`
- `_shadow_resolution_with_scraping()` → ídem

También propagar `occupancy_rate` desde el resolver regional al resultado.

### T4: Tests unitarios + integración

**Archivo**: `tests/financial_engine/test_fallback_chain_honesto.py` (NUEVO)

Mínimo 8 tests:
1. `test_user_provided_adr_measured_can_show_exact` → epistemic=measured, can_show_exact=True
2. `test_web_scraping_adr_observed_can_show_exact` → epistemic=observed, can_show_exact=True
3. `test_regional_benchmark_cannot_show_exact` → epistemic=regional_benchmark, can_show_exact=False
4. `test_legacy_hardcode_defaulted_cannot_show_exact` → epistemic=defaulted, can_show_exact=False
5. `test_caribe_region_validated` → should_use_regional_for("caribe") = True
6. `test_unknown_region_not_validated` → should_use_regional_for("bogota") = False
7. `test_full_fallback_chain_epistemic` → Cadena completa con diferentes combinaciones
8. `test_occupancy_rate_propagated_from_regional` → occupancy_rate en metadata

---

## Criterios de Completitud

- [ ] `validated_regions` incluye `"caribe"`
- [ ] `ADRResolutionResult` tiene `epistemic_status`, `can_show_exact`, `occupancy_rate`
- [ ] Cada camino de `resolve()` setea metadata epistémica correcta
- [ ] Benchmark regional nunca tiene `can_show_exact=True`
- [ ] Legacy hardcode nunca tiene `can_show_exact=True`
- [ ] `tests/financial_engine/test_fallback_chain_honesto.py` ≥8 tests pasando
- [ ] Tests existentes de `adr_resolution_wrapper` sin regresiones

---

## Restricciones

- Máximo 60 iteraciones
- **NO cambiar `regional_adr_enabled` default** — sigue `False`. Solo se expande `validated_regions`.
- **NO eliminar `LEGACY_DEFAULT_ADR`** — conservar como fallback invisible
- **NO tocar templates** (FIN-3)
- **NO modificar `main.py`** a menos que sea estrictamente necesario para propagar metadata

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-2B \
    --desc "Feature flags Caribe + ADRResolutionWrapper con metadata epistémica" \
    --archivos-nuevos "tests/financial_engine/test_fallback_chain_honesto.py" \
    --archivos-mod "modules/financial_engine/feature_flags.py,modules/financial_engine/adr_resolution_wrapper.py" \
    --tests "8" \
    --check-manual-docs
```
