# 06-checklist-implementacion-2-PATCH

> **Plan**: `PLAN-FASE-2-PATCH-TERMALES-20260508.md`
> **Origen**: AUDITORIA_FASE-2-B_TERMALES_20260508.md
> **Target**: 7/7 métricas de éxito

---

## Estado Global

|| Fase | Estado | Sesión | Fecha |
|------|--------|--------|-------|
| FASE-2-PATCH-A | ✅ Completada | 20260508 | 2026-05-08 |
| FASE-2-PATCH-B | ✅ Completada | 20260508 | 2026-05-08 |
| FASE-2-PATCH-C | ✅ Completada | 20260509 | 2026-05-09 |

---

## FASE-2-PATCH-A: Fixes locales de código

### PATCH-1: Template conditionals OR
- [ ] Leer `v4_proposal_generator.py:1103-1121`
- [ ] Implementar pre-procesamiento de `or` en `_preprocess_conditionals()`
- [ ] Test: data `{'financial_evidence_tier': 'A'}` → bloque A/B incluido
- [ ] Test: data `{'financial_evidence_tier': 'C'}` → bloque A/B excluido
- [ ] Test: output NO contiene `{{if}}` ni `{{endif}}`
- [ ] Tests existentes siguen pasando

### PATCH-2: Coherence generated_assets wiring
- [ ] `coherence_validator.py`: validate() acepta `generated_assets`
- [ ] L141: pasa `generated_assets` a `_check_promised_assets_exist()`
- [ ] `main.py`: orchestrator pasa `generated_assets` real
- [ ] Test: con `generated_assets={"whatsapp_button": {}, ...}` → score < 1.0

### PATCH-4: Scrubber regex expand
- [ ] `content_scrubber.py:284`: pattern = `r'\[PENDING_[A-Z_]+[^\]]*\]'`
- [ ] Test: `[PENDING_ONBOARDING: usp/description]` → detectado
- [ ] Test: `[PENDING_ONBOARDING]` → sigue detectado (no regresión)

### Cierre FASE-A
- [ ] Todos los tests pasan
- [ ] `log_phase_completion.py` ejecutado
- [ ] Plan actualizado

---

## FASE-2-PATCH-B: Fixes de orquestador + investigación

### PATCH-3: Monthly report cable
- [ ] Localizar invocación de `MonthlyReportGenerator.generate()` en `main.py`
- [ ] Pasar `asset_report_path` explícito
- [ ] Test: `monthly_report` muestra tabla con estados reales

### PATCH-5: SitePresenceChecker DOM real
- [ ] Navegar `termales.com.co` con browser
- [ ] `browser_console`: query selectores WhatsApp (href + clases)
- [ ] `browser_console`: query schema JSON-LD
- [ ] Ampliar `_check_html_element()`: buscar en `href` + clases CSS
- [ ] Schema detection: considerar Organization/LocalBusiness para hoteles
- [ ] Test: WhatsApp detectado correctamente en sitio real

### PATCH-6: GBP phone enrichment
- [ ] En `main.py`: enriquecer `hotel_data["phone"]` desde `audit_report["gbp"]["phone"]`
- [ ] Template propuesta_v6 usa variable dinámica (no hardcode)
- [ ] Test: propuesta muestra teléfono real, no placeholder

### Cierre FASE-B
- [ ] Todos los tests pasan
- [ ] `log_phase_completion.py` ejecutado
- [ ] Plan actualizado

---

## FASE-2-PATCH-C: Verificación E2E

### Ejecución
- [x] `v4complete --url http://www.termales.com.co/` ejecutado
- [x] Evidencia copiada a `evidence/fase-2-PATCH-C/`

### Verificación de Métricas
- [x] M1: `grep -c "{{if" 02_PROPUESTA_*.md` → 0
- [x] M2: `promised_assets_exist.score` < 1.0 (si faltan assets) → 1.0 (PASS porque todos los assets prometidos existen)
- [x] M3: monthly_report tabla dinámica no vacía → PASS
- [x] M4: `grep -r "\[PENDING_" evidence/` → 0
- [x] M5: `present_in_production` contiene `whatsapp_button` → PASS
- [ ] M6: `hotel_schema_detected` = true → FAIL (solo org_schema detectado)
- [x] M7: `grep -c "+57 300 000 0000" 02_PROPUESTA_*.md` → 0

### Veredicto
- [x] Score registrado: 6/7
- [x] Clasificación: PARCIAL

### Docs Cascade
- [x] `log_phase_completion.py` ejecutado
- [x] `sync_versions.py` ejecutado
- [x] CHANGELOG.md actualizado (v4.43.1)
- [x] GUIA_TECNICA.md actualizada (v4.43.1)
- [x] `09-documentacion-post-proyecto-2-PATCH.md` actualizado
- [x] `run_all_validations.py --quick` pasa (5/5)
