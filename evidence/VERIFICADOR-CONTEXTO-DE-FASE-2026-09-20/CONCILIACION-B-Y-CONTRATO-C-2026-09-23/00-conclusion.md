# Conclusión — conciliación de FASE-B y contrato de FASE-C (2026-09-23)

**Qué es esto.** Evidencia de una sesión de **solo documento** sobre el plan
`VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`: acepta en el plan propietario la remediación que el
**bloque A** de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` hizo en `fdd397f`, rectifica dos
advertencias del README que esa remediación dejó vencidas, y **prepara contractualmente FASE-C sin
ejecutarla**. No se modificó código, tests, configuración central, hooks ni validadores. No hubo red,
QMind, fetch, SDKs, pipeline, archivado, commit ni push. **No se volvió a registrar FASE-B en
`REGISTRY.md` ni se movió `VERSION.yaml`.**

**Qué NO es.** No es el cierre de FASE-B (cerró el 2026-09-21 y se commiteó el 2026-09-22 en
`647f436`), ni la remediación (es de las cuatro sesiones del bloque A, en `fdd397f`), ni la ejecución
de FASE-C. Los tres momentos van separados en `dependencias-fases.md` §Conciliación y no se atribuyen
entre sí.

## Estado del árbol al abrir (medido, no asumido)

| Cosa | Medido el 2026-09-23 | Comando |
|---|---|---|
| HEAD local | `fdd397f` — *fix(quality-gates): remediación bloque A de la orden de calidad 2026-09-22* | `git rev-parse --short HEAD` |
| Paridad con `origin/master` | **0** commits por delante | `git rev-list --count origin/master..HEAD` |
| Trabajo ajeno en el árbol | **1** ruta modificada: `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` — **preservada intacta**, sin `git checkout` y sin commitear | `git status --porcelain` |

Que HEAD vaya por delante de `origin/master` es **el dato más inestable de esta sesión**: el commit que
lleve estas palabras lo vuelve a mover. Por eso la fila de arranque del README del plan publica
**comandos**, no esta cifra, y por eso quien abra C la re-mide.

## Revalidación de los pendientes contractuales

Instrumentos **existentes**, reutilizados; no se añadió instrumentación nueva.

| # | Comprobación | Comando | Salida / código |
|---|---|---|---|
| 1 | **AC6** — aislamiento de imports | `python scripts/decision_client.py --scan-imports` | `[SIN-HALLAZGOS]`, **0** imports prohibidos, **0** cargas dinámicas · población **696/9655** `.py`, `excluidos` publicando `.venv-wsl: 582` · **`EXIT=0`** → `scan_imports_2026-09-23.txt`, `.meta` |
| 2 | **S11** — paridad del denominador | `git ls-files '*.py' \| wc -l` | **696**, igual al universo que incluye el escáner → **residuo 0**. La resta que B publicó (692 − 691 = `.venv-wsl/bin/activate_this.py`) ya no existe: `activate_this.py` está en disco (1) y no está rastreado (0) |
| 3 | **S12** — volver a medir no pisa el pasado | `python scripts/validate_governance_numbers.py --report` **sin destino** | **`EXIT=1`** con `status: HALLAZGOS` y `assertion_ids = ['A1','A2','A3','A4']` en **stdout JSON puro**; stderr: `# no se escribio ningun archivo: pase --report RUTA para persistir el informe` → `reporte_gobernanza_stdout_2026-09-23.json`, `_stderr_` |
| 4 | **S12** — evidencia de FASE-A intacta | `sha256sum evidence/…/FASE-A/informe.json` antes y después | **`1111f9b2e1d32e9803c50864183a92e6ebd0cc5830e4dcc8b8b5fda8b7de1037`** idéntico en las dos tomas; `git status --porcelain evidence/` **vacío** después de la corrida |
| 5 | **AC7** — proveedor no configurado | `python scripts/decision_client.py --provider-status` | `provider_status: NO-CONFIGURADO`, con `IAH_DECISION_PROVIDER` y `IAH_DECISION_PROVIDERS_DIR` buscados y **ninguna decisión por defecto** · **`EXIT=1`** (según la tabla del docstring: 1 = no resolvió) → `provider_status_2026-09-23.json` |
| 6 | **AC9** — coste de añadir un proveedor | `python scripts/decision_client.py --costura` | `files_changed_to_add_provider = **1**`, `agregados = [falsos_proveedores/falso_segundo.py]`, `modificados = []` · **`EXIT=0`** · y el informe imprime su propio límite: `alcance_de_ac9 = "medicion LOCAL… No es el coste certificado de integrar un SDK real con sus dependencias y su autenticacion; la ubicacion futura de ese SDK es CONTEXTO/S10 y D7"` → `costura_remedida_2026-09-23.json` |
| 7 | **Forma de la respuesta** (para E1) | lectura de `scripts/decision_client.py` | `RespuestaEleccion` = `eleccion` + `probabilidades` de **todas** las opciones + **`confidence` obligatoria**; `RespuestaNoul` = solo `probabilidad_si`, con **`confidence = None`** y su `confidence_motivo`. **Confirmado contra el código, no contra el docstring**: `probabilidad_si` ≠ confianza |
| 8 | **Selección de tests** (no la suite completa) | `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/quality_gates/decision_client -q -p no:cacheprovider` | **87 passed**, `EXIT=0` en 8,04 s → `pytest_seleccion_decision_client_2026-09-23.txt` |
| 9 | **Selección `governance_numbers`** (donde viven las regresiones de S11/S12) | `python -m pytest tests/quality_gates/governance_numbers -q` | **40 passed**, `EXIT=0` en 10,52 s · **35 funciones / 40 casos** (el excedente es un `parametrize` de 6 mutantes: M-A1, M-A2, M-A3, M-A4, M-POBLACION, M-SUJETO) → `pytest_seleccion_governance_numbers_2026-09-23.txt` |
| 10 | **Las regresiones de S12, aisladas por nombre** | `python -m pytest tests/quality_gates/governance_numbers/test_governance_numbers_s12_report_no_escribe.py -v` | **6 passed**, `EXIT=0` — y los nombres son la prueba de que apuntan al guard de S12 y no a otro: `…_sin_destino_no_toca_el_expediente_cerrado`, `…_declara_que_no_escribe_en_lugar_de_hacerlo_a_escondidas`, `…_publica_json_parseable_por_stdout`, `test_report_con_destino_nombrado_si_escribe_ahi`, `test_el_script_ya_no_conoce_ruta_de_evidencia_como_destino_de_escritura`, `test_la_costante_del_default_vacio_no_revive` → `pytest_s12_report_no_escribe_2026-09-23.txt` |
| 11 | **Payloads del hook que el `--quick` no cubre** | `python scripts/version_consistency_checker.py` · `python scripts/sync_versions.py --check` · `python scripts/validate_plan_closure.py` | los tres **`EXIT=0`**: 4.77.3 sincronizado y `REGISTRY OK` · `All files in sync` · `[OK] ningún plan vivo declara cierre con filas pendientes` → `instrumentos/HOOK_{1_7,2_7,5_7}_*.txt` |
| 12 | **R2.8 — mutantes de `governance_numbers`, por id** | `python -m pytest tests/quality_gates/governance_numbers/test_governance_numbers_mutation_por_asercion.py -v` | **7 passed**, `EXIT=0`: los seis mutantes nombrados (`M-A1`, `M-A4`, `M-A2`, `M-A3`, `M-POBLACION`, `M-SUJETO`) + `test_las_dos_salidas_quedan_en_disco` → `instrumentos/MUT_governance_numbers_por_asercion.txt` |
| 13 | **R2.8 — guardas de la costura, por id** | `python -m pytest tests/quality_gates/decision_client/test_decision_client_mutation_guards.py -v` | **13 passed**, `EXIT=0`: `M_AC6_token_prohibido…`, `M_AC6_carga_dinamica…`, `M_AC6_superficie_de_proveedores…`, `M_AC7_proveedor_por_defecto…`, los 6 guards de forma y `test_cada_mutante_apunta_a_un_simbolo_distinto_y_vigente` → `instrumentos/MUT_decision_client_guards.txt` |

