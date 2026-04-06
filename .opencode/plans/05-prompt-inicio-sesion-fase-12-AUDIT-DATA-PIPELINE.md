---
description: Fix Bug 1 - Pasar datos del audit al ConditionalGenerator para que assets usen datos reales del hotel
version: 1.0.0
---

# FASE 12: Audit Data Pipeline Fix

**ID**: AUDIT-DATA-PIPELINE  
**Objetivo**: Corregir la desconexión entre V4ComprehensiveAuditor y ConditionalGenerator para que los assets se generen con datos reales del hotel extraídos del audit  
**Dependencias**: FASE 11 (GOOGLE-TRAVEL-INTEGRATION) ✅ COMPLETADA  
**Duración estimada**: 1-2 horas  
**Skill**: systematic-debugging

---

## Contexto

### Problema Detectado

Durante la ejecución de `v4complete` para Hotel Visperas, se encontró que los assets generados contienen datos genéricos ("Hotel", campos vacíos) en lugar de los datos reales extraídos del sitio web.

**Síntoma**: `hotel_schema.json` contiene `"name": "Hotel"` cuando debería contener `"name": "Hotel Vísperas"`

### Análisis de Causa Raíz

El flujo actual es:

```
V4ComprehensiveAuditor.audit() 
    → audit_result.schema.properties = { name: "Hotel Vísperas", telephone: "...", ... }

V4AssetOrchestrator.generate_assets()
    → _extract_validated_fields() → solo extrae 5 campos básicos
    → validated_data = { whatsapp, rooms, adr, occupancy, direct_channel }
    → NO tiene "hotel_data" con los datos del schema

ConditionalGenerator._generate_hotel_schema()
    → hotel_data.get("name", "Hotel") → usa default "Hotel"
```

### Estado de Fases Anteriores

| Fase | ID | Estado |
|------|----|--------|
| FASE 11 | GOOGLE-TRAVEL-INTEGRATION | ✅ COMPLETADA |
| FASE 1-10 | (completadas previamente) | ✅ COMPLETADA |

### Base Técnica Disponible

**Archivos afectados**:
- `modules/asset_generation/v4_asset_orchestrator.py` (líneas 348-361: `_extract_validated_fields`)
- `modules/asset_generation/conditional_generator.py` (líneas 464-503: `_generate_hotel_schema`)
- `modules/commercial_documents/data_structures.py` (ValidationSummary, ValidatedField)

**Tests existentes**: ~90+ tests en el proyecto

**Módulos relacionados**:
- `V4ComprehensiveAuditor` - extrae datos reales
- `V4AssetOrchestrator` - orquesta generación
- `ConditionalGenerator` - genera assets individuales
- `ValidationSummary` - resumen de campos validados

---

## Tareas

### Tarea 12.1: Modificar V4AssetOrchestrator._extract_validated_fields()

**Objetivo**: Agregar los datos del `audit_result.schema.properties` a `validated_data`

**Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`

**Cambio requerido** (líneas 348-361):

```python
def _extract_validated_fields(
    self,
    validation_summary: ValidationSummary,
    audit_result: V4AuditResult = None  # NUEVO PARÁMETRO
) -> Dict[str, Any]:
    validated_data = {}
    
    # 1. Campos existentes del ValidationSummary
    for field in validation_summary.fields:
        validated_data[field.field_name] = field
    
    # 2. NUEVO: Agregar hotel_data del audit schema
    if audit_result and audit_result.schema and audit_result.schema.properties:
        validated_data["hotel_data"] = {
            "name": audit_result.schema.properties.get("name"),
            "description": audit_result.schema.properties.get("description"),
            "telephone": audit_result.schema.properties.get("telephone"),
            "url": audit_result.schema.properties.get("url"),
            "address": audit_result.schema.properties.get("address"),
            "image": audit_result.schema.properties.get("image"),
            "price_range": audit_result.schema.properties.get("price_range"),
        }
    
    return validated_data
```

**Criterios de aceptación**:
- [ ] Método `_extract_validated_fields()` acepta `audit_result` como parámetro opcional
- [ ] Los datos del schema se agregan a `validated_data["hotel_data"]`
- [ ] Se mantiene backward compatibility si `audit_result` es None

### Tarea 12.2: Actualizar llamada en generate_assets()

**Objetivo**: Pasar `audit_result` al método `_extract_validated_fields()`

**Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`

