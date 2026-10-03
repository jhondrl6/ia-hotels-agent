# Checkpoint de la sesion — reconciliacion documental JEV/VCF, 2026-10-02

## Que declaro esta sesion

**No ejecuto ninguna fase** de `EVALUACION-JEV-TYPESAFE-2026-09-21` (A/B/C/RELEASE) ni de
`VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (A/B/C/D/RELEASE). **No llamo a ninguna API de inferencia, no activo
proveedor, no autentico credencial, no instalo nada.** No escribio en `scripts/**`, `tests/**`, `modules/**`,
`.agents/**`, `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, `CHANGELOG.md`, `REGISTRY.md`, `.gitignore`,
`tmp_test/**`, `.opencode/refs_baseline.txt`, `.opencode/plans/plan_citations_baseline.json` ni
`.opencode/wiring_report.json`. No edits `.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`,
protegido por orden del operador del 2026-09-21. No toco nada bajo
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/` (lectura si, escritura no). No corrio `--fix` ni
`--update-baseline` de ningun verificador. **No commiteo ni empujo**: la sesion termina aqui y pide
instruccion.

Las unicas escrituras de `validate_wiring.py --write-report` de esta tanda llevaron destino explicito bajo
`temp/`; el informe versionado no se re-escribio, y su `--check` lo certifica CONFORME con digest impreso.

## Que se escribio

| Ruta | Que es |
|---|---|
| `.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/README.md` | Sello ⟦Sello 2026-10-02⟧ al final de §«Inicio de la siguiente sesion». El texto original no se borro ni se parafraseo |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-09-30/00-checkpoint-de-preparacion.md` | Nota fechada anadida al final, declarando vencida la fila `tmp_test/` con sus tres mediciones y re-midiendo los dos defectos de `04-`. La fila original sigue intacta |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-10-02/00-paquete-decision.md` | Las dos peticiones al operador, con dueno y puerta |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-10-02/01-re-medicion-2026-10-02.txt` | El crudo del PASO 0 y del PASO 1, cada salida con su comando literal |
| `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREPARACION-DECISION-2026-10-02/02-checkpoint.md` | este archivo |
| `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md` | Espejo de una linea hacia el paquete de decision |
| `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/FASE-{A,B,C,D,RELEASE}.md` | Los cinco packs, regenerados porque el espejo toco una fuente declarada |
| `.opencode/lecciones_index.md` y `.opencode/lecciones_index.json` | El par del indice, regenerado por el sello del README |

## Las tres afirmaciones con las que abrio la sesion, verificadas contra disco

| Afirmacion del prompt de sesion | Veredicto medido | Donde esta la medicion |
|---|---|---|
| Los items 1-3 de la preparacion ya se ejecutaron el 2026-09-30 | **CONFIRMADO**, con precision: el prompt listaba cinco piezas del expediente y en disco hay ocho archivos de trabajo (le faltaban `05-shas-y-poblaciones-medidos.txt` y los dos sellos de publicacion `06-` y `07-`, este ultimo con mtime del 2026-10-01) | `01-re-medicion-2026-10-02.txt`, bloque `ls -la` del expediente |
| La muestra sigue en borrador | **CONFIRMADO**, con precision de grafia: la clave que gobierna la muestra es `review.human_reviewed` en `muestra.json` (= `false`); la que gobierna las etiquetas es `review_status` en `etiquetas.json` (= `sin_revisar`), con sus entradas `label`/`importance`/`reviewer`/`reviewed_at` todas en `null`. El checkpoint del 2026-09-30 escribe `human_reviewed` al hablar de las etiquetas | `01-re-medicion-2026-10-02.txt`, bloque de los conteos de `etiquetas.json` y `muestra.json` |
| La salida (c) de `tmp_test/` se curo el 2026-10-01 porque el `.gitignore` declara `tmp_test/` | **CONFIRMADO en el fondo, REFUTADO en la atribucion**: las tres mediciones independientes dan la (c) aplicada, pero la declaracion del `.gitignore` es de `ede7fcb` **2026-03-26** (y `git log --since=2026-09-29 -- .gitignore` = 0 lineas), y quien goberno el alcance del wiring por esa declaracion fue `abd181c` **2026-09-30 16:18** («paso 1, salida (c)»), dos horas y media despues del mtime del checkpoint que la dejaba abierta. `0731741` **2026-10-01** trajo la pieza del derivado (schema 1.2) | `01-re-medicion-2026-10-02.txt`, bloques de `.gitignore`, del rapido, del `--check` y de los `git log -S` |

Y los **dos defectos que descubrio `04-`**: esta re-medicion **no los encuentra**. La clausula de produccion
hoy se codifica en el EXIT (`_hallazgos_del_criterio` → `verificar()` → `viol`, cura `5145173` 2026-09-30) y
el derivado versionado se contra-verifica con `--check` (`fbfdc57` 2026-09-30, corriendo en `[11/13]` del
rapido). Limite declarado: no se corrio un mutante, porque `scripts/**` no esta autorizado en esta sesion; el
contrafactual lo prueba la bateria versionada que esta en `git ls-files`.

## Lo que queda pendiente, con dueno y puerta

| # | Pendiente | Dueno | Puerta (que lo destraba) |
|---|---|---|---|
| 1 | **D-B** — elegir la salida del gap de contrato | **DECIDIDA el 2026-10-02** en (a)+(b) con dos tiempos; el ejecutor de (a) pasa a ser quien tenga `scripts/**` en alcance | Ya no espera eleccion: espera **mandato de ejecucion**. (a) autorizada y no ejecutada; (b) atada al mandato de FASE-B. Su lectura y sus letras, en §«Respuesta del operador» de `00-paquete-decision.md` |
| 2 | **D-D** — designar quien etiqueta los pares y acuerda los umbrales | **CERRADA la designacion** (2026-10-02, segunda respuesta): el operador se nombro revisor de si mismo, con la falta de independencia declarada en el acta; umbrales acordados por clave. Las cuatro etiquetas **estan dictadas y transcritas** el mismo dia (ver §Nota de rectificacion) | Ya no espera ni nombre ni juicio. Espera **una** cosa: el paso `BORRADOR → CONGELADA`, que no se ejecuto sin su palabra explicita |
| 3 | La sobrecarga de las letras (a)/(b) entre `01-gap-de-contrato.md` y `02-material-muestra-y-umbrales.md` §2 (dos ejes distintos con las mismas etiquetas) | El expediente del 2026-09-30, que no se re-escribe | **CERRADA en su efecto**: la respuesta de D-B dijo «con eje de gap», que es la forma de la fila 1. La prosa vencida del 09-30 queda como esta, con esta nota al lado |
| 4 | Las salidas (a) y (b) de la fila `tmp_test/` del checkpoint del 2026-09-30 | Dueno de `scripts/validate_wiring.py` | Ya no tienen rojo que apagar: la (c) se aplico. Quedan como opciones muertas declaradas, no como deuda |
| 5 | El `const` de `--write-report` sigue apuntando al informe versionado | Dueno de `scripts/validate_wiring.py` | Un cambio en `scripts/**`, no autorizado en esta sesion. Mientras tanto: destino explicito a `temp/` siempre |
| 6 | JEV FASE-B, FASE-C y RELEASE | Operador, en ese orden | Mandato explicito + muestra/protocolo congelados + credencial y presupuesto escritos (C es la unica con red). **Las dos decisiones que la bloqueaban por lectura ya estan dictadas (2026-10-02): lo que queda son sus ejecuciones, no sus respuestas** |
| 9 | Ejecutar la salida (a) del gap sobre `scripts/decision_client.py`, y abrir con ella la discusion S10/D7 del hermano | quien tenga `scripts/**` en alcance | Mandato de ejecucion. La autorizacion politica ya esta dada; el codigo no se escribio en esta sesion |
| 10 | El guard `unreviewed_not_frozen` llena tres campos pero **no prueba que el revisor sea humano** — la reserva de AC3/L-R.4 es documental, sin verificador | dueno de `scripts/evaluate_jev_pilot.py` | Un check nuevo, con su bateria. Registrado aqui con dueño y disparador, sin cura en esta sesion (precedente de la familia «un guard que nadie dispara») |
| 7 | D7 + S10 del hermano (el «porton» del registro) | Su fila en el registro unificado del 2026-09-29 | Credencial + presupuesto. D-B puede tocar su superficie, no la resuelve |
| 8 | Los dos partes de `SELLOS-ESTADO-2026-10-01` y su «Nota de disposicion 2026-10-02» | Ya cerrado por la tanda anterior; esta sesion no los toco | Nada. Se mencionan porque son el precedente de forma de la nota anadida al checkpoint |

## Lo que esta sesion NO produjo

Ninguna etiqueta humana, ningun umbral acordado, ninguna muestra congelada, ningun codigo de produccion,
ninguna salida del gap aplicada, ningun commit, ningun push, ningun `--fix`, ningun `--update-baseline`. Los
criterios C1-C10 del prompt de sesion se publican al cerrar la tanda, con el comando que prueba cada uno.

## POST — derivados regenerados sobre el arbol final y estado medido

El orden prescrito es packs → indice → `--check` de packs → `--check` del indice → rapido. Se corrio en ese
orden porque generar el indice antes que los packs deja el `--check` en rojo aunque el contenido sea correcto.

- `build_phase_briefing.py` (generacion): `5 packs · COMPLETO 5 · SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0`,
  con `fuentes 37` y `secciones pedidas 23, resueltas 23`. EXIT 0.
- `build_lesson_index.py` (generacion): `340 IDs definidos + 56 sin definición (16 análisis, 422 .md citados)`,
  `[fechas] nombre=329 commit=11 sin_fuente=0`. EXIT 0. Escribio `.opencode/LECCIONES-INDEX.md` y
  `.opencode/lecciones_index.json`.
- `build_phase_briefing.py --check`: los cinco packs frescos, EXIT 0. `build_lesson_index.py --check`: fresco,
  EXIT 0. `run_all_validations.py --quick`: `TOTAL: 13/13 validations passed`.
- `git rev-parse HEAD` = `ed44c51ca65608a4489597a9f3e19fddb4f129d5`, identico al de partida (C1).
- `sha256sum` de `muestra.json`, `etiquetas.json` y `protocolo.json`: los tres iguales a los del PRE, y
  `review.human_reviewed` sigue `false` con `review_status` en `sin_revisar` (C2).
- `find . -name "*.jsonl" -not -path "./venv/*"` = 0 lineas (C9).

## Efecto secundario medido de escribir los sellos: el par del indice se movio por mi propia prosa

No es un rojo, pero viaja declarado porque esta sesion lo provoco:

- El `--check` del indice estaba **fresco en el PRE con 54 citados sin definicion**. El sello del README de JEV
  nombra a las dos peticiones como `(D-B)` y `(D-D)`, y el escaner del indice recorre la familia `D-*`, asi que
  las tomo como IDs citados: **54 → 56**, con dos filas nuevas `D-B` y `D-D` cuyo dueño es
  `Archives/EVALUACION-JEV-TYPESAFE-2026-09-21`. Las definiciones existen, pero en `evidence/`, que el indice no
  recorre. Los partes de `SELLOS-ESTADO-2026-10-01` y el registro unificado del hermano ya usaban esas dos
  etiquetas; ninguna de las dos estaba en el corpus de planes antes de hoy.
- `L-VCF-19` subio de `77` a `79` menciones por la misma razon en cadena: la cite en el espejo del plan hermano
  (un mention) y el espejo se projeta dentro del pack `FASE-RELEASE.md` (otra). Medido con
  `grep -c "Espejo 2026-10-02"` sobre los cinco packs: aparece **una** vez, en `FASE-RELEASE.md`, y **cero** en
  los otros cuatro — que es lo que declara el `--listar-declarado`, porque `10-analisis-post-implementacion.md`
  solo esta en las fuentes de FASE-RELEASE.

**Decision que queda del operador, no resuelta aqui**: se puede dejar asi (los dos IDs quedan como citados sin
definicion en el indice, que es su estado honesto: se definen fuera del corpus de planes), o se puede re-nombrar
las dos letras del paquete para que no tengan forma de ID del indice. Lo segundo tocaba re-escribir el sello ya
escrito, y esta sesion no re-escribe un derivado para esconder su propia huella. Los gates quedaron verdes en los
dos casos, asi que no hay rojo que curar.

## Nota sobre el criterio C6 del prompt de sesion

La lista blanca de C6 nombra `10-analisis-post-implementacion.md` **de JEV** como ruta esperada en el
`git status`. Ningun paso del propio prompt (PASO 2 al 6) manda escribir en ese archivo: alli solo se lo cita
como *precedente de forma* del espejo. Medido: ese archivo **no esta modificado**. El alcance real de esta sesion
es un subconjunto estricto de la lista, que es lo que C6 exige («ninguna ruta fuera de esa lista»), y se declaro
en vez de inventar una escritura para llenar la lista.

## Cierre del ciclo de verificacion (para quien relea C7)

El bloque POST de arriba se midio despues de la penultima escritura. Esta nota es la ultima escritura de la
sesion, y es inerte por construccion para los derivados: `evidence/` no esta en las fuentes declaradas de
ningun pack (`build_phase_briefing.py --listar-declarado` solo enumera archivos del plan y el workflow) y el
indice recorre `.opencode/plans` y `.opencode/context`, no este directorio. Aun asi, el prompt pide que los
dos `--check` y el rapido se corran despues de la ultima escritura, y esa corrida va en la respuesta de cierre
con su `TOTAL` impreso, no aqui: publicarla en este archivo volveria a dejar el archivo como la ultima
escritura y el ciclo no termina. Es el mismo motivo por el que la cifra de cobertura vive en su fuente y no se
re-transcribe.

## Nota de disposicion del push (2026-10-02)

⟦**Nota de disposicion 2026-10-02 — el «no commiteo ni empujo» de arriba describe la ventana de ejecucion del
mandato, y esa ventana cerro con dos instrucciones del operador.** El prompt que abrio la tanda terminaba en
espera de autorizacion: primero para el commit, despues para el push. Medido, no deducido:

- **Commit `e2f7682`** — 13 archivos, +822/−65. Los ocho checks del pre-commit se ejecutaron y cerraron en
  PASSED (indice fresco en 340 IDs, packs 5/5 reproducidos por el escritor, citas de plan 0 nuevas y 0
  crecimientos). Sin `--no-verify`.
- **Pre-flight antes de empujar**: `git fetch origin --quiet` y
  `git rev-list --left-right --count origin/master...HEAD` = **`0 1`** — un commit adelante, nada atras, o sea
  fast-forward; `git push --dry-run origin master` mostro el mismo rango `ed44c51..e2f7682` con EXIT 0.
- **Push `ed44c51..e2f7682`** a `refs/heads/master` de `github.com/jhondrl6/ia-hotels-agent`. Verificado **por
  identidad y no por el mensaje del comando**: `git ls-remote origin refs/heads/master` devolvio
  `e2f7682f267a079ebb7035ffb6fa3d313b77c2ba`, igual que `git rev-parse HEAD`, y tras el fetch el conteo de
  paridad quedo en **`0 0`**.
- **Lo que de aquella frase sigue vigente**: ninguna fase ejecutada, ninguna inferencia, ninguna credencial,
  ningun `--fix` ni `--update-baseline`, ninguna etiqueta humana y ninguna linea de `scripts/**`. Y en el
  commit no entro trabajo ajeno: el arbol estaba limpio sobre `ed44c51` al abrir la sesion.
- **Rectificacion de una palabra propia, partida en sus dos sentidos**: donde §«Lo que esta sesion NO produjo»
  dice «ningun commit, ningun push, ningun `--fix`, ningun `--update-baseline`», lo primero y lo segundo ya no
  son ciertos despues de las dos instrucciones; lo tercero y lo cuarto si. Y donde §«Lo que esta sesion dejo
  explicitamente sin tocar» del paquete dice «Ningun write», la frase nunca fue cierta tal como se leia: no
  hubo escritura de codigo ni de datos del piloto, pero esta tanda escribio once rutas documentales, que son
  justo las que entran en `e2f7682`.
- **El push publica el estado, no lo produce.** Las filas 1, 6, 9 y 10 de la tabla de pendientes quedan como
  estaban, y el acto de etiquetar (D-D) sigue sin hacer: las tres piezas del piloto no entraron en el commit —
  `git show --stat` sobre esas rutas da **0 lineas** — y conservan su sha de partida con `human_reviewed=false`.⟧

⟦**Addendum 2026-10-02, tercero de la tanda — el rango que estampa la nota de arriba queda incompleto por un
commit.** Se empujo tambien `e2f7682..15feb2e`, que es la propia nota de disposicion, y el total de la sesion es
**`ed44c51..15feb2e`**: dos commits, 13 archivos, +861/−65. No se reescribio la linea anterior —esa sigue siendo
exacta sobre el acto que describe—, se le anade esta, que es la regla de la casa para un segundo push.
Y aqui se corta la recursion, declarada en vez de perseguida: esta nota se escribe antes de su propio push,
así que su valor no puede citarse a sí misma. Lo que publica **esta** línea es el rango hasta `15feb2e`; el tip
con el que quedo el remoto despues de estamparla se mide con `git ls-remote origin refs/heads/master` y no se
copia aqui. Un cuarto commit que registre eso no informa nada que la orden anterior no informe mejor.⟧

---

## Nota de rectificacion 2026-10-02 — las etiquetas se dictaron y se transcribieron, y dos afirmaciones
## mias de esta misma tanda quedan vencidas

**El dictado del revisor designado (el operador, en primera persona):** `D-AJUST.1` pertinente/alta,
`D-AJUST.2` no_pertinente/`n/a`, `D-NC2` insuficiente/`n/a`, `D-AJUST.4` pertinente/media, con
`reviewer = jhon` y `reviewed_at = 2026-10-02`. La transcription es mecanea y no judgement: el criterio es
suyo y ninguna de esas ocho decisiones se produjo en una sesion de codigo.

**Como se escribio, y por que se puede verificar que no se re-codifico nada.** Antes de mutar, el metodo de
escritura se probo contra los archivos originales: `json.dumps(obj, ensure_ascii=False, indent=2)` con
terminadores CRLF **y sin newline final** reproduce ambos bytes idénticos (2.651 y 836). Sobre esa base se
cambiaron solo las claves dictadas, y el `git diff --numstat` lo confirma: `etiquetas.json` 15/15 y
`muestra.json` 3/3, con el resto del objeto JSON comparado clave por clave e identico. `status` sigue
**BORRADOR**.

**Rectificacion numero uno, y es contra mi propio texto de arriba.** Donde §POST y la nota de disposicion
dicen que «las tres piezas del piloto conservan su sha de partida», eso fue cierto hasta este acto y ahora
no: con el dictado, `muestra.json` paso a sha256 de disco `07bb440b94002675…` y `etiquetas.json` a
`4ffbb120ef94b982…`. `protocolo.json` sigue intacto en `fa327b5887ac36cd…`. Y hay una segunda capa que ya
esta documentada en el checkpoint del 2026-09-30: los shas **de blob** difieren de los de disco por
`core.autocrlf=input`, asi que la tabla de esa tanda (disk `bf72272a…` / blob `276bda1b…` para las etiquetas)
queda vencida por contenido, no por instrumento. No la re-escribo: es evidencia cerrada de otra sesion, y se
le declara al lado.

**Dos interpretaciones que yo puse y que usted puede vetar, separadas del dictado.** (i) Sus dos `n/a`
quedaron escritos como `importance: null`, porque la rubrica de `protocolo.json` solo define
`alta|media|baja` y un literal `n/a` ampliaria el dominio sin mandato. Consecuencia medida y no escondida:
`null` significa ahora dos cosas distintas en el mismo archivo — «sin revisar» y «no aplica» — y se
distinguen solo por `review_status` y `reviewed_at`, no por el propio campo. **Deuda nueva con dueño**: la
rubrica de `protocolo.json` no modela «la importancia no aplica a una etiqueta negativa»; o se le anade un
cuarto valor o se fija la convencion `null` por documento. (ii) `review_status` paso de `sin_revisar` a
`revisada`: esa palabra no estaba dictada en ninguna parte, la puse yo como la representacion minima del
hecho, y se cambia con una linea suya.

**Rectificacion numero dos, tambien mia.** Anuncio que el guard `unreviewed_not_frozen` «deja de protestar»
con los tres campos llenos. Es impreciso: medido sobre los archivos reales, con `status: BORRADOR` el guard
da **ok** pase lo que pase con el review — solo muerde cuando el estado es `CONGELADA`. Lo que si queda
probado, y con contrafactual, es la otra direccion, sobre **copias en `temp/`** (los versionados no se
tocaron): una copia en `CONGELADA` con el review lleno da `check_status OK` y EXIT **0**; la misma copia con
el review vaciado da `FALLO` y EXIT **1**. O sea, congelar hoy pasaria, y la puerta tiene dientes.

**Lo que instrumento y suites dicen hoy, corrido sobre el árbol etiquetado.**
`python scripts/evaluate_jev_pilot.py check --muestra … --etiquetas …` → `check_status: OK` con los cinco
guards en verde (`schema`, `content_sha`, `split_disjoint`, `labels_not_in_payload`, `unreviewed_not_frozen`)
y `counts {total 4, dev 2, eval 2, excluidos 1}` intactos — los `sanitized_sha256` de los fragmentos no se
movieron, que es lo que habria roto la transcription. `pytest tests/quality_gates/jev_pilot
tests/quality_gates/decision_client -q` → **101 passed**.

**Lo que NO hice en este acto:** el paso `BORRADOR → CONGELADA` (espera su palabra explicita), el acuerdo de
las cuatro filas todavia pendientes del protocolo (`suficiencia_minima`, `margen_vs_deepseek`,
`tratamiento_abstenciones`, `revision_humana` — las tres primeras dependen del recuento de `pertinente`, que
ya existe en las etiquetas: dos de cuatro), y el commit de la tanda de codigo mas esta transcription. Con el
commit, la cifra canonica de `AGENTS.md` pasa de 4.699 a **4.706** (medido: `grep -rE "^\s*def test_" tests
--include=*.py` en el arbol contra `git grep -c` sobre HEAD) y ese archivo requiere instruccion suya aparte.

---

## Nota de cierre 2026-10-02, segunda sesion del dia — los umbrales quedan ESCRITOS en el protocolo, la
## muestra sigue en BORRADOR y la cifra canonica queda estampada

**Lo que cierra esta nota.** La tanda anterior dejaba cuatro filas pendientes y la convencion de los null. Esta
sesion escribe esas filas en `protocolo.json`. No es fase de JEV ni de VCF: FASE-A/B/C/RELEASE siguen sin
ejecutarse y `dependencias-fases.md` no se toco.

**Los valores escritos y de donde venia cada uno.** Dos procedencias distintas, separadas: las **filas 1-6 las
acepto por clave usted el 2026-10-02** (D-D parcial, acta en el paquete de decision de esta misma carpeta) y
**las filas 7-10 y las convenciones las dicta la pegada de cierre de hoy**, que es otra sesion del mismo dia.

| Clave | Lo que quedo escrito | Procedencia |
|---|---|---|
| `limites_gasto.llamadas` | `12` | fila 1, aceptada por clave el 2026-10-02 |
| `limites_gasto.tokens_in` / `tokens_out` | siguen `null` | fila 2, aceptada el 2026-10-02: el techo pide medir la recuperacion una vez |
| `limites_gasto.usd` | sigue `null` | fila 3, aceptada el 2026-10-02: sin tabla de precios nombrada |
| `parametros.timeout_s` | `30` | fila 4, aceptada el 2026-10-02 (presupuesto total por llamada, no por intento) |
| `criterios_adopcion.latencia_max` | `30000` | fila 5, aceptada el 2026-10-02 (ms por llamada) |
| `criterios_adopcion.cobertura_min` | `0.95` | fila 6, aceptada el 2026-10-02, sobre el denominador publicado de 4 |
| `criterios_adopcion.suficiencia_minima` | `0.5` | fila 7, decidida en la pegada de hoy: 2 de 4 pares pertinentes |
| `criterios_adopcion.margen_vs_deepseek` | sigue `null`, con su **unidad** escrita en la nota | fila 8, decidida hoy: diferencia absoluta de score, no de ratio; el numero espera el `score()` del runner de FASE-B. La fila cierra en su unidad, no en su valor |
| `criterios_adopcion.tratamiento_abstenciones` | «contadas como fallo de recuperacion, no como insuficiente; publicadas en denominador aparte» | fila 9, la propuesta del material §3 aceptada en la pegada de hoy |
| `criterios_adopcion.revision_humana` | «obligatoria; designado: jhon (2026-10-02, acta en `PREPARACION-DECISION-2026-10-02/`)» | fila 10: el **nombre** viene del dictado del 2026-10-02 («revisor: yo»), escribirlo en el protocolo es el acto de hoy |
| `limites_gasto.motivo` | re-escrito con los dos motivos separados | acompana a las filas 2 y 3, que siguen `null` |
| `nota` | enmendada **conservando su frase de bloqueo** | convencion de los null, unidad del margen, denominador publicado y los null que siguen bloqueando FASE-C |

Ningun valor de la tabla sale de una sesion de codigo: los unicos numeros nuevos de hoy son los que usted dicto
en la pegada. Lo que no estaba decidido —el numero del margen— queda `null`, no rellenado.

**Metodo, y su prueba antes de escribir.** `json.dumps(obj, ensure_ascii=False, indent=2)` con terminadores CRLF
**y sin newline final** reproduce el `protocolo.json` original byte a byte (1.311 B, 45 CR). Sobre esa receta se
muto y se re-escribio, asi que no hay re-codificacion de texto ajeno. `git diff --numstat` de la pieza: **9/9**,
y las nueve lineas son exactamente las claves de la tabla —`usd`, `tokens_in`, `tokens_out` y
`margen_vs_deepseek` no aparecen en el diff porque siguen `null` y no se movieron.

**Sha nuevo de `protocolo.json`.** En disco: `b656f8b46bf0862890f4e1cb53194dceec3994026776448026c31f8d46b7f04f`
(2.465 B / 45 CR / 45 lineas, sin newline final; medido dos veces, con `hashlib` y con `sha256sum`). Al
commitearse, `core.autocrlf=input` normaliza el blob a LF, asi que **el sha de blob no casa con el de disco** y
se publican los dos.

**La tabla disk/blob del 2026-09-30 queda vencida por contenido, solo en la fila de `protocolo.json`.** Esa
tabla decia disk `fa327b5887ac36cd…` / blob `654b37d212b90299…` para el protocolo; el disco ya no es esos bytes.
**No la re-escribo**: es evidencia cerrada de otra sesion y se la declara al lado, como se hizo con la tanda de
las etiquetas. Las otras dos piezas del piloto no se movieron ni un byte —`muestra.json` sigue en
`07bb440b94002675…` y `etiquetas.json` en `4ffbb120ef94b982…`, re-medido despues de la ultima escritura de esta
sesion.

**El congelado NO se ejecuto, y sigue con dueno.** `muestra.json` conserva `status: BORRADOR`; el paso a
`CONGELADA` espera su palabra explicita. Lo que si se midio, sobre **copias en `temp/`** y sin tocar los
versionados: copia en `CONGELADA` con el review lleno → `check_status OK`, EXIT **0**; la misma copia con el
review vaciado → `FALLO` con el guard `unreviewed_not_frozen` en rojo, EXIT **1**. O sea, congelar hoy pasaria,
y la puerta tiene dientes.

**Las dos interpretaciones que la tanda anterior puso quedan hoy documentadas en el protocolo.** (i)
`importance: null` en `etiquetas.json` se lee **«no aplica» al par**, no «sin revisar»: eso resuelve la doble
lectura del null que dejo la transcription, y la rubrica sigue sin cuarto valor. (ii) `review_status: revisada`
es la palabra con la que esa transcription represento su firma, no un valor dictado. Las dos viven en la `nota`
de `protocolo.json` y las dos son vetables por usted con una linea.

**Consecuencia aritmetica declarada, no corregida.** `cobertura_min 0.95` sobre un denominador de 4 exige 4 de
4: un solo par sin etiqueta la rompe. Es lo que el material de preparacion ya advertia en su columna de
revisión; la fila se acepto igual y aqui queda dicho.

**Cifra canonica.** `AGENTS.md` pasa de 4.699 a **4.706** y su fila `quality_gates` de 870 a **877**. Medido con
el metodo de la casa: `grep -rE "^\s*def test_" tests --include=*.py` = **4.706** en el arbol y
`git grep -c -E "^\s*def test_" HEAD -- tests` sumado por awk sobre `4621049` = **4.706**; la suma de las 22
filas de la tabla da 4.706 con un instrumento que enumera los sumandos. La atribucion por archivo y la nota de
la ronda aparcan en `docs/cobertura-historia.md`. Queda declarado aqui, porque es lo que la hace necesaria: el
+7 lo trajo el commit `4621049` de hoy y ese commit no llevo `AGENTS.md` entre sus rutas, asi que la cabecera
estaba vencida desde entonces. **Esta sesion no escribio ningun test ni toco `tests/`**: solo estampa la cifra.
Y como su alcance fijo que en `AGENTS.md` cambian solo la cabecera y la fila, la prosa de la nota vieja sigue
diciendo «los dos comandos dan 4,699» referida a `9181197`: esa clausula queda vencida y se declara, no se
re-escribe.

**Lo que NO hizo esta sesion.** Ninguna fase de JEV ni de VCF; no congelo, no etiqueto, no infirio; ninguna red,
ninguna API de inferencia, ninguna credencial, nada instalado; ninguna escritura en `scripts/**`, `tests/**`,
`modules/**`, `.agents/**`, `.cursorrules`, `VERSION.yaml`, `CHANGELOG.md`, `REGISTRY.md`, `.gitignore`,
`tmp_test/**`, `.opencode/refs_baseline.txt`, `.opencode/plans/plan_citations_baseline.json`,
`.opencode/wiring_report.json` ni `dependencias-fases.md`; nada bajo
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/`. No corro `--fix` ni `--update-baseline`. Las unicas cuatro
rutas escritas son `protocolo.json`, `AGENTS.md`, `docs/cobertura-historia.md` y este checkpoint.

---

## Acto de congelado 2026-10-02 — D-1 = (a): `muestra.json` queda CONGELADA y el protocolo queda declarado
## *inicial*, no definitivo

**La decision es del operador, dictada en su palabra.** Recibida como «D-1 = (a)» con el rider de declaracion
que se transcribe abajo literal. Esta sesion ejecuto el congelado y **no commiteo ni empuja**: el acto queda en
el arbol de trabajo, en espera de autorizacion explicita, que es como el contrato de ejecucion del plan pide el
commit de muestra y protocolo.

**Lo que se movio.** `status` de `BORRADOR` a **`CONGELADA`** en `muestra.json`. Nada mas: round-trip probado
antes de escribir (la receta `json.dumps(obj, ensure_ascii=False, indent=2)` con CRLF y sin newline final
reprodujo el archivo original byte a byte, 2.660 B / 64 CR, sha de disco `07bb440b94002675…`), y despues de
escribir el objeto completo fue comparado clave por clave con el anterior — `review`, `pairs`, `exclusions` y
`counts` intactos. `git diff --numstat`: **1/1**, una linea. Sha de disco nuevo: `0107a386ae5750cdc0…`
(2.661 B / 64 CR). Su sha **de blob**: `4a8b30c85a88ae4ca7af5f7595cfe8aaa06903eaaec3675614719c6287639539`
(2.597 B / 0 CR). Los dos no casan, y la diferencia son 64 bytes = los 64 CR que `core.autocrlf=input` retira al
indexar. Medido dos veces y por vias distintas antes del commit: desde el indice (`git add` +
`git cat-file blob :<ruta> | sha256sum`, con `git reset -- <ruta>` despues para no llevar la pieza al commit de
los documentos) y por normalizacion propia en memoria; las dos rutas dan el mismo valor. El blob sobrevive al
commit: es propiedad del contenido, no del commit, y se re-verifica contra `HEAD` al cerrar.

**El guard, ahora sobre el estado real.** `python scripts/evaluate_jev_pilot.py check` sobre la pieza versionada
da `check_status OK`, `muestra_status CONGELADA`, los cinco guards en verde y `counts {4, 2, 2, 1}` — o sea el
`content_sha` de los fragmentos sigue casando y `unreviewed_not_frozen` se satisface con el review lleno
(`human_reviewed: true`, `reviewer: jhon`, `reviewed_at: 2026-10-02`). Y el contrafactual deja de ser hipotetico:
una **copia** de la muestra ya congelada, con el review vaciado, da `FALLO` con el motivo «status CONGELADA sin
revision humana con dueno y fecha» y **EXIT 1**. La puerta esta puesta sobre el archivo vivo, no sobre un
ejercicio. `pytest tests/quality_gates/jev_pilot tests/quality_gates/decision_client -q` → **101 passed**; el
assert de `BORRADOR` de la bateria vive en un fixture de `tmp_path` producido por `prepare()`, no en la pieza
versionada, por eso el congelado no le mueve el verde (medido antes de escribir).

**El rider, en las palabras del operador.** `protocolo.json` queda **versionado y aprobado por el humano el
2026-10-02** como *protocolo inicial*, que es lo que `dependencias-fases.md` pide a la entrada de FASE-B; su
`status` sigue **`BORRADOR`** porque la **congelacion final** corresponde al checkpoint de FASE-C, cuando exista
el numero del margen. Queda declarado el **conflicto de letras** entre la fila P3 del README del plan («A con
muestra/protocolo congelados») y la cadena de `dependencias-fases.md` («corpus y protocolo **inicial**
versionados + aprobacion humana» en B; «checkpoint: **congelacion final**» en C): **goberna la cadena**. Y el
campo `status` del protocolo queda registrado como **deuda con dueno**: no lo lee nadie — `PROTOCOLO_SCHEMA`
esta declarado en `scripts/evaluate_jev_pilot.py` y nunca se usa, y el `check` solo toma `--muestra` y
`--etiquetas` —, por tanto hoy **no es verificable**. Su cura toca `scripts/**` y pide una sesion con ese
alcance, no esta.

**Lo que el congelado vence, declarado y no re-escrito.** Las menciones vivas de `BORRADOR` quedan como registro
cerrado de su sesion: seis en este checkpoint, cuatro en `00-paquete-decision.md` y dos en
`SELLOS-ESTADO-2026-10-01/00-parte.md`. Tambien quedan vencidos por contenido `FASE-A/muestra_check.json` (el
veredicto guardado con `muestra_status: BORRADOR`) y los dos `-COPIA-IDENTICA.json` de la preparacion del
2026-09-30, junto con la tabla disk/blob de esa tanda, que hoy desfasa en `protocolo.json` (por la firma de los
umbrales) y en `muestra.json` (por este acto). Nadie lee esos archivos desde codigo: medido con `git grep -ln` de
`muestra_check` y `COPIA-IDENTICA` sobre `scripts` y `tests`, la poblacion es vacia, y el unico assert de
`BORRADOR` en la bateria es de un fixture. Por eso se declaran aqui y no se editan.

**Lo que sigue bloqueado, y no lo quita este acto.** FASE-B necesita ademas la parte (a) de D-B (autorizada, sin
ejecutar, porque escribe en `scripts/decision_client.py`) y el mandato de ejecucion. FASE-C sigue bloqueada por
los tres `null` que el operador acepto dejar: `usd` sin tabla de precios nombrada, `tokens_in`/`tokens_out` con
techo pendiente de medir la recuperacion una vez, y el numero del `margen`, que nace con el `score()` del runner.

**Sha de blob de `protocolo.json`, cerrado con esta linea.** En `e507193` el archivo esta en disco con
`b656f8b46bf0862890f4e1cb53194dceec3994026776448026c31f8d46b7f04f` (2.465 B / 45 CR) y en el blob con
`fd9a77286af1e61f0720b66fdd3be9ee4ba4a37d141fe2212b50ba31002ad96d` (2.420 B / 0 CR), medido con
`git cat-file blob HEAD:… | sha256sum` sobre el commit y no de memoria. Con esto queda cerrada la frase de la
nota de umbrales que prometia los dos: los dos estan, al lado, en el mismo artefacto.

**D-2 ejecutada en el mismo acto (letra (c), decidida por el operador).** Se corto en `AGENTS.md`
`§Cobertura por Modulo` la prosa fechada que iba de «En el commit que lleva esta nota los dos comandos dan
4,699» hasta «…dos veces cada uno.»; quedan intactas las tres frases de definicion y el parrafo que manda el
historial a `docs/cobertura-historia.md`, y no se movieron la cabecera (4,706) ni la fila `quality_gates` (877).
La razon, la medicion de perdida y el texto rescatado verbatim aparcan en `docs/cobertura-historia.md`, que es su
fuente unica. Lo que queda vencido por contenido con este acto: la tabla disk/blob del 2026-09-30,
`FASE-A/muestra_check.json` y los dos `-COPIA-IDENTICA.json` (medido: ningun archivo de `scripts/` o `tests/` los
lee), y las menciones vivas de `BORRADOR` en este checkpoint, en `00-paquete-decision.md` y en el sello del
2026-10-01 -registradas arriba, no re-escritas-.

**Rutas escritas en este acto y una inconsistencia del mandato.** `muestra.json`, `AGENTS.md`,
`docs/cobertura-historia.md` y este checkpoint. El parrafo de autorizaciones listaba «SOLO» tres rutas y
`docs/cobertura-historia.md` no estaba entre ellas, pero el propio PUNTO 2 manda aparcar ahi la razon de la poda y
el Paso 3 la nombra en el commit de documentos: se escribio por esas dos instrucciones explicitas y se declara
aqui el hueco en la lista, no se resolvio en silencio.

---

## Acto 1 del 2026-10-02 — la nota de congelado queda vencida por su propia firma, D-B se rectifica y el

## disparador del margen ya se cumplio**Rectificacion numero uno, contra un texto mio publicado.** La nota del acto de congelado, en esta misma
carpeta, escribe que «esta sesion ejecuto el congelado y **no commiteo ni empuja**: el acto queda en el arbol de
trabajo, en espera de autorizacion explicita». Eso fue cierto hasta el mandato siguiente y hoy no: el congelado se
commiteo en `e9c8a0d` y se empujo. La frase queda como registro de su momento y **no se re-escribe**, que es la
regla de la casa sobre evidencia publicada; se declara aqui, al lado. Medido despues del push: rango empujado
`e507193..e9c8a0d` sobre dos commits (`5665fac` documentos, `e9c8a0d` congelado) y 14 objetos, `4621049`,
`e507193` y `6c89f4d` siguen siendo ancestros, paridad `0 0` y arbol limpio.

**Rectificacion numero dos, y es contra mi reporte de la tanda anterior.** Dije que FASE-B «necesita la parte (a)
de D-B». Leido el codigo versionado, la pata (a) **ya esta ejecutada**: `scripts/decision_client.py` expone
`provider_requested`, `model_requested` y `elapsed_ms` -los tres en el dict publicado, saliendo `provider_requested`
del entorno que nombro el llamador, `model_requested` del pin declarado y no de lo que reporta el proveedor, y
`elapsed_ms` en `None` cuando no hubo llamada-, y eso viajo en `4621049` con sus siete funciones de test. La propia
costura declara ademas que `attempts`, `error_kind` y `usage_normalized` **no** le pertenecen: esa es la pata (b),
y es lo que FASE-B hereda. El reportador confadio la letra del paquete de decision con el estado del arbol.

**Hallazgo estampado: el disparador del margen se cumplio sin que nadie lo declarara.** La decision del 2026-10-02
postergaba el numero «hasta que exista el `score()` del runner (FASE-B)». Medido: `score(numerator, denominator)`
existe en `scripts/evaluate_jev_pilot.py`, publica numerador, denominador y `motivo`, trata el denominador cero
como caso explícito en vez de un cero mudo, `metrics()` ya arma los cuatro cocientes (recuperacion,
precision_entre_propuestas, recall_importante_candidatos, extremo_a_extremo) y `test_jev_pilot_offline.py` los
ejercita con siete funciones dentro de las 101 verdes. Lo que sigue sin existir es la pierna de ejecucion: `run` y
`decide` se niegan con EXIT 2 porque piden preflight, presupuesto y autorizacion literal. Pero eso no afecta al
umbral, que es una decision de producto sobre una escala ya definida -con denominador 4 las unicas diferencias
absolutas posibles son 0,25, 0,50, 0,75 y 1,00-. Un aplazamiento cuya condicion se cumplio deja de ser aplazamiento:
o se fija el numero, o se declara que sigue esperando otra cosa. Dueno: el operador.

**Lo que tambien se hizo aqui, en AGENTS.md y con letra (b).** El parrafo «El historial de rondas» dejo de llevar
rango de fechas: decia «las notas medidas entre 2026-09-11 y 2026-10-01» cuando el archivo de destino ya tenia notas
del 2026-10-02. No se volvio a anclar la cota -eso es la via (a) y la habria vuelto a vencer al commit siguiente-: se retiro
el literal y el parrafo ahora apunta al archivo y describe el orden. Medido despues del cambio:
`grep -c "2026-09-11 y 2026-10-01" AGENTS.md` = **0** (la unica mencion versionada que queda es la cita con la que
`docs/cobertura-historia.md` declara su propio cierre), la cabecera `(4,706 funciones totales)` = 1, la fila
`quality_gates | 877` = 1, diff **4/3** y 538 lineas pasan a 539. La razon de la poda y su prueba de perdida estan
aparcadas en `docs/cobertura-historia.md`, que es la fuente unica; su nota de residuo «no corregido» se dejo intacta
y el cierre se agrego debajo como nota fechada.

**Rutas escritas en este acto:** `AGENTS.md`, `docs/cobertura-historia.md` y este checkpoint. `muestra.json`,
`protocolo.json` y `etiquetas.json` no se tocan: los dos ultimos conservan `4ffbb120ef94b982…` y `b656f8b46bf08628…`
en disco. Sin red, sin inferencias, sin instalar, sin `--fix` ni `--update-baseline`, sin escribir en `scripts/**`,
`tests/**` ni `modules/**`, y sin tocar `dependencias-fases.md` ni nada bajo
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/`.
