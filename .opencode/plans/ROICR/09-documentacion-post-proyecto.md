# Documentación Post-Proyecto — ROICR

**Plan**: ROICR
**Target**: v4.55.0
**Creado**: 2026-05-27

---

## Acumulador de Resultados por Fase

### FASE-1: Semántica de Activos
**Estado**: ✅ Completada (2026-05-27)

**Archivos creados**:
- `modules/quality/asset_semantics_validator.py` — validador de семантических ошибок
- `tests/test_asset_semantics_validator.py` — 15 tests cubriendo BLOCKED/IMPLEMENT/AUDIT_ONLY

**Archivos modificados**:
- `modules/asset_generation/asset_catalog.py`:
  - Campo `migration_target: Optional[str]` añadido a `AssetCatalogEntry`
  - `og_tags_guide.migration_target = "open_graph"` (redirect a asset FASE-4)
  - `indirect_traffic_optimization.migration_target = None` (consultoría manual)
  - `local_content_page.required_confidence = 0.60` (presentado como Bonus)
  - `geo_playbook.migration_target = None`
  - `voice_assistant_guide.migration_target = None`
  - Fix: `from dataclasses import dataclass` duplicated
  - Fix: `Optional` añadido a imports

- `modules/commercial_documents/pain_solution_mapper.py`:
  - `Solution` dataclass: campos `semantic_status`, `semantic_blocked_reason`, `migration_target`
  - `get_assets_for_pain()`: valida семантику antes de crear AssetSpec; БЛОКИРОВАН as missing = skip
  - `map_to_solutions()`: redirect con `migration_target` cuando mapping está bloqueado
  - `generate_asset_plan()`: mismo check семантический + propagation de `semantic_status` a AssetSpec

- `modules/commercial_documents/data_structures.py`:
  - Campo `semantic_status: str = "IMPLEMENT"` añadido a `AssetSpec`

- `modules/commercial_documents/v4_proposal_generator.py`:
  - `_build_solution_table()`: cuando `semantic_status == "AUDIT_ONLY"`, muestra "Auditar y Optimizar: {problema}"

**Criterios de completitud validados**:
- [x] `asset_semantics_validator.py` existe e importable
- [x] `INVALID_MAPPINGS` definidos para `monthly_report` y `whatsapp_conflict_guide`
- [x] `migration_target` presente en entries DEPRECATED/IMPLEMENTED del catálogo
- [x] 15 tests pasan covering BLOCKED / IMPLEMENT / AUDIT_ONLY
- [x] Bloqueantes de FASE-3 (pricing) y FASE-2 (publication_gates) NO tocados

### FASE-2: Gate Hardening
*Pendiente de ejecución*

### FASE-3: Pipeline Unificado + CAPEX/OPEX + Curva
**Estado**: ✅ Completada (2026-05-27)

**Archivos creados**:
- `modules/financial_engine/roi_formatter.py` — `calcular_metricas_roi()` con CAPEX/OPEX desacoplados. ROI SaaS = Recuperación/OPEX (NUNCA OPEX+CAPEX). `ROIMetrics` dataclass + `formatear_roi_para_propuesta()`.
- `modules/financial_engine/pillar_maturity_curve.py` — `aplicar_curva_4_pilares()` con curva `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]` (6 meses). `PillarMaturityResult` + `MaturityProjection` dataclasses + `formatear_curva_para_propuesta()`.

**Archivos modificados**:
- `config/pricing.yaml`:
  - `tiers.boutique`: `min_price: 800K` (antes 1.2M), `value_capture_cap: 0.50`, `operational_floor: 400K`, `pain_ratio_gate_max: 0.32`
- `config/scenarios.yaml`:
  - `recovery_factors.realistic`: 0.20 → 0.35
- `modules/financial_engine/pricing_calculator.py` (v4.2.0 → v4.3.0):
  - `calcular_precio_final()`: pipeline unificado de 3 pasos (Base → Pain Ratio Adjustment → Ethical Cap)
  - `PricingResult`: nuevos campos `expected_recovery_cop`, `ethical_cap_applied`, `adjustment_applied`, `operational_floor`, `value_capture_cap`
  - `calculate()`: parámetro opcional `expected_recovery_cop` activa el pipeline
  - `_calculate_with_pipeline()`: wrapper que llama `calcular_precio_final()` y retorna `PricingResult`
  - `_load_pricing_config()` + `_DEFAULT_TIER_CONFIG`: cargan nuevos campos de YAML
- `modules/commercial_documents/v4_proposal_generator.py`:
  - Imports: `calcular_metricas_roi`, `aplicar_curva_4_pilares`
  - Nuevas variables template: `roi_saas`, `capex_total`, `opex_mensual`, `curva_4_pilares_tabla`, `activos_digitales_lista`, `nota_capex_opex`
  - `_calculate_roi_saas()`: ROI sobre OPEX (NUNCA OPEX+CAPEX)
  - `_build_activos_digitales_lista()`: lista de assets propiedad del cliente
  - `rec_m1..rec_m6` + `net_m1..net_m6` + `acc_m1..acc_m6`: ahora usan curva de maduración en vez de flat
- `modules/commercial_documents/templates/propuesta_v6_template.md`:
  - Nueva sección: "Curva de Maduración: 4 Pilares" con tabla mes a mes
  - Nueva sección: "CAPEX vs OPEX: Lo que es suyo vs. lo que es servicio"
  - Garantías expandidas: Value-Capture Cap (#1), Garantía Día 55 (#3)

**Criterios de completitud validados**:
- [x] `pricing.yaml` tiene `value_capture_cap`, `operational_floor`, `pain_ratio_gate_max`
- [x] `pricing_calculator.py` tiene `calcular_precio_final()` con 3 pasos
- [x] `roi_formatter.py` existe y retorna métricas desacopladas
- [x] `pillar_maturity_curve.py` existe con curva `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]`
- [x] `grep "roi_saas" modules/commercial_documents/v4_proposal_generator.py` muestra integración
- [x] `grep "Recuperación.*OPEX.*CAPEX\|OPEX.*CAPEX.*Recuperación" modules/` retorna 0 matches (PROHIBIDO)

### FASE-4: Arbitraje Ético + Garantía Día 55
*Pendiente de ejecución*

### FASE-5: Fixtures + Regression Guardian
*Pendiente de ejecución*

### FASE-7: RELEASE v4.55.0
*Pendiente de ejecución*

### FASE-6: v4complete + Análisis
*Pendiente de ejecución*

---

## Análisis Post-Implementación (se llena en FASE-6)

### Nivel 1 — Pricing Ético
*Pendiente*

### Nivel 2 — CAPEX/OPEX Desacoplado
*Pendiente*

### Nivel 3 — Curva 4 Pilares
*Pendiente*

### Nivel 4 — Gobernanza Comercial
*Pendiente*

### Nivel 5 — Garantía Auditable
*Pendiente*

### Nivel 6 — CI/CD
*Pendiente*

---

## Veredicto Final
*Pendiente de FASE-6*
