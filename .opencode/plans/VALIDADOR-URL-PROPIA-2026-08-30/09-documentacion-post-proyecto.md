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
| Flag `--force` (reutilizado, main.py:172) | `main.py` | Bypass explícito con evento persistido en `.agent/memory/url_guard_force_events.json` | A |
| Saneamiento last_url | `main.py` | Garantía de orden (rechazo precede save_state); aviso al reinyectar desde estado persistente | B |
| Guard hook-pdf | `hook_pdf_generator.py` | Valida `report_json["url"]` (no recibe --url) | B |
| Defensa capa de datos | `web_scraper.py`, `v4_comprehensive.py` | assert_own_site protege llamadores de librería | B |

## Sección D: Métricas Acumulativas
| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base (def test_) | 3,631 | Preparación |
| Tests nuevos | +23 def test_ (45 casos con parametrize) | A |
| Tests nuevos | — | B |
| 28 canonicalización | verde (requisito) | A-C |
| Probes Don Julio | —/11 | C |
| Coherence E2E Salento Real | — (baseline 0.88) | D |
| ACs certificados | —/8 | VERIFY |

## Sección E: Archivos Afiliados Actualizados
| Archivo | Cambio | Fase |
|---------|--------|------|
| `config/url_blocklist.yaml` | Nuevo | A |
| `modules/data_validation/own_site_guard.py` | Nuevo | A |
| `main.py` | ensure_url (guard + reutilización --force) | A |
| `main.py` | saneamiento last_url | B |
| `modules/commercial_documents/hook_pdf_generator.py` | guard extract_data | B |
| `modules/scrapers/web_scraper.py`, `modules/auditors/v4_comprehensive.py` | assert_own_site | B |
| `tests/test_url_propia_guard.py`, `tests/test_guardian_ast_url_guard.py` | Nuevos | A-B |
| `AGENTS.md` | nota guard en Comandos/Flujo (si aplica tras RELEASE) | RELEASE |

## Notas de Ejecución (por fase)
- **Preparación (2026-08-30)**: plan orquestado desde contexto verificado; lecciones Paso 0 recuperadas (memoria + QMind iah-cli-lecciones).
- **FASE-A (2026-08-30)**: TDD rojo→verde (`temp/fase_a_red.txt` → `temp/fase_a_guard.txt`, 45/45); guardián AST del choke point; 28/28 canonicalización sin tocar el normalizador; regresión dirigida data_validation 166/166 y orchestration_v4 93/93; baseline re-verificada: 14 fallos preexistentes (pricing_resolution_wrapper ×9, uno orden-dependiente — pasa aislado), 0 nuevos; validaciones 7/7; smoke CLI `v4complete --url booking…` → exit 2 sin red y sin contaminar `last_url`.
