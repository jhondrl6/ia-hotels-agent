# Reintento de la consulta QMind denegada en la revisión 2 — FASE-A

**Consulta:** `00-lecciones-capitalizadas.md` Q9 / maestro §7 ("Límite de la revisión 2").
**Fecha:** 2026-09-19. **Notebook:** `iah-cli-lecciones` · `01a04d98-b7bd-778c-8441-26fdc7e35f45`.
**Herramienta:** `mcp__plugin_qoder-qmind_qoder-qmind__retrieve` (equivalente a `qmind retrieve`).

## Resultado: RECUPERADO

La denegación del clasificador de la revisión 2 **no se repitió**. Dos llamadas, ambos ejes:

| Eje | Consulta | Resultados | Fuente de mayor score |
|---|---|---|---|
| Presencia / WhatsApp | "presencia en el sitio lector WhatsApp huella de plugin falso positivo verificacion numero" | 5 | `CONTEXT-H: DT-4 root cause` (score 0.819) |
| Acta / cuarentena / veredicto | "acta revision veredicto tribunal cuarentena ZIP suprimido critical_recall details serializacion hallazgos" | 3 | `10-analisis: TRIBUNAL-OFFLINE-2026-09-09` L-E2E.3 (score 0.925) |

## Qué añade el corpus remoto frente a lo ya capitalizado

| # | Hallazgo recuperado | Estado previo en este plan | Consecuencia registrada por A |
|---|---|---|---|
| R1 | **L-E2E.3** — "el tribunal es advisory de facto: `_compute_verdict` (T1) solo consume gates y `reviewer_reports` queda `[]`". | No capitalizada en `00`. | **Queda obsoleta como descripción y refuerza AC20:** desde el enforcement (v4.77.0) el Juez **sí** consume `reviewer_reports`, medido en la corrida `output/TAREA7-2026-09-19/` (13 gates sin bloqueo + 1 CRITICAL de Bot 1 → `BLOQUEADO`). Un hueco de serialización en `details` ya no es decorativo: decide la supresión del ZIP. A no abre tarea nueva; ancla el motivo por el que AC20 va primero. |
| R2 | **L-E2E.4** — modo ZIP-only: en E2E del plan anterior la evidencia incluyó el ZIP **y** su descompresión (`deliveries/*_unpacked/`) para que VERIFY recertificara sin tocar el baseline. | `L-E2E.1` sí capitalizada (los revisores no encuentran `MANIFEST.json`); la práctica del `*_unpacked/` no. | **Segunda confirmación medida del límite de `00` §4:** la fila estaba en `.opencode/LECCIONES-INDEX.md` (líneas 67-68) y aun así no se capitalizó → el corpus remoto no amplió la cobertura; la pregunta sí cambió lo recuperado. A no lo convierte en tarea: lo deja como **observación para E/H** (AC10/AC11 necesitan una vía de lectura del paquete que no dependa de descomprimir el ZIP vivo, hoy inexistente porque `suppress()` lo borra). |
| R3 | **DT-4 BUG-6** — coverage gate y `no_whatsapp_visible`: el fix real fue propagar `skipped_assets.pain_ids_affected` al ledger y añadir `ASSET_GENERATED` a `_JUSTIFIED_STATUSES`; "el coverage gate debe consultar SitePresenceChecker" era **menos preciso**. | No capitalizada. | **Verificado en código vivo: ya está hecho** — `publication_gates.py:1386` incluye `ASSET_GENERATED` con comentario anti-reversión (L1542). A lo registra como **cableado preexistente que B no debe reinventar** y como el motivo por el que la corrida del 2026-09-19 pasó `coverage_no_silent_drop` con 12/12. |
| R4 | **HALLAZGO-N4** — `_check_whatsapp_verified()` lee `assessment.whatsapp_confidence` computado **antes** de SitePresenceChecker ("ghost module / signature-only wiring"). | Implícita en la fila CONFLICT del maestro §2. | Refuerza **L-NC6** y el prerrequisito de G: A no abre fila nueva (el plan ya gobierna el boost) pero ancla que el orden temporal pre-existe al boost. |
| R5 | **F12/F13 (adenda 2026-08-20, Zione)** — **falso positivo de conflicto WhatsApp por cruce entre sedes**: el cross-validator comparaba el GBP contra el primer `wa.me`/teléfono del DOM sin mapear número→sede, y `no_whatsapp_visible` HIGH(0.3) se publicó con el botón existente en 3 ubicaciones. | **No existe en el corpus local** (0 coincidencias de `sede`/`multi-ubicaci` en `LECCIONES-INDEX.md`) ni en el plan. | **Cerrado en código vivo y re-verificado por A** (`L-ENT.4`: el estado heredado caducó otra vez). El reconciliador existe: `CrossValidator._reconcile_whatsapp_multisede` (`cross_validator.py:198`, marcado "FASE-P1-D (F12)"), con su suite propia `tests/data_validation/test_whatsapp_multisede.py`. **Aporte neto del corpus remoto:** no abre deuda nueva, pero revela un **prerrequisito no declarado** — el plan nunca nombra el reconciliador, así que B/C pueden reintroducir la comparación ingenua (`L-NC6`) y AC6 exigir un destino "exactamente derivado del campo verificado" sin decir que ese campo ya pasó por una reconciliación por sede. A lo registra como **dependencia a citar en B/C**, no como tarea. |
| R6 | **DA-P1.4** — el acta **se excluye del paquete de cliente por nombre** (`DeliveryPackager._INTERNAL_DOC_PREFIXES = ("acta_revision",)`, código vivo en `delivery_packager.py:442`) y el ZIP no puede contener el acta enriquecida: círculo estricto (`write()` serializa bytes, el enriquecimiento exige leer ese ZIP). | El maestro cita `L-E2E.1` (orden temporal) pero no la exclusión por nombre. | **Límite explícito para E/AC11:** el resolvedor único no debe esperar `acta_revision.json` dentro del ZIP, y "snapshot interno fuera del árbol exportado" ya es construcción vigente, no disciplina. A lo ancla en `decisiones.md`, sin tocar el contrato. |

## Límites de esta consulta

- No se subió ni modificó nada en QMind: la consulta **no** autoriza write-back (`04-contrato-ejecucion.md` §límites).
- Ninguna salida contiene secretos ni material del hotel; las cifras citadas son de artefactos del repositorio.
- QMind no sustituye el código vivo: R3 y R6 se verificaron contra el código antes de registrarlas.
