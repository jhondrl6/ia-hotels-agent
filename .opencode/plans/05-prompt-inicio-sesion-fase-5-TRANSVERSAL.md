# FASE 5: Validación Transversal y Cierre de Proyecto

**ID**: FASE-5-VALIDATION-CLOSURE
**Objetivo**: Ejecutar validaciones transversales, Capability Contract y cerrar proyecto correctamente
**Dependencias**: Fases 1, 2, 3, 4 completadas
**Duración estimada**: 45-60 minutos
**Skill**: systematic-debugging, test-driven-development

---

## Contexto

### Problemas Transversales Identificados

Estos problemas NO fueron cubiertos en las Fases 1-4 porque son **transversales** al sistema completo, no específicos de un módulo.

**T1: Orden de dependencias no enforced**
```
audit_report.json: timestamp 07:32:13.949673
optimization_guide.md: 07:32:14.022182

Pero optimization_guide содержит datos del audit (metadata SEO).
No está claro si el audit se ejecutó ANTES del asset generation.
```

**T2: Coherence score no validado**
```
v4_complete_report.json muestra coherence_score: 0.8828571428571428
audit_report.json muestra: geo_score=0, 0 reviews, 0 photos, 0 citations

¿Cómo se calcula coherence con datos tan limitados?
El score de 0.88 parece inflado.
```

**T3: autonomous_researcher sin output observable**
```
Informe menciona: "Autonomous Researcher intentó investigar..."
Pero no hay archivo de evidencia, logs, ni metadata que lo referencie.
El módulo o es no-op o su output se pierde.
```

**T4-T6: Métricas, Capability Contract, y Regression E2E**
```
T4: No hay tracking de salud del sistema post-ejecución
T5: No hay Capability Contract documentado para v4.5.6
T6: No hay test E2E que verifique todas las correcciones
```

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE 1: COP COP | ✅ Completada |
| FASE 2: Asset Bugs | ✅ Completada |
| FASE 3: Quality | ✅ Completada |
| FASE 4: Features | ✅ Completada |

---

## Tareas

### Tarea T1: Verificar y corregir orden de dependencias Audit → Assets
**Objetivo**: Asegurar que audit_report se genera ANTES que cualquier asset

**Investigación**:
1. Revisar `modules/orchestration_v4/` - flujo de fases
2. Verificar timestamps en el output real
3. Identificar si el orden es fortuito o intencional

**Criterios de aceptación**:
- [ ] Flujo de generación documentado
- [ ] Si hay problema, corregir en orchestration
- [ ] Test: `test_audit_generated_before_assets`

### Tarea T2: Validar coherence score con datos reales
**Objetivo**: Entender y documentar cómo se calcula coherence

**Investigación**:
1. Buscar fórmula en `modules/quality_gates/`, `modules/coherence/`
2. Calcular manually con datos de Hotel Visperas
3. Verificar si 0.88 es razonable

**Fórmula suspecta**:
```
coherence ≈ (seo_score * 0.3) + (schema_score * 0.3) + (ia_score * 0.2) + (geo_score * 0.2)
           = (91 * 0.3) + (100 * 0.3) + (65 * 0.2) + (0 * 0.2)
           = 27.3 + 30 + 13 + 0 = 70.3 ❌ (no 88)

O hay otra fórmula...
```

**Criterios de aceptación**:
- [ ] Fórmula de coherence identificada
- [ ] Cálculo verificado con datos reales
- [ ] Documentado qué pasa cuando coherence < 0.8

### Tarea T3: Capability Contract de autonomous_researcher
**Objetivo**: Definir y documentar el contrato de capacidades

**Investigación**:
1. Revisar `modules/providers/autonomous_researcher.py`
2. Buscar dónde se invoca en el flujo
3. Verificar si genera output o es no-op

**Criterios de aceptación**:
- [ ] Comportamiento del módulo documentado
- [ ] Si es no-op, comentario/logger indica "research skipped"
- [ ] Si debe generar output, implementar evidencia mínima

### Tarea T4: Métricas de salud del sistema
**Objetivo**: Crear tracking de salud post-ejecución

**Crear**:
- `metrics/system_health.json` o similar
- O agregar a `v4_complete_report.json` sección "system_health"

**Métricas a incluir**:
- Total time to generate
- Assets success rate
- Confidence score promedio
- Warnings/Errors count

**Criterios de aceptación**:
- [ ] Métricas generadas en cada ejecución
- [ ] Documentación de métricas disponible

### Tarea T5: Capability Contract completo de v4.5.6
**Objetivo**: Documentar qué capabilities existen y cuáles están conectadas

