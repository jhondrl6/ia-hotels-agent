# Arquitectura IAH v4.0 - Sistema de Confianza

## Estructura de Directorios

```
modules/
├── data_validation/              # NUEVO v4.0
│   ├── __init__.py
│   ├── cross_validator.py        # Validación entre fuentes
│   ├── confidence_taxonomy.py    # Taxonomía VERIFIED/ESTIMATED/CONFLICT
│   └── external_apis/            # APIs de validación
│       ├── __init__.py
│       ├── pagespeed_client.py   # PageSpeed Insights API
│       ├── rich_results_client.py # Google Rich Results
│       └── gbp_enhanced_client.py # Google Places API
├── financial_engine/             # NUEVO v4.0 (reemplaza decision_engine)
│   ├── __init__.py
│   ├── scenario_calculator.py    # Cálculo por escenarios
│   ├── formula_transparency.py   # Explicación de cálculos
│   └── loss_projector.py         # Proyecciones con intervalos
├── asset_generation/             # NUEVO v4.0 (reemplaza delivery/manager)
│   ├── __init__.py
│   ├── preflight_checks.py       # Gates antes de generar
│   ├── conditional_generator.py  # Generación condicional
│   └── asset_metadata.py         # Metadatos obligatorios
└── orchestration_v4/             # NUEVO v4.0
    ├── __init__.py
    ├── two_phase_flow.py         # Flujo Hook → Input
    └── onboarding_controller.py  # Gestión de fases

archives/
└── legacy_v39/                   # Respaldo v3.9.1
    ├── modules/
    │   ├── decision_engine_v391.py
    │   └── delivery_manager_v391.py
    └── scripts/
        └── validate_v391.py

tests/
├── data_validation/              # Tests validación cruzada
├── financial_engine/             # Tests motor financiero
└── asset_generation/             # Tests generación assets
```

## Flujo de Datos v4.0

```
FASE 1 (HOOK): URL → Scraping básico → Benchmark regional
                    ↓
              Rango estimado ($X - $Y) con disclaimer
                    ↓
         [¿Usuario quiere precisión?]
                    ↓
FASE 2 (INPUT): 5 datos mínimos del hotel
                    ↓
         Validación Cruzada OBLIGATORIA
         ├── APIs externas (PageSpeed, Rich Results)
         ├── Cross-reference (Web vs GBP vs Input)
         └── Confidence Score (0-1) por dato
                    ↓
         Cálculo Financiero: Escenarios
         ├── Conservador (70% prob)
         ├── Realista (20% prob)
         └── Optimista (10% prob)
                    ↓
         Generación de Assets CONDICIONAL
         ├── Preflight checks (confidence ≥ 0.8)
         ├── Prefijo ESTIMATED_ si confidence < 0.9
         └── Metadatos _metadata obligatorios
                    ↓
         Entrega con checklist de confianza
```

## Taxonomía de Confianza

| Estado | Icono | Descripción | Usar en Assets |
|--------|-------|-------------|----------------|
| VERIFIED | 🟢 | 2+ fuentes coinciden | ✅ Sí |
| ESTIMATED | 🟡 | 1 fuente o benchmark | ✅ Con disclaimer |
| CONFLICT | 🔴 | Fuentes contradicen | ❌ No generar |

## Archivos Obsoletos (v3.9.1)

Movidos a `archives/legacy_v39/`:
- `modules/decision_engine.py` → Reemplazado por `financial_engine/`
- `modules/delivery/manager.py` → Reemplazado por `asset_generation/`
- `scripts/validate.py` (versión actual) → Nueva versión con checks v4.0

