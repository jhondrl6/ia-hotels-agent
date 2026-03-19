---
description: Auditoría técnica y aceleración de credibilidad web para hoteles.
---

# Skill: SEO Technical (Acelerador de Credibilidad)

> [!NOTE]
> **Trigger**: "mejorar velocidad", "arreglar LCP", "auditoría SEO", "optimizar credibilidad".

## Pre-requisitos (Contexto)
- [ ] URL del hotel (`{{url}}`).
- [ ] Datos geográficos previos (opcional).

## Fronteras (Scope)
- **Hará**: Análisis de Performance (LCP, CLS), Verificación de Schema JSON-LD, Auditoría de Keywords Locales. Generación de reporte de aceleración.
- **NO Hará**: No implementa cambios técnicos en el CMS, solo provee las directrices y el kit de entrega.

## Pasos de Ejecución

### 1. Auditoría de Credibilidad Web
// turbo
seo_stage --url {{url}}

*Validación*: Se ha generado el `web_score` y el listado de incidencias críticas.

### 2. Generación de Reporte SEO
Extraer el reporte Markdown del `seo_result` y prepararlo para la entrega.

*Validación*: Reporte SEO completo disponible en el directorio de salida.

### 3. Alineación con CMS
Generar recomendaciones específicas basadas en el CMS detectado (ej. optimización de sliders para Divi).

*Validación*: Directrices de corrección LCP incluidas en el toolkit.

## Criterios de Éxito
- [ ] `web_score` > 80 tras aplicar optimizaciones.
- [ ] Schema.org (LodgingBusiness) validado al 100%.
- [ ] Kit de entrega SEO generado correctamente.

## Plan de Recuperación (Fallback)
- Si el `SEOAccelerator` falla, usar el escáner ligero `watchdog_check`.
- Si el CMS es indetectable, aplicar protocolo de optimización genérico para Core Web Vitals.
