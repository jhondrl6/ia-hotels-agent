# Plan Maestro — VALIDADOR-URL-PROPIA-2026-08-30

> **ID**: VALIDADOR-URL-PROPIA-2026-08-30 | **Versión objetivo**: 4.74.0
> **Executor**: `phased_project_executor.md` v2.17.0 | **Contexto**: `/.opencode/context/Historico/CONTEXT-GAP-URL-NO-PROPIA-SONDA-2026-08-29.md`
> **Escala de complejidad**: Baja → Baja-Media → Media → Alta → MÁXIMA

## 1. Objetivo

Hacer explícito y bloqueante el invariante implícito "URL de entrada ≡ sitio web propio del hotel" (RC1): guard de entrada blocklistado en todos los comandos con URL, `--force` explícito, saneamiento de `last_url`, guard en hook-pdf y defensa en capa de datos — sin tocar la semántica del normalizador (ortogonalidad N9) y con demostración doble: rechazo sobre URLs de Finca Hotel Don Julio (OTA/Instagram) y no-regresión del v4complete tradicional sobre Hotel Salento Real.

## 2. Fases y complejidad

| Fase | Objetivo | Complejidad | Modo | Tareas (R3) | Comando largo | Riesgo principal |
|------|----------|-------------|------|-------------|---------------|------------------|
| FASE-A | Núcleo del guard (contratos TDD, blocklist config, `own_site_guard`, `ensure_url()`, `--force`) | **Media** | DIRECTO | 3 + cierre | No | Romper los 28 tests de canonicalización por tocar el normalizador |
| FASE-B | Superficies secundarias (`last_url`, hook-pdf, capa datos) | **Baja-Media** | DELEGADO (2 subagentes + parent integra) | 3 + cierre | No | Divergencia de mensajes/exit code respecto a FASE-A (mitigado: los llamadores son single-line a la misma API de FASE-A) |
| FASE-C | Verificación empírica Don Julio + regresión | **Baja** | DELEGADO | 2 + cierre | No | Falsos positivos por red/OTA durante probes |
| FASE-D | E2E v4complete Salento Real (única corrida) | **Baja** (impl) | MIXTO (comando delegado) | 3 tareas + 1 comando largo | Sí | Ejecutar con defaults es REQUERIDO para equivalencia con baseline H2 (auditoría F5: H2 corrió con defaults) |
| FASE-VERIFY | Certificación AC1-AC8 contra evidencia | **Baja-Media** | DIRECTO (no delegable §4.6) | verificación + docs | No | Declarar SUPERADO con solo tests unitarios (L29) |
| FASE-RELEASE-4.74.0 | Cierre documental oficial | **Baja** | DELEGABLE | E1-E8b | No | Omitir `validate_agents_md.py` (memoria CONTRIBUTING) |

## 3. Desglose de tareas por fase (contador R3)

### FASE-A (Media — DIRECTO)
1. Línea base: re-verificar 12 tests rojos preexistentes + 28 canonicalización (registrar en 10-analisis). [investigación]
2. Contratos TDD (`tests/test_url_propia_guard.py`, rojos primero) + implementación: `config/url_blocklist.yaml`, `modules/data_validation/own_site_guard.py`, cableado en `ensure_url()` (main.py:216-225) **DESPUÉS de la rama de reinyección de `last_url`** (auditoría: la reinyección L222 ocurre dentro de ensure_url; el guard debe validar también la URL reinyectada), `--force` **reutilizando el flag global existente** (main.py:172; prohibido re-crearlo) con warning persistido en el archivo dedicado `.agent/memory/url_guard_force_events.json`, guardián AST mínimo. Contrato extra (auditoría F6): dominios parecidos (`bookingbogota.com`) PASAN — matching por sufijo de etiquetas, no substring. [fix]
3. Tests verdes + regresión dirigida (canonicalización 28 + suites tocadas). [verificación]
✔ 3 tareas ≤ 4. Sin comando largo.

### FASE-B (Baja-Media — DELEGADO)
1. Track 1 (subagente): saneamiento `last_url` — garantía de orden (el rechazo en `ensure_url` precede a `save_state` main.py:1411, verificarlo con spy) + aviso con mención del estado persistente al reinyectar URL bloqueada + NO re-persistir bloqueadas. **Sin guards por modo** (auditoría F2: `main()` llama `ensure_url()` para TODOS los comandos en L1406; el tuple L217 solo excluye la reinyección) + contratos ensure_url por comando (`execute`/`onboard`/`deploy` con URL bloqueada → rechazo).
2. Track 2 (subagente): guard hook-pdf sobre `report_json["url"]` (hook_pdf_generator.py:179-213) + `assert_own_site()` en `WebScraper.extract_hotel_data()` y `V4ComprehensiveAuditor.audit()` (cubre llamadores de librería y handlers del harness tipo `_spark_handler`).
3. Parent: integrar, extender guardián AST a las 4 superficies reales (ensure_url + extract_hotel_data + audit + extract_data), unificar mensajes/exit code, tests + regresión dirigida.
✔ 3 tareas ≤ 4. Tracks secuencializables sobre main.py (overlap de archivo → integrar en parent, L12).

