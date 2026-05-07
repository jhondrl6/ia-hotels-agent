---
description: FASE-SOL2-D Phantom Fields & Coherence Consistency
version: 1.0.0
skill: phased_project_executor
---

# FASE-SOL2-D: Phantom Fields & Coherence Consistency

**ID**: FASE-SOL2-D  
**Objetivo**: Eliminar campos fantasma del pipeline y unificar la fuente de verdad del coherence score.  
**Dependencias**: FASE-SOL2-A, FASE-SOL2-B completadas. Puede ejecutarse en paralelo con FASE-SOL2-C.  
**Duración estimada**: 1.5-2 horas  
**Skill**: phased_project_executor, knowledge-doc-audit  

## Contexto

Durante la validación del contexto SOL-2 se identificaron campos que el documento asume existen pero que no se encuentran en el código, y discrepancias menores en reportes.

### GAP-G [ALTA]: Campos fantasma
El documento SOL-2 cita:
```json
{
  "site_verification_applied": false,
  "delivery_ready_percentage": 67.0
}
```
Como "no existen en código". Sin embargo, la ejecución v4complete de FASE-SOL2-C muestra que `asset_generation_report.json` SÍ tiene estos campos (`delivery_ready_percentage: 50.0`, `site_verification_applied: false`).

**Pregunta abierta**: ¿El contexto SOL-2 se refería a otros módulos? ¿Hay más campos fantasma en otros reportes (v4_audit, gate_report)?

### GAP-D [MEDIA]: Coherence score inconsistente
| Fuente | Score |
|--------|-------|
| coherence_validation.json | 0.89 |
| gate_report.json | 0.8911111111111112 |
| AGENTS.md | 0.84 (run diferente) |

Aunque son runs distintos, el sistema no tiene una "fuente única de verdad" para el coherence score canonico.

### GAP-E [BAJA]: Line range subestimado
Documento SOL-2 dice gate líneas 755-850, pero el método termina en 865.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SOL2-A | ✅ Completada |
| FASE-SOL2-B | ✅ Completada |
| FASE-SOL2-C | ✅ Completada (o en paralelo) |

## Tareas

### Tarea 1: Auditoría de campos fantasma
**Objetivo**: Verificar si existen campos hardcodeados/fantasma en reportes.

**Archivos a revisar**:
- `modules/asset_generation/asset_generation_report.py` (o quien genere asset_generation_report.json)
- `modules/quality_gates/publication_gates.py` (gate_report)
- `modules/orchestration_v4/v4_orchestrator.py` (v4_complete_report.json)
- Cualquier otro generador de JSONs de reporte

**Criterios de aceptación**:
- [ ] Buscar con `search_files` strings: `site_verification_applied`, `delivery_ready_percentage`, `67.0`
- [ ] Determinar si estos campos son calculados dinámicamente o hardcodeados
- [ ] Si son hardcodeados en algún módulo: eliminar o implementar cálculo real
- [ ] Si son válidos: actualizar contexto SOL-2 con la corrección

### Tarea 2: Unificar fuente de coherence score
**Objetivo**: Que coherence_validation.json y gate_report.json usen el mismo valor (misma función de cálculo).

**Archivos a revisar**:
- `modules/commercial_documents/coherence_validator.py`
- `modules/quality_gates/publication_gates.py`

**Criterios de aceptación**:
- [ ] Identificar si ambos módulos calculan el score independientemente
- [ ] Si sí: crear función compartida o hacer que uno consuma el otro
- [ ] Si no: documentar por qué difieren (redondeo, momentos distintos)
- [ ] Actualizar AGENTS.md para que cite el score como rango (≥ 0.8) en vez de valor fijo

### Tarea 3: Corregir documentación (line range)
**Objetivo**: Cerrar GAP-E.

**Archivos afectados**:
- `.opencode/context/05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md`
- `.opencode/plans/SOL-2-REFACTOR/05-prompt-inicio-sesion-fase-SOL2-B.md` (si referencia line ranges)

**Criterios de aceptación**:
- [ ] Line range del gate corregido a 755-865 (o líneas exactas actuales)
- [ ] Ningún otro line range obsoleto en documentación del plan

### Tarea 4: Validación
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

**Criterios**:
- [ ] 4/4 checks pasan
- [ ] No hay campos hardcodeados sin justificación

## Tests Obligatorios

| Test | Archivo | Criterio |
|------|---------|----------|
| test_report_fields | tests/ (nuevo o existente) | Campos reportados son calculados, no hardcodeados |
| test_coherence_source | tests/commercial_documents/test_coherence_validator.py | Score coincide con gate |

## Post-Ejecución (OBLIGATORIO)

1. `dependencias-fases.md`: FASE-SOL2-D ✅
2. `06-checklist-implementacion.md`: Estado ✅
3. `09-documentacion-post-proyecto.md`: Sección E actualizada
4. Evidencia: `git diff > evidence/SOL2-D/diff.patch`

## Criterios de Completitud (CHECKLIST)

- [ ] Campos fantasma auditados y resueltos (creados, calculados o eliminados)
- [ ] Coherence score tiene fuente única o documentación de por qué difiere
- [ ] Line ranges corregidos en docs
- [ ] Tests pasan
- [ ] run_all_validations.py --quick 4/4
- [ ] Máximo 60 iteraciones

## Restricciones

- **NO ejecutar v4complete**
- **NO modificar ROADMAP.md**
- **NO cambiar lógica de negocio** (solo reporting/consistencia)
- Si un campo es calculado dinámicamente y válido, NO eliminarlo — documentarlo

## Prompt de Ejecución

```
Actúa como auditor de calidad de datos.

OBJETIVO: Limpiar campos fantasma y unificar coherence score.

CONTEXTO:
- GAP-G: delivery_ready_percentage y site_verification_applied citados como fantasma
- GAP-D: coherence score difiere entre JSONs
- GAP-E: line range gate subestimado

TAREAS:
1. Buscar estos campos en todo el codebase; determinar si son calculados o hardcodeados
2. Unificar cálculo de coherence score o documentar diferencia
3. Corregir line ranges en docs
4. Validar

CRITERIOS:
- No quedan campos hardcodeados sin explicación
- Coherence score consistente o documentado
- Docs actualizados

VALIDACIONES:
- run_all_validations.py --quick 4/4
```
