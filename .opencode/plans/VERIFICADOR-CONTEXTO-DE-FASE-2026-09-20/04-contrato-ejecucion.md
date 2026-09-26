# Contrato de ejecución — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

Cada prompt es ejecutable en una sesión nueva leyendo este contrato, el maestro y las filas
pertinentes de `00-lecciones-capitalizadas.md`. Este archivo **no reemplaza**
`.agents/workflows/phased_project_executor.md`; concreta su aplicación a este plan.

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está concluido
contractualmente por su propia matriz. **El bloque C de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; el piloto FASE-C de este
plan sigue sin autorizar y no se ejecutó al redactarlas.** Los permisos de este plan no amplían ese
mandato.
Fuente única de resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Permisos de la sesión

| Acción | ¿Autorizada? | Base |
|---|---|---|
| Escribir en `scripts/` (cuatro archivos nuevos) y `tests/` | **Sí** | Alcance §3 del maestro |
| Escribir en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | **Sí, solo FASE-D y solo como generado** | AC19; el directorio vive dentro del plan, no en `.agents/workflows/` |
| Leer `.agents/`, `output/`, `evidence/` de otros planes, `Archives/` | **Sí, lectura** | Necesaria para AC13, AC19 y para el denominador |
| Modificar cualquier archivo bajo `.agents/` | **No** | AC17. Configuración central, y es la fuente que el verificador auditó y que FASE-D lee |
| Reescribir un prompt de fase de otro plan | **No** | FASE-D los parsea. Reescribirlos es lo que D2/D3 postergan |
| Modificar `scripts/run_all_validations.py` o `scripts/git_hooks/pre-commit` | **No** (este plan los lee como fuente de verdad) | AC16: alteraría el conteo que otros planes publican. **Lectura actualizada el 2026-09-24 (bloque C de la orden §4.C):** en `REFACTOR-WHATSAPP` quedan pineados en sus **registros de fases cerradas** (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medidos el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra), que son evidencia histórica y no se reescribe; lo que las enmiendas de ese bloque convirtieron en «el valor lo imprime la corrida, con su comando» fueron las **instrucciones prospectivas** (su bloque de arranque y sus prompts pendientes). Eso **no** satisface el disparador de **D2**: D2 pide que deje de haber *fases en vuelo* que pineen el número, y esa decisión sigue con su dueño. **Y no es un archivo libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance, así que este plan no lo escribe pero **sí** debe re-leer su etiqueta `[15/15]` y la invocación del write-back en el cierre (deuda **D10**) |
| Ejecutar `v4complete`, `v4audit`, la pipeline o cualquier API de pago | **No** | §5 del maestro. Este plan no tiene corrida ni llamadas de red |
| **Llamadas reales a un proveedor de decisiones** | **No, en ninguna fase** | Decisión del operador del 2026-09-20: Jev no entra. AC9 certifica la **costura**, no al proveedor; activarlo es deuda **D7** |
| `git commit` / `git push` | **No implícito** | Cada fase deja el checkpoint; el commit requiere instrucción literal |
| **Escribir configuración central en el cierre** — lo que `sync_versions.py` (sin `--check`) reescribe según `scripts/sync_config.yaml`: `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md`; `VERSION.yaml` (entrada, no salida); y `docs/contributing/REGISTRY.md` con su tracker `.last_doc_phase.json` cuando se pasa `--archivos-mod` | **No implícito.** Requiere autorización literal **por destino**, comprobada antes de escribir | **Rectificación 2026-09-25:** «cierre offline» y el mandato de RELEASE **no** otorgan este permiso. `--check` y `--help` leen, no escriben. Rige **C0** del `05-prompt-inicio-sesion-fase-RELEASE.md`. Alinear la política de `DOMAIN_PRIMER` es decisión aparte; tampoco la cubre un sync de cabeceras |
| Write-back a QMind | **No en fases de implementación.** En RELEASE **solo con autorización literal propia** | Orden R2.5/R2.10 lo sitúa antes del `git mv`; eso fija su *posición*, no su *permiso*. Es operación remota: ver §Dos momentos del cierre |
| Consulta a QMind (deuda D8 / consulta Q7) | **No por defecto.** Requiere la misma autorización literal | La regla «la consulta no concede permiso de subida» vale al revés: tampoco una subida autorizada concede lectura libre |

