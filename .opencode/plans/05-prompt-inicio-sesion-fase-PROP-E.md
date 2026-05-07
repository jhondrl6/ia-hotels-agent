# FASE-PROP-E: SEO/AEO — Plan Específico por Score

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~43 iteraciones
**Dependencias:** FASE-PROP-F ✅ (ideal)
**Fase siguiente:** FASE-PROP-G

## Contexto

Scores del diagnóstico para Hotelcastillareal:
- SEO Local: 25/100
- AEO: 0/100
- GEO: 70/100
- IAO: 35/100

La propuesta menciona:
- SEO Local: 1 línea genérica ("Semana 3: optimización basada en análisis técnico")
- AEO: CERO menciones
- Schema de Hotel: plan detallado con asset específico

**Objetivo**: El plan de 7/30/60/90 días priorice dinámicamente los pilares con score < 30, y AEO=0 se conecte con los assets FAQ + Open Graph que YA se generan.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-PROP-A | ✅ Completada |
| FASE-PROP-B | ✅ Completada |
| FASE-PROP-C | ✅ Completada |
| FASE-PROP-D | ✅ Completada |
| FASE-PROP-F | ✅ Completada |

## Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py`: `_build_7_day_plan()`, `_build_30_day_plan()`
- `modules/commercial_documents/templates/propuesta_v6_template.md`: tabla de entregables
- Assets existentes: FAQ Generator, Open Graph optimizer

## Tareas Específicas

### Tarea 1: Agregar lógica de priorización por score
**Objetivo**: Si un pilar tiene score < 30, incluir acción específica en quick wins.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py` (`_build_7_day_plan`, `_build_30_day_plan`)

**Criterios de aceptación**:
- [ ] Lógica: `if pilar_score < 30: incluir_en_quick_wins = True`
- [ ] Para SEO Local (25): acción específica en 7-day plan (ej. "Auditar y optimizar perfil GBP")
- [ ] Para AEO (0): acción específica en 7-day plan (ej. "Implementar Schema FAQ")
- [ ] Para IAO (35): acción en 30-day plan si aplica

### Tarea 2: Conectar AEO=0 con FAQ + Open Graph
**Objetivo**: La propuesta mencione que AEO se construye sobre assets ya incluidos.

**Archivos afectados**:
- `modules/commercial_documents/v4_proposal_generator.py`
- `modules/commercial_documents/templates/propuesta_v6_template.md`

**Criterios de aceptación**:
- [ ] En sección de AEO (o en nota general): "AEO se construye sobre Schema FAQ + Open Graph — ambos incluidos en su kit"
- [ ] No requiere nuevos assets, solo mencionar los existentes

### Tarea 3: Asegurar tabla de Estado de Entregables
**Objetivo**: La tabla mencione SEO Local y AEO como líneas.

**Archivos afectados**:
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/commercial_documents/v4_proposal_generator.py` (datos de la tabla)

**Criterios de aceptación**:
- [ ] Tabla de "Estado de Entregables" incluye fila para SEO Local
- [ ] Tabla incluye fila para AEO (aunque sea "Prerequisite: Schema FAQ")
- [ ] No duplicar filas que ya existen

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test plan priorización | `tests/commercial_documents/test_proposal_generator.py` | Con scores bajos, 7-day plan incluye acciones específicas |
| Test AEO mencionado | (mismo archivo) | Propuesta generada contiene "AEO" o "Answer Engine" al menos 1 vez |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_proposal_generator.py -v -k seo_aeo
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Notas |
|---------|---------------|-------|
| `modules/commercial_documents/v4_proposal_generator.py` | Modificación | `_build_7_day_plan`, `_build_30_day_plan` |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Modificación | Tabla de entregables + nota AEO |

## Criterios de Completitud (CHECKLIST)

- [x] **Priorización dinámica**: Score < 30 → acción específica en plan
- [x] **AEO mencionado**: La propuesta no ignora AEO=0
- [x] **Tabla completa**: Estado de Entregables incluye SEO Local y AEO
- [x] **Tests pasan**: Tests nuevos/existentes pasan (23/23)
- [x] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4

**Completada:** 2026-05-06
**Iteraciones utilizadas:** ~15

## Restricciones

- **NO crear** nuevos assets — solo conectar con los existentes
- **NO modificar** los scores del diagnóstico — solo cómo se usan en la propuesta
- **Máximo 60 iteraciones** (R2)

## Post-Ejecución (OBLIGATORIO)

1. **Actualizar `dependencias-fases.md`**: marcar FASE-PROP-E como ✅
2. **Actualizar `06-checklist-implementacion.md`**: marcar tareas completadas
3. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-E \
       --desc "SEO/AEO plan especifico: priorizar pilares con score<30, conectar AEO con assets existentes" \
       --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/templates/propuesta_v6_template.md" \
       --tests "2" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-G.md siguiendo .agents/workflows/phased_project_executor.md
```
