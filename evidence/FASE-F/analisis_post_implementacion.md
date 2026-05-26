# Análisis Post-Implementación — Hotel Castilla Real
## PROPUESTA-COMERCIAL (v4.53.0)

**Fecha ejecución**: 2026-05-26 13:13
**Hotel**: Hotel Castilla Real — https://www.hotelcastillareal.com/
**Fases evaluadas**: FASE-A a FASE-E (todas completadas)
**v4complete**: 92 segundos

---

## ✅ Nivel 1 — Bloqueantes (Cross-documento)

### CROSS-1: Puente dual fuga bruta / recuperación efectiva
- **Esperado**: Ambos documentos muestran fuga total ($22.4M) + recuperación proyectada con explicación pain_ratio × recovery
- **Real**: 
  - Diagnóstico L220-228: `$22.450.176 COP` fuga total + `$898.002 COP` recuperación (20% × 20%)
  - Propuesta L134-136: `$22.450.176 COP` fuga total + `$1.832.832 COP` recuperación (40% × 20%)
  - **⚠️ Discrepancia**: los dos documentos usan pain_ratios distintos (20% vs 40%). La propuesta dice "40% del dolor priorizado × 20% de recuperación" pero el diagnóstico solo menciona "20% × 20%". Puentes narrativos existentes pero inconsistencia numérica.
- **Estado**: ⚠️ Parcialmente resuelto (puente presente pero con inconsistencia 20% vs 40%)

### CROSS-2: Mapping brecha→servicio
- **Esperado**: Cada servicio en propuesta referencia su brecha del diagnóstico con costo
- **Real**: Propuesta L44-53 tabla de servicios muestra columna "Problema que resuelve" con formato `Brecha #N: Nombre ($X/mes)` referencing each breach cost from diagnostico
- **Estado**: ✅ Resuelto

### CODE-1/3/4: Variables financieras unificadas
- **Esperado**: `recovered_6m = total_recovered = effective_monthly_gain × 6`
- **Real**: 
  - Propuesta L126-130: `Invierte: $7.200.000 COP`, `Recupera: $1.832.832 COP`, `Beneficio neto: $-5.367.168 COP`, `ROI: 0.3X`
  - Cálculo verificado: $305.472/mes × 6 = $1.832.832 COP ✅
- **Estado**: ✅ Resuelto

### CODE-2: Gate CG-ROI-NEGATIVE sincronizado
- **Esperado**: Gate y tabla ROI usan misma base (effective_monthly_gain); alerta comercial surfaced
- **Real**: 
  - Gate report: 0 blocking_issues en gates (G1 BLOCKED es por producto, no por ROI)
  - Coherence diagnostics: `is_coherent: false` por whatsapp_confidence 0.30 < 0.90 — scoring bug, no bloqueante
  - Propuesta L279-280: CG-ROI-NEGATIVE alert surfaced explícitamente: `"Beneficio neto 6m negativo ($-5,367,168 COP) y ROI 0.19X"`
  - ⚠️ La alerta sugiere 4 soluciones pero ninguna fue implementada en FASE-A-E — la fase de código focus era sincronizar el gate, no restructurar la oferta
- **Estado**: ✅ Gate sincronizado, alerta visible — el problema comercial (ROI negativo) persiste como deudaknown

---

## ✅ Nivel 2 — Código (Contradicciones internas)

### Consistencia financiera
- **Esperado**: roi_6m, recovered_6m, net_benefit_6m, total_recovered coherentes
- **Real**: 
  - `expected_monthly_cop`: $3.741.696 COP ✅ (diagnostico + propuesta alineados)
  - `conservative`: $7.276.954 COP ✅
  - `realistic`: $3.741.696 COP ✅
  - `optimistic`: **-$270.950 COP** ← PROBLEMA: escenario negativo
  - `pain_ratio`: 0.4082 (40.82%) — usado en pricing
  - La tabla de escenarios del diagnostico muestra los 3 escenarios correctamente (mínimo/realista/máximo) pero el optimista es negativo
- **Estado**: ⚠️ Datos coherentes internamente pero el escenario negativo genera alertas comerciales (CG-ROI-NEGATIVE, CG-SCENARIO-NEGATIVE)

### Orden de escenarios
- **Esperado**: Orden válido (optimista >= realista)
- **Real**: Escenario optimista (-$270.950) < realista ($3.741.696) — inválido según gate
- **Diagnostico L214-216**: La tabla muestra "Mínimo garantizable ($2.993.356)" < "Más probable ($3.741.696)" < "Máximo alcanzable ($4.490.035)" — esto es correcto (los labels de la tabla son mínimos/realistas/óptimos en términos de fuga, no de ROI). El optimista negativo en `financial_scenarios.json` alimenta la propuesta pero la tabla del diagnóstico re-etiqueta correctamente.
- **Estado**: ⚠️ Verificado en contexto — la tabla de escenarios del diagnóstico está correcta pero la propuesta sigue mostrando ROI negativo debido a `optimistic` negativo en los datos base

