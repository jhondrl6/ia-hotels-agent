# FASE-A: Corrección Conceptual — Renombrar AEO Schema

**ID**: FASE-A  
**Objetivo**: Eliminar la confusión conceptual donde "AEO" del sistema mide schema.org tradicional, no voice search optimization  
**Dependencias**: Ninguna  
**Duración estimada**: 1-2 horas  
**Skill**: `systematic-debugging` + `code-review`

---

## Contexto

### Problema Identificado

El sistema actual命名「AEO (Schema)」en el diagnóstico cuando en realidad mide:
- Existencia de schema.org Hotel
- Existencia de FAQ schema
- Performance web

Esto NO es AEO (Auditory Engine Optimization) que busca optimizarse para asistentes de voz (Alexa, Siri, Google Assistant).

Según KB `AEO_agent_ready.md`, AEO real requiere:
- SpeakableSpecification en schema
- FAQ en formato conversacional (40-60 palabras para TTS)
- Integración con Alexa Skills, Apple Business Connect, Google Assistant
- Voice keywords

Además existe **dual counting**: el mismo schema se cuenta en AEO y en IAO.

### Base Técnica Disponible

- **Archivo principal**: `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 847-879)
- **Templates**: `modules/commercial_documents/templates/diagnostico_v4_template.md`
- **Tests**: 28 tests de regresión pasando
- **GAP analyzer**: `modules/analyzers/gap_analyzer.py`

---

## Tareas

### Tarea A.1: Renombrar "AEO (Schema)" → "Schema Infrastructure" en Diagnóstico

**Objetivo**: El diagnóstico actual muestre "Schema Infrastructure" en lugar de "AEO (Schema)" para reflejar lo que realmente mide.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (línea 180 del template)
- `modules/commercial_documents/v4_diagnostic_generator.py` (método `_calculate_aeo_score`)

**Criterios de aceptación**:
- [ ] El label en la tabla del diagnóstico cambia de "AEO (Schema)" a "Schema Infrastructure"
- [ ] El benchmark label cambia de "AEO" a "Schema Infra" 
- [ ] El nombre del método `_calculate_aeo_score` puede mantenerse o renombrarse a `_calculate_schema_infrastructure_score`
- [ ] Los tests existentes siguen pasando
- [ ] El documento `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` generado refleja el cambio

### Tarea A.2: Eliminar Dual Counting entre AEO y IAO

**Objetivo**: El Schema Hotel y FAQ Schema NO deben contar para ambas métricas.

**Lógica actual**:
- AEO: Hotel Schema (35-50 pts) + FAQ Schema (25-30 pts)
- IAO: Hotel Schema (30-40 pts) + FAQ Schema (25 pts)

**Cambio propuesto**: IAO absorbe el componente Schema, AEO se enfoca puramente en voice infrastructure.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (métodos `_calculate_aeo_score` y `_calculate_iao_score`)

**Criterios de aceptación**:
- [ ] Hotel Schema SOLO cuenta para IAO (no para AEO renombrado)
- [ ] FAQ Schema SOLO cuenta para IAO (no para AEO renombrado)
- [ ] AEO renombrado mide SOLO: SpeakableSpecification + Performance + Voice-ready content
- [ ] Tests pasan sin regresión

### Tarea A.3: Crear nueva métrica "Voice Readiness" placeholder

**Objetivo**: Dejar el espacio conceptual para cuando FASE-B implemente AEO real.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`
- Template de diagnóstico

**Criterios de aceptación**:
- [ ] Existe espacio/métrica placeholder "Voice Readiness (AEO)" que dice "Pendiente - Requiere FASE-B"
- [ ] Score por defecto: 0/100 con nota de "No implementado aún"

### Tarea A.4: Actualizar GAP Analyzer para renombrar paquetes

**Objetivo**: Los paquetes "Pro AEO" pasan a llamarse de forma que reflejen su contenido real.

**Archivos afectados**:
- `modules/analyzers/gap_analyzer.py` (líneas relacionadas a "Pro AEO")

**Criterios de aceptación**:
- [ ] Paquetes renombrados si mencionan "AEO" pero no son de voz
- [ ] Consistencia con el nuevo naming

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_diagnostic_generates` | `tests/` | Genera documento sin errores |
| `test_schema_scores` | `tests/` | AEO/IAO scores no comparten componentes |
| Regression suite | `tests/` | 28/28 tests pasan |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-A como ✅ Completada con fecha
2. **`README.md`** del plan: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Sección A (módulos nuevos), Sección E (archivos modificados)
4. **证据/fase-A/**: Guardar screenshot del diagnóstico antes/después

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests pasan**: 28/28 regression tests + tests nuevos si aplica
- [ ] **Renombrado completo**: "AEO (Schema)" → "Schema Infrastructure" en TODOS los lugares
- [ ] **Dual counting eliminado**: Schema y FAQ solo cuentan para IAO
- [ ] **Placeholder creado**: Voice Readiness existe como métrica pendiente
- [ ] **Documentación actualizada**: dependencias-fases.md, README del plan
- [ ] **Evidencia preservada**: Output del diagnóstico mostrando los cambios

---

## Restricciones

- NO modificar la lógica de cálculo de financial_scenarios
- NO cambiar la estructura del JSON de audit_report.json
- NO alterar cómo se generan los assets (eso es FASE-B)
- Mantener compatibilidad hacia atrás con tests existentes

---

## Prompt de Ejecución

```
Actúa como developer y code reviewer.

OBJETIVO: Corregir el naming conceptual del sistema AEO en iah-cli.

CONTEXTO:
- Sistema actual confunde "Schema Infrastructure" con "AEO" (voice search)
- AEO real según KB requiere: SpeakableSpecification, FAQ conversacional, integración Alexa/Siri
- Dual counting: mismo Schema cuenta para AEO y IAO
- Base: v4_diagnostic_generator.py líneas 847-879

TAREAS:
1. Renombrar "AEO (Schema)" → "Schema Infrastructure" en template y método
2. Eliminar dual counting: Schema y FAQ solo en IAO
3. Crear placeholder "Voice Readiness" con score 0/100
4. Actualizar GAP analyzer si afecta naming de paquetes

CRITERIOS:
- Todos los tests pasan (28/28 regression)
- Diagnóstico generado muestra nuevo naming
- Voice Readiness aparece como métrica pendiente

VALIDACIONES:
- python -m pytest tests/ -v
- Generar diagnóstico de prueba con hotelvisperas
```
