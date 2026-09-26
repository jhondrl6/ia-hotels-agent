# Permisos pendientes, decisiones humanas y deuda diferida

Tres listas que **no** son la misma cosa y no se mezclan: (A) permisos que faltan, (B) decisiones que
corresponden a una revisión humana y que esta sesión **no** tomó ni atribuyó, (C) deuda técnica diferida
con dueño y disparador.

---

## A. Permisos pendientes (nadie los concedió en esta sesión)

| # | Permiso | Alcance exacto que se pide | Por qué no se ejerció | Consecuencia de no tenerlo |
|---|---|---|---|---|
| A1 | **FASE-RELEASE de CONTEXTO** | Su mandato propio, **más C0**: los destinos escribibles autorizados uno por uno (ver `24-rectificacion-permisos.md`). Offline = sin red, **no** permiso de escribir | Prohibido expresamente en esta sesión | La orden queda abierta por su §6, motivo 1 |
| A2 | **Commit del árbol** | Decidir **qué viaja**: hoy están sin rastrear `scripts/build_phase_briefing.py`, los 5 `briefing/*.md`, los documentos de cierre de C, el par de índice y los `.md` de los cuatro planes | Prohibido: commit, tag, push y `git add` fuera del permiso | La evidencia de FASE-D y de esta conciliación existe **solo en el árbol de trabajo** |
| A3 | **Push** | Separado del commit | Prohibido | El remoto **se mide**, no se cita: `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` |
| A4 | **Archivado (`git mv`)** | Mover el plan a `.opencode/plans/Archives/` al cerrar | Prohibido (momento propio) | S14 **no se dispara** con ese `git mv`: ver su fila en `10-analisis-post-implementacion.md`, rectificada el 2026-09-25 |
| A5 | **Correcciones de corpus** | `validate_opencode_refs.py --fix` (reescribe `.opencode/**/*.md`) y `validate_plan_citations.py --update-baseline` (escribe `.opencode/plans/plan_citations_baseline.json`) | **Retirados de la secuencia de cierre** por la rectificación del 2026-09-25: los checks corren sin writer y ningún baseline se actualiza para absorber errores | Sus rojos se declaran con su lista, no se «arreglan» |
| A5-bis | **Escritura de configuración central en el cierre** (nuevo permiso explícito, no estaba nombrado) | `sync_versions.py` **sin** `--check` → `README.md` de raíz, `AGENTS.md`, `.cursorrules`, `docs/CONTRIBUTING.md`, `docs/GUIA_TECNICA.md` (según `scripts/sync_config.yaml`); `VERSION.yaml` (entrada, no salida: exige versión y fecha aprobadas); `log_phase_completion.py` → `REGISTRY.md` y `.last_doc_phase.json` si se pasa `--archivos-mod` | Esta sesión **no** ejecutó sync en escritura, registro, `--fix` ni `--update-baseline`: todos caen fuera del permiso documental | Sin ellos, C0 queda incompleto: **checkpoint, no cierre offline cumplido** |
| A6 | **Consulta y subida QMind (D8, D9)** | Autorización literal + presupuesto, por separado | Prohibido: sin red, sin QMind | `PENDIENTE-AUTORIZACION` en el cierre, con causa |
| A7 | **Editar trabajo ajeno** | El prompt de WHATSAPP `05-prompt-inicio-sesion-fase-G.md:52` aún manda «al menos tres observaciones medidas» | No estaba en el permiso (esta conciliación solo podía tocar el `10-` de WHATSAPP) | Queda **una** cuota viva en el repo, declarada con su línea |
| A8 | **`AGENTS.md` / `docs/CONTRIBUTING.md` sobre DOMAIN_PRIMER** | Ver §B2, con su texto exacto | Configuración central: exige instrucción literal expresa | Los dos textos siguen describiendo la misma regla de dos formas distintas |
| A9 | **Reparar `build_lesson_index.py` (S15)** | Que la fecha del par salga de una fuente declarada, no del `mtime` | **Alcance técnico separado**: código, y ni este plan ni la orden lo autorizan | El `[6/7] --check` no es reproducible entre checkouts |

## B. Decisiones de revisión humana (esta sesión las presenta; no acepta, no rechaza, no atribuye)

### B1. Las cinco propuestas del piloto que esperan decisión (contrato E3)

Registro de origen: `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-C/informe.json` →
`revision_humana` = `propuestas_pendientes: ["L-VCF-10","L-VCF-11","L-VCF-12","L-VCF-13","L-VCF-14"]`,
`n_pendientes: 5`, `registros: []`, `seccion_dos_editada_por_este_script: false`, con la nota literal
*«con proveedor falso una propuesta prueba la mecanica del camino, no la pertinencia (E3)»*.
Definiciones en `10-analisis-post-implementacion.md` §Lecciones (filas L-VCF-10…14) y recuento en
`00-lecciones-capitalizadas.md`: «propuestas aceptadas para §2: 0 · rechazadas: 0 · pendientes: 5».

| ID | Qué propone la lección (una línea) | Estado |
|---|---|---|
| L-VCF-10 | Toda prohibición de proceso necesita un instrumento que falle si se viola; si su prueba depende de un `import`, que lo resuelva un fixture | **pendiente de decisión humana** |
| L-VCF-11 | Dos poblaciones con cifras cercanas no son la misma población: la resta se desglosa o se publica como no desglosada | pendiente |
| L-VCF-12 | Antes de correr cualquier verificador con `--report`/`--write`: mirar si su default toca evidencia commiteada | pendiente |
| L-VCF-13 | Antes de dar crédito a un `[]`, medir si había algo que perder en el insumo | pendiente |
| L-VCF-14 | Enumerar también el estado «el artefacto se lee y no es lo que dice ser» | pendiente |

