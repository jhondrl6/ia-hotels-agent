# Checklist Maestro de Implementación — COPYWRITING REFACTOR

> **Plan**: COPYWRITING-REFACTOR
> **Actualizado**: 2026-05-25 (FASE-COPY-C ✅)
> **Convención**: [ ] = pendiente, [x] = completado, [~] = en progreso

---

## FASE-COPY-A: Template Restructuring + Generator Fixes

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Restructurar `diagnostico_v6_template.md`: Vista Gerencia (líneas 1-80) + Anexo Técnico (líneas 81+) | [ ] |
| T2 | Restructurar `propuesta_v6_template.md`: Finanzas honestas + OTA narrative + Quick wins del dueño | [ ] |
| T3 | Fix `_build_scenario_table_rows()`: clamp valores negativos + validar orden conservador < realista < optimista | [ ] |
| T4 | Fix `_build_financial_placeholders()`: consistencia de tier entre frontmatter, texto y financial_json | [ ] |

**Criterios de completitud:**
- [ ] Template V6 diagnóstico: secciones 1-6 en lenguaje dueño, sección 7+ anexo técnico
- [ ] Template V6 propuesta: sin "Aparece último / No aparece" absolutos no soportados; narrativa OTA presente
- [ ] `_build_scenario_table_rows`: clamp si optimista < realista o < 0 → mostrar "Equilibrio / Sin pérdida neta"
- [ ] Financial placeholders: tier unificado desde `financial_breakdown.evidence_tier` en frontmatter + texto + disclaimer

---

## FASE-COPY-B: Commercial Gates + Content Validation Rules

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Crear `modules/quality_gates/commercial_gate.py` con gates bloqueantes + advisory | [x] |
| T2 | Agregar regla "IA Bloqueada" → "IA sin guía" cuando `blocked_crawlers == []` | [x] |
| T3 | Integrar commercial gates en v4_diagnostic_generator y v4_proposal_generator | [x] |

**Criterios de completitud:**
- [x] `modules/quality_gates/commercial_gate.py` existe con al menos 5 gates (3 bloqueantes, 2 advisory)
- [x] Gate `scenario_order_valid`: bloquea si optimista < realista o realista < conservador
- [x] Gate `roi_positive_or_onboarding`: bloquea si ROI < 1.0X y no hay plan de onboarding alternativo
- [x] Gate `ia_blocked_claim_verified`: bloquea si "bloqueada" aparece y blocked_crawlers está vacío
- [x] Gate `whatsapp_lead`: advisory — advierte si WhatsApp no es el primer gancho
- [x] Gate `ota_narrative_present`: advisory — advierte si no hay menciones de Booking/Expedia en propuesta
- [x] "IA Bloqueada" → "IA sin guía" se corrige en `_pain_to_brecha()` (L2625) — fuente de datos, no regex
- [x] `commercial_gate.validate()` se llama desde ambos generators

---

## FASE-COPY-C: E2E v4complete Validation

|| # | Tarea | Estado |
||---|-------|--------|
|| T1 | Preparar ejecución E2E: verificar que COPY-A y COPY-B están completadas | [x] |
|| T2 | Ejecutar `./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/` | [x] |
|| T3 | Verificar output contra los 7 gates comerciales de Copywriting.jsonl | [x] |

**Criterios de completitud:**
- [x] v4complete ejecutado exitosamente para Hotel Castilla Real (coherencia 0.81)
- [x] Coherence score ≥ 0.80 (score: 0.81)
- [x] Escenario optimista NO negativo (optimista = $3.741.696 COP/mes, clamp activo)
- [x] Sin "IA Bloqueada" si blocked_crawlers vacío (0 matches grep 'bloqueada')
- [x] Propuesta con OTA narrative (13 menciones de booking/expedia/comisión/ota)
- [x] WhatsApp como gancho #1 en diagnóstico (primera sección breached)
- [x] Disclaimers de tier consistentes (Tier B en escenarios, coexistencia coherente con Tier A/C en definiciones)
- [x] Evidencia guardada en `evidence/COPY-C/`
- [x] Validación de cumplimiento registrada en `validation_report.md`

---

## FASE-COPY-RELEASE: Documentación y Cierre

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Diagnóstico inicial + sync versions | [ ] |
| T2 | CHANGELOG.md + GUIA_TECNICA.md | [ ] |
| T3 | Skills/workflows + SYSTEM_STATUS.md | [ ] |
| T4 | DOMAIN_PRIMER + symlink + validación final + commit | [ ] |

**Criterios de completitud:**
- [ ] `sync_versions.py` ejecutado (VERSION.yaml → 6 archivos)
- [ ] CHANGELOG.md actualizado con entrada COPYWRITING-REFACTOR
- [ ] GUIA_TECNICA.md con nota técnica por fase
- [ ] `log_phase_completion.py --fase FASE-COPY-RELEASE --check-manual-docs` ejecutado
- [ ] `run_all_validations.py --quick` pasa 4/4
- [ ] `validate_document_integration.py` pasa
