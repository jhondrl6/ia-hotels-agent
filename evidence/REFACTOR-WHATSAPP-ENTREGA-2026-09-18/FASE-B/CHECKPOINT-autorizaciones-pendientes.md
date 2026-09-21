# FASE-B — checkpoint y autorizaciones pendientes (2026-09-20)

**Actualizado al cerrar A4 y el commit.** La fase quedó **CERRADA CON DEUDA REGISTRADA
(AC5, dueño C-D)** y su código de producto **ya está commiteado** (`473ed0f`, 42 archivos,
+1.907/−266, 7/7 checks del pre-commit sin saltar ninguno). Lo que sigue abierto es una
decisión de C/D (AC5). El push también se ejecutó: `cf3ddc2..05d0cc6`, paridad 0/0. Ningún permiso se evadió ni se asumió.

> Historia de este archivo: se escribió con la fase en **INCOMPLETA** y el árbol sin
> commitear, porque A2/A3/A4 esperaban autorización. Las tres se resolvieron en la misma
> sesión: A2 con instrucción literal (`473ed0f`), A4 con la decisión O5 (§A4 abajo y
> `A4-decision.md`, commit `05d0cc6`) y A3 con instrucción literal de push
> (`cf3ddc2..05d0cc6`, paridad 0/0). Lo que queda abierto es trabajo de C/D, no un permiso.

## Árbol modificado (medido con `git diff --numstat`)

Producción (11 archivos, todos dentro de la allowlist de B menos ninguno):
`v4_asset_orchestrator.py`, `scripts/validate_wiring.py`,
`pain_solution_mapper.py`, `asset_catalog.py`, `whatsapp_setup_guide.py` (nuevo),
`conditional_generator.py`, `pain_ledger.py`, `whatsapp_conflict_guide.py`,
`service_identity.py`, `v4_diagnostic_generator.py`, `main.py` (solo comentario).
Tests: `test_fase_b_promesa_whatsapp.py` (nuevo) y re-vinculaciones en
`test_proposal_alignment.py`, `test_proposal_dynamic.py`,
`test_promised_assets_production.py`, `test_coherence_generated_assets.py`,
`test_site_verification_propagation.py`, `test_validate_wiring.py`.
Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/` (9 artefactos al commitear
`473ed0f` + `A4-decision.md` + `tests_a4_postfull.txt` = 11).

## Lo que hace falta decidir o autorizar (actualizado tras A1)

| # | Petición | Estado | Por qué |
|---|---|---|---|
| A1 | Extender la allowlist de B a `proposal_asset_alignment.py` (tabla de resolución ≠ universo contado) | **AUTORIZADA Y EJECUTADA en la misma sesión** | Cerró los 7 rojos de matriz (POST-C 83 passed) sin mover el denominador del gate. Se midieron y descartaron dos variantes: contar la guía (15 rojos, degrada cobertura) y ampliar el universo de la matriz (13 rojos, el builder devolvía filas que nadie pidió) |
| A2 | **Commit** del trabajo de B | **AUTORIZADO Y EJECUTADO el 2026-09-20** — `473ed0f` (42 archivos, +1.907/−266; 7/7 checks del pre-commit, ninguno saltado) | Instrucción literal "Procede con el commit." El commit anterior a este decía "sin commit" en cuatro documentos; ya barrido |
| A3 | **Push** a `origin/master` | **AUTORIZADO Y EJECUTADO el 2026-09-20** — `cf3ddc2..05d0cc6` (2 commits), paridad 0/0 verificada con `git ls-remote` y `git rev-list --left-right --count` | Solo con instrucción literal y pedida por separado del commit. Pre-flight medido: remoto en `cf3ddc2`, local adelante en 1 (`git rev-list --left-right --count origin/master...master` = `0 1`), fast-forward sin divergencia |
| A4 | Decisión de producto/gate: deuda de entrega de un servicio condicional | **DECIDIDA el 2026-09-20 con la opción O5** — ver `A4-decision.md` | `test_publication_gates.py::test_get_blocking_issues` esperaba 3 gates bloqueantes y veía 2: el gate toma el "PASS trivial" cuando el único comprometido es condicional. Se re-ancló el fixture a `whatsapp_conflict` (dolor de WhatsApp que sigue prometiendo servicio contado) y se reforzó la aserción; el punto ciego queda assertionado en `test_deuda_ac5_ledger_solo_condicional_pasa_trivial`, que debe ponerse rojo cuando AC5 lo gobierne. **Superficie AC5, dueño C-D** (maestro §4; el "D-E" que figuraba aquí era un error de registro). El gate no se tocó |

## Cierre documental ejecutado (T4)

`CHANGELOG.md` (subsección FASE-B bajo 4.77.3), `docs/GUIA_TECNICA.md` (nota técnica del
patrón resolución ≠ conteo), `00-lecciones-capitalizadas.md` (aplicación efectiva medida
de L-NC6, L-NC10, L-T4A.5, L-PF6, L-PF10, L-V2.3 y L-V.3), `06-checklist-implementacion.md`
(filas B/AC1/AC2/AC19 + resumen), `dependencias-fases.md` (fila B), `09` (secciones E y
registro por fase), `10-analisis` (métricas y cuatro seguimientos con dueño S-B1…S-B4),
`05-prompt-inicio-sesion-fase-B.md` (estado INCOMPLETA + checkpoint), este informe, y
`log_phase_completion.py --fase FASE-B`, `build_lesson_index.py` (+`--check`), quick y
`validate_document_integration.py`.

## Estado de los contadores

- v4complete: **0/1** (no se ejecutó ninguna corrida; el plan reserva el intento a E2E).
- Quick: 11/11 al PRE y **11/11 re-medido al cerrar A4** (con el guard de cableado: 174
  llamadas / 614 archivos, gobernadas 75, conformes 21, omisiones 0, excepciones 0,
  violaciones 0). `validate_document_integration.py`: todos los checks en verde.
  `build_lesson_index.py --check`: vencido por la fila nueva de §10 y **regenerado el par**
  (320 IDs, fresco).
- Regresión completa tras A4: **3 failed / 4.263 passed / 41 skipped / 4 xfailed** en 196,5 s
  (`tests_a4_postfull.txt`). Los 3 rojos son los mismos de la evidencia de FASE-0.
- Funciones canónicas: 4.299 → **4.300 (+1)**.
- Mutantes: 8/8 (M1–M8) rojos causados por el guard, 8/8 restaurados y verificados por sha256.
- R2: métrica **FUERA DE SERVICIO (R2.1)**; los autocuentos intermedios que figuraban aquí
  (~155) y en §10 (~165) se retiran: sin instrumento, la cifra no es comparable y solo
  producía la falsa precisión. Lo que sí se registró es el exceso sobre la referencia de 60,
  que produjo este checkpoint y no un avance de fase.

## Invariantes verificadas (nada de esto se tocó)

`TribunalJudge._compute_verdict`, `BLOCKING_VERDICTS`, `GATE_BLOCKING_ENABLED`,
umbrales de `config/pricing.yaml`, contratos `write/publish/suppress` de
`DeliveryPackager`, warehouse (`data/hotel_observations/`), esquema de onboarding
(deuda F-B diferida). Los umbrales de WhatsApp (`NEW_HOTEL_THRESHOLDS["whatsapp_button"]
= 0.3`, catálogo 0.7, coherencia 0.9) quedaron **inventariados pero sin cambiar**: AC5
es de C/D.
