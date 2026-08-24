---
generated_at: ${generated_at}
version: ${version}
hotel_id: ${hotel_id}
coherence_score: ${coherence_score}
gate_status: ${gate_status}
document_type: DIAGNOSTICO_V6
generator: IA_Hoteles_v4
financial_evidence_tier: "${evidence_tier}"
financial_source: "${financial_source_ref}"
financial_value_central: ${financial_value_central}
financial_value_range: [${financial_value_min}, ${financial_value_max}]
financial_value_range_label: "${financial_value_range_label}"
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

## 1. 🚨 HOY HAY RESERVAS ESCAPÁNDOSE POR ${seccion_1_canales}

| Antes (2023) | Ahora (2026) |
|---|---|
| Entran a Google y revisan 5 webs | Le preguntan a ChatGPT |
| Comparan en Booking | Esperan que la IA recomiende |
| Llaman o escriben por WhatsApp | Prefieren el primero que la IA menciona |

${whatsapp_conflict_business_note}

Cada día que pasa, viajeros potenciales buscan su hotel en Google Maps, le preguntan a ChatGPT o comparan en Booking.com — y algunos se van sin reservar porque no encuentran lo que buscan${seccion_1_whatsapp_clausula}.

---

## 2. 📱 LO QUE VEMOS EN SU HOTEL

${brechas_section}

---

## 3. 💰 LA FUGA FINANCIERA

**${monthly_loss_display}**${estimate_asterisk}${financial_tier_suffix}

${precision_warning}

> **¿De dónde sale esta cifra?**
> Cada mes, viajeros reservan en su zona a través de Booking, Expedia y otros intermediarios. Cada reserva cobra una comisión promedio del 15-25%.
> Mientras más reservas pasan por intermediarios, menos quedan en la caja del hotel.
> La cifra arriba es nuestra mejor estimación de cuánto dinero se escapa cada mes por fugas en su visibilidad digital.

${show_onboarding_cta}
${financial_breakdown_section}

---

## 4. 🔍 ${fugas_title}

De las ${brechas_total_count} brechas técnicas detectadas, estas ${brechas_destacadas_count} son las que más dinero le están costando HOY.
Las otras ${brechas_restantes_count} se resuelven en el plan completo de la Fase 2.

${fugas_principales_section}

---

## 5. ⚡ QUICK WINS ESTA SEMANA

${quick_wins_content}

---

## 6. 🤖 QUÉ HACE IA HOTELES AGENT

IA Hoteles Agent es el sistema que acaba de analizar su hotel. Detecta las ${brechas_total_count} fugas digitales, calcula la fuga financiera aproximada y genera un plan de recuperación personalizado.

**El resultado**: un documento llamado "Propuesta Comercial" con exactamente qué hacer, cuánto cuesta y cuánto puede recuperar.

---

## 📐 ANEXO TÉCNICO

---

### Score de Visibilidad Digital

| Indicador | Su Negocio | Promedio Regional | Estado |
|-----------|------------|------------------|--------|
| **SEO Local** (Para que te ENCUENTREN) | ${seo_score}/100 | ${seo_regional_avg}/100 | ${seo_status} |
| **GEO** (Para que te UBIQUEN) | ${geo_score}/100 | ${geo_regional_avg}/100 | ${geo_status} |
| **AEO** (Para que te CITEN) | ${aeo_score}/100 | ${aeo_regional_avg}/100 | ${aeo_status} |
| **IAO** (Para que te RECOMIENDEN) | ${iao_score}/100 | ${iao_regional_avg}/100 | ${iao_status} |

${geo_score_breakdown}
${seo_score_breakdown}
${aeo_score_breakdown}
${iao_score_breakdown}

> ⚠️ **Nota sobre divergencia de scores**: El score GEO en la tabla principal viene directamente del `geo_score` de Google Business Profile (algoritmo propio de IA Hoteles Agent sobre datos de Google Places: rating, reseñas, fotos, horario, web). El desglose GEO usa el checklist interno de iah-cli. Pueden diferir — ambos miden aspectos complementarios de tu presencia en Maps. Los scores SEO, AEO e IAO usan la misma metodología en tabla y desglose — siempre idénticos.

${excluded_factors_section}
${regional_transparency}

### Métricas de Acceso para IA

${ia_metrics_table}

${positive_findings}
### Resumen de Visibilidad en IA

${analytics_summary_text}

---

### Oportunidad de Mejora

## ✅ Validación de Calidad

${asset_confidence_note}

${manual_attention_table}

---

### Escenarios de Recuperación

${scenario_table_rows}

### 💰 Lo que está en juego

| | Fuga total estimada (6 meses) | Recuperación proyectada (6 meses) |
|---|---|---|
| **Monto** | ${fuga_total_6m} | ${recuperacion_proyectada_6m} |
| **Explicación** | Fuga bruta detectada en las brechas digitales | Curva de maduración 6 meses (equivale a 3.85 meses al ${recov_pct}%) |

> **¿Por qué la diferencia?** No toda la fuga digital es recuperable de inmediato.
> La recuperación sigue una **curva de maduración de 4 pilares** (GEO→SEO→AEO→IAO):
> el impacto mensual crece progresivamente — 15% en el mes 1 → 100% del factor
> realista (**${recov_pct}%**) en el mes 6. El semestre equivale a **3.85 meses**
> de recuperación al factor realista: una estimación conservadora y única,
> idéntica en el diagnóstico y en la propuesta comercial.

${curva_maduracion_note}

**Fuga acumulada 6 meses:** ${loss_6_months}

> ⚠️ ${financial_disclaimer}
>
> *Nivel de evidencia: **Tier ${evidence_tier}** · Precisión: **Tier ${precision_tier}***
> - Tier A: Basado en Google Analytics + Search Console
> - Tier B+: Datos operativos verificados, proyecciones con supuestos conservadores
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

## 📎 PRÓXIMO PASO

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

> ⚠️ **Divergencia GEO**: El score GEO mostrado en la tabla principal proviene del algoritmo propio de IA Hoteles Agent sobre datos de Google Places (rating, reseñas, fotos, horario, web). El desglose mostrado arriba usa la metodología del checklist GEO de iah-cli (6 factores con pesos fijos). Ambos scores pueden diferir — son mediciones complementarias, no redundantes. El checklist GEO evalúa factores técnicos que tú controlas; el score principal refleja la evaluación del agente sobre datos de Places.

**Referencias:** [Metodología completa de scoring](./scoring_methodology.md)
