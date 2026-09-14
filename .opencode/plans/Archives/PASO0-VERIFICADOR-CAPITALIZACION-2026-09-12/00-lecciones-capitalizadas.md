# Lecciones Capitalizadas — PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

> **Creado**: 2026-09-12, **antes** de `01-plan-maestro.md` y de los prompts de fase. **Actualiza**: al cierre de cada fase.
> **Plan**: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 · **Objetivo**: un verificador mecánico que impida publicar un plan sin capitalización efectiva del corpus.
> **Hito**: primera vez que el Paso 0 se ejecuta **en la concepción** del plan, no a posteriori. El archivo
> se escribe vacío de diseño: al momento de redactarlo no existe `01-plan-maestro.md` ni AC alguno, así
> que la columna «qué cambia» de §2 nombra ACs que **este mismo archivo compromete a crear** y que el
> verificador va a poder comprobar (el verificador exige que el AC exista en el maestro; si el maestro
> no los crea, el `[7/7]` bloquea el cierre).

**Estado del archivo.** Escrito con el template `.agents/workflows/templates/lecciones-capitalizadas-template.md`
(executor v2.23.1). Cada enunciado de §2 está copiado del corpus vía `.opencode/LECCIONES-INDEX.md` y su
JSON hermano, **no de memoria** — la lección viene del plan predecesor, que tuvo 7 filas mal atribuidas
hasta que el índice las corrigió. Q7 abajo verifica por adelantado que las atribuciones de este archivo
son correctas con el mismo criterio que el verificador va a exigir.

