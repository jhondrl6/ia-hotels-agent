# Documentacion Post-Proyecto

> **Plan**: PLAN-REFACTOR-TERMALES-20260508.md  
> **Proposito**: Acumular datos por fase para generacion de CHANGELOG y GUIA_TECNICA en FASE-RELEASE.

---

## Seccion A: Modulos Nuevos

| Modulo | Archivos | Descripcion | Fase |
|--------|----------|-------------|------|
| evidence/fase-2-B/ | Evidencia v4complete Termales (11 archivos) | FASE-2-B |

---

## Seccion B: Funcionalidades Nuevas

| Feature | Modulo | Descripcion | Fase |
|---------|--------|-------------|------|
| Template conditionals | v4_proposal_generator | Pre-procesador {{if}}...{{endif}} antes de safe_substitute | FASE-1-A |
| Coherence truth source | coherence_validator | Parametro generated_assets para verificar contra assets realmente generados | FASE-1-A |
| Pending marker detection | content_scrubber | Rule 6: detecta [PENDING_*] y bloquea publicacion (block_publication=True) | FASE-1-B |
| Dynamic assets table | monthly_report_generator | _generate_assets_table genera tabla desde asset_generation_report.json (no hardcoded) | FASE-1-B |
| SitePresence hardening | publication_gates | Log completo + status unknown/indeterminate en vez de None/missing | FASE-2-A |
| Audit-aware traffic | indirect_traffic_optimization_gen | Lee audit_report.json para recomendaciones contextualizadas | FASE-2-A |
| Site-aware FAQ | faq_gen | Scraping previo del sitio para FAQs especificas por servicio | FASE-2-A |
| Alignment gate policy | publication_gates | BLOCKED cuando alignment < 50% (antes: siempre WARNING) | FASE-3 |
| Tier C onboarding gate | publication_gates | Bloquea propuestas Tier C sin datos reales (nuevo gate) | FASE-3 |

---

## Seccion D: Metricas Acumulativas

| Metrica | Valor | Fase |
|---------|-------|------|
| Validaciones pre-refactor | 5/5 PASS | FASE-PRE |
| Archivos CRLF normalizados | 24 | FASE-PRE |
| Tests nuevos FASE-1-A | 11 | FASE-1-A |
| Tests nuevos FASE-1-B | 5 | FASE-1-B |
| Tests nuevos FASE-2-A | 24 | FASE-2-A |
| v4complete metricas pasadas | 2/7 | FASE-2-B |
| Veredicto E2E | PARCIAL | FASE-2-B |

---

## Seccion E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| v4_proposal_generator.py | _preprocess_conditionals + _render_template actualizado | FASE-1-A |
| coherence_validator.py | _check_promised_assets_exist con generated_assets | FASE-1-A |
| content_scrubber.py | Rule 6 _fix_pending_markers, block_publication en ScrubResult | FASE-1-B |
| monthly_report_generator.py | _generate_assets_table data-driven desde asset_generation_report.json | FASE-1-B |
| publication_gates.py | FIX-9: alignment < 50% → BLOCKED + FIX-10: nuevo gate tier_c_onboarding_required | FASE-3 |
| proposal_asset_alignment.py | AlignmentReport.indeterminate + verify_proposal_asset_alignment maneja unknown | FASE-2-A |
| indirect_traffic_optimization_gen.py | generate() acepta audit_report_path + diagnostico data-driven | FASE-2-A |
| faq_gen.py | _extract_services_from_site() + generate_list() enriquecido con servicios | FASE-2-A |

---

*Este archivo se edita despues de cada fase completada. FASE-RELEASE usa estos datos para generar CHANGELOG y GUIA_TECNICA oficiales.*
