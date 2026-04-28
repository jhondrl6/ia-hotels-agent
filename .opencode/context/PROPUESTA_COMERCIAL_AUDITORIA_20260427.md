# AUDITORÍA 02_PROPUESTA_COMERCIAL — Contexto Persistente (VALIDACIÓN v3)
## Amaziliahotel | 2026-04-26 | Auditoría: 2026-04-27 | Re-validación: 2026-04-27

---

## ARCHIVOS AUDITADOS

- **Propuesta**: `output/v4_complete/02_PROPUESTA_COMERCIAL_20260426_191233.md`
- **Diagnóstico**: `output/v4_complete/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260426_191231.md`
- **Financial scenarios**: `output/v4_complete/financial_scenarios.json`
- **Template V6**: `modules/commercial_documents/templates/propuesta_v6_template.md`
- **Módulos verificados**: `v4_proposal_generator.py`, `pricing_calculator.py`, `pricing_resolution_wrapper.py`, `calculator_v2.py`, `coherence_validator.py`, `asset_catalog.py`, `ai_crawler_auditor.py`, `service_catalog.py`, `pain_solution_mapper.py`, `proposal_asset_alignment.py`

---

## VALIDACIÓN EXHAUSTIVA — CADA HALLAZGO vs CÓDIGO REAL

### 1. PRECIO $130.500 COP/mes — "ALUCINADO"
- **VEREDICTO DOCUMENTO**: ❌ FALSO — El precio SÍ existe y tiene origen verificable
- **VALIDACIÓN**: ✅ **CONFIRMADO** — El precio es real y verificable
- **EVIDENCIA VERIFICADA**:
  - `financial_scenarios.json` línea 40: `"monthly_price_cop": 130500.0`, `"source": "legacy_fixed"`, `"pain_ratio": 0.05` ✓
  - `pricing_calculator.py` (164 líneas): tiered completo (boutique 3%, standard 2.5%, large 2%), GATE 3%-6% ✓
  - `pricing_resolution_wrapper.py` línea 26: `LEGACY_FIXED = "legacy_fixed"` ✓
  - `pricing_resolution_wrapper.py` línea 125: `source=PricingSource.LEGACY_FIXED.value` ✓
- **CÁLCULO**: `$2,610,000 × 5% (LEGACY_FIXED) = $130,500 COP` ✓

### 2. PROYECCIÓN FINANCIERA — beneficio neto $0
- **VEREDICTO DOCUMENTO**: ⚠️ PARCIALMENTE CORRECTO — bug template pain_ratio=0.05
- **VALIDACIÓN**: ✅ **CONFIRMADO** — Pero con corrección importante en la descripción del mecanismo
- **EVIDENCIA VERIFICADA**:
  - `v4_proposal_generator.py` línea 203: `self._current_pain_ratio = getattr(pricing_result, 'pain_ratio', 0.20) if pricing_result else 0.20` ✓
  - `v4_proposal_generator.py` línea 480: `pain_ratio = getattr(self, '_current_pain_ratio', 0.20)` ✓
  - `v4_proposal_generator.py` línea 481: `projected_monthly_gain = int(raw_monthly_loss * pain_ratio)` ✓
  - `v4_proposal_generator.py` líneas 529-540: `rec_m1`..`rec_m6` = `projected_monthly_gain`, `net_m1`..`net_m6` = `projected_monthly_gain - monthly_investment` ✓
- **CÁLCULO**: `2,610,000 × 0.05 = 130,500` → `rec = inv = $130,500` → `net = $0` ✓
- **PROPUESTA REAL**: Muestra exactamente `$0 COP` beneficio en los 6 meses ✓
- **CORRECCIÓN AL DOCUMENTO**: El documento dice "pain_ratio = 0.05 (legacy default cuando no hay pricing_result)". Esto es INEXACTO. El código muestra que:
  - Cuando `pricing_result` SÍ existe → usa `pricing_result.pain_ratio` = 0.05 (viene del wrapper)
  - Cuando `pricing_result` NO existe → fallback a 0.20 (NO 0.05)
  - Para Amaziliahotel, `pricing_result` SÍ fue proporcionado → pain_ratio = 0.05
  - El fallback 0.20 habría dado: `2,610,000 × 0.20 = $522,000` → net = $391,500/mes (mucho mejor)

