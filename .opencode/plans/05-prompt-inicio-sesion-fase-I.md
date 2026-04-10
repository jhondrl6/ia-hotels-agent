# FASE-I: data_structures.py Deduplication

**ID**: FASE-I
**Objetivo**: Eliminar código duplicado en `data_structures.py`: clase `Scenario` con campos duplicados, funciones `calculate_quick_wins()` y `extract_top_problems()` definidas dos veces
**Dependencias**: FASE-H completada
**Duración estimada**: 1.5-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema Detectado

`modules/commercial_documents/data_structures.py` tiene duplicaciones:

1. **Clase `Scenario`** (línea 83): Campos `monthly_opportunity_cop`, método `format_loss_cop()`, y `is_equilibrium_or_gain()` definidos DOS veces (líneas 91-103 vs 103-114)
2. **Función `calculate_quick_wins()`**: Definida en líneas ~320 Y ~419 (segunda sombrea la primera)
3. **Función `extract_top_problems()`**: Definida en líneas ~362 Y ~461 (segunda sombrea la primera)

En Python, la segunda definición silenciosamente reemplaza la primera, así que funcionalmente el código "funciona". Pero es confuso, peligroso para mantenimiento, y oculta bugs potenciales si alguien edita la versión equivocada.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-F | ✅ Completada |
| FASE-G | ✅ Completada |
| FASE-H | ✅ Completada |

### Base Técnica Disponible
- Archivo: `modules/commercial_documents/data_structures.py`
- FASE-G agregó `brechas_reales: Optional[List[Dict[str, Any]]]` a `DiagnosticSummary`
- Todos los consumers de `Scenario`, `calculate_quick_wins`, `extract_top_problems` deben seguir funcionando

---

## Tareas

### Tarea 1: Analizar ambas versiones de cada duplicado

**Objetivo**: Determinar cuál versión es la "correcta" (la que Python realmente usa) antes de eliminar

**Pasos**:
1. Leer la segunda definición de `Scenario` fields (la que realmente ejecuta)
2. Leer la segunda definición de `calculate_quick_wins()` (la que realmente ejecuta)
3. Leer la segunda definición de `extract_top_problems()` (la que realmente ejecuta)
4. Comparar ambas versiones para detectar si hay diferencias sutiles

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py`

**Criterios de aceptación**:
- [ ] Documentado cuál versión es la "viva" y cuál la "muerta" para cada duplicado
- [ ] Si hay diferencias entre versiones, documentadas y decidido cuál conservar

### Tarea 2: Eliminar definiciones muertas

**Objetivo**: Remover las primeras ocurrencias (las que Python nunca ejecuta)

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py`

**Regla**: Eliminar la PRIMERA ocurrencia de cada duplicado (la que está sombreada). Conservar la SEGUNDA (la que Python realmente ejecuta).

Excepción: Si la segunda versión es claramente inferior (falta lógica, menos robusta), invertir — pero documentar por qué.

**Criterios de aceptación**:
- [ ] `Scenario` tiene campos definidos UNA sola vez
- [ ] `calculate_quick_wins()` definida UNA sola vez
- [ ] `extract_top_problems()` definida UNA sola vez
- [ ] El archivo pasa `python -c "import modules.commercial_documents.data_structures"` sin errores

### Tarea 3: Agregar brechas_reales a DiagnosticSummary (si FASE-G no lo hizo)

**Objetivo**: Verificar que el campo `brechas_reales` agregado en FASE-G está presente y correctamente tipado

**Archivos afectados**:
- `modules/commercial_documents/data_structures.py`

**Criterios de aceptación**:
- [ ] `DiagnosticSummary` tiene `brechas_reales: Optional[List[Dict[str, Any]]] = None`
- [ ] El default es None (backward compatible)

### Tarea 4: Tests de regresión post-dedup

**Objetivo**: Verificar que la eliminación de código muerto no rompe nada

**Tests a crear/agregar**:

1. `test_scenario_no_duplicate_fields`: Verificar que Scenario tiene cada campo una sola vez
2. `test_calculate_quick_wins_single_definition`: Verificar que la función es única
3. `test_extract_top_problems_single_definition`: Verificar que la función es única
4. `test_diagnostic_summary_has_brechas_reales`: Verificar campo nuevo existe

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasando
- [ ] TODA la suite de tests existente pasa sin regresiones
- [ ] `python -c "from modules.commercial_documents.data_structures import *"` funciona

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_scenario_no_duplicate_fields` | `tests/commercial_documents/test_data_structures.py` | Sin duplicados |
| `test_calculate_quick_wins_single_definition` | `tests/commercial_documents/test_data_structures.py` | 1 sola def |
| `test_extract_top_problems_single_definition` | `tests/commercial_documents/test_data_structures.py` | 1 sola def |
| `test_diagnostic_summary_has_brechas_reales` | `tests/commercial_documents/test_data_structures.py` | Campo existe |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-I como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-I como ✅
3. **`09-documentacion-post-proyecto.md`**: Sección A, D, E
4. **`scripts/log_phase_completion.py`**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-I \
    --desc "Deduplication of Scenario class, calculate_quick_wins, extract_top_problems in data_structures.py" \
    --archivos-mod "modules/commercial_documents/data_structures.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 4/4 dedup tests exitosos
- [ ] **Tests existentes pasan**: 0 regresiones en suite COMPLETA
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa
- [ ] **Sin duplicados**: Scenario, calculate_quick_wins, extract_top_problems — una sola definición cada uno
- [ ] **Import limpio**: `from modules.commercial_documents.data_structures import *` funciona
- [ ] **brechas_reales presente**: Campo en DiagnosticSummary
- [ ] **Post-ejecución completada**: dependencias, checklist, docs actualizados

---

## Restricciones

- NO agregar nueva funcionalidad — solo eliminar duplicados
- NO cambiar la API pública de Scenario, DiagnosticSummary, calculate_quick_wins, extract_top_problems
- Si las dos versiones de un duplicado tienen diferencias, documentar ANTES de elegir
- Ejecutar suite completa de tests como validación (no solo los nuevos)

---

## Prompt de Ejecución

```
Actúa como ingeniero Python senior especializado en limpieza de código.

OBJETIVO: Eliminar código duplicado en data_structures.py.

CONTEXTO:
- Scenario class tiene campos duplicados (líneas 91-103 vs 103-114)
- calculate_quick_wins() definida 2 veces (~320 y ~419)
- extract_top_problems() definida 2 veces (~362 y ~461)
- Python usa la segunda definición (sombrea la primera)

TAREAS:
1. Analizar ambas versiones de cada duplicado
2. Eliminar la primera ocurrencia (la muerta/sombreada)
3. Verificar brechas_reales en DiagnosticSummary
4. 4 tests de no-duplicación + regresión completa

CRITERIOS:
- 0 duplicados restantes
- 0 regresiones en suite completa
- import limpio funciona

VALIDACIONES:
- python -c "from modules.commercial_documents.data_structures import DiagnosticSummary, Scenario"
- pytest tests/ -v --tb=short  # SUITE COMPLETA
- python scripts/run_all_validations.py --quick
```
