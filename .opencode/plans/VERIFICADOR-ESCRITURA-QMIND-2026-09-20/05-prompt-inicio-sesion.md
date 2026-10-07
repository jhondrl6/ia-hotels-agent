# FASE-UNICA — Verificador de escritura y frescura del write-back a QMind

**Estado:** PENDIENTE. ⟦**EJECUTADA el 2026-10-07** — momento A (entrega offline). Lo que esta sesión podía
cerrar está cerrado y medido; lo remoto quedó `PENDIENTE-AUTORIZACION` con dueño y disparador, no omitido.
Dictamen AC por AC, decisiones en voz alta y deuda: `10-analisis-post-implementacion.md` de este plan.⟧
⟦Desde el 2026-09-24 su aceptación está dividida en dos momentos (maestro §6):
**entrega offline**, que es lo que esta sesión puede cerrar, y **aceptación remota**, que no⟧.
**Dependencia inmediata:** ninguna técnica. **Disparador:** sesión propia **antes de
FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**; si ese RELEASE llega primero, aplicar el §5 del
maestro y dejar AC2–AC4 abiertos con dueño.
**AC6 se desdobla (⟦orden de calidad §4.C, fila `ESCRITURA-QMIND`⟧):** **AC6-entrega** — dejar el writer
capaz de publicar con `--title` y actualizar el prompt del padre — **sí cierra en esta fase**;
**AC6-aceptación** — `[17/18]` verde sobre el padre tras su ingesta de cierre ⟦re-anclado el 2026-10-06; se
escribió `[15/15]`, la etiqueta del check cuando el modo completo llegaba a 15⟧ — **no puede cerrar aquí por
construcción**, porque el evento que la produce es posterior a este disparador. Se hereda al momento B de
§6 con dueño y disparador, y esa pendencia **no** convierte la fase en incompleta.
**Complejidad técnica:** MEDIA: un writer, un verificador conectado al modo completo y tests con mutación.
**Scope R3:** 4 tareas, 0 comandos largos externos. **No ejecuta `v4complete` ni repara código de producto.**

## Contexto e inicio

Lee `01-plan-maestro.md` (premisas P1–P6, AC1–AC6, alcance), `00-lecciones-capitalizadas.md` (cuatro filas
capitalizadas y cinco descartes), `04-contrato-ejecucion.md` y `06-checklist-implementacion.md` del plan
padre `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (su prompt de RELEASE es el consumidor de AC6), y el workflow
canónico `.agents/workflows/phased_project_executor.md` en las reglas R2.2 (citar símbolos, no líneas),
R2.8 (rojo por mutación) y R2.10 (orden write-back → índice → `git mv`).

**Re-medición del arranque, separada por momento** (⟦orden §4.C: «resolver consulta/ingesta real frente a
prohibición de red»⟧). La versión anterior mandaba re-medir «el estado real del notebook con
`fetch_source_titles()`» en el arranque de una sesión a la que sus propias Reglas prohíben la red: dos
instrucciones ejecutables contrapuestas, y la de red ganaba por estar escrita primero.

| Re-medir al abrir, **sin red** | Cómo |
|---|---|
| HEAD y árbol | `git rev-parse --short HEAD`, `git status --porcelain` |
| Quick y sus verificadores | `run_all_validations.py --quick`, `validate_plan_citations.py`, `build_lesson_index.py --check` |
| Firma real del writer | `scripts/validate_qmind_writeback.py --help` y lectura de su `main()`: hoy acepta `--nb`, `--strict` y `--upload`; **no** `--title` ni `--file` (vuelto a medir el 2026-09-24) |
| Cómo degrada el check | Lectura de `_check_qmind_writeback()` en `run_all_validations.py`: invoca sin `--strict`, y el `exit 0` por CLI ausente se publica como PASS |
| Que el criterio de contenido sea offline | La comparación es **sha de la instantánea versionada en el repo**, no una llamada al servicio |

| Re-medir **en el momento B**, con autorización literal y presupuesto | Cómo |
|---|---|
| Estado real del notebook (número de fuentes, duplicados de `TRIBUNAL-OFFLINE-2026-09-09`) | `fetch_source_titles()` del propio validador — **es una llamada remota y no corre en esta sesión** |
| Que la ingesta de cierre coincida con la instantánea | descarga byte a byte + sha256 |

El «49 fuentes y dos de `TRIBUNAL-OFFLINE-2026-09-09`» es **antecedente fechado del 2026-09-20**, no el
valor con el que se abre la sesión. Se re-mide en el momento B; y si entonces no se autoriza la lectura, la
premisa se declara **no comprobada**, no se copia el 49.

## Tareas

1. **Writer actualizable (AC1).** Añadir a `scripts/validate_qmind_writeback.py` `--title` y `--file`
   (explícitos, con validación de que `--file` está bajo el repo y de que el título no colisiona en silencio
   con una fuente vigente del mismo plan). `--upload <PLAN>` sigue funcionando igual si no se pasan.
2. **Frescura por contenido (AC2, AC4).** Guardar junto a la subida una **instantánea versionada** en el
   repo y hacer que la verificación compare el contenido ingerido contra esa instantánea —con la prueba de
   sha inverso del saneado, que ya existe en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/`—, y
   exigir que un plan no tenga dos fuentes vigentes sin marca de reemplazo. **El dialecto de frescura ya
   existe y se reutiliza, no se reinventa**: es el contrato D2 del hermano
   `scripts/verify_qmind_context_freshness.py` — `metadata.fileSha256`/`fileSize` que publica el propio
   `source list` como **primera vía**, y la **descarga + sha256** queda como verificación de esa promesa del
   servidor; si no se pudo observar, `NO-EVALUABLE` (nunca `VENCIDO`), y si la descarga desmiente al índice
   eso es `PROMESA-ROTA` y corta rojo. ⟦Alineado el 2026-10-06 en la puesta al día del paquete⟧. Decisión abierta que hay que
   tomar en voz alta: marcar la anterior o borrarla (borrar es irreversible sobre contenido publicado).
