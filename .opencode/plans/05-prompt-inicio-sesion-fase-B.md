# FASE-B: Corregir etiquetado "Comision OTA" en diagnostico

**ID**: FASE-B
**Objetivo**: Corregir el etiquetado incorrecto en el diagnostico que presenta monthly_loss_central como "Comision OTA Actual" cuando en realidad es un costo de oportunidad mensual que combina multiples factores.
**Dependencias**: Ninguna (independiente de FASE-A)
**Duracion estimada**: 1-1.5 horas
**Skill**: phased_project_executor v2.4.0

---

## Contexto

El Veredicto forense (Hallazgo 5) confirmo que el diagnostico presenta $2,610,000 como "Comision OTA Actual (verificable)" cuando en realidad es `monthly_loss_central` del escenario realista. Este valor NO es la comision OTA pura ($5,400,000 = `monthly_ota_commission_cop`). Es un costo de oportunidad que combina perdida por comisiones OTA + falta de visibilidad IA + dependencia de canales.

**Cadena de error**:
1. `scenario_calculator.calculate_breakdown()` (linea 395-435) calcula correctamente `monthly_ota_commission_cop`
2. `calculator_v2.calculate_scenarios()` genera `FinancialScenario.monthly_loss_cop` (costo de oportunidad total)
3. `v4_diagnostic_generator._build_financial_placeholders()` (linea 733-753) usa `monthly_loss_central` como base_value
4. Linea 753: `ota_commission = format_cop(base_value)` ← ERROR: etiqueta monthly_loss como "ota_commission"
5. `_build_financial_title_label()` (linea 705-718) retorna labels enganosos

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | Pendiente o Completada (independiente) |

### Base Tecnica Disponible
- Diagnostic generator: `modules/commercial_documents/v4_diagnostic_generator.py`
- Template: `modules/commercial_documents/templates/diagnostico_v6_template.md`
- Financial engine: `modules/financial_engine/scenario_calculator.py`
- Tests base: 2224 funciones

---

## Tareas

### Tarea 1: Corregir labels en _build_financial_title_label()

