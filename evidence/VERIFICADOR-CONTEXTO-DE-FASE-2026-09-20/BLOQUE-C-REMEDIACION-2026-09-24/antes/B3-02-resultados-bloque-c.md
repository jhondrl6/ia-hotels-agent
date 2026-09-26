# Bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` — resumen único de resultados

**Sesión:** 2026-09-24. **Naturaleza:** documental, en los cuatro planes vivos y en la propia orden.
**Estado del bloque: C CONCLUIDO** en lo que su mandato autorizó (veredicto y alcance exacto en §8; las
decisiones que siguen siendo del operador, en §6: ninguna es necesaria para cerrar la parte documental).

**Lo que NO es este cierre:** no es el cierre de la orden (falta el piloto), no es la ejecución de ninguna
fase de los cuatro planes, no es autorización de nada. No hubo commit, push, red, QMind, inferencias,
instalaciones, pipeline, archivado ni cambios en código, tests, hooks, `VERSION.yaml`, `AGENTS.md`,
`.cursorrules`, `.agents/**`, configuración ni scripts.

## 1. Matriz §4.C: requisito → contrato vigente → consumidor → cambio → comprobación → estado

Los seis renglones son los de §4.C de la orden. `Consumidor` es el artefacto **ejecutable** que lee ese
contrato (a él se dirige el cambio, no a una nota al margen). `Comprobación` es la que se hizo en esta
sesión, sin heredarse de B.

