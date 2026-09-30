# Registro único de pendientes — orden de calidad 2026-09-22 y su estela (2026-09-29)

Estado al 2026-09-29, medido tras cerrar la divergencia del `CONTEXT` de JEV (commits `ec697ba` y `7737347`,
empujados; paridad `0 0`, arbol `0`). Este archivo es la version canonica del registro: unifica la tabla que el
operador trajo con lo que los registros fuente dicen hoy, corrige dos filas y anade cinco. La tabla del chat de
ese dia queda sustituida por esta.

Fuentes leidas para cada fila (todas con `archivo:linea` en la tabla):
`ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` ·
`.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/dependencias-fases.md` (DF) ·
`.opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/10-analisis-post-implementacion.md` (AN) ·
`.opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/README.md` (JEV) ·
`evidence/…/RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md` (RV) ·
`evidence/…/RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md` (RR) ·
`evidence/…/REINGESTA-CONTEXT-JEV-2026-09-29/00-expediente.md` (RI).

**La orden ya esta cerrada en su alcance aprobado** (`ORDEN:3`, decision escrita 2026-09-25, refrendada 09-27;
techo aceptado: motivos 3 y 4). Lo de abajo no es cierre de la orden: son las deudas que viven fuera de ese
alcance y cada una necesita una cosa distinta.

## Tabla unificada

