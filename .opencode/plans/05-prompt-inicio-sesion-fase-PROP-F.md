# FASE-PROP-F: Tier C — Advertencia en Propuesta

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~38 iteraciones
**Dependencias:** FASE-PROP-D ✅ (ideal)
**Fase siguiente:** FASE-PROP-E

## Contexto

El diagnóstico SÍ advierte `financial_evidence_tier: "C"` en el YAML header (L8). Pero:
- `grep -n "precision_tier\|evidence_tier\|financial_evidence" v4_proposal_generator.py` → **0 resultados**
- El template `propuesta_v6_template.md` no tiene variable para mostrar el tier

**Objetivo**: El cliente sabe que las proyecciones usan benchmarks regionales (Tier C) y que la precisión mejora con onboarding.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |
| FASE-PROP-C | ✅ Completada |
| FASE-PROP-D | ✅ Completada |

## Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` (`_prepare_template_data()`)
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `financial_scenarios.json`: campo `precision_tier`

## Tareas Específicas

### Tarea 1: Agregar financial_evidence_tier al dict de template data
**Objetivo**: `_prepare_template_data()` incluya el tier.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`

**Criterios de aceptación**:
- [ ] `financial_evidence_tier` se extrae de `financial_scenarios.precision_tier` (fallback: "C")
- [ ] Se agrega al dict que se pasa al template

### Tarea 2: Agregar bloque de advertencia en propuesta_v6_template.md
**Objetivo**: Template renderice banner para Tier C, nota sutil para A/B.

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Criterios de aceptación**:
- [ ] Bloque condicional: `{{if financial_evidence_tier == "C"}}` → banner ⚠️ visible
- [ ] Texto del banner: "Nivel de evidencia: Tier C. Estas proyecciones usan benchmarks regionales. Para precisión exacta, ejecute el onboarding con datos reales."
- [ ] Para Tier A/B: nota sutil en pie de página o sección financiera

### Tarea 3: Diferenciar visualmente Tier C vs A/B
**Objetivo**: El template use estilos/markdown distintos según tier.

**Criterios de aceptación**:
- [ ] Tier C: blockquote con ⚠️ o banner `> **⚠️ Advertencia:** ...`
- [ ] Tier A/B: nota en itálica o pie de tabla
- [ ] No romper formato existente para tiers no especificados

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test Tier C | `tests/commercial_documents/test_proposal_generator.py` | Template data incluye financial_evidence_tier="C" |
| Test Tier A | (mismo archivo) | Con Tier A, no aparece banner de advertencia |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v -k tier
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Notas |
|---------|---------------|-------|
| `modules/commercial_documents/v4_proposal_generator.py` | Modificación | `_prepare_template_data()` agrega tier |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Modificación | Banner/nota condicional |

## Criterios de Completitud (CHECKLIST)

- [ ] **Tier en template data**: `_prepare_template_data()` pasa el valor
- [ ] **Banner Tier C**: Visible y claro en template
- [ ] **A/B diferenciado**: No muestra banner alarmista para A/B
- [ ] **Tests pasan**: Tests nuevos/existentes pasan
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4

## Restricciones

- **NO modificar** la lógica de asignación de tier — solo su presentación
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar FASE-PROP-F como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar tareas completadas
3. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-F \
       --desc "Tier C advertencia: mostrar banner en propuesta cuando precision_tier=C" \
       --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
       --tests "2" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-G.md siguiendo .agents/workflows/phased_project_executor.md
```
