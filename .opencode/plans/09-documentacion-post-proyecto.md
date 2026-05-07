# Documentación Post-Proyecto

> Plan: PROPOSAL-COMERCIAL-FIX v1.0.0

---

## Sección A: Módulos Nuevos

Ninguno en esta fase.

## Sección B: Cambios en Archivos Existentes

### FASE-PROP-A: Unificación de Coherence Score

**main.py**
- L2241-2243: Calcula `pre_gate_status` (PASSED/FAILED) basado en `pre_coherence_score >= threshold`
- L2441: Pasa `coherence_score=pre_coherence_score` y `gate_status=pre_gate_status` a `diagnostic_gen.generate()`

**modules/commercial_documents/v4_diagnostic_generator.py**
- L428: `generate()` ahora acepta parámetro `gate_status: Optional[str] = None`
- L519: `_prepare_template_data()` ahora acepta parámetro `gate_status`
- L529-534: Lógica de `coherence_score` unificada — si es None/0 muestra "PENDIENTE", nunca invoca fallback automáticamente
- L587-588: Template data incluye `coherence_score_display` y `gate_status_display`
- L1182-1193: `_calculate_coherence_score()` marcado como DEPRECATED
- L398-402: Inicialización de `_region`, `_cached_brechas`, `_last_voice_score`, `_last_voice_level` en `__init__`

**modules/commercial_documents/templates/diagnostico_v6_template.md**
- L6: Agrega `gate_status: ${gate_status}` al YAML header

### FASE-PROP-B: WhatsApp Conflict Status

**modules/commercial_documents/v4_proposal_generator.py**
- `_confidence_to_nivel_significado()`: Detecta `whatsapp_status='conflict'` y retorna "⚠️ Bajo" con nota de conflicto
- Tabla de calidad muestra conflicto cuando `whatsapp_status='conflict'`

### FASE-PROP-C: Proyecciones Financieras Transparentes

**modules/commercial_documents/v4_proposal_generator.py**
- `pain_ratio_note` reescrito: explica `pain_ratio` (relación problemas/recursos) y `recovery_factor` (velocidad de recuperación)

**modules/commercial_documents/templates/propuesta_v6_template.md**
- Placeholder `${pain_ratio_note}` agregado cerca de tabla financiera

### FASE-PROP-D: Google Maps geo_playbook DEPRECATED

**modules/asset_generation/asset_catalog.py**
- `geo_playbook`: status DEPRECATED, `promised_by=[]`, `deprecation_reason="Redundante con delivery GEO existente"`

**modules/commercial_documents/pain_solution_mapper.py**
- `low_gbp_score` ahora solo mapea a `review_plan` (sin `geo_playbook`)

**modules/asset_generation/conditional_generator.py**
- `geo_playbook` eliminado de `_standard_assets` y handler elif

**modules/asset_generation/asset_diagnostic_linker.py**
- `geo_playbook` eliminado de `justifications`, `impact_map`, `asset_metadata`

**modules/asset_generation/site_presence_checker.py**
- Entrada `geo_playbook` eliminada

### FASE-PROP-E: SEO/AEO Plan Específico por Score

**modules/commercial_documents/v4_proposal_generator.py**
- `_build_7_day_plan()`: acciones específicas cuando score SEO < 30 (contenido nuevo) y score AEO < 30 (Schema FAQ)
- `_build_30_day_plan()`: acciones específicas por score bajo
- Tabla de calidad incluye AEO cuando `score_aeo < 30`

### FASE-PROP-F: Tier C Warning en Propuesta

**modules/commercial_documents/v4_proposal_generator.py**
- `_prepare_template_data()` extrae `financial_evidence_tier` desde `financial_breakdown.evidence_tier` (fallback: "C")

**modules/commercial_documents/templates/propuesta_v6_template.md**
- Bloque condicional `{{if financial_evidence_tier == "C"}}` con banner ⚠️ "Datos estimados — Tier C"
- Nota sutil para Tier A/B

### FASE-PROP-G: Rutas Persistentes de Evidencia

**main.py**
- `_make_evidence_path(hotel_id, basename)` crea `output/v4_complete/{hotel_id}/v4_audit/{basename}_{timestamp}.json`
- `gate_report.json`, `audit_report.json`, `financial_scenarios.json` ahora incluyen `hotel_id` en ruta
- `os.makedirs(..., exist_ok=True)` para crear subdirectorios automáticamente

### FASE-RELEASE-4.41.0: Documentación y Version Bump

**VERSION.yaml**
- `version: 4.41.0`, `codename: PROPOSAL-COMERCIAL-FIX`, `release_date: 2026-05-06`

**CHANGELOG.md**
- Entrada `[4.41.0]` con todas las fases A-G documentadas

**docs/GUIA_TECNICA.md**
- Nota técnica "Notas de Cambios v4.41.0 — PROPOSAL-COMERCIAL-FIX"

**docs/contributing/REGISTRY.md**
- Fases A-G registradas vía `log_phase_completion.py`

**AGENTS.md, README.md, .cursorrules, docs/CONTRIBUTING.md**
- Headers sincronizados a 4.41.0 vía `sync_versions.py`

## Sección C: Cambios Arquitectónicos

### Pipeline Timing — Coherence Score Unificado

**Antes:**
1. Diagnóstico se generaba con fallback `_calculate_coherence_score()` (0.74)
2. CoherenceValidator corría después
3. Propuesta leía el valor viejo del diagnóstico
4. Gates usaban valor del asset (0.72)

**Después:**
1. CoherenceValidator corre PRIMERO (L2199-2259)
2. Diagnóstico se regenera con `coherence_score=pre_coherence_score` (L2433-2445)
3. Un solo cómputo de coherence_score usado por diagnóstico, propuesta y gates

**Impacto:** Elimina inconsistencia entre 3 fuentes de verdad. El diagnóstico ya no muestra valores inventados.

## Sección D: Métricas Acumulativas

| Métrica | Valor |
|---------|-------|
| Tests nuevos (FASE-PROP-A) | 7 |
| Tests nuevos (FASE-PROP-B/C/D/E/F) | ~18 |
| Tests nuevos (FASE-PROP-G) | 8 |
| Tests totales nuevos | ~33 |
| Archivos modificados | 11 |
| Archivos nuevos | 3 (tests) |
| Validaciones | 4/4 PASSED |
| Versión | 4.41.0 |

## Sección E: Archivos Afiliados Actualizados

- [x] `docs/contributing/REGISTRY.md` — actualizado vía `log_phase_completion.py` (fases A-G)
- [x] `dependencias-fases.md` — actualizado con FASE-RELEASE-4.41.0
- [x] `06-checklist-implementacion.md` — todas las fases marcadas ✅
- [x] `09-documentacion-post-proyecto.md` — todas las fases B-G y RELEASE documentadas
- [x] `VERSION.yaml` — bump a 4.41.0
- [x] `CHANGELOG.md` — entrada [4.41.0]
- [x] `docs/GUIA_TECNICA.md` — nota técnica v4.41.0
- [x] `AGENTS.md`, `README.md`, `.cursorrules`, `docs/CONTRIBUTING.md` — headers sync a 4.41.0
- [x] `.opencode/plans/05-prompt-inicio-sesion-fase-RELEASE-4.41.0.md` — este plan ejecutado