| Requisito de §4.C | Contrato vigente al abrir | Consumidor | Cambio necesario | Comprobación | Estado |
|---|---|---|---|---|---|
| **CONTEXTO/C** — E1–E5 verificados contra el cliente real, sin renegociar | `04-contrato-ejecucion.md` §Enmiendas (E1–E5, escritos el 2026-09-23, ninguno re-contrastado con el código) | `05-prompt-inicio-sesion-fase-C.md`; en FASE-C real, `decision_client.py` + `triage_lesson_relevance.py` | **Reconfirmación**, no reescritura: E1 y E2 vuelven a afirmarse contra las formas reales de `RespuestaEleccion` / `RespuestaNoul` y contra la puerta que rechaza `confidence` en una respuesta noul; el prompt de C declara «cinco enmiendas» y reproduce E5 vigente | Lectura de los dos DTOs y del validador de puerta en `scripts/decision_client.py` (símbolos, no líneas); `05-…-fase-C.md` y contrato concuerdan; suite acotada de instrumentos (`06-suite-acotada.txt`) | **RESUELTO (documental).** Ejecución: **pendiente propia** (piloto, con mandato) |
| **CONTEXTO/D** — carga total con workflow obligatorio, coste de generación y consumo del pack; no equiparar concatenación con ahorro; frescura por entradas relevantes con HEAD como procedencia, sin invalidación circular por el commit del generado; admisión explícita de AC15 semántico `NO-EJERCITADO` y D6 dormida; orden regeneración/validación tras el traslado | `04-contrato-ejecucion.md` medía solo el delta del pack; `05-…-fase-D.md` Tarea 2 y 3; AC20/AC21 del maestro | `05-prompt-inicio-sesion-fase-D.md`, `06-checklist`, `09-`/`10-`, y el futuro `build_phase_briefing.py` | Nueva sección §Carga total y frescura del pack con **tres sumandos** (`workflow_obligatorio`, `coste_de_generacion`, `pack_consumido`) y resta total-vs-total; prohibición expresa de presentar la concatenación como ahorro; la caducidad se decide por `sha256` de `sources[]` (HEAD = **procedencia**, no llave) y dos tests nuevos la fijan; AC15 `NO-EJERCITADO` y **D6 dormida con causa** re-declarados en el prompt; regeneración del pack **después** del `git mv` y validación (`--context`/`--status`) **solo** en RELEASE | `04-contrato` / maestro (AC20, AC21, §2) / prompt de D / `06-checklist` / `09-` / `10-` dicen lo mismo; el prompt de D lista los dos tests que gobiernan las dos propiedades nuevas | **RESUELTO (documental).** La medición la hace FASE-D |
| **CONTEXTO/RELEASE** — «verificador verde» vs D1 sin ejecutar; subida/consulta QMind vs la regla de cero red; `--check` posterior al traslado sin regeneración prevista; no convertir RELEASE en reparación de código; no promover resultados parciales a éxito | `05-prompt-inicio-sesion-fase-RELEASE.md` mandaba Q7/`--upload` (red) dentro de un plan con «cero red», y `--check` **después** del `git mv` | `05-…-fase-RELEASE.md`; en el RELEASE real, `validate_governance_numbers.py`, `build_lesson_index.py`, `validate_qmind_writeback.py`, `doctor.py` | Modelo de **tres momentos con tres permisos** (offline / traslado / remoto) en tabla explícita; Q7 y el `--upload` pasan a `PENDIENTE-AUTORIZACION` y `--help` queda como comprobación offline; **regeneración derivada intercalada** antes de `--check` (índice y pack), con el orden anotado `⟦remoto⟧`/`⟦traslado⟧`; regla «leer el estado ≠ reparar» y D2/D6/D8-D9 declarados inalcanzables o no satisfechos en esta sesión; qué se publica si el momento remoto no está autorizado | `validate_governance_numbers.py --report` (sin destino = no escribe, S12) y `build_lesson_index.py --check` en verde; contrato §Dos momentos y §Cierres ítem 8 coinciden con el prompt | **RESUELTO (documental).** El momento remoto sigue **bloqueado por permiso**, no por este contrato |
| **WHATSAPP** — punto de reanudación real; tramos pendientes alineados con el proceso común; conservar AC5 y su dueño, contratos aditivos, botón seguro, aislamiento interno/cliente, corrida única y lectura directa de VERIFY; resolver DOMAIN_PRIMER por gobernanza distinguiendo generación de validación | `README.md:3` publicaba a B sin commit y un arranque que mandaba repetir B; el dominio apuntaba a que «A debe resolver la divergencia documental»; VERIFY se leía con 18 ACs | `README.md` §Inicio, los ocho prompts pendientes (C, D, E, F, H, E2E, VERIFY, RELEASE), `04-contrato-ejecucion.md`, `dependencias-fases.md` | Cabecera y bloque de arranque reconciliados con el estado publicado por `473ed0f`/`05d0cc6`/`7553f51` y **B CERRADA CON DEUDA → C como punto de reanudación con AC5**; los **cinco cortes sin commit** sustituyen «commit al cerrar» en contrato, R2 y prompts; cuota de lecciones retirada; proporcionalidad/reuso con invalidación explícita (herencia de B) escritos en el contrato; DOMAIN_PRIMER resuelto **por gobernanza**: regenerar al cerrar cada fase de implementación, validar con `--context`/`--status` solo en RELEASE (dos operaciones distintas); la fila contradictoria del README **eliminada**, no anotada; VERIFY releído a **AC1–AC20 (AC19 en sus dos mitades)**; dependecia de H corregida **G → F** con nota fechada | AC5 y su dueño presentes en `06-checklist` y `dependencias-fases.md`; los prompts cerrados (A, G, 0, B) y su evidencia intactos; `01-plan-maestro.md` conserva su CRLF (195/0 mixto) y su delta es 2/2 | **RESUELTO (documental).** Pipeline y regeneración de DOMAIN_PRIMER: **no ejecutados** |
| **JEV** — reconciliar arranque y disponibilidad real de la interfaz; integrar contra el contrato corregido sin duplicar cliente ni acomodar silenciosamente al consumidor; separar dependencia técnica (CONTEXTO B+C offline) del orden de cierre/índice (gobernanza) y de la aceptabilidad semántica con proveedor real; conservar revisión humana, muestra BORRADOR→congelada, comparador, reservas, cuotas, aislamiento del SDK y permisos por etapa | `README.md` y §Inicio decían «ejecutar FASE-A»; P2 afirmaba una dependencia sin medir qué existe; el contrato de B hablaba de una costura que aún no está | `README.md` §Inicio y estados, `05-…-fase-B.md`, `01-plan-maestro.md`, `04-contrato-ejecucion.md`, `09-`/`10-` | Tabla **existe / falta** con los comandos para re-medirla (`decision_client.py`, `triage_lesson_relevance.py`, `build_phase_briefing.py`, el pack); las tres cosas separadas en párrafos propios (técnica / gobernanza / aceptabilidad); **gap de contrato medido y declarado**: 8 de los 11 campos del piloto no están en la costura, con la decisión que sí queda (requested-vs-effective y `usage_normalized`) y la prohibición de duplicar la costura o recortar AC1/AC2; §Inicio reescrito: **hoy no hay fase de JEV ejecutable**, y el texto prohíbe expresamente editar el archivo protegido | `sha256` de `dependencias-fases.md` **idéntico** al de la captura inicial (`b55670d7…`) y su numstat sigue `18 0` → no editado, no stageado, no atribuido; su cabecera se auto-fecha («Estado **al ajustar el 2026-09-21**») y su tabla dice «**Estado inicial**», así que no afirma nada sobre hoy y no es una incompatibilidad escondida — se **declara** en el README, que es lo que sí se puede escribir; DeepSeek sigue siendo el comparador y Anthropic sigue excluido | **RESUELTO (documental).** Su contenido no era una incompatibilidad que exigiera ampliar el permiso; el **revisor humano de la muestra** es **decisión humana** pendiente |
| **ESCRITURA-QMIND** — resolver consulta/ingesta real frente a la prohibición de red y el AC6 posterior al cierre de WHATSAPP frente a una sesión que debe precederlo; separar entrega offline de aceptación remota con estado parcial, entregable, responsable, disparador y evidencia; conservar verificación por contenido, saneamiento, no-PASS por instrumento ausente y tratamiento autorizado de fuentes vigentes | `01-plan-maestro.md` AC6 exigía una sola condición mezclada: quedaba abierto para siempre si el RELEASE del padre aún no tenía permiso de subida; el prompt mandaba en su arranque una `fetch_source_titles()` que **es** operación remota | `README.md`, `01-plan-maestro.md`, `05-prompt-inicio-sesion.md`, `00-lecciones-capitalizadas.md`; en su ejecución, `validate_qmind_writeback.py` y `run_all_validations.py` | **AC6 dividido en AC6-entrega / AC6-aceptación**: la primera cierra en la fase, sin red, contra la instantánea versionada; la segunda queda con dueño y momento propios (§Momentos: tabla Momento A / Momento B con qué es / red / entregable / responsable / disparador / evidencia / ACs que cierra / qué hacer si falta el permiso); §5 reclasificado como procedimiento de aceptación condicionado; el arranque del prompt se parte en tabla offline y tabla momento B, **eliminando** la instrucción remota inicial; la excepción «salvo la ingesta de prueba» desaparece (tarea 4 totalmente offline); prohibición de red ≠ permiso de subida, y el saneamiento se justifica por `do_upload()` → `qmind source upload --file` sin filtro | Las lecciones L-AJUST.1 y L-QW.4 re-ancladas a AC6-entrega y §Momentos sin crear IDs nuevos; `validate_plan_citations.py` 743 citas, 0 nuevas; `--check` del índice en verde | **RESUELTO (documental).** Ninguna subida ni consulta real se hizo: **dependencia externa** al permiso y presupuesto del operador |

