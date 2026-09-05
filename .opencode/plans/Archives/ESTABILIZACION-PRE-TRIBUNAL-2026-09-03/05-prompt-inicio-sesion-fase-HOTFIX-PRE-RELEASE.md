# FASE-HOTFIX-PRE-RELEASE — Cerrar la distancia entre «cadena causal curada» y «clase de defecto erradicada»

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-HOTFIX-PRE-RELEASE (sesión extra, no es la fase 11)
**Objetivo**: cerrar los **4 ACs ⚠️** y el **único rojo introducido por el plan (S-V1)** que FASE-VERIFY
certificó con sonda propia; rematar los **dos puntos que VERIFY asignó a un hotfix** y no tenían fase
(**S-C3** mitad textual, **S-I3**); y llevar al executor las **4 reglas de proceso** que VERIFY propuso y que
hoy **no están en el archivo**, convirtiendo en **verificador mecánico** la que es mecánica (citas de línea).
Después de esta sesión, FASE-RELEASE puede certificar **12/12** o publicar la deuda restante con dueño y causa.
**Dependencias**: FASE-VERIFY ✅ (2026-09-04, commits `e8969c5` + `a653305`)
**Duración estimada**: 90-120 minutos
**Complejidad técnica**: **BAJA-MEDIA** — cinco cambios de **serialización / prosa de artefacto** y dos de
**plantilla + verificador**; **no** se toca ninguna lógica de decisión, ningún umbral y ningún criterio de
presencia.
**Modo de ejecución**: **DIRECTO** (es código de producción con contrato transversal: 3 de los 4 puntos
tocan artefactos que leen el humano y el gate a la vez; el criterio vive en `10-analisis` y no cabe en un
subagente).
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: **≤45 iteraciones** (ampliado de ≤35 al sumar H6, H7 y H9; la alternativa era partir en dos la
sesión, y el criterio para no hacerlo fue que cada partida vuelve a medir el baseline NR5 y vuelve a leer los
mismos artefactos) · **Comandos largos: 0**
**Salida**: código + tests + `evidence/FASE-HOTFIX-PRE-RELEASE/`; `scripts/validate_plan_citations.py` con su
test; las 4 reglas escritas en `.agents/workflows/phased_project_executor.md` (v2.19.0); y update de
`10-analisis` §5 y §6, `06-checklist`, `09` §C.1/§D y `dependencias-fases.md`.

---

## Paso 0 (obligatorio antes de tocar nada)

1. Memoria del proyecto: `MEMORY.md` → leer
   `ciclo-de-capitalizacion-de-lecciones-qmind-memory`, `revalidar-citas-de-c-digo-no-revalida-premisas`,
   `conteos-tests-documentados-metodo-def_test`, `extractores-de-m-trica-que-colapsan-vac-o-con-ausente`,
   `unificar-conteos-derivados-en-dtos-multi-consumer`, `grep-de-criterio-de-aceptacion-tambien-cuenta-prosa`.
2. QMind `iah-cli-lecciones` (`01a04d98-b7bd-778c-8441-26fdc7e35f45`) → `retrieve` con:
   «dos representaciones del mismo hecho sin oráculo único», «test fosilizado codifica el invariante
   invertido», «un gate saltado no es un gate pasado».
3. Leer `10-analisis-post-implementacion.md` §2.1 (matriz AC certificada), §5 (S-V1…S-V10), §6 (DA-V1…DA-V6),
   §8 (L-V1…L-V4) y §9.1.
4. **Regla transversal del plan** (cabecera de `dependencias-fases.md`): las citas de línea de ESTE prompt
   fueron verificadas el 2026-09-04 y **caducan con la primera edición**. **Citar símbolos; confirmar la
   región con `grep`/`Read` antes de editar.** Si difieren, corregir el prompt y avisar.

---

## Contexto y regla de oro

VERIFY certificó **8 ✅ / 4 ⚠️ / 0 ❌** en ACs y **10 ✅ / 1 ⚠️ / 1 ❌** en NRs, y su veredicto (§4.6) fue:
*la cadena causal está curada, pero el plan no erradicó la clase de defecto: la movió*. Los cuatro ⚠️ son la
prueba de esa frase, y comparten **una** forma: **el sistema ya decidió, y el artefacto que lee el humano no
lo refleja**.

