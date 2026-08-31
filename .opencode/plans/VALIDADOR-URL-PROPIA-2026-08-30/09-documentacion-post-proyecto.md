# Documentación Post-Proyecto — VALIDADOR-URL-PROPIA-2026-08-30

> Fuente de datos para FASE-RELEASE-4.74.0 (CHANGELOG + GUIA_TECNICA). Cada fase completa su columna al cerrar.

## Sección A: Módulos Nuevos
| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| Guard de URL propia | `modules/data_validation/own_site_guard.py` | Guard de URL propia: classify_url / assert_own_site / UrlNoPropiaError (exit 2, mensaje en español que nombra la plataforma) | A |

## Sección B: Funcionalidades Nuevas
| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Blocklist versionada de plataformas | `config/url_blocklist.yaml` | OTA/red social/buscador con matching por sufijo de etiquetas (anti-falsos-positivos) y regionales | A |
| Choke point en ensure_url | `main.py` | Rechazo fuerte antes de red/API para TODOS los comandos (main() lo llama antes del routing — auditoría F2) | A |
| Flag `--force` (reutilizado, main.py:173) | `main.py` | Bypass explícito con evento persistido en `.agent/memory/url_guard_force_events.json` | A |
| AC6: `last_url` no contamina el estado | `main.py` + contratos | **Sin cambio de código**: el orden `ensure_url()` (L1428) → `save_state()` (L1433) ya garantiza que una URL rechazada nunca se persiste. FASE-B lo congela con contratos que suben `main()` (incl. contrapositivo y estado envenenado legacy → rechazo que nombra el estado persistente) | B |
| Guard AC7 en hook-pdf | `modules/commercial_documents/hook_pdf_generator.py` | `extract_data(force=False)` valida `report_json["url"]` (la superficie no recibe `--url`); `generate()` reenvía el `--force` del CLI; `run_hook_pdf_mode` captura `UrlNoPropiaError` → mensaje en español + exit 2 sin escribir PDF | B |
| Defensa capa de datos | `modules/scrapers/web_scraper.py`, `modules/auditors/v4_comprehensive.py` | `assert_own_site()` como PRIMERA sentencia de `extract_hotel_data()` (fuera del `try` propio, para que el `except Exception` no trague el rechazo) y de `audit()` (antes de prints/schemas/Places); import lazy para no ciclar con `main` | B |
| `--force` sobrevive a la capa de datos (D-VUP-B1) | `modules/data_validation/own_site_guard.py` | Nuevos `ORIGEN_CAPA_DATOS` y `EXIT_CODE_URL_NO_PROPIA`; registro por proceso `FORZADAS_PROCESO` (netlocs autorizados con `--force` en el choke point) consultado SOLO por ese origen — sin él, el guard de scraper/auditor anularía el bypass del operador | B |

## Sección D: Métricas Acumulativas
| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base (def test_) | 3,631 | Preparación |
| Tests nuevos | +23 def test_ (45 casos con parametrize) | A |
| Tests nuevos | **+35 def test_ (47 casos)** → acumulado del plan **58 defs / 92 casos** en 3 archivos | B |
| Tests totales (grep `def test_` en `tests/`) | 3677 medido en FASE-B. **NO cuadra** con base + plan (3,631 + 58 = 3,689): la base 3,631 es una cifra documental de otra sesión. Conciliar con el método canónico en FASE-RELEASE antes de publicar el conteo | B |
| 28 canonicalización | verde (requisito) — 28/28 re-verificado tras B | A-C |
| Probes Don Julio | —/11 | C |
| Coherence E2E Salento Real | — (baseline 0.88) | D |
| ACs certificados | —/8 | VERIFY |

