# NR1 — Delta R2.7 (FASE-P3-B)

Regla R2.7: `suma_post − suma_pre == tests_nuevos`. Diferencia 0 = baseline contaminado.

## Método

- Comando canónico **idéntico** pre y post:
  `python -m pytest tests/ -q --tb=no -rf -p no:cacheprovider`
- **PRE** capturado a las 15:41 del 2026-09-14, **antes de la primera edición** de
  `main.py`, `modules/` o `tests/` → `nr1_baseline_pre.txt`.
  No hizo falta `--ignore` de los tests propios: los tres archivos de test de esta fase
  (`test_p3b_analytics_flags_wiring.py`, `test_acta_version_desde_yaml.py` y la clase
  añadida a `test_s_e2_generate_proposal_false.py`) aún no existían cuando corrió el PRE.
  **Combinación de archivos declarada**: `tests/` completo, sin exclusión, con
  `-p no:cacheprovider`.
- **POST** capturado después de todos los cambios de código y de test, con el árbol ya
  restaurado por `nr7_mutation_checks.py` → `nr1_baseline_post.txt`.
- **Flaky conocido declarado (L-VUP-1)**: `test_function_default_flags`
  (`tests/financial_engine/test_pricing_resolution_wrapper.py`, orden-dependiente). Está
  en rojo en PRE y en POST, mismo conjunto, por tanto no afecta la resta.

## Sumas canónicas (failed + passed + skipped + xfailed)

| | failed | passed | skipped | xfailed | SUMA |
|--|--------|--------|---------|---------|------|
| PRE  | 4 | 4.091 | 31 | 4 | **4.130** |
| POST | 3 | 4.115 | 31 | 4 | **4.153** |
| Δ    | **−1** | **+24** | 0 | 0 | **+23** |

## Resta R2.7

```
suma_post − suma_pre = 4153 − 4130 = 23
tests_nuevos         = 23   (14 + 4 + 5, ver desglose abajo)
23 == 23  →  OK (baseline NO contaminado)
```

El Δ de `passed` es **+24, no +23**, y la diferencia es exacta y esperada: además de los
23 tests nuevos, `test_barreda_un_solo_emisor_de_la_clave` **migró de `failed` a
`passed`** al cerrarse AC-F3. Por eso `failed` baja de 4 a 3 y la SUMA sube solo con los
tests nuevos (una migración failed→passed no cambia la suma: ambas categorías cuentan).
Ningún test existente se perdió ni se desplazó; `skipped` y `xfailed` sin cambio.

**Duraciones**: PRE 621.98 s (10:21), POST 450.26 s (7:30). La diferencia es carga de la
máquina, no de la suite — el conteo es idéntico en método.

## Tests nuevos por AC (los 23)

- **AC-F5 — cableado (10)**: `test_p3b_analytics_flags_wiring.py::TestCableadoBanderasEnFASEK`
  — `ga4_enabled`/`gsc_enabled` no son constantes (2), disponibilidad calculada antes del
  consumidor y una sola vez (2), hoist alcanzable donde lo es FASE-K (2), hoist fuera de
  todo `except` ancho (2), más 2 de la misma parametrización sobre `gsc_available`.
- **AC-F5 — MANIFEST (1)**: `TestManifiestoNoContradiceElTier::test_gsc_configured_usa_el_valor_hoisteado`.
- **AC-F5 — regla conductual (5)**: `TestReglaFASE1SigueViva` — tier `A` con analítica,
  `B+` sin analítica, `B+` con una sola fuente (2 parametrizaciones), y `A` exige dato
  verificado además de conectividad.
- **AC-F5 — régimen `generate_proposal=False` (5)**: añadidos a
  `test_s_e2_generate_proposal_false.py::TestAnalyticsFlagsReachableWithoutProposal`
  — banderas antes de decidir `generate_proposal` (2), no bajo el guard (2), y el bloque
  FASE-K tampoco bajo el guard (1).
- **AC-F6 — versión del acta (4)**: `test_acta_version_desde_yaml.py` — coincidencia con
  `VERSION.yaml` leído del disco, reflejo de un YAML distinto sin tocar código (mata el
  hardcode y el caché de import), fallback declarado sin YAML, y candado estructural de que
  el writer no lleva literales de versión.

## Fallos — POST

3 fallos, **todos ajenos a esta fase** y ya declarados en el PRE de FASE-P3-A:

1. `tests/delivery/test_faq_generator_improvements.py::test_faq_generator_output_is_jsonld` — ajeno (delivery/FAQ)
2. `tests/financial_engine/test_pricing_resolution_wrapper.py::...::test_function_default_flags` — flaky conocido (L-VUP-1)
3. `tests/test_diagnostic_geo_metrics.py::...::test_diagnostic_includes_geo_metrics` — ajeno conocido

**`test_barreda_un_solo_emisor_de_la_clave` ya no está**: se cierra la deuda **D-V.1** que
v4.76.0 publicó abierta y que AGENTS.md registra como fallo conocido. La actualización de
esa fila en AGENTS.md corresponde a **FASE-RELEASE** junto con el bump (así lo fija el
prompt de esta fase, línea "AGENTS.md registra …").

## Conteo canónico (el del `grep`, no el de pytest)

Medido al cerrar la fase con el método canónico del repo
(`grep -rE "^\s*def test_" tests --include=*.py`):

| | Al cerrar P3-A | Al cerrar P3-B | Δ |
|--|----------------|----------------|---|
| Funciones `def test_` | 4.129 | **4.146** | **+17** |
| Archivos `test_*.py` | 296 | **298** | +2 |

**+17 funciones, +23 tests recolectados.** No es una discrepancia: 6 de las 17 funciones
nuevas están parametrizadas con 2 casos (`@pytest.mark.parametrize("target",
["ga4_available", "gsc_available"])` y el de `[(True, False), (False, True)]`), así que
aportan 12 tests; las otras 11 funciones aportan 1 cada una. `12 + 11 = 23`.

Por eso la resta que gobierna **R2.7** es la de **pytest** (4.153 − 4.130 = 23), tomada
pre y post con el mismo comando: cuenta tests ejecutados, que es lo que puede dejar de
ejecutarse. El conteo canónico por `def` se reporta aparte porque es el que publican
`AGENTS.md` y `09-documentacion-post-proyecto.md` §D, y en RELEASE hay que reconciliar
ambas bases: **4.146 funciones / 4.153 recolectados / 298 archivos**, con la diferencia
explicada por la parametrización y no por tests huérfanos.