## 2. Clasificación de lo que queda

| Tipo | Contenido |
|---|---|
| **Pendiente propio** (necesita su sesión y su mandato, no un cambio de contrato) | Piloto FASE-C de CONTEXTO; FASE-D y su RELEASE; FASE-C de WHATSAPP con AC5; FASE-A (congelar muestra) → B → C de JEV; la fase única de ESCRITURA-QMIND en su **Momento A** |
| **Dependencia externa** | `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` sobre el RELEASE de WHATSAPP (orden R2.5/R2.10); D4/D5 en `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`; el ID real del notebook para D8 |
| **Decisión humana / del operador** | Congelación de etiquetas y umbrales de la muestra JEV; activación de **D7** (proveedor real) y con ella la rama alcanzable de **D6**; toda autorización y presupuesto del **momento remoto** (subidas QMind, consultas reales); commit y push de este árbol; alinear o no los textos centrales que siguen desincronizados (`AGENTS.md` y la tabla de `docs/CONTRIBUTING.md` sobre DOMAIN_PRIMER), que **se declaran y no se tocan** desde aquí |
| **Deuda con dueño intacto** | **D2** (su rama literal se cumplió en parte; su apertura exige decisión propia y toca pins de `tests/`), **D3 parcial** («Plan propio, posterior»), D10 (re-leer la interfaz del write-back al cerrar) |

