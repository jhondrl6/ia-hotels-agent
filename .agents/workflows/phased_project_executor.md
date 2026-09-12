---
description: Ejecutor de proyectos por fases. Una fase por sesión. Sin excepciones. Iteraciones medidas con `evidence/FASE-D/measure_iterations.py`, cortadas en el commit de código. El Paso 0 capitaliza lecciones en `00-lecciones-capitalizadas.md` consultando el índice generado del corpus. Ejecutado por agentes AI.
version: v2.23.1
---

# Skill: Phased Project Executor

> [!NOTE]
> **Fuente canónica de contexto**: `AGENTS.md` contiene el contexto global del proyecto
> (módulos activos, thresholds, flujo v4complete). Consultar AGENTS.md para:
> - Umbrales de coherencia (≥ 0.8), confidence (≥ 0.9/0.7), publication gates
> - Módulos activos y su propósito
> - Flujo v4complete completo (FASE 1-5)
>
> Para procedimientos documentales, ver `docs/CONTRIBUTING.md`.
> Para ejecución operativa por fases, este documento es la fuente primaria.

> [!NOTE]
> **Trigger**: "Ejecuta por fases", "Continúa en nueva sesión", "Divide en sprints", "Preserva contexto para siguiente fase", "Trabajo por fases".

## Regla de Sesión Única (OBLIGATORIO)

> [!CAUTION]
> **REGLAS MANDATORIAS - Sin excepciones**
>
> **R1: Una fase por sesión.** No se permite ejecutar múltiples fases en una misma sesión.
>
> **R2: El presupuesto de iteraciones se MIDE, no se estima.** Instrumento canónico:
> `evidence/FASE-D/measure_iterations.py`. Corte fijo: **hasta el commit de código** (lo que se
> escriba después es cierre documental y no cuenta contra el presupuesto de implementación). Si la
> fase no puede correr el instrumento, el auto-reporte se publica **en la unidad usada**
> (`tool_use`, `ids únicos`, etc.) y se declara que no es comparable con las demás. Ver §R2.1-R2.10.

## Reglas de Proceso v2.23.1 (OBLIGATORIO — propuestas por FASE-VERIFY y por el Paso 0, 2026-09-04, 2026-09-11 y 2026-09-12)

Las diez reglas siguientes existen porque un plan las violó o las descubrió tarde (y la sesión
post-release de `ESTABILIZACION-PRE-TRIBUNAL` aportó la quinta: un archivado que quedó como
reproceso, ver R2.5). R2.1-R2.5 vienen de la certificación de 2026-09-04; **R2.6 y R2.7** de la
certificación del plan `TRIBUNAL-OFFLINE-2026-09-09` (decisión D-V.3, endosada por FASE-VERIFY
2026-09-11 y ejecutada por su FASE-RELEASE); **R2.8 y R2.9** son las no-regresiones **NR7** y **NR8**
del plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`, ascendidas a regla global desde su §7 porque la
medición que las fundó no es particular de ese plan; **R2.10** pone nombre a una restricción de
timing que ya estaba escrita en dos sitios (R2.5 y el write-back del §4) y nombrada en ninguno. Cada
una lleva su medición de origen: una norma sin medición es la regla que se escribe y no se cumple
(ver R2.4).

### R2.1 — Presupuesto: medir o retirar la métrica, nunca estimar (S22 / DA-V6)

**Medido**: nueve fases medibles del plan `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` excedieron su
presupuesto (entre **2,4× y 8,6×**) y ni siquiera eran comparables entre sí: cada fase reportó en
una unidad distinta porque el instrumento canónico no corre bajo la política de permisos actual.
Un número que no se puede medir ni comparar no restringe nada (L-B3).

**Regla**: toda fase declara presupuesto **y** el instrumento con que lo corta (corte: commit de
código). Al cerrar, o (a) el presupuesto se recalibra **×3** sobre la distribución medida, o
(b) **se retira la métrica** del plan y se declara fuera de servicio. Prohibido: reportar un
cumplimiento estimado, o mezclar unidades en un total.

### R2.2 — Prohibidos los números de línea en ACs y prompts de fase: citar símbolos (L-A6 / L-V4 / L-H4)

**Medido**: **14 de 16** citas de línea que usaban los criterios de aceptación del plan estaban
desfasadas al certificar (desplazamientos entre **−88 y +104** líneas); solo 2 seguían en su
número. Y FASE-A encontró 4 citas **falsas** en el propio plan, una de ellas repetida 12 veces en
6 archivos, incluidas 3 en el prompt de la fase que iba a editarla.

**Regla**: en criterios de aceptación, prompts de fase y evidencia, se cita **símbolo**
(`def classify_promised_services`, `BLOCKING_GATE_NAMES`, `_not_evaluated_g9()`), nunca `archivo:123`.
Una cita de línea en un plan multi-fase caduca **durante la ejecución del propio plan**, porque cada
fase desplaza las líneas que las siguientes citan. Antes de editar una región ya citada hay que
confirmarla con `grep`/`Read` y, si difiere, corregir la cita y avisar.

**Verificador mecánico**: `scripts/validate_plan_citations.py` (check 8 de
`run_all_validations.py --quick`). Escribe la regla y no medirla es el mecanismo que acabó en S15.

### R2.3 — No-regresión de conteos como **delta**, con par pre/post (S26 / DA-V2)

**Medido**: una NR ordenaba preservar «848 passed / 2 skipped» a todas las fases; una fase agregó
24 tests legítimos y la corrida dio 872 — una «violación» que era exactamente lo que la fase debía
hacer. Con el número absoluto, **cumplir el plan cuenta como violación** (L-D3).

**Regla**: todo invariante de conteo se formula como **delta**:

```
passed_post = passed_pre + tests nuevos de ESTA fase
skipped_post == skipped_pre                      (idéntico)
fallos_ajenos_a_la_fase == 0
```

y es **obligatorio** el par de archivos `*_baseline_pre.txt` / `*_baseline_post.txt` en
`evidence/FASE-X/`, para que el delta sea verificable y no una afirmación. Antes de comparar dos
cifras, decir **qué mide cada una** (unidad de corrida incluida: `def test_` vs `--collect-only`
no coinciden).

### R2.4 — Regla de certificación: AC no legible en el artefacto = ⚠️, nunca ✅ (L-V1 / DA-V3)

**Medido**: AC6 y AC7 estuvieron ✅ durante nueve fases «en código y tests». Medidos sobre el
artefacto de la única corrida: `gate_report_*.json` no tenía **ni una** ocurrencia de `severity` y
`proposal_asset_matrix.json` no tenía la clave `coverage_ratio`. El sistema había decidido; el
artefacto que lee el humano no lo reflejaba.

**Regla**: *un criterio de aceptación que no es legible en el artefacto que el sistema produce se
marca ⚠️, no ✅.* **Un ✅ cuyo único respaldo es «el string está en el código» no existe.**
Consecuencias operativas:

- Cada AC declara **el artefacto y la clave** donde se lee su valor. Si esa clave no existe, el AC
  está incompleto **antes** de ejecutarse.
- Toda propiedad de régimen que deba viajar a disco lleva un **test de serialización** que lee el
  JSON del writer real, no el objeto en memoria.
- Test práctico de completitud: si el AC no puede responder *«¿dónde lo vería un humano que solo
  tiene el ZIP?»*, no está listo para certificarse.
- Donde la corrida no ejercita el camino, se dice que no lo ejercita; no se cuenta el test como
  hecho (el verde de un test prueba el régimen, no la salida).

### R2.5 — El cierre archiva: FASE-RELEASE termina con el plan en `Archives/` (2026-09-04)

**Medido**: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` se cerró con v4.75.0 y quedó en `plans/` raíz;
el archivado se ejecutó como reproceso en la sesión siguiente, pese a que la convención ya existía
(23 planes en `Archives/`, `archived_promotion()` en `validate_opencode_refs.py`, nota QMind).
Una convención que ningún paso del flujo ejecuta es la que se descubre tarde.

**Regla**: FASE-RELEASE termina con el plan archivado, dentro del mismo cierre documental:

```bash
python scripts/validate_qmind_writeback.py --upload <PLAN>    # write-back final, ANTES de archivar
python scripts/build_lesson_index.py                          # el plan cerrado queda consultable
git mv .opencode/plans/<PLAN> .opencode/plans/Archives/
python scripts/build_lesson_index.py                          # 3b (R2.10): publica la ruta nueva
python scripts/validate_opencode_refs.py --fix                # promoción «archived» de referencias
python scripts/validate_plan_citations.py --update-baseline   # claves cambian a plans/Archives/ — acto visible
python scripts/run_all_validations.py --quick                 # verde
```

Archivar primero es lo que rompe las dos cosas de arriba: el write-back resuelve la ruta del
plan por nombre y el índice del corpus se queda sin sus lecciones hasta la próxima corrida.
El orden, con su verificación medida y su pata degradada, es la regla **R2.10**: la segunda
regeneración del índice es obligatoria porque el índice publica el plan dueño **con su ruta** y
`[6/6]` del pre-commit falla contra el árbol final.

Un commit único cierra RELEASE + archivado y las referencias vivas (memoria de sesión, QMind)
apuntan a la ruta nueva. `Archives/` queda fuera del alcance de `validate_plan_closure.py`
(histórico congelado); salir de RELEASE con el plan en raíz garantiza el reproceso que esta
regla elimina.

### R2.6 — Todo lector de artefactos del pipeline se prueba contra el baseline real (D1/D5/S1-S3 · D-T2C-A1 · L-V.1)

**Medido**: en `TRIBUNAL-OFFLINE-2026-09-09` una sola causa produjo cinco defectos (D1, D5, S1, S2,
S3), causó el desvío D-T2C-A1 y dejó **AC8 ❌ al certificar**: los revisores se probaban contra
fixtures construidas por la propia fase, nunca contra un output real del pipeline. La sonda
read-only `evidence/FASE-VERIFY/TRIBUNAL-OFFLINE-2026-09-09/verify_probe_ac8.py` fijó el defecto
en **dos capas** que ningún test podía detectar: el régimen vivo de `deliveries/` es **ZIP-only**
(así que `<zip>/IMPLEMENTATION_ORDER.md` no existe en disco y `_resolve_delivery_dir()` cae al
`.zip`), y el heurístico `_is_template_stub()` contaba como contenido los separadores `---` y el
boilerplate (`non_empty_lines = 10 > 3`). Un test en verde prueba **el régimen del fixture**, no la
salida del sistema.

**Regla**: una fase que escriba **un lector de artefactos del pipeline** —cualquier código que abra
un JSON/MD/ZIP producido por otra etapa— no cierra con ✅ sin **≥1 test contra el baseline real**
(`output/FASE-D_salentoreal_post_guard/` o el output de la corrida vigente):

- El `skip` cuando falta el baseline es **explícito y visible** (`pytestmark =
  pytest.mark.skipif(...)`, no un `return` silencioso). Modelo:
  `tests/quality_gates/tribunal/test_honesty_reviewer_retro_reales.py`.
- La evidencia de la fase declara **si el test corrió o se saltó**. Un skip silencioso es la
  variante muda del mismo defecto: el verde no informa nada.
- Contra fixtures propias solo se certifica lógica pura; todo supuesto sobre la **forma del
  artefacto** (dónde vive, qué claves tiene, si está comprimido) se verifica contra disco real.

### R2.7 — El par pre/post de NR1 se valida **restando**: una resta 0 es baseline contaminado (D-T2C-A1 · rectificación T4-B)

**Medido**: la fase T4-B registró su no-regresión como `4018 → 4025` cuando la pareja medida era
`4029 → 4036`: los **+11** tests de la remediación D-T2C-A1 se habían quedado fuera del `pre`. El
informe cuadraba consigo mismo y no con el repo, y el delta quedó **inflado en 11** sin que nadie
lo notara — porque nadie restaba.

**Regla**: el par `*_baseline_pre*.txt` / `*_baseline_post*.txt` de `evidence/FASE-X/` se publica con
la **suma** `failed+passed+skipped+xfailed` de cada corrida, y la resta se comprueba:

```
suma_post − suma_pre == tests_nuevos_de ESTA fase      (> 0 si la fase añadió tests)
```

- Resta **0** con tests nuevos declarados ⇒ **baseline contaminado**: el `pre` se tomó después de
  escribir los tests, o se copió del `post`. La fase **no** puede cerrarse en ✅.
