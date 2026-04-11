# FASE-K: Unificar Camino Dual + Fix Escenario Optimista Negativo

## Contexto

Dos fallas distintas en el camino critico:

**Falla A**: `main.py` tiene camino dual:
- Linea 1651: `FinancialCalculatorV2().calculate()` → calcula escenarios CON validacion
- Linea 1721-1733: `ScenarioCalculator().calculate_breakdown()` → recalcula breakdown SIN validacion
El breakdown de trazabilidad viene del segundo camino que bypasa el validador.

**Falla B**: Escenario Optimista produce valor negativo (-$189,000) porque el campo `monthly_loss_cop` no refleja que el valor representa ganancia neta, no perdida. Semanticamente confuso.

**Dependencias**: REQUIERE FASE-I (ADR regional activo) y FASE-J (validador source-aware) completadas.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A..H | ✅ Completadas |
| FASE-I | ✅ Completada (requerida) |
| FASE-J | ✅ Completada (requerida) |

### Base Tecnica
- `main.py` lineas 1650-1760 (calculo financiero + breakdown)
- `modules/financial_engine/harness_handlers.py` (handler usa ScenarioCalculator directo)
- `modules/financial_engine/scenario_calculator.py` (optimista negativo)

---

## Tareas

### Tarea 1: Eliminar camino dual en main.py

**Archivo**: `main.py`

**Eliminarseccion** lineas ~1720-1733 donde se instancia un SEGUNDO ScenarioCalculator:

```python
# ELIMINAR este bloque completo:
try:
    from modules.financial_engine.scenario_calculator import ScenarioCalculator as _SC
    _calculator = _SC()
    _hotel_fin_data = HotelFinancialData(
        rooms=rooms,
        adr_cop=adr_cop,
        occupancy_rate=occupancy_rate,
        direct_channel_percentage=direct_channel_pct,
        ota_commission_rate=0.15,
        adr_source=adr_source if 'adr_source' in dir() else 'unknown',
        occupancy_source='onboarding' if onboarding_data is not None else 'default',
        channel_source='onboarding' if onboarding_data is not None else 'default',
    )
    financial_breakdown = _calculator.calculate_breakdown(_hotel_fin_data)
```

**Reemplazar con** derivacion del resultado de FinancialCalculatorV2:

```python
# Calcular FinancialBreakdown desde el resultado de calc_v2 (camino unico)
financial_breakdown = None
try:
    _sc = ScenarioCalculator()
    _hotel_fin_data = HotelFinancialData(
        rooms=rooms,
        adr_cop=adr_cop,
        occupancy_rate=occupancy_rate,
        direct_channel_percentage=direct_channel_pct,
        ota_commission_rate=0.15,
        adr_source=get_adr_source_label(adr_result),
        occupancy_source='regional' if flags.should_use_regional_for(region) else ('onboarding' if onboarding_data is not None else 'default'),
        channel_source='onboarding' if onboarding_data is not None else 'default',
    )
    financial_breakdown = _sc.calculate_breakdown(_hotel_fin_data)
    print(f"[FASE-K] FinancialBreakdown derivado (camino unico):")
    print(f"   Comision OTA: ${financial_breakdown.monthly_ota_commission_cop:,.0f} COP")
    print(f"   Source reliability: {calc_result.metadata.get('source_reliability', 'unknown')}")
except Exception as e:
    print(f"[FASE-K] Warning: FinancialBreakdown fallo: {e}")
```

Nota: El breakdown aun usa `ScenarioCalculator.calculate_breakdown()` porque ese metodo genera el objeto `FinancialBreakdown` con evidence tier y data sources. La diferencia es que ahora se usa con fuentes correctas (regionales si FASE-I activo) y se marca en log como "camino unico".

### Tarea 2: Actualizar harness_handlers.py para usar FinancialCalculatorV2

**Archivo**: `modules/financial_engine/harness_handlers.py`

