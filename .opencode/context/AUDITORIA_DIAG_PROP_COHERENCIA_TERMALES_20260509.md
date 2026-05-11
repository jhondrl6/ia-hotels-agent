# Contexto Completo: Auditoría de Coherencia Diagnóstico vs Propuesta Comercial — Termales Santa Rosa de Cabal

> **Generado**: 2026-05-09 — Sesión de validación post-FASE-RELEASE  
> **Actualizado**: 2026-05-09 — Validación exhaustiva contra código vivo  
> **Hotel**: Termales Santa Rosa de Cabal — http://www.termales.com.co/  
> **Origen**: Verificación de coherencia entre `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260509_153835.md` y `02_PROPUESTA_COMERCIAL_20260509_153844.md`  
> **Archivos base**: `evidence/FASE-RELEASE/` (audit_report, asset_generation_report, coherence_validation, v4_complete_report)

---

## Resumen Ejecutivo

Se identificaron **5 brechas de coherencia** entre el Diagnóstico y la Propuesta Comercial. Dos son CRÍTICAS (desconexión de servicios y contradicción en coherence checks), tres son MENORES (redondeo financiero, porcentaje recovery, assets de baja confianza no mencionados).

Adicionalmente, la validación exhaustiva contra código vivo reveló **3 hallazgos nuevos** no detectados en la auditoría original: un defecto de arquitectura en el flujo de coherencia (H6-CRÍTICO), un fallo silencioso en generación de monthly_report (H7-ALTO), y una política de gate insuficiente (H8-ALTO).

### Scores Verificados contra Código Vivo ✅

| Pilar | Score en Documento | Score Calculado | Estado |
|-------|-------------------|----------------|--------|
| SEO Local | 10/100 | 10 (solo schema_reviews=True → 10 pts) | ✅ Confirmado |
| GEO | 80/100 | 80 (redes+gbp+fotos+schema_reviews_geo) | ✅ Confirmado |
| AEO | 15/100 | 15 (solo open_graph=True → 15 pts) | ✅ Confirmado |
| IAO | 50/100 | 50 (citability+schema_advanced=35, crawler=0, brand=0) | ✅ Confirmado |
| Coherence | 0.8911111111111112 | 0.89 (promedio checks 6 items) | ✅ Confirmado |

**⚠️ DISCREPANCIA NO REPORTADA:** El `coherence_validation.json` reporta `overall_score: 0.89`, pero el `v4_complete_report.json` reporta `coherence_score: 0.9133333333333333`. Estos valores deberían ser idénticos ya que provienen del mismo pipeline. Posible causa: diferente ruta de cálculo o redondeo intermedio. **Requiere investigación.**

Cálculo IAO desde audit (`audit_report_20260509_153830.json`):
```
CHECKLIST_IAO weights: citability_score=20, contenido_extenso=15, llms_txt_exists=15,
                        crawler_access=15, brand_signals=10, ga4_indirect=10, schema_advanced=15

Elementos:
  citability_score: True  (citability.overall_score=53.39 > 50 threshold)
  contenido_extenso: True (same source as citability_score)
  llms_txt_exists: False
  crawler_access: False  (ai_crawlers.overall_score=0.5, STRICT > 0.5 → False)
  brand_signals: False   (no 'sameas'/'social' in schema.properties)
  ga4_indirect: no_evaluado
  schema_advanced: True  (org_schema_detected=True)

IAO = 20 + 15 + 15 = 50 ✅
```

---

## Hallazgo 1 — CRÍTICA: Desconexión de Servicios Prometidos

### Descripción
La Propuesta Comercial muestra solo **3 de 8 servicios** (los que tienen assets generados con éxito). El sistema de gate (`proposal_asset_alignment_gate`) verifica correctamente los 8 servicios definidos en `PROPOSAL_SERVICE_TO_ASSET` y detecta 3 missing, pero la propuesta no los muestra.

### Archivos Involved

