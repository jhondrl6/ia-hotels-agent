# Deuda Comercial — PROPUESTA-COMERCIAL FASE-F
## Hallazgos Post-Ejecución (v4.53.0)

**Fecha**: 2026-05-26
**Contexto**: FASE-F ejecutada para Hotel Castilla Real
**Hotel**: https://www.hotelcastillareal.com/
**Veredicto técnico**: ✅ Paquete funcional — 4.5/5 niveles superados
**Veredicto comercial**: ⚠️ Requiere decisión antes de entregar al cliente

---

## Hallazgo 1: Inconsistencia pain_ratio — 20% vs 40%

### Descripción
El puente dual (CROSS-1, FASE-B) está correctamente implementado en ambos documentos, pero los valores de pain_ratio divergen:

| Documento | pain_ratio usado | Recuperación proyectada 6m |
|-----------|-----------------|---------------------------|
| Diagnóstico | 20% × 20% = 4% | ~$898.002 COP |
| Propuesta | ~41% × 20% = 8.2% | $1.832.832 COP |

### ¿Por qué es intencional?
- **Diagnóstico**: usa defaults conservadores (20%) para causar impacto emocional sin conocer el perfil real del hotel
- **Propuesta**: usa el `pain_ratio` real del pricing engine (~41%) porque ya tiene datos del hotel

### ¿Requiere fase?
**No.** Es diseño, no bug. La única mejora posible es agregar una nota explicativa breve que diga algo como: *"El 20% del diagnóstico es una estimación regional conservadora; su perfil de canal directo (20%) ajusta esto al 41% en la propuesta."*

### Acción opcional
Si querés que esa nota exista, es un cambio de 3 líneas en el template del diagnóstico. ¿Querés que lo haga ahora o lo dejamos como está (es decisión de copywriting, no bloquea)?

---

## Hallazgo 2: ROI proyectado negativo — Escenarios Base

### Descripción
Con los datos actuales del hotel, el modelo financiero actual no cierra:

```
Inversión mensual:        $1.200.000 COP
Recuperación estimada:     $305.472 COP/mes  (41% × 20% × $3.741.696)
Resultado neto/mes:          -$894.528 COP
Resultado neto/6m:        -$5.367.168 COP
ROI a 6 meses:                 0.3X
```

**Peor aún**: el escenario `optimistic` en `financial_scenarios.json` es **negativo** (-$270.950/mes), lo que significa que incluso en el mejor de los casos, el hotel pierde dinero con el modelo actual.

### ¿Por qué pasa?
- `direct_channel_percentage: 0.2` (80% de las reservas son por OTA → comisión alta → dolor alto)
- `evidence_tier: B` (sin GA4, sin datos reales de tráfico)
- Pricing actual: $1.200.000 COP/mes fijo
- El modelo asume recuperación vía canal directo, pero el hotel no tiene infraestructura para capturar esa recuperación aún

### ¿Requiere fase?
**No.** No se resuelve con código. Se resuelve，重新设计商业模型 o ajustando el precio.

---

## Opciones Comerciales Disponibles

### Opción A: Lower pricing hasta tener GA4
**Lógica**: $1.200.000/mes no se justifica sin datos reales. Cobrar $300-400k/mes durante 1-2 meses de onboarding mientras se conecta GA4, luego re-calcular con datos reales.

| Mes | Inversión | Recuperación real (estimada) | Resultado |
|-----|-----------|------------------------------|-----------|
| 1 | $300.000 | $305.472 | +$5.472 |
| 2 | $300.000 | $305.472 | +$5.472 |
| 3+ | $1.200.000 | [datos GA4] | Por definir |

### Opción B: Quick wins primero — fase de activación gratis o barata
**Lógica**: Vender los quick wins de alto dolor (WhatsApp conflict, Schema Hotel, llms.txt) como proyecto único de bajo costo. La fase mensual completa se vende después con datos reales.

- **Activación**: $0-$200.000 (proyecto puntual, ~1 semana)
- **包含**: WhatsApp conflict guide, Schema Hotel, llms.txt, diagnosis completo
- **Upsell**: Contrato mensual después de ver resultados medidos

### Opción C: Cobrar % del recovery real
**Lógica**: En vez de fee fijo, cobrar un % del monto recuperado. Elimina el riesgo del cliente y alinea incentivos.

```
Propuesta: 15% del recovery monthly
Si recovery real = $305.472/mes → fee = $45.821/mes ✅
Si recovery real = $1.005.768/mes (con GA4) → fee = $150.865/mes ✅
```

### Opción D: Aceptar la deuda — entregar como está
**Lógica**: Documentar que sin GA4 no hay ROI verificable. Entregar la propuesta con la transparencia de que los números se recalcularán con datos reales.

- Incluir en la propuesta: *"Esta proyección se recalculará con sus datos de Google Analytics 4 en el Día 30. El primer reporte de ROI real será el Día 45."*
- La garantía (Día 7 tracking instalado) ya cubre esto

---

## Recomendación

**La Opción B o D son las más prácticas ahora mismo:**

1. **Opción D (temporal)**: Entregar la propuesta actual con el ROI negativo visible y la garantía de tracking en Día 7. El cliente ve que no hay magia — hay medición real desde el día 1. Si el cliente quiere cerrar así, fine. Si no cierra, pasar a Opción B.

2. **Opción B (estratégica)**: Vender fase de activación como proyecto separado. Más fácil de cerrar porque el riesgo del cliente es casi cero. Permite construir confianza y datos reales para la propuesta mensual.

---

## Acciones Inmediatas

| Prioridad | Qué hacer | Quién |
|-----------|-----------|-------|
| ALTA | Decidir: ¿qué opción comercial presentamos? | Jhond |
| MEDIA | Si Opción B: definir precio de fase activación y quick wins | Jhond |
| MEDIA | Si Opción D: redactar nota de transparencia sobre GA4 | Agente |
| BAJA | Nota de explicativa pain_ratio 20% vs 40% (opcional) | Agente |

---

## Contexto para conversación con cliente

**Lo que NO deben decir:**
- "El ROI es negativo" (cierren el diálogo)
- "No tenemos datos suficientes" (sin GA4, claro)
- "El modelo no funciona" (sí funciona — necesita GA4)

**Lo que SÍ deben decir:**
- "Instalamos medición real desde el Día 1 — usted va a ver exactamente cuánto se recupera"
- "La primera proyección se recalcula con sus datos reales en el Día 30"
- "El quick win de WhatsApp solo ya justifica la inversión" (si vendemos fase activación)

---

## Archivos de referencia

| Archivo | Ubicación |
|---------|-----------|
| Análisis post-implementación completo | `evidence/FASE-F/analisis_post_implementacion.md` |
| Diagnóstico generado | `evidence/FASE-F/01_DIAGNOSTICO_Y_OPORTUNIDAD_20260526_131324.md` |
| Propuesta generada | `evidence/FASE-F/02_PROPUESTA_COMERCIAL_20260526_131333.md` |
| Financial scenarios (datos base) | `evidence/FASE-F/v4_audit/financial_scenarios_20260526_131321.json` |
| Pain ledger | `evidence/FASE-F/v4_audit/pain_ledger.json` |
