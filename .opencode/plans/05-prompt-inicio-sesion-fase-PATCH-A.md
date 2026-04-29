# FASE-PATCH-A: Critical Bugs + Diagnostic Stubs + Unicode Fix

**ID**: FASE-PATCH-A
**Objetivo**: Corregir BUG-1 (ROI sin "X"), BUG-2 (beneficio neto $0), stubs H-3/H-4/H-5 (blog/speakable/ga4 siempre False), y crash Unicode en version_consistency_checker.py
**Dependencias**: Ninguna (primera fase del PATCH)
**Duración estimada**: ~45-60 min
**Skill**: iah-cli-phased-execution

---

## Contexto

La auditoría forense (ContextMv2.md + ContextMM.md) reveló bugs que afectan la credibilidad comercial de la propuesta:

- **BUG-1**: `v4_proposal_generator.py` L556 hace `.replace("X","")` sobre el ROI, eliminando la "X" del formato. El template v6 L98 muestra `${roi_6m}` resultando en `ROI: 0.2` en vez de `ROI: 0.2X`.
- **BUG-2**: La proyección mensual muestra beneficio neto $0 porque `pain_ratio=0.05` hace que `projected_monthly_gain == monthly_investment`. El documento NO explica qué es pain_ratio ni por qué el beneficio es $0.
- **H-3/H-4/H-5**: `v4_diagnostic_generator.py` tiene stubs que retornan siempre False sin evaluar: `blog_activo` (L1964), `speakable_schema` (L2030), `ga4_indirect` (L2083). El diagnóstico pierde puntos IAO por infraestructura nunca medida.
- **🔧 Unicode crash**: `scripts/version_consistency_checker.py` no tiene `sys.stdout.reconfigure(encoding="utf-8")`. Al imprimir emojis (✅, ⚠️) en Windows cp1252, crashea con UnicodeEncodeError. `log_phase_completion.py` ya tiene este fix (L40-46).

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-AMAZILIA-CORRECCION (1A/1B/1C) | ✅ Completada (2026-04-28) |

### Base Técnica Disponible

- `modules/commercial_documents/v4_proposal_generator.py` (~1418 líneas) — BUG-1 L556, BUG-2 L482-543
- `modules/commercial_documents/v4_diagnostic_generator.py` — H-3 L1964, H-4 L2030, H-5 L2083
- `scripts/version_consistency_checker.py` (303 líneas) — falta unicode fix
- `scripts/log_phase_completion.py` — referencia del patrón unicode fix (L40-46)
- Tests base: ~2363 funciones, 185 archivos, 0 regresiones
- CHANGELOG: 4.36.1 | VERSION.yaml: 4.36.0 (drift — se resuelve en PATCH-D)

---

## Tareas

### Tarea 1: Investigar bugs y stubs en código

**Objetivo**: Leer las líneas exactas y confirmar las causas raíz antes de modificar.

**Archivos a leer**:
- `modules/commercial_documents/v4_proposal_generator.py` L550-560 (BUG-1: .replace X)
- `modules/commercial_documents/v4_proposal_generator.py` L480-545 (BUG-2: pain_ratio + recovery_factor)
- `modules/commercial_documents/v4_diagnostic_generator.py` L1960-1970 (H-3: blog_activo)
- `modules/commercial_documents/v4_diagnostic_generator.py` L2025-2035 (H-4: speakable_schema)
- `modules/commercial_documents/v4_diagnostic_generator.py` L2078-2088 (H-5: ga4_indirect)
- `scripts/version_consistency_checker.py` L200-215 (main, sin unicode fix)
- `scripts/log_phase_completion.py` L39-46 (patrón del fix)

**Criterios de aceptación**:
- [ ] Confirmado que BUG-1 es `.replace("X","").strip()` en la línea exacta
- [ ] Confirmado que BUG-2 es `pain_ratio=0.05` causando `neto = 0`
- [ ] Confirmado que H-3/H-4/H-5 son asignaciones literales `= False` sin lógica de detección
- [ ] Confirmado que version_consistency_checker.py NO tiene `sys.stdout.reconfigure`

### Tarea 2: Fix BUG-1 + BUG-2 en v4_proposal_generator.py

**Objetivo**: Corregir el ROI y agregar explicación del pain_ratio.

**BUG-1 fix**:
```python
# L556 actual:
'roi_6m': roi_6_months.replace("X", "").strip(),

# Cambiar a:
'roi_6m': roi_6_months,  # Mantener el formato "0.2X" como lo genera _calculate_roi()
```

**BUG-2 fix** (2 opciones, elegir la más adecuada según código):

**Opción A (mínima — recomendada para PATCH)**: Agregar nota explicativa en `_prepare_template_data()` o en el template para la sección de proyección que explique:
- Qué es el pain_ratio (5% de la pérdida mensual recuperable en 6 meses)
- Por qué el beneficio neto mensual es bajo al inicio
- Que el ROI real se materializa a mediano plazo

