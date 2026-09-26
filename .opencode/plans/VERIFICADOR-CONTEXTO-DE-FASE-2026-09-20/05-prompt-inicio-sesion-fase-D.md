# FASE-D — Generador de briefing pack por fase y delta de carga de lectura

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-D
**Objetivo**: escribir `scripts/build_phase_briefing.py`, que compone por cada fase un único
archivo con las secciones que su prompt declara leer, y medir el delta de carga de lectura que eso
produce. Cubre AC19–AC23.
**Dependencias**: FASE-A ✅ (estados y `coverage_basis`), FASE-B ✅ (costura, para el candidato de
pertinencia que el pack puede anotar), FASE-C (el triaje cuyo output el pack consume como sección
propia: de ahí se hereda su **parte mecánica medida**; su **aceptabilidad** es `NO-EJERCITADO` mientras
D7 esté inactiva y, por tanto, **no** activa la deuda D6 — contrato E4).
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración (R3).
**Skill**: `phased_project_executor`.

## Contexto

Medido al diagnosticar este repo: una sesión de fase de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`
declara leer **ocho** documentos y lo hace en ocho lecturas separadas contra un presupuesto de 60
`tool_use`. Siete de ellos entran en la suma de A7 y el octavo es un archivo de `evidence/` que el pie
de esa tabla excluye. **La suma está re-medida el 2026-09-20: 263.973 bytes ≈ 65.993 tokens estimados
(divisor 4)**; al concebir el plan daba 254.010 y creció +9.963 con los cierres de FASE-G y FASE-B del
propio plan medido (maestro §1, A7 y A6). La
mitad de ese volumen es el workflow canónico, y una quinta parte de ese workflow son plantillas de
documentación que solo consumen el cierre y VERIFY.

Esta fase **no rebaná el workflow**: eso es deuda D3, exige tocar `.agents/` (AC17) y reescribir las
nueve citas al workflow canónico que hay en el plan en vuelo. Lo que hace es lo otro: construir el
artefacto derivado que unifica las lecturas declaradas, sin borrar ninguna fuente. Es el mismo
patrón que `build_lesson_index.py`: **se lee la fuente dinámica, se emite un generado, nunca se
edita a mano**.

### Estado de fases anteriores (confirmar en disco al abrir)

| Fase | Estado esperado | Qué aporta esta fase |
|---|---|---|
| FASE-A | ✅ | `status` de tres estados y convención `coverage_basis` |
| FASE-B | ✅ o con AC9 en ⚠️ | La costura; y el hecho de que **no** hay comparación de proveedores en este plan |
| FASE-C | ✅ | Los candidatos de pertinencia, que el pack exhibe como sección propia |

### Base técnica disponible

- Fuente de lo declarado: cada `05-prompt-inicio-sesion-fase-*.md` tiene su lista de lectura en el
  encabezado de tareas y en el bloque «Prompt de ejecución». El generador parsea **esa** lista; no
  se le pasa una configuración a mano.
- Plantilla de estructura de prompt: `.agents/workflows/templates/prompt-fase-template.md`
  (lectura: el generador se ajusta a sus secciones, no las modifica).
- Precedente de artefacto generado con verificador de frescura: `scripts/build_lesson_index.py`
  (`--check`, cortado por `[6/7]` del hook). Modelo de `--check` a emular.
- Salida: el subdirectorio `briefing/` **de este plan** (lo crea esta fase; al concebir el plan aún no
  existe). **Precisión corregida el 2026-09-20**: lo que hace fallar a `validate_opencode_refs.py` no es
  la forma absoluta de la ruta sino **que el destino no exista al escanear** — su regex extrae la cola
  `.opencode/...` incluso dentro de una ruta absoluta, y una referencia relativa a un directorio que
  aún no está creado rompe igual. La regla práctica sigue siendo la de la concepción: **no escribir la
  ruta del pack como referencia `.opencode/...` hasta que FASE-D lo cree**, y pasar `--plan` en el
  arranque cuando exista. **No** va a
  `.agents/workflows/`: los contadores de skills usan `glob("*.md")` no recursivo y un `.md` suelto ahí
  alteraría lo que reporta `validate_agent_ecosystem.py`, además de violar AC17.
- Cero dependencias de proveedor: esta fase es determinista y no llama a ningún modelo. El único
  contacto con el proveedor de decisiones es leer el informe que produjo FASE-C.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | Tarea 2 / **AC20**: el delta de lectura se formula como resta con par pre/post, no como «un tercio menos» |
| L-PF10 | Vacío ≠ ausente | Tarea 1 / **AC22**: una sección declarada y no resuelta **no** puede producir un pack más corto en silencio; es su propio estado |
| L-PF6 | Lector roto leído como ausencia | Tarea 1 / **AC22**: si la fuente no existe o no se parsea, el pack se niega a emitirse |
| L-NC10 | Texto estático que ignora la fuente dinámica de verdad | Tarea 3 / **AC21**: el pack declara HEAD, rutas de origen y hash por fuente; `--check` lo vence contra el árbol |
| L-V2.3 | Medir la forma del artefacto equivocado deja pasar el rojo | Tarea 3 / **AC21**: se prueba contra el archivo generado en disco, no contra el objeto en memoria |
| L-R.3 | Un `[OK]` sin denominador no informa | **AC20/AC22**: bytes exactos + tokens **estimados** con el divisor declarado, y la población de secciones miradas |
| L-HF1 | Candado con la cobertura equivocada pasa en verde mientras el artefacto miente | **AC19**: el pack dice qué **no** incluye y qué sigue siendo obligatorio leer aparte |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | **AC23**: mutation check sobre el guard de truncamiento silencioso |

## Tareas

### Tarea 1: Componer el pack desde lo declarado

**Objetivo**: `build_phase_briefing.py --plan <PLAN>` recorre los prompts de fase del plan, extrae
su lista de lectura, resuelve cada sección nombrada y emite `briefing/FASE-X.md` con la sección
copiada y su procedencia al pie.

**Archivos afectados**: `scripts/build_phase_briefing.py` (nuevo),
`tests/quality_gates/phase_briefing/` (nuevo), `…/briefing/` (generado).

**Criterios de aceptación**: **AC19** — el pack se genera para **todas** las fases del plan y
declara `no_incluye[]` y `lectura_aparte_obligatoria[]` (el workflow canónico entra aquí: este plan
no lo rebaná). Ningún archivo bajo `.agents/` es modificado ni copiado como sustituto.

### Tarea 2: Medir la **carga total** de lectura del delta

**Objetivo**: publicar el antes y el después con el mismo comando, sobre las fases de **este** plan
(las de `REFACTOR-WHATSAPP` se reportan como referencia, no como objetivo: sus nueve citas al
workflow canónico siguen intactas).

**⟦Enmendado el 2026-09-24 por la orden de calidad §4.C, fila `CONTEXTO/D`⟧**: el delta no se saca
entre «suma de las fuentes declaradas» y «bytes del pack». Cada lado publica los **tres sumandos** y
la resta va entre totales:

| Sumando | Clave en `carga.json` | Qué contiene |
|---|---|---|
| Workflow y lecturas aparte | `workflow_obligatorio` | Lo que la fase **sigue** leyendo pese al pack: `lectura_aparte_obligatoria[]` completo, con el workflow canónico a la cabeza mientras D3 no lo rebane |
| Coste de producir el pack | `coste_de_generacion` | La invocación del generador que la sesión ejecuta para obtenerlo, publicada tal cual |
| Pack leído | `pack_consumido` | Los bytes del pack que la fase efectivamente lee |

**No equiparar concatenar con ahorrar.** Unir siete documentos en un archivo no baja la suma de sus
bytes y suele subirla (encabezado, procedencia al pie, `no_incluye[]`). El único ahorro que AC20 puede
atribuirse es lo que **dejó de leerse porque no entró al pack**, y eso solo es visible si se publica
también la omisión. Un delta total cero o negativo es resultado válido y se explica (L-D3: un baseline
absoluto hace que cumplir cuente como violación).

**Criterios de aceptación**: **AC20** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before` y
`after` en **bytes exactos** y **tokens estimados con el divisor declarado**, por fase; `method`
con el comando literal de medición; y el par `*_baseline_pre.txt` / `*_baseline_post.txt` con la
resta comprobada (R2.3, R2.7). El delta se reporta por fase y en total; un delta negativo (pack más
grande que leer las fuentes) es un resultado válido y se explica, no se esconde.

