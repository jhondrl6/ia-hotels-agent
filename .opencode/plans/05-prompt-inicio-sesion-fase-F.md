# FASE-F: Phantom Cost Fix + Dead Code Removal

**ID**: FASE-F
**Objetivo**: Eliminar el bug crítico de costos fantasma (brechas inexistentes con valores COP reales) y remover código muerto de distribución fija 40/30/20/10
**Dependencias**: Ninguna (primera fase del proyecto)
**Duración estimada**: 2-3 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema Detectado

El generador de propuestas (`v4_proposal_generator.py`) usa una distribución fija 40/30/20/10 sobre `monthly_loss_max` para calcular el costo de cada brecha. Cuando existen menos de 4 problemas reales, las brechas faltantes muestran placeholders ("Tercer problema", "Cuarto problema") con valores COP no-cero, atribuyendo pérdidas ficticias al cliente.

**Ejemplo del bug**: Si solo hay 1 brecha real de $10M COP, el sistema muestra:
- Brecha 1: $4M COP (real)
- Brecha 2: $3M COP ("Segundo problema" → FICTICIO)
- Brecha 3: $2M COP ("Tercer problema" → FICTICIO)
- Brecha 4: $1M COP ("Cuarto problema" → FICTICIO)

El cliente ve $6M COP de pérdidas que no existen.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-F (esta) | 🔲 Pendiente |

### Base Técnica Disponible
- Archivo principal: `modules/commercial_documents/v4_proposal_generator.py`
- Template V6: `modules/commercial_documents/templates/propuesta_v6_template.md` — NO usa brechas
- Template V4: `modules/commercial_documents/templates/propuesta_v4_template.md` — SÍ usa brecha_1..4
- Tests existentes: `tests/test_proposal_alignment.py`
- `diagnostic_summary.top_problems: List[str]` — fuente actual de nombres
- `audit_result: Optional[Any]` — disponible pero NO se usa para brechas

---

## Tareas

### Tarea 1: Eliminar distribución fija y código muerto

**Objetivo**: Reemplazar la distribución fija 40/30/20/10 con lógica que respete la cantidad real de problemas

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (líneas 538-546)

**Código actual** (ELIMINAR):
```python
# Líneas 538-546 — DISTRIBUCIÓN FIJA (el gap)
'brecha_1_nombre': diagnostic_summary.top_problems[0] if len(diagnostic_summary.top_problems) > 0 else "Problema no identificado",
'brecha_1_costo': format_cop(int(main_scenario.monthly_loss_max * 0.4)),
'brecha_2_nombre': diagnostic_summary.top_problems[1] if len(diagnostic_summary.top_problems) > 1 else "Segundo problema",
'brecha_2_costo': format_cop(int(main_scenario.monthly_loss_max * 0.3)),
'brecha_3_nombre': diagnostic_summary.top_problems[2] if len(diagnostic_summary.top_problems) > 2 else "Tercer problema",
'brecha_3_costo': format_cop(int(main_scenario.monthly_loss_max * 0.2)),
'brecha_4_nombre': diagnostic_summary.top_problems[3] if len(diagnostic_summary.top_problems) > 3 else "Cuarto problema",
'brecha_4_costo': format_cop(int(main_scenario.monthly_loss_max * 0.1)),
```

**Código nuevo** (REEMPLAZAR CON):
```python
# Brecha variables — dinámicas, zero para slots sin problema real
# Las brechas consumen top_problems (V4 compat) con guard contra phantom costs
top_problems = diagnostic_summary.top_problems or []
max_brechas = 4
brecha_data = {}
for i in range(max_brechas):
    slot = i + 1
    if i < len(top_problems) and top_problems[i]:
        brecha_data[f'brecha_{slot}_nombre'] = top_problems[i]
        # Distribución proporcional: divide pérdida entre las brechas reales
        brecha_data[f'brecha_{slot}_costo'] = format_cop(
            int(main_scenario.monthly_loss_max / max(len(top_problems), 1))
        )
    else:
        brecha_data[f'brecha_{slot}_nombre'] = ""
        brecha_data[f'brecha_{slot}_costo'] = "$0"
```

**Nota sobre distribución**: La distribución equitativa (`len / max`) es un placeholder temporal. FASE-G conectará los impactos reales desde `_identify_brechas()`. Lo importante aquí es que:
1. No haya phantom costs
2. Los slots vacíos muestren "$0" y nombre vacío
3. top_problems None-safe

