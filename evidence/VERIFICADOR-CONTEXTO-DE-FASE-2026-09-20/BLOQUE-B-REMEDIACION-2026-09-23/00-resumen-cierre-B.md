# Bloque B — fuente única de resultados (continuación correctiva, 2026-09-23)

Este archivo es **la fuente única de resultados del bloque B** de
`.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`. Los demás documentos
(orden §4.B/§5, maestro, contrato, dependencias, análisis, executor, plantilla) referencian
estas matrices y contienen solo sus propias decisiones/estados; no transcriben estas cifras.

Es continuación correctiva de B. **No es FASE-B de CONTEXTO, ni el bloque C, ni el piloto FASE-C.**
El mandato que rige esta sesión llegó como adjunto del operador y **no está versionado en el repo**:
se archivó copia byte a byte en `99-mandato-de-remediacion-B-2026-09-23.txt`
(sha256 `5a12e90f04a1ab3e4536bbe451c62d6dab1deac268706fbef02b1e12a9c31394`); su procedencia y sus
límites están en `99-procedencia-del-mandato.md`. Toda cita «mandato §N» de este archivo apunta a esa
copia.

Fronteras de la sesión: sin red, sin QMind, sin commit/push, sin `VERSION.yaml`, sin `.cursorrules`,
sin hooks, sin renumerar/promover checks (D2), sin tocar la composición de `run_all_validations.py`
ni `build_lesson_index.py`, sin editar `scripts/sync_versions.py`, preservando el trabajo ajeno en
`.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`.

## Estado

**B CONCLUIDO contractualmente** (2026-09-24), únicamente con la evidencia correctiva de §13.
La primera edición de esta continuación estableció **B EN REMEDIACIÓN, NO CONCLUIDO**; ese fue
el checkpoint de arranque, no el dictamen actual. Se retira también el dictamen de §12 por
insuficiencia de evidencia: un archivo limpio con 86 CRLF pasaba sin lectura de bytes; una lectura
denegada podía pasar sin intentarse; la medición descartaba stdout del consumidor y comparaba PRE
con stubs contra POST real. Las operaciones Git prohibidas en temporales tampoco estaban separadas
de las operaciones sobre el repositorio real. §13 es la matriz vigente; §1–§12 son antecedentes
rectificados, no aceptación actual. La copia íntegra de partida está en
`CORRECCION-2026-09-24/PRE_resumen.md.snapshot`. REGISTRY no se restaura, borra ni re-registra.

### Antecedente retirado del 2026-09-23

**B CONCLUIDO en su propio alcance** (veredicto de la revalidación del 2026-09-23, §12). El dictamen
anterior (§10/§11) quedó retirado y se conserva como antecedente rectificado: su copia íntegra está
en `REVALIDACION-2026-09-23/PRE_resumen-cierre-B.md.snapshot`; las secciones 1–11 NO son aceptación
vigente, son el antecedente sobre el que §12 re-midió. Durante la revalidación el estado fue
«B EN REMEDIACIÓN, NO CONCLUIDO» desde la primera edición documental hasta que la matriz §12 se
cerró con evidencia sobre el árbol final.

Causas del retiro del tercer dictamen: contradicción «commit como quinto corte» persistente en
consumidores; el detector de finales de línea dejaba sin gobernar los bytes de archivos modificados
sin stagear y de archivos nuevos (un índice Git en LF no certifica el archivo modificado); salidas
de medición no preservadas completas ni con código de proceso; comparaciones de tiempos de
selecciones distintas vendidas como ahorro; y nombres de pruebas inexistentes en la matriz.
**Desviación reconocida**: la restauración de REGISTRY con `git checkout --` en la remediación
anterior **fue una operación no autorizada**, aunque deshiciera escritura propia; se retiran las
afirmaciones «por la vía autorizada» y «tocado solo a través del escritor» de §7. No se repitió, no
se borraron entradas y no se re-registró B; una rectificación futura del registro requiere su
autorización específica.

## 13. Corrección vigente — 2026-09-24

**B CONCLUIDO contractualmente.** Evidencia nueva exclusivamente en `CORRECCION-2026-09-24/`.
Los instrumentos y logs anteriores permanecen intactos; su presencia no certifica su suficiencia.
La aceptación se sustenta en las propiedades y negativos de esta matriz, no en el número de pruebas.

| Requisito | Prueba/artefacto previsto | Negativo por causa | Estado | Límite |
|---|---|---|---|---|
| Bytes reales cualquiera que sea el estado Git | `test_bytes_reales_en_todos_los_estados_git`, `test_lectura_fallida_nunca_certifica`, `test_lectores_git_reales_sin_escrituras`; `VDI_rojo_bytes` exit 1 por DOMAIN_PRIMER limpio con 86 CRLF | `test_control_snapshot_limpio_omite_bytes_y_post_los_lee`: el snapshot real omitía la lectura; el POST la intenta y rechaza CRLF/denegación por su causa | CUMPLIDO | Estados Git sintéticos explícitos (limpio/modificado/stageado/doble/nuevo), bytes reales; lectores Git reales probados separadamente. Sin commits preparatorios |
| Mismo trabajo PRE/POST real | `medir_recalculo_real.py`, `MED_v2_*` y `COMPARABILIDAD` exit 0: `run_all` versionado frente al actual, ambos con los mismos verificadores reales, raíces e inyección posterior al cálculo | Recálculo histórico con causa anclada a revisión: 17 cálculos frente a 8, idénticos resultados reales | CUMPLIDO | Reducción estructural y tiempos se publican por separado abajo |
| Salidas completas, también hijos | Capturador nuevo, stdout/stderr y códigos propios; `CTRL_captura` exit 0 verifica bytes de ambos canales y exits 3/7 de hijo/nieto | Desactivar instrumentación del hijo pierde la salida del nieto; la misma exigencia lo rechaza por `FALTA_SALIDA_NIETO` | CUMPLIDO | `PRE_bytes` falló por el capturador Windows y no valida el detector; `PRE_bytes_v2` sí reproduce el falso favorable. `TEST_B_preflight` detectó autocontaminación de evidencia: logs ahora en temporal durante la ejecución y preservados al terminar |
| Fixtures y permisos | Inspección previa y suite acotada `TEST_B_sin_contaminar`, con exit propio 0; solo Git lector, sin fixtures que configuren/commiteen/restauren | Los controles cargan fuentes reales con `git show` o snapshot, no ejecutan el arnés histórico prohibido | CUMPLIDO | Históricos sí ejecutaron config/commit/checkout en temporales; el checkout de REGISTRY fue sobre el repo real y no autorizado |
| Cinco cortes, consumidores y D3 | Documentos completos revisados; AC18/checklists C/D/RELEASE usan árbol final verificado, no commit; 09 §D fuente de métricas y 10 análisis por referencia; estados de B solo aquí | La revisión encontró condiciones de commit, doble transcripción y D1 aún pendiente en consumidores; se corrigieron sus instrucciones, no solo sus cabeceras | CUMPLIDO | D3 PARCIAL, dueño «Plan propio, posterior»; rebanado completo no ejecutado. Ninguna simplificación de B diferida a C/D2 |
| D1 y S13 | `CONTRATOS_reales` exit 0 imprime claves/motivos de seis mutantes, salidas del escritor y operaciones exactas; `test_control_observador_ciego_a_escrituras_conserva_mkdir` | Misma exigencia para las siete rutas: `mkdir` solo ya no pasa; bytes idénticos y mtime restaurado dejan escrituras observadas. Negativos A/B/C y observador ciego en expedientes desechables | CUMPLIDO | Hijos fuera del observador S13, declarado y probado; el arnés medido no lanza hijos. La captura de stdout/stderr de hijos es otro instrumento |
| REGISTRY↔sync | `CONTRATOS_reales`, `test_repetir_el_registro_y_cambiar_de_dia`, `test_control_negativo_escritor_real_fuera_del_temporal`, `test_escritor_y_tracker_reales_guardan_bytes_lf`; tres rondas registro→sync escritor→check, cambios de día y release distinta | Autoridad competidora solo en copia: misma exigencia rechaza la fecha de release; escritura adicional mediante escritor real fuera del root temporal es rechazada y no filtrada | CUMPLIDO | Registro real y tracker sin modificación; entry histórica de B conservada. Check real ejecutado in-process, modo lectura, con huellas y operaciones de todos sus destinos configurados |
| Cierre final | `FINAL_IDX`, `FINAL_IDX_check`, `FINAL_SUITE` (122 casos passed), `FINAL_CONTRATOS`, `FINAL_CAPTURA`, `FINAL_VDI`, `FINAL_GOBIERNO`, `FINAL_QUICK` (11/11), `FINAL_DIFF`, `FINAL_STAGED`, `AUDITORIA_final`: todos exit 0; `huellas-finales` sin cambios inesperados de archivos protegidos | Nombres exactos resueltos a AST; negativo de recálculo, autoridad de fecha, lecturas y observador ciego ejecutados; huellas distinguen normalización e índice Git de archivos intactos | CUMPLIDO | Sin --check completo, red, QMind, instalaciones, pipeline, commit ni push |
| Tiempo activo / espera | Sin transcript instrumentado | No se infieren de tiempos de comandos | NO MEDIDOS | Ausencia permitida por mandato; no estimación |
| Tráfico de la antigua corrida --check completa | Evidencia local anterior insuficiente | No se repite la llamada para investigarla | NO DETERMINADO | «Cero red» histórico retirado; no cambia por el resultado offline actual |

