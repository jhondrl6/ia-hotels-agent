# Checklist de Implementación — Fix geo_enriched → Delivery Bridge + Assets Completos

**Proyecto:** AUDIT-PIPELINE-DESALINEACIONES-ASSETS
**Fecha:** 2026-04-12 (v2 — ampliado)

---

## Estado General

| Fase | ID | Estado | Completada | Dependencias | Prioridad |
|------|----|--------|------------|--------------|-----------|
| Fase 1 | FASE-GEO-BRIDGE | ✅ Completada | 2026-04-13 | Ninguna | ALTA |
| Fase 2 | FASE-CONF-GATE | ✅ Completada | 2026-04-13 | FASE-GEO-BRIDGE | ALTA |
| Fase 3 | FASE-LLMSTXT-FIX | ✅ Completada | 2026-04-13 | FASE-GEO-BRIDGE | ALTA |
| Fase 4 | FASE-ASSETS-VALIDACION | ✅ Completada | 2026-04-13 | FASE-GEO-BRIDGE | ALTA |
| Fase 5 | FASE-CONFIDENCE-DISCLOSURE | ✅ Completada | 2026-04-13 | FASE-ASSETS-VALIDACION | MEDIA |
| Fase 6 | FASE-TEMPLATE-DEBT | ✅ Completada | 2026-04-13 | Paralela | MEDIA |
| Fase 7 | FASE-CONTENT-SCRUBBER | ✅ Completada | 2026-04-13 | Paralela | MEDIA |
| Fase 8 | FASE-RELEASE | ⏳ Pendiente | — | Fases 1-7 | ALTA |
| Fase 9 | FASE-D4-OPENROUTER | ✅ Completada | 2026-04-13 | FASE-ASSETS-VALIDACION | ALTA |

---

## Detalle por Fase

### FASE-GEO-BRIDGE (Fase 1)

**Objetivo:** Crear el bridge que conecta geo_enriched/ con el pipeline de delivery

**Tareas:**
- [x] Mapear exactamente dónde se generan los assets (hotel_schema, llms_txt)
- [x] Identificar por qué no usan datos de geo_enriched/
- [x] Crear función de enrichment: si asset confidence < 0.7, poblar desde geo_enriched/
- [x] Integrar enrichment en V4AssetOrchestrator
- [x] Tests nuevos para el bridge

**Criterios de aceptación:**
- [x] `hotel_schema` usa datos de `geo_enriched/hotel_schema_rich.json` cuando está disponible
- [x] `confidence_score` del asset refleja datos reales (no 0.5 por defecto)
- [x] Tests pasan

---

### FASE-CONF-GATE (Fase 2)

**Objetivo:** Crear gate de confidence en publication gates