- Diferencia ≠ `tests_nuevos` ⇒ falta una partida (tests de otra fase no contabilizados, tests
  saltados o borrados). Se explica la diferencia en `baseline-pre-post.md`, no se redondea.
- Las dos cifras se declaran **en la misma base de medición** (R2.3): `pytest --collect-only` no es
  comparable con el conteo canónico `grep -rE "^\s*def test_" tests --include=*.py`.

**Verificador mecánico**: **todavía no existe.** `validate_plan_closure.py` vigila el cierre (R2.5)
y `validate_plan_citations.py` las citas (R2.2); ninguno valida la resta de este par. Mientras no
exista, la resta se hace a mano y se publica en `evidence/FASE-X/baseline-pre-post.md`. La escritura
del verificador queda como deuda con dueño: plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` (FASE-P1 la
incluye en alcance o la reasigna explícitamente).

### R2.8 — Todo AC de detección o de bloqueo se cierra con **mutation check**: sin el rojo no hay ✅ (D-T4B-A1 · NR7)

**Medido**: la fase T4-B de `TRIBUNAL-OFFLINE-2026-09-09` certificó ✅ con **7/7 tests verdes**, su
test de serialización y `run_all_validations.py --quick` en paz. Ninguna de las tres cosas observaba
el contrato de lectura: apuntado al baseline real del pipeline, `HonestyReviewer` devolvía
`propuesta cargada: False`, `total_cg_count: 0` y un veredicto `BLOQUEAR` espurio por
`MISSING_ARTIFACT`, porque `_load_proposal()` buscaba la propuesta dos niveles por encima de donde
el pipeline la escribe (decisión **D-T4B-A1**, remediada R1–R9). El mismo defecto está nombrado en
el corpus antes que ese plan: **L-T4A.5** —«un test puede pasar sin ejecutar la rama que dice
certificar»— y **L-VUP-5** —«una fase de extensión que no produce ni un rojo es un falso verde
potencial».

**Regla**: un AC que **detecta** o **bloquea** no se cierra con el test verde: se cierra
**revirtiendo el guard o la detección y mostrando el test en rojo**. La evidencia de la fase guarda
las **dos salidas** en `evidence/FASE-X/` — rojo con el guard desactivado, verde con el fix activo —
y sin el segundo lado el AC queda **⚠️, nunca ✅** (R2.4).

- La reversión se hace **por AC**, no una vez por fase, y sobre el **símbolo real** que guarda
  (`_is_template_stub()`, `gate_blocks_publication()`, el `except` del lector), no sobre un duplicado
  escrito dentro del test. L-T2C.4 midió que reactivar código muerto **sí** cambia el comportamiento
  de producción: el chequeo tampoco puede hacerse «fuera de la ruta de ejecución real».
- Un verde obtenido en la primera corrida, sin ningún rojo previo, se reporta como **sospechoso** y
  se explica; no como éxito.
- **Qué verifica**: que el verde sea causado por el guard. El rojo demuestra que, quitado el guard,
  el test falla; sin esa diferencia el test no certifica la detección, certifica su propio fixture.

**Verificador mecánico**: **todavía no existe; la regla nace sin él** (L-R.4, mismo precedente de
R2.7). Ningún check de `run_all_validations.py` ni del pre-commit comprueba que `evidence/FASE-X/`
contenga el par verde/rojo, así que hoy la sostiene solo la disciplina de quien cierra la fase.
Dueño de instrumentarlo: `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso, en el mismo tramo
que los verificadores pendientes de R2.6 y R2.7.

### R2.9 — Todo lector de artefactos expresa los **tres estados**: sin hallazgos / ausente / lector fallido (L-PF6 · L-PF10 · DA-C3 · NR8)

**Medido**: dos veces en un mismo plan, `SR-PIPELINE-FIXES-2026-08-27`. Primera (**L-PF6**): un
JSON-LD válido en formato ARRAY detonaba `AttributeError: 'list' object has no attribute 'get'` en
el parser, el caller lo tragaba como status ERROR y el audit lo publicaba como **«0 schemas»** — un
detector roto leído como ausencia real produjo un pain falso HIGH con cifra económica. Segunda
(**L-PF10**): corregido ese único critical issue, la corrida E2E final quedó bloqueada con
`critical_recall` BLOCKED «metric not found»: la lista estaba vacía **porque el fix había
funcionado**, pero el extractor devolvía `None` igual que cuando el dato no existe. La regla general
ya estaba decidida en `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` como **DA-C3** —*vacío ≠ ausente* como
contrato: `pain_ledger = []` (resuelto, 0 brechas) no colapsa con `None` (sin fuente → catálogo
estático legado)—, así que NR8 no es una norma nueva sino el ascenso de un contrato ya vigente a
todos los lectores.

**Regla**: cualquier código que lea un artefacto producido por otra etapa y reporte sobre él
(revisor, gate, extractor de métrica, audit) distingue y **publica** los tres estados de forma
legible para quien solo tiene el artefacto (R2.4):

| Estado | Lo que pasó | Lo que debe decir el artefacto |
|--------|-------------|--------------------------------|
| **sin hallazgos** | leyó y no encontró | que midió y sobre qué (`recall_basis`, `coverage_basis`) |
| **artefacto ausente** | no había nada que leer | qué ruta buscó |
| **lector fallido** | el lector no pudo operar | el motivo o la excepción — nunca un favorable ni un `0` |

- **Ningún camino los colapsa**: prohibido el `except` que devuelve el valor por defecto de «no
  encontrado», y prohibido un `None` que sirva a la vez para «vacío» y para «ausente».
- Se cierra con **tres tests nombrados por su causa**, uno por estado. Un test que cubre dos estados
  no prueba ninguno. Modelo ejecutable:
  `tests/quality_gates/test_coverage_gate_v5.py::TestV9LedgerVacio` (las combinaciones
  {fallback, resolved} × {vacío, ausente}).
- **Complementa a R2.6, no la sustituye**: R2.6 fija **dónde** se prueba un lector (contra el
  baseline real) y R2.9 fija **qué** tiene que poder decir. `MISSING_ARTIFACT` de D-T4B-A1 es el
  segundo estado dicho con la letra del tercero.
- **Qué verifica**: que «no hay problema» y «no pude mirar» no lleguen al cliente escritos igual.

**Verificador mecánico**: **todavía no existe; la regla nace sin él** (L-R.4). Un ✅ de la suite no
prueba la no-colisión: hace falta un caso por estado, y ningún check cuenta hoy que los tres existan
y se llamen por su causa. Dueño: el mismo tramo de deuda de `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`.

### R2.10 — Orden del cierre: **write-back → índice → `git mv`**; archivar antes desactiva los verificadores

**Medido** (leído en el código de los propios verificadores, 2026-09-12):

- `validate_qmind_writeback.py --upload <PLAN>` resuelve el plan como `.opencode/plans/<PLAN>`:
  después del `git mv` ese nombre ya no existe y hay que pasar `Archives/<PLAN>` con prefijo.
- Su modo verificación escanea **solo** `.opencode/plans/Archives/`. Un plan que aún vive en raíz es
  invisible para el check, así que archivar sin haber subido deja el hueco consumado y sin señal.
- `build_lesson_index.py --check` compara **byte a byte** y el índice publica el dueño de cada ID con
  su ruta: en la tabla vigente conviven `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` (definición
  archivada) y `9 en TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` (cita viva). Mover un plan cambia esas
  celdas, así que el índice regenerate de antes del `git mv` queda vencido contra el árbol final.
- **Y no vence solo por rutas.** La última columna del índice es el **conteo de citas por ID y por
  plan**, así que cualquier edición de un `.md` de `plans/` o `context/` que nombre un ID lo mueve.
  Medido al escribir la trazabilidad de NR7/NR8 en el plan que originó estas reglas: dos menciones
  nuevas en el §7 subieron `L-R.4` de 8 a 9 y `DA-C3` de 9 a 10, y `[6/6]` bloqueó ese commit.

**Regla**: dentro del cierre de FASE-RELEASE el orden es fijo y no se permuta:

```bash
python scripts/validate_qmind_writeback.py --upload <PLAN>   # 1. SIEMPRE con el plan aún en raíz
python scripts/build_lesson_index.py                          # 2. el plan cerrado, consultable
git mv .opencode/plans/<PLAN> .opencode/plans/Archives/       # 3. archivar, por último
python scripts/build_lesson_index.py                          # 3b. el índice congela la ruta NUEVA
```

- El paso **1** no admite excepción: es el único de los tres que deja de funcionar si se corre
  tarde, y su verificación solo mira `Archives/`.
- El paso **2** precede al archivado para que las lecciones del plan cerrado entren al corpus que
  consulta el Paso 0 del siguiente; el paso **3b** es obligatorio porque el `git mv` cambia rutas que
  el índice publica: **el `[6/6]` del pre-commit bloquea el commit de cierre** si se omite. El
  invariante verificable es «el índice refleja el árbol al commitear», no «una sola corrida».
- El bloque canónico de comandos del cierre sigue siendo el de R2.5; esta regla aporta el porqué del
  orden y qué se apaga si se invierte.
- **Fuera del cierre también alcanza, pero ya está verificado**: `[6/6]` corre en **todo** commit, así
  que un commit documental que edite un `.md` de `plans/` o `context/` lleva su índice regenerado
  **en el mismo commit**. No es una obligación nueva sino lo que el hook comprueba; se escribe aquí
  para que nadie lo descubra a mitad de un cierre, que fue el caso que lo midió.

**Origen no-lección**: R2.10 no desciende de un ID del corpus. Consolida una restricción que estaba
escrita en dos sitios sin nombre propio —el bloque de R2.5 y la nota «QMind y archivado» del §4— y
los cuatro hechos de arriba, leídos en el código de los verificadores el 2026-09-12 y confirmados por
`[6/6]` el mismo día: pasó el commit que solo tocaba el executor —ese directorio no se escanea— y
bloqueó el que editó un plan.

**Verificador mecánico**: **parcial, ya activo, con una pata que se degrada.**
- Pata del índice: **dura** — `[6/6]` del pre-commit (`build_lesson_index.py --check`) bloquea el
  commit con el índice vencido contra el árbol.
- Pata de QMind: **condicional** — solo corre en `run_all_validations.py` **completo** (check
  `[12/12]`, fuera de `--quick`) y degrada a WARN con salida 0 si el CLI `qmind` no está disponible;
  `--strict` es lo único que la vuelve fallida. En una máquina sin `qmind` esta pata no está
  verificada.
- Ninguno de los dos comprueba el **orden en el momento del `git mv`**: comprueban el resultado
  final. Ese hueco queda declarado, sin dueño asignado, y es el límite de esta regla.

## Regla de Scope de Fase (OBLIGATORIO — Al Crear el Plan)

> [!CAUTION]
> **R3: Una fase no puede contener mas de UN comando de larga duracion (v4complete, v4audit, scraping, etc.) NI mas de 4 tareas de investigacion/fix counting.**
>
> Si una fase requiere investigar+implementar+ejecutar+verificar+documentar, se DIVIDE en sub-fases: `FASE-X-A`, `FASE-X-B`, etc.

#### Como evaluar si una fase es demasiado grande

Al crear un prompt de fase, el orquestador debe responder:

```
TAREAS DE LA FASE:
  [ ] Investigacion de codigo existente
  [ ] Implementar fix / desarrollo nuevo
  [ ] Ejecutar comando de larga duracion (v4complete, v4audit, etc.)
  [ ] Verificar output del comando contra criterios
  [ ] Documentacion (log_phase + docs cascade)

CONTADOR:
  - Cada [ ] = 1 tarea
  - v4complete = 1 tarea + 1 comando largo
  - Total permitido por fase: maximo 4 tareas + 0 comandos largos
           O: maximo 3 tareas + 1 comando largo
```

#### Ejemplos de Division

| FASE demasiado grande | FASE bien acotada |
|------------------------|------------------|
| Investigar 5 hallazgos + Fix 5 hallazgos + v4complete + Verificar + Docs | FASE-X-A: Investigar + Fix |
| Fix 5 hallazgos + v4complete + Verificar 5 fixes + Docs | FASE-X-B: v4complete + Verificar |
| Implementar modulo + Testear + Integrar + v4audit + Docs | FASE-X-A: Implementar + Testear |
| | FASE-X-B: Integrar + v4audit |
| | FASE-X-C: Docs cascade |

#### Regla de Decision para el Orquestador

