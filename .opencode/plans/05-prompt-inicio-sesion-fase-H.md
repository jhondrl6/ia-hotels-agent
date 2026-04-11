# FASE-H: Activación RegionalADRResolver + Validación Benchmarks Regionales

## Contexto

Post-FASE-G, el motor financiero produce $2,610,000 COP para Amaziliahotel usando `LEGACY_DEFAULT_ADR = 300000` (hardcode genérico). El sistema YA TIENE un `RegionalADRResolver` que lee `plan_maestro_data.json` con datos calibrados por investigación propia ("Más Allá de la OTA", abril 2026). El resolver está desactivado por feature flag (`regional_adr_enabled=False`).

**Objetivo**: Activar el resolver regional en modo SHADOW, validar contra 3-4 hoteles, y promover a ACTIVE si los resultados son coherentes.

## Problema Específico

```
Cadena actual (LEGACY):
  onboarding → scraping → LEGACY_DEFAULT_ADR=$300K (GENÉRICO para TODAS las regiones)

Cadena con resolver activado:
  onboarding → scraping → REGIONAL (plan_maestro_data.json) → legacy $300K (fallback)

plan_maestro_data.json (calibrado 2026-04-07):
  eje_cafetero: ADR=$330K, ocupación=52%
  antioquia:    ADR=$280K, ocupación=60%
  caribe:       ADR=$410K, ocupación=66%
  default:      ADR=$280K, ocupación=60%
```

Con ADR regional ($330K eje_cafetero), el cálculo cambia:
- Comisión OTA: 120 noches × $330K × 15% = $5,940,000 (no $5,400,000)
- El realistic se mueve proporcionalmente

## Datos de Investigación Calibrados (ya en plan_maestro_data.json)

El archivo fue actualizado 2026-04-07 con datos de:
- **Skift Research State of Travel 2024**: 65% reservas por OTA, 35% directo
- **Mordor Intelligence Mexico 2024**: comisiones OTA 18%-25%
- **PwC/UIT 2024-2025**: adopción IA 10%-20%
- **Investigación propia**: "Más Allá de la OTA" (documento en data/benchmarks/)

Parámetros globales calibrados:
```
comision_ota_base: 0.20 (20%)
reservas_ota_proporcion: 0.65
reservas_directo_proporcion: 0.35
uso_ia_proporcion_min: 0.10
uso_ia_proporcion_max: 0.20
```

## Tareas

### Tarea 1: Verificar RegionalADRResolver funciona en SHADOW (sin touch de código)

El feature flag ya soporta `SHADOW` mode. Verificar que:
1. `FinancialFeatureFlags` lee `FINANCIAL_REGIONAL_ADR_ENABLED` del .env
2. `adr_resolution_wrapper.py` invoca `RegionalADRResolver` cuando mode=SHADOW
3. El shadow comparison se loguea sin afectar el output

**Comando de verificación**:
```bash
FINANCIAL_REGIONAL_ADR_ENABLED=True ./venv/Scripts/python.exe -c "
from modules.financial_engine.feature_flags import FinancialFeatureFlags
ff = FinancialFeatureFlags.from_env()
print(f'regional_adr_enabled: {ff.regional_adr_enabled}')
print(f'regional_adr_mode: {ff.regional_adr_mode}')
print(f'should_use_regional_adr: {ff.should_use_regional_adr()}')
print(f'is_shadow_mode: {ff.is_shadow_mode()}')
"
```

### Tarea 2: Validar resolución regional para hoteles de prueba

Ejecutar el resolver directamente (sin E2E completo) para verificar valores:

```bash
./venv/Scripts/python.exe -c "
from modules.financial_engine.regional_adr_resolver import RegionalADRResolver
resolver = RegionalADRResolver()

for region in ['eje_cafetero', 'antioquia', 'caribe', 'default', 'region_inexistente']:
    result = resolver.resolve(region, rooms=10, user_provided_adr=None)
    print(f'{region:20s} → ADR: \${result.adr_cop:>10,.0f} | source: {result.source} | confidence: {result.confidence}')
"
```

Verificar:
- eje_cafetero → $330,000
- antioquia → $280,000
- caribe → $410,000
- default → $280,000
- region_inexistente → $300,000 (fallback legacy)

### Tarea 3: Correr 3-4 hoteles en SHADOW y comparar ADRs

