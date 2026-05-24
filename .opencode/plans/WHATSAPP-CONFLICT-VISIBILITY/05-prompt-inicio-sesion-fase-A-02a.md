# FASE-A-02a: Investigación de Visibilidad WhatsApp Conflict

**ID**: FASE-A-02a  
**Objetivo**: Mapear el flujo actual de generación de la tabla "Validación de Calidad" y la sección de contexto del diagnóstico para entender cómo whatsapp_conflict llega (o no) al documento final.  
**Dependencias**: Ninguna (fase inicial)  
**Duración estimada**: 30-45 min  
**Skill**: systematic-debugging

---

## Contexto

El bloque L 123 de FASE-A-01c establece que el warning de WhatsApp conflict está diluido en la tabla "Validación de Calidad" (sección `### Validación de Calidad` del diagnóstico) donde compite con items de menor urgencia (GBP sub-optimizado, fotos insuficientes, Core Web Vitals).

El problema no es de detección — el conflicto se detecta correctamente. El problema es de **visibilidad**: el hotelero no ve el impacto de negocio cuando lee el diagnóstico.

Esta fase de investigación mapea:
1. Cómo `_build_manual_attention_table()` genera las filas de conflicto
2. Cómo el template `diagnostico_v6_template.md` posiciona esa tabla
3. Cómo `pain_narratives` define el impacto de `whatsapp_conflict`
4. Qué variables de template están disponibles en la sección de contexto

### Base Técnica Disponible
- `modules/commercial_documents/v4_diagnostic_generator.py` — generador del diagnóstico
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — template v6
- `modules/asset_generation/pain_ledger.py` — pain ledger con relaciones
- `modules/commercial_documents/pain_solution_mapper.py` — pain→narrative mapping

---

## Tareas

### Tarea 1: Mapear `_build_manual_attention_table`
**Objetivo**: Entender cómo se generan las filas de conflicto en la tabla "Validación de Calidad"

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 1477-1501)

**Criterios de aceptación**:
- [ ] Identificar cómo se itera sobre `audit_result.validation.conflicts`
- [ ] Identificar el formato de fila generado para `field_name=whatsapp`
- [ ] Documentar qué datos del conflict se usan (field_name, value, discrepancies)

### Tarea 2: Mapear posición en template diagnostico_v6
**Objetivo**: Verificar dónde aparece `${manual_attention_table}` en el template y qué lo rodea

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` (líneas 96-105)

**Criterios de aceptación**:
- [ ] Confirmar que la tabla está en sección "Validación de Calidad"
- [ ] Identificar qué variables preceden y siguen a `${manual_attention_table}`
- [ ] Confirmar que NO hay variable de nota de contexto para whatsapp_conflict

### Tarea 3: Mapear pain_narratives de whatsapp_conflict
**Objetivo**: Verificar impacto y phrasing actual en el narratives dict

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (líneas 2603-2607)

**Criterios de aceptación**:
- [ ] Identificar impacto actual (value: 0.10 según contexto FASE-A-01c)
- [ ] Identificar phrasing actual del detalle
- [ ] Documentar gap con el phrasing de impacto de negocio recomendado en L 127

### Tarea 4: Crear reporte de hallazgos
**Objetivo**: Consolidar el mapa de producción en un documento de hallazgos para FASE-A-02b

**Output**: `evidence/FASE-A-02a/hallazgos_02a.md`

**Criterios de aceptación**:
- [ ] Archivo creado con: flujo actual, gaps identificados, variables candidatas para nota contexto
- [ ] Incluir предложения de ubicación para la nota de impacto de negocio

---

## Tests Obligatorios

No hay tests para esta fase — es investigación pura.

**Comando de validación**: N/A

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar, ejecutar en orden:

1. **`dependencias-fases.md`**: Marcar FASE-A-02a como ✅ Completada, actualizar fecha
2. **`README.md` del plan**: Marcar fase como completada
3. **`09-documentacion-post-proyecto.md`**: 
   - Sección A: agregar nota "investigación de visibilidad"
   - Sección B: ningún módulo nuevo
   - Sección D: 0 tests
   - Sección E: ninguno
4. **Crear `evidence/FASE-A-02a/hallazgos_02a.md`**: Documento de hallazgos

---

## Criterios de Completitud (CHECKLIST)

- [ ] `_build_manual_attention_table` mapeado completamente
- [ ] Posición en template identificada
- [ ] `pain_narratives` de whatsapp_conflict documentado
- [ ] `hallazgos_02a.md` creado en `evidence/FASE-A-02a/`
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado

---

## Restricciones

- NO modificar ningún archivo de código en esta fase — solo investigar
- NO ejecutar `v4complete` ni ningún comando de scraping
- NO alterar `pain_narratives` ni ningún valor — esto es para FASE-A-02c

---

*Fase: WHATSAPP-CONFLICT-VISIBILITY / FASE-A-02a*  
*Creado: 2026-05-24*