> **Regla de oro de esta sesión (L-V1)**: un validador que no lee el artefacto que el sistema produce
> certifica un mundo que producción no habita. **Ninguno de estos cuatro puntos se cierra con un string en
> el código**: se cierra leyendo el JSON que el writer deja en disco.

**A cambio, esta sesión sí escribe código de producción** (a diferencia de VERIFY). Por eso rige **DA-V5**:
cada tarea se limita a lo que está escrito aquí. Si al medir resulta que un punto exige cambiar una decisión
de negocio (umbral, criterio de presencia, severidad de un gate), **se detiene, abre seguimiento y pasa a
RELEASE** — no se amplía el alcance sobre la marcha.

---

## Tareas

### H1 — S-V1: migrar el test rojo al contrato que FASE-F fijó

`tests/delivery/test_delivery_contract.py::TestP05G9Gate::test_g9_gate_skipped_when_no_matrix`
(rojo medido: `1 failed / 170 passed`, y reprodujo en vivo esta sesión).

- El test aserta `g9.get("skipped") is True` **y** `g9["passed"] is True` con el mensaje «should
  default-pass when skipped». El contrato vigente es `_not_evaluated_g9()` en
  `modules/quality_gates/delivery_quality_report.py`: `{passed: False, state: "NOT_EVALUATED", ...}`.
- ⚠️ **Aplicar L-A5 antes de tocar valores**: la segunda aserción no está desactualizada, **codifica
  invertido el invariante que FASE-F vino a eliminar** (el verde vacuo de un gate no ejecutado). Se invierte
  la aserción y se **renombra** el test a lo que ahora afirma
  (propuesto: `test_g9_gate_not_evaluated_when_no_matrix`), incluyendo `state`, `passed is False`, que **no
  figure** en `summary["passed"]` y que sí figure en `summary["not_evaluated"]`.
- **No** se toca `_not_evaluated_g9()`: es el default único y canónico (AC11).

### H2 — AC7 / S-I2: que el `gate_report` diga qué gates bloquean

Hoy el artefacto serializa 7 claves por gate (`gate_name, passed, status, message, value, suggestion,
details`) y **cero** de severidad: la palabra `severity` no aparece en `gate_report_*.json` de la corrida.
Las 11 blocking + 2 advisory viven en la config y deciden el veredicto, pero el humano no lo ve por gate.

- Donde: la proyección `gate_results = [{...} for r in gate_results]` construida a mano en `main.py`
  (zona donde se escribe `gate_report_path`, `_make_evidence_path(..., "gate_report")`).
- **Cómo, sin recrear el defecto (DA-V1 / L-F2)**: serializar **desde el predicado canónico**
  `gate_blocks_publication()` (`modules/quality_gates/publication_gates.py`), no desde una tercera lista de
  nombres. Una clave literal copiada a mano en el writer es exactamente la «segunda representación del mismo
  hecho» que el plan persigue.
- El test que lo fija debe **leer el JSON en disco**, no el objeto en memoria (L-F3).

### H3 — AC6 / S-V3: publicar `coverage_ratio` en la matriz

`to_dict()` de `modules/asset_generation/proposal_asset_alignment.py` no serializa `coverage_ratio`, así que
el AC6 no es certificable sobre artefacto y el valor vuelve a `1.0` en la corrida.

- Serializar el ratio **ya calculado** por la partición canónica `classify_promised_services()`; **no**
  recalcularlo en el writer (eso produciría dos oráculos del mismo número, el defecto A4 en su forma
  vertical).
- Cuidado con `vacío ≠ ausente` (memoria homónima): un ratio con denominador 0 debe seguir distinguiéndose
  de «no se evaluó». Verificar que el valor serializado **discrimina** en el caso negativo que ya está
  candado (cobertura 0.5 / 3 de 4), no solo en el feliz.

### H4 — AC10 / S-I7: coherencia mensaje ↔ `details`

El mensaje narrado por `verify_proposal_asset_alignment` y sus `details` estructurados pueden no cuadrar
(AC10 quedó ⚠️ por eso). **Primero medir, luego decidir**: reproducir sobre los artefactos de
`evidence/FASE-I/corrida/` el par (mensaje, `details`) y escribir el delta.
- Si es el **mismo writer** que H2/H3 → arreglar aquí, con test que aserte la correspondencia.
- Si exige cambiar el **criterio** de qué se narra → **no** hacerlo: abrir seguimiento con el delta medido y
  dejarlo para el tribunal (DA-V5).

