# Registro de la enmienda — FASE-ENMIENDA (CURA-INSTRUMENTOS-QMIND-S15-2026-10-07)

**Sesión:** 2026-10-08 · **Rol:** ejecutor documental del plan — registrador de las decisiones del operador, no
constructor de código.
**HEAD medido al abrir:** `67b7e2fc770eecbf720975a0fe2084fd415804e4` (`git rev-parse HEAD`)
**Paridad al abrir:** `git ls-remote origin refs/heads/master` = `67b7e2f…` = HEAD (medido, no de memoria). FASE-A1
está publicada en tres commits: la cura `63b944a`, el sello `15f4fdd` y la addenda `67b7e2f`.
**Árbol al abrir:** `git status --porcelain -uall` = 13 rutas untracked **ajenas** (`12 briefing/FASE-*.md` bajo el
plan padre archivado y `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`), excluidas de
toda acción y de todo conteo (maestro §5 S-CIM-7, sigue vigente). Cero rutas modificadas.

## Premisa del mandato refutada al abrir

La línea base del mandato declaraba «quick archivado en `evidence/…/FASE-ENMIENDA/`». **Ese directorio no existía**:
`ls evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/` respondió solo `FASE-0/` y `FASE-A1/`. La cláusula describe el
estado que esta sesión produce (tarea 5), no el que encuentra. Se toma el quick **de apertura** aquí
(`quick_apertura.txt`, `EXIT=0`, etiqueta y denominador los imprime la corrida) además del de cierre.

## Qué se estampó

### DA-CIM.9 — gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9)

Caso A, vía a1, dictada por el operador el 2026-10-08. Los **cinco lugares** del censo, con la frase señal literal
idéntica en los cinco:

| # | Lugar | Ruta | Qué hace |
|---|---|---|---|
| 1 | maestro §4, fila AC6 | `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/01-plan-maestro.md` | **errata AÑADIDA** después de la fila original; la fila de AC6 conserva su texto íntegro |
| 2 | maestro §5, fila S-CIM-2 | ídem | estado pasa de DECLARADA a **DECIDIDA** con la vía a1 y su diente |
| 3 | prompt de FASE-A3 | `…/05-prompt-inicio-sesion-fase-A3.md` | **subtarea 3b** con la especificación, los tres dientes y el mutante; eco en su bloque pegable y en su checklist |
| 4 | dependencias de fases | `…/dependencias-fases.md` | fila A3 del estado de seguimiento **y** el seguimiento en la regla del grafo A1→A3 |
| 5 | análisis post-implementación | `…/10-analisis-post-implementacion.md` | la fila de seguimiento que dejó A1 pasa a **DECIDIDA** con este ID |

**Rutas ≠ lugares:** los lugares 1 y 2 comparten `01-plan-maestro.md`, así que el censo cubre **cuatro** rutas. La
serie se enunció además en maestro §2 (misma ruta del lugar 1, sin rutas nuevas) y en README, `06-checklist` y `09`
**sin** el token del ID: esos espejos citan la fuente canónica en lugar de re-transcribirla (AGENTS.md, «un
resultado, una fuente»).

**Especificación que quedó dentro del prompt de A3** (no se implementa en esta sesión): extraer el bloque huésped a
`_huespedes_sin_contabilidad(datos, fuentes, plan)` y llamarla también en la rama de migración antes del
`continue`; la capa D2 **no** se levanta para entradas `1.0` (siguen en abstención, nunca `[FRESCO]` sobre quien no
tiene `sha_cuerpo`); dientes (i) huésped roja sobre entrada `1.0` con `descargas == 0`, (ii) rojo + abstención de
migración en la misma corrida, (iii) `[CONTADOR]` sigue cuadrando (`cuerpo + migracion + local == N`) con la huésped
**fuera** de esa partición; mutante: apagar la llamada huésped en la rama de migración rompe (i), con restauración
verificada por sha256 sobre copia aislada. **Rechazadas:** a2 (re-publicar el `10-analisis` del padre como 1.1:
escritura remota que exige autorización propia, solo si el operador la pide aparte) y a3 (declarar y no tocar:
dejaría `[17/18]` en NO-EVALUABLE indefinidamente).

