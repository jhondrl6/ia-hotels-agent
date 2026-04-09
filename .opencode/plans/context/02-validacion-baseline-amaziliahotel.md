# VALIDACIÓN BASELINE: v4complete amaziliahotel.com (PRE-IMPLEMENTACIÓN)

**Fecha**: 2026-04-08 19:22
**URL**: https://amaziliahotel.com
**Región detectada**: nacional
**Coherence Score**: 0.8552

---

## RESULTADOS DEL DIAGNÓSTICO (ESTADO ACTUAL — CON LÍMITE DE 4)

### Brechas mostradas: 4 (TRUNCADO)
El sistema detectó potencialmente más, pero solo muestra 4:

| # | Nombre | % Impacto | Costo COP/mes |
|---|--------|-----------|---------------|
| 1 | Sin Schema de Hotel (Invisible para IA) | 28% | $887.400 |
| 2 | Sin FAQ para Rich Snippets | 28% | $887.400 |
| 3 | Canal Directo Cerrado (Sin WhatsApp) | 18% | $574.200 |
| 4 | Metadatos por Defecto del CMS | 18% | $574.200 |

**Total mostrado**: $2.923.200 COP/mes
**Pérdida reportada**: $3.132.000 COP/mes
**Gap**: $208.800 COP/mes no asignados a ninguna brecha (porque están truncados)

### PROBLEMAS DETECTADOS EN EL DOCUMENTO

1. **"LAS 4 BRECHAS CRÍTICAS IDENTIFICADAS"** — Hardcode en header (línea 71)

2. **Detalle incorrecto en BRECHA 3**: Dice "Canal Directo Cerrado (Sin WhatsApp)" pero el detalle dice "Su sitio usa titulos y descripciones por defecto del CMS" — esto es el detalle de BRECHA 4, copiado erróneamente. El OpportunityScorer está generando justificaciones incorrectas por falta de mappings.

3. **Detalle duplicado en BRECHA 4**: Mismo texto que BRECHA 3 — los justification templates se están usando como fallback cuando el pain_id no tiene mapping específico.

4. **Tabla resumen trunca a 4 filas**: La tabla "BRECHAS → OPORTUNIDADES" tiene exactamente 4 filas fijas.

5. **Brecha 4 recuperación = "siguiente generación de huespedes"**: Texto genérico hardcodeado en template (no es un valor calculado).

### BRECHAS PROBABLES QUE FALTAN (detectables pero no mostradas)

Basado en el audit:
- AEO Score: 0/100 → Probablemente hay brechas de Schema y contenido citable
- SEO Score: 40/100 → Probablemente hay metadatos CMS por defecto (ya mostrada)
- Quick wins sugiere: Schema Hotel, WhatsApp, FAQ, Fotos GBP → Hay más brechas de las que muestra
- **Falta de Reviews**: GBP probablemente tiene pocas reviews (no mostrado)
- **Sin Open Graph**: No configurado (reportado en señales de IA, no mostrado como brecha)
- **Contenido no citable**: Citabilidad no medida (no mostrado como brecha)

Estimación: El hotel podría tener **6-7 brechas**, no 4.

---

## PROPUESTA COMERCIAL

### Problemas detectados:

1. **No consume brechas del diagnóstico**: La propuesta ofrece servicios fijos (GEO, IAO, AEO, SEO, WhatsApp, Schema, Informe) sin dinámica. No diferencia entre un hotel con 3 brechas vs 7.

2. **Paquete único**: Solo ofrece "Kit Hospitalidad Digital" a $130.500 COP/mes. No hay tiers basados en brechas.

3. **ROI irreal**: Proyecta $18.009.000 COP beneficio en 6 meses invirtiendo solo $783.000 COP (ROI 24X). Esto asume que TODAS las brechas se resuelven al 100%, lo cual es optimista.

4. **Desconexión con diagnóstico**: El diagnóstico menciona Schema y FAQ como las brechas top, pero la propuesta vende "Búsqueda por Voz (AEO)" como servicio — no hay brecha de voz detectada en el diagnóstico.

5. **Typo**: "huespedes" (correcto: "huéspedes"), "complicado" por "complicado"

---

## ASSETS GENERADOS

### Assets en output:
| Asset | Tipo | ¿Cubre brecha diagnóstico? |
|-------|------|---------------------------|
| hotel_schema | Schema JSON | ✅ BRECHA 1 (Sin Schema Hotel) |
| faq_page | FAQ CSV | ✅ BRECHA 2 (Sin FAQ) |
| whatsapp_button | HTML | ✅ BRECHA 3 (Sin WhatsApp) |
| optimization_guide | Guía MD | ✅ BRECHA 4 (Metadatos CMS) |
| analytics_setup_guide | Guía GA4 | ❌ No hay brecha de analytics |
| geo_playbook | Playbook GEO | ❌ No hay brecha GEO explícita |
| review_plan | Plan reviews | ❌ No hay brecha de reviews |
| llms_txt | llms.txt | ❌ No hay brecha de llms |
| org_schema | Schema Org | ❌ No hay brecha de org schema |
| indirect_traffic_optimization | Guía | ❌ No hay brecha de tráfico |

### Hallazgo: 6 de 10 assets generados NO corresponden a brechas mostradas en el diagnóstico
Esto se debe a que:
1. El diagnóstico solo muestra 4 brechas (las reales son más)
2. PainSolutionMapper detecta SUS PROPIOS pains (con umbrales distintos)
3. Assets como org_schema, llms_txt, indirect_traffic_optimization se generan por config del catálogo, no por brechas del diagnóstico

---

## VEREDICTO BASELINE

**3 DESCONEXIONES CRÍTICAS** que el plan BRECHAS-DINAMICAS debe resolver:

1. **Truncamiento**: Se detectan N brechas pero solo se muestran 4
2. **Detalle incorrecto**: Pain_ids sin mapping en scorer reciben justificaciones de otros pain_ids
3. **Assets huérfanos**: 60% de assets no trazan a brechas visibles en el diagnóstico

**2 DESCONEXIONES SECUNDARIAS** (no cubiertas por este plan, pero documentadas):

4. **Propuesta estática**: No consume brechas dinámicamente (mejora futura)
5. **ROI sobre-optimista**: Proyección no calibra por probabilidad de resolución por brecha