**Matriz a crear**:
```
| Capability | Estado | Invocación | Output |
|------------|--------|------------|--------|
| benchmark_resolver | connected | preflight_checks.py | metadata.disclaimers |
| disclaimer_generator | connected | conditional_generator.py | metadata.disclaimers |
| autonomous_researcher | connected/disconnected | ? | ? |
| asset_content_validator | connected | conditional_generator.py | asset.failed |
| preflight_checks | connected | conditional_generator.py | preflight_status |
```

**Criterios de aceptación**:
- [ ] Matriz creada en `docs/capability_contract_v4_5_6.md`
- [ ] Todas las capabilities tienen estado (connected/disconnected)
- [ ] 0 capacidades huérfanas

### Tarea T6: Test de regresión E2E
**Objetivo**: Verificar que todas las correcciones de Fases 1-4 no regresan

**Test a crear**:
```python
# tests/test_e2e_v4_5_6_corrections.py
def test_e2e_v4_5_6_all_corrections():
    """Test E2E que verifica todas las correcciones."""
    # FASE 1: COP COP no existe
    # FASE 2: confidence_scores consistent
    # FASE 3: no false positives in validation
    # FASE 4: benchmark validation works
    pass
```

**Criterios de aceptación**:
- [ ] Test E2E creado y pasa
- [ ] Cubre todas las correcciones de Fases 1-4

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_audit_generated_before_assets` | `tests/test_order_dependencies.py` | Timestamp audit < assets |
| `test_coherence_calculation` | `tests/test_coherence_validation.py` | Score es calculable |
| `test_capability_contract_fulfilled` | `tests/test_capability_contract.py` | 0 huérfanas |
| `test_e2e_v4_5_6_corrections` | `tests/test_e2e_v4_5_6_corrections.py` | Todos los bugs fix |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar FASE 5 como ✅ Completada
   - Proyecto marcado como CERRADO

2. **`08-plan-correccion-v4-issues.md`**
   - Marcar T1-T6 como completadas
   - Estado final: ✅ PROYECTO CERRADO

3. **`09-documentacion-post-proyecto.md`** (crear si no existe)
   - Sección A: Todos los módulos nuevos
   - Sección B: Cambios de arquitectura
   - Sección C: Validación cruzada ejecutada
   - Sección D: Métricas finales
   - Sección E: Archivos afiliados actualizados

4. **`CHANGELOG.md`**
   - Entrada para v4.5.7 (o siguiente versión)
   - Lista de correcciones implementadas

5. **`evidence/fase-5-transversal/`**
   - Capability contract
   - Métricas de salud
   - Test E2E results

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ PROYECTO CERRADO** ⚠️

- [ ] T1: Orden audit → assets verificado y documentado
- [ ] T2: Coherence calculation entendida y documentada
- [ ] T3: autonomous_researcher con comportamiento explícito
- [ ] T4: Métricas de salud disponibles
- [ ] T5: Capability contract creado (0 huérfanas)
- [ ] T6: Test E2E pasa
- [ ] **CHANGELOG.md actualizado**
- [ ] **Documentación post-proyecto completa**
- [ ] **Proyecto marcado como CERRADO**

---

## Restricciones

- [ ] NO cambiar lógica de negocio en esta fase (solo documentar y validar)
- [ ] NO modificar archivos de Fases 1-4 (excepto para corregir bugs encontrados)
- [ ] SI hay bugs encontrados en fases anteriores, reportar pero NO corregir aquí

---

## Prompt de Ejecución

```
Actúa como developer con enfoque en validación y documentación.

OBJETIVO: 6 tareas transversales para cerrar el proyecto v4.5.6

T1: Orden de dependencias
- Audit debe ejecutarse ANTES de assets
- Investigar orchestration_v4/ y verificar timestamps
- Crear test si hay problema

T2: Coherence score validation
- Coherence 0.88 declarado pero con datos limitados (0 reviews, 0 photos)
- Encontrar fórmula en modules/quality_gates/
- Calcular manualmente y verificar

T3: autonomous_researcher capability
- Módulo se menciona pero no hay output
- Investigar el módulo y su invocación
- Documentar como no-op o implementar output mínimo

T4: Métricas de salud
- Time to generate, success rate, confidence promedio
- Agregar a v4_complete_report.json o crear metrics/

T5: Capability Contract
- Crear matriz de capabilities v4.5.6
- Verificar que todas están conectadas

T6: Test E2E regression
- Crear test que verifica todas las correcciones Fases 1-4

CRITERIOS:
- Todas las tareas completadas
- Tests pasan
- CHANGELOG.md actualizado
- Proyecto marcado como CERRADO
```