```
SI la fase tiene:
  - Mas de 4 tareas de investigacion/fix
  - O 1+ comando(s) de larga duracion (v4complete, etc.)
  - O combinacion de ambos que sume > 4 items de la lista

ENTONCES:
  → Dividir en FASE-X-A (investigacion/fix),
             FASE-X-B (ejecucion/verificacion),
             FASE-X-C (docs) segun corresponda
  → Cada sub-fase recibe su propio 05-prompt-inicio-sesion-fase-X-Y.md
  → Las sub-fases se ejecutan en sesiones separadas
```

#### Señales de Alerta al Planificar

- "Esta fase toma 2-3 horas" → probablemente necesita division
- "5 hallazgos para corregir" → dividir: A=investigacion, B=fixes, C=verificacion
- "Ejecutar v4complete y verificar los 5 hallazgos" → v4complete solo en su propia sub-fase
- "Docs cascade al final" → docs son su propia sub-fase

> [!WARNING]
> **El orquestador que crea fases demasiado grandes es responsable del agotamiento de las sesiones siguientes.** La regla R2 (§R2.1: presupuesto medido con el instrumento canónico) protege contra ejecución excesiva, pero la prevención empieza en el diseño del plan.

> [!TIP]
> **Convenciones de Nomenclatura de Fases**
>
> | Tipo | Formato | Ejemplo | Significado |
> |------|---------|---------|-------------|
> | Iteracion | `FASE-N` | `FASE-12` | Iteration de desarrollo |
> | Feature | `FASE-{LETRA}` | `FASE-A`, `FASE-B` | Sub-fase de un feature (A..Z) |
> | Verificación | `FASE-VERIFY` | `FASE-VERIFY` | Certificación ACs contra output E2E (condicional, §4.6) |
> | Release | `FASE-RELEASE-X.Y.Z` | `FASE-RELEASE-4.10.0` | Fase ejecutable de cierre + documentación (sesión propia) |
>
> **Regla:** Si la fase cambia la versión (nueva release), usar `FASE-RELEASE-X.Y.Z`.
> Esto activa automaticamente el Version Sync Gate.
>
> **Regla FASE-VERIFY:** Solo se incluye cuando el plan cumple los criterios de activación (§4.6). Si no aplica, las etapas son 3.

**Fases del workflow (3 o 4 etapas):**

| Etapa | Tipo de fase | Sesiones | Descripción |
|-------|-------------|----------|-------------|
| 1. Preparación | (orquestación) | 1 sesión | Crear todos los prompts, checklists, docs para todas las fases |
| 2. Implementación | `FASE-{N\|LETRA}` | N sesiones | Cada fase de código en su propia sesión nueva de agente |
| 2.5 Verificación | `FASE-VERIFY` | 1 sesión | Certificación formal de ACs contra output E2E (**condicional**, §4.6) |
| 3. Cierre / Release | `FASE-RELEASE-X.Y.Z` | 1 sesión | Documentación oficial, version bump, validaciones finales |

> **Nota**: La etapa 2.5 (FASE-VERIFY) solo se incluye cuando el plan cumple los criterios de activación (§4.6). Si no aplica, el workflow tiene 3 etapas.

**Regla de dependencia:** `FASE-RELEASE-X.Y.Z` solo se ejecuta cuando TODAS las fases previas (implementación + verificación, si aplica) están completadas (`✅`).

**Aplicación:**
- **Etapa 1 (Preparación):** En UNA sesión, Hermes (orquestador) genera todos los prompts de fase, incluyendo el de RELEASE
- **Etapa 2 (Implementación):** Cada fase requiere una sesión NUEVA del agente. El agente lee su `05-prompt-inicio-sesion-fase-{X}.md` y ejecuta las tareas de código
- **Etapa 2.5 (FASE-VERIFY, condicional):** Si el plan activa esta etapa (§4.6), una sesión NUEVA verifica formalmente que los criterios de aceptación se cumplen contra el output E2E real. No modifica código. Produce evidencia de certificación.
- **Etapa 3 (RELEASE):** Una sesión NUEVA del agente. El agente ejecuta `05-prompt-inicio-sesion-fase-RELEASE.md`. Tareas: version bump, sync, CHANGELOG, GUIA_TECNICA, validaciones, log. **NO modifica código fuente.**
- La sesión termina cuando el checklist de la fase muestra ✅ completo

## Modelo de Ejecución: Agentes AI

> [!IMPORTANT]
> **Este workflow es ejecutado por agentes AI** (Hermes, subagentes vía `delegate_task`), no por humanos.
>
> Cada prompt de fase (`05-prompt-inicio-sesion-fase-*.md`) es una **instrucción completa para un agente** en una sesión fresca. El agente:
> 1. Lee el prompt al inicio de la sesión
> 2. Planifica la ejecución de las tareas
> 3. Ejecuta — el modo de ejecución lo determinan las reglas de decisión más abajo:
>    - Código/tests puro → agente principal DIRECTO (§Regla código+tests)
>    - Comandos externos (v4complete, scraping) → §Regla v4complete
>    - Trabajo paralelo (2+ tracks) → subagentes vía `delegate_task`
>    - **NO usar subagente fuera de estos casos.**
> 4. Verifica criterios de completitud contra el checklist
> 5. Ejecuta `log_phase_completion.py` al finalizar, luego actualiza `09-documentacion-post-proyecto.md` con los datos de la fase
>
> **Implicaciones del modelo agente:**
> - Las "iteraciones" de R2 son **tool calls del agente** — no pasos humanos
> - El agente NO debe pedir confirmación para cada paso; el prompt es su mandato completo
> - Subagentes (`delegate_task`) pueden usarse para trabajo paralelo dentro de una fase, pero el total de iteraciones de la sesión no debe exceder 60
> - La fase termina cuando el checklist muestra ✅, no cuando "se acabó el tiempo"
> - **Orquestación**: La etapa de Preparación la ejecuta Hermes como orquestador. Las etapas de Implementación/RELEASE las ejecuta un agente nuevo en cada sesión.

### Regla de Iteraciones para Comandos de Larga Duración

> [!CAUTION]
> **GUIA CRITICA: presupuesto de iteraciones vs. comandos que duran minutos**
>
> `v4complete` es un comando que tarda 5-10 minutos en ejecutarse (scraping + APIs + generación de documentos + assets). Aunque `terminal(..., timeout=600)` cuenta como **1 tool call**, el comando consume tiempo real de pared, no tiempo de iteraciones del agente.
>
> **El agente debe planificar su presupuesto de iteraciones ANTES de invocar comandos largos.**

#### Calculo del Presupuesto de Iteraciones

```
Presupuesto total: el declarado por la fase (ver §R2.1: medido con
evidence/FASE-D/measure_iterations.py, cortado en el commit de codigo)

Gastos fijos por fase:
  - Leer plan y verificar estado previo: ~3 iteraciones
  - Investigar codigo/archivos: ~5-15 iteraciones
  - Ejecutar log_phase_completion.py + docs cascade: ~10 iteraciones
  - Actualizar plan al finalizar: ~5 iteraciones
  - run_all_validations.py: ~3 iteraciones
  Total fijo: ~26-36 iteraciones

Margen para trabajo especifico de la fase: 24-34 iteraciones
```

#### Regla de Desicion: ejecutar v4complete directamente o via subagente?

```
SI (investigacion + verificacion + docs) < 30 iteraciones restantes:
    → Ejecutar v4complete DIRECTAMENTE con terminal(timeout=600)
    → Usar notify_on_complete=True para no bloquear
    → Después de verificar output y hacer docs cascade

SI no:
    → Spawn subagent via delegate_task(timeout=900, notify_on_complete=True)
    → El subagent ejecuta v4complete completo
    → El agente parent usa sus iteraciones solo en verificacion + docs
```

#### Regla de Decisión: ejecutar código+tests directamente o vía subagente?

> [!IMPORTANT]
> **Para fases de implementación pura (investigación/fix/código/tests), la ejecución directa del agente principal es más eficiente que delegar a subagente.** El overhead de spawn (contexto, toolsets limitados, timeout) degrada fases que no tienen comandos de larga duración. Esta regla surgió del aprendizaje de FIN-3 (sesión 20260504_123434_49e7de): subagente agotado a 600s/37 tool calls para tareas que el agente principal habría completado en menos iteraciones sin overhead.

```
SI la fase tiene SOLO tareas de investigacion/fix/implementacion de codigo:
    → Ejecutar DIRECTAMENTE con el agente principal
    → Herramientas principales: terminal, file, execute_code
    → Budget: ~30-40 iteraciones para trabajo + ~20 para verificacion/docs
    → Este budget reemplaza el calculo generico de "Calculo del Presupuesto"
      (seccion anterior) — la ejecucion directa elimina el overhead de spawn

SI la fase requiere una decision arquitectonica cross-module que:
  - Afecta multiples consumidores en diferentes archivos
  - Implica elegir entre opciones de diseno no triviales (ej: unificar
    dos taxonomias vs crear un tercer sistema)
  - Requiere entender el contexto completo de ambas implementaciones
    → NO delegar a subagente. Ejecutar DIRECTAMENTE con el agente principal.
    → Un subagente carece del contexto completo para tomar decisiones
      arquitectonicas correctas.
    → Leccion: DT-3 FASE-2 (2026-07-25) — decision de unificar
      ProposalAssetMatrix + AlignmentReport en AssetAlignmentMatrix
      requeria entender ambas taxonomias + 4 consumidores.
    → Esta regla PREVALECE sobre cualquier consideracion de eficiencia:
      aunque la fase sea puro codigo (perfil delegable), si incluye
      una decision arquitectonica → directa.

SI la fase tiene 1+ comandos externos (v4complete, scraping, apis):
    → Regla de v4complete aplica (seccion anterior ↑)

SI la fase tiene trabajo paralelo independiente (2+ tracks separadas):
    → Subagente(s) para trabajo paralelo
    → Agente principal para coordinacion + docs

SI la fase requiere imports del proyecto (tests, integracion) Y el proyecto
   usa venv Windows accedido desde WSL:
    → Ejecutar DIRECTAMENTE con el agente principal
    → Invocar el Python del venv del proyecto via subprocess.run():
       ./venv/Scripts/python.exe -m pytest tests/...
    → NO delegar a subagentes: corren en WSL Linux sin acceso al venv
       Windows, imports como bs4/selenium fallan
    → Esta regla PREVALECE sobre la regla de trabajo paralelo (branch 3)
    → Causa raíz: subagente WSL no comparte el Python environment del
       venv Windows; los imports del proyecto fallan y el subagente
       consume iteraciones intentando resolver dependencias inexistentes
    → Lección: FASE-4 BUGS-ONBOARDING-ADR (2026-07-22) — subagente
       atascado en imports bs4/selenium, ~40 iteraciones perdidas

SI la fase documental (MD/YAML) requiere ademas editar UN script
   stdlib-only del proyecto (sin imports de modulos del proyecto, sin
   decisiones arquitectonicas — ej: añadir un check _check_* nuevo a
   scripts/run_all_validations.py):
    → Sigue siendo DELEGABLE a subagente (v2.14.0)
    → Criterio: el script solo usa stdlib (argparse/subprocess/pathlib/etc.)
      y el cambio replica un patron existente — no hay decision de diseño
    → El agente principal verifica el diff del script y ejecuta las
      validaciones (run_all_validations.py --quick) al integrar
    → Ejemplo real: FASE-E de RC1-RC2-ENTREGA-COHERENTE-2026-08-04
      (check "Prompts No Release" en run_all_validations.py)
```

#### Protocolo de Subagente para v4complete

Cuando se usa `delegate_task` para ejecutar `v4complete`:

```
1. En el context del subagente, incluir:
   - URL del hotel
   - Comando exacto: ./venv/Scripts/python.exe main.py v4complete --url {url}
   - Expected output: diagnostico, propuesta, assets, coherence >= 0.80

2. En el parent agent, usar:
   delegate_task(
     goal="Ejecutar v4complete para {hotel}...",
     context="...",
     timeout=900,  # 15 minutos — v4complete necesita 5-10 min
     notify_on_complete=True,
     toolsets=["terminal"]
   )

3. Cuando el subagente completa:
   → Parent agent verifica que los archivos existen
   → Agent generation_report y coherence_validation
   → Continua con docs cascade si todo OK
```

