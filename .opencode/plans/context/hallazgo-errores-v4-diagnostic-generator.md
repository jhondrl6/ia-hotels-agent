# Hallazgo: Errores en v4_diagnostic_generator.py

**Fecha**: 2026-04-08
**Archivo**: `modules/commercial_documents/v4_diagnostic_generator.py`
**Lineas**: 2147
**Estado**: Pendiente de fix

---

## CRITICOS (afectan produccion)

### BUG-1: `logging` sin import -- NameError en runtime
- **Linea**: 1460
- **Problema**: `logging.getLogger(__name__).debug(...)` pero NO existe `import logging` en el archivo
- **Impacto**: Cuando GA4 analytics falla, el except handler crashea con `NameError` en vez de hacer fallback graceful. El codigo de fallback en lineas 1462-1467 nunca se ejecuta.
- **Fix**: Agregar `import logging` en imports del modulo (~linea 8)

### BUG-2: Brecha "low_citability" NUNCA se detecta
- **Linea**: 2017
- **Problema**: `getattr(citability_score, 'score', None)` -- la clase tiene `overall_score`, NO `score`
- **Impacto**: Siempre retorna None. La brecha 10 "Contenido No Citable por IA" jamas aparece en diagnosticos.
- **Fix**: Cambiar `'score'` por `'overall_score'`

### BUG-3: Brecha "no_og_tags" NUNCA se detecta
- **Linea**: 2006
- **Problema**: `getattr(audit_result.seo_elements, 'has_open_graph', True)` -- el atributo es `open_graph`, NO `has_open_graph`. Ademas el default deberia ser `False` (sin OG por defecto), no `True`.
- **Impacto**: `not True` = False siempre. La brecha 9 "Sin Open Graph" jamas se detecta.
- **Fix**: Cambiar a `getattr(audit_result.seo_elements, 'open_graph', False)`

### BUG-4: `mobile_score` falsy check ignora score=0
- **Linea**: 1000
- **Problema**: `audit_result.performance.mobile_score and ... < 50` -- si mobile_score=0 (valido en PageSpeed), short-circuits a False
- **Impacto**: Un score de 0 ES menor que 50 y deberia generar alerta pero no lo hace.
- **Fix**: Cambiar a `audit_result.performance.mobile_score is not None and audit_result.performance.mobile_score < 50`

---

## MEDIOS (degradan calidad o son fragiles)

### MED-1: Metodos duplicados con shadowing
- **Lineas**: 1630 vs 2035 (`_compute_opportunity_scores`), 1699 vs 2099 (`_inject_brecha_scores`)
- **Problema**: Dos definiciones de cada metodo. La segunda (FASE-C) silencia la primera. ~120 lineas dead code.
- **Impacto**: Tipos inconsistentes (atributos vs dicts). Confuso para mantenimiento.
- **Fix**: Eliminar primera definicion (lineas 1630-1749)

### MED-2: Claves duplicadas en dict de template data
- **Lineas**: 517-520 vs 595-598
- **Problema**: `geo_regional_avg`, `competitive_regional_avg`, `seo_regional_avg`, `aeo_regional_avg` definidas 2 veces con valores identicos. Python usa la ultima silenciosamente.
- **Fix**: Eliminar primera ocurrencia (517-520)

### MED-3: Inconsistencia mayusculas/minusculas en confidence
- **Lineas**: 822 vs 833/844/854/864/868
- **Problema**: WhatsApp usa `confidence.value` (minusculas: "verified"), otros usan strings hardcodeados en mayusculas ("ESTIMATED", "VERIFIED")
- **Impacto**: Tabla de datos validados muestra estilos mezclados
- **Fix**: Estandarizar a un formato (recomendado: mayusculas via helper)

### MED-4: Tabla Markdown con pipe duplicado
- **Linea**: 298
- **Problema**: Fila AEO empieza con `||` en vez de `|` -- rompe alineacion
- **Fix**: Cambiar `|| Infraestructura` por `| Infraestructura`

### MED-5: Falta `/100` en aeo_score del template
- **Linea**: 298
- **Problema**: Demas scores muestran `42/100`, AEO muestra `42` sin sufijo
- **Fix**: Cambiar `${aeo_score}` por `${aeo_score}/100`

---

## MENORES (code smell)

| Linea | Problema | Fix |
|-------|----------|-----|
| 443 | `from datetime import datetime` redundante (ya importado linea 11) | Eliminar |
| 508-515 | Scores calculados 2 veces cada uno en vez de guardar en variable | Guardar en variable temporal |
| 490 | `_format_scenario_amount()` inconsistente con `format_cop()` de otros escenarios | Unificar |
| 1214/1273/1278 | `audit_result.competitors` sin `hasattr()` guard (fragil ante refactor) | Agregar `hasattr()` como en 1096-1098 |
| 1680 | `print()` en lugar de logging | Cambiar a `logging.warning()` |
| 1822 | `import re` dentro de un loop | Mover a imports del modulo |
| 1615 | Expresion ternaria con precedencia ambigua | Refactorizar con parentesis claros |

---

## Estadisticas

- Total errores: 15
- Criticos: 4 (2 brechas no detectadas + NameError + falsy check)
- Medios: 5
- Menores: 6
- Esfuerzo estimado total: ~30 lineas de cambio
