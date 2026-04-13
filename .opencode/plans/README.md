# Plan: Fix geo_enriched → Delivery Bridge + Assets Completos

**Estado**: Planificación completada — Listo para implementación
**Fases**: 8 (1 raíz + 3 específicas + 2 gaps + 1 release + 1 docs)
**Prioridad**: ALTA (impacta calidad del deliverable al cliente — captación y crecimiento)

---

## Resumen del Problema

El pipeline de `iah-cli` genera assets de delivery (hotel_schema, llms_txt, etc.) con **datos placeholder** (confidence 0.5, nombre "Hotel", URL vacía).
Simultáneamente, el **GEO Flow** genera `geo_enriched/` con los **mismos assets** pero con **datos reales** (nombre del hotel, URL, amenities).
**El delivery package NUNCA consume geo_enriched/** — el cliente recibe placeholders.

**Agravante**: La propuesta comercial promete 7 servicios con ✅, pero 3 de ellos NO generan asset:
- "Busqueda por Voz (AEO)" → voice_assistant_guide no se genera
- "Boton de WhatsApp" → whatsapp_button no se genera
- "Informe Mensual" → no existe en catálogo

**Si no entregamos lo que prometemos, no captamos clientes y no crecemos.**

---

## Fases

| # | ID | Nombre | Deps | Estado | Prioridad |
|---|-----|--------|------|--------|-----------|
| 1 | FASE-GEO-BRIDGE | geo_enriched → asset enrichment bridge | Ninguna | ⏳ Pendiente | ALTA |
| 2 | FASE-CONF-GATE | Asset confidence gate en publication | GEO-BRIDGE | ⏳ Pendiente | ALTA |
| 3 | FASE-LLMSTXT-FIX | Fix llms.txt generator + fallback | GEO-BRIDGE | ⏳ Pendiente | ALTA |
| 4 | FASE-ASSETS-VALIDACION | Propuesta → Assets: 7/7 servicios con asset | GEO-BRIDGE | ⏳ Pendiente | ALTA |
| 5 | FASE-CONFIDENCE-DISCLOSURE | Transparencia calidad assets en propuesta | ASSETS-VALID | ⏳ Pendiente | MEDIA |
| 6 | FASE-TEMPLATE-DEBT | Sincronizar template embebido vs V6 + typo | Paralela | ⏳ Pendiente | MEDIA |
| 7 | FASE-CONTENT-SCRUBBER | Fix self-replacement + spacing errors | Paralela | ⏳ Pendiente | MEDIA |
| 8 | FASE-RELEASE | v4.29.0 release + validación completa | 1-7 | ⏳ Pendiente | ALTA |

---

## Archivos del Plan

```
.opencode/plans/
├── README.md                                    # Este archivo
├── dependencias-fases.md                         # Diagrama de deps + conflictos
├── 06-checklist-implementacion.md                # Checklist maestro
├── 09-documentacion-post-proyecto.md             # Docs incrementales
├── 05-prompt-inicio-sesion-fase-GEO-BRIDGE.md
├── 05-prompt-inicio-sesion-fase-CONF-GATE.md
├── 05-prompt-inicio-sesion-fase-LLMSTXT-FIX.md
├── 05-prompt-inicio-sesion-fase-ASSETS-VALIDACION.md    # NUEVA
├── 05-prompt-inicio-sesion-fase-CONFIDENCE-DISCLOSURE.md # NUEVA
├── 05-prompt-inicio-sesion-fase-TEMPLATE-DEBT.md
└── 05-prompt-inicio-sesion-fase-CONTENT-SCRUBBER.md
```

---

## Uso

1. **Sesión de preparación** (esta): Generar todos los prompts ✅
2. **Sesión por fase**: Ejecutar cada prompt en su propia sesión
3. **Post-fase**: Ejecutar `log_phase_completion.py` + actualizar docs
4. **FASE-RELEASE**: Ejecutar v4complete y verificar TODOS los criterios

---

## Criterio de Éxito Global

Después de FASE-RELEASE, al ejecutar `v4complete --url https://amaziliahotel.com/`:

### Presencia de Assets (no faltar)
- [ ] Los 10+ assets del catálogo se generan (incluyendo monthly_report, voice_assistant_guide, whatsapp_button)
- [ ] 7/7 servicios de la propuesta tienen asset correspondiente

### Efectividad de Assets (materializar soluciones)
- [ ] `hotel_schema` contiene nombre real del hotel (no "Hotel")
- [ ] `llms_txt` contiene URL real y datos de contacto
- [ ] `whatsapp_button` tiene número de teléfono o marcador claro de pendiente
- [ ] `monthly_report` tiene plantilla funcional con KPIs definidos
- [ ] `voice_assistant_guide` tiene checklist por plataforma (Google, Apple, Alexa)

### Calidad y Transparencia
- [ ] Assets con confidence >= 0.7 (post-bridge enrichment)
- [ ] Propuesta incluye tabla de calidad de assets (nivel de cada entregable)
- [ ] Publication gates = 9 (incluye asset_confidence + proposal_alignment)

### Integridad
- [ ] 385+ tests pasando
- [ ] Cadena financiera intacta

---

## Monitoreo de APIs Externas — OpenRouter

Durante la ejecución de v4complete, OpenRouter puede activarse como **fallback de Hermes** si MiniMax falla (códigos 429/503/529).

### Qué Rastrear

| Indicador | Método | Umbral de Alerta |
|-----------|--------|------------------|
| Fallback activations | Logs de Hermes (`~/.hermes/logs/`) | > 0 por ejecución |
| Modelo usado en fallback | Log de provider switch | Cualquier uso = investigar |
| Tokens consumidos (fallback) | OpenRouter dashboard | > $0.10 por ejecución = optimizar |
| Latencia adicional | Time delta provider switch | > 5s adicional = degradación |

### Cómo Verificar Después de v4complete

```bash
# 1. Buscar activaciones de fallback en logs
grep -i "fallback\|openrouter\|provider.*switch" ~/.hermes/logs/*.log | tail -50

# 2. Verificar costo en OpenRouter dashboard
# https://openrouter.ai/analytics

# 3. Checkpoint: si fallback == 0, MiniMax funcionó correctamente
```

### Integración en FASE-RELEASE

Agregar a la checklist de validación final:
- [ ] **OpenRouter fallback NO se activó** (MiniMax funcionó bien)
- [ ] **Si fallback se activó**: documentar qué modelo se usó y costo estimado
- [ ] **Si fallback se activó >3 veces**: abrir issue de estabilidad de MiniMax
