# FASE 4: Feature Enhancements - Benchmark Validation y Hoteles Nuevos

**ID**: FASE-4-FEATURE-ENHANCEMENTS
**Objetivo**: Implementar mejoras de detección y features para hoteles nuevos
**Dependencias**: FASE 3 completada
**Duración estimada**: 45-60 minutos
**Skill**: systematic-debugging, code-review

---

## Contexto

### Problemas Identificados

**Problema B1: Desconexión entre benchmark y datos reales**
```
financial_scenarios.json usa ADR real: $280.000 - $520.000 COP
benchmark_resolver.py sugiere para boutique: $150.000 - $350.000 COP

No hay validación cruzada que alerte cuando los datos reales se desvían 
significativamente del benchmark regional.
```

**Problema B2: Umbrales demasiado estrictos para hoteles nuevos**
```
whatsapp_button y faq_page no se generaron para Hotel Visperas.
Razón: confidence < umbral (0.6 para whatsapp, 0.7 para faq)

Pero Hotel Visperas es un hotel nuevo (0 reviews, 0 photos en GBP).
Los umbrales actuales penalizan hoteles sin presencia digital.
```

**Problema B3: Error ortográfico en benchmark_descriptions**
```python
# benchmark_resolver.py línea 59
"un servicio personalizado en un ambiente acogedor y Refinando."
                                                          ^^^^^^^^
Error: "Refinando" no tiene sentido aquí. Debería ser "refinado" o removerse.
```

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE 1: COP COP | 🚧 Pendiente |
| FASE 2: Asset Bugs | 🚧 Pendiente |
| FASE 3: Quality | 🚧 Pendiente |

### Base Técnica Disponible
- Archivos existentes:
  - `modules/providers/benchmark_resolver.py`
  - `modules/asset_generation/conditional_generator.py`
  - `modules/asset_generation/preflight_checks.py`
- Tests base: ~1440 (después de FASE 3)
- Módulos: BenchmarkResolver, ConditionalGenerator, PreflightChecker

---

## Tareas

### Tarea 1: Implementar validación cruzada benchmark vs datos reales
**Objetivo**: Alertar cuando datos reales se desvían significativamente del benchmark

**Archivos a modificar**:
- `modules/asset_generation/preflight_checks.py`
- O crear nuevo: `modules/asset_validation/benchmark_cross_validator.py`

**Lógica a implementar**:
```
1. Obtener datos reales del hotel (ADR, rooms, etc.)
2. Comparar con benchmark regional para la categoría del hotel
3. SI desviación > 20%: generar warning en metadata
4. SI desviación > 50%: generar error (datos posiblemente incorrectos)
```

**Criterios de aceptación**:
- [ ] Warning cuando ADR real difiere >20% del benchmark
- [ ] Metadata incluye campo `benchmark_deviation` con porcentaje
- [ ] Test: verificar que validation pasa con desviación <20%

### Tarea 2: Implementar umbrales diferenciados para hoteles nuevos
**Objetivo**: Reducir umbrales de confidence para hoteles sin presencia digital

**Lógica a implementar**:
```
SI hotel.tiene_presencia_digital == False:
    umbrales_reducidos = {
        'whatsapp_button': 0.3,  # era 0.6
        'faq_page': 0.4           # era 0.7
    }
```

**Indicadores de "hotel nuevo"**:
- GBP: place_found = false
- Reviews: 0
- Photos: 0
- SEO score: <50

**Archivos a modificar**:
- `modules/asset_generation/conditional_generator.py`
- `modules/asset_generation/preflight_checks.py`

**Criterios de aceptación**:
- [ ] Hotel Visperas (0 reviews, 0 photos) genera whatsapp_button
- [ ] Hotel establecido (>10 reviews) mantiene umbrales originales
- [ ] Test: verificar ambos escenarios

### Tarea 3: Corregir error ortográfico "Refinando"
**Objetivo**: Eliminar el error ortográfico del benchmark

**Archivo a modificar**:
- `modules/providers/benchmark_resolver.py` línea 59

**Cambio**:
```python
# Antes:
"un servicio personalizado en un ambiente acogedor y Refinando."

# Después:
"un servicio personalizado en un ambiente acogedor y tranquilo."
# O simplemente remover "y Refinando"
```

