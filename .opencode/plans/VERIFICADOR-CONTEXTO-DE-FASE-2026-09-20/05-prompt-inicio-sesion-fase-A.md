# FASE-A — Lint determinista de aserciones numéricas en documentos de gobierno

**ID**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 / FASE-A
**Objetivo**: escribir `scripts/validate_governance_numbers.py`, que compara cada aserción sobre
un conteo en los documentos de gobierno contra la **fuente dinámica de verdad** (las etiquetas
que el código imprime), publica denominador y expresa los tres estados. Cubre AC1–AC5.
**Dependencias**: ninguna. Es la primera fase de la cadena.
**Duración / scope**: 1 sesión; **3 tareas** de código + **0** comandos de larga duración
(R3 permite máximo 4 tareas y 0 comandos largos).
**Skill**: `phased_project_executor` (este plan) — no ejecuta la pipeline.

## Contexto

Los documentos de gobierno del repo afirman cuántos checks corren. Cuatro de esas afirmaciones
están hoy vencidas contra el código que las ejecuta, y **ningún check las sostiene**: se
cumplen por coincidencia (L-R.1). Esta fase escribe el verificador; **no** corrige el texto.

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| — | Esta es la primera |

`REFACTOR-WHATSAPP-ENTREGA-2026-09-18` está en vuelo y **no es dependencia ni consumidor** de
esta fase. Sus superficies compartidas con usted, medidas el 2026-09-20, son **dos**: la pareja
`.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (la regenera cualquier `.md` de
plan que nombre un ID, y `[6/7]` del hook lo exige en el mismo commit) y **la cifra que ese plan
pinea** — 11 checks del `--quick` — que no está en su prompt de FASE-C sino en cuatro documentos
suyos: el bloque de arranque de FASE-B de su `README.md`, su `06-checklist-implementacion.md`, su
`09-documentacion-post-proyecto.md` y su `10-analisis-post-implementacion.md`. Por eso AC16 se formula
como delta 0. Y **hay un tercer plan en esa superficie**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`
(commiteado, PENDIENTE) declara dentro de su alcance `scripts/run_all_validations.py` — el archivo
cuyas etiquetas son la fuente de verdad de esta fase— y `scripts/validate_qmind_writeback.py`. Usted
**no** lo toca y **no** le pasa nada a FASE-A por eso; lo que cambia es el RELEASE de este plan, que
debe re-leer esa interfaz antes de correr el `--upload` (deuda **D10**).

### Base técnica disponible

- Fuente de verdad de los conteos: `def run_all` en `scripts/run_all_validations.py` ejecuta 11
  checks en modo `--quick` y 4 más solo en modo completo; cada check imprime su etiqueta
  `[N/M]` dentro de su propio método (`def _check_plan_citations`, `def _check_lesson_capitalization`).
- Otra fuente: `scripts/git_hooks/pre-commit`, que declara 7 pasos `[1/7]`…`[7/7]` en su cabecera.
- Objetos auditados (solo lectura): `.agents/workflows/phased_project_executor.md` y
  `.agents/workflows/templates/lecciones-capitalizadas-template.md`.
- Modelo a imitar en forma y alcance: `scripts/validate_plan_citations.py` (reporta, no
  reescribe; alcance hacia delante + delta) y `scripts/validate_lesson_capitalization.py`
  (aplica R2.9 a sí mismo).
- Tests: selecciones acumulativas por plan, no un número absoluto (L-D3).

### Lecciones capitalizadas aplicables a esta fase

Copiadas de `00-lecciones-capitalizadas.md` §2, filtradas por pertinencia a FASE-A.