### 3. NARRATIVA CONTRADICTORIA (SEO/AEO/IAO)
- **VEREDICTO DOCUMENTO**: ✅ CORRECTO
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- **EVIDENCIA VERIFICADA**:
  - Template V6 línea 26: `"Le pregunta a ChatGPT | No aparece | Reserva va a otro"` ✓
  - Diagnóstico: `"IAO 33/100 | Promedio Regional 20/100 | ✅ Superior"` ✓
  - La narrativa es siempre "No aparece" independientemente del score real

### 4. ESTADOS DE ENTREGABLES
- **VEREDICTO DOCUMENTO**: ⚠️ PARCIALMENTE CORRECTO — vienen de confidence_score
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- **EVIDENCIA VERIFICADA**:
  - `v4_proposal_generator.py` línea 792: `def _confidence_to_nivel_significado(self, confidence, assets_generated)` ✓
  - `confidence >= 0.7` → `"✅ Completo" / "Listo para implementar"` ✓
  - `confidence >= 0.4` → `"⚠️ En preparacion" / "Datos pendientes del cliente"` ✓
  - `confidence < 0.4` → `"🔧 En optimizacion" / "Mejora continua de calidad"` ✓
  - `assets_generated is None` → `"⏳ Incluido en su kit" / "Preparacion posterior a la firma"` ✓
- **PROPUESTA REAL**: Muestra "✅ Completo", "⚠️ En preparacion", "⏳ Incluido en su kit" ✓

### 5. SERVICIOS NO MAPEAN BRECHAS
- **VEREDICTO DOCUMENTO**: ⚠️ PARCIAL — mapeo existe pero implícito
- **VALIDACIÓN**: ✅ **CONFIRMADO** — 7+1 servicios con pain_id explícito
- **EVIDENCIA VERIFICADA** (`service_catalog.py`, 141 líneas):
  - `google_maps_optimizado` → `pain_id="low_gbp_score"` ✓
  - `seo_local` → `pain_id="poor_performance"` ✓
  - `boton_whatsapp` → `pain_id="no_whatsapp_visible"` ✓
  - `datos_estructurados` → `pain_id="no_hotel_schema"` ✓
  - `pagina_faq` → `pain_id="no_faq_schema"` ✓
  - `meta_tags_sociales` → `pain_id="no_og_tags"` ✓
  - `informe_mensual` → `pain_id="no_monthly_report"` ✓
  - `optimizacion_ia_generativa` → `pain_id="low_ia_readiness"` (condicional AEO < 20) ✓
- **PROPUESTA REAL**: Muestra exactamente estos 8 servicios ✓

### 6. COSTOS IAO — PLACEHOLDER EN BLANCO
- **VEREDICTO DOCUMENTO**: ✅ CORRECTO
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- **EVIDENCIA VERIFICADA**:
  - `v4_proposal_generator.py` línea 617: `# FIX-OPENROUTER-C: IAO cost transparency (stub - activates when API keys available)` ✓
  - Líneas 618-625: todos `'—'` (openrouter_queries, openrouter_cost, gemini_queries, gemini_cost, perplexity_queries, perplexity_cost, total_iao_queries, total_iao_cost) ✓
- **PROPUESTA REAL**: Muestra "— | — USD" en toda la tabla IAO ✓

