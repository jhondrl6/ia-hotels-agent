# FASE-F: Template Diagnóstico + Evidence Tiers en YAML

**ID**: FASE-F
**Objetivo**: Rediseñar el template `diagnostico_v6_template.md` para la narrativa de "Comisión OTA verificable → escenarios de mejora" con evidence tiers. Actualizar `v4_diagnostic_generator.py` para llenar los nuevos placeholders.
**Dependencias**: FASE-E (consumidores usan valor central)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

El template actual (`diagnostico_v6_template.md`, 115 líneas) presenta:
```
**Pérdida estimada mensual: $3,132,000 COP**
```

Esto es el techo del rango (x1.2), mezcla hechos con supuestos, y no tiene disclaimers.

El nuevo template debe presentar:
```
COMISIÓN OTA ACTUAL (verificable): $5,400,000 COP/mes
Desglose: 120 noches OTA × $300,000 ADR × 15% comisión

Potencial de recuperación con mejora digital:
  Escenario conservador: $X COP/mes
  Escenario realista: $Y COP/mes
  Escenario optimista: $Z COP/mes
  *Estimación basada en benchmarks regionales.
```

Y en el YAML header:
```yaml
financial_evidence_tier: C
financial_source: financial_scenarios.json#realistic
financial_value_central: 2610000
financial_value_range: [2088000, 3132000]
financial_method: proportional_normalized
```

### GAP D del archivo de investigación (Sección 14.4):
El template tiene 4 placeholders financieros (líneas 60, 62, 68, 82) que deben cambiar de "Pérdida" a "Comisión OTA + escenarios".

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ✅ Completada |
| FASE-D | ✅/⬜ (puede estar pendiente, es independiente) |
| FASE-E | ✅ Completada |

### Base Técnica Disponible
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (115 líneas)
- `modules/commercial_documents/v4_diagnostic_generator.py` — llena el template
- Archivo de investigación Secciones 11.1-11.5 (narrativa propuesta)
- Archivo de investigación Sección 14.4 (GAP D — estructura exacta del template)

---

## Tareas

### Tarea 1: Rediseñar `diagnostico_v6_template.md`

**Objetivo**: Nuevo template con narrativa por capas y evidence tier.

**Archivo afectado**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Estructura propuesta** (reemplazar líneas 55-85):

```markdown
## 💰 Impacto Financiero

### Comisión OTA Actual (verificable)

**${ota_commission_formatted} COP/mes**

Desglose:
- ${ota_commission_basis}
- Fuente del dato: ${ota_commission_source}

---

### Oportunidad de Mejora

Brechas detectadas que afectan su presencia digital y reservas directas:

${brechas_section}

---

### Escenarios de Recuperación

| Escenario | Ahorro mensual | Probabilidad |
|-----------|---------------|--------------|
| ${scenario_table_rows} |

**Proyección 6 meses:** ${loss_6_months} COP

> ⚠️ ${financial_disclaimer}
> 
> *Nivel de evidencia: **Tier ${evidence_tier}***
> - Tier A: Basado en Google Analytics + Search Console
> - Tier B: Basado en benchmarks regionales + datos web
> - Tier C: Basado en datos limitados de su web
```

**Nuevos placeholders**:
- `${ota_commission_formatted}` — Comisión OTA formateada en COP
- `${ota_commission_basis}` — "120 noches OTA × $300K ADR × 15%"
- `${ota_commission_source}` — "onboarding" / "scraping" / "benchmark"
- `${scenario_table_rows}` — 3 filas de escenarios
- `${financial_disclaimer}` — Disclaimer del EvidenceTier
- `${evidence_tier}` — A, B o C

**Placeholders eliminados/renombrados**:
- `${monthly_loss}` → reemplazado por comisión OTA + escenarios
- `${loss_6_months}` → se mantiene pero recalculado con valor central

**Criterios de aceptación**:
- [ ] Template tiene sección "Comisión OTA Actual (verificable)"
- [ ] Template tiene sección "Escenarios de Recuperación"
- [ ] Template tiene evidence tier disclaimer
- [ ] Template tiene YAML front matter con campos financieros

### Tarea 2: Actualizar YAML front matter del template

**Objetivo**: Agregar metadata financiera rastreable.

**Archivo afectado**: `modules/commercial_documents/templates/diagnostico_v6_template.md`

**Agregar al YAML front matter**:
```yaml
financial_evidence_tier: "${evidence_tier}"
financial_source: "${financial_source_ref}"
financial_value_central: ${financial_value_central}
financial_value_range: [${financial_value_min}, ${financial_value_max}]
financial_method: "${financial_method}"
```

**Criterios de aceptación**:
- [ ] YAML header tiene los 5 campos financieros
- [ ] Los valores son placeholders que el generador llenará

### Tarea 3: Actualizar `v4_diagnostic_generator.py` para llenar nuevos placeholders

**Objetivo**: El generador debe llenar los nuevos placeholders del template con datos de FinancialBreakdown.

