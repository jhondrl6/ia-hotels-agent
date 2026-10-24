# FASE-E — baseline pre/post (R2.3/R2.7) y atribución de rojos

Plan `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22` · cierre 2026-10-23 · sin commit (los cinco cortes terminan en espera de autorización).

## 1. Conteo de tests (funciones `def test_` en el árbol de trabajo)

Comando canónico (el que publica la cifra, no este documento):

```bash
grep -rE "^\s*def test_" tests --include=*.py | wc -l
```

| Corte | Valor |
|---|---|
| PRE (árbol al abrir la fase, en `86d3694`) | 5,380 |
| POST (árbol al cerrar la fase) | 5,428 |
| **Resta** | **+48 funciones** en tres archivos nuevos de `tests/utils/` |

Los 48 defs recolectan **54 casos** porque dos baterías están parametrizadas (`test_bloque_sin_dato_publicado_devuelve_su_maestro_declado` = 5 ids/1 def, `test_bloque_con_forque_publicado_no_lo_lee` = 3 ids/1 def). La cifra commiteada se mide sin tocar el árbol con `git grep -c -E "^\s*def test_" HEAD -- tests`.

**Verificador mecánico de la resta: no existe** (`L-R.4`, R2.7). Se publica la resta escrita y los dos valores con su comando.

## 2. Par rojo/verde de los mutantes (R2.8)

Crudo: `par-rojo-verde-mutantes.txt`.

| Mutante | Símbolo golpeado | Verde base | Rojo con mutante | Causa nombrada |
|---|---|---|---|---|
| M1 | `BenchmarkLoader.get_regional_data` restaurado a la forma vieja (`data.get("regiones", {})` en el nivel superior) | 54 passed / exit 0 | **13 failed** / 41 passed / exit 1 | el getter vuelve a ignorar `region` y devolver el fósil global |
| M2 | `run_all_validations.py`: `if divergencias:` → `if False and divergencias:` | 54 passed / exit 0 | **1 failed** / 53 passed / exit 1 | el slot `[2/13]` deja de consumir las divergencias: vuelve a ser check de parseo |
| M3 (dato) | `v25_config.regiones.caribe.precio_promedio` 450.000 → 449.000 en **copia** (árbol intacto) | `validate()` = `[]` | `['ADR DIVERGENCE [caribe]: master=450,000 vs plan_maestro=449,000']` | la comparación de valores se dispara con un dato corrompido |

Restauración verificada por sha256 sobre los bytes de `modules/utils/benchmarks.py` (`d8ee58b0fdc7…`) y `scripts/run_all_validations.py` (`b5f14e520f26…`): PRE == POST en ambos, y el verde final es idéntico al inicial (54 passed).

## 3. Valores que movió la fase (no son un conteo, son comportamiento de producto)

| Clave | PRE (fósil único para toda región) | POST (derivado del maestro por región) |
|---|---|---|
| `get_regional_data('default').revpar_cop` | 197.120 | 168.000 (280.000 × 0.60), `revpar_derivado=true` |
| `…('eje_cafetero')` | 197.120 | 143.360 (280.000 × 0.512) |
| `…('caribe')` | 197.120 | 308.250 (450.000 × 0.685) |
| `…('antioquia')` | 197.120 | 321.000 (500.000 × 0.642) |
| `…('bogota')` | 197.120 | 227.500 (350.000 × 0.65) |
| `FinancialFactors.get_all_regions()` | `AttributeError` (`loader._plan_data` no existe) | `['antioquia','bogota','caribe','default','eje_cafetero']` |
| `gap_analyzer.revpar_targets` | 171.600 / 270.600 / 168.000 literales propios | retirada; `revpar_objetivo = config.revpar_cop` |
| `ScraperFallback` respaldo regional | 330.000/0.52 · 410.000/0.66 · 280.000/0.60 | retirado; delega al lector único |
| check `[2/13]` | `Plan Maestro vv2.5.0 loaded correctly` (solo parseo) | `… parseado y 4 regiones con valores sincronizados con el maestro (exenta: default: …)` |

Consecuencia prevista por el plan: las pérdidas del escenario financiero se re-miden (AC7 acepta «la re-medida»); la re-medida es de FASE-E2E, no de esta fase. `dynamic_impact` y `package_recommender` reciben ahora revpar por región.

