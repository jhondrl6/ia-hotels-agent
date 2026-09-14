# NR1 — Delta R2.7 (FASE-P3-A)

Regla R2.7: `suma_post − suma_pre == tests_nuevos`. Diferencia 0 = baseline contaminado.

## Método
- Comando canónico (idéntico pre y post): `python -m pytest tests/ -q --tb=no -rf -p no:cacheprovider`
- **PRE** capturado ANTES de cualquier edición de `modules/` o `tests/` → `nr1_baseline_pre.txt`.
  No hizo falta `--ignore` de los tests propios porque el snapshot se tomó cuando aún no existían
  (el archivo nuevo `test_p3a_zip_tier_firstfloor.py` se creó después). Combinación de archivos:
  `tests/` completo, sin exclusión.
- **POST** capturado después de todos los cambios de código y tests → `nr1_baseline_post.txt`.
- Flaky conocido declarado (L-VUP-1): `test_function_default_flags` (orden-dependiente). Está en rojo
  en PRE y en POST → no afecta la resta (mismo conjunto de fallos).

## Sumas canónicas (failed + passed + skipped + xfailed)

| | failed | passed | skipped | xfailed | SUMA |
|--|--------|--------|---------|---------|------|
| PRE  | 4 | 4070 | 31 | 4 | **4109** |
| POST | 4 | 4091 | 31 | 4 | **4130** |
| Δ    | 0 | **+21** | 0 | 0 | **+21** |

## Resta R2.7
```
suma_post − suma_pre = 4130 − 4109 = 21
tests_nuevos         = 21   (tests/quality_gates/tribunal/test_p3a_zip_tier_firstfloor.py)
21 == 21  →  OK (baseline NO contaminado)
```

El delta de +21 cae **íntegro en `passed`** (4070 → 4091): los 21 tests nuevos pasan y ningún test
existente se desplazó ni rompió. `skipped` y `xfailed` sin cambio.

## Fallos — idénticos en PRE y POST (4, todos ajenos a P3-A)
Verificado con `diff` de los conjuntos `^FAILED`: **IDÉNTICOS**, cero fallos nuevos.

1. `tests/delivery/test_faq_generator_improvements.py::test_faq_generator_output_is_jsonld` — ajeno (delivery/FAQ)
2. `tests/financial_engine/test_pricing_resolution_wrapper.py::...::test_function_default_flags` — flaky conocido (L-VUP-1)
3. `tests/test_asset_path_clave_canonica.py::...::test_barreda_un_solo_emisor_de_la_clave` — deuda P3-B (D-V.1, AC-F3)
4. `tests/test_diagnostic_geo_metrics.py::...::test_diagnostic_includes_geo_metrics` — ajeno conocido

Ninguno está en `tests/quality_gates/tribunal/` ni lo causa P3-A; el #3 es el dueño de FASE-P3-B.
No se curan en esta fase (se declaran).

## Tests nuevos por AC (los 21)
- AC-F1 capa 1 (lectura ZIP): 6 tests (stub desde ZIP, contenido real, miembro ausente→ARTIFACT_MISSING,
  ZIP corrupto→READER_FAILED, deliveries vacío→ARTIFACT_MISSING, compatibilidad dir-first)
- AC-F1 capa 2 (stub estructural): 4 tests (boilerplate excluido, contenido real no stub,
  ítems `- [x]` cuentan como contenido, contenido en blanco→stub)
- AC-F1 R2.6 (baseline real): 2 tests (ZIP real ZIP-only detecta el stub de 468 B; dir real detecta el stub) — **corrieron, no se saltaron** (baseline disponible)
- AC-F2 (tier pre-packaging): 5 tests (scenarios-only, prioridad sobre MANIFEST, fallback MANIFEST,
  "C" sin fuente, FASE-I real lee "B" desde scenarios) — el real **corrió** (FASE-I disponible)
- AC-F4 (primer piso B+): 4 tests ("B+" en FIRST_FLOOR_TIERS, aplicado en B+, razón no miente, veredicto condicional)
