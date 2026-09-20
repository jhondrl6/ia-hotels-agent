# FASE-B — checkpoint y autorizaciones pendientes (2026-09-20)

La fase quedó **INCOMPLETA** con código de producto en el árbol de trabajo **sin
commitear**. Ningún permiso se evadió ni se asumió.

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
Evidencia: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-B/` (7 artefactos).

## Lo que hace falta decidir o autorizar (actualizado tras A1)

| # | Petición | Estado | Por qué |
|---|---|---|---|
| A1 | Extender la allowlist de B a `proposal_asset_alignment.py` (tabla de resolución ≠ universo contado) | **AUTORIZADA Y EJECUTADA en la misma sesión** | Cerró los 7 rojos de matriz (POST-C 83 passed) sin mover el denominador del gate. Se midieron y descartaron dos variantes: contar la guía (15 rojos, degrada cobertura) y ampliar el universo de la matriz (13 rojos, el builder devolvía filas que nadie pidió) |
| A2 | **Commit** del trabajo de B | **PENDIENTE** | El contrato exige autorización expresa; sin commit no se declara el corte de R2 ni se protege el árbol (22 archivos, +543/−218) |
| A3 | **Push** a `origin/master` | **PENDIENTE** | Solo con instrucción literal y pedida por separado del commit |
| A4 | Decisión de producto/gate: deuda de entrega de un servicio condicional | **PENDIENTE, con rojo medido** | `test_publication_gates.py::test_get_blocking_issues` espera 3 gates bloqueantes y ve 2: el gate toma el "PASS trivial" cuando el único comprometido es condicional. Superficie AC5 (D-E). No se re-ancló el test porque su propósito sigue vigente |

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
- Quick: 11/11 al PRE; **no vuelto a medir tras las dos últimas re-vinculaciones**.
- Mutantes: 8/8 (M1–M8) rojos causados por el guard, 8/8 restaurados y verificados por sha256.
- R2: métrica **FUERA DE SERVICIO (R2.1)**; auto-reporte ~155 intervenciones, exceso
  sobre la referencia de 60 → produjo este checkpoint, no un avance de fase.

## Invariantes verificadas (nada de esto se tocó)

`TribunalJudge._compute_verdict`, `BLOCKING_VERDICTS`, `GATE_BLOCKING_ENABLED`,
umbrales de `config/pricing.yaml`, contratos `write/publish/suppress` de
`DeliveryPackager`, warehouse (`data/hotel_observations/`), esquema de onboarding
(deuda F-B diferida). Los umbrales de WhatsApp (`NEW_HOTEL_THRESHOLDS["whatsapp_button"]
= 0.3`, catálogo 0.7, coherencia 0.9) quedaron **inventariados pero sin cambiar**: AC5
es de C/D.
