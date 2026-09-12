# evidence/FASE-V2 — Par pre/post de NR1 con la resta de R2.7

**Plan**: `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` · 2026-09-12 · FASE-V2.
**Qué añade la fase**: `tests/test_validate_lesson_capitalization.py` con **29** funciones
`def test_` y un arreglo menor en `tests/test_validate_plan_closure.py` (un contract test rojo
que esta fase encontró y repara, ver §4).

## 1. Las dos bases de medición, declaradas por separado (R2.3)

### Base canónica del repo — `def test_` en el árbol

Comando de ambas corridas, **con la combinación exacta de archivos** (L-VUP-1 exige que el par
se declare con su red de recolección, no con un «todos los tests» abstracto):

```bash
grep -rE "^\s*def test_" tests --include=*.py | wc -l                                       # POST
grep -rE "^\s*def test_" tests --include=*.py --exclude=test_validate_lesson_capitalization.py | wc -l   # PRE
```

| Momento | Suma | Cómo |
|---------|------|------|
| pre | **4.079** | árbol de la fase sin el archivo nuevo de tests excluido por `--exclude` |
| post | **4.108** | árbol final de V2 |
| **resta** | **4.108 − 4.079 = 29** | = `def test_` del archivo nuevo (**29**) ✅ R2.7 |

### Base pytest — corrida completa `python -m pytest -q --tb=no`

| Momento | failed | passed | skipped | xfailed | **suma** |
|---------|--------|--------|---------|---------|----------|
| pre (`--ignore=tests/test_validate_lesson_capitalization.py`) | 4 | 4.041 | 31 | 4 | **4.080** |
| post (corrida final, árbol actual) | 3 | 4.071 | 31 | 4 | **4.109** |
| **resta** | | | | | **29** ✅ |

- `skipped` idéntico: **31 → 31** (R2.3).
- La resta pytest (29) coincide con la canónica (29) **porque ambas miden el mismo archivo**;
  el desfase entre bases (`4.109` vs `4.108`, +1) es preexistiente y no de esta fase: pytest
  recauda un caso parametrizado adicional. La resta **dentro** de cada base es la que vale.
- Registrado para que nadie lo olvide: el conteo canónico que publica `AGENTS.md` (**4.063**)
  va **16 funciones** por detrás de este árbol. Es S-V2.1 en `10-analisis-post-implementacion.md` §5.

## 2. Corrida intermedia, incluida porque explica una partida

Se corrió un tercer `pytest` completo entre las dos tomas de arriba, **antes** de añadir los dos
tests de cableado y **antes** de arreglar el contract test del hook:

| Corrida | failed | passed | suma | Lectura |
|---------|--------|--------|------|---------|
| intermedia | 4 | 4.068 | 4.107 | 27 tests nuevos, con el rojo heredado aún en pie |

Diferencia contra la final: **+2** tests de cableado y **−1** rojo que pasó a verde. Sin esta
fila, la resta 4.107 → 4.109 parecería una partida perdida.

## 3. Flaky y orden-dependencia (L-VUP-1)

`tests/financial_engine/test_pricing_resolution_wrapper.py::test_function_default_flags` está
en la lista de rojos ajenos y **es orden-dependiente**: falla en combinación y pasa aislado.
Está en las dos corridas (pre y post), así que no afecta a la resta. Las tres corridas de esta
fase se hicieron con la **misma** red de recolección (repo completo, `--tb=no`, sin `-p no:randomly`
ni semillas fijas), que es lo que hace comparable el par.

## 4. El cuarto rojo del `pre`: heredado, no causado por V2 (y por eso se arregla aquí)

El `pre` muestra **4** fallos, no los **3** que declara `AGENTS.md`. El extra es
`tests/test_validate_plan_closure.py::TestIntegracionRepoReal::test_registrado_como_check_5_en_el_hook`,
que aserta la etiqueta `[5/5]` del hook. Medido con git:

```bash
git show b57dd83:scripts/git_hooks/pre-commit | grep -c "\[5/5\]"      # -> 0
git log --oneline -S"[6/6] Checking lesson index" -- scripts/git_hooks/pre-commit
#   4a066e1 feat(paso-0): el Paso 0 produce un artefacto y el corpus gana una capa fria indices
```

Es decir: el hook ya tenía seis checks en el commit `4a066e1` y su contract test siguió pinando
la numeración de cinco. Llegó a esta fase **rojo y sin declarar**, y no lo rompió la renumeración
de V2 (que lo deja en `[5/7]`, la posición 5 intacta). Queda arreglado en esta misma fase con su
docstring explicando que la posición es el contrato y el denominador es historia de la numeración.
Consecuencia: el `post` vuelve a los **3** rojos ajenos publicados, y se añade a la suite un test
de coherencia de numeración (`test_el_hook_versionado_invoca_el_script_y_su_numeracion_no_tiene_huecos`)
para que el próximo cambio de denominador no pueda repetirlo en silencio.

## 5. Qué NO prueba este archivo

- Que los 29 tests nuevos observen lo que dicen observar: eso lo prueba el mutation check
  (`run_nr7_capitalizacion.py`, 13/13 con sus dos salidas en este directorio), no el conteo.
- Nada sobre el árbol de `output/` ni sobre corridas del pipeline: esta fase no toca el pipeline.