3. **Fin del verde por ausencia (AC3).** Que `_check_qmind_writeback()` invoque el script con `--strict` o
   distinga un tercer estado; el resumen no puede contar como PASS una medición que no ocurrió.
4. **Cierre (AC5, AC6-entrega).** Mutaciones que pongan rojo **por el guard** en los tres estados (título
   coincidente con contenido distinto; CLI ausente; dos fuentes vigentes), con árbol restaurado por sha256;
   **tests íntegramente offline, sin excepción de red**: la ingesta de prueba sobre copia saneada **no** es
   una prueba de esta fase sino del momento B (maestro §6), y mantenerla aquí como excepción dejaba una
   instrucción que anulaba la regla. Lo verificable sin red es el **predicado del verificador** contra la
   instantánea versionada, y eso es justo lo que AC2/AC4 prometen. Actualizar el prompt de FASE-RELEASE del
   plan padre para que mande el writer en lugar de depender de que alguien recuerde el título pre-acordado
   — eso **es** AC6-entrega, y cierra en esta fase. ⟦Errata re-medida el 2026-10-07: ese prompt del padre
   cita el método del runner con un símbolo que ya no existe; el vigente es `run_all()`. Corrígelo dentro
   del mismo diff de AC6-entrega. La misma cita vive también en el `10-analisis` del padre (fila L-ENT.14),
   archivo hoy sucio por el cierre de VERIFY: esa errata queda **declarada con dueño** —el RELEASE del
   padre al tocar su 10-analisis— y no es carga de esta fase. Las tres ocurrencias de los documentos de
   este mini-plan se corrigieron el 2026-10-07⟧. Cierre incremental con la regla de siempre:
   `log_phase_completion.py` con `--fase`, `--desc` y `--fecha` y **sin** `--release`, `build_lesson_index.py`
   y su `--check`, quick y `validate_document_integration`. ⟦Puesta al día 2026-10-06: `--fecha` es
   obligatoria (`log_phase_completion.py::parse_args`, con `fecha_iso_estricta` validándola como
   fecha de calendario): es la
   fecha **real** de cierre, variable a sustituir, y si el registro fuera tardío se documenta con `--nota`
   y su motivo; el canon está en `docs/CONTRIBUTING.md` y en el executor §4.5.1⟧.

## Reglas

- No tocar Tribunal (`_compute_verdict`, flags de bloqueo, umbrales), gates, `write/publish/suppress`, hooks,
  `VERSION.yaml`, `AGENTS.md` ni el workflow canónico sin instrucción explícita del operador.
- No subir material del cliente: **cualquier** ingesta, incluida la del momento B, se hace sobre copia
  saneada y versionada, con la prueba de sha inverso. El writer **no sanea** — `do_upload()` ejecuta
  `qmind source upload --file` crudo —, así que el saneado es previo y obligatorio, no posterior.
- **Cero red en esta sesión y en las pruebas de la fase**: no `v4complete`, no scraping, no `retrieve`, no
  `fetch_source_titles()`, no `source upload`. ⟦Orden §4.C⟧: esto **no** se lee como que una prohibición de
  red permita una subida — las operaciones remotas existen, están en el maestro §6 y necesitan autorización
  literal y presupuesto propios, que **esta sesión no concede**.
- No ejecutar `v4complete` ni consumir presupuesto de corridas de otros planes.
- Citaciones en documentos: **símbolos, nunca números de línea** (R2.2; `validate_plan_citations.py` lo
  vuelve rojo).
- Commit, push, tag y write-back se piden por separado y con autorización literal: dejar checkpoint si falta.
  **Los cinco cortes se sostienen sin commit** (proceso común del bloque B de la orden de calidad, alineado
  el 2026-09-24): la autorización pendiente del commit no deja ningún corte «no consumado».