### Mediciones correctivas y límites

`COMPARABILIDAD` (exit 0) contrasta las seis corridas `MED_v2_PRE_1..3` y `MED_v2_POST_1..3`:
fuentes relevantes idénticas y resultados reales idénticos, sin stubs. Cambia solo el `run_all`
versionado (`git show da382b1:scripts/validate_document_integration.py`) frente al actual; **ambos**
usan los verificadores reales actuales. La inyección agrega el mismo hallazgo después de ejecutar
el verificador real. Se aísla el recálculo: no es un benchmark end-to-end de todas las versiones de B.

- Cálculos: **17 → 8** por ejecución; lecturas textuales del consumidor: **36 → 17**.
- Tiempo de `run_all`, tres procesos por modo, orden PRE/POST/POST/PRE/PRE/POST:
  PRE **1.977345, 1.972713, 2.086824 s**; POST **1.628908, 1.520310, 1.598819 s**.
  Medianas **1.977345 → 1.598819 s** (reducción observada **0.378526 s**, aproximadamente **19.1 %**).
  Son comandos reales con instrumentación y una muestra pequeña; no tiempo activo ni ahorro general
  de la fase. Ninguna comparación entre suites de distinta selección se interpreta como ahorro.
- El proceso medidor sale **1 en PRE** por recálculo y **0 en POST**; `run_all` devuelve `False` en
  ambos por la inyección. `consumer_cli_equivalent_exit=1` es la traducción declarada del retorno de
  función, **no** el código de un proceso adicional. Los códigos de procesos reales están en cada
  JSON de captura. Las primeras `MED_*` conservan el nombre ambiguo `consumer_returncode` y quedan
  como antecedente; `MED_v2_*` lo rectifica sin sobrescribirlas.
- `stdout`/`stderr` se conservan completos, incluidos los buffers que los consumidores capturan y
  descartan en hijos/nietos. `sitecustomize.py` es instrumentación local bajo este expediente, cargada
  solo mediante el entorno del capturador: no cambia hooks ni configuración del proyecto. Sus límites
  son procesos Python instrumentados y sus hijos observados mediante `Popen.communicate`; no se
  presenta como auditoría general del sistema operativo.

### Permisos, huellas y expediente real

Ampliación **solicitada y concedida en esta sesión**: «Autorizar solo normalización» de
`.agent/knowledge/DOMAIN_PRIMER.md`, exclusivamente CRLF→LF, sin regeneración ni cambio de versión.
`NORMALIZACION_autorizada` preserva el snapshot original y prueba identidad salvo esos 86 bytes CR;
`VDI_rojo_bytes` había demostrado exit 1 por esa causa sobre un archivo limpio para Git.

`huellas-revision` conserva la detección de dos cambios, no se reescribe su resultado:
DOMAIN_PRIMER por la ampliación y `.git/index` por actualización durante las lecturas Git. La huella
binaria del índice **no está intacta**. `INDEX_estado` (exit 0) comprueba sus 2.483 entradas por
ruta/modo/OID contra HEAD y **cero staged**, igual que al arranque. No se conservó copia binaria inicial
para atribuir qué campos cambiaron; no se restaura el índice ni se atribuye esa diferencia a un commit.
El comprobador conserva esa diferencia como operación observada, separada de los archivos protegidos.

REGISTRY conserva su entrada histórica `BLOQUE-B-REMEDIACION-ORDEN-CALIDAD-2026-09-23`: su declaración
«Tests: 69» describe aquel registro, no esta aceptación. No se restaura, borra, corrige a mano ni
re-registra. El checkout anterior del archivo real fue **no autorizado**; también fueron contrarias
al mandato las operaciones config/commit/checkout de fixtures temporales históricos. No son la misma
operación ni la misma superficie. Esta continuación no ejecuta ninguna de ellas. JEV, tracker,
VERSION, configuración prohibida, hooks e instrumentos/logs previos se verifican contra las huellas
iniciales, no contra el resumen anterior.

No se ejecuta `validate_agents_md.py`: su check de conteos importa la suite global mediante
`pytest --collect-only` y sus caminos no están autorizados ni demostrados seguros aquí. Las garantías
modificadas del proceso común se verifican con integración documental, gobernanza, lectores pertinentes
del quick y revisión de consumidores; no se reclama aquel gate global como ejecutado.

### Dictamen y estados propios de esta corrección

**B CONCLUIDO contractualmente** por la matriz correctiva anterior, sin reaprovechar los dictámenes
retirados como aceptación. **D1 CERRADA** en su alcance: fuente viva sin aserciones vencidas,
contraejemplo congelado con sus seis mutaciones, y destinos de evidencia de la plantilla separados
por plan/fase. **S13 CERRADA** en el alcance explícito de su observador, con escritor real y negativos
por operaciones de archivo. **D3 PARCIAL**, dueño **«Plan propio, posterior»**: B cumple la
simplificación encargada, no ejecuta el rebanado completo ni lo hace pasar por implementado.

Implementación terminada, verificación terminada, cierre documental y listo para revisión se
sostienen sin commit; el estado operativo es **espera de autorización**. Los tiempos activos y de
espera siguen NO MEDIDOS. C y piloto no se inician ni quedan autorizados por este cierre.

La frescura se verifica otra vez después de esta declaración mediante la batería `CIERRE_*`
(índice por generador, suite acotada, controles, integración, gobierno, quick, diff y huellas),
con salidas/códigos propios en este mismo destino nuevo. No se modifica ninguna fuente después
para hacer compatible un resultado fallido; si apareciera un fallo, el dictamen debe retirarse.

## 12. Revalidación del 2026-09-23 — antecedente retirado el 2026-09-24

Toda medición de esta sección se preservó con `REVALIDACION-2026-09-23/capturar.py`: cada corrida
queda en `<etiqueta>.stdout` y `<etiqueta>.stderr` **completos y sin filtrar** (creación exclusiva,
sin sobrescribir) más `<etiqueta>.json` con el argv exacto, el entorno pertinente, los sha256 de las
fuentes medidas y el **código de salida del proceso** (no de la cadena shell). Las corridas
anteriores (§1–§11 e `instrumentos/`) no se tocaron; su copia de referencia está en
`REVALIDACION-2026-09-23/PRE_*.snapshot` y en `huellas-protegidas-iniciales.json` (176 archivos).

