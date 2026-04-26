# FASE-A: Unificar hotel_schema dual (rico vs vacio)

**ID**: FASE-A
**Objetivo**: Garantizar que el asset hotel_schema entregado al cliente use el schema enriquecido (geo_enriched) en lugar del schema basico vacio, eliminando la contradiccion interna del pipeline.
**Dependencias**: Ninguna
**Duracion estimada**: 1.5-2 horas
**Skill**: phased_project_executor v2.4.0

---

## Contexto

El Veredicto forense (Veredicto.md Hallazgo 3) confirmo que iah-cli genera DOS versiones de hotel_schema:
1. Schema "vacio": tipo LodgingBusiness, sin amenities, confidence ~0.5. Generado por `conditional_generator._generate_hotel_schema()`.
2. Schema "rico": tipo Hotel, 16+ campos reales, confidence 0.85. Generado por `hotel_schema_enricher.py` via `geo_enrichment_layer.py`.

El bridge (`geo_enriched_bridge.try_enrich_from_geo_enriched()`) ya existe en `v4_asset_orchestrator.py` linea 310, pero solo aplica cuando confidence < 0.7. El problema es que el schema basico se entrega al cliente cuando el bridge no se aplica.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| (ninguna) | - |

### Base Tecnica Disponible
- Archivo bridge: `modules/asset_generation/geo_enriched_bridge.py`
- Orchestrador: `modules/asset_generation/v4_asset_orchestrator.py` (linea 298-343)
- Generator: `modules/asset_generation/conditional_generator.py` (linea 404-407, 772-844)
- Enricher: `modules/geo_enrichment/hotel_schema_enricher.py`
- Tests base: 2224 funciones

---

## Tareas

### Tarea 1: Modificar conditional_generator para preferir schema rico

**Objetivo**: Cuando `_generate_hotel_schema()` se ejecuta, primero verificar si existe `geo_enriched/hotel_schema_rich.json` y usarlo como base antes de generar uno nuevo vacio.

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py`

**Pasos**:
1. En `_generate_hotel_schema()` (linea 772), agregar logica de pre-check:
   - Buscar `hotel_schema_rich.json` en el directorio de output del hotel
   - Si existe y tiene confidence >= 0.7, usarlo directamente (skip generacion basica)
   - Si no existe o confidence < 0.7, proceder con generacion basica normal
2. En `_generate_content()` linea 404-407 (rama hotel_schema), integrar el mismo pre-check

**Criterios de aceptacion**:
- [ ] `_generate_hotel_schema()` verifica existencia de schema rico antes de generar basico
- [ ] Si el schema rico existe y es valido, se retorna como asset oficial
- [ ] Si no existe, la generacion basica funciona como antes (backward compatible)
- [ ] Logs claros: "Using enriched hotel_schema (confidence X)" vs "Generating basic hotel_schema"

### Tarea 2: Garantizar que el orchestrator SIEMPRE aplique el bridge

**Objetivo**: Modificar `v4_asset_orchestrator._generate_single_asset()` para que el bridge geo_enriched se aplique siempre que exista un schema rico, independientemente del confidence del basico.

**Archivos afectados**:
- `modules/asset_generation/v4_asset_orchestrator.py`

**Pasos**:
1. En `_generate_single_asset()` lineas 298-343, modificar la condicion del bridge:
   - Actual: solo aplica si `confidence < 0.7`
   - Nuevo: aplica siempre que `geo_enriched/hotel_schema_rich.json` exista y sea valido
2. Agregar metrica al bridge: contar cuantas veces se reemplazo el schema basico

**Criterios de aceptacion**:
- [ ] El bridge se aplica para hotel_schema cuando el schema rico existe, sin importar confidence
- [ ] Se registra metrica de reemplazo en logs
- [ ] No afecta otros assets (solo hotel_schema)

### Tarea 3: Tests de regresion

**Objetivo**: Verificar que los tests existentes pasan y agregar tests nuevos para la logica de preferencia.

**Archivos afectados**:
- `tests/asset_generation/test_conditional_generator.py`
- `tests/asset_generation/test_geo_enriched_bridge.py`

**Pasos**:
1. Ejecutar tests existentes: `pytest tests/asset_generation/ -v --timeout=60`
2. Agregar test: "schema rico existe → se usa directamente"
3. Agregar test: "schema rico no existe → generacion basica normal"
4. Agregar test: "schema rico con confidence bajo → generacion basica con fallback"
5. Verificar que test_schema_confusion.py pasa

**Criterios de aceptacion**:
- [ ] Todos los tests existentes pasan (0 regresiones)
- [ ] Al menos 3 tests nuevos cubriendo los escenarios
- [ ] `pytest tests/asset_generation/ -v` pasa 100%

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| test_conditional_generator.py | tests/asset_generation/ | Todos pasan |
| test_geo_enriched_bridge.py | tests/asset_generation/ | Todos pasan |
| test_content_gates.py | tests/asset_generation/ | Todos pasan |
| test_schema_confusion.py | tests/regression/ | Pasa sin regresion |
| test_asset_confidence_gate.py | tests/quality_gates/ | Pasa sin regresion |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe -m pytest tests/asset_generation/ tests/regression/test_schema_confusion.py tests/quality_gates/test_asset_confidence_gate.py -v --timeout=60
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-A como Completada con fecha
2. **`README.md` del plan**: Actualizar tabla de progreso
3. **`09-documentacion-post-proyecto.md`**: Seccion A (modulos), D (metricas), E (archivos)

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Tests de preferencia de schema rico ejecutan exitosamente
- [ ] **Tests existentes sin regresion**: `pytest tests/asset_generation/ -v` 100%
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-A marcada como completada
- [ ] **Documentacion afiliada**: CHANGELOG.md, GUIA_TECNICA.md actualizados
- [ ] **Post-ejecucion completada**: Todos los puntos anteriores realizados

---

## Restricciones

- NO modificar `hotel_schema_enricher.py` (ya funciona correctamente)
- NO cambiar la estructura del schema rico (solo reusarlo)
- NO afectar assets que no sean hotel_schema
- Mantener backward compatibility: si no hay schema rico, el basico debe seguir funcionando
- Maximo 60 iteraciones del agente en esta fase

---

## Prompt de Ejecucion

```
Actua como desarrollador senior de iah-cli.

OBJETIVO: Unificar el asset hotel_schema para que siempre use el schema enriquecido (geo_enriched) cuando este disponible, eliminando la contradiccion de tener dos schemas (rico vs vacio).

CONTEXTO:
- El pipeline genera DOS schemas: basico (conditional_generator.py linea 772) y rico (hotel_schema_enricher.py via geo_enrichment_layer.py)
- El bridge geo_enriched_bridge.py YA existe pero solo aplica condicionalmente (confidence < 0.7)
- El asset entregado al cliente es el vacio (LodgingBusiness, sin amenities)

TAREAS:
1. Modificar conditional_generator._generate_hotel_schema() (linea 772) para buscar schema rico primero
2. Modificar v4_asset_orchestrator._generate_single_asset() (lineas 298-343) para siempre aplicar bridge en hotel_schema
3. Agregar tests nuevos (preferencia rico, fallback basico, edge cases)

CRITERIOS:
- Schema rico se usa como asset oficial cuando existe
- Schema basico funciona como fallback cuando no hay rico
- 0 regresiones en tests existentes
- Logs claros del flujo seguido

VALIDACIONES:
- pytest tests/asset_generation/ tests/regression/test_schema_confusion.py -v
- run_all_validations.py --quick
```
