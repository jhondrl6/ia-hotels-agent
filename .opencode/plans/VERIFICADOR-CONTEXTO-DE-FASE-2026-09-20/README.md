# VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Estado: CONCIBIDO y AJUSTADO el 2026-09-20 (Etapa 1 — Preparación, sin ejecutar); AUDITADO y
CORREGIDO el 2026-09-20 contra código vivo y contra el Knowledge Center** (ver §Correcciones
aplicadas). Renombrado desde `PASO0-VERIFICADOR-PERTINENCIA-2026-09-20` cuando entró FASE-D, porque
el contenido dejó de ser solo pertinencia. Cuatro fases de implementación + RELEASE, todas
pendientes. Ninguna escribió código.

Objetivo: arreglar las tres cosas que hacen que un plan de este repo se lea caro, se juzgue mal y se
desfasen solo. **Coherencia** de las aserciones sobre conteos en los documentos de gobierno,
**pertinencia** de las lecciones que el Paso 0 capitaliza, y **carga de lectura** de una sesión de
fase: **263.973 bytes ≈ 65.993 tokens estimados** antes de tocar código, re-medidos el 2026-09-20
sobre la sesión de FASE-B del plan en vuelo (la medición A7 del maestro; al concebir daba 254.010 y
venció el mismo día).