**Ninguna entró en §2 de `00-lecciones-capitalizadas.md`** (AC10: §2 conserva sus 14 filas), y esta
conciliación **no** editó ese documento — no está en su permiso. Una aceptación o un rechazo necesita
`decidio`, `fecha` y `motivo`; sin los tres, el guard del propio contrato responde `REVISION-INCOMPLETA`.

### B2. Alineación exacta propuesta para DOMAIN_PRIMER (**presentada, no aplicada**)

El pendiente **documental** ya está resuelto en el plan que lo llevaba (WHATSAPP `README.md:50-64`, resuelto
por el bloque C leyendo la gobernanza): **regenerar** y **validar** son dos operaciones distintas. Lo que
queda es la **alineación de los dos textos centrales**, que ese mismo documento se declara a sí misma como
no hecha por ser configuración central:

| # | Texto vigente hoy | Texto propuesto (exacto) |
|---|---|---|
| 1 | `AGENTS.md:66` — «> **DOMAIN_PRIMER se regenera en FASE-RELEASE** (no manualmente).» | «> **DOMAIN_PRIMER se REGENERA con su writer (`scripts/doctor.py --regenerate-domain-primer`) al cerrar cada fase de implementación, y se VALIDA con `doctor.py --context`/`--status` en FASE-RELEASE. No se edita a mano.** Son dos operaciones distintas: la validación del RELEASE no sustituye la regeneración de la fase, ni la regeneración de la fase se reporta como verificación.» |
| 2 | `docs/CONTRIBUTING.md:173` — «`SEMI-AUTO via scripts/doctor.py --regenerate-domain-primer` \| **Se VERIFICA (paso 5b)**», mientras el propio `Paso 5b` (línea 176) se titula «**Regenerar** DOMAIN_PRIMER.md» | Tercera columna: «**Se REGENERA** al cerrar cada fase de implementación (Paso 5b); **se VERIFICA** en FASE-RELEASE» |
| 3 | `docs/CONTRIBUTING.md:416` — «**DOMAIN_PRIMER**: Regenerar al cerrar cada fase de implementacion, no solo verificar» | **Sin cambio**: es la regla que la propuesta aplica; queda como ancla |

**Consumidores identificados** (por eso hace falta instrucción literal y una re-ejecución, no un edit):
`AGENTS.md:92` (fila de la tabla de cross-references, con sus anclas `§Paso-5b` / `§E7`),
`scripts/validate_document_integration.py` — que **parsea esa tabla** (`:386-435`) y el mapeo de anclas
(`:185`) y verifica `DOMAIN_PRIMER vs VERSION.yaml` (`:435-472`) —, el workflow canónico
`.agents/workflows/phased_project_executor.md` §E7, `scripts/doctor.py --regenerate-domain-primer` como
único writer, `.agent/knowledge/DOMAIN_PRIMER.md` (que **ya está modificado** en el árbol por otra sesión y
no se toca aquí), y las filas `WHATSAPP` de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` §4.C.
**Efecto lateral esperado si se aplica**: tocar el ancla `§Paso-5b-DOMAIN-PRIMER` o su título corta el check
de referencias cruzadas; por eso se valida con `validate_document_integration.py` **después** del edit.

### B3. Decisiones de JEV que siguen sin dueño humano

Congelado de la muestra y umbrales del protocolo (P1, `etiquetas.review_status = sin_revisar`, muestra
`BORRADOR` de 4 pares frente a un objetivo de 60-100 → `MUESTRA-INSUFICIENTE`); y la decisión del ***gap*
de interfaz**: `provider_requested`, `model_requested`, `usage_normalized`, `elapsed_ms`, `attempts`,
`error_kind` **no** los expone la puerta — o se extiende la costura del hermano de forma aditiva o los
produce el *runner*. Esta conciliación **no** eligió ninguna de las dos.

## C. Deuda diferida (con dueño y disparador; no es permiso pendiente)

| Deuda | Estado re-validado el 2026-09-25 | Dueño / disparador |
|---|---|---|
| **D2** | abierta; su rama literal se cumplió en parte y eso **no** la abre | su plan propio; exige instrucción expresa y toca pins de `tests/` |
| **D3** | **parcial** (el workflow canónico sigue entrando en los dos lados de la resta de carga) | «Plan propio, posterior» |
| **D6** | **dormida con causa**: su disparador es un `acceptance` que no se ejercitó | se evalúa con D7 |
| **D7** | sin activar | quien active el proveedor real; con ella se abre la rama de D6 y nace S10 |
| **S10** | abierta: dónde vivirá el `import` del SDK | consumidor de D7 |
| **S14** | abierta, **disparador corregido**: el `git mv` del cierre **no** lo dispara (no llama al triaje con rutas trasladadas); lo dispara correrlo con `--plans-dir` sobre una copia o árbol extraído | este plan, FASE-D o RELEASE |
| **S15** | abierta: **un verde local de `[6/7]` no certifica otro checkout**; commitear el par no lo cura | quien pueda tocar `build_lesson_index.py` — **alcance técnico separado** |
| **S16** | abierta: la convención `Lee …` no está escrita en `prompt-fase-template.md` (medido: 0 de 121 prompts archivados) | `.agents/workflows/templates/prompt-fase-template.md` §8; disparador: el próximo mandato que autorice editar el template |
| **D4/D5** | ajenas a este lote | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda |
| **AC5 de WHATSAPP** | sigue debida, con dueño en C-D de su propio plan | REFACTOR-WHATSAPP |
| **Cuota residual en `WHATSAPP/05-prompt-inicio-sesion-fase-G.md:52`** | **no barrida** (fuera del permiso; ver A7) | el operador |
