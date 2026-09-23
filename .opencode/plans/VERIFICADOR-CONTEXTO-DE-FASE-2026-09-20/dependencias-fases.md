# Dependencias y bloqueantes — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

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
| 3 · [FASE-C](05-prompt-inicio-sesion-fase-C.md) | `triage_lesson_relevance.py`: capa de pertinencia **aditiva** sobre `lecciones_index.json`, nunca filtro | ALTA: es la mitad que el verificador de capitalización declara fuera de alcance | PENDIENTE |
| 4 · [FASE-D](05-prompt-inicio-sesion-fase-D.md) | `build_phase_briefing.py`: pack derivado por fase, proveniencia con sha, negativa a truncar y **delta de carga de lectura medido** (AC19–AC23) | MEDIA: es determinista, pero gobierna lo que todas las sesiones futuras van a leer | PENDIENTE |
| 5 · [FASE-RELEASE](05-prompt-inicio-sesion-fase-RELEASE.md) | Cierre documental, sync, write-back y archivado en orden R2.5/R2.10 | MEDIA | PENDIENTE |

## Qué debe heredar cada fase

| Fase | Hereda de | Pieza concreta |
|---|---|---|
| A | — | **Estado medido del árbol, no asumido**: al publicarse la auditoría (`2c9d0c1`, 2026-09-20, paridad 0/0 con `origin/master` verificada con `git ls-remote`) el árbol está **limpio** y el índice viene regenerado y fresco; A re-mide HEAD/status al abrir porque la pareja del índice se comparte con las fases vivas de `REFACTOR-WHATSAPP`. Las cuatro aserciones vencidas A1–A4 medidas y copiadas en el maestro §1 (con **A3 rectificada: el write-back imprime `[15/15]`**), la medición A7 de carga de lectura re-medida (263.973 bytes) y la población A8 que obliga a la regla de clases de AC1 |
| A — **notas de ejecución (2026-09-21)** | lo que A encontró al medir de verdad: HEAD ya no era `2c9d0c1` sino `2deddee` (11 commits de `EVALUACION-JEV` encima) con paridad 0/0 conservada y árbol limpio; **A1–A4 siguen vencidas y A7 no se movió** (263.973 re-medidos); la población A8 se reprodujo exacta (22 + 17 líneas + 2). Dos hallazgos nuevos de la fase, con dueño: **(N1)** el disparador de **D1** era circular — «verificador verde» solo se cumple *después* de corregir `.agents/`, así que se reformuló a «verificador operativo con mutation check + decisión escrita del operador»; **(N2)** la propia prueba de AC1 **añadió 4 pins del denominador 11 en `tests/`** (familia iii de AC2), declarados en `baseline-pre-post.md` en vez de limar la aserción |
| B — **reutilizado, no reinventado** | A | `coverage_basis` con el mismo esqueleto de AC2 (`archivos_escaneados`, `poblacion`, `excluidos_por_directorio`, `limites`, `comando`, `medido_el`) y el tri-estado de AC3, que aquí se llama `provider_status` con sus `motivo_clase`. **Una adicción propia declarada**: el `status` de la puerta es binario en el escaneo (`SIN-HALLAZGOS`/`HALLAZGOS`) porque su tercer y cuarto camino (`AUSENTE`, `LECTOR-FALLIDO`) viven en la resolución del proveedor, no en el conteo — y ahí el tercero se llama `estado_lector`, no se colapsa con `NO-CONFIGURADO`. |
| B — **notas de ejecución (2026-09-21)** | lo que B encontró al medir | HEAD ya no era `e3c4573` sino `74d8ff5` (dos commits de barrido documental de FASE-A encima); `find . -name "*.jsonl"` sigue en **0** (D-V2.1 reproducida por quinta vez, métrica retirada y unidad contable declarada); **0** imports del SDK en el árbol y el SDK **no instalado** en el venv del producto (sí en `tmp_test/venv-jev-sdk`, excluido y publicado); la poblacion que `git grep` ve (678 `.py`) y la que ve el árbol de trabajo (692 en el árbol de trabajo; 690 en el primer escaneo de la fase) **difieren** y las dos se publican |
| C | A y B | La costura de B como única puerta al proveedor; los estados `AUSENTE`/`VENCIDO` de A aplicados al índice de lecciones. **Enmienda prospectiva aceptada el 2026-09-23 (orden de calidad §4.C, solo para CONTEXTO/C):** la pregunta binaria se formula como `choice` de dos opciones con `confidence` **independiente** (no con `noul`: su probabilidad de sí **no** es confianza — ver `decision_client.py`, que prohíbe `confidence` en `noul`); **AC11 elige la ruta (b)** (leer `lecciones_index.json` tras ejecutar C **ella misma** la comprobación de frescura, sin confiar en que otro gate lo regeneró), con `AUSENTE` / `VENCIDO` / `LECTOR-FALLIDO` como tres causas distinguibles; y las propuestas del proveedor falso **no** entran a §2 del `00-` en automático: exigen **revisión humana explícita con aceptación o rechazo registrado**. Detalle en `05-prompt-inicio-sesion-fase-C.md` y en el maestro §4 |
| D | A, B y C | Los tres estados y `coverage_basis`; el informe de candidatos de C, que el pack exhibe como sección propia; el **número de aceptabilidad** de C, que es el disparador de la deuda D6 |
| RELEASE | A, B, C y D | Los cuatro `coverage.json`/`informe.json`, los pares pre/post de las cuatro fases, el delta de carga medido y el registro de deuda §6 del maestro |

