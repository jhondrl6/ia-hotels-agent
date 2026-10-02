# Paquete de decision del operador — JEV, 2026-10-02

Sesion de reconciliacion documental sobre la pareja `EVALUACION-JEV-TYPESAFE-2026-09-21` (JEV) y
`VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` (VCF). **No es una fase de ninguno de los dos planes.** Este
archivo no decide nada: empaqueta las dos unicas peticiones que hoy desbloquean la cadena, cada una con su
dueno, su puerta y que habilita exactamente al responderse.

Lo que no es esto: no es preparacion (los tres items de la preparacion se corrieron el 2026-09-30 y su
expediente vive en `../PREPARACION-DECISION-2026-09-30/`), no es re-transcripcion (las cifras y los costes de
cada decision viven en su fuente unica y aqui se referencian por nombre de archivo), y no es autorizacion
(ninguna salida queda aplicada en codigo; ver `02-checkpoint.md`).

Las mediciones que sostienen el estado de partida —HEAD de la sesion, estado del arbol, paridad con
`origin/master`, `--provider-status`, las dos selecciones de pytest, el `--check` del indice y del wiring, el
rapido y los shas de las tres piezas del piloto— estan en `01-re-medicion-2026-10-02.txt`, cada salida con su
comando literal encima.

---

## D-B — elegir la salida del gap de contrato

| | |
|---|---|
| **Dueno** | Operador (fila 7 del registro unificado del hermano: «Dueno: Operador») |
| **Puerta** | Su eleccion escrita. No hay capacidad tecnica que esperar: la costura existe, esta versionada y su seleccion de pruebas esta verde hoy |
| **Fuente unica del dossier** | `../PREPARACION-DECISION-2026-09-30/01-gap-de-contrato.md` — ahi estan el contrato pedido, la lectura del codigo, cada campo con su estado medido y el coste de cada salida. Este archivo **no** los copia |
| **Que habilita al responderse** | Que se redacte el mandato de JEV FASE-B con la interfaz real en lugar del delta abierto. Mientras no se elija, FASE-B sigue bloqueada por una decision, no por una dependencia |

Las tres salidas, en las palabras del propio dossier:

- **(a)** extender la costura del hermano de forma aditiva y compatible con sus consumidores.
- **(b)** mover el ledger de intentos y la contabilidad por llamada al runner propio de JEV
  (`scripts/evaluate_jev_pilot.py`).
- **(a)+(b)** la particion que el dossier deja escrita y **no** aplico: una pata para el trio
  pedido/efectivo con el tiempo por llamada, la otra para los contadores que solo observa quien invoca.

**Ninguna de las tres se aplica en esta sesion.** Y hay que saber que elegir **(a)** o **(a)+(b)** toca
`scripts/decision_client.py`, que es a la vez:

- la superficie de la deuda **D7** del hermano —«activar Jev como segundo proveedor detras de
  `decision_client.py`», cuyo disparador medido en la misma fila del registro es *credencial + presupuesto*,
  y que el registro llama «el porton»;
- la superficie de su geometria **S10** —donde vivira el `import` del SDK cuando D7 se active, que el hermano
  registro con dueno y disparador en vez de decidirla en silencio.

O sea: la eleccion de D-B no es un detal del piloto. Es la primera piedra de D7, y por eso viaja con la
advertencia de la fila 7 —no se adelanta escribiendo codigo.

**Ambiguedad que hay que resolver al responder, declarada en vez de acomodada.** Las letras `(a)` y `(b)` estan
sobrecargadas en el expediente del 2026-09-30: `01-gap-de-contrato.md` las usa para el eje *donde se produce
el campo* (costura vs runner), y `02-material-muestra-y-umbrales.md` §2 las usa para un eje distinto —el de la
trazabilidad del par (`par -> documento fuente` frente a enmendar la clausula de AC3). **D-B se responde con
la taxonomia de `01-gap-de-contrato.md`.** Si la eleccion llega como «(a)» sin nombre del eje, hay que
preguntar a cual de los dos se refiere antes de redactar el mandato.

---

## D-D — designar a la persona que etiqueta la muestra y acuerda los umbrales

| | |
|---|---|
| **Dueno** | La persona designada por el operador. Hoy no existe: `protocolo.json` → `criterios_adopcion.revision_humana` = «obligatoria, pendiente de designar responsable» |
| **Puerta** | Su nombre y su firma. Ninguna sesion puede producirla: etiquetar es el acto que la orden reserva a un humano (AC3 y la leccion L-R.4 del propio plan) |
| **Fuente unica del material** | `../PREPARACION-DECISION-2026-09-30/02-material-muestra-y-umbrales.md` — ahi estan la muestra con sus pares y sus dos shas, la rubrica a aplicar, cada umbral propuesto con de donde sale y que tendria que revisar la persona. Este archivo **no** los copia |
| **Que habilita al responderse** | Congelar la muestra y el protocolo. Sin esa firma la muestra queda en **BORRADOR** y **JEV FASE-B no puede congelar corpus** (`requirements-pilot.txt` y `entorno.json` se congelan en B); los umbrales en `null` de `protocolo.json` bloquean ademas FASE-C por su propia nota |

