# TAT — Puesta al día del paquete documental REFACTOR-WHATSAPP-ENTREGA-2026-09-18 + VERIFICADOR-ESCRITURA-QMIND-2026-09-20

Sesión documental del 2026-10-06. Repo `C:/Users/Jhond/Github/iah-cli`, HEAD de apertura `5398a3a`,
árbol limpio (`git status --porcelain` sin salida) y paridad `0 0` contra `origin/master`
(`git rev-list --left-right --count origin/master...HEAD`).

**Estados de la columna `Estado`:** `CERRADA` o `DIFERIDA-CON-DUENO`. El tercer estado admisible del
mandato no debe aparecer en este archivo; por eso su contador se corre como campo que decide.

Unidades de medida declaradas: coincidencias de un literal (`grep -c` / `grep -cF`), código de salida de
los verificadores y número de ficheros de `git diff --stat`. Ninguna cifra de esta tabla sale de memoria:
todas las imprimen los comandos que se citan. Los crudos viven en este mismo expediente
(`01-quick-antes-crudo.txt`, `02-quick-despues-crudo.txt`, `03-censo-etiqueta-1515.txt`,
`04-git-diff-stat.txt`).

## Tabla

| ID | Documento | Categoría | Estado | Evidencia (comando + síntoma medido) |
|---|---|---|---|---|
| U1-1 | `05-prompt-inicio-sesion-fase-C.md` | U1 | CERRADA | `grep -c "log_phase_completion.py --fase FASE-C"`: HEAD 1 sin `--fecha` → disco 1 con `--fecha "$FECHA_CIERRE"`; nota añadida bajo el bloque. Base de la obligatoriedad: `log_phase_completion.py::parse_args` (`--fecha` con `required=True` y `type=fecha_iso_estricta`); el script no se ejecutó, lo prohíbe el mandato |
| U1-2 | `05-prompt-inicio-sesion-fase-D.md` | U1 | CERRADA | mismo control: HEAD 1 sin bandera → disco 1 con `--fecha "$FECHA_CIERRE"` (`grep -c -- "--fecha"`: 0 → 2, comando y nota) |
| U1-3 | `05-prompt-inicio-sesion-fase-E.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2 |
| U1-4 | `05-prompt-inicio-sesion-fase-F.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2 |
| U1-5 | `05-prompt-inicio-sesion-fase-H.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2 |
| U1-6 | `05-prompt-inicio-sesion-fase-E2E.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2 |
| U1-7 | `05-prompt-inicio-sesion-fase-VERIFY.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2 |
| U1-8 | `05-prompt-inicio-sesion-fase-RELEASE.md` | U1 | CERRADA | `grep -c -- "--fecha"`: HEAD 0 → disco 2; el comando quedó `--fecha "$FECHA_CIERRE" ... --release "$VERSION_AUTORIZADA"` |
| U1-9 | `VERIFICADOR-ESCRITURA-QMIND-2026-09-20/05-prompt-inicio-sesion.md` | U1 | CERRADA | tarea 4: el cierre dice ahora `log_phase_completion.py` con `--fase`, `--desc` y `--fecha`; en HEAD esas dos últimas banderas no aparecían en esa fila |
| U1-10 | control sobre los 4 prompts de fases cerradas | U1 | CERRADA | `grep -rn "log_phase_completion.py --fase"` sobre los dos planes y filtrado por `grep -v -- "--fecha"`: quedan 4 coincidencias, todas en `fase-A`, `fase-G`, `fase-0` y `fase-B`. Son historia y el mandato prohibe editarlas; ningún comando de fase abierta queda sin `--fecha` |
| U2-1 | `05-prompt-inicio-sesion-fase-C.md` | U2 | CERRADA | `grep -c "DOMAIN_PRIMER"`: HEAD 0 → disco 1; cláusula condicional `grep -c "solo si el mandato"`: HEAD 0 → disco 1 |
| U2-2 | `05-prompt-inicio-sesion-fase-D.md` | U2 | CERRADA | `grep -c "DOMAIN_PRIMER"`: HEAD 0 → disco 1; condicional 0 → 1 |
| U2-3 | `05-prompt-inicio-sesion-fase-E.md` | U2 | CERRADA | la mención existía (HEAD 1 → disco 1) pero era incondicional; `grep -c "solo si el mandato"`: 0 → 1. Se referencia `04-contrato-ejecucion.md` paso 4 como fuente canónica en vez de re-transcribirla |
| U2-4 | `05-prompt-inicio-sesion-fase-F.md` | U2 | CERRADA | igual: condicional 0 → 1 sobre la frase ya existente |
| U2-5 | `05-prompt-inicio-sesion-fase-H.md` | U2 | CERRADA | igual: condicional 0 → 1 |
| U2-6 | `05-prompt-inicio-sesion-fase-RELEASE.md` | U2 | CERRADA | `grep -c "es operación de cada cierre de fase de"`: HEAD 0 → disco 1. Tarea 2 y la casilla del checklist ahora dicen que RELEASE **verifica** con `doctor.py --context`/`--status` y que **regenerar** corresponde a C, D, E, F y H; la regeneración en RELEASE queda sujeta a instrucción expresa |
| U3-1 | `05-prompt-inicio-sesion-fase-C.md` | U3 | CERRADA | bloque «Derivados vencidos» con los cuatro fixers; `grep -c "\[8/13\]"` = 1. Las etiquetas y sus nombres de check se leyeron en la corrida del quick (`02-quick-despues-crudo.txt`) |
| U3-2 | `05-prompt-inicio-sesion-fase-D.md` | U3 | CERRADA | igual: `grep -c "\[8/13\]"` = 1 |
| U3-3 | `05-prompt-inicio-sesion-fase-E.md` | U3 | CERRADA | igual |
| U3-4 | `05-prompt-inicio-sesion-fase-F.md` | U3 | CERRADA | igual |
| U3-5 | `05-prompt-inicio-sesion-fase-H.md` | U3 | CERRADA | igual |
| U3-6 | `05-prompt-inicio-sesion-fase-E2E.md` | U3 | CERRADA | igual |
| U3-7 | `05-prompt-inicio-sesion-fase-VERIFY.md` | U3 | CERRADA | igual |
| U3-8 | `05-prompt-inicio-sesion-fase-RELEASE.md` | U3 | CERRADA | igual, redactado para su corrida sin `--quick` («re-correr la validación») |
| U3-9 | `04-contrato-ejecucion.md` paso 6 | U3 | CERRADA | se distingue **absorber** un rojo nuevo (prohibido, regla vigente) de **regenerar el derivado que la propia edición venció** (obligatorio), y el `--update-baseline` queda declarado acto visible de quien documenta. Evita la contradicción con el paso 6 de HEAD, que un fase leía como veto a los cuatro fixers |
| U3-10 | acto de esta sesión: índice de lecciones | U3 | CERRADA | tras la última edición, `build_lesson_index.py --check` dio EXIT 1 con `[FAIL] Índice de lecciones vencido: LECCIONES-INDEX.md, lecciones_index.json`; se regeneró con su writer. La primera regeneración publicó una fila nueva `D-F5` en «citados sin definición» (56 → 57) causada por un token que esta sesión introdujo: se retiró el token, se volvió a correr el writer (EXIT 0) y el par quedó idéntico a HEAD, fuera de `git diff --stat`. `--check` final: `[OK] Índice de lecciones fresco (344 IDs)`, EXIT 0 |
| U4-1 | `05-prompt-inicio-sesion-fase-RELEASE.md` (versión) | U4 | CERRADA | `grep -nE "version..release_date" VERSION.yaml` publica `version: "4.78.0"` con `release_date: "2026-09-25"`; `grep -nE "^## \[" CHANGELOG.md` da como encabezado 2º `## [4.78.0] - Gobernanza, costura, pertinencia y carga medida — 2026-09-25`, release de `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`. El prompt ahora remite la versión al mandato |
| U4-2 | `05-prompt-inicio-sesion-fase-RELEASE.md` (comando) | U4 | CERRADA | `--release 4.78.0` → `--release "$VERSION_AUTORIZADA"`; `grep -c '\-\-release "\$VERSION_AUTORIZADA"'` = 1 |
| U4-3 | `01-plan-maestro.md` (padre) | U4 | CERRADA | solo anotación datada, como restringe el alcance: la fila «Objetivo de release propuesto: 4.78.0» se conserva y se le añade el ⟦2026-10-06⟧ de que el número está ocupado y la versión la decide el mandato de RELEASE |
| U4-4 | `10-analisis-post-implementacion.md` | U4 | CERRADA | misma forma: la afirmación de la concepción no se reescribe; anotación datada con el comando que mide `VERSION.yaml` |
| U4-5 | `04-contrato-ejecucion.md` paso 3 | U4 | CERRADA | «bajo versión vigente» → «bajo el encabezado `## [Sin publicar]`», con la prueba de la forma vigente del archivo y la nota de que fechar una fase intermedia inventaría una release |
| U4-6 | `05-prompt-inicio-sesion-fase-E.md` | U4 | CERRADA | `grep -c "versión vigente"`: HEAD 1 → disco 0; la nueva redirección apunta al paso 3 del contrato |
| U4-7 | `05-prompt-inicio-sesion-fase-F.md` | U4 | CERRADA | igual: 1 → 0 |
| U4-8 | `05-prompt-inicio-sesion-fase-H.md` | U4 | CERRADA | igual: 1 → 0 |
| U4-9 | `05-prompt-inicio-sesion-fase-E2E.md` | U4 | CERRADA | igual: 1 → 0 |
| U4-10 | `05-prompt-inicio-sesion-fase-VERIFY.md` | U4 | CERRADA | igual: 1 → 0 |
| U4-11 | `05-prompt-inicio-sesion-fase-RELEASE.md` (Version Sync) | U4 | CERRADA | la cláusula «resolver el rojo preexistente registrado en el maestro §7» se re-ancló a re-medición del check `[3/13]` con nota de que ese rojo se cerró por re-medición el 2026-09-19 (lo declaran maestro §7, `dependencias-fases.md` y `README.md`). La casilla del checklist que heredaba el rojo también se re-ancló |
| U4-12 | `05-prompt-inicio-sesion-fase-RELEASE.md` (CHANGELOG) | U4 | CERRADA | la consolidación dice que las subsecciones de fase están bajo `## [Sin publicar]` y que el encabezado de versión se da aquí, alineado con el paso 3 del contrato |
| U5-1 | `05-prompt-inicio-sesion-fase-RELEASE.md` | U5 | CERRADA | `03-censo-etiqueta-1515.txt`: coincidencias de `15/15` **fuera de anotación** pasan de 1 (HEAD) a 0 (disco); la etiqueta operativa del prompt es `[17/18]` con la nota del `[18/18]`. Medido con `grep -nE "1[78]/18" scripts/run_all_validations.py` |
| U5-2 | `dependencias-fases.md` | U5 | CERRADA | censo: 1 → 0 fuera de anotación; la fila QMind/write-back queda con `[17/18]` y la nota del hermano |
| U5-3 | `10-analisis-post-implementacion.md` | U5 | CERRADA | censo: 1 → 0 fuera de anotación; la fila abierta con dueño lleva `[17/18]` |
| U5-4 | `VERIFICADOR-ESCRITURA-QMIND-2026-09-20/README.md` | U5 | CERRADA | censo: 3 → 1. Se re-anclaron las dos afirmaciones vivas (hecho 1 y AC6-aceptación); la que queda es la cita en pasado del bloque de 2026-09-24 («la fila AC6 **exigía** como prueba…»), registro histórico que la regla manda no reescribir, y se le añadió la anotación cruzada que lo explica |
| U5-5 | `VERIFICADOR-ESCRITURA-QMIND-2026-09-20/01-plan-maestro.md` | U5 | CERRADA | censo: 4 → 0. Encabezado (anotación nueva junto a la de 2026-09-24, que se conserva intacta), P1, AC2 y AC6 re-anclados |
| U5-6 | `VERIFICADOR-ESCRITURA-QMIND-2026-09-20/05-prompt-inicio-sesion.md` | U5 | CERRADA | censo: 1 → 0; AC6-aceptación con `[17/18]` y nota |
| U5-7 | `09-documentacion-post-proyecto.md` | U5 | DIFERIDA-CON-DUENO | el archivo **no está en la lista de alcance de edición** de esta sesión y su mención (`grep -c`: 1 → 1) es registro fechado de la medición de FASE-G del 2026-09-20, que la regla de U5 manda no reescribir. **Dueño:** el cierre documental de FASE-RELEASE de este plan, que es quien consolida `09`. **Disparador:** cuando esa fase reescriba su sección de QMind, añada al registro la anotación datada del re-anclaje `[17/18]` / `[18/18]`; no se cierra por omisión |
| U5-8 | recaps `7/7` y `11/11` del plan padre | U5 | CERRADA | no se tocaron: `grep -rn -e "7/7" -e "11/11"` sobre los dos planes los encuentra solo en filas datadas de los cierres de A, G y 0 (2026-09-19 y 2026-09-20), en `06-checklist-implementacion.md` y `09-documentacion-post-proyecto.md` (fuera de alcance) y en los prompts de fases cerradas. Ninguna se lee como instrucción; los denominadores vivos que una fase copiaría son hook 8 checks y quick 13, y ambos se citan por el comando que los imprime |
| U5-9 | `README.md` del plan padre | U5 | CERRADA | el alcance condicionaba este sitio a «si el grep muestra algo vencido que una fase copiaría»: `grep -n -e "15/15" -e "11/11"` sobre el archivo no da coincidencias, y sus `9/10`, `10/10` y `7/7` están dentro de filas fechadas. Su bloque de arranque ya remite los números a la corrida, así que no se edita |
| U6-1 | `01-plan-maestro.md` (mini-plan), AC2 | U6 | CERRADA | la verificación por contenido declara reutilizado el **contrato D2** vigente: primera vía `metadata.fileSha256`/`fileSize` y descarga como verificación de la promesa, `NO-EVALUABLE` sin observación. Medido en `scripts/verify_qmind_context_freshness.py` (su docstring y la lectura de `metadata` en el lazo de fuentes) |
| U6-2 | `01-plan-maestro.md` (mini-plan), AC4 | U6 | CERRADA | misma cláusula, remitiendo al contrato de AC2 para no abrir un segundo dialecto |
| U6-3 | `05-prompt-inicio-sesion.md` (mini-plan), tarea 2 | U6 | CERRADA | «el dialecto de frescura ya existe y se reutiliza, no se reinventa», con los cuatro estados del D2 (`metadata` primero, descarga verifica la promesa, `NO-EVALUABLE`, `PROMESA-ROTA`), medidos en el hermano |
| U6-4 | `01-plan-maestro.md` (mini-plan), §3 no-alcance | U6 | CERRADA | se declara que el mismo «verde por ausencia» que AC3 caza en `[17/18]` vive en `[18/18]`, con dueño (operador / siguiente mandato sobre los verificadores QMind) y disparador (una AC nueva). Medido: `run_all_validations.py::_check_context_freshness()` invoca el script sin el modo estricto, y `verify_qmind_context_freshness.py` degrada a `WARN` + exit 0 |
| U6-5 | `README.md` y `01-plan-maestro.md` (mini-plan), dato para no re-descubrir | U6 | CERRADA | re-medido el 2026-10-06 en el propio script: `validate_qmind_writeback.py::main()` solo expone `--nb`, `--strict` y `--upload` (los `--title`/`--file` del archivo son los que `upload_source()` pasa al CLI `qmind`), `is_ingested()` decide por título, y `_check_qmind_writeback()` lo invoca sin `--strict`. Se publicó la etiqueta vigente `[17/18]` |
| U6-6 | `05-prompt-inicio-sesion.md` (mini-plan), cierre | U6 | CERRADA | véase U1-9 y U1-10: `--fecha` incorporada a la regla de cierre sin tocar el `--release` (que sigue excluido) |
| U6-7 | disparador y §5 del mini-plan | U6 | CERRADA | no se tocaron, medido por hunks: `git diff --unified=0` sobre el mini-plan da hunks en HEAD 6, 13, 25, 27, 29 y 41 (maestro), 7, 26, 45 y 47 (README) y 10, 54 y 66 (prompt). El §5 del maestro vive en HEAD 63-72 y el párrafo «Disparador y calendario» del README en HEAD 12-16: ningún hunk los cubre |

