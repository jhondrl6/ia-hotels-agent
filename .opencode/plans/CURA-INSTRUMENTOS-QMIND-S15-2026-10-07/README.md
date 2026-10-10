# PLAN CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07) — índice

Cura de los dos instrumentos que gobiernan las lecciones del repo: el **verificador de write-back de QMind**
(`scripts/validate_qmind_writeback.py`, check `[17/18]` del modo completo) y el **control S15 del índice de
lecciones** (`tests/test_build_lesson_index_s15_fecha_versionada.py`, que vigila `[6/8]` del pre-commit, o sea cada
commit).

**Origen:** mandato del operador del 2026-10-07 (texto de sesión nueva) y el cierre del plan padre
`REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (4.79.0), cuya sesión dejó los dos huecos medidos y sin cura: sin writer para
saneear, y sin control S15 estable.

**Estado:** preparación cerrada el 2026-10-08 contra HEAD `98c190e`. **Sin código implementado.** ⟦Estado de FASE-A1, 2026-10-08, misma fecha y sesión distinta: AC1 y AC2 landed en el árbol de trabajo contra HEAD `d8a7d80`, **sin commitear** porque el commit no se autorizó en el chat. La frase anterior describe el árbol al cerrar la preparación y se conserva como registro.⟧ ⟦**Sello 2026-10-08, misma sesión:** llegó la instrucción literal «Git Commit + L3 + Push». commit `63b944a` con los ocho checks del hook versionado en verde, revisión profunda L3 **sin hallazgos** y rango empujado `d8a7d80..63b944a` (paridad verificada con `git ls-remote`). El sha del commit que estampa esta nota no se estampa en sí mismo.⟧ ⟦**Addenda del mismo sello (segundo push de
la sesión):** la nota anterior se escribió antes de empujar el propio sello, que viajó en `15f4fdd` con rango
empujado `63b944a..15f4fdd`. El sha de esta addenda no se estampa en sí misma: el tip publicado de la fase es el
que imprima `git ls-remote origin refs/heads/master` al leerla.⟧ ⟦**Segunda addenda del mismo sello (enmienda
documental del 2026-10-08):** la sesión del sello empujó una tercera tanda, `15f4fdd..67b7e2f`, así que la banda
completa de FASE-A1 es `d8a7d80..67b7e2f` — la cura `63b944a`, el sello `15f4fdd` y la addenda `67b7e2f`, con L3 sin
hallazgos en las tres tandas. Los rangos anteriores se conservan porque cada uno describe su push; no se
re-escriben.⟧ ⟦Sello del
cierre: el operador autorizó commit, L3 y push en la misma sesión. El commit documental de la preparación es
`b536748`, los ocho checks del hook versionado pasaron, la revisión profunda L3 no produjo hallazgos y el rango
empujado es `98c190e..b536748`. El sha del commit que estampa esta nota no se estampa aquí.⟧ **Punto de reanudación: FASE-B** (AC7 y AC8). ⟦**FASE-B cerrada el 2026-10-09** contra HEAD `77e64ca`, árbol sin
commitear (no hubo instrucción literal): AC7 landed con la causa medida (el reloj del fixture contra el piso de
fechas-en-nombre del corpus, 2026-07-06) y sus dos hipótesis descartadas; AC8 landed con el par derivado, el clon
fiel por patrón S20 y sus 2 mutantes; PRE 1 failed/3 passed → POST **8 passed**. **FASE-C declarada «no aplica»**,
así que el punto de reanudación del plan es **FASE-RELEASE** (AC10), que requiere versión dictada y autorización
literal de la subida.⟧ **FASE-A3 cerró el 2026-10-09** contra HEAD `b32a5ad`: AC5 landed con sus dientes de ruta, AC6 cerrada por la opción (b) —rojo declarado con dueño y sha, nada borrado— y DA-CIM.9 landed como subtarea 3b; su árbol quedó **sin commitear** porque no hubo instrucción literal. ⟦**Sello 2026-10-09, tanda «Git Commit + L3 + Push».** La autorización literal del operador llegó después del cierre documental y se ejecutó: commit `4fec5d0` (35 rutas: 16 modificadas + 19 nuevas; 2.049 inserciones y 106 supresiones) con los **8/8 checks** del hook versionado en verde, incluido `[8/8] Briefing packs in committed tree` (5/5 reproducidos, 0 divergentes, 0 no evaluables) sobre el árbol del pathspec; commit **por pathspec**, con las 13 rutas staged del hermano REFACTOR-WHATSAPP fuera del commit y **sin des-stagear** (verificado: 0 rutas ajenas dentro). La revisión profunda L3 devolvió **0 hallazgos** sobre el rango `b32a5ad..4fec5d0` y el push publicó ese rango con paridad `origin/master..HEAD` = **0** (tip confirmado por `git ls-remote origin refs/heads/master`). Verificación repetida sobre el **árbol del commit** (L-VCF-15): selección literal `57 passed`, `EXIT=0`, e integración documental `All checks passed` (crudo `E/FASE-A3/post_commit_en_head.txt`, que además reproduce L-CIM.8: el `--check` del índice sale `EXIT=1` en el clon y `EXIT=0` con las doce rutas ajenas copiadas dentro). Dos negaciones del clasificador precedieron a la corrida y se declaran aquí: pidió `AskUserQuestion` y luego afirmó que la respuesta del selector no estaba en el transcript; la desbloqueó el literal «corre la L3 y empuja». **El sha de este sello no se estampa a sí mismo:** lo cubre la primera corrida L3 de la siguiente tanda, y el tip vigente lo imprime `git ls-remote` al leer esta nota.⟧ **FASE-A2 cerró el 2026-10-08** contra HEAD `083e6ab` (AC3 y AC4 landed; la enmienda recibió su alta tardía en REGISTRY por mandato del operador). Cada fase re-mide su línea base con `git ls-remote origin refs/heads/master` al abrir, no con una cifra de este índice: todo commit posterior la mueve. Las dos decisiones del operador del 2026-10-08 están estampadas en maestro §4 (con su errata), §5 y §3, en `04-contrato-ejecucion.md` §R2, en `dependencias-fases.md`, en `10-analisis-post-implementacion.md` §Seguimientos y en los prompts de A2 y A3.

## Por qué importa cada fila

| Hueco | Lo que impide hoy | AC que lo cierra |
|---|---|---|
| La puerta de vigencia compara la instantánea contra el **cuerpo crudo** | Ningún plan cuyo `10-analisis` lleve identidades sustituidas puede dar verde en `[17/18]`: o se publica la identidad del cliente o el check corta. Es el caso que el plan padre y su FASE-G **obligan** a saneear | AC1, AC2 |
| El slug de la instantánea truncaba a 120 caracteres | Dos publicaciones con prefijo común pisaron el mismo archivo: el registro del padre tiene dos shas y el repo **un** byte-exacto (histórico: ya no es alcanzable) | AC3 ✅ A2 |
| `fuente_id` se publica vacío | Nada en el repo dice **qué fuente del notebook** es la que se publicó; la verificación depende del título (histórico: las dos ramas de `do_upload()` ya lo capturan) | AC4 ✅ A2 |
| `--upload` con el plan archivado | La ruta equivocada corta un `[FAIL]` que no nombra lo que buscó; y el modo verificación debe resolver en las dos raíces | AC5 |
| La fuente de la era G no está contable | Al curar AC2 aparece un rojo **verdadero** `[DUPLICADO-VIGENTE]` que hoy está tapado por el rojo de vigencia | AC6 |
| El control S15 pierde según el entorno | Un rojo que se re-produce en cada sesión y empuja a debilitar un control anti-regresión | AC7, AC8 (+ AC9 condicional) |

## Documentos

| Archivo | Para qué |
|---|---|
| `00-lecciones-capitalizadas.md` | Paso 0: 10 consultas re-ejecutables por dos ejes, 15 filas capitalizadas con su efecto sobre un AC concreto, 7 descartes, cobertura declarada con su límite |
| `01-plan-maestro.md` | §1 revalidación medida del mandato (dos filas refutadas, cuatro confirmadas, una rectificada por lectura), §2 decisiones congeladas, §3 fases con R3, §4 AC1-AC10 con su artefacto legible, §5 deudas con dueño, §6 qué hizo y qué no hizo la preparación |
| `04-contrato-ejecucion.md` | Límites y precedencias, inicio de cada fase, presupuesto (R2.1 con el instrumento **fuera de servicio**), reglas de tests/mutantes/tres estados, cierre incremental en 8 pasos, orden R2.10 del write-back y del archivado |
| `dependencias-fases.md` | Grafo, tabla de conflictos por archivo y la dependencia **dura** A1→A3 leída del flujo de control |
| `05-prompt-inicio-sesion-fase-A1.md` | AC1 + AC2 — las dos identidades y la puerta de vigencia |
| `05-prompt-inicio-sesion-fase-A2.md` | AC3 + AC4 — slug sin colisión y `fuente_id` desde la tabla; desde la enmienda del 2026-10-08 trae además las **dos reglas de ejecución** (código congelado antes del cierre documental y reemplazos documentales por un solo script de bytes bajo `temp/`) |
| `05-prompt-inicio-sesion-fase-A3.md` | AC5 + AC6 — rutas archivadas y la era G declarada con dueño, más la **subtarea 3b**: gobernar el bloque huésped también en el camino de migración, con su especificación, sus tres dientes y su mutante |
| `05-prompt-inicio-sesion-fase-B.md` | AC7 + AC8 — diagnóstico medido del control S15 y cura con diente intacto |
| `05-prompt-inicio-sesion-fase-C.md` | AC9 — condicional: solo si B concluye que la cura está en el generador |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | AC10 — write-back de **este** plan con el writer curado, docs oficiales y archivado |
| `06-checklist-implementacion.md` | Casillas por fase; ninguna pendiente se marca por adelantado |
| `09-documentacion-post-proyecto.md` | **Fuente canónica** de las métricas por fase |
| `10-analisis-post-implementacion.md` | Resumen, matriz de hallazgos, lecciones (serie `L-CIM` reservada), seguimientos y decisiones DA-CIM.1…DA-CIM.8. **No declara cierre** |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/` | Crudos de apertura (quick y selección PRE) y registro de la fase de preparación |