### 7. ROI 0.2% — "NÚMERO SIN SENTIDO"
- **VEREDICTO DOCUMENTO**: ❌ FALSO — tiene cálculo verificable (0.2X)
- **VALIDACIÓN**: ✅ **CONFIRMADO** — ROI sí tiene cálculo verificable
- **EVIDENCIA VERIFICADA**:
  - `v4_proposal_generator.py` línea 815: `def _calculate_roi(self, investment, gain, months, recovery_factor=0.20)` ✓
  - Fórmula real: `roi_ratio = (gain × recovery_factor) / investment` ✓
  - Con datos: `(130,500 × 0.20) / 130,500 = 0.20` → `"0.2X"` ✓
  - Línea 553: `'roi_6m': roi_6_months.replace("X", "").strip()` → `"0.2"` (sin X ni %) ✓
- **PROPUESTA REAL**: Muestra `"ROI: 0.2 en 6 meses"` ✓
- **CORRECCIÓN MENOR**: El documento dice líneas 815-837. La función va de 815 a 837 ✓ (correcto)

---

## HALLAZGOS NUEVOS — RE-VALIDACIÓN

### N1. MÓDULOS FANTASMA EN AGENTS.md — 🔴 ALTA
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- AGENTS.md línea 148: `data_validation/consistency_checker.py | Validación inter-documento` ✓
- AGENTS.md línea 149: `data_validation/evidence_ledger.py | Almacén centralizado de evidencia` ✓
- AGENTS.md línea 150: `data_validation/contradiction_engine.py | Detección de hard/soft conflicts` ✓
- AGENTS.md líneas 399-401: También listados en árbol de directorios ✓
- **Ningún archivo .py existe** para estos módulos ✓ (0 resultados de búsqueda)

### N2. DOBLE MECANISMO DE PRICING — 🔴 ALTA
- **VALIDACIÓN**: ✅ **CONFIRMADO** — con corrección aritmética
- `pricing_resolution_wrapper.py` → LEGACY_FIXED 5% → `$130,500` ✓
- `v4_proposal_generator.py` línea 991: `_calculate_dynamic_price` → 2%, min $800K, max $2.5M ✓
- Código línea 192-195: `if pricing_result is not None → usa pricing_result; else → dynamic_price` ✓
- **CORRECCIÓN ARITMÉTICA**: El documento dice `expected_monthly = 4,065,300`. Cálculo real:
  - `5,076,000 × 0.70 = 3,553,200`
  - `2,610,000 × 0.20 = 522,000`
  - `(-189,000) × 0.10 = -18,900`
  - **Total = 4,056,300** (no 4,065,300 — diferencia de 9,000)
  - `2% × 4,056,300 = 81,126` → clamped a `$800,000` (mismo resultado final)

### N3. BUG TEMPLATE — REC = INV — 🔴 ALTA
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- Template V6 líneas 87-92: tabla con `${inv_m1}` a `${inv_m6}` y `${rec_m1}` a `${rec_m6}` ✓
- `v4_proposal_generator.py` líneas 523-546: inv = monthly_investment, rec = projected_monthly_gain, net = projected_monthly_gain - monthly_investment ✓
- Con pain_ratio=0.05: rec = inv → net siempre $0 ✓
- **PROPUESTA REAL**: 6 meses × "$130.500 | $130.500 | $0" ✓

### N4. TELÉFONO HARDCODED — 🟡 MEDIA
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- Template V6 línea 189: `"WhatsApp: +57 300 000 0000"` ✓
- Diagnóstico línea 84: `"WhatsApp verificado (+57 3104019049)"` ✓
- `audit_report.json` línea 54: `"phone_web": "+57 3104019049"` ✓
- El template NO inyecta el teléfono del diagnóstico → queda placeholder ✓

### N5. SERVICIO TRIMESTRAL FOTO $150.000 — 🟢 BAJA
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- Template V6 línea 79: `"servicio de actualización trimestral por $150.000 COP"` ✓
- No viene de `service_catalog.py` ni de ningún módulo de pricing ✓

### N6. COHERENCE VALIDATOR NO VALIDA PROYECCIÓN — 🟡 MEDIA
- **VALIDACIÓN**: ✅ **CONFIRMADO**
- `coherence_validator.py` línea 140: `self.checks.append(self._check_price_matches_pain(...))` ✓
- `coherence_validator.py` línea 420: `def _check_price_matches_pain` ✓
- Búsqueda de `projection_consistency`: 0 resultados ✓
- El validator NO detectaría la contradicción $0 beneficio vs $15.6M pérdida ✓

