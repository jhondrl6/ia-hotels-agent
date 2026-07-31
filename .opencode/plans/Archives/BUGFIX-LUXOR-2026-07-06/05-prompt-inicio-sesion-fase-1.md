# FASE-1: BUG-2 + BUG-1 — Quick Wins (Bajo Riesgo)

**ID**: FASE-1
**Objetivo**: Corregir BUG-2 (UnboundLocalError cosmético en FASE-K) y BUG-1 (lat/lng hardcoded a 0.0 en `_audit_competitors`).
**Dependencias**: Ninguna (primera fase del plan)
**Duración estimada**: 1-2 horas
**Skill**: `phased-project-executor`

---

## Contexto

Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1
Contexto origen: `.opencode/context/bugs_no_onboarding_luxor_2026-07-06.md`

Estos dos bugs son quick wins: cambios mínimos de código, bajo riesgo de regresión, alto valor inmediato.

### Estado de Fases Anteriores
- Primera fase del plan — sin dependencias previas.

### Base Técnica Disponible
- `main.py` — pipeline principal (BUG-2 en ~L1942)
- `modules/auditors/v4_comprehensive.py` — auditor comprehensivo (BUG-1 en L1159-1160, L799-800)
- `tests/test_google_places_client.py` — tests de Places API
- `tests/test_financial_breakdown.py` — tests de FinancialBreakdown

---

## Tareas

### T1: Fix BUG-2 — Eliminar `calc_result` UnboundLocalError en FASE-K

**Objetivo**: Remover la línea que referencia `calc_result` (variable que no existe en el scope de `main.py`).

**Archivos afectados**:
- `main.py` (~L1942)

**Causa raíz (verificada contra código vivo):**
- `main.py:1942` ejecuta: `print(f"   Source reliability: {calc_result.metadata.get('source_reliability', 'unknown')}")`
- `calc_result` NO existe en este scope. Es una variable del handler de harness (`harness_handlers.py:120`), no de `main.py`.
- El error se atrapa en L1943 except e imprime "FinancialBreakdown fallo".
- `financial_breakdown` YA fue asignado en L1939 (`_sc.calculate_breakdown`) ANTES del error.
- **Impacto real: ruido en log (warning falso), sin impacto en output.**

**Cambio esperado:**
- grep para `calc_result` en `main.py` cerca de L1942 (NO confiar en el número de línea — los line numbers están stale).
- Remover la línea entera `print(f"   Source reliability: {calc_result.metadata.get(...)}")` (no aporta nada: `financial_breakdown` ya tiene su propio `evidence_tier` y `disclaimer`).
- Alternativamente, si se quiere conservar el print, reemplazar `calc_result.metadata` por `financial_breakdown.evidence_tier` o similar referencia válida del scope.

**Verificación inmediata:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -n 'calc_result' main.py
# Debe mostrar: UNA sola línea (la que vamos a remover/editar)
# Post-fix: grep NO debe mostrar calc_result en main.py (o muestra la línea corregida)
```

**Criterios de aceptación:**
- [ ] `calc_result` no aparece en `main.py` (o aparece con referencia válida)
- [ ] No hay `UnboundLocalError` en el scope de FASE-K

---

### T2: Fix BUG-1 — Usar `gbp_result.lat/lng` en `_audit_competitors`

**Objetivo**: Reemplazar `lat=0.0, lng=0.0` hardcoded por `gbp_result.lat, gbp_result.lng` + validación de rango.

**Archivos afectados**:
- `modules/auditors/v4_comprehensive.py` (~L1159-1160)

**Causa raíz (verificada contra código vivo):**
- `v4_comprehensive.py:1159-1160` — `_audit_competitors()` pasa `lat=0.0, lng=0.0` hardcoded con comentario `# TODO: Get from geocoding`.
- Pero `gbp_result` SÍ tiene coords reales: `v4_comprehensive.py:799-800` asigna `lat=places_result.lat, lng=places_result.lng` desde Places API.
- El fix D1 ya añadió `lat`/`lng` a `GBPApiResult`. El campo existe, simplemente no se usa en `_audit_competitors`.

