# R2.3/R2.7 — Par pre/post de conteos — FASE-A

- Comando idéntico en pre y post: `grep -rE "^\s*def test_" tests --include=*.py | wc -l`
- `baseline_pre.txt` (medido antes de cualquier edición): **5334**
- `baseline_post.txt` (medido tras implementar): **5341**
- **Resta: 5341 − 5334 = +7** (delta ≠ 0 → el par no está contaminado)

## Tests nuevos (+7)

| Test | Archivo |
|------|---------|
| `test_spark_informa_retiro_y_sale_0_sin_attribute_error` | `tests/test_spark_retirement.py` |
| `test_simbolos_spark_retirados_de_main` | `tests/test_spark_retirement.py` |
| `test_main_sin_lector_ejecutable_de_superposition_factor` | `tests/test_spark_retirement.py` |
| `test_basic_analysis_recorre_modelo_perdidas_sin_attribute_error` | `tests/test_gap_analyzer_superposition_reader.py` |
| `test_factor_superposicion_viene_del_contrato_metodo` | `tests/test_gap_analyzer_superposition_reader.py` |
| `test_guarded_sites_sin_atributos_inexistentes` | `tests/test_main_static_guards.py` |
| `test_mutante_con_atributo_inventado_es_rojo` | `tests/test_main_static_guards.py` |

## Declaración (L-R.4)

El verificador mecánico de esta resta **no existe**; la resta se publica aquí a
mano y queda declarada sin verificador automático.

## Corrida de referencia

`./venv/Scripts/python.exe -m pytest tests/test_main_static_guards.py tests/test_spark_retirement.py tests/test_gap_analyzer_superposition_reader.py tests/test_spark_command.py tests/test_config_extraction_3b.py -q`
→ **37 passed, 1 skipped** (el skip es pre-existente, ajeno a esta fase).

`./venv/Scripts/python.exe scripts/run_all_validations.py --quick` → **13/13**
(cráudo en `run_all_validations_quick.txt`; el primer intento falló 12/13 por el
artefacto de Wiring vencido por los archivos nuevos — se re-publicó con
`validate_wiring.py --write-report`).

Smoke del CLI: `./venv/Scripts/python.exe main.py spark --url https://example.com/hotel-fixture`
→ **EXIT=0**, mensaje «MODO SPARK - RUTA RETIRADA», sin `AttributeError` (test
`test_spark_informa_retiro_y_sale_0_sin_attribute_error`).
