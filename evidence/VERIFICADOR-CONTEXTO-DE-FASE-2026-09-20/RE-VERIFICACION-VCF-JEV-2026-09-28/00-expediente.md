# Expediente — re-verificación VCF + JEV y cura de sus hallazgos (2026-09-28)

Sesión **escritora**, alcance cerrado a la población de la orden `ORDEN — CURA DE HALLAZGOS DE LA
RE-VERIFICACIÓN VCF+JEV (2026-09-28)`. Los hallazgos viajaron verbatim en la orden y cada uno se
**re-midió contra disco antes de escribir cualquier nota**; ningún hallazgo se declaró caduco sin su
salida, y ninguna nota se escribió sin su medición de hoy.

- Revisión de partida: `84c1aca` (árbol limpio: `git status --porcelain -uno` = **0** líneas; la única
  línea de `git status --porcelain` sin `-uno` es esta propia carpeta de evidencia, colapsada).
- Población: `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/` y
  `.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/`, más su evidencia.
- Crudos: `01` a `16` en este directorio, generados por los `m-*.sh` y `*.py` aquí mismos; ningún
  `.txt` se editó a mano.

---

## 1. PASO 0 — la fuente única leída antes de escribir

Se leyeron y se citan:

- `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
  — **§13 es la única matriz vigente**; §1–§12 son antecedentes rectificados. Su fila «D1 y S13» está en
  crudo en `09-censo-deudas-y-decisiones.txt`, sección C.
- El mismo archivo, **§11 filas 16 y 17**: los dos hallazgos **RECHAZADO** (crudo en la sección D del
  mismo archivo de censo).
- `.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` — encabezado
  (líneas 1-18) y **«Cierre formal de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (2026-09-27)»**.

### Las dos retracciones ya juzgadas (prohibido reabrirlas — no se reabrieron)

| # | Retracción | Estado | Comando que lo sostiene |
|---|---|---|---|
| R-1 | «12/16 vencido» | **CONGELADA.** No se actualiza la cifra al día: AC16 lleva desde el 2026-09-26 una anotación que renuncia a ser cifra vigente, y §11-17 ya rechazó re-copiar la cifra de hoy porque «copiar 4,453 en `AGENTS.md` sería publicar la cifra que el próximo commit invalida». | `grep -n 'Vencido como cifra, cumplido como delta' .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md` (línea 182) y `grep -n 'RECHAZADO' evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md` (líneas 476-477) |
| R-2 | «D1 con dueño colgante» | **REFUTADA por §13**, que dice «**D1 CERRADA** en su alcance». Lo que sobrevive es solo **D-A**, y es deuda de código, no decisión del operador. | `sed -n '126,131p' evidence/…/00-resumen-cierre-B.md` → crudo `09-censo-deudas-y-decisiones.txt` §C |

La medición que hace R-1 más verdad que nunca (y que se publicó en el crudo, no en ningún plan): los
denominadores **vivos** del verificador hoy son **quick 13 / completo 17**, medidos con
`grep -oE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py` → crudo §E de
`09-censo-deudas-y-decisiones.txt`. La nota congelada de AC16 decía 12 y 16; siete días después ya eran
13 y 17. Una cifra publicada caduca; el comando no.

---

## 2. Veredictos por plan y AC (medidos hoy en su fuente, no transcritos de la orden)

> [!IMPORTANT]
> Estos dos **NO SATISFACTORIO** viven **solo** en este expediente. No se escribieron en los planes:
> la orden los reserva aquí, y un veredicto sobre el trabajo de otra sesión no es una nota datada de
> frescura.

| Plan | Ítem | Veredicto de la orden (antecedente) | Veredicto **medido hoy** | Fuente medida |
|---|---|---|---|---|
| VCF | AC12 | PARCIAL | **CUMPLIDO** (no «PARCIAL») | `evidence/…/FASE-C/criterios-de-completitud.md` fila ⟦E1⟧ → `**CUMPLIDO**`; crudo `15-veredicto-ac12.txt` |
| VCF | AC14 | PARCIAL | **CUMPLIDO — con rojo** | ídem fila AC14: verde 14→14 y rojo 14→**3**; crudo `14-veredictos-textuales-fase-c.txt` |
| VCF | AC15 | NO-EJERCITADO | **PARCIAL por diseño** con `acceptance = NO-EJERCITADO`, `valor: null` | ídem + `evidence/…/FASE-C/coverage.json` → `aceptacion` |
| VCF | regla 1.b | — | **NO SATISFACTORIO**: afirmaciones en presente vencidas en maestro y contrato, sin nota en el párrafo (F2 y F3 de este expediente) | crudos `02`, `03`, `04` |
| JEV | AC3 | REFUTADO | **REFUTADO, con medición**: la cláusula pide «originales rastreables por sha» y **ningún `original_sha256` de los cuatro pares case con nada versionado** — 0 coincidencias sobre los 2.852 blobs de HEAD y 0 sobre los bytes en disco; el texto pre-saneado no está guardado en ninguna ruta versionada (solo dentro del propio `muestra.json`) | `python evidence/…/jev_ac3_sha.py` → crudo `13-jev-ac3-verificabilidad-sha.txt` |
| JEV | regla 1.a | — | **NO SATISFACTORIO** por AC3 REFUTADO (fila anterior) | ídem |
| JEV | regla 1.c / B / C / RELEASE | — | **PENDIENTE-POR-DISEÑO**: FASE-B «SIN AUTORIZACIÓN PARA EJECUTARLA», FASE-C «BLOQUEADA POR DEPENDENCIA Y AUTORIZACIÓN», FASE-RELEASE «PENDIENTE» — tres filas leídas del README del plan, y es el corolario lo que las vuelve diseño y no incumplimiento: la dependencia técnica del hermano **ya está entregada**, así que lo que falta es mandato humano, no trabajo atrasado | `.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/README.md` filas 23-25 → crudo `10-verdictos-por-ac.txt` §F |

**Desviación declarada contra la orden**: la orden asignaba `PARCIAL` a AC12 y AC14. El disco dice
`CUMPLIDO` en AC12 y `CUMPLIDO — con rojo` en AC14. Se publica lo medido; lo de la orden queda como
antecedente refutado, con su fuente. La regla de la casa es la misma que R-1: una cifra o un estado
viajan con el comando que los imprime, y si el comando los refuta, se corrige el reporte, no el disco.

---

## 3. Censo de vivos, **con la corrección que la pasada anterior omitió**

La pasada de censo que produjo esta orden **no incluyó D1** y D1 no está viva: §13 la tiene **CERRADA en
su alcance** (R-2 arriba). El censo corregido, leído de `dependencias-fases.md` §Deuda registrada (filas
D1–D10) y del «Cierre formal» (líneas 1042-1057), más su cruda en `09-censo-deudas-y-decisiones.txt` §A y §B:

| Fila | Estado **vigente** (medido hoy) | Dueño / disparador |
|---|---|---|
| **D1** | **CERRADA en su alcance** por §13 — *la pasada anterior la omitió del censo* | dueño histórico: «Este plan, FASE-RELEASE», adelantado por mandato de B |
| D2 | **EJECUTADA el 2026-09-26** con desviación del disparador declarada en la propia fila | cumplida |
| **D3** | **PARCIAL** (viva) | «Plan propio, posterior» |
| D4 / D5 | asignadas antes que este plan; no se reasignan | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso |
| **D6** | **DORMIDA con causa medida** (`acceptance = NO-EJERCITADO`) | re-evaluación atada a D7 |
| **D7** | **viva**, inactiva | Plan propio posterior |
| D8 | **re-corrida el 2026-09-27**: «comprobada en su corrida / no re-confirmada en sus citas» | Este plan, sesión previa a FASE-RELEASE |
| D9 | **EJECUTADO y VERIFICADO POR CONTENIDO el 2026-09-27**, con la secuela abierta que la propia fila declara (las anotaciones posteriores a la subida vencen el snapshot) | Este plan, FASE-RELEASE |
| D10 | **CUMPLIDA en su lectura el 2026-09-25** | Este plan, FASE-RELEASE |
| **S10** | **viva** | nombra el «Cierre formal»; crudo §H |
| **S14** | **viva** | ídem |
| S13 | **CERRADA** en el alcance explícito de su observador (§13) | — |
| **S17** | **CERRADA por ejecución** en finales de línea; **ABIERTO su sub-punto menor** (el `--fix` sigue promoviendo la forma minoritaria) → ese sub-punto es lo que cura F4 | dueño §S17 |
| S18 | fila con su hecho medido | dueño §S18 |
| **S19** | en su **(d)**, opción medida y no aplicada | dueño declarado |
| S20 / S21 / S29 / S31 | S29 cerrada a-prima; S31 cerrada también en su fragilidad estructural | — |
| **S32** | **fila nueva, abierta**: el pack publica bytes del workflow sin que el workflow esté en sus `sources[]` | dueño y disparador con dos salidas medidas, ninguna aplicada |

Del lado **JEV** el censo vivo es: P1 (revisión humana de la muestra), la decisión del *gap* de interfaz,
y los mandatos de B/C/RELEASE — ninguno de ellos técnico (crudo `10-verdictos-por-ac.txt` §F).

---

## 4. Tabla F1–F5: estado por ítem

| Hallazgo | Re-medio de hoy | Veredicto | Qué se escribió |
|---|---|---|---|
| **F1** archivado JEV | `git ls-files .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/` = **12** rutas; el mismo directorio bajo `.opencode/plans/` sin `Archives/` = **0**; `git show --name-status -M 84282c1` sobre el plan = **12 renombres** (**R100 ×10, R089 ×1, R099 ×1**); `git merge-base --is-ancestor 84282c1 HEAD` = **SI-ANCESTRO**. Crudo `01-f1-archivado-jev.txt` | **VIVO** (la nota del plan sigue contradicha por disco) | Nota datada en `README.md:3` y en `04-contrato-ejecucion.md:21` |
| **F2** piloto FASE-C VCF | `git ls-files evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` = **23** rutas (la orden citaba 20; **no reproduce** con `git ls-files` ni con `find -type f`, que también da 23); `7f2e9f9` y `5817edd` **ambos SI-ANCESTRO**; `scripts/triage_lesson_relevance.py` versionado; la nota `Rectificado el 2026-09-24` vive **solo** en `dependencias-fases.md` (líneas 7 y 194) y **no** en maestro ni contrato. Crudo `02-f2-piloto-fase-c-vcf.txt` | **VIVO**, con la cifra de archivos corregida (23, no 20) | Nota datada en `01-plan-maestro.md` (párrafo 18-25) y en `04-contrato-ejecucion.md` (párrafo 7-16), apuntando a la rectificación |
| **F3** «Única superviviente» | Barrido por párrafo sobre las **13 fuentes** del plan (sin los packs derivados): **11** párrafos afirman la cláusula, **2 SIN nota** (`01-plan-maestro.md:18-25` y `04-contrato-ejecucion.md:7-16`) y **9 CON nota** con el criterio débil; con el criterio fuerte (el `⟦` cae después de la negación) **5**. La orden publicaba 8 CON nota: **no reproduce** bajo ninguno de sus dos criterios, y el punto de fondo sigue en pie — hay **2** supervivientes, no 1. Mismo barrido sobre el **corpus completo** (383 `.md` incluyendo `briefing/`): 37 párrafos, 28 CON nota, **9 SIN nota** (los 2 de las fuentes + 7 proyecciones en los packs). Crudos `03` y `04` | **VIVO** | Nota datada en `10-analisis-post-implementacion.md` con el 2/9 y el 2/37 y sus comandos |
| **F4** par 518/66 de §S17 | Medido hoy con el instrumento **que nombra la fila** (`git grep -c` sobre `HEAD`, backtick dentro del patrón): ancla del mandato **166 contra 29 líneas**, ancla ancha **564 contra 73**. Por **ocurrencias** (`str.count`) sobre el corpus marcado versionado (700 `.md`): **167 contra 29** y **604 contra 73**. Sobre **todos los ficheros versionados** (2.852): **174 contra 32** y **786 contra 77**. Y en `3c2e6a3`, la revisión que **escribió** el 518/66: **147 contra 28** y **524 contra 72** líneas. **El par 518/66 no reproduce con ningún ancla, en ningún instrumento, ni siquiera en la revisión de su propia firma.** Crudos `05`, `06`, `07`, `17-f4-tres-alcances.txt` | **VIVO**, y más fuerte de lo que la orden afirmaba: tampoco reproducen **sus** cifras bajo el alcance de la fila (174/32 y 793/77 son de **otro alcance**) | Nota datada en `dependencias-fases.md` §S17 declarando los tres pares con su población y su instrumento |
| **F5** REGISTRY sin FASE-A de JEV | `grep -o -F 'EVALUACION-JEV-TYPESAFE-2026-09-21' docs/contributing/REGISTRY.md` = **0** ocurrencias (y 0 en el blob de `HEAD`). Contraste: el plan VCF sí tiene 7 menciones y su cabecera `## FASE-RELEASE (VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20) - 2026-09-25`. El escritor se probó con `--dry-run` (no escribió: `git status --porcelain -uno` = **0** después): emite `## <FASE> - datetime.now()`, o sea **hoy**, y sus 13 `add_argument` no tienen ninguna bandera de fecha ni de nota → **no soporta entrada tardía con nota datada**. Crudos `08`, §5 y §7 | **CADUCADO PARA LA ACCIÓN / VIVO COMO DEUDA**: la rama «úsalo» está **cerrada por medición**, no por interpretación; escribir hoy publicaría «FASE-A - 2026-09-28» contra un `a7564ae` que la fechó el 2026-09-21 | **No se tocó REGISTRY.** Se registra la deuda **D-F5** abajo |