Para cada hotel de prueba, correr v4complete con `FINANCIAL_REGIONAL_ADR_ENABLED=True` y comparar:
- ADR legacy vs ADR regional
- Diferencia como porcentaje
- Si la diferencia es <25%, es aceptable (el regional es benchmark, no dato exacto)

Hoteles de prueba sugeridos:
1. `amaziliahotel.com` (eje_cafetero) — baseline conocido
2. `hotelvisperas.com` (región por resolver)
3. Cualquier hotel caribeño si hay uno disponible

**No se modifica output de producción** — SHADOW solo loguea comparación.

### Tarea 4: Si validación pasa — cambiar mode a ACTIVE

Si los 3-4 hoteles muestran ADRs razonables:
- Cambiar `regional_adr_mode` de SHADOW a ACTIVE en feature_flags.py default
- O documentar que se activa vía .env: `FINANCIAL_REGIONAL_ADR_ENABLED=True`
- Re-ejecutar E2E Amaziliahotel y verificar que ADR ahora es $330K (eje_cafetero)

### Tarea 5: Absorber occupancy regional (G3)

El `RegionalADRResolver` podría extenderse para resolver también occupancy desde plan_maestro_data.json:
- eje_cafetero: 0.52
- antioquia: 0.60
- caribe: 0.66

**Si es trivial** (mismo resolver, agregar campo): hacerlo en esta fase.
**Si requiere refactor**: documentar como GAP menor y deferir.

### Tarea 6: Actualizar documentation + commit

- Actualizar `diagnostico_3132_cop_investigacion.md` sección 0 GAPs G1-G3
- Actualizar `dependencias-fases.md` con FASE-H
- Ejecutar `log_phase_completion.py --fase FASE-H`
- Commit

## Restricciones

- NO modificar `plan_maestro_data.json` (ya calibrado con investigación)
- NO modificar `RegionalADRResolver` salvo para Tarea 5 (occupancy) si es trivial
- El cambio principal es CONFIGURACIÓN (feature flag), no código
- SHADOW mode primero SIEMPRE — no activar sin evidencia
- Si algún hotel muestra ADR regional inaceptablemente lejano, investigar causa antes de activar

## Criterios de Éxito

| # | Criterio | Cómo verificar |
|---|----------|----------------|
| 1 | RegionalADRResolver funciona en SHADOW | Log muestra comparación legacy vs regional |
| 2 | ADR regional coherente para 3+ regiones | diff < 25% vs legacy $300K |
| 3 | Feature flag se lee correctamente desde .env | Print confirma enabled=True |
| 4 | E2E Amaziliahotel con ADR $330K (si se activa) | JSON muestra adr_source diferente a legacy_hardcode |
| 5 | Tests de regresión pasan | 453+ tests, 0 failures |
| 6 | (Opcional) Occupancy regional resuelta | main.py usa occupancy regional vs default 50% |

## Archivos Probablemente Afectados

| Archivo | Cambio esperado |
|---------|----------------|
| `.env` o `feature_flags.py` | Activar `regional_adr_enabled=True` |
| `feature_flags.py` default | Posible cambio de SHADOW a ACTIVE |
| `regional_adr_resolver.py` | Posible extensión para occupancy (Tarea 5) |
| `main.py` | Posible consumo de occupancy regional |
| `diagnostico_3132_cop_investigacion.md` | Actualizar GAPs G1-G3 |
| `dependencias-fases.md` | Agregar FASE-H |
| `REGISTRY.md` | Via log_phase_completion.py |

## Riesgos

| Riesgo | Probabilidad | Mitigación |
|--------|-------------|------------|
| ADR regional demasiado diferente al esperado por hotelero | MEDIA | SHADOW primero, comparar con datos conocidos |
| plan_maestro_data.json tiene datos de v2.5 (obsoletos) | BAJA | Fue recalibrado 2026-04-07 con investigación actual |
| Cambio afecta pricing (pain ratio) | BAJA | Pain ratio se recalcula automáticamente con ADR correcto |
| Región no resuelta → fallback a legacy | BAJA | Ya cubierto por diseño del resolver |

## Dependencia de Fases

```
FASE-A..G (completadas) → FASE-H
```

No depende de GA4 ni de onboarding real. Es puramente configuración + validación.

## Estimación

- **Esfuerzo**: 1 sesión
- **Complejidad**: BAJA (feature flag + validación, no construcción)
- **Impacto**: ALTO (todos los hoteles sin onboarding pasan de ADR genérico a regional)
