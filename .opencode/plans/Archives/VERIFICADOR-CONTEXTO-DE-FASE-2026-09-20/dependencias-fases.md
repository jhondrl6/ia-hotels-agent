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
| 4 · [FASE-D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura medido** (AC19–AC23) | MEDIA: es determinista, pero gobierna lo que todas las sesiones futuras van a leer | **✅ CERRADA 2026-09-24 — VERIFICADO OFFLINE (AC19–AC23; y AC16/AC17/AC18 en su parte).** Mandato propio del operador, corte **«hasta listo para revisión»**, **sin commit ni push** (instrucción separada como siempre). **Lo que produjo**: `scripts/build_phase_briefing.py` (determinista, cero proveedor, cero red) + **5 packs** en `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`, uno por fase del plan — COMPLETO **4**, SECCION-NO-RESUELTA **1** (RELEASE: el prompt nombra «los cuatro prompts de fase» en prosa y **no se adivina**), FUENTE-AUSENTE **0** — sobre **34** fuentes declaradas y **23** secciones pedidas, todas resueltas. ⟦**Re-medido el 2026-09-25 por la conciliación final de la orden de calidad**: ese `SECCION-NO-RESUELTA` era **conducta correcta del generador** (AC22: nombra la sección, las rutas intentadas y no adivina), y su causa —la prosa del prompt de RELEASE— se corrigió **en el prompt**, no en el generador. La corrida de hoy da **5 COMPLETO / 0 SECCION-NO-RESUELTA / 37 fuentes** (sus bytes y su porcentaje viven en la salida completa de `evidence/…/CONCILIACION-FINAL-ORDEN-2026-09-25/11-carga-corrida-3.txt`, no en esta fila). **`carga.json` NO se re-escribió** (evidencia cerrada de FASE-D, **S12**): lo que esta fila describía sigue siendo el estado que D certificó⟧. **AC20**: carga total medida en los dos lados con el mismo comando (divisor 4 declarado), con los tres sumandos por fase y la resta **entre cargas totales**; los dos totales y el delta **no se copian en este archivo**: viven en `carga.json` y `carga-pre-post.md` porque este `.md` está dentro del pack que ese `stat` mide (**L-VCF-19**); `instrumentos/comprobar_resta_carga.py` verifica cinco identidades y sale `exit 0`; el workflow canónico entra en los dos lados mientras **D3** no lo rebane, y por eso el ahorro real queda **muy por debajo de un tercio** (concatenar no es ahorrar). **AC21**: frescura por **sha256 de `sources[]`** contra el árbol, cuatro causas sin colapsar (`FUENTE-AUSENTE` / `SHA-DISTINTO` / `FUENTE-ILEGIBLE` / `PACK-AUSENTE`), HEAD publicado como procedencia y **con test que prohíbe que venza**; el pack no está en su propio `sources[]`; y el generador resuelve un plan **también bajo `Archives/`** (demostrado sobre archivados reales: es la llamada del RELEASE tras el `git mv`). **AC22**: a los tres estados del contrato se añadió una cuarta salida medida, `SIN-DECLARACION`, con su `--check` imprimiendo `SIN-FUENTES` en lugar de `OK`. **AC23**: `mutation/` con verde (declara) y rojo (no declara, y el pack se achica en silencio conservando el estado) del símbolo real `GUARD_NO_TRUNCAMIENTO_ACTIVO` — los dos tamaños, en `mutation/resumen.txt` y tampoco se copian aquí (**L-VCF-19**) —, destino por argumento obligatorio y expediente de FASE-A protegido por observador de escrituras + `huellas` (S13). **Tests**: 49 casos en `tests/quality_gates/phase_briefing/` (un estado por test, guard de cero red autouse). **AC17**: `.agents/` con **cero bytes aportados** — la casilla literal «`git status .agents/` vacío» **no era verificable** porque el árbol llegó con 3 rutas sucias ajenas del bloque B, y se afirmó como lo que goberna AC17: observador de escrituras + sha256/tamaño de los 4 archivos, iguales antes y después. **AC16**: delta 0 (quick 11/11 `exit 0`, hook 7→7) con los 49 casos declarados aparte. **Herencia de C aceptada sin reabrirla**: el pack exhibe la parte mecánica medida de C y su `acceptance = NO-EJERCITADO` **como lo que es**; E1–E5 no se renegociaron y **D6 sigue dormida** (ver su fila en §Deuda). **Deuda nueva con dueño y disparador: S16** — la convención `Lee …` que parsea el generador no está escrita en `prompt-fase-template.md`: medido, **0 de 121** prompts archivados la usan. ⟦**Cifra y estado vencidos el 2026-09-27 por D-b**: la forma quedó escrita en el dueño que esta deuda le asignaba, y la población re-medida vive en §S16 de este archivo, que es su fuente única —esta fila no la re-transcribe—⟧ Evidencia: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/` (`informe.json`, `carga.json`, `carga-pre-post.md`, par `faseD_carga_pre/post.txt`, par `faseD_baseline/quick_pre/post.txt`, `baseline-pre-post.md`, `r26.txt`, `cero-red.txt`, `mutation/`, `instrumentos/`) |
| 5 · [FASE-RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre documental, sync, write-back y archivado en orden R2.5/R2.10 | MEDIA | **✅ CERRADA EN SU PARTE OFFLINE el 2026-09-25 — VERIFICADO sin red.** C0 ejercido (mandato con destinos literales, luego writers): release **4.78.0** `Gobernanza, costura, pertinencia y carga medida`, `release_date`/`date` 2026-09-25; cinco cabeceras por `sync_versions.py`; `DOMAIN_PRIMER.md` regenerado con su writer; `CHANGELOG.md` +90/0; `REGISTRY.md` por `log_phase_completion.py` (cabecera 2026-09-25). **Dos defectos de instrumento declarados con su cura pendiente en `scripts/`**: los writers reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y `readme_version_header` no goberna la fecha legible del README. **Sin autorización siguen**: Q7/D8 (premissa no comprobada), `--upload`/D9, `git mv`, `--fix`/`--update-baseline`, commit, push. ⟦**Vencido el 2026-09-27 en cuatro de sus seis miembros, con sus corridas en disco.** D8 fue re-corrido, D9 subido y verificado por descarga + sha256 (no por título), y el `git mv` se ejecutó: el plan vive bajo `.opencode/plans/Archives/` y `resolver_plan()` del escritor lo sigue resolviendo con el nombre pelado. El `--fix` **sí** se corrió dentro de D-c y ahí quedaron sus dos defectos abiertos, en su mitad de la fila S17; `--update-baseline` no se corrió y sigue reservado al archivado. De la lista en pie queda **push** (y el estado de los commits locales no se fija aquí: lo lee cualquiera con `git rev-list --left-right --count origin/master...HEAD` tras `git fetch`). La premisa «no comprobada» ya no está abierta —la consulta se corrió— pero **tampoco quedó verificada en su disparador**: ver la fila D8⟧. Evidencia: `evidence/…/FASE-RELEASE/` (12 archivos), y la de las cuatro corridas en `evidence/…/CIERRE-ORDEN-2026-09-25/`. ⟦**Y cae el último miembro de esa lista el 2026-09-27**: el push se corrió con el rango `2a778a4..1e4cb52`, con su L3 ejecutado antes y hallazgos en cero. De los seis miembros que esta fila re-midió quedan corridos los cinco de fase más el push; `--update-baseline` era el sexto y su turno era el archivado, que esta orden autorizó el mismo día (paso T3). La paridad sigue sin fijarse aquí como cifra: `git ls-remote origin refs/heads/master` contra `git rev-parse HEAD`⟧ |

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
| `scripts/run_all_validations.py` | **Este plan: solo lectura** (AC16). **Pero no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance («su connection en `scripts/run_all_validations.py`») | Corregido el 2026-09-20: la cifra de 11 checks **no la pinea el prompt de FASE-C** de `REFACTOR-WHATSAPP` sino cuatro documentos suyos (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`). **⟦Re-contado el 2026-09-24 por el bloque C de la orden de calidad: esa fila quedó vencida⟧** — su bloque de arranque ya no pinea la cifra, que fue sustituida por el comando que la imprime. Lo que hoy la contiene (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G, medido el 2026-09-24 con `grep -rl` sobre las dos formas de la cifra) son **registros de fases cerradas**: evidencia histórica que no se reescribe. Consecuencia para AC16: el delta 0 se contrasta contra la corrida propia, no contra esas filas. Y ese tercer plan en vuelo puede cambiar **la etiqueta y la invocación** del write-back `[15/15]` — que es justamente la fuente de verdad de A3 y del fix de AC1. Regla: AC16 (delta 0) obliga a re-medir aquí; **D10** obliga a re-leer la interfaz del write-back antes del `--upload` de este RELEASE ⟦**Re-medido el 2026-09-26 y la regla se cumplió en el otro sentido**: el runner cambió de manos fuera de este plan (D2 ejecutada por el operador) y su número pasó de 11 a 12 en el quick y de 15 a 16 en el completo. Esta fila seguía diciendo «solo lectura (AC16)»; lo que gobierna hoy es la segunda mitad: el runner **no está libre**, y el plan de `VERIFICADOR-ESCRITURA-QMIND` lo sigue teniendo dentro de su alcance.⟧ |
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
  presupuesto. **Lo que queda es D8 como re-correr, no como descubrir.** ⟦Ese «queda» se cerró el
  2026-09-27 en UTC (la noche del 2026-09-26 en el reloj local del commit): D8 fue re-corrido con el ID
  del notebook y su salida entera en crudo, y su fila lo declara en §Deuda. La nota no toca el límite de
  abajo, que mide otra cosa⟧
  Límite que sigue en pie: el
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
| D2 | Promover `validate_governance_numbers.py` a check del `--quick` con renumeración (11 → 12) | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases que pineen «11 checks». **⟦Aclaración del bloque C, 2026-09-24: las enmiendas de ese bloque sobre `REFACTOR-WHATSAPP` NO satisfacen este disparador⟧** — convirtieron en «el valor lo imprime la corrida» las **instrucciones prospectivas**, y dejaron intactos los registros de sus fases cerradas (`06-`, `09-`, `10-`, su `dependencias-fases.md` y su prompt de FASE-G), que son evidencia histórica. D2 sigue necesitando su propia sesión y su propia decisión ⟦**EJECUTADA el 2026-09-26, en una sesión que no es la previa a FASE-RELEASE de `REFACTOR-WHATSAPP`.** Se hace constar la desviación del disparador, no solo el resultado: la orden la dio el operador sobre esta fila, y el disparador literal sigue sin cumplirse. Medido y registrado en `evidence/…/CIERRE-ORDEN-2026-09-25/18-d2-quick-doce.txt`: quick **11 → 12**, completo **15 → 16**, coste del check promovido 0,35 s, cinco pins de `tests/` re-anclados con nota datada (la mitad que la fila S8 tenía reservada para este día), tres punteros de código actualizados, y nueve aserciones normativas de este plan anotadas como antecedente sin borrar su texto. Nace además **S19**, abajo: la frescura de un pack no mira al generador que lo imprime, así que editar el writer deja los packs vencidos con el `--check` en verde.⟧ |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura de A7: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B del plan en vuelo; los 254.010 de la concepción vencieron ese mismo día) | Plan propio, posterior | Mismo disparador para el rebanado completo; **D3 parcial**, no cerrada. La simplificación encargada a B no se difiere. **No** es FASE-D: el pack unifica lecturas declaradas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** (`validate_plan_semantics.py`): prompts de fase contra estado real del plan, con falsos positivos medidos contra los archivados | Plan propio posterior; **entra en este mismo directorio** si el disparador se cumple mientras está vigente | **Condicionado al resultado de FASE-C**: que el triaje entregue candidatos que el Paso 0 no ancló, con su aceptabilidad medida publicada en el informe. Si FASE-C sale inaceptable, **no se activa**: no se apila un segundo consumidor sobre una base que no funcionó. ⟦Precisión del bloque C, 2026-09-24⟧: mientras **D7** esté inactiva, la rama «salió aceptable» **no es alcanzable** — con proveedor falso `acceptance` solo puede publicarse `NO-EJERCITADO` (contrato **E4**), así que D6 queda **dormida con causa**, no «pendiente de que alguien consulte el número». Se re-evalúa al activar D7, no antes. **⟦Medido al cerrar FASE-C el 2026-09-24: la condición se cumplió literalmente — `coverage.json` publica `acceptance = NO-EJERCITADO` con su motivo y `valor: null`, sin cifra simulada (contrato E4). D6 queda DORMIDA y este plan no abre el lint semántico sobre una base que no juzgó nada; su re-evaluación sigue atada a D7⟧** **⟦Re-declarada al cerrar FASE-D el 2026-09-24 — no re-abierta ni re-asignada por interpretación: D leyó el `coverage.json` de C y encontró exactamente lo mismo que publicó C (`NO-EJERCITADO`, `valor: null`), así que la rama «el triaje salió aceptable» sigue sin ser alcanzable mientras D7 esté inactiva. D no reabrió C, no renegoció E1–E5 y no presentó la exhibición de candidatos en el pack como aceptabilidad obtenida. Lo único que activaría D6 es un proveedor real mediante (D7), y ese no es el estado de este plan⟧** |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev) como segundo proveedor detrás de `decision_client.py`; correr la comparación de proveedores y restituir «elegir midiendo» como AC | Plan propio posterior | Acceso existente desde 2026-09-20, pospuesto por decisión del operador. El consumidor natural es D6, el único trabajo genuinamente semántico del lote |
| D8 | Re-ejecutar la consulta Q7 de QMind. **Premisa vencida: el 2026-09-20 el CLI sí estaba disponible y la consulta se corrió en la auditoría de la concepción** (cuatro `retrieve`, resultados capitalizados como L-V2.1, L-V2.2 y D-V2.1). **Y su forma publicada es incorrecta**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; hay que pasar el ID `01a04d98-b7bd-778c-8441-26fdc7e35f45` | Este plan, sesión previa a FASE-RELEASE (re-corrida, no primera vez) | Que el notebook haya cambiado desde la auditoría, o que se quiera verificar el comando corregido con las citas que ya devolvió ⟦**RE-CORRIDO el 2026-09-27** (UTC; noche del 2026-09-26 en el reloj local del commit) por instrucción escrita del operador, con el ID del notebook y no con su título, y con la salida entera en crudo: cuatro consultas, 38 chunks y ocho fuentes distintas, en los siete archivos del subdirectorio de esta corrida bajo `evidence/…/CIERRE-ORDEN-2026-09-25/` (empezando por `00-d8-consulta-q7-re-corrida.txt`). **La mitad del disparador se cumplió y la otra mitad no, y se declara la diferencia en vez de dar la fila por verde.** «Re-correr» sí se cumplió. «Verificar que las citas que ya devolvió siguen en pie» **no**: de los tres identificadores que el disparador nombra, el crudo solo contiene a **D-V2.1** (24 menciones) y sale **cero** para **L-V2.1** y **L-V2.2**, que no están entre las ocho fuentes recuperadas. A eso se suma lo que el propio encabezado del crudo declara: el texto de Q7 no está registrado verbatim en el repo, así que las cuatro consultas de hoy se reformularon a partir de su descripción y no son las de 2026-09-20. Queda entonces una re-corrida con su salida, no una confirmación de las tres citas, y la premisa de la fila pasa a **comprobada en su corrida / no re-confirmada en sus citas**⟧ |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice después ⟦**EJECUTADO y VERIFICADO POR CONTENIDO el 2026-09-27**: subida hecha antes del traslado y frescura casada descargando la fuente y comparando sha256, **no** por título. Motivo literal por el que se eligió la descarga: `validate_qmind_writeback.py` decide `is_ingested` solo por título, y `do_upload` responde `[SKIP]` cuando el título ya existe — o sea que una segunda subida sobre este plan dejaría la versión anterior como verdad publicada sin avisar. **Consecuencia abierta que deja esta misma orden**: las anotaciones del cierre del 2026-09-27 (grupo A) **editan** `10-analisis-post-implementacion.md` **después** de la subida, así que el snapshot del notebook ya es más viejo que el archivo en disco, y el PASS 12/12 del verificador **no** lo ve porque no mira el contenido. Volver a subir es decisión del operador y exige el quinto control por sha, no la fe en el `[UP]`⟧ |
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
  honesto. Sin renumerar checks (**D2** sigue fuera). ⟦D2 se ejecutó el 2026-09-26 y D-a el 2026-09-27:
  ver sus dos filas en §Deuda, que es donde vive el denominador vigente de la corrida⟧
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
    ⟦**Vencido el 2026-09-25 por el operador ejerciendo esa decisión separada**: el commit `ab664ec`
    metió los once documentos del plan al versionado, así que esta frase ya no describe el árbol. Se
    conserva porque su regla sigue siendo la casa —commit y push son decisiones aparte, y ninguna
    corrida de fase las trae puestas—; lo que cayó es la afirmación de estado⟧
  - **bloque C**: **autorizado el 2026-09-24**, y ejecutado como enmiendas documentales sobre los cuatro
    planes (§Bloque C abajo). No es el piloto.
  - **piloto FASE-C**: **sigue sin autorización** y no se ejecutó. Su contrato está conciliado y su
    prompt listo; eso habilita pedir el mandato, no ejecutarlo.
    ⟦**Vencido por esta misma fila, que se olvidó de barrer a sí misma**: el cierre de arriba
    («Rectificado el 2026-09-24 al cerrar FASE-C», bajo **Estado de B**) ya cuenta el piloto
    **autorizado y ejecutado con mandato propio y corte «hasta listo para revisión»**, con su fila en
    §Cadena y su evidencia en `evidence/…/FASE-C/`. Las dos frases vivían en el mismo archivo con
    estados opuestos; queda la de abajo como estaba, y esta nota es la que la cierra⟧
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
| `CONTEXTO/RELEASE` | **Cuatro permisos, no tres** ⟦rectificado 2026-09-25; la etiqueta «tres momentos» sigue siendo el título-history del bloque por sus cinco referencias vivas⟧: **C0 destinos escribibles** (offline = sin red, **no** permiso de escritura: `sync_versions.py` sin `--check` puede reescribir `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md` y `docs/GUIA_TECNICA.md` según `sync_config.yaml`; `VERSION.yaml` es entrada y REGISTRY + `.last_doc_phase.json` salen del escritor del registro) · **cierre offline verificado** · **remoto** (D8 y D9, cada uno con autorización literal y presupuesto) · **traslado**. Se separa el mandato de la fase de esos permisos, con `PENDIENTE-AUTORIZACION` en vez de omisión. **Leer el estado ≠ reparar**: correr `validate_governance_numbers.py` es verificación y la reparación de `.agents/` no vuelve a hacerse aquí. **Sin writers automáticos**: `--fix` y `--update-baseline` salieron de la secuencia; los checks no escriben y ningún baseline se actualiza para absorber errores. ⟦**De esa regla, el 2026-09-27 se cumplió una mitad y se incumplió la otra, y las dos cosas van con su medida.** `--update-baseline` no se corrió (sigue reservado al archivado, y ni el gate de citas lo necesitó: pasó con 0 nuevas y 0 crecimientos). `--fix` **sí** se corrió dentro de D-c, y su corrida es la que dejó los dos defectos del escritor abiertos en la fila S17 de §Deuda: los 13 archivos gobernados a CRLF y la promoción de la forma minoritaria de la ruta. La regla de esta fila no se retira ni se rebaja —es lo que hubiera evitado ese trabajo—; queda como estaba y esta nota declara que la realidad de cierre no la siguió⟧ **El `--check` posterior al traslado se apoya en una regeneración prevista**, y un rojo de un derivado no autoriza editar código. **D2 no se da por satisfecho** por las enmiendas de `REFACTOR-WHATSAPP` | contrato §Dos momentos del cierre y §Orden del cierre, prompt FASE-RELEASE |