---

## 5. Deudas y decisiones — registradas, no ejecutadas

| ID | Tipo | Dueño / disparador o salidas | Coste y diente |
|---|---|---|---|
| **D-A** | Deuda de código | `scripts/validate_governance_numbers.py:819`, `:830`, `:839` apuntan a la fila **D1**, que §13 cerró en un alcance que **no cubre esas tres familias** (prosa de conteo sin patrón, conteos fuera de documentos de gobierno, pins en `tests/`). Cura en el próximo mandato que autorice editar ese script: **re-apuntar a §13** o **publicar las familias sin dueño nominal** | Medido: las tres líneas están y dicen `D1` (crudo `09` §G). Diente: el verificador ya no puede cobrar una deuda de una fila cerrada; deja tres familias sin dueño nominal |
| **D-B** | Decisión del operador, **no resuelta aquí** | AC3 de JEV: **(a)** versionar un fichero de candidatos con `original_sha256` **verificable**, o **(b)** enmendar la cláusula | Coste de (a): produce el insumo y re-ancla la muestra; su diente es que hoy **0 de 4** shas casan con nada versionado, así que la trazabilidad que AC3 afirma no existe. Coste de (b): toca una cláusula de acceptance ajena a esta sesión y necesita instrucción literal |
| **D-C** | Diferido, sin cambios | CRLF **213** — dueño §S17 | Esta sesión **no** normalizó nada: se midió el estado y se dejó |
| **D-D** | Espera instrucción escrita | Revisión humana de la muestra BORRADOR (4 pares: `human_reviewed = false`, `reviewer = null`, `reviewed_at = null`) y mandato JeV-B | **Condición cumplida** (la dependencia del hermano está entregada y versionada); lo que falta es firma humana y mandato, no capacidad |
| **D-E** | Decisión | Re-ingesta a QMind de los **2 snapshots vencidos** | Aviso de la casa: el `--upload` responde `[SKIP]` por título, así que la re-ingesta con el mismo título deja la versión vieja como verdad publicada y crear gemelo exige título nuevo y no hay `delete` en el MCP. ⟦**2026-09-29, ejecutada a medias por instrucción literal**: el miembro de la **lección §11** quedó **subido** con título nuevo y verificado por descarga + sha256 (notebook de **54** a **55**, `01a0ef0e-…`); el aviso de esta fila resultó cierto solo **para el MCP**, porque el CLI **sí** expone `qmind source delete` — medido el 2026-09-28 y **no ejecutado**, que es una escritura compartida irreversible. Resta el otro miembro, la re-ingesta de los **2 snapshots vencidos**, con su diferencia ya medida: **+4.607 bytes** entre la fuente publicada `01a0e464-…` y el `10-analisis` en disco, **sin** artefacto CRLF. Texto larga en §6 y crudos `SESION-SCRIPTS-CURAS-2026-09-28/39-` y `40-` ⟧ ⟦**2026-09-29: ejecutado también el otro miembro, por la pegada de la orden de cierre de deudas, y con la población corregida por medición — era 1, no 2.** El `10-analisis` de JEV resultó **FRESCA** (descarga y disco con el mismo sha y los mismos 15.144 bytes), así que no se re-ingestó; el vencido era el de este plan, y subió con **título nuevo** conservando el stem —fuente nueva `01a0ef39-b514-7b10-ae86-5ff435fee0a3`, verificada por descarga + sha256 y no por título—, y el gemelo `01a0e0d3-92db-…` **quedó borrado** bajo la misma autorización. `validate_qmind_writeback.py --strict` sigue `[PASS] 13/13` después de las dos escrituras. Fuente del hecho, con sus crudos: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md`, secciones §2 y §3. Y una divergencia que esta fila no preveía quedó medida y **no curada**: el `CONTEXT` de JEV está vencido por 9 bytes (el segmento `Archives/`), presentado con opciones en el §4 de ese expediente ⟧ |
| **D-F5** | Deuda nueva, registrada en este expediente | **Dueño**: escritor de REGISTRY (`scripts/log_phase_completion.py`). **Disparador**: próximo mandato que toque ese escritor. **Contenido**: FASE-A de `EVALUACION-JEV-TYPESAFE-2026-09-21` quedó cerrada sin entrada | Nace de medir, no de opinar: el escritor estampa `datetime.now()` (línea 152) en la cabecera `## {fase_id} - {fecha}` (línea 172) y no tiene bandera de fecha ni de nota; usarlo hoy escribiría una fecha falsa. **Ninguna rama toca el archivo a mano**, y esta sesión tampoco |

