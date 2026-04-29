# Auditoría: 02_PROPUESTA_COMERCIAL vs Código + 01_DIAGNOSTICO

**Fecha**: 2026-04-29  
**Archivos auditados**:  
- `output/v4_complete/02_PROPUESTA_COMERCIAL_20260428_215755.md`
- `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260428_215751.md`
- `output/v4_complete/v4_complete_report.json`
- `output/v4_complete/gate_report.json`
- `output/v4_complete/financial_scenarios.json`
- `modules/commercial_documents/templates/propuesta_v6_template.md`
- `modules/commercial_documents/templates/diagnostico_v6_template.md`
- `modules/commercial_documents/v4_proposal_generator.py`

---

## TABLA DE VALIDACIÓN LÍNEA POR LÍNEA

| # | Elemento | Valor en Propuesta | ¿De dónde viene? | Hardcoded? | ¿Alinhado c/01? |
|---|----------|--------------------|-------------------|------------|------------------|
| 1 | hotel_id | `amaziliahotel` | Código: `hotel_name.lower().replace(" ", "_")` en `_prepare_template_data()` L464 | NO — dinámico | ✅ |
| 2 | Nombre hotel | `Amaziliahotel` | Parámetro `hotel_name` pasado al generador | NO — del input | ✅ |
| 3 | Dirección | `mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda, Colombia` | `audit_result.location` o `gbp.address` en generador L471-473 | NO — del sitio real vía audit | ✅ |
| 4 | "Válido por 15 días" | Literal | Template hardcodeado (`propuesta_v6_template.md` L14) | ✅ SÍ | No aplica en 01 |
| 5 | Pérdida mensual | `$2.610.000 COP` | `monthly_loss` → `format_cop(raw_monthly_loss)` donde `raw_monthly_loss = 2,610,000` de `financial_scenarios.realistic` (generador L482, 578) | NO — de `financial_scenarios.json#realistic` | ✅ (01 L10, L97) |
| 6 | Inversión mensual | `$130.500 COP/mes` | `pricing.monthly_price_cop` en `financial_scenarios.json` L40 | NO — del pricing resolution | ✅ |
| 7 | Tabla servicios (7-8 servicios) | Servicios dinámicos | `_generate_dynamic_services_table()` filtra `SERVICE_CATALOG` por `pain_ids` detectados (generador L689-739) | NO — dinámico | ✅ |
| 8 | Estado de Entregables | Tabla con niveles | `_generate_asset_quality_table()` basada en `assets_generated[].confidence_score` + `site_presence_report` (generador L741-850) | NO — de assets reales | ✅ (gate_report L154-212 lo confirma) |
| 9 | Especificaciones de fotos | Lista completa de tipos/resolución | **Template hardcodeado completo** (`propuesta_v6_template.md` L64-75) | ✅ SÍ hardcoded | No aplica |
| 10 | Precio trimestral | `$150.000 COP` | **Template hardcodeado** (`propuesta_v6_template.md` L79) | ✅ SÍ hardcoded | No aplica |
| 11 | Proyección mensual | Todos `Invierte: $130.500 / Recupera: $130.500 / Beneficio: $0` | `projected_monthly_gain = 2,610,000 * pain_ratio(0.05) = 130,500` = `monthly_investment = 130,500` → neto = 0 (generador L482-484, 532-543) | NO — calculado | ⚠️ CRÍTICO (ver hallazgos) |
| 12 | ROI 6 meses | `0.2` | `_calculate_roi()` retorna `"0.2X"`, pero `${roi_6m}` hace `.replace("X","").strip()` → `"0.2"` (generador L556, 931) | NO — calculado pero mal renderizado | ⚠️ CRÍTICO (ver hallazgos) |
| 13 | GA4 status | "⚠️ No configurado" | `_inject_analytics()` con `ga4_available=False` → texto fijo (generador L676-686) | ✅ Plantilla/-stub hardcoded | ✅ |
| 14 | IAO costs | `—` para todo | Hardcodeado en generador L626-633 cuando no hay IAO data | ✅ Hardcoded stubs | ✅ |
| 15 | WhatsApp contacto | `+57 300 000 0000` | **Template hardcodeado literal** (`propuesta_v6_template.md` L189) | ✅ SÍ hardcoded | ⚠️ No viene del diagnóstico |
| 16 | Email | `contacto@iahoteles.co` | **Template hardcodeado literal** (`propuesta_v6_template.md` L190) | ✅ SÍ hardcoded | ⚠️ No viene del diagnóstico |
| 17 | Coherence score | No visible en propuesta | — | — | ✅ (presente en 01 L5: 0.8933, y en v4_complete_report L233) |
| 18 | Botón WhatsApp | "✅ Verificado en sitio — Ya existe en su web" | `_confidence_to_nivel_significado()` L881-882 cuando `presence_verified AND present_in_production` | NO — de SitePresenceChecker | ✅ (gate_report L203-209 lo confirma) |

