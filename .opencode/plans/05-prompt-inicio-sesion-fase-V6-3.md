---
description: FASE V6-3 - Dynamic impact_cop desde financial_scenarios en asset_diagnostic_linker
version: 1.0.0
fase: V6-3
---

# FASE V6-3: Dynamic impact_cop desde FinancialScenarios

## Contexto

Actualmente `_get_narrative_fields()` en `asset_diagnostic_linker.py` tiene valores `impact_cop` hardcoded:
```python
"whatsapp_button": {"impact_cop": 1500000, ...}
"llms_txt": {"impact_cop": 100000, ...}  # P3 con $100K???!
```

Estos valores deben calcularse desde `financial_scenarios` del audit real para que sean coherentes con la propuesta V6.

**Dependencia:** FASE V6-1 (templates V6 creados)

## Tareas

### Tarea 1: Analizar data flow actual

Ver cómo llega `financial_scenarios` al `AssetDiagnosticLinker`:
- Leer `v4_asset_orchestrator.py` para ver si tiene acceso a `financial_scenarios`
- Leer `_get_narrative_fields()` en `asset_diagnostic_linker.py`

### Tarea 2: Calcular impact_cop proporcional

El approach correcto:
1. `impact_cop` de cada asset debe ser proporcional a la pérdida mensual del hotel
2. La distribución debe basarse en la `priority` del asset (P1=40%, P2=30%, P3=20%, P4=10%)
3. O usar una formula basada en qué porcentaje del problema resuelve ese asset

**Fórmula propuesta:**
```python
impact_cop = financial_scenarios.main.monthly_loss_max * asset_weight
```

Donde `asset_weight` viene de `pain_solution_mapper.PAIN_SOLUTION_MAP[asset_type]["estimated_impact"]`:
- "high" = 0.40
- "medium" = 0.25
- "low" = 0.15

### Tarea 3: Modificar `_get_narrative_fields()`

Agregar parámetro `financial_scenarios` y calcular `impact_cop` dinámicamente.

**IMPORTANTE:** Mantener backward compatibility - si no se pasa `financial_scenarios`, usar valores default.

## Criterios de Completitud

- [ ] `_get_narrative_fields()` acepta `financial_scenarios` como parámetro opcional
- [ ] `impact_cop` se calcula dinámicamente cuando hay datos
- [ ] Valores default cuando no hay `financial_scenarios`
- [ ] Tests pasan

## Post-Ejecución

1. Marcar checklist como completado
2. NO ejecutar `log_phase_completion.py` aún - esperar a FASE V6-5

## Archivos a Modificar

| Archivo | Acción |
|---------|--------|
| `modules/asset_generation/asset_diagnostic_linker.py` | MODIFICAR |

## Tests a Ejecutar

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -k "asset_diagnostic" -v --tb=short
```