### H5 — AC8-b / S-V4+S-V5: reformular el criterio, no el sistema

AC8-b no es ejercitable con una corrida sana: **el defecto es de la redacción del AC** (S-V5 lo dice).
Reescribirlo en `01-plan-maestro.md` / `06-checklist` como criterio **de test** (ya está candado por
`test_docstrings_no_prometen_el_regimen_antiguo` y sus vecinos), con la nota de que la evidencia admisible
es el verde del candado, no una corrida. **Sin cambiar el candado.**

### H6 — S-C3 (mitad **textual**): el mensaje que el cliente lee sigue narrando el catálogo estático

**Medido esta sesión (2026-09-04), no heredado del seguimiento**: el sitio es **uno solo** en todo el repo
(`grep -rn "len(PROPOSAL_SERVICE_TO_ASSET)\|len(ALL_PROMISED_SERVICES)" modules/ main.py` → 1 hit), en la
narración de `promised_assets_exist` dentro de `modules/commercial_documents/coherence_validator.py`
(símbolo: el `message=f"Todos los assets prometidos están implementados ({len(PROPOSAL_SERVICE_TO_ASSET)}
servicios verificados via PROPOSAL_SERVICE_TO_ASSET){prod_note}"`).

- Lo que imprime en la corrida real es **«7 servicios verificados»**, y **7** es `len()` del **catálogo
  estático**, no el número de servicios verificados en esa corrida. La matriz de la misma corrida declara
  `summary.promised = 4`. No es un «7» fosilizado que alguien olvidó editar: es el defecto **B2**
  (registro estático vs runtime) reaparecido en la **prosa del artefacto**, en la tercera superficie.
- El string llega a **3 artefactos** de la corrida (`asset_generation_report.json`,
  `coherence_validation.json`, `coherence_validation_post_gen.json`) desde ese único sitio.
- **Por qué el candado de AC2 no lo vio**: `test_narrativa_no_hardcodea_conteo_de_servicios` prohíbe la
  **forma numeral** sobre la tupla `MODULOS_NARRATIVA` (7 módulos) y
  **`coherence_validator.py` no está en ella**. Es L-V2 con otro cuerpo: el candado de forma no cubre la
  superficie que llega al cliente.
- **Qué hacer**: narrar lo que se verificó en runtime (la partición de `classify_promised_services()` / el
  recuento de la matriz), **no** el tamaño del catálogo; y extender la cobertura del candado para que este
  archivo no pueda volver a escribir un numeral de catálogo.
- ⚠️ **Medir antes de extender**: `pytest tests/common/test_service_identity_registry.py -q` **con**
  `coherence_validator.py` añadido a la tupla. Si el archivo tiene otros numerales legítimos, **no** relajar
  el candado ni excluirlos con un `# noqa`: acotar el candado a la forma «N servicios/assets verificados», o
  escribir un test específico que fije que **ese** mensaje no contiene numeral. Decidir con la salida
  delante, y registrar la decisión.
- **Fuera de alcance (lo estructura)**: `score=1.0` hardcode, el check que solo corre pre-gen y la unión del
  denominador. Eso es **P12 ❌**, dueño tribunal. Esta tarea cambia **solo el string y su candado**.
- **Barreda obligatoria antes de cerrar (L-H6)**: re-correr el `grep` de arriba y del literal
  «servicios verificados» sobre `modules/` — si aparece un segundo sitio, se arregla en la misma pasada, no
  se deja anotado.

### H7 — S-I3: una ruta, dos claves (`asset_path` vs `path`)

El mismo hecho —la ruta local de un asset— se serializa como `asset_path` en `proposal_asset_matrix.json` y
como `path` en `v4_complete_report.assets_generated[]`. **Coste ya medido en el plan**: el script de
comparación de FASE-I leyó `asset_path` en el report, obtuvo `null` en **ambas** corridas y habría afirmado
que A6 seguía roto.

- **No** es unificar las claves de los dos artefactos a machetazo: son DTOs distintos con consumidores
  distintos, y romper una clave de artefacto es romper al lector externo que la usa.
- Lo que se pide es **fijar por contract test cuál es la clave canónica de cada artefacto** y documentarlo en
  el DTO, de modo que la próxima lectura no sea una conjetura. Modelo a seguir: la memoria
  `unificar-conteos-derivados-en-dtos-multi-consumer` (helper canónico + contract test).