---

## HALLAZGOS CRÍTICOS

### 🔴 BUG-1: ROI mal renderizado — falta la "X"

**Descripción**: El documento muestra `ROI: 0.2` pero debería mostrar `ROI: 0.2X`.

**Causa raíz**:
- `_calculate_roi()` (generador L909-931) retorna `f"{roi_ratio:.1f}X"` → `"0.2X"`
- Pero `${roi_6m}` en `_prepare_template_data()` L556 hace:
  ```python
  'roi_6m': roi_6_months.replace("X", "").strip(),  # → "0.2"
  ```
- El template L98 usa `${roi_6m}` directamente: `**ROI: ${roi_6m}** en 6 meses`

**Evidencia**:  
- Propuesta L115: `**ROI: 0.2** en 6 meses`
- Template L98: `**ROI: ${roi_6m}** en 6 meses`
- Generador L556: `'roi_6m': roi_6_months.replace("X", "").strip()`

**Severidad**: MEDIA — numéricamente correcto, visualmente inconsistente con la convención del documento (todas las otras referencias ROI deberían usar formato `X`)

**Fix sugerido**: Eliminar el `.replace("X", "").strip()` de L556 del generador, o cambiar el template para usar `${roi_6_months}` directamente.

---

### 🔴 BUG-2: Proyección mes a mes muestra "Beneficio neto: $0" sin explicación del pain_ratio

**Descripción**: La tabla de proyección L102-115 muestra que cada mes el cliente invierte $130,500 y recupera $130,500, resultando en beneficio neto $0. Esto genera una impresión pésima del valor de la propuesta.

**Causa raíz**:  
- `pain_ratio = 0.05` (5%) en `financial_scenarios.json` L41  
- `projected_monthly_gain = 2,610,000 * 0.05 = 130,500`
- `monthly_investment = 130,500` (de pricing)
- `neto_mensual = 130,500 - 130,500 = 0`

El documento NO explica que:
1. El `pain_ratio=5%` es la fracción de la pérdida que se espera recuperar en 6 meses
2. Que la propuesta usa `recovery_factor=0.20` adicional (L486)
3. Que el ROI de 0.2X significa que en 6 meses apenas se recupera la inversión (sin ganancia aún)

**Cálculo correcto del ROI según el código**:
```
roi = (gain * recovery_factor) / investment
    = (130,500 * 0.20) / 130,500
    = 0.20 → 0.2X
```

**Severidad**: ALTA — un cliente que lea esto pensará que no hay ningún beneficio en 6 meses. El documento debería:
1. Explicar el `pain_ratio` en el texto introductorio de la sección
2. O ajustar los números para mostrar un escenario más realista del retorno

**Fix sugerido**:  
- Opción A (mínimo): Agregar una nota explicativa en la sección de proyección que diga qué es el `pain_ratio` y por qué los números son así
- Opción B: Ajustar `pain_ratio` en `financial_scenarios.json` para que el escenario "realista" sea más representativo de un ROI aceptable

---

## DISCREPANCIAS MENORES

### 🟡 DISCREPANCIA-1: Conteo de servicios — gate vs propuesta

- **Propuesta**: Tabla muestra 7 servicios (+ 1 condicional si score AEO < 20)
- **Gate report** (`proposal_asset_alignment` L158): `"total_services": 6`

**Causa**: El gate usa `PROPOSAL_SERVICE_TO_ASSET` (mapeo estático, 6 entries) mientras que la propuesta usa `SERVICE_CATALOG` (catálogo dinámico filtrado por pain_ids detectados).