**Cambio esperado:**
1. grep para `lat=0.0` en `modules/auditors/v4_comprehensive.py` (NO confiar en L1159 — stale).
2. Reemplazar `lat=0.0, lng=0.0` por `lat=gbp_result.lat, lng=gbp_result.lng`.
3. **Validación adicional:** antes de la llamada a `search_nearby_lodging`, verificar que lat/lng sean válidos:
   - Si lat/lng son 0.0 o fuera de rango Colombia (lat 0-13, lng -82 a -66), `return []` sin llamar a `search_nearby_lodging` con coords nulas.

**Ejemplo de validación de rango:**
```python
# Validar coords antes de llamar search_nearby_lodging
if not gbp_result.lat or not gbp_result.lng:
    return []
if not (0 <= gbp_result.lat <= 13 and -82 <= gbp_result.lng <= -66):
    # Fuera de rango Colombia — no llamar API con coords inválidas
    return []
```

**Verificación inmediata:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
grep -n 'lat=0.0' modules/auditors/v4_comprehensive.py
# Post-fix: NO debe mostrar resultados (o muestra la nueva validación)
grep -n 'gbp_result.lat' modules/auditors/v4_comprehensive.py
# Post-fix: Debe mostrar la nueva línea usando gbp_result.lat
```

**Criterios de aceptación:**
- [ ] `lat=0.0` no aparece en `_audit_competitors`
- [ ] `gbp_result.lat` y `gbp_result.lng` se usan en la llamada a `search_nearby_lodging`
- [ ] Validación de rango implementada (coords 0.0 o fuera de Colombia → return [])

---

### T3: Agregar tests de regresión

**Objetivo**: Tests que validen que los fixes no se revierten en el futuro.

**Archivos afectados**:
- `tests/test_google_places_client.py` (o `tests/auditors/test_v4_comprehensive.py` — verificar cuál existe)
- `tests/test_financial_breakdown.py`

**Test BUG-1 (regresión):**
- `_audit_competitors` con `gbp_result.lat=4.8, lng=-75.7` debe llamar `search_nearby_lodging` con esos valores (mock `CompetitorAnalyzer`).
- Test edge: `gbp_result` con `lat=0.0` → retorna `[]` sin llamar API.

**Test BUG-2 (regresión):**
- Ejecutar FASE-K con datos reales → no debe imprimir warning de `calc_result`.
- `financial_breakdown` debe tener `evidence_tier` y `disclaimer` no nulos.

**Nota:** Adaptar al patrón de los tests existentes. Verificar cómo se mockean los datos necesarios.

**Criterios de aceptación:**
- [ ] Test BUG-1 agregado y pasando
- [ ] Test BUG-2 agregado y pasando (o test existente modificado para verificar ausencia del warning)

---

### T4: Ejecutar tests de regresión

**Comando:**
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/test_google_places_client.py tests/test_financial_breakdown.py -v
```

**Criterios de éxito:**
- ✅ Todos los tests existentes pasan sin cambios
- ✅ Nuevos tests de regresión pasan
- ✅ Sin errores de importación o mock

---

## Post-Ejecución: log_phase_completion.py

**Comando (ejecutar SOLO si T1-T4 completan exitosamente):**
```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-1 --desc BUG2_calc_result_fix_plus_BUG1_lat_lng_competitors --archivos-mod main.py,modules/auditors/v4_comprehensive.py --tests 2 --check-manual-docs"
```

---

## Actualizar Documentación

**Después de log_phase_completion.py:**