**Regla de cero red.** FASE-B y FASE-C se prueban contra proveedores **falsos**. Si una sesión
necesita llamar a un servicio real para avanzar, para y deja checkpoint: la llamada no se autoriza
por conveniencia. Consecuencia aceptada y escrita en el maestro: ningún AC de este plan mide calidad
de decisiones de un modelo real.

**Alcance de la regla (precisión del bloque C, 2026-09-24).** «Cero red» gobierna las **pruebas** de
proveedor de decisiones en las cuatro fases de implementación; no describe el cierre de FASE-RELEASE,
que por su orden R2.5/R2.10 contiene dos operaciones remotas (la consulta Q7 y el `--upload`). Decir
que RELEASE «no hace ninguna llamada de red» y a la vez ordenar esas dos era la contradicción que la
fila `CONTEXTO/RELEASE` de la orden de calidad §4.C pedía resolver. Se resuelve separando momentos, no
borcando ninguna de las dos mitades: ver §Dos momentos del cierre.

## Dos momentos del cierre (añadido por el bloque C de la orden de calidad §4.C)

| Momento | Qué contiene | Red | Autorización | Qué se publica si falta |
|---|---|---|---|---|
| **Cierre offline** | Lecturas y verificadores sin escritura; sync, documentos, registro y derivados únicamente sobre destinos autorizados | **No** | Mandato de RELEASE más autorización literal de los archivos escribibles, comprobada en C0 del prompt RELEASE | Detenerse antes de escribir si falta un destino necesario: `PENDIENTE-AUTORIZACION`, no cierre cumplido |
| **Aceptación remota** | re-corrida de la consulta Q7 (D8) y `--upload` del `10-analisis` antes del `git mv` (D9) | **Sí** | **Literal y propia para cada una**, con presupuesto escrito | Estado `PENDIENTE-AUTORIZACION` con su causa, **no** un PASS ni un `[OK]` por omisión |

**Rectificación 2026-09-25:** «cierre propio de la fase» no otorgaba permiso sobre configuración central.
Rige **C0 del `05-prompt-inicio-sesion-fase-RELEASE.md`**: releer los destinos reales antes de escribir.
`sync_versions.py --check` no escribe; el sync en escritura requiere autorización literal para sus
consumidores de `scripts/sync_config.yaml`. `VERSION.yaml` es entrada, con permiso propio para cambiarla.
La alineación de política de DOMAIN_PRIMER no se autoriza mediante el sync de cabeceras. Tampoco se
actualizan baselines para absorber errores. Sin permiso suficiente, checkpoint previo, no cierre completo.

El archivado (`git mv`) es un **tercer** momento y conserva su autorización separada: no la concede el
cierre offline ni la sustituye una subida pendiente. Con la aceptación remota pendiente, el plan
**puede** archivar solo si el operador lo autoriza expresamente sabiendo que la fuente no se publicó;
si no, deja checkpoint. Nunca se promueve un resultado parcial a éxito del cierre (§Orden del cierre).

## Enmiendas prospectivas ya resueltas para FASE-C (registradas el 2026-09-23)