### Tarea 3: Frescura por entradas relevantes, proveniencia y negativa a truncar

**Objetivo**: que el pack no pueda mentir por anticuado ni achicarse por error.

**⟦Enmendado el 2026-09-24 (orden §4.C, fila `CONTEXTO/D`) — dos puntos⟧**:

1. **Qué vence el pack.** El predicado de `--check` es el **sha256 de cada fuente listada en
   `sources[]` contra el árbol vigente**, con sus causas distinguibles (`FUENTE-AUSENTE` / sha
   distinto / fuente ilegible). `provenance.head` dice **de qué árbol salió** el pack; no es la llave
   de caducidad. Si HEAD gobernara, el commit que guarda este generado lo dejaría vencido dentro del
   mismo commit — circularidad que la orden prohibió. Por tanto: HEAD distinto con fuentes idénticas
   **no** produce pack vencido (se publica como procedencia distinta); el pack **no** figura en su
   propio `sources[]`; y el generador tiene que resolver un plan **también bajo `Archives/`**, porque
   el RELEASE regenera y verifica **después** del `git mv`.
2. **Qué hace D con lo que C no midió.** D **acepta** el resultado de C como está publicado: el tramo
   semántico de AC15 es `NO-EJERCITADO` y **D6 sigue dormida**. D no reabre C, no renegocia E1–E5 y no
   presenta la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo que D hereda medido
   de C es su parte mecánica (estados del índice, umbral sobre `confidence`, aditividad, denominador
   con sus ceros), y esa es la que el pack puede mostrar.

