# FASE-SR-A — Notas de Sesión (Evidencia)

**Plan**: SR-PIPELINE-FIXES-2026-08-27 · **Fase**: SR-A (helper único `compute_unresolved()` + guardián AST L-SR1)
**Sesión**: agente 2026-08-28 · **Delegación**: ❌ DIRECTO (venv) · **Iteraciones**: ~30 (R2: máx. 60)

## Contenido de esta carpeta

| Archivo | Descripción |
|---------|-------------|
| `diff_modulos_fase_sr_a.patch` | Diff de `alignment_result.py` + `publication_gates.py` + `delivery_quality_report.py` |
| `diff_test_alignment_result.patch` | Diff de `tests/quality_gates/test_alignment_result.py` (TestCorridaCSemantics) |
| `test_main_static_guards.py` | Copia del test guardián AST L-SR1 (archivo nuevo) |
| `fase_sr_a_tests.txt` | Pytest: `test_alignment_result.py` + `test_main_static_guards.py` — 14 PASSED |
| `fase_sr_a_gates.txt` | Regresión `tests/quality_gates/test_publication_gates.py` — 56 PASSED |
| `fase_sr_a_delivery.txt` | Regresión contrato delivery (delivery_quality_report + alignment) — 47 PASSED |
| `fase_sr_a_assets.txt` | Regresión matriz + site verification — 31 PASSED |
| `fase_sr_a_validations.txt` | `run_all_validations.py --quick` — 5/6 (nota de desviación abajo) |
| `greps_residuos.txt` | Greps de residuos (análisis abajo) |

## Resultados

- **Tests**: 148 ejecutados en procesos aislados (14 + 56 + 47 + 31), 0 fallos, 0 regresiones. **6 tests nuevos**: 3 de `TestCorridaCSemantics` (contrato corrida C: ambos paths → `unresolved=1`; coherencia aritmética con `no_breach`; path legacy) + 3 del guardián AST (`exists` / `py_compile` / `no forbidden symbols`).
- **Greps (L2)**:
  - `len(report.missing)` en módulos de conteo G9 (`modules/quality_gates/`): **0**.
  - `unresolved_count = sum`: **0** en modules+tests — todo el conteo pasa por `AlignmentResult.compute_unresolved()`.
  - `logger\.` en `main.py` (AC13): **0**.
  - `len(report.missing)` global: 16 matches legítimos — 1 display-string en `proposal_asset_alignment.py:376` (`get_alignment_summary()`, contrato de display de `AlignmentReport`, NO es conteo G9) + 15 asserts en tests del contrato `AlignmentReport` (5×`test_proposal_alignment.py`, 5×`test_site_presence_hardening.py`, 5×`test_gate_presence.py`). **0 conteos paralelos del unresolved G9** — criterio T4 SATISFECHO.
- **`run_all_validations.py --quick`**: **5/6**. Única falla: `Version Sync` (headers de AGENTS.md / .cursorrules / docs/GUIA_TECNICA.md). Es **preexistente**: `git status` confirma que FASE-SR-A no tocó ningún archivo de versión ni docs oficiales; `version_consistency_checker.py` = TODO SINCRONIZADO (CHANGELOG = VERSION.yaml = 4.72.2). Se resuelve en **E2 de FASE-RELEASE-4.73.0** (`sync_versions.py`), según el flujo documental obligatorio.

## Decisiones (T2)

1. **Unificación por builder compartido**: el gate (`publication_gates._proposal_asset_alignment_gate`) deriva los estados semánticos con el MISMO builder que produce `proposal_asset_matrix.json` — `AssetAlignmentMatrix.build(DeliveryContext(), pain_ledger, generated_assets)` desde el `pain_ledger` que ya viaja en el assessment (AssessmentBuilder). Sin duplicar el criterio pain-matching (L-NC10). Fallback narrow con `logger.warning` a la semántica legacy si la derivación falla (never-block; `run_all` ya envuelve cada gate en try/except → BLOCKED).
2. **Bucket `no_breach`**: el mensaje G9 queda aritméticamente coherente: `effective_total + unresolved + no_breach == promised_services_total` (corrida C: 3 + 1 + 3 = 7). NO_BREACH ("sin costo (fallback)") no es brecha ni cobertura.
3. **Regla única de conteo**: `UNRESOLVED_STATUSES = ("MISSING_ASSET", "GENERIC_DRAFT")` + cross-reference SitePresence (`status == "exists"`) — misma semántica que `AssetAlignmentMatrix.is_delivery_ready()`.
4. **La decisión de bloqueo del gate NO cambia** (usa `effective_alignment` del AlignmentReport) — eso es FASE-SR-B; SR-A unifica solo el CONTEO (hallazgo N1).
5. **Guardián AST (D-PF5)**: `FORBIDDEN_SYMBOLS = ["logger"]` sobre `main.py` con `ast.walk` (Name + Attribute), no regex (L7: main.py menciona "logger" en comentarios L1777/L2976 — el parser evita el falso positivo). `py_compile` a .pyc efímero en `tmp_path` (no contamina `__pycache__`).

## Escenario de test (corrida C, 7 servicios)

2 LINKED (org_schema conf 0.9, faq_page conf 0.85) + 1 MISSING_ASSET con pain (hotel_schema) + 3 NO_BREACH (SEO Local, WhatsApp, Open Graph) + llms_txt (NO_BREACH en matriz) resuelto por SitePresence (`status: exists`, formato canónico `results` + claves planas) → **unresolved esperado = 1 en AMBOS reportes** (fin de la divergencia 4-vs-1 del mismo run).
