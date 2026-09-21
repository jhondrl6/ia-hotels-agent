# FASE-D — Generador de briefing pack por fase y delta de carga de lectura

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-D
**Objetivo**: escribir `scripts/build_phase_briefing.py`, que compone por cada fase un único
archivo con las secciones que su prompt declara leer, y medir el delta de carga de lectura que eso
produce. Cubre AC19–AC23.
**Dependencias**: FASE-A ✅ (estados y `coverage_basis`), FASE-B ✅ (costura, para el candidato de
pertinencia que el pack puede anotar), FASE-C ✅ (el triaje cuyo output el pack consume como
sección propia, y su medición de aceptabilidad que activa la deuda D6).
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

### Tarea 2: Medir el delta de carga de lectura

**Objetivo**: publicar el antes y el después con el mismo comando, sobre las fases de **este** plan
(las de `REFACTOR-WHATSAPP` se reportan como referencia, no como objetivo: sus nueve citas al
workflow canónico siguen intactas).

**Criterios de aceptación**: **AC20** — artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` con `before` y
`after` en **bytes exactos** y **tokens estimados con el divisor declarado**, por fase; `method`
con el comando literal de medición; y el par `*_baseline_pre.txt` / `*_baseline_post.txt` con la
resta comprobada (R2.3, R2.7). El delta se reporta por fase y en total; un delta negativo (pack más
grande que leer las fuentes) es un resultado válido y se explica, no se esconde.

### Tarea 3: Frescura, proveniencia y negativa a truncar

**Objetivo**: que el pack no pueda mentir por anticuado ni achicarse por error.

**Criterios de aceptación**: **AC21** (clave `provenance` con `head`, `generated_at`, y `sources[]`
con sha por fuente; `--check` falla si el árbol cambió; la prueba se hace **re-editando una fuente
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
| `test_briefing_check_vence_con_arbol.py` | AC21: editar una fuente y que `--check` falle; revertir y que pase |
| `test_briefing_corpus_real.py` | R2.6: genera el pack de al menos **una fase de un plan archivado real**, con `skipif` visible y su corrida declarada |

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/phase_briefing -v
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — FASE-D ✅, y **actualizar D6**: si el triaje de FASE-C salió aceptable,
   la deuda del lint de contradicciones queda con disparador vigente; si no, se re-asigna con la
   medición que lo justifica.
2. `README.md` — progreso, y el número real de ACs verificados (AC19–AC23).
3. `06-checklist-implementacion.md` — casillas de la fase.
4. `09-documentacion-post-proyecto.md` — Sección A (módulo nuevo), B, D (la métrica de carga, con
   su comando), E.
5. `10-analisis-post-implementacion.md` — fila de la fase, lecciones nuevas, métricas reales, y la
   **medición A7** (carga de lectura) con su delta.
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

- [ ] Los cinco tests pasan y ninguno cubre dos estados.
- [ ] `carga.json` trae `method` con el comando literal, bytes exactos y el divisor declarado.
- [ ] El par pre/post existe y la resta está comprobada; delta explicado por fase.
- [ ] `mutation/` tiene rojo y verde del guard de truncamiento (AC23). Sin rojo, ⚠️.
- [ ] `--check` falla contra un árbol modificado (demostrado, no afirmado).
- [ ] El test contra plan archivado real declara si **corrió** o se saltó, con motivo (R2.6).
- [ ] `.agents/` sin un solo byte cambiado; verificado con `git status` sobre esa ruta.
- [ ] `--quick` verde con su composición intacta (AC16).
- [ ] Post-ejecución completa e índice regenerado en el mismo commit.

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
tokens estimados con el divisor declarado, par pre/post y la resta comprobada. El delta se reporta
sobre las fases de ESTE plan; las del otro plan son referencia, no objetivo, porque sus nueve citas
al workflow canónico siguen intactas.
No toques .agents/ en escritura, ningun prompt de fase, run_all_validations.py, el hook,
build_lesson_index.py ni los scripts de las fases anteriores. No llames a ningun proveedor: esta
fase es determinista o no es. Actualiza D6 segun como salio el triaje de C. Registra la fase con
log_phase_completion.py y regenera el indice en el mismo commit. Deja checkpoint si falta autorizacion.
```