## Conflictos de archivo

| Archivo / ruta | Lo toca | Riesgo y regla |
|---|---|---|
| `.opencode/LECCIONES-INDEX.md`, `.opencode/lecciones_index.json` | **Este plan y las fases vivas de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`** | **Conflicto real, ya latente.** `[6/7]` del hook bloquea el commit con el índice vencido contra el árbol, así que **ambos planes lo regeneran**. Regla: regenerar en el mismo commit, nunca `--check` contra un índice ajeno; si aparece un diff que no proviene de tu edición, re-generar y volver a medir, no `git checkout` |
| `…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/` | Solo FASE-D, y solo como **generado** | Vive dentro del plan a propósito. En `.agents/workflows/` alteraría los contadores de skills (`validate_agent_ecosystem.py`, `sync_data.py`, `doctor.py` usan `glob("*.md")`) y exigiría seguimiento en su `README.md` — y AC17 prohíbe escribir en `.agents/` |
| `scripts/run_all_validations.py` | **Este plan: solo lectura** (AC16). **Pero no está libre**: `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` lo declara dentro de su alcance («su connection en `scripts/run_all_validations.py`») | Corregido el 2026-09-20: la cifra de 11 checks **no la pinea el prompt de FASE-C** de `REFACTOR-WHATSAPP` sino cuatro documentos suyos (arranque de FASE-B en su `README.md`, `06-`, `09-`, `10-`). Y ese tercer plan en vuelo puede cambiar **la etiqueta y la invocación** del write-back `[15/15]` — que es justamente la fuente de verdad de A3 y del fix de AC1. Regla: AC16 (delta 0) obliga a re-medir aquí; **D10** obliga a re-leer la interfaz del write-back antes del `--upload` de este RELEASE |
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
  `REFACTOR-WHATSAPP`; la cifra de 11 checks que ese plan pinea en cuatro de sus documentos; y
  `scripts/run_all_validations.py` + `scripts/validate_qmind_writeback.py`, que
  `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara **dentro de su alcance**. Este plan no los escribe;
  los lee como fuente de verdad, y de ahí salen AC16 (delta 0) y **D10**.
- **No hay FASE-VERIFY** y por tanto ningún AC puede certificarse contra output E2E. Techo
  alcanzable: `VERIFICADO OFFLINE` con mutation check, o `NO-EJERCITADO`.

## Deuda registrada (dueño y disparador, no silencio)