> [!WARNING]
> **NUNCA ejecutar `v4complete` sin `notify_on_complete=True` o sin subagente.**
> Si el agente parent se agota antes de que `v4complete` termine, el output
> se genera pero la verificacion/docs no se ejecutan — la fase queda incompleta.

#### Protocolo de Evidencia Proactiva (OBLIGATORIO)

> [!CAUTION]
> **Inmediatamente despues de que `v4complete` genera output**, antes de
> cualquier verificacion o investigacion adicional:
>
> 1. Copiar los archivos criticos a `evidence/{fase-id}/`:
>    ```bash
>    mkdir -p evidence/{fase-id}
>    cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/{fase-id}/
>    cp output/v4_complete/02_PROPUESTA_*.md evidence/{fase-id}/
>    cp output/v4_complete/{hotel_id}/v4_audit/*.json evidence/{fase-id}/
>    ```
> 2. **Esto es OBLIGATORIO sin importar cuanto tiempo quede en el presupuesto de iteraciones.**
>    Si el agente se agota despues, la evidencia ya esta a salvo para la siguiente sesion.
> 3. Solo despues de guardar evidencia, continuar con verificacion/docs cascade.

### Cierre Obligatorio de Sesion (SIEMPRE — aunque la fase no haya completado)

> [!IMPORTANT]
> **Al terminar la sesion (completada o no), SIEMPRE ejecutar en orden:**
>
> 1. **Guardar evidencia** (si hay output de v4complete): ejecutar el bloque bash del **Protocolo de Evidencia Proactiva** (seccion anterior §Protocolo-Evidencia-Proactiva)
> 2. **Actualizar el plan de fase** con estado real:
>    - Si completo: marcar todos los items del checklist como ✅
>    - Si incompleto: marcar como `⏳ INCOMPLETA` con checkpoint y que falta
> 3. **Preguntar por el aporte durable de todo `CONTEXT-*.md` escrito o editado en la sesion** (criterio y write-back en §4): ¿contiene una leccion de forma o de metodo que cambie como trabajara una sesion futura?
>    - Si → etiquetarla en el propio archivo (`Leccion de forma:`) y ejecutar el write-back: `python scripts/validate_qmind_writeback.py --upload <PLAN>` (sube 10-analisis + CONTEXT con declaración durable al notebook `iah-cli-lecciones`).
>    - No → no se etiqueta y no se ingiere; el archivo queda solo en el repo como estado de plan o medicion. No hace falta declarar la ausencia.
> 4. **Solo entonces** cerrar la sesion.

**Esta regla no tiene excepciones.** Aunque la sesion termine en iteracion 1 y no haya hecho nada, el plan debe reflejar ese estado.

### Recuperacion de Agotamiento (presupuesto de la fase agotado o timeout de subagente)

Cuando la fase no completa por agotamiento:

```
1. Actualizar el plan de fase (.opencode/plans/05-prompt-inicio-sesion-fase-X.md):
   - Estado: "⏳ INCOMPLETA — agotamiento en iteracion Y"
   - Ultimo checkpoint: describir que se habia completado
   - Que falta: enumerar tareas pendientes
   - Timestamp de la sesion

2. Guardar evidencia en evidence/{fase-id}/:
   - Copiar cualquier output generado hasta el momento
   - Copiar diagnosticos/propuestas/JSONs aunque esten incompletos

3. Nueva sesion:
   - Leer estado desde el plan actualizado
   - Continuar desde el checkpoint
   - NO re-ejecutar lo que ya se ejecuto correctamente
```

#### Síntomas de Agotamiento de Subagente

| Sintoma | Causa | Accion |
|---------|-------|--------|
| Subagente retorna sin output | Timeout 600s insuficiente | Re-spawn con delegate_task y timeout=900 |
| v4complete nunca termina de generar | API rate limits / network | Verificar logs, retry con backoff |
| Agent parent agota el presupuesto de la fase antes de v4complete | Presupuesto mal calculado | Dividir: subagente para v4complete |
| Docs cascade no se ejecuta post-v4complete | Agent se agoto al final | Guardar evidencia ANTES, docs en sesion separada |

## Pre-requisitos
- [ ] Proyecto con división clara en fases/sprints/etapas
- [ ] Estructura de directorio `.opencode/plans/` o similar
- [ ] Criterios de aceptación definidos por fase

## Pasos de Ejecución

### 0. Recuperación de Lecciones Aprendidas (OBLIGATORIO — antes de planificar)

> [!IMPORTANT]
> Ningún plan se redacta desde cero: la experiencia de planes anteriores vive en tres capas y DEBE consultarse antes de diseñar fases, prompts o CONTEXT. El output **no es una lectura mental**: es un archivo del plan, `00-lecciones-capitalizadas.md`, creado antes del plan maestro.

**Capa caliente — memoria del proyecto** (siempre disponible):
- Leer el índice `MEMORY.md` de la memoria de proyecto del agente y las entradas relevantes al tema del plan (pitfalls, convenciones de cierre de fase, decisiones resueltas).

**Capa tibia — QMind** (si el notebook está disponible):
- `retrieve` sobre el notebook `iah-cli-lecciones` con el tema/objetivo del plan como query (2-3 queries acotadas: módulo afectado, tipo de fallo, etapa del workflow).
- Corpus del notebook: `CONTEXT-*.md` (`.opencode/context/`) y `10-analisis-post-implementacion.md` de cada plan. Un CONTEXT entra al corpus **solo si autodeclara un aporte durable** (criterio binario en el write-back del paso 4); si no lo declara, es estado de plan o medición y se recupera del repo, no de QMind. Que un CONTEXT no esté en el notebook no es un olvido: o no declaró aporte, o la sesión que lo escribió incumplió el Cierre Obligatorio.

**Capa fría — índice generado del corpus** (`.opencode/LECCIONES-INDEX.md`):
- `grep`-ear el índice por módulo afectado, síntoma o palabra clave es la forma barata de mirar el corpus **completo** (todos los IDs definidos en análisis y `CONTEXT-*.md`, con su dueño y sus citas — el conteo vigente está en el encabezado del índice) en vez de consultar solo al plan predecesor.
- Se regenera con `python scripts/build_lesson_index.py`; el pre-commit lo verifica con `--check` (check `[6/6]` del hook versionado en `scripts/git_hooks/pre-commit`, instalar con `python scripts/install_git_hooks.py`). Si no existe o está vencido, **generarlo antes de consultar**.
- Es un índice, no un juicio: dice qué existe y dónde está escrito; si una lección aplica, lo decide quien redacta el plan y lo registra en §2 del archivo.

**Output del paso** — `00-lecciones-capitalizadas.md`, creado con el template
`.agents/workflows/templates/lecciones-capitalizadas-template.md` **antes** de `01-plan-maestro.md`:

1. **§1 Consultas literales** re-ejecutables (comando o términos exactos). ≥1 dirigida al corpus completo, no solo al predecesor.
2. **§2 Lecciones capitalizadas**, cada una con su ID, la ruta donde está definida y un **"qué cambia en este plan"** que nombra un AC, una tarea, un archivo o una restricción. Una fila sin efecto concreto citó pero no capitalizó.
3. **§3 Candidatos descartados** (mínimo 3, con motivo): la única prueba de que se miró el corpus.
4. **§4 Cobertura declarada**: si existe o no verificador mecánico sobre este archivo.

Las lecciones de §2 se inyectan en el contexto de los prompts de fase (§2 del executor) donde sean pertinentes, y en el `CONTEXT-*.md` del plan si el plan genera contexto. El archivo se **actualiza al cierre de cada fase**, no solo al inicio.

> [!WARNING]
> **Por qué ahora es un archivo y no una instrucción.** Hasta v2.21.0 el Paso 0 ordenaba producir la tabla, pero su destino era una sección de `10-analisis-post-implementacion.md` marcada `(si aplica)`. Medido sobre los 24 planes archivados: la sección aparece en **6** (18 %). Y el plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` citaba únicamente a su predecesor teniendo 24 planes más en el corpus, con un defecto ya documentado desde `EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31`. Es L-R.1 en su forma exacta: una regla que vive solo en el workflow y no en el artefacto que la fase rellena, se cumple por coincidencia.

**Fallback**: si el notebook QMind no existe o no es accesible, continuar con la memoria del proyecto y el índice generado, y registrar la limitación en `00-lecciones-capitalizadas.md` §4 y en `dependencias-fases.md`.

### 1. Analizar Plan y Detectar Conflictos
Leer el plan maestro:
- Número de fases/sprints
- Dependencias entre fases
- Entregables por fase
- **Conflictos de archivos** (qué archivo modifica cada fase)

**Output**: `dependencias-fases.md`
- Diagrama ASCII de dependencias
- Tabla de conflictos potenciales

### 2. Crear Prompts por Fase
Para cada fase, crear `.opencode/plans/05-prompt-inicio-sesion-fase-{N}.md`

Usar template `.agents/workflows/templates/prompt-fase-template.md`

**Obligatorio en cada prompt (segun CONTRIBUTING §Flujo-Post-Fase):**
- Contexto de fases anteriores
- **Lecciones capitalizadas del Paso 0** que apliquen a esta fase (solo las pertinentes, no el corpus completo), **copiadas de las filas de `00-lecciones-capitalizadas.md` §2** con su ID: el prompt no inventa su lista de lecciones
- Tareas específicas de la fase
- Seccion de documentacion post-fase (editar CHANGELOG, GUIA_TECNICA, y acumular en 09-documentacion-post-proyecto.md)
- **Post-Ejecución** (marcar checklist, actualizar estados)
- **Criterios de Completitud**
- **Restricciones** (mínimo: presupuesto de iteraciones declarado + instrumento y corte con que se mide, §R2.1; según la fase: no modificar ROADMAP.md, no ejecutar v4complete, etc.)

**Verificación:**
- [ ] Nombre de archivo coincide con título interno
- [ ] Referencias a fases previas con números correctos
- [ ] Tests base acumulativos correctos

### 2.5. Verificación Pre-Creación de Prompts (OBLIGATORIO — Anti-Deuda Acumulativa)

> [!CAUTION]
> **REGLA CRÍTICA**: Antes de crear/codificar los prompts de fase, el orquestador DEBE verificar que cada fase incluye `log_phase_completion.py` al final de su ejecución. NO delegar esto a FASE-RELEASE.

**Checklist de verificación obligatoria:**

```
□ FASE-1 a FASE-N (impl): Cada prompt termina con:
    ./venv/Scripts/python.exe scripts/log_phase_completion.py \
        --fase FASE-X --desc "..." \
        --archivos-mod "..." --tests "N" --check-manual-docs

□ FASE-RELEASE: NO registra fases anteriores. Solo sincroniza y valida.

□ Si el plan muestra T1 de FASE-RELEASE = "registrar FASE-1 a FASE-5" → ERROR.
  Las fases 1-5 DEBEN registrarse a sí mismas al completar.

□ Si no existe prompt-fase-template.md → crear uno antes de planificar fases.

□ Si 00-lecciones-capitalizadas.md NO existe, o su §2 no tiene ninguna fila con "qué
  cambia" que nombre un AC/tarea/archivo → NO crear prompts de fase. Primero se
  capitaliza, después se diseña la fase.
```

**Error típico que este paso previene:**

```
Planificador diseña desde cero, sin leer el corpus:
  FASE-1: T1=investigar, T2=fix, T3=tests
  ...
  y redescubre a mitad de camino una lección ya escrita en otro plan.

Resultado: reproceso + un error ya superado vuelve a entrar al pipeline.
```

```
Planificador diseña:
  FASE-1: T1=investigar, T2=fix, T3=tests
  FASE-2: T1=investigar, T2=fix, T3=tests
  FASE-RELEASE: T1=registrar FASE-1, T2=registrar FASE-2, ..., T5=registrar FASE-5, T6=version bump

Resultado: Deuda de 5 registros acumulada en RELEASE.
          Si RELEASE falla, las fases quedan "completadas" sin registro.
```

**Acción correctiva si se detecta el error:**

```
Si el plan tiene "T1 de FASE-RELEASE = registrar FASE-1 a FASE-5":
  → Reestructurar: Cada fase de implementación ejecuta log_phase_completion.py al terminar.
  → FASE-RELEASE solo hace: sync_versions, CHANGELOG, GUIA_TECNICA, validaciones.
  → Regenerar los prompts de fase con la sección post-ejecución incluida.