| Requisito | Prueba/artefacto | Negativo por causa | Estado | Límite |
|---|---|---|---|---|
| Cinco cortes sin commit y consumidores compatibles | Ediciones verificadas en disco: `AGENTS.md` (§Flujo Documental), executor (§R2, R2.10, *Cinco cortes*), plantilla (checklist), `CONTRIBUTING.md` (flujo), contrato §R2.1, `dependencias-fases.md`, maestro/05/06 (E5); barrido grep sin residuos (`quinto corte`, `cuatro primeros`, `Mínimo 3`, `bloques B y C diferidos`); T4 3→1 re-medido | `DLT_deltas_revalidacion` (T4 PRE 3 → POST 1) | CUMPLIDO | El commit sigue siendo decisión del operador; C/piloto no se adaptan |
| Detector de finales de línea (bytes, sin stagear, nuevos, lecturas rotas) | Contrato nuevo en `scripts/validate_document_integration.py` (`eol_tocada`, `eol_veredicto`): limpio→lado almacenado; modificado sin confirmar o nuevo→**bytes reales**; lectura/lector roto→hallazgo. 5 regresiones nuevas en `tests/test_validate_document_integration.py` (suite 14 passed, exit 0: `TEST_eol_detector`) | `CTRL_detector_PREvsPOST_v5` (exit 0): el instrumento PRE (snapshot) da **verde falso** en S1 modificado-CRLF, S2 nuevo-CRLF y S3 lectura rota, y el POST da el veredicto esperado en los seis escenarios (S5 respeta el smudge de checkout con `autocrlf=true`) | CUMPLIDO | En `autocrlf=true`, un archivo SUCIO cuyos bytes solo difieren en CRLF de checkout también caería: aquí rige `autocrlf=input` y el criterio es la conformidad del archivo |
| Árbol real conforme en bytes | `RUN_vdi_antes_normalizar` (exit 1: los tres gobernados modificados con CRLF real marcados) → normalización byte a byte de `AGENTS.md`, `docs/CONTRIBUTING.md`, executor (numstat idéntico antes/después: `numstat_*.txt`) → `RUN_vdi_despues_normalizar` exit 0 | El rojo real del árbol antes del fix | CUMPLIDO | El escritor ahora escribe REGISTRY y tracker con `newline="\n"` (12 passed: `TEST_escritor_newline`); REGISTRY existente no se re-escribe (prohibido) |
| Salidas completas y código de proceso | Los 20+ artefactos de `REVALIDACION-2026-09-23/` (formato capturar.py); corridas anteriores intactas | Creación exclusiva: una re-corrida con la misma etiqueta falla en vez de sobrescribir | CUMPLIDO | El transcript del agente sigue sin instrumento (R12 NO MEDIDO se mantiene) |
| Matriz R1–R16 revalidada sobre el árbol final | `FINAL_suite_b`: **74 passed, exit 0** (69 + 5 regresiones nuevas), 21.945 s; nombres exactos verificados en disco (17/18 existían; se corrigió el fantasma `…_recalcula_y_el_actual_no` → `test_control_negativo_el_instrumento_versionado_re_llamaba_y_el_de_hoy_no` en `dependencias-fases.md`, con nota datada) | Negativos por causa sobre el instrumento **versionado** (`da382b1`) se conservan: R1 (escritor), R6 (17 vs 8 con la misma inyección) | CUMPLIDO | R12 NO MEDIDO y R14 NO DETERMINADO se mantienen como ausencias que el mandato autoriza declarar; el auditor independiente no llegó a reportar (ver fila de revisión) |
| PRE/POST comparable | `REC_recalculo_PRE` (`--rev da382b1 --forzar-fallo`, exit 1 = hallazgo del defecto) vs `REC_recalculo_POST` (exit 0): la misma propiedad, medida con el mismo instrumento e inyección; T1 4→0, T3 3→1, T4 3→1 re-medidos tras las ediciones de texto | El PRE anclado a revisión es el control: sin fuente versionada no existirían ni el «17» ni los 3→1 | CUMPLIDO | T5 (+52 %) se retira como comparación de ahorro: eran selecciones distintas; se publica solo la figura adversaria por test — 0.207 s/test (PRE, 50) vs **0.297 s/test** (POST, 74), sin reclamar ahorro de tiempo |
| REGISTRY y permisos | `FINAL_huellas.json`: REGISTRY y `.last_doc_phase.json` byte a byte y mtime intactos desde la apertura; sin checkout, sin borrado de entradas, sin re-registro en esta continuación | Comparación de 176 huellas protegidas: 0 desviaciones | CUMPLIDO | La restauración con `git checkout --` de la remediación anterior queda reconocida como operación **no autorizada** (§Estado); una rectificación futura del registro requiere su autorización específica |
| Índice, suites, gobierno, quick y diff finales | `IDX_regenerar` + `IDX_check_frescura` (exit 0; `.md` `897d7954…` y `.json` `86e92e17…` idénticos); `VAL_gov_report_v2` `[SIN-HALLAZGOS]` 11 viva-correcta / 8 histórica-congelada / 0 no-resuelta, exit 0; `FINAL_quick_check` 11/11, exit 0; `FINAL_git_diff_check` exit 0; staged 0 (`FINAL_git_staged`) | `VAL_gov_report` (v1, exit 1): mi propia nota de rectificación D1 citaba el literal «check 8» y el verificador la marcó como aserción viva — reescrita para conservar la procedencia por revisión (`git show da382b1:…`) sin reproducir el patrón; es el control de que el verificador tiene dientes sobre este árbol | CUMPLIDO | Re-corrida de quick/diff/índice tras la última edición documental (ver nota de frescura al pie) |
| Huellas y efectos laterales | `FINAL_huellas.json`: 176 protegidos sin desviación, `jev_intacto: true`; archivos nuevos solo en `REVALIDACION-2026-09-23/` y la edición ordenada de `00-resumen-cierre-B.md`; sin staged; esta continuación estrictamente offline (ninguna llamada de red) | — | CUMPLIDO | Los 4 fallos de la suite global siguen siendo ajenos a la superficie de B (atribuidos en §4.2, antecedente) |
| Revisión adversaria independiente | Los dos revisores delegados fueron **interrumpidos antes de reportar** (estado `killed`); ningún hallazgo ajeno fue aceptado de palabra | Sustitución declarada: barrido propio de consumidores (7 contradicciones corregidas), verificador de gobierno con dientes (v1 lo demostró cazando mi propia nota), control PRE/POST del detector y de nombres exactos (1 fantasma corregido) | LÍMITE DECLARADO | Su ausencia no se suple con su aprobación: no se reclama revisión externa alguna |

**Estado de la matriz anterior (§3).** Las 16 filas CUMPLIDO y las 2 ausencias autorizadas (R12,
R14) siguen respaldadas por la suite de 74 en verde sobre el árbol final; esta revalidación no
retiró ninguna de ellas, pero las sometió a la verificación de nombres exactos y de consumidores que
la cierre anterior no hizo.

**Frescura.** Tras la última edición de cada fuente documental se re-corrió la batería sobre el árbol
definitivo: `IDX_check_frescura_v3` (exit 0), `FINAL_quick_check_v3` (**11/11, exit 0**, 22.272 s),
`FINAL_git_diff_check_v3` (exit 0) y `FINAL_gov_report_v3` (`[SIN-HALLAZGOS]`, exit 0). Las corridas
`*_v2` y `FINAL_suite_b`/`IDX_*` anteriores quedan como antecedente de las ediciones intermedias; el
código y los tests no cambiaron desde `FINAL_suite_b` (74 passed, exit 0).

**Veredicto de la revalidación.** `B CONCLUIDO en su propio alcance` — suficiencia contractual, sin
certeza absoluta: las cinco brechas del retiro están demostradas y cerradas con dientes (cortes sin
contradicción en todos los consumidores; detector que juzga bytes reales de modificados, nuevos y
lecturas rotas, con verde falso del PRE exhibido por causa; salidas completas con código de proceso;
nombres exactos verificados y un fantasma corregido; comparabilidad PRE/POST anclada a revisión con
el ahorro de tiempo NO reclamado), la desviación de REGISTRY queda reconocida como no autorizada sin
repetirla ni maquillarla, y las corridas finales corrieron sobre el árbol terminado. Límites
declarados: R12 NO MEDIDO, R14 NO DETERMINADO, revisión externa interrumpida sin reporte, y los dos
fallos de la selección amplia (ajenos, §4.2). El bloque C y el piloto FASE-C conservan su
autorización pendiente; requieren mandato propio en una sesión nueva.