**Código vivo — `modules/asset_generation/proposal_asset_alignment.py` L20-29:**
```python
PROPOSAL_SERVICE_TO_ASSET: Dict[str, str] = {
    "SEO Local": "optimization_guide",           # MISSING en propuesta
    "Botón de WhatsApp": "whatsapp_button",       # present_in_production
    "Schema Hotel": "hotel_schema",               # aligned ✅
    "Schema Organization": "org_schema",          # present_in_production
    "Informe Mensual": "monthly_report",          # MISSING en propuesta (y FAILED en generación)
    "Página de FAQ": "faq_page",                  # aligned ✅
    "Meta Tags Sociales (Open Graph)": "open_graph",  # MISSING en propuesta
    "Optimización para IA Generativa": "llms_txt",   # aligned ✅
}
```

**Evidencia — `evidence/FASE-RELEASE/v4_complete_report.json` L117-182 (Gate 9 — proposal_asset_alignment):**
```json
{
  "alignment_percentage": 0.5,
  "all_aligned": false,
  "aligned": [
    {"service": "Schema Hotel", "asset": "hotel_schema", "confidence": 0.85},
    {"service": "Página de FAQ", "asset": "faq_page", "confidence": 0.85},
    {"service": "Optimización para IA Generativa", "asset": "llms_txt", "confidence": 0.85}
  ],
  "missing": [
    {"service": "SEO Local", "asset": "optimization_guide", "message": "not generated"},
    {"service": "Informe Mensual", "asset": "monthly_report", "message": "not generated"},
    {"service": "Meta Tags Sociales (Open Graph)", "asset": "open_graph", "message": "not generated"}
  ],
  "present_in_production": [
    {"service": "Botón de WhatsApp", "asset": "whatsapp_button", "presence_status": "exists"},
    {"service": "Schema Organization", "asset": "org_schema", "presence_status": "exists"}
  ]
}
```

### Causa Raíz Confirmada

En `modules/commercial_documents/v4_proposal_generator.py`, el método `_generate_dynamic_services_table()` (L882-888) filtra servicios por `generated_asset_types`:

```python
generated_asset_types = {
    a.get("asset_type", "") for a in assets_generated if a.get("asset_type")
}
services = [
    entry for entry in SERVICE_CATALOG.values()
    if entry.asset_type in generated_asset_types
]
```

**Solo 3 assets fueron generados con éxito** (hotel_schema, faq_page, llms_txt — confidence ≥ 0.85), por lo que la tabla dinámica muestra solo esos 3 servicios. Los servicios missing (SEO Local, Informe Mensual, Open Graph) y los present_in_production (WhatsApp, org_schema) quedan fuera de la vista del cliente.

Además, `SERVICE_CATALOG` en `service_catalog.py` solo tiene 7 entradas (sin incluir el AEO condicional), y no incluye ni `analytics_setup_guide` ni `indirect_traffic_optimization`, que son assets técnicos entregados pero no mapeados como servicios vendibles.

**Dato adicional:** La propiedad `total_services` de `AlignmentReport` (proposal_asset_alignment.py L72) calcula `len(aligned) + len(missing) + len(low_quality)`, excluyendo `present_in_production` e `indeterminate`. Por eso el reporte dice `total_services: 6` y no 8.

---

## Hallazgo 2 — CRÍTICA: Coherence Validator contradice a proposal_asset_alignment_gate

### Descripción
El coherence check `promised_assets_exist` reporta **TRUE** (todos implementados, score 1.0), pero Gate 9 muestra que 3 servicios están MISSING y 2 están en producción.

### Causa Raíz Confirmada en Código Vivo (IRREFUTABLE) ⚠️

En `main.py` línea 2228-2234:

```python
pre_coherence_report = coherence_validator.validate(
    temp_diagnostic,
    temp_proposal,
    asset_plan,
    validation_summary,
    whatsapp_html_detected=getattr(audit_result.validation, 'whatsapp_html_detected', False) if audit_result else False,
    generated_assets=None  # ← GENERATED_ASSETS ES NULL
)
```

**El `CoherenceValidator` se ejecuta ANTES de generar los assets, con `generated_assets=None`.**

Cuando `generated_assets=None`, el método `_check_promised_assets_exist()` (coherence_validator.py L529-538) hace fallback al catálogo estático `is_asset_implemented()`:

```python
if generated_assets:
    asset_info = generated_assets.get(asset_type, {})
    if not asset_info.get('can_use', False):
        missing_service_assets.append(f"{service_name}→{asset_type}")
else:
    # Legacy fallback: catalogo estatico
    if not is_asset_implemented(asset_type):
        missing_service_assets.append(f"{service_name}→{asset_type}")
```

