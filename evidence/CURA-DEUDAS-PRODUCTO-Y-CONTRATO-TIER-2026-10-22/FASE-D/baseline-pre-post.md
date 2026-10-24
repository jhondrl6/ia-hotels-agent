# Baseline pre/post — FASE-D (R2.3/R2.7)

## 1. Conteo de la colección de tests (delta por fase)

| Punto | Comando | Valor | Crudo |
|-------|---------|-------|-------|
| Pre | `pytest --collect-only -q` (árbol antes de la fase) | **5513** | `baseline_pre.txt` |
| Post | `pytest --collect-only -q` (árbol con los 2 archivos nuevos) | **5545** | `baseline_post.txt` |
| **Resta** | 5545 − 5513 | **+32** | — |

Los 32 tests nuevos son `tests/test_gbp_contrato_frontera.py` (18) y `tests/test_gbp_contrato_relevo.py` (14). Verificado con `01-verde-dientes.txt` (32 passed).

**Declaración `L-R.4`**: el verificador mecánico de la resta **no existe**; la resta de arriba es manual y no se certifica por instrumento.

## 1b. Par rojo/verde (R2.8)

Ver `par-rojo-verde.md`: M1 (claves inglesas + `schema_data={}` restaurados) → 11 rojos con el reproductor de `D28` (6 brechas, 39.600.000 COP/mes); M2 (mapa schema→abandono restaurado) → 3 rojos; M3 (colapso `tipo_map` restaurado) → **2 rojos** (crudo `06`: `2 failed, 1 passed`); verdes de restauración en los crudos 03/05/07. Runner versionado: `mutation_pair_runner.py`.

## 2. Relevo de `gbp_leak_detector` (N3)

Crudo `relevo-cruce.txt`: la matriz perfil a perfil (9 perfiles en zonas de acuerdo + divergencias declaradas fijadas) demuestra que la lógica portada produce el mismo resultado que la copia muerta. Divergencias **declaradas** (no portadas): brecha por conteo de reseñas, `SIN_TELEFONO_VISIBLE`, `CERO_ACTIVIDAD_RECIENTE` (etiqueta propia nueva) y los valores de umbrales (FASE-F).

## 3. `--quick` y derivados

- `run_all_validations.py --quick`: crudo en `12-quick-final.txt` (**13/13, EXIT=0**, capturado sin tubería — `L21`).
- Derivados re-publicados como último paso del cierre: `.opencode/wiring_report.json` (`validate_wiring.py --write-report`) y `.opencode/lecciones_index.json` + `LECCIONES-INDEX.md` (`build_lesson_index.py`), ambos verificados con `--check` (crudos 08–11 y re-verificados en 14–15 con los crudos ya presentes: digest conforme e índice fresco 400 IDs). Disparador del índice: el cierre cita IDs del vocabulario (`D-T4B-A1`, `L-SR3`, `DA-C3`, `L-T4A.5`, `L-V2`) en `00-lecciones` §5.3 y `10-analisis`.

## 4. Poblaciones de los rojos

- M1: `tests/test_gbp_contrato_frontera.py` completo (18 tests → 11 failed, 7 passed; los 7 verdes son los que no ejercitan el símbolo mutado: tri-estado con `{}`/`SCHEMA_VALIDO` y la prueba de vocabulario).
- M2: `tests/test_gbp_contrato_frontera.py::TestPainSolutionMapperCaminoV4Complete` (5 tests → 3 failed: los que leen el mapa; 2 passed: `detect_pains` sobre el audit completo, que no pasa por `_map_brecha_to_issue_type`).
- M3: `tests/test_gbp_contrato_relevo.py::TestN2EtiquetasPropias` (3 tests → 2 failed, 1 passed). El verde bajo el mutante es `test_los_textos_no_repite_la_misma_queja`: lee `motivo`, que `_get_motivo_for_issue` resuelve sobre el `issue_type` original antes de `tipo_map`, así que no ejercita el símbolo mutado (límite declarado en `10-analisis` §Seguimientos).