**Qué este bloque NO tocó y por qué.** No ejecutó el piloto FASE-C ni ninguna fase; no activó D6 ni D7;
no movió `VERSION.yaml` ni las versiones documentales de `04-`/`06-`; no escribió en `AGENTS.md`,
`.agents/**`, hooks, `REGISTRY.md` ni su tracker auxiliar; no regeneró DOMAIN_PRIMER; no tocó la
evidencia histórica de FASE-A/B ni los prompts de fases cerradas. La **incompatibilidad declarada** que
queda fuera de su alcance: `AGENTS.md` (§Vinculo con la Documentación) sigue condensando DOMAIN_PRIMER
en «se regenera en FASE-RELEASE» y `docs/CONTRIBUTING.md` titula «Regenerar» a su Paso 5b mientras la
fila de su tabla dice «Se VERIFICA»; son documentos centrales que la fila `WHATSAPP` resuelve **para el
plan** (regenerar al cerrar cada fase, verificar en RELEASE), pero alinearlos a ellos exige instrucción
expresa aparte y no se hizo por arrastre. ⟦**La instrucción expresa llegó el 2026-09-27 y se aplicó la opción
(c) de aquel dosier**: `AGENTS.md` ya no dice «se regenera en FASE-RELEASE (no manualmente)», sino
regenerar **al cerrar cada fase de implementación** con el comando de `doctor.py` y verificar con `--context`
en FASE-RELEASE, y su fila de la tabla de cross-references dejó de llamarlo «auto-regenerado»; el executor
recuperó el calificador «de implementación» que su fila de Estandares Compartidos había soltado.
`docs/CONTRIBUTING.md` **no** se editó: su Paso 5b y su tabla ya decían esa política, y la aparente
contradicción entre «Regenerar» en el título y «Se VERIFICA» en la fila es la de dos operaciones distintas
que la (c) separa, no un dato que haya que reconciliar. Lo que esta nota **no** hizo: correr el writer.
Alinear la política y regenerar el archivo siguen siendo dos actos, y el segundo no estaba en el mandato⟧

## Rutas ajenas en el árbol al commitear FASE-B (medido, no supuesto)

Al cerrar FASE-B (2026-09-21) había **tres rutas ajenas** en el árbol. Al abrir su tramo de commit
quedaba **una**: `.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`, que el
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
- ⟦**CURADA el 2026-09-27 por la familia D-b de la orden de calidad, con instrucción literal del operador
  sobre configuración central**: la forma canónica de la lista de lectura está escrita desde hoy en el dueño
  que esta fila le asignaba — `prompt-fase-template.md` §8 (template v1.7.0), con sus cinco reglas leídas del
  parseador y no de la memoria — y su regla hermana («tocar un generador obliga a regenerar sus derivados y
  commitearlos juntos», que es §S19) en el checklist post-fase del executor (v2.26.0). **La población de esta
  fila quedó vencida por el traslado y se re-mide, no se recalcula a ojo**: hoy hay **126** prompts de fase
  bajo `Archives/` y **5** declaran la lectura en la forma que el generador resuelve — los cinco de este
  plan, que ya están archivados, de modo que «0 de 121 archivados la usan» se lee al revés que cuando se
  escribió. Los que siguen sin declarar son **121** prompts ajenos, y no se reescriben: así lo decidió su
  FASE-RELEASE y sigue siendo corte del generador, no deuda. Medido con el lector real
  (`parsear_lista_lectura` del propio generador, importado) y no con una imitación del regex, en el
  instrumento `…/CIERRE-ORDEN-2026-09-25/GRUPO-B-P0-CONVENCION-2026-09-27/10-poblacion-s16-dos-criterios.py`.
  Un caso sirve de advertencia para quien vuelva a contar esto con `grep`: el único prompt ajeno que tiene
  una línea que arranca en `Lee ` es un `> Lee antes …` en la prosa de su encabezado, que el parseador no
  toma ni debe tomar — cuenta prompts con la línea, que no es la misma población que prompts resueltos⟧

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

**⟦Cuarta instancia de la misma familia, medida el 2026-09-27 al ejecutar D-c — NO curada, sigue abierta
bajo el dueño de esta fila⟧.** `scripts/validate_opencode_refs.py --fix` es un writer de texto sin
`newline="\n"`, y esta vez el daño lo hizo sobre **gobernado del propio plan**: tras el `git mv`, su corrida
re-escribió **13 archivos que HEAD almacena en LF** dejándolos en CRLF sobre el disco — `CR_disco`: 87 en
`plan_citations_baseline.json`, 636 en la orden de calidad, 194 a 383 en los seis prompts, y **1.551 a 3.645
en los cinco packs**. `git status` no lo distingue (guarda LF de todos modos), así que lo que se pierde no es
un rojo sino el **numstat**: sin normalizar, el commit del archivado habría aparecido como reescritura
completa de 13 archivos en vez de los 1–34 líneas por archivo que realmente cambió. Se normalizó por bytes
antes de commitear y el diff quedó simétrico (`17/17`, `34/34`, `3/3`), que es la firma de una reescritura de
rutas pura. **El detector no es un humano acordándose**: `tests/test_sync_writers_lf_y_fecha_readme.py` cubre
los tres escritores de la cura anterior y **no** a este, así que la familia volvió a colarse por la cuarta
puerta. La cura pedida es la misma de siempre (`newline="\n"`) más una aserción en esa batería que lo incluya.