### DA-CIM.10 — presupuesto de referencia por fase

Caso C, vía c1. Estampado en los **dos** lugares del censo: `04-contrato-ejecucion.md` §R2 y `01-plan-maestro.md` §3.
Valores: **90 `tool_use`** para FASE-A2, A3 y B; **60** para FASE-RELEASE. La base medida es FASE-A1: **≈70 `tool_use`**
publicados en `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/00-registro-de-fase.md`.

**Procedencia de cada cifra, declarada:** el total ≈70 lo imprime ese registro; la separación en tres partidas
(≈30 código + tests + mutantes, ≈25 cierre documental, ≈15 verificaciones y re-tomas) la declaró el operador al
dictar la decisión y **no** la publica ningún instrumento del repo. El instrumento canónico
(`evidence/FASE-D/measure_iterations.py`) sigue FUERA DE SERVICIO (R2.1) y no se reintentó.

**Intacta** la cláusula del contrato: «Un exceso produce checkpoint y fase INCOMPLETA, no una segunda fase.» Las
mediciones históricas no se re-escriben: la fila de A1 en `10-analisis` y en `09` §D sigue diciendo «excede la
referencia de 60», porque contra 60 corrió. Los prompts de A2, A3 y B ahora dicen 90 **con su fuente** (`§R2`) en vez
de re-transcribir la decisión. **Rechazada c3** (aceptar checkpoints: el número deja de ser señal). **FASE-C no está
nombrada** en la decisión: se queda con 60 y la referencia queda abierta al operador para cuando B la abra — deuda
declarada, no resuelta por esta sesión.

### Reglas c2, dentro del prompt de FASE-A2

(i) congelar el código antes de abrir el cierre documental, con el POST y los mutantes re-tomados **una** sola vez al
final; (ii) los reemplazos documentales del cierre se ejecutan con **un solo script de bytes bajo `temp/`**, con
`count(old) == 1` por ancla, borrado al terminar. Echo en el bloque pegable y una casilla nueva en su checklist, para
que la regla tenga oportunidad de perder.

### Línea base refrescada

| Lugar | Estado antes | Estado después |
|---|---|---|
| `05-…-fase-A2.md`, tabla «Estado de fases anteriores» | «⬜ Pendiente — esta fase no arranca si A1 no cerró» | A1 ✅ CERRADA, COMMITEADA Y EMPUJADA, banda `d8a7d80..67b7e2f`, con la cláusula de que la línea base es el tip que imprime `git ls-remote` al abrir |
| `05-…-fase-A3.md`, misma tabla | ídem A1 pendiente | ídem, más la pointer a la subtarea 3b como resolución de la consecuencia 1 de A1 |
| `dependencias-fases.md`, fila 1 (A1) | «tip publicado `63b944a`» (afirmación de estado vigente, ya falsa) | se **añade** la addenda con la banda `d8a7d80..67b7e2f`; el rango del primer push no se re-escribe |
| `06-checklist-implementacion.md`, encabezado de FASE-A1 | banda del primer push | se **añade** la banda completa |
| `README.md` del plan, línea 18 | «A1 cerró commiteada y empujada (`63b944a`), así que la línea base de A2 es **ese tip**» (falso tras dos pushes más) | banda `d8a7d80..67b7e2f` y «la línea base de A2 es el tip que imprima `git ls-remote` al abrir» |
| `README.md`, tabla Progreso y §Cómo continuar | «FASE-A1 ⬜ Pendiente» y «la siguiente sesión abre con el prompt de **A1**» | A1 ✅ y punto de reanudación en FASE-A2 |
| `10-analisis-post-implementacion.md`, cabecera y fila de A1 | rango del primer push, sin señal de los dos siguientes | **addenda** con la banda completa y la L3 de las tres tandas |
| `09-documentacion-post-proyecto.md` §B y §D | sin la funcionalidad de la huésped en migración; presupuesto con la referencia sola | fila nueva en §B (⬜ A3 futura) y la referencia por fase en §D con su procedencia |

