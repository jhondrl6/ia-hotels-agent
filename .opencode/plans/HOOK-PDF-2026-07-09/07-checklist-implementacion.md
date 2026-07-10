# Checklist de Implementación — HOOK-PDF-2026-07-09

> Marcar `[x]` al completar cada tarea. Actualizar al cierre de cada sesión.

## FASE-1: Setup + Dataclass + Templates ✅ (2026-07-09)
- [x] 1.1 Dependencias instaladas (weasyprint 69.0 + pyyaml 6.0.3 + libpango + libcairo)
- [x] 1.2 HookPDFData dataclass creado en data_structures.py (línea 422, 34 campos)
- [x] 1.3 HookPDFData exportado en __init__.py (import + __all__)
- [x] 1.4 templates/hook_template.md creado (HTML, 191 líneas, 34 placeholders únicos)
- [x] 1.5 templates/hook_styles.css creado (@page A4, 2 páginas, hook figure 28pt)

## FASE-2: Generator + CLI (MAYOR COMPLEJIDAD) ✅ (2026-07-09)
- [x] 2.1 hook_pdf_generator.py creado (HookPDFGenerator: extract/validate/render/generate)
- [x] 2.2 HookPDFGenerator exportado en __init__.py
- [x] 2.3 main.py: comando hook-pdf + args (--output-dir, --template, --style, --dry-run, --force, --verbose)
- [x] 2.4 Smoke test: import OK + --help OK

## FASE-3: Tests ✅ (2026-07-09)
- [x] 3.1 test_hook_pdf_generator.py creado (fixtures + 36 tests parametrizados)
- [x] 3.2 Test extract_data (8 tests: hotel, financial, GBP, scores, brechas, pricing, tier, ROI)
- [x] 3.3 Test validate_data (4 tests: OK, missing required, empty optional, invalid tier, accent warning)
- [x] 3.4 Test render_html (3 tests: cero placeholders, hotel name, scores present)
- [x] 3.5 Test generate (2 tests: dry_run no genera PDF, force=True genera PDF)
- [x] 3.6 Test formato COP (11 tests parametrizados: int, float, str, None, non-numeric)
- [x] 3.7 Test slug (5 tests parametrizados: lowercase, acentos, espacios, especiales)
- [x] 3.8 Test glob pattern + missing file (2 tests)
- [x] 3.9 pytest -v pasa 36/36 sin regresiones (256 tests en suite completa)

## FASE-4: E2E Luxorhotel ✅ (2026-07-10)
- [x] 4.1 output/v4_complete/ regenerado vía v4complete --url luxorhotel (176s, exit 0)
- [x] 4.2 hook-pdf ejecutado → luxorhotel_gancho.pdf generado (27,552 bytes)
- [x] 4.3 PDF: 2 páginas exactas (PyPDF2 verified)
- [x] 4.4 PDF: cero {{...}} sin reemplazar (verified via text extraction)
- [x] 4.5 PDF: cifra fuga 28pt (CSS hook-figure: font-size 28pt ≥ 24pt)
- [x] 4.6 PDF: disclaimer Tier B visible ("(Estimación basada en datos de la región...)" en página 1)
- [x] 4.7 Datos coinciden con §3.2 (34 campos cross-validados contra diagnostic.md + proposal.md + JSON)
- [x] 4.8 Tiempo 1.486s (<30s)
- [x] 4.9 --dry-run funciona (datos extraídos, HTML 12,732 chars, sin generar PDF)

## FASE-5: RELEASE
- [ ] 5.1 CHANGELOG.md: v4.49.0 entry
- [ ] 5.2 VERSION.yaml: 4.49.0
- [ ] 5.3 AGENTS.md: módulos + comandos actualizados
- [ ] 5.4 sync_versions.py --check + apply
- [ ] 5.5 doctor.py --regenerate-domain-primer
- [ ] 5.6 pre-commit run --all-files
- [ ] 5.7 log_phase_completion.py
