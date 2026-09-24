# FASE-C — par pre/post, resta comprobada y presupuesto declarado

Plan: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` · Fase: **C** · Fecha: **2026-09-24**
Corte usado: **«hasta listo para revisión»** (el otro corte del contrato, «hasta el commit de código»,
**no** aplica: el commit no estaba autorizado). El commit es una acción posterior y separada, no un corte
ni condición de ninguno de los cinco (executor, *Cinco cortes*).

## 1. AC16 — conteos de checks: delta **0**, con la resta

La composición del `--quick` y del hook **no** se tocó en esta fase. Los valores los imprimen los
comandos; este archivo los registra como par, no como cifra vigente del repo.

| Conteo | Comando (idéntico en los dos lados) | PRE (antes de la primera edición) | POST (árbol final) | Resta |
|---|---|---|---|---|
| Etiquetas `[N/11]` en `scripts/run_all_validations.py` | `grep -cE '^\s*print\(f?"\[[0-9]+/11\]' scripts/run_all_validations.py` | **11** | **11** | **0** |
| Pasos `[N/7]` en `scripts/git_hooks/pre-commit` | `grep -cE '^#   \[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit` | **7** | **7** | **0** |

Archivos del par: `faseC_baseline_pre.txt` / `faseC_baseline_post.txt` y
`faseC_quick_pre.txt` / `faseC_quick_post.txt`. El PRE se capturó **antes de la primera edición de
código**, con el HEAD de la sesión anotado dentro de cada archivo.

Comprobación de la resta: 11 − 11 = 0 y 7 − 7 = 0, y el `--quick` completo quedó **11/11 con `exit 0`**
en el POST (ver `run_all_validations_quick_post.txt`). Delta esperado: **0** (AC5/AC16) — cumplido.

## 2. Lo que **sí** se movió en esta fase, declarado aparte y no maquillado

| Magnitud | PRE | POST | Por qué se mueve y quién lo mide |
|---|---|---|---|
| Funciones de test (`grep -rE '^\s*def test_' tests --include=*.py \| wc -l`) | no medido al abrir (ver nota) | **4.508**, de las que **46** son de `tests/quality_gates/lesson_relevance/` (56 casos al parametrizar) | Contribución propia contada con comando aparte. **La resta total no es achacable a C**: el árbol traía 62 rutas de trabajo ajeno sin commitear, incluidas cuatro rutas `.py` de otras sesiones. El PRE no se midió al abrir: se publica la contribución, no una resta inventada |
| IDs definidos en el índice de lecciones (`python scripts/build_lesson_index.py --check`) | **332** | **334** | La fase define dos lecciones nuevas con su medición en `10-analisis-post-implementacion.md` (**L-VCF-13**, **L-VCF-14**). Es la medición **A6** reproduciéndose sobre esta misma fila: el acto de escribir el cierre mueve la cifra del cierre, y por eso ningún artefacto de C la pinea (hay test que prohíbe los literales en el script) |
| Población del escáner AC6 vs `git ls-files '*.py'` | — | **731** vs **696**, desfase **35** | Desglosado archivo por archivo en `cero-red.txt` (15 rutas propias + 20 ajenas preexistentes). Con `.venv-wsl` ya declarado en las exclusiones (S11 aceptada), el desfase **no** es una exclusión oculta: es medir una población en disco y la otra en el índice de git. **Auto-refutación dentro de la sesión**: la primera medición dio 34 y quedó refutada por el instrumento de cierre que se escribió después |
| `.agents/` (AC17) | **3 rutas sucias ajenas** al abrir (mediado antes de la primera edición: `phased_project_executor.md`, `templates/lecciones-capitalizadas-template.md`, `templates/prompt-fase-template.md`) | **las mismas 3** | C **no** escribió en `.agents/`: no hay ninguna ruta nueva ni cambiada por esta fase. La fila de AC17/A y B decía «`git status --porcelain .agents/` vacío»; eso ya no describe el árbol, y la suciedad **no** es de C. Se declara en lugar de «limpiarla» |
| `docs/contributing/REGISTRY.md` | +27 líneas de trabajo ajeno | **+45 / −2** | `log_phase_completion.py` es **aditivo** y corrió **una sola vez** para FASE-C. La mezcla con el trabajo ajeno preexistente se declara: sin commit es ruido de atribución, no pérdida. No se hizo `checkout`/`restore`/`stash` sobre esa ruta |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | ya estaban modificados por trabajo ajeno | regenerados por C sobre el árbol final | Son artefactos generados: `[6/7]` del hook los corta si van vencidos. La regeneración se hizo **después** de la última escritura de `.md` y se verificó con `--check` |

## 3. Presupuesto (R2.1) — instrumento, corte y unidad declarada

**El instrumento canónico NO corrió.** `find . -name "*.jsonl" -not -path "./venv/*" | wc -l` devolvió
**0** al abrir la sesión (re-medido, no copiado del prompt): es la **séptima reproducción** de la
precondición que capitalizó **D-V2.1**, y vuelve a ser la misma condición que documentaron
`PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` y `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`.
`evidence/FASE-D/measure_iterations.py` pide el transcript del cliente, que no existe en el workspace,
así que **no se puede medir** el número de iteraciones con instrumento.

Consecuencia aplicada como manda el contrato (§Corte de presupuesto): **la métrica se retira y se
publica como auto-reporte con unidad declarada, no estimada, y se declara que no es comparable** con las
tres horas del bloque B ni con unidades de otros planes.

| Unidad | Valor reportado | Método y su límite (declarado, no escondido) |
|---|---|---|
| `tool_use` con ids únicos | **auto-reporte: banda 85–95 invocaciones** al cerrar el corte | Conteo **manual** sobre los bloques de herramienta de esta sesión. El método no es auditable por un tercero, por eso se publica como banda y no como cifra exacta: dar un número preciso con un método impreciso sería la familia de la aserción sin fuente que este plan caza. **Techo de 160: no alcanzado** |
| Ediciones | **49 operaciones de Write/Edit** sobre **15 archivos distintos** | El techo del mandato era «30 ediciones» y la unidad no estaba definida. **Bajo la lectura por operaciones el techo se superó; bajo la lectura por archivos no.** El operador fue consultado el mismo día y resolvió gobernar por **archivos** y autorizar el cierre documental. Se publica aquí la medición de las dos lecturas para que la decisión quede con su base, no con la memoria de la conversación |
| Archivos propios en disco | 15 de código/tests/instrumento + el expediente de `FASE-C/` | `git status --porcelain --untracked-files=all -- scripts/triage_lesson_relevance.py tests/quality_gates/lesson_relevance evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C \| grep -c '^??'` |

**Nunca se estimó cumplimiento.** Ninguna AC de esta fase se certificó apoyándose en un presupuesto
aproximado, y ningún `✅` se dio por haber llegado lejos: AC15 quedó ⚠️ porque su tramo semántico no se
ejercitó, no porque faltara tiempo.

## 4. Rojos de la fase (L-VUP-5)

Sin un solo rojo, AC14 sería ⚠️. La fase produjo rojo propio y rojo pedido: ver `cero-red.txt`
(§«Rojos que produco la fase») y `mutation/` (verde 14→14 y rojo 14→3). El rojo preexistente
`test_medido_contra_el_predecesor_entra_en_alcance…` sigue atribuido a su dueño en los registros de
`REFACTOR-WHATSAPP` y en la matriz §13 de la fuente única del bloque B; no se tocó ni se ocultó.
