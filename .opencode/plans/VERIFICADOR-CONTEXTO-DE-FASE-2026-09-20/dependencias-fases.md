# Dependencias y bloqueantes — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

**Estado de B: consultar §13 de la fuente única enlazada abajo.** El bloque B está **concluido
contractualmente** por su propia matriz. El **bloque C** de esa orden quedó autorizado el 2026-09-24
solo como enmiendas prospectivas sobre los documentos de los cuatro planes; **el piloto FASE-C de este
plan no lo estaba** y ninguna de sus fases se ejecutó ni se diseñó al conciliar.
**⟦Rectificado el 2026-09-24 al cerrar FASE-C⟧**: esa frase sigue siendo cierta sobre el **bloque C**
(enmiendas documentales) y ya no lo es sobre el **piloto**: el operador autorizó esa tarde, con mandato
propio y corte **«hasta listo para revisión»**, ejecutar FASE-C, que quedó **cerrada sin commit ni push**
(ver su fila en §Cadena y su evidencia en `evidence/…/FASE-C/`). Fuente única de
resultados y estados D1/S13:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
**§13, única matriz vigente**; §1–§12 son antecedentes rectificados, no aceptación actual.
D3 permanece parcial, con dueño **«Plan propio, posterior»**. Los cierres de FASE-A/B y la
conciliación del bloque A se conservan como históricos, distintos de la remediación del bloque B.
Evidencia de las enmiendas del bloque C:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

## Cadena

```
FASE-A ──► FASE-B ──► FASE-C ──► FASE-D ──► FASE-RELEASE-4.xx.0
 (lint      (costura   (triaje    (pack       (docs, sync, REGISTRY,
  determ.)   proveedor) pertin.)   briefing +  write-back, archivar)
                                    delta de
                                    lectura)   └─ VERIFY no aplica (§4.6 cae en criterio 2)

A y B son técnicamente independientes; C consume a ambas y D consume a las tres.
Se mantienen secuenciales por la Regla de Sesión Única del executor.
```

**No ejecutar fases en paralelo ni encadenarlas dentro de una sesión.** Un checkpoint no
habilita la fase siguiente.