## 3. Qué se tocó y qué no (efectos laterales)

Archivos modificados **por esta sesión**: 35 `.md` de los cuatro planes — los 4 de
`VERIFICADOR-ESCRITURA-QMIND`, 10 de los 13 de `VERIFICADOR-CONTEXTO`, 15 de los 20 de
`REFACTOR-WHATSAPP` y 6 de los 12 de `EVALUACION-JEV` —, la orden de calidad, y la pareja
`.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` **únicamente** mediante
`scripts/build_lesson_index.py`. Quedan fuera del diff, y es intención: en CONTEXTO su
`00-lecciones-capitalizadas.md` y los prompts de A y B; en WHATSAPP su `00-lecciones-capitalizadas.md` y
los prompts de las cuatro fases cerradas (A, G, 0, B); en JEV su `00-`, sus prompts de A, C y RELEASE y su
`06-checklist` — releídos contra las tres separaciones del README (técnica / gobernanza / aceptabilidad) y
contra la exclusión de Anthropic, y **hallados coherentes**, así que no se editaron por cuota.
**Contador del diff, no de esta sesión:** `git status` lista **7** `.md` de JEV porque
`dependencias-fases.md` —el protegido— ya venía modificado por otra sesión; su `sha256` es idéntico al de
la captura inicial y su numstat sigue `18 0`, así que **no** lo edité ni me lo atribuyo. Ninguna
`00-lecciones` recibió lecciones nuevas por cuota.

- **Resto del árbol:** el numstat final de `AGENTS.md`, `docs/**`, `scripts/**`, `tests/**`,
  `.agents/**` y `.agent/knowledge/DOMAIN_PRIMER.md` es **idéntico** al de la captura inicial
  (`00-arbol-inicial.txt` → `07-huellas-finales.txt`): es trabajo de B, sigue sin commitear y no se tocó,
  no se restauró y no se atribuye a esta sesión.
- **Archivos protegidos por ser evidencia histórica:** los prompts de las fases cerradas de WHATSAPP
  (A, G, 0, B) y sus resúmenes «tras FASE-…», y los expedientes de A y B de la orden. Comprobación **por
  el mecanismo que a cada uno le corresponde**, no por una sola prueba:
  - versionados → `git status --porcelain` por ruta: `REMEDIACION-BLOQUE-A-2026-09-22/` **26 archivos
    trackeados, 0 modificados**; `.opencode/plans/Archives/` **362, 0 modificados**; los prompts cerrados
    de WHATSAPP no aparecen en el diff.
  - **sin trackear** (los dos expedientes de B, que siguen sin commitear) → git no puede probar nada, así
    que se midió por mtime: **0 archivos** de `BLOQUE-B-ORDEN-CALIDAD-2026-09-23/` y
    `BLOQUE-B-REMEDIACION-2026-09-23/` son más recientes que `00-arbol-inicial.txt` (09:54 de hoy). Eso sí
    tienen mtime de hoy: los escribió **otra** sesión, la de su corrección §13, fechada 2026-09-24 antes
    de este arranque. Se declara en vez de esconderlo, porque un `find -newermt "2026-09-24 00:00"` a
    secas los contaba como 1731 «tocados hoy».