**Cambio requerido** (línea 220):

```python
# Antes:
validated_data = self._extract_validated_fields(validation_summary)

# Después:
validated_data = self._extract_validated_fields(validation_summary, audit_result)
```

**Criterios de aceptación**:
- [ ] Llamada actualizada en línea 220
- [ ] Se pasa `audit_result` completo (no solo schema)

### Tarea 12.3: Actualizar signatura del método en todas partes

**Objetivo**: Asegurar que todas las referencias al método se actualicen

**Búsqueda requerida**:
```bash
grep -rn "_extract_validated_fields" modules/ tests/
```

**Criterios de aceptación**:
- [ ] No hay llamadas al método con firma antigua
- [ ] Tests que usan mocks se actualizan

### Tarea 12.4: Crear test de regresión

**Objetivo**: Verificar que los datos del audit llegan al ConditionalGenerator

**Archivo**: `tests/asset_generation/test_audit_data_pipeline.py`

**Test requerido**:
```python
def test_audit_schema_passes_to_conditional_generator():
    """Verifica que audit_result.schema.properties llega a validated_data"""
    # Arrange
    mock_audit = Mock(spec=V4AuditResult)
    mock_audit.schema.properties = {
        "name": "Hotel Visperas",
        "description": "Hotel boutique de lujo",
        "telephone": "+573001234567",
        "address": "Santa Rosa de Cabal",
        "price_range": "$$"
    }
    
    # Act
    validated_data = orchestrator._extract_validated_fields(
        validation_summary, 
        audit_result=mock_audit
    )
    
    # Assert
    assert "hotel_data" in validated_data
    assert validated_data["hotel_data"]["name"] == "Hotel Visperas"
    assert validated_data["hotel_data"]["telephone"] == "+573001234567"
```

**Criterios de aceptación**:
- [ ] Test creado y pasa
- [ ] Test verifica que `hotel_data` contiene datos del audit

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_audit_schema_passes_to_conditional_generator` | `tests/asset_generation/test_audit_data_pipeline.py` | Debe pasar 1/1 |
| Test de integración `v4complete` con Hotel Visperas | `tests/e2e/test_v40_complete_flow.py` | Assets contienen "Hotel Visperas" no "Hotel" |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_audit_data_pipeline.py -v
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**:
   - Marcar FASE 12 como ✅ COMPLETADA
   - Agregar fecha de finalización
   - Agregar notas: "Bug 1 corregido: audit_data_pipeline"

2. **`README-FASES-TRACKING.md`**:
   - Marcar FASE 12 como completada
   - Actualizar tabla de progreso

3. **`09-documentacion-post-proyecto.md`**:
   - Sección A: "modules/asset_generation/v4_asset_orchestrator.py - _extract_validated_fields() ahora acepta audit_result"
   - Sección D: Tests +1
   - Sección E: Marcar archivos actualizados

4. **Evidencia**: Crear `evidence/fase-12/` con logs de ejecución

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests pasan**: `pytest tests/asset_generation/test_audit_data_pipeline.py -v` pasa 1/1
- [ ] **Validación de regresión**: `pytest tests/e2e/test_v40_complete_flow.py -v` pasa
- [ ] **`dependencias-fases.md` actualizado**: FASE 12 marcada como completada
- [ ] **README actualizado**: Tabla de progreso refleja FASE 12 completada
- [ ] **Documentación post-proyecto actualizada**: Secciones A, D, E actualizadas
- [ ] **Evidencia preservada**: Logs en `evidence/fase-12/`
- [ ] **Post-ejecución completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO modificar la interfaz pública de `ValidationSummary` (backward compatibility)
- NO cambiar el formato de `validated_data` para campos existentes
- Los assets existentes que funcionan deben seguir funcionando

---

## Dependencias con FASE 13

**FASE 12 es PREREQUISITO para FASE 13**

FASE 13 necesita que FASE 12 esté completada porque:
- FASE 13 corrige Bug 2 (precio contradictorio)
- Pero primero necesitamos que los assets tengan datos reales para verificar la coherencia

---

## Versión

- **v1.0.0** (2026-03-25): Fase inicial basada en análisis de coherencia Hotel Visperas
