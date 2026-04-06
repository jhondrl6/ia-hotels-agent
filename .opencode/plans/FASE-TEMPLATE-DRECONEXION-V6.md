# FASE-TEMPLATE-RECONEXION-V6
## Estado: PLAN REGENERADO (sesión corrupta 2026-03-31 19:58)
## Objetivo: Eliminar TODOS los `${placeholder}` sin resolver en documentos comerciales v4.0

---

## DIAGNÓSTICO: Raíz del Problema

El pipeline `v4complete` ejecuta correctamente Audit → Financial → Coherence Gate → Document Generation,
pero los generadores V4 (`v4_diagnostic_generator.py`, `v4_proposal_generator.py`) NO populate
todas las variables que las templates V6 requieren.

**Método de detección:** `string.Template.safe_substitute()` deja keys faltantes como literales
`${variable_name}` en lugar de fallar — permitiendo que el pipeline "éxitos" con documentos rotos.

---

## VARIABLES FALTANTES POR TEMPLATE

### A) diagnostico_v6_template.md (46 variables en template)

| # | Variable | Estado Actual | Fuente Esperada | Acción |
|---|----------|---------------|-----------------|--------|
| 1 | `${generated_at}` | ✅ `generated_at` | datetime | OK |
| 2 | `${version}` | ✅ `version` | literal '4.0.0' | OK |
| 3 | `${hotel_id}` | ✅ `hotel_id` | hotel_name slug | OK |
| 4 | `${coherence_score}` | ✅ `coherence_score` | coherence gate | OK |
| 5 | `${hotel_name}` | ✅ `hotel_name` | args.nombre o URL | OK |
| 6 | **``${hotel_location}`** | ❌ FALTANTE | audit_result o args | **ADD** |
| 7 | **``${hotel_region}`** | ❌ FALTANTE | `_detect_region_from_url()` en main.py | **ADD** |
| 8 | **``${regional_context}`** | ❌ FALTANTE | main.py context | **ADD** |
| 9 | **``${hotel_landmark}`** | ❌ FALTANTE | N/A (placeholder) | **ADD literal** |
| 10 | `${geo_score}` | ✅ `geo_score` | `_calculate_geo_score()` | OK |
| 11 | **``${geo_status}`** | ❌ naming mismatch | `_get_score_status(geo_score, 60)` → `geo_status` | **RENAME** |
| 12 | **``${gbp_score}`** | ❌ FALTANTE | activity→ GBP? | **ADD mapping** |
| 13 | **``${gbp_status}`** | ❌ FALTANTE | `_get_score_status(activity_score, 30)` | **ADD** |
| 14 | **``${aeo_score}`** | ❌ FALTANTE | `schema_infra_score` o `_calculate_voice_readiness_score()` | **MAP** |
| 15 | **``${aeo_status}`** | ❌ FALTANTE | `_get_score_status(schema_infra_score, 40)` | **ADD** |
| 16 | **``${iao_score}`** | ✅ `iao_score` | `_calculate_iao_score()` | OK |
| 17 | **``${iao_status}`** | ✅ `iao_status` | `_get_score_status(iao_score, 20)` | OK |
| 18 | **``${seo_score}`** | ❌ FALTANTE | `web_score`? | **MAP** |
| 19 | **``${seo_status}`** | ❌ FALTANTE | `web_status`? | **MAP** |
| 20 | **``${monthly_loss}`** | ❌ FALTANTE | `main_scenario.monthly_loss_max` → `monthly_loss` | **ADD** |
| 21 | **``${brecha_1_impacto}`** | ❌ FALTANTE | audit_result problemas | **ADD** |
| 22 | **``${brecha_2_impacto}`** | ❌ FALTANTE | audit_result problemas | **ADD** |
| 23 | **``${brecha_3_impacto}`** | ❌ FALTANTE | audit_result problemas | **ADD** |
| 24 | **``${brecha_4_impacto}`** | ❌ FALTANTE | audit_result problemas | **ADD** |
| 25 | **``${urgencia_contenido}`** | ❌ FALTANTE | KB context | **ADD** |
| 26 | **``${quick_wins_content}`** | ❌ FALTANTE | `_build_quick_wins()` | **MAP** |
| 27 | **``${brecha_1_resumen}`** | ❌ FALTANTE | extracted from problems | **ADD** |
| 28 | **``${brecha_2_resumen}`** | ❌ FALTANTE | extracted from problems | **ADD** |
| 29 | **``${brecha_3_resumen}`** | ❌ FALTANTE | extracted from problems | **ADD** |
| 30 | **``${brecha_4_resumen}`** | ❌ FALTANTE | extracted from problems | **ADD** |
| 31 | `${brecha_1_costo}` | ✅ `brecha_1_costo` | `_get_brecha_costo()` | OK |
| 32 | `${brecha_1_nombre}` | ✅ `brecha_1_nombre` | `_get_brecha_nombre()` | OK |
| 33 | `${brecha_2_costo}` | ✅ `brecha_2_costo` | `_get_brecha_costo()` | OK |
| 34 | `${brecha_2_nombre}` | ✅ `brecha_2_nombre` | `_get_brecha_nombre()` | OK |
| 35 | `${brecha_3_costo}` | ✅ `brecha_3_costo` | `_get_brecha_costo()` | OK |
| 36 | `${brecha_3_nombre}` | ✅ `brecha_3_nombre` | `_get_brecha_nombre()` | OK |
| 37 | `${brecha_4_costo}` | ✅ `brecha_4_costo` | `_get_brecha_costo()` | OK |
| 38 | `${brecha_4_nombre}` | ✅ `brecha_4_nombre` | `_get_brecha_nombre()` | OK |
| 39 | `${loss_6_months}` | ✅ `loss_6_months` | calculated | OK |
| 40-46 | (metadata) | - | - | OK |