## 1. Inventario de partida: archivo → cambio → garantía que lo exige

| Archivo | Cambio pendiente de B | Garantía |
|---|---|---|
| `scripts/log_phase_completion.py` | El escritor publica `- [x] Tests passing`, `- [x] Suite NEVER_BLOCK passing`, `- [x] Capability contract verificado` sin ejecutarlos, y marca `- [x] Coherence >= 0.8 … (FALLO)` cuando el valor incumple el umbral | mandato §3 |
| `tests/test_registry_fecha_documental.py` | Interacción real registro↔sync sobre un repositorio temporal coherente (todas las rutas, incluido `VERSION.yaml`), modo escritura, repeticiones, fechas divergentes, cambio de día, comportamiento explícito al repetir | mandato §3 |
| control negativo REGISTRY | Restituir la autoridad competidora **solo en una copia temporal** debe poner roja **la misma prueba** por discrepancia de fecha | mandato §3 |
| `tests/…/test_governance_numbers_mutation_por_asercion.py` | Observar **operaciones de escritura** del escritor real durante la ejecución medida, declarar el alcance del observador, y tres controles negativos en expediente desechable | mandato §4 |
| `scripts/validate_document_integration.py` | Su resumen de errores vuelve a llamar a los validadores (medido: 17 cálculos para 8 verificadores) | mandato §5 |
| `tests/test_validate_document_integration.py` | Cada resultado se calcula una vez por ejecución, conserva su diagnóstico y no se reutiliza entre ejecuciones con entradas cambiadas | mandato §5/§6 |
| `.agents/workflows/phased_project_executor.md` | §4.5 manda «Registrar cada fase del plan» contra §2.5 «FASE-RELEASE: NO registra fases anteriores»; métricas copiadas a README/09/10; cortes circulares por el commit | mandato §2 |
| `.agents/workflows/templates/prompt-fase-template.md` | Pasos 2/3/4 de Post-Ejecución ordenan re-transcribir métricas; checklist «Métricas consistentes»; cuatro cortes en vez de cinco utilizables sin commit | mandato §2 |
| `AGENTS.md` | Duplicación operativa del flujo de registro y cifras volátiles propias de B | mandato §2 |
| `docs/CONTRIBUTING.md`, `docs/contributing/{documentation_rules,validation}.md` | Alinear el contrato de registro/fecha con lo que hacen el escritor y las pruebas | mandato §2/§3 |
| orden + maestro/contrato/dependencias/análisis | Conciliar D1/D3/S13 y retirar «cero red» | mandato §7 |

## 2. Pruebas existentes que NO demuestran lo que afirman

| Prueba | Qué afirma | Qué mide en realidad |
|---|---|---|
| `test_motor_de_sync_no_conoce_el_registry_temporal_estampado` | «al aplicar las reglas (check, sin escribir), el REGISTRY temporal queda intacto en contenido y en mtime: nadie lo reescribe» | Solo `sync_all(check_only=True)`, que **no puede** escribir por diseño; el motor ni siquiera apunta al `tmp_path` (usa el `ROOT_DIR` real), así que la afirmación sobre «el expediente temporal» no está ejercitada |
| `test_sync_check_repetido_no_reescribe_la_fecha_del_registry_real` | interacción repetida | `--check` dos veces sobre el repo real: cubre el modo lectura, no registro→sync en **modo escritura** |
| `test_repetir_el_registro_mantiene_una_sola_cabecera_de_fecha` | comportamiento al repetir | Dos corridas **el mismo día**: no distingue «actualiza la cabecera» de «nunca la toca» y no puede ver una fecha desfasada |
| `test_log_phase_estampa_fecha_de_ultima_entrada_documental` | que el log estampa | Llama a `actualizar_registry()` y escribe a mano; no pasa por `main()`, así que `.last_doc_phase.json` y el resto del camino real quedan fuera |
| `test_la_huella_detecta_reescritura_de_bytes_identicos` | «control negativo por causa» de S13 | Define su propia `pareja()` (duplica `_huellas`) y provoca el rojo con `os.utime`: prueba la técnica en abstracto, no que **el observador del arnés** cace una escritura real |
| `test_re_medir_no_reescribe_expedientes_cerrados` | que nadie escribe en `evidence/` | Instantánea antes/después alrededor de funciones puras: no observa aperturas de escritura ni rutas indirectas |
| `test_el_arnes_no_conoce_ruta_de_evidencia_como_destino_de_escritura` | guard estructural | Busca en el texto de un archivo las palabras `evidence` y un token de escritura **en la misma línea**: una ruta guardada en variable la evade |

**Cierre de estas siete filas.** Las seis primeras quedaron sustituidas por las pruebas de §3. La
séptima (`test_el_arnes_no_conoce_ruta_de_evidencia_como_destino_de_escritura`) **se conserva tal cual
y con su límite a la vista**: es un guard de texto, fácil de evadir, y ya no es la pata dura — la dura
es la observación de operaciones de escritura (R4/R5). Se deja las dos: el guard dice «el arnés no
conoce la ruta como destino», el observador caza la escritura aunque la conozca.

Un defecto propio encontrado al re-verificar: el predicado `_aprobaciones_no_ejecutadas()` tomaba
`bloques[-1]` del REGISTRY, y como el escritor inserta la entrada **antes** del último separador, ese
último bloque era `## Formato` → verde vacío. Hoy se ancla a la cabecera `## <FASE> - ` y **lanza** si
la entrada no existe.

## 3. Matriz de autoverificación (requisito → prueba/artefacto → negativo por causa → estado → límite)

Estados al abrir la matriz: `PENDIENTE`. Re-llenados al cerrar con el verde de la última corrida
(`instrumentos/FINAL_arbol_terminado_v2.txt`, 69 passed exit 0 sobre el árbol final).