---

## 6. Lección del Paso 0

**Toda orden de re-verificación arranca leyendo la matriz vigente de la fuente única.** Esta orden la
llevaba escrita en su propio Paso 0 porque las dos sesiones que la precedieron publicaron hallazgos
contra un estado que §13 ya había cerrado: «D1 con dueño colgante» se refutaba en dos líneas de la
matriz, y «12/16 vencido» se refutaba en la anotación que el propio plan se puso el 2026-09-26.

Tres consecuencias operativas, cada una con su evidencia de hoy:

1. **El censo se lee de la matriz, no del resumen.** La pasada anterior omitió D1 y el censo salió con
   una fila muerta de más (§3).
2. **Un veredicto heredado es una hipótesis.** AC12 y AC14 llegaban como `PARCIAL` y su propio cierre de
   fase los había certificado `CUMPLIDO` (§2).
3. **Una cifra sin población y sin instrumento no es medible.** El 518/66, el 20 de F2 y el 8 de F3 son
   tres instancias del mismo defecto, y las tres se resuelven publicando el comando con la cifra (F4,
   F2, F3 arriba).

**Cómo subirla a QMind:** con **TÍTULO NUEVO** (el `--upload` responde `[SKIP]` por nombre y dejaría la
versión vieja como verdad publicada) y **verificada por descarga + sha256**, nunca por título. La subida
en sí es la decisión **D-E** y no se ejecuta en esta sesión.

