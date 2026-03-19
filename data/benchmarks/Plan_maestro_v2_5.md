## 📜 Nota Importante: Estado Actual del Plan Maestro v2.5

> Este documento refleja el estado del sistema en **febrero de 2026**, durante la transición hacia el modelo basado en evidencia y coherencia explícita (v4.0.0+).  
> Aunque el Plan Maestro v2.5.0 fue una guía estratégica importante en su tiempo, **el sistema actual (v4.0.0+) ya no genera outputs basados en paquetes predefinidos ni en los umbrales de decisión aquí descritos**.  
>  
> Los outputs actuales se basan en:  
> - **Triangulación de evidencia** (web + GBP + input del usuario)  
> - **Impacto financiero real estimado** (por causa: GBP, SEO, Schema, etc.)  
> - **Scores por área**: GEO, Activity (GBP), SEO, AEO (Schema), IAO  
> - **Coherence score global** (umbral de publicación: ≥ 0.80)  
> - **Modelo 4-Pilares de valor** (en lugar de paquetes fijos)  
>  
> Esta versión del plan maestro se mantiene **como referencia histórica y de aprendizaje**, no como guía operativa activa.  
> Para comprender cómo el sistema genera diagnósticos y propuestas hoy, revisar los outputs en `output/v4_complete/` y los módulos en:  
> - `orchestration_v4/`  
> - `data_validation/`  
> - `commercial_documents/`  
> - `asset_generation/`  
>  
> ---  
>  
> ## 🔄 Evolución desde v2.5 hacia v4.0+  
>  
> ### De: Paquetes predefinidos y umbrales fijos  
> → A: Evaluación dinámica por impacto financiero y coherencia  
>  
> | Elemento | Plan Maestro v2.5.0 | Sistema actual (v4.0.0+) |  
> |---------|---------------------|---------------------------|  
> | **Lógica de recomendación** | Paquetes basados en umbrales (GEO, GBP, RevPAR, etc.) | Impacto financiero por causa + coherence score ≥ 0.80 |  
> | **Outputs de paquetes** | Starter GEO, Pro AEO, Elite, Elite PLUS (con inversiones fijas: $1.8M, $3.8M, $4.8M, $7.5M, $9.8M) | Ningún paquete mencionado en outputs. En su lugar: desglose de pérdida por causa y propuesta basada en modelo 4-Pilares |  
> | **Inversión recomendada** | Valores fijos por paquete | Sugerida dinámicamente según brecha de conversión, capacidad de pago y umbrales de rentabilidad interna (ej: precio/pérdida ≥ 3x) |  
> | **Enfoque de valor** | Paquetes de servicios prearmados | Modelo 4-Pilares: Visibilidad Local (GEO), Autoridad en IA (AEO/IAO), Conversión Directa (botón WA, velocidad web), Confiabilidad (coverage de evidencia, zero contradictions) |  
> | **Motor de decisión** | Umbrales de Decisión v2.5 (reglas explícitas) | Triple Triangulación + Validación Cruzada + Gates de Publicación (coherence, evidence coverage, financial validity, etc.) |  
> | **Certificación** | Paquetes con nivel (Starter, Pro, Elite) | Ningún paquete. En su lugar: diagnóstico validado (coherence score reportado), propuesta comercial, y assets condicionales (PASSED/ESTIMATED/BLOCKED) |  
>  
> ---  
>  
> ## 📊 Comparación de Outputs: Entonces vs Ahora  
>  
> ### ❌ Output típico bajo Plan Maestro v2.5.0 (ej: febrero 2026)  
> ```
> [CLIP] PAQUETE RECOMENDADO: Pro AEO Plus  
> ### Inversión Mensual  
> **$4.800.000 COP/mes**  
>  
> ### ROI Proyectado  
> **200X en 6 meses  
> ```  
>  
> ### ✅ Output actual bajo v4.0.0+ (ej: marzo 2026)  
> ```
> ## [CLIP] PAQUETE RECOMENDADO: Kit Hospitalidad 4.0  
>  
> ### Inversión Mensual  
> **$800.000 COP/mes**  
>  
> ### ROI Proyectado  
> **292X en 6 meses**  
>  
> ### [MONEY] PROYECCIÓN FINANCIERA (6 MESES)  
> | Mes | Inversión | Ingreso Recuperado | Beneficio Neto | Acumulado |  
> |-----|-----------|-------------------|----------------|-----------|  
> | 1 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $2.332.000 COP |  
> | 2 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $4.664.000 COP |  
> | 3 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $6.996.000 COP |  
> | 4 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $9.328.000 COP |  
> | 5 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $11.660.000 COP |  
> | 6 | $800.000 COP | $3.132.000 COP | $2.332.000 COP | $13.992.000 COP |  
> ```  
>  
> 🔑 **Diferencia clave**:  
> - Antes: recomendación basada en encajar al hotel en un paquete predefinido.  
> - Ahora: recomendación basada en **impacto financiero real detectado**, **coherencia validada**, y **modelo de valor 4-Pilares** adaptado al caso específico.  
>  
> ---  
>  
> ## 🧩 Modelo 4-Pilares de Valor (actual, v4.0.0+)  
>  
> El sistema actual evalúa y propone acciones en torno a cuatro pilares de valor, cuyos puntajes aparecen en los diagnostics:  
>  
> | Pilar | Abreviatura | Qué mide | Ejemplo de hallazgo en output |  
> |-------|-------------|----------|-------------------------------|  
> | **Visibilidad Local** | GEO | Presencia y precisión en Google Maps, datos de ubicación, términos de búsqueda local | `Low GBP geo_score (0/100)` → $1.252.800 COP/mes en riesgo |  
> | **Autoridad en IA** | AEO + IAO | Estructura de datos para buscadores generativos (ChatGPT, Perplexity, etc.) y riqueza de contenido | `Sin Schema FAQ` → $313.200 COP/mes en riesgo (AEO)<br>`IAO: 40/100` (autoridad básica para IA) |  
> | **Conversión Directa** | CRO | Facilidad para reservar directamente (botón de WhatsApp, velocidad web, llamada a acción clara) | `Metadata: Meta description está vacía` → $626.400 COP/mes en riesgo<br>`Fix web crítico para reserva directa` (mencionado en Pro AEO Plus histórico) |  
> | **Confiabilidad y Transparencia** | TRUTH | Coherence score, cobertura de evidencia, ausencia de contradicciones duras, niveles de confianza explícitos (VERIFIED/ESTIMATED/CONFLICT) | `Coherence Score: 0.9114285714285714` (VERIFIED-like)<br>`Certificado de Veracidad: Este diagnóstico ha sido validado mediante Triple Triangulación` |  
>  
> Cada pilar contribuye al **impacto financiero total estimado** y a la **recomendación final de inversión y modelo de acción**.  
>  
> ---  
>  
> ## 📎 Conclusión  
>  
> El Plan Maestro v2.5.0 representa un hito importante en la evolución de iah-cli:  
> - Fue el puente entre un modelo basado en paquetes simples y uno basado en evidencia, coherencia y valor medible.  
> - Sus lecciones viven en el sistema actual: la importancia de la verdad en los datos, la necesidad de validación cruzada, y el enfoque en impacto financiero real.  
>  
> Pero hoy, el sistema ya no empaqueta soluciones en niveles fijos.  
> En su lugar:  
> - **Evalúa el impacto real por causa**,  
> - **Valida la coherencia y la evidencia**,  
> - **Y propone un enfoque de valor 4-Pilares adaptado**, no un paquete predefinido.  
>  
> Este documento se mantiene para que quienes revisen la historia del proyecto puedan comprender de dónde venimos — pero **los outputs actuales deben leerse tal como son: dinámicos, evidenciados y centrados en el impacto real del hotel específico**.  
>  
> ---  
>  
> > *Última actualización de esta nota: 2026-03-19*  
> > *Motivo: Alineación con realidad operacional de outputs v4.0.0+*  
> > *Versión del plan maestro mantenida: 2.5.0 (sin cambio funcional)*  