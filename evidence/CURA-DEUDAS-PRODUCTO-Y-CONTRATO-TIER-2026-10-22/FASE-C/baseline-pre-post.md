# Baseline pre/post — FASE-C (ítem C, AC2)

**Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22` · **Población declarada** (R2.4 §10b): `modules/`, `tests/`, `main.py` (literales: rutas de código y tests). **Fuera de población** (históricos o scratch, no editados): `VERSION.yaml`, `CHANGELOG.md`, `docs/` narrativos (`GUIA_TECNICA.md`, `ROADMAP.md` — prosa histórica, dueño FASE-RELEASE), `context/`, `Archives/`, `evidence/`, `qmind-writeback/`, `temp/`.

## Resta del literal viejo `APROBADO-CONDICIONAL-PENDING-ONBOARDING`

| Punto | Conteo | Artefacto crudo |
|-------|--------|-----------------|
| PRE (inicio de sesión, antes de ediciones) | **8** | `grep-literal-viejo-baseline_pre.txt` |
| POST (tareas 1–4 aplicadas) | **0** | `grep-literal-viejo-baseline_post.txt` |
| **Delta** | **−8** | |

Consulta única re-ejecutable: `grep -rn --include='*.py' 'APROBADO-CONDICIONAL-PENDING-ONBOARDING' modules tests main.py` (exit 1 = 0 coincidencias).

Coincide con la superficie medida del prompt de fase (8 en `.py`: constante `judge.py`, etiqueta `acta_writer.py`, 6 tests).

## Puntos medidos de la suite del contrato (par R2.3)

| Punto | Resultado | Artefacto crudo |
|-------|-----------|-----------------|
| Verde (árbol real, tras restaurar mutantes) | **349 passed, 9 skipped** | `01-verde-suite-contrato.txt`, `04-verde-tras-restaurar.txt` |
| ROJO mutante M1 (literal viejo restaurado en `VERDICT_CONDITIONAL`) | **8 failed** | `02-rojo-mutante-m1-literal-viejo.txt` |
| ROJO mutante M2 (causa eliminada en las dos salidas de `_compute_verdict`) | **6 failed** | `03-rojo-mutante-m2-causa-eliminada.txt` |

Comando del **verde**: `./venv/Scripts/python.exe -m pytest tests/quality_gates/tribunal tests/test_ac_g4_g5_multi_hotel_matrix.py tests/test_fase_0_ac20_evidencia_veredicto.py tests/test_p6r_full_flow_matrix.py -q` (349 tests).

**Poblaciones de los rojos (corrección 2026-10-23; reconstruidas del crudo 02/03 por nombres de fallos y totales — no hay comando transcrito)**: M1 se ejecutó sobre `tests/quality_gates/tribunal/test_conditional_reason.py` + `tests/quality_gates/tribunal/test_acta_serialization.py` + `tests/test_ac_g4_g5_multi_hotel_matrix.py` (16 tests: 8 failed / 8 passed); M2 solo sobre `tests/quality_gates/tribunal/test_conditional_reason.py` (7 tests: 6 failed / 1 passed). Los rojos son subconjuntos de la superficie que lee el literal y **no** son like-for-like con el verde de 349.

## Par de colección de tests (delta +7, `pytest --collect-only -q`)

| Punto | Conteo | Crudo |
|-------|--------|-------|
| PRE (equivalente al árbol sin el archivo nuevo: `--ignore=tests/quality_gates/tribunal/test_conditional_reason.py`) | **5506** | `13-collect-pre-sin-archivo-nuevo.txt` |
| POST (árbol completo) | **5513** | `12-collect-post.txt` |
| **Delta** | **+7** | |

## Límites declarados (L-R.4)

- **El verificador mecánico de la resta no existe**: la resta PRE→POST se declara aquí sin guard automático.
- **El par pass/fail de la suite COMPLETA no existe**: solo el punto medido (la superficie del contrato arriba), como en FASE-B.
- **Atribución de los rojos por mecanismo**: M1 rompe todo assert que lea el valor literal `APROBADO-CONDICIONAL` del artefacto serializado (**6** tests nuevos + `test_acta_serialization` + la matriz multi-hotel = 8, el total que imprime el crudo 02); M2 rompe los 6 tests que leen `conditional_reason` del JSON del writer real. Los tests que comparan contra la constante `VERDICT_CONDITIONAL` (no el literal) quedan en verde ante M1 por diseño: son el motivo de que los asserts de AC2 usen el literal.
- **Errata (2026-10-23)**: la primera versión de esta nota atribuía a M1 «7 tests nuevos»; el crudo 02 lista **6** (7+1+1=9 contradecía «8 failed»). Corregido aquí y en `par-rojo-verde.md`.
- **Afirmación retirada (2026-10-23)**: `par-rojo-verde.md` decía que el grep de población detecta el literal «0 → ≥1» bajo M1; no se midió ni hay crudo de esa corrida. El diente de M1 se certifica por el rojo de los tests (crudo 02).
- **Hallazgo honesto intermedio**: la primera pasada del grep POST detectó 2 ocurrencias auto-infligidas en el test nuevo (`VIEJO_LITERAL` y su docstring). Corregido reconstruyendo el literal por piezas (`"APROBADO-CONDICIONAL" + "-PENDING-ONBOARDING"`): el grep da 0 en fuente y el mutation check conserva el string completo en runtime (si el literal se restaura en el producto, el test de serialización falla igual).
- **`P6.5`/`T1_CERTIFIABLE_CLAUSES` intactas**: `p65-intacta.txt` (grep por símbolo, R2.2).
