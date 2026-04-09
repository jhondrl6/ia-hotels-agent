# CHECKLIST DE IMPLEMENTACIÓN: BRECHAS-DINAMICAS

**Última actualización**: 2026-04-08

## Progreso Global

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-A | ✅ Completada | 2026-04-08 | Templates dinámicos |
| FASE-B | ✅ Completada | 2026-04-08 | Generator dinámico |
| FASE-C | ✅ Completada | 2026-04-08 | OpportunityScorer mappings |
|| FASE-D | ✅ Completada | 2026-04-08 | PainSolutionMapper fix + coherencia |
|| FASE-E | ✅ Completada | 2026-04-08 | Validación amaziliahotel.com |

---

## FASE-A: Templates Dinámicos
- [x] V6 template: reemplazar 4 ranuras por `${brechas_section}`
- [x] V6 template: reemplazar tabla 4 filas por `${brechas_resumen_section}`
- [x] V4 template: reemplazar 4 ranuras por `${brechas_section}`
- [x] Default template inline: reemplazar 4 ranuras
- [x] grep confirma 0 ocurrencias de "4 BRECHAS/RAZONES"

## FASE-B: Generator Dinámico ✅
- [x] Método `_build_brechas_section()` implementado
- [x] Método `_build_brechas_resumen_section()` implementado
- [x] `_prepare_template_data()` incluye ambos placeholders
- [x] `min(..., 4)` eliminado de `_inject_brecha_scores()` (ahora 10)
- [x] 5 tests nuevos pasan
- [x] Tests existentes no se rompen (17/17 total)

## FASE-C: OpportunityScorer Mappings ✅
- [x] 5 nuevos tipos en BRECHA_SEVERITY_MAP
- [x] 5 nuevos tipos en BRECHA_EFFORT_MAP
- [x] 5 nuevos tipos en BRECHA_IMPACT_MAP
- [x] 5 nuevos tipos en _JUSTIFICATION_TEMPLATES
- [x] pain_to_type mapper actualizado en generator
- [x] 6 tests nuevos pasan

## FASE-D: PainSolutionMapper Fix + Coherencia
- [ ] Duplicate `low_ia_readiness` corregido (1 entrada, 3 assets)
- [ ] 10 pain_ids de `_identify_brechas()` verificados en PAIN_SOLUTION_MAP
- [ ] Coherence >= 0.8 con 7+ brechas verificado
- [ ] `optimization_guide.promised_by` sin "pain_solution_mapper"
- [ ] Tests de integración pasan

## FASE-E: Validación amaziliahotel.com ✅
- [x] v4complete ejecutado sin errores
- [x] Diagnóstico muestra N brechas (no 4) → 6 brechas
- [x] Header no dice "4 BRECHAS" → dice "BRECHAS CRÍTICAS IDENTIFICADAS"
- [x] Cada brecha traza a asset vía pain_id
- [x] Tabla resumen tiene N filas → 6 filas
- [x] Propuesta comercial coherente con diagnóstico
- [x] Assets cubren >= 50% de brechas → 9/11 generados
- [x] Coherence score >= 0.80 → 0.84
- [x] Reporte de validación documentado en context/02-validacion-amaziliahotel.md