**Objetivo**: Cambiar los labels para que reflejen correctamente el concepto que se muestra.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`

**Pasos**:
1. Leer `_build_financial_title_label()` (linea 705-718)
2. Cambiar labels:
   - "Comision OTA Actual (verificable)" → "Perdida Mensual Estimada (verificable)"
   - "Comision OTA Estimada" → "Perdida Mensual Estimada"
3. Si se prefiere mostrar la comision OTA real, agregar campo nuevo usando `financial_breakdown.monthly_ota_commission_cop`
4. Opcion recomendada: Agregar AMBOS valores:
   - "Comision OTA Real: $5,400,000" (desde breakdown)
   - "Costo de Oportunidad Mensual: $2,610,000" (desde escenario)

**Criterios de aceptacion**:
- [ ] Labels reflejan correctamente el dato que muestran
- [ ] Si se muestra monthly_loss, el label dice "Perdida Mensual" o "Costo de Oportunidad"
- [ ] Si se muestra ota_commission, el valor viene de `monthly_ota_commission_cop`
- [ ] Backward compatible: variables del template siguen funcionando

### Tarea 2: Corregir _build_financial_placeholders() para usar valor correcto

**Objetivo**: Las variables del placeholder deben corresponder al concepto correcto.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (lineas 733-780)

**Pasos**:
1. Linea 733-734: `main = scenarios.get_main_scenario()`, `base_value = monthly_loss_central`
2. Linea 753: Si el label es "Comision OTA", usar `financial_breakdown.monthly_ota_commission_cop` en lugar de `base_value`
3. Agregar campo nuevo para costo de oportunidad si no existe: `opportunity_cost_formatted`
4. Renombrar variables internas:
   - `ota_commission_formatted` → `opportunity_cost_formatted` (si el valor es monthly_loss)
   - O crear `ota_commission_real_formatted` (si se usa el valor del breakdown)
5. Linea 774-780: Actualizar return dict con nombres correctos

**Criterios de aceptacion**:
- [ ] `ota_commission_formatted` contiene la comision OTA real (de breakdown)
- [ ] Si se agrega `opportunity_cost_formatted`, contiene monthly_loss
- [ ] El return dict del placeholder tiene nombres semanticos correctos
- [ ] Los datos financieros no cambian, solo los labels y asignaciones

### Tarea 3: Actualizar template del diagnostico si es necesario

**Objetivo**: Asegurar que el template usa las variables correctas con los labels correctos.

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (lineas 71-77)

**Pasos**:
1. Verificar si el template usa `${financial_title_label}` y `${ota_commission_formatted}`
2. Si se agregan campos nuevos, agregarlos al template
3. Asegurar que el output final del diagnostico sea claro para el cliente

**Criterios de aceptacion**:
- [ ] Template usa variables con nombres correctos
- [ ] Si se agregan campos nuevos, el template los renderiza

### Tarea 4: Tests de regresion

**Objetivo**: Verificar tests existentes y agregar tests nuevos.

**Archivos afectados**:
- `tests/commercial_documents/test_fase_f_financial_placeholders.py`
- `tests/commercial_documents/test_diagnostic_brechas.py`

**Pasos**:
1. Ejecutar: `pytest tests/commercial_documents/ -v --timeout=60`
2. Actualizar `test_fase_f_financial_placeholders.py` si los nombres de campos cambiaron
3. Agregar test: "ota_commission_formatted usa valor de breakdown, no monthly_loss"
4. Agregar test: "labels financieros son semanticamente correctos"
5. Ejecutar tests de publication gates

**Criterios de aceptacion**:
- [ ] Todos los tests existentes pasan (0 regresiones)
- [ ] Al menos 2 tests nuevos para la correccion
- [ ] `pytest tests/commercial_documents/ tests/quality_gates/ -v` pasa 100%

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| test_fase_f_financial_placeholders.py | tests/commercial_documents/ | Labels correctos, valores correctos |
| test_diagnostic_brechas.py | tests/commercial_documents/ | Pasa sin regresion |
| test_no_defaults_source_aware.py | tests/financial_engine/ | Fuentes financieras correctas |
| test_publication_gates.py | tests/quality_gates/ | Gates pasan |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/financial_engine/test_no_defaults_source_aware.py tests/quality_gates/test_publication_gates.py -v --timeout=60
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-B como Completada con fecha
2. **`README.md` del plan**: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Seccion A (modulos), D (metricas), E (archivos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Tests de labels correctos ejecutan exitosamente
- [ ] **Tests existentes sin regresion**: `pytest tests/commercial_documents/ -v` 100%
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-B marcada como completada
- [ ] **Documentacion afiliada**: CHANGELOG.md, GUIA_TECNICA.md actualizados
- [ ] **Post-ejecucion completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO modificar `scenario_calculator.py` (los calculos ya son correctos)
- NO cambiar valores financieros, solo labels y asignaciones
- NO afectar la logica de escenarios financieros
- Mantener backward compatibility en el return dict (campos antiguos siguen existiendo)
- Maximo 60 iteraciones del agente en esta fase

---

## Prompt de Ejecucion

```
Actua como desarrollador senior de iah-cli.

OBJETIVO: Corregir el etiquetado del diagnostico que presenta $2,610,000 (monthly_loss_central) como "Comision OTA Actual" cuando la comision OTA real es $5,400,000 (monthly_ota_commission_cop del breakdown).

CONTEXTO:
- _build_financial_placeholders() linea 733-753 usa monthly_loss_central como base_value
- Linea 753 asigna base_value a ota_commission_formatted (etiqueta incorrecta)
- _build_financial_title_label() linea 705-718 genera labels enganosos
- financial_breakdown.monthly_ota_commission_cop tiene el valor correcto de comision OTA

TAREAS:
1. Corregir labels en _build_financial_title_label() para reflejar el concepto real
2. Corregir _build_financial_placeholders() para usar valor correcto segun label
3. Actualizar template si los nombres de variables cambian
4. Actualizar tests (especialmente test_fase_f_financial_placeholders.py)

CRITERIOS:
- Labels semanticamente correctos (no decir "Comision OTA" si es "Perdida Mensual")
- Valores corresponden a lo que el label indica
- 0 regresiones en tests existentes
- Backward compatible

VALIDACIONES:
- pytest tests/commercial_documents/ tests/financial_engine/ tests/quality_gates/ -v
- run_all_validations.py --quick
```
