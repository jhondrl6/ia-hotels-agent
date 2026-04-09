# DOCUMENTACIÓN POST-PROYECTO: BRECHAS-DINAMICAS

**Proyecto**: Eliminación del hardcode "LAS 4 BRECHAS"
**Fecha inicio**: 2026-04-08
**Referencia**: docs/CONTRIBUTING.md §39-52 (Flujo Post-Fase) + §56-163 (Actualizar docs oficial)

---

## Sección A: Módulos Nuevos/Modificados

*(Se completa después de cada fase)*

### FASE-A: Templates ✅ 2026-04-08
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Modificado (4 ranuras → ${brechas_section}, tabla → ${brechas_resumen_section})
- `modules/commercial_documents/templates/diagnostico_v4_template.md` — Modificado (4 ranuras → ${brechas_section})
- `modules/commercial_documents/v4_diagnostic_generator.py` (solo `_get_default_template`) — Modificado (4 ranuras → ${brechas_section})

### FASE-B: Generator ✅ 2026-04-08
- `modules/commercial_documents/v4_diagnostic_generator.py` — Métodos nuevos: `_build_brechas_section()`, `_build_brechas_resumen_section()`. Integrados en `_prepare_template_data()`. `min(..., 4)` → `min(..., 10)` en `_inject_brecha_scores()`.
- `tests/commercial_documents/test_diagnostic_brechas.py` — 5 tests nuevos: `test_build_brechas_section_with_5_brechas`, `test_build_brechas_section_with_0_brechas`, `test_build_brechas_resumen_section_dynamic`, `test_inject_brecha_scores_no_truncation`, `test_brecha_section_markdown_valid`

### FASE-C: Scorer
- `modules/financial_engine/opportunity_scorer.py` — 5 entries nuevas en maps
- `tests/financial_engine/test_opportunity_scorer.py` — Tests nuevos

### FASE-D: Mapper + Coherencia
- `modules/commercial_documents/pain_solution_mapper.py` — Fix duplicate
- `modules/asset_generation/asset_catalog.py` — Fix promised_by

### FASE-E: Validación
- Sin cambios de código. Solo ejecución + análisis.

---

## Sección B: Decisiones de Diseño

*(Se completa durante implementación)*

1. **Template approach vs code approach**: Se eligió `${brechas_section}` placeholder (inyección desde generator) en vez de lógica condicional dentro del template. Razón: templates son markdown puro, no soportan loops.
2. **min(10) vs ilimitado**: Se fijó máximo 10 brechas en `_inject_brecha_scores()` como protección contra runaway detection. 10 es suficiente para cualquier hotel.
3. **FASE-D fix scope**: Solo corrección de duplicate y promised_by, no refactoring mayor del mapper. Mantener cambio mínimo para reducir riesgo.
4. **Validación con amaziliahotel.com**: Hotel real con datos mixtos (GBP OK, schema ausente, citabilidad baja). Caso de uso representativo.

---

## Sección C: Lecciones Aprendidas

*(Se completa al final del proyecto)*

1. El límite de 4 brechas venía de 3 capas (template, generator, scorer) que se reforzaban mutuamente.
2. `_identify_brechas()` ya era dinámico (0-10) pero nunca se explotó porque las capas superiores truncaban.
3. La propuesta comercial (propuesta_v6_template) NO consume brechas directamente — usa servicios fijos. Esto es un gap arquitectónico que este proyecto NO aborda (queda como mejora futura).

---

## Sección D: Métricas Acumulativas

|| Métrica | Antes | FASE-A | FASE-B | FASE-C | FASE-D | Final |
||---------|-------|--------|--------|--------|--------|-------|
|| Max brechas mostradas | 4 | Dinámico (N) | Dinámico (N) | — | — | 6 (amaziliahotel) |
|| Pain IDs con scorer | 7 | — | — | 12 (+5) | — | 12 |
|| Tests brechas | 12 | 12 | 17 (+5) | 23 (+6) | 23 | 23 |
|| Coherence score | 0.8552 | — | — | — | — | 0.84 (E2E) |
|| Lines modified (cumulative) | 0 | ~40 | +33 | +15 | +5 | ~93 |
|| Backward compatibility | OK | OK | OK (17/17) | OK (23/23) | OK | OK |
|| E2E amaziliahotel | — | — | — | — | — | 6 brechas, READY |

