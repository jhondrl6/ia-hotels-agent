# CHECKLIST DE IMPLEMENTACIÓN: BRECHAS-DINAMICAS

**Última actualización**: 2026-04-08

## Progreso Global

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ✅ Completada | 2026-04-08 | Templates dinámicos |
| FASE-B | ⬜ Pendiente | — | Generator dinámico |
| FASE-C | ⬜ Pendiente | — | OpportunityScorer mappings |
| FASE-D | ⬜ Pendiente | — | PainSolutionMapper fix + coherencia |
| FASE-E | ⬜ Pendiente | — | Validación amaziliahotel.com |

---

## FASE-A: Templates Dinámicos
- [x] V6 template: reemplazar 4 ranuras por `${brechas_section}`
- [x] V6 template: reemplazar tabla 4 filas por `${brechas_resumen_section}`
- [x] V4 template: reemplazar 4 ranuras por `${brechas_section}`
- [x] Default template inline: reemplazar 4 ranuras
- [x] grep confirma 0 ocurrencias de "4 BRECHAS/RAZONES"

## FASE-B: Generator Dinámico
- [ ] Método `_build_brechas_section()` implementado
- [ ] Método `_build_brechas_resumen_section()` implementado
- [ ] `_prepare_template_data()` incluye ambos placeholders
- [ ] `min(..., 4)` eliminado de `_inject_brecha_scores()`
- [ ] 5 tests nuevos pasan
- [ ] Tests existentes no se rompen

## FASE-C: OpportunityScorer Mappings
- [ ] 5 nuevos tipos en BRECHA_SEVERITY_MAP
- [ ] 5 nuevos tipos en BRECHA_EFFORT_MAP
- [ ] 5 nuevos tipos en BRECHA_IMPACT_MAP
- [ ] 5 nuevos tipos en _JUSTIFICATION_TEMPLATES
- [ ] pain_to_type mapper actualizado en generator
- [ ] 6 tests nuevos pasan

## FASE-D: PainSolutionMapper Fix + Coherencia
- [ ] Duplicate `low_ia_readiness` corregido (1 entrada, 3 assets)
- [ ] 10 pain_ids de `_identify_brechas()` verificados en PAIN_SOLUTION_MAP
- [ ] Coherence >= 0.8 con 7+ brechas verificado
- [ ] `optimization_guide.promised_by` sin "pain_solution_mapper"
- [ ] Tests de integración pasan

## FASE-E: Validación amaziliahotel.com
- [ ] v4complete ejecutado sin errores
- [ ] Diagnóstico muestra N brechas (no 4)
- [ ] Header no dice "4 BRECHAS"
- [ ] Cada brecha traza a asset vía pain_id
- [ ] Tabla resumen tiene N filas
- [ ] Propuesta comercial coherente
- [ ] Assets cubren >= 50% de brechas
- [ ] Coherence score >= 0.80
- [ ] Reporte de validación documentado