- Anclas verificadas (2 sitios de serialización de `asset_path` + 1 de consumo): `asset_path` se emite dos
  veces en `modules/asset_generation/proposal_asset_alignment.py` (dos proyecciones de matriz — confirmar con
  `grep -n '"asset_path"'` y leer si son `ProposalAssetMatrix.to_dict` y `AssetAlignmentMatrix.to_dict`) y se
  consume en `modules/quality_gates/delivery_quality_report.py`. La proyección `assets_generated[]` con clave
  `path` se arma **en otro archivo**: localizarla con `grep -rn '"assets_generated"' --include=*.py` y no
  asumirla.
- Si al medir resulta que unificar exige tocar el contrato de entrega del ZIP → **diferir con causa**
  (DA-V5) y dejar solo el contract test + la documentación de la clave canónica.

### H8 — Executor v2.19.0: las 4 reglas que VERIFY propuso y el archivo no tiene

Medido el 2026-09-04: `.agents/workflows/phased_project_executor.md` (v2.18.0) no contiene **ninguna** de
estas cuatro reglas (0 coincidencias de «recalibr», «números de línea», «hasta el commit de código»,
«delta»). Su propia cabecera sigue prometiendo «Máximo 60 iteraciones por fase» mientras los presupuestos
reales del plan eran ≤35-50 y **las nueve fases medibles los excedieron** (2,4× a 8,6×). Escribir:

1. **Presupuesto (S22 / DA-V6)**: instrumento canónico `evidence/FASE-D/measure_iterations.py` + corte
   fijo **«hasta el commit de código»**; recalibrar ×3 o **retirar** la métrica. Si una fase no puede correr
   el instrumento, el auto-reporte se publica **en la unidad usada** (`tool_use`) y se declara.
2. **Prohibir números de línea** en criterios de aceptación y prompts de fase: citar **símbolos** (L-A6 +
   L-V4 + L-H4; tasa medida **14/16** citas ya desfasadas).
3. **No-regresión de conteos como delta** (S26 / DA-V2): `passed = baseline + tests nuevos`, `skipped
   idéntico`, 0 fallos ajenos, y **par pre/post** obligatorio. Un número absoluto como invariante hace que
   cumplir el plan cuente como violación.
4. **Regla de certificación (L-V1 / DA-V3)**: *un AC no legible en el artefacto que el sistema produce se
   marca ⚠️, no ✅*; un ✅ que solo respalda un string en el código **no existe**.

Actualizar la versión del archivo a **v2.19.0** y su changelog interno. **No** tocar AGENTS.md/CONTRIBUTING
por esta vía salvo que `validate_document_integration.py` lo exija (lo dice el gate, no yo).

### H9 — Materializar la regla 2 como **verificador**, no como prosa

Escribir una norma en el executor y no medirla es el mecanismo que acabó en **S15**: la regla de «revalidar
citas» se escribió, se leyó… y al certificar estaban **14 de 16** desfasadas. La versión mecánica es barata y
su población es contada, no supuesta:

- **Población medida hoy**: `grep -rEoh "[A-Za-z0-9_/]+\.py:[0-9]+" .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/*.md | wc -l` → **382** citas en los 17 archivos del plan. La mayoría están en documentos
  **históricos** que registran lo que ocurrió: borrarlas o reescribirlas sería falsificar el registro.
- **Este prompt cumple su propia regla**: 0 coincidencias de ese patrón. Sus anclas son símbolos
  (`_not_evaluated_g9()`, `gate_blocks_publication()`, `classify_promised_services()`, `to_dict()`),
  verificadas el 2026-09-04.

**Qué construir**: `scripts/validate_plan_citations.py`, registrado como **check 8** de
`run_all_validations.py --quick` siguiendo el patrón del bloque «OpenCode References» (el que invoca
`scripts/validate_opencode_refs.py` y cubre los casos «script ausente / pasó / falló»).

**Alcance — medir las tres opciones antes de elegir y dejar la medición en `evidence/`**:

1. **Hacia delante**: solo directorios de plan creados después del verificador, más los portadores que las
   sesiones futuras leen (`05-prompt-*`, `01-plan-maestro.md`).
2. **Delta** (la regla 3 de H8 aplicada a sí misma): baseline con el conteo actual y **fallar solo si sube**.
   Coherente con DA-V2, y no reescribe historia.
3. **Por sección**: aplicar solo dentro de secciones de criterios de aceptación y de tareas de fase.

