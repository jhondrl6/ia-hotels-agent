# Documentación Post-Proyecto — Fix geo_enriched → Delivery Bridge + Assets Completos

**Proyecto:** AUDIT-PIPELINE-DESALINEACIONES-ASSETS
**Fecha inicio:** 2026-04-12 (v2 — ampliado)
**Estado:** EN PROGRESO

---

## Resumen Ejecutivo

### Problema
El pipeline de iah-cli generaba assets de delivery con datos placeholder (confidence 0.5) mientras que `geo_enriched/` contenía los datos reales pero nunca se entregaba al cliente. Además, 3 de 7 servicios prometidos en la propuesta comercial NO generaban asset correspondiente.

### Solución
1. Bridge que conecta `geo_enriched/` con el pipeline de delivery
2. Asegurar que los 7 servicios de la propuesta generen asset
3. Transparencia de calidad de assets al cliente
4. Publication gates que verifican presencia + calidad

---

## Sección A: Módulos Nuevos

| Módulo | Descripción | Fase |
|--------|-------------|------|
| `modules/asset_generation/geo_enriched_bridge.py` | Bridge enrichment geo_enriched → delivery | FASE-GEO-BRIDGE |
| `modules/asset_generation/monthly_report_generator.py` | Generador de informe mensual | FASE-ASSETS-VALIDACION |
| `modules/asset_generation/proposal_asset_alignment.py` | Verificador propuesta → asset | FASE-ASSETS-VALIDACION |
| `tests/asset_generation/test_geo_enriched_bridge.py` | Tests bridge | FASE-GEO-BRIDGE |
| `tests/quality_gates/test_asset_confidence_gate.py` | Tests gate confidence | FASE-CONF-GATE |
| `tests/asset_generation/test_llmstxt_generator.py` | Tests llms.txt fix | FASE-LLMSTXT-FIX |
| `tests/asset_generation/test_monthly_report.py` | Tests informe mensual | FASE-ASSETS-VALIDACION |
| `tests/asset_generation/test_voice_guide_generation.py` | Tests voice guide | FASE-ASSETS-VALIDACION |
| `tests/asset_generation/test_whatsapp_button.py` | Tests WhatsApp button | FASE-ASSETS-VALIDACION |
| `tests/asset_generation/test_proposal_alignment.py` | Tests alineación | FASE-ASSETS-VALIDACION |
| `tests/quality_gates/test_proposal_alignment_gate.py` | Tests gate #9 | FASE-ASSETS-VALIDACION |
| `tests/commercial_documents/test_proposal_confidence_disclosure.py` | Tests disclosure | FASE-CONFIDENCE-DISCLOSURE |
| `tests/postprocessors/test_document_quality_gate.py` | Tests content scrubber | FASE-CONTENT-SCRUBBER |

---

## Sección B: Módulos Modificados

| Módulo | Cambio | Fase |
|--------|--------|------|
| `modules/asset_generation/conditional_generator.py` | Bridge integration + voice/whatsapp fix | GEO-BRIDGE, ASSETS-VALID |
| `modules/asset_generation/v4_asset_orchestrator.py` | Llamada al bridge post-generación | GEO-BRIDGE |
| `modules/asset_generation/asset_catalog.py` | Agregar monthly_report, fix promised_by | ASSETS-VALID |
| `modules/quality_gates/publication_gates.py` | Gate #8 confidence + gate #9 alignment | CONF-GATE, ASSETS-VALID |
| `modules/asset_generation/llmstxt_generator.py` | Fallback a geo_enriched/llms.txt | LLMSTXT-FIX |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Sincronizar/eliminar embebido | TEMPLATE-DEBT |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Typo fix + tabla calidad | TEMPLATE-DEBT, CONFIDENCE-DISC |
| `modules/commercial_documents/v4_proposal_generator.py` | Generación tabla calidad dinámica | CONFIDENCE-DISC |
| `modules/postprocessors/document_quality_gate.py` | Self-replacement + spacing fixes | CONTENT-SCRUBBER |

---

## Sección C: Archivos Eliminados

*(Ninguno de momento — template embebido pendiente de decisión en FASE-TEMPLATE-DEBT)*

---

## Sección D: Métricas Acumulativas

| Métrica | Antes (v4.28.0) | Después (v4.29.0) | Cambio |
|---------|-----------------|-------------------|--------|
| Assets con confidence < 0.7 | 10/10 (100%) | 7/10 (70%) (FASE-GEO-BRIDGE resuelve 3: hotel_schema, llms_txt, faq_page) | -3 |
| Servicios prometidos con asset | 4/7 (57%) | 7/7 (100%) | +3 |
| Assets placeholders | 2 (hotel_schema, llms_txt) | 0 | -2 |
| Confidence promedio assets | 0.50 | TBD | +0.35 |
| Publication gates | 7 | 9 | +2 |
| Self-replacement warnings | 3 | TBD | -3 |
| Typos de espaciado | 1 ("debeproveer") | 0 | -1 |

---

