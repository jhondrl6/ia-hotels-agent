# Contexto: Propuesta Comercial Amaziliahotel — Auditoria y Plan de Mejora

## Referencia Cruzada

- **Documento auditado:** `output/v4_complete/02_PROPUESTA_COMERCIAL_20260423_145443.md`
- **Datos financieros:** `output/v4_complete/financial_scenarios.json`
- **Hotel:** Amaziliahotel (mts a la derecha, Via Pereira a #Entrada 8 Cafelia, 600, CERRITOS, Pereira, Risaralda)
- **URL:** https://amaziliahotel.com/
- **Fecha auditoria:** 2026-04-23

---

## Arquitectura del Generador (archivos clave)

| Archivo | Rol |
|---------|-----|
| `modules/commercial_documents/v4_proposal_generator.py` | Generador principal (1151 lineas). Clase `V4ProposalGenerator`. Busca template V6, cae a V4 embebido. |
| `modules/commercial_documents/service_catalog.py` | `SERVICE_CATALOG` (7 entries): mapea pain_id → servicio vendible. Creado en FASE-CAUSAL-REFACTOR. |
| `modules/asset_generation/proposal_asset_alignment.py` | `PROPOSAL_SERVICE_TO_ASSET` (7 servicios): mapea nombre servicio → asset_type. Backward-compat con SERVICE_CATALOG. |
| `modules/commercial_documents/templates/` | Solo existe `diagnostico_v4_template.md`. NO existe `propuesta_v6_template.md`. |
| `modules/financial_engine/pricing_resolution_wrapper.py` | `PricingResolutionResult` con `monthly_price_cop`. |
| `modules/commercial_documents/data_structures.py` | `DiagnosticSummary`, `FinancialScenarios`, `AssetSpec`, `format_cop()`. |

---

## PROBLEMAS IDENTIFICADOS (ordenados por severidad)

### BUG-1 (CRITICO): Seccion "Esto es lo que hacemos por usted" VACIA

**Sintoma:** Lineas 43-46 de la propuesta no tienen contenido entre el titulo y el cierre.

**Causa raiz en codigo:**
- `_generate_dynamic_services_table()` (v4_proposal_generator.py:658-694)
- Si `detected_pain_ids` es None o vacio, retorna `""` (linea 684)
- Los pain_ids vienen de `diagnostic_summary.pain_ids` que es None porque el flujo de pain detection no se ejecuto o no detecto pains
- El template V6 (que no existe) usa `${dynamic_services_table}` en esa posicion

**Fix propuesto:**
```python
# En _generate_dynamic_services_table, reemplazar linea 683-684:
else:
    # No pains detected — show empty (awaiting data)
    return ""
# POR:
else:
    # Fallback: mostrar los 7 servicios estandar del kit
    rows = ["| Servicio | Que obtiene |", "|----------|-------------|"]
    for entry in SERVICE_CATALOG.values():
        rows.append(f"| **{entry.service_name}** | {entry.description} |")
    return "\n".join(rows)
```

### BUG-2 (CRITICO): Escenarios financieros INVERTIDOS

**Sintoma:** `financial_scenarios.json` muestra:
```json
"conservative": 5076000.0,   // MAYOR
"realistic": 2610000.0,      // MEDIO
"optimistic": -189000.0      // NEGATIVO (absurdo)
```

**Problema:** Conservative > Realistic viola la definicion de escenarios. Optimistic negativo no tiene sentido. El `_get_main_value()` usa `monthly_loss_central` o `monthly_loss_max`, pero los escenarios estan mal ordenados.

**Datos de entrada (mayoria defaults):**
```json
"adr": "legacy_hardcode"     // $300.000 — NO es dato real
"rooms": "hotel_data"        // 10 habitaciones — dato real
"occupancy": "default"       // 0.5 (50%) — default
"direct_channel": "default"  // 0.2 (20%) — default
```

**Fix propuesto:** Auditar el calculo de escenarios en `modules/financial_engine/calculator_v2.py` y corregir el orden. Verificar que optimistic > realistic > conservative siempre.

### BUG-3 (CRITICO): ROI de 20.0X irreal

**Sintoma:** Propuesta muestra "ROI: 20.0 en 6 meses" ($783K inversion → $15.66M recuperacion).

**Causa raiz:**
- `_calculate_roi()` (linea 774-786): `roi_ratio = total_gain / total_investment`
- `total_gain = monthly_loss * 6 = $2.610.000 * 6`
- `total_investment = $130.500 * 6`
- NO incluye factor de recuperacion (asume 100% de la perdida se recupera)
- Pain ratio es solo 5% (`pricing.pain_ratio: 0.05`)

**Fix propuesto:**
1. Incluir `recovery_factor` en el ROI (15-25% realista, no 100%)
2. Mostrar ROI conservador (factor 0.15) y optimista (factor 0.25)
3. Anadir disclaimer: "Basado en recuperación parcial estimada"
4. Formula corregida: `roi = (monthly_loss * recovery_factor * 6) / (monthly_price * 6)`

### BUG-4 (ALTO): Tabla de entregables muestra errores

**Sintoma:** 5 de 7 items dicen "Requiere datos" o "No generado". Solo FAQ esta "Completo".

**Causa raiz:**
- `_generate_asset_quality_table()` (linea 696-753) usa `_confidence_to_nivel_significado()`
- Si `assets_generated` es None o parcial, muestra "No generado"
- La propuesta se genera ANTES de generar los assets reales

**Fix propuesto:**
1. Si asset no generado aun, mostrar "Incluido en su kit" con checkmark
2. Solo mostrar "Completo" / "En preparacion" (nunca "No generado")
3. Idealmente: generar assets primero, propuesta despues

### BUG-5 (ALTO): No existe template V6

**Sintoma:** Propuesta usa template V4 embebido en `_get_default_template()` (linea 234-436). La seccion "Asi funciona" (linea 108 del output) no aparece en el default template — viene de un template externo ya eliminado.

**Causa raiz:**
- `__init__` busca `propuesta_v6_template.md` (linea 142), no existe
- Cae a `propuesta_v4_template.md` (linea 144), tampoco existe
- Cae a `_get_default_template()` (linea 234) que no tiene "Asi funciona"
- Hay un tercer template embebido o un archivo temporal que genera esa seccion

**Fix propuesto:** Crear `templates/propuesta_v6_template.md` completo con todas las secciones dinamicas, usando las variables ya disponibles en `_prepare_template_data()`.

### BUG-6 (ALTO): Proceso "Asi funciona" hardcoded

**Sintoma:** Seccion lineas 108-128 es identica para todos los clientes.

**Causa raiz en codigo:**
- `_build_7_day_plan()` (linea 1061): retorna string fijo, IGNORA `asset_plan`
- `_build_30_day_plan()` (linea 1071): retorna string fijo, IGNORA `asset_plan`
- `_build_60_day_plan()` (linea 1078): string fijo
- `_build_90_day_plan()` (linea 1085): string fijo

**Fix propuesto:** Hacer los planes dinamicos basados en `asset_plan`. Si el hotel tiene schema pero no WhatsApp, el dia 4 cambia. Usar prioridades P1/P2/P3 de los assets para ordenar el timeline.

### BUG-7 (MEDIO): Datos financieros sin disclaimer

**Sintoma:** `financial_scenarios.json` tiene `disclaimer: "Estimacion basada en datos limitados..."` pero este disclaimer NO aparece en la propuesta generada.

**Fix:** Incluir `${disclaimer}` en el template cuando `evidence_tier` es "C" o los data_sources tienen defaults.

### BUG-8 (MEDIO): Ortografia

| Linea | Error | Correccion |
|-------|-------|------------|
| 20 | "buscan hotels" | "buscan hoteles" |
| 68 | "que su negocio brillen" | "que su negocio brille" |
| 68 | "debe prover" | "debe proveer" |
| 155 | "Absorption" | "Absorbido" |
| 157 | "protecion" | "proteccion" |

**Causa:** El template embebido tiene estos errores. Al crear el template V6, corregir todos.

### BUG-9 (BAJO): Secciones vacias

- Linea 131-133: "METRICAS DE VISIBILIDAD" sin contenido entre separadores
- Linea 135-139: GA4 no configurado (correcto, pero podria omitirse)
- Telefono placeholder "+57 300 000 0000" necesita dato real

---

## Mapeo Completo: Servicios → Assets → Pain IDs

| Servicio (PROPOSAL_SERVICE_TO_ASSET) | asset_type | SERVICE_CATALOG pain_id | Estado en propuesta |
|--------------------------------------|------------|------------------------|---------------------|
| Google Maps Optimizado | geo_playbook | low_gbp_score | Requiere datos |
| SEO Local | optimization_guide | poor_performance | Requiere datos |
| Boton de WhatsApp | whatsapp_button | no_whatsapp_visible | No generado |
| Datos Estructurados | hotel_schema | no_hotel_schema | Requiere datos |
| Informe Mensual | monthly_report | (sin mapeo en SERVICE_CATALOG) | Requiere datos |
| Pagina de FAQ | faq_page | no_faq_schema | Completo |
| Meta Tags Sociales (Open Graph) | open_graph | no_og_tags | No generado |

**Nota:** SERVICE_CATALOG tiene 7 entries incluyendo "barra_reserva_movil" que NO esta en PROPOSAL_SERVICE_TO_ASSET. Hay desalineacion.

---

## Flujo de Datos (como se genera la propuesta)

```
v4complete command
  → modules/orchestration_v4/ (flujo 2 fases)
    → financial_scenarios.json (calculado con datos limitados)
    → diagnostic_summary (con top_problems, faltantes, pain_ids=None)
  → V4ProposalGenerator.generate()
    → _prepare_template_data()  # linea 438
      → _generate_dynamic_services_table(pain_ids=None)  # retorna ""
      → _generate_asset_quality_table(assets_generated=None)  # muestra "No generado"
      → _calculate_roi()  # sin recovery_factor
    → _load_template()  # busca V6, V4, cae a default
    → _render_template()  # safe_substitute
  → output/v4_complete/02_PROPUESTA_COMERCIAL_*.md
```

---

## Variables de Template Disponibles (prepare_template_data)

Lista completa de variables que YA existen y pueden usarse en un template V6:

**Metadatos:** generated_at, version, hotel_id, proposal_id, valid_until, hotel_name, hotel_location, hotel_region

**Diagnostico:** critical_problems_count, quick_wins_count, overall_confidence, top_problems_list, score_tecnico, coherence_score

**Brechas (dinamicas):** brecha_1_nombre, brecha_1_costo ... brecha_4_nombre, brecha_4_costo

**Servicios/Assets:** dynamic_services_table (actualmente vacio si no hay pains), asset_quality_table (muestra errores)

**Financiero:** monthly_fee, setup_fee, projected_gain, roi_6_months, break_even_months, inv_m1..inv_m6, rec_m1..rec_m6, net_m1..net_m6, acc_m1..acc_m6, conservative_gain/roi, realistic_gain/roi, optimistic_gain/roi, total_investment_6m, recovered_6m, net_benefit_6m

**Plan:** plan_7d, plan_30d, plan_60d, plan_90d, plan_7_days, plan_30_days, plan_60_days, plan_90_days (todos hardcoded)

**Secciones compuestas:** geo_section, analytics_section, coherence_checklist, guarantees_section

**IAO:** openrouter_queries/cost, gemini_queries/cost, perplexity_queries/cost, total_iao_queries/cost (todos stub "—")

**Pago:** single_payment_total, single_payment_savings, quarterly_fee, quarterly_savings

---

## Precedentes Relevantes

- **FASE-CAUSAL (2026-04-23):** Se aplico parche estatico en vez de refactorizacion completa con SERVICE_CATALOG. Los pain_ids nunca se propagan al generador.
- **PROPOSAL_SERVICE_TO_ASSET:** 7 servicios (era 5). Se agrego open_graph y og_tags_guide.
- **385 tests pasando.** v4.35.0.
- **Windows/WSL:** Usar `venv/Scripts/python.exe` (NO .venv, NO system python3).

---

## Precedentes Relevantes

- **FASE-CAUSAL (2026-04-23):** Se aplico parche estatico en vez de refactorizacion completa con SERVICE_CATALOG. Los pain_ids nunca se propagan al generador.
- **PROPOSAL_SERVICE_TO_ASSET:** 7 servicios (era 5). Se agrego open_graph y og_tags_guide.
- **385 tests pasando.** v4.35.0.
- **Windows/WSL:** Usar `venv/Scripts/python.exe` (NO .venv, NO system python3).

---

## ANALISIS CRUZADO: Desalineaciones DIAGNOSTICO ↔ PROPUESTA ↔ CONTEXT (D-1 a D-8)

> Estas desalineaciones NO se derivan del codigo fuente — son contradicciones visibles entre los documentos generados. El context.md original solo cubria bugs de codigo. Esta seccion amplia el analisis a gaps de contenido y estrategia.

---

### D-1 [CRITICA — NO estaba en context.md] AEO (0/100) sin plan de recuperacion

**Hallazgo:**
- Diagnostico: AEO score = **0/100** — el peor de los 4 pilares.
- Propuesta: NO hay ningun entregable especifico para AEO.
- Seccion IAO en propuesta: metricas stub (— queries, — USD).
- La propuesta no dice COMO piensa mejorar la citabilidad en ChatGPT/Gemini/Perplexity.

**Impacto:** AEO es el mayor gap estructural y la propuesta lo ignora como oportunidad diferenciable.

---

### D-2 [CRITICA — NO estaba en context.md] Pain_ratio 5% vs. recuperacion 100% — inconsistencia interna del ROI

**Hallazgo — contradiction no captada por BUG-3:**

| Fuente | Valor |
|--------|-------|
| `financial_scenarios.json` (BUG-2 context) | `pain_ratio: 0.05` (5%) |
| Propuesta, proyeccion 6 meses | Recupera $15.660.000 = $2.610.000 × 6 (**100% de la perdida**) |
| Propuesta, tabla escenarios | "Realista: 20%" |

**El triangulo imposible:**
- Si `pain_ratio = 5%` → recuperacion realista = $2.610.000 × 5% = **$130.500/mes** = exactamente el costo del servicio (break-even falso)
- La propuesta muestra recuperacion de $2.610.000/mes (100%) pero en escenarios dice 20%
- BUG-3 detecta el ROI irreal pero NO detecta esta contradiccion entre pain_ratio, escenario realista, y la proyeccion de recuperacion

**Causa probable:** `pain_ratio` se configura en pricing defaults (0.05) pero NUNCA se recalcula con los datos reales del diagnostico. El generador de propuesta usa `monthly_loss` directo, ignora `pain_ratio`.

---

### D-3 [CRITICA — NO estaba en context.md] ADR hardcodeado a $300K — toda la proyeccion financiera es ficcion

**Hallazgo (amplificacion de BUG-2):**
```
"adr": "legacy_hardcode"      // $300.000 — NO es dato real
"rooms": "hotel_data"         // 10 habitaciones — dato real
"occupancy": "default"        // 0.5 (50%) — default
"direct_channel": "default"   // 0.2 (20%) — default
```

**3 de 4 inputs son defaults o hardcodeados.** La perdida de $2,610,000/mes se calcula sobre ADR ficiticio. La propuesta presenta numeros como Tier B cuando son Tier C.

El context.md menciona BUG-2 pero NO senala que **toda la proyeccion de ROI depende de ADR hardcodeado** — el ROI de 20X esta construido sobre arena. La cifra de $2.61M/mes NO esta validada con datos reales del hotel.

---

### D-4 [ALTA — NO estaba en context.md] Quick wins = 30 dias en diagnostico, promesa = 7 dias

| Documento | Timeline |
|-----------|----------|
| Diagnostico, QUICK WINS | Schema (1-2 dias) + FAQ (2-3 dias) + Fotos GBP (1 dia) = 30 dias total |
| Propuesta, "Asi funciona" | Dias 2-7: WhatsApp + Maps + datos ChatGPT **todos** |

La propuesta promete en 6 dias lo que el diagnostico planea en 30. Los entregables marcados "No generado" (WhatsApp, Meta Tags) contradicen directamente la promesa de implementacion en Dias 2-7. **La promesa de 7 dias es inalcanzable given the actual deliverable state.**

---

### D-5 [ALTA — NO estaba en context.md] WhatsApp como dolor sin cuantificacion en diagnostico

**Hallazgo:**
- Diagnostico: 4 brechas con impacto financeiro asignado (suma = 98%)
- **Ninguna brecha corresponde a WhatsApp**
- Propuesta: Boton de WhatsApp aparece como entregable principal y en la tabla comparativa
- Context.md mapea `whatsapp_button → no_whatsapp_visible` pero ese pain_id **nunca fue detectado** por el flujo de pain detection (D-1 del context original: `detected_pain_ids` es None)
- La propuesta presenta WhatsApp como "problema existente" pero no esta medido ni tiene impacto financeiro asignado

**Implicacion:** Si WhatsApp no es un pain detectado, no deberia aparecer como brecha独立性. Deberia estar en la propuesta como "mejora adicional" no como "problema que resolvemos".

---

### D-6 [ALTA] GA4 promise sin plan de implementacion ni costo

- Propuesta: promete "informe mensual con metricas reales" via GA4
- Diagnostico: GA4 no configurado, GSC no configurado
- Context.md: no hay bug asignado a la configuracion de GA4
- Sin linea de implementacion tecnica en los primeros 30 dias
- Sin costo de setup de GA4 en el modelo financiero

El onboarding del cliente deberia incluir GA4 como paso tecnico 0 (antes del dia 1), no como promesa postergada.

---

### D-7 [MEDIA — NO estaba en context.md] 6 de 7 entregables bloqueados antes de firma

| Entregable | Estado en propuesta |
|------------|---------------------|
| Google Maps Optimizado | ⚠️ Requiere datos |
| SEO Local | ⚠️ Requiere datos |
| Boton de WhatsApp | ❌ No generado |
| Datos Estructurados | ⚠️ Requiere datos |
| Informe Mensual | ⚠️ Requiere datos |
| Pagina de FAQ | ✅ Completo |
| Meta Tags Sociales | ❌ No generado |

**El cliente recibe una propuesta de "Kit Hospitalidad Digital" donde 6 de 7 items requieren accion posterior o estan bloqueados.** La promesa de valor se autodestruye antes de leer la propuesta.

BUG-4 del context.md captura esto parcialmente pero no senala el dano reputacional de mostrar "No generado" al cliente.

---

### D-8 [MEDIA] Sin competidores identificados

- Diagnostico: "Competidores con FAQ capturan ese trafico" — sin nombres
- Propuesta: menciona region Eje Cafetero pero no identifica hoteles especificos como referencia
- Imposible hacer un plan de diferenciacion sin saber contra quien se compite
- La propuesta pierde poder persuasivo sin competencia directa nombrada

---

## SINTESIS: Intervencion Integral — Agenda Preliminar

### FASE 0: Auditoria de datos y propagacion de pains

**Objetivo:** Verificar por que `detected_pains = None` y ADR = hardcode. Sin esto, cualquier generacion repite los mismos problemas.

**Pasos:**
1. Averiguar por que `pain_ids` es None en `DiagnosticSummary` — tracear el flujo desde `pain_detection.py` hasta `V4ProposalGenerator`
2. Verificar si el ADR de $300K es un fallback hardcodeado o si se puede extraer de la web
3. Si no hay pain detection, el parche de FASE-CAUSAL no resolvio el problema de raiz

**Tests a verificar:** `tests/test_proposal_alignment.py`

---

### FASE 1: Bloque critico de financiera

**Objetivo:** Que los numeros sean creibles antes de presentar cualquier propuesta.

1. **D-2 (pain_ratio inconsistente):** El generador debe usar `pain_ratio` en el calculo de recuperacion, no `monthly_loss` directo. O eliminar `pain_ratio` si no se usa.
2. **D-3 (ADR hardcodeado):** Incluir disclaimer explicito en Tier C: "ADR utilizado: estimado de $300K (verifique con datos reales)". Si el ADR es hardcode, el ROI debe decirlo.
3. **D-1 (AEO sin plan):** Agregar un 5to entregable dinamico para citabilidad IA si `aoe_score < 20`.
4. **BUG-3 (ROI realista):** Incluir `recovery_factor` (15-25%) en la proyeccion. Mostrar 3 escenarios de ROI.

---

### FASE 2: Credibilidad de entregables

**Objetivo:** Que 6/7 items no digan "No generado" o "Requiere datos".

1. **D-7:** Cambiar "No generado" → "Incluido en su kit (pendiente de implementacion)" — nunca mostrar errores al cliente
2. **BUG-5 (template V6):** Crear `templates/propuesta_v6_template.md` completo
3. **D-4:** Corregir promesa de 7 dias. Si los quick wins del diagnostico son 30 dias, la propuesta debe decir 30 dias para primeros resultados, no 7.
4. **D-5:** Si WhatsApp no es un pain detectado, NO debe aparecer como brecha独立性. Incluirlo como "mejora adicional".

---

### FASE 3: Plan de implementacion dinamico

**Objetivo:** Que los planes de 7/30/60/90 dias se adapten al hotel, no sean strings hardcoded.

1. **BUG-6:** Modificar `_build_N_day_plan()` para usar `asset_plan` y prioridades P1/P2/P3
2. **D-8:** Agregar seccion de competencia identificada en el diagnostico (usando GBP data de la region)
3. **D-6:** GA4 como paso de onboarding tecnico antes del dia 1 (no como promesa postergada)

---

### FASE 4: Contenido y AEO

**Objetivo:** Cerrar el gap de AEO (0/100) que la propuesta actual ignora.

1. Agregar entregable de "Contenido para citabilidad IA" si citability_score < 60
2. Incluir estrategia de content clusters para autoridades terciarias (tripadvisor, hostelworld, booking)
3. La propuesta deberia decir explicitamente que el servicio incluye optimizacion para ChatGPT/Gemini/Perplexity

---

### Resumen de brechas por fase

| Fase | Bugs | Desalineaciones | Estimacion |
|------|------|-----------------|------------|
| FASE 0 | Trazado pain_ids | D-2 causa raiz | 1-2 horas |
| FASE 1 | BUG-2, BUG-3 | D-1, D-2, D-3 | 3 horas |
| FASE 2 | BUG-1, BUG-4, BUG-5 | D-4, D-5, D-7 | 3 horas |
| FASE 3 | BUG-6 | D-6, D-8 | 2 horas |
| FASE 4 | (nuevo) | AEO gap | 2 horas |

**Total estimado: ~12 horas en 5 fases.**

---

## Tests existentes relevantes

- `tests/test_proposal_alignment.py` (3 tests de alineacion propuesta)
- `tests/delivery/test_delivery_packager.py` (tests de entrega que incluyen PROPUESTA_COMERCIAL)

---

## Flags para proxima sesion

- [ ] Verificar por que `detected_pain_ids = None` en el flujo real
- [ ] GA4 requiere configuracion real del cliente (no es tecnico de iah-cli)
- [ ] ADR real del hotel debe verificarse con el cliente antes de otra generacion
- [ ] El telefono placeholder +57 300 000 0000 necesita dato real en config
- [ ] BUG-8 (ortografia) pendiente desde context original
