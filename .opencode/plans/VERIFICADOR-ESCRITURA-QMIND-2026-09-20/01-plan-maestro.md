# Plan maestro — VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Estado: PENDIENTE de ejecución. Una fase, una sesión, y —desde el 2026-09-24— dos momentos de aceptación
(§6).** Ningún AC de este documento está implementado. ⟦Re-medido el 2026-09-24 contra el árbol vigente,
sigue siendo cierto: el writer no expone `--title` ni `--file`, `is_ingested()` decide por título y la
indisponibilidad del CLI devuelve `exit 0`; el check [15/15] no corre en `--quick` ni en el hook⟧.
Versión base del repo al concebir el plan: `4.77.3`, HEAD `7296732` (este mini-plan no cambia `VERSION.yaml`).

## 1. Premisas medidas (no heredadas)

| # | Premisa | Cómo se midió el 2026-09-20 | Consecuencia |
|---|---|---|---|
| P1 | El validador de write-back **sí** está conectado al sistema de validaciones | `grep -rln "validate_qmind_writeback" scripts/` → 2 archivos; en `run_all_validations.py`, método `run()`, rama `if not self.quick:`, el check **[15/15]** lo ejecuta | Una afirmación anterior de esta sesión («no está en `run_all_validations.py`») era falsa y se retractó en cinco documentos. Nace `L-ENT.14` en el plan padre |
| P2 | …pero solo en el modo completo, y degrada a verde sin instrumento | `_check_qmind_writeback()` invoca el script **sin** `--strict`; el propio validador documenta en su docstring que la indisponibilidad del CLI devuelve 0 | Ninguna fase intermedia (`--quick`) ve este check, y con el CLI ausente el PASS significa «no se pudo medir» |
| P3 | La comprobación es de **título**, no de contenido | `is_ingested()` en `validate_qmind_writeback.py` compara el título de la fuente contra el nombre del plan; `do_upload()` construye el título fijo `10-analisis: <PLAN> (lecciones aprendidas y decisiones)` | Una fuente publicada a mitad de plan satisface el check para siempre: el contenido viejo pasa por cierre |
| P4 | El writer no admite actualización | `main()` del validador solo define `--nb`, `--strict` y `--upload`; `upload_source()` pasa `--file` y `--title` al CLI, que no sobrescribe | La única vía de publicar el cierre es un título nuevo, y eso **crea** una fuente duplicada |
| P5 | El duplicado ya existe en el corpus, y se toleró deliberadamente | `fetch_source_titles()` del notebook `iah-cli-lecciones`: 49 fuentes, de las cuales `TRIBUNAL-OFFLINE-2026-09-09` aporta **dos** (una de 2026-09-10 a mitad de plan y la de cierre del 2026-09-11). Su `10-analisis` archivado lo describe: «el script no tiene vía de actualización … se sube con título distinto … el notebook queda con dos versiones» | No es un hueco desconocido: es deuda **documentada y abierta** desde hace nueve días. Este mini-plan la cierra por el lado del repo |
| P6 | El saneado previo es obligatorio y hoy es manual | `do_upload()` sube el archivo crudo; en la subida de G hubo que sustituir 5 identidades del cliente con prueba de sha inverso (`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-G/qmind-writeback-G.md`) | Cualquier prueba contra el servicio real debe partir de copia saneada versionada en el repo |

## 2. Criterios de aceptación