Como `optimization_guide`, `monthly_report` y `open_graph` están en `ASSET_CATALOG` con `status=AssetStatus.IMPLEMENTED` (`asset_catalog.py` L176-345), `is_asset_implemented()` devuelve `True` para todos ellos, y el check dice "pasado: 100%".

**El `CoherenceValidator` en `v4_asset_orchestrator.py` L257 también se ejecuta sin los assets generados** (se ejecuta ANTES del bucle de generación, línea 257-262):

```python
coherence = self.coherence_validator.validate(
    diagnostic_doc, proposal_doc, asset_specs, validation_summary
)
```

Aquí `asset_specs` son especificaciones planificadas, no assets realmente generados. Luego se generan los assets (L300-360), pero **nunca se vuelve a ejecutar el CoherenceValidator con los resultados reales**.

**El resultado:** `coherence_validation.json` con `overall_score: 0.89` y `promised_assets_exist: passed: true` es un falso positivo. Refleja la situación *antes* de generar, no la realidad *después*.

### Dato Nuevo — Score de Coherencia Duplicado y Discrepante

| Fuente | Valor |
|--------|-------|
| `coherence_validation.json` → `overall_score` | 0.89 |
| `v4_complete_report.json` → `coherence_score` | 0.9133333333333333 |
| `gate_report.json` → `coherence.value` | 0.8911111111111112 |

Tres valores distintos para el mismo concepto. Ninguno refleja el estado post-generación real.

---

## Hallazgo 3 — MENOR: Error de redondeo en distribución de costos de brechas

### Descripción
La suma de las 3 brechas no coincide con `financial_value_central`.

### Datos Confirmados (financial_scenarios_20260509_153830.json)
```json
{
  "scenarios": {
    "conservative": 7276953.6,
    "realistic": 3741696.0,
    "optimistic": -270950.4
  }
}
```

```
financial_value_central: $3,741,696 COP

Brecha 1: $1,799,007 COP (48%)
Brecha 2: $863,583 COP (23%)
Brecha 3: $1,079,479 COP (28%)

Suma: 1,799,007 + 863,583 + 1,079,479 = $3,742,069 COP
Discrepancia: |3,742,069 - 3,741,696| = 373 COP (0.01%)
```

### Causa Raíz
Los porcentajes (48%, 23%, 28%) están redondeados a enteros. La distribución se hace por división equitativa entre top_problems (método `_build_brecha_data` en v4_proposal_generator.py L1374-1403). Como los problemas no tienen pesos de impacto reales en esta ejecución (no se usó `brechas_reales` con impacto), la división equitativa entre 3 problemas ($1,247,232 c/u) genera redondeos que no cuadran.

**Cálculo correcto:** 3,741,696 / 3 = $1,247,232 por brecha. Los valores mostrados indican que se usaron pesos desiguales (probablemente del OpportunityScorer) pero sin normalizar al valor central exacto.

---

## Hallazgo 4 — MENOR: Porcentaje recovery (41%) no coincide con valor recovery mostrado

### Datos Confirmados

De `financial_scenarios.json`:
```json
"pricing": {
  "pain_ratio": 0.4082
}
```

### Confusión de Conceptos

El `pain_ratio` (0.4082 = ~41%) es la **proporción del dolor financiero que se considera recuperable**. NO es un "recovery factor" de efectividad.

El **recovery_factor** es un concepto diferente usado en el cálculo de ROI:
```python
# v4_proposal_generator.py _calculate_roi()
roi_ratio = total_gain / total_investment
# donde total_gain = gain * recovery_factor * months
# recovery_factors: conservative=0.15, realistic=0.20, optimistic=0.25
```

El template muestra: *"el 41% representa la porción que consideramos recuperable con IAO"*, pero el valor de $1,527,360 es:
- $3,741,696 × 0.4082 = $1,527,360 (pain_ratio, no recovery)
- Si fuera recovery: $1,527,360 × 0.20 (recovery_factor realistic) = $305,472 realmente proyectado como ganancia

