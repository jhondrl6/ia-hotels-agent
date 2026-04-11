# FASE-E: Consumidores — Proposal, Coherence, Asset Linker

**ID**: FASE-E
**Objetivo**: Actualizar los 3 consumidores principales de `monthly_loss_max` para usar el nuevo valor central + FinancialBreakdown: v4_proposal_generator.py (22 puntos), coherence_validator.py (1 punto), asset_diagnostic_linker.py (3 puntos).
**Dependencias**: FASE-B (ScenarioCalculator produce FinancialBreakdown), FASE-C (pesos normalizados)
**Duración estimada**: 2.5-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Hay 22+ puntos donde `monthly_loss_max` se consume como valor principal. El mapa completo está en el archivo de investigación, Sección 16. Esta fase cambia TODOS esos consumidores de `max` a `central`, y donde aplica, consume el `FinancialBreakdown` para narrativa por capas.

**Principio**: Todos los cambios usan `getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max` para backward compatibility.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada — Scenario.monthly_loss_central |
| FASE-B | ✅ Completada — calculate_breakdown() |
| FASE-C | ✅ Completada — pesos normalizados |
| FASE-D | ⬜ (independiente, puede estar pendiente) |

### Base Técnica Disponible
- `modules/commercial_documents/v4_proposal_generator.py` — 22 puntos de consumo
- `modules/validation/coherence_validator.py` — línea 433: `pain = .monthly_loss_max`
- `modules/asset_generation/asset_diagnostic_linker.py` — líneas 498-507: impacto por asset
- Mapa completo: Sección 16 del archivo de investigación

---

## Tareas

### Tarea 1: Actualizar `v4_proposal_generator.py` (22 puntos)

**Objetivo**: Reemplazar todas las referencias a `monthly_loss_max` por valor central.

**Archivo afectado**: `modules/commercial_documents/v4_proposal_generator.py`

**Puntos a modificar (del mapa en Sección 16)**:

| Línea | Variable actual | Cambio |
|-------|----------------|--------|
| 457 | `projected_monthly_gain = main.monthly_loss_max` | Usar central |
| 489 | `conservative_gain = main.monthly_loss_max` | Usar central |
| 490 | `conservative_roi` | Se recalcula con central |
| 491 | `realistic_gain = main.monthly_loss_max` | Usar central |
| 492 | `realistic_roi` | Se recalcula |
| 493 | `optimistic_gain = main.monthly_loss_max` | Usar central |
| 494 | `optimistic_roi` | Se recalcula |
| 503-508 | `rec_m1` a `rec_m6` | Usar central |
| 509-514 | `net_m1` a `net_m6` | Usar central |

**Patrón de cambio**:
```python
# Helper method a agregar:
def _get_main_value(self, scenario):
    """Obtiene valor central de presentación, con fallback a max."""
    return getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max

# Reemplazar todas las ocurrencias:
# ANTES: main.monthly_loss_max
# DESPUÉS: self._get_main_value(main)
```

**Criterios de aceptación**:
- [ ] Las 22 referencias a `monthly_loss_max` cambian a valor central
- [ ] Backward compatible: si no hay central, usa max
- [ ] ROI, gains, proyecciones M1-M6 recalculan con valor central

### Tarea 2: Actualizar `coherence_validator.py`

**Objetivo**: Cambiar el cálculo de pain para usar valor central.

**Archivo afectado**: `modules/validation/coherence_validator.py` línea 433

**Cambio**:
```python
# ANTES:
pain = diagnostic.financial_impact.monthly_loss_max

# DESPUÉS:
main = diagnostic.financial_impact
pain = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
```

**Nota importante**: El coherence_validator calcula ratio precio/pain. Si pain baja (de $3.1M a $2.6M), el ratio sube. Verificar que siga pasando el gate de 0.8 con los datos de Amaziliahotel.

**Criterios de aceptación**:
- [ ] `pain` usa valor central con fallback
- [ ] Gate de coherencia (ratio 0.03-0.06) sigue funcionando
- [ ] Test de coherence_validator pasa con valor central

### Tarea 3: Actualizar `asset_diagnostic_linker.py`

**Objetivo**: Cambiar cálculo de impacto por asset para usar valor central.

**Archivo afectado**: `modules/asset_generation/asset_diagnostic_linker.py` líneas 498-507

**Cambios**:
```python
# Línea 498: impact_cop = max * weight
# Línea 504: impact_cop = max * weight
# Línea 507: impact_cop = max * 0.25

# Helper:
def _get_base_value(self, scenario):
    return getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max

# Reemplazar las 3 ocurrencias de monthly_loss_max por:
base = self._get_base_value(main)
impact_cop = base * weight  # o base * 0.25 para fallback
```

**Criterios de aceptación**:
- [ ] Las 3 referencias a `monthly_loss_max` cambian a valor central
- [ ] Backward compatible

### Tarea 4: Tests de regresión

**Objetivo**: Verificar que los cambios no rompen los consumidores.

**Tests requeridos**:
```python
# 1. Proposal usa valor central cuando existe
def test_proposal_uses_central():
    # Crear Scenario con central=2610000, max=3132000
    # Verificar que proposal genera ganancia basada en 2610000, no 3132000

# 2. Coherence pain usa central
def test_coherence_pain_central():
    # Verificar que pain = 2610000 (central), no 3132000 (max)

# 3. Asset linker usa central
def test_asset_linker_central():
    # Verificar impact_cop = central * weight

# 4. Backward compat sin central
def test_backward_compat_no_central():
    # Crear Scenario sin monthly_loss_central
    # Verificar que usa monthly_loss_max como antes
```

**Criterios de aceptación**:
- [ ] Tests nuevos pasan
- [ ] Tests existentes de proposal, coherence, asset_linker pasan
- [ ] Suite completa pasa

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_proposal_uses_central | tests del proposal | Ganancia basada en central |
| test_coherence_pain_central | tests del coherence | Pain = central |
| test_asset_linker_central | tests del asset_linker | Impact = central × weight |
| test_backward_compat_no_central | tests varios | Funciona con max como fallback |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -30
```

---

## Restricciones

- NO modificar main.py — eso es FASE-G
- NO modificar template V6 — eso es FASE-F
- Usar siempre `getattr(scenario, 'monthly_loss_central', None) or scenario.monthly_loss_max` — NUNCA asumir que central existe
- NO cambiar la lógica de ROI ni las fórmulas de proyección — solo cambiar el valor base de max a central
- La interfaz pública de los 3 módulos NO cambia (mismas funciones, mismos signatures)

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-E como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-E
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-E \
    --desc "Consumidores: proposal+coherence+asset_linker usan valor central (22 puntos)" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/validation/coherence_validator.py,modules/asset_generation/asset_diagnostic_linker.py" \
    --tests "4"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] v4_proposal_generator.py: 22 puntos cambiados a central
- [ ] coherence_validator.py: pain usa central
- [ ] asset_diagnostic_linker.py: 3 puntos cambiados a central
- [ ] Todos los cambios son backward compatible (fallback a max)
- [ ] Tests nuevos y existentes pasan
- [ ] `log_phase_completion.py` ejecutado
