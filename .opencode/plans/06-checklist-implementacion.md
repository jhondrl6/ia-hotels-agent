# Checklist de Implementación — Fix geo_enriched → Delivery Bridge + Assets Completos

**Proyecto:** AUDIT-PIPELINE-DESALINEACIONES-ASSETS
**Fecha:** 2026-04-12 (v2 — ampliado)

---

## Estado General

| Fase | ID | Estado | Completada | Dependencias | Prioridad |
|------|----|--------|------------|--------------|-----------|
| Fase 1 | FASE-GEO-BRIDGE | ✅ Completada | 2026-04-13 | Ninguna | ALTA |
| Fase 2 | FASE-CONF-GATE | ✅ Completada | 2026-04-13 | FASE-GEO-BRIDGE | ALTA |
| Fase 3 | FASE-LLMSTXT-FIX | ⏳ Pendiente | — | FASE-GEO-BRIDGE | ALTA |
| Fase 4 | FASE-ASSETS-VALIDACION | ⏳ Pendiente | — | FASE-GEO-BRIDGE | ALTA |
| Fase 5 | FASE-CONFIDENCE-DISCLOSURE | ⏳ Pendiente | — | FASE-ASSETS-VALIDACION | MEDIA |
| Fase 6 | FASE-TEMPLATE-DEBT | ✅ Completada | 2026-04-13 | Paralela | MEDIA |
| Fase 7 | FASE-CONTENT-SCRUBBER | ✅ Completada | 2026-04-13 | Paralela | MEDIA |
| Fase 8 | FASE-RELEASE | ⏳ Pendiente | — | Fases 1-7 | ALTA |

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
- [ ] Modificar `LLMSTXTGenerator.generate()` para recibir datos enriquecidos
- [ ] Usar `geo_enriched/llms.txt` como source de verdad si existe
- [ ] Si `name="Hotel"` y URL vacía → marcar como PENDIENTE_ONBOARDING
- [ ] No generar con placeholders vacíos

**Criterios de aceptación:**
- [ ] `llms_txt` contiene nombre real del hotel
- [ ] Tests pasan

---

### FASE-ASSETS-VALIDACION (Fase 4) — NUEVA

**Objetivo:** Que CADA servicio prometido en la propuesta tenga un asset generado

**Tareas:**
- [ ] Crear asset `monthly_report` en catálogo + generador
- [ ] Fix `voice_assistant_guide` — asegurar generación (agregar a pain mapping)
- [ ] Fix `whatsapp_button` — investigar por qué no se genera, corregir
- [ ] Crear mapeo `PROPOSAL_SERVICE_TO_ASSET` verificable
- [ ] Crear gate #9 `proposal_asset_alignment_gate`
- [ ] Tests para cada asset nuevo/fixed

**Criterios de aceptación:**
- [ ] 7/7 servicios de la propuesta tienen asset generado
- [ ] `monthly_report` genera plantilla funcional
- [ ] `voice_assistant_guide` se genera
- [ ] `whatsapp_button` se genera
- [ ] Gate 9 integrado en publication_gates
- [ ] Tests pasan

---

### FASE-CONFIDENCE-DISCLOSURE (Fase 5) — NUEVA

**Objetivo:** Que la propuesta informe al cliente sobre la calidad de cada asset

**Tareas:**
- [ ] Agregar sección "Estado de los Entregables" en propuesta template
- [ ] Generar tabla dinámica desde confidence scores reales
- [ ] Tests de disclosure

**Criterios de aceptación:**
- [ ] Propuesta incluye tabla con nivel de cada entregable
- [ ] Tabla refleja confidence real (Completo/Requiere datos/En desarrollo)
- [ ] Tests pasan

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

### FASE-RELEASE (Fase 8)

**Objetivo:** Release v4.29.0 con validación completa

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
