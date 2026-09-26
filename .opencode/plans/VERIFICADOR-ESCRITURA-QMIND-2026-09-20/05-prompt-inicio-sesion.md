# FASE-UNICA — Verificador de escritura y frescura del write-back a QMind

**Estado:** PENDIENTE. ⟦Desde el 2026-09-24 su aceptación está dividida en dos momentos (maestro §6):
**entrega offline**, que es lo que esta sesión puede cerrar, y **aceptación remota**, que no⟧.
**Dependencia inmediata:** ninguna técnica. **Disparador:** sesión propia **antes de
FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**; si ese RELEASE llega primero, aplicar el §5 del
maestro y dejar AC2–AC4 abiertos con dueño.
**AC6 se desdobla (⟦orden de calidad §4.C, fila `ESCRITURA-QMIND`⟧):** **AC6-entrega** — dejar el writer
capaz de publicar con `--title` y actualizar el prompt del padre — **sí cierra en esta fase**;
**AC6-aceptación** — `[15/15]` verde sobre el padre tras su ingesta de cierre — **no puede cerrar aquí por
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
   exigir que un plan no tenga dos fuentes vigentes sin marca de reemplazo. Decisión abierta que hay que
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
   — eso **es** AC6-entrega, y cierra en esta fase. Cierre incremental con la regla de siempre:
   `log_phase_completion.py` sin `--release`, `build_lesson_index.py` y su `--check`, quick y
   `validate_document_integration`.

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

- [ ] Premisas P1–P6 re-medidas al abrir, **con sus comandos y sin llamadas de red** (tabla de arriba).
- [ ] AC1: `--title`/`--file` con sus tests, sin cambiar el default de `--upload <PLAN>`.
- [ ] AC2 y AC4, **parte offline**: verificación por contenido contra la **instantánea versionada**, regla de
      una sola fuente vigente, y mutaciones M1/M3 rojas por el guard. Su **parte remota** queda en el
      momento B con dueño y disparador (maestro §6), declarada pendiente y no cerrada por omisión.
- [ ] AC3: sin PASS por ausencia de instrumento; el estado «no medible» se ve en el resumen. **Es la AC que
      sostiene la credibilidad de las demás y se comprueba íntegramente sin red.**
- [ ] AC5: 3/3 mutaciones en rojo por el guard, 0 por sintaxis o import, árbol restaurado por sha256.
- [ ] **AC6-entrega**: prompt de FASE-RELEASE del plan padre actualizado para mandar el writer con `--title`
      (`git diff` del prompt como evidencia). Cierra en esta fase.
- [ ] **AC6-aceptación**: **no** es casilla de esta fase. Se registra en el cierre como heredada al momento B
      (RELEASE del padre, tras su ingesta de cierre, verificada por descarga + sha256).
- [ ] Cierre documental completo, índice regenerado y `--check` fresco, quick TOTAL PASS.

## Inicio de la sesión

Copiar en una sesión nueva:

```text
Ejecuta la FASE-UNICA del plan C:/Users/Jhond/Github/iah-cli/.opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/. Lee 01-plan-maestro.md (premisas P1-P6, AC1-AC6 y sobre todo §6 los dos momentos), 00-lecciones-capitalizadas.md, 05-prompt-inicio-sesion.md y el prompt de FASE-RELEASE del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18, que es el consumidor de AC6-entrega. Re-mide las premisas antes de la primera tarea SIN RED: git HEAD y status, run_all_validations.py --quick, validate_plan_citations.py, build_lesson_index.py --check, y lectura de scripts/validate_qmind_writeback.py y de _check_qmind_writeback() en run_all_validations.py. NO llames fetch_source_titles() ni ninguna otra operacion remota: esa re-medicion pertenece al momento B del maestro §6 y requiere autorizacion literal y presupuesto propios que esta sesion no tiene. Objetivo: que el write-back sea actualizable (--title, --file) y que la verificacion compruebe contenido y vigencia contra la instantanea versionada en el repo en lugar de la existencia del titulo, sin degradar a PASS cuando el CLI falta. AC6 se desdobla: cierra AC6-entrega (instrumento capaz + prompt del padre actualizado); AC6-aceptacion queda heredada al momento B con dueno y disparador, declarada pendiente, no omitida. Pruebas: integramente offline, sin la excepcion de «ingesta de prueba» que tenia la version anterior. Limites: no tocar Tribunal, gates, umbrales, write/publish/suppress, hooks, VERSION.yaml, AGENTS.md ni el workflow; no subir material del cliente; no ejecutar v4complete ni scraping; citar simbolos y nunca numeros de linea en los documentos. R2: sin transcript declara FUERA DE SERVICIO con unidad contable propia y no compares. Commit, push, tag y write-back se piden por separado y con autorizacion literal: deja checkpoint si falta; los cinco cortes se sostienen sin commit.
```
