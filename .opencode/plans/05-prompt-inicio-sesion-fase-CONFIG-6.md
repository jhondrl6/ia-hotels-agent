# FASE-CONFIG-6: Config Reconnect + Deprecación Módulos Huérfanos (CR-6 + H6)

**Plan:** FEATURE-CONFIG-EXTRACTION v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.9.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~45 iteraciones
**Dependencias:** FASE-CONFIG-3A, 3B, 4, 5 (todos los YAML ya creados)
**Fase siguiente:** FASE-CONFIG-7

---

## Contexto

**Fuente:** `.opencode/context/TECHNICAL_DEBT_2026-04-29.md` §HALLAZGO 5 + §HALLAZGO 4 (revisado)

### Problema 1: CR-6 — Disconnect Config/Código

`config/settings.yaml` existe con datos de pricing PERO los generadores usan valores hardcodeados o de los nuevos YAML. Hay duplicación entre settings.yaml y los 6 YAML creados en fases anteriores.

### Problema 2: H6 — Módulos Huérfanos (NUEVO, descubierto 2026-04-29 17:00)

Investigación forense de imports reveló 4 módulos completamente huérfanos:

| Módulo | Líneas | Importado por | Realidad |
|--------|--------|--------------|----------|
| `modules/analytics/profound_client.py` | 168 | SOLO `aeo_metrics_gen.py` (también huérfano) | Stub puro — nunca instanciado en pipeline |
| `modules/analytics/semrush_client.py` | 121 | SOLO `aeo_metrics_gen.py` | Stub puro — GSC/GA4/PageSpeed cubren sus funciones |
| `modules/analytics/data_aggregator.py` | 320 | NADIE (0 imports externos) | Código muerto completo |
| `modules/delivery/generators/aeo_metrics_gen.py` | 238 | NADIE (0 callers) | Código muerto completo |

Además, hay bugs colaterales causados por estos stubs:
- **`AnalyticsStatus.is_any_missing()`** siempre retorna True (porque `profound_available=False` nunca se actualiza)
- **`AnalyticsStatus`** tiene campos `profound_*` y `semrush_*` que siempre están en default
- **`modules/analytics/__init__.py`** re-exporta `ProfoundClient`, `SemrushClient`, `AnalyticsAggregator`, `UnifiedAnalyticsData`, `ConfidenceLevel` — clases que NUNCA se usan
- **`_check_analytics_status()`** docstring dice verificar Profound/Semrush pero el código solo verifica GA4 y GSC
- **`_build_transparency_section()`** correctamente ignora Profound/Semrush (solo lista GA4, GSC, Audit, Places)

---

## Tareas Específicas

### Tarea 1: Auditar settings.yaml vs código + identificar TODOS los módulos huérfanos

**1A. Auditoría settings.yaml:**
- Leer `config/settings.yaml` completamente
- Comparar cada parámetro con los 6 YAML nuevos:
  - `config/pricing.yaml`
  - `config/scenarios.yaml`
  - `config/financial_defaults.yaml`
  - `config/fallbacks.yaml`
  - `config/commercial.yaml`
  - `config/regional_benchmarks.yaml`
- Identificar parámetros DUPLICADOS entre settings.yaml y los nuevos YAML
- Identificar parámetros ÚNICOS de settings.yaml que deban migrarse

**1B. Auditoría de módulos huérfanos:**
```bash
# Verificar imports de cada módulo analytics
for f in modules/analytics/*.py; do
  name=$(basename "$f" .py)
  [ "$name" = "__init__" ] && continue
  count=$(grep -rn "from modules.analytics.$name import\|from modules.analytics import.*$name" modules/ main.py --include="*.py" | grep -v "modules/analytics/" | wc -l)
  echo "$name: $count imports externos"
done

# Verificar si aeo_metrics_gen es llamado
grep -rn "aeo_metrics_gen\|generate_aeo_metrics" modules/ main.py --include="*.py" | grep -v "aeo_metrics_gen.py"
```

### Tarea 2: Reconectar settings.yaml con generadores + Deprecar módulos huérfanos