**Resumen: 20 variables faltantes/en mismatch en diagnostico_v6_template.md**

### B) propuesta_v6_template.md (31 variables en template)

| # | Variable | Estado Actual | Fuente Esperada | Acción |
|---|----------|---------------|-----------------|--------|
| 1 | `${generated_at}` | ✅ | datetime | OK |
| 2 | `${version}` | ✅ | literal | OK |
| 3 | `${hotel_id}` | ✅ | hotel_name slug | OK |
| 4 | **``${hotel_name}`** | ✅ pero línea 11 espera `${hotel_location}` | separate | **SPLIT** |
| 5 | **``${hotel_location}`** | ❌ FALTANTE | extract from audit | **ADD** |
| 6 | **``${hotel_region}`** | ❌ FALTANTE | `_detect_region_from_url()` | **ADD** |
| 7 | **``${monthly_loss}`** | ❌ FALTANTE | main_scenario.monthly_loss_max | **ADD** |
| 8 | **``${monthly_investment}`** | ❌ FALTANTE | `monthly_fee`? | **MAP** |
| 9-14 | `${inv_m1}`..`${inv_m6}` | ❌ FALTANTE | investment constant | **ADD** |
| 15-20 | `${rec_m1}`..`${rec_m6}` | ❌ FALTANTE | main_scenario | **ADD** |
| 21-26 | `${net_m1}`..`${net_m6}` | ✅ `net_m1`..`net_m6` | calculated | OK |
| 27 | **``${total_investment}`** | ❌ FALTANTE | `monthly_investment * 6` | **ADD** |
| 28 | **``${total_recovered}`** | ❌ FALTANTE | scenario * 6 | **ADD** |
| 29 | **``${net_benefit}`** | ❌ FALTANTE | `(rec - inv) * 6` | **ADD** |
| 30 | **``${roi_6m}`** | ❌ FALTANTE | `net_benefit / total_investment` | **ADD** |
| 31 | `${valid_until}` | ❌ FALTANTE | generated + 15 days | **ADD** |

**Resumen: 17 variables faltantes en propuesta_v6_template.md**

### C) v4_complete_report.json

| Problema | Estado | Fix |
|----------|--------|-----|
| `assets_generated` vacío `[]` aunque assets existen en disco | ❌ | Poblar desde `asset_result.generated_assets` |
| `coherence_score` no está al top level | ❌ | Agregar `coherence_score: pre_coherence_score` |
| `financial_data` falta | ❌ | Agregar `financial_data: {scenarios, pricing}` |

---

## ARCHIVOS A MODIFICAR

### 1. `modules/commercial_documents/v4_diagnostic_generator.py`

**Ubicación:** `_prepare_template_data()` (línea ~379-500)

**Cambios:**

```
A) Agregar hotel_location y hotel_region:

   hotel_location = getattr(audit_result, 'location', None) or \
                     getattr(audit_result.gbp, 'address', None) or \
                     region or "Colombia"
   hotel_region = region  # ya disponible en scope