**En resumen:** El texto confunde dos conceptos financieros distintos. El 41% es el pain_ratio (porción del dolor abordable), no un "porcentaje de recuperación". La ganancia proyectada real después del recovery_factor sería ~$305K/mes, no ~$1.5M/mes.

---

## Hallazgo 5 — MENOR: Assets de baja confianza no aparecen en propuesta

### Assets Generados Completos (asset_generation_report.json)
```
total_assets: 6, generated: 5, failed: 1, skipped: 0
can_use: 5, estimated: 2
delivery_ready_percentage: 60.0
site_verification_applied: false
```

| # | Asset | Confidence | Preflight | Status |
|---|-------|------------|-----------|--------|
| 1 | hotel_schema | 0.85 | PASSED | ✅ En propuesta |
| 2 | faq_page | 0.85 | PASSED | ✅ En propuesta |
| 3 | analytics_setup_guide | 0.5 | WARNING | ❌ NO en propuesta |
| 4 | indirect_traffic_optimization | 0.5 | WARNING | ❌ NO en propuesta |
| 5 | llms_txt | 0.85 | PASSED | ✅ En propuesta |
| - | monthly_report | — | BLOCKED | ❌ FAILED (error runtime) |
| - | optimization_guide | — | — | ❌ MISSING (no generado) |
| - | open_graph | — | — | ❌ MISSING (no generado) |
| - | whatsapp_button | — | — | ℹ️ present_in_production |
| - | org_schema | — | — | ℹ️ present_in_production |

### Causa Raíz
La tabla "Estado de los Entregables" en la propuesta solo muestra los assets que están mapeados en `SERVICE_CATALOG` (en `service_catalog.py`) y que pasaron por el filtro de `_generate_asset_quality_table()` (L988-998 en v4_proposal_generator.py). Los assets `analytics_setup_guide` e `indirect_traffic_optimization` NO están en `SERVICE_CATALOG`, solo en `ASSET_CATALOG` como assets técnicos. Por lo tanto, nunca aparecen en la tabla de entregables de la propuesta.

---

## 🔴 HALLAZGOS NUEVOS (Validados contra código vivo)

### H6 — CRÍTICO: CoherenceValidator no se ejecuta post-generación

**Problema:** La coherencia se valida ANTES de generar assets, no después. El flujo actual es:

1. `main.py:2228` → CoherenceValidator con `generated_assets=None` → score 0.89 (FALSO POSITIVO)
2. `v4_asset_orchestrator.py:257` → CoherenceValidator con `asset_specs` (plan, no realidad)
3. `v4_asset_orchestrator.py:296-360` → Generación real de assets
4. `main.py:2699` → Gate 9 detecta 3 missing (post-generación, sin coherencia)

**No existe una segunda ejecución de CoherenceValidator con los datos reales post-generación.** Esto significa que el score de coherencia del documento (0.89) es una ficción que no refleja la realidad.

**Evidencia:** `v4_asset_orchestrator.py` línea 257-262:
```python
coherence = self.coherence_validator.validate(
    diagnostic_doc, proposal_doc, asset_specs, validation_summary
)
# No se vuelve a llamar después de generar los assets
```

**Impacto:** Documentos con coherence_score inflado salen al cliente sin detección real de gaps.

### H7 — ALTO: monthly_report con promise "always" falla silenciosamente

**Evidencia:** `asset_catalog.py` L322:
```python
"monthly_report": AssetCatalogEntry(
    ...
    status=AssetStatus.IMPLEMENTED,
    promised_by=["always"]  # SIEMPRE generar
)
```

Pero en `asset_generation_report.json`:
```json
{
  "asset_type": "monthly_report",
  "reason": "Generation failed: 'list' object has no attribute 'items'",
  "preflight_status": "BLOCKED"
}
```

El promise "always" fuerza la generación PERO no hay retry ni notificación al usuario cuando falla. El error de runtime (`'list' object has no attribute 'items'`) sugiere un bug en `monthly_report_generator.py` cuando los datos de entrada tienen un formato inesperado.

**Impacto:** La propuesta SIEMPRE promete un informe mensual que no se entrega, sin que el cliente lo sepa.

### H8 — ALTO: Gate 9 no bloquea con alignment al límite (50%)

