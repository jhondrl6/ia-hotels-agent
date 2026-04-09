# DEPENDENCIAS: BRECHAS-DINAMICAS

**Generado**: 2026-04-08

## Diagrama de Dependencias

```
FASE-A: Templates dinámicos
  │  Modifica: diagnostico_v6_template.md, diagnostico_v4_template.md
  │  No depende de ninguna fase previa.
  │
  └──→ FASE-B: Generator dinámico
         │  Modifica: v4_diagnostic_generator.py (_prepare_template_data, _inject_brecha_scores)
         │  Depende de: FASE-A (los templates deben tener ${brechas_section})
         │
         └──→ FASE-C: OpportunityScorer completar mappings ✅
                │  Modifica: opportunity_scorer.py (SEVERITY/EFFORT/IMPACT_MAP, _extract_brechas)
                │  Depende de: FASE-B (los pain_ids del generator deben estar completos)
                │
                └──→ FASE-D: PainSolutionMapper fix + coherencia ✅
                       │  Modifica: pain_solution_mapper.py, asset_catalog.py
                       │  Depende de: FASE-C (scorer debe tener todos los pain_ids mapeados)
                       │
                       └──→ FASE-E: Validación v4complete ✅
                              │  Ejecuta: main.py v4complete --url https://amaziliahotel.com
                              │  Depende de: A+B+C+D completas
                              │  Output: análisis de resultados del diagnóstico generado
                              │  Resultado: 6 brechas mostradas (no 4), coherence 0.84, READY_FOR_PUBLICATION
                              │
                              └──→ DONE
```

## Tabla de Conflictos de Archivos

| Archivo | Fase(es) | Conflicto potencial |
|---------|----------|-------------------|
| `diagnostico_v6_template.md` | A | Ninguno (solo esta fase lo toca) |
| `diagnostico_v4_template.md` | A | Ninguno |
| `v4_diagnostic_generator.py` | B | Ninguno (A solo toca templates) |
| `opportunity_scorer.py` | C | Ninguno |
| `pain_solution_mapper.py` | D | Ninguno |
| `asset_catalog.py` | D | Fix optimization_guide promised_by |
| `coherence_config.py` | D | Solo verificación, no modificación |
| `tests/commercial_documents/test_diagnostic_brechas.py` | B | Se amplía, no se sobreescribe |
| `tests/financial_engine/test_opportunity_scorer.py` | C | Se amplía |

## Notas

- No hay conflictos de archivos entre fases (cada fase toca archivos distintos).
- FASE-E es solo ejecución + análisis, no modifica código fuente.
