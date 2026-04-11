# FASE-I: Activar RegionalADRResolver por Regiones Validadas

## Contexto

El motor financiero usa `LEGACY_DEFAULT_ADR = $300,000` para TODOS los hoteles sin importar region.
El `RegionalADRResolver` YA EXISTE y fue parcheado en FASE-H, pero esta DESACTIVADO (`regional_adr_enabled=False` en `feature_flags.py:30`).

FASE-H decidio NO promover a ACTIVE por la anomalia del Caribe (36.7% diff vs legacy).
Pero eje_cafetero y antioquia son coherentes. La solucion: whitelist por region.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A..H | ✅ Completadas |

### Base Tecnica Disponible
- `modules/financial_engine/regional_adr_resolver.py` — YA tiene `resolve()`, `resolve_occupancy()`, `get_segment_adr_table()`
- `modules/financial_engine/feature_flags.py` — YA tiene `regional_adr_enabled`, `RolloutMode`, `from_env()`
- `modules/financial_engine/adr_resolution_wrapper.py` — YA tiene `resolve_adr_with_shadow()`
- `data/benchmarks/plan_maestro_data.json` — YA calibrado con datos regionales

---

## Tareas

### Tarea 1: Agregar whitelist de regiones validadas a feature_flags.py

**Archivo**: `modules/financial_engine/feature_flags.py`

Agregar despues de linea 32 (`financial_v410_enabled`):

```python
# Regiones validadas para usar ADR regional (no legacy)
validated_regions: tuple = ("eje_cafetero", "antioquia")
```

Agregar metodo:
```python
def should_use_regional_for(self, region: str) -> bool:
    """Check if regional ADR should be used for a specific region."""
    return self.regional_adr_enabled and region in self.validated_regions
```

Actualizar `from_env()` para leer `FINANCIAL_REGIONAL_VALIDATED_REGIONS` (comma-separated):
```python
validated_regions_str = os.getenv("FINANCIAL_REGIONAL_VALIDATED_REGIONS", "eje_cafetero,antioquia")
validated_regions=tuple(r.strip() for r in validated_regions_str.split(",") if r.strip()),
```

### Tarea 2: Modificar adr_resolution_wrapper.py para usar regiones validadas

**Archivo**: `modules/financial_engine/adr_resolution_wrapper.py`

En la funcion `resolve_adr_with_shadow()`, agregar logica:
- Si `flags.should_use_regional_for(region)` → usar RegionalADRResolver para ADR y occupancy
- Si NO → mantener legacy (comportamiento actual)
- Siempre loguear comparacion shadow (legacy vs regional)

```python
# Pseudocodigo del cambio en resolve_adr_with_shadow():
if flags.should_use_regional_for(region):
    resolver = RegionalADRResolver(plan_maestro_path)
    regional_result = resolver.resolve(region, rooms, user_provided_adr)
    regional_occupancy = resolver.resolve_occupancy(region)
    # Usar ADR regional como principal
    adr_cop = regional_result.adr_cop
    source = f"regional_v410_{regional_result.confidence.lower()}"
    # Shadow: loguear comparacion con legacy
else:
    # Comportamiento actual (legacy)
    adr_cop = LEGACY_DEFAULT_ADR
```

### Tarea 3: Modificar harness_handlers.py para pasar region

**Archivo**: `modules/financial_engine/harness_handlers.py`

En `financial_calculation_handler()` (lineas 88-89):
```python
# ANTES:
occupancy_rate = payload.get("occupancy_rate", 0.50)
direct_channel_percentage = payload.get("direct_channel_percentage", 0.20)

# DESPUES:
# Resolver occupancy regional si el flag lo permite
flags = FinancialFeatureFlags.from_env()
region = payload.get("region", "default")

if flags.should_use_regional_for(region):
    from modules.financial_engine.regional_adr_resolver import RegionalADRResolver
    _resolver = RegionalADRResolver()
    occupancy_rate = payload.get("occupancy_rate") or _resolver.resolve_occupancy(region)
else:
    occupancy_rate = payload.get("occupancy_rate", 0.50)

direct_channel_percentage = payload.get("direct_channel_percentage", 0.20)
```

### Tarea 4: Modificar main.py para consumir occupancy regional

**Archivo**: `main.py` (~linea 1630 donde se define occupancy_rate)

