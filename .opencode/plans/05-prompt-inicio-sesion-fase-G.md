# FASE-G: Integración main.py + Validación End-to-End

**ID**: FASE-G
**Objetivo**: Conectar todos los componentes en `main.py`: construir `FinancialBreakdown` con datos de FASE-B, pasar `monthly_loss_central` a los Scenarios, propagar breakdown a los generadores, y ejecutar prueba end-to-end con Amaziliahotel para verificar que el documento final cumple los 4 criterios de éxito.
**Dependencias**: FASE-F (template + evidence tiers), FASE-D (scraper→ADR)
**Duración estimada**: 3-4 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

Esta es la fase de integración. Todos los componentes existen:
- `FinancialBreakdown` (FASE-A)
- `ScenarioCalculator.calculate_breakdown()` (FASE-B)
- Pesos normalizados (FASE-C)
- Scraper→ADR (FASE-D)
- Consumidores actualizados (FASE-E)
- Template con evidence tiers (FASE-F)

Ahora `main.py` debe orquestar todo:
1. Resolver ADR con scraping fallback (FASE-D ya tocó la llamada)
2. Calcular FinancialBreakdown vía ScenarioCalculator
3. Construir FinancialScenarios con `monthly_loss_central`
4. Pasar breakdown a los generadores
5. Verificar documento final end-to-end

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada |
| FASE-B | ✅ Completada |
| FASE-C | ✅ Completada |
| FASE-D | ✅ Completada |
| FASE-E | ✅ Completada |
| FASE-F | ✅ Completada |

### Base Técnica Disponible
- `main.py` — función `cmd_v4complete()` (~2000 líneas)
- Bloques clave:
  - Líneas 507-508: Scraper ejecuta, `hotel_data` disponible
  - Línea 1526: ADR resolution (FASE-D ya pasó web_scraping_adr)
  - Líneas 1664-1715: Cálculo financiero y guardado en JSON
  - Líneas 1875-1894: Construcción de FinancialScenarios
  - Líneas 1900+: Llamada a generadores (diagnostic, proposal)
- Caso de prueba: Amaziliahotel (datos en Sección 8 del archivo de investigación)

---

## Tareas

### Tarea 1: Construir FinancialBreakdown en el bloque financiero de main.py

**Objetivo**: Después de obtener ADR y hotel_data, llamar `calculate_breakdown()`.

**Archivo afectado**: `main.py` (~línea 1664, después del cálculo de escenarios)

**Cambios**:
```python
# Después del cálculo de escenarios existente:
calc_result = calculator.calculate_scenarios(hotel_financial_data)
expected_monthly = calc_result.get_realistic_loss()

# NUEVO: Calcular breakdown con los mismos datos
financial_breakdown = calculator.calculate_breakdown(hotel_financial_data)

# Guardar breakdown en financial_scenarios.json para auditoría
financial_data['breakdown'] = {
    'ota_commission_cop': financial_breakdown.monthly_ota_commission_cop,
    'ota_commission_basis': financial_breakdown.ota_commission_basis,
    'ota_commission_source': financial_breakdown.ota_commission_source,
    'shift_savings_cop': financial_breakdown.shift_savings_cop,
    'shift_percentage': financial_breakdown.shift_percentage,
    'shift_source': financial_breakdown.shift_source,
    'ia_revenue_cop': financial_breakdown.ia_revenue_cop,
    'ia_boost_percentage': financial_breakdown.ia_boost_percentage,
    'ia_source': financial_breakdown.ia_source,
    'evidence_tier': financial_breakdown.evidence_tier,
    'disclaimer': financial_breakdown.disclaimer,
    'data_sources': financial_breakdown.hotel_data_sources,
}
```

**Criterios de aceptación**:
- [ ] `calculate_breakdown()` se llama con `hotel_financial_data`
- [ ] Breakdown se guarda en `financial_scenarios.json`
- [ ] Si falla, no crashea el flujo (try/except con log)

### Tarea 2: Construir FinancialScenarios con `monthly_loss_central`

**Objetivo**: Las instancias de Scenario ahora incluyen el valor central.

**Archivo afectado**: `main.py` líneas 1875-1894

