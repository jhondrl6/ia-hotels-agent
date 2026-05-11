# FASE-3: Monthly Report Fail-Safe (H7 — ALTO)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA (código puro, sin comandos largos)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~30 trabajo + ~15 docs = ~45.

## Contexto previo

FASE-1 y FASE-2 completadas. El sistema ahora tiene coherence post-generación y propuesta completa con 8 servicios + gate robusto.

**Hallazgo H7 (ALTO)**: `monthly_report` tiene `promised_by=["always"]` en `asset_catalog.py` pero falló con error runtime (`'list' object has no attribute 'items'`). No hay retry ni notificación al usuario.

## Objetivo de esta fase

Hacer que la generación de `monthly_report` sea resistente a fallos, con retry, notificación en la propuesta, y corrección del bug runtime subyacente.

### Tareas

- [x] **T1: Añadir try/except + retry en conditional_generator para monthly_report**
  - Archivo: `modules/asset_generation/conditional_generator.py`
  - Localizar dónde se invoca `monthly_report_generator.generate()`
  - Añadir bloque try/except que capture `AttributeError` y errores de runtime
  - Implementar retry con backoff (máximo 2 reintentos)
  - Si falla después de reintentos: marcar asset como `BLOCKED` con mensaje descriptivo
  - El asset NO debe propagar la excepción — debe fallar graceful

- [x] **T2: Añadir nota en propuesta cuando monthly_report falla**
  - Archivo: `modules/commercial_documents/v4_proposal_generator.py`
  - En `_generate_asset_quality_table()` o sección de disclaimers, detectar si `monthly_report` está en estado `BLOCKED`
  - Añadir nota tipo: *"El informe mensual no pudo generarse automáticamente en esta ejecución. Se entregará manualmente dentro de las 24 horas siguientes."*
  - Similar al disclaimer de low_quality que ya existe

- [x] **T3: Investigar y corregir bug runtime en monthly_report_generator.py**
  - Archivo: `modules/asset_generation/monthly_report_generator.py`
  - Error: `'list' object has no attribute 'items'`
  - Buscar dónde se asume un dict pero llega una lista (probablemente en datos de entrada del hotel o métricas)
  - Añadir guard clause o conversión de tipo antes de llamar `.items()`
  - Verificar que el fix no afecta el caso feliz (datos correctos)

- [x] **T4: Tests y validaciones**
  - Test: `conditional_generator` maneja `AttributeError` de monthly_report sin propagar excepción
  - Test: `monthly_report_generator` no falla cuando recibe lista en vez de dict
  - Test: Propuesta contiene disclaimer cuando monthly_report está BLOCKED
  - Ejecutar `run_all_validations.py --quick` y confirmar 4/4

### Restricciones

- **NO** cambiar `promised_by=["always"]` en `asset_catalog.py` — el asset DEBE seguir prometiéndose
- **NO** modificar la interfaz pública de `monthly_report_generator.generate()` (firma del método)
- **NO** ejecutar `v4complete` en esta fase

### Criterios de completitud

- [x] `conditional_generator` tiene try/except + retry para monthly_report
- [x] Propuesta muestra disclaimer cuando monthly_report falla
- [x] Bug runtime `'list' object has no attribute 'items'` corregido
- [x] Tests nuevos pasan (mínimo 3)
- [x] Tests existentes no tienen regresiones
- [x] `run_all_validations.py --quick` pasa 4/4

### Próxima sesión

FASE-4: Corrección financiera (H3, H4). Se modificará `_build_brecha_data()` y templates financieros.