B) Mapeos de nombres (agregar aliases):

   # GBP Score (la template espera gbp_score, generator produce activity_score)
   'gbp_score': self._calculate_activity_score(audit_result),
   'gbp_status': self._get_score_status(self._calculate_activity_score(audit_result), 30),
   
   # SEO Score (web_score se llama seo_score en template)
   'seo_score': self._calculate_web_score(audit_result),
   'seo_status': self._get_score_status(self._calculate_web_score(audit_result), 70),
   
   # AEO Score (schema_infra_score maps to aeo_score)
   'aeo_score': self._calculate_schema_infra_score(audit_result),
   'aeo_status': self._get_score_status(self._calculate_schema_infra_score(audit_result), 40),

C) monthly_loss (alias de main_scenario_amount):

   'monthly_loss': format_cop(main_scenario.monthly_loss_max),

D) Variables de contenido (faltaban):

   'regional_context': self._build_regional_context(region),
   'hotel_landmark': f"zona de {region}" if region else "zona turística",
   'urgencia_contenido': self._build_urgencia_content(financial_scenarios, hotel_name),
   'quick_wins_content': self._build_quick_wins_content(audit_result),
   
E) Brecha impactos y resúmenes (faltaban):

   'brecha_1_impacto': self._get_brecha_impacto(audit_result, 0),
   'brecha_2_impacto': self._get_brecha_impacto(audit_result, 1),
   'brecha_3_impacto': self._get_brecha_impacto(audit_result, 2),
   'brecha_4_impacto': self._get_brecha_impacto(audit_result, 3),
   'brecha_1_resumen': self._get_brecha_resumen(audit_result, 0),
   'brecha_2_resumen': self._get_brecha_resumen(audit_result, 1),
   'brecha_3_resumen': self._get_brecha_resumen(audit_result, 2),
   'brecha_4_resumen': self._get_brecha_resumen(audit_result, 3),
```

**Methods a agregar en la clase:**
- `_build_regional_context(region)` → texto contextual sobre la región
- `_build_urgencia_content(scenarios, hotel_name)` → urgencia del porque actuar
- `_build_quick_wins_content(audit_result)` → versión markdown de quick wins
- `_get_brecha_impacto(audit_result, index)` → impacto de la brecha
- `_get_brecha_resumen(audit_result, index)` → resumen una-línea

### 2. `modules/commercial_documents/v4_proposal_generator.py`

**Ubicación:** `_prepare_template_data()` (línea ~424-557)

**Cambios:**

```
A) Agregar hotel_location y hotel_region:

   # NOTA: audit_result es Optional en esta función
   hotel_location = getattr(audit_result, 'location', None) or region or "Colombia"
   hotel_region = region  # viene de main.py vía generate()

