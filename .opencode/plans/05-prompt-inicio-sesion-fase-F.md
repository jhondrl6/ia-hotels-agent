# FASE-F: Corrección de Brechas E2E

**ID**: FASE-F  
**Objetivo**: Cerrar las 3 brechas identificadas en la validación E2E de FASE-E  
**Dependencias**: FASE-E completada  
**Duración estimada**: 1-2 horas  
**Skill**: `systematic-debugging` + `test-driven-development`

---

## Contexto

### Brechas Identificadas en FASE-E

1. **FAQ respuestas cortas**: Las respuestas FAQ generadas tienen 12-15 palabras, pero FASE-B requiere 40-60 palabras por respuesta para optimización TTS
2. **voice_assistant_guide no incluido**: Los 3 blueprints (Google Assistant, Apple Business, Alexa) existen en `modules/delivery/generators/` pero NO se incluyen en el delivery package
3. **2 tests con import errors**: `test_coherence_bloqueo.py` y `test_hotel_visperas.py` fallan en import de `commercial_documents.composer`

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-A | ✅ Completada 2026-03-25 |
| FASE-B | ✅ Completada 2026-03-25 |
| FASE-C | ✅ Completada 2026-03-25 |
| FASE-D | ✅ Completada 2026-03-25 |
| FASE-E | ✅ Completada 2026-03-25 (con brechas) |

### Base Técnica Disponible
- Blueprints en: `modules/delivery/generators/`
- FAQ generator: `modules/delivery/generators/faq_gen.py`
- Tests en: `tests/regression/`
- Delivery orchestrator: `modules/asset_generation/v4_asset_orchestrator.py`

---

## Tareas

### Tarea F.1: Corregir Largo de FAQ Conversacional

**Objetivo**: Las respuestas FAQ deben tener 40-60 palabras para optimización TTS

**Problema identificado**: El FAQ generator produce respuestas cortas tipo "Sí, incluye desayuno." (12 palabras)

**Investigación requerida**:
1. Leer `modules/delivery/generators/faq_gen.py` para entender cómo se generan las respuestas
2. Identificar si el prompt del LLM pide respuestas extensas
3. Verificar si hay truncamiento en el output

**Archivos afectados**:
- `modules/delivery/generators/faq_gen.py`

**Criterios de aceptación**:
- [ ] Respuestas FAQ tienen 40-60 palabras
- [ ] Regenerar FAQ para hotelvisperas y verificar longitud
- [ ] Test de regresión para longitud de FAQ pasa

---

### Tarea F.2: Integrar voice_assistant_guide en Delivery

**Objetivo**: Los 3 blueprints deben aparecer en el delivery package

**Problema identificado**: Los archivos existen en `modules/delivery/generators/` pero no se copian al delivery

**Investigación requerida**:
1. Leer `modules/asset_generation/conditional_generator.py` para entender cómo se incluyen assets
2. Buscar cómo se decide qué archivos van al delivery
3. Verificar si `voice_assistant_guide` está registrado como asset type

**Archivos afectados**:
- `modules/asset_generation/conditional_generator.py`
- `modules/delivery/generators/` (3 blueprints)

**Criterios de aceptación**:
- [ ] `voice_assistant_guide/` aparece en delivery output
- [ ] Los 3 archivos (google_assistant, apple_business, alexa) están presentes
- [ ] E2E test con hotelvisperas confirma inclusion

---

### Tarea F.3: Corregir Import Errors en Tests

**Objetivo**: Los 2 tests que fallan por import deben pasar

**Problema identificado**: 
```
ModuleNotFoundError: No module named 'commercial_documents.composer'
```

**Investigación requerida**:
1. Verificar si `commercial_documents/composer.py` existe
2. Leer `tests/regression/test_coherence_bloqueo.py` línea 7
3. Leer `tests/regression/test_hotel_visperas.py` línea 20
4. Comparar imports con otros tests que SÍ funcionan

**Archivos afectados**:
- `tests/regression/test_coherence_bloqueo.py`
- `tests/regression/test_hotel_visperas.py`

**Criterios de aceptación**:
- [ ] `pytest tests/regression/test_coherence_bloqueo.py` pasa
- [ ] `pytest tests/regression/test_hotel_visperas.py` pasa
- [ ] Sin modification de código production (solo imports)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| FAQ length | Nuevo test en `tests/` | Respuestas 40-60 palabras |
| voice_assistant_guide delivery | E2E check | 3 archivos en output |
| test_coherence_bloqueo | `tests/regression/` | Pasa sin errors |
| test_hotel_visperas | `tests/regression/` | Pasa sin errors |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
PYTHONPATH=. ./venv/Scripts/python.exe -m pytest tests/regression/ -v --tb=short
```

---

## Restricciones

- NO modificar lógica de negocio de FASE-A a FASE-E
- Esta fase SOLO corrige brechas, no añade features
- Los 3 blueprints son templates informativos, no código de integración real

---

## Post-Ejecución (OBLIGATORIO)

1. **`dependencias-fases.md`**: Marcar FASE-F como ✅ Completada
2. **`06-checklist-implementacion.md`**: Agregar FASE-F al progreso
3. **`09-documentacion-post-proyecto.md`**: Sección G - marcar brechas como resueltas
4. **Ejecutar E2E completo** para confirmar todas las brechas cerradas

---

## Criterios de Completitud (CHECKLIST)

- [ ] FAQ con respuestas de 40-60 palabras verificado
- [ ] voice_assistant_guide con 3 archivos en delivery
- [ ] 28/28 regression tests pasan
- [ ] `dependencias-fases.md` actualizado
- [ ] Documentación post-proyecto actualizada

---

## Prompt de Ejecución

```
Actúa como systematic-debugger y test-driven developer.

OBJETIVO: Cerrar las 3 brechas identificadas en FASE-E.

CONTEXTO:
- FASE-E completó E2E con hotelvisperas
- 3 brechas identificadas: FAQ corto, voice_guide missing, 2 tests con import errors
- Coherence score: 0.84 (aceptable)

TAREAS:
1. Investigar por qué FAQ genera respuestas cortas (12-15 vs 40-60 palabras)
2. Investigar por qué voice_assistant_guide no aparece en delivery
3. Investigar y corregir imports en test_coherence_bloqueo.py y test_hotel_visperas.py

CRITERIOS:
- FAQ respuestas: 40-60 palabras
- voice_assistant_guide: 3 archivos en delivery
- 28/28 tests pasan
- Solo debugging, NO nuevos features
```
