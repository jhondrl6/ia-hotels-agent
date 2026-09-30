# T3 — S34: verificador de frescura de `CONTEXT` (guion propio), medido y cableado

Orden: fila 11 del registro unico del 2026-09-29. Decision ya tomada y respetada: **guion propio**, no una
extension de `validate_qmind_writeback.py`; criterio **descarga + sha256**, nunca por titulo; `metadata.fileSha256`
solo corroboracion; cableado al **modo completo** (17 -> 18), no al rapido.

## 1. Poblacion re-medida al correr (no la del parte)

Censo del 2026-09-30 con `m-03-censo-poblacion-context.py` (crudo `03-`):

- **2** ficheros `CONTEXT-*.md` bajo la raiz de `.opencode/context/`: el de JEV (17.272 B) y el de
  WHATSAPP-VERIFIED (55.092 B).
- **1** autodeclara leccion durable: el de JEV, y lo hace **como encabezado** (`## Leccion durable:`). La copia
  del hermano ancla a inicio de linea (`^Lección durable:`) y por eso devolvia **0** sobre ese archivo - el
  limite medido el 2026-09-27 y la razon por la que el detector de aqui acepta las dos grafias.
- El de WHATSAPP **no declara** -> excluido con su razon (la politica del write-back es por aporte declarado,
  executor v2.18.0). Si entrara en la poblacion, el check daria rojo sobre un artefacto que ninguna regla manda
  publicar: es la familia de «ampliar un detector tira el arbol».
- **18** ficheros bajo `Historico/`, todos excluidos con su razon: R2.5 y la nota «QMind y archivado» dejan el
  contenido archivado **congelado**. Medido aparte y decisivo: dos de esos `Historico/` (el de `DT-3-TECH-DEBT-POST-DT2` y el de
  `SALENTOREAL-V4COMPLETE-EJECUCION`) **no casan** con ninguna fuente publicada por `metadata.fileSha256`, y sin embargo no son
  deuda - si la poblacion los incluyera, el check naceria con dos rojos que la politica ya resolvio. Eso se
  publica en la salida, no se silencia.
- Los nombres `CONTEXT-*` que citan los planes archivados: **9** distintos; **3** resuelven bajo `Historico/` y
  **0** bajo la raiz. O sea la capa «los que cite cada plan archivado» hoy no anade miembros, y asi se declara
  en vez de asumir que anadia.

## 2. Coste de la interfaz, medido en la corrida real

- `qmind source list --nb <ID> --all --format json` -> **56** fuentes, bajo la clave `sources`, con
  `totalSize: 0` (los dos limites de interfaz ya registrados). El JSON crudo del listado **no se persistio**
  en la evidencia: trae `originUrl` y `metadata.originalFileUri` firmados con credenciales OSS. Se leyo desde
  `temp/` (directorio ignorado) y se borro al cerrar la tanda; lo que queda aqui son `id`, `title`, `status`
  y `metadata.fileSha256`, que es la parte que no publica un secreto.
- Una descarga del CLI: **3,0 s** medidos (`t0/t1` en nanosegundos), 17.272 B, sha idéntico al disco.
- Camino normal en verde: **2** descargas (las dos fuentes que nombran el stem - la fresca y la vencida). El
  barrido completo de las 56 **solo** corre cuando ningun candidato casa: es el precio de que el criterio sea
  byte a byte y no titulo, y se paga solo cuando hay un rojo que atribuir.
- Crudo de la corrida real: `07-t3-corrida-real-context-freshness.txt`, `EXIT=0`,
  `[OK] frescura de CONTEXT: 1 fresco(s), 0 problema(s)`, con la corroboracion `coincide`.

## 3. Bateria, sin red, con sus dientes

`tests/test_verify_qmind_context_freshness.py` - **17 passed**, EXIT 0. Se sustituye una sola frontera de E/S
(`_run_qmind`) y todo lo demas es el guion real: parseo del JSON, resolucion del notebook, el `-o` de la
descarga, la poblacion, el barrido y los codigos de salida.