| ID | Lección (una línea) | Qué cambia en ESTA fase |
|----|---------------------|-------------------------|
| L-R.1 | Regla que vive solo en el workflow y no en el artefacto, se cumple por coincidencia | Tarea 1: el verificador compara contra la etiqueta que el código imprime, no contra otra frase del documento |
| L-NC10 | Texto estático que ignora la fuente dinámica de verdad | Tarea 1: la lista de aserciones se descubre escaneando los documentos, no se hardcodea como las 4 medidas |
| L-R.3 | Un `[OK]` sin denominador no informa | Tarea 2 / **AC2**: `coverage_basis` es obligatoria; sin ella no puede existir `SIN-HALLAZGOS` |
| L-PF6 | Lector roto leído como ausencia produjo un pain falso con cifra económica | Tarea 2 / **AC3**: un `except` que devuelva «sin hallazgos» está prohibido |
| L-PF10 | Vacío ≠ ausente | Tarea 2 / **AC3**: tres estados, tres tests nombrados por su causa |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | Tarea 3 / **AC4**: mutation check **por aserción**, sobre el símbolo real del guard |
| L-VUP-5 | Una fase que no produce ni un rojo es un falso verde potencial | Criterios de completitud: el verde a la primera se declara sospechoso y se explica |
| L-D3 | Baseline absoluto hace que cumplir cuente como violación | **AC5**: el conteo se formula como delta con par pre/post, delta esperado 0 |
| L-V2.3 | Renumerar sin medir quién afirma el conteo deja contrato huérfano | **AC5/AC16**: esta fase no renumera nada y mide quién afirma el 11 y el 7 |
| L-HF1 | Candado con la cobertura equivocada pasa en verde mientras el artefacto miente | **AC2/AC17**: declarar `families_not_covered[]` es AC, no nota al pie |

## Tareas

### Tarea 1: Escanear aserciones contra su fuente

**Objetivo**: `validate_governance_numbers.py` localiza, en los documentos de gobierno, toda
afirmación del tipo «este verificador es el check N de M» o «el hook corre K pasos», y la
contrasta contra las etiquetas impresas por el código.

**Archivos afectados**: `scripts/validate_governance_numbers.py` (nuevo),
`tests/quality_gates/governance_numbers/` (nuevo).

**Criterios de aceptación**: **AC1** — sobre el árbol vigente reproduce exactamente A1–A4 del
maestro §1 y ninguna otra; artefacto `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` con `findings[]`
(`assertion_id`, `document`, `claimed`, `observed`, `occurrences[]`). **La población tiene regla
explícita (medición A8 del maestro §1): sin ella este criterio es inalcanzable.** El escaneo de los
dos documentos de gobierno no devuelve cuatro coincidencias sino **22 instancias `[N/M]` en 17
líneas más 2 formas «check N»**; hay que clasificar cada una como **viva** (sostiene una regla
vigente → se contrasta y puede ser hallazgo), **histórica congelada** (mención fechada o dentro de
una entrada de changelog — el propio workflow declara en `v2.24.0` que sus menciones históricas «se
conservan literales» → se excluye **y se publica** en `historical_excluded[]` con su conteo y la
frase que la ampara) o **vigente y correcta** (entra en `assertions_checked` sin generar hallazgo).
Un hallazgo es **una aserción** con sus `occurrences[]`, no una línea: A1 está escrita en dos sitios
del workflow y sigue siendo un hallazgo. Cero coincidencias debe ser indistinguible de «no leí» solo
si falta `coverage_basis`: por eso AC2 es prerrequisito de AC1, no un extra.

### Tarea 2: Denominador y los tres estados

**Objetivo**: publicar la población mirada y distinguir `SIN-HALLAZGOS` / `AUSENTE` /
`LECTOR-FALLIDO`.

**Archivos afectados**: el mismo script y sus tests.

**Criterios de aceptación**: **AC2** (`coverage_basis` con `documents_scanned`,
`assertions_checked`, `families_not_covered[]`, `excluded[]`) y **AC3** (clave `status`, tres
tests nombrados por su causa, ninguno cubre dos estados).

### Tarea 3: Mutation check y par pre/post

**Objetivo**: probar que el verde es causado por el guard, y dejar constancia de que la fase no
alteró ningún conteo.