Y un defecto segundo del mismo `--fix`, menor pero del mismo estilo de silencio: al reparar, **promueve la
forma minoritaria** de la ruta. Escribió `` `.opencode/plans/Archives/… `` en tres referencias de
`ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` que estaban en `` `.opencode/… ``, cuando el corpus marcado
versionado está en **518 contra 66** a favor de la forma sin barra (medido con `git grep -c` sobre `HEAD`,
contando el backtick como parte del patrón).
⟦Nota datada 2026-09-28 — **el par 518/66 no es reproducible con ninguna ancla, con ningún instrumento y ni siquiera en la revisión que lo escribió**, así que se declara aquí con las medidas que sí lo son, cada una con su población y su instrumento. Todo medido sobre el árbol limpio de `84c1aca` (`git status --porcelain -uno` = **0** líneas). **(i) Con el ancla de esta fila**, el literal `` `.opencode/plans/Archives `` sobre el corpus marcado versionado (**700** `.md` de `git ls-files`): **167 contra 29** ocurrencias, o **166 contra 29** líneas con el instrumento que esta fila nombra (`git grep -c -F` sobre `HEAD`). **(ii) Con ancla ancha**, el literal `` `.opencode `` sobre el mismo corpus: **604 contra 73** ocurrencias, **564 contra 73** líneas. **(iii) Con la población ampliada** a todos los ficheros versionados (**2.852**, no solo Markdown): **174 contra 32** con el ancla de la fila y **786 contra 77** con la ancha; sumando los ficheros **sin versionar** del árbol, **180 contra 36** y **799 contra 85**. Ninguna de esas combinaciones da 518/66, y la revisión que firmó esta cifra tampoco: `git log -S '518 contra 66' --oneline -- .opencode/plans` la pone en `3c2e6a3`, y medida **allí** con el instrumento de la fila da **147 contra 28** (ancla de la fila) y **524 contra 72** (ancha). **518 contra 66 queda como antecedente refutado.** Lo que la medición no tumba es la conclusión de la fila: la forma sin barra gana **5,8 a 1** con el ancla de esta fila y **8,3 a 1** con la ancha, así que «el `--fix` promueve la minoritaria» sigue en pie con su dueño. Crudos: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/05-f4-par-de-formas-s17.txt`, su gemelo por ocurrencias `06-f4-par-de-formas.txt`, el contraste de instrumentos `07-f4-divergencia-gitgrep-head-vs-disco.txt` y la tabla de los tres alcances `17-f4-tres-alcances.txt`. **Nota de instrumento**, para no volver a pagar el error de la quinta instancia: `git grep -c` cuenta **líneas**, no ocurrencias, y `git grep -F` con patrón que empieza por `/` sigue dando **0 falso** (medido hoy: `git grep -c -F` sobre el patrón `/.opencode/plans/Archives` = **0** líneas)⟧
El verificador acepta las dos, así que **no corta nada**: se
convirtió en una incoherencia de estilo dentro de un documento que usaba una sola forma. Se reescribieron a
mano las tres a la forma dominante —no hay pelea con la herramienta, porque `--fix` solo toca referencias
rotas— y quedó declarado aquí en vez de abrir un número nuevo: **S21 a S26 están todos usados en el corpus**
(el `S22` y `S23` de `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` son otra cosa), así que esta
observación vive como sub-punto de S17 y no como fila propia.

**⟦Quinta instancia de la misma puerta, medida el 2026-09-27 al ejecutar el archivado de JEV (paso T3 de la orden
de cierre) — el defecto sigue abierto bajo el dueño de esta fila⟧.** `validate_opencode_refs.py --fix` volvió a
escribir sin `newline="\n"`: **9** archivos del corpus pasaron a CRLF sobre disco (de 87 a 3.978 CR por archivo;
detalle y guarda de bytes en `evidence/…/CIERRE-ORDEN-2026-09-25/T3-ARCHIVADO-JEV-2026-09-27/`). Se normalizó por
bytes con las dos aserciones de rigor y los cinco packs se regeneraron con su escritor, que sí emite LF: el daño
es del `--fix`, no del generador de packs. Y promovió otra vez la forma minoritaria: **4** referencias quedaron
como `` `/.opencode/plans/Archives/… `` en `ORDEN-…md`, `CONTEXT-JEV-…md` y esta misma fila, y se devolvieron a la
forma dominante a mano, con el mismo criterio que la cuarta instancia. Dos precisiones medidas esta vez, para no
repetir el error de instrumeto de la anterior: (i) el recuento de formas **no** se puede hacer con
`git grep -F "/.opencode/plans/Archives"` —devuelve **0** incluso sobre archivos que el `grep` plano muestra
llenos de esa cadena—, hay que contar con `grep -o -F` sobre la ruta; y (ii) la promoción no es universal: en
`Archives/EVALUACION-JEV-…/README.md` y en los cinco packs quedaron ocurrencias con otro carácter delante, que
no son del `--fix` y **no se tocaron** (son contenido archivado y derivado, y la cura pedida sigue siendo la del
`newline="\n"` en el escritor, no reescribir corpus ajeno).

**⟦SEXTA INSTANCIA Y CIERRE POR EJECUCIÓN — medida y curada el 2026-09-27 en la sesión de curas fuera de
plans, con mandato literal del operador sobre `scripts/validate_opencode_refs.py`⟧.** Las dos escrituras del
guion llevan ahora `newline="\n"`: la del `--fix` sobre cada Markdown que repara y la de `--write-baseline`
sobre `.opencode/refs_baseline.txt`. La fila pedía «la misma cura de siempre más una aserción en esa
batería que lo incluya», y esa batería es `tests/test_sync_writers_lf_y_fecha_readme.py`, que pasó de **7**
a **10** pruebas corriendo el guion **real** sobre un espejo temporal (el `PROJECT_ROOT` del escritor sale de
su propio `__file__`, así que el espejo se arma copiando el guion a `espejo/scripts/` y el Markdown se planta
por bytes, porque re-escribirlo con `write_text` lo pasaría a CRLF por la misma traducción que se mide):

- **Tres controles nuevos, cada uno por su puerta**: `test_el_fix_de_refs_emite_lf_y_el_commiteado_escribe_crlf`
  (el Markdown reparado), `test_la_baseline_de_refs_emite_lf_y_la_commiteada_escribe_crlf` (el baseline — es la
  escritura que dejó los 87 CR de la cuarta instancia) y `test_el_guion_de_refs_no_toca_el_arbol_del_proyecto`
  (guard de destino **por operaciones observadas**, no por estado final: S13, y con ancla positiva de que el
  escritor sí escribe en el espejo).
- **Control negativo contra la versión commiteada**, leída con `git show` y ejecutada en scratch, sin
  `checkout` ni `stash`. Va anclada a `REV_CONTROL_DEFECTUOSO` (`5817edd`), **no** a `HEAD`: esta misma cura
  entra en el commit y desde ese árbol el control se quedaría sin rojo con el que compararse — la lección ya
  está escrita arriba, medida en `bdd1c4c`. Verificado con `git show 5817edd:scripts/validate_opencode_refs.py`:
  sus dos escrituras siguen sin el parámetro.
- **Dientes medidos por mutación (R2.8)**: quitado el parámetro en las dos escrituras, caen **exactamente**
  las dos pruebas nuevas del guion (`2 failed, 8 passed` — las de sync/doctor/S18 siguen verdes, así que el rojo
  es atribuible al parámetro y no al entorno), y restaurado el archivo el `sha256` sale idéntico
  (`f68dcfe1…`) con la batería en **10 passed**. Crudos: `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T2-S17-QUINTO-ESCRITOR/`.
- **Un defecto del instrumento propio, declarado**: el conteo de las escrituras no se podía hacer con
  `grep -c ', newline="\n")'` sobre el archivo mutado —el escape del patrón devuelve **0** y el mutante abortaba
  por ese falso cero—; hay que contar con `grep -o -F 'newline="\n"'`, que da **3** (dos escrituras y el
  comentario que las documenta).
- **Lo que NO cierra esta cura**: el segundo defecto del mismo `--fix` (promueve la forma minoritaria de la
  ruta) sigue sin cura, bajo el dueño de esta fila, con su medida de formas en la cuarta y quinta instancia.
  Y el residuo que el guion ya dejó en disco **no se normaliza aquí**: medido con
  `git ls-files --eol .opencode | awk '$1=="i/lf" && $2=="w/crlf"' | wc -l` salen **213** archivos (176 `md`,
  34 `json`, 1 `txt`), todos de planes archivados ajenos a esta sesión y todos invisibles a `git status` porque
  `core.autocrlf=input` normaliza al commitear. Normalizarlos es una reescritura masiva de corpus ajeno; queda
  declarado con su reparto en `…/T2-S17-QUINTO-ESCRITOR/23-residuo-crlf-opencode.txt`.

**Estado de la fila: CERRADA por ejecución el 2026-09-27** en su defecto de finales de línea (cinco puertas:
`sync_rule`, `run_regenerate_domain_primer`, `run_status`, y las dos de `validate_opencode_refs.py`), con el
sub-punto de la forma minoritaria de la ruta **abierto** bajo este mismo dueño.

⟦**Sello 2026-09-28 — C4 de la orden de curas en `scripts/` (sesión 2): el sub-punto de la forma minoritaria
queda CURADO, y con él la fila queda sin partes abiertas.** Las dos promociones de `fix_broken` en
`scripts/validate_opencode_refs.py` dejan de anteposer «/» a la ruta promovida: la del `archived_promotion` y
la del candidato único. `ref_target` no se toca y sigue aceptando las dos formas (`lstrip("/")`), así que la
cura cambia **lo que se escribe**, no **lo que se resuelve** — medida en el mismo espejo: `ref_target` de la
ruta con y sin barra dan el mismo `Path` que existe, y la ruta citada sigue estando rota antes del `--fix`,
que es lo que da oportunidad de promocionar.