Fuente: `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.C, fila `CONTEXTO/C`, con
autorización local del operador sobre **este** plan y solo sobre **estas** cinco decisiones. **Ninguna
se implementó todavía**: son contrato para la sesión de C, no trabajo hecho. No acompañan cambio de
versión, de `REGISTRY.md` ni de configuración central.

| # | Regla que C debe cumplir | Qué deroga o precisa |
|---|---|---|
| **E1** | La pregunta de pertinencia es **`choice` de dos opciones**, con `confidence` leída como campo **independiente** del umbral. **Prohibido equiparar `probabilidad_si` con confianza.** | Precisa AC12 y su `basis`; la forma está en `scripts/decision_client.py` (`RespuestaEleccion` / `RespuestaNoul.confidence = None`) |
| **E2** | C consume `.opencode/lecciones_index.json` **después de ejecutar ella misma** la comprobación de frescura. Prohibido apoyarse en que `[6/7]` del hook u otra sesión lo regeneró. `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` son tres causas con su test cada una | **Cierra la elección abierta de AC11** en la ruta (b); con la ruta (a) `VENCIDO` habría dejado de existir y el AC pediría tres estados a un diseño de dos |
| **E3** | Una propuesta del proveedor falso **no** entra en §2 de `00-lecciones-capitalizadas.md` por sí sola: pasa a `a-revisar-humano` y solo entra con **revisión humana explícita**, dejando la **aceptación o el rechazo registrado** con quién lo decidió. Un rechazo se publica, no se borra | Corrige el paso 6 de post-ejecución del prompt de C, que mandaba «aplicar lo que proponga» sin filtro humano |
| **E4** | El tramo **semántico** de AC15 se publica `NO-EJERCITADO` con su motivo y **D6 queda dormida**. No se simula una aceptabilidad con el falso para cerrar el AC | Refuerza lo ya escrito en el prompt de C; queda elevado a contrato para que no dependa de leer un párrafo |
| **E5** | C **conserva el workflow canónico y el proceso común vigentes**: lee `.agents/workflows/phased_project_executor.md`, cierra con los seis pasos de este contrato, y no renumera checks (AC16 delta 0 sobre los valores que imprime la corrida, no pineados) | Lo que C conserva es el proceso común **tal como lo deja el bloque B**, cuyo estado vigente es la matriz §13 de la fuente única indicada al inicio; los dictámenes anteriores se conservan retirados. Ejecutar dentro de C una mejora de proceso sería colar un cambio de gobierno por arrastre de una fase |

**Reconfirmación de E1 y E2 contra el cliente real (2026-09-24, bloque C de la orden de calidad).**
No es una renegociación: es el contraste que la fila pedía, hecho sobre el código que ejecuta C y no
sobre su documentación ni sobre la transcripción de este contrato. `scripts/decision_client.py` sigue
dando la forma que E1 asume — `RespuestaEleccion` declara `__slots__` con `confidence` y su validación
**exige** el número (`confidence ausente o fuera de [0,1] - sin ella no se puede…`), mientras
`RespuestaNoul` fija `confidence = None` en la propiedad de clase y **la puerta rechaza** que un `noul`
la reporte (`noul no debe reportar confidence`), con `a _en_rango` gobernando `probabilidad_si` por
separado. **Conclusión: E1 y E2 quedan coherentes con el cliente vigente y no se mueven.** La lectura
completa con sus anclas simbólicas está en la evidencia del bloque C.

**Invariante que ninguna enmienda mueve:** el triaje es **aditivo** (AC10, `removed: []` con su test),
todo conteo lleva su **denominador** (AC15/AC2), todo verificador de detección se cierra con su
**mutation check** sobre el símbolo real del guard (AC14), al menos un test corre sobre **corpus real**
archivado con su skip declarado (AC13), y **la red sigue prohibida** en las cuatro fases (§Regla de
cero red). Lo enmendado es la **forma de la pregunta, la fuente de la frescura y el destino de las
propuestas**; no el nivel de garantía.

**Antecedente de las enmiendas, no estado actual de D1/S13.** Los dos párrafos siguientes conservan
las declaraciones de la conciliación y de los dictámenes retirados de B; **no certifican** D1/S13:
su estado solo lo determina la matriz vigente §13 de la fuente única. La obligación de no pisar
históricos en AC14 se mantiene, sin trasladar a C la validación pendiente del arnés de B.

**Lo que NO se tocó al enmendar** (antecedente de aquella sesión): las deudas **S10** (dónde vivirá el
`import` del SDK) y **D7** (activar el proveedor) siguen pendientes y **no son bloqueantes artificiales
de una C offline** — C se cierra con proveedor falso por diseño; **D6** sigue dormida; y el **rojo
contractual** de A1–A4 (`validate_governance_numbers.py`, `exit 1`) sigue vivo porque es **D1** y pide
instrucción literal sobre `.agents/`. **⟦Rectificado el 2026-09-23 por el bloque B de la orden de
calidad, con instrucción literal del operador:⟧ D1 se ejecutó desde su fuente y el árbol real de
`.agents/` ya sale `SIN-HALLAZGOS` (`exit 0`); las cuatro aserciones quedaron como contraejemplo
congelado en `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes. Este contrato de C ya
no puede dar por vivo ese rojo. La conciliación de FASE-B con la remediación del bloque A está en
`dependencias-fases.md` §Conciliación y §Ejecución del bloque B.**