**Archivos afectados**: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/`, `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/*_baseline_pre.txt`,
`*_baseline_post.txt`, `baseline-pre-post.md`.

**Criterios de aceptación**: **AC4** (reversión por aserción sobre el símbolo real, dos salidas
en disco; sin el lado rojo AC4 queda ⚠️. **Anclaje L-V2.1**: cada mutante se afirma sobre el
`assertion_id` que dice atacar — mutar la guarda de A2 y obtener «un hallazgo» cualquiera no prueba
nada, porque otra rama puede producirlo) y **AC5** (delta 0 en 11 checks del quick y 7 del hook,
resta comprobada; una resta 0 con tests nuevos declarados = baseline contaminado y no se cierra.
**La pregunta «quién afirma el 11 y el 7» se responde barriendo también `tests/`, no solo los
documentos**: L-V2.3 se capitalizó exactamente porque el rojo vivo estaba en un contract test, y hoy
sigue habiendo uno (`tests/test_validate_plan_closure.py` assertiona `[5/7]` del hook).

## Tests obligatorios

| Test | Archivo | Criterio de éxito |
|------|---------|-------------------|
| `test_governance_numbers_reproduce_A1_A4.py` | `tests/quality_gates/governance_numbers/` | 4 hallazgos con sus `assertion_id` exactos y **nada adicional**; y el inverso de la misma moneda: `historical_excluded[]` publica las menciones congeladas **con su conteo** (A8), así que el verde no puede venir de haber recortado la población a mano |
| `test_governance_numbers_por_asercion_no_por_linea.py` | ídem | A1, escrita en dos sitios del workflow, produce **un** hallazgo con `occurrences[]` de dos entradas: el conteo de hallazgos no depende de cuántas veces se repita la frase |
| `test_governance_numbers_sin_hallazgos.py` | ídem | Estado `SIN-HALLAZGOS` imprime sobre qué midió |
| `test_governance_numbers_ausente.py` | ídem | Estado `AUSENTE` imprime la ruta buscada |
| `test_governance_numbers_lector_fallido.py` | ídem | Estado `LECTOR-FALLIDO` imprime el motivo y **nunca** un favorable ni un 0 |

**Comando de validación**

```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/governance_numbers -v
./venv/Scripts/python.exe scripts/validate_governance_numbers.py --report
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-ejecución (OBLIGATORIO)

1. `dependencias-fases.md` — marcar FASE-A ✅ con fecha y notas de ejecución.
2. `README.md` del plan — progreso y contador de ACs con su estado real (⚠️ donde falte el rojo).
3. `06-checklist-implementacion.md` — casillas de AC1–AC5.
4. `09-documentacion-post-proyecto.md` — Sección A (módulo nuevo), B (funcionalidad), D (métricas), E (archivos afiliados).
5. `10-analisis-post-implementacion.md` — fila de FASE-A en el resumen, lecciones nuevas con su
   pertinencia INCLUIR/EXCLUIR, métricas reales, seguimientos, y decisiones con su rationale y
   las alternativas rechazadas.
6. `00-lecciones-capitalizadas.md` — anotar en «Qué cambia» lo que **realmente** pasó; una lección
   citada y no aplicada se marca como tal, **no se borra**; y actualizar §4 al estado del cierre.

Luego, y antes de cerrar la sesión:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A \
  --desc "validate_governance_numbers.py: asercion contra fuente dinamica, denominador y 3 estados (AC1-AC5)" \
  --archivos-mod "scripts/validate_governance_numbers.py,tests/quality_gates/governance_numbers" \
  --tests "N" --check-manual-docs
./venv/Scripts/python.exe scripts/build_lesson_index.py
```

El índice se regenera **en el mismo commit**: esta fase escribió `.md` bajo `plans/` que nombra
IDs (L-R.1, L-NC10, …), y `[6/7]` del hook lo comprueba contra el árbol final (R2.10).

## Criterios de completitud

- [ ] Los cuatro tests pasan y **ninguno** cubre dos estados.
- [ ] `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/` contiene el rojo y el verde (AC4). Si falta uno, AC4 es ⚠️.
- [ ] `baseline-pre-post.md` muestra la resta y delta 0 (AC5).
- [ ] `informe.json` tiene `coverage_basis` legible sin abrir el código (AC2).
- [ ] `run_all_validations.py --quick` verde **sin** haber tocado su composición (AC16).
- [ ] Ninguna aserción de `.agents/` fue editada (AC17).
- [ ] Rojos preexistentes ajenos declarados con dueño y causa, no arrastrados ni maquillados.
- [ ] Post-ejecución completa, incluidos `log_phase_completion.py` y el índice.

## Restricciones

- No modificar `scripts/run_all_validations.py`, `scripts/git_hooks/pre-commit`, `.agents/**`,
  `scripts/build_lesson_index.py` ni `scripts/validate_lesson_capitalization.py`.
- No ejecutar `v4complete`, `v4audit` ni la pipeline. No tocar `output/` en modo escritura: los
  artefactos de ahí son históricos y de otro plan.
- No escribir sobre ningún plan vivo, `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` en particular.
- No commitear ni empujar sin instrucción literal del operador.
- Presupuesto: instrumento y corte declarados (R2.1). Si el instrumento no corre bajo la
  política de permisos de la sesión, se publica en la unidad usada y se declara no comparable, o
  se retira la métrica. **Nunca estimada.**

## Prompt de ejecución

Copiar en una sesión nueva:

```text
Ejecuta únicamente FASE-A del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md §1 (la tabla A1-A4 con su rectificacion de
A3, la medicion A7 y la poblacion A8) y §4 (AC1-AC5 con la regla de poblacion, AC16, AC17),
04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4,
dependencias-fases.md y el workflow canónico. **Estado medido del árbol al publicarse la auditoría
(`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`): limpio, con
el índice de lecciones ya regenerado y fresco.** No lo des por supuesto: re-mide HEAD/status al abrir,
porque la pareja del índice la comparte con las fases vivas de `REFACTOR-WHATSAPP` y puede llegarte
modificada. No hay nada que rescatar de una fase anterior —A es la primera de este plan.
Re-mide antes de la primera tarea y publica el numero: git HEAD/status, la etiqueta que imprime CADA
def _check_* (emparejando etiqueta y metodo: [15/15] es el write-back de QMind y [12/15] es
dependencias; confundirlas fue el error de A3), los siete pasos del hook, y el tamano en bytes de los
siete documentos que suma A7 (263.973 al 2026-09-20, no 254.010).
Escribe scripts/validate_governance_numbers.py: compara cada asercion sobre un conteo en los
documentos de gobierno contra la etiqueta [N/M] que el codigo imprime, descubre las aserciones
escaneando los documentos (no hardcodeando las cuatro) **y aplica la regla de poblacion de A8: clase
viva, historica congelada publicada en historical_excluded[], y vigente-correcta contada en
assertions_checked; un hallazgo es una asercion con sus occurrences[], no una linea**, publica
coverage_basis con la poblacion mirada y las **cuatro** families_not_covered medidas (prosa sin
patron, conteos fuera de los documentos de gobierno -AGENTS.md, docs/GUIA_TECNICA.md,
docs/contributing/REGISTRY.md-, pins de conteo en tests/, y fuentes dinamicas que no sean etiqueta
impresa), y expresa los tres estados sin que ninguno colapse.
Reutiliza el disenno de validate_plan_citations.py (reporta, no reescribe) y de
validate_lesson_capitalization.py (R2.9 sobre si mismo).
No toques run_all_validations.py, el hook, .agents/, build_lesson_index.py ni ningun plan vivo.
Todo AC de detencion se cierra con mutation check sobre el simbolo real del guard, por asercion y
**afirmando el assertion_id del mutante (L-V2.1)**,
con las dos salidas en evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/. El conteo del quick (11) y del hook (7) se expresa como
delta con par pre/post y la resta comprobada, delta esperado 0, y la pregunta de quien afirma el 11 y
el 7 se responde barriendo tambien tests/ (L-V2.3).
Cada fase se registra a si misma con log_phase_completion.py y regenera el indice de lecciones
en el mismo commit. Deja checkpoint si falta autorizacion y conserva los ACs en el estado real
que puedan probar: VERIFICADO OFFLINE con rojo y verde, o ⚠️.
```