```

### 3. Actualizar Checklist Maestro
Actualizar `.opencode/plans/06-checklist-implementacion.md`:
- Estado de cada fase (pendiente/en progreso/completada)
- Dependencias entre fases

### 4. Documentación Incremental
**Estrategia**: Documentar durante todo el proyecto, no solo al final.

**Al inicio del proyecto**: Crear los TRES archivos. `00-…` llega **lleno** del Paso 0 (no se
crea vacío); los otros dos se crean con estructura vacía:
- `.opencode/plans/00-lecciones-capitalizadas.md` (output del Paso 0; template propio, ver §0)
- `.opencode/plans/09-documentacion-post-proyecto.md` (métricas y archivos por fase)
- `.opencode/plans/10-analisis-post-implementacion.md` (lecciones aprendidas, decisiones, matriz de verificación)

> [!IMPORTANT]
> **El análisis post-implementación se crea DESDE LA CONCEPCIÓN del plan**, no al final.
> Esto evita el reproceso de crearlo después de que las lecciones ya se perdieron.
> Estructura: ver ejemplo real en `COHERENCIA-MODULO-ENTREGA-2026-08-03/10-analisis-post-implementacion.md`.

**Después de cada fase completada**, editar directamente CHANGELOG.md y GUIA_TECNICA.md con los cambios de esa fase (segun template §6). La acumulacion en 09-documentacion-post-proyecto.md es un backup de datos para FASE-RELEASE:

- Sección A: Módulos nuevos
- Sección B: Funcionalidades nuevas
- Sección D: Métricas acumulativas
- Sección E: Archivos afiliados actualizados

**Y actualizar `10-analisis-post-implementacion.md`** con los datos de la fase:
- Resumen de Ejecución (tabla de fases)
- Lecciones Aprendidas nuevas (formato: qué pasó / por qué / qué lo previene)
- Métricas de Ejecución (tests, coherencia, etc.)
- Seguimientos abiertos detectados

**Write-back de lecciones (al cierre de cada fase)** — cierra el ciclo del Paso 0:
- Cada lección nueva con pertinencia INCLUIR se persiste en la **memoria del proyecto** del agente (una entrada durable por lección).
- El `10-analisis-post-implementacion.md` actualizado se re-ingere al notebook **`iah-cli-lecciones`** de QMind vía el script automatizado:
  ```bash
  python scripts/validate_qmind_writeback.py --upload <NOMBRE_DEL_PLAN>
  ```
  El script sube el 10-analisis y cualquier `CONTEXT-*.md` con declaración durable, detecta si ya está ingestado (evita duplicados, ver :584), y retorna código 1 si la subida falla. **Reemplaza el `add_source` manual del MCP** (que depende del scope del agente, históricamente frágil).
- El **índice del corpus** se regenera en el mismo ciclo, con el write-back ya ejecutado:
  ```bash
  python scripts/build_lesson_index.py
  ```
  Sin este paso las lecciones del plan recién cerrado no son consultables por el siguiente
  plan (el Paso 0 consulta el índice). El pre-commit lo verifica con `--check`.
- Lecciones con pertinencia EXCLUIR quedan solo en el análisis del plan.

**Write-back de CONTEXT (disparador por aporte, NO por edición)** — los `CONTEXT-*.md` de `.opencode/context/` no se ingieren por existir ni por editarse. Se ingieren cuando **autodeclaran un aporte durable**.

- **Criterio binario (sin juicio de relevancia):** ¿el archivo etiqueta explícitamente una lección de forma o de método — `Lección de forma:`, `Lección durable:`, o una sección `Lecciones capitalizadas`? Sí → ingerir. No → se queda solo en el repo.
  - Ejemplo real: `CONTEXT-AUDITORIA-BRECHAS-VS-MODULOS-SALENTOREAL-2026-09-03.md` §9.5 — *"Lección de forma: en este pipeline, revalidar citas de código no revalida premisas. Todo hallazgo está anclado a un artefacto o a una corrida, no a una lectura."* Ese aporte cambia cómo trabaja cualquier sesión futura ⟹ se ingiere. Las tablas de medición del mismo archivo no cambian cómo se trabaja ⟹ no son, por sí solas, motivo de ingesta. (La lección nació como §13.5 de `CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` y migró al dossier el 2026-09-03.)
- **Por qué autodeclarado y no inferido:** la relevancia la decide quien escribe el contexto, en el momento en que tiene la evidencia delante. Un agente futuro tendría que inferirla, y ese juicio subjetivo es exactamente lo que volvió letra muerta la sección "Lecciones capitalizadas" antes de v2.17.0. Declarar es además la única forma de que el disparador sea verificable.
- **Si declara, dos acciones (mismo ciclo que el 10-analisis):** (1) persistir la lección como entrada durable en la **memoria del proyecto**; (2) ejecutar `python scripts/validate_qmind_writeback.py --upload <PLAN>` — el script detecta automáticamente los CONTEXT con declaración durable y los sube al notebook `iah-cli-lecciones` (junto con el 10-analisis del plan).
- **Si no declara:** nada. El contenido es estado de plan, decisión pendiente o medición, y vive en el repo. No ingerirlo no es perderlo.
- **Re-ingesta:** solo cuando cambia el aporte declarado, no cuando cambian las secciones de estado o medición. El MCP no tiene `delete_source`: cada re-ingesta acumula una versión previa en el notebook, así que ingerir de más es ruido permanente.
- **Dónde se declara:** en el Cierre Obligatorio de Sesión (ver §Cierre-Obligatorio-de-Sesion). La declaración es parte del cierre, no un paso opcional posterior.

> [!NOTE]
> **QMind y archivado**: QMind indexa snapshots de contenido, no rutas locales. Mover un plan a `Archives/` o un contexto a `Historico/` NO requiere acción en QMind (solo actualizar referencias en repo/memoria). Re-ingerir SOLO cuando cambia el contenido. Orden correcto: write-back final → `python scripts/build_lesson_index.py` → archivar el directorio → **regenerar el índice otra vez** (publica el plan dueño con su ruta, así que el `git mv` lo vence; R2.10) → el contenido archivado queda congelado y no necesita mantenimiento.

**Estructura concreta de 09-documentacion-post-proyecto.md:**

```markdown
# Documentación Post-Proyecto

## Sección A: Módulos Nuevos
| Módulo | Archivos | Descripción | Fase |

## Sección B: Funcionalidades Nuevas
| Feature | Módulo | Descripción | Fase |

## Sección D: Métricas Acumulativas
| Métrica | Valor | Fase |

## Sección E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
```

Cada fase completa su columna "Fase". FASE-RELEASE usa los datos acumulados para generar CHANGELOG y GUIA_TECNICA oficiales.

**Estructura concreta de 10-analisis-post-implementacion.md:**

```markdown
# Análisis Post-Implementación — [ID DEL PLAN]

> **Estado**: [Fase actual completada] — [resumen breve]
> **Plan**: [ID del plan]
> **Versión objetivo**: [X.Y.Z]

## Resumen de Ejecución (llenar al cierre de cada fase)
| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY si aplica; si no, al cierre de última fase impl)
| # | Hallazgo | Expected | Real | Status |

## Lecciones Aprendidas (llenar — mínimo 3 por fase completada)
Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR)

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)
| Lección | Aplicación en este plan |
<!-- No se re-decide aqui: se copia del archivo 00 y se anota que paso realmente en cada fase. -->

### Lecciones nuevas de este plan (L16+ si continúa numeración previa)

## Seguimientos abiertos (llenar conforme avancen las fases)
| Tema | Estado | Acción futura |

## Métricas de Ejecución (llenar al cierre)

## Decisiones Arquitectónicas (llenar cuando aplique)
| ID | Decisión | Rationale | Alternativas rechazadas | Fase |

## Checklist de Cierre (llenar en FASE-RELEASE)
```

---

### 4.5. Ejecución de Plan de Documentación (OBLIGATORIO)

> [!CAUTION]
> **REGLA MANDATORIA**: Cuando se ejecute un plan de documentación (como `09-documentacion-post-proyecto.md`), SE DEBE seguir este procedimiento. NO ejecutar el plan directamente sin estas validaciones.

#### Flujo de Ejecución

```
Plan de documentación (09-documentacion-post-proyecto.md)
    │
    ├── Paso 4.5.1: Ejecutar log_phase_completion.py por cada fase
    │   └── Registrar en REGISTRY.md (automático)
    │
    ├── Paso 4.5.2: Ejecutar sync_versions.py
    │   └── Sincronizar VERSION.yaml → 6 archivos
    │
    ├── Paso 4.5.3: Validar CHANGELOG.md formato
    │   └── Verificar secciones requeridas por CONTRIBUTING.md
    │
    ├── Paso 4.5.4: Validar GUIA_TECNICA.md
    │   └── Verificar notas técnicas por fase
    │
    ├── Paso 4.5.5: Validación final
    │   └── run_all_validations.py --quick
    │
    ├── Paso 4.5.6: Write-back QMind (automatizado)
    │   └── python scripts/validate_qmind_writeback.py --upload <PLAN>
    │
    └── Paso 4.5.7: Archivar el plan (R2.5)
        └── git mv a plans/Archives/ + refs --fix + citas --update-baseline + --quick (mismo commit)
```

#### Paso 4.5.1: Registrar Fases en REGISTRY.md

Para cada fase mencionada en el plan, ejecutar:

```bash
# Ejemplo: Registrar FASE-GEO-BRIDGE
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-GEO-BRIDGE \
    --desc "Bridge enrichment geo_enriched → delivery" \
    --archivos-nuevos "modules/asset_generation/geo_enriched_bridge.py,tests/asset_generation/test_geo_enriched_bridge.py" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py" \
    --tests "13" \
    --check-manual-docs
```

**Regla**: Ejecutar UNA vez por cada fase documentada en el plan.

#### Paso 4.5.2: Sincronizar Versiones

```bash
# Sincronizar VERSION.yaml → AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md
./venv/Scripts/python.exe scripts/sync_versions.py

# Verificar sincronización
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

#### Paso 4.5.3: Validar CHANGELOG.md

Verificar que la entrada de CHANGELOG tenga el formato requerido por `docs/CONTRIBUTING.md §Verificar-CHANGELOG`:

```markdown
## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD

### Objetivo
{Descripcion breve del cambio}

### Cambios Implementados
- Descripción de cambios realizados

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|

### Tests
- N tests nuevos, 0 regresiones
```

**Checklist CHANGELOG:**
- [ ] Entrada `[X.Y.Z]` existe
- [ ] Tiene sección `### Objetivo`
- [ ] Tiene sección `### Cambios Implementados`
- [ ] Tiene sección `### Archivos Nuevos` (si aplica)
- [ ] Tiene sección `### Archivos Modificados` (si aplica)
- [ ] Tiene sección `### Tests`
- [ ] No hay entradas duplicadas

#### Paso 4.5.4: Validar GUIA_TECNICA.md

Verificar que `docs/GUIA_TECNICA.md` tenga nota técnica para cada fase:

**Checklist GUIA_TECNICA:**
- [ ] Cada fase tiene una sección "Notas de Cambios vX.Y.Z"
- [ ] Incluye módulos afectados
- [ ] Incluye problema/solución
- [ ] Incluye backwards compatibility
- [ ] Incluye tests (si aplica)

#### Paso 4.5.5: Validación Final

```bash
# Ejecutar todas las validaciones
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Verificar estado del sistema
./venv/Scripts/python.exe scripts/doctor.py --status

# Regenerar DOMAIN_PRIMER (al cerrar cada fase de implementacion)
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer

# Verificar DOMAIN_PRIMER (context check, solo en FASE-RELEASE)
./venv/Scripts/python.exe scripts/doctor.py --context
```

**Checklist Final:**
- [ ] `run_all_validations.py --quick` pasa (TOTAL PASS — conteo dinámico del script, NO fijar "4/4": el nº de checks cambia al añadir validaciones nuevas, ej. "Prompts No Release")
- [ ] `doctor.py --status` ejecutado sin errores
- [ ] `version_consistency_checker.py` pasa
- [ ] `sync_versions.py` ejecutado
- [ ] Todos los archivos de documentación actualizados

#### Paso 4.5.6: Write-back QMind (automatizado)

> [!IMPORTANT]
> **Obligatorio antes de archivar.** El script sube el `10-analisis-post-implementacion.md` del plan
> y cualquier `CONTEXT-*.md` con declaración durable al notebook `iah-cli-lecciones` de QMind.
> Usa el CLI `qmind` (plano local), no el plugin MCP (cuyo scope puede excluir el notebook).