| # | Deuda | Dueño | Disparador |
|---|---|---|---|
| D1 | Corregir o eliminar las aserciones A1–A4 en `.agents/` | Este plan, FASE-RELEASE, con instrucción literal del operador | **Disparador reformulado el 2026-09-21 (FASE-A):** era circular («verificador verde» no puede darse antes de la corrección que el verificador pide); pasa a *verificador operativo con su mutation check en disco* — cumplido el 2026-09-21 — **y** decisión escrita del operador sobre la forma de la corrección |
| D2 | Promover `validate_governance_numbers.py` a check del `--quick` con renumeración (11 → 12) | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP`: ya no hay fases que pineen «11 checks» |
| D3 | Rebanar el workflow canónico por fase (bajar la carga de lectura de A7: **263.973 bytes ≈ 65.993 tokens** re-medidos el 2026-09-20 sobre la sesión de FASE-B del plan en vuelo; los 254.010 de la concepción vencieron ese mismo día) | Plan propio posterior | Mismo disparador. **No** es FASE-D: el pack unifica lecturas declaradas, no recorta la fuente |
| D4 | Verificador de la resta del par pre/post (R2.7 sigue sin instrumento mecánico) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Ya asignado antes que este plan; no se reasigna |
| D5 | Instrumento que compruebe que `evidence/FASE-X/` contiene el par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda de proceso | Mismo tramo que D4 |
| **D6** | **Lint de contradicciones semánticas** (`validate_plan_semantics.py`): prompts de fase contra estado real del plan, con falsos positivos medidos contra los archivados | Plan propio posterior; **entra en este mismo directorio** si el disparador se cumple mientras está vigente | **Condicionado al resultado de FASE-C**: que el triaje entregue candidatos que el Paso 0 no ancló, con su aceptabilidad medida publicada en el informe. Si FASE-C sale inaceptable, **no se activa**: no se apila un segundo consumidor sobre una base que no funcionó |
| **D7** | **Activar el proveedor de decisiones ya habilitado** (Jev) como segundo proveedor detrás de `decision_client.py`; correr la comparación de proveedores y restituir «elegir midiendo» como AC | Plan propio posterior | Acceso existente desde 2026-09-20, pospuesto por decisión del operador. El consumidor natural es D6, el único trabajo genuinamente semántico del lote |
| D8 | Re-ejecutar la consulta Q7 de QMind. **Premisa vencida: el 2026-09-20 el CLI sí estaba disponible y la consulta se corrió en la auditoría de la concepción** (cuatro `retrieve`, resultados capitalizados como L-V2.1, L-V2.2 y D-V2.1). **Y su forma publicada es incorrecta**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; hay que pasar el ID `01a04d98-b7bd-778c-8441-26fdc7e35f45` | Este plan, sesión previa a FASE-RELEASE (re-corrida, no primera vez) | Que el notebook haya cambiado desde la auditoría, o que se quiera verificar el comando corregido con las citas que ya devolvió |
| D9 | Write-back de `10-analisis-post-implementacion.md` a QMind | Este plan, FASE-RELEASE | Orden R2.5/R2.10: `--upload` **antes** del `git mv`, y segunda regeneración del índice después |
| **D10** | **Re-leer la interfaz del write-back antes de correr el cierre.** `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` (commiteado, PENDIENTE, con disparador anterior al RELEASE de `REFACTOR-WHATSAPP`) piensa añadir `--title`/`--file` a `validate_qmind_writeback.py`, verificar contenido en vez de título, quitar la degradación a PASS y tocar su conexión en `run_all_validations.py` | Este plan, FASE-RELEASE | Al llegar el cierre: `validate_qmind_writeback.py --help` contra el árbol vigente y re-escribir el orden de `04-contrato-ejecucion.md` si la firma cambió. **No bloquea ninguna fase de implementación** |

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

**Qué NO cierra esta aceptación.** El **rojo contractual del plan sigue vivo y no se convierte en
PASS**: `validate_governance_numbers.py` sale `exit 1` con A1–A4 presentes porque `.agents/` no se
edita (AC17) — eso es **D1/S1**, con instrucción literal del operador, y la remediación del bloque A
no lo tocó. Y siguen abiertas, con dueño, **sin** convertirse en bloqueantes artificiales de una
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