| # | Requisito (mandato) | Prueba / artefacto | Negativo por causa | Estado | Límite declarado |
|---|---|---|---|---|---|
| R1 | El registro real no publica aprobaciones que no ejecutó (§3) | `test_el_registro_no_publica_aprobaciones_que_no_ejecuto` + `test_generar_entrada_registry_conserva_los_datos_declarados`, ambas sobre el `main()` real; salida del escritor en el árbol: `POST_registro_b_v2.txt` | `test_control_negativo_el_escritor_permisivo_vuelve_a_afirmar_de_mas`: **corre el escritor commiteado en `da382b1`** (leído con `git show`, materializado en un temporal) sobre el mismo expediente y su `- [x] Tests passing` rompe la misma exigencia | CUMPLIDO | el escritor **declara, no verifica**: una línea sin `[x]` no significa «falla», significa «no verificado aquí» |
| R1-b | El registro no afirma ausencias que no comprobó (§3, hallazgo de la revisión) | `test_sin_datos_no_se_afirma_una_ausencia`: sin `--archivos-*` la entrada dice «Sin dato declarado», dos veces, y no `_Ninguno_` | el escritor de `da382b1` publicaba `_Ninguno_` (visible en `instrumentos/REGISTRY_primera_entrada_B_2026-09-23.md.snapshot`) | CUMPLIDO | `--archivos-mod` se omitió a propósito: pasarla haría escribir `.last_doc_phase.json`, que el mandato solo autoriza si el escritor lo necesita |
| R2 | Interacción real registro→sync en modo escritura, repetida, con fechas divergentes y cambio de día (§3) | `test_interaccion_real_registro_sync_escritura_y_check` + `test_fecha_de_release_distinta_de_la_de_entrada_llega_a_los_otros_docs`, sobre `Expediente` (VERSION.yaml, `sync_config.yaml` real copiado, los cinco consumidores versionados byte a byte; `lpc.main()` real con sus globals y `SyncEngine` con `ROOT_DIR`/`VERSION_FILE` redirigidos al mismo temporal) | `test_control_negativo_restituir_la_autoridad_rompe_la_misma_exigencia`: restituye `registry_last_update` **solo en la copia** y la roja la pone la discrepancia `2026-09-23` vs `2026-09-20`, no un fallo de import (precondiciones: la regla no estaba en la copia, y el único delta del expediente es esa regla restituida) | CUMPLIDO | redirige globals del módulo y `git` no se ejecuta de verdad: prueba el contrato registro↔sync, no un checkout real |
| R2-b | Todas las rutas del escritor, incluido el auxiliar, redirigidas y **comprobadas** (§3, hallazgo de la revisión) | `_exigir_interaccion` exige además que `.last_doc_phase.json` aparezca entre las **aperturas de escritura observadas** del registro y que su contenido sea `{"modules/ejemplo.py": "FASE-X"}` | si el tracker se fuera al repo real, no estaría dentro del expediente y la aserción cae | CUMPLIDO | observa aperturas del proceso de pytest, no del SO |
| R3 | Comportamiento explícito al repetir un registro, sin vender idempotencia (§3) | `test_repetir_el_registro_y_cambiar_de_dia` (dos registros **en días distintos** sobre el mismo expediente) + `test_la_entrada_cerrada_antes_no_se_toca` | una cabecera duplicada o una fecha vieja ponen roja; si el escritor dejara de ser aditivo, la segunda también | CUMPLIDO | el escritor sigue **apilando** una entrada por llamada: «una entrada por fase» es regla del flujo (§4.5 del executor), no propiedad del instrumento |
| R4 | Observar operaciones de escritura del escritor real (§4) | `tests/support_observador_escrituras.py` (única implementación de `huellas()` y del observador) + `test_la_ejecucion_medida_no_abre_ninguna_escritura_dentro_de_evidence`, que primero **ancla** que el observador vio las escrituras reales del arnés | `test_control_a_el_escritor_real_redirigido_a_destino_protegido_es_cazado`: el mismo observador y el mismo escritor, en expediente desechable | CUMPLIDO | alcance declarado por el propio instrumento (`ALCANCE`): proceso actual, `pathlib`+`builtins.open`+`os`+`shutil`, rutas indirectas incluidas; **no cubre procesos hijos** |
| R5 | Bytes idénticos y mtime restaurado no ocultan la escritura (§4) | `test_control_b_reescribir_bytes_identicos_se_observa_aunque_el_hash_no` + `test_control_c_mtime_restaurado_no_oculta_la_escritura_al_observador`; el par contenido+metadatos sigue en `test_re_medir_no_reescribe_expedientes_cerrados` | los dos controles **son** el negativo: el hash no cambia / el mtime vuelve a su valor y aun así la apertura aparece en `operaciones` | CUMPLIDO | se observan llamadas al mecanismo de escritura, no eventos del sistema de archivos |
| R6 | Resumen de errores sin recálculo; resultado una vez por ejecución (§5) | `run_all` con `resultados` materializado + `test_cada_verificador_se_calcula_una_sola_vez_por_ejecucion`, `test_el_conteo_impreso_sale_del_mismo_calculo_que_el_diagnostico_impreso`, `test_una_ejecucion_nueva_con_entradas_cambiadas_no_reutiliza_el_resultado` | `test_control_negativo_el_instrumento_versionado_recalcula_y_el_actual_no`: el módulo de `da382b1` (leído con `git show`) da **exactamente 17** (3 el que falla, 2 los otros siete) y el del árbol **8**, con la misma inyección | CUMPLIDO | el control mide la estructura de `run_all` con stubs puros sobre el módulo versionado (ese módulo, materializado en un temporal, no vería el repo); no cambia el número ni el orden de los 8 checks |
| R7 | Contradicción «RELEASE no registra» vs «registrar cada fase» resuelta sin re-registrar (§2) | executor §4.5 «Paso 4.5.1: **Verificar** el registro de las fases (NO re-registrar)» + regla «una entrada por fase» + §2.5 y AGENTS alineados; `--quick --check` 11/11 | `T4` de `POST_deltas_b.txt` cuenta las frases que ordenaban (re)registrar por cada fase: 3 → 1 | CUMPLIDO | el contador es la **regex nombrada** en `medir_deltas_b.py`, no una medida de ausencia; la 1 residual es la frase del registro v2.25.0 que **describe** el arreglo citando la redacción vieja |
| R8 | Duplicación de métricas sustituida por referencia a la fuente (§2) | plantilla pasos 2/3/4 + checklist; executor §4, 09 §D y `10-analisis` referencian; E8b deja de pedir dos copias a mano; AGENTS: `Estado Actual`, `§Pruebas` y el árbol de estructuras **ya no re-transcriben** el conteo de tests, apuntan a `Cobertura por Modulo` | `T3`: 3 → 1 instrucciones que mandaban transcribir | CUMPLIDO | mismo límite de R7 (regex nombrada); `README.md` y planes ajenos no se tocan |
| R9 | Cinco cortes utilizables **sin** commit; el commit no es condición circular (§2) | executor «Proceso común» → *Cinco cortes, utilizables sin commit* + §R2.1 con la alternativa + **el frontmatter que lee el router** (`description:`) dice ahora «—o, si el commit no está autorizado, en «listo para revisión»» + checklist de la plantilla | exigir el commit para cerrar un corte vuelve a hacer circular la norma | CUMPLIDO | R2.1 sigue midiendo «hasta el commit de código» **cuando** el commit está autorizado; cada sesión declara cuál usó |
| R10 | «Sin lecciones nuevas» compatible con todos los pasos de cierre, sin cuota (§2) | executor cierre + FASE-VERIFY + `lecciones-capitalizadas-template.md` §3 («No es una cuota de lecciones nuevas») | una cuota «mínimo N lecciones» en un paso de cierre contradice el principio | CUMPLIDO | el ≥3 descartes de §3 sigue midiendo **consulta al corpus**, no producción de lecciones |
| R11 | PRE/POST comparable con fuentes previas sin tocar el árbol ajeno (§5) | `instrumentos/PRE_*` + `POST_deltas_b.py` y `medir_recalculo_doc_integration.py --rev` (PRE = `git show da382b1:<archivo>`, sin `checkout` ni `stash`) | el delta es el control: sin la fuente versionada no existirían ni el 17 ni los 3→1 | CUMPLIDO | la primera pasada de B **no está en git**, así que su estado intermedio no es recuperable y no se publica como PRE |
| R12 | Tiempo activo y espera de autorización separados o NO MEDIDOS (§5) | esta matriz | — | **NO MEDIDO** | sin transcript instrumentado no hay medición: se declara la ausencia, no se estima |
| R13 | Estados D1/D3/S13 conciliados entre orden/maestro/contrato/dependencias/análisis (§7) | §5 de este archivo + diffs de los cinco documentos + `validate_governance_numbers.py --report` `[SIN-HALLAZGOS]` (11 viva-correcta, 8 histórica-congelada, 0 no-resuelta) y `--quick --check` 11/11 | una fila que dijera «resuelto» junto a instrucciones que lo suponen pendiente: los contadores R7/R8 y el `--report` | CUMPLIDO | dueño de D3 intacto: «Plan propio, posterior»; ninguna obligación de B se movió a C o a D2 |
| R14 | Frontera de red: «cero red» retirado o determinado (§7) | `shutil.which('qmind')` medido sin invocar el CLI + búsqueda del stdout de aquella corrida en su evidencia | — | **NO DETERMINADO** | no puede saberse si hubo tráfico en aquella corrida (no se conservó su salida), así que «cero red» **se retira**. Esta continuación es estrictamente offline |
| R15 | Verificación final sobre el árbol final (§8) | `FINAL_arbol_terminado_v3.txt` (69 passed exit 0; `--quick --check` 11/11 exit 0; `git diff --check` exit 0; índice regenerado y fresco con las mismas huellas; trabajo ajeno, `VERSION.yaml` y el tracker intactos; nada stageado) + `POST_suite_seleccion_final_v2.txt` | — | CUMPLIDO | sin `--check` completo: su check [15/15] invoca QMind y esta sesión tiene prohibida la red |
| R16 | Registro de B con identificador inequívoco por su escritor autorizado (§3) | `POST_registro_b_v2.txt` (2ª emisión: cinco archivos nuevos declarados, Tests 69) + `POST_interaccion_registro_real_v2.txt` (`sync_versions.py --check` dos veces después) | — | CUMPLIDO | no re-registra FASE-B de CONTEXTO; `.last_doc_phase.json` y `VERSION.yaml` quedan byte a byte intactos. El contador `Total fases` pasa 498→499 porque el escritor suma **uno por llamada**, sin mirar el identificador |