**Cambios**:
```python
# ANTES:
realistic_value = calc_result.get_realistic_loss()  # $2,610,000
financial_scenarios_obj = FinancialScenarios(
    realistic=Scenario(
        monthly_loss_min=int(realistic_value * 0.8),     # $2,088,000
        monthly_loss_max=int(realistic_value * 1.2),     # $3,132,000
        probability=0.20,
        description="Meta esperada",
        monthly_opportunity_cop=0),
    ...
)

# DESPUÉS:
realistic_value = calc_result.get_realistic_loss()  # $2,610,000
financial_scenarios_obj = FinancialScenarios(
    realistic=Scenario(
        monthly_loss_min=int(realistic_value * 0.8),     # $2,088,000 (piso)
        monthly_loss_max=int(realistic_value * 1.2),     # $3,132,000 (techo, para rangos)
        monthly_loss_central=realistic_value,             # $2,610,000 ← VALOR CENTRAL
        probability=0.20,
        description="Meta esperada",
        monthly_opportunity_cop=0),
    conservative=Scenario(
        monthly_loss_min=conservative_value,
        monthly_loss_max=int(conservative_value * 1.2),
        monthly_loss_central=conservative_value,           # NUEVO
        probability=0.70,
        description="Peor caso plausible",
        monthly_opportunity_cop=0),
    optimistic=Scenario(
        monthly_loss_min=int(optimistic_value * 0.8) if optimistic_value > 0 else int(optimistic_value * 1.2),
        monthly_loss_max=optimistic_value,
        monthly_loss_central=optimistic_value,              # NUEVO
        probability=0.10,
        description="Mejor caso",
        monthly_opportunity_cop=optimistic_opportunity),
)
```

**Criterios de aceptación**:
- [ ] Los 3 Scenarios tienen `monthly_loss_central` poblado
- [ ] `monthly_loss_max` se mantiene como techo del rango (NO se elimina)
- [ ] El valor central es el valor calculado (sin x1.2)

### Tarea 3: Pasar breakdown a los generadores

**Objetivo**: Los generadores de diagnóstico y propuesta reciben el breakdown.

**Archivo afectado**: `main.py` (~líneas 1900+)

**Cambios**:
```python
# Pasar breakdown a generador de diagnóstico
diagnostic_result = diagnostic_generator.generate(
    audit_result=audit_result,
    financial_scenarios=financial_scenarios_obj,
    financial_breakdown=financial_breakdown,  # NUEVO parámetro
    ...
)

# Pasar breakdown a generador de propuesta (si aplica)
proposal_result = proposal_generator.generate(
    financial_scenarios=financial_scenarios_obj,
    financial_breakdown=financial_breakdown,  # NUEVO parámetro
    ...
)
```

**Nota**: Verificar las firmas de los generadores. Si el parámetro `financial_breakdown` no existe en sus firmas, agregarlo como opcional (`financial_breakdown=None`). Los generadores deben funcionar sin breakdown (backward compat).

**Criterios de aceptación**:
- [ ] `financial_breakdown` se pasa a ambos generadores
- [ ] Si los generadores no lo soportan, se agrega como parámetro opcional
- [ ] Si el generador no recibe breakdown, funciona como antes

### Tarea 4: Prueba End-to-End con Amaziliahotel

**Objetivo**: Ejecutar el flujo completo y verificar los 4 criterios de éxito.

**Datos de Amaziliahotel**:
```
hotel: amaziliahotel.com
region: eje_cafetero
rooms: 10, adr: 300,000, occupancy: 50%, direct_channel: 20%
```

**Criterios de éxito del documento generado**:

| # | Criterio | Verificación | Valor esperado |
|---|----------|-------------|----------------|
| 1 | Rastreable a fuente | Cada dato tiene fuente documentada | `hotel_data_sources` no vacío |
| 2 | Proporcional | Pesos de brechas suman 100% | Suma de impactos = ~100% |
| 3 | Etiquetado VERIFIED/ESTIMATED | Evidence tier visible | Tier C en YAML + disclaimer |
| 4 | Basado en hecho verificable | Comisión OTA como dato principal | $5,400,000 COP visible |
| 5 | Valor central (no techo) | Cifra principal = realistic sin x1.2 | $2,610,000 (no $3,132,000) |
| 6 | Pesos normalizados | No hay porción "sin explicar" | 4 brechas = 100% |