```bash
# Write-back: sube 10-analisis + CONTEXT con declaración durable
python scripts/validate_qmind_writeback.py --upload <NOMBRE_DEL_PLAN>

# Verificar que todo plan archivado está ingestado
python scripts/validate_qmind_writeback.py --strict
```

**Comportamiento del script:**
- **Idempotente**: si el 10-analisis ya está ingestado (match por título), hace skip — evita duplicados permanentes (QMind no tiene `delete_source`).
- **CONTEXT con declaración durable**: escanea `.opencode/context/CONTEXT-*.md` buscando marcadores `Lección de forma:`, `Lección durable:`, o `Lecciones capitalizadas`. Solo sube los que declaran.
- **Código de salida 1**: si la subida falla o qmind no está disponible (en modo `--strict`).
- **Código de salida 0**: write-back exitoso o skip por idempotencia.

**Checklist Write-back:**
- [ ] `validate_qmind_writeback.py --upload <PLAN>` retorna 0
- [ ] `validate_qmind_writeback.py --strict` confirma N/N archivados ingeridos

#### Ejemplo Completo de Ejecución

```bash
# 1. Registrar cada fase del plan
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-GEO-BRIDGE --desc "..." --check-manual-docs
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-CONF-GATE --desc "..." --check-manual-docs
# ... repetir para cada fase

# 2. Sincronizar versiones
./venv/Scripts/python.exe scripts/sync_versions.py

# 3. Verificar consistencia
./venv/Scripts/python.exe scripts/version_consistency_checker.py

# 4. Validar documentación manual
# Verificar CHANGELOG.md tiene formato correcto
# Verificar GUIA_TECNICA.md tiene notas técnicas

# 5. Validación final
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
./venv/Scripts/python.exe scripts/doctor.py --status
```

#### Checklist de Completitud del Plan de Documentación

Después de ejecutar el plan, verificar:

| Verificación | Comando | Estado |
|--------------|---------|--------|
| Fases registradas en REGISTRY.md | `grep "## FASE-" docs/contributing/REGISTRY.md` | [ ] |
| Versiones sincronizadas | `scripts/sync_versions.py` | [ ] |
| CHANGELOG formato correcto | Manual: verificar secciones | [ ] |
| GUIA_TECNICA actualizada | Manual: verificar notas técnicas | [ ] |
| Validaciones pasan | `scripts/run_all_validations.py --quick` | [ ] |
| Doctor sin errores | `scripts/doctor.py --status` | [ ] |

---

### 4.6. FASE-VERIFY — Certificación Formal de ACs (CONDICIONAL)

> [!IMPORTANT]
> **Etapa condicional**: Solo se incluye cuando el plan cumple los criterios de activación. Si no aplica, el workflow tiene 3 etapas (Preparación → Implementación → RELEASE).

#### Criterios de Activación

El orquestador DEBE incluir `FASE-VERIFY` cuando **TODOS** estos criterios se cumplen:

```
INCLUIR FASE-VERIFY cuando:
  1. El plan tiene ≥3 fases de implementación (complejidad suficiente)
  2. Existe al menos una fase con ejecución E2E (v4complete, v4audit, etc.)
  3. Hay criterios de aceptación (ACs) que cruzan múltiples fases
     (no verificables completamente en una sola fase de implementación)

NO INCLUIR cuando:
  - Plan de 1-2 fases con ACs autocontenidos en cada fase
  - No hay ejecución E2E (puro refactor unitario o documental)
  - Plan sin criterios de aceptación formales
```

#### Propósito

FASE-VERIFY es una fase de **verificación sin código**: certifica formalmente que los criterios de aceptación del plan se cumplen contra el output E2E real generado en las fases de implementación. No modifica código fuente ni templates.

> **Diferencia con las verificaciones de cada fase**: cada fase de implementación verifica sus propios criterios locales (tests pasan, greps limpios). FASE-VERIFY verifica la **integración coherente de todos los cambios** en el output renderizado final.

#### Metodología Mínima (generalizable)

| Paso | Acción | Entregable |
|------|--------|------------|
| 1 | Leer output post-fix y baseline (si existe) | Contexto para comparación |
| 2 | Verificar cada AC contra output real (no solo unit tests) | Columna "Real" de la matriz completada |
| 3 | Comparar antes/después (si hay baseline) | Diff narrativo/técnico documentado |
| 4 | Greps residuales de strings que deberían haber desaparecido | Tabla de patrones con 0 matches |
| 5 | Completar matriz de verificación del `10-analisis` | Todas las filas con Real/Status |
| 6 | Registrar lecciones aprendidas de la verificación | Mínimo 3 lecciones nuevas |
| 7 | Ejecutar `log_phase_completion.py` (SIN `--release`) + `run_all_validations.py --quick` | Registro + validación |

#### Reglas Específicas

- **Modo de ejecución**: DIRECTO (agente principal). No delegable — requiere juicio y contexto completo del plan.
- **NO modifica código**: si un AC falla, se documenta en "Seguimientos abiertos" y se planifica sesión de recuperación separada.
- **NO ejecuta `v4complete`**: la ejecución E2E ya ocurrió en una fase de implementación previa.
- **Dependencia**: requiere todas las fases de implementación ✅.
- **FASE-RELEASE requiere**: FASE-VERIFY ✅ (cuando aplique).

#### Estructura del Prompt (`05-prompt-inicio-sesion-fase-VERIFY.md`)

El prompt de FASE-VERIFY debe incluir:
- Lista de ACs con método de verificación (lectura directa, grep, comparación JSON, etc.)
- Rutas a baseline y output post-fix
- Tabla de diff antes/después (zonas a verificar)
- Restricción: NO modificar código, NO ejecutar v4complete
- Post-ejecución: documentación estándar + actualización de `10-analisis-post-implementacion.md`

#### Ejemplo de Plan con/sin FASE-VERIFY

| Plan | Fases impl | E2E | ACs cross-fase | ¿Incluye FASE-VERIFY? |
|------|-----------|-----|----------------|----------------------|
| REFACTOR-COHERENCIA-NARRATIVA (7 fases) | 5 (A-E) | SÍ (R0-E) | SÍ (AC1-AC12 cruzan A-D) | SÍ |
| BUGS-ONBOARDING-ADR (4 fases) | 3 | SÍ | Parcial | Opcional |
| Fix unitario (1-2 fases) | 1-2 | NO | NO | NO |

> **Lección origen**: FASE-R0-F del plan REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 demostró que la verificación formal con diff antes/después detecta incoherencias transversales que los tests unitarios individuales no capturan (título S4=7 ↔ listado=7 ↔ intro=7 ↔ contador S6=7 ↔ pain_ledger=7).

---

### 5. Validación Final de Preparación
Antes de cerrar la sesión de preparación:

```bash
# Verificar numeración de prompts
grep -n "FASE [0-9]" .opencode/plans/05-prompt-inicio-sesion-fase-*.md

# Verificar que todos los archivos de plan existen
ls -la .opencode/plans/
```

**Checklist:**
- [ ] Prompts creados para TODAS las fases
- [ ] Numeración correcta verificada
- [ ] `dependencias-fases.md` generado
- [ ] Checklist maestro actualizado
- [ ] Documentación base creada
- [ ] Sprints sincronizados (si existen)

### 6. Documentación Post-Fase (OBLIGATORIO - Según CONTRIBUTING.md)

---

#### DONDE: Ubicación en el Workflow

```
FASE completada (checklist muestra ✅)
    │
    └── Paso 6: Documentación Post-Fase ← AQUÍ
               │
               └─→ Ejecutar log_phase_completion.py
```

---

#### CUANDO: Cuándo se Activa

**INMEDIATAMENTE** después de que la fase se considera completa:
- Checklist de la fase muestra ✅ en todos los items
- Tests pasan (si aplica)
- No hay errores pendientes

**NO esperar** a la siguiente sesión. Ejecutar en la misma sesión donde se completó la fase.

---

#### COMO: Comandos Exactos

**Caso 1: Fase de iteración (FASE-N, FASE-A, etc.)**

```bash
# Minimo (registra en REGISTRY nomas)
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-12 --desc "Descripcion"
```

```bash
# Recomendado (con verificacion de docs manuales)
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-12 \
    --desc "Google Travel Scraper integration" \
    --archivos-nuevos "modules/scrapers/google_travel.py,tests/scrapers/test_google_travel.py" \
    --archivos-mod "modules/providers/benchmark_resolver.py" \
    --tests "15" \
    --coherence 0.91 \
    --check-manual-docs
```

**Caso 2: Fase de RELEASE (FASE-RELEASE-X.Y.Z)**

```bash
# Convencion: FASE-RELEASE-4.10.0 = release marker
# El script detecta automaticamente que es un release

./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-RELEASE-4.10.0 \
    --desc "Release 4.10.0" \
    --archivos-mod "modules/foo.py" \
    --check-manual-docs

# Verificar consistency antes de commit:
./venv/Scripts/python.exe scripts/version_consistency_checker.py
```

**Caso 3: Forzar skip (excepciones)**

```bash
# Solo si hay razon valida: no-aplica, en-release-posterior, etc.
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-X --desc "..." \
    --check-manual-docs --force-skip-docs --skip-reason "no-aplica"
```

---

#### QUE HACE: Salida del Script

```
1. Registra en REGISTRY.md (automatico)
2. Muestra POR_HACER para documentacion manual
3. DOCUMENTATION AUDIT (automatico si hay --archivos-mod)
4. Version Sync Gate (automatico si fase es FASE-RELEASE-X.Y.Z)
5. Checklist final en pantalla
```

---

#### VERSION SYNC GATE: Como Saber si Fallo

```
[VERSION GATE] Release: 4.10.0

  (!) CHANGELOG no tiene entrada [4.10.0]
      CHANGELOG dice: 4.9.0

  ACCION: Crear entrada en CHANGELOG.md antes de continuar
```

Si ves esto → El commit sera bloqueado por el pre-commit hook.

---

#### DOCUMENTATION AUDIT: Como Saber si Hay Gaps

```
DOCUMENTATION AUDIT - Documentacion Huérfana

  [GAP] GUIA_TECNICA.md
        Archivos de codigo que REQUIEREN actualizacion:
          - modules/asset_generation/conditional_generator.py

  Para resolver: Editar manualmente y agregar referencia a la fase
```

Si ves [GAP] → Editar GUIA_TECNICA.md y agregar la fase.

---

#### Checklist Post-Ejecucion

Después de ejecutar `log_phase_completion.py`, verificar:

- [ ] REGISTRY.md actualizado (nueva entrada visible)
- [ ] No hay [GAP] en DOCUMENTATION AUDIT
- [ ] Si fue RELEASE: VERSION SYNC GATE pasó (no hubo `(!)`)
- [ ] CHANGELOG.md actualizado (si fue release)
- [ ] `git add -A && git commit`

---

## Estandares Compartidos (CONTRIBUTING §Contrato-con-Executor)

Los siguientes estandares aplican a TODOS los documentos del workflow. La fuente canonica es `docs/CONTRIBUTING.md`.

| Estandar | Valor | Referencia |
|----------|-------|------------|
| **Python path (WSL)** | `./venv/Scripts/python.exe` | CONTRIBUTING §Reglas-Contractuales |
| **CHANGELOG heading** | `## [X.Y.Z] - Titulo — YYYY-MM-DD` | CONTRIBUTING §Formato-CHANGELOG |
| **Version header** | `version: vX.Y.Z` (con prefijo `v`) | CONTRIBUTING §Reglas-Contractuales |
| **DOMAIN_PRIMER** | Regenerar al cerrar cada fase (`--regenerate-domain-primer`) | CONTRIBUTING §Paso-5b-DOMAIN-PRIMER |
| **Template** | Fuente de verdad para docs post-fase | Template §6 |
| **Referencias** | Siempre §Section-Name, nunca §NN-MM | CONTRIBUTING §Secciones-Nominativas |

---

### Paso 7: FASE-RELEASE — Cierre y Documentación Oficial del Repositorio

> [!NOTE]
> **Este paso ES la FASE-RELEASE-X.Y.Z.** Se ejecuta como una fase más, en su propia sesión de agente, usando su prompt `05-prompt-inicio-sesion-fase-RELEASE.md`.
> La diferencia con las fases de implementación: NO modifica código fuente, solo documentación y validaciones.

**Cuando**: Una vez completadas TODAS las fases de implementación (etapa 2). El agente ejecuta esta fase en una sesión nueva. **Es la última fase del proyecto.**