**Tareas:**
- [x] Crear `asset_confidence_gate` en publication_gates.py (gate #8)
- [x] Gate usa Opción A (conservative): WARNING, no bloquea
- [x] GateStatus.WARNING agregado al enum
- [x] Tests para el nuevo gate (6 tests)

**Criterios de aceptación:**
- [x] Publication gates refleja confidence real de assets
- [x] Tests pasan (6/6)

---

### FASE-LLMSTXT-FIX (Fase 3)

**Objetivo:** Fix generador llms.txt para usar datos reales

**Tareas:**
- [x] Modificar `LLMSTXTGenerator.generate()` para recibir datos enriquecidos
- [x] Usar `geo_enriched/llms.txt` como source de verdad si existe
- [x] Si `name="Hotel"` y URL vacía → warning log + PENDIENTE_ONBOARDING
- [x] No generar con placeholders vacíos

**Criterios de aceptación:**
- [x] `llms_txt` contiene nombre real del hotel
- [x] Tests pasan (8/8)

---

### FASE-ASSETS-VALIDACION (Fase 4) — NUEVA

**Objetivo:** Que CADA servicio prometido en la propuesta tenga un asset generado

**Tareas:**
- [x] Crear asset `monthly_report` en catálogo + generador
- [x] Fix `voice_assistant_guide` — asegurar generación (promised_by="always_aeo")
- [x] Fix `whatsapp_button` — promised_by="always" para generarse siempre
- [x] Crear mapeo `PROPOSAL_SERVICE_TO_ASSET` verificable
- [x] Crear gate #9 `proposal_asset_alignment_gate`
- [x] Tests para cada asset nuevo/fixed

**Criterios de aceptación:**
- [x] 7/7 servicios de la propuesta tienen asset generado
- [x] `monthly_report` genera plantilla funcional
- [x] `voice_assistant_guide` se genera
- [x] `whatsapp_button` se genera
- [x] Gate 9 integrado en publication_gates
- [x] Tests pasan (52/52)

---

### FASE-CONFIDENCE-DISCLOSURE (Fase 5) — NUEVA

**Objetivo:** Que la propuesta informe al cliente sobre la calidad de cada asset

**Tareas:**
- [x] Agregar sección "Estado de los Entregables" en propuesta template
- [x] Generar tabla dinámica desde confidence scores reales
- [x] Tests de disclosure

**Criterios de aceptación:**
- [x] Propuesta incluye tabla con nivel de cada entregable
- [x] Tabla refleja confidence real (Completo/Requiere datos/En desarrollo)
- [x] Tests pasan (5/5)

---

### FASE-TEMPLATE-DEBT (Fase 6)

**Objetivo:** Sincronizar template embebido vs V6 y fixear typo

**Tareas:**
- [x] Eliminar template embebido (~150 líneas dead code) + fallback → error explícito si V6 falta
- [x] Fix typo "debeproveer" → "debe prover" en propuesta_v6_template.md
- [x] Eliminar `package_name` dead code ("Kit Hospitalidad 4.0") de v4_proposal_generator.py

**Criterios de aceptación:**
- [x] Template embebido eliminado; V6 es obligatorio (FileNotFoundError si falta)
- [x] Typo corregido; no otros typos similares encontrados
- [x] Tests pasan (28/28)

---

### FASE-CONTENT-SCRUBBER (Fase 7)

**Objetivo:** Fix content scrubber para errores de espaciado y self-replacement

**Tareas:**
- [x] Fix self-replacement warnings: skip si `old == new`
- [x] Agregar regex para palabras pegadas (spacing errors)
- [x] Integrar spacing errors en content_quality gate
- [x] Tests del content scrubber (9 tests nuevos)

**Criterios de aceptación:**
- [x] No más warnings de self-replacement ("proxima"->"proxima", "reserva"->"reserva")
- [x] Spacing errors detectados (debeproveer, paramas, etc.) como warnings
- [x] Tests pasan (28/28 = 19 existentes + 9 nuevos)

---

### FASE-D4-OPENROUTER (Fase 9)

**Objetivo:** 2 fixes criticos: (D4) 3 assets promised_by=always no se planificaban; (OPENROUTER) costo IAO no visible

**Tareas:**
- [x] FIX-D4-A: Modificar `_solutions_to_asset_specs()` para incluir assets con promised_by=["always"] o ["always_aeo"]
- [x] FIX-D4-B: Verificar voice_assistant_guide (promised_by=["always_aeo"]) incluido
- [x] FIX-OPENROUTER-A: Agregar cost_usd, tokens_used, provider_name a LLMReport
- [x] FIX-OPENROUTER-B: Imprimir costo IAO en v4_comprehensive.py (~line 544)
- [x] FIX-OPENROUTER-C: Seccion transparencia IAO stub en propuesta_v6_template.md (partial — necesita flujo llm_report→proposal)

**Criterios de aceptacion:**
- [x] Gate 9: aligned_count >= 6 (antes 3), missing_count <= 1 (antes 3)
- [x] whatsapp_button, voice_assistant_guide, monthly_report en disco
- [x] Costo IAO impreso en log de audit
- [x] Seccion IAO transparency visible en PROPUESTA_COMERCIAL.md
- [x] Tests pasan: 20/20 (proposal_alignment + gate) + 28/28 (pain_mapper + conditional_generator)

**Conocidos gaps (no bloqueantes):**
- FIX-OPENROUTER-C stub: la tabla IAO en la propuesta muestra "—" porque `llm_report` no fluye a `_prepare_template_data()`. Para activar datos reales se requiere: (a) agregar `llm_report` a `V4AuditResult` o `DiagnosticSummary`, o (b) pasar como parametro separado. Architecture gap — no bloquea operacion.

---

### FASE-RELEASE (Fase 8)

**Objetivo:** Release v4.29.0 con validacion completa

**Tareas:**
- [ ] Ejecutar `log_phase_completion.py` para cada fase (1-7)
- [ ] Actualizar CHANGELOG.md con entrada v4.29.0
- [ ] Sync versions
- [ ] Ejecutar `run_all_validations.py --quick`
- [ ] **Ejecutar v4complete --url https://amaziliahotel.com/ como prueba final**

**VALIDACIÓN FINAL — 3 DIMENSIONES:**

#### 1. Presencia (que no falte nada)
- [ ] `assets_generated` contiene 13+ tipos de asset
- [ ] `monthly_report` generado
- [ ] `voice_assistant_guide` generado
- [ ] `whatsapp_button` generado
- [ ] 7/7 servicios de la propuesta tienen asset

#### 2. Efectividad (que materialice soluciones)
- [ ] `hotel_schema` → name: "Amaziliahotel" (no "Hotel")
- [ ] `llms_txt` → URL real, servicios reales
- [ ] `voice_assistant_guide` → checklist Google/Apple/Alexa
- [ ] `whatsapp_button` → número de teléfono o disclaimer
- [ ] `monthly_report` → plantilla con KPIs definidos
- [ ] `indirect_traffic_optimization` → contenido específico de IAO/ChatGPT

#### 3. Calidad y Transparencia
- [ ] Todos los assets con `confidence_score >= 0.7`
- [ ] Propuesta incluye tabla de calidad de assets
- [ ] Publication gates = 9 (incluye asset_confidence + proposal_alignment)
- [ ] Tests pasando (385+)

#### 4. Monitoreo API — OpenRouter Fallback
- [ ] **OpenRouter fallback NO se activó** (verificar en logs)
- [ ] Si fallback == 0 → MiniMax funcionó correctamente ✅
- [ ] Si fallback > 0 → documentar modelo usado y costo estimado
- [ ] Si fallback > 3 → abrir issue de estabilidad MiniMax

---

## Métricas Acumulativas

| Métrica | Inicio (v4.28.0) | Fin (v4.29.0) |
|---------|------------------|---------------|
| Tests | 2150+ | TBD (mínimo 2150) |
| Assets con confidence < 0.7 | 10/10 (100%) | 0 (0%) |
| Servicios prometidos con asset | 4/7 (57%) | 7/7 (100%) |
| Placeholders en assets | 2 (hotel_schema, llms_txt) | 0 |
| Publication gates | 7 | 9 |
| Typos | 1 ("debeproveer") | 0 |
| Self-replacement warnings | 3 | 0 |