| # | Pendiente | Estado medido hoy | Que lo destraba | Dueño |
|---|---|---|---|---|
| 1 | **D-B** — AC3 de JEV: (a) versionar candidatos con `original_sha256` verificable, o (b) enmendar la clausula | Re-verificado 09-29: **0 de 4 shas casan** sobre 2.988 ficheros versionados (RV §7.3, crudo `34-`) | Decision (a)/(b); la (b) pide instruccion literal con los archivos que toca | Operador |
| 2 | **D-D** — revision humana de la muestra BORRADOR (4 pares con `human_reviewed = false`, campos `reviewer`/`reviewed_at`) + mandato JEV-B | Sin cambios (RR:118; ORDEN fila D-D) | **Firma del operador**: ninguna sesion puede producirla. Es el mismo acto que destraba el bloqueante P1 de JEV-B: una firma, dos filas | Operador |
| 3 | **S14** — corpus mixto si el triaje corre con `--plans-dir` sobre copia | ABIERTA **con dueño ya asignado** (AN:150: este plan, FASE-D o RELEASE) y disparador corregido el 09-25 (AN:156-167): el `git mv` dentro del repo **no** la dispara | Que ocurra el disparador: primera llamada de C con `--plans-dir` sobre un directorio que no sea el repo (caso RELEASE con plan archivado). **No** espera asignacion de dueño | Este plan, FASE-D/RELEASE |
| 4 | **D-F5** — `scripts/log_phase_completion.py` sin bandera de fecha; hoy una entrada tardia escribiria fecha falsa | Verificado 09-29: **13** `add_argument` sin bandera; `datetime.now()` en `:152` y `:245`; cabecera `## {fase} - {fecha}` en `:172`; `docs/contributing/REGISTRY.md` = **0** ocurrencias del plan JEV (FASE-A sin entrada) | El proximo mandato que toque ese escritor | `scripts/log_phase_completion.py` ⟦**Sello 2026-09-30 — CURADA por ejecucion en la tanda de `CURAS-SCRIPTS-Y-CONTEXT-2026-09-30`.** Banderas `--fecha` (ISO estricta: patron anclado a `YYYY-MM-DD` **antes** de `date.fromisoformat`, que en Python 3.13 tambien traga la forma basica `20260923`) y `--nota`. La cabecera de la entrada y el "> **Ultima actualizacion:**" toman la fecha declarada: no queda `datetime.now()` en ninguno de los dos sitios. Sin `--fecha` el escritor **se niega con SystemExit propio y no escribe**, medido por operaciones observadas y no por el resultado final. Dientes: 26 passed en `tests/test_registry_fecha_documental.py` con tres mutantes que caen por su causa nombrada (A fecha opcional con default de reloj -> caen los dos rechazos; B bandera ignorada -> cae la fecha declarada; C guard de forma apagado -> cae `20260923`), y un control negativo con el escritor versionado en `7737347` que **reproduce el defecto** (escribe la fecha del reloj en la misma invocacion). **Desviacion declarada**: `--fecha` es obligatoria, y eso deja vencidas las lineas de uso del escritor en el workflow y en `docs/CONTRIBUTING.md`, ninguno de los dos dentro del alcance de esta tanda. Lo que la cura **no** hace: registrar la FASE-A de JEV -- sigue siendo acto del operador, con su `--fecha 2026-09-21` y su `--nota`. ⟧ |
| 5 | **S19(d), salida (c)** — quinto patron de `NORMALIZAR` que cubra un futuro `generado_por_sha`, mas 1 linea por pack | ABIERTA por sello **2026-09-28** (C6, DF:677-693): `verify_packs_in_committed_tree.py:43` normaliza **4** tokens y ninguno cubre ese campo; el sha del escritor si se mueve entre commits. Coste medido en `SESION-SCRIPTS-CURAS-2026-09-28/21-c6-s19d-coste-medido.txt`. Al tomarla: re-medir el numerador/denominador del parte `19-` (53; 9.481→9.991; normaliza 58 — cifras del 09-29, no confiar) | Cambio en `scripts/` con mandato propio; re-medir veredictos no la cura | Operador ⟦**Sello 2026-09-30 — EJECUTADA la salida (c), que es la que esta fila prescribia.** El coste medido por el C6 sigue sosteniendose (+1 linea por pack, 5 packs, y un patron nuevo) y la superficie que entonces no estaba autorizada ahora si lo esta, asi que no hubo que PARAR. Quinto patron en `NORMALIZAR` (`generado_por_sha` -> `"S"`) y emision del campo en `build_phase_briefing.py`, calculado sobre los bytes del propio archivo. Dientes: 5 passed en `tests/test_verify_packs_quinto_patron_generado_por_sha.py`, con su control anti-verde-vacio dentro de la prueba del patron (filtrado el quinto, los dos textos **dejan** de casar) y su control negativo con el verificador leido de `7737347` sobre el mismo arbol: EXIT 1 y `DIVERGE` nombrando la clave. El campo entra en el meta y **no** en `sources[]`: `--check` sigue en verde, que es la premisa de AC21 y la razon por la que la salida (a) estaba descartada. **Par del parte 19- re-medido el 2026-09-30**: numerador **53** lineas con sello UTC (no se movio), denominador **13.544** (los 9.991 del antecedente estaban vencidos; la serie es 9.481 -> 9.621 -> 9.636 -> 9.991 -> 10.630 -> 13.544), normalizan **58** los cuatro patrones viejos, ratio **0,39 %**. ⟧ |
| 6 | **JEV B → C → RELEASE** | `JEV:20-25`: B **SIN AUTORIZACION** + 2 bloqueantes humanos (P1 = fila 2; decision del *gap* de contrato), corre **sin red** · C: congelado de B + preflight de auth/cuota + **presupuesto escrito** (la unica con red) · RELEASE: detras de C. `JEV:95`: «ninguna fase de este plan es ejecutable hoy» | Permisos del operador, en ese orden; ya estaban pendientes antes de esta tanda | Operador |
| 7 | **D7 + S10** — activar Jev como segundo proveedor detras de `decision_client.py` | Vivas (DF:115-116). **S10 se paga entera dentro de D7**: geometria del `import` del SDK, (a) la puerta lo posee o (b) re-anclar AC6; AC6 vs AC9 incompatibles en D7 (`06-checklist:140-146`) | Credencial + presupuesto; es el «porton» del registro | Operador |
| 8 | **D6** — lint `validate_plan_semantics.py` | **DORMIDA con causa**: su gate es `acceptance = NO-EJERCITADO` (AC15); no accionable hasta activar D7 | La fila 7 | D7 |
| 9 | **D3** — rebanar el workflow canonico por fase | PARCIAL (DF:112): A7 = 263.973 bytes aprox. 65.993 tokens (medidos 09-20) | Plan propio, posterior | Plan nuevo |
| 10 | **S29, sub-punto** — gobernar la *descripcion* del comportamiento, no solo el comportamiento | Medido (DF:962-975): revertir el parrafo vencido del 2.5 del workflow **no produce rojo** (gobernanza SIN-HALLAZGOS con 19 instancias, 79 passed, quick 13/13). La fila S29 cerro; este sub-punto no | Check texto vs codigo en `validate_lesson_capitalization.py` | `scripts/validate_lesson_capitalization.py` ⟦**Sello 2026-09-30 — CURADO por ejecucion, sin re-numerar el quick ni el hook.** Check nuevo `C9` dentro de `scripts/validate_lesson_capitalization.py`: lee la regla **ejecutando** `clasificar_planes` sobre un corpus en scratch de dos archivados que solo difieren en la fecha, extrae el parrafo `- **Alcance hacia delante**` de los textos gobernados (el workflow y su copia congelada de los fixtures de gobernanza, que hasta ahora solo se alineaba a mano porque no hay writer) y exige la misma polaridad en las dos direcciones. Tri-estado R2.9 con `AUSENTE` tambien para poblacion vacia. Dientes: 12 passed en `tests/test_validate_lesson_capitalization_c9_descripcion_alcance.py`, y el mutante D (revertir la cura a-prima en `clasificar_planes`) hace caer los **dos textos reales del repo** con `regla=carpeta` y `C9=2`, EXIT 1 leido sin tuberia; el control negativo con el instrumento de `7737347` aprueba el mismo corpus que el curado corta, o sea la ceguera que la fila registro esta reproducida por el instrumento y el rojo se atribuye al check nuevo. Codigo `C9` y no un miembro mas de `C1..C8` a proposito: la familia C describe el `00-lecciones-capitalizadas.md` y esta enumerada en el template y en el workflow. ⟧ |
| 11 | **Verificador de frescura de `CONTEXT`** — la deuda que la tanda del 09-29 dejo senalada, **sin ID** (la orden prohibia inventarlo sin censo) | Medido 09-29: `git grep -E 'source download|fileSha256' HEAD -- scripts` = exit **1** (ningun script baja una fuente ni lee ese campo). `validate_qmind_writeback.py` sube CONTEXT pero su poblacion son los `10-analisis` (`ANALISIS_FILENAME`, `is_ingested` decide por titulo). Fuente del hallazgo: RI §6 y §13 | Mandato de codigo; censo de ID previo (ver abajo: el siguiente libre es **S34**) | Sin dueño ⟦**Sello 2026-09-30 — CURADO, con ID tomado tras el censo que la orden exigia.** Censo re-medido hoy sobre `HEAD` con el comando de la casa: S33 = 6 archivos (usado), **S34 = 0 (exit 1)**, S35 = 0, S36 = 0 -> la toma **S34**, con cabecera desambiguada en su fila porque convive con la nota que ocupo S33. Guion **propio** `scripts/verify_qmind_context_freshness.py` (no una extension del hermano, decision escrita): criterio descarga + sha256 contra el archivo gobernado, **nunca por titulo**; `metadata.fileSha256` solo corroboracion y su desacuerdo se publica. Poblacion medida al correr: **2** `CONTEXT-*.md` en la raiz, **1** gobernado (el de JEV, declarado en forma de **encabezado** -- la grafia que el detector del hermano pierde) y **19** excluidos con su razon (1 sin autodeclaracion, 18 en `Historico/`, congelado por R2.5); los `CONTEXT-*` que citan los planes archivados resuelven **todos** bajo `Historico/`, asi que no arrastran la deuda a la raiz. Barrido completo de las 56 fuentes antes de decir VENCIDO; NO-EVALUABLE (2) si el gobernado desaparece o si la poblacion queda vacia habiendo ficheros. Cableado al **modo completo**: 17 -> **18**, con los cuatro literales re-etiquetados, la guarda de denominador (§S21) cerrando la convivencia con el rapido en 13, y el pin de gobernanza re-anclado (A3 `[17/17]` -> `[17/18]`). Bateria: 17 passed, sin red. Corrida real: **[OK] frescura de CONTEXT: 1 fresco(s), 0 problema(s)**, EXIT 0, con el sha del disco casando con la fuente `01a0efcc-...` descargada. El `validate_qmind_writeback.py --strict` sigue en **[PASS] 13/13** con el check nuevo puesto. ⟧ |
| 12 | **Snapshot vencido `01a0e4d9-…` aun publicado** en el notebook QMind (56 fuentes) | Decision (a) del operador del 09-29: la forma resultante es original + cierre, con titulos distintos | `qmind source delete` existe por CLI; irreversible; merece letra propia | Operador |