B) Poblar todas las variables de inversión/recuperación que faltan:

   # monthly_investment (alias)
   'monthly_investment': format_cop(monthly_investment),
   
   # inv_m1 a inv_m6 (investment constante cada mes)
   for i in range(1, 7):
       data[f'inv_m{i}'] = format_cop(monthly_investment)
   
   # rec_m1 a rec_m6 (recuperación cada mes)
   for i in range(1, 7):
       data[f'rec_m{i}'] = format_cop(main_scenario.monthly_loss_max)
   
   # total_investment, total_recovered, net_benefit
   'total_investment': format_cop(monthly_investment * 6),
   'total_recovered': format_cop(main_scenario.monthly_loss_max * 6),
   'net_benefit': format_cop((main_scenario.monthly_loss_max - monthly_investment) * 6),
   
   # roi_6m
   roi_6m_value = (main_scenario.monthly_loss_max - monthly_investment) * 6 / (monthly_investment * 6)
   'roi_6m': f"{roi_6m_value:.1f}X",

C) monthly_loss faltante:
   'monthly_loss': format_cop(main_scenario.monthly_loss_max),
```

**NOTA CRÍTICA:** La función `generate()` de V4ProposalGenerator recibe `audit_result=None` por defecto,
pero NUNCA se pasa `region` a `_prepare_template_data()`. Hay que agregarlo como parámetro o
capturarlo de alguna forma.

**Ver:** Línea 190-196 muestra:
```python
template_data = self._prepare_template_data(
    diagnostic_summary=diagnostic_summary,
    financial_scenarios=financial_scenarios,
    asset_plan=asset_plan,
    hotel_name=hotel_name,
    audit_result=audit_result,  # <-- audit_result disponible aquí
)
```

El `region` está disponible en main.py línea 1380 como variable local, pero NO se pasa a
`proposal_gen.generate()`. Necesitas:

1. Agregar `region: str` como parámetro a `V4ProposalGenerator.generate()`
2. Pasar `region` desde main.py (línea 1998-2006)
3. Usar `region` en `_prepare_template_data()` para `hotel_region` y `hotel_location`

### 3. `main.py` — run_v4_complete_mode()

**Ubicación:** Llamadas a generadores (líneas ~1954 y ~1998)

**Cambios:**

```
A) En la llamada a proposal_gen.generate() (línea ~1998), AGREGAR region:
   
   proposal_path = proposal_gen.generate(
       diagnostic_summary=diagnostic_summary,
       financial_scenarios=financial_scenarios_obj,
       asset_plan=asset_plan,
       hotel_name=hotel_name,
       output_dir=str(output_dir),
       audit_result=audit_result,
       pricing_result=pricing_result,
       region=region,  # <-- AGREGAR ESTO
   )

B) En v4_complete_report.json (líneas ~2259 y ~2359):
   
   # Agregar coherence_score al top level
   'coherence_score': pre_coherence_score,
   
   # Poblar assets_generated desde asset_result
   'assets_generated': [
       {
           'asset_type': a.asset_type,
           'path': a.path,
           'status': a.preflight_status
       }
       for a in asset_result.generated_assets
   ] if asset_result else [],
   
   # Agregar financial_data al top level
   'financial_data': {
       'scenarios': scenarios_dict,
       'pricing': {
           'monthly_price_cop': pricing_result.monthly_price_cop,
           'tier': pricing_result.tier,
           'roi_projected': roi_projected
       },
       'expected_monthly_cop': expected_monthly
   },