- **Baselines sin relajar:** `.opencode/plans/plan_citations_baseline.json` y
  `.opencode/refs_baseline.txt` intactos; `--update-baseline`, `--write-baseline` y `--fix` no se usaron.
- **Índice:** 332 IDs definidos + 51 sin definición (16 análisis, 417 `.md` citados). Su delta final
  (**11/11** en el `.md` y **22/21** en el `.json`) **no es atribuible solo a C**: el índice publicado en
  HEAD no conocía las ediciones de B que siguen sin commitear, y el generador escucha también
  `.opencode/context/`, donde esta sesión editó la orden. Se regeneró **dos veces** (una por pasada) y
  `--check` pasó de `EXIT=1` a `EXIT=0` en cada una; la segunda fue necesaria porque la primera aún no
  conocía los cambios de la orden.

## 4. Comprobaciones (comando exacto, entorno, salida y código propio)

Comandos ejecutados con `./venv/Scripts/python.exe` y `PYTHONIOENCODING=utf-8`, todos **de solo lectura**
salvo el generador de índice, que es el escritor autorizado. Los instrumentos son `instrumentos/*.sh` y
`instrumentos/*.py` de este expediente (viven aquí, bajo `evidence/`, porque `tmp_test/` **sí** entra en la
población que descubre `validate_wiring.py`: con mis dos auxiliares ahí, el check leyó 1328 archivos en vez
de 1326; retirados, la pasada `11-` volvió a 1326). Salidas completas en `03-validaciones-solo-lectura.txt`,
`04-indice-lecciones.txt`, `05-validaciones-post.txt`, `06-suite-acotada.txt`, `07-huellas-finales.txt`,
`08-verificacion-final.txt` (antecedente de la anterior a retirar el scratch y a editar la orden),
`09-gobierno-final.txt`, `10-quick-final.txt`, las dos pasadas definitivas
`11-verificacion-definitiva.txt` + `12-suite-acotada-final.txt`, y las tres pasadas de repaso tras cada
última edición (`13-revision-post-jev.txt`, `14-quick-post-jev.txt`, `15-revision-post-prompt.txt`). La
tabla corresponde a la **pasada definitiva** (`11-`, `12-`), hecha después de la última edición relevante
—la de la propia orden—, que volvió a vencer el índice:

| Comando | Exit | Salida |
|---|---|---|
| `scripts/build_lesson_index.py --check` (antes de cada regeneración) | **1** en `03-` y `08-`; **0** en `11-` | `Índice de lecciones vencido: LECCIONES-INDEX.md, lecciones_index.json` las dos primeras; la tercera ya estaba fresca |
| `scripts/build_lesson_index.py` | 0 | `332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` |
| `scripts/build_lesson_index.py --check` (después) | 0 | `Índice de lecciones fresco (332 IDs)` |
| `scripts/validate_plan_citations.py` | 0 | 743 citas históricas, 0 nuevas, 0 crecimientos, 79 archivos |
| `scripts/validate_lesson_capitalization.py` | 0 | forma y trazabilidad verificadas (declara que **no** verifica pertinencia) |
| `scripts/validate_document_integration.py` | 0 | todas las comprobaciones cruzadas en verde |
| `scripts/validate_opencode_refs.py` | 0 | referencias existentes |
| `scripts/validate_plan_closure.py` | 0 | `ningún plan vivo declara cierre con filas pendientes` — es el consumidor que leería un «C cerrada» prematuro en los cuatro README |
| `scripts/validate_governance_numbers.py --report` (sin destino) | 0 | informe impreso, **sin escritura** (S12): `# no se escribio ningun archivo: pase --report RUTA para persistir el informe` |
| `scripts/run_all_validations.py --quick --check` | 0 | `TOTAL: 11/11 validations passed`; población de cableado 183 llamadas / 1326 archivos / 0 violaciones |
| `git diff --check` | 0 | sin errores de espacio en blanco; 5 avisos `CRLF will be replaced by LF` (4 preexistentes + `REFACTOR-WHATSAPP/01-plan-maestro.md`, que ya era CRLF en el disco: `i/lf w/crlf`, delta 2/2) |
| `pytest -q` sobre la suite acotada (6 rutas de instrumentos documentales y de gobernanza) | **1** | **1 failed, 172 passed** (`06-` y `12-`, idénticos) |