**Evidencia:** `publication_gates.py` línea 873-908:
```python
if alignment < 0.5:
    # BLOCKED
else:
    # WARNING (pasa con 50% alignment)
```

Con Termales: 3/6 aligned = **50% exacto** → pasa como WARNING en vez de BLOCKED.

**El documento se publica potencialmente con la mitad de servicios sin entregar.** Si se aplicara el umbral de 0.8 que el propio `coherence_gate` (Gate 4) usa como estándar de calidad, el gate 9 debería al menos exigir 80%.

---

## Estructura de Assets — Estado Actual Validado

### Assets Generados (asset_generation_report.json)

| Asset | Confidence | Preflight | Pain Resolved | En Propuesta | En Catalogo SERVICE |
|-------|------------|-----------|---------------|--------------|---------------------|
| hotel_schema | 0.85 | PASSED | no_hotel_schema | ✅ Sí | ✅ (como schema_hotel) |
| faq_page | 0.85 | PASSED | no_faq_schema | ✅ Sí | ✅ |
| analytics_setup_guide | 0.5 | WARNING | no_analytics_configured | ❌ No | ❌ No |
| indirect_traffic_optimization | 0.5 | WARNING | low_organic_visibility | ❌ No | ❌ No |
| llms_txt | 0.85 | PASSED | ai_crawler_blocked | ✅ Sí | ✅ (como AEO condicional) |

### Assets Missing (Gate 9)

| Asset | Service | Pain | Causa |
|-------|---------|------|-------|
| optimization_guide | SEO Local | multiple | No se generó (fallback?) |
| monthly_report | Informe Mensual | no_monthly_report | **FAILED**: error runtime `'list' object has no attribute 'items'` |
| open_graph | Meta Tags Sociales | no_og_tags | No se generó |

### Assets Present in Production (SitePresenceChecker)

| Asset | Service | Confianza |
|-------|---------|-----------|
| whatsapp_button | Botón de WhatsApp | exists (verificado) |
| org_schema | Schema Organization | exists (verificado) |

---

## Interdependencias de los Hallazgos (Actualizada)

```
H6: Coherence pre-generación (CRÍTICO)
├── H2: Contradicción coherence vs gate (es síntoma de H6)
├── H1: Propuesta incompleta (H6 impide detectar gaps post-generación)
└── H5: Assets ocultos (sin coherencia post-generación, no se reporta)

H7: monthly_report falla silenciosamente (ALTO)
├── H1: Agrava la falta de servicios
└── Asset_generation_report no tiene retry ni alerta

H8: Gate 9 no bloquea en límite (ALTO)
└── Permite publicar con H1 sin resolver

H3 + H4: Errores financieros (MENORES)
└── Independientes, pero afectan credibilidad comercial
```

**Las causas raíz compartidas:**
1. El flujo de propuesta no está conectado al output real del pipeline de gates y generación.
2. No hay re-validación de coherencia post-generación.
3. Los assets técnicos (analytics, indirect_traffic) no están mapeados como servicios vendibles.

---

## Códigos de Módulos Clave Involucrados

| Módulo | Archivo | Líneas | Rol |
|--------|---------|--------|-----|
| Proposal generator | `modules/commercial_documents/v4_proposal_generator.py` | 847 (_generate_dynamic_services_table), 918 (_generate_asset_quality_table), 1374 (_build_brecha_data) | Genera propuesta — filtro dinámico incompleto |
| Proposal alignment | `modules/asset_generation/proposal_asset_alignment.py` | 20-29 (PROPOSAL_SERVICE_TO_ASSET), 44-68 (AlignmentReport) | Contrato de servicios (8 servicios) |
| Alignment gate | `modules/quality_gates/publication_gates.py` | 761-908 (_proposal_asset_alignment_gate) | Gate 9 — verifica alignment |
| Coherence validator | `modules/commercial_documents/coherence_validator.py` | 495-575 (_check_promised_assets_exist) | Check promised_assets — falla con generated_assets=None |
| Asset orchestrator | `modules/asset_generation/v4_asset_orchestrator.py` | 257 (pre-coherence), 296-360 (generación) | No re-valida post-generación |
| Main pipeline | `main.py` | 2228 (coherence pre), 2532-2594 (proposal gen), 2626-2699 (gates) | Orquestación — generated_assets=None en coherence |
| Diagnostic generator | `modules/commercial_documents/v4_diagnostic_generator.py` | 115-137 (checklists), 194-224 (score functions) | Scores 4 pilares |
| Service catalog | `modules/commercial_documents/service_catalog.py` | 29-124 | 7 servicios + AEO (sin analytics/indirect) |
| Asset catalog | `modules/asset_generation/asset_catalog.py` | 53-346 (ASSET_CATALOG) | 18 assets, incluye monthly_report (always), analytics |
| Site presence checker | `modules/asset_generation/site_presence_checker.py` | 152-189 (ASSET_TO_SCHEMA_MAP) | Verifica assets en producción |
| Financial scenarios | modules/financial_engine/ (precision_validator) | — | pain_ratio=0.4082, recovery_factor=0.20 |