Revisados y **dejados como históricos** (no afirman un estado vigente, afirman qué viajó en un commit):
`00-lecciones-capitalizadas.md` fila L-G3, `05-…-fase-A1.md` (su propia fila de sello, que ya dice que su sha no se
estampa allí), `09-documentacion` fila de la regresión de vecinos, y los crudos `post_commit_en_head.txt` /
`quick_sello.txt` de A1.

## Lo que NO se corrió, con su motivo

- **`scripts/log_phase_completion.py`** — es **aditivo** y FASE-A1 ya tiene su fila; esta sesión no cierra una fase de
  implementación sino una enmienda documental, y volver a ejecutarlo apilaría una entrada duplicada (executor §4.5,
  Paso 4.5.1). Sin fila nueva en `docs/contributing/REGISTRY.md`.
- **`scripts/validate_opencode_refs.py --fix`** — no entraron rutas nuevas bajo `.opencode/` (se editaron ocho
  archivos existentes) y el fixer también edita documentos de **otros** planes, lo que chocaría con la prohibición de
  tocar el plan padre archivado (contrato §Límites).
- **`scripts/validate_wiring.py --write-report`** — no entraron archivos `.py` nuevos al árbol versionado; el `--check`
  del quick manda y quedó verde con su denominador impreso.
- **`scripts/validate_plan_citations.py --update-baseline`** — se comprueba con la corrida: si imprime «0 nuevas y 0
  crecimientos», no hay citas que registrar y el acto visible no se simula.
- **`scripts/doctor.py --regenerate-domain-primer`** — no aplica: es el derivado de las fases de **implementación** y
  esta sesión no toca código fuente ni tests (AGENTS.md, §Flujo Documental).
- **`docs/GUIA_TECNICA.md`** — su lectura fue **denegada por el clasificador** con el motivo «fuera del alcance
  declarado del mandato (`.opencode/plans/*.md`, `CHANGELOG.md`, `evidence/`)». No se re-intenta y no se editó. La
  nota técnica de una enmienda sin cambio técnico queda sin escribir, declarada aquí con la denegación literal.

## Cero escrituras remotas y artefactos intactos