**2A. Reconexión config:**
- **Regla:** Cada parámetro existe en UN solo archivo YAML
- Si settings.yaml tiene `package_prices` y pricing.yaml también → eliminar de settings.yaml
- Si settings.yaml tiene datos no migrados → migrar al YAML correspondiente
- Agregar header en settings.yaml:
  ```yaml
  # ⚠️ LEGACY — Este archivo está deprecado para parámetros de generación.
  # Los parámetros activos están en:
  #   config/pricing.yaml, config/scenarios.yaml, config/financial_defaults.yaml,
  #   config/fallbacks.yaml, config/commercial.yaml, config/regional_benchmarks.yaml
  # Se mantiene por backwards compatibility con módulos no migrados.
  ```
- Verificar: generadores NO importan settings.yaml directamente

**2B. Deprecación de módulos huérfanos:**

Para CADA uno de los 4 módulos huérfanos, aplicar este patrón:

```python
# Al inicio del archivo, después de imports:
import warnings
warnings.warn(
    "Este módulo está deprecado y no se usa en el pipeline v4complete. "
    "Sus funciones son cubiertas por GoogleSearchConsoleClient, "
    "GoogleAnalyticsClient, y PageSpeedClient. "
    "Se eliminará en una versión futura.",
    DeprecationWarning,
    stacklevel=2
)
```

Actualizar docstring de cada módulo:
```
ESTADO: DEPRECADO — No usado en pipeline v4complete.
MOTIVO: Funciones cubiertas por GoogleSearchConsoleClient (tráfico orgánico),
  GoogleAnalyticsClient (GA4), y PageSpeedClient (SEO técnico).
PLAN: Eliminar en v5.0.0.
```

**2C. Limpiar `modules/analytics/__init__.py`:**
- Eliminar imports de `ProfoundClient`, `SemrushClient`, `AnalyticsAggregator`, `UnifiedAnalyticsData`, `ConfidenceLevel`
- Eliminar de `__all__`
- Mantener imports de `GoogleAnalyticsClient` y `GoogleSearchConsoleClient` (estos SÍ se usan)
- Agregar comentario: "Solo se exportan clientes activos usados en v4complete"

### Tarea 3: Corregir bugs colaterales en AnalyticsStatus

**3A. Corregir `AnalyticsStatus.is_any_missing()`:**
```python
# data_models/analytics_status.py
def is_any_missing(self) -> bool:
    """True si ALGUNA fuente ACTIVA no está disponible."""
    # Solo verificar fuentes realmente usadas en el pipeline
    return (not self.ga4_available or not self.gsc_available)
```

**3B. Marcar campos de stubs como deprecados:**
Agregar comentario en los campos `profound_*` y `semrush_*`:
```python
# DEPRECADO: Profound/Semrush son stubs no usados en pipeline.
# Se mantienen por backwards compatibility. Eliminar en v5.0.0.
profound_available: bool = False
```

**3C. Actualizar docstring de `_check_analytics_status()`:**
Corregir de "Retorna AnalyticsStatus con ga4/profound/semrush availability" a "Retorna AnalyticsStatus con ga4/gsc availability (Profound/Semrush deprecados)".

**3D. Verificar `_build_transparency_section()`:**
- Este método YA es correcto — solo lista GA4, GSC, Audit, Places
- Confirmar que con `is_any_missing()` corregido, la sección solo aparece cuando GA4 o GSC faltan

### Tarea 4: Tests de regresión

**4A. Tests de config reconnect:**
- Test: Cambio en pricing.yaml → reflejado en pricing_calculator
- Test: Cambio en commercial.yaml → reflejado en propuesta
- Test: settings.yaml con header de deprecación
- Test: `grep -rn "settings.yaml" modules/commercial_documents/` = 0 resultados (o solo comentarios)

**4B. Tests de módulos deprecados:**
- Test: Importar ProfoundClient emite DeprecationWarning
- Test: Importar SemrushClient emite DeprecationWarning
- Test: Importar AnalyticsAggregator emite DeprecationWarning
- Test: `modules/analytics/__init__.py` NO exporta clases deprecadas
- Test: `from modules.analytics import GoogleAnalyticsClient` sigue funcionando