**El rojo contractual se conservó por causa, no solo el verde.** Las filas 3 y 4 registran deliberada-
mente una salida **`EXIT=1`**: A1–A4 siguen vencidas en `.agents/` porque este plan **no** edita
configuración central (AC17) y su corrección es **D1**, con instrucción literal del operador. Ninguna
aceptación de S11/S12 convierte ese rojo en PASS, y la suite verde no lo toca.

**Resultados históricos, no de esta sesión** (para que no se confundan): la suite completa la corrieron
las sesiones del bloque A y no se repitió aquí por rutina — `sesion3_suite_completa.txt` reporta
**4.393 passed / 4 failed** y `sesion4_suite_completa.txt` **4.396 passed / 4 failed** (ambas con
`EXIT=1`, los mismos 4 fallos atribuidos allí por el bloque A); el `53 casos / 48 funciones` es de
FASE-B en `647f436`; `150` y `153 passed` son las selecciones afectadas que publicaron la sesión 3 y la
4. **De esta sesión hay tres corridas de tests: las filas 8, 9 y 10 (87 / 40 / 6 casos, todas `EXIT=0`), y
no se repitió la suite completa.**

## Baseline de validaciones

| Momento | `run_all_validations.py --quick --check` | `build_lesson_index.py --check` |
|---|---|---|
| **PRE** (antes de la primera edición) | **11/11** `ALL VALIDATIONS PASSED`, `EXIT=0` → `PRE_quick_check_11x11.txt` | `[OK] Índice de lecciones fresco (332 IDs)`, `EXIT=0` → `PRE_lesson_index_check_332.txt` |
| **POST** | ver `instrumentos/POST_verificacion_cierre.md` | ídem |