Ninguna subida, descarga ni borrado en QMind; `qmind` no se invocó. `.opencode/qmind-writeback/registro.json`,
`scripts/` y `tests/` **intactos** en esta sesión (los dientes de DA-CIM.9 se codifican en FASE-A3). No se tocaron
`AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow, los hooks ni la numeración de checks del runner. No se
iniciaron FASE-A2 ni FASE-A3.

## Atributo de cierre verificable, re-medido

El mandato fijaba `git grep -l "DA-CIM.9"` = «exactamente 5 rutas» y `git grep -l "DA-CIM.10"` = «exactamente 2 rutas».
Esos dos números **no son alcanzables** en este repo sin romper R2.10, y se declara en vez de forzarlos:

- El censo de **lugares** mandató 5 spots para DA-CIM.9 y 2 para DA-CIM.10; los spots 1 y 2 de DA-CIM.9 viven en la
  **misma** ruta (`01-plan-maestro.md`), así que el censo cubre 4 rutas de plan, no 5.
- `scripts/build_lesson_index.py` indexa la familia `DA` con `ID_RE` y el par derivado
  (`.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json`) está versionado: **toda** regeneración
  obligatoria (R2.10, `[6/8]` del hook) añade esas **dos** rutas a cualquier `git grep -l` de un ID indexado.
- Por tanto la unidad correcta del atributo es «rutas del plan que llevan la frase señal» y «rutas totales», medida
  cada una por comando. La estampa de la corrida de cierre publica ambos números.

## Corte usado y presupuesto

**Corte tomado:** hasta el **push de la enmienda** — el mandato autorizó expresamente «Git Commit + L3 + Push» con su
pegada, así que el corte de esta sesión no es «listo para revisión» sino el commit y su publicación, y la nota de
presupuesto se escribe después de ellos.

**Unidad declarada:** `tool_use` **contados a mano sobre las llamadas de esta sesión** (una llamada a herramienta = 1;
los bloques paralelos se cuentan por llamada individual). El instrumento canónico
`evidence/FASE-D/measure_iterations.py` sigue **FUERA DE SERVICIO** (R2.1): pide el transcript del cliente y su acceso
está denegado; no se reintentó. Este número **no es comparable** con las mediciones hechas con ese instrumento.

**Referencia de esta sesión documental según el propio mandato:** ≈40 `tool_use`.

**Medido al cerrar:** **≈110 `tool_use`** contados a mano sobre las llamadas de esta sesión (una llamada = 1; los
bloques paralelos cuentan por llamada individual). **Excede la referencia del mandato por ≈2.8× y se declara como
checkpoint, no como fase adicional** (contrato §R2). Dónde se fue lo que los 40 no presupuestaban, con la corrida
delantera:

| Partida | Aprox. | Causa medida |
|---|---|---|
| Escrituras de estampado | ≈45 | 19 ediciones sobre 11 rutas (los cinco lugares de DA-CIM.9, los dos de DA-CIM.10, las reglas c2 y la línea base) |
| Lectura de línea base | ≈18 | siete documentos del plan y el registro de A1, más el grafo de dependencias, re-medidos y no heredados |
| Investigación del censo y la serie DA | ≈15 | leer `ID_RE`/`FAMILIES`/`_scan` de `build_lesson_index.py` para descubrir que la familia `DA` se indexa y que el par derivado añade rutas al atributo de cierre |
| Instrumentación y verificación | ≈12 | arnés de paridad de celdas, dos corridas de quick, escritor del índice con su `--check`, integración, citas y tres censos por comando |
| Gate de seguridad y publicación | ≈12 | resolución de ajustes, dos intentos de L3 **denegados por el clasificador**, la petición de instrucción literal, la L3 con `findings_count: 0` y el push con su verificación de paridad |
| Re-intentos de instrumento propio | ≈8 | un heredoc que se comió el backslash de la regex, un `grep -o "[^\x00-\x7F]"` que no es POSIX (daba un falso sin-acento), un `print` que reventó por cp1252 y un `AskUserQuestion` que el clasificador no aceptó como confirmación |

**Cuatro negaciones o fallos de instrumento registrados en vivo, ninguno reintentado como si fuera un rojo del
repo:** la lectura de `docs/GUIA_TECNICA.md` denegada; el primer y el segundo intento de `qodersec review --layer=l3`
denegados por el gate (el segundo, pese a la respuesta del formulario; desbloqueó la instrucción literal del
operador); el heredoc de Python; y la unidad del censo publicado, errata abajo.

## Sello de la enmienda (2026-10-08, misma sesión)

El operador autorizó commit, L3 y push con la instrucción literal «corre la L3 y empuja», después de que el gate de
seguridad negara los dos intentos previos. Lo que imprimió la corrida:

- **Commit documental:** `58dc034` — 16 rutas (13 modificadas + 3 nuevas), 520 inserciones y 50 supresiones
  (`git diff --cached --numstat` antes de commitear, `git show --stat` después), con los **ocho checks** del hook
  versionado en verde, incluido `[6/8] Índice de lecciones fresco (358 IDs)`.
- **Revisión profunda L3 sobre el commit nuevo:** `findings_count: 0`, **sin hallazgos**, corrida antes del push.
- **Rango empujado:** `67b7e2f..58dc034` (`git push origin master`), con paridad verificada por
  `git ls-remote origin refs/heads/master` == `git rev-parse HEAD`.
- **El sha de este sello no se estampa en sí mismo.** El tip publicado al leer esta acta es el que imprima
  `git ls-remote origin refs/heads/master`. Los rangos anteriores de FASE-A1 (`d8a7d80..63b944a`,
  `63b944a..15f4fdd`, `15f4fdd..67b7e2f`) **no se re-escriben**: este sello añade el suyo.

## Erratas que cobra este sello (medidas, no heredadas)

- **La unidad del censo estaba mal etiquetada.** Arriba publicué «9 ocurrencias en 6 rutas» con el instrumento
  `grep -cF`, que cuenta **líneas con coincidencia**, no coincidencias. La medida correcta sobre el árbol commiteado
  es `git grep -o -F "<frase>" HEAD | wc -l` = **10 coincidencias en 6 rutas**, con `2` en cada una de
  `01-plan-maestro.md`, `05-…-A3.md`, `dependencias-fases.md` y este acta, y `1` en `10-analisis` y `CHANGELOG.md`.
  La fila original no se re-escribe: queda como registro de lo que dije; esta es la corrección con su comando.
- **El mensaje de commit lleva cuatro signos tipográficos no ASCII** (`§`, `«`, `»`, `≈`) **y cero letras acentuadas**
  (medido con `re.findall(r'[^\x00-\x7f]', msg)` sobre `git log -1 --format=%B` → `['§', «, », ≈]`, sin alfabeto). El
  mandato pedía «sin acentos» y se cumple en su letra; aun así se declara porque la convención de la casa es ASCII
  estricto en los mensajes. No se re-wordé: el commit ya está empujado y su sha `58dc034` viaja citado en este sello.
- **Los dos crudos del quick son CRLF en disco y LF en el blob** — ya declarado en la errata de instrumento arriba, y
  confirmado por el aviso de `git add` al indexar.

## Addenda del sello (segundo push de la misma sesión)

El sello de arriba se escribió y se commiteó en `f4ceada`, que **después** fue empujado (`58dc034..f4ceada`), así que su
línea «rango empujado `67b7e2f..58dc034`» quedó describiendo el primer push de la enmienda. No se re-escribe: describe
el push que existía cuando se redactó. Lo que se añade es la banda completa de la enmienda,
`67b7e2f..f4ceada` (la enmienda `58dc034` y su sello `f4ceada`), y el hecho de que **el sha de esta addenda no se
estampa en sí misma**: el tip publicado es el que imprima `git ls-remote origin refs/heads/master` al leer esta acta,
medido `f4ceada` al cerrar la tanda.

La L3 sobre el commit del sello **no se corrió**, y la razón no es una omisión de esta sesión: el intento devolvió una
**denegación del clasificador** con el motivo impreso «L3 security review already executed in this session (commit
58dc034) before push. No new unreviewed commits exist. This duplicate run is unrelated to the user's documented
request». El contrato manda no reintentar un permiso negado, así que queda registrado tal cual: **la revisión profunda
cubre el commit de la enmienda (`58dc034`, `findings_count: 0`) y no el commit del sello (`f4ceada`)**. El sello es
dos rutas de documentación bajo `evidence/` —acta y crudo—, sin código y sin secretos, y esa cobertura parcial se
declara en lugar de afirmarse como «sin hallazgos en las dos tandas».

## Estampa de la corrida de cierre

Los valores siguientes los imprimió la corrida de esta sesión sobre el árbol de trabajo; **ninguno** es heredado.

| Qué | Valor impreso | Comando e instrumento |
|---|---|---|
| Quick de apertura | `TOTAL: 13/13 validations passed`, `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick`; crudo `quick_apertura.txt`. El denominador lo publica la corrida (línea `[GUARDA]`), no este documento |
| Quick de cierre | `TOTAL: 13/13 validations passed`, `EXIT=0` | mismo comando; crudo `quick_cierre.txt`; árbol: el worktree con la enmienda sin commitear |
| Índice de lecciones (escritor) | `[OK] 358 IDs definidos + 93 sin definición (18 análisis, 449 .md citados)`, `[fechas] nombre=347 commit=11 sin_fuente=0`, `EXIT=0` | `venv/Scripts/python.exe scripts/build_lesson_index.py`; los 93 son 91 + **los dos IDs nuevos de esta enmienda**, verificado en el JSON: `citados_sin_definicion` contiene `DA-CIM.9` (15 citas) y `DA-CIM.10` (6 citas), ambos con dueño `CURA-INSTRUMENTOS-QMIND-S15-2026-10-07` |
| Integración documental | `RESULT: All checks passed`, `EXIT=0` | `venv/Scripts/python.exe scripts/validate_document_integration.py`; reporta `CHANGELOG.md … estado Git SUCIO` porque al medir todavía no estaba staged — no es un rojo |
| Citas históricas | `[OK] Plan citations: 745 citas historicas, 0 nuevas y 0 crecimientos (81 archivos en el inventario)`, `EXIT=0` | `venv/Scripts/python.exe scripts/validate_plan_citations.py`; con «0 nuevas y 0 crecimientos» impresos, **no** se invocó `--update-baseline` |
| Paridad de celdas en las tablas editadas | 0 roturas en las nueve rutas editadas; las tres líneas marcadas son trazos del grafo ASCII dentro de un bloque ``` | arnés de lectura `temp/check_cells_enmienda.py` (bajo `temp/`, excluido por declaración de Git) ejecutado con el `venv`; **borrado al terminar** |

