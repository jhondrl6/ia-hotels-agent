---
description: Calculate financial scenarios (Conservative, Realistic, Optimistic) using v4.0 financial engine.
---

# Skill: V4 Financial Scenarios Calculator

> [!NOTE]
> **Trigger**: Execute during Phase 2 of onboarding after receiving hotel operational data.

## Pre-requisitos (Contexto)
- [ ] Datos operativos validados (habitaciones, ADR, ocupación, canal directo)
- [ ] Validación cruzada completada sin conflictos críticos
- [ ] Benchmark regional como contexto (no input)

## Fronteras (Scope)
- **Hará**: Calcular escenarios financieros con intervalos de confianza. Generar proyecciones realistas.
- **NO Hará**: No usar benchmarks como input directo. No generar cifras exactas sin intervalos.

## Pasos de Ejecución

### 1. Load Validated Hotel Data
// turbo
python -c "
import json

hotel_data = {
    'rooms': {{rooms}},
    'adr_cop': {{adr_cop}},
    'occupancy_rate': {{occupancy_rate}},
    'direct_channel_percentage': {{direct_channel_percentage}},
    'ota_presence': json.loads('''{{ota_presence_json}}'''),
    'region': '{{region}}'
}

# Validate required fields
required = ['rooms', 'adr_cop', 'occupancy_rate', 'direct_channel_percentage']
missing = [f for f in required if not hotel_data.get(f)]

if missing:
    print(f'ERROR: Missing fields: {missing}')
    exit(1)

print(json.dumps(hotel_data, indent=2))
"

*Validación*: Datos mínimos requeridos están presentes.

### 2. Calculate Base Revenue Potential
// turbo
python -c "
rooms = {{rooms}}
adr = {{adr_cop}}
occupancy = {{occupancy_rate}}

# Monthly potential revenue
monthly_potential = rooms * adr * 30 * occupancy
daily_potential = rooms * adr * occupancy

print(f'Monthly Revenue Potential: ${monthly_potential:,.0f} COP')
print(f'Daily Revenue Potential: ${daily_potential:,.0f} COP')
"

*Validación*: Cálculo base de ingresos potenciales.

### 3. Calculate Scenario Projections
// turbo
python -c "
import json

# Input data
rooms = {{rooms}}
adr = {{adr_cop}}
occupancy = {{occupancy_rate}}
direct_pct = {{direct_channel_percentage}}
ota_presence = json.loads('''{{ota_presence_json}}''')

# Calculate base metrics
monthly_revenue = rooms * adr * 30 * occupancy
annual_revenue = monthly_revenue * 12

# OTA commission impact (typically 15-25%)
ota_commission_rate = 0.20 if ota_presence else 0.15
ota_bookings_pct = 1 - direct_pct

# Monthly OTA commission cost
monthly_ota_cost = monthly_revenue * ota_bookings_pct * ota_commission_rate

# Conservative scenario (70% probability) - minimal improvements
conservative_capture = 0.05  # 5% improvement in direct bookings
conservative_savings = monthly_ota_cost * conservative_capture
conservative_adr_lift = 0.02  # 2% ADR improvement
conservative_adr_impact = monthly_revenue * conservative_adr_lift
conservative_total = conservative_savings + conservative_adr_impact

# Realistic scenario (20% probability) - expected improvements
realistic_capture = 0.15  # 15% improvement
realistic_savings = monthly_ota_cost * realistic_capture
realistic_adr_lift = 0.08  # 8% ADR improvement
realistic_adr_impact = monthly_revenue * realistic_adr_lift
realistic_total = realistic_savings + realistic_adr_impact

# Optimistic scenario (10% probability) - best case
optimistic_capture = 0.30  # 30% improvement
optimistic_savings = monthly_ota_cost * optimistic_capture
optimistic_adr_lift = 0.15  # 15% ADR improvement
optimistic_adr_impact = monthly_revenue * optimistic_adr_lift
optimistic_total = optimistic_savings + optimistic_adr_impact

scenarios = {
    'conservative': {
        'probability': 0.70,
        'monthly_impact_cop': round(conservative_total),
        'annual_impact_cop': round(conservative_total * 12),
        'assumptions': [
            f'Direct booking improvement: {conservative_capture*100:.0f}%',
            f'ADR lift: {conservative_adr_lift*100:.0f}%'
        ]
    },
    'realistic': {
        'probability': 0.20,
        'monthly_impact_cop': round(realistic_total),
        'annual_impact_cop': round(realistic_total * 12),
        'assumptions': [
            f'Direct booking improvement: {realistic_capture*100:.0f}%',
            f'ADR lift: {realistic_adr_lift*100:.0f}%'
        ]
    },
    'optimistic': {
        'probability': 0.10,
        'monthly_impact_cop': round(optimistic_total),
        'annual_impact_cop': round(optimistic_total * 12),
        'assumptions': [
            f'Direct booking improvement: {optimistic_capture*100:.0f}%',
            f'ADR lift: {optimistic_adr_lift*100:.0f}%'
        ]
    }
}

