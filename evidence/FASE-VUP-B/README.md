# Evidencia FASE-B — VALIDADOR-URL-PROPIA-2026-08-30

Superficies secundarias del guard: saneamiento `last_url` (AC6), hook-pdf (AC7) y
defensa en capa de datos (`WebScraper.extract_hotel_data`, `V4ComprehensiveAuditor.audit`).
Ejecutada 2026-08-31 en modo DELEGADO (2 subagentes en tracks + parent integra).

| Archivo | Qué prueba |
|---------|-----------|
| `fase_b_track1_red.txt` / `_baseline.txt` | Track 1: `_baseline.txt` = 43 passed del archivo antes de tocarlo; `_red.txt` = corrida de mutación (los 16 contratos nuevos salen verdes a la primera porque FASE-A ya ordena `ensure_url` antes de `save_state`, así que el "rojo" se demuestra mutilando el guard en memoria, no esperando un fallo) |
| `fase_b_track1_conjunto.txt` / `_conjunto_inverso.txt` | Corrida combinada de los 3 archivos ANTES de D-VUP-B1: 7 failed / 68 passed. La lista `FAILED` es **idéntica en orden directo e inverso** (verificado con diff) → los rojos son reales, no fuga de estado entre archivos (descarte de L-VUP-1) |
| `fase_b_track1_green.txt` | `tests/test_url_propia_guard.py` 59 passed (43 FASE-A + 16 FASE-B) |
| `mutation_check_t1.py` | Anti-falso-verde: quitar el guard o limitarlo a v4complete pone rojos M1/M2/M3 (ejecutado en memoria, no en pytest) |
| `fase_b_parent_dvupb1_red.txt` / `_green.txt` | D-VUP-B1 (--force del choke point sobrevive en capa de datos): rojo por ImportError → 6 passed |
| `fase_b_track2_red.txt` / `_green.txt` | Track 2: 5 failed (DID NOT RAISE ×4 + `extract_data() force`) → 16 passed |
| `fase_b_track2_diff.txt` | Dif de los 3 archivos de producción del Track 2 |
| `fase_b_track2_baseline_superficies.txt` | Estado inicial del archivo de superficies |
| `fase_b_t3_guardian_contracts.txt` | Integración parent: guardián AST (4 superficies + F2) + 3 archivos de contratos + canonicalización = 120 passed |
| `fase_b_t3_hookpdf_scraper.txt` | Regresión hook-pdf + scrapers: 76 passed, 4 skipped |
| `fase_b_t3_auditor_neverblock.txt` | Regresión auditor + never-block architecture: 125 passed, 2 skipped |
| `fase_b_track2_test_*.txt` | Regresión archivo-por-archivo (lección L11: nunca suites de directorio), incluye los 3 archivos con fixtures de dominios bloqueados |
| `fase_b_smoke_setup.txt` | Fixture CLI derivado del reporte real de Salento Real (url original → booking) |
| `fase_b_smoke_cli.txt` | SMOKE A hook-pdf OTA → exit 2 sin PDF · SMOKE B hook-pdf reporte real propio → exit 0 · SMOKE C v4complete OTA → exit 2 |
| `fase_b_smoke_ownsite.txt` / `_v4complete.txt` | Salidas completas de los smokes B y C |
| `fase_b_validations.txt` | `run_all_validations.py --quick` → 6/7; el único fallo es Version Sync (drift documental preexistente en HEAD: AGENTS.md L1 dice `agents_version: v4.71.0` vs VERSION.yaml 4.73.0; FASE-B no tocó docs) |
| `fase_b_registry.txt` | `log_phase_completion.py --fase "FASE-B (VALIDADOR-URL-PROPIA)" --tests 47 --check-manual-docs` → "(R) Fase registrada exitosamente" en REGISTRY.md, sin `--release` (fases intermedias). Los (X) de CHANGELOG/GUIA_TECNICA/Version Sync son de FASE-RELEASE por diseño |
| `fase_b_domain_primer.txt` | `doctor.py --regenerate-domain-primer` → exit 0 (197 archivos, 379 clases, 25 modulos). DOMAIN_PRIMER.md quedo **sin diff** en git: FASE-B no agregó módulos nuevos, solo funciones/superficies dentro de módulos ya mapeados |
| `fase_b_final_green.txt` | Verdeo final pre-commit: `test_url_propia_guard` + `test_url_propia_guard_superficies` + `test_guardian_ast_url_guard` + `test_target_id_canonicalization` → **120 passed** (92 casos del guard + 28 canonicalización), exit 0 |
