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
| `main.py` | FASE-A (`ensure_url`, reutilización de `--force` main.py:173), FASE-B (AC7: `except UrlNoPropiaError` en `run_hook_pdf_mode` → exit 2). **AC6 no requirió cambios**: `ensure_url()` L1428 ya precede a `save_state()` L1433 (F2) y `ensure_url` cubre todos los comandos | Secuenciales (A→B); FASE-B arranca con `git status` limpio de A ya commiteado |
| `modules/data_validation/own_site_guard.py` | FASE-A (crea), FASE-B (añade `ORIGEN_CAPA_DATOS`, `FORZADAS_PROCESO`, `EXIT_CODE_URL_NO_PROPIA` — aditivo), FASE-C/D (solo lectura) | Cambios aditivos; los contratos C1-C10 de A siguen verdes |
| `tests/test_url_propia_guard.py` | FASE-A (contratos núcleo), FASE-B T1 (extensión AC6) | Secuenciales; FASE-B SOLO agrega tests, no reescribe los de A |
| `tests/test_url_propia_guard_superficies.py` | Creado en FASE-B (AC7 + capa de datos + D-VUP-B1) | Solo lectura en C/D; requiere fixture `registro_forzadas_aislado` (autouse) para no heredar `FORZADAS_PROCESO` |
| `tests/test_guardian_ast_url_guard.py` | FASE-A (2 defs / choke point), FASE-B T3 (10 defs / 4 superficies + contra-condición F2) | Congela el cableado; tocarlo exige justificación explícita |
| `modules/commercial_documents/hook_pdf_generator.py` | Solo FASE-B (track 2) | Sin conflicto |
| `modules/scrapers/web_scraper.py` / `modules/auditors/v4_comprehensive.py` | Solo FASE-B (assert_own_site con import lazy, primera sentencia) | Sin conflicto. FASE-D ejecuta `v4complete` sobre un dominio propio → el guard no debe interferir |
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
| 2026-08-31 | **FASE-B ✅** | Modo DELEGADO (2 subagentes + parent). AC6: contratos de orden (`ensure_url` L1428 → `save_state` L1433, verificado subiendo `main()`), paridad de mensaje con v4complete y cero repersistencia en estado envenenado — **sin** guards por modo (F2). AC7: `assert_own_site` sobre `report_json["url"]` en `hook_pdf_generator.extract_data(force=...)` + `run_hook_pdf_mode` sale con exit 2. Capa de datos: guard como primera sentencia en `WebScraper.extract_hotel_data` (fuera del `try`) y en `V4ComprehensiveAuditor.audit`. **D-VUP-B1** (no estaba en el plan, resuelta por el parent): registro por netloc `FORZADAS_PROCESO` consultado solo por `ORIGEN_CAPA_DATOS`, para que la defensa de capa de datos no anule el `--force` del operador. +35 `def test_` / 47 casos; 120 passed en contratos integrados; regresión hook-pdf/scrapers 76 passed+4 skipped, auditor/never-block 125 passed+2 skipped; smokes: `hook-pdf --dry-run` sobre el reporte real de Salento Real exit 0, reporte OTA exit 2 sin PDF, `v4complete --url booking…` exit 2. `main.py` y `ensure_url()` sin cambios funcionales. Evidencia: `evidence/FASE-VUP-B/`. Sigue: FASE-C |
| 2026-08-31 | **FASE-C ✅** | Modo DELEGADO (subagente probes + parent verifica). 11/11 probes PASS: P1-P4 rechazo OTA/red social exit 2 sin red; P5 estado envenenado rechazado con mención persistente (AC6: ensure_url aborta antes de save_state — NO re-persiste); P6 hook-pdf rechaza URL OTA via --output-dir (AC7); P7-P8 UrlNoPropiaError en scraper/auditor 0 HTTP; P9 --force bypasea guard + evento persistido (AC4); P10 28/28 canonicalización; P11 73/73 guard tests. Regresión dirigida: 101 passed 0 failed. Nota P6: probe original usó `--report-json` (inexistente); corregido a `--output-dir` con fixture en directorio. Nota P5: URL sembrada permanece en disco porque el rechazo aborta antes de save_state — comportamiento correcto (no es re-persistencia). Evidencia: `evidence/FASE-VUP-C/` + `resumen_probes.json`. Sigue: FASE-D |
| 2026-08-31 | **FASE-D ✅** | Modo MIXTO (v4complete delegado a subagente timeout 900; parent prepara + verifica). Corrida ÚNICA E2E `v4complete --url https://www.hotelsalentoreal.com/ --output output/FASE-D_salentoreal_post_guard`: EXIT_CODE=0, pared ~3 min (17:25:02Z→17:28:14Z), "Using defaults" (log:166, equivalencia F5 con baseline H2), 0 interferencias del guard (AC3/AC8). Protocolo de Evidencia Proactiva aplicado ANTES del análisis → `evidence/FASE-VUP-D/` (docs + JSON + ZIP + `run_stdout.log` + `verificar_no_regresion.py`). Verificación JSON UTF-8: **7/7 checks PASSED** vs baseline H2 — target_id `hotel_hotelsalentoreal.com`, coherence 0.88 (=), READY_FOR_PUBLICATION, 13/13 gates perfil idéntico sin regresión, plan de assets byte-equivalente (4 assets), pains→assets idéntico, escenarios financieros byte-equal. Anomalías clasificadas infraestructura preexistente (L14): gemini 403 (LLM narrativo opcional) y PageSpeed `API key not valid` (también skipped en baseline H2). Evidencia: `evidence/FASE-VUP-D/` + `comparacion.md` + `verificacion_resultados.json`. Sigue: FASE-VERIFY |
| 2026-08-31 | **FASE-VERIFY ✅** | Modo DIRECTO (no delegable §4.6). Certificación AC1-AC8 contra evidencia real: probes Don Julio (P1-P11) + E2E Salento Real (FASE-D). Matriz AC1-AC8: 8/8 CERTIFICADOS; greps residuales 0 matches (sin listas OTA hardcodeadas, 1 definición ensure_url, 1 llamada assert_own_site); GA-1/GA-2 declarados SUPERADOS con evidencia E2E; 3 lecciones nuevas capitalizadas (L-VUP-15/16/17). Registro SIN --release exitoso; validaciones 7/7 PASSED. Evidencia: matriz completada en `10-analisis-post-implementacion.md`. Sigue: FASE-RELEASE-4.74.0 |
