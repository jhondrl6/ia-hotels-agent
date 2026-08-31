# Dependencias de Fases — VALIDADOR-URL-PROPIA-2026-08-30

## Grafo de dependencias

```
Preparación (2026-08-30, esta sesión)
        │
        ▼
     FASE-A ──────────────┐   (núcleo del guard — prerrequisito de todo)
        │                 │
        ▼                 │
     FASE-B ──────────────┤   (superficies secundarias — requiere guard de A)
        │                 │
        ▼                 │
     FASE-C ──────────────┤   (verificación empírica — requiere A+B)
        │                 │
        ▼                 │
     FASE-D ──────────────┘   (E2E Salento Real — requiere A+B; C deseable)
        │
        ▼
   FASE-VERIFY  (requiere A+B+C+D ✅ — certificación sin código)
        │
        ▼
FASE-RELEASE-4.74.0  (requiere VERIFY ✅)
```

## Conflictos de archivo

| Archivo | Fases que lo tocan | Resolución |
|---------|--------------------|------------|
| `main.py` | FASE-A (`ensure_url`, reutilización de `--force` main.py:172), FASE-B (saneamiento `last_url` en el entorno de `ensure_url`/`save_state` — SIN guards por modo, auditoría F2) | Secuenciales (A→B); FASE-B arranca con `git status` limpio de A ya commiteado |
| `tests/test_url_propia_guard.py` | FASE-A (contratos núcleo), FASE-B (extensión last_url/comandos/hook-pdf) | Secuenciales; FASE-B SOLO agrega tests, no reescribe los de A |
| `modules/commercial_documents/hook_pdf_generator.py` | Solo FASE-B (track 2) | Sin conflicto |
| `modules/scrapers/web_scraper.py` / `modules/auditors/v4_comprehensive.py` | Solo FASE-B (assert_own_site) | Sin conflicto |
| `config/url_blocklist.yaml` | Creado en FASE-A; solo lectura después | Sin conflicto |

## Tracks internas de FASE-B (delegación)

```
Subagente 1 ── main.py: saneamiento last_url + contratos ensure_url por comando ┐
Subagente 2 ── hook_pdf_generator.py + web_scraper + v4_comprehensive            ├──► Parent integra,
                                                                                  ┘    extiende guardián AST (4 superficies),
                                                                                       unifica exit code/mensajes
```
Overlap en `main.py` SOLO en subagente 1 → tracks paralelizables; el parent integra y ejecuta la regresión (L12: overlap de archivo decide la integración).

## Dependencias externas

| Dependencia | Estado | Acción si falta |
|-------------|--------|-----------------|
| Contexto `.opencode/context/CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29.md` | ✅ Existe | — |
| Sondas `temp/probe_donjulio_viability.py`, `temp/probe2_donjulio.py` | Posiblemente limpiadas | Regenerar desde Apéndice A del contexto (no son requisito del guard; solo referencia empírica) |
| Baseline E2E `output/salentoreal_final_v4c_h2/` | ✅ Verificado 2026-08-30 (reporte en `v4_complete/v4_complete_report.json`) | Si desaparece, la comparación usa solo criterios absolutos (coherence ≥ 0.8, gates, target_id) |
| Onboarding Salento Real (`output/clientes/*salento*.yaml`) | ❌ NO existe (verificado 2026-08-30; solo zi-one-luxury) | Auditoría F5: NO fabricar — el baseline H2 corrió con defaults, la equivalencia AC8 exige defaults |
| Línea base de tests rojos preexistentes | ✅ Re-verificado en FASE-A T1 (2026-08-30): **14 fallos** — calculator_v2 ×3, pricing_resolution_wrapper ×9 (uno orden-dependiente: `test_function_default_flags` pasa aislado), site_verification_propagation ×1, config_pricing ×1 (`temp/fase_a_baseline.txt`) | Registrar en 10-analisis; NO atribuirlos al plan; comparar siempre con la MISMA combinación de archivos |

## Fallback documentado (Paso 0 executor)

- Notebook QMind `iah-cli-lecciones` (id 01a04d98-…): DISPONIBLE — 2 queries ejecutadas 2026-08-30 (lecciones SR, RC1-RC2, DT-4, validación coherencia). Sin limitación que registrar.

## Registro de estado (actualizar al cerrar cada sesión)

| Fecha | Sesión | Cambio |
|-------|--------|--------|
| 2026-08-30 | Preparación | Plan creado; 6 prompts + docs base listos; pendiente FASE-A |
| 2026-08-30 | Auditoría de estrategia | Re-verificación contra código vivo HEAD; 10 fallos corregidos (F1-F10, detalle en README §Auditoría): --force existente, ensure_url cubre todos los comandos, P5 sembrado, mecanismo de warning, FASE-D con defaults, matching anti-falsos-positivos |
| 2026-08-30 | **FASE-A ✅** | Núcleo del guard implementado (TDD rojo→verde 45/45): `config/url_blocklist.yaml`, `modules/data_validation/own_site_guard.py`, choke point en `ensure_url()` DESPUÉS de la reinyección `last_url`, `--force` reutilizado con eventos en `.agent/memory/url_guard_force_events.json`. Baseline real: 14 rojos preexistentes (wrapper ×9, uno orden-dependiente). 28/28 canonicalización. Sin fallos nuevos. Evidencia: `evidence/FASE-VUP-A/`. Sigue: FASE-B (sesión nueva, `git status` limpio tras el commit de A) |