## 4. Rojo declarado, no curado por esta fase

`tests/config/test_config_integration.py::TestConfigIntegration::test_all_config_files_have_description` — **PREEXISTENTE**, ya atribuido a dueño Operador en `10-analisis` §Seguimientos (fila `R` de FASE-B: `config/secret_fragment_policy.yaml` sin `description`). Crudo: `crudo-pytest-afectados.txt` (1 failed, 1383 passed, 5 skipped, 3 xfailed en la selección de `tests/utils`, `tests/financial_engine`, `tests/scrapers`, `tests/commercial_documents`, `tests/orchestration_v4`, `tests/config` y los archivos sueltos de benchmarks). No hay camino de dependencia desde los archivos de FASE-E hacia ese test.

## 6. Rojo de colección atribuido por mecanismo (no es de esta fase)

Al combinar selecciones que incluyen `tests/e2e` más un módulo que importa selenium de verdad (p. ej. `tests/test_gap_analyzer_superposition_reader.py`, de FASE-A, o `tests/regression/test_fase3_guardrails_integration.py`), la colección lanza:

```
ImportError: cannot import name 'ElementNotInteractableException' from 'selenium.common.exceptions' (unknown location)
```

Medido en tres corrídas, **ninguna de ellas con archivos de FASE-E en la selección**:

| Selección | Resultado |
|---|---|
| `tests/e2e` sola | 20 passed, 1 skipped |
| `tests/test_gap_analyzer_superposition_reader.py` + `tests/regression/test_fase3_guardrails_integration.py` (los dos que fallan al combinarlos con e2e) | 14 passed |
| `tests/e2e` + `tests/test_gap_analyzer_superposition_reader.py` | **1 error de colección** con esa traza |

Productor del envenenamiento: `tests/e2e/conftest.py:34` (`_ensure_module('selenium', is_package=True)` — «Mock external dependencies (bs4, selenium, urllib3)»), un efecto de lado en import-time del paquete e2e. Cualquier módulo recolectado después que importe `selenium.common.exceptions` de verdad cae. **PREEXISTENTE**, ajeno a FASE-E por superficie y por mecanismo; dueño **Operador / FASE-VERIFY** (higiene del conftest de e2e: el stub no debe quedar instalado para la colección posterior). No se curó aquí: tocar `tests/e2e/conftest.py` está fuera del alcance de la fase y de sus AC.

## 7. Archivo de evidencia fuera del registro

`crudo-quick-cierre.txt` (la última corrida de `--quick`, 13/13 con el índice de lecciones ya re-publicado) se escribió **después** de estampar `docs/contributing/REGISTRY.md`, así que no figura entre los nueve `--archivos-nuevos` de la entrada. Queda declarado aquí; su consolidate es la fila de FASE-E en `09-documentacion-post-proyecto.md` §E, que nombra el directorio completo. El escritor es aditivo y se niega a re-clasificar (`registry-clasifica-por-flag`), por lo que no se re-ejecutó para no apilar una entrada duplicada.


## 5. Validaciones

| Corrida | Resultado | Crudo |
|---|---|---|
| `pytest` de los 3 archivos nuevos | 54 passed, exit 0 | `par-rojo-verde-mutantes.txt` (bloque BASELINE y VERDE FINAL) |
| `python scripts/validate_benchmark_sync.py` | `BENCHMARK SYNC OK: 4 regions verified`, exit 0 | `crudo-quick-post.txt` |
| `run_all_validations.py --quick` antes de re-publicar Wiring | **12/13**, exit 1 (`Wiring: el artefacto publicado está vencido`: `cobertura.archivos_en_alcance` 730→733) | `crudo-quick.txt` |
| `validate_wiring.py --write-report` | exit 0 | `crudo-wiring-write.txt` |
| `run_all_validations.py --quick` después | **13/13**, exit 0, `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinámico` | `crudo-quick-post.txt` |

El denominador `[2/13]` conserva su ordinal y su denominador: la guarda del runner y `test_la_etiqueta_2_de_13_conserva_ordinal_y_denominador` lo comprueban (`_etiquetas_del_modo()` da `(2, 13)` y 13 ordinales contiguos en modo rápido; el modo completo llega a 18).