⟦**Nota datada 2026-09-29 — ejecutada por instrucción literal del operador, y exactamente como esta sección la
describía**: título nuevo por CLI y verificación por descarga + sha256. Fuente `01a0ef0e-aa1c-7e5d-8486-51d40b8b4f07`,
notebook `01a04d98-b7bd-778c-8441-26fdc7e35f45` de **54** a **55** fuentes, sha `d968d497…e12b1` idéntico en disco y
en la descarga (2.677 bytes en ambos lados). El pre-estado se leyó antes de escribir: **0** títulos con `lecc`, así
que la notificación de subida en segundo plano que la sesión 2 recibió sin haberla emitido **no había publicado
nada** — no hubo que retirar nada. `validate_qmind_writeback.py --strict` sigue `[PASS] 13/13`. De la fila **D-E**
queda en pie su otro miembro, la re-ingesta de los **2 snapshots vencidos**: medido hoy, la fuente publicada
`01a0e464-…` trae **106.284** bytes contra **110.891** del `10-analisis` en disco, shas distintos y **sin** artefacto
CRLF (normalizado el retorno de carro, las dos medidas no cambian). Su ejecución, y el borrado del gemelo
`01a0e0d3-92db-…`, piden instrucción literal propia. Crudos: `SESION-SCRIPTS-CURAS-2026-09-28/39-` y `40-`⟧

