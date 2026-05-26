# Documentación Post-Proyecto — PROPUESTA-COMERCIAL

> Acumulador incremental. Actualizar después de cada fase.

---

## Sección A: Módulos Modificados

| Fase | Módulo | Archivo | Cambio |
|------|--------|---------|--------|
|| FASE-A | `v4_proposal_generator.py` | `modules/commercial_documents/v4_proposal_generator.py` | CODE-1: `recovered_6m` → `effective_monthly_gain` (L796); CODE-3: `net_benefit_6m` → `effective_monthly_gain` (L797); CODE-2: CG-ROI-NEGATIVE gate sync — `monthly_gain` ahora usa `pain_ratio × recovery_realistic` (L339-352) |
|| FASE-B | `v4_diagnostic_generator.py` + `v4_proposal_generator.py` + templates | `modules/commercial_documents/v4_diagnostic_generator.py` + `modules/commercial_documents/templates/diagnostico_v6_template.md` + `modules/commercial_documents/templates/propuesta_v6_template.md` | CROSS-1: Puente dual fuga bruta/recuperación — 4 placeholders nuevos (`fuga_total_6m`, `recuperacion_proyectada_6m`, `pain_pct`, `recov_pct`) en ambos generadores; tabla dual en diagnóstico + bloque trazabilidad en propuesta; diagnóstico usa defaults 20%/20%, propuesta usa pain_ratio real del pricing |
| FASE-C | `v4_proposal_generator.py` | `modules/commercial_documents/v4_proposal_generator.py` | CROSS-2: BREACH_BY_ASSET dict (L1013-1022) mapea cada asset_type a `(brecha_num, nombre, costo_mensual)`; columna "Problema que resuelve" en tabla de servicios (L1043, L1067-1072) — 4 columnas: Servicio | Estado | Problema que resuelve | Qué obtiene |; AEO row con "—" en columna brecha (L1105). CROSS-4: `whatsapp_conflict` extraído de `audit_result.validation.whatsapp_status == CONFLICT` (L718-725) antes de `data = {}`; passed a `_generate_dynamic_services_table(whatsapp_conflict=...)` (L983); override para whatsapp_button → "⚠️ Requiere corrección" + "Guía de corrección incluida" (L1053-1058). |
| FASE-D | `v4_proposal_generator.py` + `commercial_gate.py` + `propuesta_v6_template.md` | `modules/commercial_documents/v4_proposal_generator.py` + `modules/quality_gates/commercial_gate.py` + `modules/commercial_documents/templates/propuesta_v6_template.md` | V-2: 4 labels "⚠️ En preparación/preparacion" → "En proceso de activación — Semana 2" (L1073, L1117, L1167, L1360). V-3: 8 términos nuevos en TECH_JARGON_TERMS (L85-92): OpenRouter, Perplexity, Gemini, GA4_PROPERTY_ID, GSC_SITE_URL, UTM, iah-cli, iahotels.co; tabla IAO movida de sección 7 a Anexo Técnico (L151-161 + L217-232). A-1: fallback string `'onboarding' in document_content.lower()` eliminado de has_onboarding (L361-366). CROSS-5: columna "Confianza" en tabla de servicios con ⚠️ para scores < 0.65 (L1051-1121). |
| FASE-E | `v4_proposal_generator.py` + `propuesta_v6_template.md` + `diagnostico_v6_template.md` + `main.py` | `modules/commercial_documents/v4_proposal_generator.py` + `modules/commercial_documents/templates/propuesta_v6_template.md` + `modules/commercial_documents/templates/diagnostico_v6_template.md` + `main.py` | A-2: umbral AEO unificado a 30 en `_generate_dynamic_services_table()` (L1105, coincidiendo con `_generate_technical_assets_table()` L1313). V-4: "cupo limitado" → "2 cupos disponibles para julio 2026" (L14). V-5: tracking propio Día 7 añadido a garantía (L161). V-6: sección "Hoteles que ya confiaron en nosotros" con placeholder (L169-173). A-3: typo "PASSO" → "PASO" corregido en ambos templates; grep confirma 0 residuales. CROSS-6: lógica de bloqueo por gates en main.py L2728-2774; controlado por `GATE_BLOCKING_ENABLED` env var; si NOT_READY elimina docs y escribe `BLOCKED_BY_GATES.md`. |

