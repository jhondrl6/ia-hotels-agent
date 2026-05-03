---
generated_at: ${generated_at}
version: ${version}
hotel_id: ${hotel_id}
coherence_score: ${coherence_score}
document_type: DIAGNOSTICO_V6
generator: IA_Hoteles_v4
financial_evidence_tier: "${evidence_tier}"
financial_source: "${financial_source_ref}"
financial_value_central: ${financial_value_central}
financial_value_range: [${financial_value_min}, ${financial_value_max}]
financial_method: "${financial_method}"
financial_opportunity_cost: ${opportunity_cost_formatted}
financial_ota_commission_real: ${ota_commission_real_formatted}
scoring_methodology_url: ./scoring_methodology.md
---

# 🚨 DIAGNÓSTICO DIGITAL
## ${hotel_name} - ${hotel_location}

**Fecha**: ${generated_at}  
**Analista**: IA Hoteles Agent  
**Nichos**: Hoteles Boutique | Negocios Locales (${hotel_region})

---

## 📍 CONTEXTO REGIONAL: EL EJE CAFETERO ESTÁ CAMBIANDO

### Lo que está pasando en ${hotel_region}

Cada mes, miles de turistas buscan dónde hospedarse en la región. Pero la forma de buscar cambió:

| Antes (2023) | Ahora (2026) |
|--------------|--------------|
| Entran a Google y revisan 5 webs | Le preguntan a ChatGPT: "¿Hotel boutique en ${hotel_region}?" |
| Comparan en Booking | Esperan que la IA recomiende |
| Llaman o escriben por WhatsApp | Prefieren el primero que la IA menciona |

**El resultado:** Si su hotel no aparece cuando un viajero pregunta a ChatGPT, nunca llega a su sitio web. Pierde la reserva antes de competir.

### ¿Por qué esto importa en la región?

${regional_context}

> **Pregunta clave**: Cuando alguien pregunte a ChatGPT "hotel boutique cerca de ${hotel_landmark}", ¿su hotel aparece?

---

## 📊 ANÁLISIS ACTUAL: SU POSICIÓN FRENTE A LA COMPETENCIA

### Score de Visibilidad Digital

| Indicador | Su Negocio | Promedio Regional | Estado |
|-----------|------------|------------------|--------|
| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
| **GEO** (Para que te UBIQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |

${geo_score_breakdown}

> ⚠️ **Nota sobre el score GEO**: El desglose arriba usa la metodología del checklist GEO (calcular_score_geo), que pondera 6 factores técnicos. El score en la tabla principal (${geo_score}) puede diferir porque viene directamente del geo_score de Google Business Profile, que usa su propio algoritmo. Ambos son válidos — miden aspectos complementarios de tu presencia en Google Maps.

${excluded_factors_section}

${regional_transparency}

### Métricas de Acceso para IA

${ia_metrics_table}

${positive_findings}
### Resumen de Visibilidad en IA

${analytics_summary_text}

## 💰 Impacto Financiero

${financial_tier_banner}
### ${financial_title_label}

**${ota_commission_formatted}/mes${estimate_asterisk}${financial_tier_suffix}**

Desglose:
- ${ota_commission_basis}
- Fuente del dato: ${ota_commission_source}
- Comisión OTA real (verificable): ${ota_commission_real_formatted}/mes

---

### Oportunidad de Mejora

## ✅ Validación de Calidad

${asset_confidence_note}

${manual_attention_table}

Brechas detectadas que afectan su presencia digital y reservas directas:

${brechas_section}

---

### Escenarios de Recuperación

${scenario_table_rows}

**Proyección 6 meses:** ${loss_6_months}

> ⚠️ ${financial_disclaimer}
>
> *Nivel de evidencia: **Tier ${evidence_tier}***
> - Tier A: Basado en Google Analytics + Search Console
> - Tier B: Basado en benchmarks regionales + datos web
> - Tier C: Basado en datos limitados de su web

${estimate_footnote}

---

## ⏰ ¿POR QUÉ ACTUAR AHORA? (URGENCIA REAL)

### En su región, el reloj corre

${urgencia_contenido}

### ¿Qué pasa si espera 6 meses?

- Competencia consolida posiciones en Google Maps y en las listas de IA
- El costo de recuperar liderazgo será 2-3x mayor
- **Pérdida acumulada:** ${loss_6_months}

---

## 💡 QUICK WINS DISPONIBLES (PRIMEROS 30 DÍAS)

${quick_wins_content}

---

## 📋 RESUMEN DE BRECHAS → OPORTUNIDADES

${brechas_resumen_section}

---

## 📎 PRÓXIMO PASSO

**La solución detallada está en:** `02_PROPUESTA_COMERCIAL.md`

Incluye:
- Plan a medida para su hotel
- Inversión clara y retorno proyectado
- Garantías y términos
- Próximos pasos concretos

---

*Diagnostico generado por IA Hoteles Agent*  
*Especialistas en visibilidad digital para hoteles boutique y negocios locales del Eje Cafetero*

${analytics_footnote}

${analytics_transparency_section}

---

## 📐 Metodología de Scoring

El score de Visibilidad Digital se calcula sobre 4 pilares independientes (0-100 c/u):

| Pilar | Qué mide | Qué NO mide |
|-------|---------|-------------|
| **SEO Local** | SSL, Schema Hotel, Velocidad, Alt text, Blog | Contenido editorial, backlinks |
| **GEO** | Presencia en Google Maps, fotos, NAP, horario | Tasa de respuesta a reseñas, tiempo de respuesta, calidad de respuestas |
| **AEO** | FAQ Schema, OG Tags, Schema Hotel detallado, Contenido factual | Volumen de tráfico, conversiones |
| **IAO** | Citabilidad, acceso de crawlers IA, llms.txt, señales de marca | Tráfico directo, Revenue, NPS |

> ⚠️ **Divergencia GEO**: El score GEO mostrado en la tabla principal proviene directamente del `geo_score` de Google Business Profile (algoritmo de Google). El desglose mostrado arriba usa la metodología del checklist GEO de iah-cli (6 factores con pesos fijos). Ambos scores pueden diferir — son mediciones complementarias, no redundantes. El checklist GEO evalúa factores técnicos que tú controlas; el GBP score refleja la evaluación de Google.

**Referencias:** [Metodología completa de scoring](./scoring_methodology.md)