⟦**Nota datada 2026-09-29 — las dos instrucciones literales llegaron, y esta sección quedó ejecutada tal como la
última nota la dejaba escrita**: subida por CLI con **título nuevo** y verificación **por descarga + sha256**, más
el borrado del gemelo. La población de la re-ingesta la fijó la medición del Paso 0 y fue **1, no 2**: de las dos
fuentes que la fila D-E nombraba, el `10-analisis` de JEV resultó fresco y solo el de este plan estaba vencido. El
veredicto de frescura de cada fuente, sus bytes y sus shas, y el cierre del verificador de write-back están en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md` (secciones §1
a §3), que es desde hoy la fuente del hecho; esta nota no re-transcribe esas cifras ⟧

---

## 7. Fraudes de instrumento cazados mientras se medía (declarados, no corregidos en el pasado)

- `grep -c $'\r'` **dentro de un `printf` entrecomillado** contó todas las líneas como si tuvieran CR y
  hacía ver los seis planes como CRLF. La lectura real por bytes da **CR=0, LF puro** en los seis
  objetivos de anotación (crudo `16-eol-en-bytes-de-los-planes.txt`). Sin esta comprobación, la sesión
  habría «curado» un CRLF inexistente — y justo esa es la familia de §S17.
- `git grep -c -F '/.opencode/plans/Archives'` sobre `HEAD` devuelve **0** sobre archivos llenos de esa
  cadena: el **0 falso** que la quinta instancia de §S17 ya documentó se reprodujo hoy (crudo `05` §2).
- `git grep -c` sobre una revisión cuenta **líneas**, no **ocurrencias**; por eso el mismo ancla da 166 y
  167. Un par de formas contado con el instrumento equivocado y con el alcance equivocado no es el mismo
  dato, aunque el número se parezca.
- `python -` con `<<'PY'` dentro de un `.sh` **sí** pasa el programa por stdin, pero su stdout bajo
  Windows se emite con **CRLF** y con cp1252: el crudo `10` salió con 22 CR y una corrida intermedia
  reventó imprimiendo `⟦` por la consola. Los crudos `11`-`15` se escriben por archivo con
  `newline="\n"` y UTF-8.

---

## 8. El pipeline propio de esta orden, y lo que pario

Orden estricta de la orden, ejecutada sin paralelismo. Cada verificacion con el **exit propio del
proceso** (no el de la tuberia que lo envuelve, que es la trampa que ya costo un verde falso en otra
sesion de esta casa):

| Paso | Comando | Resultado medido |
|---|---|---|
| 3 | `python scripts/validate_opencode_refs.py --fix` | reparo **1** referencia y al hacerlo **promovio la forma minoritaria sobre la nota que esta sesion acababa de escribir**: convirtio la ruta versionada que yo citaba en `` `/.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21 `` (con barra inicial) y con eso borro el sentido de la medicion, porque la frase decia «el mismo listado sobre la ruta **sin** `Archives` da 0». Reparado: la nota ahora describe esa ruta con palabras y no con un literal, y la forma dominante queda intacta. Idempotencia verificada despues: `validate_opencode_refs.py` solo da `[PASS]` con **exit 0** y una segunda corrida de `--fix` ya no escribe nada. Crudos: `21`, `22`, `24` |
| 4 | `python scripts/validate_plan_citations.py --update-baseline` | `Baseline fijado: 79 archivos, 743 citas`. El unico cambio del JSON es `created_at` (`git diff`: 1 linea, `2026-09-27T16:53:48` → `2026-09-28T16:57:37`): **mis notas no anadieron ninguna cita numerica**, deliberadamente, porque `CITATION_RE` de ese guion cuenta `archivo.ext:123` y la regla de la casa es citar simbolos y secciones, no lineas. Crudos: `25`, `27` |
| 4f | normalizacion por bytes del baseline | **defecto nuevo medido, no buscado**: `escribir_baseline()` (linea 135) usa `path.write_text(...)` **sin** `newline="
"`, asi que la corrida del paso 4 paso el baseline de `w/lf` a `w/crlf` y **movio la cifra que governa D-C: el residuo bajo `.opencode` paso de 213 a 214** (`git ls-files --eol .opencode | awk '$1=="i/lf" && $2=="w/crlf"' | wc -l`), con el desglose por extension subiendo de 34 a 35 `json`. Se probo que es el escritor y no el arbol: la misma corrida con `--baseline` apuntando a una ruta fuera del repositorio produjo un archivo **CRLF puro** (CR=87, LF=87, CRLF=87). Como `scripts/` esta prohibido en esta sesion, la cura no se hizo: se normalizo **por bytes el unico archivo que esta corrida ensucio** (6.609 → 6.522 bytes, `identico_salvo_CR: True`, JSON parseable, 79 archivos inventariados) y la poblacion volvio a **213 / 34 `json`**. Crudos: `26`, `27`, `28` |
| 5 | `python scripts/build_lesson_index.py` y su `--check` | par derivado **byte a byte intacto**: `LECCIONES-INDEX.md` `0161857e61c98643` y `lecciones_index.json` `1d254462e4755346`, identicos antes y despues; 340 IDs; `--check` **exit 0**. CR=0 en ambos |
| 6 | `python scripts/build_phase_briefing.py --plan ... --check` | primero LISTO (sin escribir): los **5** packs del plan VCF vencidos por `SHA-DISTINTO` (3 fuentes movidas; FASE-RELEASE con 4, por la nota de `10-analisis`). Regenerados los 5 y solo esos: `COMPLETO 5 · SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0 · fuentes 37`. `--check` despues: **exit 0**, cinco filas `[OK] ... fuentes frescas`. El orden de la casa (**packs → indice → `--check`**) se respeto: el indice se re-corrio despues de regenerar y siguio intacto. Crudos: `30b`, `32`, `33` |
| 6b | el mismo `--check` sobre el plan JEV | `[VENCIDO] ... PACK-AUSENTE` x4 con **exit 1**, y es **preexistente, no de esta sesion**: `git ls-tree -r --name-only HEAD -- .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/briefing` = **0** rutas, 0 en `3c2e6a3` (la revision previa al archivado) y **0 menciones en todo el historial** (`git log --all --name-only`); ademas AC19 — la clausula que obliga packs — es del plan VCF (3 menciones) y **no existe en el maestro de JEV** (0). Por eso **no** se generaron aca: crear cuatro derivados nuevos en un plan archivado esta fuera de la poblacion de esta orden y fuera de su contrato. Queda como hecho medido y declarado, con su crudo (`31`) |
| 7 | `python scripts/run_all_validations.py --quick` | **13/13, exit 0**, con la linea `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`. Detalle pertinente: `[8/13] OpenCode References: All .opencode references exist`, `[9/13] Plan Citations: 743 citas historicas, 0 nuevas y 0 crecimientos`, `[13/13] Briefing Packs in Commit Tree: packs en el árbol de HEAD (5/5 reproducidos por el escritor, 0 divergentes, 0 no evaluables)` — o sea que el verificador del arbol commiteado **no vio todavia** mis cinco packs nuevos, porque estos aun no estan commiteados: su verde se cobra despues del paso que esta sesion NO ejecuta (ver §10) |
| 8 | `git diff --check` y `git status --short` | `git diff --check` **exit 0**. Poblacion: **12** archivos versionados modificados (6 fuentes anotadas + 5 packs regenerados + el baseline de citas) y **1** directorio nuevo de evidencia. **CR=0 en los doce** (suma total 0). `130 insertions(+), 98 deletions(-)` |
| control | `REPORTA, NO REESCRIBE` | `37-inclusion-pura-head-en-disco.txt`: quitando de disco las seis notas de hoy, el texto restante es **identico caracter a caracter** al de `HEAD` (colapsando espacios) en los seis archivos, y cada nota tiene `⟦` y `⟧` pareados (1 y 1). Las lineas que el `git diff` marca como borradas son reenvolturas del mismo texto, no supresiones |

