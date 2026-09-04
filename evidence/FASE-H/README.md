# FASE-H — evidencia de verificación (2026-09-04)

## Baseline antes de tocar código
`faseH_baseline_pre.txt` — `tests/quality_gates tests/asset_generation` = **944 passed, 2 skipped**.
Nota: el "848/2" que cita `05-prompt-inicio-sesion-fase-H.md` estaba desactualizado (es el
baseline pre-plan; el de cierre de FASE-G ya era 944/2).

## Comandos ejecutados después de la integración

| Comando | Salida | Resultado |
|---------|--------|-----------|
| `pytest tests/commercial_documents/test_pain_solution_mapper.py tests/commercial_documents/test_diagnostic_brechas.py tests/commercial_documents/test_diagnostic_generator.py tests/data_validation/test_metadata_validator.py tests/auditors/test_v4_comprehensive.py tests/test_hotel_visperas_regression.py -q` | `faseH_units.txt` | 188 passed, 0 failed |
| `pytest tests/quality_gates tests/asset_generation -q` | `faseH_baseline.txt` | 944 passed, 2 skipped (baseline preservado) |
| `pytest tests/commercial_documents/test_pain_map_bijection.py tests/commercial_documents/test_detect_pains_emisiones_faseB.py tests/common/test_service_identity_registry.py -q` | `faseH_contracts.txt` | 83 passed (contract tests FASE-A y biyección FASE-B en verde) |
| `scripts/run_all_validations.py --quick` | `faseH_validations.txt` | 7/7 validations passed |
| `git diff --stat .env` / `git status --short .env` | — | vacío: `.env` SIN cambios |

Conteos por archivo de test: `faseH_conteos.txt`.

## Capturas de diff
- `faseH_code.diff` — todo el cambio de código y tests de la fase.
- `faseH_v11_textos.diff` — capture enfocada de los textos V11 en `v4_comprehensive.py` y
  `v4_diagnostic_generator.py` (cabecera de tabla, rama por estado, mensaje sanitizado en la
  fuente, `execution_trace` disjunto).

## V12 — verificación empírica (solo longitudes, nunca valores)
Medido sobre `./.env` con `python -c` + regex, sin volcar contenido:

```
PAGESPEED_API_KEY: len=39
GOOGLE_PAGESPEED_API_KEY: len=3   (placeholder 'xxx')
GOOGLE_API_KEY: AUSENTE
```

Cadena de fallback: `modules/data_validation/external_apis/pagespeed_client.py:25`
(`PAGESPEED_API_KEY or GOOGLE_PAGESPEED_API_KEY or GOOGLE_API_KEY`). Hoy resuelve la de 39
chars; eliminar la canónica hace que el fallback resuelva el placeholder de 3 chars y el
síntoma de D6 reaparece. Es decisión OPS: se documenta en `09-documentacion-post-proyecto.md`
y no se editó `.env` en esta fase.

## Fallo preexistente registrado (no corregido, ajeno a FASE-H)
`tests/test_diagnostic_geo_metrics.py::test_diagnostic_includes_geo_metrics` está rojo.
Verificado que no lo causó esta fase: la cadena que reclama ("Métricas de Optimización para
IA") aparece 0 veces tanto en `HEAD` como en el árbol de trabajo, y
`_build_geo_problems_table` no fue tocado. Va como seguimiento #16 en `10-analisis`.

## Secuencia real de las mediciones (para no leer 188 como post-borrado)
1. **188 passed / 0 failed** en la batería de 6 archivos se midió **antes** del borrado físico del
   gemelo V13, con el shim de delegación en el árbol.
2. Después del `git rm -f` (aprobado por el usuario el 2026-09-04) se re-midieron los 4 archivos
   que pueden verse afectados por ese cambio: **100 passed / 0 failed**
   (`test_metadata_validator.py` 23, `test_hotel_visperas_regression.py` 5,
   `test_pain_solution_mapper.py` 46, `test_v4_comprehensive.py` 26 → ver
   `faseH_conteos_v13_final.txt` para los dos primeros).
3. Baseline tras el borrado: **944 passed / 2 skipped**; `run_all_validations.py --quick`: **7/7**.
4. No se re-corrió la batería completa de 6 archivos después del borrado: la política de permisos
   de la sesión bloqueó ese comando como fuera del paso solicitado. Los 2 archivos restantes
   (`test_diagnostic_brechas.py`, `test_diagnostic_generator.py`) no importan la ruta borrada.
