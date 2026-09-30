# Material para la decision humana de P1 (fila 2 del registro): muestra BORRADOR y umbrales propuestos

Estado de este documento: **preparacion**. No etiqueta, no congela, no atribuye revision humana. Las tres
piezas del plan se copian aqui **identicas** (sha en `00-checkpoint-de-preparacion.md`) y `muestra.json`,
`etiquetas.json` y `protocolo.json` del plan **no se tocaron**: `git status` los muestra intactos.

## 1. La muestra disponible, tal como esta

`muestra-COPIA-IDENTICA.json` - `schema jev-pilot-muestra/v1`, `status BORRADOR`,
`review = {human_reviewed: false, reviewer: null, reviewed_at: null}`, `corpus_source own:lecciones_index`,
`temporal_cut 2026-09-12`, `counts {total 4, dev 2, eval 2, excluidos 1}`.

Cuatro pares, con sus dos shas declaradas (original y saneado):

| pair_id | split | leccion | plan de origen | fase | fragmento |
|---|---|---|---|---|---|
| `REFACTOR-WHATSAPP-ENTREGA-2026-09-18::D-AJUST.1` | eval | D-AJUST.1 | REFACTOR-WHATSAPP-ENTREGA-2026-09-18 | FASE-B | 80 caracteres |
| `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20::D-AJUST.2` | dev | D-AJUST.2 | VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 | FASE-C | 77 caracteres |
| `VERIFICADOR-ESCRITURA-QMIND-2026-09-20::D-NC2` | dev | D-NC2 | VERIFICADOR-ESCRITURA-QMIND-2026-09-20 | FASE-B | 80 caracteres |
| `EVALUACION-JEV-TYPESAFE-2026-09-21::D-AJUST.4` | eval | D-AJUST.4 | EVALUACION-JEV-TYPESAFE-2026-09-21 | FASE-C | 93 caracteres |

Exclusion declarada en la propia muestra: `EVALUACION-JEV-TYPESAFE-2026-09-21::D-NC6`, motivo "enunciado
truncado del indice, sin revision".

`etiquetas-COPIA-IDENTICA.json` - `schema jev-pilot-etiquetas/v1`, `review_status sin_revisar`, cuatro
etiquetas con `label`, `importance`, `reviewer` y `reviewed_at` **todos en null**. La rubrica que hay que
aplicar es la del protocolo: `label` en {pertinente, no_pertinente, insuficiente} e `importance` en
{alta, media, baja}. Lo que no puede hacer esta sesion (ni ninguna): escribir esos valores.

## 2. D-B: re-medida hoy la premisa de la trazabilidad, y sale partida por la mitad

La fila 1 del registro dice "0 de 4 shas casan". Re-medido el 2026-09-30 sobre tres poblaciones distintas, y
el resultado **no es un cero uniforme**: una de las dos mitades del par si es verificable.

Poblacion 1, arbol versionado (`git ls-tree -r HEAD`: **3.190 rutas**, que son **3.110 blobs**
distintos - frente a los 2.988 ficheros que midio la tanda del 2026-09-29; la diferencia es el crecimiento
del arbol, no del instrumento):

| pair_id | `original_sha256` (prefijo) | casa con algun blob de HEAD |
|---|---|---|
| REFACTOR-WHATSAPP...::D-AJUST.1 | `3be902d85bb1c426` | **no** |
| VERIFICADOR-CONTEXTO...::D-AJUST.2 | `7c22017d5c7d9c32` | **no** |
| VERIFICADOR-ESCRITURA-QMIND...::D-NC2 | `8790a0996be513ef` | **no** |
| EVALUACION-JEV...::D-AJUST.4 | `1d9617b2d0f459e9` | **no** |

Poblacion 2, arbol de trabajo completo (9.307 ficheros leidos, excluyendo `tmp_test/`, `.venv-wsl/`,
`node_modules/`, `__pycache__/`, `.git/` y `venv/`): **0 de 4 tambien**.

Poblacion 3, la otra mitad del par - y aqui el cero **no** se sostiene. Los cuatro `sanitized_sha256` se
re-calculan con la funcion del propio runner (`sha256_text` en `scripts/evaluate_jev_pilot.py:30`) sobre el
`input_fragment` que la muestra guarda:

    REFACTOR-WHATSAPP...::D-AJUST.1   IGUAL    VERIFICADOR-CONTEXTO...::D-AJUST.2   IGUAL
    VERIFICADOR-ESCRITURA-QMIND...::D-NC2 IGUAL  EVALUACION-JEV...::D-AJUST.4       IGUAL

**4 de 4 verificables contra 0 de 4.** Consecuencia para la decision (a)/(b), y es la razon de este
documento: lo que hoy no existe es la pata `par -> documento fuente`, no la pata `par -> texto saneado`. Y dos
de los cuatro pares apuntan a planes que ya no estan en la ruta que su nombre declara
(`VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` y `EVALUACION-JEV-TYPESAFE-2026-09-21`, ambos bajo `Archives/`),
con lo que la salida (a) tendria que **re-anclar** el par leccion-documento despues del archivado, no solo
escribir un fichero de candidatos. La salida (b) (enmendar la clausula) tendria que decir explicitamente que
AC3 pasa a gobernar el texto saneado y la cita de origen, y no el sha del original.

Ninguna de las dos se aplico: son decision del operador, y la (b) necesita instruccion literal con los
archivos que toca.


## 3. Los umbrales propuestos, con su justificacion y su estado