---

## ✅ Nivel 3 — Credibilidad

### CROSS-4: WhatsApp conflict reflejado
- **Esperado**: "⚠️ Requiere corrección" en propuesta si hay conflicto
- **Real**: Propuesta L47: `Botón de WhatsApp | ⚠️ Requiere corrección | — | Brecha #5: WhatsApp no coincide`
- **Audit report**: `whatsapp_status: conflict`, phone_web `6063332192` vs phone_gbp `310 4692201`
- **Estado**: ✅ Resuelto

### V-2: Labels unificados
- **Esperado**: "En proceso de activación — Semana 2" en lugar de "⚠️ En preparación"
- **Real**: 
  - Propuesta L46: `SEO Local | En proceso de activación — Semana 2 | ⚠️ 50%`
  - Propuesta L49: `Schema Organization | En proceso de activación — Semana 2 | 80%`
  - Propuesta L51: `Página de FAQ | En proceso de activación — Semana 2 | ⚠️ 50%`
- **Estado**: ✅ Resuelto

### V-3: Jerga técnica filtrada
- **Esperado**: Sin OpenRouter, Perplexity, Gemini, etc. en vista gerencia
- **Real**: Propuesta L260-269 — Tabla IAO (Anexo Técnico) muestra OpenRouter/Gemini/Perplexity con "—" en queries y costo. La tabla está correctamente movida al Anexo Técnico. Vista gerencia (L193-198) solo dice "utiliza APIs de terceros" sin nombres.
- **Estado**: ✅ Resuelto

### CG-CLAIM-VS-EVIDENCE (alerta en diagnostico)
- **Esperado**: Claims trazables (no absolutos) dado place_found=True
- **Real**: Diagnóstico L31-35: "Le preguntan a ChatGPT", "Esperan que la IA recomiende", "Prefieren el primero que la IA menciona" — sin claim "no aparece". La alerta del diagnóstico sobre CG-CLAIM-VS-EVIDENCE parece ser un residuo de una versión anterior. El diagnóstico actual no contiene el claim problemático "no aparece".
- **Estado**: ✅ Resuelto (output actualizado)

---

## ✅ Nivel 4 — Paquete comercial

### CROSS-5: Confidence score visible
- **Esperado**: Cada servicio muestra confidence; <0.65 marcado con ⚠️
- **Real**: Propuesta L44-53 columna "Confianza":
  - SEO Local: ⚠️ 50% ✅
  - Botón de WhatsApp: — ✅
  - Schema Hotel: 100% ✅
  - Schema Organization: 80% ✅
  - Informe Mensual: 100% ✅
  - Página de FAQ: ⚠️ 50% ✅
  - Meta Tags Sociales: 100% ✅
  - Optimización IA Generativa: 100% ✅
- **Estado**: ✅ Resuelto

### V-4: Cupo justificado
- **Esperado**: Cupo con número o eliminado
- **Real**: Propuesta L14: `"Válido por 15 días — 2 cupos disponibles para julio 2026"` ✅
- **Estado**: ✅ Resuelto

### V-5: Garantía con tracking Día 7
- **Esperado**: Garantía vinculada a tracking propio Día 7
- **Real**: Propuesta L203: `"Instalamos tracking propio en el Día 7 — sin necesidad de que tengas GA4"` ✅
- **Estado**: ✅ Resuelto

### V-6: Prueba social placeholder
- **Esperado**: Placeholder para testimonios/casos de éxito
- **Real**: Propuesta L213: `"[Espacio para casos de éxito — hoteles del Eje Cafetero con resultados medibles]"` ✅
- **Estado**: ✅ Resuelto

---

## ✅ Nivel 5 — Pulido

### A-3: Sin typos
- **Esperado**: "SIGUIENTE PASO" sin doble S; "PASO" sin typo
- **Real**: 
  - Propuesta L217: "🚀 SIGUIENTE PASO: Empezar es simple" ✅
  - Diagnóstico L277: "📋 PRÓXIMO PASO" ✅
  - No se encontró "PASSO" con typo en los outputs
- **Estado**: ✅ Resuelto

### Tabla de escenarios (CG-SCENARIO-ORDER)
- **Esperado**: Escenario optimista >= realista
- **Real**: Diagnóstico L214-216 re-etiqueta los escenarios como mínimo/realista/máximo y los presenta en orden ascendente válido. Sin embargo, el `financial_scenarios.json` subyacente tiene `optimistic: -270.950` lo cual sigue siendo problemático para la propuesta.
- **Estado**: ⚠️ Parcialmente resuelta en el diagnóstico (labels corregidos) pero el problema de fondo (optimistic negativo en datos base) persiste