**El único rojo, atribuido y no ocultado:**
`tests/test_validate_lesson_capitalization.py::test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-TRIBUNAL-ENFORCEMENT-OBS-2026-09-11]`.
Es el rojo preexistente con causa ya medida por FASE-G de WHATSAPP: `9c4a001` archivó ese plan y
`clasificar_planes` solo mira hijos directos de `.opencode/plans/`. Comprobado el mecanismo sin tocar
trabajo ajeno: en HEAD los hijos directos son los cuatro planes + `Archives` + la baseline, y **este árbol
no añadió ni borró ninguna ruta** bajo `.opencode/plans/`. No se ejecutó la suite global ni el `--check`
completo, y no se modificó ningún test por comodidad.

**Artefacto conocido de la captura:** en `05-validaciones-post.txt` dos líneas del subproceso de
`Lesson Capitalization` salen con mojibake (`CapitalizaciÃ³n`) por la codificación de la consola del hijo.
El check pasó; se conserva la salida tal como se produjo, sin reescribirla.

**Revisión de forma sobre los 51 `.md` implicados** (`instrumentos/bloque_c_tablas.py` y
`bloque_c_sweep.py`):

- **Tablas** (número de columnas por fila, con vallas ``` ignoradas): 9 filas desiguales. **Ninguna es
  de esta sesión**: en los dos archivos de WHATSAPP que sí edité, mis hunks caen en las líneas 3, 67, 109 y
  111 (`06-`) y 3 y 16-17 (`10-`), y las filas marcadas están en 53-54, 94-96 y 123; las restantes son de
  `00-lecciones` (WHATSAPP y CONTEXTO, sin editar) y de una fila de 2026-09-21 en
  `VERIFICADOR-CONTEXTO/dependencias-fases.md:44`. Se declaran como condición preexistente y **no** se
  arreglan: convertir una cabecera ajena en orden de repetir trabajo es justo lo que el mandato prohíbe.
- **Matriz de este expediente:** la tabla de 6 columnas de §1 pasó el chequeo sin filas desiguales.
- **Texto:** barrido de CJK, mojibake y palabras duplicadas sobre los 51 archivos → **1** coincidencia, la
  cita deliberada del mojibake de consola en este mismo apartado.
- **Nombres exactos y secciones referenciadas:** `validate_plan_closure.py`, `validate_opencode_refs.py` y
  `build_lesson_index.py --check` en verde, que son los que resuelven rutas, símbolos y referencias.

## 5. Fronteras respetadas y mandatos no concedidos

Sin red, sin QMind, sin APIs, sin inferencias, sin instalaciones ni SDKs, sin credenciales consultadas ni
impresas, sin pipeline, sin regeneración de `DOMAIN_PRIMER`, sin archivado, sin staging, sin commit ni
push, sin `git config`/`checkout` sobre temporales, sin `stash`/`reset`/`restore`. No se creó un quinto
plan, ni un framework de reportes, ni copias manuales de métricas. No se incrementó ninguna versión
documental. No se escribió en `REGISTRY.md` ni en su tracker auxiliar, ni se re-registró fase alguna.

Que el bloque C esté cerrado **no** concede el momento remoto de ningún plan, **no** autoriza el piloto, y
**no** declara concluida la orden.

## 6. Decisiones mínimas que siguen siendo del operador

1. **Commit/push de este árbol** (documental, mezclado con el de B en el mismo `git status`). Se pide por
   separado y no se ejecuta por inferencia de «C cerrada».
2. **Mandato del piloto FASE-C de CONTEXTO** — su contrato y su prompt ya están reconciliados; el prompt
   listo para pegar se entrega en la respuesta de esta sesión y no se ejecuta aquí.
3. **Congelación de la muestra JEV** (revisor humano + umbrales), que abre el paso a su FASE-B.
4. **D7** (proveedor real), del que depende que D6 deje de estar dormida con causa.
5. Si se quiere, **alineación de `AGENTS.md` y `docs/CONTRIBUTING.md`** con la regla de DOMAIN_PRIMER:
   configuración central; requiere instrucción literal y no se hizo por arrastre.

## 7. Qué quedó listo para el piloto (y qué se reparó en el bloque pegable)

`05-prompt-inicio-sesion-fase-C.md` de CONTEXTO es la fuente canónica del piloto; el prompt que se entrega
en la respuesta de esta sesión es **derivado** de él, no una copia que gobierne. Dos cosas de ese archivo
estaban mal conciliadas y se corrigieron **dentro** del bloque, no con una nota al margen (mandato §4.C:
arreglar las instrucciones ejecutables):

1. **Contradicción performativa:** el bloque pegable terminaba con «El piloto FASE-C —ejecutar este
   prompt— no está autorizado». Pegado, ese texto ordenaba a la sesión abortarse a sí misma. Hoy dice
   «este prompt **no se autoriza a sí mismo**: si tu mandato no nombra explícitamente la ejecución del
   piloto FASE-C, para y deja checkpoint». La salvaguarda queda, la auto-anulación no.
2. **Faltaba la reconciliación final:** el bloque **no** pedía cerrar reconciliando §6 de la orden. Ahora
   lo pide, por referencia, con la casilla del piloto apoyada en la evidencia de la fase y con la
   prohibición explícita de declarar terminados los cuatro planes ni sus deudas externas
   (**D2, D3 completa, D6, D7, S10**).

Lo que el piloto encontrará ya resuelto: la elección de fuente de AC11 cerrada en la ruta (b) con sus tres
causas y sus tres tests, la pregunta `choice` con umbral sobre `confidence` (E1), el bloqueo de escritura
en §2 con revisión humana registrada (E3), `acceptance = NO-EJERCITADO` con **D6 dormida** (E4) y la
conservación del workflow canónico y del proceso común (E5). Su evidencia va a
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` (`ac10_delta.json`, `coverage.json`, `r26.txt`,
`mutation/`, y el par `baseline-pre-post`), y **no** a las rutas legado `evidence/FASE-C/`, que son de
`ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` (maestro §1, R5).

## 8. Veredicto

**C CONCLUIDO**, en el sentido exacto que pedía el mandato: cada renglón de §4.C quedó conciliado contra
su contrato vigente y su consumidor, y verificado sobre el árbol final (§4 arriba), **sin ninguna decisión
necesaria pendiente** para cerrar la parte documental. Las cinco decisiones de §6 son de **otro** tramo
(ejecución, permiso del operador o configuración central) y ninguna convierte este cierre en «concluido
con pendientes».

No hay brecha exacta que reportar: ninguna fila de §4.C quedó sin reconciliar y ninguna incompatibilidad
quedó escondida — la del archivo protegido de JEV se **declaró** en su README (§1, fila JEV) en lugar de
tocarse. **La orden no está concluida**: falta el piloto, y el piloto no se ejecutó ni se autorizó aquí.