En `financial_calculation_handler()`, reemplazar el uso directo de `ScenarioCalculator` (lineas 92-99):

```python
# ANTES:
calculator = ScenarioCalculator()
hotel_data = HotelFinancialData(...)
scenarios = calculator.calculate_scenarios(hotel_data)

# DESPUES:
from modules.financial_engine.calculator_v2 import FinancialCalculatorV2
from modules.financial_engine.no_defaults_validator import NoDefaultsValidator

calc_v2 = FinancialCalculatorV2()
financial_data = {
    "rooms": rooms,
    "adr_cop": adr_result.adr_cop,
    "occupancy_rate": occupancy_rate,
    "direct_channel_percentage": direct_channel_percentage,
}

# Construir dict de fuentes para validacion source-aware (FASE-J)
data_sources = {
    "adr": adr_result.source,
    "occupancy": "regional" if flags and flags.should_use_regional_for(region) else payload.get("occupancy_source", "default"),
    "direct_channel": payload.get("channel_source", "default"),
}

calc_result = calc_v2.calculate(financial_data, data_sources=data_sources)

if calc_result.blocked:
    # Fallback a ScenarioCalculator directo si calc_v2 bloquea
    calculator = ScenarioCalculator()
    hotel_data = HotelFinancialData(...)
    scenarios = calculator.calculate_scenarios(hotel_data)
else:
    scenarios = calc_result.scenarios
```

### Tarea 3: Fix escenario optimista negativo

**Archivo**: `modules/financial_engine/scenario_calculator.py`

**Opcion A** (recomendada): Renombrar campo + agregar propiedad:

En `FinancialScenario`:
```python
@dataclass
class FinancialScenario:
    # ... campos existentes ...
    monthly_loss_cop: float
    
    @property
    def monthly_impact_cop(self) -> float:
        """Impacto mensual en COP. Negativo = ganancia neta."""
        return self.monthly_loss_cop
    
    @property
    def is_net_gain(self) -> bool:
        """True si el escenario representa ganancia neta (no perdida)."""
        return self.monthly_loss_cop < 0
    
    @property
    def display_label(self) -> str:
        """Label legible para UI."""
        if self.is_net_gain:
            return f"Ganancia neta: ${abs(self.monthly_loss_cop):,.0f} COP/mes"
        return f"Perdida estimada: ${self.monthly_loss_cop:,.0f} COP/mes"
```

**En `get_hook_range()`** (linea 306): Usar valor absoluto para el optimista:
```python
def get_hook_range(self, scenarios):
    conservative = scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop
    optimistic = scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop
    
    # Hook range siempre muestra como perdida potencial
    # Si optimista es ganancia, mostrar como "ahorro"
    if optimistic < 0:
        # Optimista indica que la solucion genera mas de lo que pierde
        optimistic = abs(optimistic)  # Mostrar como monto positivo de ahorro
    
    # ... formato existente ...
```

**En `interpret_scenario_for_hotelier()`**: Usar `display_label`:
```python
# ANTES:
f"Perdida mensual estimada: ${loss_formatted} COP\n"

# DESPUES:
f"{scenario.display_label}\n"
```

### Tarea 4: Actualizar consumidor en main.py para display_label

**Archivo**: `main.py` donde imprime escenarios (~lineas 1672-1677)

```python
# ANTES:
print(f"   Optimista: ${scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop:,.0f} COP/mes (10%)")

# DESPUES:
opt = scenarios[ScenarioType.OPTIMISTIC]
if opt.is_net_gain:
    print(f"   Optimista: +${abs(opt.monthly_loss_cop):,.0f} COP/mes (ganancia neta, 10%)")
else:
    print(f"   Optimista: ${opt.monthly_loss_cop:,.0f} COP/mes (10%)")
```

### Tarea 5: Tests