## 4. Mediciones

### 4.1 PRE (árbol de partida, antes de esta remediación)

Medidas el 2026-09-23 sobre el árbol vigente (que ya incluye lo que B hizo y no concluyó).

| Instrumento | PRE | stdout |
|---|---|---|
| `pytest tests/quality_gates/governance_numbers tests/test_registry_fecha_documental.py -q` | **50 passed, exit 0**, 10.35 s | `instrumentos/PRE_suite_governance_registry.txt` |
| `run_all_validations.py --quick --check` | **11/11, exit 0** | `instrumentos/PRE_quick_check.txt` |
| cálculos de verificador dentro de `validate_document_integration.run_all()` | 8 (todo pasa: el camino del resumen de errores no se ejercita) | `instrumentos/PRE_recalculo_doc_integration.txt` |
| ídem con un fallo inyectado, **fuente anclada a la revisión** (`--rev da382b1`) | **17 cálculos / 8 verificadores → 9 extra** (3 el que falla, 2 los otros siete), exit 1 | `instrumentos/recalculo_desde_git_PRE_vs_POST.txt` |
| `qmind` en PATH | `C:\Users\Jhond\AppData\Roaming\npm\qmind.CMD` (medido con `shutil.which`, sin invocar el CLI) | fila R14 de §3 |

El «50 passed» y el «11/11» que publicaba el cierre retirado **sí reproducen**; se re-miden igual que
todo lo demás antes de afirmar el POST.

### 4.2 POST (árbol final de la remediación, tras cerrar los hallazgos de §11)

| Instrumento | POST | stdout |
|---|---|---|
| `pytest tests/quality_gates/governance_numbers tests/test_registry_fecha_documental.py tests/test_validate_document_integration.py -q` | **69 passed, exit 0**, 21.66 s (50 → 69: +19 funciones) | `instrumentos/FINAL_arbol_terminado_v3.txt` (COMANDO A; reproduce el v2, medido tras la última edición documental) |
| `run_all_validations.py --quick --check` | **11/11, exit 0** | ídem (COMANDO B) |
| cálculos de verificador con el mismo fallo inyectado | **8 cálculos / 8 verificadores → 0 extra**, `[SIN-HALLAZGOS]`, exit 0 | `instrumentos/recalculo_desde_git_PRE_vs_POST.txt` |
| `git diff --check` | **exit 0** (7 avisos informativos de `core.autocrlf=input`) | `FINAL_arbol_terminado_v2.txt` (COMANDO C) |
| staged | vacío (cero commit) | ídem (COMANDO D) |
| selección amplia (`governance_numbers`, registry, doc-integration, `test_validate_{wiring,opencode_refs,plan_citations,plan_closure,lesson_capitalization}`, `test_doctor_reads_are_utf8_pinned`, `tests/regression`) | **171 passed, 2 failed, exit 1** (76.14 s) | `instrumentos/POST_suite_seleccion_final_v2.txt` |
| `validate_governance_numbers.py --report` | `[SIN-HALLAZGOS]`, 19 instancias / 11 viva-correcta / 8 histórica-congelada / 0 no-resuelta / 0 fallos de lectura, exit 0 | corridas de 19:45, publicado además en `POST_validadores_tras_proceso_comun.txt` |
| `build_lesson_index.py` (regenerado por su generador) + `--check` | exit 0 / exit 0; `.md` y `.json` **byte a byte idénticos** a la huella de antes (`897d7954…`, `86e92e17…`), 332 IDs | `instrumentos/POST_indice_lecciones.txt` y re-verificado a 19:47 |
| `sync_versions.py --check` sobre el árbol real tras registrar B | **exit 0**, dos veces; la cabecera de REGISTRY sigue en `2026-09-23` con `date: "2026-09-19"` en VERSION.yaml | `instrumentos/POST_interaccion_registro_real_v2.txt` |

**Procedencia de los archivos de consola de esta sesión.** `POST_suite_b_remediacion.txt` es la
corrida de las 18:34 (68 passed) y por eso nombra todavía
`…aunque_el_hash_no` con la grafía anterior al renombrado; `FINAL_arbol_terminado_v2.txt` (19:48,
69 passed) es la que rige. No se reescribió el primero: la evidencia de una corrida es lo que esa
corrida imprimió.

**Atribución de los 2 fallos de la selección amplia — por causa, no por nombre:**

- `test_validate_lesson_capitalization.py::test_medido_contra_el_predecesor_entra_en_alcance_y_su_forma_es_conforme[2026-09-11-…]`:
  `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` ya no está en la población de planes evaluados porque vive
  bajo `.opencode/plans/Archives/` (movido en `e8010ce`, verificado con `git show --name-only`). El
  `AssertionError` muestra los cuatro planes que sí están en alcance, ninguno tocado por B.
- `test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`: 5
  receptores no resueltos y **los cinco dentro de `tmp_test/venv-jev-sdk/…`** (directorio existente en
  disco, del trabajo ajeno de la evaluación JEV), no de producción.

No se reclama «0 regresiones» por identidad de nombres: son previos en su causa, ajenos a la
superficie de B, y siguen rojos por el mismo motivo antes y después de esta remediación.

### 4.3 Deltas del proceso común (`instrumentos/POST_deltas_b.txt`, PRE = `git show da382b1:`)

| # | Qué se cuenta | PRE | POST |
|---|---|---|---|
| T1 | Casillas `- [x]` en una entrada de REGISTRY con los **mismos** args (`--tests '13' --coherence 0.5`) | 4 (una de ellas diciendo `(FALLO)`) | **0**, y 3 `- [ ]` + la nota «declarado, no verificado por este script» |
| T2 | Cálculos de verificador en `run_all()` con un fallo inyectado | 17 (9 extra) | **8** (0 extra) |
| T3 | Instrucciones que mandaban transcribir la métrica a un segundo documento (plantilla) | 3 | **1** (la referencia a `09 §D`) |
| T4 | Frases que ordenaban (re)registrar por cada fase (executor) | 3 | **1** (la frase del registro v2.25.0 que **describe** el arreglo) |
| T5 | Duración de la suite afectada | 10.35 s / 50 funciones = **0.207 s/test** | 21.66 s / 69 funciones = **0.314 s/test** |

T5 es **adverso y se publica igual**: +52 % por test. Las pruebas nuevas observan escrituras y levantan
repositorios temporales con los cinco consumidores reales. Ningún delta de líneas borradas se
convierte en ahorro de tiempo, y T3/T4 miden la regex nombrada en `medir_deltas_b.py`, no la ausencia
global de ese tipo de instrucción.

## 5. Estado individual de D1, D3 y S13

- **D1 — CERRADA en su alcance, con dos capas.** Las cuatro aserciones de conteo vencidas se
  retiraron de su fuente (executor ×3, plantilla ×1) y el texto ahora dice que el valor vigente lo
  imprime la corrida y lo contrasta `validate_governance_numbers.py`; las dos salidas del mutation
  check quedaron reancladas a un contraejemplo congelado en
  `tests/quality_gates/governance_numbers/fixtures/` (los dos fixtures, byte a byte iguales al árbol
  de `da382b1`, verificado en §11). Medición: `[SIN-HALLAZGOS]`, 11 viva-correcta, 8
  histórica-congelada, 0 no-resuelta, exit 0. Las entradas históricas del changelog siguen congeladas,
  no reescritas. Lo que D1 **no** cubre y el propio verificador publica: la prosa de conteo sin
  patrón, los conteos fuera de los documentos de gobierno, los pins en tests y las fuentes dinámicas
  que no son etiqueta impresa (entre ellas, el conteo de funciones de test en `AGENTS.md`, §8 abajo).