Medido hoy, no copiado del expediente: `etiquetas.json` → `review_status` = `sin_revisar`, y sus entradas de
etiqueta tienen `label`, `importance`, `reviewer` y `reviewed_at` todos en `null` (el conteo esta en
`01-re-medicion-2026-10-02.txt`). `muestra.json` → `review.human_reviewed` = `false`. **A esta sesion no le
puede atribuir ninguna etiqueta**: no etiqueto, no acordo umbrales y no congelo nada.

Nota de grafia, porque el expediente usa las dos: la clave que gobierna la muestra es `review.human_reviewed`
en `muestra.json`, y la que gobierna las etiquetas es `review_status` en `etiquetas.json`. El checkpoint del
2026-09-30 escribe `human_reviewed` al hablar de las etiquetas; son dos objetos distintos y ambos siguen en su
valor de borrador.

---

## Orden entre las dos

No son secuenciales. **D-D** destraba el congelado del corpus y no toca codigo; **D-B** destraba el mandato de
FASE-B y, segun la salida elegida, abre una discusion de geometria en el plan hermano. Pueden responderse en
cualquier orden, pero FASE-B necesita **las dos**: sin muestra congelada no hay corpus, y sin salida elegida no
hay interfaz contra la que escribir el runner.

## Lo que esta sesion dejo explicitamente sin tocar

Ninguna fase de JEV ni de VCF. Ninguna API de inferencia. Ninguna credencial. Ningun write y ningun push. Las
piezas del piloto (`muestra.json`, `etiquetas.json`, `protocolo.json`) conservan su sha de partida, medido PRE
y POST en `01-re-medicion-2026-10-02.txt`.

---

## Respuesta del operador, 2026-10-02 — REGISTRADA, no ejecutada

Texto literal recibido: «D-B = (a)+(b) con eje de gap, (a) autorizada ahora y (b) atada al mandato de FASE-B ·
D-D = revisor `<nombre>`, umbrales: 1-6 aceptadas, 7-10 quedan pendientes de la etiqueta».

### D-B — RESUELTA: la partición con dos tiempos

El operador eligio la particion que `01-gap-de-contrato.md` §4 dejaba escrita y no aplicaba, y **nombro el eje**
(«con eje de gap»), con lo que la sobrecarga de las letras entre el dossier del gap y el §2 de
`02-material-muestra-y-umbrales.md` queda sin efecto para esta decision: (a)/(b) se leen aqui como *donde se
produce el campo*, no como *trazabilidad del par*.

- **(a)** autorizada ahora. **(b)** atada al mandato de FASE-B, que es de lo que depende segun el propio dossier.
- **Que NO hizo esta sesion**: no ejecuto (a). Su mandato prohibe escribir en `scripts/**` y prohibe ejecutar
  fases, asi que la autorizacion queda como **insumo del mandato de ejecucion**, no como cambio en el arbol.
  Medido: `git status --porcelain` de esta sesion no trae ningun archivo de `scripts/`.
- **Coste que la eleccion arrastra y hay que tener a la vista**: (a) ensancha el **resultado** de
  `scripts/decision_client.py`, que es la superficie donde el hermano activa **D7** y cobra **S10** la geometria
  del `import`. Ejecutar (a) abre esa discusion, no la cierra.

### D-D — PARCIAL: umbrales acordados por clave; la designacion sigue sin nombre

Los ordinales se resolvieron **por clave** porque la posicion no es un ancla estable, y porque el conjunto que
esta sesion habia nombrado como «los que no admiten numero» no coincide con el que sale del orden de la tabla.
Orden medido de la columna clave de la tabla §3 de `02-material-muestra-y-umbrales.md`:

- **Aceptadas (1-6)**: `limites_gasto.llamadas` · `limites_gasto.tokens_in` / `tokens_out` · `limites_gasto.usd` ·
  `parametros.timeout_s` · `criterios_adopcion.latencia_max` · `criterios_adopcion.cobertura_min`
- **Pendientes de la etiqueta humana (7-10)**: `criterios_adopcion.suficiencia_minima` ·
  `criterios_adopcion.margen_vs_deepseek` · `criterios_adopcion.tratamiento_abstenciones` ·
  `criterios_adopcion.revision_humana`

**Consecuencia declarada, porque no es lo que la palabra «aceptadas» sugiere**: aceptar esas seis filas **no**
saca `null` del protocolo. Las filas de `tokens_in`/`tokens_out` y de `usd` proponen justamente quedarse en
`null` con motivo (sin numero hasta fijar el prompt de recuperacion; sin tabla de precios nombrada), y la nota
interna de `protocolo.json` sigue diciendo que sus valores nulos **bloquean FASE-C**. O sea: un D-D parcial no
destraba FASE-C; solo fija el techo de llamadas, el timeout y los dos criterios de latencia y cobertura.