---

## 9. Deudas que pario esta sesion (registradas con dueno y disparador; no se ejecuto nada)

No estaban en la orden y nacen de las corridas que la orden mandaba. Se registran aqui, con dueno y
disparador, en vez de curarse de paso.

| ID | Hecho medido hoy | Dueno | Disparador |
|---|---|---|---|
| **D-G** | `validate_opencode_refs.py --fix` promote la forma minoritaria **tambien sobre texto ajeno recien escrito**: mordio la nota de esta sesion y le cambió el significado (paso 3 de la tabla §8). La cura pedida por el sub-punto de §S17 sigue siendo la misma y sigue sin hacerse | dueno del sub-punto abierto de **§S17** (el `--fix` promueve la forma minoritaria) | proximo mandato que autorice editar `scripts/validate_opencode_refs.py` — mismo disparador que D-C y que el sub-punto de §S17; no se abre un numero nuevo porque es la misma puerta ya declarada |
| **D-H** | `validate_plan_citations.py:135` (`escribir_baseline`) escribe sin `newline="
"` y convierte a CRLF un archivo que git almacena en LF; medido con el propio guion sobre una ruta externa (`26`, `27`) | dueno de la familia de finales de linea de **§S17** | proximo mandato que autorice editar `scripts/validate_plan_citations.py`. Miembro sexto de la serie `sync_rule`, `run_regenerate_domain_primer`, `run_status`, las dos de `validate_opencode_refs.py` |