| Orden / prompt | Objetivo | Complejidad | Estado |
|---|---|---|---|
| 1 · [FASE-A](05-prompt-inicio-sesion-fase-A.md) | `validate_governance_numbers.py`: aserción contra fuente dinámica, con denominador y tres estados | MEDIA técnica / ALTA consecuencia: es el guard de las ediciones futuras sobre `.agents/` | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC1–AC5)** |
| 2 · [FASE-B](05-prompt-inicio-sesion-fase-B.md) | `decision_client.py`: costura neutra, contract test con proveedor falso y **un solo** proveedor configurable; AC9 certifica que añadir el segundo cuesta un archivo | MEDIA-ALTA: la superficie que cambia de proveedor sin que nadie más se entere | **✅ CERRADA 2026-09-21 — VERIFICADO OFFLINE (AC6–AC9; AC16/AC17/AC18 en su parte)**. **Conciliada el 2026-09-23** con la remediación del bloque A de la orden de calidad: **S11 y S12 aceptadas** (corrección técnica en `fdd397f`, no de esta sesión); AC9 declarado con su alcance local. Ver §Conciliación |
| 3 · [FASE-C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: capa de pertinencia **aditiva** sobre `lecciones_index.json`, nunca filtro | ALTA: es la mitad que el verificador de capitalización declara fuera de alcance | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE su mecánica (AC10–AC14 y AC15 en su parte no semántica; AC16/AC17/AC18 en su parte de C). AC15 queda ⚠️ PARCIAL con `acceptance = NO-EJERCITADO` (contrato E4), que es el techo alcanzable con D7 sin activar.** Cortes: la fase llegó **hasta listo para revisión** y se paró ahí. **Push hecho el 2026-09-24** por instrucción literal del operador: publicó `da382b1..5817edd`. ⟦**La paridad no se publica como cifra (2026-09-25)**: cualquier commit posterior la mueve, así que se lee con `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` — es la regla que este plan ya aplica a HEAD en su README⟧. **Commit hecho el 2026-09-24 con autorización explícita del operador y en dos tiempos**: `7f2e9f9` (el helper `tests/support_observador_escrituras.py`, creación de BLOQUE-B, viaja aparte por dependencia técnica: 3 tests de esta fase lo cargan en 8 puntos) y `5817edd` (las **37** rutas propias de FASE-C, +3.774 líneas, con los **7** checks del hook en verde). Quedan **fuera** por decisión del operador: los documentos del plan, el par de índice y `REGISTRY.md` — a nivel de hunk no se separa el cierre de C del trabajo de BLOQUE-B/C sobre esos archivos (164 hunks, **59** nombran FASE-C, 22 otro bloque, 83 sin marca). Consecuencia medida en un árbol extraído de HEAD con `git archive`: la suite de esta fase da **14 failed / 16 passed / 26 errors** (`SueloNoLeible: VENCIDO`, que es el guard de frescura haciendo su trabajo) y pasa a **56 passed** al regenerar el par con `build_lesson_index.py` en ese árbol; el `[6/7] --check` del hook valida contra el árbol de trabajo y **no** afirma coherencia interna del commit. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/` (`informe.json`, `ac10_delta.json`, `coverage.json`, `r26.txt`, `mutation/` con su verde y su rojo, `run_tests.txt`, `regression_calidad.txt`, `cero-red.txt`, `no-piso-pasado_ANTES/DESPUES.txt`, par pre/post de AC16). Métricas por fase: `09-documentacion-post-proyecto.md` §D, no este archivo. **D6 sigue dormida con causa medida** (ver su fila en §Deuda): `acceptance` no se ejercitó y no se simuló |
| 4 · [FASE-D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura medido** (AC19–AC23) | MEDIA: es determinista, pero gobierna lo que todas las sesiones futuras van a leer | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE (AC19–AC23; y AC16/AC17/AC18 en su parte).** Mandato propio del operador, corte **«hasta listo para revisión»**, **sin commit ni push** (instrucción separada como siempre). **Lo que produjo**: `scripts/build_phase_briefing.py` (determinista, cero proveedor, cero red) + **5 packs** en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, uno por fase del plan — COMPLETO **4**, SECCION-NO-RESUELTA **1** (RELEASE: el prompt nombra «los cuatro prompts de fase» en prosa y **no se adivina**), FUENTE-AUSENTE **0** — sobre **34** fuentes declaradas y **23** secciones pedidas, todas resueltas. ⟦**Re-medido el 2026-09-25 por la conciliación final de la orden de calidad**: ese `SECCION-NO-RESUELTA` era **conducta correcta del generador** (AC22: nombra la sección, las rutas intentadas y no adivina), y su causa —la prosa del prompt de RELEASE— se corrigió **en el prompt**, no en el generador. La corrida de hoy da **5 COMPLETO / 0 SECCION-NO-RESUELTA / 37 fuentes** (sus bytes y su porcentaje viven en la salida completa de `evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt`, no en esta fila). **`carga.json` NO se re-escribió** (evidencia cerrada de FASE-D, **S12**): lo que esta fila describía sigue siendo el estado que D certificó⟧. **AC20**: carga total medida en los dos lados con el mismo comando (divisor 4 declarado), con los tres sumandos por fase y la resta **entre cargas totales**; los dos totales y el delta **no se copian en este archivo**: viven en `carga.json` y `carga-pre-post.md` porque este `.md` está dentro del pack que ese `stat` mide (**L-VCF-19**); `instrumentos/comprobar_resta_carga.py` verifica cinco identidades y sale `exit 0`; el workflow canónico entra en los dos lados mientras **D3** no lo rebane, y por eso el ahorro real queda **muy por debajo de un tercio** (concatenar no es ahorrar). **AC21**: frescura por **sha256 de `sources[]`** contra el árbol, cuatro causas sin colapsar (`FUENTE-AUSENTE` / `SHA-DISTINTO` / `FUENTE-ILEGIBLE` / `PACK-AUSENTE`), HEAD publicado como procedencia y **con test que prohíbe que venza**; el pack no está en su propio `sources[]`; y el generador resuelve un plan **también bajo `Archives/`** (demostrado sobre archivados reales: es la llamada del RELEASE tras el `git mv`). **AC22**: a los tres estados del contrato se añadió una cuarta salida medida, `SIN-DECLARACION`, con su `--check` imprimiendo `SIN-FUENTES` en lugar de `OK`. **AC23**: `mutation/` con verde (declara) y rojo (no declara, y el pack se achica en silencio conservando el estado) del símbolo real `GUARD_NO_TRUNCAMIENTO_ACTIVO` — los dos tamaños, en `mutation/resumen.txt` y tampoco se copian aquí (**L-VCF-19**) —, destino por argumento obligatorio y expediente de FASE-A protegido por observador de escrituras + `huellas` (S13). **Tests**: 49 casos en `tests/quality_gates/phase_briefing/` (un estado por test, guard de cero red autouse). **AC17**: `.agents/` con **cero bytes aportados** — la casilla literal «`git status .agents/` vacío» **no era verificable** porque el árbol llegó con 3 rutas sucias ajenas del bloque B, y se afirmó como lo que goberna AC17: observador de escrituras + sha256/tamaño de los 4 archivos, iguales antes y después. **AC16**: delta 0 (quick 11/11 `exit 0`, hook 7→7) con los 49 casos declarados aparte. **Herencia de C aceptada sin reabrirla**: el pack exhibe la parte mecánica medida de C y su `acceptance = NO-EJERCITADO` **como lo que es**; E1–E5 no se renegociaron y **D6 sigue dormida** (ver su fila en §Deuda). **Deuda nueva con dueño y disparador: S16** — la convención `Lee …` que parsea el generador no está escrita en `prompt-fase-template.md`: medido, **0 de 121** prompts archivados la usan. Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/` (`informe.json`, `carga.json`, `carga-pre-post.md`, par `faseD_carga_pre/post.txt`, par `faseD_baseline/quick_pre/post.txt`, `baseline-pre-post.md`, `r26.txt`, `cero-red.txt`, `mutation/`, `instrumentos/`) |
| 5 · [FASE-RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre documental, sync, write-back y archivado en orden R2.5/R2.10 | MEDIA | **✅ CERRADA EN SU PARTE OFFLINE el 2026-09-25 — VERIFICADO sin red.** C0 ejercido (mandato con destinos literales, luego writers): release **4.78.0** `Gobernanza, costura, pertinencia y carga medida`, `release_date`/`date` 2026-09-25; cinco cabeceras por `sync_versions.py`; `DOMAIN_PRIMER.md` regenerado con su writer; `CHANGELOG.md` +90/0; `REGISTRY.md` por `log_phase_completion.py` (cabecera 2026-09-25). **Dos defectos de instrumento declarados con su cura pendiente en `scripts/`**: los writers reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y `readme_version_header` no goberna la fecha legible del README. **Sin autorización siguen**: Q7/D8 (premissa no comprobada), `--upload`/D9, `git mv`, `--fix`/`--update-baseline`, commit, push. Evidencia: `evidence/…/FASE-RELEASE/` (12 archivos) |

## Qué debe heredar cada fase

| Fase | Hereda de | Pieza concreta |
|---|---|---|
| A | — | **Estado medido del árbol, no asumido**: al publicarse la auditoría (`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`) el árbol está **limpio** y el índice viene regenerado y fresco; A re-mide HEAD/status al abrir porque la pareja del índice se comparte con las fases vivas de `REFACTOR-WHATSAPP`. Las cuatro aserciones vencidas A1–A4 medidas y copiadas en el maestro §1 (con **A3 rectificada: el write-back imprime `[15/15]`**), la medición A7 de carga de lectura re-medida (263.973 bytes) y la población A8 que obliga a la regla de clases de AC1 |
| A — **notas de ejecución (2026-09-21)** | lo que A encontró al medir de verdad: HEAD ya no era `2c9d0c1` sino `2deddee` (11 commits de `EVALUACION-JEV` encima) con paridad 0/0 conservada y árbol limpio; **A1–A4 siguen vencidas y A7 no se movió** (263.973 re-medidos); la población A8 se reprodujo exacta (22 + 17 líneas + 2). Dos hallazgos nuevos de la fase, con dueño: **(N1)** el disparador de **D1** era circular — «verificador verde» solo se cumple *después* de corregir `.agents/`, así que se reformuló a «verificador operativo con mutation check + decisión escrita del operador»; **(N2)** la propia prueba de AC1 **añadió 4 pins del denominador 11 en `tests/`** (familia iii de AC2), declarados en `baseline-pre-post.md` en vez de limar la aserción |
| B — **reutilizado, no reinventado** | A | `coverage_basis` con el mismo esqueleto de AC2 (`archivos_escaneados`, `poblacion`, `excluidos_por_directorio`, `limites`, `comando`, `medido_el`) y el tri-estado de AC3, que aquí se llama `provider_status` con sus `motivo_clase`. **Una adicción propia declarada**: el `status` de la puerta es binario en el escaneo (`SIN-HALLAZGOS`/`HALLAZGOS`) porque su tercer y cuarto camino (`AUSENTE`, `LECTOR-FALLIDO`) viven en la resolución del proveedor, no en el conteo — y ahí el tercero se llama `estado_lector`, no se colapsa con `NO-CONFIGURADO`. |
| B — **notas de ejecución (2026-09-21)** | lo que B encontró al medir | HEAD ya no era `e3c4573` sino `74d8ff5` (dos commits de barrido documental de FASE-A encima); `find . -name "*.jsonl"` sigue en **0** (D-V2.1 reproducida por quinta vez, métrica retirada y unidad contable declarada); **0** imports del SDK en el árbol y el SDK **no instalado** en el venv del producto (sí en `tmp_test/venv-jev-sdk`, excluido y publicado); la poblacion que `git grep` ve (678 `.py`) y la que ve el árbol de trabajo (692 en el árbol de trabajo; 690 en el primer escaneo de la fase) **difieren** y las dos se publican |
| C | A y B | La costura de B como única puerta al proveedor; los estados `AUSENTE`/`VENCIDO` de A aplicados al índice de lecciones. **Enmienda prospectiva aceptada el 2026-09-23 (orden de calidad §4.C, solo para CONTEXTO/C):** la pregunta binaria se formula como `choice` de dos opciones con `confidence` **independiente** (no con `noul`: su probabilidad de sí **no** es confianza — ver `decision_client.py`, que prohíbe `confidence` en `noul`); **AC11 elige la ruta (b)** (leer `lecciones_index.json` tras ejecutar C **ella misma** la comprobación de frescura, sin confiar en que otro gate lo regeneró), con `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` como tres causas distinguibles; y las propuestas del proveedor falso **no** entran a §2 del `00-` en automático: exigen **revisión humana explícita con aceptación o rechazo registrado**. Detalle en `05-prompt-inicio-sesion-fase-C.md` y en el maestro §4 |
| D | A, B y C | Los tres estados y `coverage_basis`; el informe de candidatos de C, que el pack exhibe como sección propia; y **el resultado no medido de C, que D acepta sin reabrirlo** (⟦bloque C, 2026-09-24⟧: con D7 inactiva el `acceptance` de AC15 solo puede ser `NO-EJERCITADO`, así que **no** es un disparador de D6 que D pueda encontrar «cumplido»). D hereda medido lo mecánico de C y **no** lo no medido. Reglas de carga total y frescura del pack: contrato §Carga total y frescura del pack |
| RELEASE | A, B, C y D | Los cuatro `coverage.json`/`informe.json`, los pares pre/post de las cuatro fases, el delta de carga **total** medido y el registro de deuda §6 del maestro. **Tres momentos con tres permisos** (contrato §Dos momentos del cierre): el cierre offline es de la fase; la consulta Q7 (D8) y el `--upload` (D9) son remotos y cada uno necesita autorización literal y presupuesto propios; el `git mv` es un tercer momento con autorización expresa. Y el pack se **regenera con la ruta trasladada antes** de verificarlo |

## Conflictos de archivo

| Archivo / ruta | Lo toca | Riesgo y regla |
|---|---|---|
| `.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json` | **Este plan y las fases vivas de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`** | **Conflicto real, ya latente.** `[6/7]` del hook bloquea el commit con el índice vencido contra el árbol, así que **ambos planes lo regeneran**. Regla: regenerar en el mismo commit, nunca `--check` contra un índice ajeno; si aparece un diff que no proviene de tu edición, re-generar y volver a medir, no `git checkout` |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Solo FASE-D, y solo como **generado** (**existe desde el 2026-09-24: 5 packs**) | **Efecto colateral medido por D**: los packs son `.md` dentro del corpus que escanea `build_lesson_index.py`, así que **generarlos vuelve a vencer el par del índice** (A6 sobre un artefacto derivado). La cura no es editar el generado ni el JSON: es el paso 5 del contrato — regenerar el índice sobre el árbol final. Vive dentro del plan a propósito. En `.agents/workflows/` alteraría los contadores de skills (`validate_agent_ecosystem.py`, `sync_data.py`, `doctor.py` usan `glob("*.md")`) y exigiría seguimiento en su `README.md` — y AC17 prohíbe escribir en `.agents/` |
| `scripts/run_all_validations.py` | **Este plan: solo lectura** (AC16). **Pero no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance («su connection en `scripts/run_all_validations.py`») | Corregido el 2026-09-20: la cifra de 11 checks **no la pinea el prompt de FASE-C** de `REFACTOR-WHATSAPP` sino cuatro documentos suyos (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`). **⟦Re-contado el 2026-09-24 por el bloque C de la orden de calidad: esa fila quedó vencida⟧** — su bloque de arranque ya no pinea la cifra, que fue sustituida por el comando que la imprime. Lo que hoy la contiene (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medido el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra) son **registros de fases cerradas**: evidencia histórica que no se reescribe. Consecuencia para AC16: el delta 0 se contrasta contra la corrida propia, no contra esas filas. Y ese tercer plan en vuelo puede cambiar **la etiqueta y la invocación** del write-back `[15/15]` — que es justamente la fuente de verdad de A3 y del fix de AC1. Regla: AC16 (delta 0) obliga a re-medir aquí; **D10** obliga a re-leer la interfaz del write-back antes del `--upload` de este RELEASE |
| `evidence/` (raíz) | **Nadie escribe en las rutas legadas** | Corregido el 2026-09-20: `evidence/FASE-A/` … `evidence/FASE-D/` **ya existen y son de `ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`** (guardan `faseA_baseline_pre.txt`, `faseA_baseline_post.txt`, `faseB_baseline.txt`…), que son exactamente los nombres que produciría este plan si escribiera en la raíz: colisión y procedencia mezclada con un plan **archivado**. Toda la evidencia de este plan va a `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-X/`, como hace `REFACTOR-WHATSAPP` con su subdirectorio. **Se conserva la cita de lectura** a `evidence/FASE-D/measure_iterations.py`, que es el instrumento canónico del executor y vive en esa ruta legado |
| `scripts/git_hooks/pre-commit` | **Nadie** | Sus 7 checks son la otra mitad de AC16 |
| `.agents/**` | **Nadie en escritura** | AC17. Es el objeto auditado y, desde FASE-D, también la fuente que se lee para componer el pack. Copiar una sección al pack **no** es editar la fuente |
| `scripts/build_lesson_index.py` | **Nadie** (solo ejecutar) | FASE-C lo consume como suelo determinista; modificarlo cambiaría la población que publican AC11 y AC15 |
| Los `05-prompt-inicio-sesion-fase-*.md` de **cualquier** plan | FASE-D solo **lectura** | El generador parsea la lista de lectura que cada prompt declara. Reescribir prompts ajenos es justamente lo que D2/D3 postergan hasta el RELEASE del otro plan |
| `00-lecciones-capitalizadas.md`, `06-checklist-implementacion.md`, `09-…`, `10-…`, `README.md`, `dependencias-fases.md` | Todas las fases, incremental | Cierre obligatorio del contrato §Cierres. Escritos por la fase que cierra, no diferidos a RELEASE |
| `scripts/validate_governance_numbers.py` · `decision_client.py` · `triage_lesson_relevance.py` · `build_phase_briefing.py` y sus tests | Una fase cada uno | Propiedad exclusiva; ninguna fase posterior reescribe sobre lo que la anterior serializó |

## Prerrequisitos y límites visibles

- **Ningún prerrequisito de autorización central, y ninguna credencial necesaria.** Por decisión del
  operador del 2026-09-20 **no entra Jev en este plan**: FASE-B prueba la costura contra proveedores
  **falsos** y AC9 certifica que añadir uno real es un cambio de un archivo. Activar el proveedor
  habilitado es la deuda **D7**, con su disparador. Consecuencia aceptada y escrita: ningún AC de
  este plan mide calidad de decisiones de un modelo real; miden forma, aislamiento y no-regresión.
- **La capa tibia del Paso 0 no se consultó al concebir; sí en la auditoría del 2026-09-20.** QMind
  `iah-cli-lecciones` no estaba accesible en la sesión de concepción (consulta Q7, declarada NO
  EJECUTADA en `00-lecciones-capitalizadas.md` §1 y §4) y se aplicó el fallback: memoria de proyecto +
  índice generado. En la auditoría el CLI estuvo disponible y la consulta se corrió cuatro veces; sus
  lecciones ya están en §2 (L-V2.1, L-V2.2, D-V2.1) y sus efectos en AC4, AC11 y el corte de
  presupuesto. **Lo que queda es D8 como re-correr, no como descubrir.** Límite que sigue en pie: el
  triaje de FASE-C calibra contra 320 IDs definidos y 50 citados sin definición (re-medido al
  regenerar el índice por la entrada de este plan, maestro §1 A6); si el notebook aporta lecciones
  fuera del repo, ese conjunto está incompleto y así se declara en el denominador de AC15.
- **FASE-D no reduce por sí sola la lectura de las fases del otro plan.** Sus nueve prompts siguen
  citando el workflow canónico; el recorte real de esa fuente es la deuda D3. Lo que AC20 puede
  cerrar es el delta sobre las fases de **este** plan, y un delta cero o negativo es resultado
  válido si se explica.
- **Este plan convive con otros dos en vuelo.** No comparte ACs, no comparte contador de corrida, no
  consume el intento `v4complete: 0/1` de `REFACTOR-WHATSAPP`. Pero las superficies compartidas **no
  son una, son tres** (medidas el 2026-09-20): la pareja del índice de lecciones con
  `REFACTOR-WHATSAPP`; la cifra de 11 checks que ese plan pinea en cuatro de sus documentos (hoy
  **cinco, todos ellos registros de fases cerradas** tras el arranque de su `README.md` pasar a mandar
  el comando — medido el 2026-09-24, §Conflictos de archivo); y
  `scripts/run_all_validations.py` + `scripts/validate_qmind_writeback.py`, que
  `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara **dentro de su alcance**. Este plan no los escribe;
  los lee como fuente de verdad, y de ahí salen AC16 (delta 0) y **D10**.
- **No hay FASE-VERIFY** y por tanto ningún AC puede certificarse contra output E2E. Techo
  alcanzable: `VERIFICADO OFFLINE` con mutation check, o `NO-EJERCITADO`.

## Deuda registrada (dueño y disparador, no silencio)

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o eliminar las aserciones A1–A4 en `.agents/` | Este plan, FASE-RELEASE, con instrucción literal del operador; ejecución adelantada por mandato de B | **Estado vigente: matriz §13 de la fuente única, no certificado aquí.** Antecedente: **Disparador reformulado el 2026-09-21 (FASE-A):** era circular («verificador verde» no puede darse antes de la corrección que el verificador pide); pasa a *verificador operativo con su mutation check en disco* — cumplido el 2026-09-21 — **y** decisión escrita del operador sobre la forma de la corrección |
| D2 | Promover `validate_governance_numbers.py` a check del `--quick` con renumeración (11 → 12) | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases que pineen «11 checks». **⟦Aclaración del bloque C, 2026-09-24: las enmiendas de ese bloque sobre `REFACTOR-WHATSAPP` NO satisfacen este disparador⟧** — convirtieron en «el valor lo imprime la corrida» las **instrucciones prospectivas**, y dejaron intactos los registros de sus fases cerradas (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G), que son evidencia histórica. D2 sigue necesitando su propia sesión y su propia decisión |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura de A7: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B del plan en vuelo; los 254.010 de la concepción vencieron ese mismo día) | Plan propio, posterior | Mismo disparador para el rebanado completo; **D3 parcial**, no cerrada. La simplificación encargada a B no se difiere. **No** es FASE-D: el pack unifica lecturas declaradas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** (`validate_plan_semantics.py`): prompts de fase contra estado real del plan, con falsos positivos medidos contra los archivados | Plan propio posterior; **entra en este mismo directorio** si el disparador se cumple mientras está vigente | **Condicionado al resultado de FASE-C**: que el triaje entregue candidatos que el Paso 0 no ancló, con su aceptabilidad medida publicada en el informe. Si FASE-C sale inaceptable, **no se activa**: no se apila un segundo consumidor sobre una base que no funcionó. ⟦Precisión del bloque C, 2026-09-24⟧: mientras **D7** esté inactiva, la rama «salió aceptable» **no es alcanzable** — con proveedor falso `acceptance` solo puede publicarse `NO-EJERCITADO` (contrato **E4**), así que D6 queda **dormida con causa**, no «pendiente de que alguien consulte el número». Se re-evalúa al activar D7, no antes. **⟦Medido al cerrar FASE-C el 2026-09-24: la condición se cumplió literalmente — `coverage.json` publica `acceptance = NO-EJERCITADO` con su motivo y `valor: null`, sin cifra simulada (contrato E4). D6 queda DORMIDA y este plan no abre el lint semántico sobre una base que no juzgó nada; su re-evaluación sigue atada a D7⟧** **⟦Re-declarada al cerrar FASE-D el 2026-09-24 — no re-abierta ni re-asignada por interpretación: D leyó el `coverage.json` de C y encontró exactamente lo mismo que publicó C (`NO-EJERCITADO`, `valor: null`), así que la rama «el triaje salió aceptable» sigue sin ser alcanzable mientras D7 esté inactiva. D no reabrió C, no renegoció E1–E5 y no presentó la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo único que activaría D6 es un proveedor real mediante (D7), y ese no es el estado de este plan⟧** |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev) como segundo proveedor detrás de `decision_client.py`; correr la comparación de proveedores y restituir «elegir midiendo» como AC | Plan propio posterior | Acceso existente desde 2026-09-20, pospuesto por decisión del operador. El consumidor natural es D6, el único trabajo genuinamente semántico del lote |
| D8 | Re-ejecutar la consulta Q7 de QMind. **Premisa vencida: el 2026-09-20 el CLI sí estaba disponible y la consulta se corrió en la auditoría de la concepción** (cuatro `retrieve`, resultados capitalizados como L-V2.1, L-V2.2 y D-V2.1). **Y su forma publicada es incorrecta**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; hay que pasar el ID `01a04d98-b7bd-778c-8441-26fdc7e35f45` | Este plan, sesión previa a FASE-RELEASE (re-corrida, no primera vez) | Que el notebook haya cambiado desde la auditoría, o que se quiera verificar el comando corregido con las citas que ya devolvió |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice después |
| **D10** | **Re-leer la interfaz del write-back antes de correr el cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al RELEASE de `REFACTOR-WHATSAPP`) piensa añadir `--title`/`--file` a `validate_qmind_writeback.py`, verificar contenido en vez de título, quitar la degradación a PASS y tocar su conexión en `run_all_validations.py` | Este plan, FASE-RELEASE | **CUMPLIDA en su lectura el 2026-09-25** (FASE-RELEASE): `validate_qmind_writeback.py --help` contra el árbol vigente → `--nb`, `--strict`, `--upload`; **sin** `--title` ni `--file`, decide por título y degrada a `exit 0` sin CLI. La firma **no** cambió (el mini-plan no se ejecutó), así que `04-contrato-ejecucion.md` **no** se re-escribió; lectura con su evidencia en `evidence/…/FASE-RELEASE/02-tarea1-firma-writer.txt`. Queda vigente la advertencia para quien sí corra la subida: verificar por contenido, no por título |

### Ejecución del bloque B de la orden de calidad (2026-09-23) — coordinación, no nuevo propietario

**Estado vigente: matriz §13 de la fuente única citada al inicio.** Las declaraciones de resolución
y suficiencia de pruebas que siguen son antecedentes retirados de §1–§12; no aceptación actual.

El operador autorizó el bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y, dentro de él,
**adelantar D1 y la parte de D3 que B necesita** respecto de sus disparadores originales. Se registra
aquí sin crear un propietario paralelo: los dueños son los que fija el maestro §6 (D1 = «Este plan,
FASE-RELEASE»; D2/D3 = «Plan propio, posterior»); B ejecutó contenido bajo mandato, no reclamó la
propiedad. **Ampliación de alcance registrada:** el mandato B listaba el executor y
`prompt-fase-template.md`, pero retirar A4 (D1) exigía tocar su fuente,
`.agents/workflows/templates/lecciones-capitalizadas-template.md`; el operador autorizó expresamente
esa ampliación el 2026-09-23 y confirmó mantener los campos `version:` de frontmatter del executor
(v2.25.0) y de la plantilla (v1.6.0) como metadato documental, no bump de release (`VERSION.yaml`
intacto).

- **D1 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado** del
  2026-09-23: el dictamen decía «RESUELTA y revalidada». Las cuatro aserciones A1–A4 se corrigieron/retiraron **desde su
  fuente** (`.agents/`): el árbol vigente ya sale `SIN-HALLAZGOS` (`validate_governance_numbers.py`
  exit 0, vuelto a medir en la remediación). La decisión de forma fue retirar el denominador volátil
  en lugar de copiar la cifra vigente (la opción que el propio plan ya recomendaba: «dejar que el
  verificador la imprima es la que no se desfasa»). La detección no se debilitó: las cuatro
  aserciones quedaron reancladas a un **contraejemplo congelado** en
  `tests/quality_gates/governance_numbers/fixtures/` con sus mutantes, más una regresión del árbol
  honesto. Sin renumerar checks (**D2** sigue fuera).
- **S13 — estado vigente en la matriz §13; no certificada aquí.** **Antecedente retirado:** el
  dictamen del 2026-09-23 decía «RESUELTA, con la parte que faltaba hecha en la remediación del mismo día». El arnés
  `test_governance_numbers_mutation_por_asercion.py` ya no escribe en `evidence/…/FASE-A/mutation/`.
  El primer retiro **movió el destino pero seguía midiendo estado final** (instantáneas
  antes/después), y su control negativo definía una función de huellas propia dentro del test y
  provocaba el rojo con `os.utime`: no observaba escrituras. Ahora se observan las **operaciones de
  escritura** del escritor real con `tests/support_observador_escrituras.py` (alcance declarado:
  proceso de pytest, no procesos hijos), con ancla positiva, y los tres controles negativos del
  mandato (a escritor redirigido a destino protegido, b bytes idénticos, c mtime restaurado) sobre un
  **expediente desechable**. Se conserva la comparación de contenido y metadatos del expediente
  protegido. Cierre de la deuda que el bloque A dejó viva.
- **Controles negativos sobre el instrumento real (remediación, mismo día).** Ningún rojo por causa se
  produce ya reimplementando el defecto dentro del test:
  `test_control_negativo_el_escritor_permisivo_vuelve_a_afirmar_de_mas` corre el **escritor commiteado
  en `da382b1`** (leído con `git show`, materializado en un temporal —sin `checkout` ni `stash`—) y su
  `- [x] Tests passing` rompe la misma exigencia;
  `test_control_negativo_el_instrumento_versionado_re_llamaba_y_el_de_hoy_no` mide los **cálculos de
  verificador** en ese módulo versionado contra el del árbol, con la misma inyección y la misma conta
  (cifras PRE/POST y procedencia: resumen del bloque B, §4.1 y §4.3). Con eso
  el PRE queda anclado a una revisión, no a «el árbol que había cuando corri». ⟦Nombre rectificado el
  2026-09-23: la fila anterior citaba `…_recalcula_y_el_actual_no`, nombre que no existe en disco.⟧
- **D3 — ADELANTADA EN PARTE, NO CERRADA.** Se ejecutó lo que B requería: principio de
  proporcionalidad/reuso, retiro de cuotas «mínimo 3 lecciones», y **cortes utilizables sin commit**
  (los **cinco** terminan en espera de autorización; el commit es una acción posterior y separada,
  opcional, no el quinto corte). La remediación añadió lo que el
  primer pase dejó contradicho: la resolución de «RELEASE no registra» vs «registrar cada fase», y la
  sustitución de métricas copiadas en README/`09`/`10` por referencia a su fuente. Nada de eso se
  difiere a D2, al bloque C ni al piloto. El rebanado completo del workflow canónico (bajar la carga
  de lectura por fase) **sigue diferido** a su disparador (sesión previa a FASE-RELEASE de
  `REFACTOR-WHATSAPP`) y conserva su dueño del maestro §6: **«Plan propio, posterior»**, no se
  reasigna. No se declara D3 cumplida ni se midió reducción de carga (no hay ahorro D3 que afirmar).
- **Pendientes que B dejó y cómo están ahora.** ⟦Re-lectura el 2026-09-24 por el bloque C⟧ La fila
  original decía «el árbol de B está **sin commitear** (mandato: cero commit/push); el bloque C (enmiendas
  prospectivas a los cuatro planes) y el piloto FASE-C siguen pendientes de su autorización». De esas tres
  cosas, **dos cambiaron y una queda igual**:
  - **sin commitear**: sigue vigente y **no** lo mueve este bloque. El mandato del bloque C también
    prohíbe commit y push; su árbol —el de B y el de estas enmiendas— se entrega sin commitear y el
    commit es decisión separada del operador.
  - **bloque C**: **autorizado el 2026-09-24**, y ejecutado como enmiendas documentales sobre los cuatro
    planes (§Bloque C abajo). No es el piloto.
  - **piloto FASE-C**: **sigue sin autorización** y no se ejecutó. Su contrato está conciliado y su
    prompt listo; eso habilita pedir el mandato, no ejecutarlo.
  **Frontera de red:** la corrida `--check` **completa** que hizo la primera sesión de B
  incluye el check QMind y en esta máquina el CLI `qmind` está instalado, así que «cero red» **no puede
  afirmarse** y queda **NO DETERMINADO** (no se preservó su stdout; no se repite la llamada). El bloque C
  **tampoco** determinó esa fila: no corrió el `--check` completo ni hizo llamada alguna. Las citas
  «mandato §1…§8» tampoco apuntaban a nada versionado: el mandato llegó como adjunto del operador y se
  archivó como copia byte a byte en
  `evidence/…/BLOQUE-B-REMEDIACION-2026-09-23/99-mandato-de-remediacion-B-2026-09-23.txt`
  (sha256 `5a12e90f04a1ab3e4536bbe451c62d6dab1deac268706fbef02b1e12a9c31394`, procedencia y límites en
  `99-procedencia-del-mandato.md`).
  Fuente única de resultados de B:
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md`
  (el resumen de la primera sesión, `…/BLOQUE-B-ORDEN-CALIDAD-2026-09-23/00-resumen-bloque-B.md`,
  queda como antecedente con su cierre retirado).

## Bloque C de la orden de calidad (2026-09-24) — qué se concilió en este plan

Autorización: **solo enmiendas prospectivas sobre los documentos de los cuatro planes**, más el par del
índice de lecciones regenerado por su generador y la evidencia del bloque. Prohibido: código, tests,
`VERSION.yaml`, `AGENTS.md`, `.cursorrules`, `.agents/**`, hooks, configuración, `sync_versions.py`,
`build_lesson_index.py`, REGISTRY, red, QMind, pipeline, archivado, commit y push. Evidencia:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/BLOQUE-C-ENMIENDAS-2026-09-24/`.

| Fila §4.C | Qué quedó resuelto | Dónde |
|---|---|---|
| `CONTEXTO/C` | **Nada que renegociar.** E1–E5 se conservan y su forma se reconfirmó contra `scripts/decision_client.py` (la validación de `RespuestaEleccion` exige `confidence`; `RespuestaNoul` la fija en `None` y la puerta rechaza que un `noul` la reporte). **AC15 semántico `NO-EJERCITADO` y D6 dormida** quedan admitidos explícitamente en la fila D6 de arriba | contrato §Enmiendas + este archivo |
| `CONTEXTO/D` | **Carga total** con tres sumandos (`workflow_obligatorio`, `coste_de_generacion`, `pack_consumido`) y resta entre totales: concatenar no es ahorrar. **Frescura por sha de las fuentes relevantes; HEAD es procedencia, no llave de caducidad** (corta la invalidación circular por el commit del generado). **Regeneración del pack tras el traslado antes de verificarlo** y AC19 obliga a resolver rutas archivadas. **D acepta el resultado no medido de C** | contrato §Carga total y frescura del pack, §Cierres item 8, maestro AC19/AC20/AC21, prompt FASE-D |
| `CONTEXTO/RELEASE` | **Cuatro permisos, no tres** ⟦rectificado 2026-09-25; la etiqueta «tres momentos» sigue siendo el título-history del bloque por sus cinco referencias vivas⟧: **C0 destinos escribibles** (offline = sin red, **no** permiso de escritura: `sync_versions.py` sin `--check` puede reescribir `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md` según `sync_config.yaml`; `VERSION.yaml` es entrada y REGISTRY + `.last_doc_phase.json` salen del escritor del registro) · **cierre offline verificado** · **remoto** (D8 y D9, cada uno con autorización literal y presupuesto) · **traslado**. Se separa el mandato de la fase de esos permisos, con `PENDIENTE-AUTORIZACION` en vez de omisión. **Leer el estado ≠ reparar**: correr `validate_governance_numbers.py` es verificación y la reparación de `.agents/` no vuelve a hacerse aquí. **Sin writers automáticos**: `--fix` y `--update-baseline` salieron de la secuencia; los checks no escriben y ningún baseline se actualiza para absorber errores. **El `--check` posterior al traslado se apoya en una regeneración prevista**, y un rojo de un derivado no autoriza editar código. **D2 no se da por satisfecho** por las enmiendas de `REFACTOR-WHATSAPP` | contrato §Dos momentos del cierre y §Orden del cierre, prompt FASE-RELEASE |

**Qué este bloque NO tocó y por qué.** No ejecutó el piloto FASE-C ni ninguna fase; no activó D6 ni D7;
no movió `VERSION.yaml` ni las versiones documentales de `04-`/`06-`; no escribió en `AGENTS.md`,
`.agents/**`, hooks, `REGISTRY.md` ni su tracker auxiliar; no regeneró DOMAIN_PRIMER; no tocó la
evidencia histórica de FASE-A/B ni los prompts de fases cerradas. La **incompatibilidad declarada** que
queda fuera de su alcance: `AGENTS.md` (§Vinculo con la Documentación) sigue condensando DOMAIN_PRIMER
en «se regenera en FASE-RELEASE» y `docs/CONTRIBUTING.md` titula «Regenerar» a su Paso 5b mientras la
fila de su tabla dice «Se VERIFICA»; son documentos centrales que la fila `WHATSAPP` resuelve **para el
plan** (regenerar al cerrar cada fase, verificar en RELEASE), pero alinearlos a ellos exige instrucción
expresa aparte y no se hizo por arrastre.

## Rutas ajenas en el árbol al commitear FASE-B (medido, no supuesto)

Al cerrar FASE-B (2026-09-21) había **tres rutas ajenas** en el árbol. Al abrir su tramo de commit
quedaba **una**: `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, que el
commit de esta fase **deja fuera** y sobre la que no se hace `git checkout` (es trabajo en curso de otra
sesión, no basura que limpiar; precedente: FASE-A excluyó a propósito sus dos rutas ajenas).

Las otras dos —`ROADMAP.md` y `.opencode/context/Refuerzo.md`— se las llevó la otra sesión en `eecf246`,
que ese día era el HEAD del repo y estaba **sin empujar** (`git rev-list --left-right --count
origin/master...HEAD` → `0/1`). Consecuencia declarada: **el commit de FASE-B se apoyaba sobre un commit
ajeno todavía no publicado** — y el push del mismo 2026-09-22 lo publicó con los cuatro de esta fase,
como queda escrito debajo, y el HEAD sobre el que esta fase midió su par pre/post (`74d8ff5`) ya no es
el HEAD. Las restas no se mueven —los cuatro archivos gobernados por AC16/AC17 no están en ninguno de los
dos commits y su `git diff --numstat` sigue vacío—, pero la premisa «el árbol de partida es solo mío»
queda refutada y así queda escrita (medición A6 del maestro, cumplida sobre esta propia fase). Detalle con
comandos y mtimes en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/baseline-pre-post.md`
§Rutas ajenas.

**Cerrado el 2026-09-22.** El commit de FASE-B está hecho — **`647f436`** (46 archivos, +4.412/−97), con
instrucción literal del operador y con el par del índice de lecciones dentro, así que `[6/7]` del hook no
lo cortó y los **7** checks pasaron. Dos consecuencias re-medidas para quien abra FASE-C: la paridad con
`origin/master` era **`0/2`** al cerrarlo, **`0/3`** tras su propio barrido de citas (`612efd0`) y
**`0/5`** tras el micro-barrido (`cf64faf`) — cada commit documental suma uno, así que la cifra se re-mide
y no se copia—; y **el push se hizo el 2026-09-22 con instrucción literal del operador**, que publicó
`74d8ff5..b764e8d` —los cinco commits, incluido el ajeno `eecf246` que era su ancestro obligado— y dejó
paridad **`0/0`** medida tras `git fetch`; y el propio commit movió el denominador que la fase había publicado — **678 → 691** `.py`
rastreados —, con lo que la resta de AC6 quedó rectificada con su nota y su residuo de un archivo
(`.venv-wsl/bin/activate_this.py`, exclusión no declarada) registrado como **S11** con su lección
**L-VCF-11**. Y el re-muestreo que hizo falta para medir esa rectificación **pisó la evidencia cerrada de
FASE-A**: `validate_governance_numbers.py --report` tiene su destino hardcodeado en
`evidence/…/FASE-A/informe.json`, así que el comando canónico del plan re-escribe el registro de otra
fase en cada corrida. Se revirtió (`git checkout --` sobre ese archivo) y se re-muestreó con destino
explícito, que da el mismo `HALLAZGOS` (A1–A4, 24 instancias, `exit 1`) sin tocarlo → **S12** /
**L-VCF-12**, con su guarda publicada en el README para quien abra FASE-C.

## Conciliación con la remediación del bloque A — aceptación de S11 y S12 (2026-09-23)

**Qué se acepta y de dónde viene (procedencia, no atribución a esta sesión).** Las dos deudas
nacidas del commit de FASE-B fueron corregidas **fuera de este plan**, por las cuatro sesiones
autorizadas del **bloque A** de `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, y el
código corregido entró al repo en **`fdd397f`** sobre la superficie
`scripts/decision_client.py`, `scripts/validate_governance_numbers.py`,
`tests/quality_gates/decision_client/` y `tests/quality_gates/governance_numbers/`. El resumen de esa
remediación (`evidence/…/REMEDIACION-BLOQUE-A-2026-09-22/00-resumen-bloque-A.md` §4) dice de sí misma,
y se cita literal por ser el límite que esta fila respeta: **«lo aplicado es CORRECCIÓN TÉCNICA, no
cierre contractual»**, porque el traslado de S11/S12 a ese bloque exigía la enmienda registrada **en
este plan**, que era el pendiente. **Ese pendiente es lo que esta sección cierra**: el plan propietario
CONTEXTO acepta la remediación y registra el traslado. El mérito técnico es de esas sesiones y de `fdd397f`;
esta sesión **no** editó código ni tests.

**Alcance de lo aceptado** — solo S11 y S12, y solo en lo que el bloque A hizo:

| Deuda | Cura aceptada (en `fdd397f`) | Re-validación offline medida el 2026-09-23 |
|---|---|---|
| **S11** — `.venv-wsl` faltaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION` y las exclusiones se solapan | La exclusión entra en la lista **y su conteo se publica**; dos pruebas de población sobre árbol plantado; el escaneo se comparte entre aserciones del mismo árbol | `python scripts/decision_client.py --scan-imports` → `SIN-HALLAZGOS`, **0** imports prohibidos, `exit 0`; población escaneada **696** vs `git ls-files '*.py'` = **696** → **residuo 0** (la resta que en B cerró en 692−691 ya no existe); `.venv-wsl` figura en `excluidos_por_directorio` con **582** archivos |
| **S12** — `--report` sin destino re-escribía `evidence/…/FASE-A/informe.json` | El destino por defecto desaparece de los dos verificadores: `--report` a secas **imprime y no escribe**; el aviso va a stderr y el stdout queda JSON puro; **seis** tests nuevos en `tests/quality_gates/governance_numbers/` ⟦rectificado el 2026-09-23: esta fila decía «cinco»; corridos por nombre dan **6 funciones / 6 casos** en `test_governance_numbers_s12_report_no_escribe.py`, y el directorio completo **35 funciones / 40 casos**, `40 passed` con `EXIT=0`⟧ | `python scripts/validate_governance_numbers.py --report` sin destino → **`exit 1`** con `status: HALLAZGOS` y `assertion_ids = [A1,A2,A3,A4]`; `sha256` de `evidence/…/FASE-A/informe.json` **idéntico** antes y después de la corrida; `git status --porcelain evidence/` **vacío** |

**Los tres momentos van separados, y así quedan:** (1) **cierre original de FASE-B** — `647f436`
(2026-09-22), que cerró AC6–AC9 y **produjo** S11/S12 al mover el denominador y al re-muestrear;
(2) **corrección posterior** — `fdd397f` (2026-09-22), bloque A de la orden, técnica y probada por su
dueño; (3) **aceptación** — esta sección, 2026-09-23, que además re-mide offline. Ninguna de las tres
se atribuye a las otras dos.

**Qué NO cerró aquella aceptación (antecedente fechado).** El rojo contractual A1–A4 seguía vivo:
`validate_governance_numbers.py` salía `exit 1` porque aquella sesión no editaba `.agents/` (AC17,
D1/S1); la remediación del bloque A no lo tocó. Después B recibió autorización de corrección, pero
su estado vigente remite a la **matriz §13** de la fuente única, no a ese rojo ni a verdes retirados.
Y siguen abiertas, con dueño, **sin** convertirse en bloqueantes artificiales de una
FASE-C offline: **S10** (dónde vivirá el `import` del SDK cuando D7 se active), **D7** (activar el
proveedor) y **D6** (lint semántico, **dormida** porque su disparador es el `acceptance` de AC15).

**AC9 queda declarado con su alcance real** (no solo su cifra): certifica **extensión local** —
registrar un proveedor **falso** del repo a través de la costura, sin red ni credenciales, medido por
sha256 (`files_changed_to_add_provider = 1`, re-medido el 2026-09-23 con `--costura`, `exit 0`). **No**
certifica el coste total de integrar un **SDK real** en un archivo: dependencias y autenticación no se
midieron ni pueden medirse bajo la regla de cero red. El propio `--costura` ya imprime esa acotación
en su clave `alcance_de_ac9`, y la ubicación futura de ese SDK es **S10**/D7, coordinada con el plan
hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`.

**Instrumentos reutilizados, no nuevos.** Esta conciliación no añadió instrumentación: corrieron los
existentes de B (`--scan-imports`, `--costura`, `--provider-status`) y de A (`--report`), más la
selección `tests/quality_gates/decision_client` (**87 passed**, `exit 0`). **No se repitió la suite
completa por rutina**: su estado vigente es el que publicó la sesión 4 del bloque A, y lo que aquí se
ejecutó es la selección pertinente, distinguible de los resultados históricos de B. Crudos, comandos y
códigos en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/`.

### S16 — la convención que parsea el generador no está escrita en ninguna fuente (nueva, 2026-09-24)

**Hecho medido al cerrar FASE-D**: `build_phase_briefing.py` extrae la lista de lectura del prompt
desde la cadena `Lee …` dentro de un bloque fenced de «Prompt de ejecución». Sobre el corpus
completo: **121** prompts de fase bajo `.opencode/plans/Archives/` y **0** la usan; **5** prompts la
usan en todo el repo y son los cinco de este plan. Consecuencia directa y probada: el pack de un
plan archivado sale `SIN-DECLARACION` y su `--check` imprime `SIN-FUENTES` — el corte del
generador, no su defecto.

- **Dueño**: `.agents/workflows/templates/prompt-fase-template.md`, sección 8 (Prompt de Ejecución),
  y por arrastre los prompts de los planes vivos. **No es de FASE-D**: escribir en `.agents/` es
  AC17 y esa superficie es D1/con instrucción literal del operador.
- **Disparador**: la próxima vez que un mandato autorice tocar el template (precedente: el bloque B
  de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` autorizó `lecciones-capitalizadas-template.md` para
  retirar A4). Ahí se añade la forma canónica de la lista de lectura, y FASE-RELEASE de este plan
  **no** la reescribe.
- **Por qué se registra y no se calla**: sin esta fila, un lector de 2026-12 verá packs vacíos para
  los planes archivados y concluirá que el generador está roto. L-R.4: una regla de proceso sin
  verificador es publicable solo si la regla lo declara — y aquí lo declara el propio pack.
- **Alternativa descartada**: hacer que el generador adivine la lectura por heurística de rutas
  (`*.md` citados en el prompt). Convertiría `SECCION-NO-RESUELTA` en una invención silenciosa, que
  es la familia de defecto que L-PF6/L-PF10 trajeron a este plan.

### S17 — los writers de texto reescriben en CRLF archivos que git almacena en LF (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: la escritura final de `SyncEngine.sync_rule` en
`scripts/sync_versions.py` y la de `run_regenerate_domain_primer` en `scripts/doctor.py` cierran con
`write_text(..., encoding="utf-8")` **sin** `newline="\n"`. En Windows eso re-escribe en CRLF un
archivo que git almacena en `i/lf`. Medido en la corrida: **6** archivos quedaron
`[FAIL] Line endings` tras el sync y la regeneración (lo cortó el detector de finales de línea que el
bloque B de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` añadió a `validate_document_integration.py`), y
el expediente `FASE-RELEASE/12-normalizacion-lf.txt` registra la normalización byte a byte con
`git diff -U0` comprobando que el delta seguía siendo solo tokens de versión/fecha/codename. El
antecedente de la cura correcta vive en el propio repo: `scripts/log_phase_completion.py` pasa
`newline="\n"` y lo documenta junto a la escritura.

- **Dueño**: `scripts/sync_versions.py` y `scripts/doctor.py`. Es edición de `scripts/`, **no** de este
  plan ni de la orden: FASE-RELEASE tiene prohibido modificar código, y ese fue el motivo exacto por el
  que aquí se declaró el defecto en lugar de curarlo.
- **Disparador**: el próximo mandato que autorice literalmente editar esos dos writers. La cura es el
  parámetro en la escritura, no la normalización posterior del árbol.
- **Remedio vigente (provisional y declarado)**: normalizar por bytes al cerrar. No es la cura — deja el
  defecto en el escritor, que es la regla que este plan ya aplica a los datos: *un dato con escritor se
  arregla en el escritor o con un verificador, no con un tercero que lo reescriba a mano*.
- **Alternativa descartada**: fixedear los finales de línea en cada llamada desde los dos cierres del
  RELEASE sin tocar el writer (sería el mismo remiendo en dos sitios más) y reconfigurar `text`/`eol`
  de git: eso cambiaría el árbol de trabajo de archivos ajenos a este plan para tapar un defecto local.

**⟦CURADA el 2026-09-25 en una sesión aparte, con mandato de código del operador⟧.** El disparador de
arriba se cumplió ese mismo día: se autorizó editar `scripts/sync_versions.py` y `scripts/doctor.py` más
sus tests. Estado de la cura:

- **Tres escrituras**, no dos. Al curar apareció una tercera de la misma familia en el mismo archivo:
  `run_status` escribe `.agent/SYSTEM_STATUS.md`, y estaba dejando el árbol en `w/crlf` contra su propio
  `i/lf` (medido con `git ls-files --eol` antes de tocar nada). Las tres llevan ahora `newline="\n"`:
  `SyncEngine.sync_rule`, `run_regenerate_domain_primer` y `run_status`.
- **Prueba por comportamiento, no por parámetro**: `tests/test_sync_writers_lf_y_fecha_readme.py` corre
  los **escritores reales** sobre repositorios temporales y afirma sobre los bytes emitidos. Su control
  negativo ejecuta la versión **commiteada** de cada script (`git show HEAD:…`, sin `checkout` ni
  `stash`): el viejo escribe CRLF y el nuevo LF en el mismo entorno, así que la diferencia es
  atribuible al parámetro y no a la máquina.
- **Límite declarado**: la traducción `\n` → `\r\n` es propiedad del SO. La prueba **mide** si este SO
  traduce (`_traduce_a_crlf()`) y, donde no traduzca, las tres comprobaciones de bytes se saltan con
  motivo en vez de dar un verde que no observó nada. Las de S18 son portables.
- Con la cura hecha, el `--check` del sync volvió a `All files in sync` y la normalización manual por
  bytes del cierre de RELEASE (`12-normalizacion-lf.txt`) queda como antecedente: el próximo cierre no
  la necesita. No se re-escribió ese expediente cerrado (**S12**).

### S18 — `readme_version_header` no goberna la fecha legible de `README.md` (nueva, 2026-09-25)

**Hecho medido al cerrar FASE-RELEASE**: después del sync de cinco cabeceras, la línea de estado de
`README.md` seguía diciendo `Actualizado 11 Septiembre 2026` con `release_date: 2026-09-25` ya en la
fuente única. La regla `readme_version_header` de `scripts/sync_config.yaml` tiene patrón para el token
de versión pero no para esa etiqueta de fecha; la regla hermana `guia_tecnica_header` sí la goberna, y
`docs/GUIA_TECNICA.md` movió su fecha en la misma corrida.

- **Corte de cobertura declarado, no deducido**: el quick `[3/11] Version Sync` dio **PASS** con el
  README desfasado, así que la comprobación vigente no mira esa etiqueta. El rojo solo lo ve un lector
  humano — que es lo que lo encontró — y por eso se registra con deuda en vez de con un verde.
- **Dueño**: `scripts/sync_config.yaml` y el lector de esa regla en `scripts/sync_versions.py`.
- **Disparador**: el próximo mandato que autorice editar el config de sync o sus patrones de header; o
  la próxima release, si se quiere que la fecha del README salga por su escritor.
- **Alternativa descartada**: editar esa línea del README a mano. Crearía un segundo escritor sobre un
  dato que ya tiene uno — la familia exacta de la que `scripts/sync_config.yaml` retiró la regla
  `registry_last_update` el 2026-09-23.

**⟦CURADA el 2026-09-25, en la misma sesión que S17 y con el mismo mandato de código⟧.**

- El patrón llega ahora hasta la fecha (`… | Actualizado[^\n|]*`) y el template emite `{date_text}`, la
  forma larga que `_interpolate` ya sabía producir: «25 Septiembre 2026». **No** entra un ISO en la
  cabecera — hay prueba que lo prohíbe, porque cambiar el formato que el documento mostraba no era lo
  que pedía la deuda. `[^\n|]*` no cruza la línea ni el separador, así que no alcanza otras menciones
  de «Actualizado» (hay una línea de contexto con esa palabra como señuelo en la prueba).
- El corte de cobertura quedó cerrado en el árbol real, y se midió antes de celebrarlo: con la regla
  vigente, el `--check` del sync pasó de `IN_SYNC` a **`FAIL: README.md (readme_version_header) - needs
  update`** sobre el README que dejó la release. Ese rojo es la detección funcionando, no una regresión.
- Escribir `README.md` es destino central y no estaba en el mandato de código: se pidió y se autorizó
  aparte (`python scripts/sync_versions.py --rule readme_version_header`, 2026-09-25). Delta real: la
  **línea 5** (fecha). `git diff --numstat` contra `HEAD` marca 2/2 porque la cabecera de versión ya
  la movió la release; la separación se comprobó con `git diff -U0` y con huellas antes/después en
  `evidence/…/CIERRE-ORDEN-2026-09-25/07-guard-idempotencia-sync.txt`, donde una segunda corrida del
  mismo comando no mueve **ninguna** de las diez rutas vigiladas.
- El espejo de prueba allana **las dos** líneas que goberna la regla: con solo la cabecera allanada, el
  `FAIL` llegaba por la segunda sustitución y no por la fecha. Medido, y por eso está escrito.