Hermano de `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, que cerró la forma. Este cierra el juicio y
la economía de la lectura. **No forma parte de la cadena `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**:
no comparte ACs, no consume su contador de corrida, no toca sus archivos. Las superficies compartidas
son **tres**, medidas el 2026-09-20: el índice de lecciones (éste y las fases vivas de
`REFACTOR-WHATSAPP`), el archivo que este plan **no** escribe pero sí lee como fuente de verdad
(`scripts/run_all_validations.py`, declarado dentro del alcance del hermano
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20` → deuda **D10**), y la raíz `evidence/` (ver §Correcciones,
R5: la evidencia de este plan vive en su propio subdirectorio). Detalle en `dependencias-fases.md`
§Conflictos.

## Índice documental

- [Lecciones capitalizadas](00-lecciones-capitalizadas.md): ocho consultas re-ejecutables con su
  resultado medido, catorce lecciones con dueño y efecto concreto sobre ACs reales, cinco descartes, y
  la capa tibia (QMind) **ya consultada** el 2026-09-20 con su comando corregido.
- [Plan maestro](01-plan-maestro.md): las mediciones A1–A8 (cuatro aserciones vencidas —con A3
  re-medida—, un grep con cero coincidencias, la auto-refutación A6, la carga de lectura A7 y la
  población bajo el patrón A8), la matriz de decisión, AC1–AC23 y la deuda D1–D10.
- [Contrato de ejecución](04-contrato-ejecucion.md): permisos, **regla de cero red**, reglas sobre el
  pack generado, corte de presupuesto y por qué no hay FASE-VERIFY.
- [Dependencias y bloqueantes](dependencias-fases.md): cadena, herencias, conflictos de archivo.
- [Checklist de implementación](06-checklist-implementacion.md): matriz de ACs con el artefacto donde
  cada uno se lee.
- [Prompts de fase](05-prompt-inicio-sesion-fase-A.md) A · B · C · [D](05-prompt-inicio-sesion-fase-D.md)
  · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md).
- [Documentación post-proyecto](09-documentacion-post-proyecto.md) y
  [Análisis post-implementación](10-analisis-post-implementacion.md): acumulativos, se llenan por fase.

## Cinco sesiones, una fase por sesión

| Orden / prompt | Objetivo | Complejidad | Estado |
|---|---|---|---|
| 1 · [A](05-prompt-inicio-sesion-fase-A.md) | `validate_governance_numbers.py`: aserción contra fuente dinámica, denominador, tres estados. AC1–AC5 | MEDIA / alta consecuencia: es el guard de cualquier edición futura de `.agents/` | PENDIENTE |
| 2 · [B](05-prompt-inicio-sesion-fase-B.md) | `decision_client.py`: costura neutra, contract test de forma, extensión a un segundo proveedor **probada**. AC6–AC9 | MEDIA-ALTA | PENDIENTE |
| 3 · [C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: pertinencia **aditiva** sobre el índice generado, con su aceptabilidad medida. AC10–AC15 | ALTA | PENDIENTE |
| 4 · [D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura**. AC19–AC23 | MEDIA: gobierna lo que todas las sesiones futuras van a leer | PENDIENTE |
| 5 · [RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Sync, CHANGELOG, `REGISTRY.md`, decisión sobre D1 y D2/D3, write-back (re-leyendo su interfaz: **D10**) y archivado | MEDIA | PENDIENTE |

Cadena: **A → B → C → D → RELEASE**. A y B son técnicamente independientes; C consume a ambas y D a
las tres. **FASE-VERIFY no aplica**: §4.6 pide tres criterios y el de «fase con ejecución E2E» no
existe aquí, porque este plan tiene prohibida la pipeline y la red.

## Correcciones aplicadas (auditoría de la concepción, 2026-09-20)

Nueve fallos encontrados sobre **código vivo** y sobre el **Knowledge Center** (notebook
`iah-cli-lecciones`, cuatro `retrieve` ejecutados el mismo 2026-09-20). Ninguno tumba el diseño; todos
eran premisas publicadas como hechas. Cada fila dice qué se corrigió y dónde.

| # | Qué estaba mal | Corrección aplicada | Dónde quedó |
|---|---|---|---|
| **R1** | A3 publicaba como observado `[12/15]`, que es la etiqueta de `def _check_dependencies`. El write-back imprime `[15/15]` | Fila A3 re-escrita con su emisor correcto + rectificación datada que reconoce que el plan que caza cifras vencidas publicó una vencida | maestro §1 (tabla y nota de rectificación), Q5 de `00-`, `10-analisis` (matriz de hallazgos) |
| **R2** | AC1 exigía «exactamente A1–A4 y ninguna otra» sin regla de población: el escaneo encuentra **22 instancias `[N/M]` en 17 líneas** más 2 formas «check N» | Nueva medición **A8** + regla de población con tres clases (viva / histórica congelada / vigente-correcta), `occurrences[]`, `historical_excluded[]` y su publicación obligatoria | maestro §1 A8, §4 AC1 y AC2, `06-checklist`, prompt de FASE-A |
| **R3** | Se atribuía el pin «El quick son 11 checks.» al prompt de FASE-C de `REFACTOR-WHATSAPP` | Atribución corregida con los cuatro sitios medidos (README, 06, 09, 10 de ese plan) | maestro §2, README §Deja sin hacer, `dependencias-fases` |
| **R4** | «`run_all_validations.py`: nadie» era falso: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE) lo declara dentro de su alcance y cambia el writer del que depende el cierre | Fila de conflicto re-escrita + deuda **D10** (re-leer la interfaz del write-back en el RELEASE, sin convertirlo en dependencia de ejecución) | `dependencias-fases` §Conflictos, maestro §2 y §6, `04-contrato` |
| **R5** | La evidencia se escribía en `evidence/FASE-A/` … `FASE-D/`, que **ya están ocupadas** por `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` (con `faseA_baseline_pre.txt` y su par, nombres que el contrato de este plan repetiría) | Las 65 rutas del plan re-punteadas a `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`; la plantilla de `.agents/` sigue diciendo `evidence/fase-{N}/`, y eso queda **declarado** (no corregido: AC17) | los doce archivos del plan; nota en `04-contrato` |
| **R6** | Tres afirmaciones del README ya eran falsas al medirlas: «el índice aún refleja el nombre anterior» (está regenerado y fresco: `[OK] … (320 IDs)`, 0 coincidencias con el nombre viejo), «el árbol está limpio» (índice modificado sin commitear + plan sin trackear) y el valor vigente de A7 | Bloque de límites re-escrito con lo medido; el bloque de arranque deja de afirmar limpieza y ordena medir `git status`; A7 publicado con valor nuevo, comando y fecha | README, prompt de FASE-A |
| **R7** | D8 decía «re-ejecutar Q7, el CLI no está disponible»; y el comando publicado (`--nb iah-cli-lecciones`) devuelve `error: Bad request` | Q7 marcada como **ejecutada** el 2026-09-20 con sus resultados capitalizados (L-V2.1, L-V2.2, D-V2.1) y el comando corregido al ID del notebook | `00-lecciones` Q7 y §4, maestro §6 D8, README, prompt RELEASE |
| **R8** | Las familias no cubiertas se enumeraban «de oído» y faltaban las que hoy también están vencidas | AC2 y AC17 publican las cuatro familias medidas: prosa sin patrón, conteos fuera de los documentos de gobierno (**`AGENTS.md` con «10/10 … y 14»**, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), **pins en `tests/`** (`tests/test_validate_plan_closure.py` assertiona `[5/7]`) y fuentes dinámicas que no son etiqueta impresa; AC16 barre `tests/` al medir quién afirma el 11 y el 7 | maestro §4, `06-checklist`, prompt FASE-A |
| **R9** | Tres precisiones: la razón por la que el pack no lleva ruta absoluta estaba mal explicada; el «Dato externo» del SDK se presentaba como medido; y el conteo de dueños del Paso 0 decía 7 con 6 nombres | Razonamiento corregido (lo que rompe una referencia es que su destino no exista al escanear, no la forma de la ruta), origen del dato declarado explícitamente como externo, y dueños corregidos a **6** — con la atribución de `D-V2.1` arreglada, que la cazó el propio `validate_lesson_capitalization.py` por `C7` al re-validar este `00-` | prompt FASE-D, maestro §2, `00-lecciones`, `10-analisis` |

**Lo que NO cambió** (confirmado, no asumido): las cuatro aserciones vencidas siguen vivas en
`.agents/` y ningún check las sostiene (A1 `[9/11]`, A2 `[10/11]`, A3 `[15/15]`, A4 `[10/11]`); el
hook sigue en 7; §4.6 sigue sin activar FASE-VERIFY (criterio 2 cae); el contrato de cero red, la
prohibición de tocar `.agents/`, `run_all_validations.py` y el hook, y la cadena A→B→C→D→RELEASE
quedan intactas.

## Lo que este plan deja deliberadamente sin hacer

- **No entra Jev. Decisión del operador del 2026-09-20**, con el acceso ya habilitado. FASE-B construye
  la costura y AC9 certifica que **añadir** el proveedor cuesta un archivo; la comparación de
  proveedores se pospone como deuda **D7**. Consecuencia aceptada: ningún AC mide calidad de
  decisiones de un modelo real — miden forma, aislamiento y no-regresión.
- **No hace el lint de contradicciones semánticas** (`validate_plan_semantics.py`), que era la otra
  mitad del diagnóstico. Queda como deuda **D6** con un disparador medible: la **aceptabilidad** que
  publique FASE-C. Si el triaje sale inaceptable, D6 **no** se activa — no se apila un segundo
  consumidor sobre una base que no funcionó.
- **No altera el conteo de checks.** El `--quick` sigue en 11 y el hook en 7 (AC16, como delta con par
  pre/post). Motivo medido el 2026-09-20: el plan en vuelo pinea la cifra en **cuatro** de sus
  documentos — el bloque de arranque de FASE-B de su `README.md` («El quick son 11 checks.»),
  `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md` y
  `10-analisis-post-implementacion.md` — no en el prompt de FASE-C, como afirmaba la primera versión
  de esta fila. Promover algo aquí invalidaría la medición de fases ajenas (deuda D2).
- **No edita `.agents/`.** Las cuatro aserciones vencidas se **reportan**, no se reescriben: quien
  corrige la frase a mano produce la fosilización siguiente (deuda D1, con instrucción literal).
- **No rebaná el workflow canónico** (deuda D3). FASE-D hace lo que sí puede hacerse sin tocarlo:
  **unificar** las lecturas que cada fase declara en un pack derivado, sin sustituir ninguna fuente.
- **No filtra lecciones.** El triaje propone, el umbral se publica con su acción por debajo y ninguna
  fila de §2 puede desaparecer: eso es AC10 con su test.
- **No promete velocidad sin número.** AC20 obliga a medir el delta de carga con el mismo comando en
  los dos lados; **un delta cero o negativo es resultado válido si se explica**.

## Prerrequisitos y límites visibles

- **Ninguna credencial es necesaria y no hay llamadas de red en ninguna fase** (contrato §Regla de cero
  red). Las pruebas de proveedor se hacen con proveedores falsos.
- **La capa tibia del Paso 0 SÍ se consultó, pero después de concebir.** Al concebir, QMind
  `iah-cli-lecciones` no estaba accesible en la sesión (consulta Q7, declarada NO EJECUTADA) y se
  aplicó el fallback del executor. La auditoría del 2026-09-20 lo ejecutó con el CLI disponible
  (v3.3.0) y sus resultados ya están capitalizados en `00-lecciones-capitalizadas.md` (L-V2.1,
  L-V2.2, D-V2.1). **Queda un fix de forma: `--nb` exige el ID del notebook, no su nombre** — la
  forma con el nombre, que es la que publica el workflow canónico, devuelve `error: Bad request`.
  D8 queda como re-correr la consulta antes de RELEASE, no como primera vez.
  Límite: el triaje calibra contra 320 IDs definidos y 50 citados sin definición — **re-medido**,
  porque al crearse este plan sus propias cifras vencieron (medición A6).
- **Commitir requiere regenerar el índice** en el mismo commit (`[6/7]` del hook): los archivos de este
  plan nombran IDs reales del corpus. Medido el 2026-09-20 al auditar: el índice **ya estaba regenerado
  y fresco** (`build_lesson_index.py --check` → `[OK] … (320 IDs)`; 0 coincidencias con el nombre
  anterior del directorio, 15 con el vigente) y sus dos archivos estaban **modificados sin commitear**,
  con el plan **sin trackear**. **Ese estado ya no existe**: la auditoría se commiteó y empujó con
  instrucción literal del operador el 2026-09-20 — `2c9d0c1`, paridad `0/0` con `origin/master`
  verificada con `git ls-remote`—, así que desde aquí el árbol de partida es limpio y lo que cada fase
  encuentra modificado proviene de su propia edición o de la fase viva de `REFACTOR-WHATSAPP`.
- **Las cifras de este README son estimaciones con divisor declarado** (bytes/4), no recuento de
  tokenizer. A7 suma **siete** documentos (el octavo que declara leer la fase medida es un archivo de
  `evidence/` y queda fuera de la suma, como dice su pie) y caducan cuando cambia cualquiera de ellos:
  **ya caducaron el mismo día de la concepción** (254.010 → 263.973 bytes; ver maestro §1, A7).
- Commit y push **no** están autorizados por la existencia de este plan; cada fase deja checkpoint y
  pide su propia instrucción literal. Así se hizo con la auditoría del 2026-09-20: `2c9d0c1` se
  commiteó y se empujó solo tras la instrucción escrita del operador (y tras ofrecer el escaneo L3, que
  el operador saltó).

## Inicio de la siguiente sesión

Copiar en una sesión nueva. **Se reescribe en cada cierre de fase** y su frescura la mira
`validate_plan_closure.py`.

```text
Ejecuta únicamente FASE-A del plan
C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/.
Lee 05-prompt-inicio-sesion-fase-A.md, 01-plan-maestro.md §1 (la tabla A1-A4 con su rectificacion de
A3, la medicion A7 y la poblacion A8) y §4 (AC1-AC5 con la regla de poblacion, AC16, AC17),
04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md y el workflow
canonico. A es la primera fase de este plan y no consume nada de REFACTOR-WHATSAPP, que corre por
separado. **Estado medido del arbol tras publicarse la auditoria: limpio y en paridad 0/0 con
`origin/master` sobre `2c9d0c1` (verificado con `git ls-remote` el 2026-09-20), y el indice de
lecciones ya esta fresco.** No lo des por supuesto: vuelve a medirlo al abrir, porque una fase viva de
REFACTOR-WHATSAPP comparte esa pareja de archivos y puede entregar el arbol modificado.
Re-mide antes de la primera tarea y publica el numero que obtengas: git HEAD/status, la etiqueta que
imprime CADA def _check_* de run_all_validations.py (emparejando etiqueta y metodo, que es como nacio
la medicion vencida de A3: el write-back imprime [15/15], no [12/15]), los siete pasos del hook
versionado, y el tamano en bytes de los siete documentos que suma A7 (valor de referencia 2026-09-20:
263.973). Si alguna de las cuatro aserciones del maestro §1 ya no esta vencida, o si A7 vuelve a moverse,
dilo: la premisa del plan se re-mide, no se asume (A6 es exactamente lo que pasa cuando no se hace).
Escribe scripts/validate_governance_numbers.py: compara cada asercion sobre un conteo en los documentos
de gobierno contra la etiqueta que el codigo imprime, descubre las aserciones escaneando los documentos
(no hardcodeando las cuatro), **aplica la regla de poblacion de A8 con sus tres clases (viva /
historica congelada / vigente-correcta) y publica findings[] con occurrences[] y historical_excluded[]**,
y publica coverage_basis con la poblacion mirada y las familias no cubiertas (las cuatro de AC2, una por
una: prosa sin patron, conteos fuera de los documentos de gobierno incluyendo AGENTS.md, pins de conteo
en tests/, y fuentes dinamicas que no sean etiqueta impresa). Expresa los tres estados sin que ninguno
colapse. Reutiliza el diseno de validate_plan_citations.py (reporta, no reescribe) y de
validate_lesson_capitalization.py (R2.9 sobre si mismo).
No toques run_all_validations.py, el hook, .agents/, build_lesson_index.py ni ningun plan vivo.
Todo AC de detencion se cierra con mutation check sobre el simbolo real del guard, **por asercion y
afirmando el assertion_id del mutante (L-V2.1)**, con las dos salidas en
evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/; sin el rojo, AC4 es ⚠️. El conteo del quick y
del hook se expresa como delta con par pre/post, resta comprobada y delta esperado 0, y la pregunta
«quien afirma el 11 y el 7» se responde barriendo tambien tests/ (L-V2.3).
Registra la fase con log_phase_completion.py y regenera el indice de lecciones en el mismo commit. Deja
checkpoint si falta autorizacion y conserva cada AC en el estado que pueda probar.
```

## Cierre y aceptación

Cada fase incorpora su evidencia y su cierre incremental; no se difiere ningún control a RELEASE.
Techo alcanzable de un AC: `VERIFICADO OFFLINE` **con su mutation check en disco**, `⚠️ PARCIAL`, o
`NO-EJERCITADO` con motivo. Un `[OK]` sin denominador no informa (L-R.3) y un verde sin rojo previo se
declara sospechoso (L-VUP-5).
