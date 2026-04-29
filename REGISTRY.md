# Phase Registry

| Phase | Date | Status | Details |
|-------|------|--------|---------|
| FASE-A/B/C/D/E | 2026-04-06 | COMPLETADO | Sesion unificada. Se implementaron las 5 fases (A: Canonical Metrics/Provider Registry/Permission Modes, B: Quality Gate/Scrubber, C: OpportunityScorer, D: GSC Integration, E: Micro-Content Generator). Commit: d68b3f7. Tests: 123 nuevos. v4.25.0 |
| FASE-TRAZABILIDAD-DOCS | 2026-04-25 | COMPLETADO | Correcciones documentales "Calidad Garantizada" (9 gates, ghost cmd, Coherence variable). Commit: 83be575. Tests: 0. v4.35.1 |
| FASE-TRAZABILIDAD-RAIZ | 2026-04-25 | COMPLETADO | Unificacion detectores + cableado 9 gates + DEP-01-03 + RES-01-03 + BUG-01-02. Commits: 81a0391, e7157e2. 52 tests. v4.35.1 |
| FASE-A-PERM-FIX | 2026-04-07 | COMPLETADO | Completado ~60% faltante de Tarea 3 (Permission Modes). permission_mode integrado en TwoPhaseOrchestrator, OnboardingController, y main.py (gate antes de auditor.audit()). --permission-mode ya tiene efecto real. 19 tests pasando. Ver CHANGELOG. |
| ANALYTICS-FIX-01 | 2026-04-02 | COMPLETADO | Fix critico UnboundLocalError en main.py L1851. analytics_data movido de L1958 a L1871. Analisis D-B/D-C confirmados. v4complete exit code 0. Reporte en output/ANALYTICS_FIX_REPORT_20260402.md |
| ANALYTICS-HANDLERS-01 | 2026-04-02 | COMPLETADO | Implementados handlers para analytics_setup_guide e indirect_traffic_optimization. D-A FIX: analytics_data pasado al V4AssetOrchestrator. Assets generados: 8 (antes 7). analytics_setup_guide generado exitosamente (4952 bytes). v4.17.0 |
| FASE-3 (AMAZILIAHOTEL) | 2026-04-19 | COMPLETADO | 4 bugs corregidos: H3(faq ext .csv→.json), H4(duplicados llms.txt), H10(coherence duplicada), H12(paths Windows). Archivos: conditional_generator.py, llmstxt_generator.py, geo_enriched/llms.txt deprecated. |
| FASE-4 (AMAZILIAHOTEL) | 2026-04-19 | COMPLETADO | Asset B4 Open Graph generado. Módulo: open_graph_generator.py. Output: open_graph_meta/ESTIMATED_open_graph.html con datos GBP verificados. Integrado en v4_asset_orchestrator.py y asset_catalog.py. |
| FASE-5 (AMAZILIAHOTEL) | 2026-04-20 | COMPLETADO | 2 bugs: faq_page CSV→JSON-LD, monthly_report 27 blanks. conditional_generator.py, faq_generator.py. |
| FASE-6 (AMAZILIAHOTEL) | 2026-04-20 | COMPLETADO | Decisiones producto: WhatsApp ELIMINADO, Voice ELIMINADO, monthly_report reclasificado. Asset catalog fix. |
| FASE-PATCH-1 (AMAZILIAHOTEL) | 2026-04-20 | COMPLETADO | Places API FieldMask: agrega places.location. PlaceData: extrae lat/lng reales del API response en vez de hardcodear 0.0. _is_valid_colombia_coords rechaza (0,0). |
| FASE-1A (AMAZILIAHOTEL) | 2026-04-28 | COMPLETADO | Fix causa raiz Estado Entregables: cierra call chain site_presence_report en v4_proposal_generator.py (generate→_prepare_template_data→_generate_asset_quality_table→_confidence_to_nivel_significado). Integra SitePresenceChecker en main.py antes de proposal_gen.generate(). Fix tildes en test_proposal_alignment.py (L43, L163). 3 tests nuevos. 16/16 tests pasando. 4/4 validations. Evidencia: evidence/fase-1a/. |