**Archivo afectado**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Cambios principales**:

1. Línea ~471 (título del impacto financiero):
```python
# ANTES: main_scenario_amount = main.monthly_loss_max
# DESPUÉS: ota_commission = breakdown.monthly_ota_commission_cop si existe
# Si no hay breakdown, fallback a valor central o max
```

2. Línea ~442 (proyección 6 meses):
```python
# ANTES: loss_6_months_value = main.monthly_loss_max * 6
# DESPUÉS: loss_6_months_value = self._get_base_value(main) * 6
```

3. Línea ~551 (template V6):
```python
# ANTES: monthly_loss = format_cop(main.monthly_loss_max)
# DESPUÉS: llenar ota_commission_formatted, ota_commission_basis, etc.
```

4. Línea ~897 (empathy message):
```python
# ANTES: usa monthly_loss_max
# DESPUÉS: usa valor central con disclaimer
```

5. Nuevo: método `_build_financial_placeholders()`:
```python
def _build_financial_placeholders(self, financial_scenarios, breakdown=None):
    """Construye los placeholders financieros para el template."""
    main = financial_scenarios.get_main_scenario()
    base_value = getattr(main, 'monthly_loss_central', None) or main.monthly_loss_max
    
    if breakdown:
        ota_commission = format_cop(breakdown.monthly_ota_commission_cop)
        ota_basis = breakdown.ota_commission_basis
        ota_source = breakdown.ota_commission_source
        tier = breakdown.evidence_tier
        disclaimer = breakdown.disclaimer
    else:
        ota_commission = format_cop(base_value)
        ota_basis = "No disponible"
        ota_source = "unknown"
        tier = "C"
        disclaimer = EvidenceTier.C.disclaimer
    
    return {
        'ota_commission_formatted': ota_commission,
        'ota_commission_basis': ota_basis,
        'ota_commission_source': ota_source,
        'evidence_tier': tier,
        'financial_disclaimer': disclaimer,
        'financial_source_ref': 'financial_scenarios.json#realistic',
        'financial_value_central': base_value,
        'financial_value_min': main.monthly_loss_min,
        'financial_value_max': main.monthly_loss_max,
        'financial_method': 'proportional_normalized',
        # Mantener compatibilidad con template viejo:
        'monthly_loss': ota_commission,
        'loss_6_months': format_cop(base_value * 6),
    }
```

**Criterios de aceptación**:
- [ ] Todos los placeholders nuevos se llenan correctamente
- [ ] Si no hay breakdown, fallback a datos del Scenario (backward compat)
- [ ] Evidence tier aparece en el documento generado
- [ ] Disclaimer aparece en el documento generado

### Tarea 4: Test de generación end-to-end (parcial)

**Objetivo**: Verificar que el generador produce un documento con la nueva estructura.

**Archivo afectado**: tests del generador de diagnóstico

**Tests requeridos**:
```python
# 1. Placeholders financieros se llenan
def test_financial_placeholders_filled():
    # Generar diagnóstico con FinancialBreakdown
    # Verificar que ota_commission_formatted no es "${...}"

# 2. Evidence tier aparece
def test_evidence_tier_in_output():
    # Verificar que el output contiene "Tier C" o similar

# 3. Disclaimer aparece
def test_disclaimer_in_output():
    # Verificar que el output contiene el disclaimer

# 4. Sin breakdown (backward compat)
def test_no_breakdown_backward_compat():
    # Generar diagnóstico sin FinancialBreakdown
    # Verificar que funciona con fallback a Scenario
```

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasan
- [ ] Tests existentes del generador pasan

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| test_financial_placeholders_filled | tests del generador | Placeholders llenos |
| test_evidence_tier_in_output | tests del generador | Tier visible |
| test_disclaimer_in_output | tests del generador | Disclaimer visible |
| test_no_breakdown_backward_compat | tests del generador | Funciona sin breakdown |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -30
```

---

## Restricciones

- NO modificar main.py — eso es FASE-G
- El template viejo debe seguir funcionando si no hay FinancialBreakdown
- NO cambiar los placeholders de brechas (${brecha_1}, etc.) — esos se llenan con pesos normalizados de FASE-C
- El YAML front matter es metadata del documento generado, NO del template mismo. Los placeholders tipo `${...}` se resuelven en generación

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-F como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-F
3. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-F \
    --desc "Template diagnóstico: narrativa Comisión OTA + Evidence Tiers en YAML" \
    --archivos-mod "modules/commercial_documents/templates/diagnostico_v6_template.md,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "4"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Template rediseñado con "Comisión OTA verificable" como dato principal
- [ ] Evidence tier disclaimer en el documento
- [ ] YAML front matter con metadata financiera
- [ ] Generador llena todos los placeholders nuevos
- [ ] Backward compatible (funciona sin FinancialBreakdown)
- [ ] 4 tests nuevos pasan
- [ ] Suite completa pasa
- [ ] `log_phase_completion.py` ejecutado
