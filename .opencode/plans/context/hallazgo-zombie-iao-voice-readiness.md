# Hallazgo: Zombie References ${iao_score}/${voice_readiness_score}

**Fecha**: 2026-04-08
**Origen**: Investigacion post-FASE-CAUSAL-01
**Estado**: Pendiente de fix

---

## Descripcion

Templates v4 aun referencian `${iao_score}`, `${voice_readiness_score}`, `${iao_status}`, `${voice_readiness_status}` que fueron eliminados en FASE-CAUSAL-01. Ningun codigo Python vivo popula estas variables.

## Hallazgos

| Archivo | Problema | Severidad |
|---------|----------|-----------|
| `templates/diagnostico_ejecutivo.md:15` | Faltan `{iao_score}`, `{iao_comparativo}`, `{iao_icon}` en `.format()` | **ALTA -- KeyError en runtime** |
| `templates/diagnostico_v4_template.md:41-42` | Placeholders `${iao_score}`, `${voice_readiness_score}` sin reemplazo | BAJA (v6 es default, safe_substitute no crashea) |
| `v4_diagnostic_generator.py` (~linea 1486, 1557) | `iao_score` en fallback dict se calcula pero nunca se consume | BAJA (dead code) |
| `modules/utils/benchmarks.py:33` | `iao_score: 18` hardcoded sin consumidor | BAJA |

## Bug Critico

`diagnostico_ejecutivo.md` usa `.format()` (no `safe_substitute`). Si ese template se ejecuta, crashea con KeyError porque `report_builder.py:836-857` NO pasa `iao_score`, `iao_comparativo`, ni `iao_icon` en el dict.

## Fixes Requeridos

1. **URGENTE** -- Eliminar fila IAO de `templates/diagnostico_ejecutivo.md` linea 15
2. Eliminar filas IAO + Voice Readiness de `templates/diagnostico_v4_template.md` lineas 41-42
3. Limpiar `iao_score` del dict en `_get_analytics_fallback()` en `v4_diagnostic_generator.py`
4. Evaluar si `modules/utils/benchmarks.py` necesita la key `iao_score`

## Esfuerzo Estimado

~8 lineas de cambio total. Sin riesgo de regresion.