**D-C queda con su cifra intacta y su cuenta corregida**: el residuo sigue en **213** porque la unica
escritura CRLF de esta sesion fue revertida por bytes y declarada; pero ya no puede decirse que la
poblacion sea estable frente al pipeline — **basta correr el paso 4 para moverla**. Eso se anota contra
D-H, no contra la medida original.

---

## 10. Inventario del expediente y estado de los cinco cortes

**Escritura efectuada (nada commiteado):** 12 archivos versionados modificados — 6 fuentes anotadas
(`Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/README.md`, su `04-contrato-ejecucion.md`,
`Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/01-plan-maestro.md`, su `04-contrato-ejecucion.md`,
su `10-analisis-post-implementacion.md`, su `dependencias-fases.md`), 5 packs regenerados por su
escritor, y `.opencode/plans/plan_citations_baseline.json` (solo `created_at`) — más **1** directorio nuevo de evidencia: **46** crudos `.txt`, **2** documentos (este `00-expediente.md` y la lección `43-leccion-paso-0-2026-09-28.md`) y **14** instrumentos = **62** entradas en total:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/`.

| Corte | Estado |
|---|---|
| Implementacion terminada | **SI** — las 5 notas F1-F4 y el expediente; F5 no toco REGISTRY por la rama medida (D-F5) |
| Verificacion terminada | **SI** — quick **13/13** con `[GUARDA]` y exit 0, packs `--check` exit 0, indice `--check` exit 0, refs exit 0, citas exit 0, `git diff --check` exit 0, CR=0 en los 12 |
| Cierre documental | **SI** — este expediente con sus crudos; REGISTRY **no** se re-registra (prohibido y ademas refutado por la via del escritor, D-F5) |
| Listo para revision | **SI** |
| Espera de autorizacion | **SI** — es el estado operativo final. El `git commit` **no** es condicion de ninguno de los cinco: es accion posterior y separada, y aqui esta **pendiente de autorizacion explicita** |

**Dos controles de esta sesion que hay que leer con su instrumento correcto:**

- `36-cr-y-no-reescritura.txt` §2 es el control **ingenuo** (compara linea a linea) y sobre-reporto
  «lineas que faltan» (16-26 por archivo) que no eran supresiones sino reenvolturas y cabeceras de
  procedencia de los packs regenerados. El control que vale es `37-inclusion-pura-head-en-disco.txt`:
  quitando las notas de hoy, el texto es **identico caracter a caracter** al de `HEAD` en las seis
  fuentes. Lo primero se conserva como crudo porque muestra donde duele un control mal elegido.
- `30-paso6-check-sin-plan.txt` registra que `build_phase_briefing.py --check` **sin** `--plan` imprime
  `[2] hace falta --plan <nombre|ruta>` y, corido detras de `| tail`, devolvio un `EXIT=0` **falso**:
  el 0 era de `tail`. Todos los `EXIT_*` de este expediente desde ese aprendizaje se toman redirigiendo
  a archivo y leyendo el exit del proceso (`33`, `34`, `38`).

**Frescura declarada:** el ultimo `--quick` (13/13, exit 0) se corrio **despues** de la ultima escritura
al arbol versionado, y la ultima edicion de texto de plan fue anterior a la regeneracion de packs y a
la re-corrida del indice, en el orden de la casa (packs → indice → `--check`). Lo que **no** puede
afirmar esta sesion: que `[13/13]` haya visto los packs nuevos — ese check mira el arbol de `HEAD`, y
estos cambios aun no estan commiteados; su verde se cobra despues del commit, no aqui.

---

## 11. La leccion del Paso 0, escrita y **pendiente de autorizacion para subirla**

La leccion esta redactada y versionable en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/43-leccion-paso-0-2026-09-28.md`.
**No se subio a QMind.** Dos razones, y las dos se declaran en vez de resolverse por iniciativa propia:

- La propia orden coloca esa linea dentro de la seccion «DEUDAS Y DECISIONES — **solo registrar, no
  ejecutar**».
- Una subida a un sistema externo es escritura compartida y no reversible por la via de esta sesion.

**Correccion medida a un supuesto que la casa daba por fijo.** La advertencia «gemelo sin delete MCP»
(D-E, y la nota de proyecto) es cierta para el MCP — sus seis herramientas son `add_source`,
`get_source`, `list_notebooks`, `list_sources`, `read_source`, `retrieve`, ninguna borra — pero el **CLI
si expone `qmind source delete <source_id>`** (ayuda leida en `44-cli-qmind-help.txt`, sin ejecutarla).
O sea: si una subida con titulo nuevo dejara un gemelo, el CLI lo puede borrar; lo que no puede borrar
es el MCP. Eso **reduce** el riesgo de D-E y conviene tenerlo escrito antes de decidir esa subida, que
es la que la orden deja como decision del operador.

**Comando exacto, con la interfaz leida del guion real (`--nb`, `--file`, `--title`) y no supuesta:**

```bash
qmind source upload --non-interactive   --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45   --file "evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/43-leccion-paso-0-2026-09-28.md"   --title "LECCION — una orden de re-verificacion arranca por la matriz vigente (2026-09-28)"
```

Titulo **nuevo adrede**: `validate_qmind_writeback.py` decide `is_ingested` solo por titulo y `do_upload`
responde `[SKIP]` cuando el titulo ya existe, asi que repetir un titulo deja la version vieja como
verdad publicada sin avisar. Verificacion despues de subir: **por descarga y sha256 del archivo
descargado contra el local**, nunca por titulo (`qmind source list --nb <ID> --all --format json` para
tomar el `source_id`, luego `qmind source download <source_id> --nb <ID> -o <destino>`). El sha256 de
partida del archivo local, para casar la descarga:

```bash
sha256sum evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/43-leccion-paso-0-2026-09-28.md
```
