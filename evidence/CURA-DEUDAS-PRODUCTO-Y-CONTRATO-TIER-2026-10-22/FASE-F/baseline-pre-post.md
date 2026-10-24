# FASE-F — par pre/post y resta (R2.3/R2.7)

Medición **de árbol a árbol**: el PRE se toma con `git grep` sobre `HEAD` (`5074b51`, sin tocar el
árbol de trabajo); el POST sobre el árbol vivo de la fase. Crudos: `baseline-pre.txt`, `baseline-post.txt`.

## 1. Umbrales de fotos (`D25`, AC6)

| Magnitud | PRE (HEAD) | POST | Delta |
|---|---|---|---|
| Sitios de comparación de fotos contra un literal, en `modules/` (8 módulos) | 17 | 4 | **−13** |
| Esos 4 restantes | — | `gbp_leak_detector.py:145/403/405/435` | **congelados a propósito**: copia retirada del servicio que FASE-D conserva como oráculo del relevo (`tests/test_gbp_contrato_relevo.py` la importa); cablearla al config haría que el oráculo derive con el config |
| Sitios de comparación **vivos** medidos por AST (nombre del umbral al otro lado) | 0 (todos eran literales) | 14 en 7 módulos | **+14** |
| Nombres del vocabulario publicados en `config/regional_benchmarks.yaml` | 0 | 5 | **+5** |
| Constante local `TARGET_GBP_PHOTOS = 40` | 1 definición + 2 usos | 0 | **−3** |
| Default inline de umbral de fotos (`.get('fotos_meta', 15)`) | 1 | 0 | **−1** (hallazgo del diente de AST, no estaba en los 11 publicados) |

**Re-medición de la población**: el contexto de deudas publicó **11 sitios en 7 módulos**. FASE-F mide
**14 sitios vivos** (13 contra literal + 1 contra `TARGET_GBP_PHOTOS`): los tres que faltaban son el
segundo método de score de `GBPAuditor` (dos comparaciones) y la banda parcial `>= 5` del primero.
El conteo quedó pinchado en `test_cada_sito_lee_su_umbral_nombrado` y
`test_la_cuenta_total_de_sitios_es_la_re_medida_de_fase_f`, módulo por módulo y en total.

## 2. `D25-bis` — `recovery_factors`

| Magnitud | PRE | POST | Delta |
|---|---|---|---|
| Sitios Python con el valor del factor realista | 4 (`respaldo 0.20` + `.get(...,0.20)` en propuesta; `.get(...,0.35)` + `except: 0.35` en diagnóstico) | 1 (`RESPALDO_ESCENARIOS` en `modules/common/scenario_config.py`) | **−3** |
| Valor vivo del respaldo vs maestro | 0.20 vs **0.35** (divergencia activa) | 0.35 = 0.35 | curado |
| Lectores de `scenarios.yaml` con respaldo duplicado | 3 (propuesta, diagnóstico, `scenario_calculator`) | 2 con respaldo único + 1 declarado | ver §Deuda |

## 3. `D27` — constantes homónimas

| Nombre | PRE | POST | Consumidores |
|---|---|---|---|
| `PERDIDA_MENSUAL_BASE` (genérico) | 3 definiciones + 1 uso | **0** en `modules/`, `main.py`, `scripts/` y `tests/` | — |
| `PERDIDA_BASE_SIN_PERFIL` (2.1M, `DynamicImpactCalculator`) | — | 1 definición + 1 uso (`_calculate_loss`, factor 1.0) | vivo |
| `PERDIDA_BASE_CARIBE_CALIBRADA` (2.8M, `GBPAuditor`) | — | 1 definición, 0 usos | huérfana documentada |
| `PERDIDA_BASE_CALIBRACION_15_20_HAB` (2.1M, `GBPRevenueLeakDetector`) | — | 1 definición, 0 usos | huérfana de la copia retirada |

## 4. Tests

5428 → **5454** funciones (`grep -rE "^\s*def test_" tests --include=*.py`, árbol vivo): **+26** en
`tests/config/test_umbrales_fotos_semantica.py` (14 casos), `tests/config/test_coherencia_escenarios_d25bis.py`
(12), `tests/test_d27_perdida_base_por_semantica.py` (6) y
`tests/commercial_documents/test_h1_tier_misma_fuente.py` (4). Dos tests existentes re-escritos por el
cambio de contrato de `H1`: `test_evidence_tier_a_with_ga4` → `test_evidence_tier_sigue_si_c_con_ga4_sin_breakdown`
y el tramo GA4 de `test_diagnostic_generator_fallback_tier_no_breakdown`.

## 5. Verificador mecánico de la resta (R2.7 — `L-R.4`)

**No existe** un verificador mecánico de la resta: la resta la publican los dos crudos de este
directorio y este documento. Sí existe, en cambio, el diente que impide que la población vuelva a
mentir: los conteos por módulo y el total están asercionados por AST, así que un sitio añadido o
retirado sin re-declaración pone FASE-F en rojo.