**4C. Tests de AnalyticsStatus corregido:**
- Test: GA4 disponible + GSC disponible → is_any_missing() = False
- Test: GA4 no disponible → is_any_missing() = True
- Test: is_complete() solo verifica GA4 + GSC (no profound/semrush)
- Test: `_build_transparency_section()` no aparece cuando ambas fuentes están OK

---

## Archivos Involucrados

| Archivo | Tipo | Acción |
|---------|------|--------|
| `config/settings.yaml` | MODIFICAR | Header de deprecación, eliminar duplicados |
| `modules/analytics/profound_client.py` | MODIFICAR | Agregar DeprecationWarning + docstring |
| `modules/analytics/semrush_client.py` | MODIFICAR | Agregar DeprecationWarning + docstring |
| `modules/analytics/data_aggregator.py` | MODIFICAR | Agregar DeprecationWarning + docstring |
| `modules/delivery/generators/aeo_metrics_gen.py` | MODIFICAR | Agregar DeprecationWarning + docstring |
| `modules/analytics/__init__.py` | MODIFICAR | Limpiar exports, solo GA4 + GSC |
| `data_models/analytics_status.py` | MODIFICAR | Corregir is_any_missing(), marcar campos deprecados |
| `modules/commercial_documents/v4_diagnostic_generator.py` | MODIFICAR | Actualizar docstring _check_analytics_status() |

---

## Criterios de Completitud

**Config:**
- [ ] settings.yaml tiene header de deprecación claro
- [ ] Cero parámetros duplicados entre settings.yaml y YAML nuevos
- [ ] Generadores NO importan settings.yaml directamente
- [ ] Cambio en YAML → reflejado en output

**Deprecación:**
- [ ] 4 módulos huérfanos tienen DeprecationWarning al importarse
- [ ] Docstrings actualizados con motivo y plan de eliminación
- [ ] `__init__.py` solo exporta GA4 y GSC (no stubs)
- [ ] `from modules.analytics import GoogleAnalyticsClient` funciona

**Bugs corregidos:**
- [ ] `AnalyticsStatus.is_any_missing()` solo verifica GA4 + GSC
- [ ] `_check_analytics_status()` docstring corregido
- [ ] `_build_transparency_section()` solo aparece cuando GA4 o GSC faltan (no por stubs)

**Tests:**
- [ ] Tests de config reconnect (3 tests)
- [ ] Tests de módulos deprecados (4 tests)
- [ ] Tests de AnalyticsStatus corregido (3 tests)

---

## Restricciones

- **NO eliminar** los archivos deprecados (solo marcar) — backwards compatibility
- **NO eliminar** settings.yaml (otros módulos pueden usarlo)
- **NO modificar** lógica de scoring (solo fuente de datos + cleanup)
- **NO ejecutar** v4complete
- **NO crear** nuevos YAML
- **Máximo 60 iteraciones** (R2)

---

## Post-Ejecución

```bash
mkdir -p evidence/fase-config-6
cp config/settings.yaml evidence/fase-config-6/
cp modules/analytics/__init__.py evidence/fase-config-6/
cp data_models/analytics_status.py evidence/fase-config-6/
cp modules/analytics/profound_client.py evidence/fase-config-6/
cp modules/analytics/semrush_client.py evidence/fase-config-6/

venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-CONFIG-6 \
    --desc "Config reconnect + deprecación módulos huérfanos: settings.yaml depurado, 4 módulos deprecados (profound, semrush, data_aggregator, aeo_metrics_gen), AnalyticsStatus.is_any_missing() corregido, __init__.py limpiado." \
    --archivos-mod "config/settings.yaml,modules/analytics/__init__.py,data_models/analytics_status.py,modules/analytics/profound_client.py,modules/analytics/semrush_client.py,modules/analytics/data_aggregator.py,modules/delivery/generators/aeo_metrics_gen.py,modules/commercial_documents/v4_diagnostic_generator.py" \
    --tests "10" \
    --check-manual-docs
```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-CONFIG-7.md siguiendo .agents/workflows/phased_project_executor.md
```