## Presupuesto y checklist

Referencia **60 tool_use hasta el corte que la sesión tenga autorizado** (con el commit de código autorizado,
«hasta el commit»; sin él, «hasta listo para revisión», declarando cuál se usó), medida con el instrumento
del contrato (`evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`). Sin transcript o con acceso
denegado: **FUERA DE SERVICIO (R2.1)**, auto-reporte con **unidad contable declarada** (rutas tocadas,
corridas de baseline, mutaciones) y **sin comparar** con la referencia; no estimar.

- [x] Premisas P1–P6 re-medidas al abrir, **con sus comandos y sin llamadas de red** (tabla de arriba). Medido
      el 2026-10-07: HEAD `21ade6c`, árbol sucio con 36 entradas ajenas, quick 13/13, citas 745/0/0, índice
      fresco 344 IDs, `--help` del writer con solo `--nb`/`--strict`/`--upload`, y `_check_qmind_writeback()`
      invocando sin `--strict`. Todo lo que la tabla prometía como vigente se encontró vigente.
- [x] AC1: `--title`/`--file` con sus tests, sin cambiar el default de `--upload <PLAN>`. Control negativo
      ejercitado sobre el blob de `21ade6c`.
- [x] AC2 y AC4, **parte offline**: verificación por contenido contra la **instantánea versionada**, regla de
      una sola fuente vigente, y mutaciones M1/M3 rojas por el guard. Su **parte remota** queda en el
      momento B con dueño y disparador (maestro §6), declarada pendiente y no cerrada por omisión.
- [x] AC3: sin PASS por ausencia de instrumento; el estado «no medible» se ve en el resumen. **Es la AC que
      sostiene la credibilidad de las demás y se comprueba íntegramente sin red.**
- [x] AC5: 3/3 mutaciones en rojo por el guard, 0 por sintaxis o import, árbol restaurado por sha256
      (`evidence/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/mutation_report.json`).
- [x] **AC6-entrega**: prompt de FASE-RELEASE del plan padre actualizado para mandar el writer con `--title`
      (`git diff` del prompt como evidencia). Cierra en esta fase. Incluye la errata `run()` → `run_all()`.
- [ ] **AC6-aceptación**: **no** es casilla de esta fase. Se registra en el cierre como heredada al momento B
      (RELEASE del padre, tras su ingesta de cierre, verificada por descarga + sha256). **Así queda a propósito:**
      marcarla sería el verde hueco que esta fase vino a cerrar.
- [x] Cierre documental completo, índice regenerado y `--check` fresco, quick TOTAL PASS. ⟦La tabla de
      «Archivos Nuevos» de REGISTRY lista 7 porque `log_phase_completion.py` es aditivo y volver a ejecutarlo
      apilaría una entrada duplicada: la entrega real tiene 9 archivos nuevos (faltan dos que nacieron *después*
      del registro —`instantaneas/README.md` y el crudo del quick de cierre— y viajan con esta nota).⟧

## Inicio de la sesión

Copiar en una sesión nueva:

```text
Ejecuta la FASE-UNICA del plan C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/. Lee 01-plan-maestro.md (premisas P1-P6, AC1-AC6 y sobre todo §6 los dos momentos), 00-lecciones-capitalizadas.md, 05-prompt-inicio-sesion.md y el prompt de FASE-RELEASE del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18, que es el consumidor de AC6-entrega. Re-mide las premisas antes de la primera tarea SIN RED: git HEAD y status, run_all_validations.py --quick, validate_plan_citations.py, build_lesson_index.py --check, y lectura de scripts/validate_qmind_writeback.py y de _check_qmind_writeback() en run_all_validations.py. NO llames fetch_source_titles() ni ninguna otra operacion remota: esa re-medicion pertenece al momento B del maestro §6 y requiere autorizacion literal y presupuesto propios que esta sesion no tiene. Objetivo: que el write-back sea actualizable (--title, --file) y que la verificacion compruebe contenido y vigencia contra la instantanea versionada en el repo en lugar de la existencia del titulo, sin degradar a PASS cuando el CLI falta. AC6 se desdobla: cierra AC6-entrega (instrumento capaz + prompt del padre actualizado); AC6-aceptacion queda heredada al momento B con dueno y disparador, declarada pendiente, no omitida. Pruebas: integramente offline, sin la excepcion de «ingesta de prueba» que tenia la version anterior. Limites: no tocar Tribunal, gates, umbrales, write/publish/suppress, hooks, VERSION.yaml, AGENTS.md ni el workflow; no subir material del cliente; no ejecutar v4complete ni scraping; citar simbolos y nunca numeros de linea en los documentos. R2: sin transcript declara FUERA DE SERVICIO con unidad contable propia y no compares. Commit, push, tag y write-back se piden por separado y con autorizacion literal: deja checkpoint si falta; los cinco cortes se sostienen sin commit.
```