**S13 — dictamen anterior retirado; estado vigente solo en §13.** ⟦El dictamen del
2026-09-23 decía **«S13 resuelta por el bloque B y completada en su remediación el mismo día»**: el arnés
`test_governance_numbers_mutation_por_asercion.py` ya no escribe en
`evidence/…/FASE-A/mutation/`; su evidencia va a destino temporal explícito y **se observan las
operaciones de escritura** del escritor real (`tests/support_observador_escrituras.py`, alcance
declarado: proceso de pytest, no procesos hijos), con ancla positiva y con los tres controles
negativos del mandato sobre un expediente desechable (a escritor redirigido a destino protegido,
b bytes idénticos, c mtime restaurado). La comparación de contenido **y** metadatos del expediente
protegido se conserva además. El
párrafo siguiente sigue vigente como **regla para el mutation check propio de C (AC14)**, salvo su
última frase, que la remediación dejó corta: se reemplaza «por hash de objeto» por «por operaciones
de escritura observadas, más contenido y metadatos» — un `utime` restaurado deja el estado final
idéntico y solo el observador lo ve.⟧ **Antecedente del defecto original:** el arnés de mutación de FASE-A
(`test_governance_numbers_mutation_por_asercion.py`, por su constante `EVIDENCE` junto a `SCRIPT`) tenía el
**destino de escritura hardcodeado dentro de `evidence/…/FASE-A/mutation/`**: al re-evidenciar R2.8 el
2026-09-23 re-escribió 7 archivos cerrados de otra fase — sin daño, porque los 7 `git hash-object --path`
casaron con HEAD, pero con los `mtime` movidos, que es lo que hace invisible este patrón. Es la misma familia
que **S12 / L-VCF-12**, y aquella cura alcanzó a los dos verificadores, no al arnés. **Cuando C escriba su
mutation check de AC14 no puede heredar ese patrón**: su evidencia va a
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/mutation/`, el destino se declara con la ruta del
propio cierre (no como constante apuntando al directorio de otra fase), y la prueba de que no pisó pasado
exige **operaciones de escritura observadas, más contenido y metadatos**, con el alcance del observador
declarado. La redacción anterior «por hash de objeto, no por `git status`» queda como antecedente
insuficiente: una reescritura de bytes idénticos puede no cambiar ninguno de los dos.

## Dónde se escribe la evidencia (corregido en la auditoría del 2026-09-20)

Toda la evidencia de este plan va a **`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`**.
La primera versión del plan escribía en `evidence/FASE-A/` … `evidence/FASE-D/` a secas, y eso **no
estaba libre**: esas cuatro rutas raíz existen desde `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y guardan
su evidencia con exactamente los nombres que produciría este plan (`faseA_baseline_pre.txt`,
`faseA_baseline_post.txt`, `faseB_baseline.txt`, …). Escribir ahí mezclará procedencia de dos planes y
podrá **sobrescribir evidencia de un plan archivado sin que salte ninguna validación** (`validate_opencode_refs.py`
solo mira rutas bajo `.opencode/`, y `evidence/` no entra). El convenio vigente es el subdirectorio por
plan, que ya usa `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.

**Excepción de lectura, no de escritura**: `evidence/FASE-D/measure_iterations.py` conserva su ruta
legada porque es el instrumento canónico que publica el executor; no es destino de nueva evidencia.

**Discrepancia de la plantilla, rectificada dentro del proceso B:** al concebir el plan,
`.agents/workflows/templates/prompt-fase-template.md` prescribía `evidence/fase-{N}/` sin namespace;
AC17 impedía corregirla desde estas fases y se registró bajo D1. La escritura documental acotada de B
corrige ahora sus destinos y su ejemplo a **`evidence/{NOMBRE-PLAN}/FASE-{N}/`**, alineados con los de
este contrato. Es corrección del proceso B **sujeta a validación en la matriz vigente §13** de la
fuente única, no certificación de D1/S13 ni trabajo trasladado a C/D2.

## Corte de presupuesto (R2.1)

Instrumento canónico: `evidence/FASE-D/measure_iterations.py` (ruta legado, ver arriba), corte **hasta
el commit de código** cuando el commit está autorizado; cuando no lo está, el corte utilizable es
**«hasta listo para revisión»** y se declara cuál de los dos se usó — el commit es una acción posterior
y separada del cierre documental, no un corte ni condición de ninguno (executor, *Cinco cortes*).
Este plan declara presupuesto y **declara además si el instrumento corrió**. Si no corre bajo la
política de permisos de la sesión, el auto-reporte se publica en la unidad usada (`tool_use`,
`ids únicos`) y se declara que **no es comparable** con las demás. Prohibido reportar cumplimiento
estimado o mezclar unidades. Sin instrumento, la métrica se retira y se declara fuera de servicio,
no se estima. **Precondición medida el 2026-09-20**: `find . -name "*.jsonl"` devuelve **0** dentro del
workspace — es la misma condición que documentó `D-V2.1` (`PASO0-…`/`TRIBUNAL-ENFORCEMENT-OBS`,
reproducida en cuatro fases seguidas), así que esta sesión **espera** caer en el auto-reporte con unidad
declarada y lo declara, en lugar de prometer una medición que no puede hacer.

## Cierres incrementales obligatorios por fase

1. **Par pre/post del conteo de checks** en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`
   (`*_baseline_pre.txt`,
   `*_baseline_post.txt`) y `baseline-pre-post.md` con la **resta** comprobada. Delta esperado: **0**
   en las cuatro fases de implementación (AC5, AC16). FASE-D añade además su propio par de **carga de
   lectura** (AC20), que sí espera un delta distinto de cero y que se reporta aunque sea cero.