---

## HALLAZGOS ADICIONALES QUE EL DOCUMENTO ANTERIOR OMITE

### NEW-1. web_score HARDCODED — 🟡 MEDIA
- `v4_proposal_generator.py` línea 551: `'web_score': "85",  # Placeholder - ideally from audit`
- El score web es siempre "85" independientemente del audit real
- No se inyecta desde ningún módulo de auditoría

### NEW-2. DOBLE CONSERVATISMO EN ROI — 🔴 ALTA
- El ROI aplica DOS niveles de conservadurismo:
  1. `pain_ratio = 0.05` → solo reclama 5% de la pérdida como ganancia
  2. `recovery_factor = 0.20` → solo espera recuperar 20% de esa ganancia
- **Recuperación efectiva = 0.05 × 0.20 = 1% de la pérdida total**
- ROI final = 0.2X significa que por cada $1 invertido se recuperan $0.20
- Esto hace que la propuesta sea comercialmente INVIABLE (cualquier inversionista rechazaría 0.2X)
- El fix NO es solo subir pain_ratio — es revisar la arquitectura de doble descuento

### NEW-3. ROI SIN CONTEXTO — 🟡 MEDIA
- `v4_proposal_generator.py` línea 553: `'roi_6m': roi_6_months.replace("X", "").strip()`
- Remueve el sufijo "X", deja solo "0.2"
- **PROPUESTA REAL**: `"ROI: 0.2 en 6 meses"` — ambiguo (¿0.2%? ¿0.2X? ¿20%?)
- Debería mostrar "0.2X" o "20%" con contexto claro

### NEW-4. OPTIMISTIC SCENARIO NEGATIVO ($-189,000) — 🟡 MEDIA
- `financial_scenarios.json`: `"optimistic": -189000.0`
- Un escenario "optimista" negativo indica que el hotel YA está en equilibrio o ganancia
- Pero se usa como dato para `_calculate_dynamic_price`: `-189,000 × 0.10 = -18,900`
- La propuesta NUNCA menciona que el escenario optimista sea negativo
- El diagnóstico debería explicar qué significa esta anomalía

### NEW-5. LINEA 203 — CONFUSIÓN DE FALLBACK — 🟡 MEDIA
- El documento anterior describe incorrectamente el mecanismo de pain_ratio
- Dice: "pain_ratio = 0.05 (legacy default cuando no hay pricing_result)"
- Realidad: el código es `getattr(pricing_result, 'pain_ratio', 0.20) if pricing_result else 0.20`
  - Con pricing_result → 0.05 (del wrapper)
  - Sin pricing_result → 0.20 (NO 0.05)
- El fallback 0.20 es MÁS favorable que el 0.05 del pricing_result
- **Paradoja**: NO enviar pricing_result produce una propuesta MEJOR (beneficio $391,500 vs $0)

---

## RESUMEN DE VALIDACIÓN

### 7 hallazgos originales + 6 nuevos = 13 hallazgos totales
### 4 hallazgos adicionales nuevos = **17 hallazgos totales**