## Verificación posterior a la última edición

| Comando | Salida impresa |
|---|---|
| `run_all_validations.py --quick` | `TOTAL: 13/13 validations passed`, `STATUS: ALL VALIDATIONS PASSED`, `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`, EXIT 0 (crudo en `02-quick-despues-crudo.txt`) |
| `build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (344 IDs)`, `[fechas] nombre=333 commit=11 sin_fuente=0`, EXIT 0 |
| `validate_plan_citations.py` | `[OK] Plan citas: 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos en el inventario)`, EXIT 0 |
| `validate_opencode_refs.py` | `[PASS] OpenCode References: todas las referencias existen`, EXIT 0 |
| `git diff --stat` | 15 archivos `.md` de los dos planes, 167 inserciones y 43 borrados (crudo en `04-git-diff-stat.txt`); el resto del árbol sin cambios |

`[7/13] Prompts No Release: No --release flag in intermediate prompts` sigue verde: no se añadió `--release`
a ninguna fase intermedia; el único que lo lleva es el de RELEASE y ahora con `$VERSION_AUTORIZADA`.

## Auto-revisión del diff (C7)

Contradicciones buscadas y resueltas al releer el paquete:

- **CHANGELOG**: cinco prompts decían «bajo versión vigente» y el contrato paso 3 goberna la forma. Los
  prompts ahora remiten al contrato, y el contrato quedó re-anclado a `## [Sin publicar]`. RELEASE, que
  consolidaba sin decir dónde caían las subsecciones, ahora declara que están bajo ese encabezado y que la
  versión se le da en esa fase.