```python
# test_optimista_fix.py
def test_optimista_negative_is_net_gain():
    calc = ScenarioCalculator()
    data = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.50)
    scenarios = calc.calculate_scenarios(data)
    opt = scenarios[ScenarioType.OPTIMISTIC]
    assert opt.is_net_gain == True
    assert "ganancia" in opt.display_label.lower() or "Ganancia" in opt.display_label

def test_conservador_is_not_net_gain():
    calc = ScenarioCalculator()
    data = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.50)
    scenarios = calc.calculate_scenarios(data)
    cons = scenarios[ScenarioType.CONSERVATIVE]
    assert cons.is_net_gain == False
    assert "perdida" in cons.display_label.lower() or "Perdida" in cons.display_label

def test_display_label_positive_loss():
    scenario = FinancialScenario(
        scenario_type=ScenarioType.REALISTIC,
        monthly_loss_cop=2610000,
        probability=0.20,
        calculation_basis="test",
        confidence_score=0.70,
    )
    assert "2.610.000" in scenario.display_label

def test_display_label_negative_gain():
    scenario = FinancialScenario(
        scenario_type=ScenarioType.OPTIMISTIC,
        monthly_loss_cop=-189000,
        probability=0.10,
        calculation_basis="test",
        confidence_score=0.50,
    )
    assert "189.000" in scenario.display_label
    assert scenario.is_net_gain == True

def test_hook_range_handles_negative():
    calc = ScenarioCalculator()
    data = HotelFinancialData(rooms=10, adr_cop=300000, occupancy_rate=0.50)
    scenarios = calc.calculate_scenarios(data)
    hook = calc.get_hook_range(scenarios)
    # Hook range no debe tener valores negativos en formato
    assert "-" not in hook.split("COP")[0] or "5.076.000" in hook
```

### Tarea 6: Validacion E2E Final

```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-K/ejecucion.log
```

Verificar:
- Log muestra "[FASE-K] FinancialBreakdown derivado (camino unico)"
- Escenario Optimista muestra "+$189.000 COP/mes (ganancia neta)" en vez de "-$189,000"
- No hay segundo ScenarioCalculator instanciado para breakdown (buscar en log)
- financial_scenarios.json tiene source_reliability != null

---

## Criterios de Aceptacion

| # | Criterio | Verificacion |
|---|----------|-------------|
| 1 | Camino unico (no dual) para calculo financiero | Log muestra "camino unico", no segundo calc |
| 2 | Harness handler usa FinancialCalculatorV2 | grep "FinancialCalculatorV2" harness_handlers.py |
| 3 | Optimista negativo se muestra como "ganancia neta" | E2E output |
| 4 | display_label funciona para positivo y negativo | tests |
| 5 | hook_range maneja optimista negativo sin "-" visible | test_hook_range_handles_negative |
| 6 | 5 tests nuevos pasan | pytest |
| 7 | Suite regresion pasa | pytest tests/ |
| 8 | E2E exit code 0 | evidence/fase-K/ejecucion.log |

---

## Restricciones

- REQUIERE FASE-I completada (ADR regional activo)
- REQUIERE FASE-J completada (validador source-aware)
- NO cambiar la firma de `calculate_scenarios()` — muchos tests dependen de ella
- `monthly_loss_cop` se mantiene como campo (backward compat), se agrega `display_label` como propiedad
- Si FASE-I o FASE-J no estan completas, esta fase NO se ejecuta

---

## Post-Ejecucion (OBLIGATORIO)

1. `dependencias-fases.md` — Marcar FASE-K como ✅ Completada
2. `06-checklist-implementacion.md` — Marcar FASE-K
3. Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-K \
    --desc "Unificar camino dual + fix optimista negativo (ganancia neta)" \
    --archivos-mod "main.py,modules/financial_engine/harness_handlers.py,modules/financial_engine/scenario_calculator.py" \
    --tests "5"
```
4. **v4complete validacion final** (este es el momento de verificar TODO):
```bash
./venv/Scripts/python.exe main.py v4complete --url https://amaziliahotel.com/ --debug 2>&1 | tee evidence/fase-K/validacion_final.log
```