# Calculate weighted expected value
expected_monthly = (
    conservative_total * 0.70 +
    realistic_total * 0.20 +
    optimistic_total * 0.10
)

scenarios['expected_value'] = {
    'monthly_cop': round(expected_monthly),
    'annual_cop': round(expected_monthly * 12)
}

print(json.dumps(scenarios, indent=2, ensure_ascii=False))
"

*Validación*: Escenarios calculados con probabilidades asignadas.

### 4. Apply Confidence Intervals
// turbo
python -c "
import json

scenarios = json.loads('''{{scenarios_json}}''')

# Calculate confidence intervals (±25% for estimated data)
ci_factor = 0.25

for scenario_name in ['conservative', 'realistic', 'optimistic']:
    monthly = scenarios[scenario_name]['monthly_impact_cop']
    scenarios[scenario_name]['confidence_interval'] = {
        'lower': round(monthly * (1 - ci_factor)),
        'upper': round(monthly * (1 + ci_factor)),
        'confidence': 'MEDIA' if scenario_name == 'realistic' else 'BAJA'
    }

# Add metadata
scenarios['metadata'] = {
    'calculation_method': 'scenario_based_with_probabilities',
    'confidence_interval_applied': True,
    'ci_factor': ci_factor,
    'formula': 'Σ(scenario_value × probability)'
}

print(json.dumps(scenarios, indent=2, ensure_ascii=False))
"

*Validación*: Intervalos de confianza aplicados.

### 5. Generate Hook Message (Phase 1)
// turbo
python -c "
import json

scenarios = json.loads('''{{scenarios_json}}''')
region = '{{region}}'

conservative = scenarios['conservative']['monthly_impact_cop']
optimistic = scenarios['optimistic']['monthly_impact_cop']
expected = scenarios['expected_value']['monthly_cop']

hook_message = f'''Según el análisis preliminar, {{hotel_name}} podría estar dejando de capturar entre ${conservative:,.0f} y ${optimistic:,.0f} COP mensuales en ventas directas.

💡 Valor esperado: ${expected:,.0f} COP/mes

⚠️ Este es un rango estimado basado en benchmarks de la región {region}. Para precisar esta cifra necesitamos 5 datos de su operación.

¿Le gustaría precisar esta estimación?'''

print(hook_message)
"

*Validación*: Hook message generado con disclaimer de estimación.

### 6. Save Financial Scenarios
python -c "
import json
from datetime import datetime
from pathlib import Path

output_dir = Path('{{output_dir}}')
output_dir.mkdir(parents=True, exist_ok=True)

scenarios = json.loads('''{{scenarios_json}}''')

report = {
    'hotel': '{{hotel_name}}',
    'url': '{{url}}',
    'region': '{{region}}',
    'calculated_at': datetime.utcnow().isoformat(),
    'input_data': {
        'rooms': {{rooms}},
        'adr_cop': {{adr_cop}},
        'occupancy_rate': {{occupancy_rate}},
        'direct_channel_percentage': {{direct_channel_percentage}}
    },
    'scenarios': scenarios,
    'disclaimer': 'Estimaciones basadas en benchmarks regionales. Los resultados reales pueden variar.'
}

output_path = output_dir / 'financial_scenarios.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f'💾 Financial scenarios saved to: {output_path}')
"

*Validación*: Escenarios guardados en archivo JSON.

## Criterios de Éxito
- [ ] Todos los escenarios calculados (Conservador, Realista, Optimista).
- [ ] Probabilidades suman 100% (70+20+10).
- [ ] Intervalos de confianza aplicados.
- [ ] Hook message generado con disclaimer.
- [ ] Archivo de escenarios guardado.

## Plan de Recuperación (Fallback)
- Si faltan datos mínimos, solicitar al usuario antes de continuar.
- Si el cálculo genera valores irreales (>50% de ingresos), aplicar factor de ajuste y documentar.

## Output Format
```json
{
  "conservative": {
    "probability": 0.70,
    "monthly_impact_cop": 2500000,
    "confidence_interval": {"lower": 1875000, "upper": 3125000}
  },
  "realistic": {
    "probability": 0.20,
    "monthly_impact_cop": 8500000,
    "confidence_interval": {"lower": 6375000, "upper": 10625000}
  },
  "optimistic": {
    "probability": 0.10,
    "monthly_impact_cop": 15000000,
    "confidence_interval": {"lower": 11250000, "upper": 18750000}
  },
  "expected_value": {
    "monthly_cop": 4900000
  }
}
```