| # | Hallazgo | Veredicto | Severidad |
|---|----------|-----------|-----------|
| 1 | Precio $130,500 alucinado | ✅ CONFIRMADO: es real (legacy_fixed) | N/A (falso positivo del audit original) |
| 2 | Proyección beneficio $0 | ✅ CONFIRMADO: bug pain_ratio=0.05 | 🔴 Alta |
| 3 | Narrativa IAO contradictoria | ✅ CONFIRMADO | 🟡 Media |
| 4 | Estados inventados | ✅ CONFIRMADO: vienen de confidence_score | 🟢 Baja |
| 5 | Servicios sin mapeo | ✅ CONFIRMADO: 7+1 con pain_id explícito | 🟢 Baja |
| 6 | Costos IAO blanks | ✅ CONFIRMADO: stub FIX-OPENROUTER-C | 🟡 Media |
| 7 | ROI sin sentido | ✅ CONFIRMADO: tiene cálculo (0.2X) | N/A (falso positivo del audit original) |
| N1 | Módulos fantasma | ✅ CONFIRMADO: 3 módulos inexistentes | 🔴 Alta |
| N2 | Doble pricing | ✅ CONFIRMADO: $130.5K vs $800K | 🔴 Alta |
| N3 | Bug rec=inv | ✅ CONFIRMADO: net siempre $0 | 🔴 Alta |
| N4 | Teléfono placeholder | ✅ CONFIRMADO: 300 000 0000 | 🟡 Media |
| N5 | Foto $150.000 hardcoded | ✅ CONFIRMADO | 🟢 Baja |
| N6 | Validator sin proyección | ✅ CONFIRMADO | 🟡 Media |
| NEW-1 | web_score hardcoded 85 | ✅ NUEVO | 🟡 Media |
| NEW-2 | Doble conservadurismo ROI | ✅ NUEVO | 🔴 Alta |
| NEW-3 | ROI sin contexto (0.2 vs 0.2X) | ✅ NUEVO | 🟡 Media |
| NEW-4 | Escenario optimista negativo | ✅ NUEVO | 🟡 Media |
| NEW-5 | Confusión fallback pain_ratio | ✅ NUEVO | 🟡 Media |

### Errores del documento anterior corregidos:
1. **Línea 203 mal descrita**: Decía "pain_ratio=0.05 (legacy default)". Real: 0.05 viene de pricing_result.pain_ratio, el fallback es 0.20
2. **Aritmética N2**: Decía 4,065,300. Real: 4,056,300 (off por 9,000)
3. **No documentó**: doble conservadurismo ROI (pain_ratio × recovery_factor)

---

## ESTRATEGIA ACTUALIZADA — 7 FASES (CORREGIDA)

### Principio Rector (reconfirmado)
> **No parchear la propuesta. Corregir el pipeline que la genera.**

### FASE 1: FIX BUG TEMPLATE (rec ≠ inv) — PRIORIDAD CRÍTICA
- **Problema**: `projected_monthly_gain` con `pain_ratio=0.05` = `$130,500` = `monthly_investment` → beneficio siempre `$0`
- **Fix**: El template debe usar `raw_monthly_loss × recovery_factor` para la proyección, NO `raw_monthly_loss × pain_ratio`
  - `pain_ratio` es para PRICING (cuánto cobrar vs cuánto dolor)
  - `recovery_factor` es para PROYECCIÓN (cuánto se recupera)
  - Actualmente se mezclan: pain_ratio se usa para ambas cosas
- **Archivo**: `v4_proposal_generator.py` ~480-481
- **Cambio**: `projected_monthly_gain = int(raw_monthly_loss * pain_ratio)` → `projected_monthly_gain = int(raw_monthly_loss * 0.20)` (recovery_factor realista)
- **Resultado esperado**: `$2,610,000 × 0.20 = $522,000` → net = `$522,000 - $130,500 = $391,500/mes`

### FASE 2: UNIFICAR PRICING — PRIORIDAD ALTA
- **Problema**: Dos caminos producen precios radicalmente diferentes ($130.5K vs $800K)
- **Fix**: Eliminar `_calculate_dynamic_price` (línea 991-1007). El pipeline SIEMPRE usa `pricing_resolution_wrapper`
- **Nota**: Para boutique 10 hab, el hybrid calculator daría min $1,200,000 (3% × $2.61M = $78,300 → clamped a $1.2M). Esto es 9× el precio actual. Revisar si el GATE está bien calibrado para hoteles pequeños.

### FASE 3: COHERENCE VALIDATOR — CHECK DE PROYECCIÓN — PRIORIDAD ALTA
- **Problema**: No detecta $0 beneficio vs $15.6M pérdida
- **Fix**: Agregar `_check_projection_consistency()` en `coherence_validator.py`
- **Regla**: `IF net_benefit == 0 AND raw_monthly_loss > 0 THEN WARNING`
- **Archivo**: `coherence_validator.py` después de línea 420