- **`[15/15]`**: cada re-anclaje deja el literal viejo solo dentro de un ⟦ ⟧ datado. El censo de la columna
  «fuera de anotación» (`03-censo-etiqueta-1515.txt`) es el instrumento; sin él, un `grep -c 15/15` contaría
  las propias notas como si fueran afirmaciones vivas.
- **DOMAIN_PRIMER**: C y D no lo mencionaban; E, F y H lo mandaban regenerar sin condición; RELEASE lo
  regeneraba además de verificar. Los cinco quedan con la cláusula condicional y RELEASE con la pata de
  verificación, todos referidos al paso 4 del contrato como fuente única.
- **Versión**: maestro, `10-analisis` y RELEASE hablaban de 4.78.0 como objetivo. Queda la cifra histórica
  con su anotación y el valor pasa a `$VERSION_AUTORIZADA`; ningún documento nuevo fija un número.
- **Token propio**: la primera versión de las notas cite una deuda por su etiqueta, y el escritor del índice
  la publicó como «citado sin definición» (56 → 57). Retirada y regenerado el par, el índice volvió a casar
  con HEAD. Se declara porque fue esta sesión la que introdujo el ruido.

## Corte alcanzado

**Listo para revisión** — cuarto de los cinco cortes. Implementación documental terminada, verificación
terminada y cierre documental de este expediente publicados sin commit; no se hizo commit, push, tag, ni
registro de fase, y no se ejecutó `log_phase_completion.py` (el mandato lo prohíbe y esta sesión no es una
fase). El `git commit` queda como acción posterior, separada y opcional, sujeta a autorización explícita.