## Qué se decidió para CONTEXTO/C (contrato, sin implementar)

Cinco reglas **E1–E5** escritas en `04-contrato-ejecucion.md` §Enmiendas y conciliadas en maestro §2 y
§4, `05-prompt-inicio-sesion-fase-C.md`, `06-checklist-implementacion.md`, `09-`, `10-`,
`dependencias-fases.md` y `README.md`:

- **E1** pregunta binaria como **`choice` de dos opciones**, umbral sobre `confidence`, **nunca** sobre
  `probabilidad_si` (base: fila 7).
- **E2** **AC11 cierra su elección abierta en la ruta (b)**: C comprueba la frescura **él mismo** antes
  de consumir `lecciones_index.json`; `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` con su test cada uno.
- **E3** una propuesta del proveedor falso **no entra en §2 sin revisión humana explícita**, con
  aceptación o rechazo **registrados**. Esto **reescribió** el paso 6 del post-ejecución de C, que
  mandaba lo contrario: una nota al margen no basta contra una instrucción ejecutable vigente.
- **E4** AC15 semántico **`NO-EJERCITADO`** con motivo, **prohibido simular** la aceptabilidad; **D6
  dormida**.
- **E5** C **conserva el workflow canónico y el proceso común vigentes**; los bloques B y C de la orden
  quedan **diferidos, no aplicados ni declarados cerrados**.

**Dos contradicciones que E5 obligó a encontrar y corregir en el prompt de C**: una fila de Restricciones
ofrecía un «tope de 200 llamadas por sesión» que el contrato **no** autoriza (allí no hay tal tope: la
red está prohibida en toda fase), y el bloque pegable referenciaba una sección «tope de llamadas» del
contrato que no existe. Ambas quedan rectificados con su nota.

**Permanecen abiertas, declaradas y sin convertirse en bloqueantes artificiales de una C offline** (más **S13**, la escritura hardcodeada del arnés de mutación, hallada al re-evidenciar R2.8 y registrada en `10-analisis` con su disparador):
**S10** (dónde vivirá el `import` del SDK cuando D7 se active), **D7** (activar el proveedor), **D6**
(dormida, condicionada al `acceptance` semántico), **D1** (A1–A4 en `.agents/`), **D2/D3**, **D8/D9/D10**.

## Segunda pasada: cuatro deudas de verificación que esta conclusión declaraba abiertas

El dictamen inicial de esta sesión listó cuatro cosas que **no** había verificado. Se cerraron las cuatro,
y dos de ellas produjeron correcciones de cifra sobre los propios documentos del plan:

| Deuda declarada | Cómo se cerró | Resultado |
|---|---|---|
| «La selección `governance_numbers` no se ejecutó» | filas 9 y 10 arriba | **40 casos `EXIT=0`**, y las regresiones de S12 **6 por nombre** `EXIT=0`. **Corrección: no eran 5 sino 6 funciones** — `dependencias-fases.md` y `10-analisis` decían «cinco tests»/«5 tests», rectificados con su medición |
| «Los 7 pasos del hook no se midieron en esta sesión» | conteo por corriente en HEAD y en árbol + corrida de los payload en modo lectura | **7 → 7**, y los tres payload que el `--quick` **no** despacha (`[1/7]`, `[5/7]`, `[6/7]`, verificado leyendo a qué script llama cada check) dan **`EXIT=0`** → `baseline-pre-post.md` §«Los siete pasos del hook» |
| «No existe el par `*_baseline_pre.txt` / `*_baseline_post.txt` del contrato» | escrito el par + `baseline-pre-post.md` con la resta, en esta misma ruta | **Resta 0** en **17 de las 19** unidades que publica `baseline-pre-post.md` (las otras dos son líneas del índice regenerado y la carga de lectura, que no aspiran a ser 0); **única métrica de checks movida: ninguna — carga de lectura +54.372 bytes (+13.593 tokens)**, publicada restada y no maquillada (L-D3). Sus tres lecturas anteriores (+50.709, +52.160 y +53.337) quedaron vencidas por ediciones posteriores de esta misma sesión y se re-midió (A6) |
| «Los mutation checks de A/B no se re-evidenciaron» (era el punto 2, y **este sí quedó abierto en la primera pasada** de esta sección) | `pytest -v` sobre los dos arneses existentes, sin editar código: cada mutante imprime su id | `test_governance_numbers_mutation_por_asercion.py` → **7 passed** con los 6 ids (`M-A1`…`M-SUJETO`); `test_decision_client_mutation_guards.py` → **13 passed** con `M_AC6_*` ×3, `M_AC7_*` y los 6 guards de forma. **Y el arnés devolvió un hallazgo nuevo → S13** (escribe por ruta hardcodeada en `evidence/…/FASE-A/mutation/`) |
| «Que `evidence/` esté fuera del corpus del índice fue una inferencia» | lectura del generador | **echo de lectura, no inferencia:** el corpus son `plans_dir.rglob("*.md")` y `context_dir.rglob("*.md")` con `DEFAULT_PLANS = .opencode/plans` y `DEFAULT_CONTEXT = .opencode/context` (`scripts/build_lesson_index.py:50-51, 235, 243`). `evidence/` no entra por construcción |

**Dos artefactos de instrumento que habrían producido hallazgos falsos**, y quedan escritos para que no se
repitan:

1. **`git show HEAD:<f> | sha256sum` vs `sha256sum <f>` no casa en este repo.** Con `core.autocrlf=input`,
   el blob de `run_all_validations.py` mide 36.499 bytes y 0 CR contra 37.412 y 913 CR en disco: la
   comparación denuncia como «tocaron el script de validaciones» un script **intacto**. El instrumento que
   decide es el hash de objeto con el filtro limpio (`git rev-parse HEAD:<f>` vs
   `git hash-object --path=<f> <f>`) y `git diff`; los cuatro scripts gobernados casan.
2. **El número de IDs del índice se lee del generador, no de un conteo propio.** Un
   `grep -cE '^\| `' sobre `LECCIONES-INDEX.md` da **387** y no son IDs definidos: la cifra canónica es
   `cobertura.ids_con_definicion` = **332** en HEAD y **332** en el árbol (L-R.3).

**También rectificada la atribución de S11** en `10-analisis`: la fila decía que el bloque A la cerró «con
su test de población (2 funciones)». Medido con `git show fdd397f`, sus tres funciones de exclusión viven
en `tests/quality_gates/decision_client/test_decision_client_aislamiento_imports.py` (+83/−11), no en
`governance_numbers`.

## Lo que queda pendiente de autorización

1. **Commit** de este árbol documental — y con él la decisión sobre las cabeceras versionadas que toca el
   hook `version-sync`. **No se hizo commit en esta sesión.**
2. **Push**, instrucción aparte.
3. **FASE-C**: su ejecución pide mandato propio (esta sesión **preparó** su contrato y **no** lo ejecutó).
4. Bloques **B** y **C** de la orden de calidad, cada uno con su autorización.

## Consecuencia conocida de esta edición sobre el índice

Estos documentos citan IDs del corpus, así que `.opencode/LECCIONES-INDEX.md` y
`.opencode/lecciones_index.json` se **regeneran después de la última edición** y deben viajar en el
**mismo commit** que esta evidencia (`[6/7]` del hook). No se editaron a mano.
