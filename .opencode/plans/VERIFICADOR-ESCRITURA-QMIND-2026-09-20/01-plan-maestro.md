# Plan maestro — VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Estado: PENDIENTE de ejecución. Una fase, una sesión.** Ningún AC de este documento está implementado.
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
| AC2 | La verificación es **por contenido**: [15/15] exige que la fuente ingerida case con una instantánea versionada en el repo (sha de la copia + prueba de sha inverso del saneado). Título coincidente con contenido distinto ⇒ **rojo** | mutación M1: editar la copia versionada sin re-subir → rojo; re-subir → verde |
| AC3 | La indisponibilidad del CLI deja de ser PASS silencioso: el check lo invoca con `--strict` o el resumen distingue un tercer estado explícito | mutación M2: PATH sin `qmind` → FAIL o WARN declarado, nunca PASS |
| AC4 | Un plan no puede tener **dos fuentes vigentes**: tras publicar con título nuevo, la anterior queda retirada o marcada, y la verificación lo comprueba | mutación M3: dos fuentes del mismo plan sin marca de reemplazo → rojo |
| AC5 | Los tres rojos se demuestran **por el guard**, no por error de sintaxis ni de import, y el árbol se restaura por sha256 | `mutation_report.json` del mini-plan, con la misma forma que el de FASE-G |
| AC6 | El prompt de FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` pasa a mandar el writer con `--title`, y su texto deja de depender de que alguien recuerde el título pre-acordado | diff del prompt + [15/15] verde sobre el plan padre tras la ingesta de cierre |

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

- **Riesgo de cronología:** si FASE-RELEASE del plan padre llega antes que este mini-plan, su write-back se
  hace por CLI directo con el título pre-acordado y AC2–AC4 quedan como deuda viva. No bloquea el cierre.
- **Riesgo de verde hueco:** añadir un check de contenido que llama a un servicio externo puede colgar o
  fallar por red. Decisión de diseño: la comparación de contenido se hace contra la **instantánea versionada
  en el repo**; la llamada al servicio solo se usa para traer el contenido ingerido, y su ausencia cae del
  lado de AC3 (nunca del lado de PASS).
- **Decisión no tomada aquí:** si AC4 debe borrar la fuente antigua (`qmind source delete`) o marcarla.
  Borrar es irreversible sobre contenido publicado; el mini-plan entra proponiendo **marcar** y deja borrar
  como opción explícita del operador.

## 5. Fallback si el disparador vence

Ejecutar el write-back de cierre con `qmind source upload --nb … --file <copia saneada> --title "<título
nuevo>"`, verificar por descarga + sha256 (no por título), y registrar en el `10-analisis` del plan padre que
AC2–AC4 siguen abiertos con dueño. Es exactamente el camino que recorrió FASE-G el 2026-09-20, y está
documentado en su evidencia.