### FASE 4: ELIMINAR MÓDULOS FANTASMA DE AGENTS.md — PRIORIDAD MEDIA
- **Problema**: 3 módulos documentados pero inexistentes
- **Fix**: Remover de AGENTS.md líneas 148-150 y 399-401
- **Alternativa**: Crear stubs mínimos si se planean implementar

### FASE 5: CORREGIR NARRATIVA IAO — PRIORIDAD MEDIA
- **Problema**: Template siempre dice "No aparece" sin importar el score
- **Fix**: Hacer la fila ChatGPT del template condicional:
  - Si IAO > promedio → "Ya tiene presencia IA | Podemos mejorarla | Más reservas de IA"
  - Si IAO ≤ promedio → "No aparece" (actual)
- **Archivo**: Template V6 línea 26 + lógica en `_prepare_template_data`

### FASE 6: INYECTAR DATOS REALES — PRIORIDAD BAJA
- **6a**: WhatsApp: inyectar `audit_result.phone_web` al template en vez de placeholder
- **6b**: web_score: inyectar desde audit en vez de hardcoded "85"
- **6c**: ROI: restaurar sufijo "X" → `"ROI: 0.2X"` en vez de `"ROI: 0.2"`
- **6d**: Servicio foto $150.000: mover a `service_catalog.py` o mantener como literal del template
- **Archivos**: `v4_proposal_generator.py` líneas 551, 553, 575-579 + Template V6

### FASE 7: REGENERAR PROPUESTA CON PIPELINE CORREGIDO
- Después de Fases 1-6, regenerar y validar:
  - Precio desde pricing_resolution_wrapper ✓
  - Beneficio neto ≠ $0 ✓
  - ROI > 0.2X con proyección realista ✓
  - WhatsApp real inyectado ✓
  - Narrativa IAO consistente ✓
  - Coherence validator detecta inconsistencias ✓

---

## MATRIZ DE CLASIFICACIÓN FINAL

| Validación | Estado Actual | Meta Post-Fix |
|-----------|--------------|---------------|
| Precio con fuente de módulo | ✅ Ya tiene (legacy_fixed) | ✅ Unificado (solo wrapper) |
| Proyección ≠ $0 | ❌ Siempre $0 | ✅ Basada en recovery_factor |
| ROI > 0.2X | ❌ 0.2X (1% efectivo) | ✅ > 1.0X realista |
| ROI con contexto claro | ❌ "0.2" sin unidad | ✅ "2.0X" con contexto |
| Estados de entregables | ✅ confidence_score | ✅ Mantiene |
| Costos IAO reales | ❌ Stubs (—) | ⚠️ Mantiene (sin API keys) |
| Narrativa IAO consistente | ❌ Siempre "No aparece" | ✅ Condicional al score |
| Brechas → servicios | ✅ 7+1 pain_id mapeados | ✅ Mantiene |
| WhatsApp real | ❌ Placeholder 300 000 0000 | ✅ Desde audit |
| Coherence validator proyección | ❌ No valida | ✅ Detecta $0 vs pérdida |
| Pricing unificado | ❌ Dual ($130K vs $800K) | ✅ Solo wrapper |
| web_score real | ❌ Hardcoded "85" | ✅ Desde audit |
| Módulos fantasma | ❌ 3 en AGENTS.md | ✅ Removidos |

---

## REGISTRO DE AUDITORÍA

- Fecha auditoría original: 2026-04-27
- Fecha re-validación exhaustiva: 2026-04-27
- Método: Verificación directa contra código fuente (10 módulos + template + output)
- Resultado: 13 hallazgos previos CONFIRMADOS, 4 nuevos hallazgos agregados, 3 errores del documento corregidos
- Contexto listo para: diseño de plan de implementación en próxima sesión