**Criterios de aceptación**: **AC21** (clave `provenance` con `head`, `generated_at`, y `sources[]`
con sha por fuente; `--check` falla si cambió el sha de una fuente gobernada y **no** falla por el
solo hecho de que HEAD avanzó; la prueba se hace **re-editando una fuente
y re-midiendo en disco**, no leyendo el objeto en memoria) y **AC22** (los tres estados de R2.9:
`COMPLETO` / `SECCION-NO-RESUELTA`, con la sección pedida y las rutas intentadas /
`FUENTE-AUSENTE`; prohibido emitir un pack más corto sin declararlo; tres tests nombrados por su
causa). **AC23**: mutation check sobre el símbolo real que impide el truncamiento, con rojo y verde
en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/mutation/`.

## Tests obligatorios

| Test | Criterio de éxito |
|------|-------------------|
| `test_briefing_se_genera_por_fase.py` | AC19 con `no_incluye[]` no vacío |
| `test_briefing_seccion_no_resuelta.py` | AC22: nombra la sección pedida y las rutas intentadas; **no** emite pack corto |
| `test_briefing_fuente_ausente.py` | AC22: `FUENTE-AUSENTE` con la ruta buscada |
| `test_briefing_check_vence_con_arbol.py` | AC21: **cambiar el sha de una fuente** y que `--check` falle; revertir y que pase |
| `test_briefing_head_no_es_la_llave_de_caducidad.py` | ⟦bloque C, orden §4.C⟧ HEAD avanzado con fuentes idénticas **no** vence el pack: se publica la procedencia distinta y el check pasa |
| `test_briefing_resuelve_plan_archivado.py` | ⟦bloque C⟧ el generador resuelve un plan bajo `Archives/` (es la llamada que hace el RELEASE después del `git mv`) |
| `test_briefing_corpus_real.py` | R2.6: genera el pack de al menos **una fase de un plan archivado real**, con `skipif` visible y su corrida declarada |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/phase_briefing -v
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-D ✅, y **re-declarar D6 con el estado real de AC15**, no con una
   expectativa. ⟦Precisión del bloque C, 2026-09-24⟧: la rama «el triaje salió aceptable» **no es
   alcanzable mientras D7 esté inactiva**, porque con proveedor falso `acceptance` solo puede publicarse
   como `NO-EJERCITADO` (contrato **E4**). Así que D **no** activa D6 ni la re-asigna por interpretación:
   la deja **dormida con su causa escrita** y con el disparador intacto (proveedor real mediante). Si D
   encontrara un defecto mecánico en el output de C —estados colapsados, umbral sobre el campo
   equivocado, una fila que desaparece— eso **sí** se registra, con dueño y evidencia, y no se resuelve
   tocando el script de C desde D.
2. `README.md` — progreso, y el número real de ACs verificados (AC19–AC23).
3. `06-checklist-implementacion.md` — casillas de la fase.
4. `09-documentacion-post-proyecto.md` — Sección A (módulo nuevo), B, D (fuente de la métrica de carga
   y su delta, con comando y enlace a `carga.json`), E.
5. `10-analisis-post-implementacion.md` — fila de la fase y lecciones nuevas (o «sin lecciones nuevas»);
   analizar el delta respecto de **A7** por referencia a `09` §D y `carga.json`, sin transcribir cifras.
6. `00-lecciones-capitalizadas.md` — «Qué cambia» con lo que realmente pasó; si la fase descubrió
   una fuente que el Paso 0 no consultó, añadir la consulta y su descarte.

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D \
  --desc "build_phase_briefing.py: pack derivado por fase, proveniencia con sha, negativa a truncar y delta de carga de lectura (AC19-AC23)" \
  --archivos-mod "scripts/build_phase_briefing.py,tests/quality_gates/phase_briefing" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

## Criterios de completitud

- [ ] Los tests de la tabla pasan y ninguno cubre dos estados (⟦2026-09-24⟧ la tabla creció de cinco a
      siete al cubrir la no-circularidad de HEAD y la resolución del plan archivado).
- [ ] `carga.json` trae `method` con el comando literal, bytes exactos y el divisor declarado, **y los
      tres sumandos de la carga total** por fase (`workflow_obligatorio`, `coste_de_generacion`,
      `pack_consumido`).
- [ ] El par pre/post existe y la resta está comprobada **entre cargas totales**, no entre «fuentes» y
      «pack». La concatenación no se presenta como ahorro.
- [ ] Delta explicado por fase; cero o negativo declarado, no escondido.
- [ ] `--check` falla contra una **fuente** editada y pasa al revertir (demostrado en disco); y **no**
      falla solo porque HEAD avanzó.
- [ ] El generador resuelve un plan bajo `Archives/` (demostrado, no afirmado: es la llamada del
      RELEASE después del `git mv`).
- [ ] Tres estados de resolución de secciones, un test por estado.
- [ ] `mutation/` tiene rojo y verde del guard de truncamiento (AC23). Sin rojo, ⚠️.
- [ ] Test contra una fase de un plan **archivado real**, con `skipif` y su corrida declarada (R2.6).
- [ ] `git status .agents/` vacío al cerrar: `.agents/` sin un solo byte cambiado.
- [ ] `--quick` verde con su composición intacta (AC16, delta 0 con su par pre/post).
- [ ] Dependencia D6 **re-declarada, no re-abierta**: sigue **dormida** porque AC15 publicó
      `NO-EJERCITADO`, y D registra la causa en `dependencias-fases.md` sin reinterpretar el
      disparador ni reabrir C.
- [ ] Post-ejecución completa e índice regenerado y comprobado sobre el mismo árbol final verificado.
      El commit es opcional, posterior y requiere autorización explícita; no condiciona ninguno de
      los cinco cortes del proceso común.

## Restricciones

- **No toca `.agents/`** en modo escritura. El workflow canónico se lee, se referencia y se declara
  como lectura aparte; **no** se sustituye por el pack.
- No modifica ningún prompt de fase de ningún plan, incluido los de este: el generador los **lee**.
- No rebaná el workflow ni reescribe las nueve citas al canónico del otro plan (deuda D3).
- No llama a ningún proveedor de decisiones. Es determinista o no es.
- No ejecuta la pipeline ni toca `output/` en escritura. No commitea ni empuja sin instrucción literal.
- Presupuesto con instrumento y corte declarados (R2.1); nunca estimado.

## Prompt de ejecución

```text
Ejecuta unicamente FASE-D del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-D.md, 01-plan-maestro.md §1 (medicion A7 y la nota de divisor de
tokens), §4 (AC19-AC23, AC16, AC17), 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2,
dependencias-fases.md (cadena y la regla de donde vive el pack generado) y el workflow canonical.
Heredas de A los tres estados y coverage_basis, y de C el informe de candidatos.
Escribe scripts/build_phase_briefing.py: recorre los prompts de fase del plan, extrae la lista de
lectura que cada uno DECLARA, resuelve cada seccion nombrada y emite briefing/FASE-X.md con la
seccion copiada y su procedencia al pie. Modelo a emular: build_lesson_index.py (generado, con
--check, prohibido editar a mano).
Tres reglas duras. Una: el pack nunca se calla un recorte — seccion declarada y no resuelta es su
propio estado, con la seccion pedida y las rutas intentadas, y el script se niega a emitir un pack
mas corto en silencio. Dos: proveniencia con HEAD, fecha y sha por fuente, y --check vence contra
el arbol; la prueba se hace editando una fuente y re-midiendo en disco, no leyendo memoria. Tres:
declara no_incluye y la lectura aparte obligatoria, que incluye el workflow canonical.
AC20 mide el delta de carga de lectura con el mismo comando en antes y despues, bytes exactos y
tokens estimados con el divisor declarado, par pre/post y la resta comprobada. La resta se saca entre
CARGAS TOTALES, cada una con sus tres sumandos publicados: workflow_obligatorio (lo que la fase sigue
leyendo aparte, workflow canonico incluido mientras D3 no lo rebane), coste_de_generacion (la invocacion
del generador que la sesion ejecuta) y pack_consumido. Concatenar documentos no es ahorrar: unir siete
archivos en uno no baja la suma de sus bytes. El unico ahorro atribuible al pack es lo que dejo de
leerse porque no entro, y eso se publica con su omision. Un delta cero o negativo es resultado valido
y se explica.
AC21: la frescura la gobierna el sha256 de las fuentes listadas en sources[], con sus causas
distinguibles. head es procedencia, no llave de caducidad: si HEAD gobernara, el commit que guarda el
propio pack generado lo dejaria vencido dentro de ese commit. Por eso HEAD avanzado con fuentes
identicas NO vence el pack, y el pack no entra en su propio sources[]. El generador resuelve un plan
tambien bajo Archives/, porque el RELEASE regenera y verifica el pack despues del git mv; ese rojo se
resuelve regenerando, nunca editando codigo.
De C heredas su parte mecanica medida y aceptas su parte no medida: acceptance de AC15 es
NO-EJERCITADO y D6 sigue dormida. No reabras C, no renegocies E1-E5 y no presentes los candidatos
exhibidos en el pack como una aceptabilidad obtenida.
No toques .agents/ en escritura, ningun prompt de fase, run_all_validations.py, el hook,
build_lesson_index.py ni los scripts de las fases anteriores. No llames a ningun proveedor: esta
fase es determinista o no es. Re-declara D6 con su causa (dormida mientras D7 este inactiva), no la
actives por interpretacion. Registra la fase con log_phase_completion.py y regenera y comprueba el
indice sobre el mismo arbol final verificado.
Los cinco cortes no requieren commit: es opcional, posterior y autorizado por separado.
Deja checkpoint si falta autorizacion.
```