2. **Selección de tests de la fase** ejecutada, publicada con su resultado, y los rojos preexistentes
   ajenos a la fase declarados como tales con dueño y causa, sin arrastrarlos ni maquillarlos.
3. `run_all_validations.py --quick` en verde, **sin** que la fase haya tocado su composición.
4. **Registro de la fase por sí misma**: `scripts/log_phase_completion.py` al terminar. FASE-RELEASE
   **no** registra fases ajenas.
5. `build_lesson_index.py` regenerado y comprobado **sobre el mismo árbol final verificado** tras las
   ediciones de `.md` bajo `plans/` que nombren un ID (R2.10). Aplica también a FASE-D. El commit es
   opcional, posterior y autorizado por separado; no condiciona los cinco cortes. Si se autoriza,
   incluye fuentes y par generado coherentes, como exige `[6/7]` del hook.
6. Actualización de `00-lecciones-capitalizadas.md` §2 (lo que **realmente** pasó), §4 (cobertura al
   estado real), `06-checklist-implementacion.md`, `dependencias-fases.md` y `README.md` del plan.
7. **FASE-D únicamente**: `build_phase_briefing.py --check` en verde contra el árbol final, y ningún
   pack emitido con `SECCION-NO-RESUELTA` sin decirlo (AC22).
8. **FASE-D únicamente — hereda el resultado NO medido de C y lo acepta.** D no reabre C ni lo
   renegocia: registra que el tramo semántico de AC15 salió `NO-EJERCITADO`, que **D6 sigue dormida**,
   y que su disparador solo se evalúa cuando exista proveedor real (D7). Lo que D **sí** hereda medido
   de C es su parte mecánica: los tres estados del índice, el umbral sobre `confidence`, la aditividad
   y el denominador con sus ceros. El pack puede exhibir los candidatos de pertinencia, pero no puede
   presentar esa exhibición como aceptabilidad obtenida (§E4).

## Reglas sobre el pack generado (FASE-D)

- El pack es **derivado, no autoritativo**. Ninguna lectura canónica desaparece: lo que el pack no
  incluye se declara en `no_incluye[]` y en `lectura_aparte_obligatoria[]`, donde figura el workflow
  canónico porque este plan **no** lo rebaná (D3).
- Un pack no puede achicarse en silencio: sección pedida y no resuelta es un estado propio con la
  ruta intentada (AC22, L-PF6, L-PF10).
- Lleva `provenance` con HEAD, fecha y sha por fuente, y `--check` lo vence contra el árbol (AC21).
  Un pack vencido se regenera; no se edita a mano.

