# FASE-PROP-C: Proyecciones Financieras Transparentes

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~45 iteraciones
**Dependencias:** FASE-PROP-B ✅ (ideal)
**Fase siguiente:** FASE-PROP-D

## Contexto

El código aplica **dos descuentos** de forma inconsistente:

1. **Tabla mensual** (`v4_proposal_generator.py:645-656`): usa `projected_monthly_gain = raw_loss × pain_ratio` SIN `recovery_factor`
   - Ejemplo Hotelcastillareal: $3,741,696 × 0.4082 = $1,527,360/mes → neto $327,360/mes
2. **ROI** (`v4_proposal_generator.py:1050-1073`): aplica `recovery_factor` ADEMÁS de `pain_ratio`
   - total_gain = gain × recovery_factor × months → ROI = 0.3X

El cliente ve: "gano $327K/mes netos" en la tabla, pero el ROI de 0.3X contradice eso implícitamente. La `pain_ratio_note` (L623-626) es genérica y no explica el doble descuento.

**Decisión de diseño**: Se elige **Opción B** (mínima viable): reescribir `pain_ratio_note` para explicar AMBOS descuentos explícitamente, en lugar de refactorizar todo el pricing model (Opción A sería demasiado grande para una fase).

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |

## Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` (L591-656): cálculo de proyección mensual
- `modules/commercial_documents/v4_proposal_generator.py` (L1050-1073): `_calculate_roi()`
- `modules/commercial_documents/v4_proposal_generator.py` (L623-626): `pain_ratio_note`
- `modules/commercial_documents/templates/propuesta_v6_template.md`: render de la nota

## Tareas Específicas

### Tarea 1: Reescribir pain_ratio_note para explicar ambos descuentos
**Objetivo**: La nota financiera debe explicar claramente que hay DOS factores: pain_ratio (qué % de la pérdida es recuperable) y recovery_factor (qué % de eso se recupera en el período).

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (L623-626)

**Criterios de aceptación**:
- [ ] `pain_ratio_note` menciona ambos factores por nombre
- [ ] Incluye ejemplo numérico con valores reales del hotel (usar placeholders si es genérico)
- [ ] El lenguaje es honesto: "proyección conservadora", no promesas

Ejemplo de texto objetivo:
```
> **Nota de proyección**: De su pérdida mensual estimada, el {pain_ratio}% 
> representa la porción que consideramos recuperable con IAO. 
> De ese monto, proyectamos recuperar el {recovery_factor}% en los 
> próximos 6 meses. El ROI refleja esta proyección conservadora.
```

### Tarea 2: Verificar que el template renderice la nota en posición visible
**Objetivo**: La nota no debe quedar en letra pequeña o al final del documento.

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Criterios de aceptación**:
- [ ] Identificar dónde se renderiza `${pain_ratio_note}` (o equivalente) en el template
- [ ] Asegurar que esté cerca de la tabla de proyección mensual (no al final del documento)
- [ ] Si el template no tiene variable para la nota, agregarla en la sección financiera

### Tarea 3: Asegurar consistencia numérica tabla vs ROI
**Objetivo**: Aunque no se unifiquen los algoritmos (eso es Opción A), al menos la nota debe hacer explícita la relación.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (L591-656 y L1050-1073)

**Criterios de aceptación**:
- [ ] La nota explica por qué la tabla muestra X y el ROI muestra Y
- [ ] No se modifica la fórmula matemática de la tabla ni del ROI (para no introducir bugs de cálculo)
- [ ] Documentar en comentarios que la Opción A (unificación de algoritmos) queda como deuda técnica futura

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test pain_ratio_note | `tests/commercial_documents/test_proposal_generator.py` | La nota generada contiene "pain_ratio" y "recovery_factor" |
| Test consistencia | (mismo archivo) | Valores de tabla y ROI corresponden a las fórmulas existentes (no se introducen discrepancias nuevas) |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v -k pain_ratio
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Líneas Aprox. |
|---------|---------------|--------------|
| `modules/commercial_documents/v4_proposal_generator.py` | Modificación | L623-626 (pain_ratio_note), L591-656, L1050-1073 (referencia) |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Modificación | Posición de nota financiera |

## Criterios de Completitud (CHECKLIST)

- [x] **Nota reescrita**: Menciona pain_ratio y recovery_factor explícitamente
- [x] **Posición visible**: La nota aparece cerca de la tabla mensual
- [x] **Consistencia**: Tabla y ROI mantienen sus fórmulas originales (no se rompen cálculos)
- [x] **Honestidad**: El lenguaje es conservador, no promete ganancias seguras
- [x] **Tests pasan**: Tests nuevos/existentes pasan
- [x] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4

## Restricciones

- **NO modificar** las fórmulas de `projected_monthly_gain` ni `_calculate_roi()` — solo la nota explicativa
- **NO implementar** Opción A (effective_recovery único) — queda fuera de scope, documentar como deuda técnica
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar FASE-PROP-C como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar tareas completadas
3. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-C \
       --desc "Proyecciones financieras transparentes: pain_ratio_note explica ambos descuentos" \
       --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
       --tests "2" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-D.md siguiendo .agents/workflows/phased_project_executor.md
```