Dientes medidos con el escritor **viejo** anclado a una revisión publicada fija, no a HEAD: la batería
`tests/test_sync_writers_lf_y_fecha_readme.py` corrió el guion vigente y el de `5817edd` sobre el mismo
plantado, y el control sigue promocionando la forma con barra mientras el vigente escribe la del corpus. La
batería pasó de **10** a **14** pruebas con las cuatro de este sub-punto (forma mayoritaria, idempotencia de
la segunda corrida, el control anclado y la aceptación de las dos formas), y el mutante **R2.8** —quitar
`newline="\n"` de las dos escrituras del guion— sigue tirando **exactamente** las dos pruebas de finales de
línea de ese guion (`2 failed, 12 passed`), no las cuatro nuevas: el rojo sigue siendo atribuible al parámetro
y no a la forma. Crudos: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/07-c4-bateria.txt`,
`08-c4-mutante-r28.txt`, `09-c4-espejo-forma.txt`.

Sobre el baseline: `validate_opencode_refs.py` deja **1** entrada congelada en `.opencode/refs_baseline.txt`
y **0** con forma de barra inicial — el conteo se lee con `grep -c -v '^#' .opencode/refs_baseline.txt` y el
de formas con `grep -o -F '|/' .opencode/refs_baseline.txt`, medidos en `10-c4-baseline-refs.txt`. El cambio de
forma **no mueve entradas**, porque `validate` guarda la referencia extraída (`REF_RE` arranca en `.opencode`,
la barra nunca entró en la clave). Y sobre el árbol real el guion en modo lectura sigue dando `[PASS]` con
**exit 0**: no hay referencias que re-promover.

Lo que el sub-punto **no** toca, declarado en la fila y re-confirmado hoy: las ocurrencias con barra que
quedan en corpus archivado (`Archives/DT4-RESIDUAL-FIXES`, `ASSET-ALIGNMENT-ZIONE-2026-07-23`,
`DELIVERY-ZIP-SINGLE-WRITE-2026-08-01` y el `README.md` de JEV) son contenido archivado y derivado, no obra del
`--fix`; reescribirlas sería la reescritura masiva de corpus ajeno que la sexta instancia rechazó. La medida de
formas de la cuarta instancia sigue valiendo tal como quedó rectificada el 2026-09-28: 518/66 **refutado**, y
la forma sin barra gana **5,8 a 1** con el ancla de la fila. **Estado de la fila: CERRADA por ejecución en sus
dos defectos (finales de línea y forma promovida), sin partes abiertas.**⟧

⟦**Sello 2026-09-28 — C7 y C5 de la misma orden (sesión 2): la séptima puerta de la familia y el residuo que
esta fila heredó.** Nota de procedencia para quien lea el índice: **D-H** y **D-C** son deudas definidas en el
expediente `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md`
(§5 y §9), fuera del corpus que recorre `build_lesson_index.py`; al nombrarlas aquí desde una fuente gobernada,
el índice las proyecta a los cinco packs y las publica como «citadas sin definición» (**52 → 54**, seis
menciones cada una). Eso es disclosure del instrumento, no un rojo: no se borra la referencia para achicar la
lista, se deja con su procedencia escrita. **C7 / D-H**: la escritura de `escribir_baseline` en `scripts/validate_plan_citations.py`
lleva ahora `newline="\n"`. Medido con el propio guion sobre una **ruta externa** (la orden prohíbe probar el
escritor contra el baseline real, y el guard `test_probar_el_escritor_no_toca_el_baseline_real` lo sostiene por
huella del archivo versionado): el escritor vigente emite **CR=0, LF=87** y el de `REV_INICIO` (`84c1aca`,
anclada y no HEAD, verificada con `git show` y ejecutada en scratch) emite **CR=87, LF=87, CRLF=87** sobre la
misma copia; idénticos salvo CR y la marca `created_at`. Es el **sexto** miembro de la serie (`sync_rule`,
`run_regenerate_domain_primer`, `run_status`, las dos de `validate_opencode_refs.py`, esta). Crudos:
`22-c7-pytest.txt`, `23-c7-escritor-baseline.txt`.

**C5 / D-C**: el residuo que la sexta instancia dejó declarado —**213** archivos bajo `.opencode` en `i/lf`
contra `w/crlf`— quedó normalizado por **escritor**, no por mano. La población se calculó con el comando
canónico de la casa y se re-midió hoy: **213**, sin deriva contra la cifra de la orden, reparto **178 `md` + 34
`json` + 1 `txt`** leído con `-z` y `core.quotePath=false` (las dos rutas `md"` del crudo 28- son los nombres
con escapes octales, que con esa lectura dejan de estar entrecomillados y el mismo conteo sale **213** por las
dos vías). El escritor **no normaliza nada que no case con su blob**: identidad `POST == git cat-file blob
HEAD:<ruta>` exigida antes de escribir y re-verificada después sobre las **213** rutas (**213 iguales, 0
distintos, 0 sin blob**), no sobre la muestra de tres que citaba la orden. POST con el mismo comando del PRE:
**0**. Mutante del criterio 5: una ruta fuera de la población se rechaza con exit propio (**4**) y el fixture
quedó intacto en CRLF.

Lo que la normalización reveló y se declara, no se esconde: al escribir las 213 rutas, `git status
--porcelain -uno` saltó de **18** a **231** líneas mientras `git diff --name-only` seguía dando **18** y el
`numstat` de esas rutas estaba **vacío**. Es cache de stat del índice, no contenido: con `core.autocrlf` del
ámbito de sistema en `true` y del repositorio en `input`, la vía «segura» de `git update-index --refresh`
rechaza el round-trip y avisa `needs update`; `--really-refresh` sobre las **213 rutas del informe del
escritor** (no sobre el resto del árbol) las sacó de `git status` y devolvió la población a **18** líneas.
`git diff --cached` sigue en **0**: el refresco tocó stat, no stapeó contenido. Crudos: `24-c5-pre-poblacion.txt`,
`26-c5-fix-y-post.txt`, `27-c5-post-y-refresco.txt`, `28-c5-identidad-post.txt`, `29-c5-cierre.txt`. Instrumentos
cazados mientras se medía, por la misma familia de siempre: `git ls-files --eol -z` parte la cabecera
`i/lf  w/crlf  attr/` como **un** campo separado por espacios (comparar `cols[0] == "i/lf"` sobre la cabecera
entera devolvía **0** rutas), y una ruta con escapes octales no resuelve en disco tal como la imprime el
`ls-files` con quoting por defecto (**OSError 22**). Ninguna de las dos es un rojo del árbol: son dos rojos del
instrumento.⟧

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

### S19 — la frescura de un pack no incluye al generador que lo imprime (nueva, 2026-09-26) — **CERRADA el 2026-09-27 en su parte gobernable; sobrevive solo por (c)** ⟦la (c) se cumplió el mismo 2026-09-27 con la instrucción literal de la familia D-b: la convención quedó escrita en `.agents/`; la fila baja declara lo que de (c) sigue siendo verdad estructural y qué queda aparte, en la (d)⟧

**Medido, no inferido.** Al ejecutar D2 cambié un literal dentro de `scripts/build_phase_briefing.py`
(`[8/11]` → `[8/12]`, en un comentario y en el mensaje que el propio script copia dentro de los packs).
Después de ese cambio, `build_phase_briefing.py --check` dio **`EXIT=0`** con la nota «FASE-C/D/RELEASE:
fuentes frescas *(procedencia distinta, no vence)*» y, sin embargo, regenerar **modificó los cinco packs**
(`10/10, 9/9, 13/13, 9/9, 18/18`). La causa está en el código, no en una corrida afortunada: la frescura la
gobierna el `sha256` de `sources[]` contra el árbol vigente — línea 688: «Frescura por sha de las fuentes
gobernadas. HEAD solo informa procedencia (AC21)» — y **el escritor no está entre sus propias fuentes**.

**Por qué importa.** Un derivado commiteado puede quedar con texto viejo mientras su verificador dice verde,
y el único que lo pone al día es quien editó el generador *acordándose*. Hoy me acordé y regeneré; el día que
no, el `--quick` pasa, el hook pasa, los 7/7 pasan, y el pack publicado miente sobre qué lo generó. Ninguna
batería lo cubre: no hay test que compare el literal del writer con el contenido del pack.

**Cure posible, y por qué no la aplico en esta sesión.** (a) Meter el sha del writer en la llave de frescura:
detecta el caso, pero re-vence **todos los packs en cada edición del script**, que es exactamente lo que AC21
evitó al sacar `head` de la llave. (b) Un gate que regenere en un scratch y compare contra el árbol — no
cambia la llave, cuesta una corrida y hace falta un verificador nuevo con su propia batería. (c) Convención, la que
se usó hoy: quien edita un generador regenera los derivados y los comitea en el mismo commit. Se registra con
dueño **decisión del operador** (ninguna de las tres es un cambio menor) y su disparador es la próxima edición
de un escritor que emita texto versionado. **No se número antes de esta fila: `S19` estaba libre, medido con
`grep -rn "S19" .opencode/` sobre el corpus activo.**

⟦**Decidida el 2026-09-26 sobre el árbol, sin esperar al disparador, y con los dos riesgos medidos.** La
evidencia completa está en `evidence/…/CIERRE-ORDEN-2026-09-25/19-s19-medicion-de-los-dos-riesgos.txt`; aquí va
el resultado, que reescribe el coste de cada cura. **(a) descartada con medición en contra, no solo con el
argumento AC21:** dos regeneraciones consecutivas sin ningún cambio entre ellas divergen en 16 a 32 líneas por
pack, todas el sello `generado` — gobernar al escritor fabricaría un rojo obligatorio de información nula en
cada edición del script. **(b) viable, y más barata de lo que esta fila suponía:** el destino alterno **ya
existe** (`--briefing-dir`, líneas 1002-1003 del propio script), así que no hay que editar al paciente para
operarlo; y el diff es determinista bajo una sola normalización — **53 líneas llevan el sello UTC en todo el
conjunto de packs, y ese conteo no se mueve entre corridas ni entre ediciones de corpus** (el denominador sí:
9.481 al medir por primera vez, 9.621 después de escribir esta misma anotación, o sea el ratio que ahí aparece
es un derivado condenado y no es la cifra que hay que gobernar). Al normalizar esas 53, los cinco packs quedan
idénticos entre corridas **y** idénticos al versionado. Lo que
viaja de esa verificación es el comando, no la cifra: `sed -E 's/· generado .[0-9TZ:.+-]+.//g;
s/"generated_at": "[0-9TZ:.+-]+"/"generated_at": "N"/g' <pack> | sha256sum` sobre los cinco packs, corrido dos
veces sin cambios entre ellas, da el mismo digest por pack. Los cinco valores que publiqué en el primer borrador
de esta anotación (`53f0d4f5a4a2` y compañía) **quedaron refutados por mi propia cola canónica** unos minutos
después de escribirlos: anotar esta fila es editar una fuente gobernada, y eso mueve el contenido de los cinco
packs. Queda como antecedente fechado el 2026-09-26 y su medición en
`evidence/…/CIERRE-ORDEN-2026-09-25/19-s19-medicion-de-los-dos-riesgos.txt` §8. Su forma es el patrón ya
probado en `scripts/verify_index_in_committed_tree.py`: materializar la revisión en un clon, regenerar a
scratch y comparar por sha normalizado, con controles anclados a una revisión publicada fija y nunca a HEAD.
**Sigue sin implementar: eso es código, y el dueño de esa decisión es el operador.** ⟦**Vencido el 2026-09-26
por la cura (b)**, que es código y se hizo con instrucción del operador; y vuelve a vencerse el 2026-09-27 con
**D-a**, que ata ese verificador al `--quick`. Lo que de esta frase sigue en pie es solo **(c)**: la convención
de cierre continúa sin escribirse en `.agents/` por falta de instrucción explícita, no por falta de
acuerdo.⟧ ⟦**S19 — cierre del libro: (a) descartada con medición en contra (`19-` §5); (b) implementada el
2026-09-26 en `scripts/verify_packs_in_committed_tree.py`; (c) vigente, dueña una instrucción literal sobre
`.agents/`, y casada con S16 porque son la misma superficie; (d) `generado_por_sha` medida el 2026-09-27 en el
expediente `22-` §3 y no aplicada — su coste es +1 línea por pack y exige un quinto patrón en `NORMALIZAR`, y
se probó que (b) **no** la necesita para atribuir el rojo. Con (b) cableada al rápido desde el 2026-09-27, S19
queda CERRADA en su parte gobernable y sobrevive solo por (c).**⟧
**(c) se
mantiene como puente y queda probada su insuficiencia:** el 2026-09-26 `--check` dio `EXIT=0` con los cinco
packs ya cambiados por una edición del escritor (244 inserciones / 99 supresiones, 6 líneas de pack citando el
`[8/12]` nuevo). Prueba estructural leída del artefacto: `sources[]` de FASE-A declara 4 rutas y **ninguna es
el escritor**, mientras el bloque meta ya publica `generado_por` — el pack nombra a su productor sin casarlo.
De ahí una cuarta opción que la medición hizo visible y no se aplica: sellar `generado_por_sha` como
procedencia **no gobernante** (coste ~el de la normalización, no re-vence nada, y (b) lo necesita para atribuir
el rojo). **No se toca `.agents/`**: la convención de cierre sigue sin escribirse en el executor por falta de
instrucción explícita, no por falta de acuerdo.⟧ ⟦**S19 queda CERRADA enteramente el 2026-09-27: se cumplió
la única mitad que le quedaba abierta, la (c).** La instrucción literal sobre `.agents/` llegó con la familia
D-b de la orden de calidad y se escribió en sus dos dueños — la convención de cierre en el checklist post-fase
del executor (v2.26.0) y la forma canónica `Lee …` en §8 del template de fase (v1.7.0), que es además la cura
de **S16** con la que esta fila estaba casada. Lo que la medición de (c) probó no se retira: la convención
**por sí sola** era insuficiente como gobernanza, porque `sources[]` no declara al escritor y el `--check`
verdeaba con los packs vencidos; eso sigue siendo cierto y por lo que existe la cura (b), cableada al rápido
por D-a. Lo que cambia es el estado del libro: **(c) deja de ser deuda**. La **(d)**, `generado_por_sha`, sigue
siendo una cuarta opción medida y no aplicada, con su coste y su dueño en el operador — cerrar (c) no la
absorbe ni la descarta⟧