## Carga total y frescura del pack (añadido por el bloque C de la orden de calidad §4.C)

Las tres reglas anteriores dejan abiertos dos puntos que la fila `CONTEXTO/D` cerró: **qué se cuenta
como carga** y **qué mueve la frescura**.

**Carga total (AC20), no «bytes del pack».** El pack unifica lecturas; no las elimina. La medición de
`carga.json` publica por fase los tres sumandos y la resta se saca entre los dos totales, no entre el
pack y la lista de documentos:

| Sumando | Qué entra | Por qué no puede faltar |
|---|---|---|
| `workflow_obligatorio` | Los bytes de lo que la fase **sigue** leyendo aparte (`lectura_aparte_obligatoria[]`): el workflow canónico mientras D3 no lo rebane, y toda fuente declarada y no incluida | Si no se cuenta, el pack aparece como ahorro cuando la fase lee lo mismo más el pack |
| `coste_de_generacion` | La corrida del generador que la sesión ejecuta para obtener el pack (invocación publicada y, si el instrumento corre, su coste) | Un artefacto que hay que producir no es gratis para quien lo consume |
| `pack_consumido` | Los bytes del pack que la fase efectivamente lee | Es el único sumando que el pack reemplaza |

**Prohibido presentar la concatenación como ahorro.** Juntar N documentos en un archivo no baja la
suma de sus bytes; puede subirla (encabezados, procedencia al pie, `no_incluye[]`). El ahorro real
solo puede venir de lo que **no** se copia al pack, y eso se mide declarando qué se omitió. Un delta
cero o negativo sigue siendo resultado válido y se publica igual (AC20). La fila D3 del maestro conserva
su dueño: el recorte de la fuente **no** es lo que mide esta resta.

**Frescura por entradas relevantes; HEAD es procedencia.** AC21 fija el criterio: `--check` vence el
pack comparando **el sha256 de cada fuente listada en `sources[]` contra el árbol vigente**, y fallando
por una de tres causas distinguibles (`FUENTE-AUSENTE` / fuente con sha distinto / fuente ilegible).
`provenance.head` se publica para identificar **de qué árbol salió** el pack, no para invalidarlo: si
el sha de HEAD gobernara la caducidad, el propio commit que guarda el pack generado lo dejaría vencido
en el instante de publicarse — circularidad que la orden §4.C nombró expresamente. Consecuencias
operativas:
- el pack **no** está en su propio conjunto `sources[]`, ni tampoco el commit que lo transporta;
- un HEAD distinto con las fuentes idénticas **no** vencifica el pack: se informa el desfase como
  procedencia distinta, no como `VENCIDO`;
- la invalidación la produce un cambio en una fuente gobernada, nunca el acto de versionar el generado.

**Regeneración y verificación tras el traslado.** El `git mv` del RELEASE cambia las rutas que el pack
declara como fuentes, así que **`--check` después del traslado sin regenerar tiene que fallar**: ese
rojo es un paso del cierre, no una reparación. El orden queda fijado en §Orden del cierre: regenerar
el pack con la ruta ya trasladada y **después** verificarlo. Regenerar un artefacto derivado con su
propio generador es operación de cierre autorizada a RELEASE; **modificar `build_phase_briefing.py`
para que el check pase no lo es** (§Restricciones del prompt de RELEASE: RELEASE no modifica código).

## Reglas de forma aplicadas a los artefactos de este plan

- **Símbolos, nunca `archivo:número`** en ACs, prompts y evidencia (R2.2). Antes de citar una región,
  confirmarla con `grep`/lectura; si difiere, corregir la cita y avisar.
- **Conteos como delta** con par de archivos, no números absolutos (R2.3, R2.7).
- **Todo AC de detección se cierra con mutation check** sobre el símbolo real del guard, con las dos
  salidas en evidencia (R2.8). Verde a la primera = sospechoso y explicado.
- **Todo lector expresa tres estados** y los publica (R2.9): `sin hallazgos` / `ausente` /
  `lector fallido`. Prohibido el `except` que devuelve el valor por defecto de «no encontrado».