1. **CHANGELOG.md** (agregar entrada):
```markdown
## [4.60.1] - Bugfixes Luxor v4complete — En progreso

### Cambios Implementados
- **FASE-1 BUG-2**: Removido `calc_result` UnboundLocalError en FASE-K (main.py)
- **FASE-1 BUG-1**: `_audit_competitors` ahora usa `gbp_result.lat/lng` en lugar de 0.0 (v4_comprehensive.py)
```

2. **GUIA_TECNICA.md** (agregar nota técnica):
```markdown
### Notas de Cambios v4.60.1 - FASE-1

**Problema:** BUG-2: `calc_result` no existe en scope de main.py (warning falso). BUG-1: lat/lng hardcoded a 0.0 en `_audit_competitors`.
**Solución:** BUG-2: Removida línea que referencia `calc_result`. BUG-1: Usar `gbp_result.lat/lng` + validación de rango Colombia.
**Módulos afectados:** `main.py`, `modules/auditors/v4_comprehensive.py`
**Backwards compatibility:** ✅ Sin breaking changes
**Tests:** 2 tests de regresión nuevos
```

3. **09-documentacion-post-proyecto.md** (acumular datos):
Editar sección correspondiente con datos de FASE-1

---

## Criterios de Completitud (CHECKLIST)

- [ ] **T1**: `calc_result` removido/corregido en `main.py`
- [ ] **T2**: `gbp_result.lat/lng` usado en `_audit_competitors` + validación de rango
- [ ] **T3**: Tests de regresión agregados (BUG-1 y BUG-2)
- [ ] **T4**: `pytest tests/test_google_places_client.py tests/test_financial_breakdown.py -v` → all pass
- [ ] **log_phase_completion.py**: Ejecutado exitosamente
- [ ] **Docs cascade**: CHANGELOG, GUIA_TECNICA, 09-documentacion actualizados

---

## Restricciones

- **NO ejecutar v4complete** (eso es FASE-5)
- **NO modificar `modules/auditors/llm_mention_checker.py`** (eso es FASE-2)
- **NO modificar FASE 3.6 del pipeline en main.py** (eso es FASE-3 — solo tocar L1942)
- **NO modificar `seo_elements_detector.py`** (eso es FASE-4)
- **Máximo 60 iteraciones** del agente
- **Verificar contra código vivo** antes de aplicar patch (los line numbers pueden estar stale)

---

## Budget de Iteraciones Estimado

```
Fijos:
  - Leer plan + verificar estado: ~3 iters
  - Investigar código/archivos: ~5-10 iters
  - log_phase_completion.py + docs cascade: ~10 iters
  Total fijo: ~18-23 iters

Específico:
  - T1 (fix BUG-2): ~3-5 iters
  - T2 (fix BUG-1): ~5-8 iters
  - T3 (agregar tests): ~10-15 iters
  - T4 (run tests): ~2-3 iters
  Total específico: ~20-31 iters

Total estimado: 38-54 iters (dentro del límite de 60)
```

**Modo de ejecución:** Agente principal DIRECTO (código puro, sin comandos largos)

---

## Recuperación en Caso de Agotamiento

Si el agente alcanza 60 iteraciones:
1. Guardar estado actual de los fixes (si ya se aplicaron)
2. Marcar fase como `⏳ INCOMPLETA` en `dependencias-fases.md`
3. Documentar checkpoint: qué tarea se completó, cuál falta
4. Retomar en nueva sesión desde el checkpoint

---

## Checklist Final

- [ ] BUG-2: `calc_result` no aparece en `main.py` (o referencia válida)
- [ ] BUG-1: `lat=0.0` no aparece en `_audit_competitors`
- [ ] BUG-1: Validación de rango Colombia implementada
- [ ] Tests de regresión BUG-1 y BUG-2 agregados
- [ ] Todos los tests pasan
- [ ] log_phase_completion.py ejecutado
- [ ] CHANGELOG.md actualizado
- [ ] GUIA_TECNICA.md actualizado
- [ ] 09-documentacion-post-proyecto.md actualizado