**Opción B**: Si el código permite ajustar `pain_ratio` en `financial_scenarios.json` a un valor más representativo (ej: 0.15-0.20), hacerlo. Verificar que no rompa otros cálculos.

**Criterios de aceptación**:
- [ ] `roi_6m` en template data YA NO tiene `.replace("X","")`
- [ ] La propuesta generada muestra `ROI: 0.2X` (con X)
- [ ] La sección de proyección incluye explicación del pain_ratio O los números muestran beneficio > $0
- [ ] No se introducen errores de sintaxis

### Tarea 3: Fix H-3/H-4/H-5 en v4_diagnostic_generator.py + Unicode fix

**Objetivo**: Reemplazar stubs silenciosos por detección real o marcado explícito.

**Estrategia para H-3/H-4/H-5**: En vez de `= False` fijo, implementar detección básica:
- **H-3 (blog_activo)**: Buscar patrones de blog en el HTML scrapeado (`.blog`, `/blog/`, `wp-content`, artículos)
- **H-4 (speakable_schema)**: Verificar si el HTML contiene `speakable` en JSON-LD
- **H-5 (ga4_indirect)**: Verificar si el HTML contiene `gtag` o `G-` measurement ID

Si la detección no es viable en el alcance PATCH, cambiar `= False` por un marcador explícito tipo `"no_evaluado"` que el template renderice como "⚠️ No evaluado" en vez de un False silencioso.

**Unicode fix en version_consistency_checker.py**:

Copiar el patrón de `log_phase_completion.py` L39-46 e insertarlo después de los imports en `version_consistency_checker.py`, antes de `def main()`:

```python
# Fix encoding for Windows (cp1252 doesn't support Unicode symbols)
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
```

**Criterios de aceptación**:
- [ ] H-3/H-4/H-5 ya no son `= False` hardcodeados sin evaluación
- [ ] El diagnóstico muestra estado real o "No evaluado" explícito
- [ ] version_consistency_checker.py tiene el bloque unicode fix
- [ ] `python scripts/version_consistency_checker.py` no crashea en Windows

### Tarea 4: Ejecutar tests + documentación de fase

**Objetivo**: Verificar 0 regresiones y registrar la fase.

```bash
# Ejecutar tests relevantes
./venv/Scripts/python.exe -m pytest tests/commercial_documents/ -x -q --tb=short
./venv/Scripts/python.exe -m pytest tests/asset_generation/test_proposal_alignment.py -x -q

# Verificar unicode fix
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# Documentar fase
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-PATCH-A \
    --desc "Fix BUG-1 (ROI X), BUG-2 (pain_ratio explicacion), H-3/H-4/H-5 (stubs diagnosticos), unicode crash en version_consistency_checker" \
    --archivos-mod "modules/commercial_documents/v4_proposal_generator.py,modules/commercial_documents/v4_diagnostic_generator.py,scripts/version_consistency_checker.py" \
    --check-manual-docs
```

**Criterios de aceptación**:
- [ ] Tests pasan sin regresiones
- [ ] version_consistency_checker.py ejecuta sin crash (puede reportar drift — eso es esperado, se resuelve en PATCH-D)
- [ ] log_phase_completion.py ejecutado sin errores

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Tests de proposal generator | `tests/commercial_documents/` | Sin regresiones |
| Tests de proposal alignment | `tests/asset_generation/test_proposal_alignment.py` | Sin regresiones |
| version_consistency_checker | `scripts/version_consistency_checker.py` | Ejecuta sin UnicodeEncodeError |

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. Actualizar `dependencias-fases-v2.md`: marcar FASE-PATCH-A como ✅ Completada
2. Actualizar `06-checklist-implementacion-v2.md`: marcar items de PATCH-A
3. Actualizar `README-v2.md`: tabla de progreso

---

## Criterios de Completitud (CHECKLIST)

- [x] BUG-1 fix aplicado: `.replace("X","")` eliminado de L556
- [x] BUG-2 fix aplicado: pain_ratio explicado o ajustado
- [x] H-3 fix: blog_activo ya no es False fijo
- [x] H-4 fix: speakable_schema ya no es False fijo
- [x] H-5 fix: ga4_indirect ya no es False fijo
- [x] Unicode fix aplicado en version_consistency_checker.py
- [x] Tests pasan sin regresiones
- [x] log_phase_completion.py ejecutado

---

## Restricciones

- **NO modificar** `VERSION.yaml` (el version drift se resuelve en PATCH-D)
- **NO modificar** `CHANGELOG.md`
- **NO ejecutar** `v4complete` (eso es PATCH-C)
- **NO modificar** archivos fuera de: `v4_proposal_generator.py`, `v4_diagnostic_generator.py`, `version_consistency_checker.py`
- **Máximo 60 iteraciones** del agente