⟦**Sello 2026-09-28 — cambio C6 de la orden de curas en `scripts/` (sesión 2).** Se re-mide (d) y
queda **ABIERTA por la salida (c)**: requiere una superficie que esta orden no autoriza, y aquí queda
la justificación. Medido sobre `84c1aca` más la cura C2, con crudo en
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/21-c6-s19d-coste-medido.txt`:
el verificador del árbol commiteado normaliza **cuatro** tokens inestables y **ninguno** cubre un
futuro `generado_por_sha`; el sha del propio escritor **sí** se mueve entre commits — cuatro
revisiones que lo tocaron más el árbol de trabajo dan **4 valores distintos sobre 5 mediciones** —,
así que publicarlo en el pack sin añadir el quinto patrón produciría `DIVERGE` entre revisiones
correctas: el mismo defecto de instrumento que **S20** documentó para el clon. El coste de la línea
nueva es **+1 por pack** (cinco packs en este plan) **más** ese patrón en
`scripts/verify_packs_in_committed_tree.py`, guion que la orden no nombra entre los cinco autorizados.
No la cubre tampoco la cura **C2** de esta misma tanda: gobernar la proyección de bytes del workflow
canónico no casa la identidad del generador, y la fila ya había medido que la cura (b) no necesita
(d) para atribuir el rojo. Dueño y disparador no cambian. Una nota de instrumento de esta medición:
el primer barrido de «¿está la clave?» se hizo por substring sobre el pack y dio **SI falso** en los
cinco — la prosa de esta misma fila viaja al pack y menciona `generado_por_sha` como texto. La clave
se lee en el bloque `BRIEFING-META`, no en el cuerpo; releída así, la clave no está publicada.⟧

### S20 — el clon del verificador hereda `autocrlf` de sistema y su `--check` de packs da rojo falso (nueva, 2026-09-26)

**Medido al verificar el commit `941530e` en su propio árbol.** `scripts/verify_index_in_committed_tree.py`
salió `EXIT=0` (`[OK] índice en el árbol de HEAD (565 rutas materializadas)`), pero al re-usar ese mismo clon
para el otro derivado, `build_phase_briefing.py --check` cortó **`EXIT=1`** con `SHA-DISTINTO` en siete rutas
gobernadas (`06-checklist-implementacion.md`, `dependencias-fases.md`, `10-analisis-post-implementacion.md` y
los cuatro `05-prompt-inicio-sesion-fase-*.md`). **El árbol no estaba mal**: los packs y el par del índice se
commitearon consistentes y el `--quick` del árbol de trabajo daba 12/12. Estaba mal el instrumento.

**Causa, medida por ámbitos de configuración** y no inferida: `core.autocrlf` vale **`true` en el ámbito
system** (`C:\Program Files\Git\etc\gitconfig`), no tiene valor en global, y vale **`input` en el config local
de este repositorio**. Un `git clone` **no copia** el `core.autocrlf` local de la fuente, así que el clon que
fabrica el verificador nace sin valor local y hereda el `true` de sistema. El `-c core.autocrlf=input` que el
script pasa al comando `clone` (en `revisar`, antes del `checkout`) solo gobierna ese proceso de clonado: el
`git checkout <rev> -- <rutas>` posterior corre dentro del clon, lee la config **del clon**, y convierte LF →
CRLF al materializar. Un verificador que compara `sha256` de bytes en disco pasa a comparar bytes re-escritos.

**Prueba de la atribución, sin tocar código:** clonar igual pero escribiendo `core.autocrlf=input` en la config
del clon **antes** del checkout. Sobre `941530e` con ese árbol, los dos verificadores dan verde:
`build_phase_briefing.py --check` → cinco líneas `[OK] … fuentes frescas (procedencia distinta, no vence)` con
`EXIT=0`, y `build_lesson_index.py --check` → `[OK] Índice de lecciones fresco (339 IDs)` con `EXIT=0`.

**Por qué el rojo salió en un derivado y en el otro no:** la comprobación del índice **parsea contenido**, así
que sobrevive al cambio de remates; la de los packs **compara shas de bytes**, así que el cambio la mata. Es la
misma familia de la trampa que obligó a poner `core.longpaths` **dentro** del clon (S15), pero con el síntoma
invertido: allí el árbol llegaba parcial (519 de 6.106) y el veredicto era ruido; aquí el árbol llega completo
y el veredicto es falso. Un verde o un rojo que dependen de los remates del sistema invitado no miden el
commit.

**Cura y coste.** Una línea: fijar `core.autocrlf=input` en la config del clon junto con `core.longpaths`, antes
del `checkout`, en `revisar()`. Su batería de pruebas necesita un caso que **no exista hoy**: un `--check` de
comparación byte-exacta corrido en el árbol del commit, porque el defecto es invisible para la batería actual
(que solo ejercita el índice, y el índice es tolerante). Es código, así que **dueño: decisión del operador**.
**Disparador:** la primera vez que alguien intente re-usar el verificador para un derivado que compare bytes —
que es exactamente lo que pide la cura (b) de S19, todavía sin implementar ⟦**vencido el 2026-09-26: se
implementó ese día; y el 2026-09-27 quedó atada al `--quick` por D-a**⟧. Las dos comparten árbol materializado
y las dos fallan silenciosamente si el árbol no es fiel.

**Nota de instrumento para la próxima numeración.** La fila S19 justifica su número con
`grep -rn "S19" .opencode/`, y ese comando barrido `node_modules`: medido hoy, `grep -rn 'S20' .opencode/` da
**10 coincidencias** todas dentro de `.opencode/node_modules/` (substrings en JS minificado), mientras que el
barrido acotado al corpus —
`grep -rn --exclude-dir=node_modules --exclude-dir=Archives 'S20' .opencode/plans .opencode/context` — da **0**,
que es la afirmación que importa. `S20` está libre. Los números en uso en este libro son
S1, S8, S10-S13, S16, S17, S18, S19 y esta misma S20. ⟦**Censo re-medido el 2026-09-27, que es la regla que
esta misma nota propone**: desde entonces se abrieron **S21** (los dos denominadores del runner) y **S29** (el
verificador de capitalización no ve a los archivados), así que los números con sección propia en este libro
son hoy **S16, S17, S18, S19, S20, S21 y S29**, y `S22`…`S28`/`S30` existen en **otros** libros
(`Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` y compañía) — contar en el corpus, no en el libro, antes de
usar un número: `git grep -l -E "\bS29\b" HEAD -- '*.md'` devolvió **0** coincidencias antes de tomarlo⟧

⟦**S20 curada el 2026-09-26, por instrucción del operador de seguir el orden propuesto.** Aplicada en
`scripts/verify_index_in_committed_tree.py`: `clon_fiel()` fija `core.longpaths=true` **y**
`core.autocrlf=input` dentro del clon antes del `checkout`, y **lee el valor efectivo** — si no es `input`,
sale `EXIT=2` con motivo, porque un árbol infiel no puede dar ni verde ni rojo. Se separó el materializado
del `--check` porque hay un segundo consumidor: `scripts/verify_packs_in_committed_tree.py` (abajo). Verificado
sobre `c85dff9`, una revisión publicada fija: con `input` el `--check` de briefing da `EXIT=0` y los packs del
clon son **byte a byte** los del blob (`git ls-files --eol` dice `i/lf w/lf`, y el clone devolver `i/lf w/crlf`
era la firma del defecto); con `true` forzado el mismo commit da `EXIT=1` con `SHA-DISTINTO`. La batería vive en
`tests/test_verify_index_in_committed_tree.py` (9 funciones, cuatro nuevas) y su control negativo **ejerce** el
defecto en lugar de simularlo, con la advertencia de re-anclaje si el `--check` dejara de ser ciego. Detalle de
instrumento corregido en el camino: contar remates con `grep -c $'\r'` da **todas las líneas del archivo**, no
los retornos de carro; se cuenta por bytes (`b"\r\n"`) o con `tr -dc`.⟧

⟦**Cura (b) de S19 implementada el 2026-09-26**, en la misma instrucción: `scripts/verify_packs_in_committed_tree.py`
materializa la revisión con `clon_fiel`, regenera los packs con `--briefing-dir` hacia un scratch **dentro del
árbol del commit** (sin `--informe` ni `--carga`, que es la guarda de S12), y compara cada pack por `sha256`
**normalizado**. La normalización es la que dejó la medición de `19-`: el sello `· generado \`<UTC>\``,
`generated_at` y `head`, que AC21 ya declaró no gobernantes. Veredictos: `0` reproduce, `1` diverge, `2` no
evaluable — y esa tercera salida existe por una medición que hice mal primero: el clon materializaba solo
`scripts` y `.opencode`, así que FASE-RELEASE, que declara `docs/CONTRIBUTING.md`, salía como `PACK-AUSENTE` y
mi verificador lo contaba como divergencia. Amplié el materializado a `docs` y `.agents` (~1 s) y dejé la
clasificación honesta para lo que quede fuera. El control negativo no simula: muta en el clon el literal `[8/11]`
que el propio escritor copia al pack y exige **dos** cosas a la vez — que este verificador dé `EXIT=1` con la
diferencia señalada, y que `build_phase_briefing.py --check` dé `EXIT=0` sobre ese mismo árbol. Ese par es S19
convertido en máquina. `tests/test_verify_packs_in_committed_tree.py`: 5 funciones.⟧

⟦**D-a ejecutada el 2026-09-27 por instrucción escrita del operador** («Continuamos según tu recomendación»
sobre el dosier `22-` §5). El verificador de packs en el árbol del commit es el check **`[13/13]`** del rápido:
**12→13** en el modo rápido y **16→17** en el completo. Lo que costó, medido antes y no de memoria: **26
literales re-etiquetados en cinco rutas**, no los cinco pines que declaraba el parte — 16 dentro de
`scripts/run_all_validations.py` (doce del rápido y cuatro del completo, todos impresos como literal), 2 en
`scripts/build_phase_briefing.py` (uno de ellos un **mensaje que el escritor copia dentro de los cinco packs**,
que es por lo que esta edicion re-vence los derivados y obliga a la cola), 6 en
`test_governance_numbers_reproduce_A1_A4.py` (cuatro `observed` + el `total` de la base de cobertura + su nota
datada), 1 en `test_governance_numbers_mutation_por_asercion.py` y 1 en
`test_briefing_se_genera_por_fase.py`. **Dos cifras del parte quedan corregidas por medición**: (1) la **premisa**
del hallazgo A3 —la copia del workflow en el fixture de `governance_numbers`, la fila que afirma el `[12/12]`— **no
se mueve**: es lo que el test audita, y re-etiquetarla borraría el defecto que caracteriza; (2) las cuatro
menciones del corpus (la fila A3 de `01-plan-maestro.md`, la casilla A1–A4 de `06-checklist-implementacion.md`, la
fila A3 de `10-analisis-post-implementacion.md` y la nota del instrumento en este mismo libro) **tampoco**: son
antecedentes fechados, tres ya marcados VENCIDA o rectificada.

Tiempo añadido al rápido, re-medido hoy sobre la base de hoy: **+2,4 s** (23,99 s → 26,4 s, **+9,9 %**), con
un clon de 588 rutas. El costo real no fueron los segundos sino la **tercera ronda de re-anclaje** en once días.

Y la parte que el dosier dejaba sin gobernar, cerrada con código: los ordinales del runner son literales
**porque** `validate_governance_numbers.py` lee su registro de emisores casándolos en la fuente, así que
volverlos dinámicos cegaría al verificador. En su lugar quedó una **guarda en `_print_summary`**: exige que los
ordinales impresos sean exactamente `1..N`, que el último lleve denominador `N` y que en el rápido los N
denominadores coincidan con `len(self.results)`. No consume un ordinal a propósito: si lo consumiera, renumerar
podría apagar la propia guarda. Sus dos controles, en
`evidence/…/CIERRE-ORDEN-2026-09-25/D-A-QUICK-TRECE/01-controles-guarda.txt`: dejar el denominador viejo en el
check nuevo da rojo, y dejar el denominador viejo en **un check cualquiera** del rápido también da rojo; la
fuente sin mutar da verde. Derivación de la guarda, consignada en su docstring porque fue un rojo mío: la
primera versión filtraba por número de línea contra la barrera `if not self.quick:` (línea 95, dentro de
`run_all`), pero las etiquetas viven en los métodos (línea 118 en adelante), así que devolvía **cero etiquetas**
y cortaba rojo sobre una fuente correcta.

Un rojo que la batería nueva encontró, y que no venía de mis ediciones:
`test_un_destino_relativo_no_escribe_dentro_del_clon`
moría en la **segunda pasada seguida** porque su destino es `temp/verif-ruta-<tmp_path.name>` y ese nombre es
**estable entre corridas**, mientras el `finally` limpia con `ignore_errors=True` — bajo bloqueo de Windows el
árbol queda y el `git clone` siguiente muere con «already exists and is not an empty directory», un fallo que no
medía al verificador. Se corrigió el **mecanismo de aislamiento** (limpiar antes de clonar, y `pytest.fail` con
el diagnóstico si el residuo persiste), no la aserción. Prueba: plantando el residuo a propósito la batería pasa
5/5, y dos pasadas seguidas dan 5/5 y 5/5. Queda como deuda de procedimiento **sin número** porque su cura ya
está en el árbol: otra prueba que derive su destino de un nombre estable bajo `temp/` caerá igual.⟧

