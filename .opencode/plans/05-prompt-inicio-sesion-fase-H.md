# FASE-H: Performance Cache + Cleanup

**ID**: FASE-H
**Objetivo**: Agregar caché a `_identify_brechas()` (llamado 9x por generate) y limpiar mapping muerto `pain_to_type`
**Dependencias**: FASE-G completada (dual source resuelto)
**Duración estimada**: 1.5-2 horas
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema Detectado

`_identify_brechas()` se llama 9 veces durante una única ejecución de `generate()` en `v4_diagnostic_generator.py`:
- Líneas 1539, 1546, 1557, 1564, 1572, 1581, 1591, 1609, 1923

Cada llamada re-evalúa 10 condiciones y reconstruye la lista completa. Como `audit_result` es inmutable durante la ejecución, el resultado es idéntico en las 9 llamadas — cálculo redundante.

Adicionalmente, el mapeo `pain_to_type` (línea ~1931) incluye `low_ia_readiness` que nunca es emitido por `_identify_brechas()` — entrada muerta.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-F | ✅ Completada |
| FASE-G | ✅ Completada |

### Base Técnica Disponible
- `_identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]` — línea 1767
- `generate()` llama múltiples métodos internos que cada uno llama a `_identify_brechas()`
- `pain_to_type` dict — líneas 1924-1936

---

## Tareas

### Tarea 1: Agregar caché a _identify_brechas

**Objetivo**: Cachear el resultado de `_identify_brechas()` para evitar 9 llamadas redundantes

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`

**Implementación**:

Agregar un caché simple basado en `id(audit_result)`:

```python
def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
    """Detecta brechas reales desde audit_result. Cacheado por instancia."""
    # Cache check
    cache_key = id(audit_result)
    if hasattr(self, '_brechas_cache') and self._brechas_cache_key == cache_key:
        return self._brechas_cache

    brechas = []
    # ... lógica existente sin cambios ...

    # Sort by impacto descending
    brechas.sort(key=lambda x: x['impacto'], reverse=True)

    # Store cache
    self._brechas_cache = brechas
    self._brechas_cache_key = cache_key
    return brechas
```

**Alternativa más simple** (recomendada si generate() es single-use):

```python
def _identify_brechas(self, audit_result: V4AuditResult) -> List[Dict[str, Any]]:
    """Detecta brechas reales. Cacheado durante generate()."""
    if hasattr(self, '_cached_brechas') and self._cached_brechas is not None:
        return self._cached_brechas

    brechas = []
    # ... lógica existente ...

    brechas.sort(key=lambda x: x['impacto'], reverse=True)
    self._cached_brechas = brechas
    return brechas
```

Y limpiar caché al inicio de `generate()`:
```python
def generate(self, ...):
    self._cached_brechas = None  # Reset cache per generate() call
    # ... resto de generate() ...
```

**Criterios de aceptación**:
- [ ] `_identify_brechas()` se ejecuta máximo 1 vez por llamada a `generate()`
- [ ] El resultado es idéntico al comportamiento sin caché
- [ ] El caché se limpia entre llamadas a `generate()` (no stale data)
- [ ] Verificar con un counter que el cuerpo de `_identify_brechas` se ejecuta 1 vez (no 9)

### Tarea 2: Limpiar pain_to_type muerto

**Objetivo**: Remover entrada `low_ia_readiness` de `pain_to_type` ya que nunca es emitida

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (~línea 1931)

**Criterios de aceptación**:
- [ ] `low_ia_readiness` removido de `pain_to_type`
- [ ] Verificar que nada referencia `low_ia_readiness` como key de pain_to_type

### Tarea 3: Normalizar convenciones de loop en _build_brechas_section

**Objetivo**: Unificar las convenciones de indexación entre `_build_brechas_section` y `_build_brechas_resumen_section`

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py`