## 5. Cosas que este par NO certifica

- `v4complete` no se corrió (restricción de la fase: la evidencia de AC3 es el diente).
- `schema_data` en producción sigue sin medirse por el scraper: el contrato ahora es honesto (`None` = no medido), pero `SIN_FAQ` por canal web solo se dispara cuando alguien mida el schema; hoy lo sostiene `tiene_qa` (Q&A de GBP).
- El scraper selenium del módulo retirado (`check_google_profile`) y su rúbrica de 90 siguen como código muerto declarado (ver `10-analisis` §Seguimientos).
- `ultima_actividad_dias` no tiene productor en el scraper: con el contrato tri-estado, `CERO_ACTIVIDAD_RECIENTE` es inalcanzable en producción y el diente la dispara inyectando el valor. Deuda declarada en `10-analisis` §Seguimientos (dueño FASE-H2 / operación).

## 6. Errata del cierre (corregida el 2026-10-23 tras auditoría forense)

**Qué se corrigió**: M3 se publicó como «3 failed / 3 rojos» en cuatro sedes (`par-rojo-verde.md` fila 6, este archivo §1b y §4, `09-documentacion-post-proyecto.md` §D y `10-analisis-post-implementacion.md` §Resumen). El crudo `06-rojo-mutante-m3-tipo-map-colapsado.txt` imprime **`2 failed, 1 passed`**; el tercero queda verde bajo el mutante por la razón escrita en §4.

**Qué NO se cambió**: el código de producción y los dos archivos de tests. La mutación sigue siendo roja sobre los dos dientes que ejercitan `tipo_map`, así que `N2` queda certificado con la cifra correcta; lo erróneo era la cifra, no el veredicto.

**Hallazgo retirado por la propia auditoría**: se había declarado que `docs/contributing/REGISTRY.md` omitía `12-quick-final.txt` en «Archivos Nuevos». Re-medido contra el diff: la fila **sí está** (`git diff` la imprime como línea añadida); la lectura original venía de una salida recortada. Las filas declaradas son 19 de evidencia + 2 tests; lo que falta son 13–19, todos posteriores al `log_phase_completion.py`, como corresponde al escritor aditivo.

**Re-verificación tras la enmienda** (crudos nuevos, ninguno toca el código):

| Crudo | Instrumento | Resultado |
|-------|-------------|-----------|
| `16-quick-tras-errata.txt` | `run_all_validations.py --quick` | 13/13, `EXIT=0` |
| `17-lesson-index-check-tras-errata.txt` | `build_lesson_index.py --check` | fresco (400 IDs), `EXIT=0` |
| `18-wiring-check-tras-errata.txt` | `validate_wiring.py --check` | digest conforme `3c4b39e844e3`, `EXIT=0` |
| `19-plan-citations-check-tras-errata.txt` | `validate_plan_citations.py` | 0 citas nuevas, `EXIT=0` |

Con esta sección ya escrita se re-corrieron los cuatro instrumentos: crudos `20-quick-final-tras-enmienda.txt` (13/13, `EXIT=0`), `21-lesson-index-check-final.txt`, `22-wiring-check-final.txt` y `23-plan-citations-final.txt`, los cuatro con `EXIT=0`. La enmienda es prosa: no añade definiciones ni cita IDs del vocabulario (no vence el índice) y no añade `.py` versionado (no mueve contadores del Wiring).

**Nota de lectura del crudo 16 (instrumento preexistente, no de esta fase)**: la cabecera de `run_all_validations.py` imprime `Mode: FULL` porque etiqueta por `check_only`, no por `quick`. El modo autoritativo es la línea `MODO: rapido` del resumen y su denominador 13; `--quick` llega a 18 solo en modo completo. El crudo tampoco lleva la línea `CMD:` que sí tienen 02–07.
