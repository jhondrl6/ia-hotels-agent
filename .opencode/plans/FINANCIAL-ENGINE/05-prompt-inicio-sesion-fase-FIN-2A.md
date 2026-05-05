# 05-prompt-inicio-sesion-fase-FIN-2A

**Fase**: FIN-2A — Regional Benchmark Structured Data Source  
**Plan**: Financial Evidence Engine  
**Sesión**: Nueva (fresh)  
**Iteraciones máx**: 60  
**Depende de**: FIN-1A ✅, FIN-1B ✅  
**Bloquea a**: FIN-2B  

---

## Objetivo

Crear fuente estructurada `regional_adr_2026.json` con datos 2026 de `Benchmarking.md` y modificar `RegionalADRResolver` para devolver metadata epistémica (no solo valor crudo). Esta fase asegura que los benchmarks regionales estén disponibles como `regional_benchmark`, no como `legacy_hardcode`.

---

## Contexto de Fases Anteriores

- FIN-1A: `FinancialEvidence`, `EpistemicStatus`, `PrecisionTier` existen
- FIN-1B: `classify_source()`, `determine_precision_tier()`, `PrecisionValidator` existen

---

## Tareas

### T1: Crear `data/benchmarks/regional_adr_2026.json`

Extraer valores de `data/benchmarks/Benchmarking.md` (tablas L43-60) a JSON estructurado:

```json
{
  "version": "1.0.0",
  "description": "Benchmarks regionales 2026 para motor financiero — estimaciones, NO datos exactos de hotel",
  "last_updated": "2026-05-03",
  "source_document": "data/benchmarks/Benchmarking.md",
  "source_role": "regional_benchmark_not_hotel_specific",
  "valid_for_exact_projection": false,
  "epistemic_status": "regional_benchmark",
  "default_region": "eje_cafetero",
  "regions": {
    "eje_cafetero": {
      "boutique_10_25": {
        "adr_cop": 420000,
        "occupancy_rate": 0.512,
        "rooms_range": [10, 25]
      },
      "standard_26_60": {
        "adr_cop": 350000,
        "occupancy_rate": 0.512,
        "rooms_range": [26, 60]
      }
    },
    "caribe": {
      "boutique_10_25": {
        "adr_cop": 950000,
        "occupancy_rate": 0.685,
        "rooms_range": [10, 25]
      },
      "standard_26_60": {
        "adr_cop": 750000,
        "occupancy_rate": 0.685,
        "rooms_range": [26, 60]
      }
    },
    "antioquia": {
      "boutique_10_25": {
        "adr_cop": 620000,
        "occupancy_rate": 0.642,
        "rooms_range": [10, 25]
      },
      "standard_26_60": {
        "adr_cop": 480000,
        "occupancy_rate": 0.642,
        "rooms_range": [26, 60]
      }
    },
    "default": {
      "any": {
        "adr_cop": 300000,
        "occupancy_rate": 0.50,
        "note": "LEGACY — usado solo si no hay match regional. Marcar epistemic_status=defaulted."
      }
    }
  }
}
```

### T2: Modificar `RegionalADRResolver` para metadata

**Archivo**: `modules/financial_engine/regional_adr_resolver.py`

Cambios:

1. **Nuevo método `_load_regional_benchmarks()`** que cargue `regional_adr_2026.json` (fallback a `plan_maestro_data.json` si no existe):

```python
def _load_regional_benchmarks(self) -> Dict:
    paths = [
        "data/benchmarks/regional_adr_2026.json",
        "data/benchmarks/plan_maestro_data.json",  # fallback
    ]
    for path in paths:
        if Path(path).exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    return {}
```

2. **Extender `RegionalADRResult`** con campos epistémicos:

```python
@dataclass
class RegionalADRResult:
    adr_cop: float
    region: str
    segment: str
    confidence: str
    source: str
    is_default: bool = False
    metadata: Dict[str, Any] = None
    # NUEVOS:
    epistemic_status: str = "regional_benchmark"
    can_show_exact: bool = False
    occupancy_rate: Optional[float] = None  # Para pasar ocupación regional también
```

3. **Modificar `resolve()`** para que retorne `epistemic_status="regional_benchmark"` (no "VERIFIED"/"ESTIMATED" genérico) y `can_show_exact=False`.

4. **Agregar `resolve_occupancy()`** si no existe (el contexto dice que "ya puede leer ocupación regional" en L165). Verificar y si existe, solo asegurar que retorne metadata correcta.

### T3: Actualizar nota histórica en `plan_maestro_data.json` (si aplica)

**Solo si** `plan_maestro_data.json` vuelve a usarse como fallback. Si no, no tocar.

Si `_load_regional_benchmarks()` usa `plan_maestro_data.json` como fallback, agregar al header del JSON:

```json
"nota_v4_40": "Usado como fallback si regional_adr_2026.json no existe. Datos 2026 están en regional_adr_2026.json."
```

### T4: Tests unitarios

**Archivo**: `tests/financial_engine/test_regional_adr_2026.py` (NUEVO)

Mínimo 8 tests:
1. `test_load_regional_adr_2026_exists` → Carga correcta del JSON
2. `test_resolve_eje_cafetero_boutique` → ADR 420000, epistemic_status=regional_benchmark
3. `test_resolve_caribe_boutique` → ADR 950000
4. `test_resolve_unknown_region_fallback_default` → Caída a default
5. `test_regional_result_can_show_exact_false` → Siempre False para regional_benchmark
6. `test_regional_result_has_occupancy` → occupancy_rate en metadata
7. `test_regional_result_epistemic_status` → "regional_benchmark" (nunca "VERIFIED")
8. `test_segment_determination_boutique_vs_standard` → Segmentos correctos por rooms

---

## Criterios de Completitud

- [ ] `data/benchmarks/regional_adr_2026.json` existe con 3 regiones + default
- [ ] `RegionalADRResolver` carga nuevo JSON y retorna metadata epistémica
- [ ] `RegionalADRResult.epistemic_status` = `"regional_benchmark"` (no "VERIFIED")
- [ ] `RegionalADRResult.can_show_exact` = `False` siempre
- [ ] `RegionalADRResult.occupancy_rate` poblado
- [ ] `tests/financial_engine/test_regional_adr_2026.py` ≥8 tests pasando
- [ ] Tests existentes de regional_adr_resolver sin regresiones

---

## Restricciones

- Máximo 60 iteraciones
- **NO modificar `feature_flags.py`** (FIN-2B)
- **NO eliminar `plan_maestro_data.json`** (mantener como fallback)
- **NO tocar `ADRResolutionWrapper`** (FIN-2B)
- **NO cambiar defaults de `plan_maestro_data.json`** (es legacy, intocable)

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-2A \
    --desc "Regional benchmark 2026 structured data + RegionalADRResolver metadata" \
    --archivos-nuevos "data/benchmarks/regional_adr_2026.json,tests/financial_engine/test_regional_adr_2026.py" \
    --archivos-mod "modules/financial_engine/regional_adr_resolver.py" \
    --tests "8" \
    --check-manual-docs
```