Recomendación escrita aquí: **(1) + (2) combinadas** — los planes nuevos no introducen citas numéricas, y el
inventario de los existentes no crece. **Prohibido auto-arreglar**: el verificador **reporta, no reescribe
números**. `validate_opencode_refs.py` puede reparar porque un basename es único; una línea no tiene «la
verdad» a la que converger, y reescribirla produciría una cita que apunta a un sitio que ya no contiene lo
citado — el defecto de S15 con apariencia de arreglado.

**Requisito no negociable**: el verificador lleva **test propio** (fixture con una cita mala y una buena),
porque un validador que nunca se dispara es una instancia más de la clase que este plan certificó. Cerrar con
`run_all_validations.py --quick` → **8/8**.

---

## Verificación obligatoria (sin violar «la corrida E2E es única»)

El plan fijó **una** corrida `v4complete` (FASE-I) y esa disciplina no se rompe para celebrar un test. En su
lugar, **ejercitar el writer real sobre insumos reales**:

- Test que construye el `gate_report` / la `proposal_asset_matrix` llamando el **mismo** camino de producción
  (`_make_evidence_path` + `json.dump`; `to_dict()`), con una copia de los artefactos de
  `evidence/FASE-I/corrida/` como entrada → **sin red, sin LLM, sin `v4complete`** → y aserta las claves
  nuevas **en el JSON que quedó en disco**.
- Para H6, la misma disciplina pero sobre el texto: el mensaje de `promised_assets_exist` se ejerce con el
  fixture de la corrida y se lee **en `coherence_validation.json`**, afirmando que el número narrado es el de
  la partición verificada y no `len(PROPOSAL_SERVICE_TO_ASSET)`. Un test que aserte el objeto en memoria no
  prueba que el cliente lea otra cosa (L-V1, y es literalmente el defecto de AC7/S-V3 que VERIFY dejó ⚠️).
- Si tras eso se quiere evidencia de una corrida completa, es **decisión del usuario** correr
  `v4complete` otra vez: pedirla explícitamente, no tomarla.

Suite y validaciones (registrar salida en `evidence/FASE-HOTFIX-PRE-RELEASE/`):

```bash
python -m pytest tests/delivery/test_delivery_contract.py -q                 # H1: 0 failed
python -m pytest tests/quality_gates tests/asset_generation -q               # baseline delta (regla 3 de H8)
python -m pytest tests/common tests/commercial_documents/test_pain_map_bijection.py \
        tests/asset_generation/test_fase_c_propuesta_dinamica.py -q          # candados A/B/C sin regresión
python -m pytest tests/ -k "plan_citations" -q                               # H9: el verificador se dispara
python scripts/run_all_validations.py --quick                                 # 8/8 (antes 7/7)
```

**Baseline NR5 (ya reformulado como delta)**: `quality_gates + asset_generation` estaba en **944 passed /
2 skipped / 0 failed**. Lo admisible es `944 + (tests nuevos de esta sesión)`, `skipped` idéntico, 0 fallos
ajenos, con `faseHotfix_baseline_pre.txt` / `_post.txt`.

---

## Post-Ejecución (OBLIGATORIO)

1. **Commit de código** con las rutas exactas (el árbol puede tener trabajo de otra sesión: `git status`
   fresco, `git add` de rutas explícitas, **nunca** `-A`, **nunca** `git stash`).
2. `python scripts/log_phase_completion.py --fase FASE-HOTFIX-PRE-RELEASE --desc "..." --check-manual-docs`.
3. `evidence/FASE-HOTFIX-PRE-RELEASE/`: sondas re-ejecutables + el JSON de salida **antes/después** de H2, H3
   y H6 (no un log de consola: **el artefacto**) + el conteo de citas de H9 por alcance, medido con el comando
   que dejará escrito en el propio verificador.