**Criterios de aceptación**:
- [ ] `grep -n "Refinando" modules/providers/benchmark_resolver.py` retorna 0
- [ ] Benchmark description sigue siendo coherente

### Tarea 4: Crear tests de feature
**Objetivo**: Asegurar que las nuevas features no regresen

**Archivos a crear**:
- `tests/test_benchmark_cross_validation.py`
- `tests/test_new_hotel_thresholds.py`

**Criterios de aceptación**:
- [ ] Test de desviación benchmark pasa
- [ ] Test de umbrales diferenciados pasa
- [ ] `pytest tests/test_benchmark_cross_validation.py tests/test_new_hotel_thresholds.py -v`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_benchmark_deviation_warning` | `tests/test_benchmark_cross_validation.py` | Warning a >20% desviación |
| `test_new_hotel_generates_low_confidence_assets` | `tests/test_new_hotel_thresholds.py` | whatsapp_button generado |
| `test_established_hotel_uses_strict_thresholds` | `tests/test_new_hotel_thresholds.py` | Umbrales originales mantenidos |

**Comando de validación**:
```bash
pytest tests/test_benchmark_cross_validation.py tests/test_new_hotel_thresholds.py -v
python -m pytest tests/ -v --tb=short
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar FASE 4 como ✅ Completada

2. **`08-plan-correccion-v4-issues.md`**
   - Marcar B1, B2, B3 como completadas
   - Actualizar estado general a ✅ TODO COMPLETADO

3. **`09-documentacion-post-proyecto.md`**
   - Sección A: Agregar nuevos módulos si los hay
   - Sección D: Actualizar métricas finales

4. **`evidence/fase-4-enhancements/`**
   - Crear directorio
   - Guardar evidencia de feature testing

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Benchmark validation implementada**: Alerting cuando desviación >20%
- [ ] **Umbrales diferenciados**: Hoteles nuevos generan más assets
- [ ] **Error ortográfico corregido**: "Refinando" removido
- [ ] **Tests nuevos pasan**: `pytest tests/test_benchmark_cross*.py tests/test_new_hotel*.py -v`
- [ ] **Validación E2E**: `pytest tests/test_never_block_integration.py -v` PASS
- [ ] **Post-ejecución completada**: Todos los puntos anteriores
- [ ] **CHANGELOG.md actualizado**: Entrada para v4.5.7 o similar

---

## Restricciones

- [ ] NO cambiar umbrales para hoteles establecidos (mantener backwards compatibility)
- [ ] NO eliminar benchmark_resolver.py (es usado en FASE 1-3)
- [ ] Los warnings de benchmark deviation NO deben bloquear generación

---

## Prompt de Ejecución

```
Actúa como developer con enfoque en features y edge cases.

OBJETIVO: Implementar 3 enhancements:

B1: Validación cruzada benchmark vs datos reales
- ADR real: $280-520k, Benchmark: $150-350k (diferencia >80%)
- Alertar cuando datos reales se desvían >20% del benchmark
- Implementar en preflight_checks.py o nuevo validador

B2: Umbrales diferenciados para hoteles nuevos
- Hotel Visperas: 0 reviews, 0 photos, place_found=false
- Umbrales actuales: whatsapp_button=0.6, faq=0.7
- Reducir umbrales para hoteles nuevos: whatsapp=0.3, faq=0.4
- Lógica: Si GBP sin datos, aplicar umbrales reducidos

B3: Corregir "Refinando" en benchmark_resolver.py
- Error ortográfico en línea 59
- Cambiar a texto coherente

TAREAS:
1. Implementar benchmark_cross_validator con warning >20%
2. Implementar umbrales diferenciados en conditional_generator
3. Corregir texto en benchmark_resolver.py
4. Crear tests para ambas features

CRITERIOS:
- Warning en metadata cuando desviación >20%
- whatsapp_button generado para hotel nuevo
- "Refinando" no existe en código

VALIDACIONES:
- pytest tests/test_benchmark_cross_validation.py tests/test_new_hotel_thresholds.py -v
- grep -n "Refinando" modules/providers/benchmark_resolver.py
```