### Censo de estampado (unidad declarada: ocurrencias por ruta, medido con `grep -cF` sobre el árbol)

Frase señal literal `gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9)`:

| Ruta | Ocurrencias | Papel |
|---|---|---|
| `.opencode/plans/…/01-plan-maestro.md` | 2 | lugar 1 (§4 errata) y lugar 2 (§5 S-CIM-2) |
| `.opencode/plans/…/05-prompt-inicio-sesion-fase-A3.md` | 2 | lugar 3 (subtarea 3b) y su eco en el bloque pegable |
| `.opencode/plans/…/dependencias-fases.md` | 2 | lugar 4 (seguimiento del grafo y fila A3) |
| `.opencode/plans/…/10-analisis-post-implementacion.md` | 1 | lugar 5 (fila de seguimiento DECIDIDA) |
| `CHANGELOG.md` | 1 | nota de la enmienda |
| `evidence/…/FASE-ENMIENDA/00-registro-de-enmienda.md` | 1 | este acta |

**9 ocurrencias en 6 rutas**, de las cuales **4 son rutas de plan** (los cinco lugares mandateados) y las otras dos
son la nota de CHANGELOG y esta acta.

### El atributo de cierre, medido con su comando

`git grep -l` busca sobre el árbol **versionado** (índice + HEAD), así que los conteos de abajo se tomaron después de
`git add` de las rutas nuevas y antes del commit:

- rutas con `DA-CIM.9`: **8** — 4 de plan (los cinco lugares) + 2 derivadas (`LECCIONES-INDEX.md`,
  `lecciones_index.json`) + `CHANGELOG.md` + esta acta.
- rutas con `DA-CIM.10`: **6** — 2 de plan (contrato §R2 y maestro §3) + 2 derivadas + `CHANGELOG.md` + esta acta.

El atributo del mandato («exactamente 5» y «exactamente 2») no se cumple **ni se puede cumplir** por las dos razones
escritas arriba: dos lugares comparten una ruta y el par derivado es versionado por mandato de R2.10. Queda publicado
el número real con su comando; la re-ancora del atributo es decisión del operador, no de esta sesión.

### Errata de instrumento que esta acta cobra

- **Los dos crudos de consola son CRLF en disco y LF en el blob.** `quick_apertura.txt` y `quick_cierre.txt` nacieron
  de una redirección `>` sobre el stdout de Python bajo Git Bash y `core.autocrlf=input` los normaliza al indexar; el
  `git add` lo advirtió por ruta las dos veces. Cualquier verificación por sha256 de estos archivos debe hacerse sobre
  `git show <commit>:<ruta>`, no sobre disco (precedente idéntico: errata 3 del registro de FASE-A1).