## Sección D2: Costo de APIs Externas

| API | Uso | Costo Estimado | Observaciones |
|-----|-----|-----------------|---------------|
| OpenRouter (Hermes fallback) | Fallback si MiniMax falla | $0 si no se activa | Verificar logs post-ejecución |
| GA4 API | Tráfico indirecto | $0 (hasta 10M events/mes) | Solo si --ga4-property-id |
| PageSpeed API | Auditoría rendimiento | $0 | Rate limited |
| SerpAPI / GSC | Keywords y posiciones | $0 (cuota gratuita) | Advisory mode |

| Métrica | Antes (v4.28.0) | Después (v4.29.0) | Cambio |
|---------|-----------------|-------------------|--------|
| Tests totales | 2150+ | TBD (+13) | +13 |

---

## Sección H: Monitoreo de OpenRouter (Hermes Fallback)

OpenRouter NO es usado por iah-cli directamente. Es el **fallback de Hermes Agent** cuando MiniMax falla (429/503/529).

### Estado Esperado Post-v4complete
- [ ] **Fallback activations == 0** (MiniMax funcionó sin errores)
- [ ] **OpenRouter costs == $0** (no se facturó)

### Si Fallback se Activó
- [ ] Documentar: ¿Qué modelo usó? (buscar en `~/.hermes/logs/`)
- [ ] Documentar: ¿Cuántos tokens approximate?
- [ ] Investigar: ¿Por qué MiniMax falló? (¿rate limit? ¿ outage?)
- [ ] Si >3 activaciones en una ejecución → issue de estabilidad MiniMax

### Comando de Verificación
```bash
grep -i "fallback\|openrouter\|provider.*switch" ~/.hermes/logs/*.log 2>/dev/null | tail -20
```

---

## Sección E: Archivos Afiliados Actualizados

### CHANGELOG.md
- [ ] Entrada [4.29.0] con todos los cambios (pendiente al final release)

### GUIA_TECNICA.md
- [x] Nota técnica: "geo_enriched bridge para assets" ✅ (FASE-GEO-BRIDGE)
- [ ] Nota técnica: "asset_confidence_gate"
- [ ] Nota técnica: "proposal_asset_alignment_gate"
- [ ] Nota técnica: "llms.txt fallback"
- [ ] Nota técnica: "monthly_report generator"
- [ ] Nota técnica: "confidence disclosure en propuesta"

### REGISTRY.md
- [x] FASE-GEO-BRIDGE ✅ (2026-04-13)
- [ ] FASE-CONF-GATE ✅
- [ ] FASE-LLMSTXT-FIX ✅
- [ ] FASE-ASSETS-VALIDACION ✅
- [ ] FASE-CONFIDENCE-DISCLOSURE ✅
- [ ] FASE-TEMPLATE-DEBT ✅
- [ ] FASE-CONTENT-SCRUBBER ✅
- [ ] FASE-RELEASE v4.29.0 ✅

### docs/CONTRIBUTING.md
- [ ] Verificar que Sección E checklist se actualizó

---

## Sección F: Validaciones Pre-Commit

```bash
# Ejecutar tras cada fase
./venv/Scripts/python.exe scripts/run_all_validations.py --quick

# Ejecutar tras todas las fases
./venv/Scripts/python.exe scripts/version_consistency_checker.py
./venv/Scripts/python.exe main.py --doctor
```

---

## Sección G: Criterios de Validación Post-Release

Al ejecutar `v4complete --url https://amaziliahotel.com/` después de FASE-RELEASE:

### Presencia (que no falte)
| Criterio | Verificación |
|----------|-------------|
| 13+ tipos de asset | `v4_complete_report.json` → `assets_generated[].asset_type` count >= 13 |
| monthly_report presente | Directorio `monthly_report/` existe en output |
| voice_assistant_guide presente | Directorio `voice_assistant_guide/` existe en output |
| whatsapp_button presente | Directorio `whatsapp_button/` existe en output |
| 7/7 servicios con asset | `proposal_asset_alignment` → `missing == 0` |

### Efectividad (que materialice soluciones)
| Criterio | Verificación |
|----------|-------------|
| hotel_schema sin placeholder | `hotel_schema/*.json` → `name == "Amaziliahotel"` |
| llms_txt sin placeholder | `llms_txt/*.txt` → contiene `amaziliahotel.com` |
| voice_assistant_guide con contenido | Archivo contiene "Google Assistant" Y "Apple" Y "Alexa" |
| whatsapp_button funcional | Archivo HTML contiene número telefónico o disclaimer claro |
| monthly_report con KPIs | Archivo contiene "tráfico" Y "reservas" Y "métricas" |

### Calidad y Transparencia
| Criterio | Verificación |
|----------|-------------|
| Confidence >= 0.7 | `assets_generated[].confidence_score` todos >= 0.7 |
| Tabla calidad en propuesta | `02_PROPUESTA*.md` contiene "Estado de los Entregables" |
| Publication gates = 9 | `phase_4_publication_gates.gate_results.length == 9` |