- **D3 — PARCIAL, y su dueño no cambia.** El dueño declarado sigue siendo «Plan propio, posterior»;
  esta remediación no la asume por reasignación implícita y no declara fuera de B una obligación de B.
  Lo avanzado: el principio de proporcionalidad/reuso y los cinco cortes sin commit quedaron escritos
  en el executor como pautas (no como una R2 nueva, porque promoverla es D2) y la plantilla los
  referencia. Lo que falta —el rebanado completo del workflow canónico y medir la reducción de carga—
  es de otro plan.
- **S13 — CERRADA con dientes nuevos.** El arnés ya no escribe en `evidence/…/FASE-A/`: vuelca en
  destino temporal explícito, el observador registra **operaciones de escritura** del escritor real
  durante toda la ejecución medida, y los tres controles negativos (a escritor real redirigido a
  destino protegido; b bytes idénticos; c mtime restaurado) se ejecutan sobre un expediente desechable
  con **el mismo** observador y **el mismo** escritor. La prueba que duplicaba `pareja()` y fingía el
  rojo con `os.utime` fue eliminada, no conservada. Las siete huellas de
  `evidence/…/FASE-A/mutation/` están intactas (`FINAL_arbol_terminado_v2.txt`, COMANDO D).

## 6. Frontera de red

**«Cero red» se retira como afirmación sobre la corrida anterior de `--check` completo.** Lo medido:
el CLI `qmind` está instalado y en PATH, y la evidencia de aquella corrida no conserva su stdout, así
que no puede determinarse si el check [15/15] invocó la red. Se registra **NO DETERMINADO** (R14) y
se corrige la frase de la orden y de `dependencias-fases.md`.

**Esta continuación es estrictamente offline**: ninguna llamada de red, sin QMind, sin fetch, sin
SDKs, sin credenciales. El único `subprocess` nuevo en código de producción es
`git ls-files --eol`, de solo lectura y sin red, con su fallo tratado como `LECTOR-FALLIDO` (nunca
como «sin hallazgos»). En los tests, los `subprocess` nuevos son `git show` (leer una revisión) y
`git ls-files --eol` / `git init/add/commit` dentro de `tmp_path`.

## 7. Fronteras respetadas y desviaciones

Sin commit, sin push, sin publicación, sin archivado. `VERSION.yaml` intacto (`f2cf1a5d…`,
re-verificado a 19:48). `.cursorrules` intacto. Hooks intactos. Composición de
`run_all_validations.py` y `build_lesson_index.py` intactas. Cero checks promovidos o renumerados
(D2). `scripts/sync_versions.py` **no se editó** (0 líneas en el diff).

Trabajo ajeno preservado: `EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md` sigue en
`b55670d7ef7a02c679b00f4d1f752df3c6531c347b18f09decfb0f9124be6486`, la huella con la que se abrió la
sesión; sus 18 líneas de diff son previas a esta continuación, sin stagear y sin atribuirse.

**Desviación declarada (re-registro de B).** La primera emisión de la entrada de B se publicó con un
escritor que aún afirmaba `_Ninguno_` y que omitía tres archivos nuevos. Para corregirla **por la vía
autorizada** (REGISTRY solo a través de su escritor) sin duplicar la entrada: (1) se guardó copia de
la entrada en `instrumentos/REGISTRY_primera_entrada_B_2026-09-23.md.snapshot` (huella `7c044503…`);
(2) se verificó que el único cambio de `REGISTRY.md` en el árbol eran 22+/2− de ese registro
(`git diff --numstat`) y se restauró el archivo a su blob de HEAD con `git checkout --` (huella
`0c8aa597…`, idéntica a `git cat-file blob HEAD:…`, LF); (3) se corrigió el escritor y se volvió a
registrar con él (`efbd1dcb…`). Es el único comando destructivo de la sesión y solo deshizo escritura
propia y reproducible.

Ampliaciones **expresas y usadas**, cada una con su cota:

1. `docs/contributing/REGISTRY.md`, tocado **solo** a través de `log_phase_completion.py`: cabecera
   `2026-09-19 → 2026-09-23`, total de fases 498 → **499**, entrada
   `## BLOQUE-B-REMEDIACION-ORDEN-CALIDAD-2026-09-23` con los cinco archivos nuevos. Con
   `--archivos-nuevos` y sin `--archivos-mod` para **no** escribir el auxiliar:
   `.last_doc_phase.json` quedó idéntico (`e03741e5…`).
2. Ninguna otra. No se editó ningún archivo fuera de los 11 puntos de la superficie autorizada
   (`99-mandato-de-remediacion-B-2026-09-23.txt` §AUTORIZACIÓN); cuando una comprobación necesitaba
   leer un archivo no listado, se leyó.

Efectos laterales revisados: los tests nuevos escriben únicamente bajo `tmp_path` o bajo rutas
declaradas; **dentro de lo no autorizado por el mandato**, la única escritura en el repositorio real de
esta sesión es la entrada de REGISTRY. Ninguna prueba ejecuta `sync_versions.py` en modo escritura
sobre el árbol real (R2 lo hace sobre la copia; en el real solo se corrió `--check`).

Declaración de formato: los finales de línea se certificaron **en bytes** (`eol_en_disco`) y sobre el
lado almacenado (`git ls-files --eol`), no desde `read_text()`. El detector se prueba contra un CRLF
real (`test_el_detector_ve_crlf_en_bytes_y_read_text_no_lo_ve`) y contra la confusión checkout-CRLF /
blob-CRLF. Medición en bytes con `read_bytes()` de los artefactos nuevos de esta sesión (cero `CRLF`,
todos terminan en salto de línea): `00-resumen-cierre-B.md`, `99-procedencia-del-mandato.md`,
`tests/support_observador_escrituras.py`, `tests/test_registry_fecha_documental.py`,
`tests/test_validate_document_integration.py` y
`tests/…/test_governance_numbers_mutation_por_asercion.py`. Ese último quedó normalizado a LF durante
la sesión, con el blob sin cambios verificado por numstat. Los `.txt` de consola **no** se
re-codifican: se escriben con `>>` y se conservan como salieron.

## 8. Ahorro: medido y no medido

- **Medido:** −9 cálculos de verificador por ejecución con fallos en
  `validate_document_integration.run_all()` (17 → 8), con el PRE anclado a `da382b1`.
- **Medido:** −2 instrucciones de transcripción manual en el flujo de cierre (T3 y T4), −4 casillas de
  aprobación no ganada por entrada de REGISTRY (T1) y −2 aserciones de ausencia no comprobada
  (`_Ninguno_` → «sin dato declarado»).
- **No medido:** el ahorro de tiempo del agente y la espera de autorización. Sin instrumento sobre el
  transcript de esta sesión se declaran **NO MEDIDOS** (R12) en lugar de estimarlos.
- **Adverso y publicado:** +52 % de segundos por test en la suite afectada (T5) y +~270 caracteres por
  entrada de REGISTRY por la nota de honestidad.
- **Cifra volátil heredada, declarada no maqueda:** `AGENTS.md` publicaba 4,246 funciones de test en
  cuatro sitios. Medido con el comando canónico del propio documento: **4,453 en el árbol de trabajo,
  4,424 en `da382b1`** → el retrato de `AGENTS.md` ya venía desfasado (+178 de commits ajenos a esta
  sesión) y B añade **+29** de ese delta. No se re-copió una cifra nueva: se deja **una** fuente (la
  tabla fechada `Cobertura por Modulo`) y las otras tres referencias apuntan a ella, que es lo que
  prescribe la regla «un resultado, una fuente». El verificador ya declara esta familia como no
  cubierta (`fuentes-dinámicas-que-no-sean-etiqueta-impresa`, con `funciones_test_en_disk: 4453` y el
  ejemplo vencido), así que queda como límite visible, no como silencio.

## 9. ¿Habilita esto el bloque C?