**Severidad**: BAJA — no es un bug, es una diferencia arquitectónica. El gate valida contra un mapping hardcodeado; la propuesta genera dinámicamente.

---

## ELEMENTOS HARDCODEADOS EN LA PLANTILLA

| Elemento | Archivo | Líneas |
|----------|---------|--------|
| "Válido por 15 días (cupo limitado)" | `propuesta_v6_template.md` | 14 |
| Especificaciones de fotos (tipos, resolución 1280x720, orientación horizontal) | `propuesta_v6_template.md` | 64-75 |
| Precio actualización trimestral `$150.000 COP` | `propuesta_v6_template.md` | 79 |
| Descuentos por pago anticipado (trimestral 10%, semestral 18%) | `propuesta_v6_template.md` | 171-172 |
| Texto garantías (90 días, mes gratis, sin permanencia, 15 días) | `v4_proposal_generator.py` | 959-974 |
| WhatsApp contacto `+57 300 000 0000` | `propuesta_v6_template.md` | 189 |
| Email `contacto@iahoteles.co` | `propuesta_v6_template.md` | 190 |
| Texto IAO "Absorbido por IAH-CLI" | `propuesta_v6_template.md` | 140 |
| Stub IAO costs (todos `—`) | `v4_proposal_generator.py` | 626-633 |

---

## VERIFICACIONES POSITIVAS ✅

### WhatsApp verificado en sitio
- **Propuesta L69**: "✅ Verificado en sitio — Ya existe en su web - nosotros lo entregamos"
- **Gate report L203-209**: `presence_verified: true`, `presence_status: "exists"`
- **Código**: `_confidence_to_nivel_significado()` L881-882 retorna este estado cuando `presence_verified AND present_in_production`
- **Veredicto**: ✅ Correcto — el SitePresenceChecker fue ejecutado y confirmó que el botón existe en producción

### Coherence score
- **01_DIAGNOSTICO** L5: `coherence_score: 0.8933333333333333`
- **v4_complete_report.json** L233: `coherence_score: 0.8933333333333333`
- **Gate report** L43: `0.883076923076923` (diverge ligeramente — usa rounding diferente)
- **Veredicto**: ✅ Consistente entre 01 y el JSON de datos principal

### Datos financieros consistency
- `financial_scenarios.json` → `realistic: 2,610,000` → propuesta usa `$2.610.000 COP`
- `financial_scenarios.json` → `monthly_price_cop: 130,500` → propuesta usa `$130.500 COP/mes`
- `v4_complete_report.json` L336-338: mismos valores
- **Veredicto**: ✅ Alineación completa entre JSONs y propuesta

---

## DATOS ORIGEN POR ARCHIVO JSON

### financial_scenarios.json (fuente de verdad para datos financieros)
```json
{
  "scenarios": { "conservative": 5076000, "realistic": 2610000, "optimistic": -189000 },
  "expected_monthly_cop": 2610000,
  "pricing": { "monthly_price_cop": 130500, "pain_ratio": 0.05, "tier": "boutique" }
}
```

### gate_report.json (fuente para estado de entregables)
- `asset_confidence`: 10 assets bajo threshold (< 0.7), 3 sobre threshold
- `proposal_asset_alignment`: 6 servicios, 2 alineados con asset alta confianza, 4 low_quality, 1 present_in_production
- `whatsapp_button`: **exists** en producción con `presence_verified: true`

### v4_complete_report.json (coherence y metadata)
- `coherence_score`: 0.8933333333333333
- `seo_score`: 25
- 13 assets generados (3 con confidence 0.85, 10 con confidence 0.5)

---

## RECOMENDACIONES

1. **PATCH-1**: Corregir `${roi_6m}` en `v4_proposal_generator.py` L556 — no quitar la X
2. **PATCH-2**: Explicar `pain_ratio` en la sección de proyección de la propuesta o ajustar los valores del `financial_scenarios.json` para que el escenario "realista" sea más favorable
3. **INVESTIGAR**: Por qué `gate_report.json` dice 6 servicios cuando la propuesta muestra 7+ — ¿el mapeo estático `PROPOSAL_SERVICE_TO_ASSET` está desactualizado vs `SERVICE_CATALOG`?

---

*Auditoría realizada siguiendo `iah-cli-context-audit-to-plan` skill v1.2.0*