- **AC no legible en el artefacto = ⚠️, nunca ✅** (R2.4). Prueba práctica: si el AC no responde
  *«¿dónde lo vería un humano que solo tiene el artefacto?»*, no está listo.
- El **reporte no reescribe**: ningún script de este plan edita `.agents/` ni los planes ajenos.
- Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha**, y se re-mide al
  cerrar la fase (medición A6 del maestro: las cifras de este plan vencieron al crearse el plan).

## Orden del cierre (R2.5 / R2.10, no permutable)

**Paso 0 (D10, añadido en la auditoría del 2026-09-20):** antes de correr el bloque, verificar la
interfaz del writer contra el árbol vigente — `./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --help`
— porque `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` puede haber añadido `--title`/`--file` o quitado la
degradación a PASS. Si cambió, se re-escribe este bloque **con su nota datada** antes de ejecutarlo.
Este paso es **de lectura**: corre aunque la aceptación remota siga sin autorizar.

**Cada línea lleva su momento (§Dos momentos del cierre).** Las marcadas `⟦remoto⟧` no se ejecutan con
el permiso del cierre documental: necesitan su autorización literal y su presupuesto, y si faltan se
declaran `PENDIENTE-AUTORIZACION` sin promover el cierre a éxito. La marcadas `⟦traslado⟧` requieren la
autorización propia del archivado.

```bash
# ⟦remoto⟧ — aceptación remota, autorización y presupuesto propios
./venv/Scripts/python.exe scripts/validate_qmind_writeback.py --upload VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20
./venv/Scripts/python.exe scripts/build_lesson_index.py
# ⟦traslado⟧ — el archivado es un tercer momento, con autorización expresa
git mv .opencode/plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 .opencode/plans/Archives/
# Cola final tras todas las escrituras autorizadas: no modificar baselines para absorber errores.
./venv/Scripts/python.exe scripts/validate_opencode_refs.py
./venv/Scripts/python.exe scripts/validate_plan_citations.py
# Resolver cualquier corrección de corpus autorizada antes de regenerar los derivados.
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan>
./venv/Scripts/python.exe scripts/build_lesson_index.py
./venv/Scripts/python.exe scripts/build_phase_briefing.py --plan <ruta-vigente-del-plan> --check
./venv/Scripts/python.exe scripts/build_lesson_index.py --check
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

El `--check` del pack **no** se corrige editando `build_phase_briefing.py` ni su `provenance`: se
corrige regenerando. Si tras regenerar el pack sigue rojo, eso es un defecto del generador y su dueño
es FASE-D, no RELEASE — RELEASE lo declara y deja el checkpoint, porque tiene prohibido modificar código
fuente (§Restricciones de su prompt).

*(Forma unificada el 2026-09-20: los prompts de fase ya usaban el intérprete del `venv`; este bloque
canónico decía `python`, que bajo Git Bash resuelve al intérprete sin dependencias del proyecto. El
orden y sus argumentos no cambiaron en aquella intervención.)*

**Rectificación 2026-09-25:** retiradas las escrituras automáticas `--fix` y `--update-baseline` de la
secuencia; requieren alcance propio y nunca absorben errores. La cola del prompt y del contrato queda
alineada: últimas escrituras autorizadas → packs → índice → checks, sin sustituir C0 ni los permisos
remotos y de traslado. Si no hubo archivado autorizado, verificar en la ruta actual y declararlo pendiente.

## FASE-VERIFY: no aplica, con la razón medida

§4.6 exige **los tres** criterios de activación. Se cumplen «≥3 fases de implementación» (ahora
cuatro: A, B, C, D) y «ACs que cruzan múltiples fases» (AC15, AC16 y AC17 cruzan fases). **No** se
cumple «existe al menos una fase con ejecución E2E (`v4complete`, `v4audit`, etc.)»: este plan tiene
prohibida la pipeline y prohibida la red. Criterio 2 cae → **3 etapas**, sin sesión de certificación.

Consecuencia declarada: ningún AC de este plan puede llegar a `SUPERADO EN E2E`. Su techo es
`VERIFICADO OFFLINE` con su mutation check, o `NO-EJERCITADO` cuando algo no se ejercitó — y
`NO-EJERCITADO` **no** es una salida disponible para AC9, porque AC9 ya no pide medir una
comparación.