`protocolo-COPIA-IDENTICA.json` esta en `status BORRADOR` y su propia nota dice: "Los valores nulos son
a-decidir por el operador antes de cualquier inferencia; bloquean FASE-C". Hoy estan en null
`cobertura_min`, `margen_vs_deepseek`, `tratamiento_abstenciones`, `suficiencia_minima`, `latencia_max`, y los
cuatro `limites_gasto` (`usd`, `llamadas`, `tokens_in`, `tokens_out`, con motivo "sin presupuesto aprobado");
`revision_humana` si tiene valor: "obligatoria, pendiente de designar responsable".

Lo que sigue son **propuestas de esta preparacion para que una persona las acuerde o las rechace**. No se
escribieron en `protocolo.json`, no congelan nada y no son un acuerdo.

| Umbral | Propuesta | De donde sale el numero | Que tendria que revisar la persona |
|---|---|---|---|
| `limites_gasto.llamadas` | **12 llamadas como techo duro** | 4 pares x 3 brazos (comparacion obligatoria del plan: busqueda fria, DeepSeek y Jev; Anthropic excluido). Con `retry_policy.max_retries = 0` (valor ya escrito en el protocolo) cada llamada es 1 intento, asi que 12 llamadas = 12 intentos | Si los brazos se corren tambien sobre el split `dev` (2 pares) el techo sube a 12 igual, pero el plan pide "el mismo conjunto elegible para los tres brazos": confirmar que no se corre sobre `total + excluidos` (5 -> 15) |
| `limites_gasto.tokens_in` / `tokens_out` | **sin numero hasta fijar el prompt de recuperacion** | El plan del hermano deja `top-k` como regla de recuperacion, y aqui no hay ninguna corrida de `triage` con ese top-k: el costado de entrada depende de los caracteres del indice recuperado, no del fragmento (77-93 caracteres). Inventarlo ahora seria un default de dinero, que la casa prohibe ("No Defaults in Money") | Pedir la corrida de recuperacion una vez, medir tokens reales y convertir el techo en un multiplo declarado |
| `limites_gasto.usd` | **en null hasta que el operador nombre la tabla de precios** | Medido: no hay precios por token de Jev ni de DeepSeek en `config/provider_registry.yaml` ni en `config/`. La unica base de coste versionada del repo es la del proveedor Gemini de `modules/providers/` | Fijar la fuente de precios (URL + fecha + los dos modelos) o declarar el presupuesto en llamadas/tokens, que si son medibles |
| `parametros.timeout_s` | **30 s por llamada** (hoy null) | Es el valor medido del SDK del plan (`RetryPolicy(..., timeout=30.0)`, maestro §Reintentos, sonda offline del 2026-09-21), y el plan aclara que `timeout` es presupuesto **total por llamada**, no por intento | Confirmar que el piloto lo quiere igual que el default del SDK, o mas estricto |
| `criterios_adopcion.latencia_max` | **dejarla por debajo del timeout, no encima**: propuesta 30.000 ms por llamada | Si `latencia_max == timeout`, la latencia no goberna nada: todo lo que no es timeout pasa. La casa ya decide asi sus gates (umbral explicito por debajo del limite del instrumento) | Elegir el numero operativo (p. ej. 10.000 ms) sabiendo que es decision de producto, no de medicion |
| `criterios_adopcion.cobertura_min` | **0,95 sobre los pares etiquetados**, con denominador publicado | Es el patron del repo: `evidence_coverage >= 95 %`. Ojo: la muestra es 4 pares, asi que 0,95 sobre 4 es 4 de 4 - un solo par sin etiqueta ya la rompe | Decidir si el piloto se juzga con cobertura de gates (4/4 obligatorio) o con una regla de muestra pequena explicita |
| `criterios_adopcion.suficiencia_minima` | **no se puede proponer sin la etiqueta humana**: el numerador es "cuantos pares un humano juzgo `pertinente`", y hoy esa cuenta es 0 porque las cuatro etiquetas estan en null | Medido en `etiquetas.json` | Queda a-decidir despues de la firma; cualquier numero hoy seria una inferencia sobre texto no revisado (prohibido por la orden) |
| `criterios_adopcion.margen_vs_deepseek` | **se propone como diferencia minima absoluta de score, no de ratio**, y el numero queda pendiente del `score()` del runner | `evaluate_jev_pilot.py` ya tiene `score(numerator, denominator)` y `metrics(recovery, classification, e2e)` con denominadores separados; un ratio sobre 4 pares tiene un salto minimo de 0,25 por par, o sea "1 par de diferencia" y "margen del 20 por ciento" son el mismo numero | Fijar la unidad antes del numero: con n=4 un margen porcentual no distingue nada |
| `criterios_adopcion.tratamiento_abstenciones` | **contadas como fallo de recuperacion, no como `insuficiente`**, y publicarse en denominador aparte | La rubrica ya separa `insuficiente` de `no_pertinente`; la leccion L-R.3 del propio plan exige "denominadores separados por metrica" | Confirmar que la abstencion no se descarta (el plan prohibe "descartar filas para mejorar metricas", prompt de FASE-C item 4) |
| `criterios_adopcion.revision_humana` | **ya esta escrita**: obligatoria, pendiente de designar responsable | `protocolo.json` | Nombrar a la persona. Sin ese nombre, P1 no se destraba y FASE-B sigue bloqueada |

## 4. Lo que esta preparacion dejo dicho y no hecho

- No se etiqueto ningun par (prohibido por la orden y por AC3).
- No se congelo la muestra: `status` sigue `BORRADOR`.
- No se atribuyo revision humana: `human_reviewed` sigue `false`, `reviewer` y `reviewed_at` siguen `null`.
- No se escribieron los umbrales propuestos dentro de `protocolo.json`: quedan aqui, con su justificacion, a
  la espera de que una persona los acuerde, los cambie o los rechace.
- No se llamo a ninguna API ni se instalo nada.