---

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado medido |
|---|------|------------------|------------------|
| Q1 | Índice generado (capa fría, corpus **completo**) | `grep -icE "verificador\|cobertura\|candado\|pre-commit\|falso verde\|baseline\|plantilla\|fosiliz" .opencode/LECCIONES-INDEX.md` y luego `grep -ioE "\`\| [A-Z][A-Za-z0-9._-]*\`"` sobre esa pasada | **27** líneas recuperadas → **26** IDs: `D-NC2 D-NC4 D-NC6 DA-G4 DA-HF3 DA-V1 L-A5 L-B1 L-C2 L-D2 L-D3 L-HF1 L-NC4 L-NC10 L-NC12 L-PF10 L-R.3 L-R.4 L-T2B.1 L-T4B.5 L-VUP-1 L-VUP-5 L-VUP-6 L-VUP-14 S-H17 S-I8` — dueños en **5** planes/CONTEXTs distintos |
| Q2 | Memoria (capa caliente: usuario + proyecto) | `grep -ril "verificador\|cobertura\|automatiza\|pre-commit" ~/.qoder/memory/ ~/.qoder/projects/C--Users-Jhond-Github-iah-cli/memory/` | **8** archivos: 5 de usuario (`cobertura-del-verificador-se-mide`, `quien-produce-el-dato-publicado`, `preferencia-automatizacion-sobre-disciplina-manual`, `preferencia-diferir-alcance-con-deuda-registrada`, `feedback-contexto-decision-proceso-con-evidencia-medida`), 2 de proyecto, 1 índice |
| Q3 | Notebook QMind `iah-cli-lecciones` (46 fuentes) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "verificador mecanico de un artefacto documental: cobertura, regla que nace sin check, verde que no prueba ausencia" --format agent` | `total: 4`. Primero con score **0,9124**: `L-HF1` (ESTABILIZACION-PRE-TRIBUNAL) — «al extender la cobertura de un candado, **medir primero su población** … y escribir el candado sobre la **propiedad**, no con regex sobre el texto» |
| Q4 | Notebook QMind | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "check nuevo en pre-commit que falla contra archivos historicos: exencion grandfather, ruido permanente, hacia delante" --format agent` | `total: 2`, **ambos** el mismo archivo: `.opencode/context/Historico/CONTEXT-DECISION-PRE-COMMIT-FRAMEWORK-2026-08-29.md` → **responde la pregunta de diseño «¿dónde vive el check?»**: `.pre-commit-config.yaml` está «declarado completo (13 hooks) pero **sin enforcement real**» y la decisión registrada del usuario es que «la Opción 1 queda vigente: hook custom versionado en `scripts/git_hooks/`» |
| Q5 | Notebook QMind | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "arte factos generados que se editan a mano y quedan fosiles: plantilla, writer, declaracion de cobertura desactualizada" --format agent` | `total: 5` con scores bajos (≤ **0,4264**: `L-NC10` fosilización narrativa y el `10-analisis` del TRIBUNAL-OFFLINE). La consulta es débil tal como está redactada; el hallazgo se recupera por Q1, no por QMind → registrado en §3.b |
| Q6 | Repo (población que el verificador cubriría) | `find .opencode/plans -name "00-lecciones-capitalizadas.md" \| wc -l`; `find .opencode/plans -maxdepth 1 -type d ! -name plans ! -name Archives \| wc -l`; `find .opencode/plans/Archives -maxdepth 1 -type d ! -name Archives \| wc -l`; `ls .opencode/plans/Archives \| grep -cvE "2026-[0-9]{2}-[0-9]{2}"` | **1** archivo `00-` en todo el repo · **1** plan vivo · **25** archivados · **6** archivados **sin fecha parseable** en el nombre. Cobertura actual de la regla: **1 / 26 = 3,8 %**. Con corte «fecha del nombre ≥ 2026-09-12» (executor v2.22.0): **0 archivados** entran en alcance → el check no puede ser ruido permanente |
| Q7 | Repo (factibilidad de los checks propuestos, medida sobre el único artefacto real) | script ad-hoc: parsear la tabla §2 de `.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/00-lecciones-capitalizadas.md` y confrontar cada ID contra el dueño de `.opencode/lecciones_index.json` | §2 tiene **18** filas · **18/18** dueños coinciden con el índice · **0** mal atribuidas · **0** sin definición · **6** dueños distintos (≥ 2 que exige C8) · **17** filas nombran un `AC-*` o una tarea. El umbral no está inflado: un artefacto humano real ya lo cumple |
| Q8 | Repo (decisión de diseño del verificador) | `python -c "import sys,time; sys.path.insert(0,'scripts'); import build_lesson_index as b; t=time.time(); b.build(b.DEFAULT_PLANS,b.DEFAULT_CONTEXT); print(time.time()-t)"` | **0,30 s** para 346 `.md` y 246 IDs definidos → el verificador puede **calcular el índice en memoria** en vez de leer `.opencode/lecciones_index.json`: no depende de que otro check (`[6/6]`) lo mantenga fresco. Coste asumible en pre-commit |
| Q9 | Repo (qué hay que re-verificar antes de heredar) | `grep -nE "^\- \*\*v2\.2[0-9]\.0" .agents/workflows/phased_project_executor.md` y `grep -c "validate_plan_closure\|build_lesson_index" scripts/run_all_validations.py` | v2.22.0 y v2.23.x son **2026-09-12** (el corte es hoy) · v2.21.0 es 2026-09-11 · `validate_plan_closure.py` y `build_lesson_index.py --check` aparecen **0 veces** en `run_all_validations.py`: los dos verificadores de disciplina de plan viven **solo** en el hook (`[5/6]`, `[6/6]`), mientras `validate_plan_citations.py` y `validate_opencode_refs.py` están **doble-cableados** (hook + `--quick`) |
| Q10 | Repo (riesgo de tocar el conteo de checks) | `grep -rln "run_all_validations" tests/` y conteo de tests por validator: `grep -cE "^\s\*def test_" tests/test_validate_plan_closure.py tests/test_validate_plan_citations.py tests/test_build_lesson_index.py` | **0** contract tests afirman el número de checks de `run_all_validations.py` (el único hit es un test del hook-pdf que la menciona en un mensaje) → renumerar `[n/8]`→`[n/9]` no rompe tests. Precedente de tamaño de suite de un validator: **9 / 9 / 16** tests |

**Contraste con la señal que originó este tramo de deuda**: el predecesor llegó a citar **una sola fuente**
(su predecesor) y tuvo que instanciarse a posteriori. Este archivo, en su primera pasada, recupera 26 IDs
de 5 dueños (Q1), y dos de las respuestas que cambian el diseño — Q4 (dónde vive el check) y Q8 (de dónde
lee el verificador) — vienen de capas que el predecesor no consultó.

## 2. Lecciones capitalizadas

| ID | Enunciado del corpus | Definida en | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|-------------|------------------------|-----------------|
| L-HF1 | Un candado con la *cobertura* equivocada pasa en verde mientras el artefacto miente | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | El verificador se escribe sobre la **propiedad** (el AC nombrado existe en el maestro; el dueño del ID es el publicado por el índice), no sobre la forma de la fila; y su salida publica la **población** que miró | AC-A2 · AC-B5 · Tarea 2 de FASE-V2 |
| L-R.3 | El gate anti-contradicción de R2.5 tiene cobertura medida del 12,5 % | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | Ningún `[OK]` del script puede aparecer sin su denominador: Q6 ya midió 3,8 % de cobertura de la regla y el informe debe decir «N planes en alcance / M exentos y por qué» | AC-B5 · §4 de `01-plan-maestro.md` |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | La pregunta Q4 del plan («qué declara no poder verificar») tiene AC propio: el **límite se escribe en tres sitios** — cabecera del script, salida del check y §4 de cada `00-` | AC-A4 · AC-C1 · check C6 del script |
| DA-HF3 | El verificador de citas se acota a «hacia delante + delta» con las tres opciones medidas, y reporta sin reescribir | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | El alcance se decide por **hacia delante** (corte por fecha del nombre del plan, Q6: 0 archivados entran) y el script **reporta, no reescribe**: sin `--fix` | AC-A1 · AC-B1 · restricción del prompt de FASE-V2 |
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | Los umbrales (≥3 descartes, ≥1 AC existente, ≥2 dueños) se fijan **medidos contra el único artefacto real** (Q7: 18 filas, 6 dueños, pasa) y no por deseo; si un umbral lo incumpliera un artefacto correcto, el umbral es el defecto | AC-A2 · Tarea 1 de FASE-V1 |
| L-B1 | Un candado que nace con la forma equivocada falla en rojo aunque el código esté bien | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | Prohibido parsear el `00-` con regex suelta sobre el texto: cada check consume la **tabla** (celdas por posición) y se prueba contra el archivo real del repo **y** contra fixtures en `tmp_path` | AC-B2 · Tarea 2 de FASE-V2 |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | NR7 (R2.8) **por check**, no por fase: C1…C8 con su reversión y su rojo, y el par de salidas en evidencia | AC-B3 · FASE-V2 |
| L-T2C.4 | Un fix que reactiva código muerto cambia comportamiento de producción y por tanto NO es «sin regresión» | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | La reversión de NR7 se hace sobre el **guard real del script** desactivando la función de ese check en el archivo versionado (con copia temporal), no sobre un duplicado escrito dentro del test | AC-B3 · `evidence/FASE-V2/` |
| L-T4B.5 | Un baseline pre tomado después de crear el archivo de tests contamina NR1 de forma invisible | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | El par pre/post de FASE-V2 se toma con `--ignore` explícito del archivo de tests nuevo y la resta verificada (R2.7) | FASE-V2 · `evidence/FASE-V2/baseline-pre-post.md` |
| L-VUP-1 | `test_function_default_flags` es orden-dependiente: la baseline «13 rojos» midió 14 | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | El par pre/post se declara con la **combinación exacta de archivos** y la lista de flaky conocidos; sin eso el verificador de R2.7 inventaría una causa para ruido | FASE-V2 · misma evidencia (abre el ítem (ii) de §Deuda del predecesor) |
| L-PF10 | «Sin hallazgos» y «no midió» no se distinguen: `critical_recall` BLOCKED «metric not found» sobre una lista vacía porque el fix había funcionado | `Archives/SR-PIPELINE-FIXES-2026-08-27/10-analisis-post-implementacion.md` | El verificador es él mismo un lector de artefactos y aplica R2.9: `AUSENTE` (no hay `00-`), `SIN-HALLAZGOS` (lo leyó y encontró el defecto) y `LECTOR-FALLIDO` (maestro sin tabla de ACs, ID no parseable) son salidas distintas y el script **nunca** imprime OK desde la tercera | AC-A2 · AC-B2 · check C1 y C7 del script |
| L-NC10 | Fosilización narrativa: templates con texto estático que ignoraban la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` | El día que exista el verificador, la frase «no tiene verificador mecánico» del template y del executor queda **falsa**: actualizarlas es alcance de este plan, no detalle | AC-C1 · Tarea 3 de FASE-V2 |
| L-V.4 | Un AC que falla se documenta con causa raíz + dueño, nunca se arregla en la fase | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | Si un check resulta inejecutable sobre un artefacto legítimo, se registra como límite con dueño y AC nuevo; **prohibido** rebajar el umbral para que dé verde | restricción de FASE-V2 · §Riesgos del maestro |
| L-V.2 | Las notas de fases upstream pueden ser inexactas: hay que re-leer los artefactos, no heredar conclusiones | `Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md` | FASE-V1 re-mide los cuatro hechos en los que se apoya el encargo (`.pre-commit-config.yaml` inerte · `Archives/` = 25, no 24 · cobertura 3,8 % · doble cableado de los verificadores) en vez de heredar el §Deuda del predecesor | Tarea 1 de FASE-V1 · AC-A3 |
| L-VUP-9 | Los prompts de probes deben usar los argumentos CLI reales, no suposiciones | `Archives/VALIDADOR-URL-PROPIA-2026-08-30/10-analisis-post-implementacion.md` | Todo comando citado en los prompts y en la salida del script se verifica contra `--help` real (hecho para `qmind retrieve`: `--nb/-q/--format`, Q3); el `--help` del script nuevo se lee **antes** de redactar el prompt de FASE-V3 | AC-B4 · prompts de fase |
| S-H17 | El pre-commit sigue publicando «Última fase: FASE-G» aunque FASE-H está registrada: el checker no sabe desempatar | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | El cableado no se declara con «el hook debería bloquear»: se **ejecuta** `scripts/git_hooks/pre-commit` contra un árbol defectuoso y se guarda su salida real | AC-B4 · Tarea 4 de FASE-V2 |
| L-I1 | Una fase de evidencia también produce conocimiento, y si no lo capitaliza lo pierde | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | Los hallazgos de Q5/Q6/Q7 que no caben en un AC de este plan se escriben en §3.b con dueño y pregunta, no se dejan en el aire | §3.b de este archivo · `dependencias-fases.md` |
| L-C2 | Un test rojo heredado entre fases puede contradecir un candado más nuevo: buscar el contract test antes de «arreglar» código | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` | Q10 midió que **0** contract tests afirman el número de checks de `run_all_validations.py`: la renumeración `[n/8]`→`[n/9]` y `[n/6]`→`[n/7]` es segura; donde sí hay quejas es en las referencias **normativas** del executor al `[6/6]` | AC-A3 · AC-B4 |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| R2.6 (D1/D5/S1-S3 · L-V.1) — «todo lector de artefactos del pipeline se prueba contra el baseline real» | El `baseline real` que esa regla protege es el **layout de `output/`** (ZIP-only, `_resolve_delivery_dir()`). Este verificador no lee artefactos del pipeline: lee `.md` del plan y el árbol de `plans/`. Su «régimen real» equivalente ya está cubierto por L-B1 (archivo real del repo en vez de fixture) y por S-H17 (hook ejecutado, no simulado), ambos con AC propio (AC-B2, AC-B4) |
| L-D2 | La evidencia se fosiliza si se captura antes de estabilizar los tests: el orden que lo previene ya lo fijan L-T4B.5 y L-VUP-1 en la misma fase; no duplicar un AC con segundo ID |
| L-VUP-13 | El estado de onboarding se confirma en el log de la corrida: este plan no ejecuta `v4complete` ni `onboard`, no hay corrida que interpretar |
| L-NC4 · D-NC2 | Tratan de no re-fosilizar templates del dossier comercial (`pain_ledger` → narrativa). Ningún AC de este plan toca `templates/` de documentos comerciales ni el pipeline de generación |
| L-A5 | Un test fosilizado puede codificar el invariante invertido: medido con Q10, este plan no reescribe ningún test existente ni invierte un invariante ya codificado — añade un archivo de tests nuevo |
| L-VUP-6 | La delegación falló en **cobertura de diseño** (conflictos entre subagentes): este plan es de un solo track de archivos (`scripts/`, `tests/`, hook, docs) y no se ejecuta delegado |

## 3.b Hallazgos de la capa fría **sin efecto aplicado**

No son descartes. La capa los encontró y este archivo no los capitaliza porque aplicarlos cambiaría el
perímetro de otro plan o exigiría una decisión del usuario, no de un registro.

- **Conteo fósil del corpus**: el executor (v2.22.0) y el propio template dicen «24 planes archivados».
  Medido hoy con Q6: **25** — el archivado de `TRIBUNAL-OFFLINE-2026-09-09` sumó uno y nadie actualizó la
  prosa. Es L-NC10 en miniatura. **Dueño**: el próximo cierre que edite el executor; **no** se corrige en
  este commit para no mezclar un arreglo de docs con el del verificador.
- **`§4` del predecesor declara «19 lecciones» y su tabla §2 tiene 18 filas** (medido en Q7 con el script
  ad-hoc). Un verificador podría exigir que los conteos declarados cuadren con la tabla; **no entra** al
  alcance de este plan (es un check nuevo, no el que se pidió) y su dueño natural es `FASE-P1` del
  `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`, que es el plan que lo publica.
- **`.pre-commit-config.yaml` con 13 hooks declarados y sin enforcement** (Q4): la decisión del
  2026-08-29 sigue pendiente. Si se activara la Opción 2, el check de este plan tendría que migrar o
  duplicarse allí. Queda declarado para que el `[7/7]` no se lea como «el pre-commit framework lo cubre».
- **Q5 devolvió scores ≤ 0,43** para la consulta sobre artefactos generados fosilizados: la búsqueda por
  esa formulación no encuentra `L-NC10` (que sí lo describe) porque el término del corpus es «fosilización
  narrativa». Señal para el corpus, no para este plan: las consultas del Paso 0 tendrían que registrar qué
  formulaciones **fallaron**, no solo las que acertaron.
- **Promoción a regla R2.11** («ningún plan se concibe sin `00-` verificado»): este plan entrega el
  verificador; **ascenderlo a regla global del executor con su texto de medición** es un acto distinto y
  no está encargado por el encargo. Dueño sugerido: el plan que cierre la §Deuda del predecesor.

## 4. Cobertura declarada de este documento

- **Qué deja como evidencia**: 10 consultas con comando literal y resultado medido (26 IDs de 5 dueños en
  la capa fría; 3 consultas al notebook con su `total:` y su score; 4 mediciones de población del repo);
  18 lecciones capitalizadas con dueño, ruta y el AC/tarea/restricción que modifican; 6 descartes con
  motivo; 5 hallazgos nombrados sin efecto aplicado.
- **Qué NO verifica este documento, ni lo verificará el script de este plan**: que la lección capitalizada
  sea **la correcta** para el plan, que el efecto nombrado en «qué cambia» sea real (y no un AC cosmético
  escrito para satisfacer el check), ni que §3 exprese un juicio genuino. Todo lo verificable es de forma y
  de trazabilidad: presencia, existencia del AC nombrado, correspondencia ID↔dueño con el índice,
  diversidad de dueños y declaración de límite. **Un `[OK]` del verificador va a significar «el artefacto
  tiene la forma exigida», nunca «capitalicé bien».**
- **Verificador mecánico sobre este archivo**: **existe desde FASE-V2 de este plan**
  (`scripts/validate_lesson_capitalization.py`), cableado como check `[7/7]` del hook versionado
  `scripts/git_hooks/pre-commit` —bloqueo demostrado en `evidence/FASE-V2/hook-bloquea.txt`, con
  `exit_code_del_hook=1`— y como `[9/9]` de `run_all_validations.py --quick`. Este Paso 0 pasó de
  «disciplinado, no verificado» a **verificado en su forma**; el límite de pertinencia de arriba
  sigue vigente y C6 lo exige nombrado aquí (L-R.4, L-NC10).

### 4.1 Actualizaciones al cierre de FASE-V2 y FASE-V3 (2026-09-12)

- **Filas de §2 que se cumplieron como se prometieron**: L-HF1, L-R.3, L-R.4, DA-HF3, L-D3, L-B1,
  L-VUP-5, L-T2C.4, L-T4B.5, L-VUP-1, L-PF10, L-VUP-9, S-H17, L-V.2, L-I1 y L-V.4 (el umbral ≥3 de
  C5 no se rebajó cuando un fixture lo incumplía: se corrigió el fixture).
- **La fila que NO se aplicó como estaba redactada, y su costo medido**: **L-C2** ordenaba «buscar el
  contract test antes de tocar». Se buscó, pero sobre el artefacto equivocado: Q10 preguntó quién
  menciona `run_all_validations` dentro de `tests/` y midió **0**, mientras el riesgo de la fase era la
  **numeración del hook**. Ahí sí había un contract test —`test_registrado_como_check_5_en_el_hook`—
  rojo y **sin declarar** desde `4a066e1`, que cambió `[5/5]` a `[5/6]` sin seguirlo. Lo encontró esta
  fase al correr el par pre/post, se arregló en la misma fase y su forma corregida quedó como **L-V2.3**
  en `10-analisis-post-implementacion.md` §2. Se registra aquí, y no solo en el análisis, porque el
  punto del Paso 0 es que el error de búsqueda conste en el lugar donde se prometió acertar.
- **Dos filas cuyo efecto cambió durante la implementación**: L-B1 obligó a ampliar `AC_TOKEN_RE` a las
  dos formas vivas del repo (`AC-F1` **y** `AC8`) y obligó también a conservar los backticks de las
  celdas para que C3 pueda distinguir un comando de una intención; L-NC10 es la razón de que C6 exija
  nombrar al verificador, que es lo que hace que la línea de arriba caducara y se actualizara en vez
  de quedar mentida.
- **Filas que trabajaron en el cierre de FASE-V3**: **L-NC10** es la razón de que el template
  (`v1.1.0`) y el executor (`v2.24.0`) dejen de enseñar «no existe verificador» el mismo día que
  existe; **L-V.2** obligó a releer las menciones al `[6/6]` antes de tocarlas y produjo el reparto
  5 normativas / 4 históricas (comprobable con `grep -n "\[6/6\]" .agents/workflows/phased_project_executor.md`:
  solo quedan las cuatro de medición); **DA-V5** impidió reasignar la deuda (i) del predecesor por
  inercia — quedó cerrada en su propio checklist con fecha, commit y cobertura medida.
- **Lo que este Paso 0 prometió y sigue sin estar cubierto**, declarado para que no se lea como
  cerrado: que los prompts de fase copien las filas pertinentes de §2 (el verificador no abre los
  prompts), y el juicio de pertinencia. Ambos límites viven en §4 de este archivo y en la salida del
  script.
- **Orden del Paso 0**: este archivo se escribió **antes** de `01-plan-maestro.md`. La columna «qué cambia»
  de §2 nombra ACs aún inexistentes; el contrato del verificador (AC-B2, check C4) convierte esa promesa en
  bloqueo: si el maestro no los crea, el artefacto no pasa.