**No lo habilita ni lo bloquea B por su lado.** El bloque C y el piloto FASE-C conservan su
**autorización pendiente**: requieren un mandato nuevo en una sesión nueva, y B no puede dárselo. Lo
que B sí entrega para que ese mandato pueda redactarse: la autoridad de fecha de REGISTRY con un solo
escritor y su interacción probada en modo escritura (R1–R3), los cortes utilizables sin commit (R9),
el instrumento de observación de escrituras reutilizable (R4–R5), controles negativos que ejercitan
al instrumento versionado (R1, R6) y D1/S13 cerradas con su medición.

Deuda explícitamente **fuera de B** y no movida de B: D2 (promover/renumerar checks), D3 (dueño
«Plan propio, posterior»), el `--check` completo con su [15/15] QMind (R14 NO DETERMINADO), la
familia de conteos que `validate_governance_numbers.py` no mira (§8) y los dos fallos de la selección
amplia, que pertenecen a su plan archivado y a `tmp_test/`.

## 10. Veredicto

**`B CONCLUIDO en su propio alcance`.** Suficiencia contractual, sin promesa de certeza absoluta:

- Las 18 filas de la matriz tienen prueba/artefacto nombrado y límite declarado; 16 CUMPLIDO y las
  dos que no lo son (`R12 NO MEDIDO`, `R14 NO DETERMINADO`) son **ausencias que el propio mandato
  autoriza declarar**: R12 pide «separados **o** NO MEDIDOS», R14 «retirado **o** determinado».
- Las dos revisiones adversarias externamente producidas están verificadas en disco y cerradas
  (§11). Ningún hallazgo se aceptó de palabra y ninguno se rechazó sin medir.
- Ninguna obligación de B se declaró fuera de B para cerrarla; ninguna aserción se rebajó ni se
  actualizó un baseline para absorber un defecto; ningún fallo de instrumento se convirtió en
  resultado favorable.
- El registro de B, la regeneración del índice y los controles finales se ejecutaron **sobre el árbol
  final** y se re-midieron los checks que una edición posterior invalidaba.
- La superficie de B está verde con exit 0; los dos rojos de la selección amplia están atribuidos por
  causa y son ajenos a ella.

## 11. Revisión adversaria independiente

Dos revisores de solo lectura, cada uno con la orden, el diff y la evidencia. **Su aprobación no
reemplaza las pruebas**: cada hallazgo se re-verificó en disco antes de actuar, y abajo consta el
resultado de esa re-verificación.

| # | Hallazgo | Verificación en disco | Acción | Estado |
|---|---|---|---|---|
| 1 | El resumen de cierre no cerraba (matriz `PENDIENTE`, sin POST ni veredicto) | cierto al momento del informe (19:20); el archivo se completó después | §3 re-llenada, §4.2/§4.3, §10 | CERRADO |
| 2 | Estados «RESUELTA» citaban una matriz pendiente (`10-analisis`, `dependencias-fases`, orden) | los tres documentos apuntan a este archivo; la matriz ahora está llena | reconciliado, sin cambiar ningún estado | CERRADO |
| 3 | 2 fallos rojos sin atribuir | reproducidos (`POST_suite_seleccion_final_v2.txt`) | causas medidas: `e8010ce` archivó el plan; los 5 receptores están en `tmp_test/venv-jev-sdk/` | CERRADO (ajenos, §4.2) |
| 4 | REGISTRY decía «Archivos Modificados: _Ninguno_» con 20 archivos tocados y omitía 3 nuevos | `docs/contributing/REGISTRY.md` de la 1ª emisión, snapshotneado | escritor corregido (`Sin dato declarado…`, con comentario del porqué) + prueba `test_sin_datos_no_se_afirma_una_ausencia` (R1-b) + re-registro con los 5 archivos | CERRADO (§7 desviación) |
| 5 | Los controles negativos de R1 y R6 reimplementaban el defecto dentro del test | `tests/test_registry_fecha_documental.py` y `tests/test_validate_document_integration.py`, líneas citadas | los dos controles cargan el módulo de `da382b1` con `git show` y lo ejecutan: 17 vs 8 y `- [x] Tests passing` del escritor real | CERRADO (R1, R6) |
| 6 | `.last_doc_phase.json` redirigido pero nunca comprobado | `Expediente.tracker` sin aserción | `_exigir_interaccion` exige apertura observada + contenido exacto (R2-b) | CERRADO |
| 7 | El PRE de «17 cálculos» no estaba anclado a una fuente versionada | `medir_recalculo_doc_integration.py:32` leía el árbol | añadido `--rev`; `recalculo_desde_git_PRE_vs_POST.txt` fija 17 en `da382b1` | CERRADO (§4.1) |
| 8 | El delta adverso de tiempo no estaba publicado | T5 decía «leer los archivos» | T5 con 0.207 → 0.326 s/test declarado en §4.3 | CERRADO |
| 9 | `AGENTS.md` seguía publicando 4,246 funciones que su propio comando refuta | 4,453 árbol / 4,424 HEAD medidos con el grep canónico | tres re-transcripciones sustituidas por referencia a la tabla fechada; la familia queda declarada no cubierta | CERRADO como **declaración**, no como maqueo (§8) |
| 10 | El docstring de `test_governance_numbers_por_asercion_no_por_linea.py` describía el árbol real, no el contraejemplo congelado | líneas 3-6 del archivo | reescrito: apunta a `fixtures/` y remite la regresión del árbol a `reproduce_A1_A4` | CERRADO |
| 11 | El frontmatter del executor, que lee el router, seguía diciendo «cortadas en el commit de código» sin alternativa | `phased_project_executor.md:2` | añadido «—o, si el commit no está autorizado, en «listo para revisión»…» con puntero a *Cinco cortes* (R9) | CERRADO |
| 12 | Las citas «mandato §N» no apuntaban a nada versionado | `grep "11 puntos"` solo encontraba la propia cita | mandato archivado byte a byte + nota de procedencia con su sha256 | CERRADO (cabecera de este archivo) |
| 13 | `test_el_arnes_no_conoce_ruta_…` se conserva con la misma heurística que §2 condena | `test_governance_numbers_mutation_por_asercion.py:429` | §2 declara por qué se conservan las dos y cuál es la pata dura | CERRADO como límite declarado |
| 14 | T3/T4 miden su propia regex | `medir_deltas_b.py` | límite escrito en R7/R8 y en §4.3 | CERRADO como límite declarado |
| 15 | «La única escritura en el repositorio real» sobre-afirmaba | texto de §7 | frase acotada a «dentro de lo no autorizado por el mandato» | CERRADO |
| 16 | `[7/7]`, `[6/7]` fijos en el executor | `--report`: 11 aserciones vivas conformes, 8 históricas autorizadas, 0 no resueltas | nada que tocar: son la forma que el verificador aprueba | RECHAZADO con medición |
| 17 | «4,246» debería actualizarse a la cifra de hoy | 4,453 hoy, 4,424 en HEAD | copiar 4,453 en `AGENTS.md` sería publicar la cifra que el próximo commit invalida; se aplicó la regla de una sola fuente | RECHAZADO con motivo (§8) |

Defecto propio encontrado al re-verificar (no vino de los revisores): el predicado de R1 era **verde
vacío** por mirar el último bloque del expediente. Corregido y anotado en §2.

**Re-medición tras cerrar los hallazgos.** Las correcciones tocaron código de tests, el escritor,
`AGENTS.md`, el frontmatter del executor, `documentation_rules.md`, la orden y `dependencias-fases.md`,
así que se volvieron a correr sobre ese árbol: suite de B (69 passed, exit 0), `--quick --check`
(11/11, exit 0), `git diff --check` (exit 0), `build_lesson_index.py` regenerado + `--check` (exit 0,
mismas huellas `897d7954…`/`86e92e17…`), `validate_governance_numbers.py` y
`validate_document_integration.py` (exit 0), y las huellas de trabajo ajeno / `VERSION.yaml` / tracker
re-verificadas. Todo en `instrumentos/FINAL_arbol_terminado_v3.txt` (19:59). La selección amplia sigue
con los mismos dos rojos ajenos y 171 verdes.