**Comando de prueba**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe main.py --url https://amaziliahotel.com --full-audit
```

**Verificar en output**:
```bash
# 1. Comisión OTA aparece como dato principal
grep "5.400.000" output/v4_complete/diagnostico_*.md

# 2. Evidence tier en YAML
grep "evidence_tier" output/v4_complete/diagnostico_*.md

# 3. Valor central (no inflado)
grep "2.610.000" output/v4_complete/diagnostico_*.md

# 4. No muestra el valor inflado
# grep "3.132.000" NO debe aparecer como cifra principal

# 5. Breakdown en JSON
cat output/v4_complete/financial_scenarios.json | grep -A 20 "breakdown"
```

**Criterios de aceptación**:
- [ ] End-to-end ejecuta sin errores
- [ ] Documento muestra comisión OTA como dato principal
- [ ] Evidence tier (C) visible en YAML header
- [ ] Valor central ($2.6M) no valor inflado ($3.1M)
- [ ] Pesos de brechas suman 100%
- [ ] Disclaimer aparece en el documento

### Tarea 5: Suite de regresión completa

**Objetivo**: Verificar que NO se rompió nada existente.

**Comando**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -30
```

**Criterios de aceptación**:
- [ ] 0 failures
- [ ] 0 errors

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| E2E Amaziliahotel | `output/v4_complete/` | Genera sin errores |
| Comisión OTA visible | output diagnostico | $5,400,000 aparece |
| Evidence tier | output diagnostico YAML | Tier C |
| Valor central | output diagnostico | $2,610,000 |
| Pesos normalizados | output diagnostico | Suma ~100% |
| Suite completa | `tests/` | 0 failures |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/ -x -q 2>&1 | tail -30
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Restricciones

- Esta fase toca `main.py` en zonas específicas. NO refactorizar main.py más allá de lo necesario
- Los bloques de construcción de Scenario (con/optimistic) siguen teniendo monthly_loss_max como TECHO del rango — NO eliminarlo
- Si el end-to-end falla, debuggear y fixear antes de marcar como completa
- La ejecución de v4complete puede requerir conexión a internet (scraping real)

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`** — Marcar FASE-G como ✅ Completada
2. **`06-checklist-implementacion.md`** — Marcar FASE-G, proyecto completo
3. **`09-documentacion-post-proyecto.md`** — Completar todas las secciones
4. **Ejecutar**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-G \
    --desc "Integración main.py + validación end-to-end rediseño motor financiero" \
    --archivos-mod "main.py" \
    --tests "e2e" \
    --coherence 0.91 \
    --check-manual-docs
```
5. **Git commit**:
```bash
git add -A && git commit -m "Rediseño motor financiero: FinancialBreakdown + narrativa verificable + pesos normalizados + evidence tiers

- FASE-A: FinancialBreakdown dataclass + EvidenceTier enum
- FASE-B: ScenarioCalculator.calculate_breakdown() por capas
- FASE-C: Pesos normalizados (suma=100%) + DynamicImpactCalculator
- FASE-D: Scraper→ADR con WEB_SCRAPING como fuente
- FASE-E: 22 consumidores actualizados de max a central
- FASE-F: Template narrativa Comisión OTA + evidence tiers
- FASE-G: Integración main.py + validación end-to-end"
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] `main.py` construye FinancialBreakdown y lo pasa a generadores
- [ ] FinancialScenarios incluye `monthly_loss_central` en los 3 escenarios
- [ ] End-to-end ejecuta sin errores con Amaziliahotel
- [ ] Documento final cumple los 4 criterios de éxito (rastreable, proporcional, etiquetado, verificable)
- [ ] Valor central ($2.6M) no valor inflado ($3.1M)
- [ ] Comisión OTA ($5.4M) aparece como dato principal verificable
- [ ] Evidence tier visible en YAML header
- [ ] Suite de tests completa pasa (0 failures)
- [ ] `log_phase_completion.py` ejecutado
- [ ] Git commit realizado
