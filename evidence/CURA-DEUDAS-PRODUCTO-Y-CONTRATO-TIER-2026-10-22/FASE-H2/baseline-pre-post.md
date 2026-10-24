# FASE-H2 — par pre/post y resta (R2.3 / R2.7, AC8)

Medición de la fase sobre el árbol vivo.HEAD de partida: `3b0087c` (FASE-H1 publicado), árbol limpio al abrir la sesión.

## La resta

| Concepto | PRE | POST | Delta | Instrumento |
|---|---|---|---|---|
| Funciones test canónicas (`grep -rE "^\s*def test_" tests --include=*.py \| wc -l`) | 5.478 | 5.483 | **+5** = +17 nuevas − 12 retiradas | el comando de la fila, medido en `d18-d22-d23-d20_baseline_pre.txt` y `..._post.txt` |
| Archivos de producción que abren `config/settings.yaml` | 1 (`modules/utils/http_client.py`, por `scrapers.requests`) | 1 | 0 | `test_el_unico_consumo_del_archivo_es_scrapers_requests` |
| Referencias a las cuatro claves `thresholds` en `modules/`, `main.py`, `scripts/` | 0 | 0 | 0 (y la clave ya no existe en el YAML) | `test_d18_settings_sin_thresholds.py` |
| Claves `thresholds` publicadas en `config/settings.yaml` | 4 | 0 | **−4** | `test_el_bloque_thresholds_ya_no_es_configuracion` (AST del YAML + cabecera) |
| Definiciones de `validar_arbitraje_etico` en `modules/` | 1 | 0 | **−1** | `test_d22_arbitraje_etico_retirado.py` por AST |
| Tests que ejercitaban el dead code | 12 | 0 | **−12** | `test_no_queda_su_bateria_de_tests` |
| Consumidores de `EthicsGate` (el gate ético real) | 3 sitios en `publication_gates.py` | 3 | 0 (intacto, por contrato de la fase) | `test_el_gate_etico_real_no_se_muevo` |
| Divergencias docstring↔rama en `_check_claim_vs_evidence` | 2 (`or`↔`and`, `>`↔`>=`) | 0 | **−2** | `test_d23_claim_vs_evidence_frontera.py` (el docstring debe contener el `ast.unparse` de la rama) |
| Tablas regionales con rol declarado frente al maestro | 0 | 6 (5 de `N5` + el propio `.md`) | **+6** | §0 de `data/benchmarks/Benchmarking.md` |
| Números movidos en `regional_adr_2026.json` / `plan_maestro_data.json` | — | — | **0** | `test_benchmark_paridad_tablas_fase_e.py` sigue verde sin re-anclar |

## Poblaciones declaradas (R2.10)

- **Lectores**: población = `modules/**/*.py` + `main.py` + `scripts/**/*.py`, sin `__pycache__`. `tests/` se excluye del guard de claves retiradas porque la prosa de un test puede nombrar lo que corta (hacerlo no es leerlo); el guard de `D22` sobre tests sí corre, auto-excluyendo el archivo que nombra el símbolo.
- **Literales de config**: se comprueba por clave parseada (`yaml.safe_load`) y por cabecera de bloque (`^thresholds:` en MULTILINE), no por substring suelto: `min_reviews:` vive también en `package_thresholds`, que no es el bloque de `D18`.
- **Valores**: `D18`/`D20` se barren por **símbolo con nombre** (`gbp_min_score`, `schema_required`, `min_reviews`, `min_photos`, `gbp_score_bajo`, `umbrales_fotos`), nunca por literal global.

## Lo que NO verifica un instrumento mecánico (L-R.4)

- **No existe verificador mecánico de esta resta**: las dos columnas PRE/POST las imprime el comando de la última columna, corrido a mano sobre el árbol; nadie las cruza.
- **No existe par pass/fail de la suite completa**: se publica el punto medido (`pytest-suite-completa-post.txt`) y la atribución del rojo que sobrevive (`atribucion-rojo-deepseek.txt`).
- **La divergencia de `Benchmarking.md` con el horque `v25_config.umbrales_decision` queda declarada, no curada**: el Operador la difirió hasta después de E2E para no desplazar el baseline de AC7 (decisión del 2026-10-23). El assert de divergencia de FASE-E sigue cortando en los dos sentidos.

## Efecto del escritor, no autoría de la sesión (declarado con su crudo)

`01-plan-maestro.md` §3 y los dos prompts `05-prompt-inicio-sesion-fase-E2E{,-PRE}.md` cambiaron a las 09:40, en el minuto de la estampada con `log_phase_completion.py --check-manual-docs`. Esta sesión no los editó y no figuran en la entrada del REGISTRY. El diff íntegro queda en `crudo-efecto-del-escritor.txt` para que el Operador lo valide —es coherente con la regla de delegación ya aplicada a los prompts de este plan— o lo revierta con `git checkout --` sobre esas tres rutas antes de commitear.

## Hueco declarado del REGISTRY (no corregible por el escritor)

La entrada de FASE-H2 se estampó con `log_phase_completion.py` y lista 3 tests + 14 artefactos de evidencia. Tres archivos se escribieron **después** del estampado y no figuran en la entrada: `verificacion-final.txt`, `crudo-quick-final.txt` y `crudo-efecto-del-escritor.txt`. El escritor se niega a re-ejecutarse sobre una fase cerrada y apila duplicados si lo intentas, así que esto se corrige a mano o lo cierra FASE-RELEASE — mismo trato que el hueco declarado por FASE-F.

## Verde final verificado (no copiado de la fila anterior)

- `run_all_validations.py --quick` → **13/13, EXIT=0** con el exit leído sin tubería (crudos `crudo-quick-1.txt` 12/13 EXIT=1 por el derivado vencido, `crudo-quick-2.txt` y `crudo-quick-final.txt` 13/13 EXIT=0).
- Selección del prompt + baterías vecinas → **104 passed** y el único rojo es `test_all_config_files_have_description` (PREEXISTENTE, dueño Operador: `config/secret_fragment_policy.yaml` sin campo `description`).
- Vallas verificadas por `git diff --quiet`: `booking_scraper.py`, `autonomous_researcher.py`, `tribunal/judge.py`, `gbp_auditor.py`, `rubrica_gbp.py`, `umbrales_fotos.py`, `config/regional_benchmarks.yaml`, `regional_adr_2026.json`, `plan_maestro_data.json`, `ethics_gate.py` → **sin cambios**.


## Mutantes (R2.8)

Cuatro mutantes sobre el símbolo real del guard, en `par-rojo-verde-mutantes.txt`, con sha256 PRE/POST de los archivos tocados y verde final idéntico al inicial (32 passed):

- **M1** re-introduce el bloque `thresholds` en el YAML → 1 rojo (`test_el_bloque_thresholds_ya_no_es_configuracion`).
- **M2** restaura el módulo y su batería desde HEAD → 4 rojos del guard de `D22` (definición AST, import, batería, prosa). El test del `EthicsGate` queda verde: el mutante no lo toca, y así el guard no confunde "gate real" con "gate aparente".
- **M3a** restaura el docstring divergente → 2 rojos (cita y promesa de disyuncion/frontera). Las pruebas de comportamiento siguen verdes: prueban que el mutante es de prosa, no de rama.
- **M3b** invierte la frontera de la rama (`>=` → `>`) → 3 rojos, incluido `test_frontera_rating_igual_4_dispara`. Prueba que la frontera está juzgada por el código y no por el texto.