## Correcciones aplicadas a la tabla del operador

1. **S14 no espera asignacion de dueño**: ya lo tiene (AN:150) y el disparador fue corregido el 09-25. Las
   ordenes recientes decian «no asignar dueño de S14» como prohibicion para esas sesiones, no porque estuviera
   vacante.
2. **S19(d)**: el sello que la deja abierta es de la tanda del **2026-09-28** (C6), no de la tanda del 09-29; esta
   ultima no la toco.
3. Filas anadidas que la tabla del operador no traia: **D7+S10** (7), **D6** (8), **D3** (9), **S29 sub-punto**
   (10), **verificador de CONTEXT** (11) y **el snapshot vencido como decision** (12).

## Censo de IDs de deuda, medido el 2026-09-29 (comando exacto)

    git grep -c -E "\bSnn\b" HEAD -- '*.md'

- **S33: 6 ocurrencias en 6 archivos** — YA USADO. La nota que lo declaraba libre a proposito (DF:973-975) viaja
  reproducida dentro de los packs generados, y el censo de la casa es sobre TODO el arbol, no sobre el libro: el
  numero quedo ocupado por su propia nota.
- **S34, S35, S36: 0 ocurrencias** — libres. El siguiente libre es **S34**; quien lo tome debe re-medir el censo
  ese dia (no fiarse de este) y desambiguar en la cabecera de su fila si convive con otro asunto.

## Declaraciones (no son deudas; decirlo es parte del cierre)

- **Pytest no corrio** en la tanda del 09-29 (no estaba en su mandato). Baseline vigente: `3 failed, 4642 passed,
  41 skipped, 4 xfailed` de la tanda anterior. Cualquier «sin regresion» sobre esa tanda seria falso: no se midio.
- **Ninguna otra fuente del notebook fue contrastada** por descarga + sha256 (56 fuentes). No medido no es fresco.
- **L3 no corrio** en ninguno de los tres pasos de publicacion de la tanda (`ec697ba`, `7737347` y el rango
  `f624e02..ec697ba`), por letra expresa del operador y continuidad declarada.
- **Otros planes con fases vivas**, fuera del alcance de esta orden: WHATSAPP C/D/E/F/H/E2E/VERIFY/RELEASE + AC5
  (`ORDEN:543`) y ESCRITURA-QMIND (fase unica pendiente).
- **Evidencia archivada fuera del arbol** (`20-permisos-pre.json` y compania, en `iah-evidence-archive/`): sin
  versionar por decision del operador, no por olvido.
