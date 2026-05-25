# FASE-A: Corregir Tabla de Escenarios (E1) + Recuperar Tabla Antes/Ahora (E2)

**ID**: FASE-A
**Objetivo**: Corregir los 2 errores críticos del diagnóstico: (E1) tabla de escenarios lógicamente invertida, (E2) tabla pedagógica "Antes vs Ahora" ausente.
**Dependencias**: Ninguna (fase inicial)
**Duración estimada**: 1-2 horas
**Skill**: `phased_project_executor`

---

## Contexto

El output de v4complete para Hotel Castilla Real (2026-05-25) fue validado contra `.opencode/context/Prospección.md`, revelando 2 errores críticos en el diagnóstico generado:

- **E1**: La tabla de "Escenarios de Recuperación" muestra Conservador ($7.2M) > Realista ($3.7M) = Optimista ($3.7M). La causa raíz es doble: (a) `scenario_calculator.py` calcula `monthly_loss_cop` donde conservador = mayor pérdida, pero (b) `_build_scenario_table_rows()` (L934-979 de `v4_diagnostic_generator.py`) presenta los valores como "Recuperación" con un clamp que duplica el realista para tapar el optimistic negativo.
- **E2**: La tabla "Antes (2023) vs Ahora (2026)" que existía en versiones anteriores del diagnóstico desapareció en la refactorización v6. Era el "momento ajá" donde el dueño entendía por qué su estrategia de hace 3 años ya no funciona.

El metadata del propio documento declara `financial_value_range: [2993356, 4490035]` con central 3741696 — estos valores existen pero no se usan en la tabla de escenarios.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| — | (fase inicial) |

### Base Técnica Disponible
- Archivos existentes: `modules/commercial_documents/v4_diagnostic_generator.py` (3107 líneas), `modules/commercial_documents/templates/diagnostico_v6_template.md` (206 líneas), `modules/financial_engine/scenario_calculator.py` (534 líneas)
- Tests base: 2743 funciones, 211 archivos
- Output referencia: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260525_150325.md`
- Documento validación: `.opencode/context/Prospección.md`

---

## Tareas

### Tarea 1: Investigar `_build_scenario_table_rows` y datos de entrada (E1)

**Objetivo**: Entender la cadena completa de datos: `scenario_calculator.py` → `FinancialScenarios` → `_build_scenario_table_rows()` → template.

**Archivos a investigar**:
- `modules/financial_engine/scenario_calculator.py` — método `calculate_scenarios()` y helpers `_calculate_conservative/realistic/optimistic_scenario()`
- `modules/commercial_documents/data_structures.py` — clase `FinancialScenarios` y clase `Scenario`
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scenario_table_rows()` (L934-979), `_build_financial_placeholders()` (L999-1101), `_prepare_financial_template_vars()`

**Criterios de aceptación**:
- [ ] Documentar por qué `conservative = 7,276,953` y `optimistic = -270,950` en los datos crudos
- [ ] Identificar dónde se pierde la semántica "pérdida" → "recuperación"
- [ ] Confirmar que `financial_value_range` está disponible en el metadata

### Tarea 2: Implementar fix de Tabla de Escenarios (E1)

**Objetivo**: Reemplazar la lógica actual de `_build_scenario_table_rows()` para usar directamente `financial_value_range` del metadata del escenario realista, mapeando:
- Conservador → `financial_value_min` ($2.993.356)
- Realista → `financial_value_central` ($3.741.696)
- Optimista → `financial_value_max` ($4.490.035)

Eliminar el clamp actual (L960-964: `if opt < 0: opt = 0; if opt < real: opt = real`).

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` L934-979 (`_build_scenario_table_rows`)
- `modules/commercial_documents/templates/diagnostico_v6_template.md` L129 (label de la tabla: "Escenarios de Recuperación" → mantener o ajustar)

**Criterios de aceptación**:
- [ ] Conservador < Realista < Optimista en orden de valor
- [ ] Valores coinciden con `financial_value_range` del metadata
- [ ] Probabilidades correctas: Conservador 70%, Realista 20%, Optimista 10%
- [ ] Sin clamp agresivo que duplique valores
- [ ] El optimistic NUNCA es negativo

### Tarea 3: Recuperar tabla "Antes (2023) vs Ahora (2026)" (E2)

**Objetivo**: Insertar en `diagnostico_v6_template.md`, Sección 1, ANTES de `${whatsapp_conflict_business_note}`:

```
| Antes (2023) | Ahora (2026) |
|---|---|
| Entran a Google y revisan 5 webs | Le preguntan a ChatGPT |
| Comparan en Booking | Esperan que la IA recomiende |
| Llaman o escriben por WhatsApp | Prefieren el primero que la IA menciona |
```

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` L28-32

**Criterios de aceptación**:
- [ ] Tabla visible en Sección 1, antes de la alerta de WhatsApp
- [ ] Formato markdown correcto (3 filas, 2 columnas)
- [ ] No rompe el resto del template (variables `${...}` intactas)

### Tarea 4: Verificar fixes con tests existentes

**Objetivo**: Ejecutar tests relacionados para confirmar que los cambios no introducen regresiones.

**Comandos**:
```bash
pytest tests/commercial_documents/test_fase_f_financial_placeholders.py -v
pytest tests/financial_engine/test_calculator_v2.py -v
python scripts/run_all_validations.py --quick
```

**Criterios de aceptación**:
- [ ] `test_fase_f_financial_placeholders.py` pasa (o se actualiza si es necesario)
- [ ] `test_calculator_v2.py` pasa
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_scenario_table_rows_format` | `tests/commercial_documents/test_fase_f_financial_placeholders.py` | 3 filas con Conservador < Realista < Optimista |
| `test_calculator_v2.py` | `tests/financial_engine/test_calculator_v2.py` | Sin regresiones |
| `run_all_validations.py --quick` | `scripts/run_all_validations.py` | 4/4 checks |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada, actualizar fecha
2. **`06-checklist-implementacion.md`**: Marcar items E1 y E2 como completados
3. **`09-documentacion-post-proyecto.md`**: Agregar módulos modificados en Sección A, funcionalidades en Sección B, métricas en Sección D, archivos en Sección E
4. **`evidence/fase-A/`**: Si hay screenshots o outputs de prueba, guardarlos

Ejecutar:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-A \
    --desc "Fix E1 (tabla escenarios usa financial_value_range) + E2 (tabla Antes/Ahora en template v6)" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
    --tests "0" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] E1: `_build_scenario_table_rows()` corregido — Conservador < Realista < Optimista
- [ ] E1: Clamp eliminado, valores vienen de `financial_value_range`
- [ ] E2: Tabla "Antes vs Ahora" insertada en template v6 Sección 1
- [ ] Tests existentes pasan sin regresiones
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `dependencias-fases.md` actualizado
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado

---

## Restricciones

- NO modificar `scenario_calculator.py` — el fix es en la capa de presentación, no en el motor financiero
- NO modificar otros templates (propuesta_v6, etc.)
- NO ejecutar v4complete — solo tests unitarios
- Máximo 60 iteraciones de agente