4. `10-analisis-post-implementacion.md`: **S-V1, S-V3, S-I2, S-I7, S-V4/S-V5** a su estado real con delta
   medido, y las filas de **S-C3** y **S-I3** reescritas para que digan qué mitad cerró esta sesión y qué
   mitad sigue viva con dueño (S-C3 estructura = P12 = tribunal). Si algo no cierra, sigue ⚠️ con causa.
   **≥1 lección nueva** con pertinencia INCLUIR/**EXCLUIR** aplicada (no 100 % INCLUIR: ese default ya fue
   corregido en VERIFY).
5. `06-checklist-implementacion.md`: fila de la sesión + los 4 ACs a su estado certificado sobre artefacto.
6. `09-documentacion-post-proyecto.md` §C.1 (los valores que RELEASE va a copiar) y §D (métricas).
7. `dependencias-fases.md`: la fila de RELEASE actualizada con lo que hereda **ahora**.
8. **No** commitear ni pushear nada fuera de lo anterior; **push solo si el usuario lo pide**.

## Criterios de completitud (CHECKLIST)

- [ ] `171 contracts / 0 failed` (rojo de S-V1 cerrado, no xfail ni skip).
- [ ] `gate_report_*.json` generado por el writer real contiene la severidad **derivada del predicado
      canónico** y el test lo lee **en disco**.
- [ ] `proposal_asset_matrix.json` expone `coverage_ratio` con el valor de la partición, y **discrimina** en
      el caso negativo.
- [ ] AC10 cerrado con delta medido, o con seguimiento nuevo que explique por qué se difiere.
- [ ] AC8-b reescrito como criterio de test, sin tocar el candado.
- [ ] El mensaje de `promised_assets_exist` narra el conteo **verificado en runtime**, el candado de forma lo
      cubre (o existe el test específico que lo impide), y la barreda de `len(PROPOSAL_SERVICE_TO_ASSET)` sigue
      dando **1** sitio.
- [ ] La clave canónica de la ruta de un asset está **fijada por contract test por artefacto** y documentada
      en el DTO (H7). Nadie vuelve a conjetuar entre `asset_path` y `path`.
- [ ] `phased_project_executor.md` en **v2.19.0** con las 4 reglas (verificable con `grep`, no por memoria).
- [ ] `scripts/validate_plan_citations.py` existe, es el **check 8** de `--quick`, tiene test propio que **se
      dispara** sobre un fixture malo, y su alcance está justificado con las tres mediciones hechas (no
      elegidas de oído).
- [ ] Validaciones **8/8** y suites tocadas en verde con la **regla de delta**.
- [ ] Ningún umbral, criterio de presencia o lista de severidades alterado (contrafactual de 0 flips de
      `ready` sobre la corrida de FASE-I: **re-producirlo**, no asumirlo).

## Restricciones

> ⚠️ **Colisión de nombres**: «H1…H9» son **tareas de esta sesión**. «H7», «H8», «H10» sin prefijo son
> **hipótesis del dossier** (ROADMAP §13 / auditoría SalenteReal) y se citan así, con la fuente: debajo se
> escribe «hipótesis H7 del dossier» para que el lector no tenga que adivinar.

- **NO** tocar el umbral de coherencia (0.8), `coherence_verdict_passes()`, `is_present_in_production`,
  `PAIN_SOLUTION_MAP`, `SERVICE_IDENTITIES` ni `BLOCKING_GATE_NAMES`/`ADVISORY_GATE_NAMES`. Ni re-introducir
  `publication_state` (hipótesis **H8 del dossier**, cerrada por FASE-F) ni debilitar el guard de presencia
  (hipótesis **H7 del dossier**, intacto por contrato desde FASE-SR-E).
- **NO** tocar la estructura de **P12** en H6: ni el `score=1.0` hardcode de `promised_assets_exist`, ni la
  unión del denominador, ni hacer que el check corra post-gen. Esas tres son **dueño tribunal** y cada una
  cambia una decisión, no una serialización.
- **NO** reescribir ni borrar citas de línea **históricas** de los documentos del plan (las 382): son el
  registro de lo que se midió. H9 las deja estar; lo que impide es que **crezcan** y que los planes nuevos
  las introduzcan.
- **NO** re-ejecutar `v4complete` sin autorización explícita del usuario.
- **NO** ampliar alcance: si un punto resulta ser de lógica, se difiere con causa (DA-V5).
- **NO** delegar el cierre ni fiarse de informes de subagente sin `git status` (L-H1/L-H7).
- Baseline `output/FASE-D_salentoreal_post_guard/` es **solo lectura**.
- Todo ⚠️/❌ que subsista abre seguimiento con causa y próximo paso.

---

## Prompt de Ejecución

```
Actúa como ejecutor de la sesión FASE-HOTFIX-PRE-RELEASE del plan
ESTABILIZACION-PRE-TRIBUNAL-2026-09-03. Lee primero, íntegro:
/.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/05-prompt-inicio-sesion-fase-HOTFIX-PRE-RELEASE.md

OBJETIVO: cerrar los 4 ACs ⚠️ que FASE-VERIFY certificó sobre artefactos y el único rojo que el plan
introdujo (S-V1); rematar los dos puntos que VERIFY asignó a un hotfix (S-C3 textual, S-I3); y escribir en el
executor las 4 reglas de proceso que propuso VERIFY, convirtiendo en verificador mecánico la que es mecánica.
Todo es serialización, prosa de artefacto o plantilla: ninguna decisión de negocio cambia.

PASO 0 ANTES DE CODIGO: memoria del proyecto + retrieve en QMind iah-cli-lecciones + 10-analisis §2.1/§5/§6/§8/§9.1.

TAREAS:
H1 S-V1  tests/delivery/test_delivery_contract.py::TestP05G9Gate — migrar al contrato _not_evaluated_g9()
         (state NOT_EVALUATED, passed False, visible en summary["not_evaluated"]) y renombrar el test.
         Leer que invariante codifica antes de tocar valores (L-A5): la 2a aserción defiende el defecto.
H2 AC7   serializar severidad/bloqueo en gate_report desde el predicado canónico gate_blocks_publication(),
         no desde una tercera lista (DA-V1). Test leyendo el JSON en disco (L-F3).
H3 AC6   publicar coverage_ratio en to_dict() de proposal_asset_alignment con el valor ya calculado por
         classify_promised_services(); vacío != ausente; que discrimine en el caso negativo.
H4 AC10  medir primero el par mensaje<->details sobre evidence/FASE-I/corrida/; si exige cambiar criterio,
         difiere con causa (DA-V5).
H5 AC8-b reescribir el AC como criterio de test (S-V4/S-V5), sin tocar el candado.
H6 S-C3  el message de promised_assets_exist en coherence_validator narra len(PROPOSAL_SERVICE_TO_ASSET)
         («7 servicios verificados» con matriz de 4): narrar la partición verificada. El candado de forma
         test_narrativa_no_hardcodea_conteo_de_servicios no lo ve porque coherence_validator.py no esta en
         MODULOS_NARRATIVA: medir, extender sin relajar, y barrear que siga habiendo un solo sitio.
         NO tocar score=1.0 ni la union del denominador (eso es P12, dueno tribunal).
H7 S-I3  asset_path vs path para el mismo hecho: fijar la clave canonica POR ARTEFACTO con contract test y
         documentarlo en el DTO (no romper claves de entrega).
H8       phased_project_executor.md -> v2.19.0 con: instrumento+corte de iteraciones («hasta el commit de
         codigo»), prohibir numeros de linea en ACs/prompts, no-regresion de conteos como delta con par
         pre/post, y «AC no legible en el artefacto = WARN».
H9       scripts/validate_plan_citations.py como check 8 de run_all_validations --quick (382 citas existentes
         en los 17 md del plan; 14/16 desfasadas al certificar). Medir los 3 alcances y elegir hacia-delante
         + delta. REPORTA, no reescribe numeros. Con test propio que se dispare.

REGLA DE ORO (L-V1): nada se cierra con un string en el codigo; se cierra leyendo el artefacto que el writer
real deja en disco, usando una copia de los artefactos de FASE-I como entrada. NO correr v4complete.

RESTRICCIONES: no tocar umbral 0.8, coherence_verdict_passes, is_present_in_production, PAIN_SOLUTION_MAP,
SERVICE_IDENTITIES, las dos listas de severidad, ni la estructura de P12; no reescribir citas de linea
historicas de los docs del plan; no re-introducir publication_state (hipotesis H8 del dossier). No ampliar
alcance: si un punto es de logica, se difiere con causa. Push solo si lo pido.

VALIDACION: pytest de delivery/quality_gates/asset_generation/common + el test propio de H9, y
run_all_validations.py --quick (8/8, antes 7/7), con baseline como delta (944/2 pre) y par pre/post en
evidence/FASE-HOTFIX-PRE-RELEASE/. Cierre documental: 10-analisis §5/§6 + 06 + 09 §C.1/§D + dependencias +
REGISTRY via log_phase_completion.py. Presupuesto <=45 iteraciones; si el instrumento no corre en sandbox,
auto-reportar en la unidad usada y declararlo (precedente: VERIFY declaro ~65 tras publicar ~36).
```