---

## Sección B: Funcionalidades Agregadas/Modificadas

| Fase | Funcionalidad | Descripción |
|------|--------------|-------------|
| FASE-A | Unificación financiera en propuesta | `recovered_6m` y `net_benefit_6m` ahora usan `effective_monthly_gain` (post-recovery) sincronizados con `total_recovered`; gate CG-ROI-NEGATIVE ahora calcula con `pain_ratio × recovery` alineado a la tabla ROI |
| FASE-B | Puente dual fuga bruta/recuperación efectiva | Diagnóstico y propuesta ahora muestran AMBOS: "Fuga total estimada" y "Recuperación proyectada con servicio", con explicación visible del mecanismo `pain_ratio × recovery_factor`. Diagnóstico usa defaults conservadores (20%/20%); propuesta usa pain_ratio real del hotel (~41%) del pricing. Divergencia numérica intencional: el diagnóstico comunica urgencia con estimaciones conservadoras, la propuesta entrega precisión financiera. |
| FASE-C | Mapping brecha→servicio + WhatsApp conflict en propuesta | CROSS-2: Cada servicio en la tabla de propuesta ahora muestra qué brecha del diagnóstico resuelve y su costo mensual etiquetado — mejora trazabilidad para el cliente. CROSS-4: Si audit_result.validation.whatsapp_status == CONFLICT, el botón de WhatsApp muestra "⚠️ Requiere corrección (guía incluida)" en lugar de "ℹ️ Presente en sitio", reflejando honestamente el conflicto detectado. |
| FASE-D | Credibilidad: labels, jargon gate, onboarding, confidence column | V-2: Labels unificados eliminan inconsistencia visual (4 versiones de "En preparación"). V-3: Gate CG-TECH-JARGON ahora detecta 8 nuevos términos técnicos (incluyendo iah-cli, iahotels.co, UTM, GA4, GSC) y tabla IAO movida a anexo donde no expone costos a gerencia. A-1: Fallback string eliminado — has_onboarding ahora depende solo de pricing_result.is_onboarding, eliminando falsos positivos en el gate CG-ROI-NEGATIVE. CROSS-5: Columna "Confianza" en tabla de servicios hace visible el confidence score, permitiendo al cliente ver qué assets están por debajo del umbral 0.65 (ej: optimization_guide 50%). |
| FASE-E | Paquete comercial, pulido, gate blocking | A-2: Umbral AEO unificado a 30 en ambas tablas — elimina inconsistencia donde un hotel con score_aeo=25 veía fila AEO en una tabla pero no en otra. V-4: Cupo limitado ahora cuantificado ("2 cupos para julio 2026") en lugar de placeholder genérico. V-5: Garantía incluye mecanismo concreto de medición — "tracking propio Día 7 sin GA4" elimina ambigüedad sobre cómo se verifica el 10%. V-6: Placeholder de prueba social preparado para futuros casos de éxito. A-3: Typo "PASSO" corregido en ambos templates (propuesta + diagnóstico). CROSS-6: Gates NOT_READY ahora bloquean entrega de documentos; flag `GATE_BLOCKING_ENABLED` permite activación progresiva sin romper CI. |

---

## Sección C: Evidencia

| Fase | Tipo | Ruta |
|------|------|------|
| — | — | — |

---

## Sección D: Métricas

| Fase | Métrica | Antes | Después |
|------|---------|-------|---------|
| — | — | — | — |

---

## Sección E: Archivos del Plan

| Archivo | Estado |
|---------|--------|
| `README.md` | ✅ Creado |
| `dependencias-fases.md` | ✅ Creado |
| `06-checklist-implementacion.md` | ✅ Creado |
| `09-documentacion-post-proyecto.md` | ✅ Creado |
| `05-prompt-inicio-sesion-fase-A.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-B.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-C.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-D.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-E.md` | ✅ Completada |
| `05-prompt-inicio-sesion-fase-F.md` | ⏳ |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | ⏳ |
