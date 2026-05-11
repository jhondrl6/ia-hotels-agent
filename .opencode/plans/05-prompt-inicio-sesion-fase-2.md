# FASE-2: Propuesta Completa + Gate Robusto (H1, H5, H8 — ALTO)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.  
> **Tipo de ejecución**: DIRECTA (código puro, sin comandos largos)  
> **Límite de iteraciones**: Máximo 60. Budget estimado: ~35 trabajo + ~15 docs = ~50.

## Contexto previo

FASE-1 completada: Coherence post-generación implementado. Ahora el sistema detecta correctamente gaps entre servicios prometidos y assets realmente generados.

**Hallazgos a resolver en esta fase**:
- **H1 (CRÍTICO)**: Propuesta muestra solo 3/8 servicios. Causa: `_generate_dynamic_services_table()` filtra por `generated_asset_types`.
- **H5 (MENOR)**: Assets técnicos (`analytics_setup_guide`, `indirect_traffic_optimization`) no aparecen en propuesta. Causa: no están en `SERVICE_CATALOG`.
- **H8 (ALTO)**: Gate 9 pasa con 50% alignment. Causa: umbral de bloqueo es `< 0.5` en vez de `< 0.8`.

## Objetivo de esta fase

La propuesta comercial debe mostrar los 8 servicios definidos en `PROPOSAL_SERVICE_TO_ASSET` con sus estados reales (aligned, missing, in-production). Gate 9 debe bloquear publicación si alignment < 80%.

### Tareas

- [x] **T1: Modificar `_generate_dynamic_services_table()` para mostrar 8 servicios con estados**
  - Archivo: `modules/commercial_documents/v4_proposal_generator.py` (L882-888)
  - En vez de filtrar por `generated_asset_types`, iterar sobre `PROPOSAL_SERVICE_TO_ASSET` completo
  - Para cada servicio, determinar estado: `aligned` (asset generado, confidence >= 0.85), `missing` (no generado), `present_in_production` (ya existe en sitio)
  - Renderizar tabla con iconos/indicadores de estado (✅, ⏳, ℹ️)
  - Referencia: `modules/asset_generation/proposal_asset_alignment.py` L20-29 para el mapeo servicio→asset

- [x] **T2: Añadir sección "Assets técnicos adicionales" en propuesta**
  - Archivo: `modules/commercial_documents/v4_proposal_generator.py` — método `_generate_asset_quality_table()` (L988-998) o nuevo método
  - Añadir `analytics_setup_guide` e `indirect_traffic_optimization` como entradas en `SERVICE_CATALOG` (o tabla separada)
  - Mostrar estado: generado (confidence), no generado, o presente en producción
  - Archivo: `modules/commercial_documents/service_catalog.py` — añadir entradas si es necesario

- [x] **T3: Cambiar umbral Gate 9 de 0.5 a 0.8**
  - Archivo: `modules/quality_gates/publication_gates.py` — `_proposal_asset_alignment_gate()` (L873-908)
  - Cambiar condición de `alignment < 0.5` → `alignment < 0.8` para bloqueo
  - Ajustar mensajes de gate para reflejar nuevo umbral
  - Considerar: si `present_in_production + aligned >= 80%` de servicios totales, pasa; si no, bloquea

- [x] **T4: Tests y validaciones**
  - Test: `_generate_dynamic_services_table()` retorna 8 filas con estados correctos para hotel con 3 aligned + 2 present_in_production + 3 missing
  - Test: Gate 9 bloquea cuando alignment = 0.5 (3/6 aligned, sin present_in_production)
  - Test: Gate 9 pasa cuando alignment = 0.83 (5/6 aligned)
  - Ejecutar `run_all_validations.py --quick` y confirmar 4/4

### Restricciones

- **NO** modificar `PROPOSAL_SERVICE_TO_ASSET` ni `ASSET_CATALOG` (son contratos estables)
- **NO** cambiar la lógica de generación de assets (eso fue FASE-1 y orquestador)
- **NO** ejecutar `v4complete` en esta fase
- Preservar backwards compatibility: si un consumidor esperaba solo 3 servicios, no romper

### Criterios de completitud

- [x] Tabla de servicios en propuesta muestra 8 entradas con estados visuales
- [x] Assets técnicos aparecen en sección dedicada de la propuesta
- [x] Gate 9 bloquea con alignment < 0.8
- [x] Tests nuevos pasan (mínimo 3)
- [x] Tests existentes no tienen regresiones
- [x] `run_all_validations.py --quick` pasa 4/4

### Próxima sesión

FASE-3: Monthly report fail-safe (H7). Se modificará `conditional_generator.py` y `monthly_report_generator.py`.