⟦**Rectificado el mismo 2026-09-27, dos veces: la causa que di arriba era falsa y el control plantado era
débil.** (1) No es bloqueo ni camino largo —la ruta relativa más profunda mide **108** caracteres—: `git` deja
sus objetos de `.git/objects` **en solo lectura**, y `shutil.rmtree` en Windows levanta
`PermissionError: [WinError 5] Acceso denegado` sobre el objeto nombrado. Con `ignore_errors=True` ese error se
traga, así que el `finally` **nunca** había limpiado nada: el residuo era lo normal, no la excepción. (2) Mi
control «plantar el residuo» creaba un directorio **sin** el atributo de solo lectura, por eso daba 5/5 sobre un
caso que no era el real — plantar un árbol no reproduce la propiedad que lo hace irreborrable, y un control que
no reproduce el defecto no es un control. La cura verdadera es `shutil.rmtree(..., onexc=...)` quitando la
protección de escritura y reintentando ese nodo. (3) Lo que lo destapó fue **la suite completa**, no la batería
acotada: pasó de 4 rojos a **5** y el quinto era este test. Dos pasadas de una batería no prueban aislamiento
cuando el residuo lo fabrica la corrida anterior de esa misma batería.⟧

### S21 — el runner imprime dos denominadores distintos dentro del mismo modo (nueva, 2026-09-27)

**No confundir con `S21` de `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`**, que trata de concurrencia entre
sesiones y es asunto distinto: este es **S21 de este libro**, como `S19` y `S20` lo son.

En modo **completo** el runner ejecuta 17 checks, pero **trece** de sus líneas de progreso siguen diciendo `/13`
y solo las cuatro exclusivas del completo dicen `/17`. Leído del código (líneas 117-742 con `/13]` y 776-866 con
`/17]`) y no de una corrida: el modo completo invoca pytest y **no se corrió** para abrir esta fila. Existe desde
antes de D-a —era `/12` contra `/16`—, y la renumeración del 2026-09-27 lo **conserva sin agravarlo**: la
guarda nueva solo exige uniformidad de denominador en el modo rápido, porque gobernar la del completo sin tocar
los literales sería justo la cura dinámica que cegó al verificador.

- **Dueño:** este plan, o el siguiente que toque `run_all_validations.py`. No es bloqueante: ningún check, test
  ni documento afirma hoy el denominador del completo con forma `/N`, así que la contradicción es de **lectura
  humana** de la consola, y por eso se registra en vez de corregirse en silencio.
- **Disparador:** la próxima vez que alguien lea una corrida completa y crea el denominador que ve, o la próxima
  renumeración del runner.
- **Salidas, con su coste:** (a) re-etiquetar los doce del rápido también con `/17` en modo completo, lo que
  exige que el ordinal se componga al vuelo y **rompe** `PRINT_LABEL_RE` del verificador de gobernanza — la
  misma trampa que ya descartó la cura dinámica; (b) publicar en la cabecera de la corrida que el denominador
  impreso es **del modo rápido** y que el completo llega a 17, que es una línea y no toca ningún literal; (c)
  dejarlo y confiar en esta fila. La lectura recomendada es **(b)**.

⟦**Sello 2026-09-28 — C3 de la orden de curas en `scripts/` (sesión 2): CURADA con la salida (b), que es la
que esta misma fila recomendaba.** La cabecera de `_print_summary` publica ahora el modo de la corrida y a
qué modo pertenece el denominador impreso: «MODO: rapido — el denominador de las etiquetas impresas es el del
modo rápido (13); el modo completo llega a 17 y solo sus 4 exclusivas se etiquetan con ese numero». Los
literales de las etiquetas no se tocaron: de ellos vive el registro de emisores que lee
`validate_governance_numbers.py`, y la salida (a) lo cegaba (es la trampa que ya descartó la cura dinámica).
La lectura de la cabecera sale en ASCII, como el resto de las líneas impresas del runner, por la consola
cp1252.

Además, la **[GUARDA] corta también fuera del rápido**, que era el hueco que la fila dejó declarado: antes su
uniformidad dependía de `not self.quick`, así que en el modo completo un tercer denominador pasaba verde. Ahora
la guarda exige que los denominadores impresos estén dentro del par declarado por el modo (el del rápido y el
del total), con `len(orden_rapido)` leído del propio llamador por `_orden_del_modo()`, la misma lectura que
usa las etiquetas — así el denominador publicado y el gobernado salen de una sola lectura y no de dos cuentas
que puedan separarse.