| AC | Criterio | Instrumento esperado |
|---|---|---|
| AC1 | El writer permite publicar con **título y archivo explícitos** (`--title`, `--file`), sin cambiar el comportamiento por defecto de `--upload <PLAN>` | tests propios sobre el parser y sobre `do_upload()` con un directorio temporal |
| AC2 | La verificación es **por contenido**: [15/15] exige que la fuente ingerida case con una instantánea versionada en el repo (sha de la copia + prueba de sha inverso del saneado). Título coincidente con contenido distinto ⇒ **rojo** | **offline:** mutación M1 sobre la instantánea versionada — editarla sin re-subir → rojo; re-subir → verde. La comparación de contenido **no** necesita tocar el servicio: lo que se coteja es el sha de la copia del repo. **El verde definitivo de esta AC contra el servicio real pertenece a la aceptación remota (§6), no a esta fase** |
| AC3 | La indisponibilidad del CLI deja de ser PASS silencioso: el check lo invoca con `--strict` o el resumen distingue un tercer estado explícito | mutación M2: PATH sin `qmind` → FAIL o WARN declarado, nunca PASS. **Medible íntegramente offline**, y es la AC que hace que lo demás sea creíble: sin ella, la ausencia del instrumento se reporta como éxito |
| AC4 | Un plan no puede tener **dos fuentes vigentes**: tras publicar con título nuevo, la anterior queda retirada o marcada, y la verificación lo comprueba | **offline:** mutación M3 sobre el conjunto de fuentes esperado — dos fuentes del mismo plan sin marca de reemplazo → rojo. **Remoto:** comprobar que el marcado llegó al notebook, con su evidencia (§6) |
| AC5 | Los tres rojos se demuestran **por el guard**, no por error de sintaxis ni de import, y el árbol se restaura por sha256 | `mutation_report.json` del mini-plan, con la misma forma que el de FASE-G |
| AC6 | ⟦Desdoblada el 2026-09-24 por el bloque C de la orden de calidad: esta fila era la circular⟧ | **AC6-entrega (offline, es de esta fase):** el prompt de FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` pasa a mandar el writer con `--title`, y su texto deja de depender de que alguien recuerde el título pre-acordado. Instrumento: `diff` del prompt + tests del parser de AC1. **AC6-aceptación (remota, NO es condición de esta fase):** `[15/15]` verde sobre el plan padre **tras su ingesta de cierre**, que es un evento que ocurre **después** del disparador de esta sesión. Dueño y disparador: §6 |

## 3. Alcance y no-alcance

**Dentro:** `scripts/validate_qmind_writeback.py`, su connection en `scripts/run_all_validations.py`,
`tests/` del verificador, los prompts de RELEASE del plan padre, y la documentación de la convención de
títulos en `.agents/workflows/phased_project_executor.md` **solo si** hace falta alinear el contrato con el
código (con instrucción explícita para editar el workflow, que hoy está prohibida en fases intermedias).

**Fuera:** Tribunal (`_compute_verdict`, flags, umbrales), `write/publish/suppress`, gates, hooks,
`VERSION.yaml`, `AGENTS.md`, `main.py v4complete`, red, scraping, y la limpieza retroactiva de las dos
fuentes de `TRIBUNAL-OFFLINE-2026-09-09` — eso último requiere decisión escrita del operador porque toca
contenido ya publicado fuera del repo.

## 4. Riesgos y decisiones pendientes

- **Riesgo de cronología, en las dos direcciones** (⟦el 2026-09-24 el bloque C de la orden de calidad
  registró que solo se había previsto una⟧):
  - *El padre llega primero:* su write-back se hace por CLI directo con el título pre-acordado (§5) y
    AC2–AC4 quedan como deuda viva con dueño. No bloquea el cierre del padre.
  - *Este mini-plan llega primero —el caso para el que está concebido—:* entonces **AC6-aceptación no
    puede cerrarse todavía**, porque su evento (la ingesta de cierre del padre) está en el futuro. Eso
    **no** es un fallo de esta fase ni la obliga a esperar: su evidencia pertenece al momento B de §6 y se
    hereda al RELEASE del padre con dueño y disparador. Sin esta segunda línea, el plan exigía a una sesión
    cerrar una AC cuyo disparador era ella misma.
- **Riesgo de verde hueco:** añadir un check de contenido que llama a un servicio externo puede colgar o
  fallar por red. Decisión de diseño: la comparación de contenido se hace contra la **instantánea versionada
  en el repo**; la llamada al servicio solo se usa para traer el contenido ingerido, y su ausencia cae del
  lado de AC3 (nunca del lado de PASS). **Esta AC es verificable offline precisamente por eso**: lo que se
  prueba es el predicado del verificador, no la disponibilidad del backend.
- **Decisión no tomada aquí:** si AC4 debe borrar la fuente antigua (`qmind source delete`) o marcarla.
  Borrar es irreversible sobre contenido publicado; el mini-plan entra proponiendo **marcar** y deja borrar
  como opción explícita del operador. La decisión se toma en el momento B de §6, con su autorización.

## 5. Fallback si el disparador vence

**Procedimiento de aceptación remota condicionado** (⟦reclasificado el 2026-09-24: este §5 es el camino de
hoy sin el instrumento mejorado, y **no** es una operación que la fase pueda ejecutar por su cuenta ⟧ —
pertenece al momento B de §6): ejecutar el write-back de cierre con `qmind source upload --nb … --file
<copia saneada> --title "<título nuevo>"`, verificar por descarga + sha256 (no por título), y registrar en
el `10-analisis` del plan padre que AC2–AC4 siguen abiertos con dueño. Es exactamente el camino que recorrió
FASE-G el 2026-09-20, y está documentado en su evidencia. Requiere la misma autorización literal y el mismo
presupuesto que se listan en §6; la prohibición de red de esta sesión **no** lo habilita ni lo exime.

## 6. Los dos momentos: entregable, responsable, disparador y evidencia

⟦Añadido el 2026-09-24 por el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, fila
`ESCRITURA-QMIND`. Su §5, decisión «Entrega y permisos remotos», seguía **PENDIENTE** a esa fecha: este §6
define el procedimiento y lo que cada momento necesita, **no** lo autoriza ni ejecuta acceso remoto⟧.

| | **Momento A — entrega offline** | **Momento B — aceptación remota** |
|---|---|---|
| Qué es | Escribir/corregir el writer, el check, sus tests, las mutaciones M1–M3, la instantánea versionada y el prompt de RELEASE del padre | Usar ese writer en la ingesta de cierre del padre y comprobar que el notebook coincide con la instantánea |
| Red | **Ninguna** | Sí, y solo contra el notebook `iah-cli-lecciones` |
| Entregable | `scripts/validate_qmind_writeback.py` con `--title`/`--file`, su conexión en `run_all_validations.py` con el tercer estado, `tests/` del verificador, `mutation_report.json`, la **copia saneada versionada** con su sha, y el `diff` del prompt del padre | Fuente publicada con el título pre-acordado del padre, **más** la evidencia del estado de la fuente anterior (AC4) |
| Responsable | Quien ejecute la fase única de este mini-plan | El **RELEASE del plan padre**, con la autorización del operador; este mini-plan entrega el instrumento, no ejecuta la subida ajena |
| Disparador | Mandato propio de la sesión, sin prerrequisito remoto | La ingesta de cierre del padre, que a su vez exige el momento A entregado |
| Evidencia | Salidas de pytest y de las tres mutaciones, sha de la copia saneada, `git diff` del prompt del padre | **Descarga byte a byte + sha256 contra la instantánea**; nunca el título, nunca un `SKIP` leído como actualización |
| ACs que cierra | AC1, AC3, AC5 y la parte offline de AC2/AC4, **más AC6-entrega** | La parte remota de AC2/AC4 y **AC6-aceptación** |
| Si falta el permiso | No hay permiso que esperar: es trabajo offline | `PENDIENTE-AUTORIZACION` con causa y presupuesto. **Prohibido** cerrar por omisión, y prohibido que el check diga PASS sin instrumento (eso es AC3) |

**Autorización y presupuesto que el momento B va a necesitar** — se documentan para que nadie los invente
sobre la marcha; **esta sesión no concede ninguno**: (i) instrucción literal que nombre el notebook
`iah-cli-lecciones` (ID `01a04d98-b7bd-778c-8441-26fdc7e35f45`), la operación (`source upload`, y para AC4
`source delete` **o** marcado) y el archivo concreto que sube; (ii) confirmación de que el contenido es
**copia saneada** con su prueba de sha inverso, sin material del cliente ni secretos; (iii) presupuesto y
cota de reintentos, porque el backend **no sobrescribe** y un reintento mal interpretado **crea** el
duplicado que AC4 tiene que cazar; (iv) si se elige borrar, decisión escrita aparte — es irreversible sobre
contenido ya publicado. La limpieza retroactiva de las dos fuentes de `TRIBUNAL-OFFLINE-2026-09-09` sigue
fuera de alcance por la misma razón.