---

## Estrategia de Solución — Priorizada

### P0 — CRÍTICO: Coherence post-generación (H6)

**Problema:** CoherenceValidator solo corre antes de generar assets.  
**Solución:** Añadir `_validate_post_generation()` en `v4_asset_orchestrator.py` que re-ejecute `CoherenceValidator.validate()` con los `generated_assets` reales después del bucle de generación (después de L360). El score resultante reemplaza al pre-coherence y se incluye en el `CoherenceReport` guardado. Actualizar `main.py` para usar este score en `DiagnosticSummary.coherence_score` (L2526).

**Archivos a modificar:**
- `modules/asset_generation/v4_asset_orchestrator.py` — añadir paso post-generación
- `main.py` — consumir coherence post-generación

**Tests a añadir:** Verificar que coherence post-generación detecta missing assets.

### P1 — ALTO: Propuesta completa + Gate robusto (H1, H5, H8)

**Problemas:**
- H1: La propuesta solo muestra 3/8 servicios
- H5: Assets técnicos ocultos
- H8: Gate 9 no bloquea con 50% alignment

**Soluciones:**
1. **H1/H5:** Añadir sección "Todos los servicios" en la propuesta que muestre los 8 servicios de `PROPOSAL_SERVICE_TO_ASSET` con estado (✅ aligned, ⏳ missing, ✅ in-production). Añadir sección adicional "Assets técnicos entregados" para analytics_setup_guide e indirect_traffic_optimization.
   - Archivo: `modules/commercial_documents/v4_proposal_generator.py` — `_generate_dynamic_services_table()` y `_generate_asset_quality_table()`

2. **H8:** Cambiar umbral de bloqueo en Gate 9 de `0.5` a `0.8` para alinear con el estándar de coherence (Gate 4). O bien, añadir condición: si `present_in_production` + `aligned` < 80% de servicios totales, bloquear.
   - Archivo: `modules/quality_gates/publication_gates.py` — `_proposal_asset_alignment_gate()`

**Tests a añadir:** Test de que proposal muestra 8 servicios con estados correctos. Test de que gate 9 bloquea alignment < 0.8.

### P1 — ALTO: monthly_report fail-safe (H7)

**Problema:** monthly_report tiene `promised_by=["always"]` pero falló con error de runtime.  
**Soluciones:**
1. Añadir try/except en conditional_generator para monthly_report con error handling explícito
2. Añadir NOTA en la propuesta cuando monthly_report falla (similar a low_quality disclaimer)
3. Crear issue para corregir el bug `'list' object has no attribute 'items'` en monthly_report_generator.py

**Archivo:** `modules/asset_generation/conditional_generator.py`

### P2 — MEDIO: Corrección financiera (H3, H4)

**H3 — Redondeo:**
- Distribuir costos de brecha usando pesos del OpportunityScorer (`impacto` de `brechas_reales`) en vez de distribución equitativa
- Normalizar la suma al `financial_value_central` como paso final
- Archivo: `modules/commercial_documents/v4_proposal_generator.py` — `_build_brecha_data()`

**H4 — Confusión pain_ratio/recovery:**
- Corregir el texto del template para distinguir claramente pain_ratio (41% del dolor abordable) de recovery_factor (20% de efectividad)
- Mostrar ambos valores separados en la propuesta
- Archivos: `modules/commercial_documents/v4_proposal_generator.py` — `pain_ratio_note`, templates

### Diagrama de Flujo Corregido (Propuesto)