**Fuente de verdad**: `docs/CONTRIBUTING.md §Trigger-Documentacion-Oficial`. Los pasos E1-E8 abajo son la transcripción operativa de esa sección. Si CONTRIBUTING.md cambia, este paso se actualiza para reflejarlo.

**Que NO hace**: NO modifica ROADMAP.md, NO edita código fuente, NO ejecuta `v4complete`.

> [!TIP]
> **FASE-RELEASE es delegable a subagente.** A diferencia de las fases de implementación que pueden requerir imports del proyecto, FASE-RELEASE solo edita YAML/MD y ejecuta scripts (`sync_versions.py`, `run_all_validations.py`, `doctor.py`). Si el agente principal tiene presupuesto limitado de iteraciones, puede delegar FASE-RELEASE a un subagente con `delegate_task`. Confirmado en BUGS-ONBOARDING-ADR (2026-07-22): 18 tool calls, ~4 minutos, sin imports del proyecto.

---

#### E1. Diagnostico Inicial (CONTRIBUTING §Paso-1-Diagnostico)

```bash
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

- [ ] version_consistency_checker.py pasa sin discrepancias
- [ ] doctor no reporta errores criticos

#### E2. Sincronizacion Automatica (CONTRIBUTING §Paso-2-Sync-Automatico)

```bash
./venv/Scripts/python.exe scripts/sync_versions.py
```

Sincroniza VERSION.yaml → 6 archivos: AGENTS.md, README.md, .cursorrules, CONTRIBUTING.md, GUIA_TECNICA.md, REGISTRY.md

- [ ] sync_versions.py ejecutado sin errores

#### E3. CHANGELOG.md (CONTRIBUTING §Verificar-CHANGELOG, MANUAL)

Formato segun `docs/contributing/documentation_rules.md §Formato-CHANGELOG`:

```markdown
## [X.Y.Z] - Titulo descriptivo — YYYY-MM-DD

### Objetivo
{Descripcion breve}

### Cambios Implementados
- `ruta/archivo.py` - Descripcion del cambio

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|