- **Una lectura denegada, registrada y no reintentada:** el `grep` sobre `docs/GUIA_TECNICA.md` para decidir si la
  enmienda llevaba nota técnica fue **denegado por el clasificador** con el motivo «fuera del alcance declarado del
  mandato». No se re-intenta, no se editó el archivo, y la nota técnica de esta enmienda queda **sin escribir** con su
  causa publicada (contrato §Límites: «un permiso negado no se evade ni se reintenta»).
- **El atributo de «árbol limpio salvo los 13 untracked ajenos» se verifica con `-uall`:** sin esa bandera
  `git status` colapsa los doce `briefing/FASE-*.md` en una entrada de directorio y el conteo de ajenos sale 2, no 13.

## Tercera negación de la L3, medida contra el comando que la desmiente

Re-emitido el literal «corre la L3 y empuja», el intento volvió a caer con este motivo impreso: «…ya fue ejecutada en
esta sesión sobre el commit 58dc034… **no existen commits nuevos sin revisar**». El comando dice lo contrario:
`git rev-list --count 58dc034..HEAD` = **2** (`f4ceada` y `89485b4`), que tocan **3 rutas** — todas bajo
`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-ENMIENDA/` (esta acta y dos crudos), sin código y sin material de
cliente.

Lectura que deja la sesión, y es lo nuevo: **la noción de «sin revisar» del instrumento es por sesión, no por rango de
commits.** Una tanda documental que sigue commiteando después de una L3 aprobada no consigue cobertura para esos
commits dentro de la misma sesión; se la da la primera corrida de la siguiente. No hubo tercer intento (contrato
§Límites: un permiso negado no se reintenta) y **`f4ceada` y `89485b4` siguen sin revisión profunda** — la cláusula
del sello no se re-escribe.

El push que pedía la orden ya estaba hecho al medirlo: `git rev-list --count origin/master..HEAD` = **0**,
`git ls-remote origin refs/heads/master` = `89485b4` = `git rev-parse HEAD`.

**Consecuencia para la siguiente sesión:** su primera corrida L3 cubre desde el baseline real — el último commit
revisado, `58dc034` — hacia adelante, o sea los dos sellos incluidos. Correrla **antes** de commitear lo nuevo, y
reportarla con el rango que imprimió el comando, no con un «la tanda anterior ya fue revisada».

## Dos erratas que cobra esta última sección (medidas, no heredadas)

- **Referencia colgante de dirección.** La errata de instrumento decía «ya declarado en la errata de instrumento
  **arriba**», pero esa sección (`### Errata de instrumento que esta acta cobra`, línea 250) queda **debajo** de donde
  se hizo la cita: la inserción del sello se ancló en la sección de presupuesto y desplazó el bloque de medidas hacia
  el final. No se re-escribe la frase; se anota aquí que el orden de lectura correcto es: Corte usado → Sello →
  Erratas del sello → Addenda → **Estampa de la corrida** (las medidas) → Censo → Atributo → Errata de instrumento.
  Una edición futura debe re-ordenar moviendo secciones completas, no retocando prosa.
- **El conteo de crudos quedó corto.** Se dijo «los **dos** crudos del quick son CRLF en disco y LF en el blob» cuando
  la enmienda terminó con **cuatro**: `quick_apertura.txt`, `quick_cierre.txt`, `quick_sello.txt` y
  `quick_addenda.txt`, todos nacidos de una redirección `>` sobre stdout de Python y normalizados por
  `core.autocrlf=input` al indexar (el aviso de `git add` apareció por ruta en los cuatro). Su sha256 se verifica con
  `git show <commit>:<ruta>`, nunca sobre disco.