```
Orquestación actual:
  1. Audit ──→ Pre-coherence (sin assets) ──→ Generar assets ──→ Gate 9 ──→ Propuesta
                                              ↑
                                     coherence_validator.validate()
                                     with generated_assets=None ✗

Propuesta corregida:
  1. Audit ──→ Pre-coherence (sin assets, screening rápido)
                    ↓
             2. Generar assets (con condicionales + SitePresenceChecker)
                    ↓
             3. Coherence post-generación ← NUEVO (H6)
                    ↓
             4. Gate 9 (con datos reales) ──→ Si alignment < 0.8: BLOCKED
                    ↓
             5. Propuesta completa con 8 servicios (H1, H5)
                    ↓
             6. Publicación / Revisión manual
```

---

## Prompt para Próxima Sesión

```
Carga el contexto .opencode/context/AUDITORIA_DIAG_PROP_COHERENCIA_TERMALES_20260509.md

Diseña un PLAN DE REFACTORIZACIÓN completo que resuelva los 8 hallazgos identificados:

H0 (P0) - Coherence post-generación: Implementar _validate_post_generation() en v4_asset_orchestrator.py
  - Ejecutar CoherenceValidator con generated_assets reales después del bucle de generación
  - Reemplazar pre_coherence_score con post_coherence_score en DiagnosticSummary
  - Tests: verificar que detecta missing assets post-generación

H1 (P1) - Propuesta completa: Mostrar 8 servicios con estados
  - Modificar _generate_dynamic_services_table() y _generate_asset_quality_table()
  - Añadir sección "Assets técnicos adicionales" para analytics e indirect_traffic
  
H2 (P1) - Contradicción coherence: Resuelto por H0 (coherence post-generación)

H3 (P2) - Redondeo financiero: Normalizar distribución de brechas al valor central

H4 (P2) - Confusión pain_ratio/recovery: Separar conceptos en template

H5 (P1) - Assets ocultos: Mapear analytics_setup_guide e indirect_traffic_optimization como servicios

H6 (P0) - Archivos ya identificados con causa raíz y solución arriba

H7 (P1) - monthly_report fail-safe: Try/except + nota en propuesta + fix bug runtime

H8 (P1) - Gate 9 threshold: Cambiar de 0.5 a 0.8 o añadir lógica de bloqueo

Restricciones:
- El plan debe cubrir TODAS las fases: análisis, diseño, implementación, tests, documentación
- Cada hallazgo debe tener criterios de completitud verificables
- Máximo 60 iteraciones por fase
- No tocar el fix de FASE-12A/B (ya implementado y validado)
- El plan debe ser ejecutable por fases (1 fase = 1 sesión)

Entregables del plan:
1. Arquitectura del flujo corregido (diagrama ASCII)
2. Cambios específicos por archivo con line numbers
3. Tests para cada fix
4. Documentación de la cascada de cambios
```

---

## Estado de Validación

| Hallazgo | Validado contra código | Evidencia | Estado |
|----------|----------------------|-----------|--------|
| H1 | ✅ Sí | proposal_asset_alignment.py, v4_proposal_generator.py, v4_complete_report.json | Causa raíz confirmada |
| H2 | ✅ Sí | main.py:2228, coherence_validator.py:530-538, asset_catalog.py | Causa raíz confirmada (generated_assets=None) |
| H3 | ✅ Sí | financial_scenarios_20260509.json | Redondeo confirmado |
| H4 | ✅ Sí | financial_scenarios.json (pain_ratio=0.4082), v4_proposal_generator.py | Confusión conceptos confirmada |
| H5 | ✅ Sí | asset_generation_report.json (missing), service_catalog.py (sin analytics/indirect) | Causa raíz confirmada |
| H6 | ✅ NUEVO | main.py:2228, v4_asset_orchestrator.py:257 | Arquitectura defectuosa |
| H7 | ✅ NUEVO | asset_generation_report.json (BLOCKED monthly_report) | Bug runtime silencioso |
| H8 | ✅ NUEVO | publication_gates.py:879-908 | Política de gate insuficiente |

**Fecha de validación exhaustiva**: 2026-05-09  
**Revisor**: Validación automatizada contra código vivo del repositorio iah-cli en WSL