**Criterios de aceptación**:
- [ ] Si hay 1 problema: solo brecha_1 tiene costo no-cero; brechas 2-4 = "$0"
- [ ] Si hay 0 problemas: todas las brechas = "$0", nombre = ""
- [ ] Si top_problems es None: no TypeError (guard con `or []`)
- [ ] Template V6 generado exitosamente (no usa estas variables, pero no debe romper)
- [ ] Template V4 generado exitosamente (SÍ usa estas variables, debe mostrar correctly)

### Tarea 2: Tests de regresión para phantom cost fix

**Objetivo**: Garantizar que el fix no rompe el comportamiento correcto y elimina los phantom costs

**Archivos afectados**:
- `tests/test_proposal_alignment.py` (agregar tests nuevos)

**Tests a crear**:

1. `test_no_phantom_costs_with_one_problem`: Con 1 top_problem, brechas 2-4 deben tener "$0"
2. `test_no_phantom_costs_with_zero_problems`: Con 0 top_problems, todas las brechas = "$0"
3. `test_no_phantom_costs_with_none_problems`: Con top_problems=None, no TypeError, todas = "$0"
4. `test_costs_distributed_when_4_problems`: Con 4 problemas, todos tienen costo no-cero
5. `test_empty_name_for_missing_brechas`: Slots sin problema tienen nombre vacío, no placeholder genérico

**Criterios de aceptación**:
- [ ] 5 tests nuevos pasando
- [ ] Tests existentes en `test_proposal_alignment.py` siguen pasando (0 regresiones)

### Tarea 3: Guard contra None en top_problems

**Objetivo**: Agregar validación defensiva en `_prepare_template_data`

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Criterios de aceptación**:
- [ ] `diagnostic_summary.top_problems` puede ser None sin crash
- [ ] No se asume que siempre hay exactamente 4 problemas

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_no_phantom_costs_with_one_problem` | `tests/test_proposal_alignment.py` | brechas 2-4 = "$0" |
| `test_no_phantom_costs_with_zero_problems` | `tests/test_proposal_alignment.py` | todas = "$0" |
| `test_no_phantom_costs_with_none_problems` | `tests/test_proposal_alignment.py` | sin TypeError |
| `test_costs_distributed_when_4_problems` | `tests/test_proposal_alignment.py` | 4 costos no-cero |
| `test_empty_name_for_missing_brechas` | `tests/test_proposal_alignment.py` | nombres = "" |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_proposal_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-F como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-F como ✅
3. **`09-documentacion-post-proyecto.md`**: Sección A (módulos), D (métricas), E (archivos)
4. **`scripts/log_phase_completion.py`**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-F \
    --desc "Phantom cost fix + dead code removal in proposal generator" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py" \
    --tests "5" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 5/5 phantom cost tests exitosos
- [ ] **Tests existentes pasan**: 0 regresiones en suite completa
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa
- [ ] **Phantom costs eliminados**: Ninguna brecha sin problema muestra costo > $0
- [ ] **None-safe**: top_problems=None no causa TypeError
- [ ] **Post-ejecución completada**: dependencias, checklist, docs actualizados

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- NO modificar `v4_diagnostic_generator.py` (es responsabilidad de FASE-G/H)
- NO modificar `data_structures.py` (es responsabilidad de FASE-I)
- NO modificar template V6 (no usa brechas, no necesita cambios)
- Mantener compatibilidad con template V4 (usa brecha_1..4)
- Preservar firma de `_prepare_template_data()` — solo cambiar implementación interna

---

## Prompt de Ejecución

```
Actúa como ingeniero Python senior especializado en bugs financieros.

OBJETIVO: Eliminar phantom costs del proposal generator v4.

CONTEXTO:
- v4_proposal_generator.py líneas 538-546 tienen distribución fija 40/30/20/10
- Bug: slots sin problema real muestran costos ficticios en COP
- Template V6 no usa estas variables (código muerto parcial)
- Template V4 SÍ las usa (debe seguir funcionando)

TAREAS:
1. Reemplazar líneas 538-546 con lógica dinámica que zeroee slots vacíos
2. Agregar guard contra top_problems=None
3. Crear 5 tests en test_proposal_alignment.py

CRITERIOS:
- 0 phantom costs cuando hay < 4 problemas
- 0 regresiones en tests existentes
- run_all_validations.py --quick pasa

VALIDACIONES:
- pytest tests/test_proposal_alignment.py -v
- pytest tests/ -k proposal -v
- python scripts/run_all_validations.py --quick
```