**Lo que de D-D no tiene respuesta**: el **nombre** del revisor. Llego como el literal `<nombre>` de la
plantilla de esta sesion, sin valor. No lo produce ninguna sesion ni puede inferirse: es el unico campo que
depende del operador, y es a la vez lo que mantiene la muestra en **BORRADOR** (con FASE-B sin corpus congelado)
y la fila 10 de la tabla de umbrales. Esta nota **no** lo rellena: se registra el hueco y se para ahi.

### Estado de las dos peticiones despues de esta respuesta

| | Antes | Despues | Siguiente actor |
|---|---|---|---|
| **D-B** | abierta, sin salida elegida | **decidida** en (a)+(b) con dos tiempos; (a) con autorizacion y sin ejecucion | quien abra una sesion con `scripts/**` en alcance |
| **D-D** | sin dueno nombrado y umbrales en bloque | **mitad hecha**: umbrales acordados por clave; **designacion pendiente** | el operador, con el nombre |

### D-D — designacion recibida el 2026-10-02 (segunda respuesta de la tanda)

Texto literal recibido: «D-D = revisor: yo · reviewed_at: la fecha del dia en que etiquete · las cuatro etiquetas
las aplico yo en `etiquetas.json` en cuanto etiquete; se declara en el acta que la revision es del propio dueno
del corpus, sin independencia externa».

- **Designacion: CERRADA.** El operador se nombro a si mismo como revisor de la muestra. Con esto
  `protocolo.json` → `criterios_adopcion.revision_humana` deja de estar «pendiente de designar responsable» —
  **en este registro**, que es donde se dicta; el valor dentro del `protocolo.json` versionado no se toco en
  esta sesion porque esa escritura pertenece al acto de congelar, no al de designar.
- **Lo que la respuesta NO cierra, y por escrito para que no se lea como cierre:**
  - Las **cuatro etiquetas** (`label` + `importance` en `etiquetas.json`) y los tres campos del bloque `review`
    de `muestra.json` siguen en su valor de borrador. Nadie de esta sesion los llena: es el acto reservado al
    revisor por AC3 y por la leccion L-R.4 del plan.
  - El **valor literal de `reviewer`** lo dicta el revisor al etiquetar; en este registro figura en primera
    persona del dictado («yo») y no se transcribe a nombre propio desde aqui.
  - `reviewed_at` queda **reglado, no fijado**: la fecha del dia en que se etiquete. No se estampo una fecha de
    hoy porque la etiqueta no se dio hoy.
- **La contrapartida que el acta debe llevar, declarada por el propio revisor en su respuesta:** la revision es
  del dueno del corpus, **sin independencia externa**. Medido, el hueco que esa frase cubre: el guard
  `unreviewed_not_frozen` de `scripts/evaluate_jev_pilot.py` exige `human_reviewed` y `reviewer` y `reviewed_at`
  los tres llenos, pero **no prueba que el revisor sea humano** — la prohibicion de que lo sea un agente es
  documental (AC3, L-R.4 y la nota del propio protocolo), no verificada por test. Queda registrada como
  superficie sin verificador, con dueño (`scripts/evaluate_jev_pilot.py`) y sin cura en esta sesion.
- **Reversibilidad declarada**, que es la razon por la que se acepta la autorrevision: la muestra son cuatro
  pares y 330 caracteres de fragmentos, asi que si mas adelante se quiere independencia, otra persona
  re-etiqueta y se re-congela sin perder nada del instrumento.

### Estado de las dos peticiones, al cerrar la segunda respuesta

| | Estado | Lo que falta | Quien lo produce |
|---|---|---|---|
| **D-B** | decidida en (a)+(b); (a) autorizada, no ejecutada | mandato de ejecucion sobre `scripts/decision_client.py`, con la discusion S10/D7 que abre | una sesion con `scripts/**` en alcance |
| **D-D** | **designada** y con umbrales acordados por clave | las cuatro etiquetas, el literal de `reviewer`, la fecha real y el paso `BORRADOR → CONGELADA` | el revisor designado (el operador), con sus propias manos |

**Sobre el sello del README de JEV, para quien lo lea manana**: sigue vigente como puntero —el estado de la
pareja se lee en este paquete— pero su cuenta de «dos decisiones pendientes» quedo contestada hoy: una decidida
sin ejecutar, la otra designada sin etiquetar. No se le anadio un segundo sello el mismo dia para no re-escribir
un derivado ya regenerado (el README es corpus del indice) por una cuenta que este archivo lleva mejor; la
rectificacion vive aqui, que es a donde el sello apunta.