Dientes y cifras medidas: con un denominador foráneo reintroducido en una etiqueta del rápido, la guarda cortó
en **ambos** modos (rojo documentado en la batería nueva); y apagando la comparación —volviendo la condición
a su forma anterior— el mismo escenario del modo completo **volvió a verde**, que es exactamente el rojo falso
que esta fila registró. La batería `tests/test_run_all_validations_denominador_por_modo.py` (cinco pruebas, con
los denominadores leídos del runner y no pineados) quedó en verde, el quick en **13/13** con `[GUARDA]` verde,
y `validate_governance_numbers.py --report` en **EXIT=0** después del cambio: el lector sigue resolviendo 13
del rápido y 17 del completo, y el número de etiquetas del archivo no cambió (**17**, igual que en `REV_INICIO`)
porque la cabecera nueva no es una etiqueta. El modo completo **no se corrió como corrida real**: invoca la
suite de pytest, prohibida en esta orden; su cabecera y su guarda se imprimieron por la vía offline. Crudos:
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/11-c3-quick-post.txt`,
`15-c3-cabecera-por-modo.txt`, `14-c3-mutante.txt`. **Estado de la fila: CERRADA por ejecución en su salida (b),
con el hueco de la guarda del completo cerrado en la misma tanda.**⟧

### S29 — el verificador de capitalización excluye `Archives/` por estructura, y este `00-` se quedó sin gate (nueva, 2026-09-27)

**No confundir con ningún número vecino**: el censo del 2026-09-27 sobre `HEAD -- '*.md'` marca usados
**S1…S28 y S30**, y **S29** devuelve **cero** coincidencias — es libre, y esta fila lo toma. (El enunciado de
la orden decía «S21 a S26 están usados»; se queda corto, ver el expediente `25-` §1.)

**Hecho medido con el propio código, no deducido.** `validate_lesson_capitalization.py` reparte el corpus en
`clasificar_planes()`, y esa función **salta el directorio `Archives/` antes de mirar el cutoff**: los 28
planes archivados van al grupo `archivados`, que `verificar()` **nunca iterar** — el bucle recorre solo
`grupos["alcance"]`. Con el cutoff de casa (`2026-09-12`) la línea de cobertura publicó
`alcance 3 · archivados 28 · exento_fecha 0 · sin_fecha 0`. **Este plan está en el grupo de 28.**

**Consecuencia para esta orden, que es por lo que se abre la fila y no por curiosidad**: D-d capitalizó diez
filas en el §2 de este `00-` **después** de que D-c moviera el plan a `Archives/` (2026-09-26). Desde ese
traslado, el `[10/13]` del rápido **no lee este archivo**, así que su `[OK]` no dice nada de las diez filas.
El green de una tanda que toca un plan archivado es, respecto a ese archivo, un verde vacío: no es que el
check encuentre bien las filas, es que **no llega a mirarlas**. Lo mismo vale para cualquier plan cerrado: de
los 28 archivados, **3** tienen `00-lecciones-capitalizadas.md` y ninguno está bajo gate.

- **Dueño**: `scripts/validate_lesson_capitalization.py`, o sea **código** — no le toca a esta sesión, que no
  tiene mandato de `scripts/`. Le corresponde al operador con instrucción literal, o al plan que toque ese
  verificador. Esta fila registra el estado del instrumento, no propone la cura.
- **Disparador**: la próxima vez que alguien cite el `[OK]` de `Lesson Capitalization` como evidencia sobre un
  plan **archivado**, o la próxima capitalización posterior a un cierre — que es exactamente la forma que
  tomó D-d.
- **Salidas, con el coste corrido y no predicho** (crudo `…/GRUPO-B-P0-CONVENCION-2026-09-27/26-coste-de-ampliar-el-detector.txt`):
  **(a)** quitar la exclusión de `Archives/` — ~2 líneas, y **fabrica 25 hallazgos `C1/AUSENTE`**, uno por cada
  plan archivado anterior a la regla del Paso 0 que no tiene `00-` (el primero que imprime la corrida:
  `Archives/ASSET-ALIGNMENT-ZIONE-2026-07-23: no existe 00-lecciones-capitalizadas.md`). Ampliar un detector sin
  gobernar su población tira el árbol, que es la lección que esta casa ya pagó. **(b)** una bandera explícita
  (`--incluir-archivados`, o el `--cutoff` hacia atrás) que audite **solo** los archivados con artefacto presente
  y publique su población en C0: medido sobre los **3** que sí lo tienen, darían **0 violaciones** — o sea la cura
  es pequeña y su verde es comprobable antes de commitearla; ~10-15 líneas más su test. **(c)** dejar el
  instrumento y gobernarlo por procedimiento: toda edición post-cierre de un `00-` archivado **cita la corrida
  explícita** del verificador sobre ese plan, que es lo que esta sesión hizo y lo que quedó en el propio `00-`.
- **Lo que sí se hizo en lugar del gate, y su techo**: se importó `duenos_del_corpus` y se corrió
  `analizar_plan()` sobre este plan archivado → **C1…C8 sin hallazgos**, 7 dueños, crudo
  `…/GRUPO-B-P0-CONVENCION-2026-09-27/22-c1-c8-sobre-el-plan-archivado.txt`. Eso prueba la forma **una vez y
  a mano**: no es verificable en el árbol y no protege la siguiente edición.

**⟦DECIDIDA Y EJECUTADA el 2026-09-27 por instrucción escrita del operador (orden de cierre, paso T1). La salida
es la (a) con el cutoff vigente, no la (a) desnuda que esta fila medía: se llama (a-prima)⟧**

`clasificar_planes()` dejó de saltar `Archives/` como estructura y sus hijos pasan por **la misma regla de cutoff**
que los de raíz; `grupos["archivados"]` se conserva como marcador de corpus y `verificar()` publica además cuántos
archivados quedaron en alcance (clave nueva `archivados_en_alcance`). `_linea_de_cobertura()` ya no imprime
«archivados excluidos»: imprime «N archivados en el corpus, M de ellos en alcance».

- **Por qué prima y no exclusión a secas** (crudo `…/GRUPO-B-P0-CONVENCION-2026-09-27/26-coste-de-ampliar-el-detector.txt`,
  re-confirmado el 2026-09-27 con las funciones del propio módulo): quitar la exclusión **sin cutoff** fabricaba 25
  `C1/AUSENTE`; **con** cutoff, 0. De los 28 archivados, 2 son posteriores al corte y entran, 20 quedan exentos **por
  su fecha** y 6 sin fecha parseable. La fila (a) de arriba describía el coste de la variante sin gobernar; la prima
  conserva ese cutoff como única regla de entrada.
- **Población nueva al cutoff de casa**, con su comando exacto — `python scripts/validate_lesson_capitalization.py`:
  `cobertura: 5 plan(es) en alcance (…) | 28 archivados en el corpus, 2 de ellos en alcance | 20 exentos por fecha
  anterior a 2026-09-12 | 6 exentos SIN FECHA PARSEABLE (…)` → exit 0, **0 violaciones**. Antes de la cura la misma
  corrida publicaba `3 plan(es) en alcance · 28 archivados excluidos`.
- **Dientes** (crudos `…/S29-A-PRIMA-2026-09-27/`): `02-` es el parche de la cura y `03-` el mutante — revertido el
  script real, caen 4 tests (`test_archives_no_se_excluye_por_estructura_sino_por_su_fecha`, `test_b5_…`, el
  parametrizado `test_medido_contra_el_predecesor…[2026-09-11-…]` y el nuevo anclado a revisión fija
  `test_el_plan_archivado_posterior_al_corte_entra_en_alcance_sobre_revision_fija`, materializado con `git archive`
  sobre `9c4a001`, donde la raíz de `plans/` no tiene ningún plan con fecha) y los otros 26 pasan igual; bytes
  restaurados con sha256 igual antes y después (`e2529b32…`). `04-`/`05-` dan el POST por población: **46 → 45 rojos,
  cae exactamente el de capitalización, cero nuevos**.
- **Lo que la cura NO toca**: el workflow `phased_project_executor.md` §2.5 sigue escribiendo en su «Alcance hacia
  delante» que el gate aplica a planes «que no estén en `Archives/`», y su fixture copia en
  `tests/quality_gates/governance_numbers/fixtures/` repite la frase. Esa prosa es **norma**, y promoverla pide su
  propia entrada de changelog de workflow: queda declarada vencida por el código y pendiente de la instrucción que
  la reescriba.
- **Dueño y disparador de la fila**: se retiran los dos pendientes que la abrían (el mandato de `scripts/` y la
  cita de un `[OK]` vacío sobre archivados). Lo que queda en pie de su texto es la advertencia: un verde del rápido
  sobre un plan archivado solo dice algo **desde esta cura**.
- **Alternativa descartada**: promover un check nuevo al `--quick` que audite el `00-` de los archivados. No
  toca el fondo — el fondo no es la falta de un check, es el **reparto de población** que comparten todos los
  checks de esa familia; un check extra con el mismo reparto hereda la misma ceguera y además cuesta un
  re-numerado (eso es D2 y su familia de pins).

**⟦Sexta cosa que esta fila gobierna, medida el 2026-09-27 en la sesión de curas fuera de plans⟧.** La cura
a-prima cambió el comportamiento y dejó **la prosa del executor describiendo la regla vieja**: el §2.5
«Alcance hacia delante» publicaba todavía «y que no estén en `Archives/`» y un conteo de archivados, y su
copia del contraejemplo congelado repetía la frase. Se curo el texto (executor **v2.27.0**, con su entrada
de changelog y su copia alineada a mano porque **no hay writer** que sincronice ese fixture — medido con
`git grep -ln "governance_numbers/fixtures" HEAD -- scripts tests`, 0 resultados).

- **Lo que quedó medido y sigue abierto**: revertir el párrafo a la frase vencida **no produce rojo** —
  `validate_governance_numbers.py` sale `SIN-HALLAZGOS` (19 instancias), las dos baterías de gobernanza y
  capitalización dan 79 passed y el `--quick` 13/13. Crudos:
  `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T1-PROSA-WORKFLOW/11-…` y `12-…`.
  Es decir: gobernar el **comportamiento** no gobierna la **descripción** del comportamiento, y nadie avisa
  cuando la descripción se desfasa. Dueño propuesto: el mismo de esta fila
  (`scripts/validate_lesson_capitalization.py`, que es quien conoce el reparto real), con un check de
  consistencia texto↔código; **disparador**: el próximo mandato de código sobre ese script, porque abrir un
  check nuevo es re-numerar y eso es D2.
- **Por qué no se absorbe aquí**: curarlo pide editar `scripts/` y esta sesión tenía mandato literal sobre
  tres cosas concretas (`validate_opencode_refs.py`, los seis arneses y la prosa), no sobre el verificador de
  capitalización. Queda como sub-punto con dueño en vez de fila nueva: **S33 está libre**
  (`git grep -l -E "\bS33\b" HEAD -- '*.md'` = 0) y se deja sin tomar, porque el asunto no es un defecto
  distinto sino la sexta cara del mismo reparto de población que gobierna esta fila.

### S31 — los arneses de FASE-C y FASE-D pinean la ruta de raíz del plan y D-c la archivó (nueva, 2026-09-27)

**No confundir con ningún número vecino**: el censo del 2026-09-27 sobre `HEAD -- '*.md'` con
`git grep -l -E "\bS31\b" HEAD -- '*.md'` devuelve **0** coincidencias — es libre, y esta fila lo toma. (S29 se
tomó el mismo día por la orden de calidad; S30 existe en **otro** libro, ver la nota de censo en §S20.)

**Hecho medido, no deducido.** El `git mv` de D-c (`3c2e6a3`, 2026-09-26) sacó este plan de la raíz de
`.opencode/plans/` y lo puso bajo su hijo `Archives/`. Cinco constantes de
los arneses de FASE-C y FASE-D resolvían la ruta de raíz a pelo, sin pasar por `resolver_plan()` del escritor,
así que desde ese commit sueltan `FileNotFoundError` y **42 rojos** entran a la suite por causa del traslado,
no por un defecto de producto: **36** en `tests/quality_gates/lesson_relevance/` y **6** en
`tests/quality_gates/phase_briefing/`. Crudo de la población: `…/S29-A-PRIMA-2026-09-27/05-atribucion-post-t1.txt`
(POST de T1: 46 → 45 rojos; estos 42 son exactamente lo que queda aparte de los 3 atribuidos el 2026-09-25).

**Las constantes** (todas se llaman `PLAN`; la orden las listaba por número de línea, aquí se citan por símbolo
porque la línea rota en cuanto se edita el archivo):

| Archivo del arnés | Símbolo |
|---|---|
| `tests/quality_gates/lesson_relevance/conftest.py` | `PLAN` |
| `tests/quality_gates/lesson_relevance/test_triage_mutation_aditividad.py` | `PLAN` |
| `tests/quality_gates/lesson_relevance/test_triage_propuesta_no_escribe_seccion_dos.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/conftest.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/test_briefing_carga_total_tres_sumandos.py` | `PLAN` |
| `tests/quality_gates/phase_briefing/test_briefing_se_genera_por_fase.py` | `PLAN` — **sexta, medida al ejecutar: no estaba en la lista de cinco de la orden** |

- **Dueño**: los arneses de **FASE-C** (`lesson_relevance/`) y **FASE-D** (`phase_briefing/`) de **este plan** —
  es instrumento de este plan, no deuda de un tercero. Se abre aquí porque la produjo su propio cierre R2.5.
- **Disparador**: ya sonó. Toda lectura de «la suite da N rojos» sobre un árbol donde este plan está archivado
  incluye estos 42 hasta que la fila se cierre.
- **Estado al abrir la fila**: **abierta, con la cura autorizada** por la orden de cierre del 2026-09-27 (paso
  T2). Se re-ancla cada constante a `plans/Archives/<PLAN>` y se ejerce con control negativo: revertida una de
  ellas, su archivo de arnés vuelve a rojo **por la misma causa** (`FileNotFoundError`), restaurada vuelve a
  verde. Crudos en `evidence/…/CIERRE-ORDEN-2026-09-25/`.
- **Lo que NO es esta cura**: no se toca el generador ni `resolver_plan()`. La lección de fondo ya está escrita
  (la de D-c: el verificador de packs montaba la ruta a pelo y quedó ciego tras el archivado; la cura ahí fue
  reutilizar `resolver_plan()` del propio escritor). Aquí se re-anclan literales de fixture, así que **la
  fragilidad estructural sigue**: un próximo `git mv` de este plan volvería a tirar estas seis constantes. Se
  declara en vez de absorberla, porque gobernarla es un cambio de arnés con su propio alcance.

**⟦CERRADA el 2026-09-27, paso T2 de la orden de cierre, con su POST por población⟧**

- **Seis constantes re-ancladas, no cinco.** La orden listaba cinco; la sexta (el `PLAN` de
  `tests/quality_gates/phase_briefing/test_briefing_se_genera_por_fase.py`) apareció al ejecutar: con las cinco
  curadas ese archivo seguía dando **4 rojos**. Control de residuo:
  `grep -rn '"plans" / "VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20"' tests --include=*.py` devuelve **0**, y las seis
  rutas bajo `Archives/` devuelven **6**. Quedan en el árbol otras menciones de la ruta vieja que **no** producen
  rojo y no se tocaron: un `assert ... not in` (línea 122 del mismo archivo), dos docstrings
  (`test_build_lesson_index_s15_fecha_versionada.py`, `test_sync_writers_lf_y_fecha_readme.py`) y dos constantes de
  `test_verify_index_in_committed_tree.py` que resuelven contra el árbol versionado, no contra el de trabajo. La
  frase de arriba decía «estas cinco constantes» y se corrigió a seis en la misma sesión, antes de commitear.
- **Causa por población, medida sobre el PRE (`…/S29-A-PRIMA-2026-09-27/00-suite-pre.txt`)**: 36 de los 42 son
  `FileNotFoundError` sobre la ruta de raíz; los otros 6 muestran otra cara del mismo hecho —**1 `IndexError` y
  3 `AssertionError` («informe sin packs no responde AC19») en `se_genera_por_fase`, y 2 en `carga_total`**— porque
  esos arneses listen el directorio en vez de abrirlo. Publicar «la causa es FileNotFoundError» sin el desglose
  habría hecho buscar una traza que ahí no está.
- **Control negativo** (crudo `evidence/…/CIERRE-ORDEN-2026-09-25/S31-RUTA-ARCHIVADAS-2026-09-27/01-…`): revertida
  la sexta, su archivo vuelve a **4 failed** con la misma firma que el PRE (2× «informe sin packs no responde AC19»,
  1× «list index out of range»); restaurado, **8 passed**, y el sha256 del archivo es idéntico antes y después
  (`cbc32233…`).
- **POST por población**: `python -m pytest -q -ra` → **3 failed, 4613 passed, 41 skipped, 4 xfailed, 0 errors**,
  exit 1. Contra el POST del paso T1 caen **exactamente 42** (36 `lesson_relevance` + 6 `phase_briefing`) y entran
  **0 nuevos**. Los 3 que quedan son los atribuidos el 2026-09-25 y no son de esta fila:
  `test_function_default_flags`, `test_diagnostic_includes_geo_metrics` y
  `test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion`.
- **Arneses verdes por separado**: `tests/quality_gates/lesson_relevance` **57 passed** exit 0 y
  `tests/quality_gates/phase_briefing` **49 passed** exit 0. El `--quick` quedó en **13/13** exit 0 tras regenerar
  lo que la edición de esta fila vence.
- **Estado de la fila**: **cerrada por ejecución**, con la fragilidad estructural declarada arriba como límite y
  no como pendiente de esta tanda.

**⟦Fragilidad estructural CERRADA el 2026-09-27, segunda tanda de la misma fila, con mandato literal de la orden
de curas fuera de plans⟧.** La cura que arriba se declaraba fuera de alcance («la forma durable sería reutilizar
`resolver_plan()` del propio escritor, y eso no entra aquí») entra ahora por su puerta: los seis arneses dejan de
armar la ruta y preguntan al escritor.

- **Cómo**: un puente, `tests/support_resolucion_plan.py`, que carga `scripts/build_phase_briefing.py` por ruta
  (el mismo oficio de los dos `conftest.py`) y expone `ruta_plan()`, delegando en `resolver_plan()` del escritor.
  Las seis constantes `PLAN` pasan por él. No se reimplementó la resolución: una sola copia de la regla, en el
  escritor — y no se tocó `resolver_plan()` ni el generador, que era el límite de la tanda anterior.
- **Semántica de error conservada**: el arnés pineado fallaba con `FileNotFoundError` al leer la ruta que ya no
  estaba; `ruta_plan()` levanta **ese mismo error** nombrando las rutas intentadas (por `rutas_intentadas()` del
  propio escritor), en vez de un `None` que revienta tres líneas más tarde con un `AttributeError` que no nombra
  el plan (R2.9).
- **Dientes anclados a revisión FIJA**, con el precedente de la cura de D-c para el verificador de packs: la
  revisión testigo es `44f53c2`, el **padre** del `git mv` de D-c, verificado con
  `git ls-tree --name-only 44f53c2:.opencode/plans | grep -c VERIFICADOR-CONTEXTO` = **1** en raíz y **0** bajo
  `Archives/`. Sobre un `git archive` de esa revisión el escritor resuelve el plan **en raíz**, y sobre el árbol
  de trabajo **bajo `Archives/`** — las dos aserciones en **un solo test**
  (`test_el_escritor_resuelve_el_plan_en_raiz_y_bajo_archives_en_la_misma_prueba`), porque separarlas permitiría
  apagar una mitad sin que el verde se note. El árbol versionado se afirma primero (`05-prompt-…` presente en
  raíz y ausente bajo `Archives/` en esa revisión): si la revisión dejara de ser testigo, el test lo dice.
- **Control anti-literal**, con su defecto declarado: la primera versión del predicado buscaba solo la cadena
  `"Archives" / "<PLAN>"` y **dejo pasar** `PLAN = ARCHIVES / NOMBRE_PLAN` — un verde vacío contra la forma más
  probable de reintroducirse, medido con el mutante T3-b. Fortalecido a dos cortes (exigir el paso por
  `ruta_plan(` y prohibir la aritmética de rutas sobre `ROOT`/`ARCHIVES`/`PLANS`), el mutante cae **rojo** y
  restaurado vuelve a verde.
- **Control negativo (R2.8)**: mutado el puente para resolver la raíz a pelo —la ruta vieja, donde el plan ya no
  vive— las dos selecciones dan **17 failed + 26 errors** con `FileNotFoundError` sobre
  `plans/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/00-lecciones-capitalizadas.md` (la ruta del error va escrita
  sin el prefijo `.opencode/` a propósito: publicada con él, `validate_opencode_refs.py` la lee como referencia
  del árbol y da rojo — es la prosa del corpus viajando a los cinco packs, que fue como se cobró esta misma
  tanda—); restaurado,
  `sha256` idéntico (`6fd87384…`) y **109 passed**. Precisión de fidelidad: revertir al literal **actual**
  (`plans/Archives/<PLAN>`) **no** da rojo hoy, porque el plan sí está ahí; la fragilidad no es del día que se
  escribe el literal, es del próximo traslado. Crudos en
  `evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T3-S31-RESOLVER-PLAN/`.
- **POST por población de la tanda**: `lesson_relevance` + `phase_briefing` = **109** recogidas (eran 106: **+2**
  del archivo nuevo de esta fila y **+1** que **no** es de esta sesión — el archivado de JEV metió un caso en el
  parametrizado `test_triage_sobre_plan_archivado_real[EVALUACION-JEV-TYPESAFE-2026-09-21]`). Suite completa:
  **3 failed, 4619 passed, 41 skipped, 4 xfailed**, exit 1, con los mismos tres rojos atribuidos el 2026-09-25 y
  **0 nuevos**; `--quick` en **13/13** con `[GUARDA]`.
- **Lo que NO cubre la cura**: el control anti-literal gobierna los **seis** archivos nombrados de estas dos
  selecciones, no un arnés futuro de un tercero; y `scripts/triage_lesson_relevance.py` conserva su propio
  `resolver_plan()` (el puente usa el del generador de packs, que es el que la orden nombraba).

**Estado de la fila: cerrada por ejecución también en su fragilidad estructural**, con el sub-punto anterior
gobernado por control y no por disciplina.

### S32 — el pack publica los bytes del workflow sin que el workflow sea fuente gobernable (nueva, 2026-09-27)

**Número libre, medido antes de tomarlo**: `git grep -l -E "\bS32\b" HEAD -- '*.md'` devuelve **0**
coincidencias (y 0 también bajo `scripts` y `tests`). Se toma aquí, no como sub-punto de otra fila, porque
su dueño es otro archivo y su disparador no coincide con el de §S19, que es el vecino más cercano por tema
(frescura de un derivado).

**Hecho medido al commitear la prosa del §2.5** (tanda `e2e44cd` → `6068f40`, la misma sesión). El pack de
cada fase publica en su bloque de lectura aparte el tamaño y los tokens estimados de
`.agents/workflows/phased_project_executor.md`, pero ese archivo **no** está en `sources[]` del pack — y no
está por contrato: `test_briefing_se_genera_por_fase` afirma que copiar el workflow al pack sería
«rebanar `.agents/` por la puerta de atrás (AC17/D3)». Con el workflow editado y ya commiteado, el
`--check` del escritor dio **verde** (mira las shas de `sources[]`, y ahí el workflow no figura) mientras
`--quick` cortó en su verificador del árbol commiteado con la firma `DIVERGE` en la línea del tamaño
(`109998 bytes → 112986`). Crudo con las dos corridas:
`evidence/…/CURAS-FUERA-DE-PLANS-2026-09-27/T4-POST-POBLACION/47-hallazgo-pack-publica-bytes-del-workflow.txt`.

- **Dueño**: `scripts/build_phase_briefing.py`, en su par de funciones de lectura aparte y de verificación
  de frescura. Es edición de `scripts/`, **no** de este plan: la misma restricción de mandato de código que
  ya gobierna §S17 y §S18.
- **Disparador**: el próximo mandato que autorice literalmente editar el generador de packs. Mientras no
  suene, el único corte real es `[13/13]` del quick — que sí lo ve, pero **después** del commit que mueve
  el workflow, no en el `--check` de quien lo edita.
- **Dos salidas medidas, ninguna aplicada**: (a) que el `--check` del escritor gobierne también la lectura
  aparte (sha o al menos tamaño del workflow por fase), para que el rojo salga en el instrumento de quien
  edita y no solo en el del árbol commiteado; (b) dejar de publicar el tamaño en el pack y moverlo a la
  salida del verificador. (b) es más chica pero toca lo que AC17/D3 decidió a propósito, así que no se hace
  por omisión.
- **Alternativa descartada**: re-generar los packs en el árbol de trabajo cada vez que se mueva el
  workflow. Eso es exactamente lo que mezcló la tanda: las anotaciones datadas de §S17 y §S31, todavía sin
  commitear, habrían viajado dentro del pack. La cura del árbol se hizo clonando HEAD con la config ya
  documentada (`--no-checkout`, `core.longpaths`, `core.autocrlf=input` **dentro** del clon) y generando
  ahí — que es un procedimiento, no un instrumento, y por eso queda esta fila.
- **Lo que NO verifica nadie hoy**: que un derivado publique datos de un archivo que no declaró como
  fuente. La regla de §S19 («la frescura mira las shas de sus fuentes») no alcanza este caso porque la
  fuente no está en la lista.

**Estado de la fila: abierta, con dueño y disparador.** Se abre aquí y no en otro libro porque la población
del defecto es el escritor de packs de **este** plan y su evidencia está en el subdirectorio de esta orden.

**Antecedente que esta sesión NO leyó antes de caer, y por eso se consigna: `L-VCF-20`**, capitalizada en
§Decisiones de FASE-D de `10-analisis-post-implementacion.md` (dueño: este mismo plan) exactamente sobre
esto — «la proyección de una ruta depende de su contenido igual que un sha: `sources[]` no la gobierna, pero
la línea de carga del pack imprime su `N bytes (~M tokens)`». Su instrucción era justamente la que le faltó al
agrupamiento de esta tanda: *«si una fuente de proyección queda en otro commit, nombrar en el mensaje cuál
deja el árbol reproducible»*. La lección estaba publicada e indexada (fila `L-VCF-20` de
`.opencode/LECCIONES-INDEX.md`, 13 citas solo en el plan dueño) y no se consultó: el mandato de esta sesión
arrancaba en el estado de partida y no pedía Paso 0, y el Paso 0 no es opcional cuando el trabajo planea
commits sobre derivados. La diferencia entre aquella vez y esta es solo el instrumento que lo cazó: entonces
`[13/13]` dio rojo después del commit, y ahora también.

**Qué agrega esta fila a `L-VCF-20` y por qué no es duplicado**: la lección goberna **la conducta de quien
agrupa commits**; esta fila goberna **el hueco del instrumento** (que el `--check` del escritor no mire las
proyecciones, o que el pack deje de publicarlas), que la lección explícitamente no cierra —su «INCLUIR» pide
tratar toda métrica publicada como fuente, y eso en el guion hoy no lo hace nadie.

⟦**Sello 2026-09-28 — C2 de la orden de curas en `scripts/` (sesión 2): CURADA con la salida (a), la que
la fila dejaba medida y no aplicada.** El `--check` de `scripts/build_phase_briefing.py` contrasta ahora la
proyección publicada de bytes **y** de tokens derivados del workflow canónico contra el archivo real en
disco; la puerta es `proyecciones_de_lectura_aparte`, llamada desde `verificar` en el mismo recorrido que ya
miraba las shas. El workflow **no** entra en `sources[]` (AC17/D3 intacto: `test_briefing_se_genera_por_fase`
pasa sin cambios y sigue afirmando que el workflow es lectura aparte, no fuente) y el tamaño **no** deja de
publicarse: la salida (b) quedó rechazada porque toca lo que AC17/D3 decidió a propósito.

Dientes medidos. Con el workflow aumentado en **43** bytes y los packs **sin** regenerar, el `--check` de
los cinco packs del plan salió `EXIT=1` nombrando la proyección vencida y sus dos números
(`publicados 112986 bytes / 28246 tokens; en árbol 113049 / 28262`) — el rojo salió en el instrumento de
quien edita, que es lo que la fila pedía; al restaurar el archivo por `sha256` (idéntico) el mismo comando
volvió a `EXIT=0`. Crudo: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/17-c2-check-y-mutante.txt`.
Aparte, la batería `tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py`
(seis pruebas sobre el escritor real con un plan plantado en temporal) afirma el verde, el rojo, el
`silent drop`, que `docs/CONTRIBUTING.md` **no** entra en el contraste por bytes, y —mutante del control—
que apagando la comparación el mismo escenario vuelve a verde falso: `EXIT=1` con la cura, `EXIT=0` sin
ella, `EXIT=1` de nuevo al encenderla. La selección completa de `phase_briefing` quedó en **57 passed**
(51 preexistentes + 6) con el quick en **13/13**.

Lo que esta cura **no** cierra: la fila sigue publicando el tamaño de un archivo que no está entre sus
fuentes, y ahora se corta; pero el hueco general —«un derivado publica datos de un archivo que no declaró
como fuente», la otra mitad de `L-VCF-20`— sigue sin gobernar a los demás documentos proyectados, y por eso
el criterio 5 de la orden dejó fuera `docs/CONTRIBUTING.md`: su cifra es un reclamo de tamaño publicado como
texto, no una proyección casable contra disco desde este guion. **Estado de la fila: CERRADA por ejecución
en el hueco del instrumento (salida a), con el límite de alcance declarado arriba.**⟧

## Cierre formal de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (2026-09-27)

Espejo de una sola línea, sin re-transcribir cifras (L-VCF-19: el párrafo de estado vive en la orden, y la fuente
única de cada fila es esta sección):

- **La orden queda cerrada en su alcance aprobado** por decisión escrita del operador al pegar su orden de cierre.
  Cayeron medidos sus motivos 1 y 2 (no queda fase pendiente del plan del piloto; la re-evaluación D1–D10 está
  leída y fechada en FASE-RELEASE). Los motivos 3 y 4 **no caen**: son el techo aceptado — auto-reporte de una
  sola muestra (D-V2.1) y piloto con proveedor falso (`acceptance = NO-EJERCITADO`, contrato E4).
- **Lo que el cierre no afirma**: que los cuatro planes del lote estén terminados, ni calidad semántica real
  medida, ni que D3/D6/D7/S10/S19(d) hayan muerto — siguen con dueño y disparador, re-medidos sin tocar código en
  `evidence/…/CIERRE-ORDEN-2026-09-25/T4-DIFERIDAS-2026-09-27/00-remedicion-sin-codigo.txt`.
- **Libro de este plan al cerrar la orden**: §S29 cerrada por ejecución (a-prima), §S31 abierta y cerrada en la
  misma tanda (seis constantes), §S17 **abierta** con su quinta instancia, §S19 en su **(d)** como opción medida
  y no aplicada, y el archivado R2.5 de `EVALUACION-JEV-TYPESAFE-2026-09-21` ejecutado con su write-back verificado
  por descarga + sha256.
  ⟦**Pasada datada del mismo 2026-09-27, en la sesión de curas fuera de plans, sobre este mismo libro**: dos de sus
  miembros cambiaron de estado después de escribirse esa línea y la nota anterior ya no describe el registro.
  **§S17 quedó cerrada por ejecución** en su defecto de finales de línea —curadas las dos escrituras de
  `scripts/validate_opencode_refs.py`, quinta puerta de la familia, con su batería ampliada de 7 a 10 pruebas y su
  mutante R2.8—, y **§S31 quedó cerrada también en su fragilidad estructural**, que es justo lo que el libro de
  arriba dejaba declarado como límite: los seis arneses resuelven ahora por `resolver_plan()` del escritor.
  Siguen como estaban **§S19 (d)** con dueño y las vivas **D3, D6, D7, S10 y S14**. Queda **abierto** bajo el dueño
  de §S17 su sub-punto menor: el `--fix` sigue promoviendo la forma minoritaria de la ruta. Y **se abrió una fila
  nueva, §S32**, por el hallazgo medido al commitear la prosa del §2.5: el pack publica los bytes del workflow sin
  que el workflow esté entre sus `sources[]`, así que el `--check` del escritor da verde y solo el verificador del
  árbol commiteado corta el desfase — con dueño, disparador y dos salidas medidas, ninguna aplicada. El estado vigente de
  cada una es su fila en esta sección, fuente única⟧.
