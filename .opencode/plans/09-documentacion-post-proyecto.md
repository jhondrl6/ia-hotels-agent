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

---

## Sección C: Lecciones Aprendidas

*(Se completa al final del proyecto)*

1. El límite de 4 brechas venía de 3 capas (template, generator, scorer) que se reforzaban mutuamente.
2. `_identify_brechas()` ya era dinámico (0-10) pero nunca se explotó porque las capas superiores truncaban.
3. La propuesta comercial (propuesta_v6_template) NO consume brechas directamente — usa servicios fijos. Esto es un gap arquitectónico que este proyecto NO aborda (queda como mejora futura).

---

## Sección D: Métricas Acumulativas

|| Métrica | Antes | Después FASE-A | Después FASE-B | ... | Final |
||---------|-------|----------------|----------------|-----|-------|
|| Max brechas mostradas | 4 | Dinámico (N) | Dinámico (N) | — | — |
|| Pain IDs con scorer | 7 | — | Hasta 10 (was 4) | — | — |
|| Tests brechas | 12 | 12 (sin cambios) | 17 (+5) | — | — |
|| Tests scorer | ? | — | — | — | — |
|| Coherence score | 0.8552 | — | — | — | — |
|| run_all_validations --quick | ? | — | 4/4 | — | — |
|| Lines modified (cumulative) | 0 | ~40 (templates + default) | +33 (generator) | — | — |
|| Backward compatibility | OK | OK (tests 12/12) | OK (tests 17/17) | — | — |

---

## Sección E: Archivos Afiliados Actualizados

### Manuales (según documentation_rules.md §17-25)

- [ ] `CHANGELOG.md` — Entrada con archivos nuevos/modificados (formato §36-58)
- [ ] `docs/GUIA_TECNICA.md` — Sección "Notas de Cambios" con módulos afectados, arquitectura, backward compat
- [ ] `INDICE_DOCUMENTACION.md` — Si los módulos modificados son públicos/utilizados (diagnostic_generator, opportunity_scorer)
- [ ] `VERSION.yaml` — Solo si se produce release (FASE-RELEASE)

### Auto-sync (via sync_versions.py o log_phase_completion.py)

- [ ] `AGENTS.md` — Auto via sync_versions.py (verificar post-release)
- [ ] `README.md` — Auto via sync_versions.py
- [ ] `.cursorrules` — Auto via sync_versions.py
- [ ] `docs/CONTRIBUTING.md` — Header auto via sync_versions.py
- [ ] `docs/contributing/REGISTRY.md` — Auto via log_phase_completion.py
- [ ] `.agent/SYSTEM_STATUS.md` — Regenerar: `python main.py --doctor --status`
- [ ] `.agent/knowledge/DOMAIN_PRIMER.md` — Verificar: `python scripts/doctor.py --context` (regenerar si faltan módulos nuevos)

### Verificación post-proyecto (según CONTRIBUTING §56-163)

- [ ] `python scripts/version_consistency_checker.py` — Sin discrepancias
- [ ] `python main.py --doctor` — Sin errores (incluye symlink integrity)
- [ ] `python scripts/sync_versions.py` — Headers sincronizados
- [ ] Symlink `.agent/workflows` → `.agents/workflows` verificado

---

## Sección F: Checklist de Capability Contract (documentation_rules.md §26-34)

Aplica cuando se agregan capabilities nuevas (métodos públicos en módulos).

| Capability | Módulo | Punto de Invocación | Output Serializable | No Huérfana |
|------------|--------|--------------------|--------------------:|-------------|
| `_build_brechas_section()` | v4_diagnostic_generator | `_prepare_template_data()` | str (markdown) | SI (alimenta template) |
| `_build_brechas_resumen_section()` | v4_diagnostic_generator | `_prepare_template_data()` | str (markdown) | SI (alimenta template) |
| 5 nuevos scorer types | opportunity_scorer | `_compute_opportunity_scores()` | OpportunityScore dataclass | SI (via generator) |

- [ ] Cada capability nueva documentada en GUIA_TECNICA.md
- [ ] Ninguna capability huérfana (todas invocadas en flujo principal)

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
- [ ] FASE-C registrada en REGISTRY.md
- [ ] FASE-D registrada en REGISTRY.md
- [ ] FASE-E registrada en REGISTRY.md