**Problema**:
- `_build_brechas_section` usa `enumerate(brechas, 1)` + `i-1` (1-based display, 0-based index)
- `_build_brechas_resumen_section` usa `enumerate(brechas)` + `i` (0-based todo)

**Fix**: Ambos usan `enumerate(brechas, 1)` + `i-1` para indexación en métodos helper, para consistencia.

**Criterios de aceptación**:
- [ ] Ambos métodos usan la misma convención de loop
- [ ] Tests existentes pasan sin cambios

### Tarea 4: Tests de performance y cleanup

**Tests a crear**:

1. `test_identify_brechas_cached_once`: Verificar que el cuerpo se ejecuta 1 vez con mock counter
2. `test_cache_cleared_between_generates`: Dos llamadas a generate() producen resultados independientes
3. `test_no_low_ia_readiness_in_pain_to_type`: Verificar entrada muerta removida
4. `test_loop_conventions_consistent`: Ambos _build methods producen índices correctos

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasando
- [ ] 0 regresiones

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_identify_brechas_cached_once` | `tests/commercial_documents/test_diagnostic_brechas.py` | 1 ejecución, no 9 |
| `test_cache_cleared_between_generates` | `tests/commercial_documents/test_diagnostic_brechas.py` | Sin stale data |
| `test_no_low_ia_readiness_in_pain_to_type` | `tests/commercial_documents/test_diagnostic_brechas.py` | Key no existe |
| `test_loop_conventions_consistent` | `tests/commercial_documents/test_diagnostic_brechas.py` | Índices correctos |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_brechas.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

Al finalizar esta fase, actualizar INMEDIATAMENTE:

1. **`dependencias-fases.md`**: Marcar FASE-H como ✅ Completada
2. **`06-checklist-implementacion.md`**: Marcar items de FASE-H como ✅
3. **`09-documentacion-post-proyecto.md`**: Sección A, D, E
4. **`scripts/log_phase_completion.py`**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-H \
    --desc "Cache for _identify_brechas (9x→1x) + pain_to_type cleanup + loop normalization" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: 4/4 cache tests exitosos
- [ ] **Tests existentes pasan**: 0 regresiones en suite completa
- [ ] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa
- [ ] **Caché funciona**: _identify_brechas ejecuta 1x, no 9x
- [ ] **Caché se limpia**: Entre generate() calls no hay stale data
- [ ] **Mapping muerto removido**: low_ia_readiness no está en pain_to_type
- [ ] **Loops normalizados**: Ambos _build methods usan misma convención
- [ ] **Post-ejecución completada**: dependencias, checklist, docs actualizados

---

## Restricciones

- NO modificar la lógica de detección de brechas (condiciones, pesos) — solo agregar caché
- NO cambiar la firma de `_identify_brechas()`
- NO modificar archivos fuera de `v4_diagnostic_generator.py` y tests
- Preservar comportamiento idéntico post-caché

---

## Prompt de Ejecución

```
Actúa como ingeniero Python senior especializado en optimización.

OBJETIVO: Cachear _identify_brechas (9x→1x) + cleanup.

CONTEXTO:
- v4_diagnostic_generator.py: _identify_brechas() llamado 9 veces por generate()
- audit_result es inmutable durante generate(), resultado siempre idéntico
- pain_to_type tiene entrada muerta: low_ia_readiness
- _build_brechas_section y _build_brechas_resumen_section usan convenciones inconsistentes

TAREAS:
1. Agregar caché a _identify_brechas con reset en generate()
2. Remover low_ia_readiness de pain_to_type
3. Normalizar convención de loops (ambos enumerate(brechas, 1) + i-1)
4. 4 tests nuevos

CRITERIOS:
- _identify_brechas se ejecuta 1 vez, no 9
- Caché se limpia entre generate() calls
- 0 regresiones

VALIDACIONES:
- pytest tests/commercial_documents/test_diagnostic_brechas.py -v
- python scripts/run_all_validations.py --quick
```