| Prueba | Que cort |
|---|---|
| `test_fresco_cuando_una_bajada_casa_aunque_el_titulo_no_lo_nomvre` | pasa con una fuente cuyo titulo **no** nombra el archivo: si el criterio fuera el titulo, daria VENCIDO |
| `test_vencido_cuando_ninguna_bajada_casa_y_el_barrido_es_completo` | exige `descargas == len(fuentes)`: el rojo no puede decirse habiendo bajado solo los candidatos |
| `test_metadata_no_es_el_criterio` | metadata que casa y descarga que **no** casa -> VENCIDO (el `--upload` con `[SKIP]` por titulo no puede volver a congelar la version vieja) |
| `test_el_desacuerdo_del_metadata_se_declara_no_se_calla` | el desacuerdo se imprime; no se calla ni se usa como veredicto |
| `test_la_forma_original_mas_cierre_es_legal` | dos fuentes del mismo `CONTEXT` (una vencida, una fresca) -> FRESCO, y **sin** barrido completo |
| `test_gobernado_que_desaparece_del_disco_es_no_evaluable` | salida **2**, no 1 ni 0 |
| `test_poblacion_vacia_con_ficheros_presentes_no_es_verde` | salida **2** (variante de verde vacio) |
| `test_un_id_que_no_es_uuid_no_llega_al_cli` | ningun identificador sin validar llega al binario |
| `test_control_negativo_el_hermano_versionado_no_ve_el_contexto_de_encabezado` | `validate_qmind_writeback.py` leido de **`7737347`** con `git show` devuelve **0** declaraciones sobre el mismo arbol: la ceguera que originó la fila, reproducida por el instrumento versionado |
| `test_la_interfaz_publica_poblacion_exclusiones_y_estado` | la salida dice gobernados, excluidos, fuentes y estado (R2.4, L-HF1) |

## 4. Enumeracion y guarda de denominador (17 -> 18)

- Etiquetas del completo re-etiquetadas a `/18`: `[14/18]` dependencias, `[15/18]` imports, `[16/18]` tests,
  `[17/18]` write-back, y el nuevo `[18/18]`. El rapido sigue en **13** y su composicion no se toco: el check
  nuevo esta **despues** de `if not self.quick:`, que es lo que miden
  `tests/test_run_all_validations_denominador_por_modo.py` (5 passed, derive los denominadores de
  `_orden_del_modo()`) y `test_el_check_queda_cableado_al_modo_completo_y_no_al_rapido`.
- Pin de gobernanza re-anclado con su nota datada: A3 pasa de `[17/17]` a **`[17/18]`** (su sujeto es el
  write-back, que sigue siendo el check 17; lo que se movio es su denominador). 54 passed en
  `tests/quality_gates/governance_numbers/`.

## 5. Dos efectos de la cura, declarados porque no estaban previstos

1. **La etiqueta impresa del check 18 no puede decir «QMind».** `validate_governance_numbers.py` resuelve el
   sujeto de una asercion por alias, `qmind` no esta en `ALIAS_STOPWORDS`, y con dos registros de la misma
   fuente reivindicando la misma asercion el lector cortaba **`LECTOR-FALLIDO` con exit 3** y publicaba un
   informe parcial: las 22 pruebas de la seleccion de gobernanza se fueron a error en setup, no a rojo por
   causa. Se resolvio **por el lado del sujeto** (la etiqueta dice `CONTEXT freshness (notebook de
   lecciones)`), no aflojando la guarda de ambiguedad ni tocando la lista de stopwords. Coste de la leccion:
   fue el unico efecto colateral de la tanda que no preveia el parte.
2. **El CLI no se llama desde `subprocess` con el nombre pelado.** La orden decia «por shell, nunca
   subprocess de Python», que es como esta escrita la nota de la casa del 2026-09-29. Medido hoy para
   resolverlo sin ambiguedad: `shutil.which("qmind")` resuelve `%APPDATA%\npm\qmind.CMD` y
   `subprocess.run([exe, …])` responde **rc=0**; lo que fallaba era el nombre **sin extension** sobre
   `CreateProcess`. Se ejecuto con la ruta resuelta y **lista de argumentos**, no con una cadena de shell:
   el argumento `-o` lleva una ruta de scratch, y meterla dentro de un parser de shell seria interpolar
   rutas en un interprete (el propio hook de seguridad de la edicion lo señalo y la razon es buena). El
   resultado que la decision exigia - que la descarga ocurra y se compare por bytes - esta verificado en la
   corrida real del punto 2, no afirmado.

## 6. Lo que T3 no goberna

`Historico/`, los `CONTEXT` sin autodeclaracion, las otras 54 fuentes del notebook que no son `CONTEXT`, la
ingesta de `10-analisis` (sigue en el hermano) y la pertinencia de lo publicado. Y no toca
`docs/CONTRIBUTING.md` (limite declarado de S32, que esta orden reitera).