### Tests
- N tests en `test_xxx.py`
```

**Regla de validacion-only**: Si la fase NO modifica codigo (solo validacion/documentacion), NO crear entrada `[X.Y.Z+1]`. Agregar como subsection dentro de la version existente.

- [ ] CHANGELOG.md tiene entrada para la version actual
- [ ] No hay entradas duplicadas
- [ ] CHANGELOG describe archivos nuevos y modificados de cada fase

#### E4. GUIA_TECNICA.md (CONTRIBUTING §Paso-4-Verificar-GUIA, MANUAL)

Agregar seccion "Notas de Cambios vX.Y.Z" con:

| Campo requerido | Contenido |
|----------------|-----------|
| Modulos afectados | Lista de modulos tocados por las fases |
| Problema | Que estaba roto o incorrecto |
| Solucion | Que se cambio y por que |
| Backwards compatibility | Si la API publica cambia o no |

- [ ] GUIA_TECNICA.md tiene nota tecnica para las fases del proyecto
- [ ] Nota incluye modulos afectados, problema/solucion, backwards compatibility

#### E5. Skills/Workflows (CONTRIBUTING §Paso-5-Skills-Workflows, MANUAL)

```bash
ls -la .agents/workflows/*.md
```

- [ ] Todos los .md en .agents/workflows/ listados en .agents/workflows/README.md
- [ ] No hay skills huerfanos

#### E6. Regenerar SYSTEM_STATUS.md (CONTRIBUTING §Paso-6-SYSTEM-STATUS)

```bash
./venv/Scripts/python.exe scripts/doctor.py --status
```

- [ ] SYSTEM_STATUS.md regenerado con version actual

#### E7. Regenerar DOMAIN_PRIMER.md (CONTRIBUTING §Paso-5b-DOMAIN-PRIMER)

Al cerrar cada fase de implementacion, regenerar el Domain Primer:

```bash
./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer
```

Solo en FASE-RELEASE (cierre final del proyecto):

```bash
./venv/Scripts/python.exe scripts/doctor.py --context
```

- [ ] DOMAIN_PRIMER.md regenerado con modulos actuales
- [ ] Todo modulo en `modules/` documentado
- [ ] Archivo regenerable automaticamente (no editar manualmente)

#### E8. Symlink + Validacion Final (CONTRIBUTING §Paso-7-8-Symlink-Validacion)

```bash
ls -la .agent/workflows    # Debe mostrar → .agents/workflows
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
git diff --stat
```

- [ ] Symlink .agent/workflows → .agents/workflows intacto
- [ ] run_all_validations.py --quick pasa sin errores
- [ ] git diff --stat muestra todos los archivos modificados

#### E8b. README.md Line-by-Line Audit (MANUAL)

> [!WARNING]
> Los conteos numericos en README.md (test count, module count, fecha) pueden desincronizarse silenciosamente entre releases. DT-3 encontro el test count stale por 56 tests (3038 vs 3094 real).

Verificar que los conteos en README.md coincidan con la realidad:

```bash
# Test count real
./venv/Scripts/python.exe -m pytest --collect-only -q 2>&1 | tail -1

# Module count real
find modules/ -name '*.py' ! -path '*__pycache__*' | wc -l
```

**Checklist README audit:**
- [ ] Test count en README.md (linea del banner `vX.Y.Z`) coincide con `pytest --collect-only`
- [ ] Test count en `## Estado del Proyecto` y `## Calidad Garantizada` coincide
- [ ] Module count en README.md coincide con `find modules/`
- [ ] Fecha de actualizacion en el banner es la fecha actual
- [ ] Si hay discrepancia → corregir con `replace_all=True` y commit separado post-release

---

## Criterios de Éxito
- [ ] Prompts creados para todas las fases de implementación (1 por fase)
- [ ] Prompt creado para FASE-VERIFY (si criterios de activación §4.6 se cumplen)
- [ ] Prompt creado para FASE-RELEASE (si hay version bump)
- [ ] Checklist maestro con estados de todas las fases (incluyendo VERIFY y RELEASE)
- [ ] `dependencias-fases.md` con conflictos documentados y dependencia → VERIFY → RELEASE
- [ ] Documentación incremental preparada (`09-documentacion-post-proyecto.md` + `10-analisis-post-implementacion.md`)
- [ ] Estructura lista para que cada fase se ejecute en sesión propia de agente

## Plan de Recuperación
- Sin estructura de planes → crear `.opencode/plans/` automáticamente
- Sin división en fases → proponer estructura estándar (Fase 0-N) + FASE-RELEASE
- Prompts muy grandes → dividir en secciones dentro del mismo archivo
- **Presupuesto declarado por la fase agotado (§R2.1)** → marcar fase como `INCOMPLETA`, documentar progreso parcial en `dependencias-fases.md`, retomar en nueva sesión fresca
- Fase retomada (INCOMPLETA) → leer estado de `dependencias-fases.md`, continuar desde donde se dejó
- **FASE-RELEASE ejecutada sin implementaciones completadas** → abortar; verificar `dependencias-fases.md` que todas las fases previas estén en `✅` (incluyendo FASE-VERIFY si aplica)
- **FASE-VERIFY incluida en plan simple** → evaluar si los 3 criterios de activación se cumplen; si no, eliminar y documentar por qué en `dependencias-fases.md`

## Versiones
- **v2.23.1** (2026-09-12): Corrección medida de **R2.10**, descubierta al cerrar la trazabilidad del plan que promovió R2.8/R2.9. La regla afirmaba que el índice vence **por rutas**; es más barato de lo pensado: el índice publica el **conteo de citas por ID y por plan**, así que dos menciones nuevas en el §7 de `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` bastaron para vencerlo (`L-R.4` 8→9, `DA-C3` 9→10) y `[6/6]` bloqueó ese commit. R2.10 pasa a cuatro hechos medidos, con el invariante explícito de que **todo** commit que edite un `.md` de `plans/` o `context/` lleva su índice regenerado en el mismo commit — lo que el hook ya comprobaba, escrito por primera vez. Sin cambios en R2.8/R2.9 ni en el resto de la familia; la cabecera de la sección sube a v2.23.1 por coherencia con el archivo. El propio commit quedó como evidencia: `docs(TRIBUNAL)` del §7 con el índice regenerado dentro.
- **v2.23.0** (2026-09-12): Tres reglas nuevas a la familia R2 (la cabecera de la sección sube de v2.21.0 a v2.23.0), del Paso 0 horizontal del plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`. **R2.8** asciende **NR7** a regla global — *mutation check*: todo AC de detección o bloqueo se cierra revirtiendo el guard y mostrando el test en rojo, con las **dos salidas** en `evidence/FASE-X/`; origen medido **D-T4B-A1** (T4-B certificó ✅ con 7/7 verdes + test de serialización + `--quick` en paz, y `_load_proposal()` leía dos niveles por encima de donde el pipeline escribe la propuesta → `total_cg_count: 0` y `BLOQUEAR` espurio), con **L-T4A.5** y **L-VUP-5** como antecedentes del corpus y **L-T2C.4** como la razón de exigirlo por AC. **R2.9** asciende **NR8** — *tri-estado*: sin hallazgos / artefacto ausente / lector fallido tienen que ser distinguibles por quien lee el artefacto, cada uno con su test **nombrado por su causa**; origen **L-PF6** (parser de JSON-LD en ARRAY tragado como ERROR → audit publicando «0 schemas» y un pain falso HIGH con cifra económica), **L-PF10** (`critical_recall` BLOCKED «metric not found» sobre una lista vacía porque el fix había funcionado) y **DA-C3** (`vacío ≠ ausente`, el contrato ya vigente que NR8 subsume y que el plan dejaba pendiente en §3.b). **R2.10** nombra el timing que estaba disperso sin dueño de sección: write-back de QMind y `build_lesson_index.py` **antes** del `git mv` a `Archives/`, más la regeneración del índice **después** del movimiento; los tres hechos están leídos en el código de los verificadores (el `--upload` resuelve `.opencode/plans/<PLAN>` por nombre, su comprobación solo escanea `Archives/`, y `--check` compara byte a byte un índice que publica rutas). Se reflejan en el bloque de R2.5 y en la nota «QMind y archivado» del §4. **Lo que NO verifica todavía**: **R2.8 y R2.9 nacen sin verificador mecánico y lo declaran en su propio texto** (política **L-R.4**, precedente R2.7), con el verificador pedido en el mismo tramo de deuda de `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`; R2.10 sí trae checks pero **parciales** — `[6/6]` bloquea el índice vencido, la pata de QMind solo corre en el modo completo y degrada a WARN sin el CLI, y **ninguno comprueba el orden en el momento del `git mv`**, solo el resultado final. Cambio documental: no toca código de producción ni el template de prompt de fase.
- **v2.22.0** (2026-09-12): El Paso 0 deja de ser una instrucción y produce un artefacto. **Origen medido**: de los 24 planes archivados, la sección «Lecciones capitalizadas de planes anteriores» —que este workflow ordenaba escribir desde v2.17.0— aparece en **6** (18 %), y la plantilla la marcaba `(si aplica)`; el plan `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` citaba solo a su predecesor con 24 planes más en el corpus, y el defecto que descubrió esta sesión (Tier A inalcanzable en `v4complete`) ya estaba documentado en `EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31`. Cambios: **nueva capa fría** (`.opencode/LECCIONES-INDEX.md`, generado por `scripts/build_lesson_index.py` — cada ID con dueño, sección y citas, definido en análisis *y* `CONTEXT-*.md`; el conteo vigente está en el encabezado del índice, no en el workflow); **`00-lecciones-capitalizadas.md`** creado antes del plan maestro con template propio (`.agents/workflows/templates/lecciones-capitalizadas-template.md`): consultas literales re-ejecutables, «qué cambia en este plan» obligatorio por fila, ≥3 descartes motivados y cobertura declarada; gate nuevo en §2.5 (sin archivo lleno no se crean prompts de fase); §4 pasa de dos a tres archivos de concepción; el write-back del §4 y R2.5 ahora incluyen `build_lesson_index.py` **antes** del `git mv` a `Archives/`. **Lo que NO verifica todavía**: la *pertinencia* de lo capitalizado — ningún script comprueba que las filas de §2 sean lecciones reales aplicadas y no ceremonial; se declara en §4 del propio archivo, y el verificador queda como deuda con dueño (`TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`), misma política de R2.7.
- **v2.21.0** (2026-09-11): Dos reglas endosadas por FASE-VERIFY del plan `TRIBUNAL-OFFLINE-2026-09-09` (decisión **D-V.3**, ejecutada en su FASE-RELEASE-4.76.0). **R2.6** — toda fase que escriba un lector de artefactos del pipeline debe tener ≥1 test contra el baseline real (`output/FASE-D_salentoreal_post_guard/`) con `skipif` explícito, y el ✅ de la fase lo exige: es la causa común de D1/D5/S1/S2/S3, causó el desvío D-T2C-A1 y dejó AC8 ❌ (la sonda `verify_probe_ac8.py` fijó 2 capas: `deliveries/` es ZIP-only y `_is_template_stub()` cuenta `---`/boilerplate como contenido). **R2.7** — el par pre/post de NR1 se valida **restando**: `suma_post − suma_pre` debe diferir en exactamente `tests_nuevos`, y una resta 0 significa baseline contaminado (medido: T4-B reportó `4018 → 4025` contra la pareja real `4029 → 4036`; los +11 de D-T2C-A1 faltaban en el `pre`). A diferencia de R2.2 y R2.5, **R2.7 nace sin verificador mecánico**: el script queda como deuda con dueño (`TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`), declarado en la propia regla para que la norma no se lea como ya cumplida.
- **v2.20.0** (2026-09-04): Nueva **R2.5** «El cierre archiva»: FASE-RELEASE termina con el plan movido a `.opencode/plans/Archives/` (git mv + `validate_opencode_refs.py --fix` + `validate_plan_citations.py --update-baseline` + `--quick` verde, un commit único), en lugar de archivarlo como reproceso en la sesión siguiente (medido: `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` se cerró con v4.75.0 y quedó en raíz pese a que la convención ya existía). Enforcement mecánico: dos checks nuevos en el pre-commit — `[4/5]` citas de línea en planes (R2.2, `validate_plan_citations.py`) y `[5/5]` cierre de planes (`scripts/validate_plan_closure.py`: un plan que declara «Cierre del plan» + COMPLETADO no puede publicar filas «⬜ Pendiente»; `Archives/` fuera de alcance). Paso 4.5.6 añadido al flujo documental §4.5.
- **v2.19.0** (2026-09-04): Cuatro reglas de proceso propuestas por FASE-VERIFY del plan `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`, que el archivo **no contenía** (medido: 0 coincidencias de «recalibr», «números de línea», «hasta el commit de código», «delta»). Nuevas §R2.1-§R2.4: **R2.1** presupuesto de iteraciones medido con `evidence/FASE-D/measure_iterations.py` y corte fijo «hasta el commit de código», con la orden de recalibrar ×3 **o retirar** la métrica (S22/DA-V6: nueve fases excedieron 2,4×-8,6× y reportaron en unidades distintas); **R2.2** prohibición de números de línea en ACs y prompts — citar símbolos (L-A6/L-V4/L-H4: 14 de 16 citas ya desfasadas al certificar) y su verificador mecánico nuevo `scripts/validate_plan_citations.py`, check 8 de `run_all_validations.py --quick`; **R2.3** no-regresión de conteos formulada como **delta** con par pre/post obligatorio (S26/DA-V2); **R2.4** regla de certificación — *un AC no legible en el artefacto que el sistema produce es ⚠️, no ✅; un ✅ que solo respalda un string en el código no existe* (L-V1/DA-V3). **R2 deja de prometer «máximo 60 iteraciones»**: la cabecera y la regla mandatoria ahora ordenan medir, no estimar.
- **v2.18.0** (2026-09-02): Write-back de CONTEXT por aporte, no por edición. Los `CONTEXT-*.md` de `.opencode/context/` se ingieren a QMind solo cuando **autodeclaran** una lección durable con etiqueta explícita (`Lección de forma:`); el criterio es binario para que no dependa de un juicio de relevancia inferido (§4). La pregunta se hace en el Cierre Obligatorio de Sesión (paso 3 nuevo), que es donde el archivo se escribe, para que el disparador no sea letra muerta. Se aclara en el Paso 0 que un CONTEXT ausente del notebook no es un olvido. Origen medido: `CONTEXT-BOTS-POTENCIALIZACION-IAH-CLI-2026-09-01.md` no estaba en el notebook (40 fuentes, última ingesta 2026-08-31) pese a declarar en §13.5 *"Lección de forma: revalidar citas de código no revalida premisas"* — el ciclo v2.17.0 solo disparaba sobre `10-analisis-post-implementacion.md` al cierre de fase, y un CONTEXT de análisis/auditoría no es cierre de fase.
- **v2.17.0** (2026-08-28): Ciclo de capitalización de lecciones aprendidas. Nuevo Paso 0 obligatorio (recuperación desde memoria del proyecto + notebook QMind `iah-cli-lecciones` antes de planificar), inyección de lecciones pertinentes en prompts de fase (§2), y write-back al cierre de cada fase (§4): lecciones INCLUIR a memoria del proyecto y re-ingesta del 10-analisis a QMind. Fallback explícito si el notebook no está disponible.
- **v2.16.0** (2026-08-24): Nueva etapa condicional FASE-VERIFY (§4.6) entre Implementación y RELEASE. Certificación formal de ACs contra output E2E real, sin modificar código. Criterios de activación: ≥3 fases impl + E2E + ACs cross-fase. Resuelve gap: la referencia "llenar en FASE-E o FASE-F" en la matriz de verificación no tenía definición formal. Metodología mínima generalizable (7 pasos). Origen: FASE-R0-F del plan REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 (12/12 ACs certificados con diff narrativo antes/después).
- **v2.15.0** (2026-08-05): Paso 4 — `10-analisis-post-implementacion.md` se crea DESDE LA CONCEPCIÓN del plan (no al final), junto con `09-documentacion-post-proyecto.md`. Esto evita el reproceso de crearlo después de que las lecciones ya se perdieron. Estructura obligatoria: Resumen de Ejecución, Matriz de Verificación, Lecciones Aprendidas, Seguimientos, Métricas, Decisiones Arquitectónicas, Checklist de Cierre. Criterios de Éxito y Ejemplo de Uso actualizados para incluir el nuevo archivo.
- **v2.14.0** (2026-08-04): Conteo de `run_all_validations.py --quick` pasa de "4/4" fijo a TOTAL PASS dinámico (el nº de checks varía al añadir validaciones nuevas, ej. check "Prompts No Release" de RC1-RC2-ENTREGA-COHERENTE-2026-08-04). Nueva branch en Regla de Decisión: fases documentales delegables pueden editar UN script stdlib-only del proyecto (sin imports de módulos ni decisiones arquitectónicas) — el parent verifica diff + validaciones. Alineado con RC3 (N13/N14): enforcement automatizado de L3/L9 vía `_check_prompts_no_release` en `scripts/run_all_validations.py`.
- **v2.13.0** (2026-07-25): GAP 3 — Nueva branch en Regla de Decisión: fases con decisión arquitectónica cross-module NO son delegables (lección DT-3 FASE-2: unificar taxonomías requiere contexto completo de ambas implementaciones + consumidores). GAP 4 — Nuevo paso E8b en FASE-RELEASE: README.md line-by-line audit con live pytest count y module count para prevenir conteos stale (lección DT-3: test count desincronizado por 56 tests).
- **v2.12.0** (2026-07-22): GAP 1 — Nueva branch 4 en Regla de Decisión código+tests: proyectos con venv Windows accedidos desde WSL no deben delegar tests a subagentes (causa raíz: subagente WSL no puede importar dependencias del venv Windows como bs4/selenium; lección de FASE-4 BUGS-ONBOARDING-ADR, ~40 iteraciones perdidas). GAP 2 — Nota [!TIP] en Paso 7: FASE-RELEASE es delegable a subagente (solo edita YAML/MD + scripts, sin imports del proyecto; confirmado 18 tool calls / ~4 min).
- **v2.11.0** (2026-05-11): Nueva sección §2.5 "Verificación Pre-Creación de Prompts". Regla anti-deuda acumulativa: cada fase de implementación ejecuta `log_phase_completion.py` al terminar — NO delegar a FASE-RELEASE. Checklist obligatorio para detectar planes mal diseñados antes de crear prompts. Si T1 de RELEASE = "registrar FASE-1 a FASE-5" → error. Agregada acción correctiva.
- **v2.8.0** (2026-04-28): Protocolo de Evidencia Proactiva (obligatorio inmediatamente despues de output v4complete, antes de cualquier verificacion). Nueva seccion "Cierre Obligatorio de Sesion" — siempre guardar evidencia + actualizar plan antes de cerrar, sin excepciones.
- **v2.6.0** (2026-04-26): Modelo de Ejecución por Agentes AI explícito. Flujo reestructurado a 3 etapas (Preparación → Implementación → RELEASE). FASE-RELEASE integrada como etapa del flujo principal. Paso 7 renombrado a "FASE-RELEASE — Cierre y Documentación Oficial". Eliminada contradicción "no se ejecuta por fase". Regla de dependencia explícita: RELEASE requiere todas las implementaciones completadas.
- **v2.5.0** (2026-04-26): Límite de 60 iteraciones como regla mandatoria (R2). Sección `## Restricciones` obligatoria en prompts de fase. FASE-RELEASE formalizado como fase ejecutable con sesión propia. Alineado con estructura real de `.opencode/plans/` del PATCH Forense AmaziliaHotel 4.36.0.
- **v2.4.0** (2026-04-13): Paso 4.5: Ejecución de Plan de Documentación. Prevención de desajustes documentales al ejecutar planes como 09-documentacion-post-proyecto.md. Incluye gates de validación: log_phase_completion.py por fase, sync_versions.py, validación CHANGELOG formato CONTRIBUTING.md, validación GUIA_TECNICA.md, run_all_validations.py --quick. Checklist de completitud integrado.
- **v2.3.0** (2026-03-26): Version Sync Gate + Documentation Audit + FASE-RELEASE auto-detect. Convencion FASE-RELEASE-X.Y.Z para releases. Pre-commit hook para consistencia de versiones.
- **v2.2.0** (2026-03-25): Enforcement de docs manuales --check-manual-docs. Si hay cambios arquitectonicos en archivos de REQUIRE_ArchitectURAL_CHANGE (conditional_generator.py, faq_gen.py, voice_guide.py, aeo_kpis.py, etc.) y GUIA_TECNICA.md no menciona la fase, el script FAIL. Uso --force-skip-docs --skip-reason para excepciones.
- **v2.0.0** (2026-03-23): Simplificado — preparación en una sesión, implementación en sesión propia por fase. Elimina TDD Gate, Capability Contract, lecciones extensas.
- **v1.5.0** (2026-03-18): Regla de Sesión Única, TDD Gate
- **v1.0.0** (2026-03-03): Versión inicial

## Ejemplo de Uso

Usuario: "Divide este proyecto de refactorización en fases y prepáralo para ejecutar por sesiones"

La skill debe:
0. Recuperar lecciones aprendidas (Paso 0: memoria del proyecto + QMind) y listar las aplicables
1. Leer plan existente
2. Crear `05-prompt-inicio-sesion-fase-{X}.md` para cada fase de implementación
3. Evaluar criterios de activación §4.6 → si aplica, crear `05-prompt-inicio-sesion-fase-VERIFY.md`
4. Crear `05-prompt-inicio-sesion-fase-RELEASE.md` (fase de cierre)
5. Actualizar checklist con estados de fases (incluyendo VERIFY y RELEASE)
6. Crear `09-documentacion-post-proyecto.md` con estructura base
7. Crear `10-analisis-post-implementacion.md` con estructura base (lecciones, decisiones, matriz de verificación)
8. Verificar numeración de todos los prompts

**Output de esta sesión:**
```
.opencode/plans/
├── 05-prompt-inicio-sesion-fase-{X}.md         (1 por fase de implementación)
├── 05-prompt-inicio-sesion-fase-VERIFY.md       (si criterios §4.6 aplican)
├── 05-prompt-inicio-sesion-fase-RELEASE.md      (fase de cierre)
├── 06-checklist-implementacion.md
├── 09-documentacion-post-proyecto.md
├── 10-analisis-post-implementacion.md
├── dependencias-fases.md
└── README.md
```

La implementación de cada fase se hace en UNA sesión nueva de agente por fase. FASE-VERIFY (si aplica) va después de todas las implementaciones. FASE-RELEASE es la última sesión.