## Sección E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
|---------|--------|------|
| `config/url_blocklist.yaml` | Nuevo | A |
| `modules/data_validation/own_site_guard.py` | Nuevo | A |
| `modules/data_validation/own_site_guard.py` | Modificado (aditivo): `ORIGEN_CAPA_DATOS`, `EXIT_CODE_URL_NO_PROPIA`, `FORZADAS_PROCESO` + consulta condicionada en `assert_own_site` (D-VUP-B1) | B |
| `main.py` | ensure_url (guard + reutilización --force) | A |
| `main.py` | `run_hook_pdf_mode`: `except UrlNoPropiaError` antes del `except Exception`/`FileNotFoundError` → stderr + exit 2. **AC6: sin cambios** (el orden ensure_url→save_state ya lo garantizaba) | B |
| `modules/commercial_documents/hook_pdf_generator.py` | `extract_data(force=False)` + guard sobre `report_json["url"]`; `generate()` reenvía `force` | B |
| `modules/scrapers/web_scraper.py` | `assert_own_site` primera sentencia de `extract_hotel_data`, fuera del `try` | B |
| `modules/auditors/v4_comprehensive.py` | `assert_own_site` primera sentencia de `audit()` + `Raises:` | B |
| `tests/test_url_propia_guard.py` | Nuevo (contratos núcleo C1-C10) | A |
| `tests/test_url_propia_guard.py` | +8 `def test_` / 16 casos (AC6: paridad de mensaje, garantía de orden subiendo `main()`, cero repersistencia) — solo aditivo | B |
| `tests/test_url_propia_guard_superficies.py` | **Nuevo**: 19 `def test_` / 19 casos (AC7 librería+CLI, capa de datos, 6 contratos D-VUP-B1) con centinelas de red y fixtures `eventos_force` / `registro_forzadas_aislado` | B |
| `tests/test_guardian_ast_url_guard.py` | Nuevo (2 defs / choke point) | A |
| `tests/test_guardian_ast_url_guard.py` | Extendido a 10 defs / 14 casos: 4 superficies reales + orden guard-vs-try/prints + propagación de `force` + exit 2 en `run_hook_pdf_mode` + **exactamente 1** llamada al guard en `main.py` + contra-condición F2 (sin guards en `run_execution_mode`/`run_onboard_mode`/`run_deploy_mode`) | B |
| `evidence/FASE-VUP-B/` | 35 archivos de evidencia + `README.md` índice | B |
| `AGENTS.md` | nota guard en Comandos/Flujo (si aplica tras RELEASE) | RELEASE |

## Notas de Ejecución (por fase)
- **Preparación (2026-08-30)**: plan orquestado desde contexto verificado; lecciones Paso 0 recuperadas (memoria + QMind iah-cli-lecciones).
- **FASE-A (2026-08-30)**: TDD rojo→verde (`temp/fase_a_red.txt` → `temp/fase_a_guard.txt`, 45/45); guardián AST del choke point; 28/28 canonicalización sin tocar el normalizador; regresión dirigida data_validation 166/166 y orchestration_v4 93/93; baseline re-verificada: 14 fallos preexistentes (pricing_resolution_wrapper ×9, uno orden-dependiente — pasa aislado), 0 nuevos; validaciones 7/7; smoke CLI `v4complete --url booking…` → exit 2 sin red y sin contaminar `last_url`.
- **FASE-B (2026-08-31), modo DELEGADO (2 subagentes en paralelo + parent)**: T1 (superficie `main.py`/AC6) y T2 (hook-pdf + capa de datos) sin colisiones de archivo — `main.py` quedó exclusivamente en manos del parent. **AC6 no exigió cambio de código**: `ensure_url()` (main.py:1428) ya precede a `save_state()` (L1433), y eso quedó congelado por contratos que suben `main()` con `sys.argv` parchado y spy de `save_state`, incluido contrapositivo. **T2 cableó las 4 superficies** con import lazy. **Hallazgo no previsto por el plan**: la defensa de capa de datos habría anulado `--force` (esas funciones no reciben `args.force`) → el parent decidió **D-VUP-B1** (`FORZADAS_PROCESO` por netloc, consultado solo por `ORIGEN_CAPA_DATOS`), con rojo TDD previo (`ImportError: cannot import name 'ORIGEN_CAPA_DATOS'`) y 6 contratos que además prueban que el bypass no se filtra a otros orígenes ni duplica eventos. Integrado: **120 passed** (92 casos del guard + 28 canonicalización); regresión dirigida hook-pdf/scrapers 76✓+4s y auditor/never-block 125✓+2s; mutation check (`temp/mutation_check_t1.py` → evidencia) para descartar falso verde en los contratos de orden; smokes: `hook-pdf --dry-run` con el reporte REAL de Salento Real → exit 0, reporte con URL de Booking → exit 2 sin PDF, `v4complete --url booking…` → exit 2. Greps de residuo: 1 definición de `ensure_url`, 1 llamada a `assert_own_site` en `main.py`. Validaciones `--quick` 6/7 (único fallo Version Sync = drift documental preexistente, no código). Evidencia indexada en `evidence/FASE-VUP-B/`.