```

---

## MÉTODOD DE IMPLEMENTACIÓN

### Paso 1: Diagnostic Generator (v4_diagnostic_generator.py)

1. Agregar `region: str` parámetro a `generate()` (línea 151)
2. Guardar `region` como instance variable o pasarlo a `_prepare_template_data()`
3. En `_prepare_template_data()`, agregar:
   - `hotel_location` (extraer de audit_result o usar region)
   - `hotel_region` (usar region)
   - `regional_context`, `hotel_landmark`, `urgencia_contenido`, `quick_wins_content`
   - `brecha_1_impacto` a `brecha_4_impacto`
   - `brecha_1_resumen` a `brecha_4_resumen`
   - Aliases: `gbp_score`, `gbp_status`, `seo_score`, `seo_status`, `aeo_score`, `aeo_status`, `monthly_loss`
4. Implementar los métodos helper faltantes

### Paso 2: Proposal Generator (v4_proposal_generator.py)

1. Agregar `region: str` parámetro a `generate()` (línea 141)
2. Pasar `region` a `_prepare_template_data()`
3. En `_prepare_template_data()`, agregar:
   - `hotel_location`, `hotel_region`
   - `monthly_loss`, `monthly_investment`
   - `inv_m1` a `inv_m6`, `rec_m1` a `rec_m6`
   - `total_investment`, `total_recovered`, `net_benefit`
   - `roi_6m`, `valid_until`

### Paso 3: main.py

1. Pasar `region=region` a `proposal_gen.generate()`
2. Poblar `v4_complete_report.json` con `assets_generated`, `coherence_score`, `financial_data`

---

## CRITERIOS DE ÉXITO (GATES)

| Gate | Criterio | Test |
|------|----------|------|
| G1 | diagnostico_v6: 0 placeholders `${...}` sin resolver | `grep -c '\${' 01_DIAGNOSTICO_*.md` → 0 |
| G2 | propuesta_v6: 0 placeholders `${...}` sin resolver | `grep -c '\${' 02_PROPUESTA_*.md` → 0 |
| G3 | v4_complete_report.json: `assets_generated` no está vacío | `jq '.assets_generated | length'` → > 0 |
| G4 | v4_complete_report.json: `coherence_score` existe al top level | `jq '.coherence_score'` → number |
| G5 | coherence_score en JSON coincide con coherence_score en documents | Comparar valores |

---

## ESFUERZO ESTIMADO

| Tarea | LOC | Tiempo |
|-------|-----|--------|
| Diagnostic: agregar region param + 20 vars | ~80 | 30 min |
| Proposal: agregar region param + 17 vars | ~60 | 30 min |
| main.py: pasar region + report JSON | ~30 | 15 min |
| Testing E2E con hotelvisperas | - | 20 min |
| **Total | ~170 | ~95 min (~1.5 horas)** |

---

## VERIFICACIÓN POST-IMPLEMENTACIÓN

```bash
# 1. Ejecutar pipeline completo
python main.py v4complete --url https://www.hotelvisperas.com/ --debug 2>&1 | tee evidence/e2e-cert-YYYYMMDD.log

# 2. Verificar 0 placeholders en diagnóstico
grep -c '\${' output/v4_complete/01_DIAGNOSTICO_*.md
# Esperado: 0

# 3. Verificar 0 placeholders en propuesta
grep -c '\${' output/v4_complete/02_PROPUESTA_*.md
# Esperado: 0

# 4. Verificar assets_generated en JSON
jq '.assets_generated | length' output/v4_complete/v4_complete_report.json
# Esperado: > 0

# 5. Verificar coherence_score en JSON
jq '.coherence_score' output/v4_complete/v4_complete_report.json
# Esperado: número (ej: 0.78)

# 6. Verificar no hay errores Python
# Buscar "Error" o "Exception" o "Traceback" en output
```

---

## NOTES

- **Coherence Validator** (línea 1891-1949) calcula `pre_coherence_score` ANTES de regenerar
  el diagnóstico, pero LO USA después para `diagnostic_gen.generate(coherence_score=pre_coherence_score)`.
  Esto es correcto — el score se calcula con datos actuales y se inyecta.

- **`safe_substitute()`** es la causa raíz: no falla en keys faltantes. Considerar cambiar a
  `substitute()` con validación previa, o al menos log un warning si quedan placeholders.

- **Región detection** está en main.py línea 1380: `_detect_region_from_url(args.url)`.
  Este valor debe fluir hasta los generadores.
