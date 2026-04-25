# FASE-B: Correccion Financiera Critica

**ID**: FASE-B
**Objetivo**: Corregir escenarios financieros invertidos, ROI irreal de 20X, y aplicar pain_ratio a la proyeccion de recuperacion. Garantizar que los numeros presentados al cliente sean creibles.
**Dependencias**: FASE-A completada (catalogos alineados, tests verdes)
**Duracion estimada**: 2 - 3 horas
**Skill**: test-driven-development, systematic-debugging

---

## Contexto

El modulo financiero presenta inconsistencias internas que generan propuestas con numeros no creibles. Esta fase se enfoca exclusivamente en `modules/financial_engine/` sin tocar generacion de propuestas (eso viene en FASE-C).

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-RELEASE-4.35.0 | Completada |
| FASE-A | En progreso / Completada |

### Base Tecnica Disponible
- Archivos existentes: `modules/financial_engine/calculator_v2.py`, `modules/financial_engine/pricing_resolution_wrapper.py`, `modules/financial_engine/harness_handlers.py`
- Tests base: Tests de financial_engine (verificar cuantos al iniciar)
- Datos de referencia: `output/v4_complete/financial_scenarios.json` (ejemplo con valores invertidos)

---

## Tareas

### Tarea 1: Corregir orden de escenarios financieros
**Objetivo**: Garantizar optimistic > realistic > conservative SIEMPRE.

**Archivos afectados**:
- `modules/financial_engine/calculator_v2.py`

**Criterios de aceptacion**:
- [ ] Identificar `_get_main_value()` y verificar que extrae el valor correcto por escenario
- [ ] Los 3 escenarios respetan: conservative <= realistic <= optimistic
- [ ] Optimistic nunca es negativo
- [ ] Agregar assertion interna (no expuesta al cliente) que valide el orden
- [ ] Ejecutar tests de calculator_v2 -> todos PASS

### Tarea 2: Aplicar recovery_factor al ROI
**Objetivo**: Eliminar el ROI de 20X irreal. La recuperacion no es 100%.

**Archivos afectados**:
- `modules/financial_engine/calculator_v2.py` o `modules/commercial_documents/v4_proposal_generator.py`

**Criterios de aceptacion**:
- [ ] Definir recovery_factor: conservador 0.15, realista 0.20, optimista 0.25
- [ ] Formula corregida: `roi = (monthly_loss * recovery_factor * meses) / (monthly_price * meses)`
- [ ] `_calculate_roi()` usa el recovery_factor segun el escenario
- [ ] ROI maximo realista <= 5.0X (umbral de credibilidad)
- [ ] La propuesta muestra 3 escenarios de ROI (conservador/realista/optimista)

### Tarea 3: Aplicar pain_ratio a la proyeccion de recuperacion
**Objetivo**: Resolver D-2 (pain_ratio 5% vs recuperacion 100%).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (seccion de proyeccion)

**Criterios de aceptacion**:
- [ ] Si `pain_ratio` esta disponible en `pricing`, usarlo para ajustar `projected_gain`
- [ ] Si no esta disponible, usar default 0.20 (20%)
- [ ] La proyeccion mensual muestra: `perdida estimada * pain_ratio = recuperacion esperada`
- [ ] NO mostrar recuperacion 100% de la perdida mensual

### Tarea 4: Disclaimer explicito para datos hardcodeados/Tier C
**Objetivo**: Resolver D-3 (ADR hardcodeado $300K).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (variables de template)

**Criterios de aceptacion**:
- [ ] Si `evidence_tier` es "C" o `data_sources` contiene "default" o "legacy_hardcode", agregar disclaimer visible
- [ ] Disclaimer ejemplo: "Proyeccion basada en ADR estimado ($300K) y ocupacion promedio sectorial. Los valores reales requieren validacion con datos del hotel."
- [ ] El disclaimer aparece en la seccion financiera de la propuesta

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Tests calculator_v2 | `tests/financial_engine/test_calculator_v2.py` | Todos PASS |
| Tests escenarios | Verificar existencia | Orden correcto de escenarios |

**Comando de validacion**:
```bash
venv/Scripts/python.exe -m pytest tests/financial_engine/ -v --tb=short
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`.opencode/plans/06-checklist-implementacion.md`**
   - Marcar FASE-B como Completada

2. **`09-documentacion-post-proyecto.md`**
   - Seccion A: Archivos modificados (calculator_v2.py, v4_proposal_generator.py)
   - Seccion D: Metricas financieras validadas

3. **REGISTRY.md**:
```bash
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-B --desc "Correccion financiera: escenarios ordenados, recovery_factor en ROI, pain_ratio aplicado, disclaimer Tier C" --archivos-mod "modules/financial_engine/calculator_v2.py,modules/commercial_documents/v4_proposal_generator.py" --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] Tests financieros pasan: Todos los tests de financial_engine ejecutan exitosamente
- [ ] Validaciones del proyecto: `scripts/run_all_validations.py --quick` pasa 4/4
- [ ] `06-checklist-implementacion.md` actualizado
- [ ] Documentacion afiliada: REGISTRY.md actualizado via log_phase_completion.py
- [ ] Post-ejecucion completada

---

## Restricciones

- NO modificar estructura de datos de entrada (ADR, rooms, occupancy se siguen leyendo igual)
- NO cambiar pricing defaults (monthly_price_cop)
- NO ejecutar v4complete en esta fase (optimizacion de costos API)