Buscar donde se asigna `occupancy_rate` y agregar fallback a occupancy regional:

```python
# Si no hay onboarding_data con occupancy, usar regional si el flag lo permite
if occupancy_rate == 0.50 and flags.should_use_regional_for(region):
    from modules.financial_engine.regional_adr_resolver import RegionalADRResolver
    _reg_resolver = RegionalADRResolver()
    occupancy_rate = _reg_resolver.resolve_occupancy(region)
    print(f"   Occupancy regional: {occupancy_rate:.0%} ({region})")
```

### Tarea 5: Activar feature flag en .env

**Archivo**: `.env`

Agregar:
```
FINANCIAL_REGIONAL_ADR_ENABLED=True
FINANCIAL_REGIONAL_VALIDATED_REGIONS=eje_cafetero,antioquia
```

### Tarea 6: Tests

Crear/actualizar tests:

```python
# test_feature_flags_whitelist.py
def test_validated_regions_default():
    flags = FinancialFeatureFlags(regional_adr_enabled=True)
    assert "eje_cafetero" in flags.validated_regions
    assert "antioquia" in flags.validated_regions
    assert "caribe" not in flags.validated_regions  # NO validada

def test_should_use_regional_for():
    flags = FinancialFeatureFlags(regional_adr_enabled=True)
    assert flags.should_use_regional_for("eje_cafetero") == True
    assert flags.should_use_regional_for("antioquia") == True
    assert flags.should_use_regional_for("caribe") == False
    assert flags.should_use_regional_for("default") == False

def test_disabled_flag_never_uses_regional():
    flags = FinancialFeatureFlags(regional_adr_enabled=False)
    assert flags.should_use_regional_for("eje_cafetero") == False

def test_from_env_validated_regions():
    import os
    os.environ["FINANCIAL_REGIONAL_VALIDATED_REGIONS"] = "eje_cafetero,antioquia"
    flags = FinancialFeatureFlags.from_env()
    assert len(flags.validated_regions) == 2
    del os.environ["FINANCIAL_REGIONAL_VALIDATED_REGIONS"]
```

### Tarea 7: Validacion E2E

```bash
# Ejecutar v4complete con flag activado
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-I/ejecucion.log
```

Verificar en output:
- ADR muestra $330,000 (no $300,000)
- Occupancy muestra 52% (no 50%)
- `financial_scenarios.json` → `data_sources.adr` cambia de "legacy_hardcode" a "regional_v410_estimated"
- Comision OTA: 120 noches × $330K × 15% = $5,940,000 (no $5,400,000)

---

## Criterios de Aceptacion

| # | Criterio | Verificacion |
|---|----------|-------------|
| 1 | Feature flag con whitelist de regiones | `FinancialFeatureFlags.should_use_regional_for("eje_cafetero") == True` |
| 2 | Caribe NO usa regional (protegido) | `should_use_regional_for("caribe") == False` |
| 3 | ADR Amazilia = $330K (eje_cafetero) | `financial_scenarios.json` → `adr_cop: 330000` |
| 4 | Occupancy Amazilia = 52% | E2E log muestra "Occupancy regional: 52%" |
| 5 | Tests nuevos pasan | 4 tests, 0 failures |
| 6 | Suite regresion pasa | `./venv/Scripts/python.exe -m pytest tests/ -x --tb=short -q` |
| 7 | E2E exit code 0 | `evidence/fase-I/ejecucion.log` termina sin crash |

---

## Restricciones

- NO tocar `no_defaults_validator.py` — eso es FASE-J
- NO tocar `diagnostico_v6_template.md` — eso es FASE-J
- NO eliminar el camino dual de main.py:1721-1733 — eso es FASE-K
- NO modificar `scenario_calculator.py` — eso es FASE-K
- Caribe permanece en legacy hasta investigacion adicional
- Si E2E falla, iterar max 3 veces (patron cascada del skill)

---

## Post-Ejecucion (OBLIGATORIO)

1. `dependencias-fases.md` — Marcar FASE-I como ✅ Completada
2. `06-checklist-implementacion.md` — Marcar FASE-I
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-I \
    --desc "Activar RegionalADRResolver por regiones validadas (eje_cafetero, antioquia)" \
    --archivos-mod "modules/financial_engine/feature_flags.py,modules/financial_engine/harness_handlers.py,main.py" \
    --tests "4"
```