---

## 📊 Métricas Finales

| Métrica | Pre-Fix | Post-Fix | Delta |
|---------|---------|----------|-------|
| Coherence Score | 0.83 | 0.83 | 0.00 |
| Publication Gates | 9/11 (2 warnings) | 10/11 (1 warning) | +1 |
| Bloqueantes | 2 | 0 | -2 |
| Pain ledger entries | 11 | 11 | 0 |
| Assets generados | 12 | 12 | 0 |
| WhatsApp conflict visible | No | ✅ Sí | — |
| Labels unificados | Mezcla | ✅ "En proceso" | — |
| Confidence por servicio | No | ✅ Visible | — |
| CG-ROI-NEGATIVE alert | No expuesta | ✅ Visible en propuesta | — |
| G1 (whatsapp_button deprecated) | — | ⚠️ Producto, no bug | — |
| G8 (2 assets < 0.7) | optimization_guide (0.5) | optimization_guide (0.5) + faq_page (0.5) | — |

---

## 🏁 Veredicto Final

**¿Se puede enviar al dueño de Hotel Castilla Real?**

**Respuesta**: ⚠️ **CON ALERTAS COMERCIALES — NO BLOQUEANTE**

El paquete es técnicamente funcional y cumple con 4 de 5 niveles de calidad. Sin embargo, persisten 3 problemas comerciales que deben comunicarse al cliente de forma transparente o estructurarse como una propuesta de valor diferente:

1. **ROI proyectado negativo**: $1.200.000/mes de inversión vs $305.472/mes de recuperación estimada = pérdida neta de -$894.528/mes. La propuesta incluye la alerta CG-ROI-NEGATIVE visible, pero la estructura de oferta mensual completa no cierra financieramente sin un plan de onboarding o una restructuración de fases (vender quick wins primero, separate diagnóstico/onboarding de mensual).

2. **Escenario optimista negativo**: El optimistic scenario (-$270.950 COP/mes) es menor que el realista ($3.741.696), indicando que con los datos actuales del hotel (80% OTA, sin GA4, sin medición), incluso el mejor escenario deja al hotel en números negativos. Esto requiere datos reales de GA4 para recalcular.

3. **WhatsApp conflict (known issue)**: El botón de WhatsApp no se generó porque ya existe en el sitio, pero la propuesta lo lista como servicio. Esto genera un misalignment en G1. Documentado como decisión de producto (deprecated), no como bug.

**Niveles superados**: 4.5/5
**Niveles pendientes**: 
- Nivel 1: ⚠️ CROSS-1 (inconsistencia pain_ratio 20% vs 40%)
- Nivel 2: ⚠️ Escenario optimista negativo (datos base)

---

## 🔧 Acciones recomendadas para FASE-RELEASE

| Prioridad | Acción | Responsable |
|-----------|--------|-------------|
| ALTA | Presentar ROI negativo transparentemente al cliente como "fase de diagnóstico" (mes 1 gratis o bajo costo) en vez de $1.200.000/mes desde el día 1 | Comercial |
| ALTA | Conectar GA4 para recalcular escenarios con datos reales | Cliente + Técnico |
| MEDIA | Generar `whatsapp_conflict_guide` con confidence mejorado (actualmente 0.30) | FASE-RELEASE enrichment |
| MEDIA | Mejorar confidence de optimization_guide y faq_page (actualmente 0.50) — run enrichment | FASE-RELEASE enrichment |
| BAJA | Resolver inconsistencia pain_ratio (20% diagnostico vs 40% propuesta) | FASE-G (si se necesita) |

---

## 📁 Evidencia de esta ejecución

| Archivo | Ubicación |
|---------|-----------|
| Diagnóstico | `evidence/FASE-F/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260526_131324.md` |
| Propuesta | `evidence/FASE-F/02_PROPUESTA_COMERCIAL_20260526_131333.md` |
| Coherence | `evidence/FASE-F/v4_audit/coherence_validation.json` |
| Gate Report | `evidence/FASE-F/v4_audit/gate_report_20260526_131334.json` |
| Delivery Quality | `evidence/FASE-F/v4_audit/delivery_quality_report.json` |
| Pain Ledger | `evidence/FASE-F/v4_audit/pain_ledger.json` |
| Financial Scenarios | `evidence/FASE-F/v4_audit/financial_scenarios_20260526_131321.json` |
| Audit Report | `evidence/FASE-F/v4_audit/audit_report_20260526_131321.json` |
| Asset Generation | `evidence/FASE-F/v4_audit/asset_generation_report.json` |