### FASE-C (Baja — DELEGADO)
1. Sondas P1-P11 (tabla §4) con captura en `evidence/FASE-VUP-C/` (exit codes, mensajes, tiempos, ausencia de llamadas API).
2. Regresión: `test_url_propia_guard.py`, `test_target_id_canonicalization.py` (28), suites de hook-pdf/onboarding/main tocadas; salida a archivo.
✔ 2 tareas ≤ 4. Sin comando largo (los rechazos abortan antes de red).

### FASE-D (Baja — MIXTO)
1. Preparación: `--output output/FASE-D_salentoreal_post_guard/`, **verificar que NO exista YAML de onboarding de Salento Real (auditoría F5: el baseline H2 corrió con defaults; la equivalencia exige defaults — no poblar `clientes/`)**, grep de símbolos no definidos en ramas nuevas. [investigación]
2. Subagente ejecuta `v4complete --url https://www.hotelsalentoreal.com/` (timeout 900, "ejecutar y reportar, no interpretar"). [comando largo]
3. Parent: Protocolo de Evidencia Proactiva → comparación vs `output/salentoreal_final_v4c_h2/` (coherence, gates, plan pains→assets, target_id `hotelsalentoreal.com`). [verificación]
✔ 3 tareas + 1 comando largo = permitido (R3).

### FASE-VERIFY (Baja-Media — DIRECTO)
Metodología mínima §4.6: leer evidencia FASE-C/D → verificar AC1-AC8 contra output real → greps residuales → matriz del 10-analisis → ≥3 lecciones → `log_phase_completion.py` SIN `--release` + `run_all_validations.py --quick`. **NO modifica código, NO ejecuta v4complete.**

### FASE-RELEASE-4.74.0 (Baja — DELEGABLE)
E1-E8b del executor + pasos obligatorios de CONTRIBUTING (memoria): `validate_agents_md.py`, `validate_document_integration.py`, audit de conteos README (`pytest --collect-only`), `log_phase_completion.py --fase FASE-RELEASE-4.74.0`.

## 4. Sondas de verificación (FASE-C) — URLs reales de Finca Hotel Don Julio

| # | Comando / acción | Resultado esperado |
|---|------------------|--------------------|
| P1 | `v4complete --url https://www.booking.com/hotel/co/finca-don-julio.es.html` | exit 2, mensaje español ("sitio web propio"/"agregador"), duración < 30 s, sin artefactos nuevos en `output/`, sin marcadores de scraping/auditoría en stdout |
| P2 | `v4complete --url https://www.instagram.com/fincahoteldonjulio` | igual que P1 (red social) |
| P3 | `onboard --url <booking>` y `execute --url <booking>` | mismo rechazo (vía `ensure_url`, que cubre todos los comandos) |
| P4 | `deploy --url <instagram>` | mismo rechazo |
| P5 | **Sembrar estado** con `MemoryManager().save_state({'last_url': <booking>})` (simula estado legacy envenenado) → comando sin `--url` | rechazo con mención "estado persistente"; verificar en `current_state.json` que la URL bloqueada NO fue re-persistida; **restaurar** `last_url` a hotelsalentoreal.com al terminar |
| P6 | `hook-pdf` contra report fixture con `url` de booking | rechazo claro |
| P7 | Script: `WebScraper().extract_hotel_data(url_booking)` | excepción del guard, 0 peticiones HTTP |
| P8 | Script: `V4ComprehensiveAuditor` + URL OTA | excepción del guard, 0 llamadas Places |
| P9 | `v4complete --url <booking> --force` (captura con timeout ~45 s; el proceso se mata tras confirmar) | NO lanza el guard; warning persistido en el archivo dedicado `.agent/memory/url_guard_force_events.json` (inspección con Python); evidencia de que el pipeline pasó el guard |
| P10 | `pytest tests/test_target_id_canonicalization.py` | 28/28 PASSED |
| P11 | `pytest tests/test_url_propia_guard.py` + regresión dirigida | PASSED, salida a archivo |

## 5. Presupuesto de iteraciones (guía por fase)

| Fase | Fijo (~) | Trabajo específico | Total estimado |
|------|----------|--------------------|----------------|
| A | 26-30 | TDD + guard: 25-30 | 51-60 (ajustado — si se agota, marcar ⏳ INCOMPLETA) |
| B | 26-30 | Integrar 2 tracks: 15-20 | 41-50 |
| C | 26-30 | Probes + pytest: 10-15 | 36-45 |
| D | 26-30 | Prep + comando (1 tool call) + comparación: 15-20 | 41-50 |
| VERIFY | 26-30 | Certificación: 15-20 | 41-50 |
| RELEASE | 26-30 | E1-E8b: 12-18 | 38-48 |

## 6. Selección de modelo (guía rápida)

- **DIRECTO obligatorio**: FASE-A (decisión arquitectónica), FASE-VERIFY (juicio, §4.6).
- **DELEGADO**: FASE-B (tracks localizados), FASE-C (probes), FASE-RELEASE (docs/scripts).
- **MIXTO**: FASE-D (v4complete delegado con evidencia-first; análisis en parent — L30).
- Regla prevalente: si aparece una decisión arquitectónica no prevista en una fase delegada, el parent la toma (nunca el subagente).