---

## Sección E: Archivos Afiliados Actualizados

### Manuales (según documentation_rules.md §17-25)

- [x] `CHANGELOG.md` — Entrada BRECHAS-DINAMICAS agregada a [4.25.3]
- [x] `docs/GUIA_TECNICA.md` — Sección "Notas de Cambios BRECHAS-DINAMICAS" agregada
- [x] `INDICE_DOCUMENTACION.md` — Módulos ya documentados (diagnostic_generator, pain_solution_mapper)
- [x] `VERSION.yaml` — Sin cambio (no release, validación only)

### Auto-sync (via sync_versions.py o log_phase_completion.py)

- [x] `AGENTS.md` — sync_versions.py: OK, in sync
- [x] `README.md` — sync_versions.py: OK, in sync
- [x] `.cursorrules` — sync_versions.py: OK, in sync
- [x] `docs/CONTRIBUTING.md` — sync_versions.py: OK, in sync
- [x] `docs/contributing/REGISTRY.md` — log_phase_completion.py ejecutado
- [x] `.agent/SYSTEM_STATUS.md` — Existe, actualizado
- [x] `.agent/knowledge/DOMAIN_PRIMER.md` — Existe, sin cambios necesarios (mismos módulos)

### Verificación post-proyecto (según CONTRIBUTING §56-163)

- [x] `python scripts/version_consistency_checker.py` — Versiones sincronizadas (4.25.3, UnicodeEncodeError en emoji pero versiones OK)
- [x] `python scripts/sync_versions.py` — All files in sync
- [x] Symlink `.agent/workflows` → `.agents/workflows` — Verificado previamente

---

## Sección F: Checklist de Capability Contract (documentation_rules.md §26-34)

Aplica cuando se agregan capabilities nuevas (métodos públicos en módulos).

| Capability | Módulo | Punto de Invocación | Output Serializable | No Huérfana |
|------------|--------|--------------------|--------------------:|-------------|
| `_build_brechas_section()` | v4_diagnostic_generator | `_prepare_template_data()` | str (markdown) | SI (alimenta template) |
| `_build_brechas_resumen_section()` | v4_diagnostic_generator | `_prepare_template_data()` | str (markdown) | SI (alimenta template) |
| 5 nuevos scorer types | opportunity_scorer | `_compute_opportunity_scores()` | OpportunityScore dataclass | SI (via generator) |

- [x] Cada capability nueva documentada en GUIA_TECNICA.md — Sección "Notas de Cambios BRECHAS-DINAMICAS" agregada
- [x] Ninguna capability huérfana (todas invocadas en flujo principal) — Verificado: `_build_brechas_section()` se llama desde `_prepare_template_data()`

---

## Sección G: log_phase_completion.py (OBLIGATORIO por fase)

Según CONTRIBUTING §42-52, ejecutar al final de CADA fase:

```bash
# Ejemplo FASE-B:
venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-B \
    --desc "Generator dinamico N brechas" \
    --archivos-mod "modules/commercial_documents/v4_diagnostic_generator.py" \
    --archivos-nuevos "" \
    --tests "5" \
    --coherence 0.85 \
    --check-manual-docs
```

- [x] FASE-A registrada en REGISTRY.md
- [x] FASE-B registrada en REGISTRY.md
- [x] FASE-C registrada en REGISTRY.md (via log_phase_completion previa sesión)
- [x] FASE-D registrada en REGISTRY.md (via log_phase_completion previa sesión)
- [x] FASE-E registrada en REGISTRY.md (log_phase_completion.py ejecutado en esta sesión)
