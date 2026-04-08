# FASE-F: Limpieza de Zombie References + 6 Code Smells

> **Skill**: `phased_project_executor`
> **Version Base**: 4.25.3 (post-FASE-D)
> **Tests Base**: 1782 funciones (baseline post-FASE-D)
> **Dependencias**: FASE-D (debe estar completada)
> **Archivos Principales**: 4 archivos (templates + generators + benchmarks)
> **Sesion**: 1 fase = 1 sesion

---

## CONTEXTO

FASE-C corrigio 4 bugs criticos. FASE-D corrigio 5 bugs medios + serializacion seo_elements. FASE-E corrigio la reutilizacion HTML para OG detection. Esta fase limpia referencias zombie a IAO/Voice Readiness eliminados en FASE-CAUSAL-01 y corrige 6 code smells menores en `v4_diagnostic_generator.py`.

Los placeholders `${iao_score}`, `${voice_readiness_score}`, `${iao_status}`, `${voice_readiness_status}` persisten en templates pero ningun codigo Python vivo los popula. Ademas, `diagnostico_ejecutivo.md` usa `.format()` (no `safe_substitute`), lo que causa **KeyError en runtime** si se ejecuta con datos que no incluyen `iao_score`.

---

## TAREAS A EJECUTAR

### ZMB-1: Eliminar fila IAO de diagnostico_ejecutivo.md (CRITICO)

**Ubicacion**: `templates/diagnostico_ejecutivo.md` linea 15
**Sintoma**: `.format()` crashea con KeyError porque `report_builder.py` NO pasa `iao_score`, `iao_comparativo`, ni `iao_icon` en el dict.
**Fix**: Eliminar la fila IAO completa del template.

### ZMB-2: Eliminar filas IAO + Voice Readiness de diagnostico_v4_template.md

**Ubicacion**: `templates/diagnostico_v4_template.md` lineas 41-42
**Sintoma**: Placeholders `${iao_score}`, `${voice_readiness_score}` sin reemplazo. `safe_substitute` no crashea pero genera texto basura.
**Fix**: Eliminar las 2 filas del template.

### ZMB-3: Limpiar iao_score del dict en _get_analytics_fallback()

**Ubicacion**: `modules/commercial_documents/v4_diagnostic_generator.py` (~linea 1486, 1557)
**Sintoma**: `iao_score` en fallback dict se calcula pero nunca se consume.
**Fix**: Eliminar la clave `iao_score` del dict retornado por `_get_analytics_fallback()`.

### ZMB-4: Evaluar iao_score en benchmarks.py

**Ubicacion**: `modules/utils/benchmarks.py:33`
**Sintoma**: `iao_score: 18` hardcoded sin consumidor.
**Fix**: Eliminar la key `iao_score` del benchmark dict.

### MEN-1: Import redundante de datetime

**Ubicacion**: `v4_diagnostic_generator.py` linea 443
**Problema**: `from datetime import datetime` redundante (ya importado linea 11).
**Fix**: Eliminar la linea 443.

### MEN-2: Scores calculados 2 veces

**Ubicacion**: `v4_diagnostic_generator.py` lineas 508-515
**Problema**: Scores calculados 2 veces cada uno en vez de guardar en variable.
**Fix**: Guardar en variable temporal y reutilizar.

### MEN-3: _format_scenario_amount() inconsistente

**Ubicacion**: `v4_diagnostic_generator.py` linea 490
**Problema**: `_format_scenario_amount()` inconsistente con `format_cop()` de otros escenarios.
**Fix**: Unificar a `format_cop()`.

### MEN-4: audit_result.competitors sin hasattr() guard

**Ubicacion**: `v4_diagnostic_generator.py` lineas 1214/1273/1278
**Problema**: `audit_result.competitors` sin `hasattr()` guard (fragil ante refactor). Otras lineas (1096-1098) ya tienen el guard.
**Fix**: Agregar `hasattr(audit_result, 'competitors')` como en 1096-1098.

### MEN-5: print() en lugar de logging

**Ubicacion**: `v4_diagnostic_generator.py` linea 1680
**Problema**: `print()` en lugar de `logging.warning()`.
**Fix**: Cambiar a `logging.warning()`.

### MEN-6: Import re dentro de un loop

**Ubicacion**: `v4_diagnostic_generator.py` linea 1822
**Problema**: `import re` dentro de un loop -- se ejecuta cada iteracion.
**Fix**: Mover `import re` a los imports del modulo.

### MEN-7: Expresion ternaria con precedencia ambigua

**Ubicacion**: `v4_diagnostic_generator.py` linea 1615
**Problema**: Expresion ternaria con precedencia ambigua -- dificil de leer.
**Fix**: Refactorizar con parentesis claros.

---

## PLAN DE EJECUCION

### Paso 1: Verificacion pre-fix (5 min)

1. Confirmar que FASE-D fue completada
2. Verificar lineas exactas de cada ZMB/MEN en el archivo actual
3. Confirmar que `diagnostico_ejecutivo.md` usa `.format()` (no `safe_substitute`)
4. Confirmar que `iao_score` no tiene consumidores activos
5. Ejecutar test baseline: `python -m pytest tests/ -x --tb=short -q 2>&1 | tail -5`

### Paso 2: Aplicar fixes (15 min)

Aplicar en orden, de menor riesgo a mayor:

| Orden | Tarea | Archivo | Cambio | Riesgo |
|-------|-------|---------|--------|--------|
| 1 | ZMB-1 | diagnostico_ejecutivo.md:15 | Eliminar fila IAO | Bajo |
| 2 | ZMB-2 | diagnostico_v4_template.md:41-42 | Eliminar filas IAO+Voice | Bajo |
| 3 | ZMB-3 | v4_diagnostic_generator.py:~1486 | Limpiar iao_score dict | Bajo |
| 4 | ZMB-4 | benchmarks.py:33 | Eliminar iao_score key | Bajo |
| 5 | MEN-1 | v4_diagnostic_generator.py:443 | Eliminar import dup | Bajo |
| 6 | MEN-6 | v4_diagnostic_generator.py:1822 | Mover import re | Bajo |
| 7 | MEN-5 | v4_diagnostic_generator.py:1680 | print -> logging | Bajo |
| 8 | MEN-7 | v4_diagnostic_generator.py:1615 | Parentesis ternaria | Bajo |
| 9 | MEN-4 | v4_diagnostic_generator.py:1214/1273/1278 | hasattr() guard | Bajo |
| 10 | MEN-2 | v4_diagnostic_generator.py:508-515 | Variable temporal | Bajo |
| 11 | MEN-3 | v4_diagnostic_generator.py:490 | Unificar format_cop | Bajo |

### Paso 3: Validacion post-fix (10 min)

```bash
# Validacion rapida del ecosistema
python scripts/run_all_validations.py --quick

# Tests de regresion completos
python -m pytest tests/ -x --tb=short -q
```

### Paso 4: Verificacion manual (5 min)

1. **ZMB-1**: Confirmar que `diagnostico_ejecutivo.md` NO tiene fila IAO
2. **ZMB-2**: Confirmar que `diagnostico_v4_template.md` NO tiene placeholders IAO/Voice
3. **ZMB-3**: Confirmar que `_get_analytics_fallback()` NO retorna `iao_score`
4. **ZMB-4**: Confirmar que `benchmarks.py` NO tiene `iao_score`
5. **MEN-1..7**: Verificar cada fix segun ubicacion

### Paso 5: Post-ejecucion (5 min)

1. Marcar checklist de completitud (ver `06-checklist-implementacion.md`)
2. Actualizar `dependencias-fases.md` con estado FASE-F
3. Ejecutar: `python scripts/log_phase_completion.py --fase FASE-F`
4. Commit: `git add -A && git commit -m "fix(FASE-F): remove zombie IAO/voice refs + fix 7 code smells in v4_diagnostic_generator"`

### Paso 6: Validacion Final (post-FASE-F)

```bash
# Validacion E2E con hotel de referencia
./venv/Scripts/python.exe main.py v4complete --url https://www.hotelvisperas.com/es
```

---

## CRITERIOS DE COMPLETITUD

### Checklist de Verificacion

- [ ] **F1**: Fila IAO eliminada de `diagnostico_ejecutivo.md`
- [ ] **F2**: Filas IAO + Voice Readiness eliminadas de `diagnostico_v4_template.md`
- [ ] **F3**: `iao_score` eliminado de `_get_analytics_fallback()` dict
- [ ] **F4**: `iao_score` eliminado de `benchmarks.py`
- [ ] **F5**: Import redundante datetime eliminado (MEN-1)
- [ ] **F6**: Scores calculados 1 sola vez (MEN-2)
- [ ] **F7**: `format_cop()` unificado (MEN-3)
- [ ] **F8**: `hasattr()` guard en competitors (MEN-4)
- [ ] **F9**: `print()` reemplazado por `logging.warning()` (MEN-5)
- [ ] **F10**: `import re` movido a imports del modulo (MEN-6)
- [ ] **F11**: Ternaria refactorizada con parentesis (MEN-7)
- [ ] **F12**: `run_all_validations.py --quick` pasa sin errores
- [ ] **F13**: Todos los tests pasan (sin regresion vs FASE-D)
- [ ] **F14**: `log_phase_completion.py --fase FASE-F` ejecutado
- [ ] **F15**: Commit realizado con mensaje descriptivo
- [ ] **F16**: v4complete con https://www.hotelvisperas.com/es ejecutado (validacion final)

### Condiciones de Exito

| Criterio | Condicion |
|----------|-----------|
| Tests pasan | >= baseline post-FASE-D (sin regresion) |
| Validaciones | `--quick` sin errores |
| Bugs corregidos | 4/4 zombies + 7/7 code smells |
| Sin nuevos fallos | 0 nuevos test failures |
| Validacion E2E | v4complete https://www.hotelvisperas.com/es exitoso |

### Condiciones de Rollback

Si algo falla:
```bash
git stash
git stash drop
# Revisar error y reintentar
```

---

## ARCHIVOS AFECTADOS

| Archivo | Tipo | Cambio |
|---------|------|--------|
| `templates/diagnostico_ejecutivo.md` | MODIFICAR | Eliminar fila IAO (ZMB-1) |
| `templates/diagnostico_v4_template.md` | MODIFICAR | Eliminar filas IAO+Voice (ZMB-2) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | ZMB-3 + MEN-1..7 (~20 lineas) |
| `modules/utils/benchmarks.py` | MODIFICAR | ZMB-4 (1 linea) |

## ARCHIVOS DE REFERENCIA (solo lectura)

| Archivo | Uso |
|---------|-----|
| `modules/commercial_documents/report_builder.py` | Confirmar que NO pasa iao_score |
| `templates/diagnostico_ejecutivo.md` | Confirmar uso de .format() |
| `tests/` | Baseline y validacion post-fix |

---

## NOTAS

- ZMB-1 es CRITICO: si `diagnostico_ejecutivo.md` se ejecuta con `.format()`, crashea con KeyError.
- ZMB-2 es de baja severidad: `safe_substitute` no crashea pero genera texto basura `${iao_score}`.
- MEN-1..7 son code smells que degradan mantenibilidad sin afectar produccion directamente.
- FASE-F es la ultima fase antes de la validacion final con v4complete.
- La dependencia con FASE-D es por confianza: el generador debe estar limpio antes de tocar templates.