## Progreso

| Fase | ACs | Estado |
|---|---|---|
| Preparación | — | ✅ 2026-10-08 |
| FASE-A1 | AC1, AC2 | ✅ CERRADA, COMMITEADA Y EMPUJADA 2026-10-08 (banda `d8a7d80..67b7e2f`, L3 sin hallazgos en las tres tandas) |
| FASE-A2 | AC3, AC4 | ✅ CERRADA 2026-10-08 contra `083e6ab`; L3 sin hallazgos sobre `58dc034..083e6ab`. El tip vigente y su banda empujada los imprime `git ls-remote origin refs/heads/master` |
| FASE-A3 | AC5, AC6 | ✅ CERRADA 2026-10-09, commiteada (`4fec5d0`) y empujada (`b32a5ad..4fec5d0`, L3 con 0 hallazgos) el mismo día |
| FASE-B | AC7, AC8 | ✅ CERRADA 2026-10-09 (sin commit; árbol en «espera de autorización») |
| FASE-C | AC9 | ⬜ Condicional (la abre B) |
| FASE-RELEASE | AC10 | ⬜ Pendiente |
| FASE-VERIFY | — | **No aplica** (executor §4.6, criterio 2: cero ejecuciones E2E) |

## Cómo continuar

Una fase por sesión (R1). La siguiente sesión abre con el contenido de
`05-prompt-inicio-sesion-fase-A3.md` (bloque «Prompt de ejecución») —A1 y A2 ya cerraron— y
**re-mide** HEAD, paridad, status y el quick antes de escribir la primera línea: dos filas del mandato caducaron
entre su redacción y esta preparación, y la tercera puede caducar entre sesiones. La referencia de presupuesto y su
base medida viven en `04-contrato-ejecucion.md` §R2.

Reglas que gobiernan sin excepción (maestro §2 y contrato): ninguna fase re-baja una aserción existente para
conseguir verde; todo mutante se ejecuta sobre el instrumento versionado y se restaura verificando sha256; el
registro de QMind **solo** lo escribe el escritor; nada se borra en el notebook; commit, L3 y push requieren
instrucción literal del operador en el chat de la sesión correspondiente.
